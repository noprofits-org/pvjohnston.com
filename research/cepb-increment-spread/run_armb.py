#!/usr/bin/env python3
"""Arm B of the CEPB increment-spread experiment.

Optimizes each registered hydrocarbon at frozen-core DF-MP2 and computes a
frozen-core DF-CCSD(T) correlation energy at that geometry, per the frozen
protocol in PREREGISTRATION.md. Restartable: a molecule/basis pair whose JSON
result already exists is skipped unless --force is given.

The four C4H8 isomers carry identical CEPB bond counts, so the source's model
assigns them identical correlation energies; the pairwise differences computed
here are the quantity that prediction sets to zero.
"""

import argparse
import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"

# Starting structures. Geometry is optimized before any energy is taken, so
# these need only be the right isomer with the right connectivity.
MOLECULES = {
    "ethene": """
C   0.0000   0.0000   0.6695
C   0.0000   0.0000  -0.6695
H   0.0000   0.9289   1.2321
H   0.0000  -0.9289   1.2321
H   0.0000   0.9289  -1.2321
H   0.0000  -0.9289  -1.2321
""",
    "propene": """
C   1.2910   0.2260   0.0000
C   0.1280  -0.4180   0.0000
C  -1.2200   0.2380   0.0000
H   1.3800   1.3070   0.0000
H   2.2200  -0.3320   0.0000
H   0.1150  -1.5050   0.0000
H  -1.7900  -0.0330   0.8900
H  -1.7900  -0.0330  -0.8900
H  -1.1400   1.3260   0.0000
""",
    "1-butene": """
C   1.9560   0.4290   0.0000
C   0.7900  -0.2010   0.0000
C  -0.5340   0.5100   0.0000
C  -1.7500  -0.4090   0.0000
H   2.0400   1.5100   0.0000
H   2.8900  -0.1200   0.0000
H   0.7600  -1.2870   0.0000
H  -0.5900   1.1600   0.8800
H  -0.5900   1.1600  -0.8800
H  -1.7500  -1.0500   0.8850
H  -1.7500  -1.0500  -0.8850
H  -2.6800   0.1650   0.0000
""",
    "cis-2-butene": """
C   0.6620   0.4180   0.0000
C  -0.6620   0.4180   0.0000
C   1.5150  -0.8100   0.0000
C  -1.5150  -0.8100   0.0000
H   1.2050   1.3610   0.0000
H  -1.2050   1.3610   0.0000
H   2.1700  -0.8300   0.8800
H   2.1700  -0.8300  -0.8800
H   0.9000  -1.7150   0.0000
H  -2.1700  -0.8300   0.8800
H  -2.1700  -0.8300  -0.8800
H  -0.9000  -1.7150   0.0000
""",
    "trans-2-butene": """
C   0.6640  -0.1900   0.0000
C  -0.6640   0.1900   0.0000
C   1.8730   0.3560   0.0000
C  -1.8730  -0.3560   0.0000
H   0.5870  -1.2760   0.0000
H  -0.5870   1.2760   0.0000
H   2.7660  -0.2720   0.0000
H   2.0100   1.4360   0.0000
H   1.8700   0.2400  -0.8900
H  -2.7660   0.2720   0.0000
H  -2.0100  -1.4360   0.0000
H  -1.8700  -0.2400   0.8900
""",
    "isobutene": """
C   0.0000   0.7350   0.0000
C   0.0000  -0.5980   0.0000
C   1.2830   1.5310   0.0000
C  -1.2830   1.5310   0.0000
H   0.9290  -1.1610   0.0000
H  -0.9290  -1.1610   0.0000
H   1.8700   1.3100   0.8900
H   1.8700   1.3100  -0.8900
H   1.0700   2.6030   0.0000
H  -1.8700   1.3100   0.8900
H  -1.8700   1.3100  -0.8900
H  -1.0700   2.6030   0.0000
""",
}

# Bond counts from the dominant Lewis structure: (C-H, C-C single, C=C double).
BOND_COUNTS = {
    "ethene": (4, 0, 1),
    "propene": (6, 1, 1),
    "1-butene": (8, 2, 1),
    "cis-2-butene": (8, 2, 1),
    "trans-2-butene": (8, 2, 1),
    "isobutene": (8, 2, 1),
}

C4H8 = ("1-butene", "cis-2-butene", "trans-2-butene", "isobutene")


def run_one(name: str, basis: str, memory: str, threads: int, force: bool) -> dict:
    out_dir = RUNS / name / basis
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "result.json"
    if result_path.is_file() and not force:
        print(f"skip {name}/{basis} (already done)")
        return json.loads(result_path.read_text())

    import psi4

    psi4.core.clean()
    psi4.set_memory(memory)
    psi4.set_num_threads(threads)
    psi4.core.set_output_file(str(out_dir / "psi4.out"), False)

    molecule = psi4.geometry(MOLECULES[name] + "\nunits angstrom\n")
    psi4.set_options(
        {
            "freeze_core": "true",
            "scf_type": "df",
            "mp2_type": "df",
            "cc_type": "df",
            "basis": basis,
            "e_convergence": 1e-9,
            "d_convergence": 1e-9,
        }
    )

    started = time.time()
    psi4.optimize("mp2")
    optimized_xyz = molecule.save_string_xyz()
    (out_dir / "optimized.xyz").write_text(optimized_xyz + "\n")
    optimization_seconds = time.time() - started

    started = time.time()
    total = psi4.energy("ccsd(t)")
    energy_seconds = time.time() - started

    record = {
        "molecule": name,
        "basis": basis,
        "bond_counts": {
            "c_h": BOND_COUNTS[name][0],
            "c_c_single": BOND_COUNTS[name][1],
            "c_c_double": BOND_COUNTS[name][2],
        },
        "frozen_core": True,
        "scf_total_energy_hartree": float(psi4.variable("SCF TOTAL ENERGY")),
        "ccsd_t_total_energy_hartree": float(total),
        "ccsd_t_correlation_energy_hartree": float(
            psi4.variable("CCSD(T) CORRELATION ENERGY")
        ),
        "mp2_correlation_energy_hartree": float(
            psi4.variable("MP2 CORRELATION ENERGY")
        ),
        "t1_diagnostic": float(psi4.variable("CC T1 DIAGNOSTIC")),
        "optimized_xyz": optimized_xyz,
        "optimization_seconds": round(optimization_seconds, 1),
        "energy_seconds": round(energy_seconds, 1),
        "psi4_version": psi4.__version__,
    }
    result_path.write_text(json.dumps(record, indent=2) + "\n")
    print(
        f"done {name}/{basis}: E_corr = "
        f"{record['ccsd_t_correlation_energy_hartree']:.8f} Ha, "
        f"T1 = {record['t1_diagnostic']:.4f}, "
        f"{(optimization_seconds + energy_seconds) / 60:.1f} min"
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basis", default="cc-pVTZ")
    parser.add_argument("--molecule", action="append", choices=sorted(MOLECULES))
    parser.add_argument("--memory", default="9 GB")
    parser.add_argument("--threads", type=int, default=7)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    # C4H8 isomers first: they carry the Arm B verdict.
    order = [m for m in C4H8] + [m for m in MOLECULES if m not in C4H8]
    names = args.molecule or order
    for name in names:
        run_one(name, args.basis, args.memory, args.threads, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
