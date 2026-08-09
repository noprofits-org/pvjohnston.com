#!/usr/bin/env python3
"""Validate and return the exact canonical result bytes used by projections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from analyze import validate_analysis_result
from contract import (
    EXPERIMENT_DIR,
    REPOSITORY_ROOT,
    ContractError,
    canonical_json_bytes,
    set_deterministic_process_environment,
    verify_environment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(EXPERIMENT_DIR / "results/summary.json"))
    parser.add_argument("--setup-fixture", action="store_true")
    parser.add_argument("--repository-root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve(strict=True)
    if not input_path.is_file() or input_path.is_symlink():
        raise ContractError("analysis result must be a regular, non-symlink file")
    canonical_path = (EXPERIMENT_DIR / "results/summary.json").resolve()
    if args.setup_fixture:
        if "setup-toy" not in input_path.name or args.repository_root is None:
            raise ContractError("setup validation requires a visible setup-toy input and repository root")
        repository_root = Path(args.repository_root).resolve(strict=True)
        try:
            input_path.relative_to(repository_root)
        except ValueError as exc:
            raise ContractError("setup result is outside its synthetic repository root") from exc
        if input_path == canonical_path:
            raise ContractError("setup validation cannot address the canonical result")
        enforce_frozen_inputs = False
    else:
        if args.repository_root is not None or input_path != canonical_path:
            raise ContractError("production validation accepts only the canonical result path")
        repository_root = REPOSITORY_ROOT
        enforce_frozen_inputs = True

    set_deterministic_process_environment()
    verify_environment(require_node=False)
    payload = input_path.read_bytes()
    try:
        result = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError("analysis result is not valid UTF-8 JSON") from exc
    validate_analysis_result(
        result,
        verify_provenance=True,
        enforce_frozen_inputs=enforce_frozen_inputs,
        repository_root=repository_root,
    )
    if payload != canonical_json_bytes(result):
        raise ContractError("analysis result serialization is not canonical")
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, OSError, ValueError) as exc:
        print(f"result validation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
