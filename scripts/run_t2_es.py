#!/usr/bin/env python3
"""Focused Revelio checks: event study (ERCOT 2010 & pooled), coverage screen,
and finance-salary-share outcome."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
wf=pd.read_parquet(P/"revelio_wf.parquet"); wf["role_k10"]=wf["role_k10"].astype(str)
roles=pd.read_parquet(P/"revelio_roles.parquet"); roles["rcid"]=roles["rcid"].astype(int)
link=pd.read_parquet(P/"revelio_link.parquet")[["rcid","gvkey","grp","hq_state"]]

tot=wf.groupby(["gvkey","yr"]).agg(total=("cnt","sum"),fin_sal=("wsal","mean"),grp=("grp","first"),hq_state=("hq_state","first")).reset_index()
fin=wf[wf.role_k10.eq("Finance")].groupby(["gvkey","yr"]).agg(fin_cnt=("cnt","sum")).reset_index()
allsal=wf.groupby(["gvkey","yr"]).apply(lambda x:(x.wsal*x.cnt).sum()/x.cnt.sum(),include_groups=False).rename("avg_sal").reset_index()
d=tot.merge(fin,on=["gvkey","yr"],how="left"); d["fin_cnt"]=d["fin_cnt"].fillna(0.0)
d["fin_share"]=np.where(d.total>0,d.fin_cnt/d.total,np.nan)
piv=roles.pivot_table(index=["rcid","yr"],columns="bucket",values="hires",aggfunc="sum",fill_value=0).reset_index()
for c in ["riskfin","accounting","other"]:
    if c not in piv: piv[c]=0.0
piv["tot_hire"]=piv[["riskfin","accounting","other"]].sum(axis=1)
piv["rf_share"]=np.where(piv.tot_hire>0,piv.riskfin/piv.tot_hire,np.nan)
piv=piv.merge(link[["rcid","gvkey"]],on="rcid",how="left")
d=d.merge(piv[["gvkey","yr","rf_share","tot_hire"]],on=["gvkey","yr"],how="left")

def es(event_states,T,outcome,cov=0,label=""):
    treated=set(d.loc[(d.grp=="power")&(d.hq_state.isin(event_states)),"gvkey"])
    ctl=set(d.loc[d.grp=="control","gvkey"])
    s=d[(d.yr>=T-5)&(d.yr<=T+5)&(d.gvkey.isin(treated|ctl))].copy()
    if cov: s=s[s.total>=cov]
    s=s.dropna(subset=[outcome])
    s["treat"]=s.gvkey.isin(treated).astype(int); s["k"]=(s.yr-T).clip(-5,5)
    for k in range(-5,6):
        if k==-1: continue
        s[f"d{k}"]=((s.k==k)&(s.treat==1)).astype(int)
    dv=[f"d{k}" for k in range(-5,6) if k!=-1 and s[f"d{k}"].sum()>=3]
    idx=pd.MultiIndex.from_arrays([s.gvkey.values,s.yr.values])
    X=s[dv].copy(); X.index=idx
    yy=pd.Series(s[outcome].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(yy,X,entity_effects=True,time_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    print(f"\n[{label}] outcome={outcome} T={T} treated={s[s.treat==1].gvkey.nunique()} N={int(r.nobs):,}")
    for k in range(-5,6):
        if k==-1: print("  k=-1 (ref)"); continue
        v=f"d{k}"
        if v in r.params.index: print(f"  k={k:+d}  {r.params[v]:+.5f} (t={r.tstats[v]:+.2f})")

ERCOT={"Texas"}
es(ERCOT,2010,"fin_share",label="ERCOT fin_share")
es(ERCOT,2010,"rf_share",label="ERCOT rf_share")
es(ERCOT,2010,"fin_share",cov=50,label="ERCOT fin_share cov>=50")

# simple DiD on finance salary share (avg finance salary relative) restricted to covered firms
print("\n--- simple power-vs-control DiD at CME2012, well-covered firms (total>=50) ---")
def did(outcome,T=2012,cov=50):
    treated=set(d.loc[(d.grp=="power"),"gvkey"]); ctl=set(d.loc[d.grp=="control","gvkey"])
    s=d[(d.yr>=T-4)&(d.yr<=T+4)&(d.gvkey.isin(treated|ctl))].copy()
    s=s[s.total>=cov].dropna(subset=[outcome])
    s["treat"]=s.gvkey.isin(treated).astype(int); s["post"]=(s.yr>=T+1).astype(int); s["did"]=s.treat*s.post
    idx=pd.MultiIndex.from_arrays([s.gvkey.values,s.yr.values]); X=s[["did"]].copy(); X.index=idx
    yy=pd.Series(s[outcome].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(yy,X,entity_effects=True,time_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    print(f"  {outcome:11s} DiD={r.params['did']:+.5f} (t={r.tstats['did']:+.2f}, p={r.pvalues['did']:.3f}) N={int(r.nobs):,} treated={s[s.treat==1].gvkey.nunique()}")
for o in ["fin_share","rf_share"]: did(o)
