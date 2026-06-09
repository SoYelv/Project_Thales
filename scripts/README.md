# Scripts

Use `../docs/pipeline_map.md` as the main orientation document.

## Build Scripts

- `electricity_identification.py`
- `explore_segment_data.py`
- `build_segment_project_space.py`
- `explore_segment_project_space.py` (compatibility wrapper for `build_segment_project_space.py`)
- `segment_project_common.py`
- `segment_project_definitions.py`
- `build_segment_project_data_profile.py`
- `build_segment_project_exposure_profile.py`
- `build_segment_project_geography_profile.py`
- `build_segment_project_shock_catalog.py`
- `build_segment_project_event_readiness.py`
- `build_segment_project_workstreams.py`
- `build_segment_project_figures.py`
- `render_segment_project_space_reports.py`
- `check_segment_project_space_reports.py`
- `build_panel.py`
- `build_firmyear.py`
- `build_regdata.py`
- `build_alpha.py`
- `build_t1.py`
- `build_intensity.py`
- `build_electricity_mechanism_groups.py`
- `pull_wrds.py`
- `pull_revelio.py`
- `pull_revelio_roles.py`

## Analysis And Trial Scripts

- `final_results.py`
- `run_combos.py`
- `run_combos2.py`
- `run_modern.py`
- `run_modern_robust.py`
- `run_modern_es.py`
- `run_t2_modern.py`
- `run_electricity_output_input_rsz.py`
- `run_electricity_output_input_modern_rsz.py`
- `run_t1_alloc.py`
- `run_t1_alloc2.py`
- `run_t1_premulti.py`
- `run_t2_labor.py`
- `run_t2_labor2.py`
- `run_t2_roles.py`
- `run_t2_es.py`
- `analysis.py`
- `event_study.py`
- `triplediff.py`
- `verify.py`
- `verify_t1.py`
- `seg_coverage.py`
- `identify_electricity_derivative_users.py`

Many analysis scripts print results rather than writing a dedicated output file. Promote a script by adding a short docstring and an explicit output path under `../reports/tables/` or a clearly named report bundle under `../reports/`.

The current electricity Track 1 scripts should use `electricity_identification.py` for shock mapping and RSZ sample construction. Older scripts that duplicate RSZ construction should be treated as diagnostics until migrated.

## Segment Project-Space Report Pipeline

Run the full coauthor briefing report bundle with:

```bash
python3 scripts/build_segment_project_space.py
```

The split pipeline writes generated tables under `../reports/segment_project_space/tables/`, figures under `../reports/segment_project_space/figures/`, and renders HTML only after the analysis artifacts exist. `render_segment_project_space_reports.py` reads generated CSV/PNG artifacts and does not load the raw segment file or recompute coverage.
