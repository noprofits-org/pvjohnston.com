#!/usr/bin/env python3
"""Aggregate the H2+ fits and make the publication figure."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / "images" / "2026-07-18-where-coulomb-subtraction-helps-hero.png"

CONFIGURATIONS = {
    "primary": "Primary",
    "common-std": "Common target scale",
    "hidden-10": "10 hidden units",
    "hidden-20": "20 hidden units",
    "constant-count": "Constant point count",
    "lower-lr-long": "Longer, lower-rate fit",
    "qz-basis": "aug-cc-pVQZ",
    "log-input": "log R input",
}
RAW_R_CONTROLS = (
    "primary",
    "common-std",
    "hidden-10",
    "hidden-20",
    "constant-count",
    "lower-lr-long",
    "qz-basis",
)

INK = "#1a1d2b"
INDIGO = "#465c9b"
LIFTED = "#8fa5e3"
DEEP = "#2f417a"
CREAM = "#fbfaf6"
GRID = "#d9d5cc"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_summaries() -> dict[str, dict[float, dict[str, float]]]:
    summaries: dict[str, dict[float, dict[str, float]]] = {}
    rows: list[dict[str, object]] = []
    for tag, label in CONFIGURATIONS.items():
        payload = json.loads((HERE / f"summary-{tag}.json").read_text())
        summaries[tag] = {}
        for item in payload["cutoffs"]:
            cutoff = float(item["cutoff_bohr"])
            summaries[tag][cutoff] = item
            rows.append(
                {
                    "configuration": tag,
                    "label": label,
                    "cutoff_bohr": cutoff,
                    "median_A_rmse_cm-1": item["median_A_rmse_cm-1"],
                    "median_B_rmse_cm-1": item["median_B_rmse_cm-1"],
                    "median_A_over_B": item["median_A_over_B"],
                    "min_A_over_B": item["min_A_over_B"],
                    "max_A_over_B": item["max_A_over_B"],
                    "B_win_count": item["B_win_count"],
                    "A_win_count": item["A_win_count"],
                }
            )
    write_csv(HERE / "control-ratios.csv", rows)
    return summaries


def write_target_ranges(scan: list[dict[str, str]], cutoffs: list[float]) -> None:
    rows: list[dict[str, object]] = []
    r = np.asarray([float(row["r_bohr"]) for row in scan])
    total = np.asarray([float(row["total_hartree"]) for row in scan])
    electronic = np.asarray([float(row["electronic_hartree"]) for row in scan])
    for cutoff in cutoffs:
        keep = r >= cutoff
        rows.append(
            {
                "cutoff_bohr": cutoff,
                "n_points": int(np.sum(keep)),
                "total_range_hartree": float(np.ptp(total[keep])),
                "electronic_range_hartree": float(np.ptp(electronic[keep])),
                "total_std_hartree": float(np.std(total[keep])),
                "electronic_std_hartree": float(np.std(electronic[keep])),
                "total_over_electronic_std": float(
                    np.std(total[keep]) / np.std(electronic[keep])
                ),
            }
        )
    write_csv(HERE / "target-ranges.csv", rows)


def configure_axes(axis: plt.Axes) -> None:
    axis.set_facecolor(CREAM)
    axis.tick_params(colors=INK, labelsize=10, width=1.1, length=4)
    for spine in axis.spines.values():
        spine.set_color(INK)
        spine.set_linewidth(1.2)
    axis.grid(True, which="major", color=GRID, linewidth=0.8, alpha=0.8)
    axis.grid(True, which="minor", color=GRID, linewidth=0.5, alpha=0.35)


def callout(axis: plt.Axes, label: str, xy: tuple[float, float]) -> None:
    axis.annotate(
        label,
        xy=xy,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=CREAM,
        bbox={"boxstyle": "circle,pad=0.28", "fc": INK, "ec": CREAM, "lw": 1.0},
        zorder=10,
    )


def make_figure(
    scan: list[dict[str, str]], summaries: dict[str, dict[float, dict[str, float]]]
) -> None:
    r = np.asarray([float(row["r_bohr"]) for row in scan])
    total = np.asarray([float(row["total_hartree"]) for row in scan])
    electronic = np.asarray([float(row["electronic_hartree"]) for row in scan])
    cutoffs = np.asarray(sorted(summaries["primary"]))

    raw_values = np.asarray(
        [
            [summaries[tag][float(c)]["median_A_over_B"] for c in cutoffs]
            for tag in RAW_R_CONTROLS
        ]
    )
    primary = np.asarray(
        [summaries["primary"][float(c)]["median_A_over_B"] for c in cutoffs]
    )
    log_input = np.asarray(
        [summaries["log-input"][float(c)]["median_A_over_B"] for c in cutoffs]
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.labelcolor": INK,
            "text.color": INK,
            "savefig.facecolor": CREAM,
            "figure.facecolor": CREAM,
        }
    )
    figure, (left, right) = plt.subplots(
        1,
        2,
        figsize=(12, 6.3),
        dpi=100,
        gridspec_kw={"width_ratios": (1.03, 1.12), "wspace": 0.27},
    )

    configure_axes(left)
    left.plot(r, total, color=DEEP, linewidth=2.7, label=r"Total $V$")
    left.plot(
        r,
        electronic,
        color=LIFTED,
        linewidth=2.7,
        linestyle=(0, (5, 2.5)),
        label=r"Electronic $E_{el}$",
    )
    left.set_xscale("log")
    left.set_xlim(0.15, 20.0)
    left.set_ylim(-2.2, 5.1)
    left.set_xlabel(r"Bond distance, $R$ ($a_0$)", fontsize=12)
    left.set_ylabel("Energy (hartree)", fontsize=12)
    left.legend(
        loc="upper right",
        frameon=False,
        fontsize=10.5,
        labelcolor=INK,
        handlelength=2.8,
    )
    left.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    left.xaxis.set_minor_formatter(NullFormatter())
    callout(left, "A", (0.19, 3.15))
    callout(left, "B", (8.8, -0.605))

    configure_axes(right)
    right.fill_between(
        cutoffs,
        np.min(raw_values, axis=0),
        np.max(raw_values, axis=0),
        color=LIFTED,
        alpha=0.42,
        linewidth=0,
        label="Raw-R control range",
    )
    right.plot(
        cutoffs,
        primary,
        color=DEEP,
        marker="o",
        markersize=5.6,
        markerfacecolor=CREAM,
        markeredgewidth=1.7,
        linewidth=2.7,
        label="Primary raw-R fit",
        zorder=5,
    )
    right.plot(
        cutoffs,
        log_input,
        color=INDIGO,
        marker="s",
        markersize=5.2,
        markerfacecolor=CREAM,
        markeredgewidth=1.5,
        linewidth=2.1,
        linestyle=(0, (4, 2.5)),
        label="log-R control",
        zorder=4,
    )
    right.axhline(1.0, color=INK, linewidth=1.3, linestyle=(0, (2, 2)), label="Parity")
    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlim(0.14, 3.25)
    right.set_ylim(0.045, 100.0)
    right.set_xlabel(r"Shortest fitted distance, $R_{min}$ ($a_0$)", fontsize=12)
    right.set_ylabel(r"Out-of-fold RMSE ratio, A / B", fontsize=12)
    right.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    right.xaxis.set_minor_formatter(NullFormatter())
    right.yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    right.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    right.yaxis.set_minor_formatter(NullFormatter())
    handles, labels = right.get_legend_handles_labels()
    order = [1, 0, 2, 3]
    right.legend(
        [handles[index] for index in order],
        [labels[index] for index in order],
        loc="upper right",
        frameon=False,
        fontsize=9.4,
        labelcolor=INK,
        handlelength=2.5,
    )
    callout(right, "C", (1.55, 1.18))

    figure.subplots_adjust(left=0.075, right=0.976, bottom=0.145, top=0.965)
    IMAGE.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(IMAGE, dpi=100, facecolor=CREAM, edgecolor="none")
    plt.close(figure)

    from PIL import Image

    with Image.open(IMAGE) as rendered:
        if rendered.size != (1200, 630):
            raise RuntimeError(f"unexpected figure size: {rendered.size}")


def main() -> None:
    scan = read_csv(HERE / "h2plus-scan.csv")
    summaries = load_summaries()
    cutoffs = sorted(summaries["primary"])
    write_target_ranges(scan, cutoffs)
    make_figure(scan, summaries)
    print(f"wrote {HERE / 'control-ratios.csv'}")
    print(f"wrote {HERE / 'target-ranges.csv'}")
    print(f"wrote {IMAGE}")


if __name__ == "__main__":
    main()
