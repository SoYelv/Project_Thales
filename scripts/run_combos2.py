#!/usr/bin/env python3
"""Second combination batch: sharpen the BOLD electricity-input designs.
- continuous firm intensity restricted to MANUFACTURING (best-measured intensity)
- top vs bottom intensity tercile (multi-seg universe)
- extensive-margin outcome (segment count / HHI) for electricity-input intensity
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest2.parquet")
for c in ["inv_la","l_margin","sgrow"]: g[c]=g[c].replace([np.inf,-np.inf],np.nan)
g=g[g.n_seg_fy>=2].copy()
def zc(s): s=s.replace([np.inf,-np.inf],np.nan); return (s-s.mean())/s.std()

def rsz(d,opp,keys,clusterf):
    d=d.dropna(subset=["inv_la",opp]).copy()
    for c in ["inv_la",opp]: d[c]=d[c].clip(d[c].quantile(.01),d[c].quantile(.99))
    d["rel_inv"]=d["inv_la"]-d.groupby(["cohort","gvkey","year"])["inv_la"].transform("mean")
    d["rel_opp"]=d[opp]-d.groupby(["cohort","gvkey","year"])[opp].transform("mean")
    d["ro"]=d.rel_opp; d["rop"]=d.ro*d.post; d["roT"]=d.ro*d["T"]; d["roTp"]=d.ro*d["T"]*d.post
    cy=pd.get_dummies(d["cohort"].astype(str)+"_"+d.year.astype(str),prefix="cy",drop_first=True).astype(float)
    d["cseg"]=d["cohort"].astype(str)+"_"+d.gvkey+"_"+d.snms_u
    idx=pd.MultiIndex.from_arrays([d.cseg.values,d.year.values])
    X=pd.concat([d[keys].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    y=pd.Series(d.rel_inv.values,index=idx); cl=pd.DataFrame({"f":d[clusterf].values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    return r.params[keys[0]],r.tstats[keys[0]],r.pvalues[keys[0]],int(r.nobs),d.gvkey.nunique()

def nat(df): d=df[(df.year>=1991)&(df.year<=2001)].copy(); d["cohort"]=0; d["post"]=(d.year>=1996).astype(int); return d

print("="*98); print("BOLD electricity-input designs — sharpened"); print("="*98)

# 1) continuous firm intensity, MANUFACTURING only
man=g[(g.seg_sic>=2000)&(g.seg_sic<=3999)].copy()
man["fint_z"]=zc(man["firm_elec_int"]); man["sint_z"]=zc(man["elec_int"])
d=nat(man); d["T"]=d["fint_z"]
b,t,p,N,nf=rsz(d,"l_margin",["roTp","rop","roT","ro"],"gvkey")
print(f"\n1) firm-intensity (cont) MANUFACTURING only x nat1996 [margin]: rel_opp*T*post={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,} firms={nf}")
d["T"]=d["sint_z"]
b,t,p,N,nf=rsz(d,"l_margin",["roTp","rop","roT","ro"],"gvkey")
print(f"   seg-intensity (cont) MANUFACTURING only x nat1996 [margin]: rel_opp*T*post={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,} firms={nf}")

# 2) top vs bottom tercile of firm intensity (whole multi-seg universe)
g["terc"]=pd.qcut(g["firm_elec_int"].rank(method="first"),3,labels=[0,1,2]).astype(int)
top=g[g.terc.isin([0,2])].copy(); top["T"]=(top.terc==2).astype(int)
d=nat(top)
b,t,p,N,nf=rsz(d,"l_margin",["roTp","rop","roT","ro"],"gvkey")
print(f"\n2) top-vs-bottom intensity TERCILE x nat1996 [margin]: rel_opp*T*post={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,} firms={nf}")

# 3) extensive margin: does electricity intensity x post change firm segment count / HHI?
fy=g.drop_duplicates(["gvkey","year"])[["gvkey","year","n_seg_fy","firm_elec_int"]].copy()
# need full firm-year incl single-seg for count outcome -> use firmyear panel
fyr=pd.read_parquet(P/"firmyear.parquet"); fyr["year"]=fyr["year"].astype("Int64")
fyr=fyr[fyr.year.notna()].copy(); fyr["year"]=fyr["year"].astype(int)
si=g.drop_duplicates(["gvkey","year"])[["gvkey","year","firm_elec_int"]]
fyr=fyr.merge(si,on=["gvkey","year"],how="left")
fyr["int_z"]=zc(fyr["firm_elec_int"]); fyr["log_nseg"]=np.log1p(fyr["n_op_seg"])
d=fyr[(fyr.year>=1991)&(fyr.year<=2001)].dropna(subset=["int_z"]).copy()
d["post"]=(d.year>=1996).astype(int); d["ip"]=d.int_z*d.post
for out in ["n_op_seg","log_nseg","hhi"]:
    dd=d.dropna(subset=[out]); idx=pd.MultiIndex.from_arrays([dd.gvkey.values,dd.year.values])
    X=dd[["ip"]].copy(); X.index=idx; y=pd.Series(dd[out].values,index=idx); cl=pd.DataFrame({"f":dd.gvkey.values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,time_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    print(f"3) EXTENSIVE: {out:10s} ~ intensity_z*post : {r.params['ip']:+.4f} (t={r.tstats['ip']:+.2f}, p={r.pvalues['ip']:.3f}) N={int(r.nobs):,}")
