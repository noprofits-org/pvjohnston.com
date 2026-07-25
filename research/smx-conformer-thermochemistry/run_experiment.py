#!/usr/bin/env python3
"""Run and analyze the preregistered SMX conformer thermochemistry experiment.

The primary composite free energy is the source paper's DFT electronic energy
plus the thermochemical correction from a separately optimized
GFN2-xTB/ALPB(water) conformer. xTB's own electronic/free-energy ordering is
reported only as a secondary method-sensitivity result.

Usage:
    conda run -n qchem python research/smx-conformer-thermochemistry/run_experiment.py --preflight
    conda run -n qchem python research/smx-conformer-thermochemistry/run_experiment.py
    conda run -n qchem python research/smx-conformer-thermochemistry/run_experiment.py --analyze
    conda run -n qchem python research/smx-conformer-thermochemistry/run_experiment.py --check

The full run is restartable: an already complete, parseable run directory is
left untouched. Use --force only to replace selected run artifacts deliberately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
INPUTS_PATH = HERE / "inputs.json"
RESULTS_PATH = HERE / "results.json"
RUNS_DIR = HERE / "runs"
CONFORMER_NAMES = ("A", "B", "C", "D")
ARM_NAMES = ("rrho", "mrrho50")
NORMAL_TERMINATION = "normal termination of xtb"


def load_inputs() -> dict:
    with INPUTS_PATH.open(encoding="utf-8") as handle:
        inputs = json.load(handle)
    if tuple(inputs["conformers"]) != CONFORMER_NAMES:
        raise ValueError(f"conformers must be ordered {CONFORMER_NAMES}")
    if tuple(inputs["thermochemistry_arms"]) != ARM_NAMES:
        raise ValueError(f"thermochemistry arms must be ordered {ARM_NAMES}")
    element_orders = {
        tuple(atom[0] for atom in spec["atoms"])
        for spec in inputs["conformers"].values()
    }
    if len(element_orders) != 1:
        raise ValueError("all conformers must share one canonical atom order")
    if len(next(iter(element_orders))) != 28:
        raise ValueError("SMX inputs must contain 28 atoms")
    return inputs


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def write_xyz(path: Path, name: str, atoms: list) -> None:
    lines = [str(len(atoms)), f"SMX conformer {name}; Blackmon and Closser (2026) supplement"]
    lines.extend(
        f"{symbol:<2} {x: .10f} {y: .10f} {z: .10f}"
        for symbol, x, y, z in atoms
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_control(path: Path, inputs: dict, arm_name: str) -> None:
    conditions = inputs["conditions"]
    rotor_cutoff = inputs["thermochemistry_arms"][arm_name]["rotor_cutoff_cm"]
    path.write_text(
        "\n".join(
            [
                "$thermo",
                f"  temp={conditions['temperature_k']}",
                f"  imagthr={conditions['imaginary_threshold_cm']}",
                f"  scale={conditions['frequency_scale']}",
                f"  sthr={rotor_cutoff}",
                "$end",
                "",
            ]
        ),
        encoding="utf-8",
    )


def parse_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    atom_count = int(lines[0].strip())
    symbols = []
    coordinates = []
    for line in lines[2 : 2 + atom_count]:
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f"invalid XYZ line in {path}: {line!r}")
        symbols.append(fields[0])
        coordinates.append([float(value) for value in fields[1:]])
    if len(symbols) != atom_count:
        raise ValueError(f"{path} declares {atom_count} atoms but contains {len(symbols)}")
    return symbols, np.asarray(coordinates, dtype=float)


def last_float(pattern: str, text: str, label: str) -> float:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if not matches:
        raise ValueError(f"could not parse {label}")
    return float(matches[-1])


def parse_frequencies(text: str) -> list[float]:
    marker = "|               Frequency Printout"
    start = text.rfind(marker)
    if start < 0:
        raise ValueError("could not locate final frequency printout")
    section = text[start:]
    end = section.find("reduced masses")
    if end < 0:
        raise ValueError("could not locate end of frequency list")
    frequencies = []
    for line in section[:end].splitlines():
        if "eigval :" in line:
            frequencies.extend(
                float(value)
                for value in re.findall(r"[-+]?(?:\d+\.\d+|\d+)", line.split("eigval :", 1)[1])
            )
    if not frequencies:
        raise ValueError("no projected frequencies parsed")
    return frequencies


def parse_xtb_run(run_dir: Path, imaginary_threshold: float) -> dict:
    output_path = run_dir / "xtb.out"
    geometry_path = run_dir / "xtbopt.xyz"
    if not output_path.is_file() or not geometry_path.is_file():
        raise FileNotFoundError(f"incomplete xTB run directory: {run_dir}")
    text = output_path.read_text(encoding="utf-8", errors="replace")
    normal = NORMAL_TERMINATION in text
    total_energy = last_float(
        r"\|\s+TOTAL ENERGY\s+(-?\d+\.\d+)\s+Eh", text, "total energy"
    )
    total_free_energy = last_float(
        r"\|\s+TOTAL FREE ENERGY\s+(-?\d+\.\d+)\s+Eh",
        text,
        "total free energy",
    )
    zero_point_energy = last_float(
        r":: zero point energy\s+(-?\d+\.\d+)\s+Eh",
        text,
        "zero-point energy",
    )
    rrho_contribution = last_float(
        r":: G\(RRHO\) contrib\.\s+(-?\d+\.\d+)\s+Eh",
        text,
        "RRHO contribution",
    )
    rotor_cutoff = last_float(
        r"rotor cutoff\s+(-?\d+\.\d+)\s+cm", text, "rotor cutoff"
    )
    frequencies = parse_frequencies(text)
    symbols, coordinates = parse_xyz(geometry_path)
    imaginary = [value for value in frequencies if value < imaginary_threshold]
    correction_from_totals = total_free_energy - total_energy
    if not math.isclose(
        correction_from_totals, rrho_contribution, abs_tol=2.0e-9, rel_tol=0.0
    ):
        raise ValueError(
            f"{run_dir}: total-free minus total-energy differs from printed "
            f"G(RRHO) contribution by {correction_from_totals - rrho_contribution:.3e} Eh"
        )
    return {
        "normal_termination": normal,
        "xtb_total_energy_hartree": total_energy,
        "xtb_total_free_energy_hartree": total_free_energy,
        "thermochemical_correction_hartree": rrho_contribution,
        "zero_point_energy_hartree": zero_point_energy,
        "rotor_cutoff_cm": rotor_cutoff,
        "frequencies_cm": frequencies,
        "n_frequencies": len(frequencies),
        "imaginary_frequencies_below_threshold_cm": imaginary,
        "n_imaginary_modes_below_threshold": len(imaginary),
        "optimized_elements": symbols,
        "optimized_coordinates_angstrom": coordinates.tolist(),
        "artifacts": {
            "output": {
                "path": repository_path(output_path),
                "sha256": sha256(output_path),
            },
            "optimized_geometry": {
                "path": repository_path(geometry_path),
                "sha256": sha256(geometry_path),
            },
        },
    }


def run_directory_complete(run_dir: Path, imaginary_threshold: float) -> bool:
    try:
        parsed = parse_xtb_run(run_dir, imaginary_threshold)
        return parsed["normal_termination"]
    except (FileNotFoundError, ValueError):
        return False


def run_one(inputs: dict, conformer_name: str, arm_name: str, force: bool) -> None:
    conditions = inputs["conditions"]
    run_dir = RUNS_DIR / conformer_name / arm_name
    if run_directory_complete(run_dir, conditions["imaginary_threshold_cm"]) and not force:
        print(f"skip complete run {conformer_name}/{arm_name}")
        return
    if run_dir.exists() and force:
        shutil.rmtree(run_dir)
    elif run_dir.exists() and any(run_dir.iterdir()):
        raise RuntimeError(
            f"{run_dir} exists but is incomplete; inspect it, then rerun with --force"
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    source_xyz = run_dir / "source.xyz"
    control = run_dir / "control.inp"
    write_xyz(
        source_xyz,
        conformer_name,
        inputs["conformers"][conformer_name]["atoms"],
    )
    write_control(control, inputs, arm_name)

    xtb_binary = os.environ.get("XTB_BIN") or shutil.which("xtb")
    if not xtb_binary:
        raise RuntimeError("xtb not found; run inside the pinned conda environment")
    command = [
        xtb_binary,
        source_xyz.name,
        "--chrg",
        str(conditions["charge"]),
        "--uhf",
        str(conditions["unpaired_electrons"]),
        "--gfn",
        "2",
        "--alpb",
        conditions["solvent"],
        "--acc",
        str(conditions["scc_accuracy"]),
        "--ohess",
        conditions["optimization_level"],
        "--parallel",
        str(conditions["parallel_processes"]),
        "--json",
        "--ceasefiles",
        "-I",
        control.name,
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
        }
    )
    print(f"run {conformer_name}/{arm_name}: {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=run_dir,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    output_path = run_dir / "xtb.out"
    output_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0 or NORMAL_TERMINATION not in completed.stdout:
        raise RuntimeError(
            f"xTB failed for {conformer_name}/{arm_name}; see {output_path}"
        )
    parse_xtb_run(run_dir, conditions["imaginary_threshold_cm"])


def boltzmann_populations(
    energies_hartree: dict[str, float], temperature_k: float, boltzmann_hartree_per_k: float
) -> dict[str, float]:
    minimum = min(energies_hartree.values())
    weights = {
        name: math.exp(
            -(energy - minimum) / (boltzmann_hartree_per_k * temperature_k)
        )
        for name, energy in energies_hartree.items()
    }
    normalization = sum(weights.values())
    return {name: weight / normalization for name, weight in weights.items()}


def kabsch_rmsd(
    elements: list[str],
    coordinates_a: list[list[float]] | np.ndarray,
    coordinates_b: list[list[float]] | np.ndarray,
) -> float:
    heavy = np.asarray([element != "H" for element in elements], dtype=bool)
    a = np.asarray(coordinates_a, dtype=float)[heavy]
    b = np.asarray(coordinates_b, dtype=float)[heavy]
    a = a - a.mean(axis=0)
    b = b - b.mean(axis=0)
    covariance = a.T @ b
    left, _, right_t = np.linalg.svd(covariance)
    sign = -1.0 if np.linalg.det(left @ right_t) < 0 else 1.0
    rotation = left @ np.diag([1.0, 1.0, sign]) @ right_t
    aligned = a @ rotation
    return float(np.sqrt(np.mean(np.sum((aligned - b) ** 2, axis=1))))


def source_preflight(inputs: dict) -> dict:
    temperature = inputs["conditions"]["temperature_k"]
    boltzmann = inputs["constants"]["boltzmann_hartree_per_k"]
    source_energies = {
        name: spec["source_electronic_energy_hartree"]
        for name, spec in inputs["conformers"].items()
    }
    populations = boltzmann_populations(source_energies, temperature, boltzmann)
    rounded_differences_pp = {
        name: 100.0 * populations[name] - spec["source_reported_population_percent"]
        for name, spec in inputs["conformers"].items()
    }
    maximum_rounding_difference = max(
        abs(value) for value in rounded_differences_pp.values()
    )
    if maximum_rounding_difference > 0.15:
        raise ValueError(
            "source electronic populations do not reproduce the rounded table "
            f"(maximum difference {maximum_rounding_difference:.3f} pp)"
        )
    h2kj = inputs["constants"]["hartree_to_kj_per_mol"]
    relaxation_audit = []
    for row in inputs["source_relaxation_energy_audit"]:
        formula_value = (row["vertical_hartree"] - row["relaxed_hartree"]) * h2kj
        relaxation_audit.append(
            {
                **row,
                "vertical_minus_relaxed_kj_per_mol": formula_value,
                "printed_sign_opposes_stated_formula": (
                    math.copysign(1.0, formula_value)
                    != math.copysign(1.0, row["main_table_signed_kj_per_mol"])
                ),
                "absolute_magnitude_difference_kj_per_mol": abs(
                    abs(formula_value) - abs(row["main_table_signed_kj_per_mol"])
                ),
            }
        )
    return {
        "electronic_energies_hartree": source_energies,
        "electronic_populations": populations,
        "reported_populations_percent": {
            name: spec["source_reported_population_percent"]
            for name, spec in inputs["conformers"].items()
        },
        "rounded_population_differences_pp": rounded_differences_pp,
        "maximum_rounded_population_difference_pp": maximum_rounding_difference,
        "effective_conformer_count": 1.0
        / sum(value * value for value in populations.values()),
        "relaxation_energy_sign_audit": relaxation_audit,
    }


def analyze_arm(inputs: dict, runs: dict, arm_name: str, baseline: dict) -> dict:
    source_energies = baseline["electronic_energies_hartree"]
    composite_energies = {
        name: source_energies[name]
        + runs[name][arm_name]["thermochemical_correction_hartree"]
        for name in CONFORMER_NAMES
    }
    native_xtb_free_energies = {
        name: runs[name][arm_name]["xtb_total_free_energy_hartree"]
        for name in CONFORMER_NAMES
    }
    temperature = inputs["conditions"]["temperature_k"]
    boltzmann = inputs["constants"]["boltzmann_hartree_per_k"]
    composite_populations = boltzmann_populations(
        composite_energies, temperature, boltzmann
    )
    native_populations = boltzmann_populations(
        native_xtb_free_energies, temperature, boltzmann
    )
    shifts_pp = {
        name: 100.0
        * (composite_populations[name] - baseline["electronic_populations"][name])
        for name in CONFORMER_NAMES
    }
    maximum_shift = max(abs(value) for value in shifts_pp.values())
    effective_count = 1.0 / sum(
        value * value for value in composite_populations.values()
    )
    decision = inputs["decision"]
    shift_gate = maximum_shift < decision["maximum_population_shift_pp"]
    count_gate = (
        effective_count >= decision["minimum_effective_conformer_count"]
    )
    minimum_composite = min(composite_energies.values())
    minimum_native = min(native_xtb_free_energies.values())
    h2kj = inputs["constants"]["hartree_to_kj_per_mol"]
    return {
        "composite_free_energies_hartree": composite_energies,
        "composite_relative_free_energies_kj_per_mol": {
            name: (energy - minimum_composite) * h2kj
            for name, energy in composite_energies.items()
        },
        "composite_populations": composite_populations,
        "population_shifts_pp": shifts_pp,
        "maximum_absolute_population_shift_pp": maximum_shift,
        "effective_conformer_count": effective_count,
        "population_shift_gate_passed": shift_gate,
        "effective_count_gate_passed": count_gate,
        "arm_passed": shift_gate and count_gate,
        "native_xtb_free_energies_hartree": native_xtb_free_energies,
        "native_xtb_relative_free_energies_kj_per_mol": {
            name: (energy - minimum_native) * h2kj
            for name, energy in native_xtb_free_energies.items()
        },
        "native_xtb_populations": native_populations,
    }


def fidelity_analysis(inputs: dict, runs: dict) -> dict:
    conditions = inputs["conditions"]
    decisions = inputs["decision"]
    elements = [
        atom[0] for atom in inputs["conformers"][CONFORMER_NAMES[0]]["atoms"]
    ]
    run_checks = {}
    for conformer in CONFORMER_NAMES:
        for arm in ARM_NAMES:
            run = runs[conformer][arm]
            run_checks[f"{conformer}/{arm}"] = {
                "normal_termination": run["normal_termination"],
                "no_modes_below_imaginary_threshold": (
                    run["n_imaginary_modes_below_threshold"] == 0
                ),
                "rotor_cutoff_matches_input": math.isclose(
                    run["rotor_cutoff_cm"],
                    inputs["thermochemistry_arms"][arm]["rotor_cutoff_cm"],
                    abs_tol=1.0e-8,
                    rel_tol=0.0,
                ),
            }
    same_conformer_rmsd = {}
    for conformer in CONFORMER_NAMES:
        same_conformer_rmsd[conformer] = kabsch_rmsd(
            elements,
            runs[conformer]["rrho"]["optimized_coordinates_angstrom"],
            runs[conformer]["mrrho50"]["optimized_coordinates_angstrom"],
        )
    same_conformer_passed = all(
        value
        <= decisions["same_conformer_max_heavy_atom_rmsd_angstrom"]
        for value in same_conformer_rmsd.values()
    )

    distinct_rmsd = {}
    distinct_passed_by_arm = {}
    for arm in ARM_NAMES:
        per_arm = {}
        for first, second in combinations(CONFORMER_NAMES, 2):
            per_arm[f"{first}-{second}"] = kabsch_rmsd(
                elements,
                runs[first][arm]["optimized_coordinates_angstrom"],
                runs[second][arm]["optimized_coordinates_angstrom"],
            )
        distinct_rmsd[arm] = per_arm
        distinct_passed_by_arm[arm] = all(
            value
            >= decisions["distinct_conformer_min_heavy_atom_rmsd_angstrom"]
            for value in per_arm.values()
        )
    all_run_checks_passed = all(
        all(checks.values()) for checks in run_checks.values()
    )
    passed = (
        all_run_checks_passed
        and same_conformer_passed
        and all(distinct_passed_by_arm.values())
    )
    return {
        "imaginary_threshold_cm": conditions["imaginary_threshold_cm"],
        "run_checks": run_checks,
        "all_run_checks_passed": all_run_checks_passed,
        "same_conformer_arm_rmsd_angstrom": same_conformer_rmsd,
        "same_conformer_arm_rmsd_passed": same_conformer_passed,
        "distinct_conformer_pair_rmsd_angstrom": distinct_rmsd,
        "distinct_conformer_passed_by_arm": distinct_passed_by_arm,
        "passed": passed,
    }


def build_results(inputs: dict, generated_at: str) -> dict:
    baseline = source_preflight(inputs)
    runs = {}
    run_artifacts = []
    for conformer in CONFORMER_NAMES:
        runs[conformer] = {}
        for arm in ARM_NAMES:
            parsed = parse_xtb_run(
                RUNS_DIR / conformer / arm,
                inputs["conditions"]["imaginary_threshold_cm"],
            )
            runs[conformer][arm] = parsed
            run_artifacts.extend(parsed["artifacts"].values())

    fidelity = fidelity_analysis(inputs, runs)
    arm_analyses = {
        arm: analyze_arm(inputs, runs, arm, baseline) for arm in ARM_NAMES
    }
    passed_arms = [arm for arm in ARM_NAMES if arm_analyses[arm]["arm_passed"]]
    if not fidelity["passed"]:
        verdict = "inconclusive"
        reason = "method-fidelity gate failed"
    elif len(passed_arms) == len(ARM_NAMES):
        verdict = "supported"
        reason = "both registered thermochemistry arms passed both robustness gates"
    elif len(passed_arms) == 0:
        verdict = "falsified"
        reason = "both registered thermochemistry arms failed at least one robustness gate"
    else:
        verdict = "inconclusive"
        reason = "registered thermochemistry arms disagreed"

    return {
        "schema_version": 1,
        "experiment": inputs["experiment"],
        "generated_at": generated_at,
        "provenance": {
            "inputs": {
                "path": repository_path(INPUTS_PATH),
                "sha256": sha256(INPUTS_PATH),
            },
            "preregistration": {
                "path": repository_path(HERE / "PREREGISTRATION.md"),
                "sha256": sha256(HERE / "PREREGISTRATION.md"),
            },
            "run_artifacts": run_artifacts,
        },
        "protocol": {
            "conditions": inputs["conditions"],
            "thermochemistry_arms": inputs["thermochemistry_arms"],
            "decision": inputs["decision"],
        },
        "source_preflight": baseline,
        "runs": runs,
        "analysis": arm_analyses,
        "fidelity": fidelity,
        "verdict": {
            "value": verdict,
            "reason": reason,
            "hypothesis_supported": verdict == "supported",
            "hypothesis_falsified": verdict == "falsified",
            "result_inconclusive": verdict == "inconclusive",
        },
    }


def serialized(result: dict) -> str:
    return json.dumps(result, indent=2, sort_keys=False, allow_nan=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--conformer", choices=CONFORMER_NAMES, action="append")
    parser.add_argument("--arm", choices=ARM_NAMES, action="append")
    args = parser.parse_args()
    if sum((args.preflight, args.analyze, args.check)) > 1:
        parser.error("--preflight, --analyze, and --check are mutually exclusive")

    inputs = load_inputs()
    if args.preflight:
        print(serialized(source_preflight(inputs)), end="")
        return 0

    if args.check:
        if not RESULTS_PATH.is_file():
            raise FileNotFoundError(f"{RESULTS_PATH} does not exist")
        existing = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        expected = serialized(build_results(inputs, existing["generated_at"]))
        actual = RESULTS_PATH.read_text(encoding="utf-8")
        if expected != actual:
            print(f"{repository_path(RESULTS_PATH)} is stale", file=sys.stderr)
            return 1
        print(f"{repository_path(RESULTS_PATH)} is internally consistent")
        return 0

    if not args.analyze:
        conformers = tuple(args.conformer or CONFORMER_NAMES)
        arms = tuple(args.arm or ARM_NAMES)
        for conformer in conformers:
            for arm in arms:
                run_one(inputs, conformer, arm, args.force)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    RESULTS_PATH.write_text(
        serialized(build_results(inputs, generated_at)), encoding="utf-8"
    )
    print(f"wrote {repository_path(RESULTS_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
