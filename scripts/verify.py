#!/usr/bin/env python3
"""Verification of the within-electric alpha-centralization result:
  1. alpha-moderated event study (no pre-trend in the alpha interaction)
  2. placebo event year 1992
  3. rank-based alpha (robust to outliers)
  4. capital-allocation prediction (segment investment-performance sensitivity)
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
df=pd.read_parquet(P/"regdata.parquet"); alpha=pd.read_parquet(P/"alpha.parquet")
seg=pd.read_parquet(P/"seg_busseg.parquet")
df["lev"]=df["lev"].replace([np.inf,-np.inf],np.nan).clip(0,5)
df["logat"]=df["logat"].replace([np.inf,-np.inf],np.nan)
df["log_nseg"]=np.log1p(df["n_op_seg"])

def zwin(s,lo=.01,hi=.99):
    s=s.replace([np.inf,-np.inf],np.nan); s=s.clip(s.quantile(lo),s.quantile(hi)); return (s-s.mean())/s.std()
def zrank(s):
    r=s.replace([np.inf,-np.inf],np.nan).rank(pct=True); return (r-r.mean())/r.std()

aE=alpha[alpha.event=="ELEC1996"][["gvkey","a_segvol","a_vol"]].copy()
aE["alpha"]=zwin(aE["a_segvol"]); aE["alpha_rank"]=zrank(aE["a_segvol"])
pre=df[(df.year>=1990)&(df.year<1996)]
tr=(pre.groupby("gvkey")["exp_electric"].max()>0); tr_ids=tr[tr].index

# ---------- 1. alpha-moderated event study ----------
print("="*90); print("1. ALPHA-MODERATED EVENT STUDY (within electric); interaction = alpha x rel-year")
print("   expect: pre-period (k<=-2) alpha-interactions ~0, post turns negative for n_op_seg")
print("="*90)
d=df[(df.year>=1988)&(df.year<=2004)&(df.gvkey.isin(tr_ids))].merge(aE[["gvkey","alpha"]],on="gvkey")
d["k"]=(d.year-1996).clip(-6,6)
for k in range(-6,7):
    if k==-1: continue
    d[f"a{k}"]=((d.k==k)*d.alpha)
avars=[f"a{k}" for k in range(-6,7) if k!=-1]
for o in ["n_op_seg","log_nseg"]:
    dd=d.dropna(subset=[o,"alpha","logat","lev"]); m=dd.set_index(["gvkey","year"])
    r=PanelOLS(m[o],m[avars+["logat","lev"]],entity_effects=True,time_effects=True,
               drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
    print(f"\n  outcome={o} N={int(r.nobs):,}")
    for k in range(-6,7):
        if k==-1: print(f"   k={k:+d}  (ref)"); continue
        v=f"a{k}"
        if v in r.params.index: print(f"   k={k:+d}  {r.params[v]:+.4f} (t={r.tstats[v]:+.2f})")

# ---------- 2. placebo event year 1992 ----------
print("\n"+"="*90); print("2. PLACEBO event=1992 (within electric, sample 1988-1995) -> expect null")
print("="*90)
dp=df[(df.year>=1988)&(df.year<=1995)&(df.gvkey.isin(tr_ids))].merge(aE[["gvkey","alpha"]],on="gvkey")
dp["post"]=(dp.year>=1992).astype(int); dp["pa"]=dp.post*dp.alpha
for o in ["n_op_seg","log_nseg","multi_seg"]:
    dd=dp.dropna(subset=[o,"alpha","logat","lev"]); sp=dd.groupby("gvkey")["post"].nunique(); dd=dd[dd.gvkey.isin(sp[sp==2].index)]
    m=dd.set_index(["gvkey","year"])
    r=PanelOLS(m[o],m[["pa","logat","lev"]],entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
    print(f"  {o:12s} placebo post*alpha={r.params['pa']:+.4f} (t={r.tstats['pa']:+.2f}, p={r.pvalues['pa']:.3f})")

# ---------- 3. rank-based alpha ----------
print("\n"+"="*90); print("3. RANK-BASED alpha (a_segvol), within electric, post>=1996 -> expect negative")
print("="*90)
d3=df[(df.year>=1988)&(df.year<=2004)&(df.gvkey.isin(tr_ids))].merge(aE[["gvkey","alpha_rank"]],on="gvkey")
d3["post"]=(d3.year>=1996).astype(int); d3["pa"]=d3.post*d3.alpha_rank
for o in ["n_op_seg","log_nseg","multi_seg","hhi"]:
    dd=d3.dropna(subset=[o,"alpha_rank","logat","lev"]); sp=dd.groupby("gvkey")["post"].nunique(); dd=dd[dd.gvkey.isin(sp[sp==2].index)]
    m=dd.set_index(["gvkey","year"])
    r=PanelOLS(m[o],m[["pa","logat","lev"]],entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
    print(f"  {o:12s} post*alpha_rank={r.params['pa']:+.4f} (t={r.tstats['pa']:+.2f}, p={r.pvalues['pa']:.3f})")

# ---------- 4. capital allocation: segment investment-performance sensitivity ----------
print("\n"+"="*90); print("4. CAPITAL ALLOCATION: seg capx/assets ~ margin x post x alpha (within electric segments)")
print("   theory: post-launch high-alpha firms show stronger allocation-performance sensitivity")
print("="*90)
s=seg[(seg.is_op==1)&(seg.year>=1988)&(seg.year<=2004)].merge(aE[["gvkey","alpha"]],on="gvkey",how="inner")
s=s[s.gvkey.isin(tr_ids)].copy()
s["capx_assets"]=s["capx_assets"].replace([np.inf,-np.inf],np.nan).clip(-1,2)
s["op_margin"]=s["op_margin"].replace([np.inf,-np.inf],np.nan).clip(-2,2)
s["post"]=(s.year>=1996).astype(int)
s["m_post"]=s.op_margin*s.post; s["m_alpha"]=s.op_margin*s.alpha; s["m_post_alpha"]=s.op_margin*s.post*s.alpha
s["post_alpha"]=s.post*s.alpha
s["fy"]=s.gvkey.astype(str)  # firm
s=s.dropna(subset=["capx_assets","op_margin","alpha"])
s["segid"]=s.gvkey+"_"+s.sid.astype(str)
m=s.set_index(["segid","year"])
r=PanelOLS(m["capx_assets"],m[["op_margin","m_post","m_alpha","m_post_alpha","post_alpha"]],
           entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False).fit(cov_type="clustered",cluster_entity=True)
print(r.params.round(4).to_string())
print("tstats:"); print(r.tstats.round(2).to_string())
print(f"N={int(r.nobs):,} segments={s.segid.nunique():,}")
