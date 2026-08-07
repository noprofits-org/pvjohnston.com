#!/usr/bin/env python3
"""Frozen H2+ force-loss-weight dose-response.

The numerical trainer is imported unchanged from the predecessor experiment.
This wrapper keeps each lambda in the predecessor's 25-network batch shape,
adds held-out force scoring, runs independent scalar-lambda workers, checks the
complete lambda=0/1 legacy subgrid, and performs the registered 40k-step audit.
"""

from __future__ import annotations

import os

# These must be set before NumPy is imported by the predecessor module.
for _thread_variable in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
ROOT = EXPERIMENT_DIR.parents[1]
LEGACY_DIR = ROOT / "research" / "coulomb-force-training"
LEGACY_RUN = LEGACY_DIR / "run_experiment.py"
LEGACY_MODEL = LEGACY_DIR / "h2plus_model.py"
LEGACY_RESULTS = LEGACY_DIR / "results.json"
RESULTS_PATH = EXPERIMENT_DIR / "results.json"

# The legacy module uses a bare import for h2plus_model.py.
sys.path.insert(0, str(LEGACY_DIR))
_spec = importlib.util.spec_from_file_location("coulomb_force_training_base", LEGACY_RUN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot import predecessor module: {LEGACY_RUN}")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
np = base.np

FORCE_WEIGHTS = [0.0, 0.01, 0.1, 1.0, 10.0, 100.0]
PRIMARY_CUTOFFS = [0.15, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5]
LEGACY_CUTOFFS = [0.15, 0.25, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0]
LEGACY_ONLY_CUTOFFS = [0.25, 0.4, 0.7]
AUDIT_WEIGHTS = [0.0, 1.0, 100.0]
PRODUCTION_STEPS = 20_000
AUDIT_STEPS = 40_000
REGISTERED_WORKERS = 2
MAX_WALL_SECONDS = 3 * 60 * 60
PINNED_PYTHON = "3.12.3"
PINNED_NUMPY = "2.4.4"

if not __debug__:
    raise RuntimeError("PYTHONOPTIMIZE is unsupported; protocol checks require __debug__")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cutoff_key(value: float) -> str:
    return f"{value:.2f}"


def _run_cutoff_detailed(scheme, lam, cutoff, folds, R, targets, slopes):
    """Legacy run_cutoff with identical energy path plus held-out force RMSE."""
    elig = R >= cutoff
    Rc, fc = R[elig], folds[elig]
    tc, sc = targets[elig], slopes[elig]
    Vtrue = base.h2.potential(Rc)
    dVtrue = base.h2.d_potential(Rc)
    M = Rc.shape[0]
    seeds = base.INIT_SEEDS
    nets = [(si, fold) for si in range(len(seeds)) for fold in range(base.N_FOLDS)]
    Nn = len(nets)
    W1 = np.empty((Nn, base.HIDDEN))
    b1 = np.zeros((Nn, base.HIDDEN))
    w2 = np.empty((Nn, base.HIDDEN))
    b2 = np.zeros(Nn)
    U = np.empty((Nn, M))
    T = np.empty((Nn, M))
    S = np.empty((Nn, M))
    Wt = np.zeros((Nn, M))
    meta = []
    sigma_r_by_fold = {}

    for n, (si, fold) in enumerate(nets):
        p0 = base.init_params(seeds[si])
        W1[n], b1[n], w2[n], b2[n] = p0["W1"], p0["b1"], p0["w2"], p0["b2"]
        train = fc != fold
        mux, sigx = Rc[train].mean(), Rc[train].std()
        mut, sigt = tc[train].mean(), tc[train].std()
        U[n] = (Rc - mux) / sigx
        T[n] = (tc - mut) / sigt
        S[n] = sc * sigx / sigt
        Wt[n, train] = 1.0 / train.sum()
        meta.append((si, fold, mut, sigt, sigx))
        previous = sigma_r_by_fold.setdefault(fold, float(sigx))
        assert previous == float(sigx)

    P0 = {"W1": W1, "b1": b1, "w2": w2, "b2": b2}
    P = base.batched_adam(P0, U, T, S, Wt, lam)
    g, gp, _, _ = base.batched_forward(P, U)
    energy_predictions = {si: np.full(M, np.nan) for si in range(len(seeds))}
    derivative_predictions = {si: np.full(M, np.nan) for si in range(len(seeds))}

    for n, (si, fold, mut, sigt, sigx) in enumerate(meta):
        test = fc == fold
        target_prediction = g[n, test] * sigt + mut
        slope_prediction = gp[n, test] * sigt / sigx
        if scheme == "A":
            total_prediction = target_prediction
            total_derivative = slope_prediction
        else:
            total_prediction = target_prediction + 1.0 / Rc[test]
            total_derivative = slope_prediction - 1.0 / (Rc[test] * Rc[test])
        energy_predictions[si][test] = total_prediction
        derivative_predictions[si][test] = total_derivative

    energy_rmse_cm = {}
    force_rmse_hartree_per_bohr = {}
    for si, seed in enumerate(seeds):
        energy_rmse_hartree = float(
            np.sqrt(np.mean((energy_predictions[si] - Vtrue) ** 2))
        )
        derivative_rmse = float(
            np.sqrt(np.mean((derivative_predictions[si] - dVtrue) ** 2))
        )
        energy_rmse_cm[seed] = energy_rmse_hartree * base.HARTREE_TO_CM
        # Force and dV/dR differ only by sign, so their RMSEs are identical.
        force_rmse_hartree_per_bohr[seed] = derivative_rmse

    return {
        "energy_rmse_cm": energy_rmse_cm,
        "force_rmse_hartree_per_bohr": force_rmse_hartree_per_bohr,
        "sigma_r_by_fold": sigma_r_by_fold,
    }


def _run_weight_task(task):
    """Run one scalar lambda; safe for a spawned process."""
    index, lam, cutoffs, steps = task
    base.STEPS = int(steps)
    R, V, E_el, dV, dE_el = base.build_grid()
    folds = base.assign_folds()
    scheme_targets = {"A": (V, dV), "B": (E_el, dE_el)}
    energy = {scheme: {str(seed): {} for seed in base.INIT_SEEDS} for scheme in ("A", "B")}
    force = {scheme: {str(seed): {} for seed in base.INIT_SEEDS} for scheme in ("A", "B")}
    scales = {}
    started = time.monotonic()

    for scheme in ("A", "B"):
        targets, slopes = scheme_targets[scheme]
        for cutoff in cutoffs:
            detail = _run_cutoff_detailed(scheme, lam, cutoff, folds, R, targets, slopes)
            key = cutoff_key(cutoff)
            for seed in base.INIT_SEEDS:
                energy[scheme][str(seed)][key] = detail["energy_rmse_cm"][seed]
                force[scheme][str(seed)][key] = detail["force_rmse_hartree_per_bohr"][seed]
            fold_scales = {str(fold): value for fold, value in detail["sigma_r_by_fold"].items()}
            if key in scales:
                assert scales[key]["sigma_r_bohr_by_fold"] == fold_scales
            else:
                scales[key] = {
                    "sigma_r_bohr_by_fold": fold_scales,
                    "lambda_sigma_r2_by_fold": {
                        fold: float(lam * value * value) for fold, value in fold_scales.items()
                    },
                }
            print(
                f"lambda={lam:g} steps={steps} scheme={scheme} cutoff={cutoff:.2f} "
                f"elapsed={time.monotonic()-started:.1f}s",
                flush=True,
            )

    return {
        "index": index,
        "lambda_force": lam,
        "steps": steps,
        "cutoffs_bohr": list(cutoffs),
        "energy_rmse_cm": energy,
        "force_rmse_hartree_per_bohr": force,
        "standardization": scales,
        "worker_runtime_seconds": time.monotonic() - started,
    }


def _pool_map(tasks, workers):
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(
        max_workers=workers,
        mp_context=context,
    ) as executor:
        unordered = list(executor.map(_run_weight_task, tasks))
    return sorted(unordered, key=lambda row: row["index"])


def _wave_map(tasks, workers, started):
    """Run at most one worker-sized wave after each ceiling check."""
    completed = []
    stopped_at_ceiling = False
    for offset in range(0, len(tasks), workers):
        if completed and time.monotonic() - started >= MAX_WALL_SECONDS:
            stopped_at_ceiling = True
            break
        completed.extend(_pool_map(tasks[offset:offset + workers], workers))
        if time.monotonic() - started >= MAX_WALL_SECONDS and offset + workers < len(tasks):
            stopped_at_ceiling = True
            break
    return sorted(completed, key=lambda row: row["index"]), stopped_at_ceiling


def _median(values):
    return float(np.median(np.asarray(values, dtype=float)))


def derive_weight(record, cutoffs=PRIMARY_CUTOFFS):
    energy = record["energy_rmse_cm"]
    force = record["force_rmse_hartree_per_bohr"]
    per_cutoff = {}
    classifications = []
    for cutoff in cutoffs:
        key = cutoff_key(cutoff)
        ratios = []
        force_ratios = []
        energy_a = []
        energy_b = []
        force_a = []
        force_b = []
        for seed in base.INIT_SEEDS:
            seed_key = str(seed)
            ea = energy["A"][seed_key][key]
            eb = energy["B"][seed_key][key]
            fa = force["A"][seed_key][key]
            fb = force["B"][seed_key][key]
            ratios.append(ea / eb)
            force_ratios.append(fa / fb)
            energy_a.append(ea)
            energy_b.append(eb)
            force_a.append(fa)
            force_b.append(fb)
        median_ratio = _median(ratios)
        classifications.append(median_ratio <= 1.0)
        per_cutoff[key] = {
            "median_energy_ab_ratio": median_ratio,
            "energy_ab_ratios": [float(value) for value in ratios],
            "median_energy_rmse_a_cm": _median(energy_a),
            "median_energy_rmse_b_cm": _median(energy_b),
            "median_force_ab_ratio": _median(force_ratios),
            "force_ab_ratios": [float(value) for value in force_ratios],
            "median_force_rmse_a_hartree_per_bohr": _median(force_a),
            "median_force_rmse_b_hartree_per_bohr": _median(force_b),
        }

    crossings = []
    for index in range(1, len(cutoffs)):
        previous, current = classifications[index - 1], classifications[index]
        if previous != current:
            crossings.append({
                "lower_bohr": cutoffs[index - 1],
                "upper_bohr": cutoffs[index],
                "direction": "b_to_a" if (not previous and current) else "a_to_b",
            })

    first_index = next((i for i, reached in enumerate(classifications) if reached), None)
    crossover = None if first_index is None else cutoffs[first_index]
    bracket = None
    interpolated = None
    if first_index == 0:
        bracket = {"lower_bohr": None, "upper_bohr": cutoffs[0]}
    elif first_index is not None:
        lower, upper = cutoffs[first_index - 1], cutoffs[first_index]
        bracket = {"lower_bohr": lower, "upper_bohr": upper}
        lower_log = math.log(per_cutoff[cutoff_key(lower)]["median_energy_ab_ratio"])
        upper_log = math.log(per_cutoff[cutoff_key(upper)]["median_energy_ab_ratio"])
        if lower_log > 0.0 and upper_log <= 0.0 and lower_log != upper_log:
            interpolated = lower + (0.0 - lower_log) * (upper - lower) / (upper_log - lower_log)

    return {
        "per_cutoff": per_cutoff,
        "first_parity_cutoff_bohr": crossover,
        "first_parity_bracket_bohr": bracket,
        "interpolated_first_parity_bohr": interpolated,
        "crossings": crossings,
        "has_reverse_crossing": any(row["direction"] == "a_to_b" for row in crossings),
    }


def legacy_overlap_gate(records):
    legacy = json.loads(LEGACY_RESULTS.read_text())
    by_lambda = {row["lambda_force"]: row for row in records}
    comparisons = []
    maximum_absolute_difference = 0.0
    exact = True
    for lam, old_loss in ((0.0, "energy"), (1.0, "energy_force")):
        record = by_lambda[lam]
        for scheme in ("A", "B"):
            for seed in base.INIT_SEEDS:
                for cutoff in LEGACY_CUTOFFS:
                    key = cutoff_key(cutoff)
                    new = record["energy_rmse_cm"][scheme][str(seed)][key]
                    old = legacy["rmse_cm"][old_loss][scheme][str(seed)][key]
                    difference = abs(new - old)
                    maximum_absolute_difference = max(maximum_absolute_difference, difference)
                    same = new == old
                    exact = exact and same
                    comparisons.append({
                        "lambda_force": lam,
                        "scheme": scheme,
                        "seed": seed,
                        "cutoff_bohr": cutoff,
                        "exact": same,
                        "absolute_difference_cm": difference,
                    })
    return {
        "passed": exact,
        "comparison_count": len(comparisons),
        "maximum_absolute_difference_cm": maximum_absolute_difference,
        "comparisons": comparisons,
    }


def audit_cutoffs(derived):
    bracket = derived["first_parity_bracket_bohr"]
    if bracket and bracket["lower_bohr"] is not None:
        return [bracket["lower_bohr"], bracket["upper_bohr"]]
    if bracket:
        return PRIMARY_CUTOFFS[:2]
    return PRIMARY_CUTOFFS[-2:]


def build_audit(primary_records, workers, started):
    by_lambda = {row["lambda_force"]: row for row in primary_records}
    tasks = []
    selected = {}
    for index, lam in enumerate(AUDIT_WEIGHTS):
        chosen = audit_cutoffs(by_lambda[lam]["derived"])
        selected[lam] = chosen
        tasks.append((index, lam, chosen, AUDIT_STEPS))
    audit_records, stopped_at_ceiling = _wave_map(tasks, workers, started)
    endpoints = []
    passed = True
    for audit in audit_records:
        lam = audit["lambda_force"]
        primary = by_lambda[lam]
        for cutoff in selected[lam]:
            key = cutoff_key(cutoff)
            p_values = []
            a_values = []
            for seed in base.INIT_SEEDS:
                seed_key = str(seed)
                p_values.append(
                    primary["energy_rmse_cm"]["A"][seed_key][key]
                    / primary["energy_rmse_cm"]["B"][seed_key][key]
                )
                a_values.append(
                    audit["energy_rmse_cm"]["A"][seed_key][key]
                    / audit["energy_rmse_cm"]["B"][seed_key][key]
                )
            primary_ratio = _median(p_values)
            audit_ratio = _median(a_values)
            same_side = (primary_ratio <= 1.0) == (audit_ratio <= 1.0)
            passed = passed and same_side
            endpoints.append({
                "lambda_force": lam,
                "cutoff_bohr": cutoff,
                "primary_median_energy_ab_ratio": primary_ratio,
                "audit_median_energy_ab_ratio": audit_ratio,
                "same_side_of_parity": same_side,
            })
    complete = len(audit_records) == len(AUDIT_WEIGHTS) and not stopped_at_ceiling
    return {
        "passed": passed and complete,
        "complete": complete,
        "stopped_at_ceiling": stopped_at_ceiling,
        "steps": AUDIT_STEPS,
        "selection_rule": "first crossing bracket, otherwise last two primary cutoffs",
        "endpoints": endpoints,
        "records": audit_records,
    }


def completeness_gate(records):
    try:
        assert [row["lambda_force"] for row in records] == FORCE_WEIGHTS
        for row in records:
            expected = set(PRIMARY_CUTOFFS)
            if row["lambda_force"] in (0.0, 1.0):
                expected.update(LEGACY_ONLY_CUTOFFS)
            assert set(row["cutoffs_bohr"]) == expected
            expected_keys = {cutoff_key(value) for value in expected}
            assert set(row["standardization"]) == expected_keys
            for scales in row["standardization"].values():
                sigma = scales["sigma_r_bohr_by_fold"]
                weighted = scales["lambda_sigma_r2_by_fold"]
                assert set(sigma) == {str(fold) for fold in range(base.N_FOLDS)}
                assert set(weighted) == set(sigma)
                assert all(math.isfinite(value) and value > 0 for value in sigma.values())
                assert all(math.isfinite(value) and value >= 0 for value in weighted.values())
            for family in ("energy_rmse_cm", "force_rmse_hartree_per_bohr"):
                for scheme in ("A", "B"):
                    assert set(row[family][scheme]) == {str(seed) for seed in base.INIT_SEEDS}
                    for seed in base.INIT_SEEDS:
                        values = row[family][scheme][str(seed)]
                        assert set(values) == expected_keys
                        assert all(math.isfinite(value) and value > 0 for value in values.values())
        return {"passed": True, "message": "all registered results are finite and complete"}
    except AssertionError as error:
        return {"passed": False, "message": f"completeness assertion failed: {error}"}


def hypothesis_evaluation(records):
    by_lambda = {row["lambda_force"]: row for row in records}

    def ordered_value(lam):
        value = by_lambda[lam]["derived"]["first_parity_cutoff_bohr"]
        return math.inf if value is None else value

    values = [ordered_value(lam) for lam in FORCE_WEIGHTS]
    nonincreasing = all(right <= left for left, right in zip(values, values[1:]))
    c1 = ordered_value(1.0)
    further_inward = ordered_value(10.0) < c1 or ordered_value(100.0) < c1
    no_positive_reverse = all(
        not by_lambda[lam]["derived"]["has_reverse_crossing"]
        for lam in FORCE_WEIGHTS[1:]
    )
    supported = nonincreasing and further_inward and no_positive_reverse
    return {
        "crossover_sequence_nonincreasing": nonincreasing,
        "high_weight_strictly_inward_of_lambda_1": further_inward,
        "no_positive_weight_reverse_crossing": no_positive_reverse,
        "hypothesis_supported_if_gates_pass": supported,
    }


def _cheap_checks():
    if platform.python_version() != PINNED_PYTHON or np.__version__ != PINNED_NUMPY:
        raise RuntimeError(
            f"pinned runtime required: Python {PINNED_PYTHON}, NumPy {PINNED_NUMPY}; "
            f"found Python {platform.python_version()}, NumPy {np.__version__}"
        )
    assert base.h2._self_test()
    assert base._finite_diff_check()
    assert base._batched_consistency_check()

    original_steps = base.STEPS
    try:
        local = _run_weight_task((0, 0.0, [3.5], 7))
        spawned = _pool_map([(0, 0.0, [3.5], 7)], 1)[0]
        assert local["energy_rmse_cm"] == spawned["energy_rmse_cm"]
        assert local["force_rmse_hartree_per_bohr"] == spawned["force_rmse_hartree_per_bohr"]
    finally:
        base.STEPS = original_steps
    return True


def run(workers):
    if workers != REGISTERED_WORKERS:
        raise ValueError(f"production protocol requires --workers {REGISTERED_WORKERS}")
    _cheap_checks()
    started = time.monotonic()
    tasks = []
    for index, lam in enumerate(FORCE_WEIGHTS):
        cutoffs = list(PRIMARY_CUTOFFS)
        if lam in (0.0, 1.0):
            cutoffs = sorted(set(cutoffs + LEGACY_ONLY_CUTOFFS))
        tasks.append((index, lam, cutoffs, PRODUCTION_STEPS))
    records, primary_stopped = _wave_map(tasks, workers, started)
    for record in records:
        record["derived"] = derive_weight(record)

    elapsed_after_primary = time.monotonic() - started
    primary_complete = len(records) == len(FORCE_WEIGHTS) and not primary_stopped
    overlap = (
        legacy_overlap_gate(records)
        if primary_complete
        else {
            "passed": False,
            "comparison_count": 0,
            "maximum_absolute_difference_cm": None,
            "comparisons": [],
            "reason": "primary panel stopped at the wall-clock ceiling",
        }
    )
    completeness = completeness_gate(records)
    if primary_complete and elapsed_after_primary < MAX_WALL_SECONDS:
        audit = build_audit(records, workers, started)
    else:
        audit = {
            "passed": False,
            "complete": False,
            "stopped_at_ceiling": primary_stopped or elapsed_after_primary >= MAX_WALL_SECONDS,
            "steps": AUDIT_STEPS,
            "selection_rule": "not run because the primary sweep reached the wall-clock ceiling",
            "endpoints": [],
            "records": [],
        }
    hypothesis = (
        hypothesis_evaluation(records)
        if primary_complete
        else {
            "crossover_sequence_nonincreasing": None,
            "high_weight_strictly_inward_of_lambda_1": None,
            "no_positive_weight_reverse_crossing": None,
            "hypothesis_supported_if_gates_pass": False,
        }
    )
    total_wall_seconds = time.monotonic() - started
    within_ceiling = total_wall_seconds <= MAX_WALL_SECONDS
    gates_passed = (
        primary_complete
        and overlap["passed"]
        and completeness["passed"]
        and audit["passed"]
        and within_ceiling
    )
    verdict = (
        "supported" if gates_passed and hypothesis["hypothesis_supported_if_gates_pass"]
        else "falsified" if gates_passed
        else "inconclusive"
    )

    result = {
        "schema_version": 1,
        "protocol": {
            "model": "minimal-basis LCAO H2+ (zeta=1)",
            "force_weights": FORCE_WEIGHTS,
            "primary_cutoffs_bohr": PRIMARY_CUTOFFS,
            "legacy_control_cutoffs_bohr": LEGACY_CUTOFFS,
            "hidden_units": base.HIDDEN,
            "activation": "tanh",
            "production_steps": PRODUCTION_STEPS,
            "audit_steps": AUDIT_STEPS,
            "lr_high": base.LR_HIGH,
            "lr_low": base.LR_LOW,
            "fold_seed": base.FOLD_SEED,
            "init_seeds": base.INIT_SEEDS,
            "n_points": base.N_POINTS,
            "r_grid_bohr": [base.R_MIN_GRID, base.R_MAX_GRID],
            "n_folds": base.N_FOLDS,
            "workers": workers,
            "threads_per_worker": 1,
            "hartree_to_cm": base.HARTREE_TO_CM,
            "legacy_run_path": str(LEGACY_RUN.relative_to(ROOT)),
            "legacy_run_sha256": sha256(LEGACY_RUN),
            "legacy_model_path": str(LEGACY_MODEL.relative_to(ROOT)),
            "legacy_model_sha256": sha256(LEGACY_MODEL),
            "legacy_results_path": str(LEGACY_RESULTS.relative_to(ROOT)),
            "legacy_results_sha256": sha256(LEGACY_RESULTS),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
        },
        "records": records,
        "controls": {
            "legacy_overlap": overlap,
            "completeness": completeness,
            "optimization_sensitivity": audit,
        },
        "hypothesis": hypothesis,
        "verdict": verdict,
        "runtime": {
            "primary_wall_seconds": elapsed_after_primary,
            "total_wall_seconds": total_wall_seconds,
            "ceiling_seconds": MAX_WALL_SECONDS,
            "within_ceiling": within_ceiling,
            "primary_complete": primary_complete,
            "primary_stopped_at_ceiling": primary_stopped,
        },
    }
    RESULTS_PATH.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}; verdict={verdict}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run cheap preflight checks only")
    parser.add_argument("--workers", type=int, default=REGISTERED_WORKERS)
    arguments = parser.parse_args(argv)
    if arguments.check:
        _cheap_checks()
        print("run_experiment: preflight checks passed")
        return 0
    return run(arguments.workers)


if __name__ == "__main__":
    raise SystemExit(main())
