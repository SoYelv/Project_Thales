#!/usr/bin/env python3
"""Track 1: internal capital allocation under staggered electricity shocks.

Steps: region/event crosswalk -> segment investment panel -> diagnostics.
Outputs reports/panel/seg_invest.parquet and reports/panel/firm_event.parquet.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

from electricity_identification import add_early_shock_columns

ROOT = Path(__file__).resolve().parents[1]; P = ROOT/"reports"/"panel"
seg = pd.read_parquet(P/"seg_busseg.parquet")
company = pd.read_parquet(P/"company.parquet")

# ---------- HQ state -> first electricity-futures event ----------
fe = add_early_shock_columns(company)
fe.to_parquet(P/"firm_event.parquet", index=False)

# ---------- segment investment panel: aggregate to (gvkey, snms, year) ----------
op = seg[(seg.is_op==1)].copy()
op["snms_u"] = op["snms"].astype(str).str.upper().str.strip()
g = (op.groupby(["gvkey","snms_u","year"], as_index=False)
       .agg(sales=("sales","sum"), ops=("ops","sum"), capxs=("capxs","sum"),
            ias=("ias","sum"), elec=("seg_electric","max"), energy=("seg_energy","max")))
g = g.sort_values(["gvkey","snms_u","year"])
# lags within segment
for c in ["ias","sales","ops"]:
    g[f"l_{c}"] = g.groupby(["gvkey","snms_u"])[c].shift(1)
g["margin"]   = np.where(g["sales"].abs()>0, g["ops"]/g["sales"], np.nan)
g["l_margin"] = np.where(g["l_sales"].abs()>0, g["l_ops"]/g["l_sales"], np.nan)
g["inv_la"]   = np.where(g["l_ias"].abs()>0, g["capxs"]/g["l_ias"], np.nan)   # capx/lagged assets
g["inv_s"]    = np.where(g["sales"].abs()>0, g["capxs"]/g["sales"], np.nan)
# firm-year segment count for opportunity-allocation tests
nseg = g.groupby(["gvkey","year"])["snms_u"].nunique().rename("n_seg_fy")
g = g.join(nseg, on=["gvkey","year"])
g.to_parquet(P/"seg_invest.parquet", index=False)

# ---------- diagnostics ----------
elec_firms = op.loc[op.seg_electric==1,"gvkey"].unique()
fe_e = fe[fe.gvkey.isin(elec_firms)]
print("Electric firms:", len(elec_firms))
print("\nElectric firms by strict assigned region/event:")
print(fe_e.groupby(["region","event_year"], dropna=False).size().to_string())
print("\nElectric firms by legacy broad assigned region/event:")
print(fe_e.groupby(["legacy_region","legacy_event_year"], dropna=False).size().to_string())
# multi-segment electric firm-years in event windows
ge = g[g.gvkey.isin(elec_firms)]
print("\nElectric segment-years total:", len(ge))
mult = ge.groupby(["gvkey","year"])["snms_u"].nunique()
print("Electric firm-years with >=2 segments:", int((mult>=2).sum()))
print("  of which in 1991-2004:", int((mult[mult.index.get_level_values('year').isin(range(1991,2005))]>=2).sum()))
print("\ninvestment coverage (electric, >=2seg window 1991-2004):")
w = ge[(ge.year>=1991)&(ge.year<=2004)&(ge.n_seg_fy>=2)]
print(f"  seg-years={len(w)}, inv_la nonmiss={w.inv_la.notna().mean()*100:.0f}%, "
      f"l_margin nonmiss={w.l_margin.notna().mean()*100:.0f}%, "
      f"firms={w.gvkey.nunique()}")
print("wrote seg_invest.parquet, firm_event.parquet")
