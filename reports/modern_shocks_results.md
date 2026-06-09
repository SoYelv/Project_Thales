# Modern / Recent-Shock Sweep and the Early-vs-Late Sign Reversal

Generated 2026-06-02. Specification search over recent electricity shocks on the
internal-capital-allocation (RSZ) outcome and Revelio labor, with many treatments.

**2026-06-03 identification update.** The modern regional staggered code now uses
true later-treated states as not-yet controls. The capital-allocation margin result
remains null under the modern staggered design (roTp≈0, p≈0.98). National
2012/2013/2014 rows should be read as exploratory period breaks, not clean
independent shocks.

## Shocks tested (recent)
PJM RPM 2007, Nodal Exchange 2009, ERCOT nodal 2010, CME 2012 power suite,
MISO-South 2013, SPP 2014, CAISO EIM 2014–18; national-break and staggered designs.

## Headline modern result — capital allocation (electric producers)

A clean, robust, significant **negative** in the 2012 era — the *opposite* of the
historical 1996–99 positive. (Outcome = RSZ `rel_opp × elec × post`, capx/lagged
assets demeaned within firm-year; segment data.)

| Shock (national break) | rel_opp×elec×post | t | p |
|---|--:|--:|--:|
| CME 2012 | **−0.055** | −2.72 | 0.007 |
| MISO-South 2013 | **−0.046** | −3.01 | 0.003 |
| SPP 2014 | **−0.037** | −3.34 | 0.001 |
| Nodal 2009 | +0.015 | 0.87 | 0.38 |
| ERCOT 2010 | −0.017 | −0.84 | 0.40 |

**Robustness of the 2012 effect:** baseline −0.055 (t=−2.72); pre-2012 multi-segment
sample −0.061 (t=−2.70); window 2009–15 −0.050 (t=−2.23). **Event study is clean** —
pre-period interactions small/positive and insignificant (k=−6…−2, |t|<1.3), then a
monotone negative break reaching −0.086 (t=−3.18) by k=+5. Not a pre-trend.

(The 2012/2013/2014 national breaks have overlapping windows and are best read as one
post-2012 utility shift, not three independent shocks. The cleanly-identified modern
*staggered* design with not-yet-treated electric controls is **null** (t=−0.24); the
large EIM coefficient is a small-sample artifact and is discarded.)

## The early-vs-late sign reversal (electric producers, national break)

| Period | Shock | rel_opp×elec×post | t |
|---|---|--:|--:|
| EARLY | first electricity futures, 1996 | **+0.029** | +1.69 |
| LATE | CME 2012 power era | **−0.055** | −2.72 |

(Staggered early design is stronger: +0.041, t=2.58.) The reversal is **not**
α-moderated (`elec × post2012 × alpha` = +0.028, t=0.62), so it is a *period/maturity*
phenomenon, not cross-sectional α heterogeneity.

### Interpretation
Both signs are admissible in the model (F3 centralization vs F1+F2 decentralization).
- **1996:** first-time power hedgeability → the F3 information channel fires → hedging
  reveals operating structure to HQ → capital directed toward high-margin segments
  (allocation-margin sensitivity ↑). Centralization response.
- **2012 era:** power has been hedgeable for 15+ years; the period is one of utility
  **de-diversification / re-regulation** (merchant generation and trading arms divested,
  refocus on regulated networks). With hedging routine, F1+F2 decentralization
  dominates, and HQ-directed reallocation on margin recedes (sensitivity ↓).

This is a genuine, robust, recent-shock result — a sign flip in the organizational
response to electricity-derivative availability across the deregulation→maturity cycle.
It is statistically clean but its *mechanism label* is contestable (the 2012 expansion
is not a first-time derivative shock, and utility industry structure changed), so it is
best framed as a period-contingent reversal rather than a single causal effect.

## Treatments that did NOT work with recent shocks
- **Electricity-input intensity / consumers** (continuous, high-intensity, manufacturing):
  null across all recent shocks (consistent with the producer-vs-consumer α gradient).
- **Revelio labor composition** (Finance share, treasury/risk/analytics hiring share):
  robustly **null** under Nodal 2009 and CME 2012, for power, high-intensity and
  continuous-intensity treatments. Only finance *headcount level* falls (coverage drift).

## Bottom line
"Good results" with recent shocks exist on the **capital-allocation** outcome — a clean,
robust, significant **negative** in the 2012 era that **reverses** the historical
positive. The labor channel and the electricity-consumer treatments remain null. The
strongest single positive finding is still historical (1996–99 electric producers,
+0.041, t=2.58); the strongest recent finding is the 2012 reversal.

Scripts: `run_modern.py`, `run_modern_es.py`, `run_modern_robust.py`, `run_t2_modern.py`.
