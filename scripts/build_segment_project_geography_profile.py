#!/usr/bin/env python3
"""Build geography-profile tables for the segment project-space reports."""

from __future__ import annotations

import pandas as pd

from segment_project_common import ROOT, latest_srcdate_view, load_segments, pct, utc_now, write_json, write_table


def geography_readiness(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    geo = df[df["stype"].eq("GEOSEG")].copy()
    geo["decade"] = (geo["year"] // 10 * 10).astype("Int64").astype(str) + "s"
    geo["has_name"] = geo["snms"].notna() & geo["snms"].astype(str).str.strip().ne("")
    geo["has_currency"] = geo["isosrc"].notna() & geo["isosrc"].astype(str).str.strip().ne("")
    geo["non_us_currency"] = geo["has_currency"] & ~geo["isosrc"].astype(str).str.upper().isin(["USD", "US"])
    geo["margin_ready"] = geo[["sales", "ops"]].notna().all(axis=1) & geo["sales"].ne(0)
    geo["allocation_ready"] = geo[["sales", "ops", "capxs", "ias"]].notna().all(axis=1)
    decade = (
        geo.groupby("decade", dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            has_name_pct=("has_name", pct),
            has_source_currency_pct=("has_currency", pct),
            non_us_currency_pct=("non_us_currency", pct),
            sales_nonmissing_pct=("sales", lambda x: pct(x.notna())),
            margin_ready_pct=("margin_ready", pct),
            allocation_ready_pct=("allocation_ready", pct),
        )
        .reset_index()
        .sort_values("decade")
    )
    names = geo["snms"].fillna("").replace("", "[missing segment name]").value_counts().head(40).reset_index()
    names.columns = ["segment_name", "rows"]
    curr = geo["isosrc"].fillna("").replace("", "[missing source currency]").value_counts().head(40).reset_index()
    curr.columns = ["source_currency", "rows"]
    return decade, names, curr


def main() -> None:
    generated_at = utc_now()
    latest = latest_srcdate_view(load_segments())
    decade, names, currencies = geography_readiness(latest)
    outputs = [
        write_table(decade, "segment_project_geography_decade_readiness.csv"),
        write_table(names, "segment_project_top_geographic_names.csv"),
        write_table(currencies, "segment_project_top_geographic_currencies.csv"),
    ]
    qa = {
        "generated_at_utc": generated_at,
        "latest_srcdate_rows": int(len(latest)),
        "geoseg_rows": int(latest["stype"].eq("GEOSEG").sum()),
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Blank GEOSEG names are labeled [missing segment name].",
            "Geographic readiness is a disclosure screen, not a treatment assignment.",
        ],
    }
    write_json(qa, "segment_project_geography_profile_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_geography_profile_qa.json")


if __name__ == "__main__":
    main()
