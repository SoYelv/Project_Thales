#!/usr/bin/env python3
"""Robustness + alpha-moderation of the modern (2012) capital-allocation negative,
and a direct early-vs-late sign-reversal test."""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest2.parquet"); funda=pd.read_parquet(P/"funda.parquet")
g["inv_la"]=g["inv_la"].replace([np.inf,-np.inf],np.nan); g["l_margin"]=g["l_margin"].replace([np.inf,-np.inf],np.nan)
g=g[g.n_seg_fy>=2].copy(); g["elec"]=g["elec"].fillna(0).astype(int)

# modern alpha = std of ROA 2007-2011
funda=funda.rename(columns={"fyear":"year"}); funda["year"]=pd.to_numeric(funda["year"],errors="coerce")
funda["roa"]=funda["oibdp"]/funda["at"]
am=funda[(funda.year>=2007)&(funda.year<=2011)].groupby("gvkey")["roa"].std().rename("a_vol").reset_index()
am["alpha"]=(am.a_vol.rank(pct=True)-0.5); am["alpha"]=(am.alpha-am.alpha.mean())/am.alpha.std()
g=g.merge(am[["gvkey","alpha"]],on="gvkey",how="left")

def prep(d,opp="l_margin"):
    d=d.dropna(subset=["inv_la",opp]).copy()
    for c in ["inv_la",opp]: d[c]=d[c].clip(d[c].quantile(.01),d[c].quantile(.99))
    d["rel_inv"]=d["inv_la"]-d.groupby(["gvkey","year"])["inv_la"].transform("mean")
    d["rel_opp"]=d[opp]-d.groupby(["gvkey","year"])[opp].transform("mean")
    return d
def fitp(d,cols,key):
    cy=pd.get_dummies(d.year.astype(str),prefix="y",drop_first=True).astype(float)
    idx=pd.MultiIndex.from_arrays([d.gvkey.values+"_"+d.snms_u,d.year.values])
    X=pd.concat([d[cols].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    y=pd.Series(d.rel_inv.values,index=idx); cl=pd.DataFrame({"f":d.gvkey.values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    return r.params[key],r.tstats[key],r.pvalues[key],int(r.nobs)

print("="*90); print("2012 negative — robustness"); print("="*90)
# baseline
d=prep(g[(g.year>=2007)&(g.year<=2017)]); d["ro"]=d.rel_opp; d["roe"]=d.ro*d.elec; d["rop"]=d.ro*(d.year>=2012)
d["roep"]=d.ro*d.elec*(d.year>=2012)
b,t,p,N=fitp(d,["roep","roe","rop","ro"],"roep"); print(f"baseline 2007-2017      roep={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,}")
# pre-event multi-seg
pre=g[(g.year>=2007)&(g.year<2012)]; premulti=pre.groupby("gvkey").n_seg_fy.max(); keep=set(premulti[premulti>=2].index)
d2=prep(g[(g.year>=2007)&(g.year<=2017)&(g.gvkey.isin(keep))]); d2["ro"]=d2.rel_opp; d2["roe"]=d2.ro*d2.elec; d2["rop"]=d2.ro*(d2.year>=2012); d2["roep"]=d2.ro*d2.elec*(d2.year>=2012)
b,t,p,N=fitp(d2,["roep","roe","rop","ro"],"roep"); print(f"pre-2012 multi-seg only roep={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,}")
# narrow window
d3=prep(g[(g.year>=2009)&(g.year<=2015)]); d3["ro"]=d3.rel_opp; d3["roe"]=d3.ro*d3.elec; d3["rop"]=d3.ro*(d3.year>=2012); d3["roep"]=d3.ro*d3.elec*(d3.year>=2012)
b,t,p,N=fitp(d3,["roep","roe","rop","ro"],"roep"); print(f"window 2009-2015        roep={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,}")

print("\n-- alpha moderation: does the 2012 decline load on alpha? --")
da=prep(g[(g.year>=2007)&(g.year<=2017)].dropna(subset=["alpha"])); da["a"]=da.alpha
da["ro"]=da.rel_opp; da["roe"]=da.ro*da.elec; da["rop"]=da.ro*(da.year>=2012); da["roep"]=da.ro*da.elec*(da.year>=2012)
da["roepa"]=da.roep*da.a; da["roea"]=da.roe*da.a; da["ropa"]=da.rop*da.a; da["roa"]=da.ro*da.a
b,t,p,N=fitp(da,["roepa","roep","roea","roe","ropa","rop","roa","ro"],"roepa")
print(f"  elec x post2012 x alpha  roepa={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,}")
b,t,p,_=fitp(da,["roepa","roep","roea","roe","ropa","rop","roa","ro"],"roep")
print(f"  elec x post2012 (main)   roep ={b:+.4f} (t={t:+.2f}, p={p:.3f})")

print("\n-- EARLY vs LATE sign reversal (electric producers) --")
for lab,lo,T,hi in [("EARLY 1996",1991,1996,2001),("LATE 2012",2007,2012,2017)]:
    dd=prep(g[(g.year>=lo)&(g.year<=hi)]); dd["ro"]=dd.rel_opp; dd["roe"]=dd.ro*dd.elec; dd["rop"]=dd.ro*(dd.year>=T); dd["roep"]=dd.ro*dd.elec*(dd.year>=T)
    b,t,p,N=fitp(dd,["roep","roe","rop","ro"],"roep"); print(f"  {lab}: elec x post roep={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,}")
