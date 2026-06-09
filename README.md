# Project Thales

This repository contains the current empirical workstream for the segment-data electricity/derivatives project. It was reorganized on 2026-06-03 to separate raw inputs, scripts, generated outputs, and notes without changing the existing analysis outputs.

The shareable repository is meant to show the research design, build scripts, QA summaries, and reader-facing memos. Licensed WRDS/Compustat and Revelio inputs, bulky local panels, and most generated CSV backing tables are intentionally kept out of git.

## Useful Starting Points

- `docs/pipeline_map.md`: current source, build, and analysis map.
- `docs/electricity_output_input_identification.md`: current electricity mechanism split, keeping producer and buyer tests separate.
- `reports/segment_project_space/segment_project_space_report.html`: generated feasibility report index for the segment-data project space.
- `reports/electricity_research_agenda.md`: advisor-facing electricity agenda.
- `reports/empirical_summary_report.md`: compact empirical status summary.
- `trials/energy_shocks/energy_shock_trial_memo.md`: trial-only evidence on oil, gas, and carbon/emissions shock candidates.

## Rendered Report Site

The collaborator-facing HTML bundle lives in `reports/segment_project_space/`. GitHub Pages is configured through `.github/workflows/pages.yml` to publish that directory as a static site when `main` changes.

After Pages is enabled for this repository, the rendered site should be available at:

```text
https://soyelv.github.io/Project_Thales/
```

## Layout

- `data/raw/`: immutable local source files. These are ignored by git.
- `docs/`: source notes, paper drafts, and project-level documentation.
- `scripts/`: reproducible build, analysis, validation, and exploratory scripts.
- `reports/panel/`: generated parquet intermediates used by downstream regressions. These are ignored by git.
- `reports/tables/`: generated CSV backing tables and small QA JSON outputs.
- `reports/*.md`: narrative memos and empirical summaries.
- `trials/energy_shocks/`: isolated screening runs for non-electricity energy shock candidates.

## Start Here

1. Read `docs/source_manifest.md` for source file size/hash inventory.
2. Read `docs/pipeline_map.md` for the current script map and rough run order.
3. Use `scripts/README.md` to distinguish build scripts from exploratory and trial runs.
4. Use `reports/README.md` to distinguish narrative reports from generated machine-readable outputs.

## Notes

- The large raw CSV lives locally at `data/raw/segment_data.csv` and is not tracked.
- `scripts/build_panel.py` and `scripts/explore_segment_data.py` now read the new raw-data path, with a fallback to the old root-level path.
- `reports/panel/` and `reports/tables/` were left in place because most scripts currently read and write those paths directly.
