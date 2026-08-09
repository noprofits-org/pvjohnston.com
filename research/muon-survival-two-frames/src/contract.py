"""Frozen setup contract, deterministic serialization, and provenance checks."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import locale
import os
import platform
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


EXPERIMENT = "muon-survival-two-frames"
EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = EXPERIMENT_DIR.parents[1]
INPUTS_PATH = EXPERIMENT_DIR / "inputs.json"
CONSTANTS_PATH = EXPERIMENT_DIR / "constants.json"
SOURCES_PATH = EXPERIMENT_DIR / "sources.json"
ENVIRONMENT_PATH = EXPERIMENT_DIR / "environment.json"
SETUP_MANIFEST_PATH = EXPERIMENT_DIR / "setup-manifest.json"
WORKFLOW_PATH = EXPERIMENT_DIR / "workflow.jsonl"
WORKFLOW_GRAPH_PATH = REPOSITORY_ROOT / "research/workflow.graph.v1.json"
WORKFLOW_CLI_PATH = REPOSITORY_ROOT / "scripts/research-workflow.mjs"

EXPECTED_PYTHON = "3.12.3"
EXPECTED_NUMPY = "2.5.1"
EXPECTED_MATPLOTLIB = "3.11.1"
EXPECTED_PIP = "26.2.1"
EXPECTED_NODE = "24.18.0"
EXPECTED_WORKFLOW_GRAPH_SHA256 = "e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404"
EXPECTED_WORKFLOW_CLI_SHA256 = "f8b931150fe5c31f574fa6303cd1d9b629ad02b0e05233025288e30275515f2c"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^run-[0-9]{3}$")


class ContractError(RuntimeError):
    """Raised when a frozen input, environment, or artifact contract fails."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON without locale, timezone, key-order, or NaN ambiguity."""

    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read valid JSON at {path.name}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot hash {path.name}") from exc
    return digest.hexdigest()


def relative_repository_path(path: Path) -> str:
    try:
        relative = path.resolve(strict=True).relative_to(REPOSITORY_ROOT.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ContractError("artifact is outside the repository") from exc
    return relative.as_posix()


def digest_record(path: Path, *, public_path: str | None = None) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ContractError(f"expected a regular, non-symlink file: {path.name}")
    return {
        "path": public_path if public_path is not None else relative_repository_path(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_bytes_exclusive(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ContractError(f"refusing to overwrite {path.name}") from exc


def write_json_exclusive(path: Path, value: Any) -> None:
    write_bytes_exclusive(path, canonical_json_bytes(value))


def set_deterministic_process_environment() -> None:
    os.environ["LC_ALL"] = "C"
    os.environ["LANG"] = "C"
    os.environ["TZ"] = "UTC"
    try:
        locale.setlocale(locale.LC_ALL, "C")
    except locale.Error as exc:
        raise ContractError("the required C locale is unavailable") from exc
    if hasattr(time, "tzset"):
        time.tzset()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _validate_digest_link(link: Mapping[str, Any], label: str) -> None:
    _require(set(link) == {"path", "sha256"}, f"{label} digest link has unexpected fields")
    path_text = link["path"]
    digest = link["sha256"]
    _require(isinstance(path_text, str) and path_text, f"{label} path is invalid")
    _require(not Path(path_text).is_absolute() and ".." not in Path(path_text).parts, f"{label} path is not repository-relative")
    _require(isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None, f"{label} SHA-256 is invalid")
    resolved = REPOSITORY_ROOT / path_text
    _require(resolved.is_file() and not resolved.is_symlink(), f"{label} source is missing or a symlink")
    _require(sha256_file(resolved) == digest, f"{label} SHA-256 does not match")


def validate_digest_record(record: Mapping[str, Any], *, repository_root: Path = REPOSITORY_ROOT) -> bool:
    """Resolve a repository-relative byte/size/hash record and fail closed."""

    _require(set(record) == {"path", "bytes", "sha256"}, "artifact digest record fields mismatch")
    path_text = record.get("path")
    _require(isinstance(path_text, str) and path_text, "artifact digest path is invalid")
    relative = Path(path_text)
    _require(not relative.is_absolute() and ".." not in relative.parts, "artifact digest path is not repository-relative")
    _require(isinstance(record.get("bytes"), int) and not isinstance(record.get("bytes"), bool) and record["bytes"] >= 0, "artifact byte count is invalid")
    _require(isinstance(record.get("sha256"), str) and SHA256_RE.fullmatch(record["sha256"]) is not None, "artifact SHA-256 is invalid")
    path = repository_root / relative
    _require(path.is_file() and not path.is_symlink(), "artifact digest target is missing or linked")
    _require(path.stat().st_size == record["bytes"], "artifact byte count does not match")
    _require(sha256_file(path) == record["sha256"], "artifact SHA-256 does not match")
    return True


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def _resolve_local_schema_reference(root: Mapping[str, Any], reference: str) -> Mapping[str, Any]:
    _require(reference.startswith("#/"), "only local JSON Schema references are supported")
    value: Any = root
    for raw_piece in reference[2:].split("/"):
        piece = raw_piece.replace("~1", "/").replace("~0", "~")
        _require(isinstance(value, dict) and piece in value, "JSON Schema reference does not resolve")
        value = value[piece]
    _require(isinstance(value, dict), "JSON Schema reference must resolve to an object")
    return value


def _validate_schema_value(value: Any, rule: Mapping[str, Any], root: Mapping[str, Any], location: str) -> None:
    if "$ref" in rule:
        _validate_schema_value(value, _resolve_local_schema_reference(root, rule["$ref"]), root, location)
        return
    if "const" in rule:
        _require(value == rule["const"], f"schema const mismatch at {location}")
    if "enum" in rule:
        _require(value in rule["enum"], f"schema enum mismatch at {location}")
    expected_type = rule.get("type")
    if expected_type is not None:
        _require(isinstance(expected_type, str) and _schema_type_matches(value, expected_type), f"schema type mismatch at {location}")
    if expected_type == "object":
        required = rule.get("required", [])
        _require(isinstance(required, list) and all(isinstance(key, str) for key in required), f"invalid required list at {location}")
        for key in required:
            _require(key in value, f"schema required field missing at {location}.{key}")
        properties = rule.get("properties", {})
        _require(isinstance(properties, dict), f"invalid properties at {location}")
        if rule.get("additionalProperties") is False:
            unexpected = set(value) - set(properties)
            if unexpected:
                raise ContractError(f"schema unexpected field at {location}.{sorted(unexpected)[0]}")
        for key, child_rule in properties.items():
            if key in value:
                _require(isinstance(child_rule, dict), f"invalid property schema at {location}.{key}")
                _validate_schema_value(value[key], child_rule, root, f"{location}.{key}")
    elif expected_type == "array":
        if "minItems" in rule:
            _require(len(value) >= rule["minItems"], f"schema array too short at {location}")
        if "maxItems" in rule:
            _require(len(value) <= rule["maxItems"], f"schema array too long at {location}")
        if rule.get("uniqueItems") is True:
            _require(len({json.dumps(item, sort_keys=True) for item in value}) == len(value), f"schema array is not unique at {location}")
        item_rule = rule.get("items")
        if item_rule is not None:
            _require(isinstance(item_rule, dict), f"invalid item schema at {location}")
            for index, item in enumerate(value):
                _validate_schema_value(item, item_rule, root, f"{location}[{index}]")
    elif expected_type in {"integer", "number"}:
        numeric = float(value)
        _require(numeric == numeric and numeric not in {float("inf"), float("-inf")}, f"schema number is nonfinite at {location}")
        if "minimum" in rule:
            _require(value >= rule["minimum"], f"schema minimum violated at {location}")
        if "maximum" in rule:
            _require(value <= rule["maximum"], f"schema maximum violated at {location}")
        if "exclusiveMinimum" in rule:
            _require(value > rule["exclusiveMinimum"], f"schema exclusive minimum violated at {location}")
        if "exclusiveMaximum" in rule:
            _require(value < rule["exclusiveMaximum"], f"schema exclusive maximum violated at {location}")
    elif expected_type == "string":
        if "minLength" in rule:
            _require(len(value) >= rule["minLength"], f"schema string too short at {location}")
        if "pattern" in rule:
            _require(re.search(rule["pattern"], value) is not None, f"schema pattern mismatch at {location}")
        if rule.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContractError(f"schema date-time mismatch at {location}") from exc
            _require(parsed.tzinfo is not None, f"schema date-time lacks timezone at {location}")


def validate_json_schema(instance: Any, schema_path: Path) -> bool:
    """Validate the bounded JSON-Schema subset used by this experiment."""

    schema = load_json(schema_path)
    _require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "unsupported JSON Schema draft")
    _validate_schema_value(instance, schema, schema, "$")
    return True


def load_and_validate_constants() -> dict[str, Any]:
    data = load_json(CONSTANTS_PATH)
    validate_json_schema(data, EXPERIMENT_DIR / "schemas/constants.schema.json")
    _require(data.get("schema_version") == 1, "constants schema version mismatch")
    constants = data.get("constants")
    _require(isinstance(constants, dict), "constants object is missing")
    expected = {
        "speed_of_light_m_s": (299792458, "m/s"),
        "muon_mass_energy_mev": (105.6583755, "MeV"),
        "muon_proper_mean_lifetime_s": (2.1969811e-6, "s"),
    }
    _require(set(constants) == set(expected), "constants keys differ from the frozen protocol")
    for name, (value, unit) in expected.items():
        entry = constants[name]
        _require(entry.get("value") == value and entry.get("unit") == unit, f"frozen constant mismatch: {name}")
    _require(constants["muon_mass_energy_mev"].get("source_id") == "pdg-2024-muon-listing", "muon mass source mismatch")
    _require(constants["muon_proper_mean_lifetime_s"].get("source_id") == "pdg-2024-muon-listing", "muon lifetime source mismatch")
    return data


def load_and_validate_sources() -> dict[str, Any]:
    data = load_json(SOURCES_PATH)
    validate_json_schema(data, EXPERIMENT_DIR / "schemas/sources.schema.json")
    _require(data.get("schema_version") == 1, "source manifest schema version mismatch")
    sources = data.get("sources")
    _require(isinstance(sources, list) and len(sources) == 2, "source manifest must contain exactly two registered sources")
    by_id = {entry.get("id"): entry for entry in sources if isinstance(entry, dict)}
    expected = {
        "pdg-2024-muon-listing": (135593, "a3653f756a670b41a215b4a9746e6b5d872fe798a478e233acfc0bc1715eeb03"),
        "pdg-2024-cosmic-ray-review": (2588758, "c8f0620d58d3d61a7b0eae5d2606ce65bbe581a9000c5435299d88ca9ea0125e"),
    }
    _require(set(by_id) == set(expected), "source IDs differ from the frozen protocol")
    for source_id, (size, digest) in expected.items():
        entry = by_id[source_id]
        _require(entry.get("accessed") == "2026-08-08", f"access date mismatch for {source_id}")
        _require(entry.get("bytes") == size and entry.get("sha256") == digest, f"source digest mismatch for {source_id}")
        _require(entry.get("committed") is False, f"external source must not be bundled: {source_id}")
        for field in ("url", "license", "acquisition", "exclusion_reason"):
            _require(isinstance(entry.get(field), str) and entry[field], f"missing {field} for {source_id}")
    return data


def load_and_validate_inputs() -> dict[str, Any]:
    data = load_json(INPUTS_PATH)
    validate_json_schema(data, EXPERIMENT_DIR / "schemas/inputs.schema.json")
    _require(data.get("schema_version") == 1, "input manifest schema version mismatch")
    _require(data.get("experiment") == EXPERIMENT, "input manifest experiment mismatch")
    _require(data.get("post_type") == "understanding", "post type must remain Understanding")
    production = data.get("production", {})
    _require(production.get("normal_run_id") == "run-001", "normal run ID mismatch")
    _require(production.get("momentum_mev_c") == 3000.0, "momentum mismatch")
    grid = production.get("laboratory_grid", {})
    _require((grid.get("index_start"), grid.get("index_stop_inclusive"), grid.get("step_m")) == (0, 200, 100), "grid mismatch")
    _require(production.get("focal_index") == 150, "focal index mismatch")
    rng = production.get("rng", {})
    _require(rng.get("library") == "numpy" and rng.get("bit_generator") == "PCG64", "RNG implementation mismatch")
    _require(rng.get("seed") == 20260808 and rng.get("draw_count") == 100000, "RNG seed or draw count mismatch")
    _require(rng.get("dtype") == "float64", "RNG dtype mismatch")
    _require(production.get("canonical_command") == production_command("run-001"), "canonical command mismatch")
    raw = production.get("raw_output", {})
    _require(raw.get("shape") == [100000] and raw.get("dtype") == "float64" and raw.get("unit") == "s", "raw sample contract mismatch")
    checks = data.get("checks", {})
    _require(checks.get("frame_relative_tolerance") == 1e-12, "frame tolerance mismatch")
    _require(checks.get("focal_monte_carlo_standard_error_multiplier") == 4.0, "focal error multiplier mismatch")
    _require(checks.get("maximum_grid_absolute_discrepancy") == 0.01, "grid discrepancy tolerance mismatch")
    analysis = data.get("analysis", {})
    _require(analysis.get("canonical_result_path") == "research/muon-survival-two-frames/results/summary.json", "canonical result path mismatch")
    _require(analysis.get("figure_path") == "images/muon-survival-two-frames-hero.png", "figure path mismatch")
    _require(analysis.get("metrics_path") == "research/muon-survival-two-frames/metrics.json", "metrics path mismatch")
    for name in ("canonical_result_command", "canonical_result_check_command", "figure_command", "figure_check_command", "metrics_command", "metrics_check_command"):
        _require(isinstance(analysis.get(name), str) and analysis[name], f"missing frozen analysis command: {name}")
    restart = data.get("restart", {})
    _require(restart.get("same_run_resume") is False, "same-run resume must remain disabled")
    _require(restart.get("registered_infrastructure_retries") == 1, "retry authorization mismatch")
    _require(restart.get("only_registered_run_ids") == ["run-001", "run-002"], "registered run-ID contract mismatch")
    _require(restart.get("normal_execution_authorization") == "current setup_review or amended_setup_review approve event into execute", "normal authorization contract mismatch")
    _require(restart.get("retry_execution_authorization") == "current run_review registered_retry event into execute plus preserved incomplete run-001", "retry authorization contract mismatch")
    _require(restart.get("registered_analysis_reruns") == 0, "analysis rerun must remain unauthorized")
    lineage = data.get("lineage", {})
    _require(set(lineage) == {"protocol", "constants", "sources", "environment", "requirements", "workflow_graph", "workflow_cli"}, "input lineage fields mismatch")
    for label, link in lineage.items():
        _require(isinstance(link, dict), f"{label} lineage link is invalid")
        _validate_digest_link(link, label)
    return data


def production_command(run_id: str) -> str:
    if run_id not in {"run-001", "run-002"}:
        raise ContractError("only run-001 or the single authorized run-002 retry can be requested")
    return (
        "research/muon-survival-two-frames/.venv/bin/python "
        "research/muon-survival-two-frames/src/run.py --run-id "
        f"{run_id}"
    )


def _workflow_records(path: Path) -> list[tuple[dict[str, Any], str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ContractError("workflow ledger is unreadable") from exc
    records: list[tuple[dict[str, Any], str]] = []
    for index, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError("workflow ledger contains invalid JSON") from exc
        _require(record.get("sequence") == index, "workflow ledger sequence mismatch")
        records.append((record, line))
    _require(bool(records), "workflow ledger is empty")
    return records


def validate_workflow_ledger(
    *,
    workflow_path: Path = WORKFLOW_PATH,
    graph_path: Path = WORKFLOW_GRAPH_PATH,
    repository_root: Path = REPOSITORY_ROOT,
    workflow_cli_path: Path = WORKFLOW_CLI_PATH,
) -> list[tuple[dict[str, Any], str]]:
    """Use the repository's hash-bound verifier for complete graph replay."""

    expected_path = repository_root / "research" / EXPERIMENT / "workflow.jsonl"
    try:
        _require(workflow_path.resolve(strict=True) == expected_path.resolve(strict=True), "workflow path is not the managed experiment ledger")
        _require(graph_path.is_file() and not graph_path.is_symlink(), "workflow graph is missing or linked")
        _require(workflow_cli_path.is_file() and not workflow_cli_path.is_symlink(), "workflow verifier is missing or linked")
    except OSError as exc:
        raise ContractError("workflow contract path cannot be resolved") from exc
    _require(sha256_file(graph_path) == EXPECTED_WORKFLOW_GRAPH_SHA256, "workflow graph digest mismatch")
    _require(sha256_file(workflow_cli_path) == EXPECTED_WORKFLOW_CLI_SHA256, "workflow verifier digest mismatch")
    try:
        ledger_before = workflow_path.read_bytes()
    except OSError as exc:
        raise ContractError("workflow ledger is unreadable") from exc
    environment = os.environ.copy()
    environment["RESEARCH_WORKFLOW_ROOT"] = str(repository_root)
    environment["RESEARCH_WORKFLOW_GRAPH"] = str(graph_path)
    try:
        verified = subprocess.run(
            ["node", str(workflow_cli_path), "verify", "--experiment", EXPERIMENT],
            cwd=repository_root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ContractError("workflow graph verification could not run") from exc
    _require(verified.returncode == 0, "workflow graph replay or evidence verification failed")
    try:
        _require(workflow_path.read_bytes() == ledger_before, "workflow ledger changed during verification")
    except OSError as exc:
        raise ContractError("workflow ledger became unreadable during verification") from exc
    return _workflow_records(workflow_path)


def run_namespaces(runs_dir: Path) -> list[str]:
    """Return every entry in the production runs namespace, including links."""

    if not runs_dir.exists() and not runs_dir.is_symlink():
        return []
    _require(runs_dir.is_dir() and not runs_dir.is_symlink(), "runs path must be a real directory")
    return sorted(entry.name for entry in runs_dir.iterdir())


def _authorization_record(event: Mapping[str, Any], raw_line: str, kind: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "workflow_path": "research/muon-survival-two-frames/workflow.jsonl",
        "event_id": event["event_id"],
        "sequence": event["sequence"],
        "submission_sequence": event["submission_sequence"],
        "decision": event["decision"],
        "graph_version": event["graph_version"],
        "graph_sha256": event["graph_sha256"],
        "event_sha256": hashlib.sha256(f"{raw_line}\n".encode("utf-8")).hexdigest(),
    }


def authorize_run_request(
    run_id: str,
    *,
    workflow_path: Path = WORKFLOW_PATH,
    runs_dir: Path | None = None,
    graph_path: Path = WORKFLOW_GRAPH_PATH,
    repository_root: Path = REPOSITORY_ROOT,
    workflow_cli_path: Path = WORKFLOW_CLI_PATH,
) -> dict[str, Any]:
    """Bind normal execution or the sole retry to the current graph event."""

    if run_id not in {"run-001", "run-002"}:
        raise ContractError("unregistered run ID")
    records = validate_workflow_ledger(
        workflow_path=workflow_path,
        graph_path=graph_path,
        repository_root=repository_root,
        workflow_cli_path=workflow_cli_path,
    )
    event, raw_line = records[-1]
    namespaces = run_namespaces(runs_dir if runs_dir is not None else EXPERIMENT_DIR / "runs")
    if run_id == "run-001":
        _require(namespaces == [], "normal execution requires an empty runs namespace")
        valid = (
            event.get("type") == "review"
            and event.get("from") in {"setup_review", "amended_setup_review"}
            and event.get("to") == "execute"
            and event.get("decision") == "approve"
        )
        _require(valid, "run-001 requires the current recorded setup approval into execute")
        return _authorization_record(event, raw_line, "normal")

    _require(namespaces == ["run-001"], "registered retry requires only the preserved run-001 namespace")
    prior = (runs_dir if runs_dir is not None else EXPERIMENT_DIR / "runs") / "run-001"
    _require(prior.is_dir() and not prior.is_symlink(), "retry predecessor must be a real run-001 directory")
    _require(not (prior / "COMPLETE.json").exists() and not (prior / "COMPLETE.json").is_symlink(), "a complete run-001 cannot be retried")
    valid = (
        event.get("type") == "review"
        and event.get("from") == "run_review"
        and event.get("to") == "execute"
        and event.get("decision") == "registered_retry"
    )
    _require(valid, "run-002 requires the current recorded registered_retry event")
    return _authorization_record(event, raw_line, "registered_retry")


def validate_recorded_run_authorization(
    run_id: str,
    authorization: Mapping[str, Any],
    *,
    workflow_path: Path = WORKFLOW_PATH,
    graph_path: Path = WORKFLOW_GRAPH_PATH,
    repository_root: Path = REPOSITORY_ROOT,
    workflow_cli_path: Path = WORKFLOW_CLI_PATH,
) -> None:
    expected_kind = "normal" if run_id == "run-001" else "registered_retry" if run_id == "run-002" else None
    _require(expected_kind is not None and authorization.get("kind") == expected_kind, "run authorization kind mismatch")
    _require(authorization.get("workflow_path") == "research/muon-survival-two-frames/workflow.jsonl", "run authorization workflow path mismatch")
    records = validate_workflow_ledger(
        workflow_path=workflow_path,
        graph_path=graph_path,
        repository_root=repository_root,
        workflow_cli_path=workflow_cli_path,
    )
    matches = [(event, raw) for event, raw in records if event.get("event_id") == authorization.get("event_id")]
    _require(len(matches) == 1, "recorded run authorization event is missing or duplicated")
    event, raw_line = matches[0]
    expected = _authorization_record(event, raw_line, expected_kind)
    _require(dict(authorization) == expected, "recorded run authorization does not match its workflow event")
    if expected_kind == "normal":
        _require(event.get("from") in {"setup_review", "amended_setup_review"} and event.get("to") == "execute" and event.get("decision") == "approve", "normal authorization event is invalid")
    else:
        _require(event.get("from") == "run_review" and event.get("to") == "execute" and event.get("decision") == "registered_retry", "retry authorization event is invalid")


def verify_environment(*, require_node: bool = True) -> dict[str, str]:
    _require(platform.python_implementation() == "CPython", "CPython is required")
    _require(platform.python_version() == EXPECTED_PYTHON, f"Python {EXPECTED_PYTHON} is required")
    versions = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "numpy_version": importlib.metadata.version("numpy"),
        "matplotlib_version": importlib.metadata.version("matplotlib"),
        "pip_version": importlib.metadata.version("pip"),
    }
    _require(versions["numpy_version"] == EXPECTED_NUMPY, f"NumPy {EXPECTED_NUMPY} is required")
    _require(versions["matplotlib_version"] == EXPECTED_MATPLOTLIB, f"Matplotlib {EXPECTED_MATPLOTLIB} is required")
    _require(versions["pip_version"] == EXPECTED_PIP, f"pip {EXPECTED_PIP} is required")
    _require(platform.system() == "Linux" and platform.machine() == "x86_64", "Linux x86-64 is required by the wheel lock")
    node_version = "not-checked"
    if require_node:
        try:
            node_version = subprocess.run(
                ["node", "--version"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip().removeprefix("v")
        except (OSError, subprocess.SubprocessError) as exc:
            raise ContractError("cannot verify the registered Node.js version") from exc
        _require(node_version == EXPECTED_NODE, f"Node.js {EXPECTED_NODE} is required")
    versions["node_version"] = node_version
    return versions


def verify_setup_manifest() -> dict[str, Any]:
    manifest = load_json(SETUP_MANIFEST_PATH)
    _require(manifest.get("schema_version") == 1, "setup manifest schema version mismatch")
    _require(manifest.get("experiment") == EXPERIMENT, "setup manifest experiment mismatch")
    artifacts = manifest.get("artifacts")
    _require(isinstance(artifacts, list) and artifacts, "setup manifest has no artifact inventory")
    seen: set[str] = set()
    for entry in artifacts:
        _require(isinstance(entry, dict) and set(entry) == {"path", "bytes", "sha256"}, "invalid setup artifact entry")
        path_text = entry["path"]
        _require(isinstance(path_text, str) and path_text not in seen, "duplicate or invalid setup artifact path")
        _require(not Path(path_text).is_absolute() and ".." not in Path(path_text).parts, "setup artifact path is not repository-relative")
        seen.add(path_text)
        path = REPOSITORY_ROOT / path_text
        _require(path.is_file() and not path.is_symlink(), f"setup artifact missing or symlinked: {path_text}")
        _require(path.stat().st_size == entry["bytes"], f"setup artifact size mismatch: {path_text}")
        _require(SHA256_RE.fullmatch(entry["sha256"]) is not None, f"invalid setup artifact digest: {path_text}")
        _require(sha256_file(path) == entry["sha256"], f"setup artifact digest mismatch: {path_text}")
    return manifest


def setup_validation() -> dict[str, Any]:
    """Validate all prospective setup bytes without performing science."""

    set_deterministic_process_environment()
    versions = verify_environment(require_node=True)
    load_and_validate_constants()
    load_and_validate_sources()
    load_and_validate_inputs()
    manifest = verify_setup_manifest()
    for schema in sorted((EXPERIMENT_DIR / "schemas").glob("*.json")):
        document = load_json(schema)
        _require(document.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"schema draft mismatch: {schema.name}")
        _require(document.get("type") == "object", f"schema root must be an object: {schema.name}")
    namespaces = run_namespaces(EXPERIMENT_DIR / "runs")
    _require(namespaces == [], f"production run namespace exists: {', '.join(namespaces)}")
    return {"versions": versions, "artifact_count": len(manifest["artifacts"]), "production_absent": True, "run_namespaces": []}
