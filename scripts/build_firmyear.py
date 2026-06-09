#!/usr/bin/env python3
"""Vectorized firm-year aggregation from seg_busseg.parquet."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "panel"

bus = pd.read_parquet(OUT / "seg_busseg.parquet")
bus["sales_pos"] = bus["sales"].fillna(0).clip(lower=0)
op = bus[bus["is_op"] == 1].copy()

# total operating-segment sales per firm-year
tot = op.groupby(["gvkey", "datadate"])["sales_pos"].sum().rename("tot_op_sales")
op = op.join(tot, on=["gvkey", "datadate"])
op["sh"] = np.where(op["tot_op_sales"] > 0, op["sales_pos"] / op["tot_op_sales"], 0.0)

# HHI and operating-segment count
gp = op.groupby(["gvkey", "datadate"])
hhi = gp["sh"].apply(lambda x: float((x ** 2).sum())).rename("hhi")
n_op = gp.apply(lambda d: int((d["sales"].notna()).sum()), include_groups=False).rename("n_op_seg")

# exposure sales shares
def expo_share(flag):
    num = op.assign(v=op[flag] * op["sales_pos"]).groupby(["gvkey", "datadate"])["v"].sum()
    return (num / tot).rename(f"share_{flag.replace('seg_','')}")
shares = pd.concat([expo_share(f"seg_{x}") for x in
                    ["electric", "gas", "oilgas", "energy", "utility"]], axis=1)

# non-operating (corporate/unalloc) counts & share over ALL firm-year rows
allg = bus.groupby(["gvkey", "datadate"])
n_all = allg.size().rename("n_seg_all")
n_nonop = allg["nonop"].sum().rename("n_nonop_seg")
nonop_sales = bus.assign(v=bus["nonop"] * bus["sales_pos"]).groupby(["gvkey", "datadate"])["v"].sum()
meta = allg.agg(conm=("conm", "first"), firm_sic=("firm_sic", "first"),
                year=("year", "first")).reset_index()

fy = (meta.set_index(["gvkey", "datadate"])
      .join([n_all, n_nonop, n_op, hhi, tot, shares]))
fy["nonop_sales_share"] = (nonop_sales / tot).fillna(0.0)
fy = fy.reset_index()
fy["n_op_seg"] = fy["n_op_seg"].fillna(0).astype(int)
fy["multi_seg"] = (fy["n_op_seg"] > 1).astype(int)
fy["year"] = fy["year"].astype("Int64")
for f in ["electric", "gas", "oilgas", "energy", "utility"]:
    fy[f"share_{f}"] = fy[f"share_{f}"].fillna(0.0)
    fy[f"exp_{f}"] = (fy[f"share_{f}"] > 0).astype(int)

fy.to_parquet(OUT / "firmyear.parquet", index=False)
print(f"firmyear: {len(fy):,} firm-years, {fy.gvkey.nunique():,} firms")
print(fy[["n_op_seg", "multi_seg", "hhi", "share_energy", "share_electric",
          "share_gas", "share_oilgas", "nonop_sales_share"]].describe().round(3).to_string())
print("\nfirms with any electric exposure:", int(fy.groupby('gvkey')['exp_electric'].max().sum()))
print("firms with any energy exposure:", int(fy.groupby('gvkey')['exp_energy'].max().sum()))
