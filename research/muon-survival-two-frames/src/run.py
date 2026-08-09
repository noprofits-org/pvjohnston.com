#!/usr/bin/env python3
"""Generate and seal the single registered proper-lifetime sample only."""

from __future__ import annotations

import argparse
import platform
from datetime import datetime, timezone

from bundle import (
    RunExecutionError,
    RunSpec,
    create_new_run_directory,
    execute_and_seal,
    validate_run_bundle,
)
from contract import (
    EXPERIMENT,
    EXPERIMENT_DIR,
    ContractError,
    authorize_run_request,
    digest_record,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_and_validate_sources,
    production_command,
    set_deterministic_process_environment,
    verify_environment,
    validate_recorded_run_authorization,
    verify_setup_manifest,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_spec(run_id: str, *, recorded_authorization: dict | None = None) -> RunSpec:
    if recorded_authorization is None:
        authorization = authorize_run_request(run_id)
    else:
        validate_recorded_run_authorization(run_id, recorded_authorization)
        authorization = dict(recorded_authorization)
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
        authorization=authorization,
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
    try:
        execute_and_seal(run_dir, spec, started_at=utc_now(), completed_at=utc_now)
        validate_run_bundle(run_dir, spec)
    except RunExecutionError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
