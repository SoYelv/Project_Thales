# Reports

This directory mixes narrative memos and generated machine-readable outputs.

- `panel/`: generated parquet intermediates read by the analysis scripts. This directory is ignored by git.
- `tables/`: generated CSV backing tables and small QA JSON outputs. Top-level CSVs are ignored by git.
- `segment_project_space/`: generated feasibility report series and backing bundle from `scripts/explore_segment_project_space.py`; this is small enough to keep as a browsable collaborator artifact. It now includes a separate regression-results tab with outcome and specification definitions.
- `segment_descriptives/`: generated source-descriptive tables from `scripts/build_segment_descriptive_tables.py`, including raw/latest-source row counts, segments-per-firm-year distributions, variable quartiles, and definitions.
- `*.md`: narrative memos and empirical summaries.

The `panel/` and `tables/` paths are intentionally left here for now because scripts read and write them directly.
