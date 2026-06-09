# Energy Shock Trials

This folder is intentionally separate from the production pipeline. It scans
oil, gas, and carbon/emissions shock candidates against existing project panels,
then writes only trial outputs under this directory.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 trials/energy_shocks/run_energy_shock_trials.py
```

Outputs:

- `energy_shock_all_specs.csv`: all estimated specifications.
- `energy_shock_robustness_summary.csv`: grouped robustness scores.
- `energy_shock_trial_qa.json`: inputs, sample counts, and definitions.
- `energy_shock_trial_summary.md`: reader-facing interpretation.
- `energy_shock_trial_memo.md`: concise human-written takeaways after the
  drilldown checks.

Identification status:

- Oil and gas derivative-availability shocks use existing project dates:
  WTI crude oil futures launch in 1983 and NYMEX natural gas futures launch in
  1990. FERC Order 636 in 1992 is included as a gas-market restructuring check.
- Additional exploratory non-derivative shocks include the 1986 oil price
  collapse, the 1995 SO2 allowance-market start, the 2001 gas price spike, and
  a 2005 EU ETS/high-carbon period proxy.
- Carbon shocks are exploratory because current panels do not observe plant
  emissions, allowance positions, or geographic segment emissions. RGGI 2009
  and California cap-and-trade 2013 are implemented with headquarters-state
  exposure and high-carbon segment SIC proxies.
