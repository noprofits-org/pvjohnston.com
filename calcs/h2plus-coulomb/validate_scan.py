#!/usr/bin/env python3
"""Independent electronic-structure checks for the production H2+ scan."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DISTANCES = (0.15, 0.25, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00)
METHODS = (
    ("aug-cc-pvtz", "uhf", "df"),
    ("aug-cc-pvqz", "uhf", "df"),
    ("aug-cc-pv5z", "uhf", "df"),
    ("aug-cc-pv5z", "uhf", "direct"),
    ("aug-cc-pv5z", "rohf", "df"),
)
HIGH_ACCURACY_ELECTRONIC_R2 = -1.1026342144949
HIGH_ACCURACY_SOURCE_DOI = "10.1063/1.2842068"


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="psi4-h2plus-validation-") as scratch:
        os.environ["PSI_SCRATCH"] = scratch
        import psi4

        psi4.core.be_quiet()
        psi4.set_num_threads(2)
        psi4.set_memory("4 GB")
        rows: list[dict[str, object]] = []

        for basis, reference, scf_type in METHODS:
            for distance in DISTANCES:
                psi4.set_options(
                    {
                        "reference": reference,
                        "basis": basis,
                        "scf_type": scf_type,
                        "e_convergence": 12,
                        "d_convergence": 10,
                        "s_tolerance": 1.0e-8,
                        "maxiter": 200,
                        "guess": "core",
                    }
                )
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
                total, wavefunction = psi4.energy(
                    "scf", molecule=molecule, return_wfn=True
                )
                repulsion = float(molecule.nuclear_repulsion_energy())
                overlap = np.asarray(
                    psi4.core.MintsHelper(wavefunction.basisset()).ao_overlap()
                )
                rows.append(
                    {
                        "r_bohr": distance,
                        "basis": basis,
                        "reference": reference,
                        "scf_type": scf_type,
                        "total_hartree": float(total),
                        "electronic_hartree": float(total) - repulsion,
                        "two_electron_hartree": float(
                            psi4.core.variable("TWO-ELECTRON ENERGY")
                        ),
                        "scf_iterations": int(
                            round(float(psi4.core.variable("SCF ITERATIONS")))
                        ),
                        "n_ao": wavefunction.basisset().nbf(),
                        "n_mo": wavefunction.nmo(),
                        "minimum_overlap_eigenvalue": float(
                            np.linalg.eigvalsh(overlap)[0]
                        ),
                    }
                )
                psi4.core.clean()
                print(
                    f"{basis:13s} {reference:4s} {scf_type:6s} "
                    f"R={distance:5.2f}  E={float(total): .12f}",
                    flush=True,
                )

        write_rows(HERE / "electronic-structure-validation.csv", rows)

        def values(basis: str, reference: str, scf_type: str) -> np.ndarray:
            selected = [
                float(row["total_hartree"])
                for row in rows
                if row["basis"] == basis
                and row["reference"] == reference
                and row["scf_type"] == scf_type
            ]
            return np.asarray(selected)

        five_df = values("aug-cc-pv5z", "uhf", "df")
        five_direct = values("aug-cc-pv5z", "uhf", "direct")
        five_rohf = values("aug-cc-pv5z", "rohf", "df")
        qz = values("aug-cc-pvqz", "uhf", "df")
        tz = values("aug-cc-pvtz", "uhf", "df")
        scan = np.genfromtxt(HERE / "h2plus-scan.csv", delimiter=",", names=True)
        minimum_index = int(np.argmin(scan["total_hartree"]))
        summary = {
            "distances_bohr": list(DISTANCES),
            "max_abs_df_minus_direct_hartree": float(
                np.max(np.abs(five_df - five_direct))
            ),
            "max_abs_uhf_minus_rohf_hartree": float(
                np.max(np.abs(five_df - five_rohf))
            ),
            "max_abs_qz_minus_5z_hartree": float(np.max(np.abs(qz - five_df))),
            "max_abs_tz_minus_5z_hartree": float(np.max(np.abs(tz - five_df))),
            "max_abs_two_electron_hartree": float(
                max(abs(float(row["two_electron_hartree"])) for row in rows)
            ),
            "scan_minimum_r_bohr": float(scan["r_bohr"][minimum_index]),
            "scan_minimum_total_hartree": float(
                scan["total_hartree"][minimum_index]
            ),
            "scan_total_at_20_bohr": float(scan["total_hartree"][-1]),
            "five_z_electronic_at_2_bohr": float(five_df[4] - 0.5),
            "high_accuracy_electronic_at_2_bohr": HIGH_ACCURACY_ELECTRONIC_R2,
            "high_accuracy_source_doi": HIGH_ACCURACY_SOURCE_DOI,
            "five_z_error_at_2_bohr_hartree": float(
                (five_df[4] - 0.5) - HIGH_ACCURACY_ELECTRONIC_R2
            ),
        }
        criteria = {
            "df_matches_direct": summary["max_abs_df_minus_direct_hartree"]
            < 1.0e-9,
            "uhf_matches_rohf": summary["max_abs_uhf_minus_rohf_hartree"]
            < 1.0e-10,
            "two_electron_energy_is_zero": summary[
                "max_abs_two_electron_hartree"
            ]
            < 1.0e-10,
            "minimum_near_two_bohr": abs(summary["scan_minimum_r_bohr"] - 2.0)
            < 0.02,
            "dissociation_near_half_hartree": abs(
                summary["scan_total_at_20_bohr"] + 0.5
            )
            < 2.0e-5,
        }
        summary["criteria"] = criteria
        if not all(criteria.values()):
            raise RuntimeError(f"validation failed: {criteria}")
        (HERE / "electronic-structure-validation.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
