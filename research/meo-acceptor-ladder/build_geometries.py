#!/usr/bin/env python
"""
Construct starting structures for the acceptor-strength ladder.

The donor is fixed as para-methoxy and the acceptor is varied across three
rungs of increasing strength: cyano (CN), dicyanovinyl (DCV), and the
tricyanodihydrofuran (TCF) acceptor from the DCDHF series.

  meo-cn:   p-methoxybenzonitrile, built analytically.
  meo-dcv:  p-methoxybenzylidenemalononitrile, built analytically.
  meo-tcf:  OMe-substituted DCDHF, built by deleting the NMe2 group from the
            DCDHF-Me2 B3LYP/def2-SVP minimum and placing OMe along the
            original C(aryl)-N bond vector.

As in the donor-ladder experiment, every analytic start is twisted 30 degrees
about the aryl-acceptor bond so that a planar optimized structure is a result
the optimizer reached, not an assumption built into the input.

Usage: build_geometries.py [--force]
"""
import os, sys, math, json, argparse, hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = os.path.join(HERE, "geometry")

# The DCDHF-Me2 minimum this experiment substitutes into. Read-only.
ME2_OPT = os.path.normpath(os.path.join(
    HERE, "..", "dcdhf-me2-transitions", "geometry", "dcdhf-me2-def2-svp-opt.xyz"))

# ------------------------------------------------------------------ constants
# Standard sp2 organic bond lengths, in Angstrom. These are starting-structure
# inputs; the B3LYP/def2-SVP optimization decides the real values.
R_RING = 1.3915        # aromatic C-C; hexagon circumradius equals side
CH_ARYL = 1.08
C_ARYL_VINYL = 1.46    # aryl C -- vinyl C single bond
C_C_DOUBLE = 1.35      # exocyclic C=C bridge
C_CN = 1.43            # sp2 C -- nitrile C
CN_TRIPLE = 1.16
CH_VINYL = 1.09
C_ARYL_O = 1.36        # aryl C -- methoxy O
C_O_METHYL = 1.43      # methoxy O -- methyl C
C_H_METHYL = 1.09

SP2 = 120.0
TETRAHEDRAL = 109.5

# Dicyanovinyl arm angles, copied from the donor-ladder construction. The
# geminal nitriles are crowded against the ortho ring hydrogens, so the bridge
# angles are opened from ideal sp2 values.
ANGLE_ARYL_VINYL_C = 130.0     # C(aryl)-C(vinyl)=C
ANGLE_ARYL_VINYL_H = 115.0     # C(aryl)-C(vinyl)-H
ANGLE_VINYL_CN = 122.0         # C(vinyl)=C-C(N)

# Preregistered distortion.
TWIST_DEG = 30.0

# Methyl rotamer offset, copied from the donor ladder. At 0 degrees a C-H
# eclipses the ortho ring hydrogen; 60 degrees is staggered and gives the
# widest clearance.
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


# Cordero covalent radii, Angstrom.
COVALENT_RADII = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57}
BOND_TOLERANCE = 1.25


def bonded_pairs(symbols, coords):
    """Adjacency from element-aware covalent radii."""
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
    """Closest approach between atoms that are not bonded or geminal (1-2/1-3)."""
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
    """Atoms reachable from j once the i-j bond is cut."""
    adj = bonded_pairs(symbols, coords)
    if j not in adj[i]:
        raise ValueError(f"atoms {i} and {j} are not bonded; cannot rotate about them")
    seen, stack = {j}, [j]
    while stack:
        k = stack.pop()
        for m in adj[k]:
            if m == i and k == j:
                continue
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


def in_plane(origin, ref_dir, angle_deg, length):
    """Place an atom `length` from `origin`, at `angle_deg` from `ref_dir`."""
    d = rotation_matrix([0, 0, 1], angle_deg) @ unit(np.asarray(ref_dir, dtype=float))
    return np.asarray(origin, dtype=float) + length * unit(d)


def methyl_hydrogens(c_pos, anchor_pos, reference_pos, r=C_H_METHYL,
                     angle_deg=TETRAHEDRAL, offset_deg=METHYL_ROTAMER_OFFSET):
    """Three tetrahedral H around a methyl carbon bonded to `anchor_pos`."""
    u = unit(anchor_pos - c_pos)
    ref = reference_pos - c_pos
    perp = ref - (ref @ u) * u
    if np.linalg.norm(perp) < 1e-6:
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


# ------------------------------------------------------- common ring
# Atom order is FIXED for the analytic rungs where it can be:
#   0-5   aryl ring carbons, C0 bears the acceptor, C3 bears OMe
#   6-9   aryl H on C1, C2, C4, C5
ARYL_RING = [0, 1, 2, 3, 4, 5]
ARYL_H = [6, 7, 8, 9]
IPSO_ACCEPTOR = 0
IPSO_OMe = 3


def build_ring_and_hydrogens():
    """The 10 atoms every analytic rung shares: ring + H, planar in xy."""
    symbols, coords = [], []

    for k in range(6):
        a = math.radians(60.0 * k)
        symbols.append("C")
        coords.append([R_RING * math.cos(a), R_RING * math.sin(a), 0.0])

    for k in (1, 2, 4, 5):
        a = math.radians(60.0 * k)
        r = R_RING + CH_ARYL
        symbols.append("H")
        coords.append([r * math.cos(a), r * math.sin(a), 0.0])

    return symbols, np.asarray(coords)


def add_omethoxy(symbols, coords, ipso_index):
    """Append a methoxy group at ring carbon `ipso_index`; return new lists.

    The C(aryl)-O-C(methyl) angle is set to 120 degrees, roughly the sp2 value
    for anisole, so the methyl carbon is not collinear with the aryl-O bond.
    """
    symbols, coords = list(symbols), list(coords)
    c_ipso = np.asarray(coords[ipso_index])
    out = unit(c_ipso)                       # from ring centre toward ipso C
    o_pos = c_ipso + C_ARYL_O * out
    # Vector from O back toward the ring centre, then opened to ~120 deg.
    back = -out
    methyl_dir = rotation_matrix([0, 0, 1], 120.0) @ back
    methyl_c = o_pos + C_O_METHYL * unit(methyl_dir)
    symbols += ["O", "C"]
    coords += [o_pos, methyl_c]
    for h in methyl_hydrogens(methyl_c, o_pos, c_ipso):
        symbols.append("H")
        coords.append(h)
    return symbols, np.asarray(coords)


# ----------------------------------------------------------- meo-cn scaffold
# Atom order:
#   0-5   aryl ring carbons
#   6-9   aryl H
#   10    nitrile C, 11 nitrile N
#   12    methoxy O, 13 methyl C, 14-16 methyl H
CN_C, CN_N = 10, 11
CN_LINK_BOND = (0, 10)


def build_meo_cn():
    """p-methoxybenzonitrile, with the CN group tilted 30 deg out of the aryl plane."""
    symbols, coords = build_ring_and_hydrogens()
    symbols, coords = list(symbols), list(coords)

    c0 = np.asarray(coords[IPSO_ACCEPTOR])
    out = unit(c0)
    cn_c = c0 + C_CN * out
    n_pos = cn_c + CN_TRIPLE * out
    symbols += ["C", "N"]
    coords += [cn_c, n_pos]

    symbols, coords = add_omethoxy(symbols, coords, IPSO_OMe)

    coords = np.asarray(coords, dtype=float)
    return symbols, coords


# ---------------------------------------------------------- meo-dcv scaffold
# Atom order for the DCV arm matches the donor-ladder BMN core at indices
# 10-16, so the index tables in run_tddft.py can be reused directly.
# OMe follows at indices 17-21.
VINYL_C, VINYL_H, ACCEPTOR_C = 10, 11, 12
NITRILES = [(13, 14), (15, 16)]
LINK_BOND = (0, 10)          # aryl -- vinyl, the twist axis
BRIDGE_BOND = (10, 12)       # exocyclic C=C


def build_meo_dcv():
    """p-methoxybenzylidenemalononitrile."""
    symbols, coords = build_ring_and_hydrogens()
    symbols, coords = list(symbols), list(coords)

    c0 = np.asarray(coords[IPSO_ACCEPTOR])
    out = unit(c0)

    c_vinyl = c0 + C_ARYL_VINYL * out
    back = -out
    c_acceptor = in_plane(c_vinyl, back, -ANGLE_ARYL_VINYL_C, C_C_DOUBLE)
    h_vinyl = in_plane(c_vinyl, back, ANGLE_ARYL_VINYL_H, CH_VINYL)

    back2 = unit(c_vinyl - c_acceptor)
    cn1 = in_plane(c_acceptor, back2, ANGLE_VINYL_CN, C_CN)
    cn2 = in_plane(c_acceptor, back2, -ANGLE_VINYL_CN, C_CN)
    n1 = cn1 + CN_TRIPLE * unit(cn1 - c_acceptor)
    n2 = cn2 + CN_TRIPLE * unit(cn2 - c_acceptor)

    for sym, pos in (("C", c_vinyl), ("H", h_vinyl), ("C", c_acceptor),
                     ("C", cn1), ("N", n1), ("C", cn2), ("N", n2)):
        symbols.append(sym)
        coords.append(list(pos))

    symbols, coords = add_omethoxy(symbols, coords, IPSO_OMe)

    coords = np.asarray(coords, dtype=float)
    coords = twist_about_bond(symbols, coords, *LINK_BOND, TWIST_DEG)
    return symbols, coords


# ---------------------------------------------------------- meo-tcf scaffold
# Indices into the 39-atom DCDHF-Me2 optimized structure, copied from its
# run_tddft.py. The NMe2 group is deleted and replaced by OMe.
ME2_AMINE_N = 0
ME2_RING_C_ON_N = 1
ME2_METHYL_C = [11, 12]
ME2_METHYL_H = [13, 14, 15, 16, 17, 18]
ME2_DELETE = sorted([ME2_AMINE_N] + ME2_METHYL_C + ME2_METHYL_H)


def build_meo_tcf():
    """OMe-substituted DCDHF, by substitution from the DCDHF-Me2 minimum."""
    symbols, coords, src_comment = read_xyz(ME2_OPT)
    if len(symbols) != 39:
        raise SystemExit(f"{ME2_OPT}: expected 39 atoms, found {len(symbols)}")
    for k in [ME2_AMINE_N] + ME2_METHYL_C:
        expected = "N" if k == ME2_AMINE_N else "C"
        if symbols[k] != expected:
            raise SystemExit(f"{ME2_OPT}: atom {k} is {symbols[k]}, expected {expected}")
    for k in ME2_METHYL_H:
        if symbols[k] != "H":
            raise SystemExit(f"{ME2_OPT}: atom {k} is {symbols[k]}, expected H")

    c_ring = coords[ME2_RING_C_ON_N]

    # The NMe2 donor in DCDHF-Me2 is pyramidal, so the original C(aryl)-N vector
    # points out of the aryl plane. For anisole the C(aryl)-O bond must lie in
    # the aryl plane. Use the in-plane direction from the donor-ring centroid to
    # the ipso carbon.
    donor_ring_src = [1, 2, 4, 6, 7, 9]
    ring_pts = np.asarray([coords[k] for k in donor_ring_src])
    centroid = ring_pts.mean(axis=0)
    _, _, vt = np.linalg.svd(ring_pts - centroid)
    ring_normal = unit(vt[2])
    direction = unit(c_ring - centroid)             # in-plane C(aryl) -> O vector

    # OMe replaces NMe2. The O sits in the aryl plane and the methyl carbon is
    # opened to ~120 degrees from the O -> ring vector, also in the aryl plane.
    o_pos = c_ring + C_ARYL_O * direction
    back = -direction
    perp = unit(np.cross(ring_normal, back))        # in-plane, perpendicular to back
    if np.linalg.norm(perp) < 1e-6:
        perp = unit(np.cross(back, [0.0, 0.0, 1.0]))
    methyl_dir = unit(back * math.cos(math.radians(120.0)) +
                       perp * math.sin(math.radians(120.0)))
    methyl_c = o_pos + C_O_METHYL * methyl_dir
    new_atoms = [o_pos, methyl_c] + methyl_hydrogens(methyl_c, o_pos, c_ring)
    new_symbols = ["O", "C", "H", "H", "H"]

    keep = [k for k in range(39) if k not in ME2_DELETE]
    remap = {old: new for new, old in enumerate(keep)}
    new_symbols = [symbols[k] for k in keep] + new_symbols
    new_coords = np.vstack([coords[keep], np.asarray(new_atoms)])

    link = (remap[6], remap[19])  # aryl -- dihydrofuran single bond
    # The DCDHF-Me2 minimum is planar. Twisting the rigid dihydrofuran
    # acceptor 30 deg out of that plane produced an optimization that could
    # not recover planarity under gau_tight (trust radius collapsed). Start
    # planar instead; the optimizer still has to find and verify the minimum.
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
    ("meo-cn", "p-methoxybenzonitrile", "analytic",
     {"C": 8, "H": 7, "N": 1, "O": 1}),
    ("meo-dcv", "p-methoxybenzylidenemalononitrile", "analytic",
     {"C": 11, "H": 8, "N": 2, "O": 1}),
    ("meo-tcf", "OMe-substituted DCDHF", "substitution",
     {"C": 17, "H": 13, "N": 3, "O": 2}),
]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--force", action="store_true",
                   help="overwrite existing geometry/<slug>-start.xyz")
    args = p.parse_args()
    os.makedirs(GEOM, exist_ok=True)

    derived = {}
    for slug, name, method, formula in MOLECULES:
        out_path = os.path.join(GEOM, f"{slug}-start.xyz")
        if os.path.exists(out_path) and not args.force:
            print(f"[{slug}] {os.path.relpath(out_path, HERE)} exists; skipping")
            continue

        if method == "analytic":
            if slug == "meo-cn":
                symbols, coords = build_meo_cn()
            else:
                symbols, coords = build_meo_dcv()
            provenance = (f"built analytically from standard bond lengths "
                          f"(no force field available); twist {TWIST_DEG:g} deg")
        else:
            symbols, coords, remap, link, src = build_meo_tcf()
            provenance = (f"NMe2 -> OMe substitution on the DCDHF-Me2 "
                          f"B3LYP/def2-SVP minimum; kept planar")
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
        path = os.path.join(GEOM, "meo-tcf-derived-indices.json")
        with open(path, "w") as fh:
            json.dump(derived, fh, indent=2)
        print(f"wrote {os.path.relpath(path, HERE)} (index tables for run_tddft.py "
              f"to be checked against)")


if __name__ == "__main__":
    main()
