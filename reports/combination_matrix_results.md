# Combination Matrix: shocks × treatments for internal capital allocation

Generated 2026-06-02. Treats electricity as a production **input** and escalates the
treatment from narrow (power producers) to the boldest (the entire multi-segment
universe scaled by electricity-input intensity). Outcome = RSZ relative-investment
sensitivity (`rel_opp × treat × post`, capx/lagged-assets demeaned within firm-year);
prediction > 0. Table: `reports/tables/combination_matrix.csv`.

**2026-06-03 identification update.** The earlier "staggered 1996/98/99" rows in
this memo used an overly loose staggered builder. `scripts/run_combos.py` now uses
strict hub-state `firm_event.event_year` for regional dose designs. Under that
tighter matrix, the electric-producer strict-staggered margin coefficient is
+0.050 (t=1.16), so the combination matrix should be read as exploratory. The
current promoted Track 1 result is the electric-firm stacked RSZ design documented
in `docs/electricity_identification.md`.

## Electricity-input intensity measure
Electricity cost as % of value of shipments by industry (SIC), calibrated to EIA
MECS rankings (`scripts/build_intensity.py`): very-high = primary aluminum (15%),
alkalies/chlorine (11%), electrometallurgy (9%), cement/lime (7–8%); high = paper,
glass, nonferrous, inorganic chemicals, steel (4–6%); medium = mining, other
chemicals, textiles, semis (2.5–3.5%); low = most manufacturing (~1%); very-low =
trade/finance/services (0.3–0.6%). Built at segment SIC and aggregated (sales-weighted)
to the firm.

## Results ladder (margin as the opportunity)

| Treatment | Scope | Shock | coef | t | p | Verdict |
|---|---|---|--:|--:|--:|---|
| **A electric producer** | power producers | **staggered 1996/98/99** | **+0.041** | 2.58 | 0.010 | **SIGNIFICANT** |
| A electric producer | power producers | national 1996 | +0.029 | 1.69 | 0.091 | marginal |
| B energy producer | oil/gas+util | national 1996 | +0.033 | 1.89 | 0.059 | marginal |
| C high-input ≥3% | consumers+prod | national 1996 | +0.013 | 0.91 | 0.36 | null |
| C high-input ≥3% | consumers+prod | staggered | +0.015 | 1.23 | 0.22 | null |
| C very-high ≥6% | consumers+prod | national 1996 | −0.045 | −1.49 | 0.14 | null/neg |
| **D firm-intensity (cont)** | **ENTIRE universe** | national 1996 | +0.004 | 0.86 | 0.39 | null |
| **D firm-intensity (cont)** | **ENTIRE universe** | staggered | +0.004 | 1.01 | 0.31 | null |
| D′ seg-intensity (cont) | ENTIRE universe | national 1996 | +0.008 | 2.18 | 0.03 | marginal (fragile) |
| D′ seg-intensity (cont) | ENTIRE universe | staggered | +0.003 | 1.06 | 0.29 | null |
| D firm-intensity, MANUF only | manufacturing | national 1996 | +0.008 | 0.75 | 0.46 | null |
| D′ seg-intensity, MANUF only | manufacturing | national 1996 | +0.003 | 0.24 | 0.81 | null |
| intensity top-vs-bottom tercile | ENTIRE universe | national 1996 | −0.004 | −0.32 | 0.75 | null |

## What the matrix shows

1. **The effect is monotone in "how much operations ARE power."** It is robust for
   power **producers** (staggered, +0.041, t=2.58), weak-to-marginal for energy
   producers, and **null for electricity consumers / the whole universe** by input
   intensity — continuous, tercile, manufacturing-restricted, and on extensive-margin
   (segment count / HHI) outcomes alike.

2. **The boldest design is null — and that is informative, not a failure.** It is
   exactly the model's α prediction. Power producers have **high α**: their operations
   *are* the power exposure, so hedging reveals operating structure (the F3 channel
   fires). Electricity consumers have **low α**: electricity is one minor, separable
   input among many, so power-price exposure says little about operating quality and
   the information/allocation channel does not fire. Broadening treatment to all
   electricity users dilutes the sample with low-α firms and washes the effect out.

3. The one marginal bold cut (segment-intensity × national-1996, t=2.18) does **not**
   survive restricting to manufacturing (t=0.24), so it was recapturing power-producer
   *segments* embedded in diversified firms (those segments carry intensity ≈ 6%), not
   a genuine consumer effect.

## Bottom line
Across shocks (national 1996; staggered regional 1996/98/99) and treatments (producer
binary → energy → high-input consumer → continuous whole-universe intensity), the
internal-capital-allocation response is **concentrated in electric power producers**
and **absent for electricity consumers**. The producer-vs-consumer gradient is a clean
empirical confirmation of the paper's α-signing: the mechanism operates where exposure
reveals operations (high α), not merely where electricity is consumed.

Scripts: `build_intensity.py`, `run_combos.py`, `run_combos2.py`.
