#!/usr/bin/env python3
"""Modern 2000+/2010+ electricity shocks by output/input mechanism group.

Regional designs use within-mechanism not-yet/never controls. National breaks
are reported separately as exploratory period breaks because they do not have a
clean regional control pool.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from electricity_identification import add_sgrow, winsorize_in_place

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "panel"
TABLES = ROOT / "reports" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

GROUPS = [
    ("output_producer", "electricity_output_firm"),
    ("input_manufacturing_high", "electricity_input_mfg_high"),
    ("input_manufacturing_very_high", "electricity_input_mfg_very_high"),
    ("input_industrial_high", "electricity_input_industrial_high"),
]

NATIONAL_BREAKS = [
    ("NODAL_EXCHANGE_2009", 2009, 2004, 2014),
    ("CME_POWER_EXPANSION_2012", 2012, 2007, 2017),
]


def fit_rsz(d: pd.DataFrame, opp: str) -> dict[str, object]:
    d = d.dropna(subset=["inv_la", opp, "T", "post"]).copy()
    if len(d) < 500 or d["gvkey"].nunique() < 30:
        return {"status": "too_few_rows"}
    obs = d.groupby(["cohort", "gvkey", "year"])["snms_u"].transform("nunique")
    d = d[obs >= 2].copy()
    if d.empty:
        return {"status": "too_few_multiseg_obs"}
    winsorize_in_place(d, ["inv_la", opp])
    d["rel_inv"] = d["inv_la"] - d.groupby(["cohort", "gvkey", "year"])["inv_la"].transform("mean")
    d["rel_opp"] = d[opp] - d.groupby(["cohort", "gvkey", "year"])[opp].transform("mean")
    d["ro"] = d["rel_opp"]
    d["rop"] = d["ro"] * d["post"]
    d["roT"] = d["ro"] * d["T"]
    d["roTp"] = d["ro"] * d["T"] * d["post"]
    d["cseg"] = d["cohort"].astype(str) + "_" + d["gvkey"].astype(str) + "_" + d["snms_u"].astype(str)
    d["cy"] = d["cohort"].astype(str) + "_" + d["year"].astype(str)
    cy = pd.get_dummies(d["cy"], prefix="cy", drop_first=True).astype(float)
    idx = pd.MultiIndex.from_arrays([d["cseg"].values, d["year"].values])
    x = pd.concat([d[["roTp", "rop", "roT", "ro"]].reset_index(drop=True), cy.reset_index(drop=True)], axis=1)
    x.index = idx
    y = pd.Series(d["rel_inv"].values, index=idx)
    clusters = pd.DataFrame({"firm": d["gvkey"].values}, index=idx)
    try:
        r = PanelOLS(y, x, entity_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", clusters=clusters
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": f"fit_error:{type(exc).__name__}"}
    try:
        coef = float(r.params["roTp"])
        se = float(r.std_errors["roTp"])
        t = float(r.tstats["roTp"])
        p = float(r.pvalues["roTp"])
    except Exception as exc:  # noqa: BLE001
        return {"status": f"cov_error:{type(exc).__name__}"}
    return {
        "status": "ok",
        "coef": coef,
        "se": se,
        "t": t,
        "p": p,
        "nobs": int(r.nobs),
        "firms_in_estimation": int(d["gvkey"].nunique()),
        "treated_firms_in_stack": int(d.loc[d["T"].abs() > 1e-12, "gvkey"].nunique()),
        "control_firms_in_stack": int(d.loc[d["T"].abs() <= 1e-12, "gvkey"].nunique()),
    }


def stacked_regional(
    g: pd.DataFrame,
    fe: pd.DataFrame,
    flag: str,
    event_col: str,
    region_col: str,
    *,
    span: int = 5,
    post_lag: int = 1,
    sample: str = "all_multiseg",
) -> pd.DataFrame:
    fe_group = fe[fe[flag]].drop_duplicates("gvkey").copy()
    event_years = sorted(int(x) for x in fe_group[event_col].dropna().unique())
    parts = []
    for event_year in event_years:
        treated = set(fe_group.loc[fe_group[event_col].eq(event_year), "gvkey"])
        controls = set(fe_group.loc[fe_group[event_col].gt(event_year) | fe_group[event_col].isna(), "gvkey"])
        firms = treated | controls
        d = g[g["year"].between(event_year - span, event_year + span) & g["gvkey"].isin(firms)].copy()
        if sample == "pre_multiseg":
            pre = g[g["year"].between(event_year - span, event_year - 1) & g["gvkey"].isin(firms)]
            keep = set(pre.groupby("gvkey")["n_seg_fy"].max().loc[lambda s: s >= 2].index)
            d = d[d["gvkey"].isin(keep)].copy()
        d = d[d["n_seg_fy"] >= 2].copy()
        d["cohort"] = event_year
        d["shock_region"] = fe_group.loc[fe_group[event_col].eq(event_year), region_col].iloc[0]
        d["T"] = d["gvkey"].isin(treated).astype(float)
        d["post"] = (d["year"] >= event_year + post_lag).astype(int)
        parts.append(d)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def national_break(
    g: pd.DataFrame,
    fe: pd.DataFrame,
    flag: str,
    shock: str,
    event_year: int,
    lo: int,
    hi: int,
    *,
    sample: str = "all_multiseg",
) -> pd.DataFrame:
    # Exploratory: compare mechanism group to all other non-group firms in the
    # same period. This is not a clean within-mechanism treated/control design.
    group_firms = set(fe.loc[fe[flag], "gvkey"])
    d = g[g["year"].between(lo, hi)].copy()
    if sample == "pre_multiseg":
        pre = g[g["year"].between(lo, event_year - 1)]
        keep = set(pre.groupby("gvkey")["n_seg_fy"].max().loc[lambda s: s >= 2].index)
        d = d[d["gvkey"].isin(keep)].copy()
    d = d[d["n_seg_fy"] >= 2].copy()
    d["cohort"] = event_year
    d["shock_region"] = "national"
    d["T"] = d["gvkey"].isin(group_firms).astype(float)
    d["post"] = (d["year"] >= event_year).astype(int)
    d["shock"] = shock
    return d


def run_design(g: pd.DataFrame, fe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, flag in GROUPS:
        for design, event_col, region_col in [
            ("modern_regional", "modern_event_year", "modern_region"),
            ("eim_staggered", "eim_event_year", "eim_region"),
        ]:
            for sample in ["all_multiseg", "pre_multiseg"]:
                d = stacked_regional(g, fe, flag, event_col, region_col, sample=sample)
                for opp in ["l_margin", "sgrow"]:
                    res = fit_rsz(d, opp)
                    rows.append(
                        {
                            "design": design,
                            "shock": "stacked",
                            "mechanism_group": group_name,
                            "sample": sample,
                            "opportunity": opp,
                            "post_lag": 1,
                            "control": "notyet_or_never_within_mechanism",
                            **res,
                        }
                    )
        for shock, event_year, lo, hi in NATIONAL_BREAKS:
            for sample in ["all_multiseg", "pre_multiseg"]:
                d = national_break(g, fe, flag, shock, event_year, lo, hi, sample=sample)
                for opp in ["l_margin", "sgrow"]:
                    res = fit_rsz(d, opp)
                    rows.append(
                        {
                            "design": "exploratory_national_break",
                            "shock": shock,
                            "mechanism_group": group_name,
                            "sample": sample,
                            "opportunity": opp,
                            "post_lag": 0,
                            "control": "all_other_multiseg_firms_not_same_mechanism",
                            **res,
                        }
                    )
    return pd.DataFrame(rows)


def main() -> None:
    g = pd.read_parquet(PANEL / "seg_invest2.parquet")
    fe = pd.read_parquet(PANEL / "electricity_mechanism_firm_event.parquet")
    g = add_sgrow(g)
    out = run_design(g, fe)
    out.to_csv(TABLES / "electricity_output_input_modern_rsz_results.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
