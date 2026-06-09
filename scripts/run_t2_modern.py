#!/usr/bin/env python3
"""Revelio labor retry with mechanism-valid modern derivative shocks.
Shocks: Nodal Exchange 2009 (post>=2010), CME 2012 power suite (post>=2013).
Treatments: power producer; continuous electricity-input intensity; high-intensity.
Outcomes: Finance headcount share; treasury/risk/analytics hiring share; finance salary.
Designs: power vs non-power; continuous-intensity whole universe; event studies.
"""
from __future__ import annotations
import warnings, sys
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
sys.path.insert(0,str(ROOT/"scripts"))
from build_intensity import elec_intensity
wf=pd.read_parquet(P/"revelio_wf.parquet"); wf["role_k10"]=wf["role_k10"].astype(str)
roles=pd.read_parquet(P/"revelio_roles.parquet"); roles["rcid"]=roles["rcid"].astype(int)
link=pd.read_parquet(P/"revelio_link.parquet")[["rcid","gvkey","grp"]]
company=pd.read_parquet(P/"company.parquet"); company["sicn"]=pd.to_numeric(company["sic"],errors="coerce")
company["elec_int"]=company["sicn"].map(elec_intensity)

tot=wf.groupby(["gvkey","yr"]).agg(total=("cnt","sum"),grp=("grp","first")).reset_index()
fin=wf[wf.role_k10.eq("Finance")].groupby(["gvkey","yr"]).agg(fin_cnt=("cnt","sum"),fin_sal=("wsal","mean")).reset_index()
d=tot.merge(fin,on=["gvkey","yr"],how="left"); d["fin_cnt"]=d["fin_cnt"].fillna(0.0)
d["fin_share"]=np.where(d.total>0,d.fin_cnt/d.total,np.nan); d["log_fin"]=np.log1p(d.fin_cnt)
piv=roles.pivot_table(index=["rcid","yr"],columns="bucket",values="hires",aggfunc="sum",fill_value=0).reset_index()
for c in ["riskfin","accounting","other"]:
    if c not in piv: piv[c]=0.0
piv["th"]=piv[["riskfin","accounting","other"]].sum(axis=1)
piv["rf_share"]=np.where(piv.th>0,piv.riskfin/piv.th,np.nan)
piv=piv.merge(link[["rcid","gvkey"]],on="rcid",how="left")
d=d.merge(piv[["gvkey","yr","rf_share","th"]],on=["gvkey","yr"],how="left")
d=d.merge(company[["gvkey","elec_int","sicn"]].drop_duplicates("gvkey"),on="gvkey",how="left")
d=d[d.total>=20].copy()
d["int_z"]=(d.elec_int-d.elec_int.mean())/d.elec_int.std()
d["power"]=(d.grp=="power").astype(int); d["highint"]=(d.elec_int>=3).astype(int)
d["log_tot"]=np.log1p(d.total)

def did(shock_T,treatcol,outcome,binary=True,ctrl="nonpower",lo=None,hi=None):
    lo=lo or shock_T-4; hi=hi or shock_T+4
    if ctrl=="nonpower": pool=d[(d.power==1)|(d.grp=="control")]
    else: pool=d
    s=pool[(pool.yr>=lo)&(pool.yr<=hi)].copy()
    s["T"]=s[treatcol] if not binary else s[treatcol].astype(float)
    s["post"]=(s.yr>=shock_T+1).astype(int); s["did"]=s["T"]*s.post
    s=s.dropna(subset=[outcome,"T"])
    idx=pd.MultiIndex.from_arrays([s.gvkey.values,s.yr.values]); X=s[["did"]].copy(); X.index=idx
    y=pd.Series(s[outcome].values,index=idx); cl=pd.DataFrame({"f":s.gvkey.values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,time_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    b,t,p=r.params["did"],r.tstats["did"],r.pvalues["did"]; flag=" *" if p<0.10 else ""
    print(f"  {treatcol:9s} x post>={shock_T+1} -> {outcome:10s} DiD={b:+.5f} (t={t:+.2f}, p={p:.3f}) N={int(r.nobs):,}{flag}")

print("="*92); print("REVELIO LABOR — modern valid shocks (Nodal 2009, CME 2012)"); print("="*92)
for T in [2009,2012]:
    print(f"\n-- shock {T} --")
    for out in ["fin_share","rf_share","log_fin"]:
        did(T,"power",out,binary=True)
    for out in ["fin_share","rf_share"]:
        did(T,"int_z",out,binary=False)
        did(T,"highint",out,binary=True)

# event study: power outcomes around 2012
print("\n-- event study: power x relative year, residualized by firm and year --")
def twfe_residual(series, firm, year):
    return (series
            - series.groupby(firm).transform("mean")
            - series.groupby(year).transform("mean")
            + series.mean())

def cluster_ols(y, x, cluster):
    cluster=pd.Series(cluster).reset_index(drop=True)
    xmat=x.to_numpy(dtype=float)
    yvec=y.to_numpy(dtype=float)
    bread=np.linalg.pinv(xmat.T@xmat)
    beta=bread@(xmat.T@yvec)
    resid=yvec-xmat@beta
    meat=np.zeros((xmat.shape[1],xmat.shape[1]))
    for _,idx in pd.Series(np.arange(len(cluster))).groupby(cluster).groups.items():
        loc=np.asarray(list(idx))
        score=xmat[loc].T@resid[loc]
        meat+=np.outer(score,score)
    g=cluster.nunique(); n=len(yvec); k=xmat.shape[1]
    adj=(g/(g-1))*((n-1)/(n-k)) if g>1 and n>k else 1.0
    vcov=adj*bread@meat@bread
    se=np.sqrt(np.diag(vcov))
    return beta,se

def es(T,out,lo,hi):
    pool=d[(d.power==1)|(d.grp=="control")]; s=pool[(pool.yr>=lo)&(pool.yr<=hi)].dropna(subset=[out]).copy()
    s["k"]=(s.yr-T)
    for k in range(lo-T,hi-T+1):
        if k==-1: continue
        s[f"d{k}"]=((s.k==k)&(s.power==1)).astype(int)
    dv=[f"d{k}" for k in range(lo-T,hi-T+1) if k!=-1 and s[f"d{k}"].sum()>=5]
    y=twfe_residual(s[out],s.gvkey,s.yr)
    x=s[dv].apply(lambda col: twfe_residual(col,s.gvkey,s.yr))
    beta,se=cluster_ols(y,x,s.gvkey)
    print(f"\n  {out} around {T}:")
    bmap=dict(zip(dv,beta)); semap=dict(zip(dv,se))
    for k in range(lo-T,hi-T+1):
        if k==-1: print("   k=-1 (ref)"); continue
        v=f"d{k}"
        if v in bmap:
            t=bmap[v]/semap[v] if semap[v]>0 else np.nan
            print(f"   k={k:+d} {bmap[v]:+.5f} (t={t:+.2f})")
es(2012,"fin_share",2008,2017)
es(2012,"rf_share",2008,2017)
