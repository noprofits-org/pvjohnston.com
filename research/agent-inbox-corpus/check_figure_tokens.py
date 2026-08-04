#!/usr/bin/env python3
"""Check Figure 4's drawn token counts against the committed token table.

TikZ blocks cannot carry metric references, so the counts lettered into
Figure 4's transition labels are the one place a filename-token number exists
outside the metrics projection. This script extracts every `\\texttt{token} N`
pair from the post's Figure 4 and compares it with `filename-tokens.csv`
under the same case-variant merge Table 1 documents (SCREAMING_SNAKE folds
into kebab-lowercase). A committed figure that disagrees with the committed
table fails, so the drawing cannot drift from the data.
"""

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POST = HERE.parent.parent / "posts" / "2026-08-03-counting-the-inbox.md"
EXPECTED_PAIRS = 8


def merged_counts() -> dict:
    counts = {}
    with open(HERE / "filename-tokens.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canonical = row["token"].lower().replace("_", "-")
            counts[canonical] = counts.get(canonical, 0) + int(row["filenames"])
    return counts


def figure_pairs() -> list:
    blocks = re.findall(r"```tikzpicture\n(.*?)```", POST.read_text(encoding="utf-8"), re.S)
    machines = [b for b in blocks if "\\texttt{GO}" in b]
    if len(machines) != 1:
        raise SystemExit(f"expected exactly one state-machine figure, found {len(machines)}")
    return [
        (token.lower().replace("_", "-"), int(count))
        for token, count in re.findall(
            r"\\texttt\{([A-Za-z_-]+)\}(?:\\\\|[:\s])*(\d+)", machines[0]
        )
    ]


def main() -> int:
    counts = merged_counts()
    pairs = figure_pairs()
    failures = []
    if len(pairs) != EXPECTED_PAIRS:
        failures.append(
            f"expected {EXPECTED_PAIRS} token/count pairs in Figure 4, matched {len(pairs)}"
        )
    for token, drawn in pairs:
        if token not in counts:
            failures.append(f"Figure 4 token {token} is not in filename-tokens.csv")
        elif counts[token] != drawn:
            failures.append(
                f"Figure 4 draws {token} as {drawn}, the token table merges to {counts[token]}"
            )
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"agent-inbox-corpus: Figure 4's {len(pairs)} drawn counts match filename-tokens.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
