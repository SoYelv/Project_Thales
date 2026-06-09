#!/usr/bin/env python3
"""Pull Revelio workforce composition for power/energy + control firms.

treated universe = power/utility firms; plus energy and a non-energy control
sample. Aggregate workforce_dynamics_geo to rcid-year-role_k10 (US), with
headcount and headcount-weighted salary. Output reports/panel/revelio_wf.parquet
and the gvkey<->rcid link reports/panel/revelio_link.parquet.
"""
from __future__ import annotations
import signal
from pathlib import Path
import numpy as np, pandas as pd, wrds

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
signal.signal(signal.SIGALRM, lambda s,f:(_ for _ in ()).throw(TimeoutError())); signal.alarm(1500)

fy=pd.read_parquet(P/"firmyear.parquet")
company=pd.read_parquet(P/"company.parquet")
company["sicn"]=pd.to_numeric(company["sic"],errors="coerce")

ever=fy.groupby("gvkey")[["exp_electric","exp_utility","exp_energy"]].max()
power=set(ever[(ever.exp_electric==1)|(ever.exp_utility==1)].index)
power|=set(company.loc[(company.sicn>=4900)&(company.sicn<=4999),"gvkey"])
energy=set(ever[ever.exp_energy==1].index)|set(company.loc[(company.sicn==1311)|((company.sicn>=1380)&(company.sicn<=1389))|(company.sicn==2911),"gvkey"])
allgv=set(fy.gvkey)|set(company.gvkey)
np.random.seed(7)
nonenergy=list(allgv-power-energy)
ctrl_sample=set(np.random.choice(nonenergy,size=min(3000,len(nonenergy)),replace=False))
universe=power|energy|ctrl_sample
print(f"universe: power={len(power)} energy={len(energy)} ctrl={len(ctrl_sample)} total={len(universe)}")

db=wrds.Connection(); print("connected")
cm=db.raw_sql("select rcid,gvkey,ticker,hq_state,hq_country from revelio_common.company_mapping where gvkey is not null")
cm["gvkey"]=cm["gvkey"].astype(str).str.zfill(6)
cm=cm[cm.gvkey.isin(universe)].dropna(subset=["rcid"]).drop_duplicates("gvkey")
cm["rcid"]=cm["rcid"].astype(int)
cm["grp"]=np.where(cm.gvkey.isin(power),"power",np.where(cm.gvkey.isin(energy),"energy","control"))
cm.to_parquet(P/"revelio_link.parquet",index=False)
print(f"linked rcids: {len(cm)} (power={ (cm.grp=='power').sum() }, energy={(cm.grp=='energy').sum()}, control={(cm.grp=='control').sum()})")

rcids=cm["rcid"].tolist()
def chunks(l,n):
    for i in range(0,len(l),n): yield l[i:i+n]
out=[]
for i,ch in enumerate(chunks(rcids,400)):
    ids=",".join(map(str,ch))
    q=f"""select rcid, extract(year from datemonth)::int as yr, role_k10,
                 sum(count) as cnt, sum(count*salary)/nullif(sum(count),0) as wsal
          from revelio_workforce_dynamics.workforce_dynamics_geo
          where rcid in ({ids}) and country='United States'
            and datemonth between '2007-01-01' and '2021-12-31'
          group by rcid, yr, role_k10"""
    out.append(db.raw_sql(q))
    if i%5==0: print(f"  batch {i}: cumulative rows={sum(len(o) for o in out):,}")
wf=pd.concat(out,ignore_index=True)
wf=wf.merge(cm[["rcid","gvkey","grp","hq_state"]],on="rcid",how="left")
wf.to_parquet(P/"revelio_wf.parquet",index=False)
print(f"workforce rows: {len(wf):,}; firms={wf.gvkey.nunique()}; years {wf.yr.min()}-{wf.yr.max()}")
print(wf.groupby("role_k10")["cnt"].sum().sort_values(ascending=False).round(0).to_string())
db.close()
