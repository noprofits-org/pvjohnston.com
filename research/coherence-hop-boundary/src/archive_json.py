#!/usr/bin/env python3
"""Create or verify a byte-preserving, deterministic gzip JSON archive."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = EXPERIMENT_DIR / "results" / "sweep.json"
DEFAULT_OUTPUT = EXPERIMENT_DIR / "results" / "sweep.json.gz"


def _validate_json(data: bytes, label: Path) -> None:
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label}: invalid UTF-8 JSON ({error})") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label}: top-level JSON value must be an object")


def _compress(data: bytes) -> bytes:
    # mtime=0 suppresses the clock; gzip.compress does not embed the input name.
    return gzip.compress(data, compresslevel=9, mtime=0)


def _write(input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    _validate_json(data, input_path)
    archived = _compress(data)
    if gzip.decompress(archived) != data:
        raise RuntimeError("gzip round-trip did not preserve the input bytes")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_bytes(archived)
    os.replace(temporary, output_path)


def _check(output_path: Path) -> None:
    archived = output_path.read_bytes()
    try:
        data = gzip.decompress(archived)
    except (gzip.BadGzipFile, EOFError) as error:
        raise ValueError(f"{output_path}: invalid gzip archive ({error})") from error
    _validate_json(data, output_path)
    if _compress(data) != archived:
        raise ValueError(f"{output_path}: gzip bytes are not canonical")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check:
            _check(args.output)
            action = "current"
        else:
            _write(args.input, args.output)
            action = "written"
    except (OSError, ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"{args.output}: deterministic gzip archive {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
