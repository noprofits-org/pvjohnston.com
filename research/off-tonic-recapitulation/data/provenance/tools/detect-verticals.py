#!/usr/bin/env python3

import argparse

import numpy as np
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("y0", type=int)
parser.add_argument("y1", type=int)
parser.add_argument("--threshold", type=int, default=150)
parser.add_argument("--minimum-run", type=int, default=90)
args = parser.parse_args()

pixels = np.asarray(Image.open(args.image).convert("L"))[args.y0:args.y1]
dark = pixels < args.threshold
runs = np.zeros(dark.shape[1], dtype=int)
for x in range(dark.shape[1]):
    padded = np.concatenate(([False], dark[:, x], [False]))
    transitions = np.flatnonzero(padded[1:] != padded[:-1])
    if transitions.size:
        runs[x] = int(np.max(transitions[1::2] - transitions[::2]))

selected = np.flatnonzero(runs >= args.minimum_run)
groups = []
for value in selected:
    if not groups or value > groups[-1][-1] + 1:
        groups.append([int(value)])
    else:
        groups[-1].append(int(value))

for group in groups:
    peak = max(group, key=lambda x: runs[x])
    print(f"{group[0]:4d}-{group[-1]:4d} peak={peak:4d} run={runs[peak]:3d}")
