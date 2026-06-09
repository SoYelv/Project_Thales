#!/usr/bin/env python3
"""DiD / event-study engine for the derivative-availability design.

First batch: baseline TWFE DiD for the natural-gas (1990) and electricity (1996)
launches, across segment-reporting and centralization outcomes.
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "reports" / "panel"

df = pd.read_parquet(P / "regdata.parquet")

def winsor(s, lo=0.01, hi=0.99):
    ql, qh = s.quantile(lo), s.quantile(hi)
    return s.clip(ql, qh)

# clean controls
for c in ["lev", "roa", "capx_at", "cash_at", "logat"]:
    df[c] = df[c].replace([np.inf, -np.inf], np.nan)
df["lev"] = df["lev"].clip(0, 5)
df["log_nseg"] = np.log1p(df["n_op_seg"])

# firm-level pre-event exposure helper
def pre_event_treat(data, expo_col, event_year, pre_lo=None):
    pre_lo = pre_lo if pre_lo is not None else event_year - 6
    pre = data[(data.year >= pre_lo) & (data.year < event_year)]
    treat = (pre.groupby("gvkey")[expo_col].max() > 0).astype(int).rename("treat")
    return treat

def run_did(data, expo_col, event_year, lo, hi, outcome,
            controls=("logat", "lev"), label=""):
    d = data[(data.year >= lo) & (data.year <= hi)].copy()
    treat = pre_event_treat(data, expo_col, event_year, pre_lo=lo)
    d = d.merge(treat, on="gvkey", how="inner")
    d["post"] = (d.year >= event_year).astype(int)
    d["did"] = d["treat"] * d["post"]
    d = d.dropna(subset=[outcome])
    keep = ["gvkey", "year", outcome, "did"] + list(controls)
    d = d.dropna(subset=list(controls)) if controls else d
    d = d[keep + (["treat","post"])].copy()
    # need within-firm variation: keep firms seen in both pre & post
    spread = d.groupby("gvkey")["post"].nunique()
    d = d[d.gvkey.isin(spread[spread == 2].index)]
    d = d.set_index(["gvkey", "year"])
    exog = ["did"] + list(controls)
    mod = PanelOLS(d[outcome], d[exog], entity_effects=True, time_effects=True,
                   drop_absorbed=True, check_rank=False)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    b = res.params["did"]; se = res.std_errors["did"]; t = res.tstats["did"]; p = res.pvalues["did"]
    n_tr = d.reset_index().query("treat==1").gvkey.nunique()
    n_co = d.reset_index().query("treat==0").gvkey.nunique()
    print(f"{label:42s} {outcome:18s} beta={b:+.4f} se={se:.4f} t={t:+.2f} p={p:.3f} "
          f"N={int(res.nobs):>7,} tr={n_tr} co={n_co}")
    return dict(label=label, outcome=outcome, beta=b, se=se, t=t, p=p, n=int(res.nobs),
                n_treat=n_tr, n_ctrl=n_co)

OUTCOMES = ["n_op_seg", "log_nseg", "multi_seg", "hhi", "n_nonop_seg", "nonop_sales_share"]

print("="*120)
print("BATCH 1: baseline TWFE DiD, controls = logat + lev")
print("="*120)
results = []
print("\n--- Natural gas 1990, treat = pre-event energy exposure, window 1980-2000 ---")
for o in OUTCOMES:
    results.append(run_did(df, "exp_energy", 1990, 1980, 2000, o, label="NG1990 energy"))

print("\n--- Natural gas 1990, treat = gas/oilgas only, window 1980-2000 ---")
df["exp_gasoil"] = ((df.exp_gas == 1) | (df.exp_oilgas == 1)).astype(int)
for o in OUTCOMES:
    results.append(run_did(df, "exp_gasoil", 1990, 1980, 2000, o, label="NG1990 gas/oil"))

print("\n--- Electricity 1996, treat = pre-event electric exposure, window 1990-2004 ---")
for o in OUTCOMES:
    results.append(run_did(df, "exp_electric", 1996, 1990, 2004, o, label="ELEC1996 electric"))

print("\n--- Crude oil 1983, treat = pre-event oilgas exposure, window 1978-1990 ---")
for o in OUTCOMES:
    results.append(run_did(df, "exp_oilgas", 1983, 1978, 1990, o, label="WTI1983 oilgas"))

pd.DataFrame(results).to_csv(ROOT / "reports" / "tables" / "did_batch1.csv", index=False)
print("\nsaved did_batch1.csv")
