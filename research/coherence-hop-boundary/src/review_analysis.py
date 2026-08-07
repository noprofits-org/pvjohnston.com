#!/usr/bin/env python3
"""Reanalyse the reviewed experiment without conflating its two observables."""

from __future__ import annotations

import argparse
import hashlib
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
LEGACY_ENVIRONMENT_FIELDS = frozenset({
    "python", "numpy", "platform", "machine", "openblas_num_threads",
})
FROZEN_STABLE_ENVIRONMENT = {
    "schema_version": 2,
    "python_implementation": "CPython",
    "python": "3.12.9",
    "numpy": "2.2.5",
    "operating_system": "Linux",
    "machine": "x86_64",
    "openblas_num_threads": "1",
}
STABLE_ENVIRONMENT_FIELDS = frozenset(FROZEN_STABLE_ENVIRONMENT)
LEGACY_CONVERGENCE_LIMITS = {
    "accepted_event_fraction": 0.02,
    "coherence_lifetime_fs": 0.15,
    "upper_population": 0.02,
    "product_qx_lt_0": 0.02,
    "centroid_x_sigma": 0.03,
}
LEGACY_INITIAL_SIGMA_X = 8.035823190306067


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _validate_environment_fingerprint(
    artifact: dict[str, Any], label: str
) -> None:
    """Verify either the historical host record or the stable v2 contract.

    Existing artifacts retain their schema-v1 host provenance, including the
    kernel/libc string.  Future artifacts use a schema-v2 record containing
    only declared numerical controls.  Both are verified from their embedded
    record, so changing the runtime policy never silently rewrites history.
    """

    environment = artifact.get("environment")
    if not isinstance(environment, dict):
        raise ValueError(f"{label} lacks an environment record")
    schema_version = environment.get("schema_version", 1)
    expected_fields = (
        LEGACY_ENVIRONMENT_FIELDS
        if schema_version == 1 else STABLE_ENVIRONMENT_FIELDS
        if schema_version == 2 else None
    )
    if expected_fields is None:
        raise ValueError(
            f"{label} has unsupported environment schema {schema_version!r}"
        )
    if set(environment) != expected_fields:
        raise ValueError(
            f"{label} environment fields do not match schema {schema_version}"
        )
    if schema_version == 2:
        mismatches = [
            f"{field}={environment[field]!r} (required {expected!r})"
            for field, expected in FROZEN_STABLE_ENVIRONMENT.items()
            if type(environment[field]) is not type(expected)
            or environment[field] != expected
        ]
        if mismatches:
            raise ValueError(
                f"{label} environment violates frozen schema 2: "
                + "; ".join(mismatches)
            )
    recomputed = hashlib.sha256(
        _canonical_json(environment).encode("utf-8")
    ).hexdigest()
    if artifact.get("environment_fingerprint") != recomputed:
        raise ValueError(f"{label} environment fingerprint is stale or edited")


def _require_local_contract(artifact: dict[str, Any], label: str) -> None:
    contract = artifact.get("coherence_observable_contract", {})
    if (
        contract.get("allowed_interpretation")
        != "mean_single_trajectory_coherence_magnitude"
        or contract.get("post_hoc_phase_sensitive_recovery_possible") is not False
    ):
        raise ValueError(f"{label} lacks the reviewed local-magnitude contract")


def _fingerprint_group(artifacts: dict[str, dict[str, Any]]) -> dict[str, str]:
    for name, artifact in artifacts.items():
        _validate_environment_fingerprint(artifact, name)
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


def _validate_embedded_fingerprints(
    artifact: dict[str, Any], trace: dict[str, Any], label: str
) -> None:
    configuration = trace.get("configuration", {})
    for field in core.FINGERPRINT_FIELDS:
        if configuration.get(field) != artifact.get(field):
            raise ValueError(f"{label} has foreign {field}")
    contract = configuration.get("model_contract")
    if not isinstance(contract, dict):
        raise ValueError(f"{label} lacks its frozen model contract")
    contract_fingerprint = hashlib.sha256(
        _canonical_json(contract).encode("utf-8")
    ).hexdigest()
    if contract_fingerprint != configuration.get("model_fingerprint"):
        raise ValueError(f"{label} model contract fingerprint is stale or edited")


def _validate_legacy_convergence_run(
    artifact: dict[str, Any], label: str, run: dict[str, Any],
    *, dt_fs: float, electronic_substeps: int,
) -> None:
    core._require_configuration(run, label, {
        "pfm_rate_scale": 0.05,
        "seed": 2699,
        "geometry_count": 4000,
        "n": 4000,
        "dt_fs": dt_fs,
        "requested_dt_fs": dt_fs,
        "actual_dt_fs": dt_fs,
        "electronic_substeps": electronic_substeps,
        "electronic_dt_fs": dt_fs / electronic_substeps,
        "total_fs": 20.0,
        "center_fraction": 0.5,
        "momentum_kick_toward_ci_sigma_px": 0.0,
        "initial_sigma_x": LEGACY_INITIAL_SIGMA_X,
    })
    _validate_embedded_fingerprints(artifact, run, label)
    hop_times = run.get("full_hop_time_fs")
    full_summary = run.get("event_summary", {}).get("full", {})
    retained_times = full_summary.get("accepted_event_time_fs")
    accepted_count = full_summary.get("counts", {}).get("accepted")
    if (
        not isinstance(hop_times, list)
        or hop_times != retained_times
        or accepted_count != len(hop_times)
    ):
        raise ValueError(f"{label} retained accepted-event inputs disagree")


def _legacy_gate_classification(outcome: dict[str, Any]) -> dict[str, bool]:
    classifications = outcome["classifications"]
    majority = bool(classifications["majority_early_hop"])
    robust = bool(classifications["compound_robust"])
    return {
        "boundary_reached_and_robust": majority and robust,
        "majority_accepted_events_before_coherence_lifetime": majority,
        "rp_axe_within_compound_error_thresholds": robust,
    }


def _finite_abs_difference(
    left: float | None, right: float | None
) -> float | None:
    if left is None or right is None:
        return None
    if not (math.isfinite(float(left)) and math.isfinite(float(right))):
        return None
    return abs(float(left) - float(right))


def _legacy_convergence(artifact: dict[str, Any]) -> dict[str, Any]:
    """Rebuild the archived one-seed gate solely from retained inputs."""

    coarse, fine = artifact["coarse"], artifact["fine"]
    _validate_legacy_convergence_run(
        artifact, "legacy coarse convergence", coarse,
        dt_fs=0.025, electronic_substeps=10,
    )
    _validate_legacy_convergence_run(
        artifact, "legacy fine convergence", fine,
        dt_fs=0.0125, electronic_substeps=20,
    )
    coarse_outcome = _legacy_run_outcome(coarse)
    fine_outcome = _legacy_run_outcome(fine)
    coarse_time = core._time_grid(coarse)
    fine_time = core._time_grid(fine)
    paired: dict[str, float] = {}
    for observable, output_name, scale in (
        ("upper_population", "upper_population", 1.0),
        ("product_qx_lt_0", "product_qx_lt_0", 1.0),
        ("centroid_x", "centroid_x_sigma", LEGACY_INITIAL_SIGMA_X),
    ):
        fine_values = np.interp(
            coarse_time, fine_time, core._array(fine["full"], observable)
        )
        paired[output_name] = float(np.max(np.abs(
            core._array(coarse["full"], observable) - fine_values
        )) / scale)

    fraction_difference = _finite_abs_difference(
        coarse_outcome["early_hop_fraction"],
        fine_outcome["early_hop_fraction"],
    )
    lifetime_difference = _finite_abs_difference(
        coarse_outcome["local_magnitude_lifetime_fs"],
        fine_outcome["local_magnitude_lifetime_fs"],
    )
    coarse_class = _legacy_gate_classification(coarse_outcome)
    fine_class = _legacy_gate_classification(fine_outcome)
    checks = {
        "accepted_event_fraction_difference_within_0_02": bool(
            fraction_difference is not None
            and fraction_difference
            <= LEGACY_CONVERGENCE_LIMITS["accepted_event_fraction"]
        ),
        "coherence_lifetime_difference_within_0_15_fs": bool(
            lifetime_difference is not None
            and lifetime_difference
            <= LEGACY_CONVERGENCE_LIMITS["coherence_lifetime_fs"]
        ),
        "full_upper_population_difference_within_0_02": (
            paired["upper_population"]
            <= LEGACY_CONVERGENCE_LIMITS["upper_population"]
        ),
        "full_product_difference_within_0_02": (
            paired["product_qx_lt_0"]
            <= LEGACY_CONVERGENCE_LIMITS["product_qx_lt_0"]
        ),
        "full_centroid_difference_within_0_03_sigma": (
            paired["centroid_x_sigma"]
            <= LEGACY_CONVERGENCE_LIMITS["centroid_x_sigma"]
        ),
        "majority_classification_unchanged": (
            coarse_class["majority_accepted_events_before_coherence_lifetime"]
            == fine_class["majority_accepted_events_before_coherence_lifetime"]
        ),
        "compound_robustness_classification_unchanged": (
            coarse_class["rp_axe_within_compound_error_thresholds"]
            == fine_class["rp_axe_within_compound_error_thresholds"]
        ),
    }
    checks["passed"] = bool(all(checks.values()))
    return {
        "limits": LEGACY_CONVERGENCE_LIMITS,
        "accepted_event_fraction_abs_difference": fraction_difference,
        "coherence_lifetime_abs_difference_fs": lifetime_difference,
        "maximum_paired_full_time_series_differences": paired,
        "coarse_classification": coarse_class,
        "fine_classification": fine_class,
        "gate": checks,
        "selected_final_numerics": {
            "dt_fs": 0.025 if checks["passed"] else 0.0125,
            "electronic_substeps": 10 if checks["passed"] else 20,
            "reason": (
                "coarse setting passed the frozen convergence gate"
                if checks["passed"]
                else "one or more frozen checks failed; promote the fine setting"
            ),
        },
    }


def _verified_legacy_convergence(artifact: dict[str, Any]) -> dict[str, Any]:
    recomputed = _legacy_convergence(artifact)
    if _canonical_json(artifact.get("comparison")) != _canonical_json(recomputed):
        raise ValueError("stored legacy convergence summary is stale or edited")
    return recomputed


def _legacy_exact(exact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    coarse, fine = exact["coarse"], exact["fine"]
    for label, trace, expected_grid in (
        ("coarse", coarse, 384), ("fine", fine, 512)
    ):
        core._require_configuration(trace, f"legacy {label} exact", {
            "grid_n": expected_grid,
            "half_width": 96.0,
            "dx": 192.0 / expected_grid,
            "requested_dt_fs": 0.025,
            "actual_dt_fs": 0.025,
            "sample_every_fs": 0.025,
            "total_fs": 20.0,
            "center_fraction": 0.5,
            "center_x": 7.7625,
            "momentum_kick_toward_ci_sigma_px": 0.0,
            "mean_momentum_x": 0.0,
            "initial_sigma_x": LEGACY_INITIAL_SIGMA_X,
        })
        _validate_embedded_fingerprints(exact, trace, f"legacy {label} exact")
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
    legacy_gate = _verified_legacy_convergence(legacy_convergence)
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
