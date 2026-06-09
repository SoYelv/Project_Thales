#!/usr/bin/env python3
"""Track 1 main result: stacked DiD on internal capital-allocation sensitivity.

Stacked cohorts (Cengiz et al.) across electricity events 1996/1998/1999.
Treated = electric firms in the region whose hub launches in year T.
Controls = not-yet-treated / never-treated electric firms (event_year>T or NaN).
Outcome  = segment investment (capx / lagged assets).
Key term = l_margin x post x treat  -> investment-to-profitability sensitivity.
Prediction (Delv3-2 sec 4.3): treated firms allocate MORE to high-margin
segments post-shock (positive); stronger for high-alpha firms.
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest.parquet")
fe=pd.read_parquet(P/"firm_event.parquet")
alpha=pd.read_parquet(P/"alpha.parquet")

def zrank(s): r=s.replace([np.inf,-np.inf],np.nan).rank(pct=True); return (r-r.mean())/r.std()
aE=alpha[alpha.event=="ELEC1996"][["gvkey","a_segvol"]].copy(); aE["alpha"]=zrank(aE["a_segvol"])

elec_firms=g.loc[g.elec==1,"gvkey"].unique()
fe=fe[fe.gvkey.isin(elec_firms)].drop_duplicates("gvkey")
g=g.merge(fe[["gvkey","region","event_year"]],on="gvkey",how="inner")
g=g.merge(aE[["gvkey","alpha"]],on="gvkey",how="left")
# winsorize
g["inv_la"]=g["inv_la"].replace([np.inf,-np.inf],np.nan)
g["l_margin"]=g["l_margin"].replace([np.inf,-np.inf],np.nan)
g=g.dropna(subset=["inv_la","l_margin"])
g["inv_la"]=g["inv_la"].clip(g["inv_la"].quantile(.01),g["inv_la"].quantile(.99))
g["l_margin"]=g["l_margin"].clip(g["l_margin"].quantile(.01),g["l_margin"].quantile(.99))
g["l_logassets"]=np.log(g["l_ias"].clip(lower=1e-3))
g["segid"]=g["gvkey"]+"_"+g["snms_u"]

EVENTS=[1996,1998,1999]
def build_stacked(control="notyet"):
    parts=[]
    for T in EVENTS:
        treated=set(fe.loc[fe.event_year==T,"gvkey"])
        if control=="notyet":
            ctrl=set(fe.loc[(fe.event_year>T)|(fe.event_year.isna()),"gvkey"])
        else:  # never-treated only (Other/NE)
            ctrl=set(fe.loc[fe.event_year.isna(),"gvkey"])
        d=g[(g.year>=T-5)&(g.year<=T+5)&(g.gvkey.isin(treated|ctrl))].copy()
        d["cohort"]=T; d["treat"]=d.gvkey.isin(treated).astype(int)
        d["post"]=(d.year>=T).astype(int)
        parts.append(d)
    s=pd.concat(parts,ignore_index=True)
    s["cohort_seg"]=s["cohort"].astype(str)+"_"+s["segid"]
    s["cohort_year"]=s["cohort"].astype(str)+"_"+s["year"].astype(str)
    return s

def run(s,alpha_mod=False,label=""):
    s=s.dropna(subset=["l_logassets"]).copy()
    s["m"]=s["l_margin"]; s["mp"]=s.m*s.post; s["mt"]=s.m*s.treat
    s["mtp"]=s.m*s.treat*s.post; s["tp"]=s.treat*s.post
    cy=pd.get_dummies(s["cohort_year"],prefix="cy",drop_first=True).astype(float)
    base=["m","mp","mt","mtp","tp","l_logassets"]
    X=pd.concat([s[base].reset_index(drop=True),cy.reset_index(drop=True)],axis=1)
    if alpha_mod:
        s["a"]=s["alpha"].fillna(0.0)
        for nm,expr in [("ma",s.m*s.a),("mta",s.m*s.treat*s.a),("mpa",s.m*s.post*s.a),
                        ("mtpa",s.m*s.treat*s.post*s.a),("tpa",s.treat*s.post*s.a)]:
            s[nm]=expr; X[nm]=s[nm].values
    idx=pd.MultiIndex.from_arrays([s["cohort_seg"].values,s["year"].values])
    y=pd.Series(s["inv_la"].values,index=idx,name="inv_la")
    X.index=idx
    clusters=pd.DataFrame({"f":s["gvkey"].values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(
        cov_type="clustered",clusters=clusters)
    show=["mtp"]+(["mtpa"] if alpha_mod else [])
    print(f"\n[{label}] N={int(r.nobs):,} cohort-segs={s.cohort_seg.nunique():,} firms={s.gvkey.nunique()}")
    for k in show+["mp","mt","m","tp"]:
        if k in r.params.index:
            print(f"   {k:6s} {r.params[k]:+.4f} (se={r.std_errors[k]:.4f}, t={r.tstats[k]:+.2f}, p={r.pvalues[k]:.3f})")
    return r

print("="*90); print("STACKED DiD — capital-allocation sensitivity (inv = capx/lagged assets)")
print("key term mtp = l_margin x treat x post ; prediction > 0"); print("="*90)
s1=build_stacked("notyet"); run(s1,label="not-yet-treated controls")
s2=build_stacked("never"); run(s2,label="never-treated controls")
print("\n--- alpha-moderated (mtpa = l_margin x treat x post x alpha) ---")
run(s1,alpha_mod=True,label="not-yet-treated + alpha")
