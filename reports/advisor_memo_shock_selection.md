# Memo: Which power-market events are admissible as the derivative-availability shock?

**To:** [Advisor]
**From:** Sophie Zhang
**Date:** 2026-06-02
**Re:** Treatment definition for "Risk Management as Internal Information Production" —
request for your judgment on a shock-admissibility rule and its design consequences

---

## 1. The decision I'm asking you to evaluate

I propose a rule for which electricity-sector events can serve as the **treatment**
("derivative availability"), grounded in the paper's mechanism rather than in data
convenience. The rule classifies candidate shocks into four tiers and would commit us
to using **exchange-traded power-derivative launches** (Tier 1) as the headline
treatment and to **excluding** organized-market formations (Tier 3) and the Western
Energy Imbalance Market (Tier 4) from the headline design. This memo states the rule,
shows where it bites, and flags three judgment calls where I'd value your view before
I lock it in.

The decision matters because it changes both empirical tracks (below) and, in
particular, may explain why one of our two results is currently null.

## 2. The admissibility criterion (from the model)

The model's channel is specific. Derivative availability matters because hedging
produces **hard information** (Stein 2002 — marked-to-market, FAS-133/ASC-815 disclosed,
third-party verifiable) as a **byproduct of an activity that forces the firm to map its
exposure** (Diamond 1984 bundling: treasury cannot design the hedge without eliciting
which divisions are exposed), which **cleans the divisional performance signal** and
thereby changes contracting and the allocation of decision rights (F1–F3).

A valid shock should therefore satisfy four conditions:
1. it creates a **tradeable financial instrument** referencing the operating risk;
2. the position is **hard information** (mark-to-market, disclosable) that transmits to HQ;
3. using it **forces exposure elicitation** (the F3 byproduct);
4. it references a **price that contaminates divisional performance**, so hedging strips
   signal noise and shifts incentives.

## 3. Classification

| Tier | Fit | Events | Why |
|---|---|---|---|
| **1 — true derivatives** | Headline | CME/NYMEX power futures 1996–99 (COB, Palo Verde, Alberta, Cinergy, Entergy, PJM); CME 2012 ISO/RTO suite; **Nodal Exchange 2009+**; ICE; CME **weather** 1999; NYMEX gas 1990 / WTI 1983 | Position is FAS-133-hard; sizing the hedge forces exposure mapping; references a contaminating price. Satisfies all four. |
| **2 — derivative-like** | Supporting | FTRs/CRRs; capacity forward auctions (PJM RPM 2007, ISO-NE FCM 2010) | Financial, settle on price differences, hedge a specific risk; capacity markets hedge a *different* risk (resource-adequacy revenue). |
| **3 — enabling infrastructure** | Robustness only | ISO **LMP** market formations: PJM 1997, CAISO 1998, NYISO 1999, ISO-NE 2003, MISO 2005, ERCOT nodal 2010, MISO-South 2013, SPP 2014 | Manufacture the hard *price* (the underlying) but the firm's exposure is not a disclosed derivative position and they do not force exposure elicitation. Precondition, not the instrument. |
| **4 — invalid** | Exclude | CAISO Western EIM (2014–18 staggered); FERC Orders 888/2000 | EIM is a *physical* real-time balancing market — no hedge position, no FAS-133 hardness, no byproduct information. FERC orders are restructuring (our confound). |

(Full descriptions and dates: `reports/candidate_power_shocks.md`.)

## 4. Where this bites — and why it may matter empirically

We have two tracks. The classification cuts cleanly across them:

- **Track 1 (internal capital allocation, segment data).** Treatment = the 1996–99 CME
  power-futures launches — **Tier 1, mechanism-valid.** Result is positive and robust:
  within a stacked design over the three launches, treated electric firms' segment
  investment becomes more sensitive to segment operating margin (rotp = +0.09, t = 2.3,
  pre-event-multi-segment sample). This is the result we like, and it uses an admissible
  shock.

- **Track 2 (Revelio labor composition, 2008+).** I had used ERCOT-nodal 2010,
  MISO-South 2013 and SPP 2014 as the staggered treatment — **these are Tier 3 (LMP
  market formations), not derivatives** — plus CME 2012 (Tier 1). Result is **null**.
  The classification suggests a substantive reason: the modern treatment was largely
  *mechanism-invalid*. The implied fix is to re-run the labor track on **Nodal Exchange
  2009 / CME 2012** (Tier 1) rather than on market formations.

So the rule is not academic bookkeeping: it reinterprets the null labor result as
plausibly a treatment-validity problem, and it tells us exactly what to substitute.

## 5. Three judgment calls I'd like your view on

**(a) Is an LMP market a "hard information technology," i.e., should Tier 3 be promoted?**
The strongest counterargument to my rule: before an LMP market exists there is *no*
verifiable, settlement-grade market price for power at a location; afterward there is.
The paper's notion of "hardness" is precisely verifiability and transmissibility — which
an LMP price has. One could argue the market formation is the *deepest* hard-information
shock and the futures merely repackage it. My reason for keeping it in Tier 3: the
model's distinctive content is the F3 *byproduct* channel (hedging forces exposure
elicitation), and a price merely existing does not force a firm to map its exposure —
only taking a position sized to exposure does. Do you agree that the F3 byproduct, not
mere price transparency, is the binding criterion?

**(b) Mechanism validity vs. identification.** The EIM (Tier 4) gives us *firm-level,
exact-date* staggered treatment (named utilities, clean timing) — ideal for
identification — but is mechanism-invalid. The valid Tier 1 modern shocks (Nodal, CME
2012) are national or hub-referenced and require a firm→hub operating-footprint
crosswalk to assign. Are you comfortable paying the identification cost (messier
assignment, footprint data) to keep the mechanism clean, rather than using EIM and
reframing the mechanism? My inclination is yes — using an invalid shock would undercut
the paper's contribution — but it raises the cost of the labor track.

**(c) Should FAS 133 enter the design?** FAS 133 (effective FY > June 2000) is the
standard that *makes* derivative positions hard/disclosed — arguably the literal
"hardness technology" in the model. It is economy-wide, so it lacks regional staggering,
but it interacts with pre-existing exposure. Worth using as an interacted shock or
moderator, or better left as a control?

## 6. My recommendation

1. Adopt the tier rule; **headline treatment = Tier 1**, with Tier 2 as support and
   Tier 3 as explicitly-labeled robustness ("underlying-price creation").
2. Keep **Track 1 as is** (1996–99 CME launches; pre-event multi-segment sample).
3. **Rebuild Track 2 on Nodal 2009 / CME 2012** and drop the EIM and the LMP-formation
   shocks from the headline; this requires a firm→ISO/hub footprint crosswalk
   (EIA-860/861, ISO membership), which I would build next.
4. Treat FERC 888/2000 strictly as confounds, addressed by within-α and
   not-yet-treated-region controls.

## 7. Specific questions

- Do you accept the **F3 byproduct (forced exposure elicitation)** as the binding test
  that separates Tier 1 from Tier 3? (§5a)
- Is the **mechanism-over-measurement** trade in §5b the right call, given it makes the
  labor track substantially more data-intensive?
- Should I invest in the **firm→hub footprint crosswalk** now (needed for a valid modern
  labor test), or concentrate the paper on the **Track-1 capital-allocation result**
  (already clean and mechanism-valid) and demote the labor channel to suggestive?
- Any concern that the 1996–99 Tier-1 launches are themselves **contemporaneous with the
  Tier-3/4 restructuring** (FERC 888 in 1996; LMP markets 1997–99), such that even our
  preferred shock is partly entangled?

---

*Supporting material:* `reports/candidate_power_shocks.md` (tiers, dates, descriptions,
sources); `reports/results_capital_and_labor.md` (both tracks, results, robustness);
`reports/electricity_research_agenda.md` (original design).
