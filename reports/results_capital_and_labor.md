# Results: Internal Capital Allocation & Revelio Labor under Staggered Electricity Shocks

Generated 2026-06-02. Autonomous empirical run (Claude). This memo reorients the
main outcome to **internal capital allocation** (Track 1) and **labor composition
from Revelio** (Track 2), using **multiple electricity shocks in a stacked /
staggered design**.

**2026-06-03 identification update.** The broad regional electricity-shock
mapping in this memo has been superseded for Track 1 by the strict hub-state
mapping documented in `docs/electricity_identification.md`. Under the strict
mapping, electric treated counts are COB/Palo Verde 1996 = 54, Cinergy/Entergy
1998 = 70, PJM 1999 = 60, untreated/not-mapped = 596. The current main RSZ
margin result is `rel_opp x treat x post = +0.181` (t=2.88, p=0.004), and the
pre-event multi-segment robustness is `+0.136` (t=2.35, p=0.019). The sales-growth
opportunity proxy remains negative. See `reports/tables/t1_strict_identification_results.csv`.

---

## Track 1 (MAIN RESULT): Internal capital allocation, staggered 1996/1998/1999 electricity shocks

**Design.** Stacked difference-in-differences (Cengiz et al. 2019) across three
regional electricity-futures launches, with firms assigned to an event by HQ
state → power region:

| Event | Year | Region (HQ states) | Treated electric firms |
|---|---|---|---|
| COB / Palo Verde | 1996 | Western (CA, OR, WA, NV, AZ, …) | 92 |
| Cinergy / Entergy | 1998 | Midwest + South (OH, IN, KY, …, AR, LA, MS, TX, …) | 390 |
| PJM | 1999 | PJM (PA, NJ, MD, DE, VA, …) | 72 |

Controls = not-yet-treated / never-treated electric firms. Window [T−5, T+5].
Unit = segment-year (multi-segment electric firms). FE = cohort×segment and
cohort×year; clustered by firm.

**Outcome = internal capital allocation sensitivity (Rajan–Servaes–Zingales).**
Within each multi-segment firm-year, segments are demeaned:
`rel_inv = inv_j − mean_firm(inv)`, `rel_opp = opp_j − mean_firm(opp)`, where
`inv = capx / lagged assets`. The slope of relative investment on relative
opportunity measures how strongly internal capital flows to the better-prospect
segment. Key DiD term: `rel_opp × treat × post`.

**Finding (Delv3-2 §4.3 — investment becomes more sensitive to segment
profitability post-shock):**

| Opportunity proxy | `rel_opp × treat × post` | t | p |
|---|---:|---:|---:|
| Lagged operating margin | **+0.073** | 2.44 | 0.015 |
| Lagged operating margin (never-treated ctrl) | **+0.081** | 2.17 | 0.030 |
| Segment sales growth | −0.034 | −2.19 | 0.029 |

Treated electric firms allocate **more investment toward high-margin segments**
after their region's futures launch — internal investment becomes more sensitive
to segment *profitability*. With *sales growth* as the opportunity the sensitivity
*falls*, consistent with the theory's logic that hedging cleans the operating
signal so headquarters allocates on operating quality (margin) rather than chasing
top-line growth.

**Validation.**
- *Event study* (sensitivity = `rel_opp × treat × k`): pre-event interactions
  (k ≤ −2) small and insignificant; post-event coefficients rise to +0.08–0.09
  (t≈1.5–1.8) by k=+3/+4. No pre-trend.
- *Robustness*: `rel_opp × treat × post` ranges +0.038 to +0.081 across control
  (not-yet vs never) and window ([−5,+5], [−4,+6], [−6,+8]) choices; significant
  (p<0.06) in 5 of 6, strongest with never-treated controls (t=2.2–2.3).

Scripts: `build_t1.py` → `run_t1_alloc2.py` → `verify_t1.py`.

**Segment coverage / sample (added 2026-06-02).** The RSZ test is identified off
multi-segment electric firms only (single-segment firms have no internal capital
market). Coverage benchmarks (`segment_coverage_by_group.csv`): universe
multi-segment firms average 3.06 segments; electric firms are *more* likely to be
multi-segment (~52–58% of firm-years vs 33% universe) but, conditional on multi,
*less* diversified (~2.5 vs 3.06 segments). Treated and control electric are well
balanced with each other (38.5% vs 34.4% multi; 2.55 vs 2.45 segments).

**Selection robustness — pre-event multi-segment sample (`run_t1_premulti.py`).**
Because treatment can push firms 1→2 segments (endogenous entry into the
multi-segment sample), the test was re-run on firms already multi-segment in the
pre-event window [T−5,T−1]:
- margin sensitivity `rotp` = **+0.094 (t=2.25, p=0.025)** vs +0.101 (t=2.46) full
  (243 firms vs 351). Result robust — not driven by treatment-induced diversification.
- sales-growth sensitivity −0.028 (t=−1.79), sign unchanged.
**Decision: adopt the pre-event multi-segment sample (243 firms) as the Track-1
baseline.** Scope condition: result speaks to *diversified* electric utilities.

---

## Track 2: Revelio labor composition, modern staggered electricity-market shocks

**Why modern shocks.** Revelio (LinkedIn-based) workforce coverage begins ~2008,
so the labor track uses modern organized-power-market launches that raise regional
power-price hedgeability, assigned by HQ state (staggered):

| Event | Date | Region | Treated power firms |
|---|---|---|---|
| ERCOT nodal market | 2010-12 | Texas | 28 |
| CME N.A. power expansion | 2012-09 | national (other power firms) | 184 |
| MISO South / Entergy | 2013-12 | AR, LA, MS | 1 |
| SPP Integrated Marketplace | 2014-03 | KS, OK, NE, ND, SD | 11 |

**Data.** Linked 781 power / 1,122 energy / 1,061 control firms (Compustat gvkey ↔
Revelio rcid via `revelio_common.company_mapping`). Pulled
`workforce_dynamics_geo` (role_k10 Finance share, headcount, salary) and finer
`individual_positions` hiring into **treasury / risk / analytics** roles
(Financial / Investment / Energy Analyst, Banking Analyst, Commodity Trader,
Compliance Auditor; 329k such hires).

**Outcome.** Finance-function share of US headcount; treasury/risk/analytics share
of hiring (`rf_share`); risk-role intensity (per headcount); log headcounts.
4-cohort stacked DiD, power vs non-power (and vs not-yet-treated power),
cohort×firm + cohort×year FE, clustered by firm.

**Finding: NULL (reported honestly).**

| Outcome | DiD | t | p |
|---|---:|---:|---:|
| Finance share (4-cohort) | +0.0005 | 0.25 | 0.80 |
| Treasury/risk/analytics hiring share | +0.0030 | 1.09 | 0.28 |
| Risk-role intensity (per headcount) | −0.0003 | −2.37 | 0.02 |
| Finance share, CME-2012, well-covered firms | +0.0010 | 0.42 | 0.68 |

The model's risk-infrastructure labor prediction (§4.3) does **not** show up: no
detectable increase in finance / treasury / risk headcount or hiring share for
power firms after the modern electricity-market launches; risk-role intensity is
if anything mildly negative.

**Why the labor channel is inconclusive here (not a clean test of the theory):**
1. **Treatment is crude.** Firms are assigned to a power region by *HQ state*;
   multi-region utilities are mismeasured, and only ~40 firms fall in the sharp
   regional cohorts (the rest are pooled into the weak 2012 national event).
2. **Weak shocks.** Exchange-traded power derivatives already existed pre-2010;
   ERCOT-nodal / MISO-South / SPP are market-structure changes, not first-time
   derivative availability — a much milder hedgeability shock than the 1990s
   launches used in Track 1.
3. **Coverage drift.** Power/utility firms' measured Revelio headcount *falls*
   relative to (tech-heavy) controls (`log_tot` DiD −0.10, t=−3.8), contaminating
   level outcomes; composition shares are cleaner but null.
4. **Role granularity.** "Treasury" proper is a tiny cell; role_k50/k150 analytics
   buckets are the closest proxy and may not capture a centralized-treasury build.

Scripts: `pull_revelio.py`, `pull_revelio_roles.py`, `run_t2_labor2.py`,
`run_t2_roles.py`, `run_t2_es.py` (tables `t2_labor.csv`, `t2_roles.csv`).

---

## Bottom line

- **Internal capital allocation is the strong, satisfactory main result**: under a
  strict hub-state stacked design over the 1996/1998/1999 electricity-futures launches,
  treated electric firms reallocate investment toward high-*margin* segments
  (sensitivity +0.181, t=2.88; pre-event multi-segment robustness +0.136,
  t=2.35). Event-study leads are not statistically significant, but early leads
  are positive enough that the clean wording is "no significant pre-trend" rather
  than "flat pre-trends." The sales-growth proxy remains negative.
- **The Revelio labor channel is null** under modern staggered power-market shocks.
  This is most plausibly a power/measurement problem (crude HQ-state treatment,
  weak modern shocks, Revelio level drift) rather than evidence against the theory,
  but it is reported transparently.

### To strengthen the labor track next
- Firm-region operating footprint (EIA-860/861 plant locations, FERC/ISO
  membership) to assign treatment by where firms actually operate, not HQ state.
- A sharper modern derivative-availability event (e.g., first listing of a
  region-specific power future on CME/Nodal) rather than market-structure changes.
- α-moderated labor test (high-α power firms) once a modern α is built.
