#!/usr/bin/env python3
"""Write a standalone detailed shock-catalog note outside the HTML reports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "reports" / "segment_project_space" / "tables"
OUT_PATH = ROOT / "docs" / "segment_candidate_shock_catalog_detail.md"


def read_table(name: str) -> pd.DataFrame:
    path = TABLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path.relative_to(ROOT)}")
    return pd.read_csv(path)


def clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def split_semicolon(value: object) -> list[str]:
    text = clean(value)
    return [part.strip() for part in text.split(";") if part.strip()]


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "_No rows._\n"
    out = df.loc[:, columns].copy()
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for _, row in out.iterrows():
        cells = []
        for col in columns:
            text = clean(row[col]).replace("\n", " ").replace("|", "\\|")
            cells.append(text)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def source_links(sources: pd.DataFrame) -> str:
    if sources.empty:
        return "_No source rows recorded._\n"
    lines = []
    for _, row in sources.sort_values(["source_type", "source_title"]).iterrows():
        title = clean(row["source_title"])
        url = clean(row["source_url"])
        source_type = clean(row["source_type"])
        claim = clean(row["source_claim"])
        lines.append(f"- [{title}]({url}) ({source_type}): {claim}")
    return "\n".join(lines) + "\n"


def granularity_note(row: pd.Series) -> str:
    start = int(row["window_start_year"])
    end = int(row["window_end_year"])
    anchor = int(row["event_anchor_year"])
    if start == end:
        return (
            f"This row is represented as a one-year candidate window. "
            f"The current coverage screen uses {anchor} as the anchor year."
        )
    return (
        f"This row spans {start}-{end} because the source-backed institutional change has multiple components. "
        f"The current coverage screen places the row at anchor year {anchor}; separate sub-events can be "
        "documented later if the research design needs one treatment year per event."
    )


def window_table(readiness: pd.DataFrame) -> str:
    cols = [
        "window",
        "start_year",
        "end_year",
        "rows",
        "firms",
        "firm_years",
        "margin_ready_pct",
        "allocation_ready_pct",
    ]
    return markdown_table(readiness.sort_values(["start_year", "window"]), cols)


def write_document() -> None:
    catalog = read_table("segment_project_candidate_shock_catalog.csv")
    sources = read_table("segment_project_candidate_shock_sources.csv")
    readiness = read_table("segment_project_event_window_readiness.csv")
    type_summary = read_table("segment_project_candidate_shock_type_summary.csv")

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    catalog = catalog.sort_values(["event_anchor_year", "shock_type", "shock_family", "shock_id"]).reset_index(drop=True)

    lines: list[str] = []
    lines.append("# Segment Project Candidate Shock Catalog Detail")
    lines.append("")
    lines.append(f"Generated at UTC: {generated_at}")
    lines.append("")
    lines.append("This is a standalone research note. It is not part of the HTML report bundle under `reports/segment_project_space/`.")
    lines.append("")
    lines.append("The file documents candidate shocks found so far for the segment-data project. It records source-backed event windows, source links, current segment-data exposure screens, mechanical coverage around the event windows, mapping requirements, and caveats. It does not choose a research design and does not define treatment/control status.")
    lines.append("")
    lines.append("## How To Read This Note")
    lines.append("")
    lines.append("- `shock_family` is the reader-facing candidate shock name.")
    lines.append("- `shock_type` is only a grouping label, such as derivative availability, power-market design, or policy/market access.")
    lines.append("- `candidate_window` is the source-backed window over which the relevant market or institutional change occurs.")
    lines.append("- `event_anchor_year` is the single year currently used for mechanical pre/event/post coverage screens.")
    lines.append("- `exposure_families` are current BUSSEG/OPSEG screening proxies from the segment data. They are not final treatment definitions.")
    lines.append("- The coverage tables are mechanical data-support summaries. They do not imply a causal design.")
    lines.append("")
    lines.append("## Current Catalog Summary")
    lines.append("")
    lines.append(f"- Candidate shocks recorded: {len(catalog):,}")
    lines.append(f"- Shock types recorded: {catalog['shock_type'].nunique():,}")
    lines.append(f"- Source rows recorded: {len(sources):,}")
    lines.append(f"- Anchor-year range: {int(catalog['event_anchor_year'].min())}-{int(catalog['event_anchor_year'].max())}")
    lines.append("")
    lines.append(markdown_table(type_summary, ["shock_type", "candidate_windows", "first_anchor_year", "last_anchor_year", "shock_families"]))
    lines.append("")
    lines.append("## Candidate Shocks")
    lines.append("")

    for idx, row in catalog.iterrows():
        shock_id = clean(row["shock_id"])
        shock_sources = sources[sources["shock_id"].eq(shock_id)].copy()
        shock_ready = readiness[readiness["shock_id"].eq(shock_id)].copy()
        exposure_list = ", ".join(f"`{item}`" for item in split_semicolon(row["exposure_families"]))

        lines.append(f"### {idx + 1}. {clean(row['shock_family'])}")
        lines.append("")
        lines.append(f"- `shock_id`: `{shock_id}`")
        lines.append(f"- `shock_type`: {clean(row['shock_type'])}")
        lines.append(f"- `candidate_window`: {clean(row['candidate_window'])}")
        lines.append(f"- `event_anchor_year`: {int(row['event_anchor_year'])}")
        lines.append(f"- `window_start_year` / `window_end_year`: {int(row['window_start_year'])} / {int(row['window_end_year'])}")
        lines.append(f"- Current exposure-family screen: {exposure_list}")
        lines.append("")
        lines.append("**Source-backed event description**")
        lines.append("")
        lines.append(clean(row["source_summary"]))
        lines.append("")
        lines.append("**Source rows**")
        lines.append("")
        lines.append(source_links(shock_sources))
        lines.append("")
        lines.append("**Segment-data mapping note**")
        lines.append("")
        lines.append(clean(row["segment_mapping_note"]))
        lines.append("")
        lines.append("**Mapping work still separate from this catalog**")
        lines.append("")
        lines.append(clean(row["mapping_requirement"]))
        lines.append("")
        lines.append("**Window granularity note**")
        lines.append("")
        lines.append(granularity_note(row))
        lines.append("")
        lines.append("**Current caveat**")
        lines.append("")
        lines.append(clean(row["caveats"]))
        lines.append("")
        lines.append("**Mechanical segment-data coverage around anchor year**")
        lines.append("")
        lines.append(window_table(shock_ready))
        lines.append("")

    lines.append("## Source Artifacts")
    lines.append("")
    lines.append("- `reports/segment_project_space/tables/segment_project_candidate_shock_catalog.csv`")
    lines.append("- `reports/segment_project_space/tables/segment_project_candidate_shock_sources.csv`")
    lines.append("- `reports/segment_project_space/tables/segment_project_event_window_readiness.csv`")
    lines.append("- `reports/segment_project_space/tables/segment_project_candidate_shock_type_summary.csv`")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    write_document()
