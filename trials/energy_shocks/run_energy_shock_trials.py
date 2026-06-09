#!/usr/bin/env python3
"""Trial-only scan of oil, gas, and carbon/emissions shock candidates.

This script deliberately writes only inside trials/energy_shocks. It is a
screening tool, not a production result generator.
"""
from __future__ import annotations

import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
TRIAL = Path(__file__).resolve().parent
PANEL = ROOT / "reports" / "panel"


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


@dataclass(frozen=True)
class Shock:
    name: str
    family: str
    year: int
    base_span: int
    design: str
    states: frozenset[str] = frozenset()
    post_start: int | None = None
    note: str = ""

    def window(self, span: int | None = None) -> tuple[int, int]:
        s = self.base_span if span is None else span
        return self.year - s, self.year + s


SHOCKS = [
    Shock(
        "WTI_1983",
        "oil",
        1983,
        5,
        "national",
        note="NYMEX WTI crude oil futures launch; treated exposure is oil/gas SIC proxy.",
    ),
    Shock(
        "OIL_COLLAPSE_1986",
        "oil",
        1986,
        5,
        "national",
        note="Exploratory oil price-collapse shock; not a derivative-availability event.",
    ),
    Shock(
        "NATGAS_1990",
        "gas",
        1990,
        5,
        "national",
        note="NYMEX natural gas futures launch; treated exposure is gas/oilgas/energy SIC proxy.",
    ),
    Shock(
        "FERC636_1992",
        "gas",
        1992,
        5,
        "national",
        note="Gas open-access/unbundling restructuring check; not a pure derivative launch.",
    ),
    Shock(
        "SO2_ALLOWANCE_1995",
        "carbon",
        1995,
        5,
        "national",
        note="Exploratory emissions-market analog: Acid Rain Program SO2 allowance compliance start, not CO2 carbon.",
    ),
    Shock(
        "GAS_SPIKE_2001",
        "gas",
        2001,
        5,
        "national",
        note="Exploratory natural-gas price-spike shock; not a derivative-availability event.",
    ),
    Shock(
        "EU_ETS_2005",
        "carbon",
        2005,
        5,
        "national",
        note="Exploratory high-carbon period proxy for EU ETS start; current data lacks facility/allowance exposure.",
    ),
    Shock(
        "RGGI_2009",
        "carbon",
        2009,
        5,
        "regional",
        frozenset({"CT", "DE", "ME", "MD", "MA", "NH", "NJ", "NY", "RI", "VT"}),
        note="RGGI compliance-period shock using HQ-state membership and high-carbon SIC exposure.",
    ),
    Shock(
        "CA_CARBON_2013",
        "carbon",
        2013,
        5,
        "regional",
        frozenset({"CA"}),
        note="California cap-and-trade compliance-period shock using HQ-state and high-carbon SIC exposure.",
    ),
]

STACKED_CARBON = Shock(
    "CARBON_STACK_2009_2013",
    "carbon",
    2009,
    5,
    "stacked_regional",
    note="Stacked RGGI 2009 and California 2013 regional carbon trial.",
)

CARBON_COHORTS = [
    ("RGGI", 2009, frozenset({"CT", "DE", "ME", "MD", "MA", "NH", "NJ", "NY", "RI", "VT"})),
    ("CA", 2013, frozenset({"CA"})),
]

SPAN_GRID = [3, 5, 7]
SAMPLES = ["all_multiseg", "pre_multiseg"]
OPP_COLS = ["l_margin", "sgrow"]
FIRM_OUTCOMES = ["n_op_seg", "log_nseg", "hhi", "nonop_sales_share", "multi_seg"]


def finite(s: pd.Series) -> pd.Series:
    return s.replace([np.inf, -np.inf], np.nan)


def zscore(s: pd.Series) -> pd.Series:
    s = finite(s)
    sd = s.std()
    if sd == 0 or pd.isna(sd):
        return s * np.nan
    return (s - s.mean()) / sd


def exposure_flags(sic: object) -> dict[str, int]:
    if pd.isna(sic):
        return {"seg_gas": 0, "seg_oilgas": 0, "seg_utility": 0, "seg_energy_trial": 0}
    try:
        s = int(float(sic))
    except (TypeError, ValueError):
        return {"seg_gas": 0, "seg_oilgas": 0, "seg_utility": 0, "seg_energy_trial": 0}
    gas = int(4920 <= s <= 4925)
    oilgas = int(s == 1311 or 1380 <= s <= 1389 or s == 2911 or 4610 <= s <= 4619)
    utility = int(4900 <= s <= 4999)
    return {
        "seg_gas": gas,
        "seg_oilgas": oilgas,
        "seg_utility": utility,
        "seg_energy_trial": int(bool(gas or oilgas or utility)),
    }


def carbon_heavy_sic(sic: object) -> int:
    """Exploratory high-emissions proxy from segment SIC."""
    if pd.isna(sic):
        return 0
    try:
        s = int(float(sic))
    except (TypeError, ValueError):
        return 0
    ranges = [
        (1000, 1499),   # mining, coal, oil/gas extraction
        (2610, 2631),   # pulp and paper mills
        (2810, 2899),   # industrial chemicals
        (2900, 2999),   # petroleum refining
        (3240, 3275),   # cement, lime, mineral products
        (3310, 3399),   # primary metals
        (4900, 4999),   # utilities
    ]
    return int(any(lo <= s <= hi for lo, hi in ranges))


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    g = pd.read_parquet(PANEL / "seg_invest2.parquet")
    reg = pd.read_parquet(PANEL / "regdata.parquet")
    company = pd.read_parquet(PANEL / "company.parquet")
    state = (
        company[["gvkey", "state"]]
        .dropna(subset=["gvkey"])
        .drop_duplicates("gvkey")
        .assign(state=lambda d: d["state"].astype(str).str.upper())
    )

    g = g.merge(state, on="gvkey", how="left")
    reg = reg.drop(columns=["state"], errors="ignore").merge(state, on="gvkey", how="left")

    flags = g["seg_sic"].map(exposure_flags).apply(pd.Series)
    g = pd.concat([g, flags], axis=1)
    g["seg_carbon"] = g["seg_sic"].map(carbon_heavy_sic).astype(int)
    g["seg_elec_trial"] = g["elec"].fillna(0).astype(int)
    g["seg_energy_trial"] = np.maximum(g["seg_energy_trial"], g["energy"].fillna(0).astype(int))
    g["sales_pos"] = g["sales"].fillna(0).clip(lower=0)

    carbon_sales = (
        g.assign(v=lambda d: d["sales_pos"] * d["seg_carbon"])
        .groupby(["gvkey", "year"], as_index=False)
        .agg(carbon_sales=("v", "sum"), op_sales=("sales_pos", "sum"))
    )
    carbon_sales["share_carbon"] = np.where(
        carbon_sales["op_sales"] > 0,
        carbon_sales["carbon_sales"] / carbon_sales["op_sales"],
        0.0,
    )
    reg = reg.merge(carbon_sales[["gvkey", "year", "share_carbon"]], on=["gvkey", "year"], how="left")
    reg["share_carbon"] = reg["share_carbon"].fillna(0.0)
    reg["log_nseg"] = np.log1p(reg["n_op_seg"])

    for c in ["inv_la", "l_margin", "sgrow", "firm_elec_int"]:
        if c in g:
            g[c] = finite(g[c])
    for c in ["lev", "roa", "capx_at", "cash_at", "logat"]:
        if c in reg:
            reg[c] = finite(reg[c])
    reg["lev"] = reg["lev"].clip(0, 5)

    qa = {
        "inputs": {
            "seg_invest2": relpath(PANEL / "seg_invest2.parquet"),
            "regdata": relpath(PANEL / "regdata.parquet"),
            "company": relpath(PANEL / "company.parquet"),
        },
        "segment_rows": int(len(g)),
        "segment_firms": int(g["gvkey"].nunique()),
        "segment_year_min": int(g["year"].min()),
        "segment_year_max": int(g["year"].max()),
        "firmyear_rows": int(len(reg)),
        "firmyear_firms": int(reg["gvkey"].nunique()),
        "firmyear_year_min": int(reg["year"].min()),
        "firmyear_year_max": int(reg["year"].max()),
        "exposure_counts_segment_years": {
            "seg_oilgas": int(g["seg_oilgas"].sum()),
            "seg_gas": int(g["seg_gas"].sum()),
            "seg_energy_trial": int(g["seg_energy_trial"].sum()),
            "seg_carbon": int(g["seg_carbon"].sum()),
        },
    }
    return g, reg, qa


def pre_exposure(
    reg: pd.DataFrame,
    event_year: int,
    lo: int,
    source_col: str,
    *,
    threshold: float = 0.0,
    high: bool = False,
) -> pd.Series:
    pre = reg[reg["year"].between(lo, event_year - 1)].copy()
    if pre.empty:
        return pd.Series(dtype=float, name="T")
    agg = pre.groupby("gvkey")[source_col].mean()
    if high:
        out = (agg >= threshold).astype(float)
    else:
        out = (pre.groupby("gvkey")[source_col].max() > threshold).astype(float)
    out.name = "T"
    return out


def continuous_pre_exposure(reg: pd.DataFrame, event_year: int, lo: int, source_col: str) -> pd.Series:
    pre = reg[reg["year"].between(lo, event_year - 1)].copy()
    if pre.empty:
        return pd.Series(dtype=float, name="T")
    out = zscore(pre.groupby("gvkey")[source_col].mean())
    out.name = "T"
    return out


def build_rsz_data(
    g: pd.DataFrame,
    reg: pd.DataFrame,
    shock: Shock,
    treatment: dict[str, object],
    span: int,
    sample: str,
) -> pd.DataFrame:
    lo, hi = shock.window(span)
    gg = g[g["year"].between(lo, hi) & (g["n_seg_fy"] >= 2)].copy()
    gg["cohort"] = shock.year
    gg["post"] = (gg["year"] >= (shock.post_start or shock.year)).astype(int)

    if sample == "pre_multiseg":
        pre_multi = set(
            g[g["year"].between(lo, shock.year - 1)]
            .groupby("gvkey")["n_seg_fy"]
            .max()
            .loc[lambda s: s >= 2]
            .index
        )
        gg = gg[gg["gvkey"].isin(pre_multi)].copy()

    if shock.design == "regional":
        region = gg["state"].isin(shock.states).astype(float)
        gg["region_treat"] = region
    else:
        gg["region_treat"] = 1.0

    scope = str(treatment["scope"])
    col = str(treatment["col"])
    if scope == "segment":
        gg["T"] = gg[col].fillna(0).astype(float) * gg["region_treat"]
    elif scope == "firm_pre_binary":
        threshold = float(treatment.get("threshold", 0.0))
        high = bool(treatment.get("high", False))
        t = pre_exposure(reg, shock.year, lo, col, threshold=threshold, high=high)
        gg = gg.merge(t.reset_index(), on="gvkey", how="left")
        gg["T"] = gg["T"].fillna(0.0) * gg["region_treat"]
    elif scope == "firm_pre_continuous":
        t = continuous_pre_exposure(reg, shock.year, lo, col)
        gg = gg.merge(t.reset_index(), on="gvkey", how="left")
        gg["T"] = gg["T"].fillna(0.0) * gg["region_treat"]
    else:
        raise ValueError(f"unknown treatment scope: {scope}")
    return gg


def build_stacked_carbon(
    g: pd.DataFrame,
    reg: pd.DataFrame,
    treatment: dict[str, object],
    span: int,
    sample: str,
) -> pd.DataFrame:
    state_event = {state: year for _, year, states in CARBON_COHORTS for state in states}
    parts = []
    for cohort_name, event_year, states in CARBON_COHORTS:
        lo, hi = event_year - span, event_year + span
        part = g[g["year"].between(lo, hi) & (g["n_seg_fy"] >= 2)].copy()
        if sample == "pre_multiseg":
            pre_multi = set(
                g[g["year"].between(lo, event_year - 1)]
                .groupby("gvkey")["n_seg_fy"]
                .max()
                .loc[lambda s: s >= 2]
                .index
            )
            part = part[part["gvkey"].isin(pre_multi)].copy()
        event_for_state = part["state"].map(state_event)
        eligible = event_for_state.isna() | (event_for_state >= event_year)
        part = part[eligible].copy()
        part["cohort"] = event_year
        part["cohort_name"] = cohort_name
        part["post"] = (part["year"] >= event_year).astype(int)
        part["region_treat"] = part["state"].isin(states).astype(float)
        col = str(treatment["col"])
        scope = str(treatment["scope"])
        if scope == "segment":
            part["T"] = part[col].fillna(0).astype(float) * part["region_treat"]
        elif scope == "firm_pre_binary":
            threshold = float(treatment.get("threshold", 0.0))
            high = bool(treatment.get("high", False))
            t = pre_exposure(reg, event_year, lo, col, threshold=threshold, high=high)
            part = part.merge(t.reset_index(), on="gvkey", how="left")
            part["T"] = part["T"].fillna(0.0) * part["region_treat"]
        elif scope == "firm_pre_continuous":
            t = continuous_pre_exposure(reg, event_year, lo, col)
            part = part.merge(t.reset_index(), on="gvkey", how="left")
            part["T"] = part["T"].fillna(0.0) * part["region_treat"]
        else:
            raise ValueError(f"unknown treatment scope: {scope}")
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def fit_rsz(d: pd.DataFrame, opp: str) -> dict[str, object]:
    d = d.dropna(subset=["inv_la", opp, "T", "post", "cohort"]).copy()
    if len(d) < 500:
        return {"status": "too_few_rows"}
    obs_per_firmyear = d.groupby(["cohort", "gvkey", "year"])["snms_u"].transform("nunique")
    d = d[obs_per_firmyear >= 2].copy()
    if d["gvkey"].nunique() < 30 or (d["T"].abs() > 1e-12).sum() == 0:
        return {"status": "too_few_firms_or_no_treat"}

    for c in ["inv_la", opp]:
        qlo, qhi = d[c].quantile(0.01), d[c].quantile(0.99)
        d[c] = d[c].clip(qlo, qhi)

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
    x = pd.concat(
        [d[["roTp", "rop", "roT", "ro"]].reset_index(drop=True), cy.reset_index(drop=True)],
        axis=1,
    )
    x.index = idx
    y = pd.Series(d["rel_inv"].values, index=idx)
    clusters = pd.DataFrame({"firm": d["gvkey"].values}, index=idx)

    try:
        res = PanelOLS(y, x, entity_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", clusters=clusters
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": f"fit_error:{type(exc).__name__}"}

    active = d.loc[d["T"].abs() > 1e-12, "gvkey"].nunique()
    inactive = d.loc[d["T"].abs() <= 1e-12, "gvkey"].nunique()
    return {
        "status": "ok",
        "beta": float(res.params.get("roTp", np.nan)),
        "se": float(res.std_errors.get("roTp", np.nan)),
        "t": float(res.tstats.get("roTp", np.nan)),
        "p": float(res.pvalues.get("roTp", np.nan)),
        "nobs": int(res.nobs),
        "firms": int(d["gvkey"].nunique()),
        "treated_firms": int(active),
        "control_firms": int(inactive),
        "rows": int(len(d)),
    }


def treatment_grid(shock: Shock) -> list[dict[str, object]]:
    common = {
        "oil": [
            ("seg_oilgas", "segment", "oilgas_segment"),
            ("share_oilgas", "firm_pre_binary", "pre_oilgas_any"),
            ("share_oilgas", "firm_pre_continuous", "pre_oilgas_share_z"),
            ("share_energy", "firm_pre_binary", "pre_energy_any"),
        ],
        "gas": [
            ("seg_gas", "segment", "gas_segment"),
            ("seg_oilgas", "segment", "oilgas_segment"),
            ("seg_energy_trial", "segment", "energy_segment"),
            ("share_gas", "firm_pre_binary", "pre_gas_any"),
            ("share_oilgas", "firm_pre_binary", "pre_oilgas_any"),
            ("share_energy", "firm_pre_binary", "pre_energy_any"),
            ("share_energy", "firm_pre_continuous", "pre_energy_share_z"),
        ],
        "carbon": [
            ("seg_carbon", "segment", "carbon_segment"),
            ("share_carbon", "firm_pre_binary", "pre_carbon_any"),
            ("share_carbon", "firm_pre_binary", "pre_carbon_high25"),
            ("share_carbon", "firm_pre_continuous", "pre_carbon_share_z"),
            ("share_energy", "firm_pre_binary", "pre_energy_any"),
            ("share_electric", "firm_pre_binary", "pre_electric_any"),
        ],
    }
    out = []
    for col, scope, name in common[shock.family]:
        spec: dict[str, object] = {"col": col, "scope": scope, "name": name}
        if name == "pre_carbon_high25":
            spec["threshold"] = 0.25
            spec["high"] = True
        out.append(spec)
    return out


def run_rsz_grid(g: pd.DataFrame, reg: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    shock_list = SHOCKS + [STACKED_CARBON]
    for shock in shock_list:
        for treatment in treatment_grid(shock):
            for span in SPAN_GRID:
                for sample in SAMPLES:
                    if shock.design == "stacked_regional":
                        base = build_stacked_carbon(g, reg, treatment, span, sample)
                    else:
                        base = build_rsz_data(g, reg, shock, treatment, span, sample)
                    for opp in OPP_COLS:
                        res = fit_rsz(base, opp)
                        row = {
                            "model": "rsz",
                            "shock": shock.name,
                            "family": shock.family,
                            "design": shock.design,
                            "event_year": shock.year,
                            "span": span,
                            "window_start": int(shock.year - span),
                            "window_end": int(shock.year + span),
                            "sample": sample,
                            "outcome": "rel_inv",
                            "opp": opp,
                            "treatment": treatment["name"],
                            "treatment_col": treatment["col"],
                            "treatment_scope": treatment["scope"],
                            "note": shock.note,
                        }
                        row.update(res)
                        rows.append(row)
    return rows


def build_firm_did_data(
    reg: pd.DataFrame,
    shock: Shock,
    treatment: dict[str, object],
    span: int,
) -> pd.DataFrame:
    lo, hi = shock.window(span)
    d = reg[reg["year"].between(lo, hi)].copy()
    d["post"] = (d["year"] >= (shock.post_start or shock.year)).astype(int)
    if shock.design == "regional":
        region = d["state"].isin(shock.states).astype(float)
    else:
        region = 1.0
    col = str(treatment["col"])
    if treatment["scope"] == "firm_pre_binary":
        t = pre_exposure(
            reg,
            shock.year,
            lo,
            col,
            threshold=float(treatment.get("threshold", 0.0)),
            high=bool(treatment.get("high", False)),
        )
    elif treatment["scope"] == "firm_pre_continuous":
        t = continuous_pre_exposure(reg, shock.year, lo, col)
    else:
        # Segment-level treatments do not map cleanly to firm-year DID.
        t = pre_exposure(reg, shock.year, lo, col.replace("seg_", "share_"), threshold=0.0)
    d = d.merge(t.reset_index(), on="gvkey", how="left")
    d["T"] = d["T"].fillna(0.0) * region
    d["did"] = d["T"] * d["post"]
    return d


def fit_firm_did(d: pd.DataFrame, outcome: str) -> dict[str, object]:
    controls = ["logat", "lev"]
    needed = [outcome, "did"] + controls
    d = d.dropna(subset=needed).copy()
    spread = d.groupby("gvkey")["post"].nunique()
    d = d[d["gvkey"].isin(spread[spread == 2].index)].copy()
    if len(d) < 500 or d["gvkey"].nunique() < 30 or (d["T"].abs() > 1e-12).sum() == 0:
        return {"status": "too_few_firms_or_no_treat"}
    idx = pd.MultiIndex.from_arrays([d["gvkey"].values, d["year"].values])
    x = d[["did"] + controls].copy()
    x.index = idx
    y = pd.Series(d[outcome].values, index=idx)
    try:
        res = PanelOLS(y, x, entity_effects=True, time_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", cluster_entity=True
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": f"fit_error:{type(exc).__name__}"}
    active = d.loc[d["T"].abs() > 1e-12, "gvkey"].nunique()
    inactive = d.loc[d["T"].abs() <= 1e-12, "gvkey"].nunique()
    return {
        "status": "ok",
        "beta": float(res.params.get("did", np.nan)),
        "se": float(res.std_errors.get("did", np.nan)),
        "t": float(res.tstats.get("did", np.nan)),
        "p": float(res.pvalues.get("did", np.nan)),
        "nobs": int(res.nobs),
        "firms": int(d["gvkey"].nunique()),
        "treated_firms": int(active),
        "control_firms": int(inactive),
        "rows": int(len(d)),
    }


def run_firm_did_grid(reg: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for shock in SHOCKS:
        firm_treatments = [t for t in treatment_grid(shock) if str(t["scope"]).startswith("firm_pre")]
        for treatment in firm_treatments:
            for span in SPAN_GRID:
                base = build_firm_did_data(reg, shock, treatment, span)
                for outcome in FIRM_OUTCOMES:
                    res = fit_firm_did(base, outcome)
                    row = {
                        "model": "firm_did",
                        "shock": shock.name,
                        "family": shock.family,
                        "design": shock.design,
                        "event_year": shock.year,
                        "span": span,
                        "window_start": int(shock.year - span),
                        "window_end": int(shock.year + span),
                        "sample": "firmyear",
                        "outcome": outcome,
                        "opp": "",
                        "treatment": treatment["name"],
                        "treatment_col": treatment["col"],
                        "treatment_scope": treatment["scope"],
                        "note": shock.note,
                    }
                    row.update(res)
                    rows.append(row)
    return rows


def robustness_summary(results: pd.DataFrame) -> pd.DataFrame:
    ok = results[results["status"].eq("ok")].copy()
    if ok.empty:
        return pd.DataFrame()
    ok["sign"] = np.sign(ok["beta"])
    ok["abs_t"] = ok["t"].abs()
    ok["p05"] = ok["p"] < 0.05
    ok["p10"] = ok["p"] < 0.10
    keys = ["model", "shock", "family", "design", "treatment", "outcome", "opp"]
    rows = []
    for key, d in ok.groupby(keys, dropna=False):
        signs = d.loc[d["beta"].notna(), "sign"]
        modal_sign = np.nan
        sign_consistency = np.nan
        if not signs.empty:
            counts = signs.value_counts()
            modal_sign = float(counts.index[0])
            sign_consistency = float(counts.iloc[0] / len(signs))
        rows.append(
            dict(
                zip(keys, key),
                n_specs=int(len(d)),
                n_p05=int(d["p05"].sum()),
                n_p10=int(d["p10"].sum()),
                share_p05=float(d["p05"].mean()),
                share_p10=float(d["p10"].mean()),
                median_beta=float(d["beta"].median()),
                median_t=float(d["t"].median()),
                median_abs_t=float(d["abs_t"].median()),
                min_p=float(d["p"].min()),
                max_p=float(d["p"].max()),
                modal_sign=modal_sign,
                sign_consistency=sign_consistency,
                min_treated_firms=int(d["treated_firms"].min()),
                min_control_firms=int(d["control_firms"].min()),
                median_nobs=int(d["nobs"].median()),
            )
        )
    out = pd.DataFrame(rows)
    out["robust_score"] = (
        out["n_p05"] * 2
        + out["n_p10"]
        + out["sign_consistency"].fillna(0)
        + np.minimum(out["median_abs_t"].fillna(0), 5) / 2
    )
    out["robust_candidate"] = (
        (out["n_specs"] >= 4)
        & (out["n_p05"] >= 3)
        & (out["sign_consistency"] >= 0.80)
        & (out["median_abs_t"] >= 1.8)
        & (out["min_treated_firms"] >= 20)
        & (out["min_control_firms"] >= 50)
    )
    return out.sort_values(["robust_candidate", "robust_score", "n_p05"], ascending=[False, False, False])


def write_summary(results: pd.DataFrame, summary: pd.DataFrame, qa: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append("# Energy Shock Trial Summary")
    lines.append("")
    lines.append("This is a trial-only screening output. It should not be cited as a production result without a separate identification memo and source validation.")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Oil: WTI 1983 derivative-availability shock.")
    lines.append("- Gas: NATGAS 1990 derivative-availability shock plus FERC 636 1992 restructuring check.")
    lines.append("- Carbon: RGGI 2009 and California 2013 regional cap-and-trade proxies; these are exploratory because plant emissions and allowance holdings are not observed.")
    lines.append("")
    lines.append("## Robustness Gate")
    lines.append("")
    lines.append("A grouped candidate is flagged only when at least 3 specs have p<0.05, at least 80% of coefficients share the same sign, median |t| is at least 1.8, and minimum treated/control firm counts clear 20/50.")
    lines.append("")
    ok = results[results["status"].eq("ok")]
    lines.append(f"- Estimated specs: {len(results):,}")
    lines.append(f"- Successful specs: {len(ok):,}")
    lines.append(f"- Failed/skipped specs: {len(results) - len(ok):,}")
    lines.append("")
    if summary.empty or not summary["robust_candidate"].any():
        lines.append("## Robust Candidates")
        lines.append("")
        lines.append("No group passed the current robustness gate.")
    else:
        cand = summary[summary["robust_candidate"]].head(20)
        lines.append("## Robust Candidates")
        lines.append("")
        for _, r in cand.iterrows():
            opp = "" if pd.isna(r["opp"]) or r["opp"] == "" else f", opp={r['opp']}"
            lines.append(
                f"- `{r['model']}` `{r['shock']}` `{r['treatment']}` outcome=`{r['outcome']}`{opp}: "
                f"n_p05={int(r['n_p05'])}/{int(r['n_specs'])}, median_beta={r['median_beta']:+.4f}, "
                f"median_t={r['median_t']:+.2f}, sign_consistency={r['sign_consistency']:.2f}, "
                f"min treated/control firms={int(r['min_treated_firms'])}/{int(r['min_control_firms'])}."
            )
    lines.append("")
    lines.append("## Top Screened Groups")
    lines.append("")
    top = summary.head(15) if not summary.empty else pd.DataFrame()
    if top.empty:
        lines.append("No successful grouped results.")
    else:
        for _, r in top.iterrows():
            flag = "PASS" if bool(r["robust_candidate"]) else "screen"
            opp = "" if pd.isna(r["opp"]) or r["opp"] == "" else f", opp={r['opp']}"
            lines.append(
                f"- {flag}: `{r['model']}` `{r['shock']}` `{r['treatment']}` outcome=`{r['outcome']}`{opp}; "
                f"p<.05 {int(r['n_p05'])}/{int(r['n_specs'])}, median_t={r['median_t']:+.2f}, "
                f"median_beta={r['median_beta']:+.4f}."
            )
    lines.append("")
    lines.append("## Identification Notes")
    lines.append("")
    lines.append("- WTI 1983 and NATGAS 1990 are the cleanest derivative-availability candidates in this trial.")
    lines.append("- FERC 636 is a gas-market structure shock, so it should be interpreted separately from derivative contract availability.")
    lines.append("- Carbon results require extra validation before use: firm exposure is based on HQ state plus high-carbon segment SIC, not facility emissions.")
    lines.append("- Significant trial results should be re-estimated after freezing a single pre-specified sample and writing an identification memo.")

    (TRIAL / "energy_shock_trial_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (TRIAL / "energy_shock_trial_qa.json").write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    g, reg, qa = load_inputs()
    rows = []
    rows.extend(run_rsz_grid(g, reg))
    rows.extend(run_firm_did_grid(reg))
    results = pd.DataFrame(rows)
    summary = robustness_summary(results)

    all_path = TRIAL / "energy_shock_all_specs.csv"
    summary_path = TRIAL / "energy_shock_robustness_summary.csv"
    results.to_csv(all_path, index=False)
    summary.to_csv(summary_path, index=False)

    qa.update(
        {
            "script": relpath(Path(__file__)),
            "outputs": {
                "all_specs": relpath(all_path),
                "robustness_summary": relpath(summary_path),
                "summary_md": relpath(TRIAL / "energy_shock_trial_summary.md"),
                "qa_json": relpath(TRIAL / "energy_shock_trial_qa.json"),
            },
            "shock_definitions": [s.__dict__ | {"states": sorted(s.states)} for s in SHOCKS]
            + [STACKED_CARBON.__dict__ | {"states": []}],
            "span_grid": SPAN_GRID,
            "samples": SAMPLES,
            "opp_cols": OPP_COLS,
            "firm_outcomes": FIRM_OUTCOMES,
            "successful_specs": int(results["status"].eq("ok").sum()),
            "total_specs": int(len(results)),
            "robust_candidates": int(summary["robust_candidate"].sum()) if not summary.empty else 0,
        }
    )
    write_summary(results, summary, qa)

    print(f"wrote {all_path.relative_to(ROOT)}")
    print(f"wrote {summary_path.relative_to(ROOT)}")
    print(f"wrote {(TRIAL / 'energy_shock_trial_summary.md').relative_to(ROOT)}")
    if not summary.empty:
        cols = [
            "robust_candidate",
            "model",
            "shock",
            "treatment",
            "outcome",
            "opp",
            "n_specs",
            "n_p05",
            "median_beta",
            "median_t",
            "sign_consistency",
            "min_treated_firms",
            "min_control_firms",
        ]
        print(summary[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
