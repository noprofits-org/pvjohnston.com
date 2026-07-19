#!/usr/bin/env python3

import argparse

import numpy as np
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("treble_y0", type=int)
parser.add_argument("treble_y1", type=int)
parser.add_argument("bass_y0", type=int)
parser.add_argument("bass_y1", type=int)
parser.add_argument("--threshold", type=int, default=150)
parser.add_argument("--minimum-run", type=int, default=80)
parser.add_argument("--tolerance", type=int, default=5)
args = parser.parse_args()

pixels = np.asarray(Image.open(args.image).convert("L"))


def longest_runs(region):
    dark = region < args.threshold
    result = np.zeros(dark.shape[1], dtype=int)
    for x in range(dark.shape[1]):
        padded = np.concatenate(([False], dark[:, x], [False]))
        transitions = np.flatnonzero(padded[1:] != padded[:-1])
        if transitions.size:
            result[x] = int(np.max(transitions[1::2] - transitions[::2]))
    return result


treble = longest_runs(pixels[args.treble_y0:args.treble_y1])
bass = longest_runs(pixels[args.bass_y0:args.bass_y1])
treble_selected = np.flatnonzero(treble >= args.minimum_run)
bass_selected = np.flatnonzero(bass >= args.minimum_run)
selected = []
for value in treble_selected:
    lo = max(0, value - args.tolerance)
    hi = min(len(bass), value + args.tolerance + 1)
    if np.any(bass[lo:hi] >= args.minimum_run):
        selected.append(int(value))

groups = []
for value in selected:
    if not groups or value > groups[-1][-1] + 1:
        groups.append([value])
    else:
        groups[-1].append(value)

for group in groups:
    peak = max(group, key=lambda x: treble[x] + np.max(bass[max(0, x-args.tolerance):x+args.tolerance+1]))
    bass_peak = max(range(max(0, peak-args.tolerance), min(len(bass), peak+args.tolerance+1)), key=lambda x: bass[x])
    print(
        f"{group[0]:4d}-{group[-1]:4d} peak={peak:4d}/{bass_peak:4d} "
        f"runs={treble[peak]:3d}/{bass[bass_peak]:3d}"
    )
