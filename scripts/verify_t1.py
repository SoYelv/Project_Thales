#!/usr/bin/env python3
"""Verify Track 1 allocation-sensitivity result: event study + robustness."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd

from electricity_identification import add_sgrow, fit_rsz, fit_rsz_event_study, stacked_rsz_sample

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest.parquet"); fe=pd.read_parquet(P/"firm_event.parquet")
elec=g.loc[g.elec==1,"gvkey"].unique(); fe=fe[fe.gvkey.isin(elec)].drop_duplicates("gvkey")
g=g.merge(fe[["gvkey","event_year"]],on="gvkey",how="inner")
g=add_sgrow(g)

def stack(ctrl="notyet",lo=5,hi=5):
    return stacked_rsz_sample(g, fe, "l_margin", control=ctrl, window=(-lo, hi))

# ---- event study: rel_opp x treat x rel-year ----
print("="*80); print("EVENT STUDY: sensitivity = rel_opp x treat x k (omit k=-1). expect pre~0, post>0"); print("="*80)
s=stack("notyet",5,5)
r=fit_rsz_event_study(s, min_k=-5, max_k=5, ref_k=-1)
for k in range(-5,6):
    if k==-1: print("  k=-1 (ref)"); continue
    v=f"s{k}"
    if v in r.params.index: print(f"  k={k:+d}  {r.params[v]:+.4f} (t={r.tstats[v]:+.2f})")

# ---- robustness grid for rotp ----
print("\n"+"="*80); print("ROBUSTNESS: rotp under control/window/winsor variants"); print("="*80)
def rotp(ctrl,lo,hi):
    s=stack(ctrl,lo,hi)
    rr=fit_rsz(s)
    return rr.params["rotp"],rr.tstats["rotp"],rr.pvalues["rotp"],int(rr.nobs)
for ctrl in ["notyet","never"]:
    for lo,hi in [(5,5),(4,6),(6,8)]:
        b,t,p,n=rotp(ctrl,lo,hi)
        print(f"  ctrl={ctrl:6s} window[-{lo},+{hi}]  rotp={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={n:,}")
