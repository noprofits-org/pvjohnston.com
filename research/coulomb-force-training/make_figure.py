"""Hero figure: median A/B energy-RMSE ratio vs fitting-domain cutoff, for the
energy-only and energy-plus-force losses. 1200x630 for the in-post hero and the
social card. House palette; lettered callouts defined in the post caption."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

INK = "#1a1d2b"
INDIGO = "#465c9b"
LIFT = "#8fa5e3"
DEEP = "#2f417a"
CREAM = "#f5f2ea"

here = Path(__file__).parent
data = json.loads((here / "results.json").read_text())
cutoffs = data["protocol"]["cutoffs_bohr"]


def ratios(loss):
    pc = data["derived"][loss]["per_cutoff"]
    return [pc[f"{c:.2f}"]["median_ab_ratio"] for c in cutoffs]


r_energy = ratios("energy")
r_force = ratios("energy_force")
cross_e = data["derived"]["energy"]["crossover_cutoff"]
cross_f = data["derived"]["energy_force"]["crossover_cutoff"]

fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.axhline(1.0, color=INK, lw=1.6, ls=(0, (5, 4)), zorder=1)

ax.plot(cutoffs, r_energy, "-o", color=DEEP, lw=2.6, ms=9, zorder=3,
        markeredgecolor=CREAM, markeredgewidth=1.4, label="energy-only loss")
ax.plot(cutoffs, r_force, "-s", color=LIFT, lw=2.6, ms=9, zorder=3,
        markeredgecolor=INK, markeredgewidth=1.2, label="energy + force loss")

ax.set_yscale("log")
ax.set_xscale("log")
ax.set_xlim(0.12, 3.6)
ticks = cutoffs
ax.xaxis.set_major_locator(FixedLocator(ticks))
ax.xaxis.set_major_formatter(FixedFormatter([f"{c:.2f}" for c in ticks]))
ax.set_xlabel("fitting-domain lower cutoff  $R_{\\min}$  (bohr)",
              fontsize=15, color=INK)
ax.set_ylabel("median  RMSE$_A$ / RMSE$_B$", fontsize=15, color=INK)

# callouts
def mark(x, y, letter, dx, dy):
    ax.annotate(letter, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=16, fontweight="bold", color=INK, zorder=6)

# A: near-wall gap, widest under the energy+force loss
mark(cutoffs[0], r_force[0], "A", 12, -2)
# B: energy+force ratio drops below one first, at R_min = 2 bohr
if cross_f is not None:
    yf = data["derived"]["energy_force"]["per_cutoff"][f"{cross_f:.2f}"]["median_ab_ratio"]
    ax.plot([cross_f], [yf], marker="o", ms=17, mfc="none",
            markeredgecolor=INK, markeredgewidth=2.0, zorder=5)
    mark(cross_f, yf, "B", 10, 8)
# C: energy-only ratio stays above one until R_min = 3 bohr
if cross_e is not None:
    ye = data["derived"]["energy"]["per_cutoff"][f"{cross_e:.2f}"]["median_ab_ratio"]
    ax.plot([cross_e], [ye], marker="o", ms=17, mfc="none",
            markeredgecolor=DEEP, markeredgewidth=2.0, zorder=5)
    mark(cross_e, ye, "C", 8, -22)

for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color(INK)
ax.tick_params(colors=INK, labelsize=12)
ax.legend(frameon=False, fontsize=14, loc="upper right", labelcolor=INK)
ax.set_title("Where subtracting the exact 1/R helps an H$_2^+$ neural fit",
             fontsize=17, color=INK, pad=12, loc="left")

fig.tight_layout()
out = here.parent.parent / "images" / \
    "2026-07-21-does-force-training-move-the-coulomb-subtraction-crossover-hero.png"
fig.savefig(out, facecolor=CREAM, bbox_inches="tight")
# enforce 1200x630 by re-saving at fixed size
fig.set_size_inches(12, 6.3)
fig.savefig(out, facecolor=CREAM, dpi=100)
print("wrote", out)
print("cross_e", cross_e, "cross_f", cross_f)
print("r_energy", [round(x, 3) for x in r_energy])
print("r_force", [round(x, 3) for x in r_force])
