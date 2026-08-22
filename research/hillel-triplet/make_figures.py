#!/usr/bin/env python3
"""Render the three post figures from the committed results projection."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[2]
RESULT = json.loads(
    (Path(__file__).resolve().parent / "results" / "results.json").read_text()
)
SLUG = "2026-08-22-does-push-pull-abolish-the-s0-t1-crossing"
IMAGES = ROOT / "images"

CREAM = "#f5f2ea"
INK = "#1a1d2b"
GRID = "#d8d2c6"
S0 = "#2f417a"
T1 = "#b03a2e"
M4 = "#6c3483"
M2 = "#c0392b"
M0 = "#7f8c8d"
M1 = "#2471a3"
M3 = "#1e8449"


def linear_zero(x0, y0, x1, y1):
    return x0 - (y0 * (x1 - x0)) / (y1 - y0)


def m4_series():
    points = RESULT["molecules"]["M4"]["points"]
    angles, s0, t1, s0_ok, t1_ok, gaps = [], [], [], [], [], []
    for p in points:
        angles.append(p["cnnc_deg"])
        s0.append(p["s0_rel_kjmol"])
        t1.append(p["t1_rel_kjmol"])
        s0_ok.append(p["s0_converged"])
        t1_ok.append(p["t1_converged"])
        if "gap_kjmol" in p:
            gaps.append(p["gap_kjmol"])
        else:
            gaps.append(p["s0_rel_kjmol"] - p["t1_rel_kjmol"])
    return angles, s0, t1, s0_ok, t1_ok, gaps


def style_ax(ax):
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(INK)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=INK, labelsize=9)
    ax.xaxis.set_major_locator(MultipleLocator(15))
    ax.set_xlim(180, 0)


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


def fig1():
    angles, _s0, _t1, s0_ok, t1_ok, gaps = m4_series()
    m2 = RESULT["molecules"]["M2"]["gaps_kjmol"]
    crossings = {
        "M0": RESULT["molecules"]["M0"]["crossings_deg"][0],
        "M1": RESULT["molecules"]["M1"]["crossings_deg"][0],
        "M3": RESULT["molecules"]["M3"]["crossings_deg"][0],
        "M4": linear_zero(120, gaps[angles.index(120)], 105, gaps[angles.index(105)]),
    }
    colors = {"M0": M0, "M1": M1, "M3": M3, "M4": M4}

    fig, ax = plt.subplots(figsize=(12.00, 6.30), facecolor=CREAM)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.16)
    style_ax(ax)
    ax.axhline(0, color=INK, linewidth=1.0)

    both_x, both_y, un_x, un_y = [], [], [], []
    for a, g, ok0, ok1 in zip(angles, gaps, s0_ok, t1_ok):
        if ok0 and ok1:
            both_x.append(a)
            both_y.append(g)
        else:
            un_x.append(a)
            un_y.append(g)
    ax.plot(both_x, both_y, "-", color=M4, linewidth=1.8, zorder=3)
    ax.plot(both_x, both_y, "o", color=M4, markersize=6, zorder=4)
    ax.plot(un_x, un_y, "x", color=M4, markersize=7, markeredgewidth=1.6, zorder=4)
    ax.plot(
        [120, 105],
        [float(m2["120"]), float(m2["105"])],
        "s",
        color=M2,
        markersize=7,
        zorder=5,
    )

    for label, ang in crossings.items():
        ax.axvline(ang, color=colors[label], linewidth=0.9, linestyle=":", alpha=0.85)
        ax.plot(ang, 0, marker="|", color=colors[label], markersize=14, markeredgewidth=2)

    ax.set_xlabel("CNNC dihedral (deg)  [180 = trans, 0 = cis]", color=INK)
    ax.set_ylabel("S0 − T1 gap (kJ/mol)", color=INK)
    ax.set_ylim(-160, 40)
    handles = [
        Line2D([0], [0], color=M4, marker="o", linewidth=1.8, label="M4 gap, both-converged"),
        Line2D([0], [0], color=M4, marker="x", linewidth=0, markersize=7, label="M4, S0 unconverged"),
        Line2D([0], [0], color=M2, marker="s", linewidth=0, markersize=7, label="M2 gap at 120° and 105°"),
        Line2D([0], [0], color=M0, linestyle=":", linewidth=1.2, label="M0 upper zero"),
        Line2D([0], [0], color=M1, linestyle=":", linewidth=1.2, label="M1 upper zero"),
        Line2D([0], [0], color=M3, linestyle=":", linewidth=1.2, label="M3 upper zero"),
        Line2D([0], [0], color=M4, linestyle=":", linewidth=1.2, label="M4 120°/105° zero"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=8, facecolor="white")
    return save(fig, "fig1", size=(1200, 630))


def _m4_profiles(ax, letter=True):
    angles, s0, t1, s0_ok, t1_ok, gaps = m4_series()
    style_ax(ax)
    ax.axhline(0, color=INK, linewidth=0.7)
    s0c_x = [a for a, ok in zip(angles, s0_ok) if ok]
    s0c_y = [e for e, ok in zip(s0, s0_ok) if ok]
    s0u_x = [a for a, ok in zip(angles, s0_ok) if not ok]
    s0u_y = [e for e, ok in zip(s0, s0_ok) if not ok]
    ax.plot(s0c_x, s0c_y, "-o", color=S0, linewidth=1.7, markersize=5.5, label="S0 (RKS)")
    ax.plot(angles, t1, "-s", color=T1, linewidth=1.7, markersize=5.0, label="T1 (UKS)")
    ax.plot(s0u_x, s0u_y, "x", color=S0, markersize=7, markeredgewidth=1.6, label="S0 unconverged")
    crossing = linear_zero(120, gaps[angles.index(120)], 105, gaps[angles.index(105)])
    y_cross = 116.51 + (115.49 - 116.51) * (crossing - 120) / (105 - 120)
    if letter:
        ax.plot(crossing, y_cross, "o", color=INK, markersize=5, zorder=6)
        ax.annotate(
            "A",
            (crossing, y_cross),
            textcoords="offset points",
            xytext=(8, 10),
            fontsize=11,
            fontweight="bold",
            color=INK,
        )
    ax.set_xlabel("CNNC dihedral (deg)  [180 = trans, 0 = cis]", color=INK)
    ax.set_ylabel("E relative to trans-S0 (kJ/mol)", color=INK)
    ax.set_ylim(-5, 175)
    ax.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white")
    return crossing


def fig2():
    fig, ax = plt.subplots(figsize=(8.6, 5.4), facecolor="white")
    fig.subplots_adjust(left=0.11, right=0.97, top=0.96, bottom=0.14)
    _m4_profiles(ax)
    return save(fig, "fig2")


def fig3():
    angles, _s0, _t1, s0_ok, t1_ok, gaps = m4_series()
    m2 = RESULT["molecules"]["M2"]["gaps_kjmol"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.0), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.15, wspace=0.28)
    _m4_profiles(ax1)
    style_ax(ax2)
    ax2.axhline(0, color=INK, linewidth=1.0)
    both_x = [a for a, ok0, ok1 in zip(angles, s0_ok, t1_ok) if ok0 and ok1]
    both_y = [g for g, ok0, ok1 in zip(gaps, s0_ok, t1_ok) if ok0 and ok1]
    un_x = [a for a, ok0, ok1 in zip(angles, s0_ok, t1_ok) if not (ok0 and ok1)]
    un_y = [g for g, ok0, ok1 in zip(gaps, s0_ok, t1_ok) if not (ok0 and ok1)]
    ax2.plot(both_x, both_y, "-o", color=M4, linewidth=1.7, markersize=5.5, label="M4 gap")
    ax2.plot(un_x, un_y, "x", color=M4, markersize=7, markeredgewidth=1.6, label="M4, S0 unconverged")
    ax2.plot(
        [120, 105],
        [float(m2["120"]), float(m2["105"])],
        "s-",
        color=M2,
        markersize=6.5,
        linewidth=1.4,
        label="M2 gap (120°, 105°)",
    )
    crossing = linear_zero(120, gaps[angles.index(120)], 105, gaps[angles.index(105)])
    ax2.plot(crossing, 0, "o", color=INK, markersize=5)
    ax2.annotate(
        "A",
        (crossing, 0),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=11,
        fontweight="bold",
        color=INK,
    )
    ax2.set_xlabel("CNNC dihedral (deg)  [180 = trans, 0 = cis]", color=INK)
    ax2.set_ylabel("S0 − T1 gap (kJ/mol)", color=INK)
    ax2.set_ylim(-160, 40)
    ax2.legend(loc="lower right", fontsize=8, frameon=True, facecolor="white")
    return save(fig, "fig3")


def main():
    paths = [fig1(), fig2(), fig3()]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
