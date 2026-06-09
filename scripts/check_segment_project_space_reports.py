#!/usr/bin/env python3
"""Validate the generated segment-project report bundle.

Run from the repository root:

    python3 scripts/check_segment_project_space_reports.py

The check fails only when a required report file is missing or when a local
reference declared by the HTML/QA bundle is broken. Obsolete score artifacts are
reported as warnings because they require cleanup, not a broken report build.
"""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "reports" / "segment_project_space"

EXPECTED_REPORT_FILES = [
    "segment_project_space_report.html",
    "01_data_guide.html",
    "02_research_paths.html",
    "03_evidence_appendix.html",
    "segment_project_space_qa.json",
]

OBSOLETE_SCORE_ARTIFACTS = [
    "segment_project_lane_scores.csv",
    "project_lane_scores.png",
    "tables/segment_project_lane_scores.csv",
    "figures/project_lane_scores.png",
]

LOCAL_REF_ATTRS = {"href", "src"}
SKIP_SCHEMES = {
    "about",
    "data",
    "http",
    "https",
    "javascript",
    "mailto",
    "tel",
}


class LocalReferenceParser(HTMLParser):
    """Collect local href/src references and approximate source positions."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line, column = self.getpos()
        for attr, value in attrs:
            if attr not in LOCAL_REF_ATTRS or value is None:
                continue
            self.references.append(
                {
                    "tag": tag,
                    "attr": attr,
                    "value": value,
                    "line": line,
                    "column": column,
                }
            )


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "QA manifest is missing."
    except json.JSONDecodeError as exc:
        return None, f"QA manifest is not valid JSON: {exc}"


def local_reference_target(base_file: Path, raw_value: str) -> Path | None:
    value = raw_value.strip()
    if not value or value.startswith("#"):
        return None

    parsed = urlsplit(value)
    if parsed.scheme in SKIP_SCHEMES:
        return None
    if parsed.scheme and parsed.scheme != "file":
        return None
    if not parsed.scheme and parsed.netloc:
        return None
    if not parsed.path:
        return None

    if parsed.scheme == "file":
        target = Path(unquote(parsed.path))
    else:
        target = base_file.parent / unquote(parsed.path)
    return target.resolve()


def check_expected_files(report_dir: Path) -> tuple[list[str], list[str]]:
    checked = []
    missing = []
    for name in EXPECTED_REPORT_FILES:
        path = report_dir / name
        checked.append(rel(path))
        if not path.is_file():
            missing.append(rel(path))
    return checked, missing


def check_html_references(report_dir: Path) -> dict[str, Any]:
    checked_refs: list[dict[str, Any]] = []
    broken_refs: list[dict[str, Any]] = []
    html_files = sorted(report_dir.glob("*.html"))

    for html_file in html_files:
        parser = LocalReferenceParser()
        try:
            parser.feed(html_file.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))

        for ref in parser.references:
            target = local_reference_target(html_file, ref["value"])
            if target is None:
                continue

            item = {
                "source": rel(html_file),
                "line": ref["line"],
                "tag": ref["tag"],
                "attr": ref["attr"],
                "value": ref["value"],
                "target": rel(target),
            }
            checked_refs.append(item)
            if not target.exists():
                broken_refs.append(item)

    return {
        "html_files_checked": [rel(path) for path in html_files],
        "local_reference_count": len(checked_refs),
        "broken_references": broken_refs,
    }


def check_qa_manifest(report_dir: Path) -> dict[str, Any]:
    qa_path = report_dir / "segment_project_space_qa.json"
    qa, error = load_json(qa_path)
    result: dict[str, Any] = {
        "path": rel(qa_path),
        "loaded": qa is not None,
        "parse_error": error,
        "declared_reports": [],
        "declared_tables": [],
        "declared_figures": [],
        "missing_reports": [],
        "missing_tables": [],
        "missing_figures": [],
    }
    if qa is None:
        return result

    for raw_path in qa.get("report_paths", []):
        path = ROOT / str(raw_path)
        result["declared_reports"].append(rel(path))
        if not path.is_file():
            result["missing_reports"].append(rel(path))

    for name in qa.get("tables_written", []):
        path = report_dir / "tables" / str(name)
        result["declared_tables"].append(rel(path))
        if not path.is_file():
            result["missing_tables"].append(rel(path))

    for name in qa.get("figures_written", []):
        path = report_dir / "figures" / str(name)
        result["declared_figures"].append(rel(path))
        if not path.is_file():
            result["missing_figures"].append(rel(path))

    return result


def check_obsolete_score_artifacts(report_dir: Path) -> dict[str, Any]:
    checked = []
    found = []
    for name in OBSOLETE_SCORE_ARTIFACTS:
        path = report_dir / name
        checked.append(rel(path))
        if path.exists():
            found.append(rel(path))
    return {"checked": checked, "found": found}


def build_summary(report_dir: Path) -> dict[str, Any]:
    expected_checked, expected_missing = check_expected_files(report_dir)
    html = check_html_references(report_dir) if report_dir.exists() else {
        "html_files_checked": [],
        "local_reference_count": 0,
        "broken_references": [],
    }
    qa_manifest = check_qa_manifest(report_dir)
    stale = check_obsolete_score_artifacts(report_dir)

    errors = []
    warnings = []

    if expected_missing:
        errors.append(
            {
                "type": "missing_expected_report_files",
                "paths": expected_missing,
            }
        )
    if html["broken_references"]:
        errors.append(
            {
                "type": "broken_html_local_references",
                "references": html["broken_references"],
            }
        )
    if qa_manifest["parse_error"] and not expected_missing:
        warnings.append(
            {
                "type": "qa_manifest_unreadable",
                "message": qa_manifest["parse_error"],
            }
        )
    for key, error_type in [
        ("missing_reports", "qa_declared_reports_missing"),
        ("missing_tables", "qa_declared_tables_missing"),
        ("missing_figures", "qa_declared_figures_missing"),
    ]:
        if qa_manifest[key]:
            errors.append({"type": error_type, "paths": qa_manifest[key]})

    if stale["found"]:
        warnings.append(
            {
                "type": "obsolete_score_artifacts_present",
                "paths": stale["found"],
            }
        )

    return {
        "status": "failed" if errors else "ok",
        "report_dir": rel(report_dir),
        "expected_files": {
            "checked": expected_checked,
            "missing": expected_missing,
        },
        "html": html,
        "qa_manifest": {
            "path": qa_manifest["path"],
            "loaded": qa_manifest["loaded"],
            "parse_error": qa_manifest["parse_error"],
            "report_count": len(qa_manifest["declared_reports"]),
            "table_count": len(qa_manifest["declared_tables"]),
            "figure_count": len(qa_manifest["declared_figures"]),
            "missing_reports": qa_manifest["missing_reports"],
            "missing_tables": qa_manifest["missing_tables"],
            "missing_figures": qa_manifest["missing_figures"],
        },
        "obsolete_score_artifacts": stale,
        "warnings": warnings,
        "errors": errors,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        f"Segment project report QA: {summary['status'].upper()}",
        f"Report dir: {summary['report_dir']}",
        (
            "Expected files: "
            f"{len(summary['expected_files']['checked'])} checked, "
            f"{len(summary['expected_files']['missing'])} missing"
        ),
        (
            "HTML local references: "
            f"{summary['html']['local_reference_count']} checked, "
            f"{len(summary['html']['broken_references'])} broken"
        ),
        (
            "QA manifest: "
            f"{summary['qa_manifest']['table_count']} tables, "
            f"{summary['qa_manifest']['figure_count']} figures, "
            f"{len(summary['qa_manifest']['missing_tables'])} missing tables, "
            f"{len(summary['qa_manifest']['missing_figures'])} missing figures"
        ),
        (
            "Obsolete score artifacts: "
            f"{len(summary['obsolete_score_artifacts']['found'])} found"
        ),
    ]

    if summary["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        for warning in summary["warnings"]:
            paths = ", ".join(warning.get("paths", []))
            lines.append(f"- {warning['type']}: {paths}")

    if summary["errors"]:
        lines.append("")
        lines.append("Errors:")
        for error in summary["errors"]:
            if "paths" in error:
                detail = ", ".join(error["paths"])
            elif "references" in error:
                detail = ", ".join(
                    f"{ref['source']}:{ref['line']} -> {ref['target']}"
                    for ref in error["references"]
                )
            else:
                detail = error.get("message", "")
            lines.append(f"- {error['type']}: {detail}")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated reports/segment_project_space assets."
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Report bundle directory. Defaults to reports/segment_project_space.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Defaults to text.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report_dir = args.report_dir
    if not report_dir.is_absolute():
        report_dir = ROOT / report_dir
    summary = build_summary(report_dir.resolve())

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))

    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
