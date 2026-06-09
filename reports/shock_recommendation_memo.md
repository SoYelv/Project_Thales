# Shock Recommendation Memo

Generated at UTC: 2026-06-01T01:50:00+00:00

## Recommendation

Start with energy commodity derivative availability, and use the 1990 NYMEX natural gas futures launch as the first concrete shock. Keep the March 1983 NYMEX WTI crude oil futures launch as the natural companion event or robustness check.

This is the best match between the proposal and the data currently in the project.

Launch-date checks: [CME Group describes NYMEX launching Light Sweet Crude Oil futures in March 1983](https://www.cmegroup.com/openmarkets/energy/2023/how-wti-became-the-most-important-commodity-contract-on-the-planet.html), and the [U.S. Energy Information Administration states that the first natural gas futures contracts began trading at NYMEX in 1990](https://www.eia.gov/todayinenergy/detail.php?id=62605).

## Why This Fits The Proposal

The proposal needs a derivative-availability shock that can be connected to:

1. pre-existing firm exposure;
2. segment operating performance, to estimate the alpha moderator;
3. segment investment or resource allocation, to test internal capital allocation and authority implications.

Energy commodity shocks satisfy those requirements better than the other candidate shock families in the current WRDS segment file.

## What The Data Says

The segment file has 2,843,285 raw rows, 30,000 firms, and 364,006 firm-years from 1976 to 2026. Because many historical segment-year records appear more than once with different `srcdate` values, the exploratory report also keeps a latest-source-date version by provisional segment key (`gvkey`, `datadate`, `stype`, `sid`).

In the latest-source-date view:

- `BUSSEG` has 674,184 rows, with `sales` non-missing for 99.0%, `ops` for 83.0%, `capxs` for 77.7%, and `ias` for 86.0%.
- `GEOSEG` has 757,202 rows, but `ops` is non-missing for only 25.4% and `capxs` for only 15.1%.
- Oil/gas and petroleum business/operating segments have 34,307 rows, 2,108 firms, and 21,722 firm-years, with `ops` non-missing for 86.0% and `capxs` for 90.4%.
- Utilities and power segments have 33,185 rows, 1,145 firms, and 16,965 firm-years, with `ops` non-missing for 78.4% and `capxs` for 87.0%.

Around the natural gas launch window, using oil/gas plus utilities as mechanical exposure groups:

- 1980-1989 pre-window: 8,830 firm-years; 99.2% alpha-ready (`sales` and `ops` non-missing); 96.2% allocation-ready (`sales`, `ops`, and `capxs` non-missing).
- 1985-1995 symmetric window: 9,213 firm-years; 98.9% alpha-ready; 96.0% allocation-ready.
- 1991-2000 post-window: 7,718 firm-years; 90.2% alpha-ready; 84.3% allocation-ready.

Around the WTI crude oil launch window, using oil/gas and petroleum:

- 1976-1982 observed pre-window: 3,289 firm-years; 96.6% alpha-ready; 88.0% allocation-ready.
- 1978-1988 symmetric window: 6,617 firm-years; 98.9% alpha-ready; 94.9% allocation-ready.
- 1984-1993 post-window: 5,603 firm-years; 98.7% alpha-ready; 95.2% allocation-ready.

## Why Not The Other Shock Families First

Currency is closest to the motivating example, but it is not the best first shock with this file alone. Geographic segments are plentiful, but the operating and investment variables needed for alpha and capital allocation are sparse. Also, usable geographic names and source-currency fields mainly appear after the late 1990s, while many major currency derivative launches predate the segment data.

Weather is theoretically attractive and connects to prior contracting work, but the current segment data is too geographically coarse for clean weather exposure. `STSEG` has only 2,331 latest-source-date rows and 73 firms, so state-level segment reporting cannot carry the design. Country/region `GEOSEG` rows are not enough for temperature or precipitation shocks without another location dataset.

Freight is feasible only as a narrow extension. Transport and freight segments are identifiable, but the treated universe is smaller than energy, and the derivative-launch mapping would need more external work before it is as clean as natural gas or WTI crude.

## Next Empirical Step

Build the first analysis panel from `BUSSEG` and `OPSEG`, keeping the latest `srcdate` per provisional segment key for the baseline. Exclude corporate, eliminations, other, no operations, and unallocated segments; construct segment operating margin (`ops / sales`), segment investment (`capxs / lagged ias` or `capxs / sales`), and firm-year segment granularity. Then classify exposed firms/segments using SIC/NAICS groups for oil/gas and utilities, and estimate pre-period sensitivity of segment operating margin to the relevant natural gas price shock to construct alpha.

The first research-design decision I would take to your advisor is:

> The current WRDS segment data supports an energy commodity derivative shock best. I recommend starting with the 1990 NYMEX natural gas futures launch, using WTI crude oil futures in 1983 as the companion event or robustness check.
