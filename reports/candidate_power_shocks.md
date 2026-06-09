# Candidate Power / Electricity Hedgeability Shocks (online research, 2026-06-02)

Events that change the hedgeability / derivative availability of electricity price
risk for a definable set of firms. Tagged by which track they fit:
- **[HIST]** historical capital-allocation track (segment data, 1976–2007)
- **[MOD]** modern Revelio labor track (workforce data, 2008+)

## A. Exchange-traded electricity derivative launches (cleanest "derivative availability")
| Event | Date | Region / firms | Track |
|---|---|---|---|
| CME COB & Palo Verde power futures | 1996-03 | Western | HIST (used) |
| CME Alberta power futures | 1996-09 | Alberta/W. Canada | HIST |
| CME Cinergy & Entergy power futures | 1998-07 | Midwest / South | HIST (used) |
| CME PJM power futures | 1999-03 | PJM | HIST (used) |
| ICE electricity futures (Europe) | 2004 | EU | — |
| **Nodal Exchange launch** (first independent nodal power futures) | **2009-04** | CAISO first, then all ISOs | MOD ✅ |
| CME N.A. gas/power market expansion | 2012-09 | national | MOD (used) |
| Nodal Exchange ERCOT contracts | ~2011 (post nodal) | ERCOT | MOD |
| **Nodal Exchange SPP contracts** (40 new) | **2015-12** | SPP | MOD ✅ |
| CME European power | 2015-06 | EU | — |

## B. ISO/RTO organized-market formation (LMP day-ahead market → power priceable/hedgeable at hubs)
| Event | Date | Region | Track |
|---|---|---|---|
| PJM LMP market | 1997–98 | PJM (PA, NJ, MD, …) | HIST |
| CAISO market | 1998 | California | HIST |
| NYISO market | 1999 | New York | HIST |
| ISO-NE Standard Market Design (day-ahead) | 2003-03-01 | New England | HIST |
| **MISO day-ahead + FTR market** | **2005-04-01** | Midwest (large) | HIST ✅ |
| ERCOT nodal market | 2010-12-01 | Texas | MOD (used) |
| MISO South / Entergy integration | 2013-12-19 | AR, LA, MS | MOD (used) |
| SPP Integrated Marketplace | 2014-03-01 | KS, OK, NE, ND, SD | MOD (used) |

## C. Capacity markets (new forward hedgeable product = capacity price risk)
| Event | Date | Region | Track |
|---|---|---|---|
| PJM Reliability Pricing Model (RPM) | 2007-06-01 (1st auction Apr 2007) | PJM | HIST/MOD edge |
| ISO-NE Forward Capacity Market | FCA1 2008; 1st delivery 2010-06 | New England | MOD |

## D. CAISO Western Energy Imbalance Market — STAGGERED, FIRM-LEVEL entry ⭐ best for Revelio
Exact go-live dates by **named utility** (match to gvkey/rcid → exact treatment timing,
not HQ-state guessing):
| Utility | EIM entry | States |
|---|---|---|
| PacifiCorp | 2014-11-01 | UT, OR, WY, ID, WA, CA |
| NV Energy | 2015-12-01 | NV |
| Arizona Public Service | 2016-10-01 | AZ |
| Puget Sound Energy | 2016-10-01 | WA |
| Portland General Electric | 2017-10-01 | OR |
| Idaho Power | 2018-04-04 | ID |
| Powerex (BC Hydro) | 2018-04-04 | BC |
| (later: SMUD, Seattle City Light, Salt River, LADWP, BANC, etc. 2019+) | 2019+ | West |

## E. Related hedgeable-risk shocks (robustness / placebo)
- CME weather derivatives, 1999 (Armstrong-Glaeser-Huang setting; utilities/ag).
- NYMEX natural gas futures, 1990; WTI crude, 1983 (companion energy, already tested — mostly null).

---

## Recommendation (highest value-add)

**Historical capital-allocation track (Track 1):** add **MISO day-ahead market
(2005-04)** as a new cohort — large, clean, well-dated, many Midwest firms — and
optionally **ISO-NE SMD 2003** and **PJM RPM 2007**. This turns the 3-event stack
(1996/98/99) into a 5–6-event stack with more treated firms and more staggering.

**Modern Revelio labor track (Track 2):** the **CAISO Western EIM staggered entry
(2014–2018)** is the single best fix. It gives **firm-level, exact-date** treatment
for named utilities (PacifiCorp, NV Energy, APS, PSE, PGE, Idaho Power, …) — exactly
what was missing (the null labor result was driven by crude HQ-state assignment).
Combine with **Nodal Exchange 2009 / SPP 2015** derivative launches as the
true "derivative availability" shocks in the Revelio window.

---

# Mechanism-fit classification (Delv3-2.pdf)

A shock is admissible as treatment only if it matches the paper's channel: a
**hedging technology** that produces **hard information** (Stein 2002 — marked-to-
market, FAS-133 / ASC-815 disclosed, third-party verifiable) as a **byproduct of an
activity that forces the firm to map its exposure** (Diamond 1984 bundling), thereby
**cleaning the divisional performance signal** and changing contracting / decision-
right incentives. Four tests:

1. Creates a **tradeable financial instrument** referencing the operating risk
   (not just a physical/operational change).
2. The position is **hard information** (mark-to-market, verifiable, disclosable) →
   transmits up to HQ.
3. Using it **forces exposure elicitation** (treasury must quantify which divisions
   are exposed = the F3 byproduct).
4. It references a **price that contaminates divisional performance**, so hedging
   strips signal noise and shifts incentives.

## TIER 1 — True derivatives (clean fit; the literal mechanism)
Exchange-traded futures/options: positions are mark-to-market and FAS-133-disclosed
(hard), sizing the hedge forces exposure mapping (byproduct info), and they reference
a price that contaminates divisional EBIT.

- **CME/NYMEX power futures (1996–99): COB, Palo Verde (Mar 1996), Alberta (Sep 1996),
  Cinergy, Entergy (Jul 1998), PJM (Mar 1999).** The first exchange-traded North
  American electricity futures — monthly cash/physically-settled contracts on regional
  power hubs that let firms lock a forward power price. First time power price risk
  became exchange-hedgeable; strongest historical fit.
- **CME N.A. gas/power suite (Sep 2012).** CME migrated OTC power swaps to cleared,
  exchange-listed futures across ISO/RTO hubs (PJM, MISO, NYISO, ISO-NE, ERCOT, CAISO,
  SPP) post-Dodd-Frank — a large expansion of locational hedgeable coverage. Best
  *true-derivative* shock inside the Revelio window.
- **Nodal Exchange (Apr 2009+).** First independent exchange offering *locational /
  nodal* power futures & options at thousands of nodes, hubs and zones across all
  ISOs; cleared via Nodal Clear (2015). Dramatically refined the granularity of
  hedgeable locational power-price risk; CAISO at launch, ERCOT post-2010, SPP +40
  contracts Dec 2015.
- **ICE power futures (US hubs, 2000s–2010s).** OTC-originated, later cleared power
  futures/options on major hubs (PJM West, ERCOT North, MISO Indiana, ISO-NE Mass Hub,
  CAISO SP-15). Same hard-information mechanics as CME/Nodal.
- **CME weather derivatives (1999).** HDD/CDD temperature futures & options hedging
  weather-driven demand/volume risk for utilities — *exactly the Armstrong-Glaeser-
  Huang (2022) setting, the paper's named empirical antecedent.*
- **NYMEX natural gas futures (1990), WTI crude futures (1983).** Commodity futures
  hedging fuel-cost / commodity-price risk; valid mechanism (already tested, mostly
  null — electricity is the higher-α setting).

## TIER 2 — Derivative-*like* financial instruments (good fit)
ISO-administered financial contracts that settle on price differences and hedge a
specific risk.

- **Financial Transmission Rights (FTRs) / Congestion Revenue Rights (CRRs).**
  ISO-auctioned financial instruments paying the congestion price difference between
  two nodes; hedge locational/congestion price risk. Financial, hard, settled on LMP —
  introduced alongside each LMP market (PJM 1999, MISO 2005, etc.).
- **Capacity-market forward auctions — PJM RPM (Jun 2007), ISO-NE FCM (FCA1 2008,
  delivery 2010).** Forward auctions that set a clearing *price for capacity* (MW of
  resource adequacy) 1–3 years ahead, creating a hard forward price. Derivative-like,
  but for a *different* risk (capacity/resource-adequacy revenue, not energy price).

## TIER 3 — Enabling infrastructure (creates the hard *price*, not itself a derivative)
Organized wholesale day-ahead/real-time markets using **locational marginal pricing
(LMP)** that manufacture a transparent, verifiable hub/nodal price — the *underlying*
that Tier 1/2 reference. They change the information environment (a market benchmark
for divisional performance now exists) but a firm's exposure is not a disclosed
derivative position, and they don't by themselves force exposure-elicitation. Best
used as a labeled robustness / "underlying-creation" proxy; entangled with the
restructuring confound.

- **PJM LMP market (1997–98)** — first US LMP day-ahead/real-time energy market.
- **CAISO market (1998)**, **NYISO market (1999)** — California / New York ISO markets.
- **ISO-NE Standard Market Design (Mar 2003)** — added day-ahead market + LMP in New England.
- **MISO day-ahead + FTR market (Apr 2005)** — large Midwest LMP market launch.
- **ERCOT nodal market (Dec 2010)** — Texas zonal→nodal transition (~4,000 nodes).
- **MISO South / Entergy integration (Dec 2013)** — Entergy footprint (AR, LA, MS) joins MISO LMP.
- **SPP Integrated Marketplace (Mar 2014)** — SPP day-ahead market + LMP go-live.

## TIER 4 — NOT valid for this mechanism
- **CAISO Western EIM (staggered 2014–2018: PacifiCorp, NV Energy, APS, PSE, PGE,
  Idaho Power).** A real-time *physical* imbalance/balancing market optimizing dispatch
  across balancing areas every 5 minutes. Improves operational price transparency and
  market access, but there is **no hedge position, no FAS-133 hardness, no exposure-
  elicitation byproduct**. Measurement-clean (named firms, exact dates) but
  **mechanism-invalid** — do not use as the derivative shock.
- **FERC Order 888 (1996, open-access transmission) / Order 2000 (1999, RTO
  formation).** Market-structure / restructuring, not a hard-information hedging
  technology — and the central identification confound, not a treatment.

## Special case — FAS 133 (effective fiscal years beginning after 15 Jun 2000)
The accounting standard (Accounting for Derivative Instruments and Hedging Activities;
now ASC 815) that *makes* derivative positions hard: requires derivatives at fair value
on the balance sheet with mandatory hedge-accounting disclosure. It is the economy-wide
"hardness technology" the paper's Stein-2002 channel relies on. Interacts with pre-
existing power/commodity exposure → a candidate moderator or stand-alone shock (and a
useful control, since it shifts the *disclosure/hardness* margin for all derivative users).

## Bottom line for treatment choice
- **Headline treatment = Tier 1** (optionally Tier 2). Modern/Revelio window →
  **Nodal Exchange 2009 and CME 2012 power suite**, not EIM or LMP formations.
- **Tier 3** = robustness proxy, explicitly labeled "underlying-price creation."
- **Tier 4** = excluded (EIM) or treated as confound (FERC orders).

## Sources
- Nodal Exchange history & launch (2009; CAISO/ERCOT/SPP expansion): [MarketsWiki](https://www.marketswiki.com/wiki/Nodal_Exchange), [Nodal Exchange Power](https://www.nodalexchange.com/products-services/power/)
- ISO/RTO formation (PJM 1997, CAISO 1998, NYISO 1999): [FERC Electric Power Markets](https://www.ferc.gov/electric-power-markets), [APPA](https://www.publicpower.org/policy/wholesale-electricity-markets-and-regional-transmission-organizations)
- MISO day-ahead + FTR market 2005-04-01: [MISO/Wikipedia](https://en.wikipedia.org/wiki/Midcontinent_Independent_System_Operator), [Sustainable FERC – Navigating MISO](https://sustainableferc.org/navigating-miso/)
- ISO-NE SMD 2003-03-01; FCM FCA1 2008 / delivery 2010: [ISO-NE history](https://www.iso-ne.com/about/who-we-are/our-history), [ISO-NE FCM](https://www.iso-ne.com/markets-operations/markets/forward-capacity-market)
- PJM RPM 2007-06-01: [PJM RPM](https://www.pjm.com/markets-and-operations/rpm.aspx), [CRS](https://www.congress.gov/crs-product/R48553)
- ERCOT nodal 2010-12-01; MISO South 2013-12-19; SPP IM 2014-03-01: [ERCOT/Lexology], [Entergy MISO PRNewswire](https://www.prnewswire.com/news-releases/entergy-utilities-complete-miso-integration-236533081.html), [SPP](https://www.spp.org/newsroom/press-releases/spp-stakeholders-vote-to-proceed-with-integrated-marketplace-march-1/)
- CAISO Western EIM entry dates: [CAISO EIM](https://www.caiso.com/documents/westerneimparticipantprofiles.pdf), [Puget Sound Energy EIM FAQ](https://www.pse.com/en/pages/energy-supply/energy-imbalance-market-faq)
- ICE electricity futures (Europe 2004; US hubs): [ICE Electricity](https://www.theice.com/energy/power), [ICE Futures Europe](https://www.marketswiki.com/wiki/ICE_Futures_Europe)
