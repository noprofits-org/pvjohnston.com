#!/usr/bin/env python3
"""Emit the TikZ body for the post's Figure 1 from the canonical result.

The populations plotted in the post must not be typed by hand: a regenerated
results.json would leave stale literals in the figure while metrics.json and
the site build both still passed. This script derives the bar coordinates from
results.json, and --check verifies that the figure committed in the post
matches what the canonical result implies.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS_PATH = HERE / "results.json"
POST_PATH = (
    ROOT / "posts" / "2026-08-03-does-the-near-uniform-smx-ensemble-survive-thermal-correction.md"
)
CONFORMERS = ("A", "B", "C", "D")


def coordinates(populations: dict) -> str:
    return " ".join(f"({name},{100.0 * populations[name]:.1f})" for name in CONFORMERS)


def figure_body() -> str:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    source = results["source_preflight"]["electronic_populations"]
    rrho = results["analysis"]["rrho"]["composite_populations"]
    mrrho50 = results["analysis"]["mrrho50"]["composite_populations"]
    return f"""\\begin{{tikzpicture}}[font=\\small]
  \\begin{{axis}}[
    width=12.4cm, height=6.4cm,
    ybar, bar width=9pt,
    ymin=0, ymax=50,
    symbolic x coords={{A,B,C,D}},
    xtick=data,
    axis lines=left,
    enlarge x limits=0.18,
    ylabel={{population (\\%)}},
    ylabel style={{font=\\fontsize{{6.6}}{{8}}\\selectfont}},
    xticklabel style={{font=\\fontsize{{6.6}}{{8}}\\selectfont}},
    yticklabel style={{font=\\fontsize{{6}}{{7}}\\selectfont}},
    ymajorgrids, grid style={{black!12, line width=0.3pt}},
    axis line style={{black!55, line width=0.35pt}},
    tick style={{black!55}},
    legend style={{font=\\fontsize{{5.8}}{{7}}\\selectfont, draw=black!30,
                  at={{(0.98,0.95)}}, anchor=north east}},
    legend cell align=left,
  ]
    \\addplot[draw=black!50, fill=black!20, line width=0.2pt]
      coordinates {{{coordinates(source)}}};
    \\addplot[draw=blue!55!black, fill=blue!35!white, line width=0.2pt]
      coordinates {{{coordinates(rrho)}}};
    \\addplot[draw=blue!55!black, fill=blue!70!black, line width=0.2pt]
      coordinates {{{coordinates(mrrho50)}}};
    \\legend{{source electronic, rrho, mrrho50}}
  \\end{{axis}}
\\end{{tikzpicture}}"""


def committed_figure() -> str:
    blocks = re.findall(r"```tikzpicture\n(.*?)```", POST_PATH.read_text(encoding="utf-8"), re.S)
    if len(blocks) != 1:
        raise SystemExit(f"expected exactly one tikzpicture block in the post, found {len(blocks)}")
    return blocks[0].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = figure_body()
    if not args.check:
        print(expected)
        return 0

    if expected != committed_figure():
        print(
            "the post's Figure 1 does not match a fresh projection of results.json",
            file=sys.stderr,
        )
        return 1
    print("smx-conformer-thermochemistry: Figure 1 matches the canonical result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
