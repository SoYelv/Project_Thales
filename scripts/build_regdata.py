#!/usr/bin/env python3
"""Assemble firm-year regression dataset: firmyear + funda controls + HQ state,
firm-level pre-event exposure treatment, and alpha proxies.

Output: reports/panel/regdata.parquet
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "reports" / "panel"

fy = pd.read_parquet(P / "firmyear.parquet")
funda = pd.read_parquet(P / "funda.parquet")
company = pd.read_parquet(P / "company.parquet")

fy["year"] = fy["year"].astype("Int64")
fy = fy[fy["year"].notna()].copy()
fy["year"] = fy["year"].astype(int)

# ---- firm-level controls from funda (one obs per gvkey-fyear) ----
funda = funda.sort_values(["gvkey", "fyear"]).copy()
funda["lev"] = (funda["dltt"].fillna(0) + funda["dlc"].fillna(0)) / funda["at"]
funda["roa"] = funda["oibdp"] / funda["at"]
funda["capx_at"] = funda["capx"] / funda["at"]
funda["cash_at"] = funda["che"] / funda["at"]
funda["logat"] = np.log(funda["at"].clip(lower=1e-3))
funda["cf"] = (funda["oibdp"]) / funda["at"]
# cash-flow volatility: rolling 5y std of roa within firm
funda["cf_vol"] = (funda.groupby("gvkey")["roa"]
                   .transform(lambda x: x.rolling(5, min_periods=3).std()))
ctrl = funda[["gvkey", "fyear", "logat", "lev", "roa", "capx_at", "cash_at",
              "cf_vol", "at", "sale", "sich"]].rename(columns={"fyear": "year"})
ctrl = ctrl.dropna(subset=["year"]).copy()
ctrl["year"] = ctrl["year"].astype(int)

df = fy.merge(ctrl, on=["gvkey", "year"], how="left")
df = df.merge(company[["gvkey", "state", "loc", "sic", "naics"]]
              .rename(columns={"sic": "hdr_sic"}), on="gvkey", how="left")

# firm-level SIC (prefer header funda sich, then firm_sic from segments, then company sic)
def to_int(x):
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return np.nan
df["sic_use"] = df["sich"].map(to_int)
df["sic_use"] = df["sic_use"].fillna(df["firm_sic"]).fillna(df["hdr_sic"].map(to_int))

# clean inf in nonop share
df["nonop_sales_share"] = df["nonop_sales_share"].replace([np.inf, -np.inf], np.nan)

df.to_parquet(P / "regdata.parquet", index=False)
print(f"regdata: {len(df):,} firm-years, {df.gvkey.nunique():,} firms")
print("control non-missing: logat %.1f%%  lev %.1f%%  roa %.1f%%" % (
    df.logat.notna().mean()*100, df.lev.notna().mean()*100, df.roa.notna().mean()*100))
print("state non-missing: %.1f%%" % (df.state.notna().mean()*100))
print(df[["n_op_seg","multi_seg","hhi","share_energy","share_electric","logat","lev"]].describe().round(3).to_string())
