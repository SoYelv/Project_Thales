#!/usr/bin/env python3
"""Candidate non-power firms with plausible electricity-derivative demand.

This is a demand proxy, not proof of contract use. Actual use should be verified
from 10-K Item 7A / derivative footnote text or contract-level disclosures.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "panel"
TABLES = ROOT / "reports" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def industry_label(sic: object) -> str:
    if pd.isna(sic):
        return "Missing SIC"
    s = int(sic)
    if s == 3334:
        return "Primary aluminum"
    if s == 2812:
        return "Alkalies/chlorine"
    if s in {2813, 2819} or 2810 <= s <= 2819:
        return "Industrial inorganic chemicals"
    if s in {3312, 3313, 3315, 3316, 3317}:
        return "Steel/electrometallurgical"
    if 3330 <= s <= 3399:
        return "Nonferrous metals"
    if s in {3241, 3274} or 3270 <= s <= 3275:
        return "Cement/lime/minerals"
    if 2610 <= s <= 2631 or 2600 <= s <= 2699:
        return "Paper and pulp"
    if s in {3211, 3221, 3229, 3231}:
        return "Glass"
    if 1000 <= s <= 1099:
        return "Metal mining"
    if 1400 <= s <= 1499:
        return "Nonmetallic mining"
    if 2820 <= s <= 2899:
        return "Other chemicals"
    if 2200 <= s <= 2299:
        return "Textiles"
    if 4900 <= s <= 4999:
        return "Utility/power/waste"
    if 2000 <= s <= 3999:
        return "Other manufacturing"
    return "Other"


def candidate_tier(max_intensity: float, mean_intensity: float) -> str:
    if max_intensity >= 6:
        return "very_high_input"
    if max_intensity >= 3:
        return "high_input"
    return "not_candidate"


def main() -> None:
    g = pd.read_parquet(PANEL / "seg_invest2.parquet")
    company = pd.read_parquet(PANEL / "company.parquet")
    firm_event = pd.read_parquet(PANEL / "firm_event.parquet")

    power_firms = set(g.loc[g.elec.eq(1), "gvkey"])
    firmyear = (
        g.drop_duplicates(["gvkey", "year"])
        [["gvkey", "year", "firm_elec_int", "n_seg_fy"]]
        .copy()
    )
    firmyear["is_power_segment_firm"] = firmyear.gvkey.isin(power_firms)

    firm = (
        firmyear[~firmyear.is_power_segment_firm]
        .groupby("gvkey")
        .agg(
            max_firm_elec_int=("firm_elec_int", "max"),
            mean_firm_elec_int=("firm_elec_int", "mean"),
            years_observed=("year", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
            high_intensity_years=("firm_elec_int", lambda x: int((x >= 3).sum())),
            very_high_intensity_years=("firm_elec_int", lambda x: int((x >= 6).sum())),
            multiseg_years=("n_seg_fy", lambda x: int((x >= 2).sum())),
        )
        .reset_index()
    )

    seg = g[~g.gvkey.isin(power_firms)].copy()
    seg["industry_label"] = seg.seg_sic.map(industry_label)
    top_segment = (
        seg.sort_values(["gvkey", "elec_int", "sales"], ascending=[True, False, False])
        .drop_duplicates("gvkey")
        [["gvkey", "seg_sic", "industry_label", "elec_int"]]
        .rename(columns={"seg_sic": "top_electricity_sic", "elec_int": "top_segment_elec_int"})
    )

    out = firm.merge(top_segment, on="gvkey", how="left")
    out = out.merge(company[["gvkey", "conm", "state", "loc", "sic"]].drop_duplicates("gvkey"), on="gvkey", how="left")
    out = out.merge(
        firm_event[["gvkey", "region", "event_year", "legacy_region", "legacy_event_year"]].drop_duplicates("gvkey"),
        on="gvkey",
        how="left",
    )
    out["candidate_tier"] = [
        candidate_tier(mx, mn)
        for mx, mn in zip(out.max_firm_elec_int, out.mean_firm_elec_int)
    ]
    out["candidate_reason"] = np.select(
        [
            out.candidate_tier.eq("very_high_input"),
            out.candidate_tier.eq("high_input"),
        ],
        [
            "Electricity-intensive non-power firm: very high input exposure proxy.",
            "Electricity-intensive non-power firm: high input exposure proxy.",
        ],
        default="Below current input-intensity candidate threshold.",
    )
    out = out[out.candidate_tier.ne("not_candidate")].copy()
    out = out.sort_values(["candidate_tier", "max_firm_elec_int", "years_observed"], ascending=[False, False, False])

    cols = [
        "gvkey", "conm", "state", "loc", "sic", "candidate_tier", "candidate_reason",
        "max_firm_elec_int", "mean_firm_elec_int", "high_intensity_years",
        "very_high_intensity_years", "years_observed", "multiseg_years",
        "top_electricity_sic", "industry_label", "top_segment_elec_int",
        "region", "event_year", "legacy_region", "legacy_event_year",
    ]
    out[cols].to_csv(TABLES / "electricity_derivative_user_candidates.csv", index=False)

    summary = (
        out.groupby(["candidate_tier", "industry_label"], dropna=False)
        .agg(
            firms=("gvkey", "nunique"),
            avg_max_elec_int=("max_firm_elec_int", "mean"),
            avg_years_observed=("years_observed", "mean"),
            firms_with_multiseg=("multiseg_years", lambda x: int((x > 0).sum())),
        )
        .reset_index()
        .sort_values(["candidate_tier", "firms"], ascending=[False, False])
    )
    summary.to_csv(TABLES / "electricity_derivative_user_candidate_summary.csv", index=False)

    print(f"wrote {len(out):,} candidate firms")
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
