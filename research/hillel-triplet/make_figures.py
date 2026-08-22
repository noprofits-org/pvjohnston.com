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


def gap_of(point):
    if "gap_kjmol" in point:
        return point["gap_kjmol"]
    return point["s0_rel_kjmol"] - point["t1_rel_kjmol"]


def point_at(mol, deg):
    found = next(
        (p for p in RESULT["molecules"][mol]["points"] if p["cnnc_deg"] == deg),
        None,
    )
    if found is None:
        raise KeyError(f"missing {mol} point at {deg}")
    return found


def trans_side_zero(mol):
    return linear_zero(120, gap_of(point_at(mol, 120)), 105, gap_of(point_at(mol, 105)))


def m4_series():
    points = RESULT["molecules"]["M4"]["points"]
    angles, s0, t1, s0_ok, t1_ok, gaps = [], [], [], [], [], []
    for p in points:
        angles.append(p["cnnc_deg"])
        s0.append(p.get("s0_rel_kjmol"))
        t1.append(p.get("t1_rel_kjmol"))
        s0_run = p.get("s0_not_run") is not True and p.get("s0_rel_kjmol") is not None
        s0_ok.append(bool(p.get("s0_converged")) and s0_run)
        t1_ok.append(bool(p.get("t1_converged")) and p.get("t1_rel_kjmol") is not None)
        if "gap_kjmol" in p:
            gaps.append(p["gap_kjmol"])
        elif s0_run and p.get("t1_rel_kjmol") is not None:
            gaps.append(p["s0_rel_kjmol"] - p["t1_rel_kjmol"])
        else:
            gaps.append(None)
    return angles, s0, t1, s0_ok, t1_ok, gaps


def segments(xs, ys, ok):
    """Split a series wherever a point is missing or not eligible to connect."""
    segs = []
    cur_x, cur_y = [], []
    for x, y, flag in zip(xs, ys, ok):
        if flag and y is not None:
            cur_x.append(x)
            cur_y.append(y)
        else:
            if cur_x:
                segs.append((cur_x, cur_y))
                cur_x, cur_y = [], []
    if cur_x:
        segs.append((cur_x, cur_y))
    return segs


def plot_segments(ax, xs, ys, ok, *, color, linewidth, marker=None, markersize=None, zorder=3, label=None):
    first = True
    for seg_x, seg_y in segments(xs, ys, ok):
        ax.plot(
            seg_x,
            seg_y,
            "-",
            color=color,
            linewidth=linewidth,
            marker=marker,
            markersize=markersize,
            zorder=zorder,
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
    m2_120 = gap_of(point_at("M2", 120))
    m2_105 = gap_of(point_at("M2", 105))
    crossings = {
        "M0": trans_side_zero("M0"),
        "M1": trans_side_zero("M1"),
        "M3": trans_side_zero("M3"),
        "M4": linear_zero(120, gaps[angles.index(120)], 105, gaps[angles.index(105)]),
    }
    colors = {"M0": M0, "M1": M1, "M3": M3, "M4": M4}

    fig, ax = plt.subplots(figsize=(12.00, 6.30), facecolor=CREAM)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.16)
    style_ax(ax)
    ax.axhline(0, color=INK, linewidth=1.0)

    both_ok = [ok0 and ok1 and g is not None for ok0, ok1, g in zip(s0_ok, t1_ok, gaps)]
    plot_segments(ax, angles, gaps, both_ok, color=M4, linewidth=1.8, marker="o", markersize=6, zorder=3)
    un_x = [a for a, g, ok0, ok1 in zip(angles, gaps, s0_ok, t1_ok) if g is not None and not (ok0 and ok1)]
    un_y = [g for g, ok0, ok1 in zip(gaps, s0_ok, t1_ok) if g is not None and not (ok0 and ok1)]
    ax.plot(un_x, un_y, "x", color=M4, markersize=7, markeredgewidth=1.6, zorder=4)
    ax.plot(
        [120, 105],
        [m2_120, m2_105],
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
    plot_segments(ax, angles, s0, s0_ok, color=S0, linewidth=1.7, marker="o", markersize=5.5, label="S0 (RKS)")
    plot_segments(ax, angles, t1, t1_ok, color=T1, linewidth=1.7, marker="s", markersize=5.0, label="T1 (UKS)")
    s0u_x = [a for a, e, ok in zip(angles, s0, s0_ok) if e is not None and not ok]
    s0u_y = [e for e, ok in zip(s0, s0_ok) if e is not None and not ok]
    ax.plot(s0u_x, s0u_y, "x", color=S0, markersize=7, markeredgewidth=1.6, label="S0 unconverged")
    crossing = linear_zero(120, gaps[angles.index(120)], 105, gaps[angles.index(105)])
    t1_120 = t1[angles.index(120)]
    t1_105 = t1[angles.index(105)]
    y_cross = t1_120 + (t1_105 - t1_120) * (crossing - 120) / (105 - 120)
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
    ax.set_ylim(-5, 195)
    ax.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white")
    return crossing


def fig2():
    fig, ax = plt.subplots(figsize=(8.6, 5.4), facecolor="white")
    fig.subplots_adjust(left=0.11, right=0.97, top=0.96, bottom=0.14)
    _m4_profiles(ax)
    return save(fig, "fig2")


def fig3():
    angles, _s0, _t1, s0_ok, t1_ok, gaps = m4_series()
    m2_120 = gap_of(point_at("M2", 120))
    m2_105 = gap_of(point_at("M2", 105))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.0), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.15, wspace=0.28)
    _m4_profiles(ax1)
    style_ax(ax2)
    ax2.axhline(0, color=INK, linewidth=1.0)
    both_ok = [ok0 and ok1 and g is not None for ok0, ok1, g in zip(s0_ok, t1_ok, gaps)]
    plot_segments(ax2, angles, gaps, both_ok, color=M4, linewidth=1.7, marker="o", markersize=5.5, label="M4 gap")
    un_x = [a for a, g, ok0, ok1 in zip(angles, gaps, s0_ok, t1_ok) if g is not None and not (ok0 and ok1)]
    un_y = [g for g, ok0, ok1 in zip(gaps, s0_ok, t1_ok) if g is not None and not (ok0 and ok1)]
    ax2.plot(un_x, un_y, "x", color=M4, markersize=7, markeredgewidth=1.6, label="M4, S0 unconverged")
    ax2.plot(
        [120, 105],
        [m2_120, m2_105],
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
