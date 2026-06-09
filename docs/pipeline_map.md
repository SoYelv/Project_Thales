# Pipeline Map

This map reflects the current state of the scripts after the 2026-06-03 cleanup. It is descriptive, not a claim that every trial result is final.

## Source Inputs

- `data/raw/segment_data.csv`: main WRDS/Compustat segment file.
- WRDS pulls, when available, write `reports/panel/funda.parquet` and `reports/panel/company.parquet`.
- Revelio pulls, when available, write `reports/panel/revelio_*.parquet`.

## Build Layer

Run these when rebuilding the local panel from inputs:

1. `scripts/explore_segment_data.py`: profiles the raw segment file and writes `reports/segment_exploration.md` plus source/coverage CSVs in `reports/tables/`.
2. `scripts/explore_segment_project_space.py`: runs a broader feasibility exploration and writes `reports/segment_project_space/` with a linked HTML report series, QA manifest, figures, and backing tables.
3. `scripts/build_panel.py`: reads `data/raw/segment_data.csv` and writes `reports/panel/seg_busseg.parquet` and `reports/panel/firmyear.parquet`.
4. `scripts/pull_wrds.py`: pulls Compustat fundamentals/company metadata into `reports/panel/`. Requires WRDS access.
5. `scripts/build_regdata.py`: builds `reports/panel/regdata.parquet` from firm-year, fundamentals, and company metadata.
6. `scripts/build_alpha.py`: builds `reports/panel/alpha.parquet`.
7. `scripts/build_t1.py`: builds `reports/panel/seg_invest.parquet` and `reports/panel/firm_event.parquet`.
8. `scripts/build_intensity.py`: builds `reports/panel/seg_invest2.parquet` with electricity-input intensity fields.
9. `scripts/pull_revelio.py` and `scripts/pull_revelio_roles.py`: pull Revelio workforce/role panels. Require WRDS/Revelio access.

Electricity-shock identification details live in `docs/electricity_identification.md`. The current Track 1 baseline uses the strict hub-state mapping in `scripts/electricity_identification.py`; legacy broad mapping columns are retained only for robustness checks.

Output-vs-input electricity identification details live in
`docs/electricity_output_input_identification.md`. The mechanism split is built
by `scripts/build_electricity_mechanism_groups.py`.

## Analysis Layer

Current or recently promoted sweeps:

- `scripts/final_results.py`: writes `reports/tables/final_results.csv`.
- `scripts/run_combos.py`: treatment-by-shock capital-allocation matrix.
- `scripts/run_combos2.py`: sharpened electricity-input designs.
- `scripts/run_modern.py`: modern electricity shock sweep.
- `scripts/run_modern_robust.py`: robustness checks for the 2012 modern shock result.
- `scripts/run_modern_es.py`: event-study diagnostics for modern capital-allocation shocks.
- `scripts/run_t2_modern.py`: Revelio labor analyses around Nodal 2009 and CME 2012.
- `scripts/identify_electricity_derivative_users.py`: identifies non-power firms with plausible electricity-derivative demand from electricity-input intensity.
- `scripts/build_electricity_mechanism_groups.py`: builds mutually exclusive electricity-output and electricity-input firm-event groups.
- `scripts/run_electricity_output_input_rsz.py`: runs separated RSZ baselines for output and input groups.
- `scripts/run_electricity_output_input_modern_rsz.py`: runs 2000+/2010+ regional, EIM, and national-period-break screens by output/input group.

Diagnostics and earlier trial runs:

- `scripts/analysis.py`
- `scripts/event_study.py`
- `scripts/triplediff.py`
- `scripts/run_t1_alloc.py`
- `scripts/run_t1_alloc2.py`
- `scripts/run_t1_premulti.py`
- `scripts/run_t2_labor.py`
- `scripts/run_t2_labor2.py`
- `scripts/run_t2_roles.py`
- `scripts/run_t2_es.py`
- `scripts/verify.py`
- `scripts/verify_t1.py`
- `scripts/seg_coverage.py`

## Generated Outputs

- `reports/panel/*.parquet`: machine-readable intermediates.
- `reports/tables/*.csv`: backing tables for memos and empirical reports.
- `reports/segment_project_space/`: broad segment-data feasibility report series and backing bundle.
- `reports/*.md`: narrative reports. Some are exploratory snapshots; check modification dates and backing tables before treating one as final.
