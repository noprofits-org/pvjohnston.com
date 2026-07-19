#!/usr/bin/env python3

import argparse

import numpy as np
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("y0", type=int)
parser.add_argument("y1", type=int)
parser.add_argument("--threshold", type=int, default=150)
parser.add_argument("--minimum", type=int, default=120)
args = parser.parse_args()

pixels = np.asarray(Image.open(args.image).convert("L"))[args.y0:args.y1]
counts = np.sum(pixels < args.threshold, axis=0)
selected = np.flatnonzero(counts >= args.minimum)
groups = []
for value in selected:
    if not groups or value > groups[-1][-1] + 1:
        groups.append([int(value)])
    else:
        groups[-1].append(int(value))

for group in groups:
    peak = max(group, key=lambda x: counts[x])
    print(f"{group[0]:4d}-{group[-1]:4d} peak={peak:4d} black={counts[peak]:3d}")
