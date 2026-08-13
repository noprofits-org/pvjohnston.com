#!/usr/bin/env python
"""
Turn the per-molecule state lists into the post's figure data and tables.

Two molecules are asked the same question and give opposite answers:

  dcdhf-me2 - an engineered single-molecule fluorophore. Its visible band is
              ONE transition carrying most of the oscillator strength, so the
              two-level idealization is earned rather than assumed.
  benzene   - whose strongly allowed band is a symmetry-degenerate PAIR: one
              apparent band, two transitions, strength split between them.

The figure has to make that contrast visible, so the stick spectrum is the
primary data and the smooth curve is secondary.

IMPORTANT, and stated in every artifact this writes: the broadened curve is
NOT a computed line shape. It is a Gaussian of fixed width applied by hand,
the same cosmetic convention used in calcs/uvvis-pushpull and in the 2025
DCDHF work. Real band width has vibronic and inhomogeneous contributions that
nothing here computes. The curve exists to show that closely spaced sticks
merge into one apparent band -- it is not evidence about width.

Usage: postprocess.py [--fwhm-ev 0.35]
"""
import os, json, glob, argparse, csv, math, hashlib, platform, datetime, sys

# run_tddft owns the geometry helpers and the topology check; importing them
# keeps one definition of each diagnostic rather than two that can drift.
# It pulls in psi4, which costs a few seconds here and nothing else.
from run_tddft import (read_xyz, geometry_report, verify_topology, MOLECULES,
                       manifold_summary)

HERE = os.path.dirname(os.path.abspath(__file__))
EV2NM = 1239.841984

# The hand-applied width. Matches the push-pull leg and the 2025 DCDHF figure
# so the spectra are visually comparable. Cosmetic, not computed.
DEFAULT_FWHM_EV = 0.35

# Which molecule the headline metrics come from, and which functional. Both
# fixed in advance: CAM-B3LYP because range separation is the a priori right
# choice for charge transfer, not because of how the numbers turned out.
PRIMARY_MOLECULE = "dcdhf-me2"
PRIMARY_FUNCTIONAL = "cam-b3lyp"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def provenance_block(input_paths):
    """Record what produced summary.json and from exactly which bytes.

    Without this, summary.json is the one link in the chain that asserts its
    numbers rather than evidencing them: metrics.json fingerprints summary.json,
    and each states file records its own environment, but nothing tied the two
    together.
    """
    return {
        "generator": "research/dcdhf-me2-transitions/postprocess.py",
        "command": "python postprocess.py " + " ".join(sys.argv[1:]),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                 .isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "inputs": [{"path": os.path.relpath(p, HERE), "sha256": sha256_of(p)}
                   for p in sorted(input_paths)],
    }


def slug_of(run):
    """Molecule slug for a results file, tolerating records written before
    molecule_slug was added to the schema."""
    if run.get("molecule_slug"):
        return run["molecule_slug"]
    name = run.get("molecule", "").lower()
    for slug, spec in MOLECULES.items():
        if spec["name"].lower() == name:
            return slug
    raise SystemExit(f"cannot identify molecule for record {run.get('molecule')!r}")


def load_states():
    """Load every states_*.json, grouped by molecule slug.

    Also returns the paths, so the provenance block can fingerprint exactly
    the bytes this run consumed.
    """
    by_mol, paths = {}, []
    for path in sorted(glob.glob(os.path.join(HERE, "results", "states_*.json"))):
        with open(path) as fh:
            run = json.load(fh)
        by_mol.setdefault(slug_of(run), []).append(run)
        paths.append(path)
    if not by_mol:
        raise SystemExit("no results/states_*.json found -- run run_tddft.py excite first")
    return by_mol, paths


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
    and the window is deliberately the inherited cosmetic width rather than
    one chosen once the numbers were visible.
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
        "f_fraction_under_band": round(f_inside / f_total, 4) if f_total else None,
        "f_fraction_outside_band": round(1.0 - f_inside / f_total, 4) if f_total else None,
    }


def state_gaps(states):
    """Absolute spacings between the low-lying states.

    The band-occupancy count depends on the +/-0.35 eV window, an inherited
    empirical convention rather than a computed width. These gaps do not depend
    on that choice at all, so a reader who prefers a different band width can
    apply it directly. The argument should survive either way.
    """
    if len(states) < 2:
        return None
    gaps = {"s1_s2_gap_eV": round(states[1]["energy_eV"] - states[0]["energy_eV"], 4)}
    if len(states) >= 3:
        gaps["s1_s3_gap_eV"] = round(states[2]["energy_eV"] - states[0]["energy_eV"], 4)
    bright = [s for s in states if s["bright"]]
    if len(bright) >= 2:
        # Order by (energy, state index) and take the first two. Selecting the
        # partner with a strict energy > comparison silently SKIPS an exactly
        # degenerate state -- which for benzene meant reporting the E1u pair as
        # one state carrying 98% of the strength, the exact opposite of the
        # 50/50 split that is the whole reason benzene is in this experiment.
        ordered = sorted(bright, key=lambda s: (s["energy_eV"], s["state"]))
        low, nxt = ordered[0], ordered[1]
        if nxt:
            gaps["lowest_two_bright_gap_eV"] = round(
                nxt["energy_eV"] - low["energy_eV"], 4)
            gaps["lowest_two_bright_states"] = [low["state"], nxt["state"]]
            gaps["lowest_two_bright_f"] = [low["f"], nxt["f"]]
            # How evenly the two lowest bright states share their strength.
            # 0.5 is an even split (benzene's degenerate pair); near 1.0 means
            # one transition dominates (DCDHF-Me2).
            tot = low["f"] + nxt["f"]
            gaps["lowest_bright_f_share"] = round(low["f"] / tot, 4) if tot else None
    return gaps


HA2EV = 27.211386245988


def dipole_strength_au(state):
    """|mu|^2 in atomic units from the oscillator strength and energy.

    f = (2/3) dE |mu|^2  =>  |mu|^2 = 3f / (2 dE), with dE in hartree.

    Why this belongs beside f rather than instead of it: f carries an energy
    factor, so a high-energy transition can post a larger f on a smaller
    transition dipole. Benzene's band edges out the dye's in f while the dye's
    single transition has roughly twice the dipole strength of benzene's whole
    band -- reading only f inverts which molecule is the stronger absorber per
    photon it can absorb.
    """
    de_ha = state["energy_eV"] / HA2EV
    if de_ha <= 0:
        return 0.0
    return 3.0 * state["f"] / (2.0 * de_ha)


def dipole_summary(states):
    """Per-molecule dipole strengths, and how concentrated they are.

    The share of total |mu|^2 in the lowest bright state is the sharper
    statement of this experiment's finding than the oscillator-strength share,
    precisely because it removes the energy weighting.
    """
    per = [{"state": s["state"], "dipole_strength_au": round(dipole_strength_au(s), 4)}
           for s in states]
    total = sum(dipole_strength_au(s) for s in states)
    bright = [s for s in states if s["bright"]]
    out = {"per_state": per, "total_au": round(total, 4)}
    if bright and total > 0:
        low = min(bright, key=lambda s: (s["energy_eV"], s["state"]))
        d_low = dipole_strength_au(low)
        out["lowest_bright_state"] = low["state"]
        out["lowest_bright_dipole_strength_au"] = round(d_low, 4)
        out["lowest_bright_share"] = round(d_low / total, 4)
    return out


def multiplet_summary(states, tol_ev=1e-3):
    """Degenerate groups of two or more states, and what they carry together.

    A multiplet is one apparent line in a spectrum, so its combined oscillator
    strength -- not its largest member -- is what the band absorbs. Reporting
    the members separately and never their sum is how a degenerate pair ends up
    looking weaker than it is.
    """
    groups = [g for g in degenerate_groups(states, tol_ev) if len(g) > 1]
    out = []
    for g in groups:
        out.append({
            "energy_eV": g[0]["energy_eV"],
            "wavelength_nm": g[0]["wavelength_nm"],
            "states": [s["state"] for s in g],
            "multiplicity": len(g),
            "f_each": [s["f"] for s in g],
            "f_total": round(sum(s["f"] for s in g), 5),
            # Band intensity goes as the SUM over the multiplet in either
            # measure: the members are separate transitions that happen to
            # coincide in energy, not one transition counted twice.
            "dipole_strength_each_au": [round(dipole_strength_au(s), 4) for s in g],
            "dipole_strength_total_au": round(
                sum(dipole_strength_au(s) for s in g), 4),
            "bright": any(s["bright"] for s in g),
        })
    return out


def write_csvs(run, slug, fwhm_ev):
    tag = f"{slug}_{run['functional']}_{run['basis']}"
    sticks = os.path.join(HERE, "results", f"spectra_sticks_{tag}.csv")
    with open(sticks, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["state", "energy_eV", "wavelength_nm", "oscillator_strength",
                    "hole_particle_dist_ang", "type", "dominant"])
        for s in run["states"]:
            dom = "; ".join(f"{c['from']}->{c['to']} ({c['weight_pct']}%)"
                            for c in s["dominant"]) or "-"
            w.writerow([s["state"], s["energy_eV"], s["wavelength_nm"], s["f"],
                        s["hole_particle_dist_ang"], s["type"], dom])

    lo, hi = spectrum_window(run["states"])
    grid, curve = gaussian_curve(run["states"], fwhm_ev, lo, hi)
    curve_path = os.path.join(HERE, "results", f"spectra_curve_{tag}.csv")
    with open(curve_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wavelength_nm", f"intensity_arb_gaussian_fwhm_{fwhm_ev}eV_COSMETIC"])
        for nm, y in zip(grid, curve):
            w.writerow([round(nm, 3), round(y, 8)])
    return sticks, curve_path


def spectrum_window(states):
    """Wavelength range covering the computed states with a margin.

    Benzene's band sits near 7 eV (~175 nm) and DCDHF-Me2's near 3.3 eV
    (~375 nm), so a single hard-coded window would clip one of them.
    """
    nm = [s["wavelength_nm"] for s in states]
    lo = max(80.0, min(nm) - 60.0)
    hi = max(nm) + 120.0
    return lo, hi


def geometry_comparison(slug):
    """Starting structure vs. the B3LYP minimum, per molecule."""
    spec = MOLECULES[slug]
    start_path = os.path.join(HERE, "geometry", spec["geometry"])
    opt_path = os.path.join(HERE, "geometry", f"{slug}-def2-svp-opt.xyz")
    if not os.path.exists(start_path):
        return None
    sym_u, xyz_u, _ = read_xyz(start_path)
    verify_topology(sym_u, xyz_u, slug)
    start = geometry_report(xyz_u, slug)
    if not os.path.exists(opt_path):
        return {"start": start, "optimized": None,
                "note": f"{os.path.basename(opt_path)} not found; optimization incomplete"}
    sym_o, xyz_o, comment = read_xyz(opt_path)
    verify_topology(sym_o, xyz_o, slug)
    opt = geometry_report(xyz_o, slug)
    out = {"start": start, "optimized": opt, "optimized_comment": comment,
           "start_geometry": os.path.relpath(start_path, HERE)}
    # Deltas for the diagnostics both structures share.
    for key in start:
        if isinstance(start[key], (int, float)) and key in opt:
            out[f"delta_{key}"] = round(start[key] - opt[key], 4)
    return out


def tikz_figure(runs, slug, fwhm_ev, step_nm=2.0):
    """Emit a pgfplots block: sticks under one apparent band.

    Generated rather than hand-transcribed so the figure cannot drift from the
    results. The caller places and captions it; this only produces coordinates.

    Sticks are oscillator strengths on the left axis. The envelope is scaled to
    the tallest stick and carries NO physical width information -- it exists to
    show whether closely spaced transitions merge into one apparent band.
    """
    primary = next((r for r in runs if r["functional"] == PRIMARY_FUNCTIONAL), runs[0])
    states = primary["states"]
    lo_nm, hi_nm = spectrum_window(states)
    fmax = max((s["f"] for s in states), default=0.0) or 1.0

    n = max(2, int((hi_nm - lo_nm) / step_nm) + 1)
    grid, curve = gaussian_curve(states, fwhm_ev, lo_nm, hi_nm, n)
    cmax = max(curve) or 1.0
    scaled = [y / cmax * fmax for y in curve]

    ymax = fmax * 1.25
    name = primary["molecule"]
    lines = [
        "```tikzpicture",
        "\\begin{axis}[",
        "    width=14cm, height=9cm,",
        "    xlabel={wavelength (nm)},",
        "    ylabel={oscillator strength $f$},",
        f"    title={{{name}: {len(states)} computed singlet transitions}},",
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
        row.append(f"({nm:.1f},{y:.4f})")
        if len(row) == 6:
            lines.append("  " + " ".join(row))
            row = []
    if row:
        lines.append("  " + " ".join(row))
    lines.append("};")
    lines.append("\\addplot[ycomb, thick, color=red!70!black, mark=*, "
                 "mark size=1.2pt] coordinates {")
    lines.append("  " + " ".join(f"({s['wavelength_nm']:.1f},{s['f']:.4f})"
                                 for s in states))
    lines.append("};")
    lines.append(f"\\legend{{envelope (cosmetic, {fwhm_ev} eV FWHM), "
                 f"computed transitions}}")
    for s in states:
        # Label states carrying at least 5% of the strongest transition, so
        # the annotation density adapts to molecules with very different fmax.
        if s["f"] >= 0.05 * fmax:
            lines.append(f"\\node[font=\\small, anchor=south] at "
                         f"(axis cs:{s['wavelength_nm']:.1f},{s['f'] + ymax * 0.03:.4f}) "
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


def post_table(run):
    """Table 1 for the post: no hole-particle distance, no auto Character.

    The centroid-based CT label is unreliable for this dye -- it calls S1
    pi->pi* because both frontier orbitals are delocalized over the whole
    conjugated backbone -- and publishing a column only to disavow it in the
    same post is worse than not publishing it. Charge-transfer character is
    argued in prose from the functional shift instead. The full table, with
    both columns, stays in tables.md as the complete record.

    Generated rather than hand-stripped: transcription is how a table drifts
    from the data it claims to report.
    """
    rows = ["| State | E (eV) | λ (nm) | f | Dominant excitation |",
            "|---:|---:|---:|---:|---|"]
    for s in run["states"]:
        dom = "; ".join(f"{c['from']}→{c['to']} ({c['weight_pct']}%)"
                        for c in s["dominant"]) or "—"
        rows.append("| S%d | %.2f | %.0f | %.4f | %s |" %
                    (s["state"], s["energy_eV"], s["wavelength_nm"], s["f"], dom))
    return "\n".join(rows)


def tikz_comparison(by_mol, fwhm_ev):
    """Two panels on one shared ENERGY axis: f on top, |mu|^2 below.

    The second panel exists because the first one, alone, misleads. Oscillator
    strength carries a factor of the transition energy, so benzene's band --
    at more than twice the dye's excitation energy -- edges the dye out in f
    while having roughly HALF its transition dipole strength. A reader taking
    the f panel as "which molecule absorbs more strongly" gets the ranking
    backwards, and that is a misreading the picture invited rather than the
    reader's error.

    Plotting both makes the inversion the teaching point: the ranking flips
    between panels, and the reason is the energy factor in f = (2/3)dE|mu|^2.

    Energy rather than wavelength on x because the bands are far apart (the dye
    near 3.3 eV, benzene near 7.1 eV) and a shared eV axis holds both without
    squeezing either into the margin.

    Deliberately NOT normalized, in either panel. The quantities are directly
    comparable as computed, and normalizing each molecule to its own maximum
    would erase exactly the comparison the figure exists to make.

    Molar absorptivity was considered as a third panel and rejected: a peak
    epsilon needs a band width, this experiment computes none, and deriving one
    from the cosmetic FWHM would manufacture experiment-comparable numbers out
    of an arbitrary display parameter.
    """
    # Upper stack segments need enough contrast against white to read as part
    # of the stick rather than as background -- the whole point of the stack is
    # that the reader sees two states, so a segment that fades out defeats it.
    colors = {PRIMARY_MOLECULE: ("red!70!black", "red!55!white"),
              "benzene": ("blue!65!black", "blue!50!white")}
    series, emax = [], 0.0
    for slug in sorted(by_mol):
        run = next((r for r in by_mol[slug] if r["functional"] == PRIMARY_FUNCTIONAL),
                   by_mol[slug][0])
        # No filter. A dark state draws as a marker on the axis, which is
        # honest; the previous f > 1e-4 cut silently removed 8 of benzene's 12
        # states from a figure whose legend says "computed transitions".
        groups = degenerate_groups(run["states"])
        if not groups:
            continue
        emax = max(emax, max(g[0]["energy_eV"] for g in groups))
        series.append((slug, run["molecule"], groups))
    if len(series) < 2:
        return "% fewer than two molecules with bright states; no comparison figure\n"

    panels = [
        {"key": lambda s: s["f"],
         "ylabel": "oscillator strength $f$",
         "name": "fpanel", "letter": "A", "fmt": "{:.4f}"},
        {"key": dipole_strength_au,
         "ylabel": r"dipole strength $|\mu|^2$ (a.u.)",
         "name": "mupanel", "letter": "B", "fmt": "{:.4f}"},
    ]
    lines = ["```tikzpicture"]
    callouts = []
    for pi, panel in enumerate(panels):
        # Each panel is scaled to its OWN tallest stack. Sharing a y scale
        # across two different physical quantities would be meaningless.
        ymax = max(sum(panel["key"](s) for s in g)
                   for _, _, groups in series for g in groups) * 1.25
        lines += _panel_axis(pi, panel, emax, ymax, series, colors, callouts)
    lines.append("```")
    for name, n, e, tot, letter, label in callouts:
        lines.append(f"% callout {letter}: {name}, {n} degenerate states at "
                     f"{e:.3f} eV, stacked to a band total of {label} = {tot:.4f}")
    return "\n".join(lines) + "\n"


def _panel_axis(pi, panel, emax, ymax, series, colors, callouts):
    """One axis environment of the two-panel comparison figure.

    The panels are separate axis environments positioned relative to each
    other rather than a groupplot: the site's TikZ preamble loads pgfplots but
    not the groupplots library, so relative anchoring is what will actually
    compile here.
    """
    top = pi == 0
    lines = ["\\begin{axis}[", f"    name={panel['name']},"]
    if not top:
        lines.append("    at={(fpanel.below south west)}, anchor=north west,")
    lines += [
        "    width=14cm, height=6.4cm,",
        f"    ylabel={{{panel['ylabel']}}},",
        f"    xmin=2.5, xmax={emax + 0.5:.1f}, ymin=0, ymax={ymax:.3f},",
        "    grid=major,",
        "    grid style={line width=.2pt, draw=gray!40},",
        "    axis lines=left,",
        "    every axis label/.style={font=\\large},",
        "    every tick label/.style={font=\\large},",
    ]
    if top:
        lines += [
            "    title={One apparent band, one transition or two},",
            "    title style={font=\\large\\bfseries},",
            "    xticklabels={},",
            "    legend pos=north west,",
            "    legend style={draw=none, fill=white, fill opacity=0.85},",
        ]
    else:
        lines.append("    xlabel={excitation energy (eV)},")
    lines.append("]")

    for slug, name, groups in series:
        dark, light = colors.get(slug, ("black", "gray"))
        if top:
            lines.append(f"\\addlegendimage{{ycomb, very thick, color={dark}, "
                         f"mark=*, mark size=1.4pt}}")
            lines.append(f"\\addlegendentry{{{name}}}")
        for g in groups:
            e = g[0]["energy_eV"]
            cum = 0.0
            for i, s in enumerate(g):
                v = panel["key"](s)
                if v <= 0.0:
                    continue
                col = dark if i == 0 else light
                lines.append(f"\\draw[very thick, color={col}] "
                             f"(axis cs:{e:.3f},{cum:.4f}) -- "
                             f"(axis cs:{e:.3f},{cum + v:.4f});")
                cum += v
            lines.append(f"\\addplot[only marks, color={dark}, mark=*, "
                         f"mark size=1.4pt, forget plot] coordinates "
                         f"{{({e:.3f},{cum:.4f})}};")
            if len([s for s in g if panel["key"](s) > 0.0]) > 1:
                div = panel["key"](g[0])
                lines.append(f"\\draw[black, thick] (axis cs:{e - 0.06:.3f},{div:.4f}) -- "
                             f"(axis cs:{e + 0.06:.3f},{div:.4f});")
                lines.append(f"\\node[font=\\small\\bfseries, anchor=west] at "
                             f"(axis cs:{e + 0.10:.3f},{div:.4f}) "
                             f"{{{panel['letter']}}};")
                callouts.append((name, len(g), e, cum, panel["letter"],
                                 "f" if top else "|mu|^2"))
    lines.append("\\end{axis}")
    return lines


def degenerate_groups(states, tol_ev=1e-3):
    """Group states that are degenerate within `tol_ev` (default 1 meV).

    Symmetry-required degeneracies come out of the solver equal to many
    decimals, so the tolerance only has to absorb numerical noise. Grouping is
    what lets the figure draw a multiplet as one stick carrying the band's real
    strength instead of overlapping members that hide each other.
    """
    out = []
    for s in sorted(states, key=lambda s: (s["energy_eV"], s["state"])):
        if out and abs(s["energy_eV"] - out[-1][0]["energy_eV"]) <= tol_ev:
            out[-1].append(s)
        else:
            out.append([s])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fwhm-ev", type=float, default=DEFAULT_FWHM_EV)
    args = p.parse_args()

    by_mol, state_paths = load_states()
    summary = {"provenance": provenance_block(state_paths),
               "broadening_note": (
        "The Gaussian FWHM below is applied by hand for display only. It is not "
        "a computed line shape: no vibronic (Franck-Condon) or inhomogeneous "
        "broadening was calculated. Band widths in the figures carry no physical "
        "information; positions and oscillator strengths do."),
        "broadening_fwhm_eV_cosmetic": args.fwhm_ev,
        "primary_molecule": PRIMARY_MOLECULE,
        "primary_functional": PRIMARY_FUNCTIONAL,
        "molecules": {}}

    for slug, runs in sorted(by_mol.items()):
        entry = {"name": runs[0]["molecule"], "formula": runs[0].get("formula"),
                 "geometry": geometry_comparison(slug), "runs": []}
        for run in sorted(runs, key=lambda r: r["functional"]):
            sticks, curve = write_csvs(run, slug, args.fwhm_ev)
            occ = band_occupancy(run["states"], args.fwhm_ev)
            entry["runs"].append({
                "functional": run["functional"], "basis": run["basis"],
                "method": run["method"], "n_basis_functions": run["n_basis_functions"],
                # Recomputed from the state list rather than copied from the
                # states file. `manifold` is a DERIVED aggregate written at
                # compute time, so a file produced by an older harness carries
                # that harness's arithmetic -- including the strict `>` that
                # under-reported benzene's f_above_lowest_bright by 20x.
                # Primary data (energies, f, eigenvectors) is never recomputed
                # here; only quantities derived from it.
                "manifold": manifold_summary(run["states"]),
                "manifold_as_recorded": run["manifold"],
                "band_occupancy": occ,
                "state_gaps": state_gaps(run["states"]),
                "degenerate_multiplets": multiplet_summary(run["states"]),
                "dipole_strengths": dipole_summary(run["states"]),
                "tdscf_effective": run.get("tdscf_effective"),
                "sticks_csv": os.path.relpath(sticks, HERE),
                "curve_csv": os.path.relpath(curve, HERE),
            })
            if occ:
                print(f"[{slug} {run['functional']}] "
                      f"{occ['n_states_under_band']} states "
                      f"({occ['n_bright_under_band']} bright) within "
                      f"+/-{args.fwhm_ev} eV of the {occ['band_center_nm']:.0f} nm band; "
                      f"{occ['f_fraction_outside_band']:.1%} of total f outside it")
        summary["molecules"][slug] = entry

        fig = os.path.join(HERE, "results", f"figure_manifold_{slug}.tikz")
        with open(fig, "w") as fh:
            fh.write("% generated by postprocess.py -- do not hand-edit coordinates.\n"
                     "% Paste into the post as a ```tikzpicture block and add a\n"
                     "% numbered caption. The envelope is cosmetic: it carries no\n"
                     "% computed width information.\n")
            fh.write(tikz_figure(runs, slug, args.fwhm_ev))

    with open(os.path.join(HERE, "results", "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)

    with open(os.path.join(HERE, "results", "tables.md"), "w") as fh:
        fh.write("<!-- generated by postprocess.py; do not edit by hand -->\n")
        for slug, entry in sorted(summary["molecules"].items()):
            fh.write(f"\n## {entry['name']} ({entry['formula']})\n")
            for run in sorted(by_mol[slug], key=lambda r: r["functional"]):
                fh.write(f"\n### {run['functional'].upper()}/{run['basis']} "
                         f"({run['method']})\n\n{markdown_table(run)}\n")
    with open(os.path.join(HERE, "results", "figure_comparison.tikz"), "w") as fh:
        fh.write("% generated by postprocess.py -- do not hand-edit coordinates.\n")
        fh.write(tikz_comparison(by_mol, args.fwhm_ev))

    with open(os.path.join(HERE, "results", "tables_post.md"), "w") as fh:
        fh.write("<!-- generated by postprocess.py; paste as-is, do not restrip "
                 "columns by hand -->\n")
        for slug, entry in sorted(summary["molecules"].items()):
            run = next((r for r in by_mol[slug]
                        if r["functional"] == PRIMARY_FUNCTIONAL), None)
            if run:
                fh.write(f"\n### {entry['name']} — {run['functional'].upper()}/"
                         f"{run['basis']}\n\n{post_table(run)}\n")
    print("wrote results/summary.json, results/tables.md, results/tables_post.md, "
          "results/figure_manifold_<molecule>.tikz, results/figure_comparison.tikz")


if __name__ == "__main__":
    main()
