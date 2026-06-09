# Electricity Shock Identification

Updated on 2026-06-03.

## Current Baseline

The baseline early-electricity design now uses a strict HQ-state proxy for the first NYMEX electricity futures hubs:

| Shock | Year | Strict HQ-state proxy |
| --- | ---: | --- |
| COB / Palo Verde | 1996 | CA, OR, WA, AZ, NV |
| Cinergy / Entergy | 1998 | OH, IN, KY, AR, LA, MS |
| PJM | 1999 | PA, NJ, MD, DE, DC |

All other electric firms are treated as not-yet-treated or never-treated controls, depending on cohort. The older broad regional mapping is preserved in `reports/panel/firm_event.parquet` as `legacy_region` and `legacy_event_year`, but it is not the default.

Backing counts: `reports/tables/electricity_identification_counts.csv`.

## Why This Is Tighter

- The previous mapping assigned broad census-like regions to hub shocks. That made the treatment more powerful but too easy to challenge.
- The strict mapping keeps only states directly tied to the named delivery hubs or core operating footprints.
- This is still an HQ-state proxy, not a plant/service-territory assignment. The next identification upgrade should use plant locations, utility operating-company service territories, or EIA/FERC operating footprints.

## Current Track 1 Results

Main strict stacked RSZ results are in `reports/tables/t1_strict_identification_results.csv`.

| Sample | Opportunity proxy | `rel_opp x treat x post` | t | p |
| --- | --- | ---: | ---: | ---: |
| All multi-segment firm-years | Lagged operating margin | +0.181 | 2.88 | 0.004 |
| Pre-event multi-segment firms only | Lagged operating margin | +0.136 | 2.35 | 0.019 |
| All multi-segment firm-years | Segment sales growth | -0.039 | -2.20 | 0.028 |
| Pre-event multi-segment firms only | Segment sales growth | -0.042 | -1.67 | 0.094 |

Interpretation: the tightened design preserves the positive margin-allocation result. It does not support a generic "opportunity" result, because the sales-growth proxy moves in the opposite direction.

## Event-Study Caveat

The strict event-study has no statistically significant pre-trend, but the early leads are positive rather than flat. Use cautious wording: "no significant pre-trend" rather than "pre-period coefficients are small."

## Modern Shocks

The 2010+ modern electricity-market scripts remain exploratory. Regional staggered controls now include true later-treated power states where available. The national-break outputs are explicitly labeled as exploratory period breaks, not clean causal shocks.

## Sources To Cite

- NYMEX electricity futures began with COB and Palo Verde contracts on March 29, 1996: https://www.osti.gov/biblio/319013
- FERC market report records later NYMEX delivery points including Cinergy/Entergy in 1998 and PJM in 1999: https://www.ferc.gov/sites/default/files/2020-05/som-2003.pdf
- CME 2012 power-market expansion: https://investor.cmegroup.com/news-releases/news-release-details/cme-group-launches-new-natural-gas-and-power-markets
- Nodal Exchange launched its power platform in 2009: https://www.nodalexchange.com/nodal-exchange-receives-cftc-approval-to-register-as-a-designated-contract-market/
- ERCOT nodal go-live was December 1, 2010: https://www.ercot.com/files/docs/2013/12/30/42122_2013_nodal_accounting.pdf
- SPP Integrated Marketplace launched March 1, 2014: https://spp.org/markets-operations/spp-portal/
- CAISO EIM launched November 1, 2014: https://www.caiso.com/content/monthly-market-performance/nov-2020/energy-imbalance-market.html
