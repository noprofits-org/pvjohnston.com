#!/usr/bin/env python3
"""Reanalyse the reviewed experiment without conflating its two observables."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENT_DIR = HERE.parent
RESULTS_DIR = EXPERIMENT_DIR / "results"
ANALYSE_SPEC = importlib.util.spec_from_file_location(
    "coherence_hop_analysis_core", HERE / "analyse.py"
)
assert ANALYSE_SPEC and ANALYSE_SPEC.loader
core = importlib.util.module_from_spec(ANALYSE_SPEC)
ANALYSE_SPEC.loader.exec_module(core)

LEGACY_OBSERVABLES = (
    "upper_population",
    "product_qx_lt_0",
    "centroid_x",
    "coherence_amplitude",
)


def _require_local_contract(artifact: dict[str, Any], label: str) -> None:
    contract = artifact.get("coherence_observable_contract", {})
    if (
        contract.get("allowed_interpretation")
        != "mean_single_trajectory_coherence_magnitude"
        or contract.get("post_hoc_phase_sensitive_recovery_possible") is not False
    ):
        raise ValueError(f"{label} lacks the reviewed local-magnitude contract")


def _fingerprint_group(artifacts: dict[str, dict[str, Any]]) -> dict[str, str]:
    output = {}
    for field in core.FINGERPRINT_FIELDS:
        values = {name: artifact.get(field) for name, artifact in artifacts.items()}
        if any(value is None for value in values.values()) or len(set(values.values())) != 1:
            raise ValueError(f"fingerprint mismatch for {field}: {values}")
        output[field] = next(iter(values.values()))
    return output


def _validate_legacy_trace(container: dict[str, Any], time_size: int) -> None:
    for field in LEGACY_OBSERVABLES:
        if core._array(container, field).size != time_size:
            raise ValueError(f"legacy {field} length differs from time grid")
    magnitude = core._array(container, "coherence_amplitude")
    if np.any(magnitude < -1e-12) or np.any(magnitude > 1.0 + 1e-12):
        raise ValueError("local coherence magnitude must lie in [0, 1]")


def _pool_legacy(runs: list[dict[str, Any]], method: str) -> dict[str, list[float]]:
    fields = runs[0][method]
    return {
        field: np.mean(
            [core._array(run[method], field) for run in runs], axis=0
        ).tolist()
        for field in fields
    }


def _legacy_run_outcome(run: dict[str, Any]) -> dict[str, Any]:
    time_fs = core._time_grid(run)
    for method in ("full", "reprop_axe"):
        _validate_legacy_trace(run[method], time_fs.size)
    lifetime = core._first_crossing(
        time_fs, core._array(run["full"], "coherence_amplitude")
    )
    accepted_times = core._accepted_event_times(run)
    early = None
    if lifetime is not None and accepted_times.size:
        early = float(np.mean(accepted_times <= lifetime))
    errors = core._max_errors(
        time_fs, run["full"], run["reprop_axe"], core._sigma_x(run)
    )
    return {
        "seed": int(run["configuration"]["seed"]),
        "local_magnitude_lifetime_fs": lifetime,
        "accepted_hops": int(accepted_times.size),
        "early_hop_fraction": early,
        "max_fp_rp_errors": errors,
        "classifications": core._classifications(lifetime, early, errors),
    }


def _legacy_exact(exact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    coarse, fine = exact["coarse"], exact["fine"]
    for label, trace, expected_grid in (
        ("coarse", coarse, 384), ("fine", fine, 512)
    ):
        configuration = trace["configuration"]
        if int(configuration["grid_n"]) != expected_grid:
            raise ValueError(f"legacy {label} exact grid is off protocol")
        time_fs = core._time_grid(trace)
        _validate_legacy_trace(trace, time_fs.size)
    time_fs = core._time_grid(coarse)
    sigma = core._sigma_x(coarse, fine)
    differences = {}
    for name, field, scale in (
        ("upper_population", "upper_population", 1.0),
        ("product_probability", "product_qx_lt_0", 1.0),
        ("centroid_x_sigma", "centroid_x", sigma),
        ("mean_trajectory_coherence_magnitude", "coherence_amplitude", 1.0),
    ):
        residual = (
            core._array(coarse, field)
            - np.interp(time_fs, core._time_grid(fine), core._array(fine, field))
        ) / scale
        differences[name] = float(np.max(np.abs(residual)))
    norm_error = float(np.max(np.abs(core._array(fine, "norm") - 1.0)))
    criteria = {
        "upper_population": differences["upper_population"] <= 2.0e-4,
        "product_probability": differences["product_probability"] <= 0.005,
        "centroid_x_sigma": differences["centroid_x_sigma"] <= 0.01,
        "fine_norm": norm_error < 1.0e-10,
    }
    spatial_passed = bool(all(criteria.values()))
    return {
        "maximum_time_series_differences": differences,
        "fine_max_norm_error": norm_error,
        "criteria": criteria,
        "spatial_grid_audit_passed": spatial_passed,
        "selected_grid_n": 384 if spatial_passed else 512,
        "timestep_audited": False,
        "box_size_audited": False,
        "interpretation": "secondary selected reference, not a complete exact convergence proof",
    }, coarse if spatial_passed else fine


def _legacy_regime(
    runs: list[dict[str, Any]], exact_trace: dict[str, Any]
) -> dict[str, Any]:
    runs = sorted(runs, key=lambda run: int(run["configuration"]["seed"]))
    time_fs = core._time_grid(runs[0])
    for run in runs:
        if not np.allclose(time_fs, core._time_grid(run), rtol=0.0, atol=1e-12):
            raise ValueError("legacy seed time grids differ")
        for method in ("full", "reprop_axe"):
            _validate_legacy_trace(run[method], time_fs.size)
    pooled = {
        method: _pool_legacy(runs, method) for method in ("full", "reprop_axe")
    }
    lifetime = core._first_crossing(
        time_fs, core._array(pooled["full"], "coherence_amplitude")
    )
    events = core._event_diagnostics(runs, lifetime)
    early = None
    if lifetime is not None and events["accepted"]:
        early = events["accepted_early"] / events["accepted"]
    sigma = core._sigma_x(*runs)
    errors = core._max_errors(time_fs, pooled["full"], pooled["reprop_axe"], sigma)
    per_seed = [_legacy_run_outcome(run) for run in runs]
    interval_values: dict[str, list[float | None]] = {
        "local_magnitude_lifetime_fs": [
            item["local_magnitude_lifetime_fs"] for item in per_seed
        ],
        "early_hop_fraction": [item["early_hop_fraction"] for item in per_seed],
        "accepted_hops": [item["accepted_hops"] for item in per_seed],
    }
    for key in ("upper_population", "product_probability", "centroid_x_sigma", "coherence_amplitude"):
        interval_values[f"max_{key}_error"] = [
            item["max_fp_rp_errors"][key]["value"] for item in per_seed
        ]
    consistency = [
        float(run["diagnostics"]["max_full_internal_consistency_error"])
        for run in runs
    ]
    return {
        "pfm_rate_scale": float(runs[0]["configuration"]["pfm_rate_scale"]),
        "seeds": [int(run["configuration"]["seed"]) for run in runs],
        "geometry_count_per_seed": int(runs[0]["configuration"]["geometry_count"]),
        "nuclear_paths_per_seed": {"fp": int(runs[0]["configuration"]["geometry_count"]),
                                   "rp_axe": 2 * int(runs[0]["configuration"]["geometry_count"])},
        "outcomes": {
            "local_magnitude_lifetime_fs": lifetime,
            "coherence_lifetime_fs": lifetime,
            "early_hop_fraction": early,
            "max_fp_rp_errors": errors,
            "classifications": core._classifications(lifetime, early, errors),
        },
        "per_seed": per_seed,
        "intervals_95": {
            key: core._mean_ci95(values) for key, values in interval_values.items()
        },
        "event_diagnostics": events,
        "fp_coefficient_active_state_inconsistency": {
            "per_seed_maxima": consistency,
            "minimum": min(consistency),
            "maximum": max(consistency),
        },
        "rmse_to_selected_exact": {
            method: core._rmse_to_exact(time_fs, pooled[method], exact_trace, sigma)
            for method in ("full", "reprop_axe")
        },
        # Compatibility alias for the deterministic metrics projection.
        "rmse_to_exact": {
            method: core._rmse_to_exact(time_fs, pooled[method], exact_trace, sigma)
            for method in ("full", "reprop_axe")
        },
    }


def build(
    lineage: dict[str, Any],
    corrective_convergence: dict[str, Any],
    legacy_convergence: dict[str, Any],
    exact: dict[str, Any],
    sweep: dict[str, Any],
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    for label, artifact in (
        ("lineage", lineage),
        ("corrective convergence", corrective_convergence),
        ("legacy convergence", legacy_convergence),
        ("legacy exact", exact),
        ("legacy sweep", sweep),
    ):
        core._reject_volatile_metadata(artifact, label)
    for label, artifact in (
        ("legacy convergence", legacy_convergence),
        ("legacy exact", exact),
        ("legacy sweep", sweep),
    ):
        _require_local_contract(artifact, label)

    corrected_fingerprints = _fingerprint_group({
        "lineage": lineage, "convergence": corrective_convergence
    })
    legacy_fingerprints = _fingerprint_group({
        "convergence": legacy_convergence, "exact": exact, "sweep": sweep
    })
    original_convergence_sha = legacy_convergence["artifact_correction"]["source_sha256"]
    if sweep.get("convergence_sha256") != original_convergence_sha:
        raise ValueError("legacy sweep does not identify the recovered convergence source")
    if exact.get("convergence_sha256") != original_convergence_sha:
        raise ValueError("legacy exact audit does not identify the recovered convergence source")

    convergence_summary = core._analyse_convergence(corrective_convergence)
    if convergence_summary["passed"] != bool(
        corrective_convergence["comparison"]["gate"]["passed"]
    ):
        raise ValueError("stored and independently recomputed convergence verdicts differ")
    convergence_summary["production_blocked"] = not convergence_summary["passed"]
    convergence_summary["candidate_pooled_outcome"] = core._pooled_outcomes(
        corrective_convergence["candidate"]
    )
    convergence_summary["reference_pooled_outcome"] = core._pooled_outcomes(
        corrective_convergence["reference"]
    )

    exact_summary, exact_trace = _legacy_exact(exact)
    if sweep.get("complete") is not True or len(sweep.get("runs", [])) != 28:
        raise ValueError("legacy sweep must contain all 28 archived runs")
    groups: defaultdict[float, list[dict[str, Any]]] = defaultdict(list)
    for run in sweep["runs"]:
        groups[float(run["configuration"]["pfm_rate_scale"])].append(run)
    if set(groups) != set(core.DECLARED_SCALES):
        raise ValueError("legacy sweep has off-protocol rate scales")
    regimes = [_legacy_regime(groups[scale], exact_trace) for scale in core.DECLARED_SCALES]
    finite = [r for r in regimes if r["outcomes"]["early_hop_fraction"] is not None]
    early = [r["outcomes"]["early_hop_fraction"] for r in finite]
    correlations = {}
    for key in ("upper_population", "product_probability", "centroid_x_sigma", "coherence_amplitude"):
        errors = [r["outcomes"]["max_fp_rp_errors"][key]["value"] for r in finite]
        correlations[key] = {"rho": core._spearman(early, errors), "n": len(finite)}
    local_majority = [
        regime for regime in regimes
        if regime["outcomes"]["classifications"]["majority_early_hop"]
    ]
    local_nonrobust = [
        regime for regime in local_majority
        if not regime["outcomes"]["classifications"]["compound_robust"]
    ]
    legacy_gate = legacy_convergence["comparison"]
    if legacy_gate["gate"]["passed"] is not False:
        raise ValueError("legacy convergence gate was expected to fail")

    return {
        "schema_version": 2,
        "experiment": core.EXPERIMENT,
        "publication_status": "reframed_after_observable_correction",
        "input_sha256": input_hashes,
        "artifact_fingerprints": {
            "corrective_phase_sensitive": corrected_fingerprints,
            "legacy_local_magnitude": legacy_fingerprints,
        },
        "observable_scope": {
            "legacy_primary": "mean_single_trajectory_coherence_magnitude",
            "legacy_formula": "mean_over_trajectories_of_2_abs(c_minus_conjugate_times_c_plus)",
            "legacy_not_equivalent_to": "phase_sensitive_ensemble_optical_coherence",
            "corrective_primary": "magnitude_of_ensemble_mean_signed_density_matrix_components",
        },
        "declared": {
            "pfm_rate_scales": list(core.DECLARED_SCALES),
            "error_tolerances": core.ERROR_TOLERANCES,
            "majority_early_hop_threshold": 0.5,
        },
        "lineage_gate": lineage["comparison"],
        "convergence_gate": convergence_summary,
        "legacy_convergence_gate": legacy_gate,
        "exact_grid_gate": exact_summary,
        "regimes": regimes,
        "exploratory_spearman_early_hop_vs_error": correlations,
        "legacy_local_magnitude_summary": {
            "majority_regime_count": len(local_majority),
            "nonrobust_majority_regime_count": len(local_nonrobust),
            "numerically_converged": False,
            "interpretation": "descriptive archived FP-RP comparison only",
        },
        "hypothesis": {
            "verdict": "inconclusive",
            "supported": False,
            "falsified": False,
            "inconclusive": True,
            "majority_regime_reached": False,
            "majority_regime_count": 0,
            "nonrobust_majority_regime_count": 0,
            "all_required_gates_passed": False,
            "optical_coherence_claim_supported": False,
            "corrective_production_run": False,
            "reason": "phase-sensitive production was blocked by the registered fine/finer centroid gate",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lineage", type=Path, default=RESULTS_DIR / "lineage.json")
    parser.add_argument("--convergence", type=Path, default=RESULTS_DIR / "convergence.json")
    parser.add_argument(
        "--legacy-convergence", type=Path,
        default=RESULTS_DIR / "legacy-convergence.json",
    )
    parser.add_argument("--exact", type=Path, default=RESULTS_DIR / "exact.json")
    parser.add_argument("--sweep", type=Path, default=RESULTS_DIR / "sweep.json.gz")
    parser.add_argument("--output", type=Path, default=RESULTS_DIR / "analysis.json")
    parser.add_argument("--figure", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = {
        "lineage": args.lineage,
        "corrective_convergence": args.convergence,
        "legacy_convergence": args.legacy_convergence,
        "legacy_exact": args.exact,
        "legacy_sweep": args.sweep,
    }
    artifacts = {key: core._load(path) for key, path in paths.items()}
    analysis = build(
        artifacts["lineage"], artifacts["corrective_convergence"],
        artifacts["legacy_convergence"], artifacts["legacy_exact"],
        artifacts["legacy_sweep"],
        {key: core._sha256(path) for key, path in paths.items()},
    )
    serialized = json.dumps(analysis, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != serialized:
            raise ValueError(f"{args.output} is missing or stale")
    else:
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(serialized, encoding="utf-8")
        os.replace(temporary, args.output)
    if args.figure:
        core.render_figure(analysis, args.figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
