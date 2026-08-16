#!/usr/bin/env python
"""
Compute leg for the donor-strength ladder.

Adapted from research/dcdhf-me2-transitions/run_tddft.py. The protocol is
deliberately unchanged from that experiment -- B3LYP/def2-SVP optimization,
full-RPA TD-DFT at def2-TZVP with >=10 singlets, both b3lyp and cam-b3lyp --
because this experiment's whole argument is a comparison against its
DCDHF-Me2 numbers, and a ladder computed at a shifted level of theory cannot
be compared along its rungs.

What is new here is the molecule registry (six molecules across two scaffolds
rather than two unrelated ones) and the band-window enclosure record described
below.

    run_tddft.py optimize --molecule bmn-h    # -> geometry/bmn-h-def2-svp-opt.xyz
    run_tddft.py excite   --molecule bmn-h --functional cam-b3lyp

Each `excite` call is a separate process reading the optimized geometry off
disk, so a failure in one functional or basis costs only that call. Nothing
overwrites a previous stage's output unless --force is given.
"""
import os, sys, json, math, argparse, datetime, platform

HERE = os.path.dirname(os.path.abspath(__file__))
# gotcha #1 (inherited): PSI_SCRATCH must be set before import psi4
os.environ.setdefault("PSI_SCRATCH", os.path.join(HERE, "scratch"))
os.makedirs(os.environ["PSI_SCRATCH"], exist_ok=True)
for sub in ("geometry", "results", "logs"):
    os.makedirs(os.path.join(HERE, sub), exist_ok=True)

import numpy as np
import psi4
from psi4.driver.procrouting.response.scf_response import tdscf_excitations

HA2EV = 27.211386245988
EV2NM = 1239.841984
BOHR2ANG = 0.529177210903

# Brightness threshold and band half-width, both inherited verbatim from
# dcdhf-me2-transitions (which inherited them from calcs/uvvis-pushpull) and
# both preregistered. Neither is widened after seeing results.
BRIGHT_F = 0.01
BAND_HALFWIDTH_EV = 0.35

# ---------------------------------------------------------------- index tables
# Benzylidenemalononitrile. build_geometries.py fixes this atom order and makes
# it IDENTICAL across all four rungs for indices 0-16, so one table describes
# every molecule in the ladder and a diagnostic cannot quietly mean something
# different on a different rung. The substituent occupies 17 onwards.
BMN_ARYL_RING = [0, 1, 2, 3, 4, 5]
BMN_VINYL_C, BMN_VINYL_H, BMN_ACCEPTOR_C = 10, 11, 12
BMN_NITRILES = [(13, 14), (15, 16)]
BMN_LINK_BOND = (0, 10)              # aryl -- vinyl
BMN_BRIDGE_BOND = (10, 12)           # exocyclic C=C
BMN_IPSO_X = 3                       # ring carbon bearing X
BMN_X_FIRST = 17
# Best-fit plane of the acceptor arm, for the twist diagnostic.
BMN_ACCEPTOR_PLANE = [10, 11, 12, 13, 15]

# DCDHF-F / DCDHF-H, after deleting the NMe2 group from the 39-atom DCDHF-Me2
# structure. NOT transcribed by eye: build_geometries.py derives the remapping
# and writes it to geometry/dcdhf-derived-indices.json, and check_derived_indices()
# below asserts these constants against that file at runtime.
DCDHF_DONOR_RING = [0, 1, 3, 5, 6, 8]
DCDHF_ACCEPTOR_RING = [10, 11, 16, 15, 13]    # C,C,C,O,C
DCDHF_NITRILES = [(12, 14), (26, 28), (27, 29)]
DCDHF_LINK_BOND = (5, 10)            # aryl -- dihydrofuran
DCDHF_IPSO_X = 0                     # ring carbon bearing X
DCDHF_X_INDEX = 30

MOLECULES = {
    "bmn-h": {
        "name": "benzylidenemalononitrile",
        "formula": {"C": 10, "H": 6, "N": 2},
        "geometry": "bmn-h-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "bmn", "substituent": "H", "sigma_p_plus": 0.00,
    },
    "bmn-f": {
        "name": "4-fluorobenzylidenemalononitrile",
        "formula": {"C": 10, "H": 5, "F": 1, "N": 2},
        "geometry": "bmn-f-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "bmn", "substituent": "F", "sigma_p_plus": -0.07,
    },
    "bmn-nh2": {
        "name": "4-aminobenzylidenemalononitrile",
        "formula": {"C": 10, "H": 7, "N": 3},
        "geometry": "bmn-nh2-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "bmn", "substituent": "NH2", "sigma_p_plus": -1.30,
    },
    "bmn-nme2": {
        "name": "4-(dimethylamino)benzylidenemalononitrile",
        "formula": {"C": 12, "H": 11, "N": 3},
        "geometry": "bmn-nme2-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "bmn", "substituent": "NMe2", "sigma_p_plus": -1.70,
    },
    "dcdhf-h": {
        "name": "DCDHF-H",
        "formula": {"C": 16, "H": 11, "N": 3, "O": 1},
        "geometry": "dcdhf-h-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "dcdhf", "substituent": "H", "sigma_p_plus": 0.00,
    },
    "dcdhf-f": {
        "name": "DCDHF-F",
        "formula": {"C": 16, "H": 10, "F": 1, "N": 3, "O": 1},
        "geometry": "dcdhf-f-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "dcdhf", "substituent": "F", "sigma_p_plus": -0.07,
    },
}

# The rung this experiment is defined against, computed by the PRIOR experiment
# and reused rather than recomputed. Listed here so the ladder ordering has a
# single definition; run_tddft.py never computes it.
REUSED_RUNG = {
    "slug": "dcdhf-me2", "name": "DCDHF-Me2", "scaffold": "dcdhf",
    "substituent": "NMe2", "sigma_p_plus": -1.70,
    "source": "research/dcdhf-me2-transitions",
}


def check_derived_indices():
    """Assert the hardcoded DCDHF tables against what the substitution produced.

    The tables above are a hand-copy of a remapping that build_geometries.py
    computes. A hand-copy is exactly the kind of thing that is right today and
    wrong after someone changes the deletion list, and a wrong index table does
    not crash -- it silently reports a twist angle between the wrong two planes.
    """
    path = os.path.join(HERE, "geometry", "dcdhf-derived-indices.json")
    if not os.path.exists(path):
        return
    with open(path) as fh:
        derived = json.load(fh)
    expected = {
        "donor_ring": DCDHF_DONOR_RING,
        "acceptor_ring": DCDHF_ACCEPTOR_RING,
        "nitriles": [list(p) for p in DCDHF_NITRILES],
        "link_bond": list(DCDHF_LINK_BOND),
        "ipso_carbon": DCDHF_IPSO_X,
        "substituent_index": DCDHF_X_INDEX,
    }
    for slug, table in derived.items():
        for key, want in expected.items():
            if table.get(key) != want:
                raise SystemExit(
                    f"index table drift for {slug}: run_tddft.py has {key}={want}, "
                    f"but build_geometries.py derived {table.get(key)}. "
                    f"Rebuild geometries or fix the table -- do not run on this.")


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


def verify_topology(symbols, coords, molecule):
    """Fail loudly if the structure is not the molecule we think it is.

    Cheap insurance: the diagnostics are meaningless if the atom order ever
    changes, and a silently wrong twist angle is worse than a crash.
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

    # Bail before the index-table checks: they index fixed atom positions, so
    # running them against a structure that already failed the formula check
    # raises IndexError and buries the real diagnosis.
    if problems:
        raise SystemExit("topology check failed:\n  " + "\n  ".join(problems))

    if spec["scaffold"] == "bmn":
        ring, nitriles = BMN_ARYL_RING, BMN_NITRILES
        link, ipso, x_first = BMN_LINK_BOND, BMN_IPSO_X, BMN_X_FIRST
        for i in ring:
            if symbols[i] != "C":
                problems.append(f"aryl ring atom {i} is {symbols[i]}, expected C")
        for a, b in zip(ring, ring[1:] + ring[:1]):
            if not 1.2 < d(a, b) < 1.6:
                problems.append(f"aryl ring bond {a}-{b} = {d(a, b):.2f} A")
        if symbols[BMN_VINYL_C] != "C" or symbols[BMN_ACCEPTOR_C] != "C":
            problems.append("vinyl/acceptor carbons are not both C")
        if not 1.25 < d(*BMN_BRIDGE_BOND) < 1.50:
            problems.append(f"C=C bridge {BMN_BRIDGE_BOND} = {d(*BMN_BRIDGE_BOND):.2f} A")
    else:
        ring, nitriles = DCDHF_DONOR_RING, DCDHF_NITRILES
        link, ipso, x_first = DCDHF_LINK_BOND, DCDHF_IPSO_X, DCDHF_X_INDEX
        for i in ring:
            if symbols[i] != "C":
                problems.append(f"donor ring atom {i} is {symbols[i]}, expected C")
        ring_syms = "".join(symbols[i] for i in DCDHF_ACCEPTOR_RING)
        if ring_syms != "CCCOC":
            problems.append(f"acceptor ring symbols {ring_syms}, expected CCCOC")
        for a, b in zip(DCDHF_ACCEPTOR_RING,
                        DCDHF_ACCEPTOR_RING[1:] + DCDHF_ACCEPTOR_RING[:1]):
            if not 1.2 < d(a, b) < 1.7:
                problems.append(f"acceptor ring bond {a}-{b} = {d(a, b):.2f} A")

    for c, nn in nitriles:
        if symbols[c] != "C" or symbols[nn] != "N":
            problems.append(f"nitrile ({c},{nn}) is ({symbols[c]},{symbols[nn]})")
        elif not 1.05 < d(c, nn) < 1.30:
            problems.append(f"nitrile {c}#{nn} = {d(c, nn):.2f} A, not a triple bond")
    if not 1.3 < d(*link) < 1.6:
        problems.append(f"aryl-acceptor link {link} = {d(*link):.2f} A")

    # The substituent is the whole point of the experiment, so its identity and
    # attachment are checked rather than assumed.
    want = {"H": "H", "F": "F", "NH2": "N", "NMe2": "N"}[spec["substituent"]]
    if symbols[x_first] != want:
        problems.append(f"substituent atom {x_first} is {symbols[x_first]}, "
                        f"expected {want} for X={spec['substituent']}")
    elif not 0.9 < d(ipso, x_first) < 1.6:
        problems.append(f"ipso-X bond {ipso}-{x_first} = {d(ipso, x_first):.2f} A")

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


def plane_angle(pts_a, pts_b):
    _, na = best_fit_plane(pts_a)
    _, nb = best_fit_plane(pts_b)
    return math.degrees(math.acos(min(1.0, abs(float(na @ nb)))))


def geometry_report(coords, molecule, symbols=None):
    """Geometry diagnostics, dispatched by scaffold.

    The donor-acceptor twist is the coordinate this experiment cares about on
    both scaffolds -- it is the one that controls conjugation, and therefore
    whether a charge-transfer band exists at all -- so it is reported under the
    same key for every molecule and stays comparable across the ladder.
    """
    spec = MOLECULES[molecule]
    if spec["scaffold"] == "bmn":
        rep = {
            "interfragment_twist_deg": round(
                plane_angle(coords[BMN_ARYL_RING], coords[BMN_ACCEPTOR_PLANE]), 2),
            "aryl_acceptor_bond_ang": round(float(np.linalg.norm(
                coords[BMN_LINK_BOND[0]] - coords[BMN_LINK_BOND[1]])), 4),
            "bridge_cc_bond_ang": round(float(np.linalg.norm(
                coords[BMN_BRIDGE_BOND[0]] - coords[BMN_BRIDGE_BOND[1]])), 4),
            "nitrile_bond_ang": [round(float(np.linalg.norm(coords[c] - coords[n])), 4)
                                 for c, n in BMN_NITRILES],
            "ipso_substituent_bond_ang": round(float(np.linalg.norm(
                coords[BMN_IPSO_X] - coords[BMN_X_FIRST])), 4),
        }
        ring = coords[BMN_ARYL_RING]
        c, nrm = best_fit_plane(ring)
        rep["aryl_ring_rms_planarity_ang"] = round(
            float(np.sqrt((((ring - c) @ nrm) ** 2).mean())), 4)
        if spec["substituent"] in ("NH2", "NMe2"):
            N = coords[BMN_X_FIRST]
            subs = [BMN_IPSO_X, BMN_X_FIRST + 1, BMN_X_FIRST + 2]
            s = sum(angle(coords[i], N, coords[j])
                    for k, i in enumerate(subs) for j in subs[k + 1:])
            rep["amine_N_angle_sum_deg"] = round(s, 1)        # 360 = planar sp2
            rep["amine_pyramidalization_deg"] = round(360.0 - s, 1)
        return rep

    rep = {
        "interfragment_twist_deg": round(
            plane_angle(coords[DCDHF_DONOR_RING], coords[DCDHF_ACCEPTOR_RING]), 2),
        "aryl_acceptor_bond_ang": round(float(np.linalg.norm(
            coords[DCDHF_LINK_BOND[0]] - coords[DCDHF_LINK_BOND[1]])), 4),
        "nitrile_bond_ang": [round(float(np.linalg.norm(coords[c] - coords[n])), 4)
                             for c, n in DCDHF_NITRILES],
        "ipso_substituent_bond_ang": round(float(np.linalg.norm(
            coords[DCDHF_IPSO_X] - coords[DCDHF_X_INDEX])), 4),
    }
    ring = coords[DCDHF_DONOR_RING]
    c, nrm = best_fit_plane(ring)
    rep["donor_ring_rms_planarity_ang"] = round(
        float(np.sqrt((((ring - c) @ nrm) ** 2).mean())), 4)
    return rep


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
    """Conservative auto-label, same convention as the prior run: a dark state
    is not asserted to be n->pi* without orbital-symmetry inspection.

    The prior experiment established that this centroid diagnostic UNDERSTATES
    charge transfer when both frontier orbitals are delocalized over the whole
    backbone, which is exactly the situation here. It is retained for
    completeness and is not what any claim rests on -- CT character is argued
    from the B3LYP -> CAM-B3LYP shift instead.
    """
    bright = f >= BRIGHT_F
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

    start = geometry_report(coords, args.molecule, symbols)
    report = geometry_report(opt_coords, args.molecule, symbols)
    report.update({"molecule": spec["name"], "molecule_slug": args.molecule,
                   "scaffold": spec["scaffold"], "substituent": spec["substituent"],
                   "opt_level": f"{args.functional}/{args.basis} (C1, {args.g_convergence})",
                   "opt_energy_Ha": float(energy),
                   "start_geometry": os.path.relpath(args.geometry, HERE),
                   "start_diagnostics": start,
                   "environment": environment_record(args)})
    with open(os.path.join(HERE, "results",
                           f"geometry_{args.molecule}_{args.basis}.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"[optimize {args.molecule}] E={energy:.8f} Ha  "
          f"twist {start['interfragment_twist_deg']:.1f} -> "
          f"{report['interfragment_twist_deg']:.1f} deg -> {out_path}")


# ---------------------------------------------------------------- stage: excite
def stage_excite(args):
    spec = MOLECULES[args.molecule]
    tag = f"{args.molecule}_{args.functional}_{args.basis}" + ("_tda" if args.tda else "")
    if args.states != 12:
        tag += f"_s{args.states}"
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
    solver_opts = parse_solver_options(os.path.join(HERE, "logs", f"td_{tag}.out"))

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
           "scaffold": spec["scaffold"], "substituent": spec["substituent"],
           "sigma_p_plus": spec["sigma_p_plus"],
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
    warn = "" if m["window_enclosed"] else "  *** WINDOW NOT ENCLOSED: rerun with more states"
    print(f"[{tag}] nbf={out['n_basis_functions']} states={len(states)} "
          f"bright={m['n_bright']} lowest_bright={m['lowest_bright_nm']} nm "
          f"isolation_count={m['isolation_count']} gap={m['isolation_gap_eV']}{warn}")


def manifold_summary(states):
    """The preregistered quantities, computed at the point of measurement.

    `window_enclosed` is the guard against this design manufacturing its own
    expected answer. The isolation count looks +-0.35 eV around the lowest
    bright state; for a weak donor that state blue-shifts toward the top of the
    manifold, and the upper half of the window can then contain states that
    were never computed. The count comes back 1 because the calculation
    stopped, not because the band is isolated -- an artifact that mimics the
    hypothesis. Recording enclosure here makes it impossible to read the count
    without also seeing whether it means anything.
    """
    bright = [s for s in states if s["bright"]]
    f_total = sum(s["f"] for s in states)
    low = min(bright, key=lambda s: (s["energy_eV"], s["state"])) if bright else None
    summary = {
        "n_states": len(states),
        "n_bright": len(bright),
        "f_total": round(f_total, 5),
        "bright_threshold_f": BRIGHT_F,
        "band_halfwidth_eV": BAND_HALFWIDTH_EV,
        "energy_range_eV": [states[0]["energy_eV"], states[-1]["energy_eV"]] if states else None,
        "lowest_bright_state": low["state"] if low else None,
        "lowest_bright_eV": low["energy_eV"] if low else None,
        "lowest_bright_nm": low["wavelength_nm"] if low else None,
        "lowest_bright_f": low["f"] if low else None,
        "lowest_bright_type": low["type"] if low else None,
        "isolation_count": None,
        "isolation_gap_eV": None,
        "window_enclosed": True,
    }
    if not low:
        summary["window_enclosed"] = False
        return summary

    e0 = low["energy_eV"]
    summary["isolation_count"] = sum(
        1 for s in states if s["bright"] and abs(s["energy_eV"] - e0) <= BAND_HALFWIDTH_EV)
    # Selected by identity, not by a strict energy comparison: `energy > e0`
    # silently drops a state at exactly the same energy. That trap cost the
    # prior experiment a 20x error on benzene before its contrast case caught
    # it, and it is the reason this reads `state != low.state`.
    above = [s for s in states if s["bright"] and s["state"] != low["state"]
             and s["energy_eV"] >= e0]
    if above:
        summary["isolation_gap_eV"] = round(
            min(s["energy_eV"] for s in above) - e0, 4)
    summary["window_enclosed"] = bool(
        states and states[-1]["energy_eV"] >= e0 + BAND_HALFWIDTH_EV)
    if f_total > 0:
        summary["f_fraction_in_lowest_bright"] = round(low["f"] / f_total, 4)
    return summary


# ---------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="stage", required=True)

    def common(sp, default_basis):
        sp.add_argument("--molecule", choices=sorted(MOLECULES), required=True)
        sp.add_argument("--geometry", default=None)
        sp.add_argument("--basis", default=default_basis)
        sp.add_argument("--functional", default="b3lyp")
        # Sized for a 15 GB / 8-core box, same as the prior experiment.
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
    # 12 is preregistered and fixed across the ladder: the f-fraction metric
    # has total computed f in its denominator, so it is only comparable at a
    # fixed state count. Raise it only under the enclosure rule.
    sp.add_argument("--states", type=int, default=12)
    sp.add_argument("--tda", action="store_true",
                    help="Tamm-Dancoff approximation: cheaper fallback if full RPA "
                         "will not fit in memory. Applies to the whole ladder or "
                         "none of it -- see PREREGISTRATION.md")
    sp.add_argument("--r-convergence", type=float, default=1e-5)
    sp.add_argument("--td-maxiter", type=int, default=120)
    sp.add_argument("--no-save-jk", dest="save_jk", action="store_false",
                    help="drop the saved JK object to cut memory")
    sp.set_defaults(func=stage_excite, save_jk=True)

    args = p.parse_args()
    check_derived_indices()
    if args.geometry is None:
        args.geometry = os.path.join(HERE, "geometry",
                                     MOLECULES[args.molecule]["geometry"])
    args.func(args)


if __name__ == "__main__":
    main()
