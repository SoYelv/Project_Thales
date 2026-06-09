# Electricity Shock Research Agenda

Generated at UTC: 2026-06-01T02:05:00+00:00

## Core Recommendation

Use electricity derivative availability as a regional hedgeability shock. The baseline should not be "all utilities after 1996." The better design is an event-level treatment in which firms are treated when they have pre-existing electric-power exposure and operate in the region served by the newly listed electricity futures contract.

Main empirical question:

> When electricity price risk becomes more hedgeable in a firm's relevant power market, do multidivisional firms change segment reporting, internal capital allocation, and centralization patterns in ways predicted by the proposal?

## Why Electricity Fits The Proposal

Electricity is a high-alpha setting. Exposure is closely connected to operating structure: generation assets, service territory, fuel mix, transmission constraints, wholesale market participation, load shape, and weather sensitivity. A treasury team designing a power hedge likely needs information that is directly informative about operations, so the headquarters information-production channel should be strong.

This makes electricity a good first setting for the distinctive prediction of the proposal: derivative availability should not simply decentralize through cleaner performance signals. In high-alpha settings, it may centralize authority by revealing operational structure to headquarters.

## Event Set

Use a two-tier event set.

### Tier 1: Historical Electricity Futures

These are the strongest first tests because they are early derivative-availability shocks and have meaningful pre/post windows in the WRDS segment data.

| Event | Launch date | Initial treated region or hub | Source |
| --- | --- | --- | --- |
| California-Oregon Border power futures | March 29, 1996 | Western power market | CME historical first trade dates |
| Palo Verde power futures | March 29, 1996 | Western/Southwest power market | CME historical first trade dates |
| Alberta power futures | September 27, 1996 | Alberta/Western Canada | CME historical first trade dates |
| Cinergy power futures | July 10, 1998 | Midwest/Eastern interconnect hub | CME historical first trade dates |
| Entergy power futures | July 10, 1998 | South/Central power market | CME historical first trade dates |
| PJM power futures | March 19, 1999 | PJM territory | CME historical first trade dates |

Source: [CME historical first trade dates](https://www.cmegroup.com/media-room/historical-first-trade-dates.html).

### Tier 2: Modern Electricity-Market Expansion

Use these for modern relevance after the historical results are understood.

| Event | Launch date | Role in study | Source |
| --- | --- | --- | --- |
| CME new gas and power markets | September 10, 2012 | Modern North American ISO/RTO expansion | CME press release |
| CME Europe power futures | June 15, 2015 | International extension, likely not first-pass with Compustat-only data | CME press release |
| PJM electricity contract expansion | May 11, 2026 | Too late for current outcome tests, but useful for proposal motivation | CME SER 9705R |

Sources: [CME 2012 launch](https://investor.cmegroup.com/news-releases/news-release-details/cme-group-launches-new-natural-gas-and-power-markets), [CME 2015 European power launch](https://www.cmegroup.com/media-room/press-releases/2015/5/20/cme_group_announceseightneweuropeanpowercontractsoncmeeurope.html), [CME SER 9705R](https://www.cmegroup.com/notices/ser/2026/05/ser-9705r.pdf).

## Key Confound

Electricity futures launches occurred during electricity restructuring. FERC Order No. 888 promoted open-access, non-discriminatory transmission service, and FERC Order No. 2000 encouraged regional transmission organizations. These are not nuisance details; they are central threats to identification.

Sources: [FERC Order No. 888](https://www.ferc.gov/industries-data/electric/industry-activities/open-access-transmission-tariff-oatt-reform/history-oatt-reform/order-no-888), [FERC RTO/ISO overview](https://www.ferc.gov/industries-data/electric/rtos-and-isos), [FERC electric power markets overview](https://www.ferc.gov/electric-power-markets).

Research-design implication: control firms should be electric/power firms in not-yet-treated or non-contract regions, not generic non-utility firms.

## Treatment Definition

Define treatment at the firm-event level.

For firm `i` and electricity event `k`:

```text
Treated_i,k = ElectricExposure_i,k_pre * RegionMatch_i,k
```

Where:

```text
ElectricExposure_i,k_pre = pre-event BUSSEG sales share in electricity/power segments
RegionMatch_i,k = 1 if the firm is mapped to the relevant power hub/ISO/RTO/service region
```

Baseline electric exposure from BUSSEG:

- SIC 4911: electric services
- SIC 4931: electric and other services combined
- SIC 4939: combination utilities, not elsewhere classified
- SIC 4910-4939 and 4991 as a broader utility/power definition

Exposure variants:

1. Binary: any pre-event electric BUSSEG sales.
2. Intensive: pre-event electric BUSSEG sales share.
3. Strong treatment: electric BUSSEG sales share above 10%, 25%, or top tercile.

Region mapping hierarchy:

1. Best: utility service territory or generator/operator location from EIA Form 861, EIA Form 860, or FERC/ISO membership data.
2. Good: subsidiary/segment geographic names plus headquarters state.
3. Minimum viable: headquarters state mapped to power region, used only as a first-pass screen.

## Control Definition

Use controls that face similar electricity industry conditions but did not receive the same derivative-availability shock at that time.

Preferred control groups:

1. Electric/power-exposed firms outside the event region.
2. Electric/power-exposed firms in not-yet-treated regions.
3. Matched utility and power firms balanced on pre-period size, operating margin, capex intensity, segment count, leverage if firm-level Compustat is added, and region-level restructuring exposure.

Avoid controls that are too broad, such as all non-electric firms, except as a descriptive benchmark.

## Main Outcomes

### 1. Segment Reporting And Information Acquisition

Use BUSSEG and OPSEG to test whether electricity derivative availability changes the internal information environment.

Outcomes:

- number of business segments per firm-year;
- Herfindahl concentration of segment sales;
- probability of reporting multiple operating/business segments;
- segment disclosure detail, if textual 10-K data is later added;
- appearance/disappearance of electric/power segments.

Prediction:

Derivative availability should increase reporting granularity or change segment definitions if firms build more internal exposure-mapping infrastructure.

### 2. Internal Capital Allocation

Use segment-year BUSSEG outcomes.

Outcomes:

- segment investment: `capxs / lagged ias`, `capxs / sales`, or `capxs / lagged sales`;
- sensitivity of segment investment to segment operating margin;
- sensitivity of segment investment to segment sales growth;
- within-firm reallocation toward high-performing segments.

Prediction:

If electricity is high-alpha, post-shock treated firms should show stronger headquarters-directed allocation. Empirically, this means segment investment becomes more sensitive to segment profitability or opportunities, especially in high-alpha firms.

### 3. Centralization Proxies

Segment data alone only partially captures centralization, so use these as first-pass proxies:

- decrease in segment autonomy proxies, such as fewer independently named operating segments;
- increase in corporate/unallocated/corporate-and-other segments;
- stronger firm-level coordination of capex across segments.

If text data is added later:

- mentions of centralized procurement;
- corporate approval;
- risk committee;
- centralized treasury;
- energy procurement;
- power hedging policies;
- enterprise risk management.

Prediction:

For high-alpha electricity firms, the centralization response should be stronger than in lower-alpha exposed firms.

### 4. Hedging And Risk Infrastructure

This likely requires 10-K text or derivative footnote data.

Outcomes:

- electricity/power derivative mentions;
- notional or fair value of commodity/power derivatives;
- hedge accounting discussion;
- risk-management committee or centralized treasury mentions.

Prediction:

Residual hedging and risk-infrastructure intensity should increase more for high-alpha treated firms.

## Alpha Moderator

Estimate alpha from pre-event operating sensitivity:

```text
OperatingMargin_i,t = a_i + b_i PowerPriceShock_region,t + controls + error_i,t
Alpha_i,k = abs(b_i)
```

Preferred operating performance:

```text
segment operating margin = ops / sales
```

Use only pre-event years. For region-specific shocks, use hub prices where available:

- Palo Verde price index for Palo Verde event;
- COB price index for COB event;
- PJM price index for PJM event;
- Cinergy/Entergy hub prices for 1998 events.

If hub price histories are unavailable at first, use EIA regional wholesale electricity price series or state-level retail/industrial electricity prices as a fallback, clearly labeled as weaker.

## Empirical Specifications

### Stacked Event Study

Build one dataset per event, then stack.

```text
Y_i,t,k = sum_l beta_l * Treated_i,k * 1[EventTime_t,k = l]
        + firm-event FE
        + calendar-year FE
        + event FE
        + controls
        + error_i,t,k
```

Use event windows such as `[-5, +5]` and `[-10, +10]`.

### Difference-in-Differences Baseline

```text
Y_i,t,k = beta * Treated_i,k * Post_t,k
        + firm-event FE
        + year FE
        + event FE
        + controls
        + error_i,t,k
```

### Triple Difference With Alpha

```text
Y_i,t,k = beta1 * Treated_i,k * Post_t,k
        + beta2 * Treated_i,k * Post_t,k * Alpha_i,k
        + firm-event FE
        + year FE
        + event FE
        + controls
        + error_i,t,k
```

Expected signs:

- information/risk-infrastructure outcomes: `beta1 > 0`, `beta2 > 0`;
- decentralization outcomes: `beta2 < 0` if high-alpha firms centralize relative to low-alpha firms;
- capital-allocation sensitivity: stronger post-shock allocation-performance sensitivity for high-alpha firms.

## Validation Tests

Before interpreting organizational outcomes, show that treatment captures hedgeability.

1. Treated firms increase power/electricity derivative disclosures after launch.
2. Treated firms mention power price risk or electricity procurement more after launch.
3. Treated firms' operating margins become less sensitive to power price shocks after launch, if hedging is effective.
4. No similar change occurs in placebo regions or placebo years.

## Required Data Additions

Minimum additions:

- firm headquarters state from Compustat company file;
- electricity hub/ISO/RTO region crosswalk;
- power price series by hub or region;
- firm-level Compustat controls.

High-value additions:

- EIA Form 861 service territory/utility data;
- EIA Form 860 generator ownership/operator data;
- 10-K text for power derivative and centralization language;
- derivative footnote data if available.

## First-Pass Feasibility From Current Segment Data

The current BUSSEG file has workable coverage for electric/utility SIC proxies.

| Event window | Firm-years | Alpha-ready share |
| --- | ---: | ---: |
| 1996 COB/Palo Verde, pre-1991-1995 | 1,858 | 99.5% |
| 1999 PJM, pre-1994-1998 | 1,815 | 97.5% |
| 2012 CME gas/power suite, pre-2007-2011 | 1,744 | 69.7% |
| 2026 PJM expansion, pre-2021-2025 | 1,270 | 68.7% |

The 2026 event is useful for motivation but cannot yet support post-period outcome tests with the current data.

## Proposed Execution Order

1. Build clean BUSSEG electric segment-year panel.
2. Create electric exposure shares using pre-event BUSSEG sales.
3. Add headquarters-state region mapping as a temporary treatment screen.
4. Produce event-level treated/control counts for 1996, 1998, 1999, and 2012.
5. Run pre-trend plots for segment reporting granularity and capital allocation outcomes.
6. Add better region mapping from EIA/FERC/ISO data.
7. Estimate stacked event-study and DID models.
8. Add alpha moderator.
9. Add 10-K text/derivative disclosure validation.

## Main Risks

1. Electricity restructuring may confound the derivative launch effect.
2. Headquarters state may misclassify firm exposure if operations are geographically dispersed.
3. Electricity firms may already have bilateral hedging or long-term power contracts before exchange-traded futures.
4. Utility regulation can mute operating-margin responses.
5. Segment recasts and source-date duplicates must be handled consistently.

## Bottom Line

Electricity is a strong empirical setting for the theory, especially for the high-alpha centralization channel. The agenda should begin with 1996-1999 regional power futures as the historical core and use the 2012 CME power-market expansion for modern relevance. The crucial next step is not more segment profiling; it is building a credible region-treatment crosswalk.
