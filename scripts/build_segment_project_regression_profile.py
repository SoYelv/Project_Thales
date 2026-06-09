#!/usr/bin/env python3
"""Build method and result tables for the regression-results report tab."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from segment_project_common import ROOT, read_existing_csv, utc_now, write_json, write_table


RESULT_SPECS = [
    {
        "result_id": "strict_early_electricity",
        "path": ROOT / "reports" / "tables" / "t1_strict_identification_results.csv",
        "table_role": "Strict early electricity producer-side RSZ result table.",
        "source_script": "Exact CSV writer not located by current script search; schema matches scripts/electricity_identification.py stacked RSZ helpers.",
    },
    {
        "result_id": "output_input_electricity",
        "path": ROOT / "reports" / "tables" / "electricity_output_input_rsz_results.csv",
        "table_role": "Early electricity RSZ result table split into output-producer and input-user mechanism groups.",
        "source_script": "scripts/run_electricity_output_input_rsz.py",
    },
    {
        "result_id": "modern_electricity",
        "path": ROOT / "reports" / "tables" / "electricity_output_input_modern_rsz_results.csv",
        "table_role": "Modern regional, EIM, and exploratory national-break electricity RSZ result table.",
        "source_script": "scripts/run_electricity_output_input_modern_rsz.py",
    },
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def result_manifest() -> pd.DataFrame:
    rows = []
    for spec in RESULT_SPECS:
        df = read_existing_csv(spec["path"])
        rows.append(
            {
                "result_id": spec["result_id"],
                "table_role": spec["table_role"],
                "path": rel(spec["path"]),
                "source_script": spec["source_script"],
                "status": "present" if spec["path"].exists() else "missing",
                "rows": int(len(df)) if not df.empty else 0,
                "columns": "; ".join(df.columns.astype(str)) if not df.empty else "",
            }
        )
    return pd.DataFrame(rows)


def outcome_definitions() -> pd.DataFrame:
    rows = [
        (
            "analysis_unit",
            "Segment-year row inside a stacked firm-event-year panel.",
            "The core panel is built from BUSSEG operating segments, grouped to gvkey, normalized segment name, and year before estimation.",
            "scripts/build_panel.py; scripts/build_intensity.py; scripts/electricity_identification.py",
        ),
        (
            "inv_la",
            "Segment investment intensity.",
            "Constructed as current segment capital expenditures divided by lagged segment identifiable assets: capxs / lagged ias.",
            "scripts/build_intensity.py",
        ),
        (
            "rel_inv",
            "Regression outcome variable.",
            "The segment's inv_la minus the mean inv_la across segments in the same cohort, firm, and year. This makes the outcome a within-firm allocation measure.",
            "scripts/electricity_identification.py; scripts/run_electricity_output_input_modern_rsz.py",
        ),
        (
            "l_margin",
            "Lagged segment operating margin opportunity measure.",
            "Lagged operating profit divided by lagged sales: lagged ops / lagged sales. In the regression it is demeaned within cohort, firm, and year as rel_opp.",
            "scripts/build_intensity.py; scripts/electricity_identification.py",
        ),
        (
            "sgrow",
            "Segment sales-growth opportunity measure.",
            "Current segment sales divided by lagged segment sales minus one: sales / lagged sales - 1. In the regression it is demeaned within cohort, firm, and year as rel_opp.",
            "scripts/build_intensity.py; scripts/electricity_identification.py",
        ),
        (
            "rel_opp",
            "Within-firm relative opportunity measure.",
            "The chosen opportunity variable minus the mean opportunity value across segments in the same cohort, firm, and year.",
            "scripts/electricity_identification.py; scripts/run_electricity_output_input_modern_rsz.py",
        ),
        (
            "coef",
            "Reported treatment coefficient.",
            "Coefficient on rel_opp x treated x post. It measures whether treated firms reallocate investment more or less toward high-opportunity segments after the event.",
            "reports/tables/*rsz*_results.csv",
        ),
        (
            "sample_all_multiseg",
            "All-multisegment estimation sample.",
            "The stacked sample keeps firm-years with at least two segment observations after required outcome/opportunity fields are present.",
            "scripts/electricity_identification.py",
        ),
        (
            "sample_pre_multiseg",
            "Pre-multisegment estimation sample.",
            "The stacked sample additionally requires the firm to have at least one multisegment pre-period year inside the cohort window.",
            "scripts/electricity_identification.py",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=["term", "plain_english_definition", "construction_rule", "source"],
    )


def specification_definitions() -> pd.DataFrame:
    rows = [
        {
            "specification": "strict_early_electricity",
            "result_table": "reports/tables/t1_strict_identification_results.csv",
            "shock_or_design": "Stacked early electricity hub events in 1996, 1998, and 1999.",
            "treated_group": "Electricity-output firms assigned to the event year by strict headquarters-state hub mapping.",
            "control_group": "Not-yet-treated and never-treated electricity firms where the result row reports control=notyet.",
            "window": "Event year minus five through event year plus five.",
            "outcome": "rel_inv = segment capx / lagged assets, demeaned within cohort-firm-year.",
            "key_interaction": "rel_opp x treat x post.",
            "fixed_effects_and_errors": "Cohort-segment fixed effects, cohort-year indicators, and firm-clustered standard errors in the shared RSZ helpers.",
            "notes": "This table is retained as existing evidence; exact CSV writer was not located by current filename search.",
        },
        {
            "specification": "output_input_electricity",
            "result_table": "reports/tables/electricity_output_input_rsz_results.csv",
            "shock_or_design": "Same strict early electricity hub-event structure, split by output/input mechanism group.",
            "treated_group": "One mechanism group at a time: output_producer, input_manufacturing_high, input_manufacturing_very_high, or input_industrial_high.",
            "control_group": "Not-yet-treated and never-treated firms within the mechanism group.",
            "window": "Event year minus five through event year plus five.",
            "outcome": "rel_inv = segment capx / lagged assets, demeaned within cohort-firm-year.",
            "key_interaction": "rel_opp x treat x post.",
            "fixed_effects_and_errors": "Cohort-segment fixed effects, cohort-year indicators, and firm-clustered standard errors.",
            "notes": "Rows are estimated separately for l_margin and sgrow, and for all_multiseg and pre_multiseg samples.",
        },
        {
            "specification": "modern_regional_and_eim",
            "result_table": "reports/tables/electricity_output_input_modern_rsz_results.csv",
            "shock_or_design": "Modern regional and Western EIM staggered electricity event screens.",
            "treated_group": "Mechanism-group firms assigned to each modern event year.",
            "control_group": "Not-yet-treated or never-treated firms within the same mechanism group.",
            "window": "Event year minus five through event year plus five.",
            "outcome": "rel_inv = segment capx / lagged assets, demeaned within cohort-firm-year.",
            "key_interaction": "rel_opp x T x post, reported as coef.",
            "fixed_effects_and_errors": "Cohort-segment fixed effects, cohort-year indicators, and firm-clustered standard errors.",
            "notes": "post_lag is one in the current modern regional and EIM rows.",
        },
        {
            "specification": "exploratory_national_break",
            "result_table": "reports/tables/electricity_output_input_modern_rsz_results.csv",
            "shock_or_design": "NODAL_EXCHANGE_2009 and CME_POWER_EXPANSION_2012 period-break screens.",
            "treated_group": "The mechanism group being screened.",
            "control_group": "Other multisegment firms not in the same mechanism group.",
            "window": "2004-2014 for NODAL_EXCHANGE_2009; 2007-2017 for CME_POWER_EXPANSION_2012.",
            "outcome": "rel_inv = segment capx / lagged assets, demeaned within cohort-firm-year.",
            "key_interaction": "rel_opp x T x post, reported as coef.",
            "fixed_effects_and_errors": "Cohort-segment fixed effects, cohort-year indicators, and firm-clustered standard errors.",
            "notes": "These rows are period-break screens rather than clean regional treated/control designs.",
        },
    ]
    return pd.DataFrame(rows)


def normalize_results() -> pd.DataFrame:
    rows = []
    for spec in RESULT_SPECS:
        df = read_existing_csv(spec["path"])
        if df.empty:
            continue
        work = df.copy()
        work["result_id"] = spec["result_id"]
        if "design" not in work.columns:
            work["design"] = "strict_early"
        if "shock" not in work.columns:
            work["shock"] = "stacked_1996_1998_1999"
        if "mechanism_group" not in work.columns:
            work["mechanism_group"] = np.where(
                work["result_id"].eq("strict_early_electricity"),
                "output_producer",
                "",
            )
        if "status" not in work.columns:
            work["status"] = "ok"
        if "post_lag" not in work.columns:
            work["post_lag"] = 0
        if "firms_in_estimation" not in work.columns and "firms" in work.columns:
            work["firms_in_estimation"] = work["firms"]
        if "treated_firms_in_stack" not in work.columns:
            work["treated_firms_in_stack"] = np.nan
        if "control_firms_in_stack" not in work.columns:
            work["control_firms_in_stack"] = np.nan
        if "control" not in work.columns:
            work["control"] = ""
        for col in ["coef", "se", "t", "p", "nobs", "firms_in_estimation"]:
            if col not in work.columns:
                work[col] = np.nan
        rows.append(work)

    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True, sort=False)
    keep = [
        "result_id",
        "design",
        "shock",
        "mechanism_group",
        "sample",
        "opportunity",
        "post_lag",
        "control",
        "status",
        "coef",
        "se",
        "t",
        "p",
        "nobs",
        "firms_in_estimation",
        "treated_firms_in_stack",
        "control_firms_in_stack",
    ]
    return out[[col for col in keep if col in out.columns]].sort_values(
        ["result_id", "design", "shock", "mechanism_group", "sample", "opportunity"],
        na_position="last",
    )


def result_summary(compact: pd.DataFrame) -> pd.DataFrame:
    if compact.empty:
        return pd.DataFrame()
    rows = []
    for (result_id, design, mechanism_group, opportunity), part in compact.groupby(
        ["result_id", "design", "mechanism_group", "opportunity"], dropna=False
    ):
        ok = part[part["status"].eq("ok")].copy()
        rows.append(
            {
                "result_id": result_id,
                "design": design,
                "mechanism_group": mechanism_group,
                "opportunity": opportunity,
                "result_rows": int(len(part)),
                "ok_rows": int(len(ok)),
                "min_coef": float(ok["coef"].min()) if len(ok) else np.nan,
                "median_coef": float(ok["coef"].median()) if len(ok) else np.nan,
                "max_coef": float(ok["coef"].max()) if len(ok) else np.nan,
                "min_p": float(ok["p"].min()) if len(ok) else np.nan,
                "max_nobs": int(ok["nobs"].max()) if len(ok) and ok["nobs"].notna().any() else np.nan,
                "max_firms": int(ok["firms_in_estimation"].max())
                if len(ok) and ok["firms_in_estimation"].notna().any()
                else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["result_id", "design", "mechanism_group", "opportunity"])


def main() -> None:
    generated_at = utc_now()
    manifest = result_manifest()
    outcomes = outcome_definitions()
    specs = specification_definitions()
    compact = normalize_results()
    summary = result_summary(compact)

    outputs = [
        write_table(manifest, "segment_project_regression_result_manifest.csv"),
        write_table(outcomes, "segment_project_regression_outcome_definitions.csv"),
        write_table(specs, "segment_project_regression_specifications.csv"),
        write_table(compact, "segment_project_regression_results_compact.csv"),
        write_table(summary, "segment_project_regression_result_summary.csv"),
    ]
    qa = {
        "generated_at_utc": generated_at,
        "result_tables_present": int(manifest["status"].eq("present").sum()),
        "result_tables_missing": int(manifest["status"].eq("missing").sum()),
        "compact_result_rows": int(len(compact)),
        "summary_rows": int(len(summary)),
        "tables_written": [rel(path) for path in outputs],
        "notes": [
            "Regression profile tables document existing result CSVs; this script does not re-estimate models.",
            "The reported coefficient is the RSZ allocation-sensitivity interaction, not a treatment effect on investment levels.",
        ],
    }
    write_json(qa, "segment_project_regression_profile_qa.json")
    for path in outputs:
        print(f"wrote {rel(path)}")
    print("wrote reports/segment_project_space/segment_project_regression_profile_qa.json")


if __name__ == "__main__":
    main()
