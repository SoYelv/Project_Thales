# Electricity Output vs Input Identification

Generated on 2026-06-07.

## Core Decision

Electricity shocks must be split into two mutually exclusive empirical designs.

1. **Electricity as output**: electric power producers sell electricity. The
   mechanism is output-price risk management and producer-side hedgeability.
2. **Electricity as input**: electricity-intensive manufacturers buy electricity.
   The mechanism is input-cost risk management and procurement-side hedgeability.

Do not pool these groups in one treatment. The predicted sign and relevant
outcomes need not be the same.

## Shock Assignment

The early baseline uses the strict electricity hub-state mapping from
`scripts/electricity_identification.py`:

| Shock | Year | Strict HQ-state proxy |
| --- | ---: | --- |
| COB / Palo Verde | 1996 | CA, OR, WA, AZ, NV |
| Cinergy / Entergy | 1998 | OH, IN, KY, AR, LA, MS |
| PJM | 1999 | PA, NJ, MD, DE, DC |

This is still an HQ-state proxy. The preferred future upgrade is plant/service
territory exposure.

## 2000+ / 2010+ Shock Expansion

The expanded modern set is kept separate from the early baseline.

Regional staggered shocks with not-yet/never controls:

| Shock | Event year | HQ-state proxy |
| --- | ---: | --- |
| PJM RPM | 2007 | PA, NJ, MD, DE, DC |
| ERCOT nodal market | 2010 | TX |
| MISO South / Entergy integration | 2013 | AR, LA, MS |
| SPP Integrated Marketplace | 2014 | KS, OK, NE, SD, ND |

CAISO EIM staggered proxy:

| Event year | HQ-state proxy |
| ---: | --- |
| 2015 | CA, OR, UT, WY |
| 2016 | NV |
| 2017 | AZ, WA |
| 2018 | ID |

Exploratory national period breaks:

| Shock | Event year | Identification status |
| --- | ---: | --- |
| Nodal Exchange power platform | 2009 | national period break; no clean within-mechanism regional control |
| CME power-market expansion | 2012 | national period break; no clean within-mechanism regional control |

## Output Group

Definition: firm ever has an electric-power operating segment in
`reports/panel/seg_invest2.parquet`, using `elec == 1`.

Controls: other output-producer firms in not-yet-treated or never/unmapped hub
states.

Current counts:

| Cohort/control | Firms | Firms with any multiseg year |
| --- | ---: | ---: |
| 1996 COB/Palo Verde | 54 | 36 |
| 1998 Cinergy/Entergy | 70 | 35 |
| 1999 PJM | 60 | 39 |
| Never/unmapped controls | 596 | 462 |

## Input Group

Main definition: non-output firm whose top electricity-intensity segment is a
manufacturing SIC (`2000-3999`) and whose maximum firm-year electricity input
intensity is at least 3%.

Robustness definitions:

- `input_manufacturing_very_high`: same as main, but max intensity at least 6%.
- `input_industrial_high`: non-output firm with top electricity-intensity SIC
  in `1000-3999` and max intensity at least 3%, adding mining and other
  industrial firms.

Controls: other input-candidate firms in not-yet-treated or never/unmapped hub
states. Output producers are excluded from every input group.

Current main input-manufacturing counts:

| Cohort/control | Firms | Firms with any multiseg year |
| --- | ---: | ---: |
| 1996 COB/Palo Verde | 74 | 49 |
| 1998 Cinergy/Entergy | 82 | 52 |
| 1999 PJM | 111 | 80 |
| Never/unmapped controls | 612 | 439 |

Frequent input-manufacturing industries are paper and pulp, steel and
electrometallurgical products, nonferrous metals, cement/lime/minerals,
industrial inorganic chemicals, glass, primary aluminum, and alkalies/chlorine.

## Separated RSZ Baseline

The same stacked RSZ design gives different results by mechanism group.

| Mechanism group | Sample | Opportunity | Coef. | t | p |
| --- | --- | --- | ---: | ---: | ---: |
| output producer | all multiseg | lagged margin | +0.181 | +2.88 | 0.004 |
| output producer | pre-event multiseg | lagged margin | +0.136 | +2.35 | 0.019 |
| output producer | all multiseg | sales growth | -0.039 | -2.20 | 0.028 |
| output producer | pre-event multiseg | sales growth | -0.042 | -1.67 | 0.094 |
| input manufacturing high | all multiseg | lagged margin | -0.012 | -0.34 | 0.737 |
| input manufacturing high | pre-event multiseg | lagged margin | -0.009 | -0.24 | 0.807 |
| input manufacturing high | all multiseg | sales growth | +0.018 | +1.33 | 0.184 |
| input manufacturing high | pre-event multiseg | sales growth | +0.020 | +1.37 | 0.169 |

Interpretation: the producer-side margin-allocation result survives the refined
split. The input-manufacturing group is not showing the same RSZ mechanism under
the current proxy. That is useful evidence against pooling the groups.

## 2000+ / 2010+ RSZ Screen

The expanded modern screen is in
`reports/tables/electricity_output_input_modern_rsz_results.csv`.

Main regional stacked results:

| Design | Mechanism group | Sample | Opportunity | Coef. | t | p |
| --- | --- | --- | --- | ---: | ---: | ---: |
| modern regional | output producer | all multiseg | lagged margin | -0.003 | -0.18 | 0.853 |
| modern regional | output producer | pre-event multiseg | lagged margin | -0.003 | -0.18 | 0.857 |
| modern regional | input manufacturing high | all multiseg | lagged margin | -0.191 | -2.36 | 0.018 |
| modern regional | input manufacturing high | pre-event multiseg | lagged margin | -0.178 | -2.10 | 0.036 |
| modern regional | input industrial high | all multiseg | lagged margin | -0.122 | -1.53 | 0.127 |
| modern regional | input industrial high | pre-event multiseg | lagged margin | -0.119 | -1.47 | 0.141 |

EIM screen:

| Design | Mechanism group | Sample | Opportunity | Coef. | t | p |
| --- | --- | --- | --- | ---: | ---: | ---: |
| EIM staggered | output producer | all multiseg | lagged margin | -0.090 | -3.16 | 0.002 |
| EIM staggered | output producer | pre-event multiseg | lagged margin | -0.090 | -3.14 | 0.002 |
| EIM staggered | input manufacturing high | all multiseg | lagged margin | -0.026 | -0.44 | 0.659 |
| EIM staggered | input manufacturing high | pre-event multiseg | lagged margin | -0.026 | -0.43 | 0.664 |

Interpretation:

- The early output-producer shock remains the main clean electricity result.
- Modern regional output-producer shocks are null under the separated
  not-yet-control design.
- Modern regional input-manufacturing shocks show a negative margin-allocation
  coefficient. This is plausibly a different input-cost mechanism, not the
  producer-side derivative story.
- The EIM output result is statistically strong but relies on very few treated
  firms in the stacked sample, so it should be treated as exploratory until
  service-territory or plant exposure is added.
- Nodal 2009 and CME 2012 rows are period-break screens only.

## Files

- `scripts/build_electricity_mechanism_groups.py`: builds mutually exclusive
  output/input firm-event groups.
- `scripts/run_electricity_output_input_rsz.py`: runs separated RSZ baselines.
- `reports/panel/electricity_mechanism_firm_event.parquet`: machine-readable
  firm-level mechanism flags.
- `reports/tables/electricity_output_firm_event.csv`: output producer firm-event
  table.
- `reports/tables/electricity_input_mfg_firm_event.csv`: main input
  manufacturing firm-event table.
- `reports/tables/electricity_input_industrial_firm_event.csv`: broader input
  industrial robustness table.
- `reports/tables/electricity_output_input_group_counts.csv`: counts by cohort.
- `reports/tables/electricity_output_input_modern_group_counts.csv`: modern and
  EIM counts by cohort.
- `reports/tables/electricity_modern_shock_definitions.csv`: modern shock
  definitions.
- `reports/tables/electricity_input_mfg_industry_counts.csv`: input industry
  composition.
- `reports/tables/electricity_output_input_rsz_results.csv`: separated RSZ
  estimates.
- `reports/tables/electricity_output_input_modern_rsz_results.csv`: separated
  modern RSZ screen.
- `reports/tables/electricity_output_input_group_qa.json`: construction QA.

## Next Steps

For the paper's main result, keep the output-producer design as the primary
electricity shock.

For the input design, do not force the same RSZ mechanism. Better next tests are:

- direct evidence of power/electricity derivative disclosure in 10-K Item 7A;
- input-cost exposure outcomes such as margins, volatility, capex smoothing, or
  segment survival;
- plant or state-level operating exposure rather than headquarters state;
- separate treatment intensity based on pre-event electricity intensity, not
  only binary hub-state treatment.
