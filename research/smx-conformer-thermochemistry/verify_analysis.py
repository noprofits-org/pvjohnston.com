#!/usr/bin/env python3
"""Fast deterministic checks for the SMX thermochemistry analysis."""

from __future__ import annotations

import hashlib
import importlib.util
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "smx_run_experiment", HERE / "run_experiment.py"
)
experiment = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(experiment)


def close(actual: float, expected: float, tolerance: float = 1.0e-12) -> None:
    # rel_tol admits the 12-significant-digit serialization rounding of
    # results.json; abs_tol admits its clamp-to-zero below 1e-12.
    assert math.isclose(actual, expected, abs_tol=tolerance, rel_tol=1.0e-11)


def independently_verify_result(inputs: dict, result: dict) -> None:
    temperature = inputs["conditions"]["temperature_k"]
    boltzmann = inputs["constants"]["boltzmann_hartree_per_k"]
    source_energies = {
        name: spec["source_electronic_energy_hartree"]
        for name, spec in inputs["conformers"].items()
    }
    source_populations = result["source_preflight"]["electronic_populations"]

    for arm in experiment.ARM_NAMES:
        analysis = result["analysis"][arm]
        composite = {
            name: source_energies[name]
            + result["runs"][name][arm]["thermochemical_correction_hartree"]
            for name in experiment.CONFORMER_NAMES
        }
        minimum = min(composite.values())
        weights = {
            name: math.exp(
                -(energy - minimum) / (boltzmann * temperature)
            )
            for name, energy in composite.items()
        }
        normalization = sum(weights.values())
        populations = {
            name: weight / normalization for name, weight in weights.items()
        }
        shifts = {
            name: 100.0 * (populations[name] - source_populations[name])
            for name in experiment.CONFORMER_NAMES
        }
        maximum_shift = max(abs(value) for value in shifts.values())
        effective_count = 1.0 / sum(value * value for value in populations.values())

        for name in experiment.CONFORMER_NAMES:
            close(analysis["composite_free_energies_hartree"][name], composite[name])
            close(analysis["composite_populations"][name], populations[name])
            close(analysis["population_shifts_pp"][name], shifts[name])
        close(analysis["maximum_absolute_population_shift_pp"], maximum_shift)
        close(analysis["effective_conformer_count"], effective_count)

        shift_passed = maximum_shift < inputs["decision"]["maximum_population_shift_pp"]
        count_passed = (
            effective_count >= inputs["decision"]["minimum_effective_conformer_count"]
        )
        assert analysis["population_shift_gate_passed"] is shift_passed
        assert analysis["effective_count_gate_passed"] is count_passed
        assert analysis["arm_passed"] is (shift_passed and count_passed)

    for artifact in result["provenance"]["run_artifacts"]:
        digest = hashlib.sha256(
            (experiment.ROOT / artifact["path"]).read_bytes()
        ).hexdigest()
        assert digest == artifact["sha256"]

    passed_arms = sum(
        result["analysis"][arm]["arm_passed"] for arm in experiment.ARM_NAMES
    )
    expected_verdict = (
        "inconclusive"
        if not result["fidelity"]["passed"]
        else "supported"
        if passed_arms == len(experiment.ARM_NAMES)
        else "falsified"
        if passed_arms == 0
        else "inconclusive"
    )
    assert result["verdict"]["value"] == expected_verdict


def main() -> None:
    inputs = experiment.load_inputs()
    preflight = experiment.source_preflight(inputs)
    assert math.isclose(
        sum(preflight["electronic_populations"].values()),
        1.0,
        abs_tol=1.0e-14,
    )
    assert preflight["maximum_rounded_population_difference_pp"] < 0.05
    assert all(
        row["printed_sign_opposes_stated_formula"]
        for row in preflight["relaxation_energy_sign_audit"]
    )

    elements = ["C", "N", "O", "H"]
    reference = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.2, 0.0],
            [-0.3, 1.2, 0.4],
            [0.2, -0.1, 1.5],
        ]
    )
    rotation = np.asarray(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    transformed = reference @ rotation + np.asarray([4.0, -2.0, 7.5])
    assert experiment.kabsch_rmsd(elements, reference, transformed) < 1.0e-12

    if experiment.RESULTS_PATH.is_file():
        existing = experiment.RESULTS_PATH.read_text(encoding="utf-8")
        result = experiment.json.loads(existing)
        independently_verify_result(inputs, result)
        expected = experiment.serialized(
            experiment.build_results(inputs, result["generated_at"])
        )
        assert expected == existing

    print("SMX thermochemistry analysis checks passed")


if __name__ == "__main__":
    main()
