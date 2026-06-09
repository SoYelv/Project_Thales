# Segment Project Candidate Shock Catalog Detail

Generated at UTC: 2026-06-09T16:19:30+00:00

This is a standalone research note. It is not part of the HTML report bundle under `reports/segment_project_space/`.

The file documents candidate shocks found so far for the segment-data project. It records source-backed event windows, source links, current segment-data exposure screens, mechanical coverage around the event windows, mapping requirements, and caveats. It does not choose a research design and does not define treatment/control status.

## How To Read This Note

- `shock_family` is the reader-facing candidate shock name.
- `shock_type` is only a grouping label, such as derivative availability, power-market design, or policy/market access.
- `candidate_window` is the source-backed window over which the relevant market or institutional change occurs.
- `event_anchor_year` is the single year currently used for mechanical pre/event/post coverage screens.
- `exposure_families` are current BUSSEG/OPSEG screening proxies from the segment data. They are not final treatment definitions.
- The coverage tables are mechanical data-support summaries. They do not imply a causal design.

## Current Catalog Summary

- Candidate shocks recorded: 27
- Shock types recorded: 11
- Source rows recorded: 48
- Anchor-year range: 1980-2020

| shock_type | candidate_windows | first_anchor_year | last_anchor_year | shock_families |
| --- | --- | --- | --- | --- |
| market rule episode | 1 | 1980 | 1980 | Silver market rule shock |
| commodity derivative availability | 5 | 1983 | 1990 | Petroleum market opening and crude futures; Refined petroleum product futures and spreads; Agriculture/food options and contract extensions; Metals futures/options availability; Natural gas futures and pipeline unbundling |
| freight derivative availability | 1 | 1985 | 1985 | Freight and shipping derivatives |
| power derivative availability | 7 | 1996 | 2012 | Western power futures: COB and Palo Verde; Eastern Interconnection power futures: Cinergy and Entergy; PJM exchange-traded electricity futures; Western hub expansion: Mid-Columbia; Cleared nodal power contracts; Financially settled power swap futures expansion; Short-dated daily power contracts |
| power market design | 3 | 1998 | 2010 | PJM bid-based, LMP, and market-based energy-market transition; MISO day-ahead and real-time energy markets; ERCOT nodal market |
| weather risk derivative availability | 1 | 1999 | 1999 | Weather derivatives |
| capacity market design | 1 | 2007 | 2007 | PJM Reliability Pricing Model capacity market |
| environmental/compliance market | 2 | 2011 | 2013 | California carbon allowances; Renewable Identification Number credits |
| regional power market expansion | 3 | 2013 | 2014 | MISO South integration; SPP Integrated Marketplace; CAISO / Western Energy Imbalance Market |
| policy/market access | 2 | 2015 | 2016 | U.S. crude export reopening; U.S. LNG export opening |
| event shock | 1 | 2020 | 2020 | WTI storage/futures dislocation |


## Candidate Shocks

### 1. Silver market rule shock

- `shock_id`: `silver_market_rules_1980_1981`
- `shock_type`: market rule episode
- `candidate_window`: 1979-1981
- `event_anchor_year`: 1980
- `window_start_year` / `window_end_year`: 1979 / 1981
- Current exposure-family screen: `metals_mining`

**Source-backed event description**

CFTC historical material links the Hunt silver episode to subsequent exchange and regulatory market-rule actions.

**Source rows**

- [CFTC History of the CFTC: 1980s](https://www.cftc.gov/About/HistoryoftheCFTC/history_1980s.html) (regulator): CFTC history records the 1979-1980 silver episode and subsequent market-rule response.
- [CFTC Testimony on Metal Markets](https://www.cftc.gov/PressRoom/SpeechesTestimony/metalmarkets032510_berkovitz) (regulator): CFTC testimony discusses the Hunt silver crisis and exchange emergency-limit actions.


**Segment-data mapping note**

Maps mostly to silver and diversified mining exposure.

**Mapping work still separate from this catalog**

Need commodity-specific mining exposure examples.

**Window granularity note**

This row spans 1979-1981 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1980; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

This is a market-integrity/rule-change episode rather than a broad operating hedgeability shock.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1970 | 1979 | 3346 | 807 | 2330 | 93.0 | 77.5 |
| event_pm5y | 1975 | 1985 | 10713 | 1473 | 7874 | 95.4 | 89.3 |
| post_10y | 1981 | 1990 | 11610 | 1711 | 9137 | 93.4 | 94.4 |


### 2. Petroleum market opening and crude futures

- `shock_id`: `petroleum_futures_institutionalization_1981_1986`
- `shock_type`: commodity derivative availability
- `candidate_window`: 1981-1986
- `event_anchor_year`: 1983
- `window_start_year` / `window_end_year`: 1981 / 1986
- Current exposure-family screen: `oil_gas_petroleum`, `airlines_fuel_sensitive`, `transport_freight`, `chemicals`

**Source-backed event description**

Oil/refined-product price decontrol in 1981; NYMEX WTI crude futures in 1983; WTI options by 1986.

**Source rows**

- [CME Group Historical First Trade Dates](https://www.cmegroup.com/media-room/historical-first-trade-dates.html) (exchange): CME historical list records first trade dates for listed futures and options contracts.
- [CME OpenMarkets, How WTI Became the Most Important Commodity Contract on the Planet](https://www.cmegroup.com/openmarkets/energy/2023/how-wti-became-the-most-important-commodity-contract-on-the-planet.html) (exchange): NYMEX launched the Light Sweet Crude Oil futures contract in March 1983.
- [Executive Order 12287, Decontrol of Crude Oil and Refined Petroleum Products](https://www.presidency.ucsb.edu/documents/executive-order-12287-decontrol-crude-oil-and-refined-petroleum-products) (government): U.S. crude oil and refined-product price controls were removed in January 1981.
- [CFTC, Energy Derivatives: The Regulatory Challenge of a Global Marketplace](https://www.cftc.gov/sites/default/files/opa/speeches/opadial-69.htm) (regulator): CFTC describes early energy derivative trading, including first electricity futures trading on March 29, 1996.


**Segment-data mapping note**

Maps mechanically to oil/gas producers, petroleum refining, petroleum distribution, oilfield services, and fuel-sensitive users.

**Mapping work still separate from this catalog**

Separate output-price exposure from fuel/feedstock input exposure before treatment coding.

**Window granularity note**

This row spans 1981-1986 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1983; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

This is an institutional hedgeability window, not a single commodity-price shock.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1973 | 1982 | 11875 | 1887 | 8260 | 96.3 | 85.9 |
| event_pm5y | 1978 | 1988 | 21135 | 2642 | 15561 | 98.0 | 94.2 |
| post_10y | 1984 | 1993 | 18986 | 2715 | 14770 | 96.7 | 94.4 |


### 3. Refined petroleum product futures and spreads

- `shock_id`: `refined_products_hedgeability_1978_1994`
- `shock_type`: commodity derivative availability
- `candidate_window`: 1978-1994
- `event_anchor_year`: 1984
- `window_start_year` / `window_end_year`: 1978 / 1994
- Current exposure-family screen: `oil_gas_petroleum`, `airlines_fuel_sensitive`, `transport_freight`, `chemicals`

**Source-backed event description**

Heating oil, gasoline, and later crack-spread products appear inside the segment-data window.

**Source rows**

- [CME Group Historical First Trade Dates](https://www.cmegroup.com/media-room/historical-first-trade-dates.html) (exchange): CME historical list records first trade dates for listed futures and options contracts.


**Segment-data mapping note**

Relevant for refiners, fuel wholesalers, airlines, transport, and fuel/feedstock users.

**Mapping work still separate from this catalog**

Segment SIC/name screens do not by themselves distinguish refined-product producers from fuel users.

**Window granularity note**

This row spans 1978-1994 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1984; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Multiple product dates should be represented as separate sub-events if used for estimation.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1974 | 1983 | 13955 | 2004 | 9766 | 96.6 | 87.2 |
| event_pm5y | 1979 | 1989 | 21228 | 2693 | 15771 | 97.9 | 94.3 |
| post_10y | 1985 | 1994 | 18934 | 2659 | 14829 | 96.4 | 94.3 |


### 4. Agriculture/food options and contract extensions

- `shock_id`: `ag_options_and_extensions_1984_2011`
- `shock_type`: commodity derivative availability
- `candidate_window`: 1984-2011
- `event_anchor_year`: 1985
- `window_start_year` / `window_end_year`: 1984 / 2011
- Current exposure-family screen: `agriculture_food`

**Source-backed event description**

Agricultural options and extensions arrive inside the sample even though core grain futures are much older.

**Source rows**

- [CME Group Historical First Trade Dates](https://www.cmegroup.com/media-room/historical-first-trade-dates.html) (exchange): CME historical list records first trade dates for listed futures and options contracts.


**Segment-data mapping note**

Maps to agriculture, food processors, livestock, dairy, fertilizer, and farm inputs.

**Mapping work still separate from this catalog**

Choose sub-events by commodity and producer/user mechanism.

**Window granularity note**

This row spans 1984-2011 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1985; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

A broad 1984-2011 row is only a catalog grouping, not a single event design.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1975 | 1984 | 3521 | 450 | 2486 | 94.9 | 80.6 |
| event_pm5y | 1980 | 1990 | 3787 | 543 | 2958 | 98.5 | 93.0 |
| post_10y | 1986 | 1995 | 3196 | 514 | 2651 | 97.7 | 93.5 |


### 5. Freight and shipping derivatives

- `shock_id`: `freight_derivatives_1985_and_modern_routes`
- `shock_type`: freight derivative availability
- `candidate_window`: 1985 and later route products
- `event_anchor_year`: 1985
- `window_start_year` / `window_end_year`: 1985 / 2009
- Current exposure-family screen: `transport_freight`, `oil_gas_petroleum`

**Source-backed event description**

Baltic freight-index derivatives begin in the 1980s; modern exchange listings cover container, tanker, LNG/LPG, and petroleum freight.

**Source rows**

- [Baltic Exchange Timeline, 1980-1992](https://www.balticexchange.com/en/who-we-are/history/baltic-timeline/1980-1992.html) (exchange): Baltic Exchange history records the freight-index and freight-derivative market foundations in the 1980s.
- [CME Group Freight Futures and Options](https://www.cmegroup.com/markets/energy/freight.html) (exchange): CME currently lists multiple freight futures and options products.


**Segment-data mapping note**

Maps to shipping, logistics, commodity exporters/importers, and energy transport.

**Mapping work still separate from this catalog**

Needs route, shipping, or trade-flow exposure to go beyond broad transport SIC.

**Window granularity note**

This row spans 1985-2009 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1985; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Modern route products are not captured by a single 1985 event year.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1975 | 1984 | 11416 | 1626 | 8582 | 97.0 | 89.5 |
| event_pm5y | 1980 | 1990 | 15061 | 1955 | 11740 | 98.0 | 94.5 |
| post_10y | 1986 | 1995 | 12081 | 1711 | 9660 | 97.4 | 94.1 |


### 6. Metals futures/options availability

- `shock_id`: `metals_contract_availability_1982_1990`
- `shock_type`: commodity derivative availability
- `candidate_window`: 1982-1990
- `event_anchor_year`: 1988
- `window_start_year` / `window_end_year`: 1982 / 1990
- Current exposure-family screen: `metals_mining`

**Source-backed event description**

Options and contract extensions for gold, silver, copper, and platinum occur inside the segment-data window.

**Source rows**

- [CME Group Historical First Trade Dates](https://www.cmegroup.com/media-room/historical-first-trade-dates.html) (exchange): CME historical list records first trade dates for listed futures and options contracts.


**Segment-data mapping note**

Maps to mining, primary metals, and industrial metal users.

**Mapping work still separate from this catalog**

Separate commodity producers from downstream metal users if mechanism matters.

**Window granularity note**

This row spans 1982-1990 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1988; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Some core metals futures predate the segment sample; options/extensions are the cleaner timing variation.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1978 | 1987 | 11597 | 1651 | 8812 | 95.3 | 94.2 |
| event_pm5y | 1983 | 1993 | 11977 | 1721 | 9658 | 91.8 | 94.0 |
| post_10y | 1989 | 1998 | 9932 | 1339 | 7966 | 89.6 | 91.5 |


### 7. Natural gas futures and pipeline unbundling

- `shock_id`: `natural_gas_market_liberalization_1990_1993`
- `shock_type`: commodity derivative availability
- `candidate_window`: 1990-1993
- `event_anchor_year`: 1990
- `window_start_year` / `window_end_year`: 1990 / 1993
- Current exposure-family screen: `oil_gas_petroleum`, `gas_utility`, `electric_power_output`, `chemicals`, `cement_minerals`

**Source-backed event description**

Henry Hub natural gas futures launched in 1990; FERC Order 636 restructured interstate pipeline services.

**Source rows**

- [CME Group, Natural Gas: from Pipelines to Portfolios](https://www.cmegroup.com/articles/2023/natural-gas-from-pipelines-to-portfolios.html) (exchange): NYMEX introduced Henry Hub Natural Gas futures in April 1990.
- [FERC Order No. 636, Restructuring Pipeline Services](https://www.ferc.gov/order-no-636-restructuring-pipeline-services) (regulator): FERC Order 636 required restructuring and unbundling of interstate natural-gas pipeline services.


**Segment-data mapping note**

Maps to gas producers, gas utilities, pipelines, power producers, and gas-intensive industrial users.

**Mapping work still separate from this catalog**

Local basis and pipeline exposure require geography or facility data beyond segment rows.

**Window granularity note**

This row spans 1990-1993 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1990; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Henry Hub benchmark exposure is not equivalent to local delivered-gas exposure.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1980 | 1989 | 21189 | 2684 | 15373 | 97.4 | 95.1 |
| event_pm5y | 1985 | 1995 | 22844 | 2928 | 17286 | 95.8 | 94.7 |
| post_10y | 1991 | 2000 | 25166 | 2911 | 16941 | 86.4 | 83.3 |


### 8. Western power futures: COB and Palo Verde

- `shock_id`: `early_exchange_futures_west_1996`
- `shock_type`: power derivative availability
- `candidate_window`: 1996
- `event_anchor_year`: 1996
- `window_start_year` / `window_end_year`: 1996 / 1996
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

First two exchange-traded electricity futures began trading for COB and Palo Verde in March 1996.

**Source rows**

- [CME/NYMEX Delists Physically Settled Electricity Contracts](https://www.cmegroup.com/media-room/press-releases/2006/1/17/exchange_to_delistphysicallysettledelectricitycontractsonnymexcl.html) (exchange): NYMEX announced delisting of several physically settled electricity contracts in 2006.
- [CFTC, Energy Derivatives: The Regulatory Challenge of a Global Marketplace](https://www.cftc.gov/sites/default/files/opa/speeches/opadial-69.htm) (regulator): CFTC describes early energy derivative trading, including first electricity futures trading on March 29, 1996.
- [FERC Staff Report on Western Energy Markets](https://www.caiso.com/documents/fercstaffreportel00-95-3.pdf) (regulator): FERC/CAISO staff report discusses western electricity futures hubs including COB, Palo Verde, and Mid-Columbia.


**Segment-data mapping note**

Maps to western power hubs; segment data need an external hub-to-state or service-territory crosswalk.

**Mapping work still separate from this catalog**

Use an explicit western hub footprint before assigning treated firms.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 1996 as the anchor year.

**Current caveat**

Some later regulatory summaries describe western trading history differently; log source conflicts if using exact first-trade timing.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1986 | 1995 | 4590 | 555 | 3657 | 98.6 | 96.1 |
| event_pm5y | 1991 | 2001 | 6732 | 758 | 4169 | 82.6 | 77.6 |
| post_10y | 1997 | 2006 | 8958 | 760 | 4357 | 66.4 | 60.3 |


### 9. Eastern Interconnection power futures: Cinergy and Entergy

- `shock_id`: `early_exchange_futures_midwest_south_1998`
- `shock_type`: power derivative availability
- `candidate_window`: 1998
- `event_anchor_year`: 1998
- `window_start_year` / `window_end_year`: 1998 / 1998
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

Regulatory/exchange records document Cinergy and Entergy electricity futures in the late-1990s expansion.

**Source rows**

- [CFTC 1999 Futures by Exchange](https://www.cftc.gov/sites/default/files/files/anr/anr1999_futures_by_exchange.pdf) (regulator): CFTC annual tables list electricity futures including PJM, Cinergy, Entergy, Palo Verde, and COB.
- [FERC Midwest Power Market Staff Report](https://www.ferc.gov/sites/default/files/2020-05/mastback.pdf) (regulator): FERC staff report discusses Cinergy and Entergy power futures and the Midwest/South power-market context.


**Segment-data mapping note**

Maps to Midwest and South utility or hub exposure, not generic electric SIC alone.

**Mapping work still separate from this catalog**

Define each hub footprint separately.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 1998 as the anchor year.

**Current caveat**

Hub definitions and physical-market footprints need external documentation.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1988 | 1997 | 4616 | 539 | 3613 | 98.6 | 95.5 |
| event_pm5y | 1993 | 2003 | 7822 | 786 | 4407 | 75.6 | 70.3 |
| post_10y | 1999 | 2008 | 9678 | 719 | 4527 | 62.6 | 56.8 |


### 10. PJM bid-based, LMP, and market-based energy-market transition

- `shock_id`: `pjm_energy_market_design_1997_1999`
- `shock_type`: power market design
- `candidate_window`: 1997-1999
- `event_anchor_year`: 1998
- `window_start_year` / `window_end_year`: 1997 / 1999
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

PJM opened a bid-based market in 1997 and moved through LMP and market-based bidding implementation by 1999.

**Source rows**

- [PJM 1999 State of the Market Report](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/1999/state-of-the-market-report-1999.pdf) (market_monitor): PJM market-monitor report documents early PJM LMP and market-based bidding implementation.
- [PJM History](https://www.pjm.com/about-pjm/who-we-are/pjm-history.aspx) (rto_iso): PJM opened its first bid-based energy market on April 1, 1997.


**Segment-data mapping note**

Maps to PJM-footprint electric-power segments and potentially load-serving entities.

**Mapping work still separate from this catalog**

Keep market-design timing separate from derivative-listing timing.

**Window granularity note**

This row spans 1997-1999 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 1998; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Annual segment data may not distinguish the three close implementation milestones.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1988 | 1997 | 4616 | 539 | 3613 | 98.6 | 95.5 |
| event_pm5y | 1993 | 2003 | 7822 | 786 | 4407 | 75.6 | 70.3 |
| post_10y | 1999 | 2008 | 9678 | 719 | 4527 | 62.6 | 56.8 |


### 11. PJM exchange-traded electricity futures

- `shock_id`: `early_exchange_futures_pjm_1999`
- `shock_type`: power derivative availability
- `candidate_window`: 1999
- `event_anchor_year`: 1999
- `window_start_year` / `window_end_year`: 1999 / 1999
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

CFTC tables list PJM electricity futures in the late-1990s exchange-traded power contract set.

**Source rows**

- [CFTC 1999 Futures by Exchange](https://www.cftc.gov/sites/default/files/files/anr/anr1999_futures_by_exchange.pdf) (regulator): CFTC annual tables list electricity futures including PJM, Cinergy, Entergy, Palo Verde, and COB.


**Segment-data mapping note**

More directly a derivative-availability row than the PJM market-design row.

**Mapping work still separate from this catalog**

Link firms to PJM exposure before using this as a treated event.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 1999 as the anchor year.

**Current caveat**

Do not pool with PJM LMP unless the estimand is explicitly broad institutional change.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1989 | 1998 | 4841 | 582 | 3626 | 97.0 | 92.8 |
| event_pm5y | 1994 | 2004 | 8383 | 785 | 4519 | 72.5 | 66.9 |
| post_10y | 2000 | 2009 | 9768 | 694 | 4584 | 62.3 | 56.4 |


### 12. Weather derivatives

- `shock_id`: `weather_derivatives_1999`
- `shock_type`: weather risk derivative availability
- `candidate_window`: 1999
- `event_anchor_year`: 1999
- `window_start_year` / `window_end_year`: 1999 / 1999
- Current exposure-family screen: `electric_power_output`, `agriculture_food`

**Source-backed event description**

CME introduced exchange-traded weather derivatives in 1999.

**Source rows**

- [CME Group Weather Derivatives](https://www.cmegroup.com/articles/2023/cme-group-weather-suite-expanded.html) (exchange): CME weather derivatives began in 1999 and were later expanded across cities and products.


**Segment-data mapping note**

Possible link to utilities, agriculture/food, seasonal retail, and insurance-like exposures.

**Mapping work still separate from this catalog**

Requires local weather exposure or revenue-seasonality evidence.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 1999 as the anchor year.

**Current caveat**

GEOSEG and segment names are likely too coarse to observe weather exposure directly.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1989 | 1998 | 8259 | 1068 | 6321 | 96.8 | 91.9 |
| event_pm5y | 1994 | 2004 | 13539 | 1269 | 7529 | 76.0 | 69.8 |
| post_10y | 2000 | 2009 | 14917 | 1087 | 6887 | 64.7 | 58.7 |


### 13. Western hub expansion: Mid-Columbia

- `shock_id`: `western_hub_expansion_midc_2000`
- `shock_type`: power derivative availability
- `candidate_window`: 2000
- `event_anchor_year`: 2000
- `window_start_year` / `window_end_year`: 2000 / 2000
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

FERC/CAISO staff report identifies Mid-Columbia as an additional western electricity futures hub.

**Source rows**

- [FERC Staff Report on Western Energy Markets](https://www.caiso.com/documents/fercstaffreportel00-95-3.pdf) (regulator): FERC/CAISO staff report discusses western electricity futures hubs including COB, Palo Verde, and Mid-Columbia.


**Segment-data mapping note**

Adds Pacific Northwest hub exposure.

**Mapping work still separate from this catalog**

Needs Pacific Northwest hub footprint and utility operating territory mapping.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2000 as the anchor year.

**Current caveat**

Western crisis timing may confound a narrow derivative-availability interpretation.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1990 | 1999 | 5283 | 626 | 3669 | 91.3 | 86.8 |
| event_pm5y | 1995 | 2005 | 8922 | 786 | 4624 | 70.2 | 64.3 |
| post_10y | 2001 | 2010 | 9851 | 684 | 4649 | 62.3 | 56.7 |


### 14. MISO day-ahead and real-time energy markets

- `shock_id`: `miso_energy_market_2005`
- `shock_type`: power market design
- `candidate_window`: 2005
- `event_anchor_year`: 2005
- `window_start_year` / `window_end_year`: 2005 / 2005
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

FERC describes MISO market operations beginning in April 2005.

**Source rows**

- [FERC Electric Power Markets: MISO](https://www.ferc.gov/industries-data/electric/electric-power-markets/miso) (regulator): FERC describes MISO market operations and regional footprint.


**Segment-data mapping note**

Maps to the original MISO footprint rather than later MISO South integration.

**Mapping work still separate from this catalog**

Separate original MISO states/members from MISO South entrants.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2005 as the anchor year.

**Current caveat**

This is market-design access, not direct hedge-use evidence.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1995 | 2004 | 7915 | 764 | 4153 | 70.9 | 65.1 |
| event_pm5y | 2000 | 2010 | 10752 | 720 | 5040 | 62.2 | 56.5 |
| post_10y | 2006 | 2015 | 9552 | 659 | 4478 | 64.4 | 58.3 |


### 15. PJM Reliability Pricing Model capacity market

- `shock_id`: `pjm_capacity_rpm_2007`
- `shock_type`: capacity market design
- `candidate_window`: 2007
- `event_anchor_year`: 2007
- `window_start_year` / `window_end_year`: 2007 / 2007
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

PJM completed its first annual RPM capacity auction in April 2007.

**Source rows**

- [PJM Completes First Reliability Pricing Model Auction](https://www.pjm.com/-/media/DotCom/Images/ctc-display/modules/timeline/2007-first-annual-pdf.ashx) (rto_iso): PJM completed its first annual RPM capacity auction in April 2007.


**Segment-data mapping note**

Maps to PJM generators, load-serving entities, and capacity-exposed utilities.

**Mapping work still separate from this catalog**

Keep capacity-market exposure separate from energy-price hedgeability.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2007 as the anchor year.

**Current caveat**

Capacity-market incentives are not the same mechanism as energy futures availability.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1997 | 2006 | 8958 | 760 | 4357 | 66.4 | 60.3 |
| event_pm5y | 2002 | 2012 | 10751 | 701 | 5068 | 62.6 | 56.9 |
| post_10y | 2008 | 2017 | 9350 | 635 | 4357 | 65.0 | 58.4 |


### 16. Cleared nodal power contracts

- `shock_id`: `cleared_nodal_power_contracts_2009`
- `shock_type`: power derivative availability
- `candidate_window`: 2009
- `event_anchor_year`: 2009
- `window_start_year` / `window_end_year`: 2009 / 2009
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

Nodal Exchange launched cleared cash-settled nodal power contracts and later registered as a DCM.

**Source rows**

- [Nodal Exchange Receives CFTC Approval to Register as a Designated Contract Market](https://www.nodalexchange.com/nodal-exchange-receives-cftc-approval-to-register-as-a-designated-contract-market/) (exchange): Nodal Exchange received CFTC approval to register as a designated contract market.
- [Nodal Exchange and LCH.Clearnet Launch Service for Nodal Power Contracts](https://www.nodalexchange.com/lch-clearnet-and-nodal-exchange-launch-service-for-nodal-power-contracts/) (exchange): Nodal Exchange launched cleared cash-settled nodal power contracts in April 2009.


**Segment-data mapping note**

Maps to ISO/RTO nodes and hubs, not directly to segment geography.

**Mapping work still separate from this catalog**

Requires node/hub-to-firm or service-territory mapping.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2009 as the anchor year.

**Current caveat**

Better treated as national/exploratory until a node-footprint layer exists.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1999 | 2008 | 9678 | 719 | 4527 | 62.6 | 56.8 |
| event_pm5y | 2004 | 2014 | 10656 | 699 | 5002 | 63.6 | 57.6 |
| post_10y | 2010 | 2019 | 8949 | 602 | 4146 | 66.7 | 59.0 |


### 17. Financially settled power swap futures expansion

- `shock_id`: `cleared_power_swap_expansion_2005_2009`
- `shock_type`: power derivative availability
- `candidate_window`: 2005-2009
- `event_anchor_year`: 2009
- `window_start_year` / `window_end_year`: 2005 / 2009
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

NYMEX/CME added financially settled power futures across PJM, NYISO, ISO-NE, MISO, ERCOT, and CAISO-related hubs.

**Source rows**

- [CME Group Announces Launch of New PJM, ISO Electricity Futures](https://investor.cmegroup.com/news-releases/news-release-details/cme-group-announces-launch-new-pjm-iso-electricity-futures) (exchange): CME announced new PJM and ISO electricity futures in 2009.
- [CME Market Regulation Advisory SER-4999](https://www.cmegroup.com/tools-information/lookups/advisories/market-regulation/SER-4999.html) (exchange): CME advisory documents additional electricity product listings in September 2009.
- [NYMEX to Launch Eleven New Financially Settled Electricity Futures Contracts](https://www.cmegroup.com/media-room/press-releases/2005/2/09/exchange_to_launchelevennewfinanciallysettledelectricityfuturesc.html) (exchange): NYMEX announced financially settled electricity futures across several power markets in 2005.


**Segment-data mapping note**

Broad derivative-menu expansion; each contract still maps to a specific hub or ISO/RTO.

**Mapping work still separate from this catalog**

Group contracts by hub/ISO before constructing regional treatment.

**Window granularity note**

This row spans 2005-2009 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 2009; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

This is more market-access/menu expansion than a local institutional shock.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 1999 | 2008 | 9678 | 719 | 4527 | 62.6 | 56.8 |
| event_pm5y | 2004 | 2014 | 10656 | 699 | 5002 | 63.6 | 57.6 |
| post_10y | 2010 | 2019 | 8949 | 602 | 4146 | 66.7 | 59.0 |


### 18. ERCOT nodal market

- `shock_id`: `ercot_nodal_market_2010`
- `shock_type`: power market design
- `candidate_window`: 2010
- `event_anchor_year`: 2010
- `window_start_year` / `window_end_year`: 2010 / 2010
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

ERCOT implemented the nodal wholesale market in December 2010.

**Source rows**

- [ERCOT 2010 Financial Statements](https://www.ercot.com/files/docs/2011/04/26/ercot_2010_financial_statements.pdf) (rto_iso): ERCOT documents the 2010 nodal market implementation and market redesign.


**Segment-data mapping note**

Annual Texas-market window if a Texas/utility operating-footprint crosswalk exists.

**Mapping work still separate from this catalog**

Identify ERCOT operating exposure; headquarters state alone is a fallback proxy.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2010 as the anchor year.

**Current caveat**

ERCOT is institutionally distinct from FERC-jurisdictional RTOs.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2000 | 2009 | 9768 | 694 | 4584 | 62.3 | 56.4 |
| event_pm5y | 2005 | 2015 | 10559 | 689 | 4949 | 64.4 | 58.3 |
| post_10y | 2011 | 2020 | 8695 | 599 | 4044 | 67.2 | 58.7 |


### 19. California carbon allowances

- `shock_id`: `california_carbon_2011`
- `shock_type`: environmental/compliance market
- `candidate_window`: 2011
- `event_anchor_year`: 2011
- `window_start_year` / `window_end_year`: 2011 / 2011
- Current exposure-family screen: `electric_power_output`, `cement_minerals`, `chemicals`, `paper_pulp`, `metals_mining`

**Source-backed event description**

ICE announced the first exchange-cleared California Carbon Allowance forward trade in 2011.

**Source rows**

- [ICE Announces First Trade of California Emissions Contract](https://www.prnewswire.com/news-releases/ice-announces-first-trade-of-california-emissions-contract-128580553.html) (exchange): ICE announced the first exchange-cleared California Carbon Allowance forward trade in August 2011.


**Segment-data mapping note**

Maps to California emitters, fuels, industrial facilities, and utilities-adjacent segments.

**Mapping work still separate from this catalog**

Requires California facility/program exposure.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2011 as the anchor year.

**Current caveat**

Not a national treatment without state/program mapping.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2001 | 2010 | 42140 | 3260 | 20305 | 62.8 | 64.2 |
| event_pm5y | 2006 | 2016 | 45995 | 3653 | 22812 | 62.5 | 64.5 |
| post_10y | 2012 | 2021 | 40340 | 3472 | 21087 | 62.7 | 64.5 |


### 20. Short-dated daily power contracts

- `shock_id`: `short_dated_power_contracts_2012`
- `shock_type`: power derivative availability
- `candidate_window`: 2012
- `event_anchor_year`: 2012
- `window_start_year` / `window_end_year`: 2012 / 2012
- Current exposure-family screen: `electric_power_output`, `gas_utility`

**Source-backed event description**

NYMEX/CME listed daily electricity futures and a broader suite of natural gas and power markets in 2012.

**Source rows**

- [CME Group Launches New Natural Gas and Power Markets](https://www.cmegroup.com/media-room/press-releases/2012/9/10/cme_group_launchesnewnaturalgasandpowermarkets.html) (exchange): CME announced a broad suite of new natural gas and power markets in 2012.
- [CME Market Regulation Advisory SER-6378](https://www.cmegroup.com/tools-information/lookups/advisories/market-regulation/SER-6378.html) (exchange): NYMEX listed daily electricity futures across PJM, NYISO, and ISO-NE hubs/zones in October 2012.


**Segment-data mapping note**

Contract-design expansion across several hubs and zones.

**Mapping work still separate from this catalog**

Use as a national/exploratory derivative-market expansion unless hub-level mapping is added.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2012 as the anchor year.

**Current caveat**

Not a single regional institutional shock.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2002 | 2011 | 10245 | 756 | 4964 | 63.0 | 57.4 |
| event_pm5y | 2007 | 2017 | 10939 | 766 | 5399 | 66.2 | 60.1 |
| post_10y | 2013 | 2022 | 8814 | 695 | 4424 | 68.7 | 59.8 |


### 21. Renewable Identification Number credits

- `shock_id`: `rin_credit_hedgeability_2010_2013`
- `shock_type`: environmental/compliance market
- `candidate_window`: 2010-2013
- `event_anchor_year`: 2013
- `window_start_year` / `window_end_year`: 2010 / 2013
- Current exposure-family screen: `oil_gas_petroleum`, `agriculture_food`

**Source-backed event description**

EPA RFS2 and tradable RIN compliance credits precede exchange-listed D4/D5/D6 RIN futures in 2013.

**Source rows**

- [CME Group Announces New Futures Contracts for Renewable Identification Numbers](https://investor.cmegroup.com/news-releases/news-release-details/cme-group-announces-new-futures-contracts-renewable) (exchange): CME announced D4, D5, and D6 RIN futures for May 2013 trading.
- [EPA Renewable Fuel Standard RFS2 Final Rule](https://www.epa.gov/renewable-fuel-standard/renewable-fuel-standard-rfs2-final-rule) (regulator): EPA RFS2 established the expanded renewable-fuel compliance framework.
- [EPA, Renewable Identification Numbers under the RFS Program](https://www.epa.gov/renewable-fuel-standard/renewable-identification-numbers-rins-under-renewable-fuel-standard-program) (regulator): EPA describes RINs as compliance credits under the Renewable Fuel Standard program.


**Segment-data mapping note**

Maps to refiners, fuel blenders, biofuel producers, and petroleum marketing.

**Mapping work still separate from this catalog**

Compliance status and blender/refiner role must be identified outside generic industry screens.

**Window granularity note**

This row spans 2010-2013 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 2013; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Industry SIC does not equal RFS obligated-party status.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2003 | 2012 | 15878 | 1369 | 8185 | 66.1 | 62.5 |
| event_pm5y | 2008 | 2018 | 17170 | 1291 | 8779 | 65.9 | 59.6 |
| post_10y | 2014 | 2023 | 12721 | 1081 | 6574 | 69.1 | 57.3 |


### 22. MISO South integration

- `shock_id`: `miso_south_integration_2013`
- `shock_type`: regional power market expansion
- `candidate_window`: 2013
- `event_anchor_year`: 2013
- `window_start_year` / `window_end_year`: 2013 / 2013
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

MISO South systems integrated into MISO in December 2013.

**Source rows**

- [EIA Today in Energy, MISO South Integration](https://www.eia.gov/todayinenergy/detail.cfm?id=13511) (government): EIA describes the December 2013 integration of MISO South utilities and systems.
- [FERC Electric Power Markets: MISO](https://www.ferc.gov/industries-data/electric/electric-power-markets/miso) (regulator): FERC describes MISO market operations and regional footprint.


**Segment-data mapping note**

Maps to AR/LA/MS/TX utility footprints and named joining systems.

**Mapping work still separate from this catalog**

Use utility/service-area membership, not all firms in broad states.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2013 as the anchor year.

**Current caveat**

MISO market operations existed since 2005; this is a regional expansion window.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2003 | 2012 | 9763 | 681 | 4596 | 62.7 | 56.9 |
| event_pm5y | 2008 | 2018 | 10141 | 640 | 4718 | 65.5 | 58.4 |
| post_10y | 2014 | 2023 | 7990 | 571 | 3792 | 67.0 | 56.3 |


### 23. CAISO / Western Energy Imbalance Market

- `shock_id`: `western_eim_launch_2014`
- `shock_type`: regional power market expansion
- `candidate_window`: 2014
- `event_anchor_year`: 2014
- `window_start_year` / `window_end_year`: 2014 / 2014
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

CAISO and PacifiCorp launched the financially binding Western EIM in November 2014.

**Source rows**

- [FERC Electric Power Markets: CAISO](https://www.ferc.gov/industries-data/electric/electric-power-markets/caiso) (regulator): FERC describes CAISO and Western EIM institutional context.
- [California ISO and PacifiCorp Launch First Western Energy Market](https://www.caiso.com/documents/californiaiso_pacificorplaunchfirstwesternenergymarket.pdf) (rto_iso): CAISO and PacifiCorp launched the Western Energy Imbalance Market in November 2014.


**Segment-data mapping note**

Maps first to PacifiCorp and later staggered EIM balancing-authority footprints.

**Mapping work still separate from this catalog**

Represent later EIM entrants as staggered rows if the design uses expansion timing.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2014 as the anchor year.

**Current caveat**

Real-time imbalance market only; it is not the same as full RTO membership.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2004 | 2013 | 9689 | 687 | 4568 | 63.1 | 57.3 |
| event_pm5y | 2009 | 2019 | 9932 | 633 | 4606 | 66.1 | 58.6 |
| post_10y | 2015 | 2024 | 7678 | 551 | 3709 | 66.5 | 55.2 |


### 24. SPP Integrated Marketplace

- `shock_id`: `spp_integrated_marketplace_2014`
- `shock_type`: regional power market expansion
- `candidate_window`: 2014
- `event_anchor_year`: 2014
- `window_start_year` / `window_end_year`: 2014 / 2014
- Current exposure-family screen: `electric_power_output`

**Source-backed event description**

SPP launched the Integrated Marketplace with day-ahead, real-time, TCR, RUC, reserve, and balancing authority functions.

**Source rows**

- [SPP Markets and Operations](https://www.spp.org/markets-operations/) (rto_iso): SPP describes Integrated Marketplace components including day-ahead, real-time, TCR, RUC, reserve, and balancing authority functions.
- [SPP Marks a Decade of Integrated Marketplace](https://www.spp.org/news-list/spp-marks-a-decade-of-integrated-marketplace-and-more-than-102-billion-in-savings/) (rto_iso): SPP identifies March 1, 2014 as the Integrated Marketplace launch date.


**Segment-data mapping note**

Maps to SPP footprint states and members.

**Mapping work still separate from this catalog**

Construct SPP member/territory exposure before treatment coding.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2014 as the anchor year.

**Current caveat**

Broad multi-state event.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2004 | 2013 | 9689 | 687 | 4568 | 63.1 | 57.3 |
| event_pm5y | 2009 | 2019 | 9932 | 633 | 4606 | 66.1 | 58.6 |
| post_10y | 2015 | 2024 | 7678 | 551 | 3709 | 66.5 | 55.2 |


### 25. U.S. crude export reopening

- `shock_id`: `crude_export_reopening_2015_2016`
- `shock_type`: policy/market access
- `candidate_window`: 2015-2016
- `event_anchor_year`: 2015
- `window_start_year` / `window_end_year`: 2015 / 2016
- Current exposure-family screen: `oil_gas_petroleum`

**Source-backed event description**

U.S. crude export restrictions were lifted in late 2015, with export access expanding afterward.

**Source rows**

- [EIA Petroleum Exports Data](https://www.eia.gov/dnav/pet/pet_move_exp_a_epc0_eex_mbbl_a.htm) (government): EIA tracks U.S. crude oil export quantities before and after the export-policy change.
- [GAO-21-118, Crude Oil Exports](https://www.gao.gov/products/gao-21-118) (government): GAO reviews effects and implementation issues around the lifting of crude-oil export restrictions.


**Segment-data mapping note**

Maps to U.S. crude producers, Gulf Coast midstream/export infrastructure, and refiners facing changed crude spreads.

**Mapping work still separate from this catalog**

Separate domestic producers from refiners whose input spreads may move differently.

**Window granularity note**

This row spans 2015-2016 because the source-backed institutional change has multiple components. The current coverage screen places the row at anchor year 2015; separate sub-events can be documented later if the research design needs one treatment year per event.

**Current caveat**

Policy exposure depends on production/refining position and geography.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2005 | 2014 | 11022 | 1021 | 6199 | 65.8 | 63.8 |
| event_pm5y | 2010 | 2020 | 11117 | 915 | 6241 | 66.7 | 62.2 |
| post_10y | 2016 | 2025 | 7305 | 666 | 4150 | 69.2 | 60.8 |


### 26. U.S. LNG export opening

- `shock_id`: `gas_globalization_2016`
- `shock_type`: policy/market access
- `candidate_window`: 2016
- `event_anchor_year`: 2016
- `window_start_year` / `window_end_year`: 2016 / 2016
- Current exposure-family screen: `oil_gas_petroleum`, `gas_utility`

**Source-backed event description**

Modern Lower-48 LNG export capacity opened U.S. gas markets more directly to global demand.

**Source rows**

- [EIA Today in Energy, U.S. LNG export development](https://www.eia.gov/TODAYINENERGY/detail.php?id=67224) (government): EIA documents the modern U.S. LNG export opening after Lower-48 LNG export terminal development.


**Segment-data mapping note**

Maps to gas production, LNG terminals, Gulf Coast midstream, and industrial gas demand.

**Mapping work still separate from this catalog**

Needs geography/facility linkage for LNG terminal or Gulf Coast exposure.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2016 as the anchor year.

**Current caveat**

Post-2010 window only; sample composition and shale-era trends need separate controls.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2006 | 2015 | 12439 | 1015 | 6346 | 64.0 | 62.3 |
| event_pm5y | 2011 | 2021 | 11891 | 903 | 6173 | 65.9 | 62.0 |
| post_10y | 2017 | 2026 | 6949 | 644 | 3715 | 68.2 | 59.9 |


### 27. WTI storage/futures dislocation

- `shock_id`: `oil_storage_dislocation_2020`
- `shock_type`: event shock
- `candidate_window`: 2020
- `event_anchor_year`: 2020
- `window_start_year` / `window_end_year`: 2020 / 2020
- Current exposure-family screen: `oil_gas_petroleum`, `transport_freight`

**Source-backed event description**

WTI May 2020 futures settled below zero amid storage constraints, demand collapse, and contract-market mechanics.

**Source rows**

- [EIA Today in Energy, WTI Futures Price Fell Below Zero](https://www.eia.gov/todayinenergy/detail.php?id=43495) (government): EIA links the April 2020 negative WTI settlement to storage constraints, demand collapse, and contract-market mechanics.
- [CFTC Press Release on Negative WTI Settlement Review](https://www.cftc.gov/PressRoom/PressReleases/8315-20) (regulator): CFTC reviewed the April 20, 2020 negative WTI futures settlement episode.


**Segment-data mapping note**

Maps to crude producers, storage, midstream, refiners, and oilfield services.

**Mapping work still separate from this catalog**

Need to account for COVID demand collapse and storage/geography exposure.

**Window granularity note**

This row is represented as a one-year candidate window. The current coverage screen uses 2020 as the anchor year.

**Current caveat**

This is an event/dislocation window, not a contract-availability window.

**Mechanical segment-data coverage around anchor year**

| window | start_year | end_year | rows | firms | firm_years | margin_ready_pct | allocation_ready_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pre_10y | 2010 | 2019 | 15302 | 1216 | 7925 | 68.0 | 61.2 |
| event_pm5y | 2015 | 2025 | 13593 | 1071 | 7136 | 70.3 | 58.0 |
| post_10y | 2021 | 2030 | 5202 | 706 | 2861 | 72.1 | 56.1 |


## Source Artifacts

- `reports/segment_project_space/tables/segment_project_candidate_shock_catalog.csv`
- `reports/segment_project_space/tables/segment_project_candidate_shock_sources.csv`
- `reports/segment_project_space/tables/segment_project_event_window_readiness.csv`
- `reports/segment_project_space/tables/segment_project_candidate_shock_type_summary.csv`
