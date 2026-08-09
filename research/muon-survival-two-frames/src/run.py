#!/usr/bin/env python3
"""Generate and seal the single registered proper-lifetime sample only."""

from __future__ import annotations

import argparse
import platform
from datetime import datetime, timezone

from bundle import (
    RunSpec,
    create_new_run_directory,
    generate_lifetimes,
    record_failure_without_completion,
    seal_run_bundle,
    validate_run_bundle,
)
from contract import (
    EXPERIMENT,
    EXPERIMENT_DIR,
    REPOSITORY_ROOT,
    RUN_ID_RE,
    ContractError,
    digest_record,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_and_validate_sources,
    load_json,
    production_command,
    set_deterministic_process_environment,
    verify_environment,
    verify_setup_manifest,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_spec(run_id: str) -> RunSpec:
    if RUN_ID_RE.fullmatch(run_id) is None:
        raise ContractError("run ID must have the form run-NNN")
    versions = verify_environment(require_node=True)
    constants = load_and_validate_constants()
    load_and_validate_sources()
    inputs = load_and_validate_inputs()
    verify_setup_manifest()
    production = inputs["production"]
    lineage = {
        "protocol": dict(inputs["lineage"]["protocol"]),
        "setup_manifest": digest_record(EXPERIMENT_DIR / "setup-manifest.json"),
        "inputs": digest_record(EXPERIMENT_DIR / "inputs.json"),
        "constants": dict(inputs["lineage"]["constants"]),
        "sources": dict(inputs["lineage"]["sources"]),
        "environment": dict(inputs["lineage"]["environment"]),
        "requirements": dict(inputs["lineage"]["requirements"]),
    }
    platform_record = {
        "os": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        **versions,
    }
    return RunSpec(
        experiment=EXPERIMENT,
        purpose="canonical-production",
        run_id=run_id,
        command=production_command(run_id),
        seed=production["rng"]["seed"],
        draw_count=production["rng"]["draw_count"],
        scale_s=constants["constants"]["muon_proper_mean_lifetime_s"]["value"],
        lineage=lineage,
        platform=platform_record,
        path_prefix=f"research/{EXPERIMENT}/runs/{run_id}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    set_deterministic_process_environment()
    spec = build_spec(args.run_id)
    run_dir = create_new_run_directory(EXPERIMENT_DIR / "runs", args.run_id)
    started_at = utc_now()
    try:
        sample = generate_lifetimes(spec)
        completed_at = utc_now()
        seal_run_bundle(run_dir, sample, spec, started_at=started_at, completed_at=completed_at)
        validate_run_bundle(run_dir, spec)
    except BaseException as exc:
        record_failure_without_completion(run_dir, exc)
        raise
    print(f"sealed {spec.path_prefix}; scientific values were not printed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
