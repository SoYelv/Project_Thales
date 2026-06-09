#!/usr/bin/env python3
"""Shared electricity-shock identification and RSZ helpers.

The default early-shock mapping is intentionally narrow. It treats headquarters
state as a proxy for hub exposure only when the state is directly tied to the
named NYMEX electricity futures hub or its core operating footprint.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS


EARLY_EVENTS = (1996, 1998, 1999)


@dataclass(frozen=True)
class ShockDef:
    name: str
    year: int
    states: frozenset[str]
    note: str


STRICT_EARLY_SHOCKS = (
    ShockDef(
        "COB/Palo Verde",
        1996,
        frozenset({"CA", "OR", "WA", "AZ", "NV"}),
        "Direct western hub states for the initial COB and Palo Verde contracts.",
    ),
    ShockDef(
        "Cinergy/Entergy",
        1998,
        frozenset({"OH", "IN", "KY", "AR", "LA", "MS"}),
        "Core Cinergy states plus core Entergy Gulf/South states.",
    ),
    ShockDef(
        "PJM",
        1999,
        frozenset({"PA", "NJ", "MD", "DE", "DC"}),
        "Original Mid-Atlantic PJM footprint proxy.",
    ),
)


LEGACY_BROAD_SHOCKS = (
    ShockDef("Western broad", 1996, frozenset({"CA", "OR", "WA", "NV", "AZ", "NM", "UT", "ID", "MT", "WY", "CO", "AK", "HI"}), ""),
    ShockDef("Midwest broad", 1998, frozenset({"OH", "IN", "KY", "IL", "MI", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"}), ""),
    ShockDef("South broad", 1998, frozenset({"AR", "LA", "MS", "TX", "OK", "AL", "TN", "GA", "FL", "SC", "NC"}), ""),
    ShockDef("PJM broad", 1999, frozenset({"PA", "NJ", "MD", "DE", "VA", "DC", "WV"}), ""),
)


def _assign_from_defs(state: object, shocks: tuple[ShockDef, ...]) -> tuple[str, float]:
    if pd.isna(state):
        return "Other/untreated", np.nan
    state = str(state).upper()
    for shock in shocks:
        if state in shock.states:
            return shock.name, float(shock.year)
    return "Other/untreated", np.nan


def add_early_shock_columns(company: pd.DataFrame) -> pd.DataFrame:
    out = company[["gvkey", "state"]].copy()
    strict = pd.DataFrame(
        out["state"].map(lambda state: _assign_from_defs(state, STRICT_EARLY_SHOCKS)).tolist(),
        index=out.index,
        columns=["region", "event_year"],
    )
    legacy = pd.DataFrame(
        out["state"].map(lambda state: _assign_from_defs(state, LEGACY_BROAD_SHOCKS)).tolist(),
        index=out.index,
        columns=["legacy_region", "legacy_event_year"],
    )
    out = pd.concat([out, strict, legacy], axis=1)
    out["id_tier"] = np.where(out["event_year"].notna(), "strict_hub_state", "untreated_or_not_mapped")
    return out


def add_sgrow(g: pd.DataFrame) -> pd.DataFrame:
    out = g.copy()
    out["sgrow"] = np.where(out["l_sales"].abs() > 0, out["sales"] / out["l_sales"] - 1, np.nan)
    return out


def winsorize_in_place(df: pd.DataFrame, cols: list[str], lo: float = 0.01, hi: float = 0.99) -> None:
    for col in cols:
        qlo, qhi = df[col].quantile(lo), df[col].quantile(hi)
        df[col] = df[col].clip(qlo, qhi)


def stacked_rsz_sample(
    g: pd.DataFrame,
    fe: pd.DataFrame,
    oppcol: str,
    *,
    events: tuple[int, ...] = EARLY_EVENTS,
    control: str = "notyet",
    window: tuple[int, int] = (-5, 5),
    sample: str = "all_multiseg",
    winsorize: bool = True,
) -> pd.DataFrame:
    """Build one consistent stacked RSZ sample.

    sample:
      all_multiseg: firm-year must have at least two operating segments.
      pre_multiseg: firm must have at least one multi-segment pre-period year
                    inside each cohort window.
    """
    if control not in {"notyet", "never"}:
        raise ValueError("control must be 'notyet' or 'never'")
    if sample not in {"all_multiseg", "pre_multiseg"}:
        raise ValueError("sample must be 'all_multiseg' or 'pre_multiseg'")

    gg = g.copy()
    gg["inv_la"] = gg["inv_la"].replace([np.inf, -np.inf], np.nan)
    gg[oppcol] = gg[oppcol].replace([np.inf, -np.inf], np.nan)
    lo, hi = window
    parts: list[pd.DataFrame] = []
    for event_year in events:
        treated = set(fe.loc[fe.event_year.eq(event_year), "gvkey"])
        if control == "notyet":
            controls = set(fe.loc[fe.event_year.gt(event_year) | fe.event_year.isna(), "gvkey"])
        else:
            controls = set(fe.loc[fe.event_year.isna(), "gvkey"])
        firms = treated | controls
        d = gg[
            gg.year.between(event_year + lo, event_year + hi)
            & gg.gvkey.isin(firms)
        ].copy()
        if sample == "pre_multiseg":
            pre = gg[
                gg.year.between(event_year + lo, event_year - 1)
                & gg.gvkey.isin(firms)
            ]
            keep = set(pre.groupby("gvkey")["n_seg_fy"].max().loc[lambda x: x >= 2].index)
            d = d[d.gvkey.isin(keep)]
        d = d[d.n_seg_fy >= 2].copy()
        d["cohort"] = event_year
        d["treat"] = d.gvkey.isin(treated).astype(int)
        d["post"] = (d.year >= event_year).astype(int)
        d["k"] = d.year - event_year
        parts.append(d)

    s = pd.concat(parts, ignore_index=True)
    s = s.dropna(subset=["inv_la", oppcol]).copy()
    if winsorize:
        winsorize_in_place(s, ["inv_la", oppcol])
    obs_per_firmyear = s.groupby(["cohort", "gvkey", "year"])["snms_u"].transform("nunique")
    s = s[obs_per_firmyear >= 2].copy()
    s["rel_inv"] = s["inv_la"] - s.groupby(["cohort", "gvkey", "year"])["inv_la"].transform("mean")
    s["rel_opp"] = s[oppcol] - s.groupby(["cohort", "gvkey", "year"])[oppcol].transform("mean")
    s["segid"] = s.gvkey + "_" + s.snms_u
    s["cseg"] = s.cohort.astype(str) + "_" + s.segid
    s["cy"] = s.cohort.astype(str) + "_" + s.year.astype(str)
    return s


def fit_rsz(s: pd.DataFrame, *, alpha_mod: bool = False):
    d = s.copy()
    d["ro"] = d.rel_opp
    d["rop"] = d.ro * d.post
    d["rot"] = d.ro * d.treat
    d["rotp"] = d.ro * d.treat * d.post
    cols = ["ro", "rop", "rot", "rotp"]
    if alpha_mod:
        d["a"] = d["alpha"].fillna(0.0)
        d["roa"] = d.ro * d.a
        d["ropa"] = d.rop * d.a
        d["rota"] = d.rot * d.a
        d["rotpa"] = d.rotp * d.a
        cols += ["roa", "ropa", "rota", "rotpa"]
    cy = pd.get_dummies(d.cy, prefix="cy", drop_first=True).astype(float)
    idx = pd.MultiIndex.from_arrays([d.cseg.values, d.year.values])
    x = pd.concat([d[cols].reset_index(drop=True), cy.reset_index(drop=True)], axis=1)
    x.index = idx
    y = pd.Series(d.rel_inv.values, index=idx)
    clusters = pd.DataFrame({"firm": d.gvkey.values}, index=idx)
    return PanelOLS(y, x, entity_effects=True, check_rank=False, drop_absorbed=True).fit(
        cov_type="clustered", clusters=clusters
    )


def fit_rsz_event_study(s: pd.DataFrame, *, min_k: int = -5, max_k: int = 5, ref_k: int = -1):
    d = s.copy()
    for k in range(min_k, max_k + 1):
        if k == ref_k:
            continue
        d[f"s{k}"] = d.rel_opp * d.treat * d.k.eq(k).astype(int)
        d[f"r{k}"] = d.rel_opp * d.k.eq(k).astype(int)
    svars = [f"s{k}" for k in range(min_k, max_k + 1) if k != ref_k]
    rvars = [f"r{k}" for k in range(min_k, max_k + 1) if k != ref_k]
    d["rot"] = d.rel_opp * d.treat
    cy = pd.get_dummies(d.cy, prefix="cy", drop_first=True).astype(float)
    idx = pd.MultiIndex.from_arrays([d.cseg.values, d.year.values])
    x = pd.concat([d[svars + rvars + ["rot"]].reset_index(drop=True), cy.reset_index(drop=True)], axis=1)
    x.index = idx
    y = pd.Series(d.rel_inv.values, index=idx)
    clusters = pd.DataFrame({"firm": d.gvkey.values}, index=idx)
    return PanelOLS(y, x, entity_effects=True, check_rank=False, drop_absorbed=True).fit(
        cov_type="clustered", clusters=clusters
    )
