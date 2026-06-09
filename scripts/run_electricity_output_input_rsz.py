#!/usr/bin/env python3
"""RSZ baseline separately for electricity-output and electricity-input groups."""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from electricity_identification import add_sgrow, fit_rsz, stacked_rsz_sample

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "panel"
TABLES = ROOT / "reports" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

GROUPS = [
    ("output_producer", "electricity_output_firm"),
    ("input_manufacturing_high", "electricity_input_mfg_high"),
    ("input_manufacturing_very_high", "electricity_input_mfg_very_high"),
    ("input_industrial_high", "electricity_input_industrial_high"),
]


def run_group(g: pd.DataFrame, fe: pd.DataFrame, group_name: str, flag: str) -> list[dict[str, object]]:
    fe_group = fe[fe[flag]].drop_duplicates("gvkey").copy()
    g_group = g[g["gvkey"].isin(set(fe_group["gvkey"]))].copy()
    rows: list[dict[str, object]] = []
    if fe_group.empty:
        return rows
    for sample in ["all_multiseg", "pre_multiseg"]:
        for opp in ["l_margin", "sgrow"]:
            try:
                s = stacked_rsz_sample(
                    g_group,
                    fe_group[["gvkey", "event_year"]],
                    opp,
                    control="notyet",
                    window=(-5, 5),
                    sample=sample,
                )
                r = fit_rsz(s)
                rows.append(
                    {
                        "mechanism_group": group_name,
                        "sample": sample,
                        "opportunity": opp,
                        "coef": float(r.params["rotp"]),
                        "se": float(r.std_errors["rotp"]),
                        "t": float(r.tstats["rotp"]),
                        "p": float(r.pvalues["rotp"]),
                        "nobs": int(r.nobs),
                        "firms_in_estimation": int(s["gvkey"].nunique()),
                        "treated_firms_in_stack": int(s.loc[s["treat"].eq(1), "gvkey"].nunique()),
                        "control_firms_in_stack": int(s.loc[s["treat"].eq(0), "gvkey"].nunique()),
                        "status": "ok",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                rows.append(
                    {
                        "mechanism_group": group_name,
                        "sample": sample,
                        "opportunity": opp,
                        "coef": None,
                        "se": None,
                        "t": None,
                        "p": None,
                        "nobs": None,
                        "firms_in_estimation": None,
                        "treated_firms_in_stack": None,
                        "control_firms_in_stack": None,
                        "status": f"fit_error:{type(exc).__name__}",
                    }
                )
    return rows


def main() -> None:
    g = pd.read_parquet(PANEL / "seg_invest2.parquet")
    fe = pd.read_parquet(PANEL / "electricity_mechanism_firm_event.parquet")
    g = add_sgrow(g)

    rows: list[dict[str, object]] = []
    for group_name, flag in GROUPS:
        rows.extend(run_group(g, fe, group_name, flag))

    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "electricity_output_input_rsz_results.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
