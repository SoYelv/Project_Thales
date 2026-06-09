#!/usr/bin/env python3
"""Trend-adjusted checks for promising but pre-trending trial candidates."""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from run_energy_shock_trials import (
    ROOT,
    TRIAL,
    SHOCKS,
    build_firm_did_data,
    build_rsz_data,
    load_inputs,
    relpath,
    treatment_grid,
)
from run_candidate_drilldown import prepare_rsz

warnings.filterwarnings("ignore")


def shock_by_name(name: str):
    return {s.name: s for s in SHOCKS}[name]


def treatment_by_name(shock, name: str):
    return {str(t["name"]): t for t in treatment_grid(shock)}[name]


def fit_firm_trend(d: pd.DataFrame, outcome: str, event_year: int) -> dict[str, object]:
    controls = ["logat", "lev"]
    d = d.dropna(subset=[outcome, "did", "T"] + controls).copy()
    spread = d.groupby("gvkey")["post"].nunique()
    d = d[d["gvkey"].isin(spread[spread == 2].index)].copy()
    if d.empty or d["T"].std() == 0:
        return {"status": "too_few_or_no_variation"}
    d["trend"] = d["year"] - event_year
    d["Ttrend"] = d["T"] * d["trend"]
    idx = pd.MultiIndex.from_arrays([d["gvkey"].values, d["year"].values])
    x = d[["did", "Ttrend"] + controls].copy()
    x.index = idx
    y = pd.Series(d[outcome].values, index=idx)
    try:
        res = PanelOLS(y, x, entity_effects=True, time_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", cluster_entity=True
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": f"fit_error:{type(exc).__name__}"}
    return {
        "status": "ok",
        "beta": float(res.params.get("did", np.nan)),
        "se": float(res.std_errors.get("did", np.nan)),
        "t": float(res.tstats.get("did", np.nan)),
        "p": float(res.pvalues.get("did", np.nan)),
        "trend_beta": float(res.params.get("Ttrend", np.nan)),
        "trend_t": float(res.tstats.get("Ttrend", np.nan)),
        "nobs": int(res.nobs),
        "firms": int(d["gvkey"].nunique()),
    }


def fit_rsz_trend(d: pd.DataFrame, opp: str) -> dict[str, object]:
    d = prepare_rsz(d, opp)
    if d.empty:
        return {"status": "too_few_rows"}
    d["ro"] = d["rel_opp"]
    d["rop"] = d["ro"] * d["post"]
    d["roT"] = d["ro"] * d["T"]
    d["roTp"] = d["ro"] * d["T"] * d["post"]
    d["trend"] = d["year"] - d["cohort"]
    d["roTrend"] = d["ro"] * d["trend"]
    d["roTtrend"] = d["ro"] * d["T"] * d["trend"]
    cy = pd.get_dummies(d["cy"], prefix="cy", drop_first=True).astype(float)
    idx = pd.MultiIndex.from_arrays([d["cseg"].values, d["year"].values])
    x = pd.concat(
        [
            d[["roTp", "rop", "roT", "ro", "roTrend", "roTtrend"]].reset_index(drop=True),
            cy.reset_index(drop=True),
        ],
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
    return {
        "status": "ok",
        "beta": float(res.params.get("roTp", np.nan)),
        "se": float(res.std_errors.get("roTp", np.nan)),
        "t": float(res.tstats.get("roTp", np.nan)),
        "p": float(res.pvalues.get("roTp", np.nan)),
        "trend_beta": float(res.params.get("roTtrend", np.nan)),
        "trend_t": float(res.tstats.get("roTtrend", np.nan)),
        "nobs": int(res.nobs),
        "firms": int(d["gvkey"].nunique()),
    }


def firm_candidates() -> pd.DataFrame:
    path = TRIAL / "energy_shock_firm_did_drilldown_summary.csv"
    if not path.exists():
        return pd.DataFrame()
    d = pd.read_csv(path)
    return d[
        (d["baseline_p05"] == 3)
        & (d["baseline_sign_consistency"] >= 1.0)
        & (d["loo_p_lt_05"] >= 10)
        & (d["loo_sign_consistency"] >= 1.0)
        & (d["placebo_p_lt_10"] <= 1)
    ].copy()


def rsz_candidates() -> pd.DataFrame:
    path = TRIAL / "energy_shock_candidate_drilldown_summary.csv"
    if not path.exists():
        return pd.DataFrame()
    d = pd.read_csv(path)
    return d[
        (d["loo_p_lt_05"] >= 8)
        & (d["loo_sign_consistency"] >= 1.0)
        & (d["placebo_p_lt_10"] <= 1)
    ].copy()


def main() -> None:
    g, reg, _ = load_inputs()
    rows = []

    for _, cand in firm_candidates().iterrows():
        shock = shock_by_name(str(cand["shock"]))
        treatment = treatment_by_name(shock, str(cand["treatment"]))
        for span in [3, 5, 7]:
            d = build_firm_did_data(reg, shock, treatment, span)
            res = fit_firm_trend(d, str(cand["outcome"]), shock.year)
            res.update(
                {
                    "model": "firm_did_trend",
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": cand["outcome"],
                    "opp": "",
                    "span": span,
                }
            )
            rows.append(res)

    for _, cand in rsz_candidates().iterrows():
        shock = shock_by_name(str(cand["shock"]))
        treatment = treatment_by_name(shock, str(cand["treatment"]))
        for span in [3, 5, 7]:
            d = build_rsz_data(g, reg, shock, treatment, span, "pre_multiseg")
            res = fit_rsz_trend(d, str(cand["opp"]))
            res.update(
                {
                    "model": "rsz_trend",
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": "rel_inv",
                    "opp": cand["opp"],
                    "span": span,
                }
            )
            rows.append(res)

    out = pd.DataFrame(rows)
    if not out.empty:
        key_cols = ["model", "shock", "treatment", "outcome", "opp"]
        summary = (
            out[out["status"].eq("ok")]
            .groupby(key_cols, dropna=False)
            .agg(
                n_specs=("p", "size"),
                n_p05=("p", lambda s: int((s < 0.05).sum())),
                median_beta=("beta", "median"),
                median_t=("t", "median"),
                max_p=("p", "max"),
                sign_consistency=("beta", lambda s: float((np.sign(s) == np.sign(s.median())).mean())),
                median_trend_t=("trend_t", "median"),
            )
            .reset_index()
        )
        summary["trend_adjusted_pass"] = (
            (summary["n_specs"] == 3)
            & (summary["n_p05"] == 3)
            & (summary["sign_consistency"] >= 1.0)
            & (summary["max_p"] < 0.05)
        )
    else:
        summary = pd.DataFrame()

    out_path = TRIAL / "energy_shock_trend_adjusted_specs.csv"
    summary_path = TRIAL / "energy_shock_trend_adjusted_summary.csv"
    out.to_csv(out_path, index=False)
    summary.to_csv(summary_path, index=False)

    md = TRIAL / "energy_shock_trial_summary.md"
    text = md.read_text(encoding="utf-8") if md.exists() else ""
    lines = ["", "## Trend-Adjusted Checks", ""]
    if summary.empty:
        lines.append("No candidates met the preconditions for trend-adjusted checks.")
    else:
        for _, r in summary.iterrows():
            verdict = "PASS" if bool(r["trend_adjusted_pass"]) else "FAIL"
            opp = "" if pd.isna(r["opp"]) or r["opp"] == "" else f", opp=`{r['opp']}`"
            lines.append(
                f"- {verdict}: `{r['model']}` `{r['shock']}` `{r['treatment']}` "
                f"outcome=`{r['outcome']}`{opp}; p<.05={int(r['n_p05'])}/{int(r['n_specs'])}, "
                f"median_beta={r['median_beta']:+.4f}, median_t={r['median_t']:+.2f}."
            )
    md.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")

    qa_path = TRIAL / "energy_shock_trial_qa.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else {}
    qa["trend_adjusted_outputs"] = {"specs": relpath(out_path), "summary": relpath(summary_path)}
    qa["trend_adjusted_pass_count"] = int(summary["trend_adjusted_pass"].sum()) if not summary.empty else 0
    qa_path.write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"wrote {summary_path.relative_to(ROOT)}")
    if not summary.empty:
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
