#!/usr/bin/env python
"""
Turn the per-functional state lists into the post's figure data and the
canonical results table.

The figure has to make one point: a spectrometer reports a single broad band,
but the calculation puts several distinct electronic transitions underneath it.
So the stick spectrum is the primary data and the smooth curve is secondary.

IMPORTANT, and stated in every artifact this writes: the broadened curve is
NOT a computed line shape. It is a Gaussian of fixed width applied by hand,
the same cosmetic convention used in calcs/uvvis-pushpull and in the 2025
DCDHF work. Real band width has vibronic and inhomogeneous contributions that
nothing here computes. The curve exists to show that closely spaced sticks
merge into one apparent band -- it is not evidence about width.

Usage: postprocess.py [--fwhm-ev 0.35] [--out-prefix spectra]
"""
import os, json, glob, argparse, csv, math

# run_tddft owns the geometry helpers and the topology check; importing them
# keeps one definition of "the twist angle" rather than two that can drift.
# It pulls in psi4, which costs a few seconds here and nothing else.
from run_tddft import read_xyz, geometry_report, verify_topology, DEFAULT_GEOM

HERE = os.path.dirname(os.path.abspath(__file__))
EV2NM = 1239.841984

# The hand-applied width. Matches the push-pull leg and the 2025 DCDHF figure
# so the spectra are visually comparable. Cosmetic, not computed.
DEFAULT_FWHM_EV = 0.35


def load_states():
    """Load every states_*.json, keyed by (functional, basis, method)."""
    runs = []
    for path in sorted(glob.glob(os.path.join(HERE, "results", "states_*.json"))):
        with open(path) as fh:
            runs.append(json.load(fh))
    if not runs:
        raise SystemExit("no results/states_*.json found -- run run_tddft.py excite first")
    return runs


def gaussian_curve(states, fwhm_ev, lo_nm=250.0, hi_nm=800.0, n=1101):
    """Sum of equal-width Gaussians in ENERGY, sampled on a wavelength grid.

    Broadening in energy rather than wavelength is the physically conventional
    choice: a Gaussian in eV is asymmetric in nm, which is what real bands look
    like. Amplitude is proportional to f, so relative peak heights stay
    meaningful even though the vertical scale is arbitrary.
    """
    sigma = fwhm_ev / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    grid_nm = [lo_nm + (hi_nm - lo_nm) * i / (n - 1) for i in range(n)]
    curve = []
    for nm in grid_nm:
        e = EV2NM / nm
        y = sum(s["f"] * math.exp(-((e - s["energy_eV"]) ** 2) / (2 * sigma ** 2))
                for s in states)
        curve.append(y)
    return grid_nm, curve


def band_occupancy(states, fwhm_ev):
    """How many transitions actually sit under the main band?

    Defines the band as lowest-bright-state energy +/- FWHM and counts the
    states inside it. This is the quantitative version of the post's claim,
    and it is deliberately conservative: only states with non-negligible
    oscillator strength count as contributing.
    """
    bright = [s for s in states if s["bright"]]
    if not bright:
        return None
    low = min(bright, key=lambda s: s["energy_eV"])
    e0 = low["energy_eV"]
    inside = [s for s in states if abs(s["energy_eV"] - e0) <= fwhm_ev]
    inside_bright = [s for s in inside if s["bright"]]
    f_inside = sum(s["f"] for s in inside)
    f_total = sum(s["f"] for s in states)
    return {
        "band_center_eV": e0,
        "band_center_nm": low["wavelength_nm"],
        "band_halfwidth_eV": fwhm_ev,
        "n_states_under_band": len(inside),
        "n_bright_under_band": len(inside_bright),
        "states_under_band": [s["state"] for s in inside],
        "f_under_band": round(f_inside, 5),
        "f_total_all_states": round(f_total, 5),
        "f_fraction_outside_band": round(1.0 - f_inside / f_total, 4) if f_total else None,
    }


def state_gaps(states):
    """Absolute spacings between the low-lying states.

    The band-occupancy count depends on the +/-0.35 eV window, which is an
    inherited empirical convention rather than a computed width. These gaps do
    not depend on that choice at all: a reader who prefers a different band
    width can apply it to these numbers directly. The manifold argument should
    survive either way, so both are reported.
    """
    if len(states) < 2:
        return None
    gaps = {"s1_s2_gap_eV": round(states[1]["energy_eV"] - states[0]["energy_eV"], 4)}
    if len(states) >= 3:
        gaps["s1_s3_gap_eV"] = round(states[2]["energy_eV"] - states[0]["energy_eV"], 4)
    bright = [s for s in states if s["bright"]]
    if len(bright) >= 2:
        low = min(bright, key=lambda s: s["energy_eV"])
        nxt = min((s for s in bright if s["energy_eV"] > low["energy_eV"]),
                  key=lambda s: s["energy_eV"], default=None)
        if nxt:
            gaps["lowest_two_bright_gap_eV"] = round(
                nxt["energy_eV"] - low["energy_eV"], 4)
            gaps["lowest_two_bright_states"] = [low["state"], nxt["state"]]
    return gaps


def write_csvs(run, prefix, fwhm_ev):
    tag = f"{run['functional']}_{run['basis']}"
    sticks = os.path.join(HERE, "results", f"{prefix}_sticks_{tag}.csv")
    with open(sticks, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["state", "energy_eV", "wavelength_nm", "oscillator_strength",
                    "hole_particle_dist_ang", "type", "dominant"])
        for s in run["states"]:
            dom = "; ".join(f"{c['from']}->{c['to']} ({c['weight_pct']}%)"
                            for c in s["dominant"]) or "-"
            w.writerow([s["state"], s["energy_eV"], s["wavelength_nm"], s["f"],
                        s["hole_particle_dist_ang"], s["type"], dom])

    grid, curve = gaussian_curve(run["states"], fwhm_ev)
    curve_path = os.path.join(HERE, "results", f"{prefix}_curve_{tag}.csv")
    with open(curve_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wavelength_nm", f"intensity_arb_gaussian_fwhm_{fwhm_ev}eV_COSMETIC"])
        for nm, y in zip(grid, curve):
            w.writerow([round(nm, 3), round(y, 8)])
    return sticks, curve_path


def tikz_figure(runs, fwhm_ev, lo_nm=250.0, hi_nm=750.0, step_nm=4.0):
    """Emit a pgfplots block for the post: sticks under one apparent band.

    Generated rather than hand-transcribed so the figure cannot drift from the
    results. The caller places and captions it; this only produces coordinates.

    Sticks are oscillator strengths on the left axis. The envelope is scaled to
    the tallest stick and carries NO physical width information -- it exists to
    show that closely spaced transitions merge into one apparent band.
    """
    primary = next((r for r in runs if r["functional"] == "cam-b3lyp"), runs[0])
    states = [s for s in primary["states"] if lo_nm <= s["wavelength_nm"] <= hi_nm]
    if not states:
        return "% no states inside the plotted wavelength window\n"
    fmax = max(s["f"] for s in states) or 1.0

    grid, curve = gaussian_curve(primary["states"], fwhm_ev, lo_nm, hi_nm,
                                 int((hi_nm - lo_nm) / step_nm) + 1)
    cmax = max(curve) or 1.0
    scaled = [y / cmax * fmax for y in curve]

    ymax = fmax * 1.25
    lines = [
        "```tikzpicture",
        "\\begin{axis}[",
        "    width=14cm, height=9cm,",
        "    xlabel={wavelength (nm)},",
        "    ylabel={oscillator strength $f$},",
        f"    title={{DCDHF-Me2: {len(primary['states'])} singlet transitions "
        f"under one apparent band}},",
        f"    xmin={lo_nm:.0f}, xmax={hi_nm:.0f}, ymin=0, ymax={ymax:.3f},",
        "    grid=major,",
        "    grid style={line width=.2pt, draw=gray!40},",
        "    axis lines=left,",
        "    legend pos=north east,",
        "    legend style={draw=none, fill=white, fill opacity=0.85},",
        "    every axis label/.style={font=\\large},",
        "    every tick label/.style={font=\\large},",
        "    title style={font=\\large\\bfseries}",
        "]",
        "\\addplot[thick, color=blue!60!black] coordinates {",
    ]
    row = []
    for nm, y in zip(grid, scaled):
        row.append(f"({nm:.0f},{y:.4f})")
        if len(row) == 7:
            lines.append("".join(["  "] + [r + " " for r in row]).rstrip())
            row = []
    if row:
        lines.append("".join(["  "] + [r + " " for r in row]).rstrip())
    lines.append("};")
    lines.append("\\addplot[ycomb, thick, color=red!70!black, mark=*, "
                 "mark size=1.2pt] coordinates {")
    lines.append("  " + " ".join(f"({s['wavelength_nm']:.0f},{s['f']:.4f})"
                                 for s in states))
    lines.append("};")
    lines.append(f"\\legend{{envelope (cosmetic, {fwhm_ev} eV FWHM), "
                 f"computed transitions}}")
    for s in states:
        if s["f"] >= 0.02:
            lines.append(f"\\node[font=\\small, anchor=south] at "
                         f"(axis cs:{s['wavelength_nm']:.0f},{s['f'] + ymax * 0.03:.4f}) "
                         f"{{S$_{{{s['state']}}}$}};")
    lines.append("\\end{axis}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def markdown_table(run):
    rows = ["| State | E (eV) | λ (nm) | f | Δr(h–e) (Å) | Character | Dominant excitation |",
            "|---:|---:|---:|---:|---:|---|---|"]
    for s in run["states"]:
        dom = "; ".join(f"{c['from']}→{c['to']} ({c['weight_pct']}%)"
                        for c in s["dominant"]) or "—"
        rows.append("| S%d | %.2f | %.0f | %.4f | %.2f | %s | %s |" %
                    (s["state"], s["energy_eV"], s["wavelength_nm"], s["f"],
                     s["hole_particle_dist_ang"], s["type"], dom))
    return "\n".join(rows)


def geometry_comparison(opt_xyz):
    """UFF starting structure vs. the B3LYP minimum.

    The optimization is not a formality for a conjugated push-pull dye: the
    force field and DFT disagree about how coplanar the donor and acceptor
    rings are, and that twist controls the donor-acceptor conjugation the whole
    spectrum depends on.
    """
    sym_u, xyz_u, _ = read_xyz(DEFAULT_GEOM)
    verify_topology(sym_u, xyz_u)
    start = geometry_report(xyz_u)
    if not os.path.exists(opt_xyz):
        return {"start_uff": start, "optimized": None,
                "note": f"{os.path.basename(opt_xyz)} not found; optimization incomplete"}
    sym_o, xyz_o, comment = read_xyz(opt_xyz)
    verify_topology(sym_o, xyz_o)
    opt = geometry_report(xyz_o)
    return {
        "start_uff": start,
        "optimized": opt,
        "optimized_comment": comment,
        "interring_twist_change_deg": round(
            start["interring_twist_deg"] - opt["interring_twist_deg"], 2),
        "amine_pyramidalization_change_deg": round(
            start["amine_pyramidalization_deg"] - opt["amine_pyramidalization_deg"], 2),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fwhm-ev", type=float, default=DEFAULT_FWHM_EV)
    p.add_argument("--out-prefix", default="spectra")
    p.add_argument("--optimized-geometry",
                   default=os.path.join(HERE, "geometry", "dcdhf-me2-def2-svp-opt.xyz"))
    args = p.parse_args()

    runs = load_states()
    summary = {"broadening_note": (
        "The Gaussian FWHM below is applied by hand for display only. It is not "
        "a computed line shape: no vibronic (Franck-Condon) or inhomogeneous "
        "broadening was calculated. Band widths in the figure carry no physical "
        "information; positions and oscillator strengths do."),
        "broadening_fwhm_eV_cosmetic": args.fwhm_ev,
        "geometry": geometry_comparison(args.optimized_geometry),
        "runs": []}

    for run in runs:
        sticks, curve = write_csvs(run, args.out_prefix, args.fwhm_ev)
        occ = band_occupancy(run["states"], args.fwhm_ev)
        summary["runs"].append({
            "functional": run["functional"], "basis": run["basis"],
            "method": run["method"], "n_basis_functions": run["n_basis_functions"],
            "manifold": run["manifold"], "band_occupancy": occ,
            "state_gaps": state_gaps(run["states"]),
            "sticks_csv": os.path.relpath(sticks, HERE),
            "curve_csv": os.path.relpath(curve, HERE),
        })
        print(f"[{run['functional']}/{run['basis']}] "
              f"{occ['n_states_under_band']} states ({occ['n_bright_under_band']} bright) "
              f"within +/-{args.fwhm_ev} eV of the {occ['band_center_nm']:.0f} nm band; "
              f"{occ['f_fraction_outside_band']:.1%} of total f lies outside it")

    with open(os.path.join(HERE, "results", "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)

    with open(os.path.join(HERE, "results", "tables.md"), "w") as fh:
        fh.write("<!-- generated by postprocess.py; do not edit by hand -->\n")
        for run in runs:
            fh.write(f"\n### {run['functional'].upper()}/{run['basis']} "
                     f"({run['method']})\n\n{markdown_table(run)}\n")
    fig_path = os.path.join(HERE, "results", "figure_manifold.tikz")
    with open(fig_path, "w") as fh:
        fh.write("% generated by postprocess.py -- do not hand-edit coordinates.\n"
                 "% Paste into the post as a ```tikzpicture block and add a\n"
                 "% numbered caption. The envelope is cosmetic: it carries no\n"
                 "% computed width information.\n")
        fh.write(tikz_figure(runs, args.fwhm_ev))
    print("wrote results/summary.json, results/tables.md, results/figure_manifold.tikz")


if __name__ == "__main__":
    main()
