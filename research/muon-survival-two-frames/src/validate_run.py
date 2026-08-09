#!/usr/bin/env python3
"""Read-only integrity validation for a completed proper-lifetime run."""

from __future__ import annotations

import argparse
import json

from bundle import validate_run_bundle
from contract import EXPERIMENT_DIR, load_json, set_deterministic_process_environment
from run import build_spec


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    set_deterministic_process_environment()
    run_dir = EXPERIMENT_DIR / "runs" / args.run_id
    manifest = load_json(run_dir / "run-manifest.json")
    spec = build_spec(args.run_id, recorded_authorization=manifest.get("authorization"))
    report = validate_run_bundle(run_dir, spec)
    print(json.dumps(report, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
