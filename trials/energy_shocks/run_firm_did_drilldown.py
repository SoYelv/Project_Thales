#!/usr/bin/env python3
"""Firm-year outcome drilldown for strong continuous-exposure energy shocks."""
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
    build_firm_did_data,
    load_inputs,
    relpath,
    treatment_grid,
)

warnings.filterwarnings("ignore")


def find_shock(name: str) -> Shock:
    return {s.name: s for s in SHOCKS}[name]


def find_treatment(shock: Shock, treatment_name: str) -> dict[str, object]:
    return {str(t["name"]): t for t in treatment_grid(shock)}[treatment_name]


def fit_did(d: pd.DataFrame, outcome: str) -> dict[str, object]:
    controls = ["logat", "lev"]
    d = d.dropna(subset=[outcome, "did"] + controls).copy()
    spread = d.groupby("gvkey")["post"].nunique()
    d = d[d["gvkey"].isin(spread[spread == 2].index)].copy()
    if len(d) < 500 or d["gvkey"].nunique() < 30 or d["T"].std() == 0:
        return {"status": "too_few_or_no_variation"}
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
    return {
        "status": "ok",
        "beta": float(res.params.get("did", np.nan)),
        "se": float(res.std_errors.get("did", np.nan)),
        "t": float(res.tstats.get("did", np.nan)),
        "p": float(res.pvalues.get("did", np.nan)),
        "nobs": int(res.nobs),
        "firms": int(d["gvkey"].nunique()),
        "t_std": float(d.drop_duplicates("gvkey")["T"].std()),
        "t_p25": float(d.drop_duplicates("gvkey")["T"].quantile(0.25)),
        "t_p75": float(d.drop_duplicates("gvkey")["T"].quantile(0.75)),
    }


def fit_event_study(d: pd.DataFrame, outcome: str, event_year: int, min_k: int = -5, max_k: int = 5, ref_k: int = -1) -> list[dict[str, object]]:
    controls = ["logat", "lev"]
    d = d.dropna(subset=[outcome, "T"] + controls).copy()
    d["k"] = d["year"] - event_year
    d = d[d["k"].between(min_k, max_k)].copy()
    if d.empty or d["T"].std() == 0:
        return []
    for k in range(min_k, max_k + 1):
        if k == ref_k:
            continue
        d[f"Tk{k}"] = d["T"] * d["k"].eq(k).astype(float)
    tvars = [f"Tk{k}" for k in range(min_k, max_k + 1) if k != ref_k]
    idx = pd.MultiIndex.from_arrays([d["gvkey"].values, d["year"].values])
    x = d[tvars + controls].copy()
    x.index = idx
    y = pd.Series(d[outcome].values, index=idx)
    try:
        res = PanelOLS(y, x, entity_effects=True, time_effects=True, check_rank=False, drop_absorbed=True).fit(
            cov_type="clustered", cluster_entity=True
        )
    except Exception as exc:  # noqa: BLE001
        return [{"status": f"fit_error:{type(exc).__name__}"}]
    rows = []
    for k in range(min_k, max_k + 1):
        if k == ref_k:
            continue
        key = f"Tk{k}"
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
            }
        )
    return rows


def select_candidates(summary: pd.DataFrame) -> pd.DataFrame:
    d = summary[
        (summary["model"] == "firm_did")
        & (summary["n_specs"] >= 3)
        & (summary["n_p05"] >= 3)
        & (summary["sign_consistency"] >= 1.0)
        & (summary["median_abs_t"] >= 2.3)
        & (summary["treatment"].str.endswith("_share_z") | summary["treatment"].eq("pre_energy_any"))
        & (
            summary["shock"].isin(
                [
                    "NATGAS_1990",
                    "FERC636_1992",
                    "WTI_1983",
                    "OIL_COLLAPSE_1986",
                    "SO2_ALLOWANCE_1995",
                    "GAS_SPIKE_2001",
                    "EU_ETS_2005",
                ]
            )
        )
    ].copy()
    keep_outcomes = {"n_op_seg", "log_nseg", "hhi", "multi_seg"}
    d = d[d["outcome"].isin(keep_outcomes)]
    return d.sort_values(["robust_score", "median_abs_t"], ascending=False).head(12)


def run_baseline_grid(reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        for span in [3, 5, 7]:
            d = build_firm_did_data(reg, shock, treatment, span)
            res = fit_did(d, str(cand["outcome"]))
            res.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": cand["outcome"],
                    "span": span,
                    "check": "baseline_span",
                }
            )
            rows.append(res)
    return pd.DataFrame(rows)


def run_event_studies(reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        d = build_firm_did_data(reg, shock, treatment, 5)
        for row in fit_event_study(d, str(cand["outcome"]), shock.year, -5, 5, -1):
            row.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": cand["outcome"],
                    "span": 5,
                    "check": "event_study",
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def run_placebos(reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        for offset in [4, 5, 6]:
            pseudo_year = shock.year - offset
            pseudo = replace(shock, name=f"{shock.name}_PLACEBO_{pseudo_year}", year=pseudo_year, base_span=3)
            d = build_firm_did_data(reg, pseudo, treatment, 3)
            res = fit_did(d, str(cand["outcome"]))
            res.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": cand["outcome"],
                    "pseudo_year": pseudo_year,
                    "span": 3,
                    "check": "pre_only_placebo",
                }
            )
            rows.append(res)
    return pd.DataFrame(rows)


def run_leave_one_year(reg: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cand in candidates.iterrows():
        shock = find_shock(str(cand["shock"]))
        treatment = find_treatment(shock, str(cand["treatment"]))
        d0 = build_firm_did_data(reg, shock, treatment, 5)
        d0["k"] = d0["year"] - shock.year
        for k in range(-5, 6):
            d = d0[d0["k"] != k].copy()
            res = fit_did(d, str(cand["outcome"]))
            res.update(
                {
                    "shock": shock.name,
                    "treatment": treatment["name"],
                    "outcome": cand["outcome"],
                    "dropped_k": k,
                    "span": 5,
                    "check": "leave_one_relative_year",
                }
            )
            rows.append(res)
    return pd.DataFrame(rows)


def summarize(es: pd.DataFrame, placebos: pd.DataFrame, loo: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["shock", "treatment", "outcome"]
    for key, d in es[es["status"].eq("ok")].groupby(keys, dropna=False):
        pre = d[d["k"] <= -2]
        post = d[d["k"] >= 0]
        p = placebos[
            placebos["shock"].eq(key[0]) & placebos["treatment"].eq(key[1]) & placebos["outcome"].eq(key[2])
        ]
        ly = loo[loo["shock"].eq(key[0]) & loo["treatment"].eq(key[1]) & loo["outcome"].eq(key[2])]
        bg = base[base["shock"].eq(key[0]) & base["treatment"].eq(key[1]) & base["outcome"].eq(key[2])]
        rows.append(
            {
                "shock": key[0],
                "treatment": key[1],
                "outcome": key[2],
                "baseline_p05": int((bg["p"] < 0.05).sum()) if not bg.empty else np.nan,
                "baseline_sign_consistency": float((np.sign(bg["beta"]) == np.sign(bg["beta"].median())).mean())
                if not bg.empty
                else np.nan,
                "event_study_pre_p_lt_10": int((pre["p"] < 0.10).sum()) if not pre.empty else np.nan,
                "event_study_pre_max_abs_t": float(pre["t"].abs().max()) if not pre.empty else np.nan,
                "event_study_post_p_lt_10": int((post["p"] < 0.10).sum()) if not post.empty else np.nan,
                "event_study_post_median_beta": float(post["beta"].median()) if not post.empty else np.nan,
                "placebo_p_lt_10": int((p["p"] < 0.10).sum()) if not p.empty else np.nan,
                "placebo_min_p": float(p["p"].min()) if not p.empty else np.nan,
                "loo_p_lt_05": int((ly["p"] < 0.05).sum()) if not ly.empty else np.nan,
                "loo_min_abs_t": float(ly["t"].abs().min()) if not ly.empty else np.nan,
                "loo_sign_consistency": float((np.sign(ly["beta"]) == np.sign(ly["beta"].median())).mean())
                if not ly.empty
                else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["firm_drilldown_pass"] = (
        (out["baseline_p05"] == 3)
        & (out["baseline_sign_consistency"] >= 1.0)
        & (out["event_study_pre_p_lt_10"] <= 1)
        & (out["placebo_p_lt_10"] == 0)
        & (out["loo_p_lt_05"] >= 9)
        & (out["loo_sign_consistency"] >= 0.90)
    )
    return out.sort_values(["firm_drilldown_pass", "baseline_p05", "loo_p_lt_05"], ascending=[False, False, False])


def append_markdown(drill: pd.DataFrame) -> None:
    path = TRIAL / "energy_shock_trial_summary.md"
    text = path.read_text(encoding="utf-8")
    lines = ["", "## Firm-Year Drilldown", ""]
    if drill.empty:
        lines.append("No firm-year drilldown rows were produced.")
    else:
        for _, r in drill.iterrows():
            verdict = "PASS" if bool(r["firm_drilldown_pass"]) else "FAIL"
            lines.append(
                f"- {verdict}: `{r['shock']}` `{r['treatment']}` outcome=`{r['outcome']}`; "
                f"baseline p<.05={int(r['baseline_p05'])}/3, "
                f"pre p<.10={int(r['event_study_pre_p_lt_10'])}, "
                f"placebo p<.10={int(r['placebo_p_lt_10'])}, "
                f"leave-one p<.05={int(r['loo_p_lt_05'])}/11."
            )
    path.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    _, reg, _ = load_inputs()
    summary = pd.read_csv(TRIAL / "energy_shock_robustness_summary.csv")
    candidates = select_candidates(summary)
    if candidates.empty:
        raise SystemExit("No firm-year candidates selected.")

    base = run_baseline_grid(reg, candidates)
    es = run_event_studies(reg, candidates)
    placebos = run_placebos(reg, candidates)
    loo = run_leave_one_year(reg, candidates)
    drill = summarize(es, placebos, loo, base)

    base_path = TRIAL / "energy_shock_firm_did_baseline_candidates.csv"
    es_path = TRIAL / "energy_shock_firm_did_event_study.csv"
    placebo_path = TRIAL / "energy_shock_firm_did_placebos.csv"
    loo_path = TRIAL / "energy_shock_firm_did_leave_one_year.csv"
    drill_path = TRIAL / "energy_shock_firm_did_drilldown_summary.csv"
    selected_path = TRIAL / "energy_shock_firm_did_selected_candidates.csv"
    candidates.to_csv(selected_path, index=False)
    base.to_csv(base_path, index=False)
    es.to_csv(es_path, index=False)
    placebos.to_csv(placebo_path, index=False)
    loo.to_csv(loo_path, index=False)
    drill.to_csv(drill_path, index=False)
    append_markdown(drill)

    qa_path = TRIAL / "energy_shock_trial_qa.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else {}
    qa["firm_did_drilldown_outputs"] = {
        "selected_candidates": relpath(selected_path),
        "baseline": relpath(base_path),
        "event_study": relpath(es_path),
        "placebos": relpath(placebo_path),
        "leave_one_year": relpath(loo_path),
        "drilldown_summary": relpath(drill_path),
    }
    qa["firm_did_drilldown_pass_count"] = int(drill["firm_drilldown_pass"].sum()) if not drill.empty else 0
    qa_path.write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {selected_path.relative_to(ROOT)}")
    print(f"wrote {base_path.relative_to(ROOT)}")
    print(f"wrote {es_path.relative_to(ROOT)}")
    print(f"wrote {placebo_path.relative_to(ROOT)}")
    print(f"wrote {loo_path.relative_to(ROOT)}")
    print(f"wrote {drill_path.relative_to(ROOT)}")
    print(drill.to_string(index=False))


if __name__ == "__main__":
    main()
