#!/usr/bin/env python3
"""Enforce the preregistered method-fidelity gates from the committed artifacts.

The registered gates (PREREGISTRATION.md) are: every optimization and CCSD(T)
run converges; every optimized structure keeps the intended isomer's
heavy-atom connectivity; and the largest C4H8 T1 diagnostic stays at or below
0.02. `analyze.py` enforces only the T1 gate, because the other two live in
the raw Psi4 outputs and optimized geometries rather than in the run records.
This script checks all three against the committed files, so the post's
fidelity paragraph is verifiable by code rather than by hand. It reads only;
it changes no registered number.

Exit status 0 means every gate passes; any failure is listed and exits 1.
"""

import json
import math
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
BASES = ("cc-pVDZ", "cc-pVTZ")
C4H8 = ("1-butene", "cis-2-butene", "trans-2-butene", "isobutene")
T1_CEILING = 0.02
HEAVY_BOND_MAX_ANGSTROM = 1.75

# Heavy-atom degree sequences of the intended isomers' carbon skeletons.
EXPECTED_DEGREES = {
    "ethene": [1, 1],
    "propene": [1, 1, 2],
    "1-butene": [1, 1, 2, 2],
    "cis-2-butene": [1, 1, 2, 2],
    "trans-2-butene": [1, 1, 2, 2],
    "isobutene": [1, 1, 1, 3],
}


def read_xyz_atoms(path: Path) -> list:
    atoms = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0].isalpha():
            atoms.append((parts[0], tuple(float(x) for x in parts[1:])))
    return atoms


def heavy_degree_sequence(atoms: list) -> list:
    heavy = [c for symbol, c in atoms if symbol.upper() != "H"]
    degree = [0] * len(heavy)
    for i, j in combinations(range(len(heavy)), 2):
        if math.dist(heavy[i], heavy[j]) < HEAVY_BOND_MAX_ANGSTROM:
            degree[i] += 1
            degree[j] += 1
    return sorted(degree)


def check_run(name: str, basis: str) -> list:
    failures = []
    run_dir = RUNS / name / basis
    output = run_dir / "psi4.out"
    geometry = run_dir / "optimized.xyz"
    record_path = run_dir / "result.json"

    for required in (output, geometry, record_path):
        if not required.is_file():
            return [f"{name}/{basis}: missing {required.name}"]

    text = output.read_text(encoding="utf-8")
    if "Final optimized geometry and variables:" not in text:
        failures.append(f"{name}/{basis}: no converged optimization in psi4.out")
    if "* CCSD(T) total energy" not in text:
        failures.append(f"{name}/{basis}: no completed CCSD(T) energy in psi4.out")

    degrees = heavy_degree_sequence(read_xyz_atoms(geometry))
    if degrees != EXPECTED_DEGREES[name]:
        failures.append(
            f"{name}/{basis}: heavy-atom degree sequence {degrees} "
            f"differs from the intended isomer's {EXPECTED_DEGREES[name]}"
        )

    record = json.loads(record_path.read_text(encoding="utf-8"))
    if name in C4H8 and record["t1_diagnostic"] > T1_CEILING:
        failures.append(
            f"{name}/{basis}: T1 diagnostic {record['t1_diagnostic']:.4f} "
            f"exceeds the registered ceiling {T1_CEILING}"
        )
    return failures


def main() -> int:
    failures = []
    checked = 0
    for name in EXPECTED_DEGREES:
        for basis in BASES:
            failures.extend(check_run(name, basis))
            checked += 1
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(
        f"cepb-increment-spread: {checked} run(s) pass the registered "
        "convergence, connectivity, and T1 gates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
