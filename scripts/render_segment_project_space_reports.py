#!/usr/bin/env python3
"""Render the segment project-space HTML reports from generated artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
import pandas as pd

from segment_project_common import (
    APPENDIX_PATH,
    DATA_PATH,
    FIG_DIR,
    GUIDE_PATH,
    INDEX_PATH,
    OUT_DIR,
    PATHS_PATH,
    QA_PATH,
    REGRESSION_PATH,
    REPORT_PATH,
    ROOT,
    TABLE_DIR,
    read_existing_csv,
    read_table,
    utc_now,
)


REQUIRED_TABLES = [
    "segment_project_source_metadata.csv",
    "segment_project_latest_srcdate_dedup_summary.csv",
    "segment_project_stype_summary.csv",
    "segment_project_design_readiness.csv",
    "segment_project_variable_coverage.csv",
    "segment_project_code_coverage.csv",
    "segment_project_decade_readiness.csv",
    "segment_project_key_uniqueness.csv",
    "segment_project_variable_dictionary.csv",
    "segment_project_coverage_definitions.csv",
    "segment_project_exposure_definitions.csv",
    "segment_project_exposure_family_readiness.csv",
    "segment_project_name_keyword_readiness.csv",
    "segment_project_geography_decade_readiness.csv",
    "segment_project_top_geographic_names.csv",
    "segment_project_top_geographic_currencies.csv",
    "segment_project_candidate_shock_catalog.csv",
    "segment_project_candidate_shock_sources.csv",
    "segment_project_candidate_shock_type_summary.csv",
    "segment_project_event_family_mapping.csv",
    "segment_project_event_window_readiness.csv",
    "segment_project_workstream_inventory.csv",
    "segment_project_existing_result_manifest.csv",
    "segment_project_regression_result_manifest.csv",
    "segment_project_regression_outcome_definitions.csv",
    "segment_project_regression_specifications.csv",
    "segment_project_regression_results_compact.csv",
    "segment_project_regression_result_summary.csv",
]

PRIMARY_NUMERIC = ["sales", "ops", "capxs", "ias", "emps", "rds", "ppents"]
DESCRIPTIVE_TABLE_DIR = ROOT / "reports" / "segment_descriptives" / "tables"


def fmt_number(value: object, decimals: int = 1) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        if abs(value) >= 1000:
            return f"{float(value):,.{decimals}f}"
        return f"{float(value):.{decimals}f}"
    return str(value)


def escape(value: object) -> str:
    return html.escape("" if pd.isna(value) else str(value))


def linkify(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    parts = [part.strip() for part in text.split(";") if part.strip()]
    if parts and all(part.startswith(("http://", "https://")) for part in parts):
        links = []
        for idx, url in enumerate(parts, start=1):
            links.append(f'<a href="{escape(url)}">source {idx}</a>')
        return "; ".join(links)
    if text.startswith(("http://", "https://")):
        return f'<a href="{escape(text)}">source</a>'
    return escape(value)


def html_table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    max_rows: int | None = None,
    classes: str = "",
) -> str:
    if columns is not None:
        out = df.loc[:, columns].copy()
    else:
        out = df.copy()
    if max_rows is not None:
        out = out.head(max_rows).copy()
    if out.empty:
        return '<p class="muted">No rows.</p>'

    header = "".join(f"<th>{escape(col)}</th>" for col in out.columns)
    rows = []
    for _, row in out.iterrows():
        cells = []
        for col, value in row.items():
            if isinstance(value, (int, float, np.integer, np.floating)):
                cells.append(f'<td class="num">{escape(fmt_number(value))}</td>')
            elif "url" in str(col).lower():
                cells.append(f"<td>{linkify(value)}</td>")
            else:
                cells.append(f"<td>{escape(value)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<div class="table-wrap"><table class="{classes}">'
        f'<thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def base_css() -> str:
    return """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #1f2933; background: #f6f7f5; }
    main { max-width: 1120px; margin: 0 auto; padding: 34px 28px 64px; background: #fff; }
    h1 { font-size: 30px; margin: 0 0 10px; letter-spacing: 0; }
    h2 { font-size: 21px; margin-top: 32px; border-top: 1px solid #d9ded6; padding-top: 22px; }
    h3 { font-size: 17px; margin-top: 22px; }
    p, li { line-height: 1.5; font-size: 15px; }
    a { color: #245d6b; }
    code { background: #eef1ed; padding: 1px 4px; border-radius: 3px; }
    .muted { color: #667085; }
    .summary { background: #eef4f1; border-left: 4px solid #3c7d8f; padding: 14px 18px; margin: 20px 0; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 18px 0 24px; }
    .grid.four { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .card, .metric, .note { border: 1px solid #d9ded6; padding: 14px; border-radius: 6px; background: #fbfcfb; }
    .metric strong { display: block; font-size: 20px; margin-top: 4px; }
    .table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    table { width: 100%; border-collapse: collapse; margin: 14px 0 22px; font-size: 13px; }
    th, td { border-bottom: 1px solid #e2e5df; padding: 8px 9px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
    th { background: #f0f2ef; font-weight: 650; }
    td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
    figure { margin: 20px 0 24px; }
    img { max-width: 100%; height: auto; border: 1px solid #e2e5df; border-radius: 6px; background: #fff; }
    figcaption { color: #667085; font-size: 12px; margin-top: 6px; }
    .callout { border: 1px solid #d9ded6; border-radius: 6px; padding: 14px 16px; background: #fbfcfb; }
    .nav { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 24px; }
    .nav a { border: 1px solid #cad2c7; border-radius: 4px; padding: 7px 10px; text-decoration: none; background: #fff; font-size: 14px; }
    .nav a.active { background: #245d6b; border-color: #245d6b; color: #fff; }
    @media (max-width: 820px) { .grid, .grid.four { grid-template-columns: 1fr; } main { padding: 24px 16px 48px; } }
    """


def nav_html(active: str) -> str:
    links = [
        ("overview", "Overview", "index.html"),
        ("report", "Start Here", "segment_project_space_report.html"),
        ("guide", "Data Guide", "01_data_guide.html"),
        ("paths", "Workstream Update", "02_research_paths.html"),
        ("regression", "Regression Results", "04_regression_results.html"),
        ("appendix", "Evidence Appendix", "03_evidence_appendix.html"),
    ]
    items = []
    for key, label, href in links:
        cls = "active" if key == active else ""
        items.append(f'<a class="{cls}" href="{href}">{escape(label)}</a>')
    return '<nav class="nav">' + "".join(items) + "</nav>"


def report_shell(title: str, generated_at: str, active: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{base_css()}</style>
</head>
<body>
<main>
  <h1>{escape(title)}</h1>
  <p class="muted">Generated at UTC: {escape(generated_at)}. Source: {escape(DATA_PATH.relative_to(ROOT))}.</p>
  {nav_html(active)}
{body}
</main>
</body>
</html>
"""


def img_tag(filename: str, alt: str) -> str:
    path = FIG_DIR / filename
    if not path.exists():
        return ""
    rel = path.relative_to(OUT_DIR)
    return f'<figure><img src="{escape(rel)}" alt="{escape(alt)}"><figcaption>{escape(alt)}</figcaption></figure>'


def source_meta_value(meta: pd.DataFrame, field: str, default: object = "") -> object:
    if meta.empty or field not in meta.columns:
        return default
    return meta.iloc[0][field]


def read_descriptive_table(name: str) -> pd.DataFrame:
    path = DESCRIPTIVE_TABLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Missing generated descriptive table: {path.relative_to(ROOT)}. "
            "Run scripts/build_segment_descriptive_tables.py first."
        )
    return pd.read_csv(path)


def maybe_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [col for col in columns if col in df.columns]


def render_overview_page(
    generated_at: str,
    source_meta: pd.DataFrame,
    shock_catalog: pd.DataFrame,
) -> str:
    raw_rows = int(source_meta_value(source_meta, "raw_rows", 0))
    dedup_rows = int(source_meta_value(source_meta, "latest_source_rows", 0))
    source_hash = str(source_meta_value(source_meta, "source_sha256", ""))
    body = f"""
  <section>
    <h2>Coauthor Orientation</h2>
    <div class="summary">
      <p><strong>This static report bundle is written for a coauthor joining the project midstream.</strong> It separates data orientation, workstream status, regression evidence, and detailed appendix tables so the reader can enter at the level they need.</p>
      <p><strong>The report pages are generated from checked tables and figures.</strong> The raw WRDS/Compustat and other licensed inputs are not included in this browsable bundle.</p>
    </div>
    <div class="grid four">
      <div class="metric"><span>Raw rows</span><strong>{raw_rows:,}</strong></div>
      <div class="metric"><span>Latest-source rows</span><strong>{dedup_rows:,}</strong></div>
      <div class="metric"><span>Candidate shocks</span><strong>{len(shock_catalog):,}</strong></div>
      <div class="metric"><span>Source hash</span><strong style="font-size:12px">{escape(source_hash[:12])}</strong></div>
    </div>
  </section>

  <section>
    <h2>Open The Report</h2>
    <div class="grid">
      <div class="card">
        <h3>Start Here</h3>
        <p>Main coauthor orientation, current design choices, and links to the rest of the report series.</p>
        <p><a href="segment_project_space_report.html">Open start page</a></p>
      </div>
      <div class="card">
        <h3>Data Guide</h3>
        <p>Row definitions, segment types, deduplication, descriptive statistics, variable quartiles, and coverage definitions.</p>
        <p><a href="01_data_guide.html">Open data guide</a></p>
      </div>
      <div class="card">
        <h3>Workstream Update</h3>
        <p>Neutral status update on possible research directions, source-backed shock windows, and open design choices.</p>
        <p><a href="02_research_paths.html">Open update</a></p>
      </div>
      <div class="card">
        <h3>Regression Results</h3>
        <p>Current RSZ-style regression result tables, outcome construction, treatment definitions, and model specification notes.</p>
        <p><a href="04_regression_results.html">Open regression tab</a></p>
      </div>
      <div class="card">
        <h3>Evidence Appendix</h3>
        <p>Detailed coverage tables, shock source rows, geography/name screens, and event-window readiness tables.</p>
        <p><a href="03_evidence_appendix.html">Open appendix</a></p>
      </div>
    </div>
  </section>

  <section>
    <h2>Suggested Reading Order</h2>
    <ol>
      <li><a href="segment_project_space_report.html">Start Here</a> for the short orientation.</li>
      <li><a href="01_data_guide.html">Data Guide</a> for what the data contains and the descriptive tables.</li>
      <li><a href="02_research_paths.html">Workstream Update</a> for project direction and open decisions.</li>
      <li><a href="04_regression_results.html">Regression Results</a> for model definitions and current result tables.</li>
      <li><a href="03_evidence_appendix.html">Evidence Appendix</a> when you need source and coverage details behind a claim.</li>
    </ol>
  </section>

  <section>
    <h2>Repository Context</h2>
    <div class="note">
      <p>This static site is served from <code>reports/segment_project_space/</code>. The renderer writes standalone HTML, figures, and backing tables; it does not load the raw segment file when the site is viewed.</p>
    </div>
  </section>
"""
    return report_shell("Project Thales: Segment Data Briefing", generated_at, "overview", body)


def render_index_report(
    generated_at: str,
    source_meta: pd.DataFrame,
    workstreams: pd.DataFrame,
    shock_catalog: pd.DataFrame,
    shock_type_summary: pd.DataFrame,
) -> str:
    raw_rows = int(source_meta_value(source_meta, "raw_rows", 0))
    dedup_rows = int(source_meta_value(source_meta, "latest_source_rows", 0))
    source_hash = str(source_meta_value(source_meta, "source_sha256", ""))
    body = f"""
  <section>
    <h2>Coauthor Orientation</h2>
    <div class="summary">
      <p><strong>This report series is written for a new coauthor.</strong> It starts with what the segment dataset contains, explains coverage terms, then summarizes the workstreams and source-backed candidate shock windows explored so far.</p>
      <p><strong>The workstream and shock tables are descriptive.</strong> They record current data anchors, source windows, unresolved mapping requirements, and possible follow-up data so the research direction can be chosen separately.</p>
    </div>
    <div class="grid four">
      <div class="metric"><span>Raw rows</span><strong>{raw_rows:,}</strong></div>
      <div class="metric"><span>Latest-source rows</span><strong>{dedup_rows:,}</strong></div>
      <div class="metric"><span>Candidate shocks cataloged</span><strong>{len(shock_catalog):,}</strong></div>
      <div class="metric"><span>Source hash</span><strong style="font-size:12px">{escape(source_hash[:12])}</strong></div>
    </div>
  </section>

  <section>
    <h2>Report Series</h2>
    <div class="grid">
      <div class="card">
        <h3>1. Data Guide</h3>
        <p>Plain-English variable descriptions, segment types, deduplication, descriptive tables, and how coverage is defined.</p>
        <p><a href="01_data_guide.html">Open the data guide</a></p>
      </div>
      <div class="card">
        <h3>2. Workstream Update</h3>
        <p>A neutral status update on possible workstreams, specific shock windows, current data anchors, and open design choices.</p>
        <p><a href="02_research_paths.html">Open the workstream update</a></p>
      </div>
      <div class="card">
        <h3>3. Regression Results</h3>
        <p>Current RSZ-style regression evidence, outcome construction, treatment/control definitions, and model specification notes.</p>
        <p><a href="04_regression_results.html">Open the regression tab</a></p>
      </div>
      <div class="card">
        <h3>4. Evidence Appendix</h3>
        <p>The detailed tables, charts, online source table, geography/name screens, and mechanical event-window screens.</p>
        <p><a href="03_evidence_appendix.html">Open the evidence appendix</a></p>
      </div>
    </div>
  </section>

  <section>
    <h2>Current Project Snapshot</h2>
    <p><strong>Dataset:</strong> the raw source is a Compustat segment file with business, geographic, operating, and state segment rows. The report series uses the latest <code>srcdate</code> per provisional segment key as the default cleaned view.</p>
    <p><strong>Variables in active use:</strong> sales, operating profit, capital expenditures, identifiable assets, employees, R&D, segment names, segment type, and industry codes.</p>
    <p><strong>Open design choices:</strong> which shock family to center, which exposure definition is acceptable, whether to treat input-cost and output-price mechanisms separately, and what external data are needed for exposure validation.</p>
  </section>

  <section>
    <h2>Generated Result Contracts</h2>
    <p>The HTML pages are rendered from generated CSV, JSON, and PNG artifacts under <code>reports/segment_project_space/</code> plus the generated descriptive-statistics bundle under <code>reports/segment_descriptives/</code>. The renderer does not load the raw segment file or recompute coverage.</p>
    {html_table(workstreams[["workstream", "current_data_anchor", "unresolved_items"]].head(5))}
  </section>
"""
    return report_shell("Segment Data Coauthor Briefing: Start Here", generated_at, "report", body)


def render_data_guide(
    generated_at: str,
    source_meta: pd.DataFrame,
    dedup_summary: pd.DataFrame,
    stypes: pd.DataFrame,
    design: pd.DataFrame,
    variables: pd.DataFrame,
    var_dict: pd.DataFrame,
    cov_defs: pd.DataFrame,
    desc_source: pd.DataFrame,
    desc_segment_counts: pd.DataFrame,
    desc_variable_quartiles: pd.DataFrame,
    desc_firmyear_structure: pd.DataFrame,
    desc_defs: pd.DataFrame,
) -> str:
    raw_rows = int(source_meta_value(source_meta, "raw_rows", 0))
    dedup_rows = int(source_meta_value(source_meta, "latest_source_rows", 0))
    primary_cov = variables[variables["variable"].isin(PRIMARY_NUMERIC)].copy().sort_values(["stype", "variable"])
    guide_design = design[
        design["design"].isin(["Segment operating margin", "RSZ capital allocation", "Employment allocation", "R&D allocation", "Geographic FX exposure"])
    ].copy()
    latest_counts = desc_segment_counts[
        desc_segment_counts["view"].eq("latest_source")
        & desc_segment_counts["measure"].eq("reported_segment_rows")
    ].copy()
    selected_quartiles = desc_variable_quartiles[
        desc_variable_quartiles["view"].eq("latest_source")
        & desc_variable_quartiles["stype"].isin(["ALL_STYPES", "BUSSEG", "GEOSEG", "OPSEG"])
        & desc_variable_quartiles["variable"].isin(["sales", "ops", "capxs", "ias", "emps", "rds", "op_margin", "capx_to_assets"])
    ].copy()
    selected_structure = desc_firmyear_structure[
        desc_firmyear_structure["view"].eq("latest_source")
        & desc_firmyear_structure["stype"].isin(["ALL_STYPES", "BUSSEG", "GEOSEG", "OPSEG"])
        & desc_firmyear_structure["variable"].isin(["reported_segment_rows", "total_positive_sales", "sales_hhi", "top_segment_sales_share"])
    ].copy()
    body = f"""
  <section>
    <h2>What A Row Represents</h2>
    <p>A row is a reported Compustat segment observation for a firm at a fiscal date. It is not automatically a unique operating business: historical rows can repeat across source update dates, and some segment rows are corporate, elimination, unallocated, or reconciliation rows.</p>
    <div class="grid">
      <div class="metric"><span>Raw source rows</span><strong>{raw_rows:,}</strong></div>
      <div class="metric"><span>Rows after latest-source dedup</span><strong>{dedup_rows:,}</strong></div>
      <div class="metric"><span>Default key</span><strong style="font-size:13px">gvkey + datadate + stype + sid</strong></div>
    </div>
    <p><strong>Default cleaning rule:</strong> this report keeps the latest <code>srcdate</code> for each provisional <code>gvkey</code>, <code>datadate</code>, <code>stype</code>, <code>sid</code> key. This removes older duplicate source snapshots; it is not a research-sample exclusion.</p>
    <h3>Rows removed by latest-source deduplication</h3>
    {html_table(dedup_summary)}
  </section>

  <section>
    <h2>Segment Types</h2>
    <p>The same variable can have very different coverage by segment type. In the current scripts, <code>BUSSEG</code> is the main source for business-segment performance and allocation outcomes, while <code>GEOSEG</code> is used for geography and disclosure-oriented checks.</p>
    {html_table(stypes, ["stype", "rows", "firms", "firm_years", "min_year", "max_year", "unique_segment_names"])}
  </section>

  <section>
    <h2>Table-Style Descriptives From The Original Data</h2>
    <p>These tables are generated by <code>scripts/build_segment_descriptive_tables.py</code>. The latest-source view is the cleaner default for paper-style descriptive tables because repeated source snapshots are removed; the raw-source view is retained in the standalone descriptive bundle for audit.</p>
    <p><a href="https://github.com/SoYelv/Project_Thales/blob/main/reports/segment_descriptives/segment_descriptive_report.md">Open the standalone descriptive-statistics memo on GitHub</a></p>
    <h3>Source rows by segment type</h3>
    {html_table(desc_source)}
    <h3>Reported segments per firm-year-stype</h3>
    {html_table(latest_counts, ["stype", "firm_year_units", "mean", "sd", "p25", "p50", "p75", "p90", "p95", "max", "share_gt1_pct"])}
    <h3>Selected segment-level variable quartiles</h3>
    {html_table(selected_quartiles, ["stype", "variable", "segment_rows", "nonmissing_n", "missing_pct", "mean", "sd", "p25", "p50", "p75", "p95"], max_rows=40)}
    <h3>Selected firm-year segment structure</h3>
    {html_table(selected_structure, ["stype", "variable", "firm_year_units", "nonmissing_n", "missing_pct", "mean", "sd", "p25", "p50", "p75", "p95"], max_rows=24)}
    <h3>Additional descriptive definitions</h3>
    {html_table(desc_defs.tail(5))}
  </section>

  <section>
    <h2>How Coverage Is Defined</h2>
    <p>Coverage is measured at the row level unless the table explicitly says firms or firm-years. A row can be present in the data but not usable for a particular design if one required variable is missing.</p>
    {html_table(cov_defs)}
    <div class="callout">
      <p><strong>Example:</strong> a BUSSEG row is margin-ready only when <code>sales</code> and <code>ops</code> are both present and <code>sales</code> is not zero. A BUSSEG row is RSZ allocation-ready only when <code>sales</code>, <code>ops</code>, <code>capxs</code>, and <code>ias</code> are all present.</p>
    </div>
  </section>

  <section>
    <h2>Variable Descriptions</h2>
    <p>This glossary describes how the project currently reads each field. It is meant to orient collaborators; final paper language can cite the WRDS/Compustat data dictionary for formal field definitions.</p>
    {html_table(var_dict)}
  </section>

  <section>
    <h2>Which Designs Have Enough Fields?</h2>
    <p>Design-ready definitions require multiple fields at once, so they are more restrictive than single-variable nonmissingness.</p>
    {html_table(guide_design.sort_values(["design", "ready_rows"], ascending=[True, False]), ["stype", "design", "outcome_family", "rows", "ready_rows", "ready_pct", "firms_with_ready_rows", "firm_years_with_ready_rows", "min_year", "max_year"])}
    <h3>Primary variable coverage</h3>
    {html_table(primary_cov, ["variable", "stype", "rows", "nonmissing_pct", "positive_pct", "firms_nonmissing", "firm_years_nonmissing", "min_year", "max_year"])}
  </section>
"""
    return report_shell("Segment Data Guide", generated_at, "guide", body)


def render_research_paths(
    generated_at: str,
    workstreams: pd.DataFrame,
    family: pd.DataFrame,
    exposure_defs: pd.DataFrame,
    shock_catalog: pd.DataFrame,
    shock_type_summary: pd.DataFrame,
    events: pd.DataFrame,
) -> str:
    top_family = family.head(10)
    event_core = events[events["window"].eq("event_pm5y")].copy()
    event_core = event_core.sort_values(["shock_type", "event_anchor_year", "shock_id"])
    catalog_display = shock_catalog.sort_values(["shock_type", "event_anchor_year", "shock_id"])[
        [
            "shock_family",
            "candidate_window",
            "event_anchor_year",
            "shock_type",
            "source_summary",
            "exposure_families",
            "mapping_requirement",
            "caveats",
        ]
    ]
    body = f"""
  <section>
    <h2>Workstream Update</h2>
    <div class="summary">
      <p><strong>This page records the project space as a status update.</strong> Each row states what question the workstream could answer, what the current segment data anchor is, what has already been run, and what remains unresolved.</p>
      <p><strong>The tables are for discussion.</strong> They do not choose a direction or define treatment/control rules.</p>
    </div>
  </section>

  <section>
    <h2>Workstream Inventory</h2>
    {html_table(workstreams, ["workstream", "question_it_would_help_answer", "current_data_anchor", "segment_data_inputs", "work_completed_so_far", "unresolved_items", "possible_follow_up_data"])}
  </section>

  <section>
    <h2>Candidate Shock Windows By Specific Shock</h2>
    <p>The shock catalog is based on online source checks and is separated from treatment assignment. The visible unit here is the specific candidate shock. The type field is retained only to help scan whether the row is a derivative-listing window, market-design change, regional market expansion, compliance market, policy-market access row, or event shock.</p>
    {img_tag("candidate_shock_windows_by_shock.png", "Candidate shock windows by specific shock")}
    <h3>Candidate window catalog</h3>
    {html_table(catalog_display)}
  </section>

  <section>
    <h2>Exposure Families Available In BUSSEG/OPSEG</h2>
    <p>The current script screens industry and segment-SIC exposure because those fields connect to segment operating and investment outcomes. These are coverage screens, not final treatment definitions.</p>
    <p>The exposure screen starts from <code>seg_sic</code>, defined as the first nonmissing value of <code>sics1</code>, <code>sics2</code>, then firm-level <code>sic</code>. A few segment-name keyword checks are added where the SIC alone may miss labeled segments.</p>
    <h3>Current exposure-screen rules</h3>
    {html_table(exposure_defs)}
    <h3>Coverage under those rules</h3>
    {img_tag("industry_family_sample.png", "Industry exposure families available in BUSSEG/OPSEG")}
    {html_table(top_family, ["exposure_family", "rows", "firms", "firm_years", "min_year", "max_year", "margin_ready_pct", "allocation_ready_pct"])}
  </section>

  <section>
    <h2>Mechanical Event-Window Coverage</h2>
    <p>The event-window table applies the current exposure-family screen to each source-backed candidate. It shows whether there are segment rows around the anchor year; it does not assign treated firms.</p>
    {html_table(event_core, ["shock_family", "candidate_window", "event_anchor_year", "shock_type", "exposure_families", "firms", "firm_years", "margin_ready_pct", "allocation_ready_pct"])}
  </section>

  <section>
    <h2>Open Design Choices</h2>
    <ol>
      <li><strong>Shock family:</strong> electricity, natural gas, WTI crude, weather, freight, metals/mining, RIN/carbon, policy-market access, or currency/geography exposure.</li>
      <li><strong>Exposure definition:</strong> HQ-state proxy, segment industry proxy, input-intensity proxy, plant/service-territory data, or filing-text evidence.</li>
      <li><strong>Mechanism split:</strong> whether output-price hedgeability and input-cost hedgeability belong in one paper frame or separate analyses.</li>
      <li><strong>Outcome family:</strong> segment reporting, RSZ-style capital allocation, margin volatility, segment survival, employment/R&D/resource allocation, or derivative disclosure text.</li>
    </ol>
  </section>
"""
    return report_shell("Segment Workstream Update", generated_at, "paths", body)


def render_regression_results(
    generated_at: str,
    result_manifest: pd.DataFrame,
    outcome_defs: pd.DataFrame,
    spec_defs: pd.DataFrame,
    compact_results: pd.DataFrame,
    result_summary: pd.DataFrame,
) -> str:
    early_results = compact_results[compact_results["result_id"].eq("strict_early_electricity")].copy()
    output_input_results = compact_results[compact_results["result_id"].eq("output_input_electricity")].copy()
    modern_results = compact_results[compact_results["result_id"].eq("modern_electricity")].copy()
    key_cols = [
        "result_id",
        "design",
        "shock",
        "mechanism_group",
        "sample",
        "opportunity",
        "post_lag",
        "control",
        "status",
        "coef",
        "se",
        "t",
        "p",
        "nobs",
        "firms_in_estimation",
        "treated_firms_in_stack",
        "control_firms_in_stack",
    ]
    compact_cols = maybe_columns(compact_results, key_cols)
    body = f"""
  <section>
    <h2>What The Current Regressions Estimate</h2>
    <div class="summary">
      <p><strong>The current tables are RSZ-style internal capital-allocation regressions.</strong> The reported coefficient is the interaction between a segment's relative opportunity measure, the treated-firm indicator, and the post-event period. It is not a treatment effect on the level of investment.</p>
      <p><strong>The outcome is within-firm allocation.</strong> Segment investment intensity is <code>capxs / lagged ias</code>, then demeaned across segments inside the same cohort, firm, and year. This asks whether treated firms allocate relatively more or less investment to high-opportunity segments after the event.</p>
    </div>
    <p>Current result rows use two opportunity variables: <code>l_margin</code>, lagged segment operating margin, and <code>sgrow</code>, segment sales growth. Both are converted to within-firm relative opportunity measures before entering the regression.</p>
  </section>

  <section>
    <h2>Outcome And Variable Construction</h2>
    {html_table(outcome_defs)}
  </section>

  <section>
    <h2>Regression Specifications</h2>
    <p>The table below states the design used by each result table. The national-break rows are kept separate because their control group is a period-break screen, not a clean regional not-yet-treated control pool.</p>
    {html_table(spec_defs)}
  </section>

  <section>
    <h2>Model Form</h2>
    <p>The common estimating equation can be read as:</p>
    <div class="callout">
      <p><code>rel_inv[j,f,t,c] = beta * rel_opp[j,f,t,c] x treated[f,c] x post[t,c] + controls/interactions + cohort-segment FE + cohort-year FE + error[j,f,t,c]</code></p>
    </div>
    <p><code>beta</code> is the coefficient reported as <code>coef</code> in the result tables. Standard errors are clustered by firm in the current scripts. The estimation sample is restricted to multisegment firm-years after required variables are present; <code>pre_multiseg</code> additionally requires pre-period multisegment status inside the cohort window.</p>
  </section>

  <section>
    <h2>Generated Result Manifest</h2>
    {html_table(result_manifest)}
  </section>

  <section>
    <h2>Compact Result Summary</h2>
    <p>This summary groups the existing result rows by result table, design, mechanism group, and opportunity variable. It is an index into the full rows below.</p>
    {html_table(result_summary)}
  </section>

  <section>
    <h2>Full Current Regression Rows</h2>
    <h3>Strict early electricity</h3>
    {html_table(early_results, compact_cols)}
    <h3>Separated output/input early electricity</h3>
    {html_table(output_input_results, compact_cols)}
    <h3>Modern electricity screens</h3>
    {html_table(modern_results, compact_cols)}
  </section>

  <section>
    <h2>How To Read The Result Columns</h2>
    <ul>
      <li><code>coef</code>: coefficient on the RSZ allocation-sensitivity interaction.</li>
      <li><code>opportunity</code>: segment opportunity measure before within-firm demeaning; currently <code>l_margin</code> or <code>sgrow</code>.</li>
      <li><code>nobs</code>: segment-year observations used by the fitted panel model.</li>
      <li><code>firms_in_estimation</code>: distinct firms in the fitted stacked sample.</li>
      <li><code>treated_firms_in_stack</code> and <code>control_firms_in_stack</code>: distinct treated/control firms in the stacked sample when the runner records them.</li>
      <li><code>status</code>: fit status reported by the runner; <code>ok</code> means the model returned coefficient, standard error, t-statistic, and p-value.</li>
    </ul>
  </section>
"""
    return report_shell("Segment Regression Results", generated_at, "regression", body)


def render_evidence_appendix(
    generated_at: str,
    stypes: pd.DataFrame,
    design: pd.DataFrame,
    variables: pd.DataFrame,
    codes: pd.DataFrame,
    decades: pd.DataFrame,
    keys: pd.DataFrame,
    family: pd.DataFrame,
    event_mapping: pd.DataFrame,
    events: pd.DataFrame,
    geodecade: pd.DataFrame,
    geo_names: pd.DataFrame,
    geo_curr: pd.DataFrame,
    name_keywords: pd.DataFrame,
    shock_sources: pd.DataFrame,
    result_manifest: pd.DataFrame,
) -> str:
    important_vars = variables[variables["variable"].isin([*PRIMARY_NUMERIC, "oibdps", "oiadps", "salexg", "intseg", "oelim"])].copy()
    source_display = shock_sources[["shock_id", "source_title", "source_type", "source_claim", "source_url"]].copy()
    body = f"""
  <section>
    <h2>Outcome Readiness Detail</h2>
    {img_tag("outcome_readiness_by_stype.png", "Outcome readiness by segment type")}
    {html_table(design.sort_values(["outcome_family", "ready_rows"], ascending=[True, False]))}
  </section>

  <section>
    <h2>Segment Type And Variable Coverage</h2>
    {html_table(stypes)}
    <h3>Selected variable coverage</h3>
    {html_table(important_vars.sort_values(["variable", "stype"]), ["variable", "stype", "rows", "nonmissing_pct", "positive_pct", "firms_nonmissing", "firm_years_nonmissing", "min_year", "max_year"])}
    <h3>Code-field coverage</h3>
    {html_table(codes.sort_values(["code_field", "stype"]))}
  </section>

  <section>
    <h2>Time, Keys, And Deduplication</h2>
    <h3>Decade readiness</h3>
    {html_table(decades)}
    <h3>Candidate key uniqueness before deduplication</h3>
    {html_table(keys)}
  </section>

  <section>
    <h2>Exposure And Event Screens</h2>
    {img_tag("industry_family_sample.png", "Industry exposure families available in BUSSEG/OPSEG")}
    {html_table(family)}
    <h3>Shock-to-exposure family mapping</h3>
    {html_table(event_mapping)}
    <h3>Event-window readiness</h3>
    {html_table(events.sort_values(["shock_type", "event_anchor_year", "shock_id", "window"]))}
  </section>

  <section>
    <h2>Online Source Table For Candidate Shocks</h2>
    <p>These source rows back the candidate shock catalog. They document event windows and institutional changes, not firm-level hedge use.</p>
    {html_table(source_display)}
  </section>

  <section>
    <h2>Geography, Currency, And Names</h2>
    {img_tag("geographic_feasibility_by_decade.png", "Geographic segment feasibility by decade")}
    {html_table(geodecade)}
    <h3>Top geographic names</h3>
    <p>The first row can be missing because older GEOSEG records often have no reported <code>snms</code> segment name. Treat <code>[missing segment name]</code> as source-data missingness, not as a geography category.</p>
    {html_table(geo_names.head(40))}
    <h3>Top geographic source currencies</h3>
    {html_table(geo_curr.head(40))}
    <h3>Segment-name keyword screens</h3>
    {html_table(name_keywords)}
  </section>

  <section>
    <h2>Regression Table Locations</h2>
    <p>The regression result tables are now documented in a separate page because they require outcome construction and model-specification context. Use <a href="04_regression_results.html">Regression Results</a> for the model definitions and current coefficients.</p>
    <h3>Existing result manifest</h3>
    {html_table(result_manifest)}
  </section>
"""
    return report_shell("Segment Evidence Appendix", generated_at, "appendix", body)


def load_generated_tables() -> dict[str, pd.DataFrame]:
    return {name: read_table(name) for name in REQUIRED_TABLES}


def load_descriptive_tables() -> dict[str, pd.DataFrame]:
    return {
        "table1_source_rows_by_segment_type.csv": read_descriptive_table("table1_source_rows_by_segment_type.csv"),
        "table2_segments_per_firm_year_distribution.csv": read_descriptive_table(
            "table2_segments_per_firm_year_distribution.csv"
        ),
        "table3_segment_variable_quartiles.csv": read_descriptive_table("table3_segment_variable_quartiles.csv"),
        "table4_firm_year_segment_structure.csv": read_descriptive_table("table4_firm_year_segment_structure.csv"),
        "table5_descriptive_definitions.csv": read_descriptive_table("table5_descriptive_definitions.csv"),
    }


def remove_obsolete_artifacts() -> None:
    for obsolete in [
        TABLE_DIR / "segment_project_lane_scores.csv",
        FIG_DIR / "project_lane_scores.png",
    ]:
        if obsolete.exists():
            obsolete.unlink()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_obsolete_artifacts()
    generated_at = utc_now()
    tables = load_generated_tables()
    desc_tables = load_descriptive_tables()

    reports = {
        INDEX_PATH: render_overview_page(
            generated_at=generated_at,
            source_meta=tables["segment_project_source_metadata.csv"],
            shock_catalog=tables["segment_project_candidate_shock_catalog.csv"],
        ),
        REPORT_PATH: render_index_report(
            generated_at=generated_at,
            source_meta=tables["segment_project_source_metadata.csv"],
            workstreams=tables["segment_project_workstream_inventory.csv"],
            shock_catalog=tables["segment_project_candidate_shock_catalog.csv"],
            shock_type_summary=tables["segment_project_candidate_shock_type_summary.csv"],
        ),
        GUIDE_PATH: render_data_guide(
            generated_at=generated_at,
            source_meta=tables["segment_project_source_metadata.csv"],
            dedup_summary=tables["segment_project_latest_srcdate_dedup_summary.csv"],
            stypes=tables["segment_project_stype_summary.csv"],
            design=tables["segment_project_design_readiness.csv"],
            variables=tables["segment_project_variable_coverage.csv"],
            var_dict=tables["segment_project_variable_dictionary.csv"],
            cov_defs=tables["segment_project_coverage_definitions.csv"],
            desc_source=desc_tables["table1_source_rows_by_segment_type.csv"],
            desc_segment_counts=desc_tables["table2_segments_per_firm_year_distribution.csv"],
            desc_variable_quartiles=desc_tables["table3_segment_variable_quartiles.csv"],
            desc_firmyear_structure=desc_tables["table4_firm_year_segment_structure.csv"],
            desc_defs=desc_tables["table5_descriptive_definitions.csv"],
        ),
        PATHS_PATH: render_research_paths(
            generated_at=generated_at,
            workstreams=tables["segment_project_workstream_inventory.csv"],
            family=tables["segment_project_exposure_family_readiness.csv"],
            exposure_defs=tables["segment_project_exposure_definitions.csv"],
            shock_catalog=tables["segment_project_candidate_shock_catalog.csv"],
            shock_type_summary=tables["segment_project_candidate_shock_type_summary.csv"],
            events=tables["segment_project_event_window_readiness.csv"],
        ),
        REGRESSION_PATH: render_regression_results(
            generated_at=generated_at,
            result_manifest=tables["segment_project_regression_result_manifest.csv"],
            outcome_defs=tables["segment_project_regression_outcome_definitions.csv"],
            spec_defs=tables["segment_project_regression_specifications.csv"],
            compact_results=tables["segment_project_regression_results_compact.csv"],
            result_summary=tables["segment_project_regression_result_summary.csv"],
        ),
        APPENDIX_PATH: render_evidence_appendix(
            generated_at=generated_at,
            stypes=tables["segment_project_stype_summary.csv"],
            design=tables["segment_project_design_readiness.csv"],
            variables=tables["segment_project_variable_coverage.csv"],
            codes=tables["segment_project_code_coverage.csv"],
            decades=tables["segment_project_decade_readiness.csv"],
            keys=tables["segment_project_key_uniqueness.csv"],
            family=tables["segment_project_exposure_family_readiness.csv"],
            event_mapping=tables["segment_project_event_family_mapping.csv"],
            events=tables["segment_project_event_window_readiness.csv"],
            geodecade=tables["segment_project_geography_decade_readiness.csv"],
            geo_names=tables["segment_project_top_geographic_names.csv"],
            geo_curr=tables["segment_project_top_geographic_currencies.csv"],
            name_keywords=tables["segment_project_name_keyword_readiness.csv"],
            shock_sources=tables["segment_project_candidate_shock_sources.csv"],
            result_manifest=tables["segment_project_existing_result_manifest.csv"],
        ),
    }
    for path, content in reports.items():
        path.write_text(content, encoding="utf-8")

    source_meta = tables["segment_project_source_metadata.csv"]
    qa = {
        "generated_at_utc": generated_at,
        "source_path": str(DATA_PATH.relative_to(ROOT)),
        "source_sha256": str(source_meta_value(source_meta, "source_sha256", "")),
        "raw_rows": int(source_meta_value(source_meta, "raw_rows", 0)),
        "latest_srcdate_rows": int(source_meta_value(source_meta, "latest_source_rows", 0)),
        "tables_written": sorted(p.name for p in TABLE_DIR.glob("*.csv")),
        "figures_written": sorted(p.name for p in FIG_DIR.glob("*.png")),
        "report_paths": [str(path.relative_to(ROOT)) for path in reports],
        "required_tables_read": REQUIRED_TABLES,
        "descriptive_tables_read": [str((DESCRIPTIVE_TABLE_DIR / name).relative_to(ROOT)) for name in desc_tables],
        "notes": [
            "Report renderer reads generated CSV/JSON/PNG artifacts only.",
            "Candidate shocks are source-backed windows, not treatment/control rules.",
            "Workstream inventory rows are descriptive and do not choose project directions.",
            "Regression results are documented in a separate tab because they require outcome and model-specification context.",
        ],
    }
    QA_PATH.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    for path in reports:
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"wrote {QA_PATH.relative_to(ROOT)}")
    print(f"tables: {len(qa['tables_written'])}, figures: {len(qa['figures_written'])}")


if __name__ == "__main__":
    main()
