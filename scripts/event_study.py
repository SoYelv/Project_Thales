#!/usr/bin/env python3
"""Event-study (leads/lags) for the electricity 1996 launch.
Checks for pre-trends vs. a clean post-launch turn-on, which matters for
separating the hedging/information channel from SFAS 131 (FY1998) and
FERC restructuring confounds.
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
df["lev"] = df["lev"].replace([np.inf,-np.inf],np.nan).clip(0,5)
df["logat"] = df["logat"].replace([np.inf,-np.inf],np.nan)
df["log_nseg"] = np.log1p(df["n_op_seg"])

def event_study(expo_col, event_year, lo, hi, outcome, controls=("logat","lev"),
                kmin=-6, kmax=6, label=""):
    pre = df[(df.year>=lo)&(df.year<event_year)]
    treat = (pre.groupby("gvkey")[expo_col].max()>0).astype(int).rename("treat")
    d = df[(df.year>=lo)&(df.year<=hi)].merge(treat,on="gvkey",how="inner")
    d = d.dropna(subset=[outcome]+list(controls))
    spread = d.groupby("gvkey")["year"].nunique()
    d = d[d.gvkey.isin(spread[spread>=4].index)]
    d["k"] = (d.year - event_year).clip(kmin,kmax)
    # relative-time dummies interacted with treat, omit k=-1
    for k in range(kmin,kmax+1):
        if k==-1: continue
        d[f"d{k}"] = ((d.k==k)&(d.treat==1)).astype(int)
    dvars = [f"d{k}" for k in range(kmin,kmax+1) if k!=-1]
    dd = d.set_index(["gvkey","year"])
    mod = PanelOLS(dd[outcome], dd[dvars+list(controls)], entity_effects=True,
                   time_effects=True, drop_absorbed=True, check_rank=False)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    print(f"\n=== Event study: {label} | outcome={outcome} | N={int(res.nobs):,} ===")
    print(" k    beta      se      t")
    for k in range(kmin,kmax+1):
        if k==-1:
            print(f"{k:+d}   (omitted reference)"); continue
        v=f"d{k}"
        if v in res.params.index:
            print(f"{k:+d}  {res.params[v]:+.4f}  {res.std_errors[v]:.4f}  {res.tstats[v]:+.2f}")

for o in ["n_op_seg","log_nseg","n_nonop_seg"]:
    event_study("exp_electric",1996,1988,2004,o,label="ELEC1996 electric vs all")
