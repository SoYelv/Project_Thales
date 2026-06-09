#!/usr/bin/env python3
"""Build exposure-profile tables for the segment project-space reports."""

from __future__ import annotations

import pandas as pd

from segment_project_common import (
    EXPOSURE_FAMILIES,
    NONOP,
    ROOT,
    latest_srcdate_view,
    load_segments,
    pct,
    utc_now,
    write_json,
    write_table,
)
from segment_project_definitions import exposure_definitions


def exposure_family_readiness(df: pd.DataFrame) -> pd.DataFrame:
    work = df[df["stype"].isin(["BUSSEG", "OPSEG"])].copy()
    rows = []
    for family in EXPOSURE_FAMILIES:
        part = work[work[family].eq(1)]
        margin = part[["sales", "ops"]].notna().all(axis=1) & part["sales"].ne(0)
        alloc = part[["sales", "ops", "capxs", "ias"]].notna().all(axis=1)
        rows.append(
            {
                "exposure_family": family,
                "rows": int(len(part)),
                "firms": int(part["gvkey"].nunique(dropna=True)),
                "firm_years": int(part[["gvkey", "datadate"]].drop_duplicates().shape[0]),
                "min_year": int(part["year"].min()) if len(part) else pd.NA,
                "max_year": int(part["year"].max()) if len(part) else pd.NA,
                "margin_ready_pct": pct(margin),
                "allocation_ready_pct": pct(alloc),
                "busseg_rows": int(part["stype"].eq("BUSSEG").sum()),
                "opseg_rows": int(part["stype"].eq("OPSEG").sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("firm_years", ascending=False)


def segment_name_keyword_readiness(df: pd.DataFrame) -> pd.DataFrame:
    name = df["snms"].fillna("").astype(str).str.upper()
    groups = {
        "corporate_or_unallocated": NONOP.pattern,
        "electric_power": r"ELECTRIC|POWER|UTILITY|UTILITIES",
        "oil_gas_petroleum": r"OIL|GAS|PETROLEUM|REFIN",
        "foreign_or_international": r"FOREIGN|INTERNATIONAL|EUROPE|ASIA|CANADA|CHINA|JAPAN|LATIN",
        "metals_or_mining": r"METAL|MINING|STEEL|ALUMIN|COPPER",
        "transport_or_freight": r"TRANSPORT|FREIGHT|AIRLINE|RAIL|SHIPPING|LOGISTICS",
        "manufacturing_inputs": r"CHEMICAL|PAPER|PULP|CEMENT|GLASS|MINERAL",
    }
    rows = []
    for group, pattern in groups.items():
        mask = name.str.contains(pattern, regex=True)
        part = df[mask]
        margin = part[["sales", "ops"]].notna().all(axis=1) & part["sales"].ne(0)
        alloc = part[["sales", "ops", "capxs", "ias"]].notna().all(axis=1)
        rows.append(
            {
                "name_keyword_group": group,
                "rows": int(len(part)),
                "firms": int(part["gvkey"].nunique(dropna=True)),
                "firm_years": int(part[["gvkey", "datadate"]].drop_duplicates().shape[0]),
                "share_of_all_rows_pct": round(float(len(part) / len(df) * 100), 1),
                "margin_ready_pct": pct(margin),
                "allocation_ready_pct": pct(alloc),
            }
        )
    return pd.DataFrame(rows).sort_values("rows", ascending=False)


def main() -> None:
    generated_at = utc_now()
    latest = latest_srcdate_view(load_segments())
    outputs = [
        write_table(exposure_definitions(), "segment_project_exposure_definitions.csv"),
        write_table(exposure_family_readiness(latest), "segment_project_exposure_family_readiness.csv"),
        write_table(segment_name_keyword_readiness(latest), "segment_project_name_keyword_readiness.csv"),
    ]
    qa = {
        "generated_at_utc": generated_at,
        "latest_srcdate_rows": int(len(latest)),
        "exposure_families": EXPOSURE_FAMILIES,
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Exposure fields are current screening proxies for coverage exploration.",
            "seg_sic is first nonmissing sics1, sics2, then firm-level sic.",
        ],
    }
    write_json(qa, "segment_project_exposure_profile_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_exposure_profile_qa.json")


if __name__ == "__main__":
    main()
