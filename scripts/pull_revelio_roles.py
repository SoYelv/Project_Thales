#!/usr/bin/env python3
"""Pull finer finance/risk/analytics role hire-counts from revelio_individual.
Outcome bucket: treasury/risk/analytics roles (role_k50 Financial Analyst,
Banking Analyst, Compliance Auditor; plus energy/commodity/investment analysts).
Counts position spells STARTING in each year (inflow into the role) per firm.
Output reports/panel/revelio_roles.parquet (rcid, yr, bucket, hires).
"""
from __future__ import annotations
import signal
from pathlib import Path
import numpy as np, pandas as pd, wrds
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
signal.signal(signal.SIGALRM, lambda s,f:(_ for _ in ()).throw(TimeoutError())); signal.alarm(2400)
link=pd.read_parquet(P/"revelio_link.parquet"); rcids=link["rcid"].astype(int).tolist()
db=wrds.Connection(); print("connected; rcids",len(rcids))
# role map: k17000 -> k50/k150
lk=db.raw_sql("select role_k17000_v3, role_k50_v3, role_k150_v3 from revelio_individual.individual_role_lookup_v3")
lk["role_k50_v3"]=lk["role_k50_v3"].astype("string").fillna("")
lk["role_k150_v3"]=lk["role_k150_v3"].astype("string").fillna("")
risk_k50={'Financial Analyst','Banking Analyst','Compliance Auditor'}
risk_k150={'Investment Analyst','Energy Analyst','Commodity Trader','Financial Analyst','Security Analyst'}
is_risk=lk.role_k50_v3.isin(risk_k50)|lk.role_k150_v3.isin(risk_k150)
lk["bucket"]=np.where(is_risk,"riskfin",np.where(lk.role_k50_v3.eq('Accounting'),"accounting","other"))
codes=lk.loc[lk.bucket.ne("other"),["role_k17000_v3","bucket"]].dropna()
print("target role codes:",len(codes))
def chunks(l,n):
    for i in range(0,len(l),n): yield l[i:i+n]
out=[]
for i,ch in enumerate(chunks(rcids,300)):
    ids=",".join(map(str,ch))
    q=f"""select rcid, extract(year from startdate)::int as yr, role_k17000_v3, count(*) hires
          from revelio_individual.individual_positions
          where rcid in ({ids}) and country='United States'
            and startdate between '2006-01-01' and '2020-12-31'
            and role_k17000_v3 is not null
          group by rcid, yr, role_k17000_v3"""
    out.append(db.raw_sql(q))
    if i%3==0: print(f"  batch {i} cum rows={sum(len(o) for o in out):,}")
pos=pd.concat(out,ignore_index=True)
pos=pos.merge(lk[["role_k17000_v3","bucket"]],on="role_k17000_v3",how="left")
agg=pos.groupby(["rcid","yr","bucket"],as_index=False)["hires"].sum()
agg.to_parquet(P/"revelio_roles.parquet",index=False)
print("saved revelio_roles.parquet rows",len(agg),"firms",agg.rcid.nunique())
print(agg.groupby("bucket")["hires"].sum().to_string())
db.close()
