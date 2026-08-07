"""Make the 1200x630 publication figure from the canonical result artifact."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

INK = "#1a1d2b"
INDIGO = "#465c9b"
LIFT = "#8fa5e3"
DEEP = "#2f417a"
CREAM = "#f5f2ea"

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
DATA = json.loads((HERE / "results.json").read_text())
OUT = ROOT / "images" / (
    "2026-08-06-does-force-weight-keep-moving-the-coulomb-crossover-hero.png"
)

records = DATA["records"]
lambdas = [record["lambda_force"] for record in records]
first_parity = [record["derived"]["first_parity_cutoff_bohr"] for record in records]
brackets = [record["derived"]["first_parity_bracket_bohr"] for record in records]
audit = DATA["controls"]["optimization_sensitivity"]["endpoints"]

fig, (ax1, ax2) = plt.subplots(
    1,
    2,
    figsize=(12, 6.3),
    dpi=100,
    gridspec_kw={"width_ratios": [0.92, 1.18], "wspace": 0.25},
)
fig.patch.set_facecolor(CREAM)
for ax in (ax1, ax2):
    ax.set_facecolor(CREAM)

# Panel 1: registered first-parity cutoffs and their tested brackets.
x1 = list(range(len(lambdas)))
ax1.plot(x1, first_parity, color=DEEP, lw=2.4, zorder=2)
for x, cutoff, bracket in zip(x1, first_parity, brackets):
    lower = bracket["lower_bohr"]
    upper = bracket["upper_bohr"]
    ax1.vlines(x, lower, upper, color=INDIGO, lw=7, alpha=0.7, zorder=3)
    ax1.hlines([lower, upper], x - 0.08, x + 0.08, color=INDIGO, lw=2, zorder=3)
    ax1.plot(
        x,
        cutoff,
        "o",
        color=DEEP,
        ms=9,
        markeredgecolor=CREAM,
        markeredgewidth=1.3,
        zorder=4,
    )

# A hollow ring flags that lambda = 100 later reverse-crosses and then crosses
# forward again; its first parity cutoff is not one persistent crossover.
ax1.plot(
    x1[-1],
    first_parity[-1],
    marker="o",
    ms=16,
    mfc="none",
    markeredgecolor=INK,
    markeredgewidth=1.7,
    zorder=5,
)

ax1.set_xticks(x1, ["0", "0.01", "0.1", "1", "10", "100"])
ax1.set_ylim(1.0, 3.25)
ax1.set_yticks([1.0, 1.5, 2.0, 2.5, 3.0])
ax1.set_xlabel("standardized force-loss weight  $\\lambda$", fontsize=13, color=INK)
ax1.set_ylabel("first tested parity cutoff  (bohr)", fontsize=13, color=INK)

# A: the first small positive force weight produces the largest inward move.
ax1.annotate(
    "A",
    xy=(1, first_parity[1]),
    xytext=(-2, -25),
    textcoords="offset points",
    fontsize=16,
    fontweight="bold",
    color=INK,
)
# B: the registered first-parity cutoff then turns outward.
ax1.annotate(
    "B",
    xy=(4, first_parity[4]),
    xytext=(8, 8),
    textcoords="offset points",
    fontsize=16,
    fontweight="bold",
    color=INK,
)

# Panel 2: exactly the six registered 40k audit endpoints.
x2 = list(range(len(audit)))
labels = [
    f"{endpoint['lambda_force']:g}\n{endpoint['cutoff_bohr']:.2f}"
    for endpoint in audit
]
primary = [endpoint["primary_median_energy_ab_ratio"] for endpoint in audit]
extended = [endpoint["audit_median_energy_ab_ratio"] for endpoint in audit]

for x, endpoint, y20, y40 in zip(x2, audit, primary, extended):
    if not endpoint["same_side_of_parity"]:
        ax2.axvspan(x - 0.36, x + 0.36, color=LIFT, alpha=0.22, zorder=0)
    ax2.plot([x, x], [y20, y40], color=INDIGO, lw=2.0, zorder=2)
    ax2.plot(
        x,
        y20,
        "o",
        color=DEEP,
        ms=9,
        markeredgecolor=CREAM,
        markeredgewidth=1.2,
        zorder=3,
    )
    ax2.plot(
        x,
        y40,
        "s",
        color=LIFT,
        ms=9,
        markeredgecolor=INK,
        markeredgewidth=1.0,
        zorder=3,
    )

ax2.axhline(1.0, color=INK, lw=1.5, ls=(0, (5, 4)), zorder=1)
ax2.set_yscale("log")
ax2.set_ylim(0.5, 12.0)
ax2.set_xticks(x2, labels)
ax2.set_xlabel("audit endpoint:  $\\lambda$  /  $R_{\\min}$ (bohr)", fontsize=13, color=INK)
ax2.set_ylabel("median energy RMSE$_A$ / RMSE$_B$", fontsize=13, color=INK)
ax2.legend(
    handles=[
        Line2D([0], [0], marker="o", color="none", markerfacecolor=DEEP,
               markeredgecolor=CREAM, markersize=9, label="20,000 steps"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=LIFT,
               markeredgecolor=INK, markersize=9, label="40,000 steps"),
    ],
    frameon=False,
    fontsize=11,
    loc="upper left",
    labelcolor=INK,
)

# C: one of three highlighted endpoint classifications that changed sides.
ax2.annotate(
    "C",
    xy=(3, extended[3]),
    xytext=(9, 2),
    textcoords="offset points",
    fontsize=16,
    fontweight="bold",
    color=INK,
)

for ax in (ax1, ax2):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(INK)
    ax.tick_params(colors=INK, labelsize=10)

fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.18)
fig.savefig(OUT, facecolor=CREAM, dpi=100)
print(f"wrote {OUT}")
