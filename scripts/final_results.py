#!/usr/bin/env python3
"""Consolidated final results + tables for the empirical_results memo."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"; T=ROOT/"reports"/"tables"
df=pd.read_parquet(P/"regdata.parquet"); alpha=pd.read_parquet(P/"alpha.parquet")
df["lev"]=df["lev"].replace([np.inf,-np.inf],np.nan).clip(0,5)
df["logat"]=df["logat"].replace([np.inf,-np.inf],np.nan)
df["log_nseg"]=np.log1p(df["n_op_seg"])
df["util_or_energy"]=((df.share_utility>0)|(df.share_energy>0)).astype(int)

def zrank(s): r=s.replace([np.inf,-np.inf],np.nan).rank(pct=True); return (r-r.mean())/r.std()
aE=alpha[alpha.event=="ELEC1996"][["gvkey","a_segvol"]].copy(); aE["alpha"]=zrank(aE["a_segvol"])
pre=df[(df.year>=1990)&(df.year<1996)]; tr=(pre.groupby("gvkey")["exp_electric"].max()>0); tr_ids=tr[tr].index
CT=["logat","lev"]; rows=[]

def fit(d,y,x,key):
    d=d.dropna(subset=[y]+x+CT); m=d.set_index([d.columns[0] if False else "ent","year"])
    r=PanelOLS(m[y],m[x+CT],entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
    return r,r.params[key],r.std_errors[key],r.tstats[key],r.pvalues[key],int(r.nobs)

# ---- Table 1: average DiD, electric vs (a) all, (b) energy/utility controls ----
print("TABLE 1 — Average DiD (treated = pre-1996 electric exposure)")
for ctrl_name,mask in [("vs all firms", df.year.notna()),
                       ("vs energy/utility ctrl", (df.util_or_energy==1)|(df.gvkey.isin(tr_ids)))]:
    d=df[(df.year>=1988)&(df.year<=2004)&mask].copy()
    d["treat"]=d.gvkey.isin(tr_ids).astype(int); d["post"]=(d.year>=1996).astype(int); d["did"]=d.treat*d.post
    d["ent"]=d.gvkey
    for y in ["n_op_seg","log_nseg","multi_seg","hhi","n_nonop_seg"]:
        dd=d.copy(); sp=dd.dropna(subset=[y]+CT).groupby("gvkey")["post"].nunique()
        dd=dd[dd.gvkey.isin(sp[sp==2].index)]
        r,b,se,t,p,n=fit(dd,y,["did"],"did")
        rows.append(dict(table="T1_avgDiD",spec=ctrl_name,outcome=y,coef=b,se=se,t=t,p=p,N=n))
        print(f"  {ctrl_name:24s} {y:14s} DiD={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={n:,}")

# ---- Table 2: within-electric Post x alpha (headline) ----
print("\nTABLE 2 — Within-electric Post x alpha_rank (segment-margin-volatility alpha)")
d=df[(df.year>=1988)&(df.year<=2004)&(df.gvkey.isin(tr_ids))].merge(aE[["gvkey","alpha"]],on="gvkey")
d["post"]=(d.year>=1996).astype(int); d["pa"]=d.post*d.alpha; d["ent"]=d.gvkey
for y in ["n_op_seg","log_nseg","multi_seg","hhi","n_nonop_seg"]:
    dd=d.copy(); sp=dd.dropna(subset=[y]+CT).groupby("gvkey")["post"].nunique(); dd=dd[dd.gvkey.isin(sp[sp==2].index)]
    r,b,se,t,p,n=fit(dd,y,["pa"],"pa")
    rows.append(dict(table="T2_within_alpha",spec="post*alpha_rank",outcome=y,coef=b,se=se,t=t,p=p,N=n))
    print(f"  {y:14s} post*alpha={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={n:,}")

# ---- Table 3: full-sample triple difference with rank alpha ----
print("\nTABLE 3 — Full-sample triple difference: treat x post x alpha_rank")
d=df[(df.year>=1988)&(df.year<=2004)].copy()
d["treat"]=d.gvkey.isin(tr_ids).astype(int); d["post"]=(d.year>=1996).astype(int)
d=d.merge(aE[["gvkey","alpha"]],on="gvkey",how="left"); d["alpha"]=d["alpha"].fillna(0.0)
d["tp"]=d.treat*d.post; d["tpa"]=d.treat*d.post*d.alpha; d["pa"]=d.post*d.alpha; d["ent"]=d.gvkey
for y in ["n_op_seg","log_nseg","multi_seg","hhi"]:
    dd=d.dropna(subset=[y]+CT); m=dd.set_index(["ent","year"])
    r=PanelOLS(m[y],m[["tp","tpa","pa"]+CT],entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
    rows.append(dict(table="T3_triple",spec="tpa",outcome=y,coef=r.params["tpa"],se=r.std_errors["tpa"],t=r.tstats["tpa"],p=r.pvalues["tpa"],N=int(r.nobs)))
    print(f"  {y:14s} b1(tp)={r.params['tp']:+.3f}(t={r.tstats['tp']:+.2f})  b2(tp*alpha)={r.params['tpa']:+.4f}(t={r.tstats['tpa']:+.2f},p={r.pvalues['tpa']:.3f}) N={int(r.nobs):,}")

pd.DataFrame(rows).to_csv(T/"final_results.csv",index=False)
print("\nsaved reports/tables/final_results.csv")
print(f"\nHeadline sample: {len(tr_ids)} electric-exposed firms; alpha = pre-1996 segment op-margin volatility (rank, std).")
