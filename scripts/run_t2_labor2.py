#!/usr/bin/env python3
"""Track 2 (v2): 4-cohort staggered electricity-shock DiD on Revelio labor.

Every power firm is assigned to the FIRST modern electricity derivative/market
shock relevant to it (staggered timing):
  ERCOT nodal      2010 (post>=2011)  HQ Texas
  CME power expan. 2012 (post>=2013)  all other power firms (national)
  MISO South       2013 (post>=2014)  HQ AR/LA/MS
  SPP Integ. Mkt   2014 (post>=2014)  HQ KS/OK/NE/SD/ND
Controls = non-power firms (grp 'control'), entered into each cohort window.
Outcomes: Finance headcount share, log Finance headcount, log total headcount.
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
wf=pd.read_parquet(P/"revelio_wf.parquet")
wf["role_k10"]=wf["role_k10"].astype(str)
tot=wf.groupby(["gvkey","yr"]).agg(total=("cnt","sum"),grp=("grp","first"),hq_state=("hq_state","first")).reset_index()
fin=wf[wf.role_k10.eq("Finance")].groupby(["gvkey","yr"]).agg(fin_cnt=("cnt","sum")).reset_index()
d=tot.merge(fin,on=["gvkey","yr"],how="left"); d["fin_cnt"]=d["fin_cnt"].fillna(0.0)
d["fin_share"]=np.where(d.total>0,d.fin_cnt/d.total,np.nan)
d["log_fin"]=np.log1p(d.fin_cnt); d["log_tot"]=np.log1p(d.total)
d=d[d.total>=20].copy()

ERCOT={"Texas"}; MISO={"Arkansas","Louisiana","Mississippi"}; SPP={"Kansas","Oklahoma","Nebraska","South Dakota","North Dakota"}
def assign(row):
    s=row.hq_state
    if row.grp!="power": return (None,None)
    if s in ERCOT: return ("ERCOT",2010)
    if s in MISO:  return ("MISO",2013)
    if s in SPP:   return ("SPP",2014)
    return ("CME",2012)   # national power expansion for all other power firms
d["cohort_nm"],d["event_year"]=zip(*d.apply(assign,axis=1))
pw=d[d.grp=="power"]
print("Power firms by cohort:")
print(pw.dropna(subset=['event_year']).groupby('cohort_nm').gvkey.nunique().to_string())

COH={"ERCOT":2010,"CME":2012,"MISO":2013,"SPP":2014}
def stacked():
    parts=[]
    for nm,T in COH.items():
        tr=set(d.loc[(d.grp=="power")&(d.cohort_nm==nm),"gvkey"])
        ctl=set(d.loc[d.grp=="control","gvkey"])
        post0=T+1
        c=d[(d.yr>=T-4)&(d.yr<=T+4)&(d.gvkey.isin(tr|ctl))].copy()
        c["cohort"]=nm; c["treat"]=c.gvkey.isin(tr).astype(int); c["post"]=(c.yr>=post0).astype(int)
        parts.append(c)
    s=pd.concat(parts,ignore_index=True); s["cfirm"]=s.cohort+"_"+s.gvkey; s["cy"]=s.cohort+"_"+s.yr.astype(str)
    return s

def run(s,y,ctrl_var=True,label=""):
    s=s.dropna(subset=[y]).copy(); s["did"]=s.treat*s.post
    cy=pd.get_dummies(s["cy"],prefix="cy",drop_first=True).astype(float)
    cols=["did"]+(["log_tot"] if (ctrl_var and y!="log_tot") else [])
    idx=pd.MultiIndex.from_arrays([s.cfirm.values,s.yr.values])
    X=pd.concat([s[cols].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    yy=pd.Series(s[y].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(yy,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    b,se,t,p=r.params["did"],r.std_errors["did"],r.tstats["did"],r.pvalues["did"]
    print(f"  [{label:22s}] {y:10s} DiD={b:+.5f} (se={se:.5f}, t={t:+.2f}, p={p:.3f}) N={int(r.nobs):,} firms={s.gvkey.nunique()} treated={int(s.treat.sum()>0 and s[s.treat==1].gvkey.nunique())}")
    return r

print("\n"+"="*92); print("4-COHORT STACKED DiD — Revelio Finance, power vs non-power, staggered electricity shocks"); print("="*92)
s=stacked()
for y in ["fin_share","log_fin","log_tot"]:
    run(s,y,label="power vs control")
