#!/usr/bin/env python3
"""Build coauthor-update workstream inventory tables."""

from __future__ import annotations

import pandas as pd

from segment_project_common import ROOT, read_existing_csv, read_table, utc_now, write_json, write_table


def existing_result_manifest() -> pd.DataFrame:
    specs = [
        ("strict_early_electricity", ROOT / "reports" / "tables" / "t1_strict_identification_results.csv", "Early electricity producer-side result table"),
        ("output_input_electricity", ROOT / "reports" / "tables" / "electricity_output_input_rsz_results.csv", "Separated output/input electricity result table"),
        ("modern_electricity", ROOT / "reports" / "tables" / "electricity_output_input_modern_rsz_results.csv", "Modern electricity screen result table"),
        ("electricity_group_counts", ROOT / "reports" / "tables" / "electricity_output_input_group_counts.csv", "Output/input mechanism group counts"),
        ("modern_electricity_group_counts", ROOT / "reports" / "tables" / "electricity_output_input_modern_group_counts.csv", "Modern mechanism group counts"),
    ]
    rows = []
    for result_id, path, description in specs:
        df = read_existing_csv(path)
        rows.append(
            {
                "result_id": result_id,
                "description": description,
                "path": str(path.relative_to(ROOT)),
                "status": "present" if path.exists() else "missing",
                "rows": int(len(df)) if not df.empty else 0,
                "columns": "; ".join(df.columns.astype(str)) if not df.empty else "",
            }
        )
    return pd.DataFrame(rows)


def project_workstreams(
    family: pd.DataFrame,
    geodecade: pd.DataFrame,
    early_results: pd.DataFrame,
    input_results: pd.DataFrame,
    shock_type_summary: pd.DataFrame,
) -> pd.DataFrame:
    def metric_row(name: str) -> pd.Series:
        matches = family[family["exposure_family"].eq(name)]
        return matches.iloc[0] if len(matches) else pd.Series(dtype=object)

    electricity = metric_row("electric_power_output")
    oilgas = metric_row("oil_gas_petroleum")
    transport = metric_row("transport_freight")
    metals = metric_row("metals_mining")
    geo_margin = float(geodecade["margin_ready_pct"].mean()) if len(geodecade) else 0.0

    early_status = "Strict early electricity tables are not present in reports/tables/t1_strict_identification_results.csv."
    if not early_results.empty and {"coef", "t", "p"}.issubset(early_results.columns):
        row = early_results.iloc[0]
        early_status = f"Strict early RSZ margin row is present: coef {row['coef']:+.3f}, t={row['t']:.2f}."

    input_status = "Input-user mechanism groups have not been summarized from the existing RSZ table."
    if not input_results.empty and "mechanism_group" in input_results.columns:
        m = input_results[input_results["mechanism_group"].astype(str).str.contains("input", case=False, na=False)]
        if len(m):
            row = m.iloc[0]
            input_status = f"Input manufacturing RSZ margin row is present: coef {row['coef']:+.3f}, t={row['t']:.2f}."

    shock_summary = f"{len(shock_type_summary):,} source-backed shock types are cataloged."
    if len(shock_type_summary):
        years = (int(shock_type_summary["first_anchor_year"].min()), int(shock_type_summary["last_anchor_year"].max()))
        shock_summary = f"{len(shock_type_summary):,} source-backed shock types are cataloged, spanning anchor years {years[0]}-{years[1]}."

    rows = [
        {
            "workstream": "Candidate shock catalog",
            "question_it_would_help_answer": "Which event families and windows are available for discussion before choosing a research design.",
            "current_data_anchor": shock_summary,
            "segment_data_inputs": "Generated shock catalog, source table, exposure-family mapping, and event-window readiness screens.",
            "work_completed_so_far": "Online source-backed catalog rows are grouped by shock type and separated from treatment/control decisions.",
            "unresolved_items": "Each candidate still needs an explicit treatment map if it is used in estimation.",
            "possible_follow_up_data": "Contract rulebooks, exchange histories, ISO/RTO membership, utility territories, plant locations, and filing examples.",
        },
        {
            "workstream": "Early electricity output-producer hedgeability",
            "question_it_would_help_answer": "Whether new electricity hedgeability is associated with changes in segment reporting or internal capital allocation among electricity producers.",
            "current_data_anchor": f"{int(electricity.get('firms', 0)):,} firms; {int(electricity.get('firm_years', 0)):,} firm-years in the electric-power exposure screen.",
            "segment_data_inputs": "BUSSEG/OPSEG segment operating margin, capex, assets, segment counts, HHI, and non-operating segment indicators.",
            "work_completed_so_far": early_status,
            "unresolved_items": "HQ-state shock assignment is currently a proxy for operating exposure.",
            "possible_follow_up_data": "Plant locations, utility operating-company footprints, service territories, EIA/FERC data, or other operating-footprint evidence.",
        },
        {
            "workstream": "Electricity input-cost users",
            "question_it_would_help_answer": "Whether high-electricity-input firms respond differently when electricity procurement or market structure changes.",
            "current_data_anchor": "Existing input-intensity files identify high-usage manufacturing and industrial candidates.",
            "segment_data_inputs": "BUSSEG/OPSEG electricity-input intensity proxies, margins, capex, segment survival, and industry composition.",
            "work_completed_so_far": input_status,
            "unresolved_items": "The outcome definition for input-cost users remains to be specified separately from the producer-side RSZ outcome.",
            "possible_follow_up_data": "Direct power-procurement disclosures, Item 7A derivative text, plant-level electricity intensity, margin volatility, or procurement-region exposure.",
        },
        {
            "workstream": "Modern electricity market expansion screens",
            "question_it_would_help_answer": "Whether later power-market changes are visible in segment allocation or reporting outcomes.",
            "current_data_anchor": f"Segment data extends through {int(electricity.get('max_year', 0))} for the electric-power exposure screen.",
            "segment_data_inputs": "BUSSEG/OPSEG RSZ-style allocation outcomes and firm-year segment granularity measures.",
            "work_completed_so_far": "Modern regional, EIM, and period-break result tables are present in reports/tables/ where generated.",
            "unresolved_items": "Regional treatment mapping and treated cohort size vary across events.",
            "possible_follow_up_data": "Event-specific operating footprints, market participation data, and a written event-by-event treatment map.",
        },
        {
            "workstream": "Energy commodity producer shocks: WTI and natural gas",
            "question_it_would_help_answer": "Whether energy commodity derivative availability is associated with segment-level performance or investment allocation.",
            "current_data_anchor": f"{int(oilgas.get('firms', 0)):,} firms; {int(oilgas.get('firm_years', 0)):,} firm-years in the oil/gas and petroleum exposure screen.",
            "segment_data_inputs": "BUSSEG/OPSEG operating margin, capex, assets, and energy-industry exposure groups.",
            "work_completed_so_far": "The shock catalog now separates petroleum, refined-product, natural-gas, RIN, export, and storage/dislocation windows.",
            "unresolved_items": "The treatment map and mechanism narrative need to be separated from the electricity-output workstream.",
            "possible_follow_up_data": "Contract launch documentation, commodity exposure validation, facility/geography links, and firm/segment examples.",
        },
        {
            "workstream": "Geographic and currency exposure",
            "question_it_would_help_answer": "Whether foreign or currency exposure can be measured from geographic segment disclosures.",
            "current_data_anchor": f"GEOSEG average margin-ready share across decades is {geo_margin:.1f}%; name and source-currency availability improve after the 1990s.",
            "segment_data_inputs": "GEOSEG names, source currency/country fields, sales, and geographic segment counts.",
            "work_completed_so_far": "The report series profiles GEOSEG decade coverage, top geography names, and top source currencies.",
            "unresolved_items": "Geographic labels are broad, and ops/capxs coverage is lower than in BUSSEG.",
            "possible_follow_up_data": "Country/region parsing, FX derivative launch dates, foreign-sales controls, and text examples from filings.",
        },
        {
            "workstream": "Weather derivative or weather-risk exposure",
            "question_it_would_help_answer": "Whether weather-risk hedging or exposure can be linked to segment reporting or allocation.",
            "current_data_anchor": "STSEG is small; GEOSEG is mostly country/region geography rather than local operating exposure.",
            "segment_data_inputs": "STSEG where available, GEOSEG names, utility/agriculture segment screens, and segment reporting granularity.",
            "work_completed_so_far": "The shock catalog includes a 1999 weather-derivative window and a mechanical coverage screen.",
            "unresolved_items": "Local exposure is not directly observed in the segment file.",
            "possible_follow_up_data": "Plant/location data, local weather exposure, service territories, and weather-derivative market event documentation.",
        },
        {
            "workstream": "Freight and transport derivative exposure",
            "question_it_would_help_answer": "Whether freight or transport derivative availability can be connected to segment investment or operating outcomes.",
            "current_data_anchor": f"{int(transport.get('firms', 0)):,} firms; {int(transport.get('firm_years', 0)):,} firm-years in the transport/freight exposure screen.",
            "segment_data_inputs": "BUSSEG/OPSEG transport/freight industry screens, operating margin, capex, and assets.",
            "work_completed_so_far": "The shock catalog separates early Baltic freight derivatives from modern route products.",
            "unresolved_items": "The treated population has not been connected to route or trade-flow exposure.",
            "possible_follow_up_data": "Freight derivative launch sources, shipping/airline/rail exposure checks, and industry-specific examples.",
        },
        {
            "workstream": "Metals/mining and commodity producer exposure",
            "question_it_would_help_answer": "Whether metal or mining commodity derivative availability can be connected to segment performance or investment.",
            "current_data_anchor": f"{int(metals.get('firms', 0)):,} firms; {int(metals.get('firm_years', 0)):,} firm-years in the metals/mining exposure screen.",
            "segment_data_inputs": "BUSSEG/OPSEG metals/mining industry screens, operating margin, capex, and assets.",
            "work_completed_so_far": "The shock catalog includes metals contract availability and silver market-rule windows.",
            "unresolved_items": "Commodity-specific producer/user exposure is not yet separated.",
            "possible_follow_up_data": "Contract launch sources, commodity exposure examples, and industry-specific treatment definitions.",
        },
        {
            "workstream": "Segment-name and 10-K text exposure discovery",
            "question_it_would_help_answer": "Whether segment names and filings can help validate exposure groups or find examples.",
            "current_data_anchor": "The raw segment file includes segment names; the report series includes keyword coverage screens.",
            "segment_data_inputs": "Segment names, keyword groups, SIC/NAICS fields, and candidate firm lists.",
            "work_completed_so_far": "Keyword screens cover corporate/unallocated, electricity, oil/gas, foreign, metals, transport, and manufacturing-input terms.",
            "unresolved_items": "Segment names include generic labels and require validation before they can define exposure groups.",
            "possible_follow_up_data": "10-K Item 7A text, derivative disclosures, hand-checked examples, and exposure validation notes.",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    generated_at = utc_now()
    family = read_table("segment_project_exposure_family_readiness.csv")
    geodecade = read_table("segment_project_geography_decade_readiness.csv")
    shock_type_summary = read_table("segment_project_candidate_shock_type_summary.csv")
    early_results = read_existing_csv(ROOT / "reports" / "tables" / "t1_strict_identification_results.csv")
    output_input_results = read_existing_csv(ROOT / "reports" / "tables" / "electricity_output_input_rsz_results.csv")

    workstreams = project_workstreams(family, geodecade, early_results, output_input_results, shock_type_summary)
    manifest = existing_result_manifest()
    outputs = [
        write_table(workstreams, "segment_project_workstream_inventory.csv"),
        write_table(manifest, "segment_project_existing_result_manifest.csv"),
    ]
    qa = {
        "generated_at_utc": generated_at,
        "workstream_count": int(len(workstreams)),
        "existing_result_tables_present": int(manifest["status"].eq("present").sum()),
        "existing_result_tables_missing": int(manifest["status"].eq("missing").sum()),
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Workstream rows are descriptive coauthor-update entries.",
            "Rows do not choose a research direction or define treatment/control.",
        ],
    }
    write_json(qa, "segment_project_workstreams_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_workstreams_qa.json")


if __name__ == "__main__":
    main()
