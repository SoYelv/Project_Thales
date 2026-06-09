#!/usr/bin/env python3
"""Build the source-backed candidate shock catalog for the segment reports."""

from __future__ import annotations

from collections import defaultdict

import pandas as pd

from segment_project_common import ROOT, utc_now, write_json, write_table


SOURCE_LIBRARY = {
    "exec_order_12287": {
        "source_title": "Executive Order 12287, Decontrol of Crude Oil and Refined Petroleum Products",
        "source_url": "https://www.presidency.ucsb.edu/documents/executive-order-12287-decontrol-crude-oil-and-refined-petroleum-products",
        "source_type": "government",
        "source_claim": "U.S. crude oil and refined-product price controls were removed in January 1981.",
    },
    "cftc_energy_derivatives": {
        "source_title": "CFTC, Energy Derivatives: The Regulatory Challenge of a Global Marketplace",
        "source_url": "https://www.cftc.gov/sites/default/files/opa/speeches/opadial-69.htm",
        "source_type": "regulator",
        "source_claim": "CFTC describes early energy derivative trading, including first electricity futures trading on March 29, 1996.",
    },
    "cftc_history_1980s": {
        "source_title": "CFTC History of the CFTC: 1980s",
        "source_url": "https://www.cftc.gov/About/HistoryoftheCFTC/history_1980s.html",
        "source_type": "regulator",
        "source_claim": "CFTC history records the 1979-1980 silver episode and subsequent market-rule response.",
    },
    "cftc_metals_testimony": {
        "source_title": "CFTC Testimony on Metal Markets",
        "source_url": "https://www.cftc.gov/PressRoom/SpeechesTestimony/metalmarkets032510_berkovitz",
        "source_type": "regulator",
        "source_claim": "CFTC testimony discusses the Hunt silver crisis and exchange emergency-limit actions.",
    },
    "cme_first_trade_dates": {
        "source_title": "CME Group Historical First Trade Dates",
        "source_url": "https://www.cmegroup.com/media-room/historical-first-trade-dates.html",
        "source_type": "exchange",
        "source_claim": "CME historical list records first trade dates for listed futures and options contracts.",
    },
    "cme_wti_40_years": {
        "source_title": "CME OpenMarkets, How WTI Became the Most Important Commodity Contract on the Planet",
        "source_url": "https://www.cmegroup.com/openmarkets/energy/2023/how-wti-became-the-most-important-commodity-contract-on-the-planet.html",
        "source_type": "exchange",
        "source_claim": "NYMEX launched the Light Sweet Crude Oil futures contract in March 1983.",
    },
    "cme_natural_gas": {
        "source_title": "CME Group, Natural Gas: from Pipelines to Portfolios",
        "source_url": "https://www.cmegroup.com/articles/2023/natural-gas-from-pipelines-to-portfolios.html",
        "source_type": "exchange",
        "source_claim": "NYMEX introduced Henry Hub Natural Gas futures in April 1990.",
    },
    "ferc_order_636": {
        "source_title": "FERC Order No. 636, Restructuring Pipeline Services",
        "source_url": "https://www.ferc.gov/order-no-636-restructuring-pipeline-services",
        "source_type": "regulator",
        "source_claim": "FERC Order 636 required restructuring and unbundling of interstate natural-gas pipeline services.",
    },
    "eia_lng_exports": {
        "source_title": "EIA Today in Energy, U.S. LNG export development",
        "source_url": "https://www.eia.gov/TODAYINENERGY/detail.php?id=67224",
        "source_type": "government",
        "source_claim": "EIA documents the modern U.S. LNG export opening after Lower-48 LNG export terminal development.",
    },
    "cme_weather": {
        "source_title": "CME Group Weather Derivatives",
        "source_url": "https://www.cmegroup.com/articles/2023/cme-group-weather-suite-expanded.html",
        "source_type": "exchange",
        "source_claim": "CME weather derivatives began in 1999 and were later expanded across cities and products.",
    },
    "baltic_timeline": {
        "source_title": "Baltic Exchange Timeline, 1980-1992",
        "source_url": "https://www.balticexchange.com/en/who-we-are/history/baltic-timeline/1980-1992.html",
        "source_type": "exchange",
        "source_claim": "Baltic Exchange history records the freight-index and freight-derivative market foundations in the 1980s.",
    },
    "cme_freight": {
        "source_title": "CME Group Freight Futures and Options",
        "source_url": "https://www.cmegroup.com/markets/energy/freight.html",
        "source_type": "exchange",
        "source_claim": "CME currently lists multiple freight futures and options products.",
    },
    "epa_rfs2": {
        "source_title": "EPA Renewable Fuel Standard RFS2 Final Rule",
        "source_url": "https://www.epa.gov/renewable-fuel-standard/renewable-fuel-standard-rfs2-final-rule",
        "source_type": "regulator",
        "source_claim": "EPA RFS2 established the expanded renewable-fuel compliance framework.",
    },
    "epa_rins": {
        "source_title": "EPA, Renewable Identification Numbers under the RFS Program",
        "source_url": "https://www.epa.gov/renewable-fuel-standard/renewable-identification-numbers-rins-under-renewable-fuel-standard-program",
        "source_type": "regulator",
        "source_claim": "EPA describes RINs as compliance credits under the Renewable Fuel Standard program.",
    },
    "cme_rin_futures": {
        "source_title": "CME Group Announces New Futures Contracts for Renewable Identification Numbers",
        "source_url": "https://investor.cmegroup.com/news-releases/news-release-details/cme-group-announces-new-futures-contracts-renewable",
        "source_type": "exchange",
        "source_claim": "CME announced D4, D5, and D6 RIN futures for May 2013 trading.",
    },
    "ice_cca": {
        "source_title": "ICE Announces First Trade of California Emissions Contract",
        "source_url": "https://www.prnewswire.com/news-releases/ice-announces-first-trade-of-california-emissions-contract-128580553.html",
        "source_type": "exchange",
        "source_claim": "ICE announced the first exchange-cleared California Carbon Allowance forward trade in August 2011.",
    },
    "eia_crude_exports": {
        "source_title": "EIA Petroleum Exports Data",
        "source_url": "https://www.eia.gov/dnav/pet/pet_move_exp_a_epc0_eex_mbbl_a.htm",
        "source_type": "government",
        "source_claim": "EIA tracks U.S. crude oil export quantities before and after the export-policy change.",
    },
    "gao_crude_exports": {
        "source_title": "GAO-21-118, Crude Oil Exports",
        "source_url": "https://www.gao.gov/products/gao-21-118",
        "source_type": "government",
        "source_claim": "GAO reviews effects and implementation issues around the lifting of crude-oil export restrictions.",
    },
    "eia_negative_wti": {
        "source_title": "EIA Today in Energy, WTI Futures Price Fell Below Zero",
        "source_url": "https://www.eia.gov/todayinenergy/detail.php?id=43495",
        "source_type": "government",
        "source_claim": "EIA links the April 2020 negative WTI settlement to storage constraints, demand collapse, and contract-market mechanics.",
    },
    "cftc_negative_wti": {
        "source_title": "CFTC Press Release on Negative WTI Settlement Review",
        "source_url": "https://www.cftc.gov/PressRoom/PressReleases/8315-20",
        "source_type": "regulator",
        "source_claim": "CFTC reviewed the April 20, 2020 negative WTI futures settlement episode.",
    },
    "caiso_ferc_staff": {
        "source_title": "FERC Staff Report on Western Energy Markets",
        "source_url": "https://www.caiso.com/documents/fercstaffreportel00-95-3.pdf",
        "source_type": "regulator",
        "source_claim": "FERC/CAISO staff report discusses western electricity futures hubs including COB, Palo Verde, and Mid-Columbia.",
    },
    "ferc_midwest_report": {
        "source_title": "FERC Midwest Power Market Staff Report",
        "source_url": "https://www.ferc.gov/sites/default/files/2020-05/mastback.pdf",
        "source_type": "regulator",
        "source_claim": "FERC staff report discusses Cinergy and Entergy power futures and the Midwest/South power-market context.",
    },
    "cme_delist_power": {
        "source_title": "CME/NYMEX Delists Physically Settled Electricity Contracts",
        "source_url": "https://www.cmegroup.com/media-room/press-releases/2006/1/17/exchange_to_delistphysicallysettledelectricitycontractsonnymexcl.html",
        "source_type": "exchange",
        "source_claim": "NYMEX announced delisting of several physically settled electricity contracts in 2006.",
    },
    "pjm_history": {
        "source_title": "PJM History",
        "source_url": "https://www.pjm.com/about-pjm/who-we-are/pjm-history.aspx",
        "source_type": "rto_iso",
        "source_claim": "PJM opened its first bid-based energy market on April 1, 1997.",
    },
    "pjm_som_1999": {
        "source_title": "PJM 1999 State of the Market Report",
        "source_url": "https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/1999/state-of-the-market-report-1999.pdf",
        "source_type": "market_monitor",
        "source_claim": "PJM market-monitor report documents early PJM LMP and market-based bidding implementation.",
    },
    "cftc_1999_futures": {
        "source_title": "CFTC 1999 Futures by Exchange",
        "source_url": "https://www.cftc.gov/sites/default/files/files/anr/anr1999_futures_by_exchange.pdf",
        "source_type": "regulator",
        "source_claim": "CFTC annual tables list electricity futures including PJM, Cinergy, Entergy, Palo Verde, and COB.",
    },
    "cme_power_2005": {
        "source_title": "NYMEX to Launch Eleven New Financially Settled Electricity Futures Contracts",
        "source_url": "https://www.cmegroup.com/media-room/press-releases/2005/2/09/exchange_to_launchelevennewfinanciallysettledelectricityfuturesc.html",
        "source_type": "exchange",
        "source_claim": "NYMEX announced financially settled electricity futures across several power markets in 2005.",
    },
    "cme_power_2009": {
        "source_title": "CME Group Announces Launch of New PJM, ISO Electricity Futures",
        "source_url": "https://investor.cmegroup.com/news-releases/news-release-details/cme-group-announces-launch-new-pjm-iso-electricity-futures",
        "source_type": "exchange",
        "source_claim": "CME announced new PJM and ISO electricity futures in 2009.",
    },
    "cme_power_ser4999": {
        "source_title": "CME Market Regulation Advisory SER-4999",
        "source_url": "https://www.cmegroup.com/tools-information/lookups/advisories/market-regulation/SER-4999.html",
        "source_type": "exchange",
        "source_claim": "CME advisory documents additional electricity product listings in September 2009.",
    },
    "nodal_launch": {
        "source_title": "Nodal Exchange and LCH.Clearnet Launch Service for Nodal Power Contracts",
        "source_url": "https://www.nodalexchange.com/lch-clearnet-and-nodal-exchange-launch-service-for-nodal-power-contracts/",
        "source_type": "exchange",
        "source_claim": "Nodal Exchange launched cleared cash-settled nodal power contracts in April 2009.",
    },
    "nodal_dcm": {
        "source_title": "Nodal Exchange Receives CFTC Approval to Register as a Designated Contract Market",
        "source_url": "https://www.nodalexchange.com/nodal-exchange-receives-cftc-approval-to-register-as-a-designated-contract-market/",
        "source_type": "exchange",
        "source_claim": "Nodal Exchange received CFTC approval to register as a designated contract market.",
    },
    "pjm_rpm_auction": {
        "source_title": "PJM Completes First Reliability Pricing Model Auction",
        "source_url": "https://www.pjm.com/-/media/DotCom/Images/ctc-display/modules/timeline/2007-first-annual-pdf.ashx",
        "source_type": "rto_iso",
        "source_claim": "PJM completed its first annual RPM capacity auction in April 2007.",
    },
    "ercot_2010_financials": {
        "source_title": "ERCOT 2010 Financial Statements",
        "source_url": "https://www.ercot.com/files/docs/2011/04/26/ercot_2010_financial_statements.pdf",
        "source_type": "rto_iso",
        "source_claim": "ERCOT documents the 2010 nodal market implementation and market redesign.",
    },
    "ferc_miso": {
        "source_title": "FERC Electric Power Markets: MISO",
        "source_url": "https://www.ferc.gov/industries-data/electric/electric-power-markets/miso",
        "source_type": "regulator",
        "source_claim": "FERC describes MISO market operations and regional footprint.",
    },
    "eia_miso_south": {
        "source_title": "EIA Today in Energy, MISO South Integration",
        "source_url": "https://www.eia.gov/todayinenergy/detail.cfm?id=13511",
        "source_type": "government",
        "source_claim": "EIA describes the December 2013 integration of MISO South utilities and systems.",
    },
    "spp_integrated_marketplace": {
        "source_title": "SPP Marks a Decade of Integrated Marketplace",
        "source_url": "https://www.spp.org/news-list/spp-marks-a-decade-of-integrated-marketplace-and-more-than-102-billion-in-savings/",
        "source_type": "rto_iso",
        "source_claim": "SPP identifies March 1, 2014 as the Integrated Marketplace launch date.",
    },
    "spp_markets": {
        "source_title": "SPP Markets and Operations",
        "source_url": "https://www.spp.org/markets-operations/",
        "source_type": "rto_iso",
        "source_claim": "SPP describes Integrated Marketplace components including day-ahead, real-time, TCR, RUC, reserve, and balancing authority functions.",
    },
    "caiso_eim": {
        "source_title": "California ISO and PacifiCorp Launch First Western Energy Market",
        "source_url": "https://www.caiso.com/documents/californiaiso_pacificorplaunchfirstwesternenergymarket.pdf",
        "source_type": "rto_iso",
        "source_claim": "CAISO and PacifiCorp launched the Western Energy Imbalance Market in November 2014.",
    },
    "ferc_caiso": {
        "source_title": "FERC Electric Power Markets: CAISO",
        "source_url": "https://www.ferc.gov/industries-data/electric/electric-power-markets/caiso",
        "source_type": "regulator",
        "source_claim": "FERC describes CAISO and Western EIM institutional context.",
    },
    "cme_daily_power_2012": {
        "source_title": "CME Market Regulation Advisory SER-6378",
        "source_url": "https://www.cmegroup.com/tools-information/lookups/advisories/market-regulation/SER-6378.html",
        "source_type": "exchange",
        "source_claim": "NYMEX listed daily electricity futures across PJM, NYISO, and ISO-NE hubs/zones in October 2012.",
    },
    "cme_gas_power_2012": {
        "source_title": "CME Group Launches New Natural Gas and Power Markets",
        "source_url": "https://www.cmegroup.com/media-room/press-releases/2012/9/10/cme_group_launchesnewnaturalgasandpowermarkets.html",
        "source_type": "exchange",
        "source_claim": "CME announced a broad suite of new natural gas and power markets in 2012.",
    },
}


CATALOG_ROWS = [
    {
        "shock_id": "petroleum_futures_institutionalization_1981_1986",
        "shock_type": "commodity derivative availability",
        "shock_family": "Petroleum market opening and crude futures",
        "candidate_window": "1981-1986",
        "event_anchor_year": 1983,
        "window_start_year": 1981,
        "window_end_year": 1986,
        "source_ids": "exec_order_12287; cftc_energy_derivatives; cme_wti_40_years; cme_first_trade_dates",
        "source_summary": "Oil/refined-product price decontrol in 1981; NYMEX WTI crude futures in 1983; WTI options by 1986.",
        "exposure_families": "oil_gas_petroleum; airlines_fuel_sensitive; transport_freight; chemicals",
        "segment_mapping_note": "Maps mechanically to oil/gas producers, petroleum refining, petroleum distribution, oilfield services, and fuel-sensitive users.",
        "mapping_requirement": "Separate output-price exposure from fuel/feedstock input exposure before treatment coding.",
        "caveats": "This is an institutional hedgeability window, not a single commodity-price shock.",
    },
    {
        "shock_id": "refined_products_hedgeability_1978_1994",
        "shock_type": "commodity derivative availability",
        "shock_family": "Refined petroleum product futures and spreads",
        "candidate_window": "1978-1994",
        "event_anchor_year": 1984,
        "window_start_year": 1978,
        "window_end_year": 1994,
        "source_ids": "cme_first_trade_dates",
        "source_summary": "Heating oil, gasoline, and later crack-spread products appear inside the segment-data window.",
        "exposure_families": "oil_gas_petroleum; airlines_fuel_sensitive; transport_freight; chemicals",
        "segment_mapping_note": "Relevant for refiners, fuel wholesalers, airlines, transport, and fuel/feedstock users.",
        "mapping_requirement": "Segment SIC/name screens do not by themselves distinguish refined-product producers from fuel users.",
        "caveats": "Multiple product dates should be represented as separate sub-events if used for estimation.",
    },
    {
        "shock_id": "natural_gas_market_liberalization_1990_1993",
        "shock_type": "commodity derivative availability",
        "shock_family": "Natural gas futures and pipeline unbundling",
        "candidate_window": "1990-1993",
        "event_anchor_year": 1990,
        "window_start_year": 1990,
        "window_end_year": 1993,
        "source_ids": "cme_natural_gas; ferc_order_636",
        "source_summary": "Henry Hub natural gas futures launched in 1990; FERC Order 636 restructured interstate pipeline services.",
        "exposure_families": "oil_gas_petroleum; gas_utility; electric_power_output; chemicals; cement_minerals",
        "segment_mapping_note": "Maps to gas producers, gas utilities, pipelines, power producers, and gas-intensive industrial users.",
        "mapping_requirement": "Local basis and pipeline exposure require geography or facility data beyond segment rows.",
        "caveats": "Henry Hub benchmark exposure is not equivalent to local delivered-gas exposure.",
    },
    {
        "shock_id": "early_exchange_futures_west_1996",
        "shock_type": "power derivative availability",
        "shock_family": "Western power futures: COB and Palo Verde",
        "candidate_window": "1996",
        "event_anchor_year": 1996,
        "window_start_year": 1996,
        "window_end_year": 1996,
        "source_ids": "cftc_energy_derivatives; caiso_ferc_staff; cme_delist_power",
        "source_summary": "First two exchange-traded electricity futures began trading for COB and Palo Verde in March 1996.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to western power hubs; segment data need an external hub-to-state or service-territory crosswalk.",
        "mapping_requirement": "Use an explicit western hub footprint before assigning treated firms.",
        "caveats": "Some later regulatory summaries describe western trading history differently; log source conflicts if using exact first-trade timing.",
    },
    {
        "shock_id": "early_exchange_futures_midwest_south_1998",
        "shock_type": "power derivative availability",
        "shock_family": "Eastern Interconnection power futures: Cinergy and Entergy",
        "candidate_window": "1998",
        "event_anchor_year": 1998,
        "window_start_year": 1998,
        "window_end_year": 1998,
        "source_ids": "ferc_midwest_report; cftc_1999_futures",
        "source_summary": "Regulatory/exchange records document Cinergy and Entergy electricity futures in the late-1990s expansion.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to Midwest and South utility or hub exposure, not generic electric SIC alone.",
        "mapping_requirement": "Define each hub footprint separately.",
        "caveats": "Hub definitions and physical-market footprints need external documentation.",
    },
    {
        "shock_id": "pjm_energy_market_design_1997_1999",
        "shock_type": "power market design",
        "shock_family": "PJM bid-based, LMP, and market-based energy-market transition",
        "candidate_window": "1997-1999",
        "event_anchor_year": 1998,
        "window_start_year": 1997,
        "window_end_year": 1999,
        "source_ids": "pjm_history; pjm_som_1999",
        "source_summary": "PJM opened a bid-based market in 1997 and moved through LMP and market-based bidding implementation by 1999.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to PJM-footprint electric-power segments and potentially load-serving entities.",
        "mapping_requirement": "Keep market-design timing separate from derivative-listing timing.",
        "caveats": "Annual segment data may not distinguish the three close implementation milestones.",
    },
    {
        "shock_id": "early_exchange_futures_pjm_1999",
        "shock_type": "power derivative availability",
        "shock_family": "PJM exchange-traded electricity futures",
        "candidate_window": "1999",
        "event_anchor_year": 1999,
        "window_start_year": 1999,
        "window_end_year": 1999,
        "source_ids": "cftc_1999_futures",
        "source_summary": "CFTC tables list PJM electricity futures in the late-1990s exchange-traded power contract set.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "More directly a derivative-availability row than the PJM market-design row.",
        "mapping_requirement": "Link firms to PJM exposure before using this as a treated event.",
        "caveats": "Do not pool with PJM LMP unless the estimand is explicitly broad institutional change.",
    },
    {
        "shock_id": "western_hub_expansion_midc_2000",
        "shock_type": "power derivative availability",
        "shock_family": "Western hub expansion: Mid-Columbia",
        "candidate_window": "2000",
        "event_anchor_year": 2000,
        "window_start_year": 2000,
        "window_end_year": 2000,
        "source_ids": "caiso_ferc_staff",
        "source_summary": "FERC/CAISO staff report identifies Mid-Columbia as an additional western electricity futures hub.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Adds Pacific Northwest hub exposure.",
        "mapping_requirement": "Needs Pacific Northwest hub footprint and utility operating territory mapping.",
        "caveats": "Western crisis timing may confound a narrow derivative-availability interpretation.",
    },
    {
        "shock_id": "miso_energy_market_2005",
        "shock_type": "power market design",
        "shock_family": "MISO day-ahead and real-time energy markets",
        "candidate_window": "2005",
        "event_anchor_year": 2005,
        "window_start_year": 2005,
        "window_end_year": 2005,
        "source_ids": "ferc_miso",
        "source_summary": "FERC describes MISO market operations beginning in April 2005.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to the original MISO footprint rather than later MISO South integration.",
        "mapping_requirement": "Separate original MISO states/members from MISO South entrants.",
        "caveats": "This is market-design access, not direct hedge-use evidence.",
    },
    {
        "shock_id": "cleared_power_swap_expansion_2005_2009",
        "shock_type": "power derivative availability",
        "shock_family": "Financially settled power swap futures expansion",
        "candidate_window": "2005-2009",
        "event_anchor_year": 2009,
        "window_start_year": 2005,
        "window_end_year": 2009,
        "source_ids": "cme_power_2005; cme_power_2009; cme_power_ser4999",
        "source_summary": "NYMEX/CME added financially settled power futures across PJM, NYISO, ISO-NE, MISO, ERCOT, and CAISO-related hubs.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Broad derivative-menu expansion; each contract still maps to a specific hub or ISO/RTO.",
        "mapping_requirement": "Group contracts by hub/ISO before constructing regional treatment.",
        "caveats": "This is more market-access/menu expansion than a local institutional shock.",
    },
    {
        "shock_id": "pjm_capacity_rpm_2007",
        "shock_type": "capacity market design",
        "shock_family": "PJM Reliability Pricing Model capacity market",
        "candidate_window": "2007",
        "event_anchor_year": 2007,
        "window_start_year": 2007,
        "window_end_year": 2007,
        "source_ids": "pjm_rpm_auction",
        "source_summary": "PJM completed its first annual RPM capacity auction in April 2007.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to PJM generators, load-serving entities, and capacity-exposed utilities.",
        "mapping_requirement": "Keep capacity-market exposure separate from energy-price hedgeability.",
        "caveats": "Capacity-market incentives are not the same mechanism as energy futures availability.",
    },
    {
        "shock_id": "cleared_nodal_power_contracts_2009",
        "shock_type": "power derivative availability",
        "shock_family": "Cleared nodal power contracts",
        "candidate_window": "2009",
        "event_anchor_year": 2009,
        "window_start_year": 2009,
        "window_end_year": 2009,
        "source_ids": "nodal_launch; nodal_dcm",
        "source_summary": "Nodal Exchange launched cleared cash-settled nodal power contracts and later registered as a DCM.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to ISO/RTO nodes and hubs, not directly to segment geography.",
        "mapping_requirement": "Requires node/hub-to-firm or service-territory mapping.",
        "caveats": "Better treated as national/exploratory until a node-footprint layer exists.",
    },
    {
        "shock_id": "ercot_nodal_market_2010",
        "shock_type": "power market design",
        "shock_family": "ERCOT nodal market",
        "candidate_window": "2010",
        "event_anchor_year": 2010,
        "window_start_year": 2010,
        "window_end_year": 2010,
        "source_ids": "ercot_2010_financials",
        "source_summary": "ERCOT implemented the nodal wholesale market in December 2010.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Annual Texas-market window if a Texas/utility operating-footprint crosswalk exists.",
        "mapping_requirement": "Identify ERCOT operating exposure; headquarters state alone is a fallback proxy.",
        "caveats": "ERCOT is institutionally distinct from FERC-jurisdictional RTOs.",
    },
    {
        "shock_id": "short_dated_power_contracts_2012",
        "shock_type": "power derivative availability",
        "shock_family": "Short-dated daily power contracts",
        "candidate_window": "2012",
        "event_anchor_year": 2012,
        "window_start_year": 2012,
        "window_end_year": 2012,
        "source_ids": "cme_daily_power_2012; cme_gas_power_2012",
        "source_summary": "NYMEX/CME listed daily electricity futures and a broader suite of natural gas and power markets in 2012.",
        "exposure_families": "electric_power_output; gas_utility",
        "segment_mapping_note": "Contract-design expansion across several hubs and zones.",
        "mapping_requirement": "Use as a national/exploratory derivative-market expansion unless hub-level mapping is added.",
        "caveats": "Not a single regional institutional shock.",
    },
    {
        "shock_id": "miso_south_integration_2013",
        "shock_type": "regional power market expansion",
        "shock_family": "MISO South integration",
        "candidate_window": "2013",
        "event_anchor_year": 2013,
        "window_start_year": 2013,
        "window_end_year": 2013,
        "source_ids": "ferc_miso; eia_miso_south",
        "source_summary": "MISO South systems integrated into MISO in December 2013.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to AR/LA/MS/TX utility footprints and named joining systems.",
        "mapping_requirement": "Use utility/service-area membership, not all firms in broad states.",
        "caveats": "MISO market operations existed since 2005; this is a regional expansion window.",
    },
    {
        "shock_id": "spp_integrated_marketplace_2014",
        "shock_type": "regional power market expansion",
        "shock_family": "SPP Integrated Marketplace",
        "candidate_window": "2014",
        "event_anchor_year": 2014,
        "window_start_year": 2014,
        "window_end_year": 2014,
        "source_ids": "spp_integrated_marketplace; spp_markets",
        "source_summary": "SPP launched the Integrated Marketplace with day-ahead, real-time, TCR, RUC, reserve, and balancing authority functions.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps to SPP footprint states and members.",
        "mapping_requirement": "Construct SPP member/territory exposure before treatment coding.",
        "caveats": "Broad multi-state event.",
    },
    {
        "shock_id": "western_eim_launch_2014",
        "shock_type": "regional power market expansion",
        "shock_family": "CAISO / Western Energy Imbalance Market",
        "candidate_window": "2014",
        "event_anchor_year": 2014,
        "window_start_year": 2014,
        "window_end_year": 2014,
        "source_ids": "caiso_eim; ferc_caiso",
        "source_summary": "CAISO and PacifiCorp launched the financially binding Western EIM in November 2014.",
        "exposure_families": "electric_power_output",
        "segment_mapping_note": "Maps first to PacifiCorp and later staggered EIM balancing-authority footprints.",
        "mapping_requirement": "Represent later EIM entrants as staggered rows if the design uses expansion timing.",
        "caveats": "Real-time imbalance market only; it is not the same as full RTO membership.",
    },
    {
        "shock_id": "weather_derivatives_1999",
        "shock_type": "weather risk derivative availability",
        "shock_family": "Weather derivatives",
        "candidate_window": "1999",
        "event_anchor_year": 1999,
        "window_start_year": 1999,
        "window_end_year": 1999,
        "source_ids": "cme_weather",
        "source_summary": "CME introduced exchange-traded weather derivatives in 1999.",
        "exposure_families": "electric_power_output; agriculture_food",
        "segment_mapping_note": "Possible link to utilities, agriculture/food, seasonal retail, and insurance-like exposures.",
        "mapping_requirement": "Requires local weather exposure or revenue-seasonality evidence.",
        "caveats": "GEOSEG and segment names are likely too coarse to observe weather exposure directly.",
    },
    {
        "shock_id": "freight_derivatives_1985_and_modern_routes",
        "shock_type": "freight derivative availability",
        "shock_family": "Freight and shipping derivatives",
        "candidate_window": "1985 and later route products",
        "event_anchor_year": 1985,
        "window_start_year": 1985,
        "window_end_year": 2009,
        "source_ids": "baltic_timeline; cme_freight",
        "source_summary": "Baltic freight-index derivatives begin in the 1980s; modern exchange listings cover container, tanker, LNG/LPG, and petroleum freight.",
        "exposure_families": "transport_freight; oil_gas_petroleum",
        "segment_mapping_note": "Maps to shipping, logistics, commodity exporters/importers, and energy transport.",
        "mapping_requirement": "Needs route, shipping, or trade-flow exposure to go beyond broad transport SIC.",
        "caveats": "Modern route products are not captured by a single 1985 event year.",
    },
    {
        "shock_id": "metals_contract_availability_1982_1990",
        "shock_type": "commodity derivative availability",
        "shock_family": "Metals futures/options availability",
        "candidate_window": "1982-1990",
        "event_anchor_year": 1988,
        "window_start_year": 1982,
        "window_end_year": 1990,
        "source_ids": "cme_first_trade_dates",
        "source_summary": "Options and contract extensions for gold, silver, copper, and platinum occur inside the segment-data window.",
        "exposure_families": "metals_mining",
        "segment_mapping_note": "Maps to mining, primary metals, and industrial metal users.",
        "mapping_requirement": "Separate commodity producers from downstream metal users if mechanism matters.",
        "caveats": "Some core metals futures predate the segment sample; options/extensions are the cleaner timing variation.",
    },
    {
        "shock_id": "silver_market_rules_1980_1981",
        "shock_type": "market rule episode",
        "shock_family": "Silver market rule shock",
        "candidate_window": "1979-1981",
        "event_anchor_year": 1980,
        "window_start_year": 1979,
        "window_end_year": 1981,
        "source_ids": "cftc_history_1980s; cftc_metals_testimony",
        "source_summary": "CFTC historical material links the Hunt silver episode to subsequent exchange and regulatory market-rule actions.",
        "exposure_families": "metals_mining",
        "segment_mapping_note": "Maps mostly to silver and diversified mining exposure.",
        "mapping_requirement": "Need commodity-specific mining exposure examples.",
        "caveats": "This is a market-integrity/rule-change episode rather than a broad operating hedgeability shock.",
    },
    {
        "shock_id": "ag_options_and_extensions_1984_2011",
        "shock_type": "commodity derivative availability",
        "shock_family": "Agriculture/food options and contract extensions",
        "candidate_window": "1984-2011",
        "event_anchor_year": 1985,
        "window_start_year": 1984,
        "window_end_year": 2011,
        "source_ids": "cme_first_trade_dates",
        "source_summary": "Agricultural options and extensions arrive inside the sample even though core grain futures are much older.",
        "exposure_families": "agriculture_food",
        "segment_mapping_note": "Maps to agriculture, food processors, livestock, dairy, fertilizer, and farm inputs.",
        "mapping_requirement": "Choose sub-events by commodity and producer/user mechanism.",
        "caveats": "A broad 1984-2011 row is only a catalog grouping, not a single event design.",
    },
    {
        "shock_id": "rin_credit_hedgeability_2010_2013",
        "shock_type": "environmental/compliance market",
        "shock_family": "Renewable Identification Number credits",
        "candidate_window": "2010-2013",
        "event_anchor_year": 2013,
        "window_start_year": 2010,
        "window_end_year": 2013,
        "source_ids": "epa_rfs2; epa_rins; cme_rin_futures",
        "source_summary": "EPA RFS2 and tradable RIN compliance credits precede exchange-listed D4/D5/D6 RIN futures in 2013.",
        "exposure_families": "oil_gas_petroleum; agriculture_food",
        "segment_mapping_note": "Maps to refiners, fuel blenders, biofuel producers, and petroleum marketing.",
        "mapping_requirement": "Compliance status and blender/refiner role must be identified outside generic industry screens.",
        "caveats": "Industry SIC does not equal RFS obligated-party status.",
    },
    {
        "shock_id": "california_carbon_2011",
        "shock_type": "environmental/compliance market",
        "shock_family": "California carbon allowances",
        "candidate_window": "2011",
        "event_anchor_year": 2011,
        "window_start_year": 2011,
        "window_end_year": 2011,
        "source_ids": "ice_cca",
        "source_summary": "ICE announced the first exchange-cleared California Carbon Allowance forward trade in 2011.",
        "exposure_families": "electric_power_output; cement_minerals; chemicals; paper_pulp; metals_mining",
        "segment_mapping_note": "Maps to California emitters, fuels, industrial facilities, and utilities-adjacent segments.",
        "mapping_requirement": "Requires California facility/program exposure.",
        "caveats": "Not a national treatment without state/program mapping.",
    },
    {
        "shock_id": "gas_globalization_2016",
        "shock_type": "policy/market access",
        "shock_family": "U.S. LNG export opening",
        "candidate_window": "2016",
        "event_anchor_year": 2016,
        "window_start_year": 2016,
        "window_end_year": 2016,
        "source_ids": "eia_lng_exports",
        "source_summary": "Modern Lower-48 LNG export capacity opened U.S. gas markets more directly to global demand.",
        "exposure_families": "oil_gas_petroleum; gas_utility",
        "segment_mapping_note": "Maps to gas production, LNG terminals, Gulf Coast midstream, and industrial gas demand.",
        "mapping_requirement": "Needs geography/facility linkage for LNG terminal or Gulf Coast exposure.",
        "caveats": "Post-2010 window only; sample composition and shale-era trends need separate controls.",
    },
    {
        "shock_id": "crude_export_reopening_2015_2016",
        "shock_type": "policy/market access",
        "shock_family": "U.S. crude export reopening",
        "candidate_window": "2015-2016",
        "event_anchor_year": 2015,
        "window_start_year": 2015,
        "window_end_year": 2016,
        "source_ids": "eia_crude_exports; gao_crude_exports",
        "source_summary": "U.S. crude export restrictions were lifted in late 2015, with export access expanding afterward.",
        "exposure_families": "oil_gas_petroleum",
        "segment_mapping_note": "Maps to U.S. crude producers, Gulf Coast midstream/export infrastructure, and refiners facing changed crude spreads.",
        "mapping_requirement": "Separate domestic producers from refiners whose input spreads may move differently.",
        "caveats": "Policy exposure depends on production/refining position and geography.",
    },
    {
        "shock_id": "oil_storage_dislocation_2020",
        "shock_type": "event shock",
        "shock_family": "WTI storage/futures dislocation",
        "candidate_window": "2020",
        "event_anchor_year": 2020,
        "window_start_year": 2020,
        "window_end_year": 2020,
        "source_ids": "eia_negative_wti; cftc_negative_wti",
        "source_summary": "WTI May 2020 futures settled below zero amid storage constraints, demand collapse, and contract-market mechanics.",
        "exposure_families": "oil_gas_petroleum; transport_freight",
        "segment_mapping_note": "Maps to crude producers, storage, midstream, refiners, and oilfield services.",
        "mapping_requirement": "Need to account for COVID demand collapse and storage/geography exposure.",
        "caveats": "This is an event/dislocation window, not a contract-availability window.",
    },
]


def build_catalog() -> pd.DataFrame:
    catalog = pd.DataFrame(CATALOG_ROWS)
    catalog["source_urls"] = catalog["source_ids"].apply(
        lambda value: "; ".join(SOURCE_LIBRARY[src.strip()]["source_url"] for src in value.split(";") if src.strip())
    )
    return catalog.sort_values(["shock_type", "event_anchor_year", "shock_id"]).reset_index(drop=True)


def build_sources(catalog: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, shock in catalog.iterrows():
        for source_id in [src.strip() for src in shock["source_ids"].split(";") if src.strip()]:
            source = SOURCE_LIBRARY[source_id]
            rows.append(
                {
                    "shock_id": shock["shock_id"],
                    "source_id": source_id,
                    **source,
                }
            )
    return pd.DataFrame(rows).drop_duplicates().sort_values(["shock_id", "source_id"])


def build_windows(catalog: pd.DataFrame) -> pd.DataFrame:
    windows = []
    for _, row in catalog.iterrows():
        year = int(row["event_anchor_year"])
        for window, start, end in [
            ("pre_10y", year - 10, year - 1),
            ("event_pm5y", year - 5, year + 5),
            ("post_10y", year + 1, year + 10),
        ]:
            windows.append(
                {
                    "shock_id": row["shock_id"],
                    "shock_type": row["shock_type"],
                    "shock_family": row["shock_family"],
                    "event_anchor_year": year,
                    "window": window,
                    "start_year": start,
                    "end_year": end,
                }
            )
    return pd.DataFrame(windows)


def build_type_summary(catalog: pd.DataFrame) -> pd.DataFrame:
    grouped_sources: defaultdict[str, set[str]] = defaultdict(set)
    for _, row in catalog.iterrows():
        for source_id in [src.strip() for src in row["source_ids"].split(";") if src.strip()]:
            grouped_sources[row["shock_type"]].add(SOURCE_LIBRARY[source_id]["source_url"])
    summary = (
        catalog.groupby("shock_type", as_index=False)
        .agg(
            candidate_windows=("shock_id", "size"),
            first_anchor_year=("event_anchor_year", "min"),
            last_anchor_year=("event_anchor_year", "max"),
            shock_families=("shock_family", lambda x: "; ".join(x)),
        )
        .sort_values(["first_anchor_year", "shock_type"])
    )
    summary["source_urls"] = summary["shock_type"].map(lambda key: "; ".join(sorted(grouped_sources[key])))
    return summary


def main() -> None:
    generated_at = utc_now()
    catalog = build_catalog()
    sources = build_sources(catalog)
    windows = build_windows(catalog)
    type_summary = build_type_summary(catalog)

    outputs = [
        write_table(catalog, "segment_project_candidate_shock_catalog.csv"),
        write_table(sources, "segment_project_candidate_shock_sources.csv"),
        write_table(windows, "segment_project_candidate_shock_windows.csv"),
        write_table(type_summary, "segment_project_candidate_shock_type_summary.csv"),
    ]

    qa = {
        "generated_at_utc": generated_at,
        "candidate_shock_count": int(len(catalog)),
        "shock_type_count": int(catalog["shock_type"].nunique()),
        "source_count": int(sources["source_id"].nunique()),
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Candidate shock rows are source-backed catalog entries, not treatment/control rules.",
            "Derivative-listing windows are separated from ISO/RTO market-design windows.",
            "Exposure-family entries are mechanical segment-data screens used by the event-readiness script.",
        ],
    }
    write_json(qa, "segment_project_shock_catalog_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_shock_catalog_qa.json")


if __name__ == "__main__":
    main()
