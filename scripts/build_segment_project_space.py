#!/usr/bin/env python3
"""Run the full segment project-space report pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "scripts/build_segment_project_data_profile.py",
    "scripts/build_segment_project_exposure_profile.py",
    "scripts/build_segment_project_geography_profile.py",
    "scripts/build_segment_project_shock_catalog.py",
    "scripts/build_segment_project_event_readiness.py",
    "scripts/build_segment_project_workstreams.py",
    "scripts/build_segment_project_figures.py",
    "scripts/render_segment_project_space_reports.py",
    "scripts/check_segment_project_space_reports.py",
]


def run_step(script: str) -> None:
    print(f"==> {script}", flush=True)
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def main() -> None:
    for script in STEPS:
        run_step(script)


if __name__ == "__main__":
    main()
