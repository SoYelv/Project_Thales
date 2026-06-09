#!/usr/bin/env python3
"""Build data-profile tables for the segment project-space reports."""

from __future__ import annotations

import numpy as np
import pandas as pd

from segment_project_common import (
    CODE_FIELDS,
    DATA_PATH,
    EXTENDED_NUMERIC,
    PRIMARY_NUMERIC,
    ROOT,
    latest_srcdate_dedup_summary,
    latest_srcdate_view,
    load_segments,
    pct,
    sha256_file,
    utc_now,
    write_json,
    write_table,
)
from segment_project_definitions import coverage_definitions, variable_dictionary


def stype_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("stype", dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            firm_years=("datadate", lambda x: df.loc[x.index, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
            min_year=("year", "min"),
            max_year=("year", "max"),
            unique_segment_names=("snms", pd.Series.nunique),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )


def design_readiness(df: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("Segment operating margin", ["sales", "ops"], "Alpha / segment performance"),
        ("RSZ capital allocation", ["sales", "ops", "capxs", "ias"], "Internal capital allocation"),
        ("Capex-to-sales allocation", ["sales", "capxs"], "Investment intensity"),
        ("Asset allocation", ["ias", "capxs"], "Investment relative to segment assets"),
        ("Employment allocation", ["sales", "emps"], "Labor/resources"),
        ("R&D allocation", ["sales", "rds"], "Innovation/resources"),
        ("Segment granularity", ["sid"], "Information production / disclosure"),
        ("Geographic FX exposure", ["sales", "snms"], "Foreign/currency exposure"),
    ]
    rows = []
    for stype, part in df.groupby("stype", dropna=False):
        for design, cols, family in specs:
            if design == "Geographic FX exposure" and stype != "GEOSEG":
                continue
            ready = part[cols].notna().all(axis=1)
            if design == "Segment operating margin":
                ready = ready & part["sales"].ne(0)
            rows.append(
                {
                    "stype": stype,
                    "design": design,
                    "outcome_family": family,
                    "rows": int(len(part)),
                    "ready_rows": int(ready.sum()),
                    "ready_pct": pct(ready),
                    "firms_with_ready_rows": int(part.loc[ready, "gvkey"].nunique(dropna=True)),
                    "firm_years_with_ready_rows": int(part.loc[ready, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
                    "min_year": int(part.loc[ready, "year"].min()) if ready.any() else np.nan,
                    "max_year": int(part.loc[ready, "year"].max()) if ready.any() else np.nan,
                }
            )
    return pd.DataFrame(rows).sort_values(["outcome_family", "ready_rows"], ascending=[True, False])


def variable_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in [*PRIMARY_NUMERIC, *EXTENDED_NUMERIC]:
        for stype, part in df.groupby("stype", dropna=False):
            nonmissing = part[col].notna()
            numeric = pd.to_numeric(part[col], errors="coerce")
            rows.append(
                {
                    "variable": col,
                    "stype": stype,
                    "rows": int(len(part)),
                    "nonmissing_pct": pct(nonmissing),
                    "positive_pct": pct(numeric.gt(0)),
                    "firms_nonmissing": int(part.loc[nonmissing, "gvkey"].nunique(dropna=True)),
                    "firm_years_nonmissing": int(
                        part.loc[nonmissing, ["gvkey", "datadate"]].drop_duplicates().shape[0]
                    ),
                    "min_year": int(part.loc[nonmissing, "year"].min()) if nonmissing.any() else np.nan,
                    "max_year": int(part.loc[nonmissing, "year"].max()) if nonmissing.any() else np.nan,
                }
            )
    return pd.DataFrame(rows)


def code_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in CODE_FIELDS:
        for stype, part in df.groupby("stype", dropna=False):
            nonmissing = part[col].notna()
            rows.append(
                {
                    "code_field": col,
                    "stype": stype,
                    "rows": int(len(part)),
                    "nonmissing_pct": pct(nonmissing),
                    "unique_values": int(part[col].nunique(dropna=True)),
                }
            )
    return pd.DataFrame(rows)


def decade_readiness(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["decade"] = (out["year"] // 10 * 10).astype("Int64").astype(str) + "s"
    rows = []
    for (decade, stype), part in out.groupby(["decade", "stype"], dropna=False):
        margin = part[["sales", "ops"]].notna().all(axis=1) & part["sales"].ne(0)
        alloc = part[["sales", "ops", "capxs", "ias"]].notna().all(axis=1)
        rows.append(
            {
                "decade": decade,
                "stype": stype,
                "rows": int(len(part)),
                "firms": int(part["gvkey"].nunique(dropna=True)),
                "margin_ready_pct": pct(margin),
                "allocation_ready_pct": pct(alloc),
                "sales_rows": int(part["sales"].notna().sum()),
                "ops_rows": int(part["ops"].notna().sum()),
                "capxs_rows": int(part["capxs"].notna().sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["decade", "stype"])


def key_uniqueness(df: pd.DataFrame) -> pd.DataFrame:
    key_sets = [
        ("gvkey_datadate_stype_sid", ["gvkey", "datadate", "stype", "sid"]),
        ("plus_segment_name", ["gvkey", "datadate", "stype", "sid", "snms"]),
        ("plus_srcdate", ["gvkey", "datadate", "stype", "sid", "srcdate"]),
    ]
    rows = []
    for name, keys in key_sets:
        grouped = df.groupby(keys, dropna=False).size().rename("rows_per_key").reset_index()
        dup = grouped[grouped["rows_per_key"] > 1]
        rows.append(
            {
                "candidate_key": name,
                "key_columns": ", ".join(keys),
                "unique_key_count": int(len(grouped)),
                "duplicate_key_count": int(len(dup)),
                "duplicate_rows": int(dup["rows_per_key"].sum()),
                "max_rows_per_key": int(grouped["rows_per_key"].max()),
                "duplicate_row_pct": round(float(dup["rows_per_key"].sum() / len(df) * 100), 1),
            }
        )
    return pd.DataFrame(rows)


def source_metadata(raw_rows: int, latest_rows: int, generated_at: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_path": str(DATA_PATH.relative_to(ROOT)),
                "source_sha256": sha256_file(DATA_PATH),
                "generated_at_utc": generated_at,
                "raw_rows": raw_rows,
                "latest_source_rows": latest_rows,
                "dedup_key": "gvkey + datadate + stype + sid",
                "dedup_rule": "sort by srcdate_dt within dedup_key and keep last row",
            }
        ]
    )


def main() -> None:
    generated_at = utc_now()
    raw = load_segments()
    latest = latest_srcdate_view(raw)

    outputs = [
        write_table(source_metadata(len(raw), len(latest), generated_at), "segment_project_source_metadata.csv"),
        write_table(latest_srcdate_dedup_summary(raw, latest), "segment_project_latest_srcdate_dedup_summary.csv"),
        write_table(stype_summary(latest), "segment_project_stype_summary.csv"),
        write_table(design_readiness(latest), "segment_project_design_readiness.csv"),
        write_table(variable_coverage(latest), "segment_project_variable_coverage.csv"),
        write_table(code_coverage(latest), "segment_project_code_coverage.csv"),
        write_table(decade_readiness(latest), "segment_project_decade_readiness.csv"),
        write_table(key_uniqueness(raw), "segment_project_key_uniqueness.csv"),
        write_table(variable_dictionary(), "segment_project_variable_dictionary.csv"),
        write_table(coverage_definitions(), "segment_project_coverage_definitions.csv"),
    ]

    qa = {
        "generated_at_utc": generated_at,
        "source_path": str(DATA_PATH.relative_to(ROOT)),
        "source_sha256": sha256_file(DATA_PATH),
        "raw_rows": int(len(raw)),
        "latest_srcdate_rows": int(len(latest)),
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Raw segment file is read-only and not mutated.",
            "Latest-source-date deduplication keeps one row per gvkey, datadate, stype, sid key.",
        ],
    }
    write_json(qa, "segment_project_data_profile_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_data_profile_qa.json")


if __name__ == "__main__":
    main()
