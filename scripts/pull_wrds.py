#!/usr/bin/env python3
"""Pull firm-level Compustat controls + HQ state from WRDS.

Outputs (reports/panel/):
  funda.parquet     annual fundamentals for controls + cash-flow volatility
  company.parquet   company header (state, loc, sic, naics) for region mapping
"""
from __future__ import annotations
import signal
from pathlib import Path
import pandas as pd
import wrds

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "panel"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(600)
    db = wrds.Connection()
    print("connected")

    funda = db.raw_sql("""
        select gvkey, datadate, fyear, sich, at, sale, oibdp, oiadp, capx,
               ppent, ni, dltt, dlc, che, dvc, dp, xrd, emp, prcc_f, csho
        from comp.funda
        where indfmt='INDL' and datafmt='STD' and popsrc='D' and consol='C'
          and datadate between '1975-01-01' and '2012-12-31'
    """, date_cols=["datadate"])
    funda["gvkey"] = funda["gvkey"].astype(str).str.zfill(6)
    funda.to_parquet(OUT / "funda.parquet", index=False)
    print(f"funda: {len(funda):,} rows, {funda.gvkey.nunique():,} firms")

    company = db.raw_sql("""
        select gvkey, conm, state, loc, sic, naics, fic, city, addzip
        from comp.company
    """)
    company["gvkey"] = company["gvkey"].astype(str).str.zfill(6)
    company.to_parquet(OUT / "company.parquet", index=False)
    print(f"company: {len(company):,} rows")
    print(company["state"].value_counts(dropna=False).head(10))
    db.close()

if __name__ == "__main__":
    main()
