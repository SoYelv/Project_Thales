#!/usr/bin/env python3
"""Build clean firm-segment-year and firm-year panels from data/raw/segment_data.csv.

Outputs (in reports/panel/):
  seg_busseg.parquet     segment-level BUSSEG rows, deduped, with exposure flags
  firmyear.parquet       firm-year aggregates (granularity, centralization, exposure shares)

Design choices follow electricity_research_agenda.md / Delv3-2.pdf:
  - dedup to latest srcdate per provisional key (gvkey, datadate, stype, sid)
  - exclude corporate / eliminations / other / unallocated / no-operations segments
    from "real operating segment" counts and HHI (but keep them to build
    centralization proxies: count & sales share of corporate/unallocated rows)
  - SIC exposure groups for energy/utility derivative shocks
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "segment_data.csv"
if not DATA.exists():
    DATA = ROOT / "segment_data.csv"
OUT = ROOT / "reports" / "panel"
OUT.mkdir(parents=True, exist_ok=True)

COLS = ["stype", "gvkey", "datadate", "conm", "sic", "sics1", "sics2",
        "snms", "soptp1", "geotp", "sales", "ops", "capxs", "ias",
        "ppents", "emps", "sid", "srcdate"]

# segment-name patterns that mark a non-operating / reconciliation segment
NONOP = re.compile(r"CORPORAT|ELIMINAT|UNALLOC|RECONCIL|INTERSEG|INTERCOMP|"
                   r"ADJUST|NO OPERATION|NONOPERAT|ALL OTHER|^OTHER$|OTHER SEGMENT|"
                   r"GENERAL CORP|HEADQUART|TREASURY")

def first_code(*vals):
    for v in vals:
        if pd.notna(v):
            try:
                return int(float(v))
            except (ValueError, TypeError):
                continue
    return None

def exposure_flags(sic):
    """Return dict of exposure indicators from a SIC code."""
    if sic is None:
        return dict(electric=0, gas=0, oilgas=0, energy=0, utility=0)
    electric = int(sic in (4911, 4931, 4939) or 4910 <= sic <= 4939 or sic == 4991)
    gas = int(4920 <= sic <= 4925)
    oilgas = int(sic == 1311 or 1380 <= sic <= 1389 or sic == 2911 or 4610 <= sic <= 4619)
    utility = int(4900 <= sic <= 4999)
    energy = int(bool(electric or gas or oilgas))
    return dict(electric=electric, gas=gas, oilgas=oilgas, energy=energy, utility=utility)

def main():
    print("reading...")
    df = pd.read_csv(DATA, usecols=COLS, low_memory=False)
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df["srcdate_dt"] = pd.to_datetime(df["srcdate"], errors="coerce")
    df["year"] = df["datadate"].dt.year
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    print(f"raw rows: {len(df):,}")

    # dedup: latest srcdate per provisional key
    key = ["gvkey", "datadate", "stype", "sid"]
    df = (df.sort_values(key + ["srcdate_dt"], na_position="first")
            .drop_duplicates(key, keep="last").copy())
    print(f"after latest-srcdate dedup: {len(df):,}")

    bus = df[df["stype"].eq("BUSSEG")].copy()
    print(f"BUSSEG rows: {len(bus):,}")

    # segment SIC exposure (segment industry first, fall back to firm sic)
    seg_sic = bus.apply(lambda r: first_code(r["sics1"], r["sics2"], r["sic"]), axis=1)
    firm_sic = bus["sic"].apply(lambda x: first_code(x))
    flags = seg_sic.apply(exposure_flags).apply(pd.Series)
    bus = pd.concat([bus, flags.add_prefix("seg_")], axis=1)
    bus["seg_sic"] = seg_sic
    bus["firm_sic"] = firm_sic

    # non-operating / reconciliation segment flag
    nm = bus["snms"].astype(str).str.upper()
    bus["nonop"] = nm.str.contains(NONOP).astype(int)
    bus["is_op"] = (1 - bus["nonop"])
    # real operating segment must also have positive/again-non-null sales
    bus["op_with_sales"] = ((bus["is_op"] == 1) & bus["sales"].notna()).astype(int)

    # segment-level outcomes for allocation tests
    bus["op_margin"] = np.where(bus["sales"].abs() > 0, bus["ops"] / bus["sales"], np.nan)
    bus["capx_sales"] = np.where(bus["sales"].abs() > 0, bus["capxs"] / bus["sales"], np.nan)
    bus["capx_assets"] = np.where(bus["ias"].abs() > 0, bus["capxs"] / bus["ias"], np.nan)

    bus.to_parquet(OUT / "seg_busseg.parquet", index=False)
    print(f"wrote seg_busseg.parquet ({len(bus):,} rows)")

    # ---- firm-year aggregates ----
    g = bus.groupby(["gvkey", "datadate"], dropna=False)

    def agg(part):
        op = part[part["is_op"] == 1]
        sales_op = op["sales"].fillna(0).clip(lower=0)
        tot = sales_op.sum()
        hhi = float(((sales_op / tot) ** 2).sum()) if tot > 0 else np.nan
        n_op = int((part["op_with_sales"] == 1).sum())
        # exposure shares over operating-segment sales
        def share(flag):
            num = op.loc[op[flag] == 1, "sales"].fillna(0).clip(lower=0).sum()
            return float(num / tot) if tot > 0 else 0.0
        return pd.Series({
            "year": part["year"].iloc[0],
            "conm": part["conm"].iloc[0],
            "firm_sic": first_code(part["sic"].iloc[0]),
            "n_seg_all": len(part),
            "n_op_seg": n_op,
            "n_nonop_seg": int((part["nonop"] == 1).sum()),
            "multi_seg": int(n_op > 1),
            "hhi": hhi,
            "tot_op_sales": tot,
            "share_electric": share("seg_electric"),
            "share_gas": share("seg_gas"),
            "share_oilgas": share("seg_oilgas"),
            "share_energy": share("seg_energy"),
            "share_utility": share("seg_utility"),
            # centralization proxy: nonop (corporate/unalloc) sales share
            "nonop_sales_share": (part.loc[part["nonop"] == 1, "sales"].fillna(0).clip(lower=0).sum() / tot)
                                  if tot > 0 else 0.0,
        })

    fy = g.apply(agg, include_groups=False).reset_index()
    fy["year"] = fy["year"].astype("Int64")
    # firm-level exposure indicators
    for f in ["electric", "gas", "oilgas", "energy", "utility"]:
        fy[f"exp_{f}"] = (fy[f"share_{f}"] > 0).astype(int)
    fy.to_parquet(OUT / "firmyear.parquet", index=False)
    print(f"wrote firmyear.parquet ({len(fy):,} firm-years)")
    print(fy[["n_op_seg", "multi_seg", "hhi", "share_energy", "share_electric"]].describe().round(3))

if __name__ == "__main__":
    main()
