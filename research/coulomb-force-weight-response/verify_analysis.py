#!/usr/bin/env python3
"""Stdlib-only independent verifier for the force-weight response analysis."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
ROOT = EXPERIMENT_DIR.parents[1]
RESULTS_PATH = EXPERIMENT_DIR / "results.json"
LEGACY_DIR = ROOT / "research" / "coulomb-force-training"
LEGACY_RESULTS = LEGACY_DIR / "results.json"
FORCE_WEIGHTS = [0.0, 0.01, 0.1, 1.0, 10.0, 100.0]
PRIMARY_CUTOFFS = [0.15, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5]
LEGACY_CUTOFFS = [0.15, 0.25, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0]
SEEDS = [11, 29, 47, 71, 101]
AUDIT_WEIGHTS = [0.0, 1.0, 100.0]
PINNED_PYTHON = "3.12.3"
PINNED_NUMPY = "2.4.4"

if not __debug__:
    raise RuntimeError("PYTHONOPTIMIZE is unsupported; protocol checks require __debug__")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cutoff_key(value):
    return f"{value:.2f}"


def median(values):
    return float(statistics.median(values))


def derive(record):
    energy = record["energy_rmse_cm"]
    force = record["force_rmse_hartree_per_bohr"]
    per_cutoff = {}
    classifications = []
    for cutoff in PRIMARY_CUTOFFS:
        key = cutoff_key(cutoff)
        energy_a = [energy["A"][str(seed)][key] for seed in SEEDS]
        energy_b = [energy["B"][str(seed)][key] for seed in SEEDS]
        force_a = [force["A"][str(seed)][key] for seed in SEEDS]
        force_b = [force["B"][str(seed)][key] for seed in SEEDS]
        energy_ratios = [a / b for a, b in zip(energy_a, energy_b)]
        force_ratios = [a / b for a, b in zip(force_a, force_b)]
        median_ratio = median(energy_ratios)
        classifications.append(median_ratio <= 1.0)
        per_cutoff[key] = {
            "median_energy_ab_ratio": median_ratio,
            "energy_ab_ratios": energy_ratios,
            "median_energy_rmse_a_cm": median(energy_a),
            "median_energy_rmse_b_cm": median(energy_b),
            "median_force_ab_ratio": median(force_ratios),
            "force_ab_ratios": force_ratios,
            "median_force_rmse_a_hartree_per_bohr": median(force_a),
            "median_force_rmse_b_hartree_per_bohr": median(force_b),
        }

    crossings = []
    for index in range(1, len(PRIMARY_CUTOFFS)):
        previous, current = classifications[index - 1], classifications[index]
        if previous != current:
            crossings.append({
                "lower_bohr": PRIMARY_CUTOFFS[index - 1],
                "upper_bohr": PRIMARY_CUTOFFS[index],
                "direction": "b_to_a" if (not previous and current) else "a_to_b",
            })
    first_index = next((index for index, reached in enumerate(classifications) if reached), None)
    crossover = None if first_index is None else PRIMARY_CUTOFFS[first_index]
    bracket = None
    interpolated = None
    if first_index == 0:
        bracket = {"lower_bohr": None, "upper_bohr": PRIMARY_CUTOFFS[0]}
    elif first_index is not None:
        lower = PRIMARY_CUTOFFS[first_index - 1]
        upper = PRIMARY_CUTOFFS[first_index]
        bracket = {"lower_bohr": lower, "upper_bohr": upper}
        lower_log = math.log(per_cutoff[cutoff_key(lower)]["median_energy_ab_ratio"])
        upper_log = math.log(per_cutoff[cutoff_key(upper)]["median_energy_ab_ratio"])
        if lower_log > 0 and upper_log <= 0 and lower_log != upper_log:
            interpolated = lower + (0 - lower_log) * (upper - lower) / (upper_log - lower_log)
    return {
        "per_cutoff": per_cutoff,
        "first_parity_cutoff_bohr": crossover,
        "first_parity_bracket_bohr": bracket,
        "interpolated_first_parity_bohr": interpolated,
        "crossings": crossings,
        "has_reverse_crossing": any(row["direction"] == "a_to_b" for row in crossings),
    }


def check_protocol(data):
    protocol = data["protocol"]
    assert protocol["force_weights"] == FORCE_WEIGHTS
    assert protocol["primary_cutoffs_bohr"] == PRIMARY_CUTOFFS
    assert protocol["legacy_control_cutoffs_bohr"] == LEGACY_CUTOFFS
    assert protocol["init_seeds"] == SEEDS
    assert protocol["python_version"] == PINNED_PYTHON
    assert protocol["numpy_version"] == PINNED_NUMPY
    for name in ("legacy_run", "legacy_model", "legacy_results"):
        path = ROOT / protocol[f"{name}_path"]
        assert path.is_file()
        assert sha256(path) == protocol[f"{name}_sha256"]


def check_records(data):
    records = data["records"]
    primary_complete = data["runtime"]["primary_complete"]
    observed_weights = [record["lambda_force"] for record in records]
    if primary_complete:
        assert observed_weights == FORCE_WEIGHTS
    else:
        assert observed_weights == FORCE_WEIGHTS[:len(observed_weights)]
        assert data["runtime"]["primary_stopped_at_ceiling"]
    for record in records:
        cutoffs = set(PRIMARY_CUTOFFS)
        if record["lambda_force"] in (0.0, 1.0):
            cutoffs.update((0.25, 0.4, 0.7))
        assert set(record["cutoffs_bohr"]) == cutoffs
        expected_keys = {cutoff_key(value) for value in cutoffs}
        for family in ("energy_rmse_cm", "force_rmse_hartree_per_bohr"):
            assert set(record[family]) == {"A", "B"}
            for scheme in ("A", "B"):
                assert set(record[family][scheme]) == {str(seed) for seed in SEEDS}
                for seed in SEEDS:
                    values = record[family][scheme][str(seed)]
                    assert set(values) == expected_keys
                    assert all(math.isfinite(value) and value > 0 for value in values.values())
        assert set(record["standardization"]) == expected_keys
        for key, scales in record["standardization"].items():
            sigma = scales["sigma_r_bohr_by_fold"]
            weighted = scales["lambda_sigma_r2_by_fold"]
            assert set(sigma) == {"0", "1", "2", "3", "4"}
            assert set(weighted) == set(sigma)
            for fold, value in sigma.items():
                assert weighted[fold] == record["lambda_force"] * value * value
        assert derive(record) == record["derived"]
    assert data["controls"]["completeness"]["passed"] == primary_complete


def recompute_overlap(data):
    legacy = json.loads(LEGACY_RESULTS.read_text())
    by_lambda = {record["lambda_force"]: record for record in data["records"]}
    comparisons = []
    maximum = 0.0
    passed = True
    for lam, loss in ((0.0, "energy"), (1.0, "energy_force")):
        for scheme in ("A", "B"):
            for seed in SEEDS:
                for cutoff in LEGACY_CUTOFFS:
                    key = cutoff_key(cutoff)
                    new = by_lambda[lam]["energy_rmse_cm"][scheme][str(seed)][key]
                    old = legacy["rmse_cm"][loss][scheme][str(seed)][key]
                    difference = abs(new - old)
                    exact = new == old
                    maximum = max(maximum, difference)
                    passed = passed and exact
                    comparisons.append({
                        "lambda_force": lam,
                        "scheme": scheme,
                        "seed": seed,
                        "cutoff_bohr": cutoff,
                        "exact": exact,
                        "absolute_difference_cm": difference,
                    })
    expected = {
        "passed": passed,
        "comparison_count": len(comparisons),
        "maximum_absolute_difference_cm": maximum,
        "comparisons": comparisons,
    }
    assert expected == data["controls"]["legacy_overlap"]


def expected_audit_cutoffs(derived):
    bracket = derived["first_parity_bracket_bohr"]
    if bracket and bracket["lower_bohr"] is not None:
        return [bracket["lower_bohr"], bracket["upper_bohr"]]
    if bracket:
        return PRIMARY_CUTOFFS[:2]
    return PRIMARY_CUTOFFS[-2:]


def check_audit_record(record, expected_cutoffs):
    assert record["steps"] == 40_000
    assert record["cutoffs_bohr"] == expected_cutoffs
    expected_keys = {cutoff_key(value) for value in expected_cutoffs}
    assert set(record["standardization"]) == expected_keys
    for family in ("energy_rmse_cm", "force_rmse_hartree_per_bohr"):
        assert set(record[family]) == {"A", "B"}
        for scheme in ("A", "B"):
            assert set(record[family][scheme]) == {str(seed) for seed in SEEDS}
            for seed in SEEDS:
                values = record[family][scheme][str(seed)]
                assert set(values) == expected_keys
                assert all(math.isfinite(value) and value > 0 for value in values.values())


def recompute_audit(data):
    records = {record["lambda_force"]: record for record in data["records"]}
    audit = data["controls"]["optimization_sensitivity"]
    observed_audit_weights = [record["lambda_force"] for record in audit["records"]]
    if audit["complete"]:
        assert observed_audit_weights == AUDIT_WEIGHTS
        assert not audit["stopped_at_ceiling"]
    else:
        assert observed_audit_weights == AUDIT_WEIGHTS[:len(observed_audit_weights)]
        assert audit["stopped_at_ceiling"] or not data["runtime"]["primary_complete"]
    audit_records = {record["lambda_force"]: record for record in audit["records"]}
    endpoints = []
    passed = True
    for lam in observed_audit_weights:
        expected_cutoffs = expected_audit_cutoffs(records[lam]["derived"])
        check_audit_record(audit_records[lam], expected_cutoffs)
        for cutoff in expected_cutoffs:
            key = cutoff_key(cutoff)
            primary_ratios = []
            audit_ratios = []
            for seed in SEEDS:
                skey = str(seed)
                primary_ratios.append(
                    records[lam]["energy_rmse_cm"]["A"][skey][key]
                    / records[lam]["energy_rmse_cm"]["B"][skey][key]
                )
                audit_ratios.append(
                    audit_records[lam]["energy_rmse_cm"]["A"][skey][key]
                    / audit_records[lam]["energy_rmse_cm"]["B"][skey][key]
                )
            primary_ratio = median(primary_ratios)
            audit_ratio = median(audit_ratios)
            same = (primary_ratio <= 1) == (audit_ratio <= 1)
            passed = passed and same
            endpoints.append({
                "lambda_force": lam,
                "cutoff_bohr": cutoff,
                "primary_median_energy_ab_ratio": primary_ratio,
                "audit_median_energy_ab_ratio": audit_ratio,
                "same_side_of_parity": same,
            })
    assert endpoints == audit["endpoints"]
    assert (passed and audit["complete"]) == audit["passed"]


def recompute_hypothesis_and_verdict(data):
    if not data["runtime"]["primary_complete"]:
        assert data["hypothesis"] == {
            "crossover_sequence_nonincreasing": None,
            "high_weight_strictly_inward_of_lambda_1": None,
            "no_positive_weight_reverse_crossing": None,
            "hypothesis_supported_if_gates_pass": False,
        }
        assert data["verdict"] == "inconclusive"
        return
    records = {record["lambda_force"]: record for record in data["records"]}

    def value(lam):
        result = records[lam]["derived"]["first_parity_cutoff_bohr"]
        return math.inf if result is None else result

    sequence = [value(lam) for lam in FORCE_WEIGHTS]
    nonincreasing = all(right <= left for left, right in zip(sequence, sequence[1:]))
    further = value(10.0) < value(1.0) or value(100.0) < value(1.0)
    no_reverse = all(
        not records[lam]["derived"]["has_reverse_crossing"] for lam in FORCE_WEIGHTS[1:]
    )
    supported = nonincreasing and further and no_reverse
    expected_hypothesis = {
        "crossover_sequence_nonincreasing": nonincreasing,
        "high_weight_strictly_inward_of_lambda_1": further,
        "no_positive_weight_reverse_crossing": no_reverse,
        "hypothesis_supported_if_gates_pass": supported,
    }
    assert expected_hypothesis == data["hypothesis"]
    gates = (
        data["controls"]["legacy_overlap"]["passed"]
        and data["controls"]["completeness"]["passed"]
        and data["controls"]["optimization_sensitivity"]["passed"]
        and data["runtime"]["within_ceiling"]
    )
    verdict = "supported" if gates and supported else "falsified" if gates else "inconclusive"
    assert verdict == data["verdict"]


def main(argv):
    if argv not in ([], ["--check"]):
        print("usage: python verify_analysis.py [--check]", file=sys.stderr)
        return 2
    if not RESULTS_PATH.is_file():
        print("results.json missing; run run_experiment.py", file=sys.stderr)
        return 1
    data = json.loads(RESULTS_PATH.read_text())
    assert data["schema_version"] == 1
    check_protocol(data)
    check_records(data)
    assert data["runtime"]["within_ceiling"] == (
        data["runtime"]["total_wall_seconds"] <= data["runtime"]["ceiling_seconds"]
    )
    if data["runtime"]["primary_complete"]:
        recompute_overlap(data)
    else:
        assert not data["controls"]["legacy_overlap"]["passed"]
    recompute_audit(data)
    recompute_hypothesis_and_verdict(data)
    print("verify_analysis: canonical results and derived analysis are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
