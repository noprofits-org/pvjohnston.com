#!/usr/bin/env python
"""
Compute leg for the DCDHF-Me2 excited-state manifold.

The question is how many electronic transitions sit under what a spectrometer
reports as one absorption band, so the deliverable is the *manifold*: every
computed singlet with its oscillator strength, not just the bright one.

Two independent stages, because the optimization is expensive and the TD-DFT
leg is the part that can run out of memory:

    run_tddft.py optimize                      # -> geometry/dcdhf-me2-<basis>-opt.xyz
    run_tddft.py excite --functional b3lyp     # -> results/states_b3lyp_<basis>.json
    run_tddft.py excite --functional cam-b3lyp

Each `excite` call is a separate process reading the optimized geometry off
disk, so a failure in one functional or basis costs only that call. Nothing
here overwrites a previous stage's output unless --force is given.

Recipe follows calcs/uvvis-pushpull/run_one.py (B3LYP/def2-SVP optimization,
full-RPA TD-DFT at def2-TZVP, >=10 singlets) so the numbers stay comparable to
the published push-pull set. Defaults for memory and threads are sized for a
15 GB / 8-core machine, NOT inherited from that script -- see --help.
"""
import os, sys, json, math, argparse, datetime, platform

HERE = os.path.dirname(os.path.abspath(__file__))
# gotcha #1 (inherited from run_one.py): PSI_SCRATCH must be set before import psi4
os.environ.setdefault("PSI_SCRATCH", os.path.join(HERE, "scratch"))
os.makedirs(os.environ["PSI_SCRATCH"], exist_ok=True)
for sub in ("geometry", "results", "logs"):
    os.makedirs(os.path.join(HERE, sub), exist_ok=True)

import numpy as np
import psi4
from psi4.driver.procrouting.response.scf_response import tdscf_excitations

HA2EV = 27.211386245988
EV2NM = 1239.841984
EV2CM = 8065.543937
BOHR2ANG = 0.529177210903

DEFAULT_GEOM = os.path.join(HERE, "geometry", "dcdhf-me2-uff.xyz")

# Atom indices into the input ordering (0-based). Verified at runtime by
# verify_topology() -- psi4 keeps input order under no_reorient/no_com, so
# these stay valid through the optimization.
DONOR_RING = [1, 2, 4, 6, 7, 9]        # dimethylaniline ring carbons
ACCEPTOR_RING = [19, 20, 25, 24, 22]   # 2,5-dihydrofuran ring (C,C,C,O,C)
AMINE_N = 0
AMINE_SUBS = [1, 11, 12]               # ring C + two N-methyl C
NITRILES = [(21, 23), (35, 37), (36, 38)]  # (C, N) of the three C#N groups
LINK_BOND = (6, 19)                    # aryl -- dihydrofuran single bond

# Benzene, for the contrast case: its strongly allowed band is a symmetry-
# degenerate E1u PAIR, so one apparent band is genuinely two transitions.
# D6h, so the only geometry diagnostics worth recording are ring planarity
# and the C-C/C-H bond lengths.
BENZENE_RING = [0, 1, 2, 3, 4, 5]

MOLECULES = {
    "dcdhf-me2": {
        "name": "DCDHF-Me2",
        "formula": {"C": 18, "H": 16, "N": 4, "O": 1},
        "geometry": "dcdhf-me2-uff.xyz",
        "charge": 0, "multiplicity": 1,
        "diagnostics": "dcdhf",
    },
    "benzene": {
        "name": "benzene",
        "formula": {"C": 6, "H": 6},
        "geometry": "benzene-ideal.xyz",
        "charge": 0, "multiplicity": 1,
        "diagnostics": "benzene",
    },
}


# ---------------------------------------------------------------- geometry io
def read_xyz(path):
    """Read a standard xyz. Returns (symbols, coords_angstrom, comment)."""
    with open(path) as fh:
        lines = fh.read().splitlines()
    n = int(lines[0].split()[0])
    comment = lines[1].strip()
    symbols, coords = [], []
    for ln in lines[2:2 + n]:
        parts = ln.split()
        symbols.append(parts[0])
        coords.append([float(x) for x in parts[1:4]])
    if len(symbols) != n:
        raise ValueError(f"{path}: header says {n} atoms, found {len(symbols)}")
    return symbols, np.asarray(coords), comment


def write_xyz(path, symbols, coords, comment):
    with open(path, "w") as fh:
        fh.write("%d\n%s\n" % (len(symbols), comment.replace("\n", " ")))
        for s, (x, y, z) in zip(symbols, coords):
            fh.write("%-2s %14.8f %14.8f %14.8f\n" % (s, x, y, z))


def psi4_geometry_block(symbols, coords, charge=0, multiplicity=1):
    lines = ["%d %d" % (charge, multiplicity)]
    lines += ["%s %.8f %.8f %.8f" % (s, x, y, z) for s, (x, y, z) in zip(symbols, coords)]
    # no_reorient/no_com keep the input atom order and frame, which the index
    # tables above depend on
    lines += ["symmetry c1", "units angstrom", "no_reorient", "no_com"]
    return "\n".join(lines)


def verify_topology(symbols, coords, molecule="dcdhf-me2"):
    """Fail loudly if the structure is not the molecule we think it is.

    Cheap insurance: the diagnostics are meaningless if the atom order ever
    changes, and a silently wrong twist angle is worse than a crash. Generic
    checks (formula, no overlapping atoms, single connected fragment) run for
    every molecule; the index-table checks are DCDHF-Me2-specific and run only
    for it.
    """
    def d(i, j):
        return float(np.linalg.norm(coords[i] - coords[j]))

    spec = MOLECULES[molecule]
    problems = []

    formula = {}
    for s in symbols:
        formula[s] = formula.get(s, 0) + 1
    if formula != spec["formula"]:
        problems.append(f"expected {spec['formula']}, got {formula}")

    # Generic sanity, molecule-independent: no two atoms on top of each other,
    # and the structure is one connected fragment rather than dissociated bits.
    n = len(symbols)
    for i in range(n):
        for j in range(i + 1, n):
            if d(i, j) < 0.6:
                problems.append(f"atoms {i} and {j} are {d(i, j):.2f} A apart")
    seen, stack = {0}, [0]
    while stack:
        i = stack.pop()
        for j in range(n):
            if j not in seen and d(i, j) < 1.9:
                seen.add(j); stack.append(j)
    if len(seen) != n:
        problems.append(f"structure is not connected: {len(seen)}/{n} atoms "
                        f"reachable from atom 0")

    if spec["diagnostics"] != "dcdhf":
        if problems:
            raise SystemExit("topology check failed:\n  " + "\n  ".join(problems))
        return

    if symbols[AMINE_N] != "N":
        problems.append(f"atom {AMINE_N} should be the amine N, is {symbols[AMINE_N]}")
    for i in AMINE_SUBS:
        if symbols[i] != "C" or not 1.2 < d(AMINE_N, i) < 1.6:
            problems.append(f"amine substituent {i} ({symbols[i]}) at {d(AMINE_N, i):.2f} A")
    for i in DONOR_RING:
        if symbols[i] != "C":
            problems.append(f"donor ring atom {i} is {symbols[i]}, expected C")
    ring_syms = "".join(symbols[i] for i in ACCEPTOR_RING)
    if ring_syms != "CCCOC":
        problems.append(f"acceptor ring symbols {ring_syms}, expected CCCOC")
    for a, b in zip(ACCEPTOR_RING, ACCEPTOR_RING[1:] + ACCEPTOR_RING[:1]):
        if not 1.2 < d(a, b) < 1.7:
            problems.append(f"acceptor ring bond {a}-{b} = {d(a, b):.2f} A")
    for c, n in NITRILES:
        if symbols[c] != "C" or symbols[n] != "N":
            problems.append(f"nitrile ({c},{n}) is ({symbols[c]},{symbols[n]})")
        elif not 1.05 < d(c, n) < 1.30:
            problems.append(f"nitrile {c}#{n} = {d(c, n):.2f} A, not a triple bond")
    if not 1.3 < d(*LINK_BOND) < 1.6:
        problems.append(f"aryl-furan link {LINK_BOND} = {d(*LINK_BOND):.2f} A")
    if problems:
        raise SystemExit("topology check failed:\n  " + "\n  ".join(problems))


# ---------------------------------------------------------------- diagnostics
def best_fit_plane(pts):
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c)
    return c, vt[2]                     # centroid, normal (smallest singular vector)


def angle(a, b, c):
    v1, v2 = a - b, c - b
    cosv = v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return math.degrees(math.acos(np.clip(cosv, -1, 1)))


def geometry_report(coords, molecule="dcdhf-me2"):
    """Geometry diagnostics, dispatched by molecule.

    Different molecules have different coordinates worth recording: for a
    push-pull dye it is the donor-acceptor twist and the amine pyramidality;
    for benzene, whose point is its symmetry, it is how equal the C-C bonds
    are and how planar the ring is, since a broken degeneracy would show up
    there first.
    """
    if MOLECULES[molecule]["diagnostics"] == "benzene":
        return benzene_report(coords)
    _, n_don = best_fit_plane(coords[DONOR_RING])
    _, n_acc = best_fit_plane(coords[ACCEPTOR_RING])
    twist = math.degrees(math.acos(min(1.0, abs(float(n_don @ n_acc)))))

    ring = coords[DONOR_RING]
    c_don, nd = best_fit_plane(ring)
    ring_rms = float(np.sqrt((((ring - c_don) @ nd) ** 2).mean()))

    N = coords[AMINE_N]
    s = sum(angle(coords[i], N, coords[j])
            for k, i in enumerate(AMINE_SUBS) for j in AMINE_SUBS[k + 1:])
    rep = {
        "interring_twist_deg": round(twist, 2),          # 0 = coplanar/conjugated
        "donor_ring_rms_planarity_ang": round(ring_rms, 4),
        "amine_N_angle_sum_deg": round(s, 1),            # 360 = planar sp2 donor
        "amine_pyramidalization_deg": round(360.0 - s, 1),
        "aryl_furan_bond_ang": round(float(np.linalg.norm(
            coords[LINK_BOND[0]] - coords[LINK_BOND[1]])), 4),
        "nitrile_bond_ang": [round(float(np.linalg.norm(coords[c] - coords[n])), 4)
                             for c, n in NITRILES],
    }
    return rep


def benzene_report(coords):
    """Ring planarity and C-C bond equality.

    These matter because benzene is in this experiment for its symmetry: the
    two components of the strongly allowed band are degenerate only while the
    ring is regular. A spread in the C-C bonds is the first place a broken
    D6h would show, so recording it is what lets the degeneracy claim be
    checked rather than asserted.
    """
    ring = coords[BENZENE_RING]
    c, n = best_fit_plane(ring)
    rms = float(np.sqrt((((ring - c) @ n) ** 2).mean()))
    cc = [float(np.linalg.norm(ring[i] - ring[(i + 1) % 6])) for i in range(6)]
    ch = [float(np.linalg.norm(coords[i] - coords[i + 6])) for i in range(6)]
    return {
        "ring_rms_planarity_ang": round(rms, 5),
        "cc_bond_mean_ang": round(sum(cc) / 6, 4),
        "cc_bond_spread_ang": round(max(cc) - min(cc), 5),
        "ch_bond_mean_ang": round(sum(ch) / 6, 4),
        "ch_bond_spread_ang": round(max(ch) - min(ch), 5),
    }


def orbital_centroids(wfn):
    """MO centroids <phi|r|phi> in Angstrom, for the hole-particle distance."""
    mints = psi4.core.MintsHelper(wfn.basisset())
    dip = [np.asarray(m) for m in mints.ao_dipole()]
    C = np.asarray(wfn.Ca_subset("AO", "ALL"))
    cent = np.zeros((C.shape[1], 3))
    for ax in range(3):
        cent[:, ax] = np.einsum("pi,pq,qi->i", C, dip[ax], C)
    return cent * BOHR2ANG


def analyze_state(st, nocc, cent, tda):
    """Dominant orbital character (%) and hole-particle distance for one state."""
    X = np.asarray(st["RIGHT EIGENVECTOR ALPHA"])
    if tda:
        w = X ** 2                       # TDA: no de-excitation amplitudes
    else:
        L = np.asarray(st["LEFT EIGENVECTOR ALPHA"])
        Xamp, Yamp = 0.5 * (X + L), 0.5 * (X - L)
        w = Xamp ** 2 - Yamp ** 2        # RPA weight
    wabs = np.abs(w)
    tot = wabs.sum()
    order = np.dstack(np.unravel_index(np.argsort(wabs, axis=None)[::-1], w.shape))[0]
    contribs = []
    for (i, a) in order[:4]:
        pct = 100.0 * wabs[i, a] / tot
        if pct < 5:
            break
        occ = "HOMO" + ("" if i == nocc - 1 else "-%d" % (nocc - 1 - i))
        vir = "LUMO" + ("" if a == 0 else "+%d" % a)
        contribs.append({"from": occ, "to": vir, "weight_pct": round(pct, 1),
                         "occ_index": int(i), "vir_index": int(a)})
    i0, a0 = order[0]
    d_ct = float(np.linalg.norm(cent[nocc + a0] - cent[i0]))
    return contribs, d_ct


def classify(f, d_ct):
    """Conservative auto-label, same convention as the push-pull run: a dark
    state is not asserted to be n->pi* without orbital-symmetry inspection."""
    bright = f >= 0.01
    if d_ct >= 2.0 and bright:
        return "CT", bright
    if bright:
        return "pi->pi*", bright
    return "dark/weak", bright


def parse_solver_options(log_path):
    """Read back what the eigensolver actually ran with, from its own header.

    Psi4 1.9.1 does not honour either the `maxiter` keyword argument to
    tdscf_excitations OR the TDSCF_MAXITER global option: both are accepted
    silently and the solver runs at 60 regardless. `r_convergence` does take
    effect. Rather than record what we asked for -- which would put a false
    number in a published artifact -- parse the solver's printed options.

    The solver prints these from the variables it is really using
    (psi4/driver/p4util/solvers.py), so this is the authoritative source.
    Takes the LAST occurrence, since the SCF section prints similar headings.
    """
    found = {}
    try:
        with open(log_path) as fh:
            for line in fh:
                if "Max number of iterations" in line:
                    found["maxiter"] = int(line.split("=")[1].strip())
                elif "Eigenvector tolerance" in line:
                    found["r_convergence"] = float(line.split("=")[1].strip())
                elif "Max number of expansion vectors" in line:
                    found["max_expansion_vectors"] = int(line.split("=")[1].strip())
    except OSError:
        return None
    return found or None


def environment_record(args):
    return {
        "psi4_version": psi4.__version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "threads_requested": args.threads,
        "memory_requested": args.memory,
        "run_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }


def configure(args):
    psi4.set_memory(args.memory)
    psi4.set_num_threads(args.threads)


# ---------------------------------------------------------------- stage: optimize
def stage_optimize(args):
    spec = MOLECULES[args.molecule]
    out_path = args.out or os.path.join(
        HERE, "geometry", f"{args.molecule}-{args.basis}-opt.xyz")
    if os.path.exists(out_path) and not args.force:
        raise SystemExit(f"{out_path} exists; pass --force to overwrite")

    symbols, coords, _ = read_xyz(args.geometry)
    verify_topology(symbols, coords, args.molecule)
    configure(args)
    psi4.core.set_output_file(
        os.path.join(HERE, "logs", f"opt_{args.molecule}_{args.basis}.out"), False)

    mol = psi4.geometry(psi4_geometry_block(symbols, coords,
                                            spec["charge"], spec["multiplicity"]))
    psi4.set_options({"basis": args.basis, "scf_type": "df", "reference": "rks",
                      "e_convergence": 1e-8, "d_convergence": 1e-8,
                      "g_convergence": args.g_convergence,
                      "geom_maxiter": args.geom_maxiter, "maxiter": 300})
    energy = psi4.optimize(args.functional, molecule=mol)
    opt_coords = np.asarray(mol.geometry()) * BOHR2ANG
    verify_topology(symbols, opt_coords, args.molecule)

    comment = (f"{spec['name']} optimized {args.functional}/{args.basis} (C1, "
               f"{args.g_convergence}) E={energy:.8f} Ha; from {os.path.basename(args.geometry)}")
    write_xyz(out_path, symbols, opt_coords, comment)

    report = geometry_report(opt_coords, args.molecule)
    report.update({"molecule": spec["name"],
                   "opt_level": f"{args.functional}/{args.basis} (C1, {args.g_convergence})",
                   "opt_energy_Ha": float(energy),
                   "start_geometry": os.path.relpath(args.geometry, HERE),
                   "environment": environment_record(args)})
    with open(os.path.join(HERE, "results",
                           f"geometry_{args.molecule}_{args.basis}.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    diag = ", ".join(f"{k}={v}" for k, v in report.items()
                     if k.endswith(("_deg", "_ang")) and not isinstance(v, list))
    print(f"[optimize {args.molecule}] E={energy:.8f} Ha  {diag} -> {out_path}")


# ---------------------------------------------------------------- stage: excite
def stage_excite(args):
    spec = MOLECULES[args.molecule]
    tag = f"{args.molecule}_{args.functional}_{args.basis}" + ("_tda" if args.tda else "")
    out_path = os.path.join(HERE, "results", f"states_{tag}.json")
    if os.path.exists(out_path) and not args.force:
        raise SystemExit(f"{out_path} exists; pass --force to overwrite")

    symbols, coords, comment = read_xyz(args.geometry)
    verify_topology(symbols, coords, args.molecule)
    configure(args)
    psi4.core.clean()                    # gotcha #1: clean between jobs
    psi4.core.set_output_file(os.path.join(HERE, "logs", f"td_{tag}.out"), False)

    mol = psi4.geometry(psi4_geometry_block(symbols, coords,
                                            spec["charge"], spec["multiplicity"]))
    opts = {"basis": args.basis, "scf_type": "df", "reference": "rks",
            "e_convergence": 1e-8, "d_convergence": 1e-8, "maxiter": 300,
            # r_convergence genuinely takes effect through this option. maxiter
            # does NOT: Psi4 1.9.1 ignores both the kwarg and this option and
            # runs the solver at 60 regardless. Set anyway so intent is on the
            # record; parse_solver_options() reports what was really used.
            "tdscf_maxiter": args.td_maxiter,
            "tdscf_r_convergence": args.r_convergence}
    if args.save_jk:
        opts["save_jk"] = True           # reused by tdscf; costs memory
    psi4.set_options(opts)

    escf, wfn = psi4.energy(args.functional, molecule=mol, return_wfn=True)
    nocc, nmo = wfn.nalpha(), wfn.nmo()
    cent = orbital_centroids(wfn)
    res = tdscf_excitations(wfn, states=args.states, tda=args.tda,
                            r_convergence=args.r_convergence, maxiter=args.td_maxiter)
    psi4.core.flush_outfile()
    solver_opts = parse_solver_options(
        os.path.join(HERE, "logs", f"td_{tag}.out"))

    states = []
    for k, st in enumerate(res):
        e_ev = float(st["EXCITATION ENERGY"]) * HA2EV
        f = float(st["OSCILLATOR STRENGTH (LEN)"])
        contribs, d_ct = analyze_state(st, nocc, cent, args.tda)
        typ, bright = classify(f, d_ct)
        states.append({"state": k + 1, "energy_eV": round(e_ev, 4),
                       "wavelength_nm": round(EV2NM / e_ev, 2), "f": round(f, 5),
                       "hole_particle_dist_ang": round(d_ct, 2),
                       "type": typ, "bright": bright, "dominant": contribs})

    formula = "".join(f"{el}{n if n > 1 else ''}"
                      for el, n in sorted(spec["formula"].items()))
    out = {"molecule": spec["name"], "molecule_slug": args.molecule,
           "formula": formula,
           "geometry_source": os.path.relpath(args.geometry, HERE),
           "geometry_comment": comment,
           "functional": args.functional, "basis": args.basis,
           "method": "TDA" if args.tda else "full RPA",
           "n_states_requested": args.states,
           # What we asked for vs. what the solver actually ran with. These
           # disagree on maxiter in Psi4 1.9.1 -- see parse_solver_options.
           "tdscf_requested": {"maxiter": args.td_maxiter,
                               "r_convergence": args.r_convergence},
           "tdscf_effective": solver_opts,
           "scf_energy_Ha": float(escf), "n_occupied": int(nocc), "n_mo": int(nmo),
           "n_basis_functions": int(wfn.basisset().nbf()),
           "states": states,
           "manifold": manifold_summary(states),
           "environment": environment_record(args)}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)

    m = out["manifold"]
    print(f"[{tag}] nbf={out['n_basis_functions']} states={len(states)} "
          f"bright={m['n_bright']} lowest_bright={m['lowest_bright_nm']} nm "
          f"f_sum={m['f_total']:.4f} -> {out_path}")


def manifold_summary(states):
    """Quantify the point of the experiment: how much of the absorption is NOT
    the single lowest transition the two-level picture keeps."""
    bright = [s for s in states if s["bright"]]
    f_total = sum(s["f"] for s in states)
    low = min(bright, key=lambda s: s["energy_eV"]) if bright else None
    summary = {
        "n_states": len(states),
        "n_bright": len(bright),
        "f_total": round(f_total, 5),
        "energy_range_eV": [states[0]["energy_eV"], states[-1]["energy_eV"]] if states else None,
        "lowest_bright_nm": low["wavelength_nm"] if low else None,
        "lowest_bright_f": low["f"] if low else None,
        "lowest_bright_type": low["type"] if low else None,
    }
    if low and f_total > 0:
        summary["f_fraction_in_lowest_bright"] = round(low["f"] / f_total, 4)
        summary["f_above_lowest_bright"] = round(
            sum(s["f"] for s in states if s["energy_eV"] > low["energy_eV"]), 5)
    return summary


# ---------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="stage", required=True)

    def common(sp, default_basis):
        sp.add_argument("--molecule", choices=sorted(MOLECULES), default="dcdhf-me2")
        # Defaults to the molecule's own starting structure; override to feed
        # an optimized geometry into the excite stage.
        sp.add_argument("--geometry", default=None)
        sp.add_argument("--basis", default=default_basis)
        sp.add_argument("--functional", default="b3lyp")
        # Sized for a 15 GB / 8-core box. Do not raise these blindly: the
        # push-pull script's 24 GB / 9 threads cannot run here.
        sp.add_argument("--memory", default="4 GB")
        sp.add_argument("--threads", type=int, default=4)
        sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("optimize", help="geometry optimization")
    common(sp, "def2-svp")
    sp.add_argument("--out")
    sp.add_argument("--g-convergence", default="gau_tight")
    sp.add_argument("--geom-maxiter", type=int, default=200)
    sp.set_defaults(func=stage_optimize)

    sp = sub.add_parser("excite", help="TD-DFT excited states")
    common(sp, "def2-tzvp")
    sp.add_argument("--states", type=int, default=12)
    sp.add_argument("--tda", action="store_true",
                    help="Tamm-Dancoff approximation: cheaper fallback if full RPA "
                         "will not fit in memory")
    sp.add_argument("--r-convergence", type=float, default=1e-5)
    sp.add_argument("--td-maxiter", type=int, default=120)
    sp.add_argument("--no-save-jk", dest="save_jk", action="store_false",
                    help="drop the saved JK object to cut memory")
    sp.set_defaults(func=stage_excite, save_jk=True)

    args = p.parse_args()
    if args.geometry is None:
        args.geometry = os.path.join(HERE, "geometry",
                                     MOLECULES[args.molecule]["geometry"])
    args.func(args)


if __name__ == "__main__":
    main()
