#!/usr/bin/env python3
"""Make the 1200x630 publication figure from the canonical result artifacts.

Reads results/stage1.json and results/stage2.json; no result digits are
recomputed here beyond medians over the committed per-rep values. Uses
matplotlib from a disposable venv; the figure is a rendering, not a result.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

INK = "#1a1d2b"
INDIGO = "#465c9b"
LIFT = "#8fa5e3"
DEEP = "#2f417a"
CREAM = "#fbfaf6"
PANEL = "#f5f2ea"

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
STAGE1 = json.loads((HERE / "results" / "stage1.json").read_text())
STAGE2 = json.loads((HERE / "results" / "stage2.json").read_text())
OUT = ROOT / "images" / "2026-08-11-momentum-recovery-region-hero.png"

BETAS = STAGE1["betas"]
THRESHOLD = STAGE1["floor_threshold"]
BETA_COLOR = {0.0: "#b9c6ec", 0.3: LIFT, 0.6: INDIGO, 0.9: DEEP, 0.99: INK}
CLIP_TOP = 1e2  # points above are collected into the overflow marker row


def medians(rows, beta, conv):
    lrs = sorted({r["lr"] for r in rows if r["beta"] == beta})
    out = []
    for lr in lrs:
        vals = [r["test"] for r in rows
                if r["beta"] == beta and r["conv"] == conv and r["lr"] == lr]
        out.append((lr, None if len(vals) != 3 or any(v is None for v in vals)
                    else float(np.median(vals))))
    return out


fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=CREAM)
grid = fig.add_gridspec(2, 2, width_ratios=[1.45, 1.0], height_ratios=[1, 1],
                        wspace=0.22, hspace=0.42,
                        left=0.075, right=0.975, top=0.90, bottom=0.11)
ax = fig.add_subplot(grid[:, 0])
axw = fig.add_subplot(grid[0, 1])
axb = fig.add_subplot(grid[1, 1])

for a in (ax, axw, axb):
    a.set_facecolor(PANEL)
    for spine in a.spines.values():
        spine.set_color(INK)
    a.tick_params(colors=INK, labelsize=9)
    for label in (a.xaxis.label, a.yaxis.label):
        label.set_color(INK)

# ---- Panel A: described-convention error curves per beta (stage 1).
for beta in BETAS:
    pts = medians(STAGE1["rows"], beta, "described")
    xs = [lr for lr, m in pts if m is not None and m <= CLIP_TOP]
    ys = [m for lr, m in pts if m is not None and m <= CLIP_TOP]
    over = [lr for lr, m in pts if m is None or m > CLIP_TOP]
    ax.loglog(xs, ys, "-o", ms=3.5, lw=1.4, color=BETA_COLOR[beta],
              label=f"$\\beta={beta:g}$")
    if over:
        ax.scatter(over, [CLIP_TOP * 1.6] * len(over), marker="v", s=26,
                   color=BETA_COLOR[beta], edgecolor=INK, linewidth=0.4,
                   zorder=5)
ax.axhline(THRESHOLD, color=INK, lw=1.0, ls=(0, (4, 3)))
ax.set_ylim(1e-31, 3e2)
ax.set_xlabel("learning rate")
ax.set_ylabel("median normalized test MSE")
ax.legend(loc="lower right", fontsize=8.5, frameon=False)
ax.text(1.30e-3, 1.7e-29, "A", fontsize=13, fontweight="bold", color=INK,
        ha="center", va="center",
        bbox=dict(boxstyle="circle,pad=0.25", fc=CREAM, ec=INK, lw=1.2))
ax.text(2.1e-4, 3e-27, "B", fontsize=13, fontweight="bold", color=INK,
        ha="center", va="center",
        bbox=dict(boxstyle="circle,pad=0.25", fc=CREAM, ec=INK, lw=1.2))
ax.text(5.2e-4, 8.0, "C", fontsize=13, fontweight="bold", color=INK,
        ha="center", va="center",
        bbox=dict(boxstyle="circle,pad=0.25", fc=CREAM, ec=INK, lw=1.2))
ax.set_title("described convention, stage-1 grid", color=INK, fontsize=11,
             loc="left")

# ---- Panel B (top): refined recovery-region width vs beta.
widths = {0.9: 0.03, 0.99: 0.68}
xs = list(range(len(BETAS)))
heights = [widths.get(b, 0.0) for b in BETAS]
bars = axw.bar(xs, heights, width=0.62, color=[BETA_COLOR[b] for b in BETAS],
               edgecolor=INK, linewidth=0.8)
axw.annotate("", xy=(4, 0.78), xytext=(4, 0.66),
             arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
axw.text(4, 0.83, "D", fontsize=12, fontweight="bold", color=INK,
         ha="center", va="center",
         bbox=dict(boxstyle="circle,pad=0.22", fc=CREAM, ec=INK, lw=1.2))
axw.set_xticks(xs, [f"{b:g}" for b in BETAS])
axw.set_xlabel("$\\beta$")
axw.set_ylabel("width (decades)")
axw.set_ylim(0, 0.95)
axw.set_title("recovery-region width (0.01-decade grid)", color=INK,
              fontsize=11, loc="left")

# ---- Panel B (bottom): divergence-boundary ratio vs 1+beta.
bound = {}
for beta in BETAS:
    lrs = sorted({r["lr"] for r in STAGE1["rows"] if r["beta"] == beta})
    bound[beta] = next(lr for lr in lrs if any(
        r["test"] is None for r in STAGE1["rows"]
        if r["beta"] == beta and r["conv"] == "described" and r["lr"] == lr))
ratio = [bound[b] / bound[0.0] for b in BETAS]
axb.plot(BETAS, [1 + b for b in BETAS], "--", color=LIFT, lw=1.4,
         label="$1+\\beta$")
axb.plot(BETAS, ratio, "-o", ms=4.5, lw=1.6, color=DEEP, label="measured")
axb.set_xlabel("$\\beta$")
axb.set_ylabel("boundary ratio to $\\beta=0$")
axb.legend(loc="center right", fontsize=8.5, frameon=False)
axb.set_title("described divergence boundary", color=INK, fontsize=11,
              loc="left")
axb.set_ylim(0.85, 2.15)

fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
