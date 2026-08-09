#!/usr/bin/env python3
"""Reconstruct the admitted sample into the canonical Understanding result."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def _analysis_admission(event_id: str, run_id: str) -> dict[str, Any]:
    lines = (EXPERIMENT_DIR / "workflow.jsonl").read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ContractError("workflow ledger is empty")
    event = json.loads(lines[-1])
    if (
        event.get("event_id") != event_id
        or event.get("type") != "review"
        or event.get("from") != "run_review"
        or event.get("to") != "analyze"
        or event.get("decision") != "approve"
    ):
        raise ContractError("analysis requires the current recorded run_review approval")
    artifacts = event.get("artifacts", [])
    receipt_mentions_run = False
    for artifact in artifacts:
        source_path = artifact.get("source_path")
        if isinstance(source_path, str):
            candidate = REPOSITORY_ROOT / source_path
            if candidate.is_file() and run_id in candidate.read_text(encoding="utf-8"):
                receipt_mentions_run = True
    if not receipt_mentions_run:
        raise ContractError("run-review evidence does not name the requested run ID")
    return {
        "event_id": event_id,
        "sequence": event["sequence"],
        "decision": "approve",
        "event_sha256": hashlib.sha256(f"{lines[-1]}\n".encode("utf-8")).hexdigest(),
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
        integrity_flags=spec.integrity_flags,
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
        "generator": "research/muon-survival-two-frames/src/analyze.py",
        "generator_sha256": sha256_file(EXPERIMENT_DIR / "src/analyze.py"),
        "inputs": [dict(spec.source_run), digest_record(EXPERIMENT_DIR / "inputs.json"), digest_record(EXPERIMENT_DIR / "constants.json")],
    }
    return result


def write_or_check_result(path: Path, result: Mapping[str, Any], *, check: bool) -> None:
    expected = canonical_json_bytes(result)
    if check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != expected:
            raise ContractError("canonical result is missing or stale")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_bytes_exclusive(path, expected)


def registered_analysis_spec(run_id: str, run_review_event: str, generated_at: str) -> tuple[np.ndarray, AnalysisSpec]:
    run_dir = EXPERIMENT_DIR / "runs" / run_id
    manifest = load_json(run_dir / "run-manifest.json")
    run_spec = build_spec(run_id, recorded_authorization=manifest.get("authorization"))
    integrity = validate_run_bundle(run_dir, run_spec)
    admission = _analysis_admission(run_review_event, run_id)
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
    checks = inputs["checks"]
    return sample, AnalysisSpec(
        paths_m=paths,
        primitives=primitives,
        focal_index=inputs["production"]["focal_index"],
        frame_relative_tolerance=checks["frame_relative_tolerance"],
        standard_error_multiplier=checks["focal_monte_carlo_standard_error_multiplier"],
        maximum_grid_discrepancy=checks["maximum_grid_absolute_discrepancy"],
        source_run=source_run,
        integrity_flags={"schema": True, "manifest": True, "provenance": True, "hashes": True, "run_bundle": bool(integrity["valid"]), "run_admission": True},
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
