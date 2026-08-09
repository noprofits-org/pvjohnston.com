#!/usr/bin/env python3
"""Reconstruct the admitted sample into the canonical Understanding result."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bundle import RAW_NAME, validate_run_bundle
from contract import (
    EXPERIMENT,
    EXPERIMENT_DIR,
    REPOSITORY_ROOT,
    ContractError,
    canonical_json_bytes,
    digest_record,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_json,
    set_deterministic_process_environment,
    sha256_file,
    validate_digest_record,
    validate_json_schema,
    validate_workflow_ledger,
    write_bytes_exclusive,
)
from reconstruct import (
    PRIMITIVE_UNITS,
    assemble_understanding_result,
    detector_frame,
    empirical_survival,
    evaluate_checks,
    muon_frame,
    same_speed_no_lifetime_dilation_counterfactual,
)
from run import build_spec


@dataclass(frozen=True)
class AnalysisSpec:
    paths_m: np.ndarray
    primitives: Mapping[str, Any]
    focal_index: int
    frame_relative_tolerance: float
    standard_error_multiplier: float
    maximum_grid_discrepancy: float
    source_run: Mapping[str, Any]
    integrity_flags: Mapping[str, bool]
    generated_at: str
    analysis_admission: Mapping[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def analysis_admission(
    event_id: str,
    run_id: str,
    *,
    workflow_path: Path = EXPERIMENT_DIR / "workflow.jsonl",
    graph_path: Path = REPOSITORY_ROOT / "research/workflow.graph.v1.json",
    repository_root: Path = REPOSITORY_ROOT,
    workflow_cli_path: Path = REPOSITORY_ROOT / "scripts/research-workflow.mjs",
) -> dict[str, Any]:
    """Bind an immutable historical run approval after complete graph replay."""

    verified_ledger = validate_workflow_ledger(
        workflow_path=workflow_path,
        graph_path=graph_path,
        repository_root=repository_root,
        workflow_cli_path=workflow_cli_path,
    )
    matches = [(event, raw) for event, raw in verified_ledger.records if event.get("event_id") == event_id]
    if len(matches) != 1:
        raise ContractError("analysis approval event is missing or duplicated")
    event, raw_line = matches[0]
    if (
        event.get("type") != "review"
        or event.get("from") != "run_review"
        or event.get("to") != "analyze"
        or event.get("decision") != "approve"
    ):
        raise ContractError("analysis requires a validated historical run_review approval")
    artifacts = event.get("artifacts", [])
    receipt_mentions_run = False
    for artifact in artifacts:
        snapshot_path = artifact.get("snapshot_path")
        if isinstance(snapshot_path, str):
            payload = verified_ledger.snapshot_bytes.get(snapshot_path)
            if payload is not None:
                try:
                    receipt_mentions_run = receipt_mentions_run or run_id in payload.decode("utf-8")
                except UnicodeError as exc:
                    raise ContractError("immutable run-review evidence is not UTF-8") from exc
    if not receipt_mentions_run:
        raise ContractError("immutable run-review evidence does not name the requested run ID")
    return {
        "event_id": event_id,
        "sequence": event["sequence"],
        "submission_sequence": event["submission_sequence"],
        "decision": "approve",
        "graph_version": event["graph_version"],
        "graph_sha256": event["graph_sha256"],
        "workflow_path": "research/muon-survival-two-frames/workflow.jsonl",
        "event_sha256": hashlib.sha256(f"{raw_line}\n".encode("utf-8")).hexdigest(),
    }


def build_analysis_result(proper_lifetimes_s: np.ndarray, spec: AnalysisSpec) -> dict[str, Any]:
    detector = detector_frame(spec.paths_m, **{key: spec.primitives[key] for key in ("momentum_mev_c", "mass_energy_mev", "tau0_s", "c_m_s")})
    muon = muon_frame(spec.paths_m, **{key: spec.primitives[key] for key in ("momentum_mev_c", "mass_energy_mev", "tau0_s", "c_m_s")})
    counterfactual = same_speed_no_lifetime_dilation_counterfactual(
        spec.paths_m,
        detector_beta=detector["beta"],
        tau0_s=spec.primitives["tau0_s"],
        c_m_s=spec.primitives["c_m_s"],
    )
    counts, empirical_probability = empirical_survival(proper_lifetimes_s, muon["elapsed_time_s"])
    def assemble(integrity_flags: Mapping[str, bool]) -> dict[str, Any]:
        checks = evaluate_checks(
            detector,
            muon,
            counterfactual,
            spec.paths_m,
            spec.primitives,
            counts,
            empirical_probability,
            proper_lifetimes_s,
            focal_index=spec.focal_index,
            expected_grid_size=spec.paths_m.size,
            expected_draw_count=proper_lifetimes_s.size,
            frame_relative_tolerance=spec.frame_relative_tolerance,
            standard_error_multiplier=spec.standard_error_multiplier,
            maximum_grid_discrepancy=spec.maximum_grid_discrepancy,
            integrity_flags=integrity_flags,
        )
        result = assemble_understanding_result(
            source_run=spec.source_run,
            primitive_inputs=spec.primitives,
            paths_m=spec.paths_m,
            detector=detector,
            muon=muon,
            counterfactual=counterfactual,
            counts=counts,
            empirical_probability=empirical_probability,
            focal_index=spec.focal_index,
            checks=checks,
        )
        result["generated_at"] = spec.generated_at
        result["analysis_admission"] = dict(spec.analysis_admission)
        result["provenance"] = {
            "generator": digest_record(EXPERIMENT_DIR / "src/analyze.py"),
            "schema": digest_record(EXPERIMENT_DIR / "schemas/analysis-result.schema.json"),
            "inputs": [
                dict(spec.source_run["manifest"]),
                dict(spec.source_run["sample"]),
                dict(spec.source_run["completion"]),
                digest_record(EXPERIMENT_DIR / "inputs.json"),
                digest_record(EXPERIMENT_DIR / "constants.json"),
            ],
        }
        return result

    flags = dict(spec.integrity_flags)
    upstream_schema_valid = flags.get("schema") is True
    flags["schema"] = False
    provisional = assemble(flags)
    result_schema_valid = validate_analysis_result(
        provisional,
        verify_provenance=False,
        enforce_frozen_inputs=False,
    )
    flags["schema"] = bool(upstream_schema_valid and result_schema_valid)
    result = assemble(flags)
    validate_analysis_result(result, verify_provenance=False, enforce_frozen_inputs=False)
    return result


def _focal_matches(frame: Mapping[str, Any], focal: Mapping[str, Any], index: int) -> bool:
    if set(frame) != set(focal):
        return False
    for key, value in frame.items():
        expected = value[index] if isinstance(value, list) else value
        if focal[key] != expected:
            return False
    return True


def validate_analysis_result(
    result: Mapping[str, Any],
    *,
    verify_provenance: bool,
    enforce_frozen_inputs: bool = True,
    repository_root: Path = REPOSITORY_ROOT,
) -> bool:
    """Validate the bound schema plus cross-field result invariants."""

    validation_experiment_dir = repository_root / "research" / EXPERIMENT
    validate_json_schema(result, validation_experiment_dir / "schemas/analysis-result.schema.json")
    grid = result["grid_m"]
    length = len(grid)
    primitive = result["primitive_inputs"]
    calculation_arguments = {
        key: primitive[key]
        for key in ("momentum_mev_c", "mass_energy_mev", "tau0_s", "c_m_s")
    }
    grid_array = np.asarray(grid, dtype=np.float64)
    expected_detector = detector_frame(grid_array, **calculation_arguments)
    expected_muon = muon_frame(grid_array, **calculation_arguments)
    expected_counterfactual = same_speed_no_lifetime_dilation_counterfactual(
        grid_array,
        detector_beta=expected_detector["beta"],
        tau0_s=primitive["tau0_s"],
        c_m_s=primitive["c_m_s"],
    )

    def frame_matches(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
        if set(actual) != set(expected):
            return False
        for key, expected_value in expected.items():
            actual_value = actual[key]
            if isinstance(expected_value, np.ndarray):
                if not np.array_equal(np.asarray(actual_value, dtype=np.float64), expected_value):
                    return False
            elif actual_value != expected_value:
                return False
        return True

    if not frame_matches(result["detector_frame"], expected_detector):
        raise ContractError("analysis detector frame is not derived from its primitives")
    if not frame_matches(result["muon_frame"], expected_muon):
        raise ContractError("analysis muon frame is not derived from its primitives")
    if not frame_matches(result["same_speed_no_lifetime_dilation_counterfactual"], expected_counterfactual):
        raise ContractError("analysis counterfactual is not derived from its primitives")
    counts = np.asarray(result["empirical"]["counts"], dtype=np.int64)
    empirical = np.asarray(result["empirical"]["survival_probability"], dtype=np.float64)
    if not np.array_equal(empirical, counts.astype(np.float64) / counts[0]):
        raise ContractError("analysis empirical probabilities do not match survivor counts")
    if enforce_frozen_inputs:
        inputs = load_and_validate_inputs()
        constants = load_and_validate_constants()["constants"]
        frozen_grid = inputs["production"]["laboratory_grid"]
        frozen_indices = np.arange(frozen_grid["index_start"], frozen_grid["index_stop_inclusive"] + 1, dtype=np.int64)
        frozen_paths = (frozen_indices * frozen_grid["step_m"]).astype(np.float64)
        frozen_primitives = {
            "momentum_mev_c": inputs["production"]["momentum_mev_c"],
            "mass_energy_mev": constants["muon_mass_energy_mev"]["value"],
            "tau0_s": constants["muon_proper_mean_lifetime_s"]["value"],
            "c_m_s": constants["speed_of_light_m_s"]["value"],
            "units": dict(PRIMITIVE_UNITS),
        }
        if primitive != frozen_primitives or not np.array_equal(grid_array, frozen_paths):
            raise ContractError("analysis result does not retain the frozen primitives and grid")
        if result["focal"]["index"] != inputs["production"]["focal_index"] or int(counts[0]) != inputs["production"]["rng"]["draw_count"]:
            raise ContractError("analysis result focal index or draw count differs from the frozen protocol")
    arrays = [
        result["detector_frame"][key]
        for key in ("laboratory_distance_m", "elapsed_time_s", "decay_exponent", "survival_probability")
    ] + [
        result["muon_frame"][key]
        for key in ("contracted_distance_m", "elapsed_time_s", "decay_exponent", "survival_probability")
    ] + [
        result["same_speed_no_lifetime_dilation_counterfactual"][key]
        for key in ("laboratory_distance_m", "elapsed_time_s", "decay_exponent", "survival_probability")
    ] + [result["empirical"]["counts"], result["empirical"]["survival_probability"]]
    if any(len(array) != length for array in arrays):
        raise ContractError("analysis result arrays do not share the frozen grid length")
    focal_index = result["focal"]["index"]
    if not 0 <= focal_index < length:
        raise ContractError("analysis focal index is outside the grid")
    if not _focal_matches(result["detector_frame"], result["focal"]["detector"], focal_index):
        raise ContractError("analysis detector focal projection is stale")
    if not _focal_matches(result["muon_frame"], result["focal"]["muon"], focal_index):
        raise ContractError("analysis muon focal projection is stale")
    if not _focal_matches(result["same_speed_no_lifetime_dilation_counterfactual"], result["focal"]["counterfactual"], focal_index):
        raise ContractError("analysis counterfactual focal projection is stale")
    if result["focal"]["empirical_count"] != result["empirical"]["counts"][focal_index]:
        raise ContractError("analysis empirical focal count is stale")
    if result["focal"]["empirical_survival_probability"] != result["empirical"]["survival_probability"][focal_index]:
        raise ContractError("analysis empirical focal probability is stale")
    pass_names = (
        "frame_agreement",
        "focal_monte_carlo_within_four_standard_errors",
        "maximum_grid_discrepancy_at_most_threshold",
        "counts_valid_and_monotonic",
        "numeric_shapes_dtypes_units_valid",
        "schema_manifest_provenance_and_hashes_valid",
    )
    if result["checks"]["all_passed"] != all(result["checks"][name] is True for name in pass_names):
        raise ContractError("analysis aggregate check is inconsistent")
    expected_detail_names = {
        "shapes_valid", "dtypes_valid", "primitive_inputs_valid", "grid_valid",
        "derived_fields_valid", "counterfactual_valid", "units_valid",
        "detector_units_valid", "muon_units_valid",
        "raw_lifetimes_finite_nonnegative", "primitive_momentum_mev_c_valid",
        "primitive_mass_energy_mev_valid", "primitive_tau0_s_valid",
        "primitive_c_m_s_valid", "primitive_units_valid", "detector_beta_valid",
        "detector_gamma_valid", "detector_laboratory_distance_valid",
        "detector_elapsed_time_valid", "detector_mean_lifetime_valid",
        "detector_decay_exponent_valid", "detector_survival_probability_valid",
        "muon_beta_valid", "muon_gamma_valid", "muon_contracted_distance_valid",
        "muon_elapsed_time_valid", "muon_mean_lifetime_valid",
        "muon_decay_exponent_valid", "muon_survival_probability_valid",
        "counterfactual_label_valid", "counterfactual_units_valid",
        "counterfactual_laboratory_distance_valid", "counterfactual_elapsed_time_valid",
        "counterfactual_decay_exponent_valid", "counterfactual_survival_probability_valid",
        "count_dtype_valid", "count_bounds_valid", "zero_distance_count_valid",
        "counts_monotonic", "empirical_matches_counts",
    }
    details = result["checks"]["details"]
    if set(details) != expected_detail_names or any(not isinstance(value, bool) for value in details.values()):
        raise ContractError("analysis check details do not match the registered contract")
    expected_diagnostic_names = {
        "frame_probability_max_relative_error", "frame_exponent_max_relative_error_nonzero_path",
        "beta_relative_error", "gamma_relative_error", "focal_binomial_standard_error",
        "focal_absolute_discrepancy", "maximum_grid_absolute_discrepancy",
    }
    diagnostics = result["checks"]["diagnostics"]
    if set(diagnostics) != expected_diagnostic_names or any(
        not isinstance(value, (int, float)) or isinstance(value, bool) or not np.isfinite(value)
        for value in diagnostics.values()
    ):
        raise ContractError("analysis diagnostics do not match the registered contract")
    if verify_provenance:
        source_records = [result["source_run"][name] for name in ("manifest", "sample", "completion")]
        for record in source_records:
            validate_digest_record(record, repository_root=repository_root)
        provenance = result["provenance"]
        validate_digest_record(provenance["generator"], repository_root=repository_root)
        validate_digest_record(provenance["schema"], repository_root=repository_root)
        for record in provenance["inputs"]:
            validate_digest_record(record, repository_root=repository_root)
        expected_generator = digest_record(
            validation_experiment_dir / "src/analyze.py",
            public_path=f"research/{EXPERIMENT}/src/analyze.py",
        )
        expected_schema = digest_record(
            validation_experiment_dir / "schemas/analysis-result.schema.json",
            public_path=f"research/{EXPERIMENT}/schemas/analysis-result.schema.json",
        )
        expected_inputs = [
            *source_records,
            digest_record(
                validation_experiment_dir / "inputs.json",
                public_path=f"research/{EXPERIMENT}/inputs.json",
            ),
            digest_record(
                validation_experiment_dir / "constants.json",
                public_path=f"research/{EXPERIMENT}/constants.json",
            ),
        ]
        if provenance["generator"] != expected_generator:
            raise ContractError("analysis generator provenance mismatch")
        if provenance["schema"] != expected_schema:
            raise ContractError("analysis schema provenance mismatch")
        if provenance["inputs"] != expected_inputs:
            raise ContractError("analysis input provenance mismatch")
    return True


def write_or_check_result(
    path: Path,
    result: Mapping[str, Any],
    *,
    check: bool,
    verify_provenance: bool = True,
    enforce_frozen_inputs: bool = True,
    repository_root: Path = REPOSITORY_ROOT,
) -> None:
    validate_analysis_result(
        result,
        verify_provenance=verify_provenance,
        enforce_frozen_inputs=enforce_frozen_inputs,
        repository_root=repository_root,
    )
    expected = canonical_json_bytes(result)
    if check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != expected:
            raise ContractError("canonical result is missing or stale")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_bytes_exclusive(path, expected)


def derive_integrity_flags(
    run_integrity: Mapping[str, Any],
    source_run: Mapping[str, Any],
    admission: Mapping[str, Any],
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, bool]:
    """Derive every integrity flag from a completed validation, not literals."""

    expected_admission_keys = {
        "event_id", "sequence", "submission_sequence", "decision",
        "graph_version", "graph_sha256", "workflow_path", "event_sha256",
    }
    admission_valid = (
        set(admission) == expected_admission_keys
        and admission.get("decision") == "approve"
        and admission.get("graph_version") == 1
        and admission.get("graph_sha256") == "e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404"
        and admission.get("workflow_path") == "research/muon-survival-two-frames/workflow.jsonl"
        and isinstance(admission.get("sequence"), int)
        and isinstance(admission.get("submission_sequence"), int)
        and isinstance(admission.get("event_sha256"), str)
        and len(admission["event_sha256"]) == 64
    )
    source_shape_valid = set(source_run) == {"run_id", "manifest", "sample", "completion"}
    if not source_shape_valid:
        raise ContractError("analysis source-run provenance fields mismatch")
    digest_records_valid = all(
        validate_digest_record(source_run[name], repository_root=repository_root)
        for name in ("manifest", "sample", "completion")
    )
    return {
        "schema": run_integrity.get("schema_valid") is True,
        "manifest": run_integrity.get("manifest_valid") is True,
        "provenance": bool(run_integrity.get("provenance_valid") is True and admission_valid and digest_records_valid),
        "hashes": bool(run_integrity.get("hashes_valid") is True and digest_records_valid),
        "run_bundle": run_integrity.get("valid") is True,
        "run_admission": bool(admission_valid),
    }


def registered_analysis_spec(run_id: str, run_review_event: str, generated_at: str) -> tuple[np.ndarray, AnalysisSpec]:
    run_dir = EXPERIMENT_DIR / "runs" / run_id
    manifest = load_json(run_dir / "run-manifest.json")
    run_spec = build_spec(run_id, recorded_authorization=manifest.get("authorization"))
    integrity = validate_run_bundle(run_dir, run_spec)
    admission = analysis_admission(run_review_event, run_id)
    inputs = load_and_validate_inputs()
    constants = load_and_validate_constants()["constants"]
    grid = inputs["production"]["laboratory_grid"]
    integer_indices = np.arange(grid["index_start"], grid["index_stop_inclusive"] + 1, dtype=np.int64)
    paths = (integer_indices * grid["step_m"]).astype(np.float64)
    primitives = {
        "momentum_mev_c": inputs["production"]["momentum_mev_c"],
        "mass_energy_mev": constants["muon_mass_energy_mev"]["value"],
        "tau0_s": constants["muon_proper_mean_lifetime_s"]["value"],
        "c_m_s": constants["speed_of_light_m_s"]["value"],
        "units": dict(PRIMITIVE_UNITS),
    }
    sample = np.load(run_dir / RAW_NAME, allow_pickle=False)
    source_run = {
        "run_id": run_id,
        "manifest": digest_record(run_dir / "run-manifest.json"),
        "sample": digest_record(run_dir / RAW_NAME),
        "completion": digest_record(run_dir / "COMPLETE.json"),
    }
    integrity_flags = derive_integrity_flags(integrity, source_run, admission)
    checks = inputs["checks"]
    return sample, AnalysisSpec(
        paths_m=paths,
        primitives=primitives,
        focal_index=inputs["production"]["focal_index"],
        frame_relative_tolerance=checks["frame_relative_tolerance"],
        standard_error_multiplier=checks["focal_monte_carlo_standard_error_multiplier"],
        maximum_grid_discrepancy=checks["maximum_grid_absolute_discrepancy"],
        source_run=source_run,
        integrity_flags=integrity_flags,
        generated_at=generated_at,
        analysis_admission=admission,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-review-event", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    set_deterministic_process_environment()
    output = EXPERIMENT_DIR / "results/summary.json"
    if args.check:
        existing = load_json(output)
        generated_at = existing.get("generated_at")
        if not isinstance(generated_at, str):
            raise ContractError("canonical result lacks its frozen generation timestamp")
    else:
        generated_at = utc_now()
    sample, spec = registered_analysis_spec(args.run_id, args.run_review_event, generated_at)
    result = build_analysis_result(sample, spec)
    write_or_check_result(output, result, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
