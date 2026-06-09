#!/usr/bin/env python3
"""Capital-allocation RSZ test on a sample fixed by PRE-EVENT multi-segment
status, to remove endogenous selection into the multi-segment sample
(treatment can cause single-segment firms to add segments)."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd

from electricity_identification import add_sgrow, fit_rsz, stacked_rsz_sample

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest.parquet"); fe=pd.read_parquet(P/"firm_event.parquet")
elec=g.loc[g.elec==1,"gvkey"].unique(); fe=fe[fe.gvkey.isin(elec)].drop_duplicates("gvkey")
g=g.merge(fe[["gvkey","event_year"]],on="gvkey",how="inner")
g=add_sgrow(g)

def stacked(oppcol,sample="all_multiseg"):
    return stacked_rsz_sample(g, fe, oppcol, control="notyet", window=(-5, 5), sample=sample)

def run(s,label):
    r=fit_rsz(s)
    b,se,t,p=r.params["rotp"],r.std_errors["rotp"],r.tstats["rotp"],r.pvalues["rotp"]
    print(f"  [{label:38s}] rotp={b:+.4f} (se={se:.4f}, t={t:+.2f}, p={p:.3f}) N={int(r.nobs):,} firms={s.gvkey.nunique()}")

print("="*92); print("RSZ capital allocation: full multi-seg sample vs PRE-EVENT multi-seg (fixed) sample"); print("="*92)
print("\n### opportunity = lagged operating margin ###")
run(stacked("l_margin","all_multiseg"),"all multi-seg firm-years (original)")
run(stacked("l_margin","pre_multiseg"),"PRE-event multi-seg firms only")
print("\n### opportunity = sales growth ###")
run(stacked("sgrow","all_multiseg"),"all multi-seg firm-years (original)")
run(stacked("sgrow","pre_multiseg"),"PRE-event multi-seg firms only")
