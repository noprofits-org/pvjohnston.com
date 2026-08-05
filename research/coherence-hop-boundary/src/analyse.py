#!/usr/bin/env python3
"""Deterministic analysis for the coherence--hop-boundary experiment."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


EXPERIMENT = "coherence-hop-boundary"
HERE = Path(__file__).resolve().parent
EXPERIMENT_DIR = HERE.parent
RESULTS_DIR = EXPERIMENT_DIR / "results"
DECLARED_SCALES = (1.0, 0.5, 0.25, 0.125, 0.10, 0.075, 0.05)
DECLARED_SEEDS = (2701, 2702, 2703, 2704)
ERROR_TOLERANCES = {
    "upper_population": 0.05,
    "product_probability": 0.05,
    "centroid_x_sigma": 0.10,
}
CONVERGENCE_TOLERANCES = {
    "early_hop_fraction": 0.02,
    "coherence_lifetime_fs": 0.15,
    "full_upper_population": 0.02,
    "full_product_probability": 0.02,
    "full_centroid_x_sigma": 0.03,
}
EXACT_TOLERANCES = {
    "upper_population": 2.0e-4,
    "product_probability": 0.005,
    "centroid_x_sigma": 0.01,
    "fine_norm_error": 1.0e-10,
}
OBSERVABLES = (
    "upper_population",
    "product_qx_lt_0",
    "centroid_x",
    "coherence_amplitude",
)
T_CRITICAL_95 = {2: 12.706, 3: 4.303, 4: 3.182}
FINGERPRINT_FIELDS = (
    "model_fingerprint",
    "simulator_sha256",
    "config_sha256",
    "environment_fingerprint",
)
FINAL_GEOMETRY_COUNT = 4000
FINAL_TOTAL_FS = 20.0
FINAL_CENTER_FRACTION = 0.5
FINAL_MOMENTUM_KICK_SIGMA = 0.0


def _load(path: Path) -> dict[str, Any]:
    if path.suffix == ".gz":
        handle = gzip.open(path, mode="rt", encoding="utf-8")
    else:
        handle = path.open(encoding="utf-8")
    with handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _current_runtime_fingerprints() -> dict[str, str]:
    environment = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS", ""),
    }
    environment_fingerprint = hashlib.sha256(
        json.dumps(
            environment, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()
    return {
        "simulator_sha256": _sha256(HERE / "simulate.py"),
        "config_sha256": _sha256(EXPERIMENT_DIR / "config.json"),
        "environment_fingerprint": environment_fingerprint,
    }


def _finite(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _array(container: dict[str, Any], field: str) -> np.ndarray:
    values = container[field]
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.size == 0 or not np.all(np.isfinite(result)):
        raise ValueError(f"{field} must be a nonempty finite one-dimensional series")
    return result


def _time_grid(record: dict[str, Any]) -> np.ndarray:
    time_fs = _array(record, "time_fs")
    total_fs = _finite(record.get("configuration", {}).get("total_fs"), "total_fs")
    if (
        not math.isclose(float(time_fs[0]), 0.0, abs_tol=1e-12)
        or not math.isclose(float(time_fs[-1]), total_fs, abs_tol=1e-12)
        or np.any(np.diff(time_fs) <= 0.0)
    ):
        raise ValueError("time grid must increase strictly from zero to total_fs")
    return time_fs


def _trace_container(trace: dict[str, Any]) -> dict[str, Any]:
    return trace.get("observables", trace)


def _sigma_x(*records: dict[str, Any]) -> float:
    for record in records:
        configuration = record.get("configuration", {})
        if "initial_sigma_x" in configuration:
            return _finite(configuration["initial_sigma_x"], "initial_sigma_x")
        if "initial_sigma_x" in record:
            return _finite(record["initial_sigma_x"], "initial_sigma_x")
    return math.sqrt(1.0 / (2.0 * 7.743e-3))


def _first_crossing(time_fs: np.ndarray, coherence: np.ndarray) -> float | None:
    threshold = coherence[0] / math.e
    indices = np.flatnonzero(coherence <= threshold)
    if not indices.size:
        return None
    index = int(indices[0])
    if index == 0:
        return float(time_fs[0])
    t0, t1 = time_fs[index - 1:index + 1]
    y0, y1 = coherence[index - 1:index + 1]
    if abs(y1 - y0) <= 1.0e-15:
        return float(t1)
    return float(t0 + (threshold - y0) * (t1 - t0) / (y1 - y0))


def _accepted_events(run: dict[str, Any]) -> list[dict[str, Any]]:
    records = run["events"]["full"]
    return [event for event in records if event["outcome"] == "accepted"]


def _event_diagnostics(
    runs: list[dict[str, Any]], lifetime_fs: float | None
) -> dict[str, Any]:
    proposed = frustrated = accepted = 0
    total_trajectories = sum(
        int(run["configuration"]["geometry_count"]) for run in runs
    )
    timing = {
        "early": {
            "proposed": 0, "frustrated": 0, "accepted": 0,
            "first_accepted": 0, "repeat_accepted": 0,
        },
        "late": {
            "proposed": 0, "frustrated": 0, "accepted": 0,
            "first_accepted": 0, "repeat_accepted": 0,
        },
    }
    directions = {
        "lower_to_upper": {"proposed": 0, "frustrated": 0, "accepted": 0},
        "upper_to_lower": {"proposed": 0, "frustrated": 0, "accepted": 0},
    }
    by_trajectory: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    early = 0
    for run in runs:
        seed = int(run["configuration"]["seed"])
        for order, event in enumerate(run["events"]["full"]):
            outcome = str(event["outcome"])
            if outcome not in ("accepted", "frustrated"):
                raise ValueError(f"unknown event outcome {outcome!r}")
            source = int(event["from_state"])
            target = int(event["to_state"])
            direction = (
                "lower_to_upper" if (source, target) == (0, 1)
                else "upper_to_lower" if (source, target) == (1, 0)
                else None
            )
            if direction is None:
                raise ValueError("hop direction must be 0->1 or 1->0")
            proposed += 1
            directions[direction]["proposed"] += 1
            time = _finite(event["time_fs"], "event time")
            period = None
            if lifetime_fs is not None:
                period = "early" if time <= lifetime_fs else "late"
                timing[period]["proposed"] += 1
            if outcome == "frustrated":
                frustrated += 1
                directions[direction]["frustrated"] += 1
                if period is not None:
                    timing[period]["frustrated"] += 1
                continue
            accepted += 1
            directions[direction]["accepted"] += 1
            trajectory_key = (seed, int(event["trajectory_id"]))
            hop_class = event.get("accepted_hop_class")
            if hop_class not in ("first", "repeat"):
                hop_class = "first" if not by_trajectory[trajectory_key] else "repeat"
            if period is not None:
                timing[period]["accepted"] += 1
                timing[period][f"{hop_class}_accepted"] += 1
            if period == "early":
                early += 1
            copied = dict(event)
            copied["_order"] = order
            by_trajectory[trajectory_key].append(copied)

    repeat = recrossing = trajectories_with_repeats = 0
    trajectories_with_recrossing = 0
    for events in by_trajectory.values():
        events.sort(key=lambda event: (float(event["time_fs"]), int(event["_order"])))
        repeats_here = max(0, len(events) - 1)
        repeat += repeats_here
        trajectories_with_repeats += int(repeats_here > 0)
        initial_state = int(events[0]["from_state"])
        recross_here = sum(
            bool(event.get("recrossing", int(event["to_state"]) == initial_state))
            for event in events[1:]
        )
        recrossing += recross_here
        trajectories_with_recrossing += int(recross_here > 0)

    unique = len(by_trajectory)
    return {
        "proposed": proposed,
        "frustrated": frustrated,
        "accepted": accepted,
        "accepted_early": early if lifetime_fs is not None else None,
        "accepted_late": accepted - early if lifetime_fs is not None else None,
        "acceptance_fraction": accepted / proposed if proposed else None,
        "timing": timing if lifetime_fs is not None else {
            "early": {
                "proposed": None, "frustrated": None, "accepted": None,
                "first_accepted": None, "repeat_accepted": None,
            },
            "late": {
                "proposed": None, "frustrated": None, "accepted": None,
                "first_accepted": None, "repeat_accepted": None,
            },
        },
        "directions": directions,
        "trajectory_count": total_trajectories,
        "unique_hopping_trajectories": unique,
        "first_hop_events": unique,
        "repeat_hop_events": repeat,
        "recrossing_events": recrossing,
        "trajectories_with_repeats": trajectories_with_repeats,
        "trajectories_with_recrossing": trajectories_with_recrossing,
        "unique_first_fraction_of_accepted": unique / accepted if accepted else None,
        "repeat_fraction_of_accepted": repeat / accepted if accepted else None,
        "recrossing_fraction_of_accepted": recrossing / accepted if accepted else None,
        "hopping_trajectory_fraction": (
            unique / total_trajectories if total_trajectories else None
        ),
        "repeat_hopping_trajectory_fraction": (
            trajectories_with_repeats / total_trajectories
            if total_trajectories else None
        ),
        "recrossing_trajectory_fraction": (
            trajectories_with_recrossing / total_trajectories
            if total_trajectories else None
        ),
        "early_first_hop_fraction": (
            timing["early"]["first_accepted"] / unique
            if lifetime_fs is not None and unique else None
        ),
        "early_repeat_hop_fraction": (
            timing["early"]["repeat_accepted"] / repeat
            if lifetime_fs is not None and repeat else None
        ),
    }


def _max_errors(time_fs: np.ndarray, full: dict[str, Any], rp: dict[str, Any], sigma: float) -> dict[str, Any]:
    definitions = (
        ("upper_population", "upper_population", 1.0),
        ("product_probability", "product_qx_lt_0", 1.0),
        ("centroid_x_sigma", "centroid_x", sigma),
        ("coherence_amplitude", "coherence_amplitude", 1.0),
    )
    output: dict[str, Any] = {}
    for name, field, scale in definitions:
        difference = np.abs(_array(full, field) - _array(rp, field)) / scale
        index = int(np.argmax(difference))
        output[name] = {
            "value": float(difference[index]),
            "time_fs": float(time_fs[index]),
        }
    return output


def _classifications(lifetime: float | None, early_fraction: float | None, errors: dict[str, Any]) -> dict[str, bool]:
    majority = lifetime is not None and early_fraction is not None and early_fraction >= 0.5
    robust = all(errors[key]["value"] <= tolerance for key, tolerance in ERROR_TOLERANCES.items())
    return {
        "coherence_lifetime_censored": lifetime is None,
        "majority_early_hop": majority,
        "compound_robust": robust,
        "nonrobust_majority": majority and not robust,
    }


def _run_outcomes(run: dict[str, Any]) -> dict[str, Any]:
    time_fs = _time_grid(run)
    full = run["full"]
    rp = run["reprop_axe"]
    for container in (full, rp):
        for field in OBSERVABLES:
            if _array(container, field).size != time_fs.size:
                raise ValueError(f"{field} length differs from time grid")
    lifetime = _first_crossing(time_fs, _array(full, "coherence_amplitude"))
    accepted = _accepted_events(run)
    early = None
    if lifetime is not None and accepted:
        early = sum(float(event["time_fs"]) <= lifetime for event in accepted) / len(accepted)
    errors = _max_errors(time_fs, full, rp, _sigma_x(run))
    return {
        "coherence_lifetime_fs": lifetime,
        "accepted_hops": len(accepted),
        "early_hop_fraction": early,
        "max_fp_rp_errors": errors,
        "classifications": _classifications(lifetime, early, errors),
    }


def _mean_ci95(values: list[float | None]) -> dict[str, Any]:
    finite = np.asarray([value for value in values if value is not None], dtype=float)
    if not finite.size:
        return {"mean": None, "lower": None, "upper": None, "half_width": None, "n": 0}
    mean = float(np.mean(finite))
    if finite.size == 1:
        half_width = None
    else:
        critical = T_CRITICAL_95.get(int(finite.size), 1.96)
        half_width = float(critical * np.std(finite, ddof=1) / math.sqrt(finite.size))
    return {
        "mean": mean,
        "lower": None if half_width is None else mean - half_width,
        "upper": None if half_width is None else mean + half_width,
        "half_width": half_width,
        "n": int(finite.size),
    }


def _interp(reference: dict[str, Any], field: str, time_fs: np.ndarray) -> np.ndarray:
    reference_time = _array(reference, "time_fs")
    reference_values = _array(_trace_container(reference), field)
    if time_fs[0] < reference_time[0] - 1e-12 or time_fs[-1] > reference_time[-1] + 1e-12:
        raise ValueError("exact trace does not cover the trajectory time grid")
    return np.interp(time_fs, reference_time, reference_values)


def _rmse_to_exact(
    time_fs: np.ndarray,
    method: dict[str, Any],
    exact: dict[str, Any],
    sigma: float,
) -> dict[str, float]:
    output = {}
    for name, field, scale in (
        ("upper_population", "upper_population", 1.0),
        ("product_probability", "product_qx_lt_0", 1.0),
        ("centroid_x_sigma", "centroid_x", sigma),
        ("coherence_amplitude", "coherence_amplitude", 1.0),
    ):
        residual = (_array(method, field) - _interp(exact, field, time_fs)) / scale
        output[name] = float(np.sqrt(np.mean(residual * residual)))
    return output


def _require_configuration(
    record: dict[str, Any], label: str, expected: dict[str, Any]
) -> None:
    configuration = record.get("configuration", {})
    for field, value in expected.items():
        if configuration.get(field) != value:
            raise ValueError(f"{label} has off-protocol {field}")


def _analyse_exact(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    coarse, fine = data["coarse"], data["fine"]
    for label, record, grid_n in (("coarse exact", coarse, 384), ("fine exact", fine, 512)):
        _require_configuration(record, label, {
            "grid_n": grid_n,
            "half_width": 96.0,
            "requested_dt_fs": 0.025,
            "total_fs": FINAL_TOTAL_FS,
            "center_fraction": FINAL_CENTER_FRACTION,
            "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
        })
    time_fs = _time_grid(coarse)
    _time_grid(fine)
    sigma = _sigma_x(coarse, fine)
    differences = {}
    for name, field, scale in (
        ("upper_population", "upper_population", 1.0),
        ("product_probability", "product_qx_lt_0", 1.0),
        ("centroid_x_sigma", "centroid_x", sigma),
        ("coherence_amplitude", "coherence_amplitude", 1.0),
    ):
        delta = (_array(_trace_container(coarse), field) - _interp(fine, field, time_fs)) / scale
        differences[name] = float(np.max(np.abs(delta)))
    fine_norm_error = float(np.max(np.abs(_array(_trace_container(fine), "norm") - 1.0)))
    criteria = {
        "upper_population": differences["upper_population"] <= EXACT_TOLERANCES["upper_population"],
        "product_probability": differences["product_probability"] <= EXACT_TOLERANCES["product_probability"],
        "centroid_x_sigma": differences["centroid_x_sigma"] <= EXACT_TOLERANCES["centroid_x_sigma"],
        "fine_norm": fine_norm_error < EXACT_TOLERANCES["fine_norm_error"],
    }
    coarse_accepted = all(criteria.values())
    summary = {
        "tolerances": EXACT_TOLERANCES,
        "maximum_time_series_differences": differences,
        "fine_max_norm_error": fine_norm_error,
        "criteria": criteria,
        "coarse_grid_accepted": coarse_accepted,
        "production_grid_n": int((coarse if coarse_accepted else fine)["configuration"]["grid_n"]),
        "passed": bool(criteria["fine_norm"]),
    }
    return summary, coarse if coarse_accepted else fine


def _analyse_convergence(data: dict[str, Any]) -> dict[str, Any]:
    coarse, fine = data["coarse"], data["fine"]
    for label, record, dt_fs, substeps in (
        ("coarse convergence", coarse, 0.025, 10),
        ("fine convergence", fine, 0.0125, 20),
    ):
        _require_configuration(record, label, {
            "pfm_rate_scale": 0.05,
            "seed": 2699,
            "geometry_count": FINAL_GEOMETRY_COUNT,
            "dt_fs": dt_fs,
            "electronic_substeps": substeps,
            "total_fs": FINAL_TOTAL_FS,
            "center_fraction": FINAL_CENTER_FRACTION,
            "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
        })
    coarse_outcome, fine_outcome = _run_outcomes(coarse), _run_outcomes(fine)
    coarse_time = _time_grid(coarse)
    fine_time = _time_grid(fine)
    sigma = _sigma_x(coarse, fine)
    differences = {}
    for name, field, scale in (
        ("full_upper_population", "upper_population", 1.0),
        ("full_product_probability", "product_qx_lt_0", 1.0),
        ("full_centroid_x_sigma", "centroid_x", sigma),
    ):
        fine_values = np.interp(coarse_time, fine_time, _array(fine["full"], field))
        differences[name] = float(np.max(np.abs(_array(coarse["full"], field) - fine_values)) / scale)
    for key in ("early_hop_fraction", "coherence_lifetime_fs"):
        a, b = coarse_outcome[key], fine_outcome[key]
        differences[key] = None if a is None or b is None else abs(float(a) - float(b))
    unchanged = {
        name: coarse_outcome["classifications"][name] == fine_outcome["classifications"][name]
        for name in ("majority_early_hop", "compound_robust")
    }
    criteria = {
        key: differences[key] is not None and differences[key] <= tolerance
        for key, tolerance in CONVERGENCE_TOLERANCES.items()
    }
    criteria.update({f"{key}_unchanged": value for key, value in unchanged.items()})
    coarse_accepted = all(criteria.values())
    production = coarse if coarse_accepted else fine
    return {
        "tolerances": CONVERGENCE_TOLERANCES,
        "differences": differences,
        "classification_unchanged": unchanged,
        "criteria": criteria,
        "coarse_setting_accepted": coarse_accepted,
        "production_dt_fs": float(production["configuration"]["dt_fs"]),
        "production_electronic_substeps": int(production["configuration"]["electronic_substeps"]),
        "passed": True,
    }


def _rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def _spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(y) < 2:
        return None
    xr, yr = _rank(np.asarray(x, dtype=float)), _rank(np.asarray(y, dtype=float))
    if np.std(xr) == 0.0 or np.std(yr) == 0.0:
        return None
    return float(np.corrcoef(xr, yr)[0, 1])


def _analyse_regime(runs: list[dict[str, Any]], exact: dict[str, Any]) -> dict[str, Any]:
    runs = sorted(runs, key=lambda run: int(run["configuration"]["seed"]))
    time_fs = _time_grid(runs[0])
    for run in runs[1:]:
        if not np.allclose(time_fs, _time_grid(run), rtol=0.0, atol=1e-12):
            raise ValueError("seed time grids differ")
    pooled = {
        method: {
            field: np.mean([_array(run[method], field) for run in runs], axis=0).tolist()
            for field in OBSERVABLES
        }
        for method in ("full", "reprop_axe")
    }
    sigma = _sigma_x(*runs)
    lifetime = _first_crossing(time_fs, _array(pooled["full"], "coherence_amplitude"))
    events = _event_diagnostics(runs, lifetime)
    early_fraction = None
    if lifetime is not None and events["accepted"]:
        early_fraction = events["accepted_early"] / events["accepted"]
    errors = _max_errors(time_fs, pooled["full"], pooled["reprop_axe"], sigma)
    per_seed = []
    for run in runs:
        values = _run_outcomes(run)
        per_seed.append({"seed": int(run["configuration"]["seed"]), **values})
    interval_fields = {
        "coherence_lifetime_fs": [item["coherence_lifetime_fs"] for item in per_seed],
        "early_hop_fraction": [item["early_hop_fraction"] for item in per_seed],
        "accepted_hops": [item["accepted_hops"] for item in per_seed],
    }
    for error in ("upper_population", "product_probability", "centroid_x_sigma", "coherence_amplitude"):
        interval_fields[f"max_{error}_error"] = [
            item["max_fp_rp_errors"][error]["value"] for item in per_seed
        ]
    return {
        "pfm_rate_scale": float(runs[0]["configuration"]["pfm_rate_scale"]),
        "seeds": [int(run["configuration"]["seed"]) for run in runs],
        "geometry_count_per_seed": int(runs[0]["configuration"]["geometry_count"]),
        "time_fs": time_fs.tolist(),
        "pooled": pooled,
        "outcomes": {
            "coherence_lifetime_fs": lifetime,
            "early_hop_fraction": early_fraction,
            "max_fp_rp_errors": errors,
            "classifications": _classifications(lifetime, early_fraction, errors),
        },
        "per_seed": per_seed,
        "intervals_95": {key: _mean_ci95(values) for key, values in interval_fields.items()},
        "event_diagnostics": events,
        "rmse_to_exact": {
            method: _rmse_to_exact(time_fs, pooled[method], exact, sigma)
            for method in ("full", "reprop_axe")
        },
    }


def build_analysis(
    lineage: dict[str, Any],
    convergence: dict[str, Any],
    exact: dict[str, Any],
    sweep: dict[str, Any],
) -> dict[str, Any]:
    artifacts = {
        "lineage": lineage,
        "convergence": convergence,
        "exact": exact,
        "sweep": sweep,
    }
    fingerprints = {}
    for field in FINGERPRINT_FIELDS:
        values = {label: artifact.get(field) for label, artifact in artifacts.items()}
        if any(value is None for value in values.values()):
            raise ValueError(f"all canonical artifacts must declare {field}")
        if len(set(values.values())) != 1:
            raise ValueError(f"canonical artifact {field} values do not match")
        fingerprints[field] = next(iter(values.values()))
    if not bool(sweep.get("complete")):
        raise ValueError("confirmatory sweep must be marked complete")
    expected_sweep_metadata = {
        "scales": list(DECLARED_SCALES),
        "seeds": list(DECLARED_SEEDS),
        "declared_replicates": len(DECLARED_SCALES) * len(DECLARED_SEEDS),
        "completed_replicates": len(DECLARED_SCALES) * len(DECLARED_SEEDS),
    }
    for field, expected in expected_sweep_metadata.items():
        if sweep.get(field) != expected:
            raise ValueError(f"sweep has off-protocol {field}")
    exact_summary, exact_trace = _analyse_exact(exact)
    convergence_summary = _analyse_convergence(convergence)
    groups: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for run in sweep["runs"]:
        groups[float(run["configuration"]["pfm_rate_scale"])].append(run)
    if set(groups) != set(DECLARED_SCALES):
        raise ValueError("sweep must contain all and only the seven declared PFM-rate scales")
    for scale, runs in groups.items():
        seeds = [int(run["configuration"]["seed"]) for run in runs]
        if sorted(seeds) != list(DECLARED_SEEDS):
            raise ValueError(f"scale {scale:g} must contain exactly seeds 2701--2704")
        for run in runs:
            configuration = run["configuration"]
            expected_run = {
                "pfm_rate_scale": scale,
                "geometry_count": FINAL_GEOMETRY_COUNT,
                "total_fs": FINAL_TOTAL_FS,
                "center_fraction": FINAL_CENTER_FRACTION,
                "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
            }
            for field, expected in expected_run.items():
                if configuration.get(field) != expected:
                    raise ValueError(
                        f"scale {scale:g} seed {configuration.get('seed')} "
                        f"has off-protocol {field}"
                    )
            for field, expected in fingerprints.items():
                if configuration.get(field) != expected:
                    raise ValueError(
                        f"scale {scale:g} seed {configuration.get('seed')} "
                        f"has a foreign {field}"
                    )
            if (
                not math.isclose(float(configuration["dt_fs"]), convergence_summary["production_dt_fs"], abs_tol=1e-15)
                or int(configuration["electronic_substeps"])
                != convergence_summary["production_electronic_substeps"]
            ):
                raise ValueError(f"scale {scale:g} does not use convergence-selected numerics")
    regimes = [_analyse_regime(groups[scale], exact_trace) for scale in DECLARED_SCALES]
    finite_regimes = [
        regime for regime in regimes
        if regime["outcomes"]["early_hop_fraction"] is not None
    ]
    early = [regime["outcomes"]["early_hop_fraction"] for regime in finite_regimes]
    correlations = {}
    for key in ("upper_population", "product_probability", "centroid_x_sigma", "coherence_amplitude"):
        errors = [
            regime["outcomes"]["max_fp_rp_errors"][key]["value"]
            for regime in finite_regimes
        ]
        correlations[key] = {"rho": _spearman(early, errors), "n": len(finite_regimes)}
    majority = [r for r in regimes if r["outcomes"]["classifications"]["majority_early_hop"]]
    nonrobust = [r for r in majority if not r["outcomes"]["classifications"]["compound_robust"]]
    lineage_comparison = lineage["comparison"]
    lineage_passed = bool(lineage_comparison["passed"])
    gates_ready = lineage_passed and convergence_summary["passed"] and exact_summary["passed"]
    if not gates_ready:
        verdict = "inconclusive"
    elif majority and nonrobust:
        verdict = "supported"
    else:
        verdict = "falsified"
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT,
        "artifact_fingerprints": fingerprints,
        "declared": {
            "pfm_rate_scales": list(DECLARED_SCALES),
            "error_tolerances": ERROR_TOLERANCES,
            "majority_early_hop_threshold": 0.5,
        },
        "lineage_gate": lineage_comparison,
        "convergence_gate": convergence_summary,
        "exact_grid_gate": exact_summary,
        "regimes": regimes,
        "exploratory_spearman_early_hop_vs_error": correlations,
        "hypothesis": {
            "verdict": verdict,
            "supported": verdict == "supported",
            "falsified": verdict == "falsified",
            "inconclusive": verdict == "inconclusive",
            "majority_regime_reached": bool(majority),
            "majority_regime_count": len(majority),
            "nonrobust_majority_regime_count": len(nonrobust),
            "all_required_gates_passed": gates_ready,
        },
    }


def render_figure(analysis: dict[str, Any], output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from PIL import Image

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 14,
        "axes.linewidth": 1.5,
        "svg.hashsalt": EXPERIMENT,
    })
    palette = {
        "ink": "#1a1d2b", "ink2": "#232a48", "indigo": "#465c9b",
        "lifted": "#8fa5e3", "deep": "#2f417a", "cream": "#f5f2ea",
        "paper": "#fbfaf6",
    }
    fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100, facecolor=palette["paper"])
    ax.set_facecolor(palette["paper"])
    x = np.asarray([
        np.nan if r["outcomes"]["early_hop_fraction"] is None
        else r["outcomes"]["early_hop_fraction"]
        for r in analysis["regimes"]
    ], dtype=float)
    series = (
        ("upper_population", ERROR_TOLERANCES["upper_population"], r"$P_+$", "A", palette["indigo"], "o", (7, 9)),
        ("product_probability", ERROR_TOLERANCES["product_probability"],
         r"$P(q_x<0)$", "B", palette["lifted"], "s", (7, -20)),
        ("centroid_x_sigma", ERROR_TOLERANCES["centroid_x_sigma"],
         r"$\langle q_x\rangle/\sigma_x$", "C", palette["deep"], "^", (7, 9)),
    )
    for key, tolerance, label, letter, color, marker, offset in series:
        y = np.asarray([r["outcomes"]["max_fp_rp_errors"][key]["value"] / tolerance for r in analysis["regimes"]])
        finite = np.isfinite(x) & np.isfinite(y)
        if not np.any(finite):
            continue
        x_series, y_series = x[finite], y[finite]
        order = np.argsort(x_series)
        ax.plot(x_series[order], y_series[order], color=color, marker=marker, linewidth=2.8,
                markersize=8, markeredgecolor=palette["ink"], markeredgewidth=0.8, label=label)
        index = int(np.argmax(y_series))
        ax.annotate(letter, (x_series[index], y_series[index]), xytext=offset, textcoords="offset points",
                    color=palette["ink"], fontsize=16, fontweight="bold")
    ax.axhline(1.0, color=palette["ink2"], linewidth=1.3, linestyle="--")
    ax.axvline(0.5, color=palette["ink2"], linewidth=1.3, linestyle=":")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel(r"$f_{\mathrm{early}}$")
    ax.set_ylabel(r"$\max_t|\mathrm{FP}-\mathrm{RP}|\,/\,\mathrm{tol.}$")
    ax.tick_params(colors=palette["ink"], width=1.2, length=6)
    for spine in ax.spines.values():
        spine.set_color(palette["ink"])
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        legend = ax.legend(frameon=True, facecolor=palette["cream"], edgecolor=palette["ink2"], ncol=3)
        legend.get_frame().set_linewidth(1.0)
    ax.margins(x=0.06, y=0.14)
    fig.tight_layout(pad=1.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".png", dir=output.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        fig.savefig(temporary, dpi=100, facecolor=palette["paper"], metadata={"Software": EXPERIMENT})
        plt.close(fig)
        with Image.open(temporary) as opened:
            pixels = opened.convert("RGB")
            pixels.save(output, format="PNG", compress_level=9, dpi=(100, 100))
    finally:
        temporary.unlink(missing_ok=True)


def _serialize(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, allow_nan=False) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lineage", type=Path, default=RESULTS_DIR / "lineage.json")
    parser.add_argument("--convergence", type=Path, default=RESULTS_DIR / "convergence.json")
    parser.add_argument("--exact", type=Path, default=RESULTS_DIR / "exact.json")
    parser.add_argument("--sweep", type=Path, default=RESULTS_DIR / "sweep.json.gz")
    parser.add_argument("--output", type=Path, default=RESULTS_DIR / "analysis.json")
    parser.add_argument("--figure", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lineage = _load(args.lineage)
    convergence = _load(args.convergence)
    exact = _load(args.exact)
    sweep = _load(args.sweep)
    lineage_sha256 = _sha256(args.lineage)
    convergence_sha256 = _sha256(args.convergence)
    exact_sha256 = _sha256(args.exact)
    for label, artifact in (("convergence", convergence), ("exact", exact), ("sweep", sweep)):
        if artifact.get("lineage_gate", {}).get("sha256") != lineage_sha256:
            raise ValueError(f"{label} is not bound to the selected lineage artifact")
    if exact.get("convergence_sha256") != convergence_sha256:
        raise ValueError("exact audit is not bound to the selected convergence artifact")
    if sweep.get("convergence_sha256") != convergence_sha256:
        raise ValueError("sweep is not bound to the selected convergence artifact")
    if sweep.get("exact_gate", {}).get("sha256") != exact_sha256:
        raise ValueError("sweep is not bound to the selected exact-grid artifact")
    document = build_analysis(lineage, convergence, exact, sweep)
    for field, expected in _current_runtime_fingerprints().items():
        if document["artifact_fingerprints"].get(field) != expected:
            raise ValueError(f"canonical artifacts do not match current {field}")
    document["input_sha256"] = {
        "lineage": lineage_sha256,
        "convergence": convergence_sha256,
        "exact": exact_sha256,
        "sweep": _sha256(args.sweep),
    }
    expected = _serialize(document)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            print(f"{args.output}: missing or stale", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(expected, encoding="utf-8")
        os.replace(temporary, args.output)
    if args.figure is not None:
        render_figure(document, args.figure)
    print(f"{EXPERIMENT}: analysis {'current' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
