#!/usr/bin/env python3
"""Build figures for the segment project-space reports from generated CSVs."""

from __future__ import annotations

import numpy as np
import textwrap

from segment_project_common import FIG_DIR, ROOT, read_table, utc_now, write_json

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:  # pragma: no cover - matplotlib is available locally
    plt = None

try:
    import seaborn as sns
except ModuleNotFoundError:
    sns = None


def make_figures() -> list:
    if plt is None:
        return []
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for obsolete in [FIG_DIR / "candidate_shock_windows_by_type.png"]:
        if obsolete.exists():
            obsolete.unlink()
    paths = []

    design = read_table("segment_project_design_readiness.csv")
    family = read_table("segment_project_exposure_family_readiness.csv")
    geodecade = read_table("segment_project_geography_decade_readiness.csv")
    shock_catalog = read_table("segment_project_candidate_shock_catalog.csv")

    if sns is not None:
        sns.set_theme(style="whitegrid")
    else:
        plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.25})

    pivot = (
        design[design["design"].isin(["Segment operating margin", "RSZ capital allocation", "Employment allocation", "R&D allocation"])]
        .pivot_table(index="stype", columns="design", values="ready_pct", aggfunc="max")
        .fillna(0)
    )
    fig, ax = plt.subplots(figsize=(9, 4.8))
    if sns is not None:
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "Ready rows (%)"}, ax=ax)
    else:
        im = ax.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), labels=pivot.columns, rotation=30, ha="right")
        ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                ax.text(j, i, f"{pivot.iloc[i, j]:.1f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, label="Ready rows (%)")
    ax.set_title("Outcome readiness by segment type")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    path = FIG_DIR / "outcome_readiness_by_stype.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(path)

    top_family = family.head(10).copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = top_family["exposure_family"].str.replace("_", " ")
    y = np.arange(len(top_family))
    ax.barh(y, top_family["firm_years"], color="#3c7d8f")
    ax.set_yticks(y, labels=labels)
    ax.invert_yaxis()
    ax.set_xlabel("Firm-years")
    ax.set_title("Industry exposure families available in BUSSEG/OPSEG")
    for idx, value in enumerate(top_family["allocation_ready_pct"]):
        ax.text(top_family["firm_years"].iloc[idx], idx, f"  alloc {value:.1f}%", va="center", fontsize=8)
    fig.tight_layout()
    path = FIG_DIR / "industry_family_sample.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(path)

    if len(geodecade):
        fig, ax = plt.subplots(figsize=(8.5, 4.6))
        x = np.arange(len(geodecade))
        ax.plot(x, geodecade["has_source_currency_pct"], marker="o", label="Source currency present")
        ax.plot(x, geodecade["margin_ready_pct"], marker="o", label="Margin ready")
        ax.plot(x, geodecade["allocation_ready_pct"], marker="o", label="Allocation ready")
        ax.set_xticks(x, labels=geodecade["decade"])
        ax.set_ylabel("Rows (%)")
        ax.set_title("Geographic segment feasibility by decade")
        ax.legend()
        fig.tight_layout()
        path = FIG_DIR / "geographic_feasibility_by_decade.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)

    plot = shock_catalog.sort_values(["event_anchor_year", "shock_family", "shock_id"]).copy()
    plot["display_label"] = plot["shock_family"].apply(lambda value: "\n".join(textwrap.wrap(str(value), 42)))
    height = max(9.0, 0.34 * len(plot) + 2.2)
    fig, ax = plt.subplots(figsize=(11, height))
    y = np.arange(len(plot))
    ax.scatter(
        plot["event_anchor_year"],
        y,
        s=70,
        color="#A3D576",
        edgecolor="#386411",
        linewidth=0.8,
        zorder=3,
    )
    for idx, row in enumerate(plot.itertuples(index=False)):
        ax.text(
            int(row.event_anchor_year) + 0.35,
            idx,
            str(row.candidate_window),
            va="center",
            fontsize=8.5,
            color="#464C55",
        )
    ax.set_yticks(y, labels=plot["display_label"])
    ax.invert_yaxis()
    ax.set_xlabel("Anchor year")
    ax.set_ylabel("")
    ax.set_xlim(int(plot["event_anchor_year"].min()) - 2, int(plot["event_anchor_year"].max()) + 7)
    ax.grid(axis="x", color="#E6E8F0", linewidth=0.8)
    ax.grid(axis="y", color="#F4F5F7", linewidth=0.5)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#D7DBE7")
    ax.spines["bottom"].set_color("#D7DBE7")
    fig.suptitle("Candidate shock windows by specific shock", x=0.40, ha="left", y=0.985, fontsize=16)
    fig.text(
        0.40,
        0.955,
        "Marker = anchor year; label = candidate window.",
        ha="left",
        va="top",
        fontsize=10,
        color="#6F768A",
    )
    fig.subplots_adjust(left=0.40, right=0.97, top=0.92, bottom=0.07)
    path = FIG_DIR / "candidate_shock_windows_by_shock.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(path)

    return paths


def main() -> None:
    generated_at = utc_now()
    paths = make_figures()
    qa = {
        "generated_at_utc": generated_at,
        "figures_written": [str(path.relative_to(ROOT)) for path in paths],
        "figure_count": len(paths),
        "notes": ["Figures are generated from CSV artifacts under reports/segment_project_space/tables."],
    }
    write_json(qa, "segment_project_figures_qa.json")
    for path in paths:
        print(f"wrote {path.relative_to(ROOT)}")
    print("wrote reports/segment_project_space/segment_project_figures_qa.json")


if __name__ == "__main__":
    main()
