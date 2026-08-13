#!/usr/bin/env python
"""
Is the planar B3LYP structure a minimum, or a saddle point?

The optimization converges to a structure that is planar to four decimals:
inter-ring twist 0.0 deg, amine angle sum exactly 360 deg. Two reasons not to
take that at face value:

  1. calcs/uvvis-pushpull/run_one.py seeds its aniline N-H bonds umbrella-style
     specifically to avoid relaxing "toward the planar saddle" -- the author of
     the earlier work hit this trap on a smaller molecule.
  2. B3LYP is known to over-planarize conjugated amine donors.

A frequency calculation is the rigorous answer, but an analytic Hessian on 39
atoms is hours of CPU for a question that is not this experiment's deliverable.
This is the proportionate check instead: rigidly displace along the two
coordinates that could be unstable and see whether the energy rises. If it does
in both directions, the planar structure is at least a local minimum along
those coordinates -- which is the specific worry, not a general one.

LIMITATION, stated plainly: these are RIGID displacements, not relaxed scans,
and they probe two coordinates rather than all 3N-6. A rise in energy here does
not prove the structure is a true minimum; it only rules out the two specific
instabilities that motivated the check. The README says so too.

Usage: check_stationary.py [--basis def2-svp] [--threads 4] [--memory "4 GB"]
"""
import os, sys, json, math, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PSI_SCRATCH", os.path.join(HERE, "scratch"))

import numpy as np
import psi4

from run_tddft import (read_xyz, psi4_geometry_block, verify_topology,
                       geometry_report, AMINE_N, AMINE_SUBS, LINK_BOND)

# Every atom on the dimethylaniline side of the aryl-furan bond. Rotating this
# fragment about that bond is the inter-ring twist coordinate.
DONOR_FRAGMENT = list(range(0, 19))


def rotate_about_axis(coords, indices, p0, p1, degrees):
    """Rigidly rotate `indices` about the axis p0->p1 by `degrees`."""
    axis = p1 - p0
    axis = axis / np.linalg.norm(axis)
    th = math.radians(degrees)
    c, s = math.cos(th), math.sin(th)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    R = np.eye(3) + s * K + (1 - c) * (K @ K)      # Rodrigues
    out = coords.copy()
    out[indices] = (out[indices] - p0) @ R.T + p0
    return out


def pyramidalize_amine(coords, delta_ang):
    """Push the amine N out of the plane of its three substituents.

    Rigid and therefore crude: it stretches the three N-C bonds by <0.5% at
    the displacements used here. Adequate to answer "does the energy rise?",
    not a relaxed umbrella scan.
    """
    out = coords.copy()
    subs = out[AMINE_SUBS]
    centroid = subs.mean(0)
    u, s, vt = np.linalg.svd(subs - centroid)
    normal = vt[2]
    out[AMINE_N] = out[AMINE_N] + normal * delta_ang
    return out


def single_point(symbols, coords, functional, basis, label, log_dir):
    psi4.core.clean()
    psi4.core.set_output_file(os.path.join(log_dir, f"chk_{label}.out"), False)
    mol = psi4.geometry(psi4_geometry_block(symbols, coords))
    psi4.set_options({"basis": basis, "scf_type": "df", "reference": "rks",
                      "e_convergence": 1e-8, "d_convergence": 1e-8, "maxiter": 300})
    return float(psi4.energy(functional, molecule=mol))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--geometry",
                   default=os.path.join(HERE, "geometry", "dcdhf-me2-def2-svp-opt.xyz"))
    p.add_argument("--basis", default="def2-svp")
    p.add_argument("--functional", default="b3lyp")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--memory", default="4 GB")
    p.add_argument("--twist-deg", type=float, nargs="*", default=[-20.0, -10.0, 10.0, 20.0])
    p.add_argument("--pyramid-ang", type=float, nargs="*", default=[-0.15, 0.15])
    args = p.parse_args()

    symbols, coords, comment = read_xyz(args.geometry)
    verify_topology(symbols, coords)
    psi4.set_memory(args.memory)
    psi4.set_num_threads(args.threads)
    log_dir = os.path.join(HERE, "logs")
    os.makedirs(log_dir, exist_ok=True)

    ref = single_point(symbols, coords, args.functional, args.basis, "ref", log_dir)
    print(f"reference (optimized, planar): {ref:.8f} Ha")

    out = {"reference_energy_Ha": ref, "geometry": os.path.relpath(args.geometry, HERE),
           "geometry_comment": comment,
           "level": f"{args.functional}/{args.basis} single points, rigid displacements",
           "limitation": ("Rigid displacements along two coordinates only, not a "
                          "frequency calculation. Rules out the two specific "
                          "instabilities motivating the check; does not prove a "
                          "true minimum."),
           "twist_scan": [], "pyramidalization_scan": []}

    p0, p1 = coords[LINK_BOND[0]], coords[LINK_BOND[1]]
    for deg in args.twist_deg:
        disp = rotate_about_axis(coords, DONOR_FRAGMENT, p0, p1, deg)
        e = single_point(symbols, disp, args.functional, args.basis,
                         f"twist{deg:+.0f}".replace(".", "p"), log_dir)
        rep = geometry_report(disp)
        d_kcal = (e - ref) * 627.5094740631
        out["twist_scan"].append({
            "displacement_deg": deg,
            "resulting_twist_deg": rep["interring_twist_deg"],
            "energy_Ha": e, "delta_E_kcal_per_mol": round(d_kcal, 4)})
        print(f"  twist {deg:+6.1f} deg -> twist={rep['interring_twist_deg']:5.1f} deg  "
              f"dE = {d_kcal:+8.3f} kcal/mol")

    for delta in args.pyramid_ang:
        disp = pyramidalize_amine(coords, delta)
        e = single_point(symbols, disp, args.functional, args.basis,
                         f"pyr{delta:+.2f}".replace(".", "p"), log_dir)
        rep = geometry_report(disp)
        d_kcal = (e - ref) * 627.5094740631
        out["pyramidalization_scan"].append({
            "displacement_ang": delta,
            "resulting_pyramidalization_deg": rep["amine_pyramidalization_deg"],
            "energy_Ha": e, "delta_E_kcal_per_mol": round(d_kcal, 4)})
        print(f"  amine N {delta:+.2f} A -> pyr={rep['amine_pyramidalization_deg']:5.1f} deg  "
              f"dE = {d_kcal:+8.3f} kcal/mol")

    # The optimized structure is planar, so every +/- displacement pair is
    # related by the molecular mirror plane and MUST be isoenergetic. Any split
    # within a pair measures error in the displacement construction, not
    # physics -- so this is a self-test of the machinery above, and it runs
    # before the conclusion is allowed to depend on it.
    out["symmetry_pairs"] = []
    for scan, key, unit in (("twist_scan", "displacement_deg", "deg"),
                            ("pyramidalization_scan", "displacement_ang", "ang")):
        by_mag = {}
        for s in out[scan]:
            by_mag.setdefault(abs(s[key]), []).append(s)
        for mag, pair in sorted(by_mag.items()):
            if len(pair) != 2:
                continue
            split = abs(pair[0]["energy_Ha"] - pair[1]["energy_Ha"])
            out["symmetry_pairs"].append({
                "scan": scan, "magnitude": mag, "unit": unit,
                "energy_split_Ha": split,
                "energy_split_microhartree": round(split * 1e6, 4),
                "consistent": bool(split < 1e-6)})
            flag = "ok" if split < 1e-6 else "INCONSISTENT"
            print(f"  symmetry pair {scan} +/-{mag}{unit}: "
                  f"split = {split * 1e6:.4f} uHa  [{flag}]")
    out["symmetry_check_passed"] = bool(
        out["symmetry_pairs"]) and all(p["consistent"] for p in out["symmetry_pairs"])
    if not out["symmetry_check_passed"]:
        print("  WARNING: mirror-related displacements are not isoenergetic; "
              "suspect the displacement construction before believing the verdict")

    rises = ([s["delta_E_kcal_per_mol"] > 0 for s in out["twist_scan"]] +
             [s["delta_E_kcal_per_mol"] > 0 for s in out["pyramidalization_scan"]])
    out["all_displacements_raise_energy"] = bool(all(rises))
    if not out["symmetry_check_passed"]:
        out["verdict"] = ("INCONCLUSIVE: mirror-related displacements are not "
                          "isoenergetic, so the displacement construction is "
                          "suspect and the energy comparisons cannot be trusted.")
    elif all(rises):
        out["verdict"] = ("Energy rises for every tested displacement: the planar "
                          "structure is a local minimum along the inter-ring twist "
                          "and amine pyramidalization coordinates. This is NOT a "
                          "frequency calculation and no true minimum is claimed.")
    else:
        out["verdict"] = ("At least one displacement LOWERS the energy: the planar "
                          "structure is a saddle point along that coordinate.")
    print("\n" + out["verdict"])

    with open(os.path.join(HERE, "results", "stationary_check.json"), "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
