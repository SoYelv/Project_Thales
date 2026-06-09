#!/usr/bin/env python3
"""Track 2 (faithful): treasury/risk/analytics hiring under staggered electricity
shocks. Outcome = riskfin share of hiring & riskfin intensity (per headcount).
riskfin = Financial/Investment/Energy Analyst, Banking Analyst, Commodity Trader,
Compliance Auditor, Security Analyst (treasury/risk/FP&A/analytics proxy, sec 4.3).
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
roles=pd.read_parquet(P/"revelio_roles.parquet")
link=pd.read_parquet(P/"revelio_link.parquet")[["rcid","gvkey","grp","hq_state"]]
wf=pd.read_parquet(P/"revelio_wf.parquet")
roles["rcid"]=roles["rcid"].astype(int)
piv=roles.pivot_table(index=["rcid","yr"],columns="bucket",values="hires",aggfunc="sum",fill_value=0).reset_index()
for c in ["riskfin","accounting","other"]:
    if c not in piv: piv[c]=0.0
piv["tot_hire"]=piv[["riskfin","accounting","other"]].sum(axis=1)
piv["rf_share"]=np.where(piv.tot_hire>0,piv.riskfin/piv.tot_hire,np.nan)
piv["log_rf"]=np.log1p(piv.riskfin)
# total headcount from workforce for intensity
tot=wf.groupby(["gvkey","yr"]).agg(total=("cnt","sum")).reset_index()
d=piv.merge(link,on="rcid",how="left").merge(tot,on=["gvkey","yr"],how="left")
d["total"]=pd.to_numeric(d["total"],errors="coerce")
d["rf_intensity"]=np.where(d.total.fillna(0)>0,d.riskfin/d.total.replace(0,np.nan),np.nan)
d["log_tot"]=np.log1p(d.total)
d=d[(d.tot_hire>=3)].copy()   # firm-years with meaningful hiring

ERCOT={"Texas"}; MISO={"Arkansas","Louisiana","Mississippi"}; SPP={"Kansas","Oklahoma","Nebraska","South Dakota","North Dakota"}
def assign(r):
    if r.grp!="power": return (None,None)
    if r.hq_state in ERCOT: return ("ERCOT",2010)
    if r.hq_state in MISO:  return ("MISO",2013)
    if r.hq_state in SPP:   return ("SPP",2014)
    return ("CME",2012)
d["cohort_nm"],d["event_year"]=zip(*d.apply(assign,axis=1))
print("power firm-years:",(d.grp=='power').sum(),"control firm-years:",(d.grp=='control').sum())
print("riskfin hires total:",int(d.riskfin.sum()),"| mean rf_share:",round(d.rf_share.mean(),3))

COH={"ERCOT":2010,"CME":2012,"MISO":2013,"SPP":2014}
def stacked(ctrl="control"):
    parts=[]
    for nm,T in COH.items():
        tr=set(d.loc[(d.grp=="power")&(d.cohort_nm==nm),"gvkey"])
        if ctrl=="control": ctl=set(d.loc[d.grp=="control","gvkey"])
        else: ctl=set(d.loc[(d.grp=="power")&((d.cohort_nm.map(COH)>T)|(d.cohort_nm.isna())),"gvkey"])
        c=d[(d.yr>=T-4)&(d.yr<=T+4)&(d.gvkey.isin(tr|ctl))].copy()
        c["cohort"]=nm; c["treat"]=c.gvkey.isin(tr).astype(int); c["post"]=(c.yr>=T+1).astype(int)
        parts.append(c)
    s=pd.concat(parts,ignore_index=True); s["cfirm"]=s.cohort+"_"+s.gvkey; s["cy"]=s.cohort+"_"+s.yr.astype(str)
    return s

def run(s,y,label=""):
    s=s.dropna(subset=[y]).copy(); s["did"]=s.treat*s.post
    cy=pd.get_dummies(s["cy"],prefix="cy",drop_first=True).astype(float)
    idx=pd.MultiIndex.from_arrays([s.cfirm.values,s.yr.values])
    X=pd.concat([s[["did"]].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    yy=pd.Series(s[y].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(yy,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    b,se,t,p=r.params["did"],r.std_errors["did"],r.tstats["did"],r.pvalues["did"]
    nt=s[s.treat==1].gvkey.nunique()
    print(f"  [{label:26s}] {y:13s} DiD={b:+.5f} (se={se:.5f}, t={t:+.2f}, p={p:.3f}) N={int(r.nobs):,} treated_firms={nt}")
    return dict(label=label,outcome=y,coef=b,se=se,t=t,p=p,N=int(r.nobs))

print("\n"+"="*94); print("STACKED DiD — treasury/risk/analytics hiring, staggered electricity shocks"); print("="*94)
res=[]
s=stacked("control")
for y in ["rf_share","rf_intensity","log_rf"]:
    res.append(run(s,y,"power vs non-power"))
print()
s2=stacked("notyet")
for y in ["rf_share","rf_intensity"]:
    res.append(run(s2,y,"power: not-yet ctrl"))
pd.DataFrame(res).to_csv(ROOT/"reports"/"tables"/"t2_roles.csv",index=False)
print("\nsaved t2_roles.csv")
