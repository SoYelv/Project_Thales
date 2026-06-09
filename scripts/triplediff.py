#!/usr/bin/env python3
"""Alpha-moderated tests (Prediction 3/4): the post-launch organizational
response should be stronger for high-alpha firms.

Two designs:
  A. Within-electric Post x alpha  (year FE absorbs common SFAS131/dereg shock)
  B. Full-sample triple difference  Treat x Post x alpha
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
alpha = pd.read_parquet(P / "alpha.parquet")
df["lev"]=df["lev"].replace([np.inf,-np.inf],np.nan).clip(0,5)
df["logat"]=df["logat"].replace([np.inf,-np.inf],np.nan)
df["log_nseg"]=np.log1p(df["n_op_seg"])

def zwin(s, lo=0.01, hi=0.99):
    s=s.replace([np.inf,-np.inf],np.nan)
    s=s.clip(s.quantile(lo),s.quantile(hi))
    return (s-s.mean())/s.std()

OUT=["n_op_seg","log_nseg","n_nonop_seg","hhi","multi_seg"]

def within_treated(expo,event_year,lo,hi,acol,event="ELEC1996",controls=("logat","lev"),post_year=None):
    post_year = post_year or event_year
    pre=df[(df.year>=lo)&(df.year<event_year)]
    treat=(pre.groupby("gvkey")[expo].max()>0)
    tr_ids=treat[treat].index
    a=alpha[alpha.event==event][["gvkey",acol]].copy()
    a["alpha"]=zwin(a[acol])
    d=df[(df.year>=lo)&(df.year<=hi)&(df.gvkey.isin(tr_ids))].merge(a[["gvkey","alpha"]],on="gvkey",how="inner")
    d["post"]=(d.year>=post_year).astype(int)
    d["post_alpha"]=d.post*d.alpha
    print(f"\n### WITHIN-{expo.upper()} Post x {acol} (event {event}, post>={post_year}); firms={d.gvkey.nunique()} ###")
    for o in OUT:
        dd=d.dropna(subset=[o,"alpha"]+list(controls))
        sp=dd.groupby("gvkey")["post"].nunique(); dd=dd[dd.gvkey.isin(sp[sp==2].index)]
        if dd.gvkey.nunique()<20: print(f"  {o}: too few"); continue
        m=dd.set_index(["gvkey","year"])
        r=PanelOLS(m[o],m[["post_alpha"]+list(controls)],entity_effects=True,time_effects=True,
                   drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
        b,se,t,p=r.params["post_alpha"],r.std_errors["post_alpha"],r.tstats["post_alpha"],r.pvalues["post_alpha"]
        print(f"  {o:14s} post*alpha={b:+.4f} se={se:.4f} t={t:+.2f} p={p:.3f} N={int(r.nobs):,}")

def triple(expo,event_year,lo,hi,acol,event="ELEC1996",controls=("logat","lev")):
    pre=df[(df.year>=lo)&(df.year<event_year)]
    treat=(pre.groupby("gvkey")[expo].max()>0).astype(int).rename("treat")
    a=alpha[alpha.event==event][["gvkey",acol]].copy(); a["alpha"]=zwin(a[acol])
    d=df[(df.year>=lo)&(df.year<=hi)].merge(treat,on="gvkey",how="inner").merge(a[["gvkey","alpha"]],on="gvkey",how="left")
    d["alpha"]=d["alpha"].fillna(0.0)
    d["post"]=(d.year>=event_year).astype(int)
    d["tp"]=d.treat*d.post; d["tpa"]=d.treat*d.post*d.alpha; d["pa"]=d.post*d.alpha
    print(f"\n### TRIPLE-DIFF {expo} x post x {acol} (event {event}) ###")
    for o in OUT:
        dd=d.dropna(subset=[o]+list(controls))
        m=dd.set_index(["gvkey","year"])
        r=PanelOLS(m[o],m[["tp","tpa","pa"]+list(controls)],entity_effects=True,time_effects=True,
                   drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
        b1,b2=r.params["tp"],r.params["tpa"]; t1,t2=r.tstats["tp"],r.tstats["tpa"]; p2=r.pvalues["tpa"]
        print(f"  {o:14s} b1(tp)={b1:+.3f}(t={t1:+.2f})  b2(tp*alpha)={b2:+.4f}(t={t2:+.2f},p={p2:.3f})  N={int(r.nobs):,}")

print("="*100); print("DESIGN A: within-electric, several alpha proxies"); print("="*100)
for ac in ["a_vol","a_segvol","a_pricebeta","a_share_elec"]:
    within_treated("exp_electric",1996,1988,2004,ac)
print("\n--- robustness: post turn-on at 1998 ---")
within_treated("exp_electric",1996,1988,2004,"a_segvol",post_year=1998)
within_treated("exp_electric",1996,1988,2004,"a_vol",post_year=1998)

print("\n"+"="*100); print("DESIGN B: full-sample triple difference"); print("="*100)
for ac in ["a_segvol","a_vol","a_share_energy"]:
    triple("exp_electric",1996,1988,2004,ac)
