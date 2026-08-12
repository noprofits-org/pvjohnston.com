"""Ensemble broadening demonstration for the single-molecule vs bulk spectroscopy post.

A single two-level molecule has a Lorentzian line centred at its own transition
frequency. In a bulk sample the molecules sit in slightly different
environments, so their centre frequencies are drawn from a Gaussian
inhomogeneous distribution. Summing the Lorentzians of many molecules recovers
the smooth, broad absorption band measured in a cuvette.

Deterministic: the only randomness is `random.gauss` driven by `random.seed(0)`,
so every run reproduces the same centre frequencies, the same SVG, and the same
canonical summary.

Outputs (paths relative to the repository root):
- images/2026-08-12-from-blinking-to-absorption-ensemble.svg  (Figure 2)
- research/from-blinking-to-absorption/results/summary.json   (canonical results)

This script uses only the Python standard library so it needs no installed
packages.
"""
import json
import math
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_DIR = Path(__file__).resolve().parents[1]

# Frequency axis in wavenumbers, relative to the mean transition frequency.
NU_MIN, NU_MAX = -300.0, 300.0
N_POINTS = 1000
nu = [NU_MIN + (NU_MAX - NU_MIN) * i / (N_POINTS - 1) for i in range(N_POINTS)]

# Natural (homogeneous) Lorentzian linewidth for one molecule (HWHM).
GAMMA = 2.0

# Inhomogeneous Gaussian width (standard deviation) of the centre-frequency
# distribution across the ensemble.
SIGMA_INHOM = 40.0

# Plot geometry.
WIDTH, HEIGHT = 700, 650
MARGIN = 60
PLOT_W = WIDTH - 2 * MARGIN
PLOT_H_PER_PANEL = 150
PANEL_GAP = 40
N_PANELS = 3
PLOT_TOTAL_H = N_PANELS * PLOT_H_PER_PANEL + (N_PANELS - 1) * PANEL_GAP

# Scale so the whole drawing fits comfortably.
SCALE = 0.9
DX = PLOT_W / (NU_MAX - NU_MIN)

def lorentzian(x, x0, gamma):
    return (gamma / math.pi) / ((x - x0) ** 2 + gamma ** 2)

def gaussian(x, mu, sigma):
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

def fwhm(xs, ys):
    """Full width at half maximum of a sampled curve, by linear interpolation
    of the two half-maximum crossings around the global peak."""
    peak_index = max(range(len(ys)), key=ys.__getitem__)
    half = ys[peak_index] / 2.0

    def crossing(i, j):
        # Interpolate x where y crosses `half` between samples i and j.
        x0, x1, y0, y1 = xs[i], xs[j], ys[i], ys[j]
        return x0 + (half - y0) * (x1 - x0) / (y1 - y0)

    left = next(crossing(i, i + 1)
                for i in range(peak_index, -1, -1) if ys[i] < half <= ys[i + 1])
    right = next(crossing(i, i + 1)
                 for i in range(peak_index, len(ys) - 1) if ys[i] >= half > ys[i + 1])
    return right - left

def panel_top_left(panel):
    """Return (x, y) of the top-left corner of a panel."""
    x = MARGIN
    y = MARGIN + panel * (PLOT_H_PER_PANEL + PANEL_GAP)
    return x, y

def panel_path(panel, y_values, y_max):
    """Return SVG path data for a curve in a given panel, normalised to y_max."""
    x0, y0 = panel_top_left(panel)
    pts = []
    for i, y in enumerate(y_values):
        x = x0 + i * PLOT_W / (len(y_values) - 1)
        py = y0 + PLOT_H_PER_PANEL - (y / y_max) * PLOT_H_PER_PANEL * SCALE
        pts.append(f"{x:.2f},{py:.2f}")
    return "M" + " L".join(pts)

def axis_svg(panel, y_label):
    x0, y0 = panel_top_left(panel)
    lines = []
    # Box.
    lines.append(f'<rect x="{x0}" y="{y0}" width="{PLOT_W}" height="{PLOT_H_PER_PANEL}" fill="none" stroke="#333" stroke-width="1"/>')
    # X ticks at -200, 0, 200.
    for tick_val in (-200, 0, 200):
        tx = x0 + (tick_val - NU_MIN) * DX
        lines.append(f'<line x1="{tx}" y1="{y0 + PLOT_H_PER_PANEL}" x2="{tx}" y2="{y0 + PLOT_H_PER_PANEL + 5}" stroke="#333" stroke-width="1"/>')
        lines.append(f'<text x="{tx}" y="{y0 + PLOT_H_PER_PANEL + 18}" font-size="10" text-anchor="middle" fill="#333">{tick_val}</text>')
    # Y label.
    lines.append(f'<text x="{x0 - 45}" y="{y0 + 10}" font-size="10" fill="#333">{y_label}</text>')
    # X axis label on bottom panel only.
    if panel == N_PANELS - 1:
        lines.append(f'<text x="{x0 + PLOT_W / 2}" y="{y0 + PLOT_H_PER_PANEL + 32}" font-size="11" text-anchor="middle" fill="#333">frequency relative to &#x03bd;&#x0303;&#x2091;&#x2092; (cm&#x207b;&#x00b9;)</text>')
    return "\n".join(lines)

random.seed(0)
example_centres = [random.gauss(0.0, SIGMA_INHOM) for _ in range(4)]

# Panel 1: one molecule at zero.
spectrum_1 = [lorentzian(x, 0.0, GAMMA) for x in nu]
max_1 = max(spectrum_1)

# Panel 2: four example molecules.
spectra_4 = [[lorentzian(x, c, GAMMA) for x in nu] for c in example_centres]
max_4 = max(max(s) for s in spectra_4)

# Panel 3: ensemble averages.
Ns = [10, 100, 10000]
spectra_N = []
for N in Ns:
    centres = [random.gauss(0.0, SIGMA_INHOM) for _ in range(N)]
    spectrum = [sum(lorentzian(x, c, GAMMA) for c in centres) / N for x in nu]
    spectra_N.append(spectrum)
max_N = max(max(s) for s in spectra_N)
# Analytic Gaussian limit.
analytic = [gaussian(x, 0.0, SIGMA_INHOM) for x in nu]
max_N = max(max_N, max(analytic))

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')

# Title.
parts.append(f'<text x="{WIDTH / 2}" y="{MARGIN - 25}" font-size="14" text-anchor="middle" font-weight="bold" fill="#111">From one molecule to a bulk absorption band</text>')

# Panel 1.
parts.append(axis_svg(0, "intensity"))
parts.append(f'<path d="{panel_path(0, spectrum_1, max_1)}" fill="none" stroke="{COLORS[0]}" stroke-width="2"/>')
parts.append(f'<text x="{MARGIN + 10}" y="{panel_top_left(0)[1] + 20}" font-size="11" fill="#111">One molecule</text>')

# Panel 2.
parts.append(axis_svg(1, "intensity"))
for s in spectra_4:
    parts.append(f'<path d="{panel_path(1, s, max_4)}" fill="none" stroke="{COLORS[0]}" stroke-width="1.2" opacity="0.5"/>')
parts.append(f'<text x="{MARGIN + 10}" y="{panel_top_left(1)[1] + 20}" font-size="11" fill="#111">Four molecules in different environments</text>')

# Panel 3.
parts.append(axis_svg(2, "intensity"))
for s, N, color in zip(spectra_N, Ns, COLORS[1:]):
    parts.append(f'<path d="{panel_path(2, s, max_N)}" fill="none" stroke="{color}" stroke-width="1.5"/>')
parts.append(f'<path d="{panel_path(2, analytic, max_N)}" fill="none" stroke="#333" stroke-width="1.5" stroke-dasharray="4,3"/>')

# Legend for panel 3.
legend_x = MARGIN + PLOT_W - 140
legend_y = panel_top_left(2)[1] + 20
for i, (N, color) in enumerate(zip(Ns, COLORS[1:])):
    parts.append(f'<line x1="{legend_x}" y1="{legend_y + i * 16}" x2="{legend_x + 20}" y2="{legend_y + i * 16}" stroke="{color}" stroke-width="1.5"/>')
    parts.append(f'<text x="{legend_x + 26}" y="{legend_y + 4 + i * 16}" font-size="10" fill="#333">N = {N:,}</text>')
parts.append(f'<line x1="{legend_x}" y1="{legend_y + 3 * 16}" x2="{legend_x + 20}" y2="{legend_y + 3 * 16}" stroke="#333" stroke-width="1.5" stroke-dasharray="4,3"/>')
parts.append(f'<text x="{legend_x + 26}" y="{legend_y + 4 + 3 * 16}" font-size="10" fill="#333">Gaussian limit</text>')

parts.append('</svg>')

svg = "\n".join(parts)
out_svg = REPO_ROOT / "images" / "2026-08-12-from-blinking-to-absorption-ensemble.svg"
out_svg.parent.mkdir(parents=True, exist_ok=True)
with open(out_svg, "w") as f:
    f.write(svg)
print(f"wrote {out_svg}")

# Canonical summary: declared parameters plus the linewidths measured on the
# generated curves, for the metrics projection.
gaussian_limit_fwhm = 2.0 * math.sqrt(2.0 * math.log(2.0)) * SIGMA_INHOM
ensemble_fwhm = fwhm(nu, spectra_N[Ns.index(10000)])
summary = {
    "parameters": {
        "gamma_hwhm_cm1": GAMMA,
        "sigma_inhom_cm1": SIGMA_INHOM,
        "seed": 0,
        "nu_range_cm1": [NU_MIN, NU_MAX],
        "n_points": N_POINTS,
        "ensemble_sizes": Ns,
    },
    "fwhm_cm1": {
        "single_molecule": round(fwhm(nu, spectrum_1), 4),
        "ensemble_10000": round(ensemble_fwhm, 4),
        "gaussian_limit": round(gaussian_limit_fwhm, 4),
    },
    "fwhm_gaussian_deviation": round(
        abs(ensemble_fwhm - gaussian_limit_fwhm) / gaussian_limit_fwhm, 6
    ),
}
out_summary = EXPERIMENT_DIR / "results" / "summary.json"
out_summary.parent.mkdir(parents=True, exist_ok=True)
with open(out_summary, "w") as f:
    json.dump(summary, f, indent=2)
    f.write("\n")
print(f"wrote {out_summary}")
