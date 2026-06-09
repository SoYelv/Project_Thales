#!/usr/bin/env python3
"""Track 2: Revelio labor composition under modern staggered electricity shocks.

Outcome = Finance-function share of a firm's US headcount (proxy for treasury /
risk / FP&A / analytics infrastructure, Delv3-2 sec 4.3). Also Finance headcount
and Finance salary.

Modern staggered organized-power-market launches (raise regional power-price
hedgeability), assigned by HQ state:
  ERCOT nodal       2010-12  -> Texas                       (post >= 2011)
  MISO South/Entergy2013-12  -> Arkansas, Louisiana, Miss.  (post >= 2014)
  SPP Integ. Mkt    2014-03  -> Kansas, Oklahoma, Nebraska, N/S Dakota (post >= 2014)
Treated = power firms HQ'd in an event region; controls = not-yet/never-treated
power firms (and, as a check, non-power firms).
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
wf=pd.read_parquet(P/"revelio_wf.parquet")

# firm-year role table -> Finance share & totals
wf["role_k10"]=wf["role_k10"].astype(str)
tot=wf.groupby(["gvkey","yr"]).agg(total=("cnt","sum"),grp=("grp","first"),hq_state=("hq_state","first")).reset_index()
fin=wf[wf.role_k10.eq("Finance")].groupby(["gvkey","yr"]).agg(fin_cnt=("cnt","sum"),fin_sal=("wsal","mean")).reset_index()
d=tot.merge(fin,on=["gvkey","yr"],how="left")
d["fin_cnt"]=d["fin_cnt"].fillna(0.0)
d["fin_share"]=np.where(d.total>0,d.fin_cnt/d.total,np.nan)
d["log_fin"]=np.log1p(d.fin_cnt); d["log_tot"]=np.log1p(d.total)
d=d[d.total>=20]   # firms with a meaningful US presence in Revelio

EVENTS={"ERCOT":(2010,{"Texas"}),
        "MISO_South":(2013,{"Arkansas","Louisiana","Mississippi"}),
        "SPP":(2014,{"Kansas","Oklahoma","Nebraska","South Dakota","North Dakota"})}
state2T={};
for nm,(T,states) in EVENTS.items():
    for s in states: state2T[s]=T
d["event_year"]=d.hq_state.map(state2T)

power=d[d.grp=="power"].copy()
print("Power firm-years:",len(power),"firms:",power.gvkey.nunique())
print("Power firms by event region:")
print(power[power.event_year.notna()].groupby(["event_year"]).gvkey.nunique().to_string())
print("Never-treated power firms:",power[power.event_year.isna()].gvkey.nunique())

def stacked(df,treated_grp="power",ctrl="power_notyet"):
    parts=[]
    for nm,(T,states) in EVENTS.items():
        tr=set(df.loc[(df.grp==treated_grp)&(df.event_year==T),"gvkey"])
        if ctrl=="power_notyet":
            ctl=set(df.loc[(df.grp=="power")&((df.event_year>T)|(df.event_year.isna())),"gvkey"])
        elif ctrl=="nonpower":
            ctl=set(df.loc[df.grp=="control","gvkey"])
        post0 = T+1   # go-lives late in year T -> first full post year T+1
        c=df[(df.yr>=T-4)&(df.yr<=T+4)&(df.gvkey.isin(tr|ctl))].copy()
        c["cohort"]=nm; c["treat"]=c.gvkey.isin(tr).astype(int); c["post"]=(c.yr>=post0).astype(int)
        parts.append(c)
    s=pd.concat(parts,ignore_index=True)
    s["cfirm"]=s.cohort+"_"+s.gvkey; s["cy"]=s.cohort+"_"+s.yr.astype(str)
    return s

def run(s,y,label=""):
    s=s.dropna(subset=[y]).copy(); s["did"]=s.treat*s.post
    cy=pd.get_dummies(s["cy"],prefix="cy",drop_first=True).astype(float)
    idx=pd.MultiIndex.from_arrays([s.cfirm.values,s.yr.values])
    X=pd.concat([s[["did","log_tot"]].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    yy=pd.Series(s[y].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(yy,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    b,se,t,p=r.params["did"],r.std_errors["did"],r.tstats["did"],r.pvalues["did"]
    print(f"  [{label:28s}] {y:10s} DiD={b:+.5f} (se={se:.5f}, t={t:+.2f}, p={p:.3f}) N={int(r.nobs):,} firms={s.gvkey.nunique()}")
    return dict(label=label,outcome=y,coef=b,se=se,t=t,p=p,N=int(r.nobs))

print("\n"+"="*92); print("STACKED DiD — Revelio Finance-share / headcount, power firms, staggered ISO launches"); print("="*92)
res=[]
s=stacked(d,ctrl="power_notyet")
for y in ["fin_share","log_fin","log_tot"]:
    res.append(run(s,y,"power: not-yet ctrl"))
print()
s2=stacked(d,ctrl="nonpower")
for y in ["fin_share","log_fin"]:
    res.append(run(s2,y,"power vs non-power ctrl"))
pd.DataFrame(res).to_csv(ROOT/"reports"/"tables"/"t2_labor.csv",index=False)
print("\nsaved t2_labor.csv")
