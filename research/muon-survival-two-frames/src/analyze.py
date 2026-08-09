#!/usr/bin/env python3
"""Reconstruct the admitted sample into the canonical Understanding result."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np

from bundle import (
    CHECKSUMS_NAME,
    COMPLETION_NAME,
    MANIFEST_NAME,
    RAW_NAME,
    STDERR_NAME,
    STDOUT_NAME,
    RunSpec,
    validate_run_bundle,
)
from contract import (
    EXPERIMENT,
    EXPERIMENT_DIR,
    REPOSITORY_ROOT,
    ContractError,
    canonical_json_bytes,
    capture_digest_record,
    digest_record,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_json,
    set_deterministic_process_environment,
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


ADMITTED_RUN_MARKER_PREFIX = "- **Admitted run:**"
ADMITTED_RUN_MARKER_RE = re.compile(r"^- \*\*Admitted run:\*\* `([a-z][a-z0-9-]*)`$")
REGISTERED_ANALYSIS_RUN_IDS = frozenset({"run-001", "run-002"})


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_admitted_run_evidence(
    payloads: Iterable[bytes],
    *,
    allowed_run_ids: frozenset[str] = REGISTERED_ANALYSIS_RUN_IDS,
) -> str:
    """Return the sole exact admitted-run marker across approval artifacts."""

    markers: list[str] = []
    for payload in payloads:
        try:
            text = payload.decode("utf-8")
        except UnicodeError as exc:
            raise ContractError("immutable run-review evidence is not UTF-8") from exc
        for line in text.splitlines():
            if not line.startswith(ADMITTED_RUN_MARKER_PREFIX):
                continue
            match = ADMITTED_RUN_MARKER_RE.fullmatch(line)
            if match is None:
                raise ContractError("immutable run-review admitted-run marker is malformed")
            marker = match.group(1)
            if marker not in allowed_run_ids:
                raise ContractError("immutable run-review admitted-run marker names an unregistered run")
            markers.append(marker)
    if not markers:
        raise ContractError("immutable run-review evidence lacks an admitted-run marker")
    if len(markers) != 1:
        if len(set(markers)) == 1:
            raise ContractError("immutable run-review admitted-run marker is duplicated")
        raise ContractError("immutable run-review admitted-run markers conflict")
    return markers[0]


def analysis_admission(
    event_id: str,
    run_id: str,
    *,
    workflow_path: Path = EXPERIMENT_DIR / "workflow.jsonl",
    graph_path: Path = REPOSITORY_ROOT / "research/workflow.graph.v1.json",
    repository_root: Path = REPOSITORY_ROOT,
    workflow_cli_path: Path = REPOSITORY_ROOT / "scripts/research-workflow.mjs",
    allowed_run_ids: frozenset[str] = REGISTERED_ANALYSIS_RUN_IDS,
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
    evidence_payloads: list[bytes] = []
    for artifact in artifacts:
        snapshot_path = artifact.get("snapshot_path")
        if isinstance(snapshot_path, str):
            payload = verified_ledger.snapshot_bytes.get(snapshot_path)
            if payload is None:
                raise ContractError("immutable run-review approval artifact bytes are missing")
            evidence_payloads.append(payload)
    admitted_run_id = parse_admitted_run_evidence(
        evidence_payloads,
        allowed_run_ids=allowed_run_ids,
    )
    if admitted_run_id != run_id:
        raise ContractError("immutable run-review admitted run differs from the requested run ID")
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
    result_schema_valid = validate_json_schema(
        provisional,
        EXPERIMENT_DIR / "schemas/analysis-result.schema.json",
    )
    flags["schema"] = bool(upstream_schema_valid and result_schema_valid)
    result = assemble(flags)
    validate_json_schema(result, EXPERIMENT_DIR / "schemas/analysis-result.schema.json")
    return result


def _focal_matches(frame: Mapping[str, Any], focal: Mapping[str, Any], index: int) -> bool:
    if set(frame) != set(focal):
        return False
    for key, value in frame.items():
        expected = value[index] if isinstance(value, list) else value
        if focal[key] != expected:
            return False
    return True


def _captured_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"captured {label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ContractError(f"captured {label} is not a JSON object")
    return value


def _source_prefix(run_id: str, *, enforce_frozen_inputs: bool) -> tuple[str, str]:
    if enforce_frozen_inputs:
        if run_id not in {"run-001", "run-002"}:
            raise ContractError("production analysis source run ID is not registered")
        return f"research/{EXPERIMENT}/runs/{run_id}", "canonical-production"
    if run_id != "toy-run":
        raise ContractError("setup validation accepts only the visibly synthetic toy-run")
    return "setup-toy/toy-run", "setup-toy"


def _capture_validated_source_bundle(
    source_run: Mapping[str, Any],
    primitive: Mapping[str, Any],
    *,
    repository_root: Path,
    enforce_frozen_inputs: bool,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Validate a private replay of one exact captured six-file run bundle."""

    if set(source_run) != {"run_id", "manifest", "sample", "completion"}:
        raise ContractError("analysis source-run provenance fields mismatch")
    run_id = source_run["run_id"]
    if not isinstance(run_id, str):
        raise ContractError("analysis source run ID is invalid")
    prefix, expected_purpose = _source_prefix(run_id, enforce_frozen_inputs=enforce_frozen_inputs)
    expected_paths = {
        "manifest": f"{prefix}/{MANIFEST_NAME}",
        "sample": f"{prefix}/{RAW_NAME}",
        "completion": f"{prefix}/{COMPLETION_NAME}",
    }
    captured: dict[str, bytes] = {}
    for label, expected_path in expected_paths.items():
        record = source_run[label]
        if not isinstance(record, dict) or record.get("path") != expected_path:
            raise ContractError(f"analysis source {label} path mismatch")
        _path, captured[label] = capture_digest_record(record, repository_root=repository_root)

    manifest = _captured_json(captured["manifest"], "run manifest")
    completion = _captured_json(captured["completion"], "completion marker")
    validate_json_schema(manifest, EXPERIMENT_DIR / "schemas/run-manifest.schema.json")
    validate_json_schema(completion, EXPERIMENT_DIR / "schemas/completion.schema.json")
    if manifest.get("run_id") != run_id or completion.get("run_id") != run_id:
        raise ContractError("source run ID does not match manifest and completion identity")
    if manifest.get("purpose") != expected_purpose:
        raise ContractError("source run purpose does not match the validation boundary")
    if completion.get("run_manifest") != source_run["manifest"]:
        raise ContractError("completion marker does not identify the source run manifest")
    manifest_sample = manifest.get("sample", {})
    if not isinstance(manifest_sample, dict) or {
        key: manifest_sample.get(key) for key in ("path", "bytes", "sha256")
    } != source_run["sample"]:
        raise ContractError("run manifest does not identify the source raw sample")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ContractError("run manifest artifact inventory is invalid")
    artifact_by_name: dict[str, Mapping[str, Any]] = {}
    for record in artifacts:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ContractError("run manifest artifact record is invalid")
        name = Path(record["path"]).name
        if name in artifact_by_name:
            raise ContractError("run manifest artifact name is duplicated")
        artifact_by_name[name] = record
    if set(artifact_by_name) != {RAW_NAME, STDOUT_NAME, STDERR_NAME}:
        raise ContractError("run manifest artifact inventory is incomplete")
    if artifact_by_name[RAW_NAME] != source_run["sample"]:
        raise ContractError("run manifest raw artifact differs from source provenance")

    bundle_payloads = {
        MANIFEST_NAME: captured["manifest"],
        RAW_NAME: captured["sample"],
        COMPLETION_NAME: captured["completion"],
    }
    for name in (STDOUT_NAME, STDERR_NAME):
        record = artifact_by_name[name]
        if record.get("path") != f"{prefix}/{name}":
            raise ContractError(f"run artifact path mismatch: {name}")
        _path, bundle_payloads[name] = capture_digest_record(record, repository_root=repository_root)
    checksums_record = completion.get("checksums")
    if not isinstance(checksums_record, dict) or checksums_record.get("path") != f"{prefix}/{CHECKSUMS_NAME}":
        raise ContractError("completion checksum path mismatch")
    _path, bundle_payloads[CHECKSUMS_NAME] = capture_digest_record(
        checksums_record,
        repository_root=repository_root,
    )

    try:
        sample = np.load(io.BytesIO(captured["sample"]), allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ContractError("captured raw sample is not a valid non-pickle NumPy array") from exc
    try:
        spec = RunSpec(
            experiment=manifest["experiment"],
            purpose=manifest["purpose"],
            run_id=manifest["run_id"],
            command=manifest["command"],
            seed=manifest["rng"]["seed"],
            draw_count=manifest["rng"]["draw_count"],
            scale_s=float(primitive["tau0_s"]),
            lineage=manifest["lineage"],
            authorization=manifest["authorization"],
            platform=manifest["platform"],
            path_prefix=prefix,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("captured run manifest cannot reconstruct its run specification") from exc
    with tempfile.TemporaryDirectory(prefix="muon-setup-run-validation-") as temporary:
        staged_run = Path(temporary) / "captured-run"
        staged_run.mkdir()
        for name, payload in bundle_payloads.items():
            (staged_run / name).write_bytes(payload)
        run_integrity = validate_run_bundle(staged_run, spec)
    return sample, run_integrity


def _validate_result_provenance(
    result: Mapping[str, Any],
    *,
    repository_root: Path,
) -> bool:
    validation_experiment_dir = repository_root / "research" / EXPERIMENT
    source_records = [result["source_run"][name] for name in ("manifest", "sample", "completion")]
    provenance = result["provenance"]
    expected_named = (
        (provenance["generator"], f"research/{EXPERIMENT}/src/analyze.py"),
        (provenance["schema"], f"research/{EXPERIMENT}/schemas/analysis-result.schema.json"),
        (provenance["inputs"][3], f"research/{EXPERIMENT}/inputs.json"),
        (provenance["inputs"][4], f"research/{EXPERIMENT}/constants.json"),
    )
    for record, expected_path in expected_named:
        if not isinstance(record, dict) or record.get("path") != expected_path:
            raise ContractError("analysis provenance path mismatch")
        capture_digest_record(record, repository_root=repository_root)
    if provenance["inputs"] != [*source_records, provenance["inputs"][3], provenance["inputs"][4]]:
        raise ContractError("analysis input provenance does not bind the source run first")
    if (validation_experiment_dir / "src/analyze.py").is_symlink():
        raise ContractError("analysis generator provenance target is linked")
    return True


def _validation_check_context(
    result: Mapping[str, Any],
    sample: np.ndarray,
    *,
    enforce_frozen_inputs: bool,
) -> dict[str, Any]:
    if enforce_frozen_inputs:
        inputs = load_and_validate_inputs()
        return {
            "focal_index": inputs["production"]["focal_index"],
            "expected_grid_size": 201,
            "expected_draw_count": inputs["production"]["rng"]["draw_count"],
            "frame_relative_tolerance": inputs["checks"]["frame_relative_tolerance"],
            "standard_error_multiplier": inputs["checks"]["focal_monte_carlo_standard_error_multiplier"],
            "maximum_grid_discrepancy": inputs["checks"]["maximum_grid_absolute_discrepancy"],
        }
    if len(result["grid_m"]) != 3 or result["focal"]["index"] != 1 or sample.shape != (16,):
        raise ContractError("setup result differs from the registered three-point, 16-draw toy context")
    return {
        "focal_index": 1,
        "expected_grid_size": 3,
        "expected_draw_count": 16,
        "frame_relative_tolerance": 1e-12,
        "standard_error_multiplier": 4.0,
        "maximum_grid_discrepancy": 0.5,
    }


def validate_analysis_result(
    result: Mapping[str, Any],
    *,
    enforce_frozen_inputs: bool = True,
    repository_root: Path = REPOSITORY_ROOT,
) -> bool:
    """Reconstruct and validate the complete result, source, and admission contract."""

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
    provenance_valid = _validate_result_provenance(result, repository_root=repository_root)
    sample, run_integrity = _capture_validated_source_bundle(
        result["source_run"],
        primitive,
        repository_root=repository_root,
        enforce_frozen_inputs=enforce_frozen_inputs,
    )
    expected_counts, expected_empirical = empirical_survival(sample, expected_muon["elapsed_time_s"])
    counts = np.asarray(result["empirical"]["counts"], dtype=np.int64)
    empirical = np.asarray(result["empirical"]["survival_probability"], dtype=np.float64)
    if not np.array_equal(counts, expected_counts) or not np.array_equal(empirical, expected_empirical):
        raise ContractError("analysis empirical arrays are not derived from the captured raw sample")
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
    expected_admission = analysis_admission(
        result["analysis_admission"]["event_id"],
        result["source_run"]["run_id"],
        workflow_path=repository_root / "research" / EXPERIMENT / "workflow.jsonl",
        graph_path=repository_root / "research/workflow.graph.v1.json",
        repository_root=repository_root,
        workflow_cli_path=repository_root / "scripts/research-workflow.mjs",
        allowed_run_ids=(REGISTERED_ANALYSIS_RUN_IDS if enforce_frozen_inputs else frozenset({"toy-run"})),
    )
    if result["analysis_admission"] != expected_admission:
        raise ContractError("analysis admission does not match the replayed run-review approval")
    integrity_flags = {
        "schema": run_integrity.get("schema_valid") is True,
        "manifest": run_integrity.get("manifest_valid") is True,
        "provenance": bool(run_integrity.get("provenance_valid") is True and provenance_valid),
        "hashes": run_integrity.get("hashes_valid") is True,
        "run_bundle": run_integrity.get("valid") is True,
        "run_admission": True,
    }
    check_context = _validation_check_context(
        result,
        sample,
        enforce_frozen_inputs=enforce_frozen_inputs,
    )
    expected_checks = evaluate_checks(
        expected_detector,
        expected_muon,
        expected_counterfactual,
        grid_array,
        primitive,
        expected_counts,
        expected_empirical,
        sample,
        integrity_flags=integrity_flags,
        **check_context,
    )
    if result["checks"] != expected_checks:
        raise ContractError("analysis checks, details, or diagnostics do not match independent recomputation")
    return True


def write_or_check_result(
    path: Path,
    result: Mapping[str, Any],
    *,
    check: bool,
    enforce_frozen_inputs: bool = True,
    repository_root: Path = REPOSITORY_ROOT,
) -> None:
    validate_analysis_result(
        result,
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


def registered_analysis_spec(
    run_id: str,
    run_review_event: str,
    generated_at: str,
    *,
    runs_dir: Path = EXPERIMENT_DIR / "runs",
    repository_root: Path = REPOSITORY_ROOT,
    workflow_path: Path = EXPERIMENT_DIR / "workflow.jsonl",
    graph_path: Path = REPOSITORY_ROOT / "research/workflow.graph.v1.json",
    workflow_cli_path: Path = REPOSITORY_ROOT / "scripts/research-workflow.mjs",
    run_spec_builder: Callable[..., RunSpec] = build_spec,
    inputs_loader: Callable[[], Mapping[str, Any]] = load_and_validate_inputs,
    constants_loader: Callable[[], Mapping[str, Any]] = load_and_validate_constants,
) -> tuple[np.ndarray, AnalysisSpec]:
    """Load one registered run; injectable paths keep setup tests nonproduction."""

    if run_id not in REGISTERED_ANALYSIS_RUN_IDS:
        raise ContractError("analysis run ID is not registered")
    run_dir = runs_dir / run_id
    manifest = load_json(run_dir / "run-manifest.json")
    run_spec = run_spec_builder(run_id, recorded_authorization=manifest.get("authorization"))
    integrity = validate_run_bundle(run_dir, run_spec)
    admission = analysis_admission(
        run_review_event,
        run_id,
        workflow_path=workflow_path,
        graph_path=graph_path,
        repository_root=repository_root,
        workflow_cli_path=workflow_cli_path,
    )
    inputs = inputs_loader()
    constants = constants_loader()["constants"]
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

    def source_record(path: Path) -> dict[str, Any]:
        try:
            relative = path.resolve(strict=True).relative_to(repository_root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise ContractError("analysis source artifact is outside the selected repository") from exc
        return digest_record(path, public_path=relative.as_posix())

    source_run = {
        "run_id": run_id,
        "manifest": source_record(run_dir / "run-manifest.json"),
        "sample": source_record(run_dir / RAW_NAME),
        "completion": source_record(run_dir / "COMPLETE.json"),
    }
    integrity_flags = derive_integrity_flags(
        integrity,
        source_run,
        admission,
        repository_root=repository_root,
    )
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


def main(
    argv: list[str] | None = None,
    *,
    output_path: Path = EXPERIMENT_DIR / "results/summary.json",
    spec_loader: Callable[[str, str, str], tuple[np.ndarray, AnalysisSpec]] = registered_analysis_spec,
    result_builder: Callable[[np.ndarray, AnalysisSpec], dict[str, Any]] = build_analysis_result,
    result_writer: Callable[..., None] = write_or_check_result,
    existing_loader: Callable[[Path], Any] = load_json,
    now: Callable[[], str] = utc_now,
    environment_setter: Callable[[], None] = set_deterministic_process_environment,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-review-event", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    environment_setter()
    if args.check:
        existing = existing_loader(output_path)
        generated_at = existing.get("generated_at")
        if not isinstance(generated_at, str):
            raise ContractError("canonical result lacks its frozen generation timestamp")
    else:
        generated_at = now()
    sample, spec = spec_loader(args.run_id, args.run_review_event, generated_at)
    result = result_builder(sample, spec)
    result_writer(output_path, result, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
