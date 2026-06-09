# Data

`raw/` contains local source files and is ignored by git. Treat these files as immutable inputs:

- Do not edit raw files by hand.
- Record file size and SHA-256 in `../docs/source_manifest.md` when adding or replacing a raw input.
- Write cleaned, joined, or modeled data to `../reports/panel/` unless the pipeline is intentionally refactored.
