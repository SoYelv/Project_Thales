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
    OUT_DIR,
    PATHS_PATH,
    QA_PATH,
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
]

PRIMARY_NUMERIC = ["sales", "ops", "capxs", "ias", "emps", "rds", "ppents"]


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
    .card, .metric { border: 1px solid #d9ded6; padding: 14px; border-radius: 6px; background: #fbfcfb; }
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
        <p>Plain-English variable descriptions, segment types, deduplication, and how coverage is defined.</p>
        <p><a href="01_data_guide.html">Open the data guide</a></p>
      </div>
      <div class="card">
        <h3>2. Workstream Update</h3>
        <p>A neutral status update on possible workstreams, specific shock windows, current data anchors, and open design choices.</p>
        <p><a href="02_research_paths.html">Open the workstream update</a></p>
      </div>
      <div class="card">
        <h3>3. Evidence Appendix</h3>
        <p>The detailed tables, charts, current regression evidence, online source table, and mechanical event-window screens.</p>
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
    <p>The HTML pages are rendered from generated CSV, JSON, and PNG artifacts under <code>reports/segment_project_space/</code>. The renderer does not load the raw segment file or recompute coverage.</p>
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
) -> str:
    raw_rows = int(source_meta_value(source_meta, "raw_rows", 0))
    dedup_rows = int(source_meta_value(source_meta, "latest_source_rows", 0))
    primary_cov = variables[variables["variable"].isin(PRIMARY_NUMERIC)].copy().sort_values(["stype", "variable"])
    guide_design = design[
        design["design"].isin(["Segment operating margin", "RSZ capital allocation", "Employment allocation", "R&D allocation", "Geographic FX exposure"])
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
    early_results = read_existing_csv(ROOT / "reports" / "tables" / "t1_strict_identification_results.csv")
    output_input_results = read_existing_csv(ROOT / "reports" / "tables" / "electricity_output_input_rsz_results.csv")
    modern_results = read_existing_csv(ROOT / "reports" / "tables" / "electricity_output_input_modern_rsz_results.csv")
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
    <h2>Current Evidence Tables From The Repo</h2>
    <h3>Existing result manifest</h3>
    {html_table(result_manifest)}
    <h3>Strict early electricity results</h3>
    {html_table(early_results)}
    <h3>Separated output/input RSZ results</h3>
    {html_table(output_input_results)}
    <h3>Modern electricity screen</h3>
    {html_table(modern_results)}
  </section>
"""
    return report_shell("Segment Evidence Appendix", generated_at, "appendix", body)


def load_generated_tables() -> dict[str, pd.DataFrame]:
    return {name: read_table(name) for name in REQUIRED_TABLES}


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

    reports = {
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
        "notes": [
            "Report renderer reads generated CSV/JSON/PNG artifacts only.",
            "Candidate shocks are source-backed windows, not treatment/control rules.",
            "Workstream inventory rows are descriptive and do not choose project directions.",
        ],
    }
    QA_PATH.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    for path in reports:
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"wrote {QA_PATH.relative_to(ROOT)}")
    print(f"tables: {len(qa['tables_written'])}, figures: {len(qa['figures_written'])}")


if __name__ == "__main__":
    main()
