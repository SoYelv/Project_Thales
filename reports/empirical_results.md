# Empirical Results: Risk Management as Internal Information Production

Generated 2026-06-01. Author workflow: Claude (autonomous empirical run).

This memo reports the first set of empirical tests of the model in `Delv3-2.pdf`,
using the WRDS Compustat segment file plus firm-level Compustat fundamentals and
company headers pulled live from WRDS. The headline result supports the model's
**distinctive, signed cross-sectional prediction**: derivative availability is
decentralizing for low-α firms but **centralizing for high-α firms**.

---

## 1. Setting and identification

**Shock.** Staggered launches of exchange-traded electricity futures
(California-Oregon Border / Palo Verde, March 1996; Cinergy / Entergy, 1998;
PJM, 1999) as a regional/sectoral derivative-availability shock for electric
power firms. Companion energy events (NYMEX natural gas 1990, WTI crude 1983)
are used as comparison shocks.

**Treatment.** Firm has pre-event electric-power segment exposure
(`share_electric > 0` in any pre-event year), measured from BUSSEG SIC codes
(4911/4931/4939, 4910–4939, 4991). Treatment is fixed at the firm level from the
pre-period only, so it is not contaminated by post-event reclassification.

**Sample.** Firm-year panel built from `segment_data.csv`, deduplicated to the
latest `srcdate` per (gvkey, datadate, stype, sid), excluding
corporate/eliminations/unallocated/other reconciliation segments from operating-
segment counts. 352,429 firm-years / 29,843 firms; 298–308 electric-exposed firms
in the 1988–2004 estimation window. Merged with `comp.funda` controls (log assets,
leverage) and `comp.company` headers.

**Outcomes.**
- `n_op_seg`, `log_nseg` — count of real operating segments (disaggregation /
  reporting granularity; a *decentralization* proxy in the sense of the agenda).
- `multi_seg` — indicator for >1 operating segment.
- `hhi` — Herfindahl concentration of segment sales (a *centralization* /
  consolidation proxy).
- `n_nonop_seg` — count of corporate/unallocated reconciliation segments.

**The moderator α.** Per `Delv3-2.pdf` §4.2, α is **not** exposure magnitude; it is
the extent to which exposure is *informative about operations*, proxied by
pre-event operating sensitivity. Main proxy: pre-1996 within-firm volatility of
segment operating margin (`a_segvol`), rank-transformed and standardized.
Robustness proxies: pre-period ROA volatility (`a_vol`), and |slope| of pre-period
ROA on a fossil-fuel price index (`a_pricebeta`, the paper's preferred operating-
sensitivity measure). A deliberately *wrong* proxy — exposure intensity
(`a_share_elec`) — is included as a methodological check.

---

## 2. Headline results

### Table 1 — Average DiD (treated electric firms, post ≥ 1996), TWFE (firm + year FE), clustered by firm

| Outcome | vs all firms | vs energy/utility controls |
|---|---|---|
| n_op_seg | **+0.326** (t=3.5) | **+0.429** (t=4.2) |
| log_nseg | **+0.073** (t=3.0) | **+0.107** (t=4.1) |
| multi_seg | +0.006 (t=0.2) | **+0.065** (t=2.1) |
| hhi | −0.016 (t=−1.1) | **−0.054** (t=−3.4) |
| n_nonop_seg | **+0.280** (t=6.7) | **+0.328** (t=7.5) |

*Reading:* on average, electric firms become **more disaggregated** after the
futures launch — more operating segments, more corporate/unallocated segments,
and (vs the cleaner energy/utility control group) lower sales concentration and a
higher chance of multi-segment reporting. This matches **Prediction 2** (derivative
availability raises internal information production / reporting granularity).

### Table 2 — Within-electric Post × α (rank), headline. Firm + year FE, clustered by firm. N≈3,640, 298 firms

| Outcome | Post × α | t | p |
|---|---:|---:|---:|
| n_op_seg | **−0.363** | −4.33 | 0.000 |
| log_nseg | **−0.124** | −5.67 | 0.000 |
| multi_seg | **−0.186** | −7.15 | 0.000 |
| hhi | **+0.053** | +3.88 | 0.000 |
| n_nonop_seg | −0.021 | −0.49 | 0.623 |

*Reading:* among electric firms, the ones whose **operations are more informative
about energy-price risk (high α)** move in the **opposite** direction from the
average — fewer operating segments, lower multi-segment probability, and **higher
concentration**. Because year fixed effects absorb anything common to all electric
firms (SFAS 131, FERC restructuring), this within-electric heterogeneity is the
clean test. It is exactly the model's **β₂ < 0** prediction on decentralization
outcomes (§4.4) and **Prediction 3** (high-α firms hedge-and-centralize).

### Table 3 — Full-sample triple difference: treat × post × α (rank)

| Outcome | β₁ (treat×post) | β₂ (treat×post×α) | t(β₂) | p(β₂) |
|---|---:|---:|---:|---:|
| n_op_seg | +0.316 (t=3.4) | **−0.251** | −2.88 | 0.004 |
| log_nseg | +0.070 (t=3.0) | **−0.085** | −3.73 | 0.000 |
| multi_seg | +0.001 (t=0.05) | **−0.124** | −4.57 | 0.000 |
| hhi | −0.013 (t=−0.9) | **+0.031** | +2.16 | 0.031 |

*Reading:* the average treated effect is disaggregation (β₁>0), but it is undone
and reversed as α rises (β₂<0; HHI β₂>0). **Low-α firms delegate/disaggregate
(Regime B); high-α firms centralize/consolidate (Regime C).** This is the signed
cross-sectional core of the model.

---

## 3. Validation and robustness

- **α-moderated event study (within electric).** The α × relative-year
  interactions are small and insignificant for all pre-event years (k = −6…−2,
  |t| < 1.6) and turn progressively negative after the launch, reaching
  −0.44 (t=−2.2) by k=+4…+6 for `n_op_seg` (and −0.145, t=−2.6, for `log_nseg`).
  **No pre-trend in the α-channel** — this is what rescues identification, since
  the *level* DiD on `n_op_seg` has a mild pre-trend and turns on around 1998
  (overlapping SFAS 131).
- **Placebo event (1992).** Within-electric Post × α at a fake pre-launch date is
  null for all outcomes (p = 0.30 / 0.31 / 0.16).
- **Alternative α proxies.** Same-signed and significant for ROA-volatility α and
  fuel-price-beta α (the paper's preferred operating-sensitivity measure): e.g.
  `a_pricebeta` gives n_op_seg −2.52 (t=−2.8), n_nonop_seg −1.18 (t=−3.8).
- **Methodological check (intensity ≠ α).** Using exposure *intensity*
  (`share_electric`) as the moderator flips every sign (n_op_seg +0.24, t=6.6).
  This is precisely the error the paper warns against in §4.2 ("heterogeneity based
  on whether exposure *reveals* operations, not merely whether exposure exists").
  The sign-flip is a feature: it confirms the result is driven by the operations-
  informativeness content of α, not by how much power exposure a firm has.
- **Cleaner control group.** Restricting controls to energy/utility firms (vs all
  firms) strengthens the average effect and makes HHI and multi-segment
  significant, consistent with the agenda's recommendation to avoid generic
  non-utility controls.

---

## 4. What did *not* work (reported honestly)

- **Natural gas 1990 and WTI crude 1983** average DiDs are mostly null on segment
  outcomes — consistent with the agenda's claim that electricity is the high-α
  setting where the distinctive channel is strongest, but it means the design is
  currently identified off electricity alone.
- **Capital-allocation prediction** (segment investment-margin sensitivity rising
  with post × α) has the right sign (m_post_alpha = +0.021) but is **insignificant**
  (t=0.9, N=7,113 segment-years). Underpowered with current data; needs the
  segment-investment panel built out and possibly firm-level capex authority data.
- **Level `n_op_seg` DiD** has a mild negative pre-trend and a turn-on around 1998,
  so the *average* effect alone cannot be cleanly separated from SFAS 131. The
  within-electric α design is what delivers clean identification.

---

## 5. Bottom line

The model's signed prediction holds in the data. Electricity-futures availability
is associated with **more internal information production on average** (Prediction
2), and the organizational response is **signed by α exactly as the model predicts**
(Predictions 3–4): firms whose operations are tightly informative about energy
price risk **centralize** (fewer, more concentrated segments) after the shock,
while weakly-exposed firms **decentralize**. The result has no pre-trend, passes a
placebo, is robust across three operating-sensitivity α proxies, and reverses under
the (theoretically wrong) intensity proxy — a clean internal validation of the
paper's central measurement claim.

### Next steps to strengthen
1. Region crosswalk (EIA 861/860, ISO/RTO membership) to stagger PJM/COB/Palo Verde
   treatment and add not-yet-treated-region controls (kills the remaining
   restructuring confound directly).
2. Hub price series (Palo Verde, COB, PJM) for a sharper, region-specific α.
3. 10-K / FAS 133 derivative-footnote text (wrdssec is available) to validate
   that treated high-α firms actually increase power-hedging and centralized-
   treasury language — the model's first-stage.
4. Build the segment-investment panel to re-test capital allocation with power.
```

### Reproduction
Scripts in `scripts/`: `build_panel.py` → `build_firmyear.py` → `pull_wrds.py`
→ `build_regdata.py` → `build_alpha.py` → `analysis.py` (Table 1 batch) →
`event_study.py` → `triplediff.py` → `verify.py` → `final_results.py`
(Tables 1–3, saved to `reports/tables/final_results.csv`).
