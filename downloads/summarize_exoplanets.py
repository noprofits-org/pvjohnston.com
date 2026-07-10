#!/usr/bin/env python3
"""Summarize the NASA exoplanet CSV used in the Excel automation demo."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def present(value: str | None) -> bool:
    return bool(value and value.strip())


def summarize(path: Path) -> dict[str, object]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    years = [int(float(row["disc_year"])) for row in rows if present(row["disc_year"])]
    methods = Counter(row["discoverymethod"] for row in rows if present(row["discoverymethod"]))
    fields = ["pl_orbper", "pl_orbsmax", "pl_rade", "pl_bmasse", "pl_eqt", "st_teff", "sy_dist"]

    return {
        "planets": len(rows),
        "host_systems": len({row["hostname"] for row in rows if present(row["hostname"])}),
        "earliest_discovery_year": min(years),
        "latest_discovery_year": max(years),
        "top_discovery_methods": methods.most_common(10),
        "field_coverage": {
            field: {
                "available": sum(present(row[field]) for row in rows),
                "share": sum(present(row[field]) for row in rows) / len(rows),
            }
            for field in fields
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON destination")
    args = parser.parse_args()

    result = summarize(args.csv_path)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
