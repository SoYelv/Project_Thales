# Empirical Summary: Risk Management as Internal Information Production

Date: 2026-06-03. Source: `reports/tables/all_specifications_summary.csv` (60 specifications).

**2026-06-03 identification update.** Track 1 has been tightened after this
summary table was compiled. The current baseline uses strict hub-state shock
assignment, documented in `docs/electricity_identification.md`, with backing
results in `reports/tables/t1_strict_identification_results.csv`. The strict
margin result is +0.181 (t=2.88); the pre-event multi-segment robustness is
+0.136 (t=2.35).

## 1. What was tested

Electricity-derivative availability as a shock to the hedgeability of power-price
risk, across three outcome families, many shocks, and many treatment definitions.

- **Tracks (outcomes):** segment reporting / information production (22 specs);
  internal capital allocation (30 specs); Revelio labor composition (8 specs).
- **Shocks:** historical exchange-traded power futures (COB/Palo Verde 1996,
  Cinergy/Entergy 1998, PJM 1999), companion energy futures (NYMEX gas 1990,
  WTI 1983), and recent shocks (Nodal Exchange 2009, ERCOT 2010, CME 2012,
  MISO-South 2013, SPP 2014, CAISO EIM 2014–18, PJM RPM 2007).
- **Treatments:** electric power producers; energy producers; electricity-input
  intensity (continuous and high/low) for electricity *consumers*; the entire
  multi-segment universe; α-moderated (operating-sensitivity) cuts.
- **Method:** stacked / staggered DiD and triple-difference; capital allocation via
  the Rajan–Servaes–Zingales relative-investment-to-opportunity sensitivity;
  firm/segment + year (or cohort×year) fixed effects; clustered by firm; controls
  = log assets & leverage (reporting), within-firm-year demeaning (allocation),
  log total headcount (labor).

## 2. Headline results (clean and significant)

**(a) Information production rises for treated power firms (1996 launches).**
Electric firms report more operating segments and more corporate/unallocated
segments after the futures launch — e.g. n_op_seg +0.33 (t=3.5), and +0.43
(t=4.2) vs energy/utility controls; n_nonop_seg +0.28 (t=6.7). [specs 1–10]

**(b) The organizational response is signed by α (the model's distinctive
prediction).** Within electric firms, those whose operations are more informative
about power-price risk (high α) *centralize* — fewer operating segments
(−0.36, t=−4.3), lower multi-segment probability (−0.19, t=−7.2), higher
concentration (HHI +0.05, t=+3.9). Triple-difference confirms (β₂<0). [specs 11–19]

**(c) Internal capital allocation: treated firms allocate to high-margin segments
(1996–99).** RSZ relative-investment sensitivity to segment operating margin rises:
+0.073 (t=2.44); +0.094 (t=2.25) on the selection-robust pre-event multi-segment
sample; +0.081 (t=2.17) with never-treated controls. With sales growth as the
opportunity the sensitivity *falls* (−0.034, t=−2.19) — consistent with allocating
on operating quality, not chasing top-line growth. [specs 23–26]

## 3. The early-vs-late sign reversal (recent shocks)

On the same capital-allocation outcome, the sign **flips** in the modern era:
electric producers' margin-sensitivity *declines* after the 2012 power-market
expansion — −0.055 (t=−2.72), robust to window and pre-event sample (−0.061),
clean event study (no pre-trend), and confirmed at MISO 2013 (−0.046) and SPP 2014
(−0.037). It is **not** α-moderated (period effect, not heterogeneity). [specs 41–52]

Reading: first-time hedgeability (1996) fires the HQ-information channel →
centralized, margin-directed allocation (sensitivity ↑); by 2012, with hedging
routine and utilities de-diversifying/re-regulating, decentralization forces
dominate (sensitivity ↓). Statistically clean, but the mechanism label is
contestable because 2012 is not a first-time derivative shock.

## 4. What did NOT work (reported honestly)

- **Electricity *consumers* / the whole-universe input-intensity treatment** — null
  across continuous, tercile, manufacturing-only, and extensive-margin outcomes
  [specs 30–40]. Consistent with the α gradient: producers (operations ≈ power) are
  high-α; consumers (electricity a minor separable input) are low-α, where the
  channel does not fire.
- **Revelio labor composition** — Finance and treasury/risk/analytics hiring shares
  do not move for power or electricity-intensive firms under any modern shock
  (Nodal 2009, CME 2012, staggered) [specs 53–60]. Likely measurement: crude
  HQ-state treatment, weak/late shocks, and Revelio coverage drift.
- **Companion energy events** (NYMEX gas 1990, WTI 1983) — largely null on segment
  outcomes; electricity is the higher-α setting.

## 5. Bottom line

Of 60 specifications, ~25 are significant. The robust, theory-consistent core is
**electric power producers** (high α): information production rises, the response is
α-signed toward centralization, and internal capital allocation tilts toward
high-margin segments after first-time electricity hedging (1996–99). Broadening to
electricity consumers or to the modern labor margin yields nulls; the most
interesting recent finding is a clean **sign reversal** in capital-allocation
sensitivity between the 1996 and 2012 eras.

**Scope condition:** all capital-allocation results are identified off *diversified*
(multi-segment) firms. **Caveat:** the breadth of the specification search means
individual estimates should be read against the full grid, not in isolation; the
CSV's `verdict` column flags confounded and discardable specs.
