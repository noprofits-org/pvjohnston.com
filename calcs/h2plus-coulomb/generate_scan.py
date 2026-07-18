#!/usr/bin/env python3
"""Generate the H2+ Born--Oppenheimer curve used in the Coulomb-fit study."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import qcelemental as qcel


HERE = Path(__file__).resolve().parent

R_MIN_BOHR = 0.15
R_MAX_BOHR = 20.0
N_POINTS = 401
BASIS = "aug-cc-pv5z"
REFERENCE = "uhf"
SCF_TYPE = "df"
THREADS = 2
MEMORY = "4 GB"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basis", default=BASIS)
    parser.add_argument("--points", type=int, default=N_POINTS)
    parser.add_argument("--output-prefix", default="h2plus-scan")
    args = parser.parse_args()
    out_csv = HERE / f"{args.output_prefix}.csv"
    out_meta = HERE / f"{args.output_prefix}-metadata.json"

    # Psi4 reads PSI_SCRATCH during import. A private temporary directory avoids
    # collisions with other calculations and is removed automatically.
    with tempfile.TemporaryDirectory(prefix="psi4-h2plus-") as scratch:
        os.environ["PSI_SCRATCH"] = scratch
        import psi4

        psi4.core.be_quiet()
        psi4.set_num_threads(THREADS)
        psi4.set_memory(MEMORY)
        psi4.set_options(
            {
                "reference": REFERENCE,
                "basis": args.basis,
                "scf_type": SCF_TYPE,
                "e_convergence": 12,
                "d_convergence": 10,
                "s_tolerance": 1.0e-8,
                "maxiter": 200,
                "guess": "core",
            }
        )

        distances = np.geomspace(R_MIN_BOHR, R_MAX_BOHR, args.points)
        rows: list[dict[str, float]] = []
        started = time.perf_counter()

        for index, distance in enumerate(distances, start=1):
            molecule = psi4.geometry(
                f"""
                1 2
                H 0.0 0.0 {-0.5 * distance:.16f}
                H 0.0 0.0 {0.5 * distance:.16f}
                units bohr
                symmetry d2h
                no_reorient
                no_com
                """
            )

            point_started = time.perf_counter()
            total_energy, wavefunction = psi4.energy(
                "scf", molecule=molecule, return_wfn=True
            )
            total_energy = float(total_energy)
            elapsed = time.perf_counter() - point_started
            nuclear_repulsion = float(molecule.nuclear_repulsion_energy())
            expected_repulsion = 1.0 / float(distance)
            electronic_energy = total_energy - nuclear_repulsion
            one_electron_energy = float(psi4.core.variable("ONE-ELECTRON ENERGY"))
            two_electron_energy = float(psi4.core.variable("TWO-ELECTRON ENERGY"))
            scf_iterations = int(round(float(psi4.core.variable("SCF ITERATIONS"))))
            overlap = np.asarray(
                psi4.core.MintsHelper(wavefunction.basisset()).ao_overlap()
            )
            minimum_overlap_eigenvalue = float(np.linalg.eigvalsh(overlap)[0])

            if not np.isclose(
                nuclear_repulsion, expected_repulsion, rtol=0.0, atol=2.0e-12
            ):
                raise RuntimeError(
                    "Psi4 nuclear repulsion does not equal 1/R at "
                    f"R={distance:.16g}: {nuclear_repulsion:.16g} vs "
                    f"{expected_repulsion:.16g}"
                )
            if wavefunction.nalpha() != 1 or wavefunction.nbeta() != 0:
                raise RuntimeError(
                    f"wrong electron count at R={distance:.16g}: "
                    f"nalpha={wavefunction.nalpha()}, nbeta={wavefunction.nbeta()}"
                )
            if abs(two_electron_energy) > 1.0e-10:
                raise RuntimeError(
                    f"two-electron energy is not zero at R={distance:.16g}: "
                    f"{two_electron_energy:.16g} Eh"
                )
            if not np.isclose(
                electronic_energy, one_electron_energy, rtol=0.0, atol=2.0e-12
            ):
                raise RuntimeError(
                    f"one-electron decomposition does not close at R={distance:.16g}"
                )

            rows.append(
                {
                    "r_bohr": float(distance),
                    "r_angstrom": float(distance) * qcel.constants.bohr2angstroms,
                    "total_hartree": total_energy,
                    "nuclear_repulsion_hartree": nuclear_repulsion,
                    "electronic_hartree": electronic_energy,
                    "one_electron_hartree": one_electron_energy,
                    "two_electron_hartree": two_electron_energy,
                    "scf_iterations": scf_iterations,
                    "n_ao": wavefunction.basisset().nbf(),
                    "n_mo": wavefunction.nmo(),
                    "minimum_overlap_eigenvalue": minimum_overlap_eigenvalue,
                    "point_group": wavefunction.molecule().point_group().symbol(),
                    "scf_seconds": elapsed,
                }
            )
            psi4.core.clean()

            if index == 1 or index % 10 == 0 or index == args.points:
                print(
                    f"{index:3d}/{args.points}: R={distance:8.5f} a0  "
                    f"V={total_energy: .12f} Eh  {elapsed:5.2f} s",
                    flush=True,
                )

        total_seconds = time.perf_counter() - started
        with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        metadata = {
            "system": "H2+ ground electronic state",
            "charge": 1,
            "multiplicity": 2,
            "method": "SCF (one electron; exact within the finite basis)",
            "reference": REFERENCE,
            "basis": args.basis,
            "scf_type": SCF_TYPE,
            "distance_grid": "geometric",
            "r_min_bohr": R_MIN_BOHR,
            "r_max_bohr": R_MAX_BOHR,
            "n_points": args.points,
            "threads": THREADS,
            "memory": MEMORY,
            "psi4_version": psi4.__version__,
            "numpy_version": np.__version__,
            "qcelemental_version": qcel.__version__,
            "bohr_to_angstrom": qcel.constants.bohr2angstroms,
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "total_seconds": total_seconds,
            "mean_point_seconds": float(np.mean([row["scf_seconds"] for row in rows])),
            "command": " ".join(sys.argv),
        }
        out_meta.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out_csv}")
        print(f"wrote {out_meta}")
        print(f"total: {total_seconds:.1f} s")


if __name__ == "__main__":
    main()
