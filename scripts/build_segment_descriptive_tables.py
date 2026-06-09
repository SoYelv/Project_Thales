#!/usr/bin/env python3
"""Build econ-style descriptive tables for the raw segment source file."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from segment_project_common import (
    DATA_PATH,
    DEDUP_KEY,
    EXTENDED_NUMERIC,
    NONOP,
    PRIMARY_NUMERIC,
    ROOT,
    latest_srcdate_dedup_summary,
    latest_srcdate_view,
    load_segments,
    sha256_file,
    utc_now,
)
from segment_project_definitions import coverage_definitions, variable_dictionary


OUT_DIR = ROOT / "reports" / "segment_descriptives"
TABLE_DIR = OUT_DIR / "tables"
REPORT_PATH = OUT_DIR / "segment_descriptive_report.md"
QA_PATH = OUT_DIR / "segment_descriptive_qa.json"

ALL_STYPES = "ALL_STYPES"

DERIVED_VARIABLES = [
    "op_margin",
    "capx_to_sales",
    "capx_to_assets",
    "rd_to_sales",
    "segment_sales_share",
    "log_sales",
]

VARIABLE_LABELS = {
    "sales": "Segment sales",
    "ops": "Segment operating profit",
    "capxs": "Segment capital expenditures",
    "ias": "Segment identifiable assets",
    "emps": "Segment employees",
    "rds": "Segment R&D",
    "ppents": "Segment PP&E",
    "op_margin": "Operating profit / sales",
    "capx_to_sales": "Capital expenditures / sales",
    "capx_to_assets": "Capital expenditures / identifiable assets",
    "rd_to_sales": "R&D / sales",
    "segment_sales_share": "Segment positive sales / firm-year-stype positive sales",
    "log_sales": "Log(1 + sales), for nonnegative sales",
}

SEGMENT_COUNT_LABELS = {
    "reported_segment_rows": "All segment rows in a firm-year-stype",
    "nonblank_named_segment_rows": "Rows with a nonblank segment name",
    "positive_sales_segment_rows": "Rows with sales greater than zero",
    "operating_candidate_segment_rows": "Rows not flagged by corporate/elimination/unallocated name patterns",
}

FIRM_YEAR_LABELS = {
    "reported_segment_rows": "All segment rows in a firm-year-stype",
    "nonblank_named_segment_rows": "Rows with a nonblank segment name",
    "positive_sales_segment_rows": "Rows with sales greater than zero",
    "operating_candidate_segment_rows": "Rows not flagged by corporate/elimination/unallocated name patterns",
    "total_positive_sales": "Sum of positive segment sales within firm-year-stype",
    "sales_hhi": "HHI of positive segment-sales shares within firm-year-stype",
    "top_segment_sales_share": "Largest positive segment-sales share within firm-year-stype",
}


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_table(df: pd.DataFrame, filename: str) -> Path:
    ensure_dirs()
    path = TABLE_DIR / filename
    df.to_csv(path, index=False)
    return path


def clean_stype(value: object) -> str:
    if pd.isna(value):
        return "MISSING_STYPE"
    text = str(value).strip()
    return text if text else "MISSING_STYPE"


def numeric(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce") if column in df.columns else pd.Series(np.nan, index=df.index)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    out = numerator / denominator
    return out.replace([np.inf, -np.inf], np.nan)


def with_segment_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    name = out["snms"].fillna("").astype(str).str.strip()
    sales = numeric(out, "sales")
    out["segment_name_clean"] = name
    out["has_nonblank_segment_name"] = name.ne("")
    out["positive_sales"] = sales.where(sales.gt(0), 0.0)
    out["has_positive_sales"] = sales.gt(0)
    out["nonop_name_flag"] = name.str.upper().str.contains(NONOP, regex=True, na=False)
    out["operating_candidate_flag"] = ~out["nonop_name_flag"]
    return out


def add_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
    out = with_segment_flags(df)
    sales = numeric(out, "sales")
    capxs = numeric(out, "capxs")
    ias = numeric(out, "ias")
    ops = numeric(out, "ops")
    rds = numeric(out, "rds")

    out["op_margin"] = safe_divide(ops, sales)
    out["capx_to_sales"] = safe_divide(capxs, sales)
    out["capx_to_assets"] = safe_divide(capxs, ias)
    out["rd_to_sales"] = safe_divide(rds, sales)
    out["log_sales"] = np.nan
    nonnegative_sales = sales.ge(0)
    out.loc[nonnegative_sales, "log_sales"] = np.log1p(sales.loc[nonnegative_sales])

    totals = out.groupby(["gvkey", "datadate", "stype"], dropna=False)["positive_sales"].transform("sum")
    out["segment_sales_share"] = safe_divide(out["positive_sales"], totals)
    return out


def variable_label_lookup() -> dict[str, str]:
    labels = dict(VARIABLE_LABELS)
    definitions = variable_dictionary()
    for _, row in definitions.iterrows():
        field = str(row["field"])
        if "," in field or "/" in field:
            continue
        labels.setdefault(field, str(row["plain_english_description"]))
    return labels


def format_round(df: pd.DataFrame, digits: int = 3) -> pd.DataFrame:
    out = df.copy()
    float_cols = out.select_dtypes(include=["float"]).columns
    out[float_cols] = out[float_cols].round(digits)
    return out


def stat_summary(values: pd.Series) -> dict[str, float | int]:
    numeric_values = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if numeric_values.empty:
        return {
            "nonmissing_n": 0,
            "mean": np.nan,
            "sd": np.nan,
            "min": np.nan,
            "p1": np.nan,
            "p25": np.nan,
            "p50": np.nan,
            "p75": np.nan,
            "p90": np.nan,
            "p95": np.nan,
            "p99": np.nan,
            "max": np.nan,
        }
    quantiles = numeric_values.quantile([0.01, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
    return {
        "nonmissing_n": int(numeric_values.shape[0]),
        "mean": float(numeric_values.mean()),
        "sd": float(numeric_values.std(ddof=1)) if numeric_values.shape[0] > 1 else 0.0,
        "min": float(numeric_values.min()),
        "p1": float(quantiles.loc[0.01]),
        "p25": float(quantiles.loc[0.25]),
        "p50": float(quantiles.loc[0.50]),
        "p75": float(quantiles.loc[0.75]),
        "p90": float(quantiles.loc[0.90]),
        "p95": float(quantiles.loc[0.95]),
        "p99": float(quantiles.loc[0.99]),
        "max": float(numeric_values.max()),
    }


def source_metrics(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for stype, part in df.groupby("stype", dropna=False):
        rows.append(
            {
                "stype": clean_stype(stype),
                f"{prefix}_rows": int(len(part)),
                f"{prefix}_firms": int(part["gvkey"].nunique(dropna=True)),
                f"{prefix}_firm_years": int(part[["gvkey", "datadate"]].drop_duplicates().shape[0]),
                f"{prefix}_min_year": int(part["year"].min()) if part["year"].notna().any() else np.nan,
                f"{prefix}_max_year": int(part["year"].max()) if part["year"].notna().any() else np.nan,
                f"{prefix}_unique_nonblank_segment_names": int(
                    part["snms"].fillna("").astype(str).str.strip().replace("", np.nan).nunique(dropna=True)
                ),
                f"{prefix}_source_currencies": int(part["isosrc"].nunique(dropna=True)),
            }
        )

    rows.append(
        {
            "stype": ALL_STYPES,
            f"{prefix}_rows": int(len(df)),
            f"{prefix}_firms": int(df["gvkey"].nunique(dropna=True)),
            f"{prefix}_firm_years": int(df[["gvkey", "datadate"]].drop_duplicates().shape[0]),
            f"{prefix}_min_year": int(df["year"].min()) if df["year"].notna().any() else np.nan,
            f"{prefix}_max_year": int(df["year"].max()) if df["year"].notna().any() else np.nan,
            f"{prefix}_unique_nonblank_segment_names": int(
                df["snms"].fillna("").astype(str).str.strip().replace("", np.nan).nunique(dropna=True)
            ),
            f"{prefix}_source_currencies": int(df["isosrc"].nunique(dropna=True)),
        }
    )
    return pd.DataFrame(rows)


def table1_source_rows(raw: pd.DataFrame, latest: pd.DataFrame) -> pd.DataFrame:
    dedup = latest_srcdate_dedup_summary(raw, latest).copy()
    dedup["stype"] = dedup["stype"].map(clean_stype)
    total = pd.DataFrame(
        [
            {
                "stype": ALL_STYPES,
                "raw_rows": int(len(raw)),
                "latest_source_rows": int(len(latest)),
                "dropped_older_srcdate_rows": int(len(raw) - len(latest)),
                "dropped_pct_of_raw": round(float((len(raw) - len(latest)) / len(raw) * 100), 1),
            }
        ]
    )
    dedup = pd.concat([dedup, total], ignore_index=True)

    raw_metrics = source_metrics(raw, "raw").drop(columns=["raw_rows"])
    latest_metrics = source_metrics(latest, "latest")
    out = (
        dedup.merge(raw_metrics, on="stype", how="left")
        .merge(latest_metrics, on="stype", how="left")
        .sort_values(["stype"], key=lambda s: s.ne(ALL_STYPES), ascending=True)
    )
    ordered = [
        "stype",
        "raw_rows",
        "latest_source_rows",
        "dropped_older_srcdate_rows",
        "dropped_pct_of_raw",
        "latest_firms",
        "latest_firm_years",
        "latest_min_year",
        "latest_max_year",
        "latest_unique_nonblank_segment_names",
        "latest_source_currencies",
        "raw_firms",
        "raw_firm_years",
    ]
    return format_round(out[ordered])


def firm_year_segment_measures(df: pd.DataFrame, view: str, include_all_stypes: bool = True) -> pd.DataFrame:
    work = with_segment_flags(df)
    rows: list[pd.DataFrame] = []

    for keys, stype_value in [
        (["gvkey", "datadate", "stype"], None),
        (["gvkey", "datadate"], ALL_STYPES),
    ]:
        if stype_value == ALL_STYPES and not include_all_stypes:
            continue

        grouped = (
            work.groupby(keys, dropna=False)
            .agg(
                reported_segment_rows=("sid", "size"),
                nonblank_named_segment_rows=("has_nonblank_segment_name", "sum"),
                positive_sales_segment_rows=("has_positive_sales", "sum"),
                operating_candidate_segment_rows=("operating_candidate_flag", "sum"),
                total_positive_sales=("positive_sales", "sum"),
            )
            .reset_index()
        )

        totals = work.groupby(keys, dropna=False)["positive_sales"].transform("sum")
        shares = safe_divide(work["positive_sales"], totals)
        share_work = work[keys].copy()
        share_work["sales_share"] = shares
        share_work["sales_share_sq"] = shares.pow(2)
        hhi = (
            share_work.groupby(keys, dropna=False)
            .agg(
                sales_hhi=("sales_share_sq", "sum"),
                top_segment_sales_share=("sales_share", "max"),
            )
            .reset_index()
        )
        grouped = grouped.merge(hhi, on=keys, how="left")
        no_positive_sales = grouped["total_positive_sales"].le(0)
        grouped.loc[no_positive_sales, ["sales_hhi", "top_segment_sales_share"]] = np.nan

        if stype_value == ALL_STYPES:
            grouped["stype"] = ALL_STYPES
        else:
            grouped["stype"] = grouped["stype"].map(clean_stype)
        grouped["view"] = view
        rows.append(grouped)

    out = pd.concat(rows, ignore_index=True)
    return out[
        [
            "view",
            "gvkey",
            "datadate",
            "stype",
            "reported_segment_rows",
            "nonblank_named_segment_rows",
            "positive_sales_segment_rows",
            "operating_candidate_segment_rows",
            "total_positive_sales",
            "sales_hhi",
            "top_segment_sales_share",
        ]
    ]


def table2_segment_count_distribution(firm_years: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    count_measures = list(SEGMENT_COUNT_LABELS)
    for (view, stype), part in firm_years.groupby(["view", "stype"], dropna=False):
        for measure in count_measures:
            stats = stat_summary(part[measure])
            rows.append(
                {
                    "view": view,
                    "stype": stype,
                    "measure": measure,
                    "plain_english_description": SEGMENT_COUNT_LABELS[measure],
                    "firm_year_units": int(len(part)),
                    "share_gt1_pct": round(float(pd.to_numeric(part[measure], errors="coerce").gt(1).mean() * 100), 1),
                    **stats,
                }
            )
    return format_round(pd.DataFrame(rows).sort_values(["view", "stype", "measure"]))


def stype_partitions(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    parts: list[tuple[str, pd.DataFrame]] = [(ALL_STYPES, df)]
    for stype, part in df.groupby("stype", dropna=False):
        parts.append((clean_stype(stype), part))
    return parts


def table3_variable_quartiles(df: pd.DataFrame, view: str) -> pd.DataFrame:
    labels = variable_label_lookup()
    work = add_derived_variables(df)
    variables = [col for col in [*PRIMARY_NUMERIC, *EXTENDED_NUMERIC, *DERIVED_VARIABLES] if col in work.columns]

    rows: list[dict[str, object]] = []
    for stype, part in stype_partitions(work):
        for variable in variables:
            series = pd.to_numeric(part[variable], errors="coerce").replace([np.inf, -np.inf], np.nan)
            stats = stat_summary(series)
            rows.append(
                {
                    "view": view,
                    "stype": stype,
                    "variable": variable,
                    "plain_english_description": labels.get(variable, variable),
                    "segment_rows": int(len(part)),
                    "missing_pct": round(float(series.isna().mean() * 100), 1) if len(part) else np.nan,
                    "zero_pct": round(float(series.eq(0).mean() * 100), 1) if len(part) else np.nan,
                    "positive_pct": round(float(series.gt(0).mean() * 100), 1) if len(part) else np.nan,
                    **stats,
                }
            )
    return format_round(pd.DataFrame(rows).sort_values(["view", "stype", "variable"]))


def table4_firm_year_distributions(firm_years: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (view, stype), part in firm_years.groupby(["view", "stype"], dropna=False):
        for measure, label in FIRM_YEAR_LABELS.items():
            series = pd.to_numeric(part[measure], errors="coerce").replace([np.inf, -np.inf], np.nan)
            stats = stat_summary(series)
            rows.append(
                {
                    "view": view,
                    "stype": stype,
                    "variable": measure,
                    "plain_english_description": label,
                    "firm_year_units": int(len(part)),
                    "missing_pct": round(float(series.isna().mean() * 100), 1) if len(part) else np.nan,
                    **stats,
                }
            )
    return format_round(pd.DataFrame(rows).sort_values(["view", "stype", "variable"]))


def table5_definitions() -> pd.DataFrame:
    definitions = coverage_definitions()
    additions = pd.DataFrame(
        [
            (
                "firm-year-stype",
                "A gvkey, datadate, and stype combination.",
                "Main unit for segment-count tables because business, geographic, and operating segment tables are overlapping reporting dimensions.",
            ),
            (
                "ALL_STYPES",
                "All segment rows pooled across stype.",
                "Included as an inventory check only. Paper tables should usually keep stype separate unless the design explicitly pools reporting dimensions.",
            ),
            (
                "nonblank segment name",
                "snms after trimming whitespace is not blank.",
                "Used so blank names do not count as named segments.",
            ),
            (
                "operating candidate segment rows",
                "Rows whose segment name does not match corporate, elimination, unallocated, reconciliation, all-other, or similar nonoperating patterns.",
                "A descriptive screen only. It is not a final sample rule.",
            ),
            (
                "segment sales share",
                "Positive segment sales divided by positive sales summed within gvkey, datadate, and stype.",
                "Used to summarize concentration and segment size. Undefined when the firm-year-stype has no positive segment sales.",
            ),
        ],
        columns=["term", "definition", "how_to_read_it"],
    )
    return pd.concat([definitions, additions], ignore_index=True)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{int(float(value)):,}"


def fmt_num(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):,.3f}"


def md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    out = df.head(max_rows).copy()
    for col in out.columns:
        if pd.api.types.is_integer_dtype(out[col]):
            out[col] = out[col].map(fmt_int)
        elif pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(fmt_num)
    out = out.fillna("").astype(str)
    headers = list(out.columns)
    rows = out.values.tolist()
    widths = [max(len(str(header)), *(len(str(row[i])) for row in rows)) for i, header in enumerate(headers)]
    header_line = "| " + " | ".join(str(header).ljust(widths[i]) for i, header in enumerate(headers)) + " |"
    separator = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = ["| " + " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)) + " |" for row in rows]
    return "\n".join([header_line, separator, *body])


def write_report(
    generated_at: str,
    raw: pd.DataFrame,
    latest: pd.DataFrame,
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    table4: pd.DataFrame,
    table_paths: list[Path],
) -> Path:
    latest_segment_counts = table2[
        (table2["view"] == "latest_source") & (table2["measure"] == "reported_segment_rows")
    ].copy()
    latest_key_variables = table3[
        (table3["view"] == "latest_source")
        & (table3["stype"].isin([ALL_STYPES, "BUSSEG", "GEOSEG", "OPSEG"]))
        & (table3["variable"].isin(["sales", "ops", "capxs", "ias", "emps", "rds", "op_margin", "capx_to_assets"]))
    ].copy()
    firm_year_preview = table4[
        (table4["view"] == "latest_source")
        & (table4["stype"].isin([ALL_STYPES, "BUSSEG", "GEOSEG", "OPSEG"]))
        & (table4["variable"].isin(["reported_segment_rows", "total_positive_sales", "sales_hhi", "top_segment_sales_share"]))
    ].copy()

    lines = [
        "# Segment Data Descriptive Tables",
        "",
        "This memo is a generated companion to the segment project-space reports. It describes the original segment source file without choosing a research design.",
        "",
        "## Source And Units",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Source file: `{rel(DATA_PATH)}`",
        f"- Source SHA-256: `{sha256_file(DATA_PATH)}`",
        f"- Raw rows: `{len(raw):,}`",
        f"- Latest-source rows: `{len(latest):,}`",
        f"- Latest-source rule: sort rows within `{', '.join(DEDUP_KEY)}` by parsed `srcdate`, then keep the last row.",
        "- Segment types are kept separate because BUSSEG, GEOSEG, and OPSEG are overlapping reporting dimensions rather than mutually exclusive samples.",
        "",
        "## Table 1. Source Rows By Segment Type",
        "",
        "This table shows how many rows are in the raw file, how many remain after the latest-source rule, and how many older source snapshots are removed.",
        "",
        md_table(table1, max_rows=12),
        "",
        "## Table 2. Segments Per Firm-Year",
        "",
        "The unit is `gvkey + datadate + stype`. The `ALL_STYPES` rows are only an inventory check because segment types overlap.",
        "",
        md_table(
            latest_segment_counts[
                [
                    "stype",
                    "measure",
                    "firm_year_units",
                    "mean",
                    "p25",
                    "p50",
                    "p75",
                    "p90",
                    "p95",
                    "max",
                    "share_gt1_pct",
                ]
            ],
            max_rows=16,
        ),
        "",
        "## Table 3. Segment-Level Variable Distributions",
        "",
        "The preview below uses latest-source rows. The full CSV includes raw-source and latest-source views, each segment type, pooled `ALL_STYPES`, raw variables, and derived ratios.",
        "",
        md_table(
            latest_key_variables[
                [
                    "stype",
                    "variable",
                    "segment_rows",
                    "nonmissing_n",
                    "missing_pct",
                    "mean",
                    "sd",
                    "p25",
                    "p50",
                    "p75",
                    "p95",
                ]
            ],
            max_rows=32,
        ),
        "",
        "## Table 4. Firm-Year Segment Structure",
        "",
        "This table summarizes firm-year-stype aggregates, including segment concentration. The full CSV includes raw-source and latest-source views.",
        "",
        md_table(
            firm_year_preview[
                [
                    "stype",
                    "variable",
                    "firm_year_units",
                    "nonmissing_n",
                    "missing_pct",
                    "mean",
                    "sd",
                    "p25",
                    "p50",
                    "p75",
                    "p95",
                ]
            ],
            max_rows=24,
        ),
        "",
        "## Generated Files",
        "",
        *[f"- `{rel(path)}`" for path in table_paths],
        "",
        "## Reading Notes",
        "",
        "- The latest-source view is the cleaner default for paper-style descriptive tables because repeated source snapshots are removed.",
        "- The raw-source view is retained for auditing the original file exactly as received.",
        "- `operating_candidate_segment_rows` is a descriptive name screen, not a final research-sample restriction.",
        "- Missingness percentages use the displayed table unit: segment rows for Table 3 and firm-year-stype rows for Table 4.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def main() -> None:
    ensure_dirs()
    generated_at = utc_now()

    raw = load_segments()
    latest = latest_srcdate_view(raw)

    firm_years = pd.concat(
        [
            firm_year_segment_measures(raw, "raw_source"),
            firm_year_segment_measures(latest, "latest_source"),
        ],
        ignore_index=True,
    )

    table1 = table1_source_rows(raw, latest)
    table2 = table2_segment_count_distribution(firm_years)
    table3 = pd.concat(
        [
            table3_variable_quartiles(raw, "raw_source"),
            table3_variable_quartiles(latest, "latest_source"),
        ],
        ignore_index=True,
    )
    table4 = table4_firm_year_distributions(firm_years)
    table5 = table5_definitions()

    outputs = [
        write_table(table1, "table1_source_rows_by_segment_type.csv"),
        write_table(table2, "table2_segments_per_firm_year_distribution.csv"),
        write_table(table3, "table3_segment_variable_quartiles.csv"),
        write_table(table4, "table4_firm_year_segment_structure.csv"),
        write_table(table5, "table5_descriptive_definitions.csv"),
    ]
    report_path = write_report(generated_at, raw, latest, table1, table2, table3, table4, outputs)

    qa = {
        "generated_at_utc": generated_at,
        "source_path": rel(DATA_PATH),
        "source_sha256": sha256_file(DATA_PATH),
        "raw_rows": int(len(raw)),
        "latest_source_rows": int(len(latest)),
        "latest_source_dedup_key": DEDUP_KEY,
        "latest_source_rule": "sort by parsed srcdate within dedup key and keep last row",
        "outputs": [rel(path) for path in [*outputs, report_path]],
        "table_row_counts": {
            "table1_source_rows_by_segment_type": int(len(table1)),
            "table2_segments_per_firm_year_distribution": int(len(table2)),
            "table3_segment_variable_quartiles": int(len(table3)),
            "table4_firm_year_segment_structure": int(len(table4)),
            "table5_descriptive_definitions": int(len(table5)),
        },
        "notes": [
            "The raw file is not mutated.",
            "The bundle includes both raw-source and latest-source views.",
            "ALL_STYPES is an inventory view because segment types are overlapping reporting dimensions.",
        ],
    }
    QA_PATH.write_text(json.dumps(qa, indent=2), encoding="utf-8")

    for path in outputs:
        print(f"wrote {rel(path)}")
    print(f"wrote {rel(report_path)}")
    print(f"wrote {rel(QA_PATH)}")


if __name__ == "__main__":
    main()
