#!/usr/bin/env python3
"""Verify frozen setup artifacts without executing any production quantity."""

from __future__ import annotations

import json

from contract import setup_validation


def main() -> int:
    report = setup_validation()
    print(json.dumps(report, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
