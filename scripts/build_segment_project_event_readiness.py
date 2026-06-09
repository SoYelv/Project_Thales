#!/usr/bin/env python3
"""Compute segment-data coverage around the candidate shock catalog."""

from __future__ import annotations

import pandas as pd

from segment_project_common import (
    EXPOSURE_FAMILIES,
    ROOT,
    latest_srcdate_view,
    load_segments,
    pct,
    read_table,
    utc_now,
    write_json,
    write_table,
)


def split_families(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]


def build_event_family_mapping(catalog: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in catalog.iterrows():
        for family in split_families(row["exposure_families"]):
            rows.append(
                {
                    "shock_id": row["shock_id"],
                    "shock_type": row["shock_type"],
                    "shock_family": row["shock_family"],
                    "event_anchor_year": row["event_anchor_year"],
                    "exposure_family": family,
                }
            )
    return pd.DataFrame(rows)


def event_window_readiness(df: pd.DataFrame, catalog: pd.DataFrame, windows: pd.DataFrame) -> pd.DataFrame:
    work = df[df["stype"].isin(["BUSSEG", "OPSEG"])].copy()
    rows = []
    for _, shock in catalog.iterrows():
        families = split_families(shock["exposure_families"])
        mask = pd.Series(False, index=work.index)
        for family in families:
            mask = mask | work[family].eq(1)
        exposed = work[mask]
        shock_windows = windows[windows["shock_id"].eq(shock["shock_id"])]
        for _, window in shock_windows.iterrows():
            part = exposed[exposed["year"].between(int(window["start_year"]), int(window["end_year"]))]
            margin = part[["sales", "ops"]].notna().all(axis=1) & part["sales"].ne(0)
            alloc = part[["sales", "ops", "capxs", "ias"]].notna().all(axis=1)
            rows.append(
                {
                    "shock_id": shock["shock_id"],
                    "shock_type": shock["shock_type"],
                    "shock_family": shock["shock_family"],
                    "candidate_window": shock["candidate_window"],
                    "event_anchor_year": int(shock["event_anchor_year"]),
                    "exposure_families": shock["exposure_families"],
                    "window": window["window"],
                    "start_year": int(window["start_year"]),
                    "end_year": int(window["end_year"]),
                    "rows": int(len(part)),
                    "firms": int(part["gvkey"].nunique(dropna=True)),
                    "firm_years": int(part[["gvkey", "datadate"]].drop_duplicates().shape[0]),
                    "margin_ready_pct": pct(margin),
                    "allocation_ready_pct": pct(alloc),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    generated_at = utc_now()
    catalog = read_table("segment_project_candidate_shock_catalog.csv")
    windows = read_table("segment_project_candidate_shock_windows.csv")
    mapping = build_event_family_mapping(catalog)
    unknown = sorted(set(mapping["exposure_family"]) - set(EXPOSURE_FAMILIES))
    if unknown:
        raise ValueError(f"Unknown exposure families in shock catalog: {unknown}")

    latest = latest_srcdate_view(load_segments())
    readiness = event_window_readiness(latest, catalog, windows)
    outputs = [
        write_table(mapping, "segment_project_event_family_mapping.csv"),
        write_table(readiness, "segment_project_event_window_readiness.csv"),
    ]
    qa = {
        "generated_at_utc": generated_at,
        "latest_srcdate_rows": int(len(latest)),
        "candidate_shock_count": int(len(catalog)),
        "event_window_rows": int(len(readiness)),
        "unknown_exposure_families": unknown,
        "tables_written": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Event-window readiness is a mechanical coverage screen around source-backed candidate windows.",
            "It does not assign treatment/control status.",
        ],
    }
    write_json(qa, "segment_project_event_readiness_qa.json")
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_event_readiness_qa.json")


if __name__ == "__main__":
    main()
