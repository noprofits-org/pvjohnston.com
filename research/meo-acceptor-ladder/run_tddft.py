#!/usr/bin/env python
"""
Compute leg for the acceptor-strength ladder.

The donor is fixed as para-methoxy and the acceptor is varied across three
rungs: cyano (CN), dicyanovinyl (DCV), and tricyanodihydrofuran (TCF). The
protocol is unchanged from the donor-ladder experiment and from
research/dcdhf-me2-transitions: B3LYP/def2-SVP optimization, full-RPA TD-DFT
at def2-TZVP with >=12 singlets, both b3lyp and cam-b3lyp.

    run_tddft.py optimize --molecule meo-cn
    run_tddft.py excite   --molecule meo-cn --functional cam-b3lyp

Each `excite` call is a separate process reading the optimized geometry off
disk, so a failure in one functional or basis costs only that call.
"""
import os, sys, json, math, argparse, datetime, platform

HERE = os.path.dirname(os.path.abspath(__file__))
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

# Brightness threshold and band half-width, inherited verbatim.
BRIGHT_F = 0.01
BAND_HALFWIDTH_EV = 0.35

# ---------------------------------------------------------------- index tables
# meo-cn: p-methoxybenzonitrile. The acceptor is a single linear CN group, so
# there is no acceptor plane. The interfragment twist is reported as the angle
# between the aryl best-fit plane and the C(aryl)-C(nitrile) bond vector.
MEOCN_RING = [0, 1, 2, 3, 4, 5]
MEOCN_CN = (10, 11)                  # (C, N)
MEOCN_LINK_BOND = (0, 10)            # aryl -- nitrile C
MEOCN_IPSO_OMe = 3
MEOCN_OMe_FIRST = 12

# meo-dcv: p-methoxybenzylidenemalononitrile. Same core atom order as the donor
# ladder's BMN scaffold; OMe occupies indices 17-21.
MEODCV_RING = [0, 1, 2, 3, 4, 5]
MEODCV_VINYL_C, MEODCV_VINYL_H, MEODCV_ACCEPTOR_C = 10, 11, 12
MEODCV_NITRILES = [(13, 14), (15, 16)]
MEODCV_LINK_BOND = (0, 10)           # aryl -- vinyl
MEODCV_BRIDGE_BOND = (10, 12)        # exocyclic C=C
MEODCV_ACCEPTOR_PLANE = [10, 11, 12, 13, 15]
MEODCV_IPSO_OMe = 3
MEODCV_OMe_FIRST = 17

# meo-tcf: OMe-substituted DCDHF. Index tables are asserted at runtime against
# the derived-indices file written by build_geometries.py.
MEOTCF_DONOR_RING = [0, 1, 3, 5, 6, 8]
MEOTCF_ACCEPTOR_RING = [10, 11, 16, 15, 13]   # C,C,C,O,C
MEOTCF_NITRILES = [(12, 14), (26, 28), (27, 29)]
MEOTCF_LINK_BOND = (5, 10)           # aryl -- dihydrofuran
MEOTCF_IPSO_OMe = 0
MEOTCF_OMe_FIRST = 30

MOLECULES = {
    "meo-cn": {
        "name": "p-methoxybenzonitrile",
        "formula": {"C": 8, "H": 7, "N": 1, "O": 1},
        "geometry": "meo-cn-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "meo-cn", "acceptor": "CN", "acceptor_strength": 1,
    },
    "meo-dcv": {
        "name": "p-methoxybenzylidenemalononitrile",
        "formula": {"C": 11, "H": 8, "N": 2, "O": 1},
        "geometry": "meo-dcv-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "meo-dcv", "acceptor": "DCV", "acceptor_strength": 2,
    },
    "meo-tcf": {
        "name": "OMe-substituted DCDHF",
        "formula": {"C": 17, "H": 13, "N": 3, "O": 2},
        "geometry": "meo-tcf-start.xyz", "charge": 0, "multiplicity": 1,
        "scaffold": "meo-tcf", "acceptor": "TCF", "acceptor_strength": 3,
    },
}


def check_derived_indices():
    """Assert the hardcoded meo-tcf tables against the substitution output."""
    path = os.path.join(HERE, "geometry", "meo-tcf-derived-indices.json")
    if not os.path.exists(path):
        return
    with open(path) as fh:
        derived = json.load(fh)
    expected = {
        "donor_ring": MEOTCF_DONOR_RING,
        "acceptor_ring": MEOTCF_ACCEPTOR_RING,
        "nitriles": [list(p) for p in MEOTCF_NITRILES],
        "link_bond": list(MEOTCF_LINK_BOND),
        "ipso_carbon": MEOTCF_IPSO_OMe,
    }
    table = derived.get("meo-tcf", {})
    for key, want in expected.items():
        if table.get(key) != want:
            raise SystemExit(
                f"index table drift for meo-tcf: run_tddft.py has {key}={want}, "
                f"but build_geometries.py derived {table.get(key)}. "
                f"Rebuild geometries or fix the table -- do not run on this.")


# ---------------------------------------------------------------- geometry io
def read_xyz(path):
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
    lines += ["symmetry c1", "units angstrom", "no_reorient", "no_com"]
    return "\n".join(lines)


def verify_topology(symbols, coords, molecule):
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

    if problems:
        raise SystemExit("topology check failed:\n  " + "\n  ".join(problems))

    scaf = spec["scaffold"]
    if scaf == "meo-cn":
        ring, nitriles = MEOCN_RING, [MEOCN_CN]
        link, ipso_ome, ome_first = MEOCN_LINK_BOND, MEOCN_IPSO_OMe, MEOCN_OMe_FIRST
        for i in ring:
            if symbols[i] != "C":
                problems.append(f"aryl ring atom {i} is {symbols[i]}, expected C")
        for a, b in zip(ring, ring[1:] + ring[:1]):
            if not 1.2 < d(a, b) < 1.6:
                problems.append(f"aryl ring bond {a}-{b} = {d(a, b):.2f} A")
        if symbols[MEOCN_CN[0]] != "C" or symbols[MEOCN_CN[1]] != "N":
            problems.append("nitrile atoms are not C,N")
        if not 1.05 < d(*MEOCN_CN) < 1.30:
            problems.append(f"nitrile bond = {d(*MEOCN_CN):.2f} A")
        if symbols[ome_first] != "O":
            problems.append(f"methoxy atom {ome_first} is {symbols[ome_first]}, expected O")
    elif scaf == "meo-dcv":
        ring, nitriles = MEODCV_RING, MEODCV_NITRILES
        link, ipso_ome, ome_first = MEODCV_LINK_BOND, MEODCV_IPSO_OMe, MEODCV_OMe_FIRST
        for i in ring:
            if symbols[i] != "C":
                problems.append(f"aryl ring atom {i} is {symbols[i]}, expected C")
        for a, b in zip(ring, ring[1:] + ring[:1]):
            if not 1.2 < d(a, b) < 1.6:
                problems.append(f"aryl ring bond {a}-{b} = {d(a, b):.2f} A")
        if symbols[MEODCV_VINYL_C] != "C" or symbols[MEODCV_ACCEPTOR_C] != "C":
            problems.append("vinyl/acceptor carbons are not both C")
        if not 1.25 < d(*MEODCV_BRIDGE_BOND) < 1.50:
            problems.append(f"C=C bridge {MEODCV_BRIDGE_BOND} = {d(*MEODCV_BRIDGE_BOND):.2f} A")
        if symbols[ome_first] != "O":
            problems.append(f"methoxy atom {ome_first} is {symbols[ome_first]}, expected O")
    else:
        ring, nitriles = MEOTCF_DONOR_RING, MEOTCF_NITRILES
        link, ipso_ome, ome_first = MEOTCF_LINK_BOND, MEOTCF_IPSO_OMe, MEOTCF_OMe_FIRST
        for i in ring:
            if symbols[i] != "C":
                problems.append(f"donor ring atom {i} is {symbols[i]}, expected C")
        ring_syms = "".join(symbols[i] for i in MEOTCF_ACCEPTOR_RING)
        if ring_syms != "CCCOC":
            problems.append(f"acceptor ring symbols {ring_syms}, expected CCCOC")
        for a, b in zip(MEOTCF_ACCEPTOR_RING,
                        MEOTCF_ACCEPTOR_RING[1:] + MEOTCF_ACCEPTOR_RING[:1]):
            if not 1.2 < d(a, b) < 1.7:
                problems.append(f"acceptor ring bond {a}-{b} = {d(a, b):.2f} A")
        if symbols[ome_first] != "O":
            problems.append(f"methoxy atom {ome_first} is {symbols[ome_first]}, expected O")

    for c, nn in nitriles:
        if symbols[c] != "C" or symbols[nn] != "N":
            problems.append(f"nitrile ({c},{nn}) is ({symbols[c]},{symbols[nn]})")
        elif not 1.05 < d(c, nn) < 1.30:
            problems.append(f"nitrile {c}#{nn} = {d(c, nn):.2f} A, not a triple bond")
    if not 1.3 < d(*link) < 1.6:
        problems.append(f"aryl-acceptor link {link} = {d(*link):.2f} A")
    if not 0.9 < d(ipso_ome, ome_first) < 1.6:
        problems.append(f"aryl-O bond {ipso_ome}-{ome_first} = {d(ipso_ome, ome_first):.2f} A")

    if problems:
        raise SystemExit("topology check failed:\n  " + "\n  ".join(problems))


# ---------------------------------------------------------------- diagnostics
def _unit(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise ValueError("cannot normalize a zero-length vector")
    return np.asarray(v, dtype=float) / n


def best_fit_plane(pts):
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c)
    return c, vt[2]


def angle(a, b, c):
    v1, v2 = a - b, c - b
    cosv = v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return math.degrees(math.acos(np.clip(cosv, -1, 1)))


def plane_angle(pts_a, pts_b):
    _, na = best_fit_plane(pts_a)
    _, nb = best_fit_plane(pts_b)
    return math.degrees(math.acos(min(1.0, abs(float(na @ nb)))))


def vector_plane_angle(pts_plane, vec):
    """Angle between a plane and a vector, in degrees. 0 = vector lies in plane."""
    _, normal = best_fit_plane(pts_plane)
    v = _unit(vec)
    # angle with plane normal
    theta_norm = math.degrees(math.acos(np.clip(abs(float(normal @ v)), -1, 1)))
    return 90.0 - theta_norm


def geometry_report(coords, molecule, symbols=None):
    spec = MOLECULES[molecule]
    scaf = spec["scaffold"]

    if scaf == "meo-cn":
        rep = {
            "interfragment_twist_deg": round(
                vector_plane_angle(coords[MEOCN_RING],
                                   coords[MEOCN_CN[0]] - coords[MEOCN_LINK_BOND[0]]), 2),
            "aryl_acceptor_bond_ang": round(float(np.linalg.norm(
                coords[MEOCN_LINK_BOND[0]] - coords[MEOCN_LINK_BOND[1]])), 4),
            "nitrile_bond_ang": [round(float(np.linalg.norm(coords[MEOCN_CN[0]] - coords[MEOCN_CN[1]])), 4)],
            "aryl_OMe_bond_ang": round(float(np.linalg.norm(
                coords[MEOCN_IPSO_OMe] - coords[MEOCN_OMe_FIRST])), 4),
        }
        ring = coords[MEOCN_RING]
    elif scaf == "meo-dcv":
        rep = {
            "interfragment_twist_deg": round(
                plane_angle(coords[MEODCV_RING], coords[MEODCV_ACCEPTOR_PLANE]), 2),
            "aryl_acceptor_bond_ang": round(float(np.linalg.norm(
                coords[MEODCV_LINK_BOND[0]] - coords[MEODCV_LINK_BOND[1]])), 4),
            "bridge_cc_bond_ang": round(float(np.linalg.norm(
                coords[MEODCV_BRIDGE_BOND[0]] - coords[MEODCV_BRIDGE_BOND[1]])), 4),
            "nitrile_bond_ang": [round(float(np.linalg.norm(coords[c] - coords[n])), 4)
                                 for c, n in MEODCV_NITRILES],
            "aryl_OMe_bond_ang": round(float(np.linalg.norm(
                coords[MEODCV_IPSO_OMe] - coords[MEODCV_OMe_FIRST])), 4),
        }
        ring = coords[MEODCV_RING]
    else:
        rep = {
            "interfragment_twist_deg": round(
                plane_angle(coords[MEOTCF_DONOR_RING], coords[MEOTCF_ACCEPTOR_RING]), 2),
            "aryl_acceptor_bond_ang": round(float(np.linalg.norm(
                coords[MEOTCF_LINK_BOND[0]] - coords[MEOTCF_LINK_BOND[1]])), 4),
            "nitrile_bond_ang": [round(float(np.linalg.norm(coords[c] - coords[n])), 4)
                                 for c, n in MEOTCF_NITRILES],
            "aryl_OMe_bond_ang": round(float(np.linalg.norm(
                coords[MEOTCF_IPSO_OMe] - coords[MEOTCF_OMe_FIRST])), 4),
        }
        ring = coords[MEOTCF_DONOR_RING]

    c, nrm = best_fit_plane(ring)
    rep["aryl_ring_rms_planarity_ang"] = round(
        float(np.sqrt((((ring - c) @ nrm) ** 2).mean())), 4)
    return rep


def orbital_centroids(wfn):
    mints = psi4.core.MintsHelper(wfn.basisset())
    dip = [np.asarray(m) for m in mints.ao_dipole()]
    C = np.asarray(wfn.Ca_subset("AO", "ALL"))
    cent = np.zeros((C.shape[1], 3))
    for ax in range(3):
        cent[:, ax] = np.einsum("pi,pq,qi->i", C, dip[ax], C)
    return cent * BOHR2ANG


def analyze_state(st, nocc, cent, tda):
    X = np.asarray(st["RIGHT EIGENVECTOR ALPHA"])
    if tda:
        w = X ** 2
    else:
        L = np.asarray(st["LEFT EIGENVECTOR ALPHA"])
        Xamp, Yamp = 0.5 * (X + L), 0.5 * (X - L)
        w = Xamp ** 2 - Yamp ** 2
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
    bright = f >= BRIGHT_F
    if d_ct >= 2.0 and bright:
        return "CT", bright
    if bright:
        return "pi->pi*", bright
    return "dark/weak", bright


def parse_solver_options(log_path):
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
                   "scaffold": spec["scaffold"], "acceptor": spec["acceptor"],
                   "acceptor_strength": spec["acceptor_strength"],
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
    psi4.core.clean()
    psi4.core.set_output_file(os.path.join(HERE, "logs", f"td_{tag}.out"), False)

    mol = psi4.geometry(psi4_geometry_block(symbols, coords,
                                            spec["charge"], spec["multiplicity"]))
    opts = {"basis": args.basis, "scf_type": "df", "reference": "rks",
            "e_convergence": 1e-8, "d_convergence": 1e-8, "maxiter": 300,
            "tdscf_maxiter": args.td_maxiter,
            "tdscf_r_convergence": args.r_convergence}
    if args.save_jk:
        opts["save_jk"] = True
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
           "scaffold": spec["scaffold"], "acceptor": spec["acceptor"],
           "acceptor_strength": spec["acceptor_strength"],
           "formula": formula,
           "geometry_source": os.path.relpath(args.geometry, HERE),
           "geometry_comment": comment,
           "functional": args.functional, "basis": args.basis,
           "method": "TDA" if args.tda else "full RPA",
           "n_states_requested": args.states,
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
    sp.add_argument("--tda", action="store_true")
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
