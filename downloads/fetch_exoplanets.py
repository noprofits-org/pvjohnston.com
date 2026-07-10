#!/usr/bin/env python3
"""Download a reproducible NASA Exoplanet Archive CSV snapshot.

The query targets PSCompPars: one composite row per confirmed planet.  It is a
convenient table for population-level exploration, but NASA cautions that a
row can combine values from multiple references.  See the source links in the
companion workbook before using this snapshot for research.
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TAP_SYNC_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERY = """select
pl_name,hostname,disc_year,discoverymethod,disc_facility,
pl_orbper,pl_orbsmax,pl_rade,pl_bmasse,pl_eqt,
st_teff,sy_dist,sy_snum,sy_pnum
from pscomppars
order by disc_year,pl_name""".replace("\n", " ")


def download_csv() -> bytes:
    """Return the CSV response after basic structural validation."""
    url = f"{TAP_SYNC_URL}?{urlencode({'query': QUERY, 'format': 'csv'})}"
    request = Request(url, headers={"User-Agent": "pvjohnston.com-excel-demo/1.0"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()

    text = payload.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) < 1_000:
        raise RuntimeError(f"Expected at least 1,000 planets; received {len(rows)}")
    if any(not row.get("pl_name") for row in rows):
        raise RuntimeError("The response contains a row without pl_name")
    if len({row["pl_name"] for row in rows}) != len(rows):
        raise RuntimeError("PSCompPars response unexpectedly contains duplicate planets")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("nasa-exoplanets-2026-07-10.csv"),
        help="Destination CSV path",
    )
    args = parser.parse_args()

    payload = download_csv()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {args.output} ({len(payload):,} bytes)")


if __name__ == "__main__":
    main()
