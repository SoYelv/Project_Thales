#!/usr/bin/env python3
"""Segment-coverage diagnostics: how many segments do treated vs control firms
have, and how do they compare to the full universe of multi-segment firms?"""
from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
fy=pd.read_parquet(P/"firmyear.parquet")
fe=pd.read_parquet(P/"firm_event.parquet")
sinv=pd.read_parquet(P/"seg_invest.parquet")
fy["year"]=fy["year"].astype("Int64")
fy=fy[fy.year.notna()].copy(); fy["year"]=fy["year"].astype(int)

def prof(df,name):
    n=df["n_op_seg"]
    return dict(group=name, firms=df.gvkey.nunique(), firm_years=len(df),
        mean_seg=round(n.mean(),2), median_seg=int(n.median()) if len(n) else 0,
        pct_multi=round((n>=2).mean()*100,1), pct_3plus=round((n>=3).mean()*100,1),
        pct_4plus=round((n>=4).mean()*100,1),
        mean_seg_if_multi=round(n[n>=2].mean(),2) if (n>=2).any() else np.nan)

# --- universe benchmarks ---
rows=[prof(fy,"UNIVERSE: all firm-years"),
      prof(fy[fy.n_op_seg>=2],"UNIVERSE: multi-segment firm-years")]

# --- Track 1: electric firms, event-assigned, in stacked windows ---
elec=set(fy.loc[fy.exp_electric==1,"gvkey"]) | set(sinv.loc[sinv.elec==1,"gvkey"])
fed=fe.drop_duplicates("gvkey").set_index("gvkey")
def assigned(gv): return fed.event_year.get(gv,np.nan)
fy_e=fy[fy.gvkey.isin(elec)].copy()
fy_e["event_year"]=fy_e.gvkey.map(lambda g: fed.event_year.get(g,np.nan))
EV=[1996,1998,1999]
# build stacked window membership
treat_parts=[]; ctrl_parts=[]
for T in EV:
    tr=fy_e[(fy_e.event_year==T)&(fy_e.year.between(T-5,T+5))]; tr=tr.assign(cohort=T); treat_parts.append(tr)
    ct=fy_e[((fy_e.event_year>T)|(fy_e.event_year.isna()))&(fy_e.year.between(T-5,T+5))]; ct=ct.assign(cohort=T); ctrl_parts.append(ct)
T1_treat=pd.concat(treat_parts); T1_ctrl=pd.concat(ctrl_parts)
rows+=[prof(T1_treat,"T1 TREATED electric (stacked windows)"),
       prof(T1_ctrl,"T1 CONTROL electric not-yet/never (stacked windows)")]
# the actual RSZ estimation sample (multi-segment electric in seg_invest)
rsz=sinv[(sinv.n_seg_fy>=2)].copy()
rsz_fy=rsz.groupby(["gvkey","year"]).agg(n_op_seg=("snms_u","nunique")).reset_index()
rsz_fy["event_year"]=rsz_fy.gvkey.map(lambda g: fed.event_year.get(g,np.nan))
rsz_w=pd.concat([rsz_fy[(rsz_fy.year.between(T-5,T+5))] for T in EV]).drop_duplicates(["gvkey","year"])
rows+=[prof(rsz_w,"T1 RSZ estimation sample (multi-seg electric, windows)")]

# --- Track 2: power vs non-power (segment counts, any era + modern) ---
# crude power tag = electric/utility exposure ever
pw=set(fy.loc[(fy.exp_electric==1)|(fy.exp_utility==1),"gvkey"])
fy2=fy.copy(); fy2["power"]=fy2.gvkey.isin(pw)
rows+=[prof(fy2[fy2.power],"T2 POWER firms (all years)"),
       prof(fy2[~fy2.power],"T2 NON-POWER firms (all years)"),
       prof(fy2[(fy2.power)&(fy2.year.between(2008,2018))],"T2 POWER firms (2008-2018)"),
       prof(fy2[(~fy2.power)&(fy2.year.between(2008,2018))],"T2 NON-POWER firms (2008-2018)")]

out=pd.DataFrame(rows)
pd.set_option('display.width',200); pd.set_option('display.max_columns',20)
print(out.to_string(index=False))
out.to_csv(ROOT/"reports"/"tables"/"segment_coverage_by_group.csv",index=False)

# distribution of segment counts for key groups
print("\nSegment-count distribution (% of firm-years):")
def dist(df,name):
    n=df.n_op_seg.clip(upper=6); vc=(n.value_counts(normalize=True).sort_index()*100).round(1)
    print(f"  {name:42s} " + "  ".join(f"{int(k)}{'+' if k==6 else ''}:{v}" for k,v in vc.items()))
dist(fy[fy.n_op_seg>=2],"UNIVERSE multi-seg")
dist(T1_treat,"T1 treated electric")
dist(T1_ctrl,"T1 control electric")
dist(rsz_w,"T1 RSZ sample")
