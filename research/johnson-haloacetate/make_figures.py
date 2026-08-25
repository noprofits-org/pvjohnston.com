#!/usr/bin/env python3
"""Render the post figures from the committed scan CSVs."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SLUG = "2026-08-24-does-cx3-rotation-oscillate-carboxylate-oxygen-charge"
IMAGES = ROOT / "images"

CREAM = "#f5f2ea"
INK = "#1a1d2b"
GRID = "#d8d2c6"
CF3 = "#2f417a"
CCL3 = "#4a7fb5"
EH_TO_KCAL = 627.509474


def read_scan(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    points = []
    for row in rows:
        ok = (
            row["converged_optking"] == "true"
            and row["converged_exit"] == "true"
        )
        angle = float(row["angle"])
        if not ok:
            points.append({"angle": angle, "ok": False})
            continue
        points.append(
            {
                "angle": angle,
                "energy": float(row["energy_eh"]),
                # q_o_mbis is the arithmetic mean of the two carboxylate
                # oxygen MBIS charges. q_coo_mbis is the group sum.
                "q_o": float(row["q_o_mbis"]),
                "q_coo": float(row["q_coo_mbis"]),
                "ok": True,
            }
        )
    points.sort(key=lambda p: p["angle"])
    for i, point in enumerate(points):
        if point["angle"] != i * 15:
            raise RuntimeError(f"{path}: expected angle {i * 15}, got {point['angle']}")
    # Unconverged scheduled rows stay in the CSV and are dropped here.
    return [point for point in points if point["ok"]]


def neighbor_segments(xs: list[float], ys: list[float]) -> list[tuple[list[float], list[float]]]:
    """Connect only 15°-neighbour points. No bridging."""
    segs: list[tuple[list[float], list[float]]] = []
    cur_x: list[float] = []
    cur_y: list[float] = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        if not cur_x:
            cur_x.append(x)
            cur_y.append(y)
            continue
        if abs(x - cur_x[-1] - 15) < 1e-9:
            cur_x.append(x)
            cur_y.append(y)
        else:
            segs.append((cur_x, cur_y))
            cur_x = [x]
            cur_y = [y]
    if cur_x:
        segs.append((cur_x, cur_y))
    return segs


def deviations(points, key):
    if not points:
        return [], []
    mean = sum(point[key] for point in points) / len(points)
    return [point["angle"] for point in points], [point[key] - mean for point in points]


def relative_kcal(points):
    if not points:
        return [], []
    energies = [point["energy"] for point in points]
    floor = min(energies)
    return (
        [point["angle"] for point in points],
        [(energy - floor) * EH_TO_KCAL for energy in energies],
    )


def empty_panel_note(ax):
    ax.text(
        0.5,
        0.5,
        "no both-converged points",
        transform=ax.transAxes,
        ha="center",
        va="center",
        color=INK,
        fontsize=9,
    )


def plot_series(ax, xs, ys, *, color, marker, label):
    first = True
    for seg_x, seg_y in neighbor_segments(xs, ys):
        ax.plot(
            seg_x,
            seg_y,
            "-",
            color=color,
            linewidth=1.7,
            marker=marker,
            markersize=6,
            zorder=3,
            label=label if first else None,
        )
        first = False


def style_ax(ax):
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(INK)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=INK, labelsize=9)
    ax.xaxis.set_major_locator(MultipleLocator(15))
    ax.set_xlim(-2, 122)


def save(fig, name, size=None):
    IMAGES.mkdir(exist_ok=True)
    path = IMAGES / f"{SLUG}-{name}.png"
    if size is not None:
        fig.set_size_inches(size[0] / 100, size[1] / 100)
        fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    else:
        fig.savefig(path, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def fig1(m1, m3):
    angles_m1, q_o_cf3 = deviations(m1, "q_o")
    angles_m3, q_o_ccl3 = deviations(m3, "q_o")
    _, q_coo_cf3 = deviations(m1, "q_coo")
    _, q_coo_ccl3 = deviations(m3, "q_coo")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.00, 6.30), facecolor=CREAM)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.16, wspace=0.28)
    for ax in (ax1, ax2):
        style_ax(ax)
        ax.axhline(0, color=INK, linewidth=0.7)
        ax.set_ylim(-0.00045, 0.00045)
        ax.set_xlabel(r"frozen $\phi$ (deg)", color=INK)

    plot_series(ax1, angles_m1, q_o_cf3, color=CF3, marker="o", label=r"CF$_3$COO$^-$")
    plot_series(ax1, angles_m3, q_o_ccl3, color=CCL3, marker="s", label=r"CCl$_3$COO$^-$")
    ax1.set_ylabel(r"$q(\mathrm{O})-\langle q(\mathrm{O})\rangle$ (e)", color=INK)
    ax1.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white")

    plot_series(ax2, angles_m1, q_coo_cf3, color=CF3, marker="o", label=r"CF$_3$COO$^-$")
    plot_series(ax2, angles_m3, q_coo_ccl3, color=CCL3, marker="s", label=r"CCl$_3$COO$^-$")
    ax2.set_ylabel(r"$q(\mathrm{COO})-\langle q(\mathrm{COO})\rangle$ (e)", color=INK)
    ax2.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white")
    if not m1 and not m3:
        empty_panel_note(ax1)
        empty_panel_note(ax2)
    return save(fig, "fig1", size=(1200, 630))


def fig2(m1, m3):
    angles_m1, rel1 = relative_kcal(m1)
    angles_m3, rel3 = relative_kcal(m3)
    fig, ax = plt.subplots(figsize=(8.6, 5.2), facecolor="white")
    fig.subplots_adjust(left=0.12, right=0.97, top=0.96, bottom=0.14)
    style_ax(ax)
    plot_series(
        ax,
        angles_m1,
        rel1,
        color=CF3,
        marker="o",
        label=r"CF$_3$COO$^-$",
    )
    plot_series(
        ax,
        angles_m3,
        rel3,
        color=CCL3,
        marker="s",
        label=r"CCl$_3$COO$^-$",
    )
    ax.set_xlabel(r"frozen $\phi$ (deg)", color=INK)
    ax.set_ylabel("E relative to the scan minimum (kcal/mol)", color=INK)
    ax.set_ylim(-0.005, 0.055)
    ax.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white")
    if not m1 and not m3:
        empty_panel_note(ax)
    return save(fig, "fig2")


def main():
    m1 = read_scan(HERE / "results" / "m1_cf3_scan.csv")
    m3 = read_scan(HERE / "results" / "m3_ccl3_scan.csv")
    paths = [fig1(m1, m3), fig2(m1, m3)]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
