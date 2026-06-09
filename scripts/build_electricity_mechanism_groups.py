#!/usr/bin/env python3
"""Build separate electricity-output and electricity-input identification groups.

The output mechanism is for electric power producers selling electricity.
The input mechanism is for non-power, electricity-intensive manufacturers or
industrial firms buying electricity as a production input. These groups are
kept mutually exclusive.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "panel"
TABLES = ROOT / "reports" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

MODERN_REGIONAL_SHOCKS = (
    ("PJM_RPM_2007", 2007, frozenset({"PA", "NJ", "MD", "DE", "DC"})),
    ("ERCOT_NODAL_2010", 2010, frozenset({"TX"})),
    ("MISO_SOUTH_2013", 2013, frozenset({"AR", "LA", "MS"})),
    ("SPP_MARKET_2014", 2014, frozenset({"KS", "OK", "NE", "SD", "ND"})),
)

EIM_SHOCKS = {
    "CA": ("CAISO_EIM_2015", 2015),
    "OR": ("CAISO_EIM_2015", 2015),
    "UT": ("CAISO_EIM_2015", 2015),
    "WY": ("CAISO_EIM_2015", 2015),
    "NV": ("CAISO_EIM_2016", 2016),
    "AZ": ("CAISO_EIM_2017", 2017),
    "WA": ("CAISO_EIM_2017", 2017),
    "ID": ("CAISO_EIM_2018", 2018),
}


def assign_modern_region(state: object) -> tuple[str, float]:
    if pd.isna(state):
        return "Other/untreated", np.nan
    st = str(state).upper()
    for name, year, states in MODERN_REGIONAL_SHOCKS:
        if st in states:
            return name, float(year)
    return "Other/untreated", np.nan


def assign_eim_region(state: object) -> tuple[str, float]:
    if pd.isna(state):
        return "Other/untreated", np.nan
    st = str(state).upper()
    name_year = EIM_SHOCKS.get(st)
    if name_year is None:
        return "Other/untreated", np.nan
    name, year = name_year
    return name, float(year)


def industry_label(sic: object) -> str:
    if pd.isna(sic):
        return "Missing SIC"
    s = int(sic)
    if s == 3334:
        return "Primary aluminum"
    if s == 2812:
        return "Alkalies/chlorine"
    if 2810 <= s <= 2819:
        return "Industrial inorganic chemicals"
    if s in {3312, 3313, 3315, 3316, 3317}:
        return "Steel/electrometallurgical"
    if 3330 <= s <= 3399:
        return "Nonferrous metals"
    if 3240 <= s <= 3275:
        return "Cement/lime/minerals"
    if 2600 <= s <= 2699:
        return "Paper and pulp"
    if s in {3211, 3221, 3229, 3231}:
        return "Glass"
    if 1000 <= s <= 1099:
        return "Metal mining"
    if 1200 <= s <= 1399:
        return "Coal/oil/gas extraction"
    if 1400 <= s <= 1499:
        return "Nonmetallic mining"
    if 2820 <= s <= 2899:
        return "Other chemicals"
    if 2000 <= s <= 3999:
        return "Other manufacturing"
    if 4900 <= s <= 4999:
        return "Utility/power/waste"
    return "Other"


def make_counts(df: pd.DataFrame, flag: str, group_label: str) -> pd.DataFrame:
    d = df[df[flag]].copy()
    rows = []
    for event_year, region in [(1996, "COB/Palo Verde"), (1998, "Cinergy/Entergy"), (1999, "PJM")]:
        part = d[d["event_year"].eq(event_year)]
        rows.append(
            {
                "mechanism_group": group_label,
                "event_year": event_year,
                "region": region,
                "role": "treated_cohort",
                "firms": int(part["gvkey"].nunique()),
                "firms_with_any_multiseg_year": int(part["has_multiseg_year"].sum()),
            }
        )
    never = d[d["event_year"].isna()]
    rows.append(
        {
            "mechanism_group": group_label,
            "event_year": np.nan,
            "region": "Other/untreated",
            "role": "never_or_unmapped_controls",
            "firms": int(never["gvkey"].nunique()),
            "firms_with_any_multiseg_year": int(never["has_multiseg_year"].sum()),
        }
    )
    return pd.DataFrame(rows)


def make_event_counts(
    df: pd.DataFrame,
    flag: str,
    group_label: str,
    event_col: str,
    region_col: str,
    design: str,
) -> pd.DataFrame:
    d = df[df[flag]].copy()
    rows = []
    events = (
        d.dropna(subset=[event_col])
        .drop_duplicates([event_col, region_col])
        .sort_values(event_col)[[event_col, region_col]]
        .itertuples(index=False, name=None)
    )
    for event_year, region in events:
        part = d[d[event_col].eq(event_year)]
        rows.append(
            {
                "design": design,
                "mechanism_group": group_label,
                "event_year": int(event_year),
                "region": region,
                "role": "treated_cohort",
                "firms": int(part["gvkey"].nunique()),
                "firms_with_any_multiseg_year": int(part["has_multiseg_year"].sum()),
            }
        )
    never = d[d[event_col].isna()]
    rows.append(
        {
            "design": design,
            "mechanism_group": group_label,
            "event_year": np.nan,
            "region": "Other/untreated",
            "role": "never_or_unmapped_controls",
            "firms": int(never["gvkey"].nunique()),
            "firms_with_any_multiseg_year": int(never["has_multiseg_year"].sum()),
        }
    )
    return pd.DataFrame(rows)


def main() -> None:
    g = pd.read_parquet(PANEL / "seg_invest2.parquet")
    company = pd.read_parquet(PANEL / "company.parquet")
    firm_event = pd.read_parquet(PANEL / "firm_event.parquet")

    power_firms = set(g.loc[g["elec"].eq(1), "gvkey"])
    firmyear = g.drop_duplicates(["gvkey", "year"])[["gvkey", "year", "firm_elec_int", "n_seg_fy"]].copy()
    firm = (
        firmyear.groupby("gvkey")
        .agg(
            max_firm_elec_int=("firm_elec_int", "max"),
            mean_firm_elec_int=("firm_elec_int", "mean"),
            years_observed=("year", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
            multiseg_years=("n_seg_fy", lambda x: int((x >= 2).sum())),
        )
        .reset_index()
    )
    firm["has_multiseg_year"] = firm["multiseg_years"].gt(0)
    firm["electricity_output_firm"] = firm["gvkey"].isin(power_firms)

    # Top electricity-intensity segment is used only to classify input users.
    top = (
        g.sort_values(["gvkey", "elec_int", "sales"], ascending=[True, False, False])
        .drop_duplicates("gvkey")
        [["gvkey", "seg_sic", "elec_int"]]
        .rename(columns={"seg_sic": "top_electricity_sic", "elec_int": "top_segment_elec_int"})
    )
    firm = firm.merge(top, on="gvkey", how="left")
    firm["top_industry_label"] = firm["top_electricity_sic"].map(industry_label)
    firm["top_is_manufacturing"] = firm["top_electricity_sic"].between(2000, 3999)
    firm["top_is_industrial"] = firm["top_electricity_sic"].between(1000, 3999)

    firm["electricity_input_mfg_high"] = (
        ~firm["electricity_output_firm"]
        & firm["top_is_manufacturing"]
        & firm["max_firm_elec_int"].ge(3)
    )
    firm["electricity_input_mfg_very_high"] = (
        ~firm["electricity_output_firm"]
        & firm["top_is_manufacturing"]
        & firm["max_firm_elec_int"].ge(6)
    )
    firm["electricity_input_industrial_high"] = (
        ~firm["electricity_output_firm"]
        & firm["top_is_industrial"]
        & firm["max_firm_elec_int"].ge(3)
    )

    cols = [
        "gvkey",
        "conm",
        "state",
        "loc",
        "sic",
        "region",
        "event_year",
        "legacy_region",
        "legacy_event_year",
        "id_tier",
    ]
    out = (
        firm.merge(company[["gvkey", "conm", "state", "loc", "sic"]].drop_duplicates("gvkey"), on="gvkey", how="left")
        .merge(
            firm_event[["gvkey", "region", "event_year", "legacy_region", "legacy_event_year", "id_tier"]].drop_duplicates("gvkey"),
            on="gvkey",
            how="left",
        )
    )
    modern = pd.DataFrame(
        out["state"].map(assign_modern_region).tolist(),
        columns=["modern_region", "modern_event_year"],
        index=out.index,
    )
    eim = pd.DataFrame(
        out["state"].map(assign_eim_region).tolist(),
        columns=["eim_region", "eim_event_year"],
        index=out.index,
    )
    out = pd.concat([out, modern, eim], axis=1)

    mechanism_cols = [
        "gvkey",
        "conm",
        "state",
        "loc",
        "sic",
        "region",
        "event_year",
        "legacy_region",
        "legacy_event_year",
        "id_tier",
        "modern_region",
        "modern_event_year",
        "eim_region",
        "eim_event_year",
        "electricity_output_firm",
        "electricity_input_mfg_high",
        "electricity_input_mfg_very_high",
        "electricity_input_industrial_high",
        "max_firm_elec_int",
        "mean_firm_elec_int",
        "years_observed",
        "first_year",
        "last_year",
        "multiseg_years",
        "has_multiseg_year",
        "top_electricity_sic",
        "top_industry_label",
        "top_segment_elec_int",
    ]
    out[mechanism_cols].to_parquet(PANEL / "electricity_mechanism_firm_event.parquet", index=False)

    output = out[out["electricity_output_firm"]].copy()
    input_main = out[out["electricity_input_mfg_high"]].copy()
    input_broad = out[out["electricity_input_industrial_high"]].copy()
    output[mechanism_cols].to_csv(TABLES / "electricity_output_firm_event.csv", index=False)
    input_main[mechanism_cols].to_csv(TABLES / "electricity_input_mfg_firm_event.csv", index=False)
    input_broad[mechanism_cols].to_csv(TABLES / "electricity_input_industrial_firm_event.csv", index=False)

    counts = pd.concat(
        [
            make_counts(out, "electricity_output_firm", "output_producer"),
            make_counts(out, "electricity_input_mfg_high", "input_manufacturing_high"),
            make_counts(out, "electricity_input_mfg_very_high", "input_manufacturing_very_high"),
            make_counts(out, "electricity_input_industrial_high", "input_industrial_high"),
        ],
        ignore_index=True,
    )
    counts.to_csv(TABLES / "electricity_output_input_group_counts.csv", index=False)

    modern_counts = pd.concat(
        [
            make_event_counts(out, "electricity_output_firm", "output_producer", "modern_event_year", "modern_region", "modern_regional"),
            make_event_counts(out, "electricity_input_mfg_high", "input_manufacturing_high", "modern_event_year", "modern_region", "modern_regional"),
            make_event_counts(out, "electricity_input_mfg_very_high", "input_manufacturing_very_high", "modern_event_year", "modern_region", "modern_regional"),
            make_event_counts(out, "electricity_input_industrial_high", "input_industrial_high", "modern_event_year", "modern_region", "modern_regional"),
            make_event_counts(out, "electricity_output_firm", "output_producer", "eim_event_year", "eim_region", "eim_staggered"),
            make_event_counts(out, "electricity_input_mfg_high", "input_manufacturing_high", "eim_event_year", "eim_region", "eim_staggered"),
            make_event_counts(out, "electricity_input_mfg_very_high", "input_manufacturing_very_high", "eim_event_year", "eim_region", "eim_staggered"),
            make_event_counts(out, "electricity_input_industrial_high", "input_industrial_high", "eim_event_year", "eim_region", "eim_staggered"),
        ],
        ignore_index=True,
    )
    modern_counts.to_csv(TABLES / "electricity_output_input_modern_group_counts.csv", index=False)

    shock_defs = pd.DataFrame(
        [
            {
                "design": "modern_regional",
                "shock": name,
                "event_year": year,
                "states": " ".join(sorted(states)),
                "interpretation": "regional market-structure / organized-market shock; can use not-yet or never controls within mechanism group",
            }
            for name, year, states in MODERN_REGIONAL_SHOCKS
        ]
        + [
            {
                "design": "eim_staggered",
                "shock": name,
                "event_year": year,
                "states": state,
                "interpretation": "CAISO EIM staggered entry proxy; can use not-yet or never controls within mechanism group",
            }
            for state, (name, year) in sorted(EIM_SHOCKS.items())
        ]
        + [
            {
                "design": "exploratory_national_break",
                "shock": "NODAL_EXCHANGE_2009",
                "event_year": 2009,
                "states": "national",
                "interpretation": "national period break; no clean within-mechanism regional control",
            },
            {
                "design": "exploratory_national_break",
                "shock": "CME_POWER_EXPANSION_2012",
                "event_year": 2012,
                "states": "national",
                "interpretation": "national period break; no clean within-mechanism regional control",
            },
        ]
    )
    shock_defs.to_csv(TABLES / "electricity_modern_shock_definitions.csv", index=False)

    industry_counts = (
        input_main.groupby(["top_industry_label"], dropna=False)
        .agg(
            firms=("gvkey", "nunique"),
            treated_strict_state_firms=("event_year", lambda s: int(s.notna().sum())),
            any_multiseg_firms=("has_multiseg_year", "sum"),
            avg_max_firm_elec_int=("max_firm_elec_int", "mean"),
        )
        .reset_index()
        .sort_values("firms", ascending=False)
    )
    industry_counts.to_csv(TABLES / "electricity_input_mfg_industry_counts.csv", index=False)

    qa = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "seg_invest2": relpath(PANEL / "seg_invest2.parquet"),
            "company": relpath(PANEL / "company.parquet"),
            "firm_event": relpath(PANEL / "firm_event.parquet"),
        },
        "outputs": {
            "mechanism_firm_event": relpath(PANEL / "electricity_mechanism_firm_event.parquet"),
            "output_firm_event_csv": relpath(TABLES / "electricity_output_firm_event.csv"),
            "input_mfg_firm_event_csv": relpath(TABLES / "electricity_input_mfg_firm_event.csv"),
            "input_industrial_firm_event_csv": relpath(TABLES / "electricity_input_industrial_firm_event.csv"),
            "group_counts": relpath(TABLES / "electricity_output_input_group_counts.csv"),
            "modern_group_counts": relpath(TABLES / "electricity_output_input_modern_group_counts.csv"),
            "modern_shock_definitions": relpath(TABLES / "electricity_modern_shock_definitions.csv"),
            "input_mfg_industry_counts": relpath(TABLES / "electricity_input_mfg_industry_counts.csv"),
        },
        "definitions": {
            "output_producer": "Firm ever has an electric-power operating segment in seg_invest2.elec.",
            "input_manufacturing_high": "Non-output firm whose top electricity-intensity segment SIC is 2000-3999 and whose max firm-year electricity input intensity is at least 3%.",
            "input_manufacturing_very_high": "Same as input_manufacturing_high but max intensity is at least 6%.",
            "input_industrial_high": "Non-output firm whose top electricity-intensity segment SIC is 1000-3999 and whose max firm-year electricity input intensity is at least 3%.",
            "event_assignment": "Strict 1996/1998/1999 HQ-state hub mapping from firm_event.parquet.",
            "modern_regional_assignment": "PJM RPM 2007, ERCOT nodal 2010, MISO South 2013, and SPP Integrated Marketplace 2014 HQ-state proxies.",
            "eim_assignment": "CAISO EIM staggered entry by state, 2015-2018.",
        },
        "counts": {
            "all_firms_in_segment_panel": int(out["gvkey"].nunique()),
            "output_producer_firms": int(output["gvkey"].nunique()),
            "input_mfg_high_firms": int(input_main["gvkey"].nunique()),
            "input_mfg_very_high_firms": int(out["electricity_input_mfg_very_high"].sum()),
            "input_industrial_high_firms": int(input_broad["gvkey"].nunique()),
        },
    }
    (TABLES / "electricity_output_input_group_qa.json").write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")

    print("wrote electricity mechanism firm-event split")
    print(counts.to_string(index=False))
    print("\nModern / EIM counts:")
    print(modern_counts.to_string(index=False))
    print("\nInput manufacturing high industries:")
    print(industry_counts.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
