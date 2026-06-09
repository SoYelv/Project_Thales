#!/usr/bin/env python3
"""Exploratory profile for WRDS Compustat segment data.

The goal is not to clean the data yet. It is to answer a design question from
the proposal: which derivative-availability shock is best supported by the
segment file currently in the project?
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "segment_data.csv"
if not DATA_PATH.exists():
    DATA_PATH = ROOT / "segment_data.csv"
REPORT_DIR = ROOT / "reports"
TABLE_DIR = REPORT_DIR / "tables"
REPORT_PATH = REPORT_DIR / "segment_exploration.md"

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
    "ops",
    "capxs",
    "ias",
    "emps",
    "rds",
    "ppents",
    "sid",
    "srcdate",
]

KEY_VARS = ["sales", "ops", "capxs", "ias", "emps", "rds", "ppents"]
READY_VARS = ["sales", "ops", "capxs", "ias"]


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def first_nonmissing_code(*values: object) -> float | None:
    for value in values:
        if pd.notna(value):
            return float(value)
    return None


def sic_group(row: pd.Series) -> str:
    code = first_nonmissing_code(row.get("sics1"), row.get("sics2"), row.get("sic"))
    if code is None:
        return "Missing SIC"
    sic = int(code)

    if sic == 1311 or 1380 <= sic <= 1389 or sic == 2911 or 4600 <= sic <= 4699:
        return "Oil/gas and petroleum"
    if 1000 <= sic <= 1499 or 3310 <= sic <= 3399:
        return "Metals and mining"
    if 4900 <= sic <= 4999:
        return "Utilities and power"
    if 4000 <= sic <= 4799:
        return "Transport and freight"
    if 100 <= sic <= 999 or 2000 <= sic <= 2099:
        return "Agriculture and food"
    return "Other industries"


def write_table(df: pd.DataFrame, name: str) -> None:
    df.to_csv(TABLE_DIR / name, index=False)


def pct(series: pd.Series) -> pd.Series:
    return (series * 100).round(1)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{int(value):,}"


def fmt_num(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):,.2f}"


def md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    out = df.head(max_rows).copy()
    for col in out.columns:
        if pd.api.types.is_integer_dtype(out[col]):
            out[col] = out[col].map(fmt_int)
        elif pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(fmt_num)
    out = out.fillna("").astype(str)
    headers = list(out.columns)
    rows = out.values.tolist()
    widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows))
        for i, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(str(header).ljust(widths[i]) for i, header in enumerate(headers)) + " |"
    separator = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)) + " |"
        for row in rows
    ]
    return "\n".join([header_line, separator, *body])


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, usecols=USECOLS, low_memory=False)
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df["srcdate_dt"] = pd.to_datetime(df["srcdate"], errors="coerce")
    df["year"] = df["datadate"].dt.year
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    rows = len(df)
    firms = df["gvkey"].nunique(dropna=True)
    firm_years = df[["gvkey", "datadate"]].drop_duplicates().shape[0]

    source_meta = pd.DataFrame(
        [
            {
                "source_path": str(DATA_PATH),
                "bytes": DATA_PATH.stat().st_size,
                "sha256": sha256_file(DATA_PATH),
                "rows": rows,
                "columns_read": len(USECOLS),
                "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        ]
    )
    write_table(source_meta, "segment_source_metadata.csv")

    stype_summary = (
        df.groupby("stype", dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            firm_years=("datadate", lambda x: df.loc[x.index, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
            min_year=("year", "min"),
            max_year=("year", "max"),
            unique_segment_names=("snms", pd.Series.nunique),
            unique_source_currencies=("isosrc", pd.Series.nunique),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    write_table(stype_summary, "segment_stype_summary.csv")

    missing_rows = []
    for stype, part in df.groupby("stype", dropna=False):
        row = {"stype": stype, "rows": len(part)}
        for col in KEY_VARS:
            row[f"{col}_nonmissing_pct"] = round(part[col].notna().mean() * 100, 1)
        row["alpha_ready_sales_ops_pct"] = round(part[["sales", "ops"]].notna().all(axis=1).mean() * 100, 1)
        row["allocation_ready_sales_ops_capxs_pct"] = round(
            part[["sales", "ops", "capxs"]].notna().all(axis=1).mean() * 100, 1
        )
        row["full_ready_sales_ops_capxs_ias_pct"] = round(part[READY_VARS].notna().all(axis=1).mean() * 100, 1)
        missing_rows.append(row)
    missingness = pd.DataFrame(missing_rows).sort_values("rows", ascending=False)
    write_table(missingness, "segment_key_variable_coverage.csv")

    annual = (
        df.groupby(["year", "stype"], dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            firm_years=("datadate", lambda x: df.loc[x.index, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
            sales_nonmissing_pct=("sales", lambda x: round(x.notna().mean() * 100, 1)),
            ops_nonmissing_pct=("ops", lambda x: round(x.notna().mean() * 100, 1)),
            capxs_nonmissing_pct=("capxs", lambda x: round(x.notna().mean() * 100, 1)),
        )
        .reset_index()
        .sort_values(["stype", "year"])
    )
    write_table(annual, "segment_annual_coverage_by_stype.csv")

    seg_counts = (
        df.groupby(["stype", "gvkey", "datadate"], dropna=False)
        .agg(segment_rows=("sid", "size"), named_segments=("snms", pd.Series.nunique))
        .reset_index()
    )
    granularity = (
        seg_counts.groupby("stype", dropna=False)
        .agg(
            firm_years=("segment_rows", "size"),
            mean_segment_rows=("segment_rows", "mean"),
            median_segment_rows=("segment_rows", "median"),
            p75_segment_rows=("segment_rows", lambda x: x.quantile(0.75)),
            p90_segment_rows=("segment_rows", lambda x: x.quantile(0.90)),
            share_multi_segment=("segment_rows", lambda x: round((x > 1).mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("firm_years", ascending=False)
    )
    write_table(granularity, "segment_granularity_by_stype.csv")

    key_cols = ["gvkey", "datadate", "stype", "sid"]
    duplicates = (
        df.groupby(key_cols, dropna=False)
        .size()
        .reset_index(name="rows_per_key")
        .query("rows_per_key > 1")
        .groupby("stype", dropna=False)
        .agg(duplicate_keys=("rows_per_key", "size"), duplicate_rows=("rows_per_key", "sum"), max_rows_per_key=("rows_per_key", "max"))
        .reset_index()
        .sort_values("duplicate_rows", ascending=False)
    )
    write_table(duplicates, "segment_duplicate_key_check.csv")

    latest = (
        df.sort_values(["gvkey", "datadate", "stype", "sid", "srcdate_dt"], na_position="first")
        .drop_duplicates(key_cols, keep="last")
        .copy()
    )
    dedup_summary = (
        df.groupby("stype", dropna=False)
        .size()
        .rename("raw_rows")
        .reset_index()
        .merge(
            latest.groupby("stype", dropna=False).size().rename("latest_srcdate_rows").reset_index(),
            on="stype",
            how="left",
        )
    )
    dedup_summary["dropped_rows"] = dedup_summary["raw_rows"] - dedup_summary["latest_srcdate_rows"]
    dedup_summary["dropped_pct"] = (dedup_summary["dropped_rows"] / dedup_summary["raw_rows"] * 100).round(1)
    dedup_summary = dedup_summary.sort_values("raw_rows", ascending=False)
    write_table(dedup_summary, "segment_latest_srcdate_dedup_summary.csv")

    latest_missing_rows = []
    for stype, part in latest.groupby("stype", dropna=False):
        row = {"stype": stype, "rows": len(part)}
        for col in KEY_VARS:
            row[f"{col}_nonmissing_pct"] = round(part[col].notna().mean() * 100, 1)
        row["alpha_ready_sales_ops_pct"] = round(part[["sales", "ops"]].notna().all(axis=1).mean() * 100, 1)
        row["allocation_ready_sales_ops_capxs_pct"] = round(
            part[["sales", "ops", "capxs"]].notna().all(axis=1).mean() * 100, 1
        )
        row["full_ready_sales_ops_capxs_ias_pct"] = round(part[READY_VARS].notna().all(axis=1).mean() * 100, 1)
        latest_missing_rows.append(row)
    latest_missingness = pd.DataFrame(latest_missing_rows).sort_values("rows", ascending=False)
    write_table(latest_missingness, "segment_latest_key_variable_coverage.csv")

    top_geo_names = (
        df.loc[df["stype"].eq("GEOSEG"), "snms"]
        .value_counts(dropna=False)
        .head(40)
        .rename_axis("segment_name")
        .reset_index(name="rows")
    )
    write_table(top_geo_names, "segment_top_geographic_names.csv")

    top_geo_currency = (
        df.loc[df["stype"].eq("GEOSEG"), "isosrc"]
        .value_counts(dropna=False)
        .head(40)
        .rename_axis("source_currency")
        .reset_index(name="rows")
    )
    write_table(top_geo_currency, "segment_top_geographic_source_currencies.csv")

    geo = df[df["stype"].eq("GEOSEG")].copy()
    geo["has_source_currency"] = geo["isosrc"].notna()
    geo["has_segment_name"] = geo["snms"].notna()
    geo_annual = (
        geo.groupby("year")
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            has_segment_name_pct=("has_segment_name", lambda x: round(x.mean() * 100, 1)),
            has_source_currency_pct=("has_source_currency", lambda x: round(x.mean() * 100, 1)),
            ops_nonmissing_pct=("ops", lambda x: round(x.notna().mean() * 100, 1)),
            capxs_nonmissing_pct=("capxs", lambda x: round(x.notna().mean() * 100, 1)),
        )
        .reset_index()
    )
    write_table(geo_annual, "segment_geoseg_annual_currency_readiness.csv")

    work = df[df["stype"].isin(["BUSSEG", "OPSEG"])].copy()
    work["shock_family_proxy"] = work.apply(sic_group, axis=1)
    industry = (
        work.groupby("shock_family_proxy", dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            firm_years=("datadate", lambda x: work.loc[x.index, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
            min_year=("year", "min"),
            max_year=("year", "max"),
            sales_nonmissing_pct=("sales", lambda x: round(x.notna().mean() * 100, 1)),
            ops_nonmissing_pct=("ops", lambda x: round(x.notna().mean() * 100, 1)),
            capxs_nonmissing_pct=("capxs", lambda x: round(x.notna().mean() * 100, 1)),
            ias_nonmissing_pct=("ias", lambda x: round(x.notna().mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    write_table(industry, "segment_industry_proxy_coverage.csv")

    event_windows = [
        ("crude_oil_1983", 1983, ["Oil/gas and petroleum"]),
        ("natural_gas_1990", 1990, ["Oil/gas and petroleum", "Utilities and power"]),
        ("weather_1997_1999", 1998, ["Utilities and power", "Agriculture and food"]),
        ("freight_derivatives", 1992, ["Transport and freight"]),
    ]
    event_rows = []
    for event, event_year, groups in event_windows:
        part = work[work["shock_family_proxy"].isin(groups)].copy()
        for window_name, lo, hi in [
            ("minus5_plus5", event_year - 5, event_year + 5),
            ("minus10_minus1", event_year - 10, event_year - 1),
            ("plus1_plus10", event_year + 1, event_year + 10),
        ]:
            window = part[part["year"].between(lo, hi)]
            event_rows.append(
                {
                    "event": event,
                    "proxy_groups": "; ".join(groups),
                    "window": window_name,
                    "start_year": lo,
                    "end_year": hi,
                    "rows": len(window),
                    "firms": window["gvkey"].nunique(dropna=True),
                    "firm_years": window[["gvkey", "datadate"]].drop_duplicates().shape[0],
                    "alpha_ready_sales_ops_pct": round(window[["sales", "ops"]].notna().all(axis=1).mean() * 100, 1)
                    if len(window)
                    else 0,
                    "allocation_ready_sales_ops_capxs_pct": round(
                        window[["sales", "ops", "capxs"]].notna().all(axis=1).mean() * 100, 1
                    )
                    if len(window)
                    else 0,
                }
            )
    event_readiness = pd.DataFrame(event_rows)
    write_table(event_readiness, "segment_candidate_shock_window_readiness.csv")

    latest_work = latest[latest["stype"].isin(["BUSSEG", "OPSEG"])].copy()
    latest_work["shock_family_proxy"] = latest_work.apply(sic_group, axis=1)
    latest_industry = (
        latest_work.groupby("shock_family_proxy", dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            firm_years=("datadate", lambda x: latest_work.loc[x.index, ["gvkey", "datadate"]].drop_duplicates().shape[0]),
            min_year=("year", "min"),
            max_year=("year", "max"),
            sales_nonmissing_pct=("sales", lambda x: round(x.notna().mean() * 100, 1)),
            ops_nonmissing_pct=("ops", lambda x: round(x.notna().mean() * 100, 1)),
            capxs_nonmissing_pct=("capxs", lambda x: round(x.notna().mean() * 100, 1)),
            ias_nonmissing_pct=("ias", lambda x: round(x.notna().mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    write_table(latest_industry, "segment_latest_industry_proxy_coverage.csv")

    latest_event_rows = []
    for event, event_year, groups in event_windows:
        part = latest_work[latest_work["shock_family_proxy"].isin(groups)].copy()
        for window_name, lo, hi in [
            ("minus5_plus5", event_year - 5, event_year + 5),
            ("minus10_minus1", event_year - 10, event_year - 1),
            ("plus1_plus10", event_year + 1, event_year + 10),
        ]:
            window = part[part["year"].between(lo, hi)]
            latest_event_rows.append(
                {
                    "event": event,
                    "proxy_groups": "; ".join(groups),
                    "window": window_name,
                    "start_year": lo,
                    "end_year": hi,
                    "rows": len(window),
                    "firms": window["gvkey"].nunique(dropna=True),
                    "firm_years": window[["gvkey", "datadate"]].drop_duplicates().shape[0],
                    "alpha_ready_sales_ops_pct": round(window[["sales", "ops"]].notna().all(axis=1).mean() * 100, 1)
                    if len(window)
                    else 0,
                    "allocation_ready_sales_ops_capxs_pct": round(
                        window[["sales", "ops", "capxs"]].notna().all(axis=1).mean() * 100, 1
                    )
                    if len(window)
                    else 0,
                }
            )
    latest_event_readiness = pd.DataFrame(latest_event_rows)
    write_table(latest_event_readiness, "segment_latest_candidate_shock_window_readiness.csv")

    annual_group = (
        work.groupby(["year", "shock_family_proxy"], dropna=False)
        .agg(
            rows=("stype", "size"),
            firms=("gvkey", pd.Series.nunique),
            alpha_ready_rows=("sales", lambda x: work.loc[x.index, ["sales", "ops"]].notna().all(axis=1).sum()),
            allocation_ready_rows=("sales", lambda x: work.loc[x.index, ["sales", "ops", "capxs"]].notna().all(axis=1).sum()),
        )
        .reset_index()
    )
    write_table(annual_group, "segment_annual_industry_proxy_readiness.csv")

    report = f"""# Segment Data Exploration

Generated at UTC: {datetime.now(timezone.utc).isoformat(timespec="seconds")}

## Proposal-Implied Data Requirements

The proposal needs a derivative-availability shock that can be linked to pre-existing firm exposure. The segment data is most useful if it supports:

1. segment operating performance, especially `ops / sales`, to estimate the pre-period moderator alpha;
2. segment investment or resources, especially `capxs`, `ias`, `ppents`, or `emps`, for internal capital allocation and information granularity outcomes;
3. a credible exposure proxy before the derivative launch, such as geography/currency or segment industry.

## Source Inventory

- Source file: `{DATA_PATH.relative_to(ROOT)}`
- Rows: {rows:,}
- Firms: {firms:,}
- Firm-years: {firm_years:,}
- Date range: {int(df["year"].min())}-{int(df["year"].max())}
- SHA-256: `{source_meta.loc[0, "sha256"]}`

## Segment Type Coverage

{md_table(stype_summary)}

## Key Variable Coverage

{md_table(missingness)}

## Reporting Granularity

{md_table(granularity)}

## Duplicate Key Check

Using `gvkey`, `datadate`, `stype`, and `sid` as a provisional key produces duplicate keys, so future cleaning should not assume this is a unique identifier without additional segment-name or source-date logic.

{md_table(duplicates)}

Keeping the latest `srcdate` per provisional key gives the following de-duplicated row counts:

{md_table(dedup_summary)}

Latest-source-date key variable coverage:

{md_table(latest_missingness)}

## Geography/Currency Readiness

Geographic segment rows are abundant, but operating variables are thin. This makes geography useful for identifying foreign exposure or segment granularity, but weaker as the main source for alpha or internal capital allocation tests.

Top geographic segment names:

{md_table(top_geo_names.head(20))}

Top source currencies in geographic rows:

{md_table(top_geo_currency.head(20))}

## Industry Shock Proxy Coverage

Business and operating segments have much better operating-performance and investment fields. SIC-based industry proxies are therefore the stronger match for the proposal's alpha and capital-allocation tests.

{md_table(industry)}

The same coverage after keeping only the latest `srcdate` per provisional segment key:

{md_table(latest_industry)}

## Candidate Shock Window Readiness

The table below is a mechanical coverage check, not a causal design. It asks whether the current segment file has enough observations around plausible derivative-availability windows for the affected segment industries.

{md_table(event_readiness)}

Latest-source-date de-duplicated version:

{md_table(latest_event_readiness)}

## Bottom Line

Based on this file alone, commodity/energy derivative shocks are the best-supported starting point. Business and operating segments provide enough sales, operating profit, assets, and capex coverage to estimate segment operating margins and internal capital allocation around energy-related launch windows. Currency shocks are conceptually closest to the motivating example, and the file has many geographic rows, but the key operating variables in `GEOSEG` are too sparse for alpha and allocation tests without another data source or substantial text parsing. Weather shocks are attractive theoretically because prior work exists, but this file has very limited state-level segment data and country/region geography is too coarse for clean weather exposure. Freight is feasible only as a narrow robustness or extension because transport/freight segments are identifiable but much smaller.

Recommended next empirical path:

1. Start with oil/gas and energy derivative availability as the primary shock family.
2. Use `BUSSEG` and `OPSEG` to construct segment operating margin and segment capex/investment outcomes.
3. Treat `GEOSEG` as a secondary source for foreign-exposure controls or reporting-granularity outcomes, not as the primary alpha dataset.
4. Build the next script around a firm-segment-year panel with clean keys, segment exclusions for corporate/eliminations/other, winsorized operating margins, and SIC/NAICS exposure groups.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
