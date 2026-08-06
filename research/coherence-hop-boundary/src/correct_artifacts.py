#!/usr/bin/env python3
"""Apply the review corrections to canonical experiment artifacts.

The transformations are deterministic and deliberately do not manufacture
missing coefficient phases.  Legacy production data remain scoped to the
mean magnitude of per-trajectory coherence; corrective convergence data are
compacted without removing any registered gate input.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen


VOLATILE_KEYS = {"runtime_seconds", "generated_at", "generated_at_utc"}
LOCAL_MAGNITUDE_CONTRACT = {
    "stored_field": "coherence_amplitude",
    "definition": "mean_over_trajectories_of_2_abs(c_minus_conjugate_times_c_plus)",
    "allowed_interpretation": "mean_single_trajectory_coherence_magnitude",
    "excluded_interpretations": [
        "phase_sensitive_ensemble_off_diagonal_density_matrix",
        "pump_generated_optical_coherence",
    ],
    "post_hoc_phase_sensitive_recovery_possible": False,
    "reason": "the archived production runs do not retain coefficient phases",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return raw, value


def _validate_source_url(url: str) -> None:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "raw.githubusercontent.com"
        or not parsed.path.startswith("/noprofits-org/pvjohnston.com/")
    ):
        raise ValueError(
            "artifact source URL must be an HTTPS raw.githubusercontent.com "
            "path for noprofits-org/pvjohnston.com"
        )


def _decode_source(raw: bytes, label: str) -> dict[str, Any]:
    payload = gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{label}: top-level JSON value must be an object")
    return value


def _strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_volatile(item)
            for key, item in value.items()
            if key not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [_strip_volatile(item) for item in value]
    return value


def _correct_event_records(records: list[dict[str, Any]]) -> dict[str, int]:
    """Reclassify accepted repeats and true returns from event order."""

    initial_state: dict[int, int] = {}
    accepted_count: defaultdict[int, int] = defaultdict(int)
    accepted_repeat = 0
    accepted_recrossing = 0
    for event in records:
        trajectory_id = int(event["trajectory_id"])
        initial_state.setdefault(trajectory_id, int(event["from_state"]))
        accepted = str(event.get("outcome")) == "accepted" or bool(
            event.get("accepted", False)
        )
        if not accepted:
            event["recrossing"] = False
            continue
        is_repeat = accepted_count[trajectory_id] > 0
        is_return = is_repeat and int(event["to_state"]) == initial_state[trajectory_id]
        event["accepted_hop_class"] = "repeat" if is_repeat else "first"
        event["accepted_hops_before_event"] = accepted_count[trajectory_id]
        event["recrossing"] = bool(is_return)
        accepted_count[trajectory_id] += 1
        accepted_repeat += int(is_repeat)
        accepted_recrossing += int(is_return)
    return {
        "accepted_repeat": accepted_repeat,
        "accepted_recrossing": accepted_recrossing,
        "accepted_nonrecrossing_repeat": accepted_repeat - accepted_recrossing,
    }


def _correct_run_events(run: dict[str, Any]) -> None:
    for stream in ("full", "axe"):
        records = run.get("events", {}).get(stream)
        summary = run.get("event_summary", {}).get(stream)
        summary_records = summary.get("records") if isinstance(summary, dict) else None
        if records is None and summary_records is None:
            continue
        if records is not None:
            counts = _correct_event_records(records)
        else:
            counts = _correct_event_records(summary_records)
        if summary_records is not None:
            summary_counts = _correct_event_records(summary_records)
            if summary_counts != counts:
                raise ValueError(f"{stream} event copies disagree after correction")
        if isinstance(summary, dict):
            summary.setdefault("counts", {}).update(counts)


def sanitize_legacy_sweep(data: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    corrected = _strip_volatile(data)
    for run in corrected.get("runs", []):
        _correct_run_events(run)
    corrected["schema_version"] = 2
    corrected["artifact_type"] = "legacy_local_magnitude_sweep"
    corrected["scientific_status"] = "descriptive_only_not_corrective_confirmation"
    corrected["coherence_observable_contract"] = LOCAL_MAGNITUDE_CONTRACT
    corrected.setdefault("artifact_correction", {
        "version": 1,
        "source_sha256": source_sha256,
        "operations": [
            "removed_wall_clock_runtimes_and_generation_timestamps",
            "reconstructed_recrossings_from_ordered_event_sequences",
            "declared_local_magnitude_observable_scope",
        ],
    })
    return corrected


def sanitize_legacy_exact(data: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    corrected = _strip_volatile(data)
    corrected["schema_version"] = 2
    corrected["artifact_type"] = "legacy_local_magnitude_exact_grid_audit"
    corrected["scientific_status"] = "secondary_selected_reference"
    corrected["coherence_observable_contract"] = LOCAL_MAGNITUDE_CONTRACT
    corrected.setdefault("artifact_correction", {
        "version": 1,
        "source_sha256": source_sha256,
        "operations": [
            "removed_wall_clock_runtimes_and_generation_timestamps",
            "declared_local_magnitude_observable_scope",
        ],
    })
    return corrected


def sanitize_legacy_convergence(
    data: dict[str, Any], source_sha256: str
) -> dict[str, Any]:
    corrected = _strip_volatile(data)
    for setting in ("coarse", "fine"):
        run = corrected[setting]
        _correct_run_events(run)
        _compact_run(run)
    corrected["schema_version"] = 2
    corrected["artifact_type"] = "legacy_local_magnitude_convergence_gate"
    corrected["scientific_status"] = "failed_gate_fine_selected_without_finer_audit"
    corrected["coherence_observable_contract"] = LOCAL_MAGNITUDE_CONTRACT
    corrected.setdefault("artifact_correction", {
        "version": 1,
        "source_sha256": source_sha256,
        "operations": [
            "removed_wall_clock_runtimes_and_generation_timestamps",
            "removed_redundant_event_records_and_per_trajectory_count_arrays",
            "declared_local_magnitude_observable_scope",
        ],
    })
    return corrected


def _compact_run(run: dict[str, Any]) -> None:
    run.pop("events", None)
    for summary in run.get("event_summary", {}).values():
        for key in (
            "records",
            "per_trajectory_accepted_counts",
            "per_trajectory_frustrated_counts",
            "per_trajectory_proposed_counts",
        ):
            summary.pop(key, None)


def compact_convergence(data: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    corrected = _strip_volatile(data)
    if corrected.get("complete") is not True:
        raise ValueError("refusing to compact an incomplete convergence artifact")
    for setting in ("candidate", "reference"):
        for run in corrected.get(setting, []):
            _compact_run(run)
    corrected.pop("runs", None)
    corrected["schema_version"] = 2
    corrected["artifact_type"] = "corrective_phase_sensitive_convergence_gate"
    corrected["scientific_status"] = (
        "failed_gate_production_blocked" if not corrected["comparison"]["gate"]["passed"]
        else "passed_gate"
    )
    corrected.setdefault("artifact_compaction", {
        "version": 1,
        "source_sha256": source_sha256,
        "removed_redundant_fields": [
            "duplicate_top_level_runs",
            "event_records",
            "per_trajectory_event_count_arrays",
        ],
        "retained_gate_inputs": [
            "observable_time_series",
            "accepted_event_times",
            "event_counts",
            "per_seed_comparisons",
            "paired_seed_intervals",
        ],
    })
    return corrected


def _serialize(value: dict[str, Any], gzip_output: bool) -> bytes:
    payload = (json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False
    ) + "\n").encode("utf-8")
    return gzip.compress(payload, compresslevel=9, mtime=0) if gzip_output else payload


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def transform(
    kind: str,
    input_path: Path | None,
    output_path: Path,
    git_object: str | None = None,
    source_url: str | None = None,
) -> None:
    if sum(source is not None for source in (input_path, git_object, source_url)) != 1:
        raise ValueError("provide exactly one of input_path, git_object, or source_url")
    if git_object is not None:
        raw = subprocess.run(
            ["git", "show", git_object], check=True, capture_output=True
        ).stdout
        value = _decode_source(raw, git_object)
    elif source_url is not None:
        _validate_source_url(source_url)
        with urlopen(source_url, timeout=60) as response:
            raw = response.read()
        value = _decode_source(raw, source_url)
    else:
        assert input_path is not None and git_object is None and source_url is None
        raw, value = _load_bytes(input_path)
    source_sha256 = value.get("artifact_correction", {}).get(
        "source_sha256",
        value.get("artifact_compaction", {}).get("source_sha256", _sha256_bytes(raw)),
    )
    if kind == "legacy-sweep":
        output = sanitize_legacy_sweep(value, source_sha256)
    elif kind == "legacy-exact":
        output = sanitize_legacy_exact(value, source_sha256)
    elif kind == "legacy-convergence":
        output = sanitize_legacy_convergence(value, source_sha256)
    elif kind == "convergence":
        output = compact_convergence(value, source_sha256)
    else:  # pragma: no cover - argparse prevents this branch
        raise ValueError(f"unknown transformation {kind}")
    encoded = _serialize(output, output_path.suffix == ".gz")
    _write_atomic(output_path, encoded)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind",
        choices=("legacy-sweep", "legacy-exact", "legacy-convergence", "convergence"),
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--git-object")
    source.add_argument("--url")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    transform(args.kind, args.input, args.output, args.git_object, args.url)
    print(f"{args.output}: corrected {args.kind} artifact written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
