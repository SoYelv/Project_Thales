#!/usr/bin/env python3
"""Interpret the modern national-break negative: event study of the allocation-
margin sensitivity for electric producers vs rest, around 2012. If the negative
is a pre-existing utility trend (pre-period interactions already negative), it is
a period effect, not a shock effect."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest2.parquet")
g["inv_la"]=g["inv_la"].replace([np.inf,-np.inf],np.nan); g["l_margin"]=g["l_margin"].replace([np.inf,-np.inf],np.nan)
g=g[g.n_seg_fy>=2].dropna(subset=["inv_la","l_margin"]).copy()
for c in ["inv_la","l_margin"]: g[c]=g[c].clip(g[c].quantile(.01),g[c].quantile(.99))
g["rel_inv"]=g["inv_la"]-g.groupby(["gvkey","year"])["inv_la"].transform("mean")
g["rel_opp"]=g["l_margin"]-g.groupby(["gvkey","year"])["l_margin"].transform("mean")
g["elec"]=g["elec"].fillna(0).astype(int)

def es(T,lo,hi):
    d=g[(g.year>=lo)&(g.year<=hi)].copy(); d["k"]=(d.year-T).clip(lo-T,hi-T)
    for k in range(lo-T,hi-T+1):
        if k==-1: continue
        d[f"s{k}"]=d.rel_opp*d.elec*(d.k==k).astype(int)
    sv=[f"s{k}" for k in range(lo-T,hi-T+1) if k!=-1 and d[f"s{k}"].abs().sum()>0]
    # absorb rel_opp main + rel_opp x year (non-elec slope by year) + rel_opp x elec level
    for k in range(lo-T,hi-T+1):
        if k==-1: continue
        d[f"r{k}"]=d.rel_opp*(d.k==k).astype(int)
    rv=[f"r{k}" for k in range(lo-T,hi-T+1) if k!=-1]
    d["roe"]=d.rel_opp*d.elec
    idx=pd.MultiIndex.from_arrays([d.gvkey.values+"_"+d.snms_u,d.year.values])
    X=d[sv+rv+["roe"]].copy(); X.index=idx
    y=pd.Series(d.rel_inv.values,index=idx); cl=pd.DataFrame({"f":d.gvkey.values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    print(f"\nEvent study around {T} (electric x rel_opp x k); N={int(r.nobs):,}")
    for k in range(lo-T,hi-T+1):
        if k==-1: print("  k=-1 (ref)"); continue
        v=f"s{k}"
        if v in r.params.index: print(f"  k={k:+d}  {r.params[v]:+.4f} (t={r.tstats[v]:+.2f})")

es(2012,2006,2017)
