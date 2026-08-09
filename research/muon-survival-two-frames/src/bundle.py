"""Immutable new-run creation and byte-level completion verification."""

from __future__ import annotations

import os
import re
import sys
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from contract import (
    ContractError,
    EXPERIMENT_DIR,
    digest_record,
    load_json,
    SHA256_RE,
    sha256_file,
    validate_json_schema,
    write_bytes_exclusive,
    write_json_exclusive,
)


SAFE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
RAW_NAME = "proper_lifetimes_s.npy"
STDOUT_NAME = "stdout.log"
STDERR_NAME = "stderr.log"
MANIFEST_NAME = "run-manifest.json"
CHECKSUMS_NAME = "checksums.sha256"
COMPLETION_NAME = "COMPLETE.json"
COMPLETE_FILES = {
    RAW_NAME,
    STDOUT_NAME,
    STDERR_NAME,
    MANIFEST_NAME,
    CHECKSUMS_NAME,
    COMPLETION_NAME,
}


@dataclass(frozen=True)
class RunSpec:
    experiment: str
    purpose: str
    run_id: str
    command: str
    seed: int
    draw_count: int
    scale_s: float
    lineage: Mapping[str, Mapping[str, Any]]
    authorization: Mapping[str, Any]
    platform: Mapping[str, str]
    path_prefix: str


def generate_lifetimes(spec: RunSpec) -> np.ndarray:
    """Perform the one registered draw call, or a strictly bounded setup toy."""

    if spec.purpose == "setup-toy":
        if spec.seed != 0 or not 1 <= spec.draw_count <= 16:
            raise ContractError("setup toy generation is limited to PCG64 seed 0 and at most 16 draws")
    elif spec.purpose == "canonical-production":
        if spec.seed != 20260808 or spec.draw_count != 100000:
            raise ContractError("production RNG parameters differ from the frozen protocol")
    else:
        raise ContractError("unknown run purpose")
    if not np.isfinite(spec.scale_s) or spec.scale_s <= 0.0:
        raise ContractError("exponential scale must be finite and positive")
    generator = np.random.Generator(np.random.PCG64(spec.seed))
    sample = generator.exponential(scale=spec.scale_s, size=spec.draw_count)
    if sample.dtype != np.dtype("float64") or sample.shape != (spec.draw_count,):
        raise ContractError("NumPy returned an unexpected sample dtype or shape")
    if not bool(np.all(np.isfinite(sample))) or bool(np.any(sample < 0.0)):
        raise ContractError("proper-lifetime sample contains an invalid value")
    return sample


def create_new_run_directory(parent: Path, run_id: str) -> Path:
    """Claim a new namespace once; an existing or linked path is never reused."""

    if SAFE_ID_RE.fullmatch(run_id) is None:
        raise ContractError("unsafe run ID")
    if parent.exists() and (not parent.is_dir() or parent.is_symlink()):
        raise ContractError("runs parent must be a real directory")
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink():
        raise ContractError("runs parent must not be a symlink")
    run_dir = parent / run_id
    if run_dir.exists() or run_dir.is_symlink():
        raise ContractError("run namespace already exists; resume and overwrite are forbidden")
    try:
        run_dir.mkdir(mode=0o755)
    except FileExistsError as exc:
        raise ContractError("run namespace was claimed concurrently") from exc
    return run_dir


def _artifact(run_dir: Path, name: str, path_prefix: str) -> dict[str, Any]:
    return digest_record(run_dir / name, public_path=f"{path_prefix}/{name}")


def save_array_exclusive(path: Path, values: np.ndarray) -> None:
    """Create the final raw path with O_EXCL; interrupted bytes stay quarantined."""

    try:
        with path.open("xb") as handle:
            np.save(handle, values, allow_pickle=False)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ContractError("refusing to overwrite the raw sample") from exc


@contextmanager
def capture_process_streams(run_dir: Path):
    """Redirect the process file descriptors into new, exclusive run logs."""

    stdout_path = run_dir / STDOUT_NAME
    stderr_path = run_dir / STDERR_NAME
    try:
        stdout_handle = stdout_path.open("xb", buffering=0)
    except FileExistsError as exc:
        raise ContractError("refusing to overwrite stdout.log") from exc
    try:
        stderr_handle = stderr_path.open("xb", buffering=0)
    except FileExistsError as exc:
        stdout_handle.close()
        raise ContractError("refusing to overwrite stderr.log") from exc
    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(stdout_handle.fileno(), 1)
        os.dup2(stderr_handle.fileno(), 2)
        yield
        sys.stdout.flush()
        sys.stderr.flush()
        os.fsync(stdout_handle.fileno())
        os.fsync(stderr_handle.fileno())
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os.dup2(saved_stdout, 1)
            os.dup2(saved_stderr, 2)
            os.close(saved_stdout)
            os.close(saved_stderr)
            stdout_handle.close()
            stderr_handle.close()


def seal_run_bundle(
    run_dir: Path,
    sample: np.ndarray,
    spec: RunSpec,
    *,
    started_at: str,
    completed_at: str | Callable[[], str],
) -> dict[str, Any]:
    """Write a complete namespace once, placing COMPLETE.json last."""

    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ContractError("run namespace must be a real directory")
    if {entry.name for entry in run_dir.iterdir()} != {RAW_NAME, STDOUT_NAME, STDERR_NAME}:
        raise ContractError("pre-seal run namespace must contain exactly raw sample and process streams")
    if sample.dtype != np.dtype("float64") or sample.shape != (spec.draw_count,):
        raise ContractError("sample does not match its run specification")
    if not bool(np.all(np.isfinite(sample))) or bool(np.any(sample < 0.0)):
        raise ContractError("sample contains nonfinite or negative lifetimes")

    raw_record = _artifact(run_dir, RAW_NAME, spec.path_prefix)
    stdout_record = _artifact(run_dir, STDOUT_NAME, spec.path_prefix)
    stderr_record = _artifact(run_dir, STDERR_NAME, spec.path_prefix)
    manifest = {
        "schema_version": 1,
        "experiment": spec.experiment,
        "purpose": spec.purpose,
        "run_id": spec.run_id,
        "status": "complete",
        "started_at": started_at,
        "completed_at": completed_at,
        "command": spec.command,
        "lineage": dict(spec.lineage),
        "authorization": dict(spec.authorization),
        "platform": dict(spec.platform),
        "rng": {
            "library": "numpy",
            "bit_generator": "PCG64",
            "seed": spec.seed,
            "draw_count": spec.draw_count,
            "operation": f"Generator.exponential(scale=tau0_s, size={spec.draw_count})",
            "dtype": "float64",
            "draw_order": "retained; not sorted",
        },
        "sample": {
            **raw_record,
            "shape": [spec.draw_count],
            "dtype": "float64",
            "unit": "s",
            "finite": True,
            "nonnegative": True,
        },
        "artifacts": [raw_record, stdout_record, stderr_record],
    }
    write_json_exclusive(run_dir / MANIFEST_NAME, manifest)
    manifest_record = _artifact(run_dir, MANIFEST_NAME, spec.path_prefix)

    checksum_records = [raw_record, stdout_record, stderr_record, manifest_record]
    checksum_payload = "".join(
        f"{entry['sha256']}  {Path(entry['path']).name}\n" for entry in checksum_records
    ).encode("ascii")
    write_bytes_exclusive(run_dir / CHECKSUMS_NAME, checksum_payload)
    checksums_record = _artifact(run_dir, CHECKSUMS_NAME, spec.path_prefix)

    completion = {
        "schema_version": 1,
        "experiment": spec.experiment,
        "run_id": spec.run_id,
        "status": "complete",
        "completed_at": completed_at,
        "exit_status": 0,
        "run_manifest": manifest_record,
        "checksums": checksums_record,
    }
    write_json_exclusive(run_dir / COMPLETION_NAME, completion)
    return completion


class RunExecutionError(RuntimeError):
    """Signals a failure already recorded in the run's real stderr stream."""


def execute_and_seal(
    run_dir: Path,
    spec: RunSpec,
    *,
    started_at: str,
    completed_at: str,
    draw=generate_lifetimes,
) -> dict[str, Any]:
    """Capture real process streams, create raw bytes exclusively, then seal."""

    failure: BaseException | None = None
    completion: dict[str, Any] | None = None
    with capture_process_streams(run_dir):
        try:
            print(f"run_id={spec.run_id}")
            print(f"authorization={spec.authorization.get('kind', 'unknown')}")
            print("scientific_values_printed=false")
            sample = draw(spec)
            save_array_exclusive(run_dir / RAW_NAME, sample)
            print("raw_sample_written=true")
            print("sealing_requested=true")
            sys.stdout.flush()
            sys.stderr.flush()
            completion_time = completed_at() if callable(completed_at) else completed_at
            completion = seal_run_bundle(
                run_dir,
                sample,
                spec,
                started_at=started_at,
                completed_at=completion_time,
            )
        except BaseException as exc:
            failure = exc
            print("status=incomplete", file=sys.stderr)
            print("namespace_must_be_quarantined=true", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    if failure is not None:
        raise RunExecutionError("run failed; inspect the sealed process streams in the incomplete namespace") from None
    if completion is None:
        raise RunExecutionError("run did not produce a completion marker")
    return completion


def _parse_checksums(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ContractError("checksums file is unreadable") from exc
    parsed: dict[str, str] = {}
    for line in lines:
        pieces = line.split("  ", 1)
        if len(pieces) != 2 or SHA256_RE.fullmatch(pieces[0]) is None:
            raise ContractError("malformed checksums line")
        name = pieces[1]
        if name in parsed or name not in {RAW_NAME, STDOUT_NAME, STDERR_NAME, MANIFEST_NAME}:
            raise ContractError("checksums file has an unexpected or duplicate path")
        parsed[name] = pieces[0]
    if set(parsed) != {RAW_NAME, STDOUT_NAME, STDERR_NAME, MANIFEST_NAME}:
        raise ContractError("checksums file is incomplete")
    return parsed


def validate_run_bundle(run_dir: Path, spec: RunSpec) -> dict[str, Any]:
    """Validate schema-level fields, completeness, hashes, and raw-array integrity."""

    if not run_dir.is_dir() or run_dir.is_symlink():
        raise ContractError("run namespace is missing or linked")
    entries = {entry.name for entry in run_dir.iterdir()}
    if entries != COMPLETE_FILES:
        raise ContractError("complete run namespace has missing or unexpected files")
    for name in COMPLETE_FILES:
        path = run_dir / name
        if not path.is_file() or path.is_symlink():
            raise ContractError(f"run artifact is missing, non-regular, or linked: {name}")

    manifest = load_json(run_dir / MANIFEST_NAME)
    completion = load_json(run_dir / COMPLETION_NAME)
    manifest_schema_valid = validate_json_schema(
        manifest,
        EXPERIMENT_DIR / "schemas/run-manifest.schema.json",
    )
    completion_schema_valid = validate_json_schema(
        completion,
        EXPERIMENT_DIR / "schemas/completion.schema.json",
    )
    expected_manifest_keys = {
        "schema_version", "experiment", "purpose", "run_id", "status",
        "started_at", "completed_at", "command", "lineage", "authorization", "platform",
        "rng", "sample", "artifacts",
    }
    if set(manifest) != expected_manifest_keys:
        raise ContractError("run manifest fields do not match schema contract")
    if manifest["schema_version"] != 1 or manifest["experiment"] != spec.experiment:
        raise ContractError("run manifest identity mismatch")
    if manifest["purpose"] != spec.purpose or manifest["run_id"] != spec.run_id:
        raise ContractError("run manifest purpose or ID mismatch")
    if manifest["status"] != "complete" or manifest["command"] != spec.command:
        raise ContractError("run manifest state or command mismatch")
    if manifest["lineage"] != dict(spec.lineage):
        raise ContractError("run lineage mismatch")
    if manifest["authorization"] != dict(spec.authorization):
        raise ContractError("run authorization lineage mismatch")
    platform_record = manifest["platform"]
    if spec.purpose == "setup-toy":
        if platform_record != dict(spec.platform):
            raise ContractError("toy run platform record mismatch")
    else:
        expected_platform = {
            "os": "Linux",
            "architecture": "x86_64",
            "python_implementation": "CPython",
            "python_version": "3.12.3",
            "numpy_version": "2.5.1",
            "matplotlib_version": "3.11.1",
            "pip_version": "26.2.1",
            "node_version": "24.18.0",
        }
        if not isinstance(platform_record, dict) or any(platform_record.get(key) != value for key, value in expected_platform.items()):
            raise ContractError("production platform record violates the locked environment")
        if not isinstance(platform_record.get("release"), str) or not platform_record["release"]:
            raise ContractError("production kernel release is missing")
    rng = manifest["rng"]
    if rng.get("library") != "numpy" or rng.get("bit_generator") != "PCG64":
        raise ContractError("run RNG implementation mismatch")
    if rng.get("seed") != spec.seed or rng.get("draw_count") != spec.draw_count or rng.get("dtype") != "float64":
        raise ContractError("run RNG parameters mismatch")

    parsed = _parse_checksums(run_dir / CHECKSUMS_NAME)
    for name, expected_digest in parsed.items():
        if sha256_file(run_dir / name) != expected_digest:
            raise ContractError(f"artifact checksum mismatch: {name}")
    manifest_record = _artifact(run_dir, MANIFEST_NAME, spec.path_prefix)
    checksums_record = _artifact(run_dir, CHECKSUMS_NAME, spec.path_prefix)
    expected_completion_keys = {
        "schema_version", "experiment", "run_id", "status", "completed_at",
        "exit_status", "run_manifest", "checksums",
    }
    if set(completion) != expected_completion_keys:
        raise ContractError("completion fields do not match schema contract")
    if (
        completion["schema_version"] != 1
        or completion["experiment"] != spec.experiment
        or completion["run_id"] != spec.run_id
        or completion["status"] != "complete"
        or completion["exit_status"] != 0
        or completion["completed_at"] != manifest["completed_at"]
        or completion["run_manifest"] != manifest_record
        or completion["checksums"] != checksums_record
    ):
        raise ContractError("completion marker does not bind the manifest and checksums")

    raw_record = _artifact(run_dir, RAW_NAME, spec.path_prefix)
    if manifest["sample"] != {
        **raw_record,
        "shape": [spec.draw_count],
        "dtype": "float64",
        "unit": "s",
        "finite": True,
        "nonnegative": True,
    }:
        raise ContractError("sample metadata mismatch")
    expected_artifacts = [
        raw_record,
        _artifact(run_dir, STDOUT_NAME, spec.path_prefix),
        _artifact(run_dir, STDERR_NAME, spec.path_prefix),
    ]
    if manifest["artifacts"] != expected_artifacts:
        raise ContractError("manifest artifact inventory mismatch")

    try:
        sample = np.load(run_dir / RAW_NAME, allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ContractError("raw sample is not a valid non-pickle NumPy array") from exc
    if sample.dtype != np.dtype("float64") or sample.shape != (spec.draw_count,):
        raise ContractError("raw sample dtype or shape mismatch")
    if not bool(np.all(np.isfinite(sample))) or bool(np.any(sample < 0.0)):
        raise ContractError("raw sample has nonfinite or negative values")
    return {
        "run_id": spec.run_id,
        "file_count": len(COMPLETE_FILES),
        "sample_shape": list(sample.shape),
        "sample_dtype": str(sample.dtype),
        "manifest_sha256": sha256_file(run_dir / MANIFEST_NAME),
        "completion_sha256": sha256_file(run_dir / COMPLETION_NAME),
        "checksums_sha256": sha256_file(run_dir / CHECKSUMS_NAME),
        "schema_valid": bool(manifest_schema_valid and completion_schema_valid),
        "manifest_valid": manifest["artifacts"] == expected_artifacts,
        "provenance_valid": manifest["lineage"] == dict(spec.lineage) and manifest["authorization"] == dict(spec.authorization),
        "hashes_valid": all(sha256_file(run_dir / name) == digest for name, digest in parsed.items()),
        "valid": True,
    }
