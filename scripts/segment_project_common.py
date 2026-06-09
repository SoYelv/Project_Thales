#!/usr/bin/env python3
"""Shared helpers for the segment project-space report pipeline."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "segment_data.csv"
if not DATA_PATH.exists():
    DATA_PATH = ROOT / "segment_data.csv"

OUT_DIR = ROOT / "reports" / "segment_project_space"
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"
REPORT_PATH = OUT_DIR / "segment_project_space_report.html"
INDEX_PATH = OUT_DIR / "index.html"
GUIDE_PATH = OUT_DIR / "01_data_guide.html"
PATHS_PATH = OUT_DIR / "02_research_paths.html"
APPENDIX_PATH = OUT_DIR / "03_evidence_appendix.html"
REGRESSION_PATH = OUT_DIR / "04_regression_results.html"
QA_PATH = OUT_DIR / "segment_project_space_qa.json"

USECOLS = [
    "stype",
    "tic",
    "datadate",
    "gvkey",
    "conm",
    "sic",
    "naics",
    "gsubind",
    "gind",
    "curcds",
    "isosrc",
    "snms",
    "soptp1",
    "soptp2",
    "geotp",
    "naicss1",
    "naicss2",
    "sics1",
    "sics2",
    "sales",
    "oibdps",
    "dps",
    "oiadps",
    "capxs",
    "ias",
    "esubs",
    "ivaeqs",
    "emps",
    "rds",
    "obs",
    "salexg",
    "intseg",
    "ptis",
    "ibs",
    "nis",
    "ops",
    "ppents",
    "iints",
    "atlls",
    "caxts",
    "cogss",
    "nopxs",
    "nxints",
    "ocaxs",
    "oelim",
    "revts",
    "spis",
    "txts",
    "txws",
    "xidos",
    "xints",
    "xsgas",
    "sid",
    "srcdate",
]

PRIMARY_NUMERIC = ["sales", "ops", "capxs", "ias", "emps", "rds", "ppents"]
EXTENDED_NUMERIC = [
    "oibdps",
    "dps",
    "oiadps",
    "esubs",
    "ivaeqs",
    "obs",
    "salexg",
    "intseg",
    "ptis",
    "ibs",
    "nis",
    "iints",
    "atlls",
    "caxts",
    "cogss",
    "nopxs",
    "nxints",
    "ocaxs",
    "oelim",
    "revts",
    "spis",
    "txts",
    "txws",
    "xidos",
    "xints",
    "xsgas",
]
CODE_FIELDS = ["sic", "naics", "gsubind", "gind", "sics1", "sics2", "naicss1", "naicss2"]
DEDUP_KEY = ["gvkey", "datadate", "stype", "sid"]
EXPOSURE_FAMILIES = [
    "electric_power_output",
    "gas_utility",
    "oil_gas_petroleum",
    "broader_energy",
    "metals_mining",
    "agriculture_food",
    "transport_freight",
    "airlines_fuel_sensitive",
    "chemicals",
    "paper_pulp",
    "cement_minerals",
]

NONOP = re.compile(
    r"CORPORAT|ELIMINAT|UNALLOC|RECONCIL|INTERSEG|INTERCOMP|ADJUST|"
    r"NO OPERATION|NONOPERAT|ALL OTHER|^OTHER$|OTHER SEGMENT|GENERAL CORP|"
    r"HEADQUART|TREASURY"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_output_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def write_table(df: pd.DataFrame, name: str) -> Path:
    ensure_output_dirs()
    path = TABLE_DIR / name
    df.to_csv(path, index=False)
    return path


def write_json(payload: dict, name: str) -> Path:
    ensure_output_dirs()
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def read_table(name: str, required: bool = True) -> pd.DataFrame:
    path = TABLE_DIR / name
    if path.exists():
        return pd.read_csv(path)
    if required:
        raise FileNotFoundError(f"Missing required generated table: {path.relative_to(ROOT)}")
    return pd.DataFrame()


def pct(mask: pd.Series) -> float:
    if len(mask) == 0:
        return 0.0
    return round(float(mask.mean() * 100), 1)


def first_code_frame(df: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    out = pd.Series(np.nan, index=df.index, dtype="float64")
    for col in columns:
        vals = pd.to_numeric(df[col], errors="coerce")
        out = out.where(out.notna(), vals)
    return out


def code_between(code: pd.Series, lo: int, hi: int) -> pd.Series:
    return code.between(lo, hi, inclusive="both")


def add_code_fields(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["seg_sic"] = first_code_frame(out, ["sics1", "sics2", "sic"])
    out["firm_sic"] = first_code_frame(out, ["sic"])
    out["seg_naics"] = first_code_frame(out, ["naicss1", "naicss2", "naics"])
    return out


def add_exposure_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    sic = out["seg_sic"]
    name = out["snms"].fillna("").astype(str).str.upper()

    electric = code_between(sic, 4910, 4939) | sic.eq(4991) | name.str.contains("ELECTRIC|POWER|UTILITY")
    gas_utility = code_between(sic, 4920, 4925) | name.str.contains("NATURAL GAS|GAS UTILITY")
    oil_gas = (
        sic.eq(1311)
        | code_between(sic, 1380, 1389)
        | sic.eq(2911)
        | code_between(sic, 4610, 4619)
        | name.str.contains("OIL|GAS|PETROLEUM|REFIN")
    )
    utility = code_between(sic, 4900, 4999) | name.str.contains("UTILITY|UTILITIES")
    metals_mining = code_between(sic, 1000, 1499) | code_between(sic, 3310, 3399)
    agriculture_food = code_between(sic, 100, 999) | code_between(sic, 2000, 2099)
    transport_freight = code_between(sic, 4000, 4799)
    airlines = sic.isin([4512, 4513, 4581]) | name.str.contains("AIRLINE|AVIATION|AIR ")
    chemicals = code_between(sic, 2800, 2899)
    paper_pulp = code_between(sic, 2600, 2699) | name.str.contains("PAPER|PULP")
    cement_minerals = code_between(sic, 3200, 3299) | name.str.contains("CEMENT|LIME|MINERAL|GLASS")

    flags = {
        "electric_power_output": electric,
        "gas_utility": gas_utility,
        "oil_gas_petroleum": oil_gas,
        "broader_energy": electric | gas_utility | oil_gas | utility,
        "metals_mining": metals_mining,
        "agriculture_food": agriculture_food,
        "transport_freight": transport_freight,
        "airlines_fuel_sensitive": airlines,
        "chemicals": chemicals,
        "paper_pulp": paper_pulp,
        "cement_minerals": cement_minerals,
    }
    for col, mask in flags.items():
        out[col] = mask.fillna(False).astype(int)
    return out


def load_segments() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Cannot find segment source file: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, usecols=USECOLS, low_memory=False)
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df["srcdate_dt"] = pd.to_datetime(df["srcdate"], errors="coerce")
    df["year"] = df["datadate"].dt.year
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = add_code_fields(df)
    df = add_exposure_flags(df)
    return df


def latest_srcdate_view(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.sort_values([*DEDUP_KEY, "srcdate_dt"], na_position="first")
        .drop_duplicates(DEDUP_KEY, keep="last")
        .copy()
    )


def latest_srcdate_dedup_summary(raw: pd.DataFrame, latest: pd.DataFrame) -> pd.DataFrame:
    raw_counts = raw.groupby("stype", dropna=False).size().rename("raw_rows")
    latest_counts = latest.groupby("stype", dropna=False).size().rename("latest_source_rows")
    out = pd.concat([raw_counts, latest_counts], axis=1).fillna(0).reset_index()
    out["raw_rows"] = out["raw_rows"].astype(int)
    out["latest_source_rows"] = out["latest_source_rows"].astype(int)
    out["dropped_older_srcdate_rows"] = out["raw_rows"] - out["latest_source_rows"]
    out["dropped_pct_of_raw"] = np.where(
        out["raw_rows"].gt(0),
        (out["dropped_older_srcdate_rows"] / out["raw_rows"] * 100).round(1),
        0.0,
    )
    return out.sort_values("raw_rows", ascending=False)


def read_existing_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
