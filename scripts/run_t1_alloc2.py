#!/usr/bin/env python3
"""Track 1 (v2): internal capital allocation via the Rajan-Servaes-Zingales /
Shin-Stulz *relative* sensitivity, restricted to multi-segment firms.

For each segment in a multi-segment firm-year:
  rel_inv  = inv_j  - firm-year mean(inv)
  rel_opp  = opp_j  - firm-year mean(opp)     opp in {lagged margin, sales growth}
Internal-allocation sensitivity = slope of rel_inv on rel_opp (capital flows to
the better-prospect segment). DiD: does it rise for treated firms post-shock?
Key term: rel_opp x treat x post  (Delv3-2 sec 4.3, prediction > 0).
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd

from electricity_identification import add_sgrow, fit_rsz, stacked_rsz_sample

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest.parquet"); fe=pd.read_parquet(P/"firm_event.parquet")
alpha=pd.read_parquet(P/"alpha.parquet")
def zrank(s): r=s.replace([np.inf,-np.inf],np.nan).rank(pct=True); return (r-r.mean())/r.std()
aE=alpha[alpha.event=="ELEC1996"][["gvkey","a_segvol"]].copy(); aE["alpha"]=zrank(aE["a_segvol"])

elec=g.loc[g.elec==1,"gvkey"].unique()
fe=fe[fe.gvkey.isin(elec)].drop_duplicates("gvkey")
g=g.merge(fe[["gvkey","region","event_year"]],on="gvkey",how="inner").merge(aE[["gvkey","alpha"]],on="gvkey",how="left")
g=add_sgrow(g)

def stacked(oppcol):
    return stacked_rsz_sample(g, fe, oppcol, control="notyet", window=(-5, 5))

def run(s,alpha_mod=False,label=""):
    r=fit_rsz(s, alpha_mod=alpha_mod)
    key=["rotp"]+(["rotpa"] if alpha_mod else [])
    print(f"\n[{label}] N={int(r.nobs):,} firms={s.gvkey.nunique()} cohort-segs={s.cseg.nunique():,}")
    for k in key+["rop","rot","ro"]:
        if k in r.params.index:
            print(f"   {k:6s} {r.params[k]:+.4f} (se={r.std_errors[k]:.4f}, t={r.tstats[k]:+.2f}, p={r.pvalues[k]:.3f})")
    return r

print("="*90); print("RSZ relative-investment sensitivity, strict hub-state electric firms, stacked DiD")
print("key rotp = rel_opp x treat x post (prediction > 0)"); print("="*90)
print("\n### opportunity = lagged segment operating margin ###")
run(stacked("l_margin"),label="margin")
run(stacked("l_margin"),alpha_mod=True,label="margin + alpha")
print("\n### opportunity = segment sales growth ###")
run(stacked("sgrow"),label="sales growth")
run(stacked("sgrow"),alpha_mod=True,label="sales growth + alpha")
