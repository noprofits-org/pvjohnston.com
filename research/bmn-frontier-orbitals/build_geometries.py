#!/usr/bin/env python
"""
Construct every starting structure for the donor-strength ladder.

Two families, built two different ways, both writing geometry/<slug>-start.xyz:

  Phase 1, benzylidenemalononitrile p-X-C6H4-CH=C(CN)2 for X = H, F, NH2, NMe2.
      Built ANALYTICALLY from standard bond lengths and sp2 angles. No force
      field is available in this environment -- RDKit, OpenBabel and ASE are
      all absent from both the psi4_19 env and the system interpreter -- which
      is the same wall research/dcdhf-me2-transitions hit for benzene, and it
      is handled the same way. The force-field-to-DFT continuity of that
      experiment's DCDHF-Me2 leg is NOT available here and is not claimed.

  Phase 2, DCDHF-F and DCDHF-H. Built by SUBSTITUTION from that experiment's
      optimized DCDHF-Me2 structure: delete the NMe2 group and place one atom
      along the original C-N bond vector.

Both families then get the same deliberate distortion, and that is the point
of this script rather than an afterthought. A hand-built planar structure with
a planar amine can be a symmetry-imposed stationary point: the optimizer sits
on it and "planar" gets reported as a result when it was an assumption. So
every start is twisted 30 degrees about the aryl-acceptor bond, and every
amine nitrogen is pushed 0.20 A out of its substituent plane, so that a planar
optimized structure is a destination the optimizer had to travel to. Both
magnitudes are preregistered; for scale, the prior experiment's UFF DCDHF-Me2
start carried 54.6 degrees of twist and 11.3 degrees of pyramidalization and
relaxed to 0.0 on both.

Usage: build_geometries.py [--force]
"""
import os, sys, math, json, argparse, hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = os.path.join(HERE, "geometry")

# The DCDHF-Me2 minimum this experiment substitutes into. Read-only: the prior
# experiment is never modified, only consumed.
ME2_OPT = os.path.normpath(os.path.join(
    HERE, "..", "dcdhf-me2-transitions", "geometry", "dcdhf-me2-def2-svp-opt.xyz"))

# ------------------------------------------------------------------ constants
# Standard sp2 organic bond lengths, in Angstrom. These are starting-structure
# inputs, not results: the B3LYP/def2-SVP optimization decides the real ones,
# and geometry_report() records how far it moved.
R_RING = 1.3915        # aromatic C-C; also the hexagon circumradius (side==R)
CH_ARYL = 1.08
C_ARYL_VINYL = 1.46    # aryl C -- vinyl C single bond
C_C_DOUBLE = 1.35      # the exocyclic C=C bridge
C_CN = 1.43            # sp2 C -- nitrile C
CN_TRIPLE = 1.16
CH_VINYL = 1.09
C_F_ARYL = 1.35        # preregistered substitution length
C_H_SUB = 1.09         # preregistered substitution length
C_N_ARYL = 1.40        # aryl C -- amine N
N_H = 1.01
N_CH3 = 1.45
C_H_METHYL = 1.09

SP2 = 120.0
TETRAHEDRAL = 109.5

# The dicyanovinyl arm does NOT get idealized 120 degree angles, and this is a
# correction to the obvious construction rather than a refinement of it. The
# geminal nitriles are crowded against the ortho ring hydrogens: at 120 degrees
# throughout, the cis nitrile carbon lands 1.60 A from the ortho H -- shorter
# than a C-H bond, and close enough that the connectivity check would read it
# as bonded. Real benzylidenemalononitrile relieves that by opening the angles
# at the bridge, so those values are used here.
ANGLE_ARYL_VINYL_C = 130.0     # C(aryl)-C(vinyl)=C
ANGLE_ARYL_VINYL_H = 115.0     # C(aryl)-C(vinyl)-H
ANGLE_VINYL_CN = 122.0         # C(vinyl)=C-C(N), giving N-C-C-N of 116

# Preregistered distortions.
TWIST_DEG = 30.0
PYRAMID_ANG = 0.20

# N-methyl rotamer, as a rotation about the N-CH3 axis away from the position
# that eclipses the N->ring direction. Not preregistered, because it is a
# construction detail the optimizer relaxes and no diagnostic here reads a
# methyl torsion -- but it is not arbitrary either: at 0 degrees one C-H points
# straight at the ortho ring hydrogen, 1.57 A away, which is a real clash rather
# than a geminal contact. 60 degrees is the staggered position, symmetric
# between the two methyls, and it is also where the clearance is widest
# (2.11 A). Scanned over the full 120-degree period to confirm both.
METHYL_ROTAMER_OFFSET = 60.0

# --------------------------------------------------------- small vector tools
def unit(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise ValueError("cannot normalize a zero-length vector")
    return v / n


def rotation_matrix(axis, angle_deg):
    """Right-handed rotation about `axis` through the origin (Rodrigues)."""
    a = unit(np.asarray(axis, dtype=float))
    t = math.radians(angle_deg)
    K = np.array([[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]])
    return np.eye(3) + math.sin(t) * K + (1.0 - math.cos(t)) * (K @ K)


# Cordero covalent radii, Angstrom. Only the elements this experiment uses.
COVALENT_RADII = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57}
BOND_TOLERANCE = 1.25


def bonded_pairs(symbols, coords):
    """Adjacency from element-aware covalent radii.

    A single flat cutoff does not work here and the failure is not academic. At
    1.9 A a crowded H...H contact of 1.57 A reads as a bond, which (a) makes
    split_at_bond believe an open bond is part of a ring, and (b) hides real
    steric clashes from the very check meant to catch them -- a clash and a bond
    become indistinguishable. Scaling the sum of covalent radii separates them
    cleanly: H-H bonds at 0.78 A, so a 1.57 A contact is correctly non-bonded,
    while a 1.54 A C-C stays a bond.
    """
    n = len(symbols)
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            limit = BOND_TOLERANCE * (COVALENT_RADII[symbols[i]]
                                      + COVALENT_RADII[symbols[j]])
            if np.linalg.norm(coords[i] - coords[j]) < limit:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def min_nonbonded_contact(symbols, coords):
    """Closest approach between atoms that are not bonded or geminal (1-2/1-3).

    Geminal pairs are excluded because their distance is fixed by bond lengths
    and the angle between them -- two methyl hydrogens are 1.78 A apart in every
    correct structure, and reporting that as a clash would bury the real ones.
    """
    adj = bonded_pairs(symbols, coords)
    worst, where = float("inf"), None
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            if j in adj[i] or (adj[i] & adj[j]):
                continue
            d = float(np.linalg.norm(coords[i] - coords[j]))
            if d < worst:
                worst, where = d, (i, j)
    return worst, where


def split_at_bond(symbols, coords, i, j):
    """Atoms reachable from j once the i-j bond is cut. Raises if i and j stay
    connected by another path, which would mean the 'bond' is in a ring and
    rotating about it would tear the molecule apart."""
    adj = bonded_pairs(symbols, coords)
    if j not in adj[i]:
        raise ValueError(f"atoms {i} and {j} are not bonded; cannot rotate about them")
    seen, stack = {j}, [j]
    while stack:
        k = stack.pop()
        for m in adj[k]:
            if m == i and k == j:
                continue                      # the cut bond itself
            if m not in seen:
                seen.add(m)
                stack.append(m)
    if i in seen:
        raise ValueError(f"bond {i}-{j} is in a ring; rotating about it is not defined")
    return sorted(seen)


def twist_about_bond(symbols, coords, i, j, angle_deg):
    """Rotate the j-side fragment about the axis through atoms i and j."""
    coords = coords.copy()
    movers = [k for k in split_at_bond(symbols, coords, i, j) if k != j]
    R = rotation_matrix(coords[j] - coords[i], angle_deg)
    coords[movers] = (R @ (coords[movers] - coords[j]).T).T + coords[j]
    return coords


def pyramidalize(coords, n_idx, sub_idx, displacement):
    """Push atom n_idx out of the plane of its three substituents.

    This is the amine coordinate the prior experiment's stationary check probed
    at 0.15 A. Displacing the nitrogen rather than tilting its substituents
    keeps the construction to one number and one direction, at the cost of
    stretching the three bonds by well under 2% -- which the optimizer removes
    in its first few steps.
    """
    coords = coords.copy()
    a, b, c = (coords[k] for k in sub_idx)
    normal = unit(np.cross(b - a, c - a))
    coords[n_idx] = coords[n_idx] + displacement * normal
    return coords


def in_plane(origin, ref_dir, angle_deg, length):
    """Place an atom `length` from `origin`, at `angle_deg` from `ref_dir`.

    Rotation is about z, so this is only valid while the fragment being built
    still lies in the xy-plane -- which it does: every structure here is
    assembled flat and distorted afterwards.
    """
    d = rotation_matrix([0, 0, 1], angle_deg) @ unit(np.asarray(ref_dir, dtype=float))
    return np.asarray(origin, dtype=float) + length * unit(d)


def methyl_hydrogens(c_pos, anchor_pos, reference_pos, r=C_H_METHYL,
                     angle_deg=TETRAHEDRAL, offset_deg=METHYL_ROTAMER_OFFSET):
    """Three tetrahedral H around a methyl carbon bonded to `anchor_pos`.

    The rotamer is measured from the direction of `reference_pos` projected
    perpendicular to the C-anchor axis, so it is deterministic rather than
    dependent on an arbitrary axis choice, and then rotated by `offset_deg`.
    See METHYL_ROTAMER_OFFSET for why that offset is not zero.
    """
    u = unit(anchor_pos - c_pos)
    ref = reference_pos - c_pos
    perp = ref - (ref @ u) * u
    if np.linalg.norm(perp) < 1e-6:            # reference is collinear; pick any
        perp = np.cross(u, [0.0, 0.0, 1.0])
        if np.linalg.norm(perp) < 1e-6:
            perp = np.cross(u, [0.0, 1.0, 0.0])
    v = unit(perp)
    w = np.cross(u, v)
    t = math.radians(angle_deg)
    out = []
    for k in range(3):
        a = math.radians(120.0 * k + offset_deg)
        d = math.cos(t) * u + math.sin(t) * (math.cos(a) * v + math.sin(a) * w)
        out.append(c_pos + r * unit(d))
    return out


# ------------------------------------------------------------------- xyz i/o
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


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------- phase 1: the BMN scaffold
# Atom order is FIXED and identical across all four rungs for indices 0-16, so
# one set of index tables describes every molecule in the ladder and the
# diagnostics cannot silently mean different things on different rungs. The
# substituent occupies 17 onwards.
#
#   0-5   aryl ring carbons, C0 bears the vinyl arm, C3 bears X
#   6-9   aryl H on C1, C2, C4, C5
#   10    vinyl CH carbon      11  its H       12  dicyanovinyl central C
#   13,14 first  C#N           15,16  second C#N
#   17+   substituent X
ARYL_RING = [0, 1, 2, 3, 4, 5]
ARYL_H = [6, 7, 8, 9]
VINYL_C, VINYL_H, ACCEPTOR_C = 10, 11, 12
BMN_NITRILES = [(13, 14), (15, 16)]
BMN_LINK_BOND = (0, 10)          # aryl -- vinyl, the twist axis
BMN_BRIDGE_BOND = (10, 12)       # the exocyclic C=C
BMN_IPSO_X = 3                   # ring carbon bearing the substituent
BMN_X_FIRST = 17


def build_bmn_core():
    """The 17 atoms every rung shares, planar, in the xy-plane."""
    symbols, coords = [], []

    # Regular hexagon: for a regular hexagon the side equals the circumradius,
    # so this reproduces the 1.3915 A C-C of the prior experiment's benzene.
    for k in range(6):
        a = math.radians(60.0 * k)
        symbols.append("C")
        coords.append([R_RING * math.cos(a), R_RING * math.sin(a), 0.0])

    # Ring hydrogens, radially outward from the ring centre.
    for k in (1, 2, 4, 5):
        a = math.radians(60.0 * k)
        r = R_RING + CH_ARYL
        symbols.append("H")
        coords.append([r * math.cos(a), r * math.sin(a), 0.0])

    c0 = np.array(coords[0])
    out = np.array([1.0, 0.0, 0.0])            # radial direction at C0

    # Everything below is still planar (all z = 0); the twist comes later.
    c_vinyl = c0 + C_ARYL_VINYL * out
    back = -out                                 # from the vinyl C toward the ring
    c_acceptor = in_plane(c_vinyl, back, -ANGLE_ARYL_VINYL_C, C_C_DOUBLE)
    h_vinyl = in_plane(c_vinyl, back, ANGLE_ARYL_VINYL_H, CH_VINYL)

    # Dicyanovinyl carbon: two nitrile arms straddling the bridge bond.
    back2 = unit(c_vinyl - c_acceptor)
    cn1 = in_plane(c_acceptor, back2, ANGLE_VINYL_CN, C_CN)
    cn2 = in_plane(c_acceptor, back2, -ANGLE_VINYL_CN, C_CN)
    n1 = cn1 + CN_TRIPLE * unit(cn1 - c_acceptor)     # nitriles are linear
    n2 = cn2 + CN_TRIPLE * unit(cn2 - c_acceptor)

    for sym, pos in (("C", c_vinyl), ("H", h_vinyl), ("C", c_acceptor),
                     ("C", cn1), ("N", n1), ("C", cn2), ("N", n2)):
        symbols.append(sym)
        coords.append(list(pos))
    return symbols, np.asarray(coords)


def build_bmn(substituent):
    """One rung of the ladder, distortions applied."""
    symbols, coords = build_bmn_core()
    symbols, coords = list(symbols), list(coords)

    c_ipso = np.asarray(coords[BMN_IPSO_X])
    out = unit(c_ipso)                          # radially outward at C3

    if substituent == "H":
        symbols.append("H")
        coords.append(c_ipso + CH_ARYL * out)
    elif substituent == "F":
        symbols.append("F")
        coords.append(c_ipso + C_F_ARYL * out)
    elif substituent in ("NH2", "NMe2"):
        n_pos = c_ipso + C_N_ARYL * out
        back = -out
        d1 = rotation_matrix([0, 0, 1], SP2) @ back
        d2 = rotation_matrix([0, 0, 1], -SP2) @ back
        symbols.append("N")
        coords.append(n_pos)
        if substituent == "NH2":
            for d in (d1, d2):
                symbols.append("H")
                coords.append(n_pos + N_H * d)
        else:
            m1 = n_pos + N_CH3 * d1
            m2 = n_pos + N_CH3 * d2
            symbols += ["C", "C"]
            coords += [m1, m2]
            for m in (m1, m2):
                for h in methyl_hydrogens(m, n_pos, c_ipso):
                    symbols.append("H")
                    coords.append(h)
    else:
        raise ValueError(f"unknown substituent {substituent!r}")

    coords = np.asarray(coords, dtype=float)
    coords = twist_about_bond(symbols, coords, *BMN_LINK_BOND, TWIST_DEG)
    if substituent in ("NH2", "NMe2"):
        n_idx = BMN_X_FIRST
        subs = [BMN_IPSO_X, BMN_X_FIRST + 1, BMN_X_FIRST + 2]
        coords = pyramidalize(coords, n_idx, subs, PYRAMID_ANG)
    return symbols, coords


# --------------------------------------------- phase 2: the DCDHF scaffold
# Index tables into the PRIOR experiment's 39-atom DCDHF-Me2 file. Copied from
# its run_tddft.py, and re-derived for the substituted structures below rather
# than transcribed by hand.
ME2_AMINE_N = 0
ME2_RING_C_ON_N = 1                 # aryl carbon the NMe2 hangs off
ME2_METHYL_C = [11, 12]
ME2_METHYL_H = [13, 14, 15, 16, 17, 18]
ME2_LINK_BOND = (6, 19)             # aryl -- dihydrofuran, the twist axis
ME2_DELETE = sorted([ME2_AMINE_N] + ME2_METHYL_C + ME2_METHYL_H)


def build_dcdhf(substituent):
    """DCDHF-F or DCDHF-H, by substitution from the DCDHF-Me2 minimum."""
    symbols, coords, src_comment = read_xyz(ME2_OPT)
    if len(symbols) != 39:
        raise SystemExit(f"{ME2_OPT}: expected 39 atoms, found {len(symbols)}")
    for k in [ME2_AMINE_N] + ME2_METHYL_C:
        expected = "N" if k == ME2_AMINE_N else "C"
        if symbols[k] != expected:
            raise SystemExit(f"{ME2_OPT}: atom {k} is {symbols[k]}, expected "
                             f"{expected} -- atom order is not what this script assumes")
    for k in ME2_METHYL_H:
        if symbols[k] != "H":
            raise SystemExit(f"{ME2_OPT}: atom {k} is {symbols[k]}, expected H")

    # Substitution direction: along the original C(ring)->N bond vector, so the
    # replacement sits where the donor was rather than in an invented direction.
    c_ring = coords[ME2_RING_C_ON_N]
    direction = unit(coords[ME2_AMINE_N] - c_ring)
    r_new = C_F_ARYL if substituent == "F" else C_H_SUB
    new_atom = c_ring + r_new * direction

    keep = [k for k in range(39) if k not in ME2_DELETE]
    remap = {old: new for new, old in enumerate(keep)}
    new_symbols = [symbols[k] for k in keep] + [substituent]
    new_coords = np.vstack([coords[keep], new_atom])

    link = (remap[ME2_LINK_BOND[0]], remap[ME2_LINK_BOND[1]])
    new_coords = twist_about_bond(new_symbols, new_coords, *link, TWIST_DEG)
    return new_symbols, new_coords, remap, link, src_comment


# ------------------------------------------------------------------ checking
def formula_of(symbols):
    counts = {}
    for s in symbols:
        counts[s] = counts.get(s, 0) + 1
    return counts


def format_formula(counts):
    return "".join(f"{el}{n if n > 1 else ''}" for el, n in sorted(counts.items()))


def check_structure(slug, symbols, coords, expected_formula):
    """Fail loudly rather than hand a broken structure to a multi-hour job."""
    problems = []
    got = formula_of(symbols)
    if got != expected_formula:
        problems.append(f"formula {format_formula(got)}, expected "
                        f"{format_formula(expected_formula)}")
    n = len(symbols)
    # A starting structure is allowed to be strained -- that is the whole point
    # of the deliberate twist -- but not broken. 1.4 A is below any real
    # non-bonded contact these molecules can reach under a 30 degree twist and
    # above the compressions the twist actually produces, so this catches a
    # construction error without vetoing the intended strain.
    contact, where = min_nonbonded_contact(symbols, coords)
    if where is not None and contact < 1.4:
        i, j = where
        problems.append(f"non-bonded {i}({symbols[i]})...{j}({symbols[j]}) "
                        f"only {contact:.2f} A apart")
    adj = bonded_pairs(symbols, coords)
    seen, stack = {0}, [0]
    while stack:
        i = stack.pop()
        for j in adj[i]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    if len(seen) != n:
        problems.append(f"not a single connected fragment: {len(seen)}/{n} atoms")
    if problems:
        raise SystemExit(f"[{slug}] construction failed:\n  " + "\n  ".join(problems))
    return contact, where


MOLECULES = [
    ("bmn-h", "benzylidenemalononitrile", "H", {"C": 10, "H": 6, "N": 2}),
    ("bmn-f", "4-fluorobenzylidenemalononitrile", "F", {"C": 10, "H": 5, "F": 1, "N": 2}),
    ("bmn-nh2", "4-aminobenzylidenemalononitrile", "NH2", {"C": 10, "H": 7, "N": 3}),
    ("bmn-nme2", "4-(dimethylamino)benzylidenemalononitrile", "NMe2",
     {"C": 12, "H": 11, "N": 3}),
    ("dcdhf-h", "DCDHF-H", "H", {"C": 16, "H": 11, "N": 3, "O": 1}),
    ("dcdhf-f", "DCDHF-F", "F", {"C": 16, "H": 10, "F": 1, "N": 3, "O": 1}),
]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--force", action="store_true",
                   help="overwrite existing geometry/<slug>-start.xyz")
    args = p.parse_args()
    os.makedirs(GEOM, exist_ok=True)

    derived = {}
    for slug, name, sub, formula in MOLECULES:
        out_path = os.path.join(GEOM, f"{slug}-start.xyz")
        if os.path.exists(out_path) and not args.force:
            print(f"[{slug}] {os.path.relpath(out_path, HERE)} exists; skipping")
            continue

        if slug.startswith("bmn"):
            symbols, coords = build_bmn(sub)
            provenance = (f"built analytically from standard bond lengths "
                          f"(no force field available); twist {TWIST_DEG:g} deg")
            if sub in ("NH2", "NMe2"):
                provenance += f", amine N displaced {PYRAMID_ANG:g} A out of plane"
        else:
            symbols, coords, remap, link, src = build_dcdhf(sub)
            provenance = (f"NMe2 -> {sub} substitution on the DCDHF-Me2 "
                          f"B3LYP/def2-SVP minimum; twist {TWIST_DEG:g} deg")
            # Emit the remapped index tables so run_tddft.py's hardcoded
            # tables can be checked against what the substitution actually
            # produced, instead of being transcribed by eye.
            derived[slug] = {
                "source": os.path.relpath(ME2_OPT, os.path.join(HERE, "..", "..")),
                "source_comment": src,
                "source_sha256": sha256_of(ME2_OPT),
                "deleted_atoms_in_source": ME2_DELETE,
                "substituent_index": len(symbols) - 1,
                "donor_ring": [remap[k] for k in [1, 2, 4, 6, 7, 9]],
                "acceptor_ring": [remap[k] for k in [19, 20, 25, 24, 22]],
                "nitriles": [[remap[a], remap[b]]
                             for a, b in [(21, 23), (35, 37), (36, 38)]],
                "link_bond": list(link),
                "ipso_carbon": remap[ME2_RING_C_ON_N],
            }

        contact, where = check_structure(slug, symbols, coords, formula)
        write_xyz(out_path, symbols, coords,
                  f"{name} ({format_formula(formula)}) starting structure; {provenance}")
        print(f"[{slug}] {len(symbols):2d} atoms  {format_formula(formula):12s} "
              f"closest non-bonded contact {contact:.2f} A "
              f"({symbols[where[0]]}{where[0]}...{symbols[where[1]]}{where[1]})  -> "
              f"{os.path.relpath(out_path, HERE)}")

    if derived:
        path = os.path.join(GEOM, "dcdhf-derived-indices.json")
        with open(path, "w") as fh:
            json.dump(derived, fh, indent=2)
        print(f"wrote {os.path.relpath(path, HERE)} (index tables for run_tddft.py "
              f"to be checked against)")


if __name__ == "__main__":
    main()
