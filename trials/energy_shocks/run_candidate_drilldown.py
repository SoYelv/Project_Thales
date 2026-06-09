#!/usr/bin/env python3
"""Drill-down checks for robust candidates from run_energy_shock_trials.py."""
from __future__ import annotations

import json
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from run_energy_shock_trials import (
    ROOT,
    TRIAL,
    SHOCKS,
    Shock,
    build_rsz_data,
    fit_rsz,
    load_inputs,
    relpath,
    treatment_grid,
)

warnings.filterwarnings("ignore")


def prepare_rsz(d: pd.DataFrame, opp: str) -> pd.DataFrame:
    d = d.dropna(subset=["inv_la", opp, "T", "post", "cohort"]).copy()
    obs_per_firmyear = d.groupby(["cohort", "gvkey", "year"])["snms_u"].transform("nunique")
    d = d[obs_per_firmyear >= 2].copy()
    for c in ["inv_la", opp]:
        qlo, qhi = d[c].quantile(0.01), d[c].quantile(0.99)
        d[c] = d[c].clip(qlo, qhi)
    d["rel_inv"] = d["inv_la"] - d.groupby(["cohort", "gvkey", "year"])["inv_la"].transform("mean")
    d["rel_opp"] = d[opp] - d.groupby(["cohort", "gvkey", "year"])[opp].transform("mean")
    d["k"] = d["year"] - d["cohort"]
    d["cseg"] = d["cohort"].astype(str) + "_" + d["gvkey"].astype(str) + "_" + d["snms_u"].astype(str)
    d["cy"] = d["cohort"].astype(str) + "_" + d["year"].astype(str)
    return d


def fit_event_study(d: pd.DataFrame, opp: str, min_k: int = -5, max_k: int = 5, ref_k: int = -1) -> list[dict[str, object]]:
    d = prepare_rsz(d, opp)
    if d.empty:
        return []
    for k in range(min_k, max_k + 1):
        if k == ref_k:
            continue
        d[f"s{k}"] = d["rel_opp"] * d["T"] * d["k"].eq(k).astype(float)
        d[f"r{k}"] = d["rel_opp"] * d["k"].eq(k).astype(float)
    d["roT"] = d["rel_opp"] * d["T"]
    svars = [f"s{k}" for k in range(min_k, max_k + 1) if k != ref_k]
    rvars = [f"r{k}" for k in range(min_k, max_k + 1) if k != ref_k]
    cy = pd.get_dummies(d["cy"], prefix="cy", drop_first=True).astype(float)
    idx = pd.MultiIndex.from_arrays([d["cseg"].values, d["year"].values])
    x = pd.concat([d[svars + rvars + ["roT"]].reset_index(drop=True), cy.reset_index(drop=True)], axis=1)
    x.index = idx
    y = pd.Series(d["rel_inv"].values, index=idx)
    clusters = pd.DataFrame({"firm": d["gvkey"].values}, index=idx)
    try:
        res = PanelOLS(y, x, entity_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", clusters=clusters
        )
    except Exception as exc:  # noqa: BLE001
        return [{"status": f"fit_error:{type(exc).__name__}"}]
    rows = []
    for k in range(min_k, max_k + 1):
        if k == ref_k:
            continue
        key = f"s{k}"
        rows.append(
            {
                "status": "ok",
                "k": k,
                "beta": float(res.params.get(key, np.nan)),
                "se": float(res.std_errors.get(key, np.nan)),
                "t": float(res.tstats.get(key, np.nan)),
                "p": float(res.pvalues.get(key, np.nan)),
                "nobs": int(res.nobs),
                "firms": int(d["gvkey"].nunique()),
                "treated_firms": int(d.loc[d["T"].abs() > 1e-12, "gvkey"].nunique()),
                "control_firms": int(d.loc[d["T"].abs() <= 1e-12, "gvkey"].nunique()),
            }
        )
    return rows


def find_shock(name: str) -> Shock:
    by_name = {s.name: s for s in SHOCKS}
    return by_name[name]


def find_treatment(shock: Shock, treatment_name: str) -> dict[str, object]:
    by_name = {str(t["name"]): t for t in treatment_grid(shock)}
    return by_name[treatment_name]


def run_event_studies(g: pd.DataFrame, reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        d = build_rsz_data(g, reg, shock, treatment, 5, "pre_multiseg")
        for row in fit_event_study(d, str(cand["opp"]), -5, 5, -1):
            row.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "opp": cand["opp"],
                    "span": 5,
                    "sample": "pre_multiseg",
                    "check": "event_study",
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def run_placebos(g: pd.DataFrame, reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        for offset in [4, 5, 6]:
            pseudo_year = shock.year - offset
            pseudo = replace(shock, name=f"{shock.name}_PLACEBO_{pseudo_year}", year=pseudo_year, base_span=3)
            d = build_rsz_data(g, reg, pseudo, treatment, 3, "pre_multiseg")
            res = fit_rsz(d, str(cand["opp"]))
            res.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "opp": cand["opp"],
                    "pseudo_year": pseudo_year,
                    "span": 3,
                    "sample": "pre_multiseg",
                    "check": "pre_only_placebo",
                }
            )
            rows.append(res)
    return pd.DataFrame(rows)


def run_leave_one_year(g: pd.DataFrame, reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        d0 = build_rsz_data(g, reg, shock, treatment, 5, "pre_multiseg")
        d0["k"] = d0["year"] - shock.year
        for k in range(-5, 6):
            d = d0[d0["k"] != k].copy()
            res = fit_rsz(d, str(cand["opp"]))
            res.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "opp": cand["opp"],
                    "dropped_k": k,
                    "span": 5,
                    "sample": "pre_multiseg",
                    "check": "leave_one_relative_year",
                }
            )
            rows.append(res)
    return pd.DataFrame(rows)


def summarize_drilldown(es: pd.DataFrame, placebos: pd.DataFrame, loo: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["shock", "treatment", "opp"]
    for key, d in es[es["status"].eq("ok")].groupby(keys, dropna=False):
        pre = d[d["k"] <= -2]
        post = d[d["k"] >= 0]
        placebo = placebos[
            placebos["shock"].eq(key[0]) & placebos["treatment"].eq(key[1]) & placebos["opp"].eq(key[2])
        ]
        ly = loo[loo["shock"].eq(key[0]) & loo["treatment"].eq(key[1]) & loo["opp"].eq(key[2])]
        rows.append(
            {
                "shock": key[0],
                "treatment": key[1],
                "opp": key[2],
                "event_study_pre_p_lt_10": int((pre["p"] < 0.10).sum()) if not pre.empty else np.nan,
                "event_study_pre_max_abs_t": float(pre["t"].abs().max()) if not pre.empty else np.nan,
                "event_study_post_median_beta": float(post["beta"].median()) if not post.empty else np.nan,
                "event_study_post_sign_consistency": float((np.sign(post["beta"]) == np.sign(post["beta"].median())).mean())
                if not post.empty
                else np.nan,
                "placebo_p_lt_10": int((placebo["p"] < 0.10).sum()) if not placebo.empty else np.nan,
                "placebo_min_p": float(placebo["p"].min()) if not placebo.empty else np.nan,
                "loo_p_lt_05": int((ly["p"] < 0.05).sum()) if not ly.empty else np.nan,
                "loo_min_abs_t": float(ly["t"].abs().min()) if not ly.empty else np.nan,
                "loo_sign_consistency": float((np.sign(ly["beta"]) == np.sign(ly["beta"].median())).mean())
                if not ly.empty
                else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["drilldown_pass"] = (
        (out["event_study_pre_p_lt_10"] == 0)
        & (out["placebo_p_lt_10"] == 0)
        & (out["loo_p_lt_05"] >= 8)
        & (out["loo_sign_consistency"] >= 0.90)
    )
    return out


def append_markdown(drill: pd.DataFrame) -> None:
    path = TRIAL / "energy_shock_trial_summary.md"
    text = path.read_text(encoding="utf-8")
    lines = ["", "## Candidate Drilldown", ""]
    if drill.empty:
        lines.append("No drilldown rows were produced.")
    else:
        for _, r in drill.iterrows():
            verdict = "PASS" if bool(r["drilldown_pass"]) else "FAIL"
            lines.append(
                f"- {verdict}: `{r['shock']}` `{r['treatment']}` opp=`{r['opp']}`; "
                f"pre p<.10={int(r['event_study_pre_p_lt_10'])}, "
                f"placebo p<.10={int(r['placebo_p_lt_10'])}, "
                f"leave-one p<.05={int(r['loo_p_lt_05'])}/11, "
                f"leave-one sign consistency={r['loo_sign_consistency']:.2f}."
            )
    path.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    g, reg, qa = load_inputs()
    summary_path = TRIAL / "energy_shock_robustness_summary.csv"
    summary = pd.read_csv(summary_path)
    candidates = summary[(summary["robust_candidate"]) & (summary["model"] == "rsz")].copy()
    if candidates.empty:
        raise SystemExit("No robust RSZ candidates to drill down.")

    es = run_event_studies(g, reg, candidates)
    placebos = run_placebos(g, reg, candidates)
    loo = run_leave_one_year(g, reg, candidates)
    drill = summarize_drilldown(es, placebos, loo)

    es_path = TRIAL / "energy_shock_candidate_event_study.csv"
    placebo_path = TRIAL / "energy_shock_candidate_placebos.csv"
    loo_path = TRIAL / "energy_shock_candidate_leave_one_year.csv"
    drill_path = TRIAL / "energy_shock_candidate_drilldown_summary.csv"
    es.to_csv(es_path, index=False)
    placebos.to_csv(placebo_path, index=False)
    loo.to_csv(loo_path, index=False)
    drill.to_csv(drill_path, index=False)
    append_markdown(drill)

    qa_path = TRIAL / "energy_shock_trial_qa.json"
    old_qa = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else {}
    old_qa["drilldown_outputs"] = {
        "event_study": relpath(es_path),
        "placebos": relpath(placebo_path),
        "leave_one_year": relpath(loo_path),
        "drilldown_summary": relpath(drill_path),
    }
    old_qa["drilldown_candidates"] = candidates[["shock", "treatment", "opp", "n_specs", "n_p05"]].to_dict("records")
    old_qa["drilldown_pass_count"] = int(drill["drilldown_pass"].sum()) if not drill.empty else 0
    qa_path.write_text(json.dumps(old_qa | {"latest_load_counts": qa}, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {es_path.relative_to(ROOT)}")
    print(f"wrote {placebo_path.relative_to(ROOT)}")
    print(f"wrote {loo_path.relative_to(ROOT)}")
    print(f"wrote {drill_path.relative_to(ROOT)}")
    print(drill.to_string(index=False))


if __name__ == "__main__":
    main()
