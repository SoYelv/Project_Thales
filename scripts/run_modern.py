#!/usr/bin/env python3
"""Capital-allocation (RSZ) sweep over RECENT electricity shocks, segment data.
Shocks: PJM RPM 2007, Nodal Exchange 2009, ERCOT nodal 2010, CME 2012,
MISO-South 2013, SPP 2014, plus a stacked modern-staggered design and EIM 2014-18.
Treatments: electric producer, energy, high electricity-input intensity,
continuous firm/segment intensity.
Key term: rel_opp x TREAT x post (>0 predicted).
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest2.parquet")
fe=pd.read_parquet(P/"firm_event.parquet").drop_duplicates("gvkey")
for c in ["inv_la","l_margin","sgrow"]: g[c]=g[c].replace([np.inf,-np.inf],np.nan)
g=g[g.n_seg_fy>=2].merge(fe[["gvkey","state"]],on="gvkey",how="left").copy()
def zc(s): s=s.replace([np.inf,-np.inf],np.nan); return (s-s.mean())/s.std()
g["fint_z"]=zc(g["firm_elec_int"]); g["sint_z"]=zc(g["elec_int"])
g["t_elec"]=g["elec"].fillna(0).astype(int); g["t_energy"]=g["energy"].fillna(0).astype(int)
g["t_high"]=(g["firm_elec_int"]>=3).astype(int)

ERCOT={"TX"}; MISO={"AR","LA","MS"}; SPP={"KS","OK","NE","SD","ND"}
EIM={ "OR":2015,"WA":2017,"NV":2016,"AZ":2017,"ID":2018,"UT":2015,"WY":2015,"CA":2015}

def rsz(d,opp,clusterf="gvkey"):
    d=d.dropna(subset=["inv_la",opp]).copy()
    if len(d)<200: return None
    for c in ["inv_la",opp]: d[c]=d[c].clip(d[c].quantile(.01),d[c].quantile(.99))
    d["rel_inv"]=d["inv_la"]-d.groupby(["cohort","gvkey","year"])["inv_la"].transform("mean")
    d["rel_opp"]=d[opp]-d.groupby(["cohort","gvkey","year"])[opp].transform("mean")
    d["ro"]=d.rel_opp; d["rop"]=d.ro*d.post; d["roT"]=d.ro*d["T"]; d["roTp"]=d.ro*d["T"]*d.post
    cy=pd.get_dummies(d["cohort"].astype(str)+"_"+d.year.astype(str),prefix="cy",drop_first=True).astype(float)
    d["cseg"]=d["cohort"].astype(str)+"_"+d.gvkey+"_"+d.snms_u
    idx=pd.MultiIndex.from_arrays([d.cseg.values,d.year.values])
    X=pd.concat([d[["roTp","rop","roT","ro"]].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    y=pd.Series(d.rel_inv.values,index=idx); cl=pd.DataFrame({"f":d[clusterf].values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    return r.params["roTp"],r.tstats["roTp"],r.pvalues["roTp"],int(r.nobs),d.gvkey.nunique()

def national(T,lo,hi,treatcol):
    d=g[(g.year>=lo)&(g.year<=hi)].copy(); d["cohort"]=0; d["post"]=(d.year>=T).astype(int); d["T"]=d[treatcol]
    return d
def staggered_regional(regions_year,treatcol="t_elec",span=5):
    # treated = electric firm in region at its event; control = electric not-yet/never
    state_event={state:Tn for states,Tn in regions_year for state in states}
    parts=[]
    for states,Tn in regions_year:
        tr=g[(g.t_elec==1)&(g.state.isin(states))&(g.year.between(Tn-span,Tn+span))].copy(); tr["TRZ"]=1
        event_for_state=g.state.map(state_event)
        notyet_or_never=event_for_state.gt(Tn)|event_for_state.isna()
        ctl=g[(g.t_elec==1)&notyet_or_never&(g.year.between(Tn-span,Tn+span))].copy(); ctl["TRZ"]=0
        c=pd.concat([tr,ctl]); c["cohort"]=Tn; c["post"]=(c.year>=Tn+1).astype(int); c["T"]=c["TRZ"]
        parts.append(c)
    return pd.concat(parts,ignore_index=True)

def show(name,d,opps=("l_margin","sgrow")):
    for opp in opps:
        res=rsz(d,opp)
        if res is None: print(f"  {name:46s} [{opp:9s}] insufficient"); continue
        b,t,p,N,nf=res
        flag=" *" if p<0.10 else ""
        print(f"  {name:46s} [{'margin' if opp=='l_margin' else 'salesg':9s}] roTp={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,} f={nf}{flag}")

print("="*100); print("MODERN-SHOCK capital-allocation sweep (RSZ); key=rel_opp*TREAT*post"); print("="*100)
NB=[("PJM_RPM_2007",2007,2002,2012),("Nodal_2009",2009,2004,2014),("ERCOT_2010",2010,2005,2015),
    ("CME_2012",2012,2007,2017),("MISO_2013",2013,2008,2018),("SPP_2014",2014,2009,2019)]
for nm,T,lo,hi in NB:
    print(f"\n-- {nm} (exploratory national period break, post>={T}) --")
    show(f"{nm}: electric producer",national(T,lo,hi,"t_elec"))
    show(f"{nm}: high-input >=3%",national(T,lo,hi,"t_high"))
    show(f"{nm}: firm-intensity cont(z)",national(T,lo,hi,"fint_z"))

print("\n-- MODERN STAGGERED (ERCOT2010/MISO2013/SPP2014), electric producers, not-yet ctrl --")
show("modern staggered: electric",staggered_regional([(ERCOT,2010),(MISO,2013),(SPP,2014)]))
print("\n-- EIM staggered (2015-2018 by state), electric producers --")
eim_regions=[({s},y) for s,y in EIM.items()]
show("EIM staggered: electric",staggered_regional(eim_regions))
