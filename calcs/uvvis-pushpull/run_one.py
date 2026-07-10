#!/usr/bin/env python
"""
Compute leg for the "UV-Vis from first principles" post.
One molecule per process: geometry opt (B3LYP/def2-SVP, C1) then TD-DFT
(full RPA, >=10 singlets, def2-TZVP) with B3LYP and CAM-B3LYP.

Usage: run_one.py <label>
Writes: geometries/<label>.xyz, results/<label>.json, logs/<label>_<func>.out
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["PSI_SCRATCH"] = os.path.join(HERE, "scratch")   # gotcha #1: before import

import numpy as np
import psi4
from psi4.driver.procrouting.response.scf_response import tdscf_excitations

HA2EV = 27.211386245988
EV2NM = 1239.841984
EV2CM = 8065.543937
BOHR2ANG = 0.529177210903
N_STATES = 12                 # >= 10 requested
FUNCS = ["b3lyp", "cam-b3lyp"]
OPT_BASIS = "def2-svp"
TD_BASIS = "def2-tzvp"

# ---------------------------------------------------------------- geometry build
def hexagon(sub):
    """Build a planar-ish para-disubstituted benzene starting geometry.
    sub = {0: 'H'|'NH2'|'NO2', 3: ...} for ring carbons; others get H.
    Returns (xyz_lines, symbols, idx) with atom-order-preserving index map."""
    Rc = 1.39                      # ring circumradius (~C-C)
    atoms = []                     # (symbol, x,y,z)
    idx = {"ring_c": [], "donor_N": None, "donor_H": [], "acc_N": None, "acc_O": []}
    ring_xy = []
    for k in range(6):
        th = math.radians(60 * k)
        ring_xy.append((Rc * math.cos(th), Rc * math.sin(th), th))
    # place ring carbons first (indices 0..5)
    for k, (x, y, th) in enumerate(ring_xy):
        idx["ring_c"].append(len(atoms)); atoms.append(("C", x, y, 0.0))
    # substituents / hydrogens
    for k, (x, y, th) in enumerate(ring_xy):
        s = sub.get(k, "H")
        ux, uy = math.cos(th), math.sin(th)      # outward radial unit vector
        px, py = -math.sin(th), math.cos(th)     # in-plane perpendicular
        if s == "H":
            r = Rc + 1.086
            atoms.append(("H", r * ux, r * uy, 0.0))
        elif s == "NH2":
            rN = Rc + 1.40
            nx, ny = rN * ux, rN * uy
            idx["donor_N"] = len(atoms); atoms.append(("N", nx, ny, 0.10))
            # two N-H spread by ~120 deg in-plane, BOTH seeded to +z (umbrella) so the
            # optimizer relaxes toward the real pyramidal minimum, not the planar saddle
            for sign in (+1, -1):
                hx = nx + 1.01 * (0.5 * ux + sign * 0.866 * px)
                hy = ny + 1.01 * (0.5 * uy + sign * 0.866 * py)
                idx["donor_H"].append(len(atoms)); atoms.append(("H", hx, hy, 0.55))
        elif s == "NO2":
            rN = Rc + 1.47
            nx, ny = rN * ux, rN * uy
            idx["acc_N"] = len(atoms); atoms.append(("N", nx, ny, 0.0))
            for sign in (+1, -1):
                ox = nx + 1.22 * (0.5 * ux + sign * 0.866 * px)
                oy = ny + 1.22 * (0.5 * uy + sign * 0.866 * py)
                idx["acc_O"].append(len(atoms)); atoms.append(("O", ox, oy, 0.0))
    symbols = [a[0] for a in atoms]
    lines = ["%s %.6f %.6f %.6f" % a for a in atoms]
    return lines, symbols, idx

MOLECULES = {
    "benzene":      dict(sub={},                       charge=0, name="benzene",
                         smiles="c1ccccc1"),
    "aniline":      dict(sub={0: "NH2"},               charge=0, name="aniline",
                         smiles="Nc1ccccc1"),
    "nitrobenzene": dict(sub={0: "NO2"},               charge=0, name="nitrobenzene",
                         smiles="O=[N+]([O-])c1ccccc1"),
    "pNA":          dict(sub={0: "NH2", 3: "NO2"},     charge=0, name="para-nitroaniline",
                         smiles="Nc1ccc(cc1)[N+](=O)[O-]"),
}

# ---------------------------------------------------------------- geometry metrics
def best_fit_plane(pts):
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c)
    n = vt[2]                       # plane normal = smallest singular vector
    return c, n

def planarity_report(coords_ang, idx):
    """coords_ang: (natom,3) in Angstrom. Return dict of geometry diagnostics."""
    ring = coords_ang[idx["ring_c"]]
    c, n = best_fit_plane(ring)
    dev = np.abs((coords_ang - c) @ n)
    rep = {"ring_rms_planarity_ang": float(np.sqrt((((ring - c) @ n) ** 2).mean())),
           "max_heavy_out_of_plane_ang": float(dev[[i for i in range(len(coords_ang))]].max())}
    if idx["donor_N"] is not None:
        N = coords_ang[idx["donor_N"]]
        H1, H2 = coords_ang[idx["donor_H"][0]], coords_ang[idx["donor_H"][1]]
        # find ring C bonded to N (nearest ring carbon)
        Cn = ring[np.argmin(np.linalg.norm(ring - N, axis=1))]
        def ang(a, b, cc):
            v1, v2 = a - b, cc - b
            return math.degrees(math.acos(np.clip(v1 @ v2 /
                     (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1)))
        s = ang(H1, N, H2) + ang(H1, N, Cn) + ang(H2, N, Cn)
        rep["donor_N_angle_sum_deg"] = round(s, 1)           # 360 = planar, <360 pyramidal
        rep["donor_pyramidalization_deg"] = round(360.0 - s, 1)
    if idx["acc_N"] is not None:
        N = coords_ang[idx["acc_N"]]
        O1, O2 = coords_ang[idx["acc_O"][0]], coords_ang[idx["acc_O"][1]]
        Cn = ring[np.argmin(np.linalg.norm(ring - N, axis=1))]
        # NO2 twist = dihedral of the NO2 plane vs the ring plane (0 = coplanar)
        nno2 = np.cross(O1 - N, O2 - N); nno2 /= np.linalg.norm(nno2)
        phi = math.degrees(math.acos(min(1, abs(nno2 @ n))))  # angle between plane normals
        rep["acc_NO2_twist_deg"] = round(phi, 1)             # 0 = coplanar, 90 = perpendicular
    return rep

# ---------------------------------------------------------------- orbital analysis
def orbital_centroids(wfn):
    """Return (natom-independent) MO centroids <phi|r|phi> in Angstrom for all MOs."""
    mints = psi4.core.MintsHelper(wfn.basisset())
    dip = [np.asarray(m) for m in mints.ao_dipole()]     # x,y,z AO dipole ints (<mu|r|nu>)
    C = np.asarray(wfn.Ca_subset("AO", "ALL"))           # (nao, nmo)
    cent = np.zeros((C.shape[1], 3))
    for ax in range(3):
        cent[:, ax] = np.einsum("pi,pq,qi->i", C, dip[ax], C)
    return cent * BOHR2ANG

def analyze_state(st, nocc, cent):
    """Dominant orbital character (%), hole-particle distance for one TD state."""
    X = np.asarray(st["RIGHT EIGENVECTOR ALPHA"])   # (nocc, nvir)
    L = np.asarray(st["LEFT EIGENVECTOR ALPHA"])
    # RPA X/Y split; weights w = X^2 - Y^2 (alpha), report relative %
    Xamp = 0.5 * (X + L); Yamp = 0.5 * (X - L)
    w = Xamp ** 2 - Yamp ** 2
    wabs = np.abs(w)
    tot = wabs.sum()
    order = np.dstack(np.unravel_index(np.argsort(wabs, axis=None)[::-1], w.shape))[0]
    contribs = []
    for (i, a) in order[:4]:
        pct = 100.0 * wabs[i, a] / tot
        if pct < 5:
            break
        occ_lbl = "HOMO" + ("" if i == nocc - 1 else "-%d" % (nocc - 1 - i))
        vir_lbl = "LUMO" + ("" if a == 0 else "+%d" % a)
        contribs.append({"from": occ_lbl, "to": vir_lbl, "weight_pct": round(pct, 1),
                         "occ_index": int(i), "vir_index": int(a)})
    # hole-particle distance from dominant pair
    i0, a0 = order[0]
    d_ct = float(np.linalg.norm(cent[nocc + a0] - cent[i0]))
    return contribs, d_ct

def classify(f, d_ct, contribs):
    """Conservative, defensible auto-label. n->pi* vs forbidden-pi->pi* is NOT
    asserted automatically (needs orbital-symmetry inspection) -> 'dark/weak'.
    The specific n->pi* assignments are made by inspection in results.md."""
    bright = f >= 0.01
    if d_ct >= 2.0 and bright:
        typ = "CT"
    elif bright:
        typ = "pi->pi*"
    else:
        typ = "dark/weak"
    return typ, bright

# ---------------------------------------------------------------- main
def run(label):
    spec = MOLECULES[label]
    lines, symbols, idx = hexagon(spec["sub"])
    geom = "\n".join(["%d 1" % spec["charge"]] + lines +
                     ["symmetry c1", "units angstrom", "no_reorient", "no_com"])
    psi4.set_memory("24 GB")
    psi4.set_num_threads(9)

    # ---- geometry optimization
    psi4.core.set_output_file(os.path.join(HERE, "logs", f"{label}_opt.out"), False)
    mol = psi4.geometry(geom)
    psi4.set_options({"basis": OPT_BASIS, "scf_type": "df", "reference": "rks",
                      "e_convergence": 1e-8, "d_convergence": 1e-8,
                      "g_convergence": "gau_tight", "geom_maxiter": 200,
                      "maxiter": 300})
    eopt = psi4.optimize("b3lyp", molecule=mol)
    coords = np.asarray(mol.geometry()) * BOHR2ANG        # Angstrom, input atom order
    # save xyz
    with open(os.path.join(HERE, "geometries", f"{label}.xyz"), "w") as fh:
        fh.write("%d\n%s  optimized B3LYP/%s (C1)  E=%.8f Ha\n" %
                 (len(symbols), spec["name"], OPT_BASIS, eopt))
        for s, (x, y, z) in zip(symbols, coords):
            fh.write("%-2s %14.8f %14.8f %14.8f\n" % (s, x, y, z))
    geo_metrics = planarity_report(coords, idx)
    geo_metrics["opt_level"] = f"B3LYP/{OPT_BASIS} (C1, gau_tight)"
    geo_metrics["opt_energy_Ha"] = float(eopt)

    out = {"label": label, "name": spec["name"], "smiles": spec["smiles"],
           "geometry": geo_metrics, "td_basis": TD_BASIS, "functionals": {}}

    # ---- TD-DFT per functional
    for func in FUNCS:
        psi4.core.clean()                                  # gotcha #1: between jobs
        psi4.core.set_output_file(os.path.join(HERE, "logs", f"{label}_{func}.out"), False)
        m2 = psi4.geometry(geom)
        m2.set_geometry(mol.geometry())                    # reuse optimized coords
        psi4.set_options({"basis": TD_BASIS, "scf_type": "df", "reference": "rks",
                          "e_convergence": 1e-8, "d_convergence": 1e-8, "maxiter": 300,
                          "save_jk": True})
        escf, wfn = psi4.energy(func, molecule=m2, return_wfn=True)
        nocc = wfn.nalpha()
        cent = orbital_centroids(wfn)
        res = tdscf_excitations(wfn, states=N_STATES, tda=False,
                                r_convergence=1e-5, maxiter=120)
        states = []
        for k, st in enumerate(res):
            e_ev = float(st["EXCITATION ENERGY"]) * HA2EV
            f = float(st["OSCILLATOR STRENGTH (LEN)"])
            contribs, d_ct = analyze_state(st, nocc, cent)
            typ, bright = classify(f, d_ct, contribs)
            states.append({
                "state": k + 1,
                "energy_eV": round(e_ev, 4),
                "wavelength_nm": round(EV2NM / e_ev, 2),
                "f": round(f, 5),
                "hole_particle_dist_ang": round(d_ct, 2),
                "type": typ,
                "bright": bright,
                "dominant": contribs,
            })
        # lowest bright state + radiative lifetime  (A21 = 0.667 * nu_cm^2 * f)
        bright_states = [s for s in states if s["f"] >= 0.01]
        tau = None; bright_ref = None
        if bright_states:
            b = min(bright_states, key=lambda s: s["energy_eV"])
            nu_cm = b["energy_eV"] * EV2CM
            A21 = 0.667 * nu_cm ** 2 * b["f"]
            tau = 1.0 / A21
            bright_ref = {"state": b["state"], "energy_eV": b["energy_eV"],
                          "wavelength_nm": b["wavelength_nm"], "f": b["f"],
                          "A21_s^-1": A21, "tau_rad_s": tau, "tau_rad_ns": tau * 1e9,
                          "type": b["type"]}
        out["functionals"][func] = {
            "scf_energy_Ha": float(escf),
            "n_states": len(states),
            "states": states,
            "lowest_bright": bright_ref,
        }

    with open(os.path.join(HERE, "results", f"{label}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[{label}] done: opt E={eopt:.6f}; "
          + "; ".join(f"{fn} lowest-bright "
                      f"{out['functionals'][fn]['lowest_bright']['wavelength_nm'] if out['functionals'][fn]['lowest_bright'] else 'none'} nm"
                      for fn in FUNCS))


if __name__ == "__main__":
    run(sys.argv[1])
