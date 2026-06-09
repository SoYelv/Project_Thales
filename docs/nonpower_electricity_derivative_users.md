# Non-Power Electricity-Derivative User Candidates

Generated on 2026-06-03.

## Can Electricity Shocks Apply Outside Power Producers?

Yes, conceptually. Electricity derivatives can be used by both sellers of power and large buyers of power. The empirical question is whether a firm has enough electricity price exposure and market access for the derivative-availability shock to matter.

In this project, power producers remain the cleanest treated group. Non-power firms should be treated as a separate electricity-input design, not mixed into the producer design without a separate exposure rule.

## What We Can Observe Locally

The current data does not directly observe electricity futures, forwards, swaps, or options usage. The local proxy is electricity-input exposure:

- `reports/panel/seg_invest2.parquet` contains segment-level and firm-year electricity intensity.
- `scripts/build_intensity.py` constructs approximate electricity cost as percent of shipments by SIC.
- `scripts/identify_electricity_derivative_users.py` flags non-power firms with high electricity-input exposure.

Backing outputs:

- `reports/tables/electricity_derivative_user_candidates.csv`
- `reports/tables/electricity_derivative_user_candidate_summary.csv`

Current threshold:

- `very_high_input`: non-power firm with max firm-year electricity intensity >= 6%.
- `high_input`: non-power firm with max firm-year electricity intensity >= 3%.

Current counts:

- High or very-high non-power candidates: 1,869 firms.
- Very-high candidates: 446 firms.
- High/very-high candidate firm-years: 18,270 at the 3% threshold; 3,768 at the 6% threshold.

Frequent candidate industries include metal mining, paper and pulp, nonferrous metals, steel/electrometallurgical products, cement/lime/minerals, glass, industrial inorganic chemicals, alkalies/chlorine, and primary aluminum.

## How To Verify Actual Contract Use

The best next step is a text/disclosure screen. Search 10-K Item 7A and derivative footnotes for terms such as:

- electricity derivative(s)
- power derivative(s)
- power futures
- electricity futures
- power swaps
- electricity swaps
- power forwards
- electricity forwards
- fixed-price electricity contract
- commodity derivative(s)
- energy price risk
- power purchase agreement

Classify hits into:

- `actual_power_derivative_user`: explicit electricity/power futures, forwards, swaps, options, financial transmission rights, or congestion revenue rights.
- `possible_energy_hedger`: generic commodity/energy derivative disclosure but no explicit electricity term.
- `physical_contract_only`: power purchase agreement or fixed-price supply contract without derivative language.
- `no_disclosure`: no relevant disclosure found.

## Identification Implication

Non-power high-intensity firms can be used in a separate electricity-input treatment. They should not be left in a generic control group if they are plausibly able to hedge electricity price risk. For the current Track 1 producer result, this mainly matters for alternative designs that use the broad multi-segment universe.

## Source Pointers

- Nodal Exchange describes power futures/options as tools for market participants to manage price, basis, and credit risk across RTO/ISO locations.
- CME describes power contracts as tools to mitigate price risk in day-ahead and real-time power markets.
- CFTC bona fide hedge rules recognize commercial end-user hedging needs for anticipated requirements and other commercial risks.
