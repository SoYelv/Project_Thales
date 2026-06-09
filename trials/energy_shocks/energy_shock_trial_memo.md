# Energy Shock Trial Memo

This memo summarizes the trial scan. All outputs in this folder are exploratory
and isolated from the production pipeline.

## What Was Run

- 1,278 oil/gas/carbon/emissions specifications were screened.
- Outcome families:
  - RSZ internal-capital-allocation tests: `rel_inv ~ rel_opp * treatment * post`.
  - Firm-year organization tests: `n_op_seg`, `log_nseg`, `hhi`, `multi_seg`,
    `nonop_sales_share`.
- Robustness layers:
  - `±3`, `±5`, and `±7` windows.
  - `all_multiseg` and `pre_multiseg` segment samples for RSZ.
  - Event-study leads/lags.
  - Pre-only placebo years.
  - Leave-one-relative-year-out.
  - Treatment-specific linear trend checks for candidates with strong baseline
    results but visible pre-trends.

## Best Candidates

### 1. FERC 636 1992 x pre-gas exposure, RSZ margin

This is the strongest gas-market candidate for the RSZ allocation outcome, but
it should be labeled as a gas-market restructuring shock, not a derivative
launch.

- Baseline robustness: 4 of 6 specs have `p < .05`; median beta `-0.0321`,
  median t `-2.36`.
- Drilldown: placebo is clean (`0` placebo specs with `p < .10`), leave-one is
  stable (`10/11` with `p < .05`), but one pre lead is marginal.
- Trend-adjusted check: passes. With `rel_opp * treatment * linear trend`
  included, 3 of 3 specs have `p < .05`; median beta `-0.0599`, median t
  `-2.42`.

Interpretation: after gas restructuring, pre-gas-exposed firms show lower
allocation sensitivity to lagged segment margin. This is opposite in sign to the
early electricity producer result, so it is not a direct replication of the
electricity mechanism.

### 2. Oil collapse 1986 x pre-oil/gas share, firm-year organization outcomes

This is the strongest oil candidate, but it is a price shock rather than a
financial-contract-availability shock.

- Baseline firm-year results are stable across all three windows.
- Placebos are clean (`0` placebo specs with `p < .10` for the selected oil
  outcomes).
- Leave-one-year checks are stable (`11/11` for `hhi`, `log_nseg`, and
  `n_op_seg`).
- Event-study leads show differential pre-trends, so the raw DiD should not be
  used without a trend adjustment.
- Trend-adjusted checks pass for:
  - `hhi`: median beta `-0.0077`, median t `-2.85`, 3 of 3 specs with `p < .05`.
  - `n_op_seg`: median beta `+0.0190`, median t `+2.52`, 3 of 3 specs with
    `p < .05`.

Interpretation: oil/gas-exposed firms become less concentrated and operate more
segments after the 1986 oil collapse, conditional on a treatment-specific linear
trend.

## Screen-Only Results

These looked significant in the first-pass grid but failed drilldown:

- `GAS_SPIKE_2001 x energy_segment`, RSZ margin: clean pre leads, but placebo
  fails and trend-adjusted result disappears.
- `NATGAS_1990 x pre_energy_any`, RSZ sales growth: fails placebo and
  leave-one-year checks.
- `SO2_ALLOWANCE_1995 x pre_electric_any`, RSZ margin: fails pre-lead,
  placebo, and leave-one-year checks.
- Firm-year gas and EU ETS/high-carbon proxies: many strong baseline
  coefficients, but broad pre-trend/placebo failures.

## Carbon Assessment

Do not use the current carbon results as a main design.

- California 2013 produces huge RSZ coefficients, but the treated-firm count is
  only 4 to 7 in key specs, so the result is not credible.
- RGGI/EU ETS/high-carbon proxies do not survive pre-trend/placebo checks.
- Current data lacks facility emissions, allowance holdings, or credible
  geographic emissions exposure. Headquarters state plus SIC is too weak for a
  main carbon identification strategy.

## Recommendation

Use one of two paths if this trial is promoted:

1. For an RSZ-style energy-market result, develop `FERC636_1992 x pre_gas_any`
   as a separate gas restructuring design with a treatment-specific trend.
2. For an oil shock result, develop `OIL_COLLAPSE_1986 x pre_oilgas_share_z`
   on firm organization outcomes (`hhi`, `n_op_seg`) with trend-adjusted DiD.

Do not present these as the same estimand as the electricity derivative shock.
They are useful as parallel energy-market evidence, not as a clean substitute
for the original electricity identification.
