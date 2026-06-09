#!/usr/bin/env python3
"""Build electricity-input-intensity by industry (SIC) and a segment panel that
carries it, so we can treat ELECTRICITY AS A PRODUCTION INPUT for the whole
multi-segment universe (not just power producers).

Intensity = electricity purchased as % of value of shipments, calibrated to EIA
Manufacturing Energy Consumption Survey (MECS) industry rankings. This is a
transparent proxy; values are approximate industry-typical shares.

Output: reports/panel/seg_invest2.parquet  (adds elec_int at segment + firm level)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"

def elec_intensity(sic):
    """Electricity cost as % of value of shipments (MECS-calibrated)."""
    if sic is None or (isinstance(sic,float) and np.isnan(sic)): return np.nan
    s=int(sic)
    # --- very high (electro-intensive processing) ---
    if s==3334: return 15.0          # primary aluminum (smelting)
    if s==2812: return 11.0          # alkalies & chlorine (electrolysis)
    if s==2813: return 8.0           # industrial gases
    if s in (3313,): return 9.0      # electrometallurgical products
    if s==3274: return 8.0           # lime
    if s==3241: return 7.0           # cement, hydraulic
    if s in (3312,3315,3316,3317): return 6.0   # steel works / blast furnaces
    # --- high ---
    if 2610<=s<=2631: return 5.0     # pulp & paper mills
    if s in (3211,3221,3229,3231): return 4.5   # glass
    if 3330<=s<=3399: return 5.0     # nonferrous / other primary & secondary metals
    if 2810<=s<=2819: return 4.0     # industrial inorganic chemicals
    if s in (3275,3271,3272,3273): return 4.0   # gypsum, concrete products
    if 3250<=s<=3269: return 4.0     # structural clay, pottery
    # --- medium ---
    if 1000<=s<=1099: return 3.5     # metal mining
    if 1400<=s<=1499: return 3.0     # nonmetallic mining/quarrying
    if 2820<=s<=2899: return 2.5     # other chemicals
    if 2200<=s<=2299: return 2.5     # textiles
    if 3320<=s<=3329 or 3360<=s<=3369: return 2.5   # foundries
    if 3000<=s<=3089: return 2.0     # rubber & plastics
    if 2400<=s<=2499: return 2.0     # lumber & wood
    if 2600<=s<=2699: return 3.0     # other paper/converted
    # --- low manufacturing ---
    if 2000<=s<=2099: return 1.5     # food
    if 2100<=s<=2199: return 1.2     # tobacco
    if 2500<=s<=2599: return 1.3     # furniture
    if 2700<=s<=2799: return 1.2     # printing/publishing
    if 2900<=s<=2999: return 2.5     # petroleum refining (electric-intensive)
    if 3400<=s<=3499: return 1.2     # fabricated metal
    if 3500<=s<=3599: return 1.0     # machinery
    if 3600<=s<=3699: return 1.3     # electronics/electrical (incl semis ~ higher)
    if s in (3674,): return 3.0      # semiconductors (fabs electricity-heavy)
    if 3700<=s<=3799: return 1.0     # transportation equipment
    if 3800<=s<=3899: return 0.8     # instruments
    if 3900<=s<=3999: return 1.0     # misc manufacturing
    # --- agriculture / construction ---
    if 100<=s<=999: return 1.0
    if 1500<=s<=1799: return 0.4     # construction
    if 1200<=s<=1399: return 2.0     # coal/oil&gas extraction
    # --- power producers themselves (consume + produce) ---
    if 4900<=s<=4999: return 6.0
    # --- services / trade / finance / transport (low) ---
    if 4000<=s<=4799: return 0.6     # transport
    if 4800<=s<=4899: return 1.5     # communications (data centers later higher)
    if 5000<=s<=5999: return 0.5     # wholesale/retail trade
    if 6000<=s<=6999: return 0.3     # finance/insurance/real estate
    if 7000<=s<=8999: return 0.5     # services (some data-heavy higher)
    return 1.0                        # default

def main():
    bus=pd.read_parquet(P/"seg_busseg.parquet")
    bus["seg_elec_int"]=bus["seg_sic"].map(elec_intensity)
    op=bus[bus.is_op==1].copy()
    op["snms_u"]=op["snms"].astype(str).str.upper().str.strip()
    g=(op.groupby(["gvkey","snms_u","year"],as_index=False)
         .agg(sales=("sales","sum"),ops=("ops","sum"),capxs=("capxs","sum"),ias=("ias","sum"),
              elec=("seg_electric","max"),energy=("seg_energy","max"),
              elec_int=("seg_elec_int","mean"),seg_sic=("seg_sic","first")))
    g=g.sort_values(["gvkey","snms_u","year"])
    for c in ["ias","sales","ops"]:
        g[f"l_{c}"]=g.groupby(["gvkey","snms_u"])[c].shift(1)
    g["margin"]=np.where(g["sales"].abs()>0,g["ops"]/g["sales"],np.nan)
    g["l_margin"]=np.where(g["l_sales"].abs()>0,g["l_ops"]/g["l_sales"],np.nan)
    g["inv_la"]=np.where(g["l_ias"].abs()>0,g["capxs"]/g["l_ias"],np.nan)
    g["sgrow"]=np.where(g["l_sales"].abs()>0,g["sales"]/g["l_sales"]-1,np.nan)
    nseg=g.groupby(["gvkey","year"])["snms_u"].nunique().rename("n_seg_fy")
    g=g.join(nseg,on=["gvkey","year"])
    # firm-level (sales-weighted) electricity intensity per firm-year
    g["w"]=g["sales"].fillna(0).clip(lower=0)
    fw=g.groupby(["gvkey","year"]).apply(
        lambda d:(d["elec_int"]*d["w"]).sum()/d["w"].sum() if d["w"].sum()>0 else d["elec_int"].mean(),
        include_groups=False).rename("firm_elec_int")
    g=g.join(fw,on=["gvkey","year"])
    g.to_parquet(P/"seg_invest2.parquet",index=False)
    print(f"seg_invest2: {len(g):,} segment-years, {g.gvkey.nunique():,} firms")
    print("\nFirm electricity intensity distribution (firm-year, sales-weighted):")
    print(g.drop_duplicates(['gvkey','year'])['firm_elec_int'].describe(percentiles=[.1,.25,.5,.75,.9,.95]).round(2).to_string())
    print("\nMulti-segment firm-years by intensity tier:")
    m=g[g.n_seg_fy>=2].drop_duplicates(['gvkey','year'])
    tier=pd.cut(m['firm_elec_int'],[0,1,3,6,100],labels=['low(<1%)','med(1-3%)','high(3-6%)','vhigh(>6%)'])
    print(tier.value_counts().sort_index().to_string())
    print("\nTop electricity-intensive segments present (by segment-years):")
    print(g[g.elec_int>=4].groupby(pd.cut(g[g.elec_int>=4].elec_int,[4,6,8,20])).size().to_string())

if __name__=="__main__":
    main()
