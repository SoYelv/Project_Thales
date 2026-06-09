#!/usr/bin/env python3
"""Static definition tables for the segment project-space reports."""

from __future__ import annotations

import pandas as pd


def variable_dictionary() -> pd.DataFrame:
    rows = [
        ("gvkey", "Firm identifier", "Compustat firm key. Used as the firm id for counts, panels, joins, and clustering.", "Identifier coverage is treated as a build prerequisite, not as a feasibility metric."),
        ("datadate", "Fiscal period date", "Report date for the segment observation. The script extracts calendar year from this date.", "A row needs a parsed date to enter year or event-window summaries."),
        ("year", "Derived year", "Calendar year derived from datadate for time windows and decade summaries.", "Not a raw field; missing when datadate cannot be parsed."),
        ("stype", "Segment table type", "Distinguishes business, geographic, operating, and state segment records.", "Coverage is summarized separately by stype because fields behave very differently across segment types."),
        ("sid", "Segment id", "Segment identifier used with gvkey, datadate, stype, and srcdate for provisional row keys.", "Not treated as globally unique by itself."),
        ("srcdate", "Source update date", "Compustat source date. The baseline keeps the latest srcdate per provisional key.", "Used for deduplication, not as an outcome."),
        ("conm", "Company name", "Readable company label for examples and inspection.", "Not used to define coverage."),
        ("tic", "Ticker", "Readable ticker where available.", "Not used to define coverage."),
        ("snms", "Segment name", "Reported segment name. Useful for screening geography, electricity, oil/gas, corporate, or unallocated labels.", "Name coverage means snms is nonblank; keyword coverage is only a discovery aid."),
        ("sic", "Firm SIC", "Firm-level industry code. Used as fallback when segment SIC is absent.", "Code coverage means the field is nonmissing; final exposure definitions can be externally validated."),
        ("sics1, sics2", "Segment SIC codes", "Segment-level industry codes. Used before firm SIC for exposure screens.", "Coverage is nonmissingness in either segment code field."),
        ("naics, naicss1, naicss2", "Firm and segment NAICS codes", "Alternative industry codes retained for future exposure checks.", "Currently profiled, but SIC is the main exposure map in this script."),
        ("gind, gsubind", "GICS fields", "Industry classification fields retained for optional robustness.", "Coverage is reported, but these fields are not the primary exposure definitions."),
        ("curcds", "Segment currency code", "Currency code associated with segment data where reported.", "Potential control or audit field, not a primary coverage denominator."),
        ("isosrc", "Source country/currency marker", "In GEOSEG rows this often behaves like a source country or currency marker.", "Currency readiness requires isosrc to be nonblank; non-US currency excludes USD/US."),
        ("geotp", "Geographic type", "Geographic segment type/category when reported.", "Profiled as a possible geography-quality field."),
        ("sales", "Segment sales", "Main scale denominator for margins, shares, and segment weights.", "Sales coverage is nonmissing; margin calculations also require sales not equal to zero."),
        ("ops", "Segment operating profit", "Used with sales to form operating margin and alpha-style performance measures.", "Margin-ready rows require sales and ops both present and sales nonzero."),
        ("capxs", "Segment capital expenditures", "Core investment outcome for capital-allocation tests.", "Allocation-ready rows require capxs plus the relevant denominator and performance fields."),
        ("ias", "Segment identifiable assets", "Main asset denominator for capex/assets and RSZ-style investment scaling.", "RSZ allocation readiness requires sales, ops, capxs, and ias."),
        ("ppents", "Segment property, plant, and equipment", "Possible tangible-capital resource measure.", "Profiled as an optional outcome/control field."),
        ("emps", "Segment employees", "Possible labor/resource allocation outcome.", "Employment-ready rows require sales and emps."),
        ("rds", "Segment R&D", "Possible innovation/resource allocation outcome.", "R&D-ready rows require sales and rds."),
        ("ops / sales", "Derived operating margin", "Segment operating performance used for alpha and opportunity measures.", "Defined only when sales and ops are present and sales is not zero."),
        ("capxs / ias", "Derived capex/assets", "Investment intensity relative to segment assets.", "Defined only when capxs and ias are present and ias is not zero."),
        ("segment count", "Derived disclosure granularity", "Number of segment rows or operating segments within a firm-year.", "Ready when the segment rows are present after deduplication."),
        ("HHI", "Derived concentration", "Sales concentration across operating segments within a firm-year.", "Requires positive operating-segment sales within the firm-year."),
    ]
    return pd.DataFrame(rows, columns=["field", "plain_english_description", "how_this_project_uses_it", "coverage_rule"])


def coverage_definitions() -> pd.DataFrame:
    rows = [
        ("raw rows", "All rows read from data/raw/segment_data.csv before deduplication.", "This is the source inventory count."),
        ("latest-source rows", "Rows after keeping the latest srcdate for each gvkey, datadate, stype, sid key.", "This is the default denominator for the report series."),
        ("dropped older srcdate rows", "Rows removed because a newer source snapshot exists for the same gvkey, datadate, stype, sid key.", "This removes duplicate source snapshots; it is not a research-sample exclusion."),
        ("rows", "Segment-level observations in the displayed group after latest-source deduplication.", "Used to show raw table scale."),
        ("firms", "Distinct gvkey values with at least one row in the displayed group.", "Used to show the number of companies represented."),
        ("firm-years", "Distinct gvkey and datadate combinations with at least one row in the displayed group.", "Used to show panel support for regressions."),
        ("nonmissing pct", "Share of rows where a single field is not missing.", "Used for variable-level coverage."),
        ("margin-ready pct", "Share of rows with sales and ops present and sales not equal to zero.", "Used for operating-margin and alpha-style analyses."),
        ("RSZ allocation-ready pct", "Share of rows with sales, ops, capxs, and ias all present.", "Used for segment capital-allocation feasibility."),
        ("employment-ready rows", "Rows with sales and emps present.", "Used for segment labor/resource feasibility."),
        ("R&D-ready rows", "Rows with sales and rds present.", "Used for segment innovation/resource feasibility."),
        ("geographic FX exposure readiness", "GEOSEG rows with sales and a nonblank segment name.", "A screen for possible geography/currency exposure, not a complete causal design."),
        ("event-window readiness", "Coverage within mechanical pre/event/post windows around candidate shocks.", "A data support screen only; it does not prove identification."),
    ]
    return pd.DataFrame(rows, columns=["term", "definition", "how_to_read_it"])


def exposure_definitions() -> pd.DataFrame:
    rows = [
        ("seg_sic", "first nonmissing of sics1, sics2, then firm sic", "Segment SIC is used first. Firm SIC is only a fallback when segment SIC is missing."),
        ("electric_power_output", "SIC 4910-4939 or 4991; or segment name contains ELECTRIC, POWER, UTILITY", "Captures electric power or utility segment exposure for coverage exploration."),
        ("gas_utility", "SIC 4920-4925; or segment name contains NATURAL GAS or GAS UTILITY", "Captures gas utility segment exposure."),
        ("oil_gas_petroleum", "SIC 1311, 1380-1389, 2911, 4610-4619; or segment name contains OIL, GAS, PETROLEUM, REFIN", "Captures oil, gas, petroleum, refining, and pipeline-related segment exposure."),
        ("broader_energy", "electric_power_output or gas_utility or oil_gas_petroleum or SIC 4900-4999", "Broad energy/utility screen used to summarize overall energy exposure."),
        ("metals_mining", "SIC 1000-1499 or 3310-3399", "Mining plus primary metal manufacturing screen."),
        ("agriculture_food", "SIC 0100-0999 or 2000-2099", "Agriculture and food manufacturing screen."),
        ("transport_freight", "SIC 4000-4799", "Transportation and freight industry screen."),
        ("airlines_fuel_sensitive", "SIC 4512, 4513, 4581; or segment name contains AIRLINE, AVIATION, AIR", "Air transport screen used as a possible fuel-sensitive subgroup."),
        ("chemicals", "SIC 2800-2899", "Chemical manufacturing screen."),
        ("paper_pulp", "SIC 2600-2699; or segment name contains PAPER or PULP", "Paper and pulp screen."),
        ("cement_minerals", "SIC 3200-3299; or segment name contains CEMENT, LIME, MINERAL, GLASS", "Stone, clay, glass, cement, and minerals screen."),
    ]
    return pd.DataFrame(rows, columns=["exposure_field", "current_rule", "how_to_read_it"])
