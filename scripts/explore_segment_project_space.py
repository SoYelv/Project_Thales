#!/usr/bin/env python3
"""Compatibility wrapper for the split segment project-space pipeline.

The former monolithic exploration/report generator has been split into analysis
builders plus an artifact-only HTML renderer. Keep this entry point so existing
commands still rebuild the report bundle.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, "scripts/build_segment_project_space.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
