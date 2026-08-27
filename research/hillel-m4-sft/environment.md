# Environment

The canonical ORCA run was performed on a local Apple Silicon machine
in the private Molecules lab. This public repository records that
boundary and does not rerun ORCA. The analysis projection (sign
changes, interpolant, site metrics) is regenerated from the committed
Bayes file on whatever host checks out the post branch.

- Operating system and version (canonical run): macOS on Apple Silicon
- Architecture (canonical run): arm64
- Quantum-chemistry executable: ORCA 6.1.1. Hillel et al. 2024 used
  ORCA 5.0.3. This repository does not pin a host path and does not
  run ORCA in CI.
- Method: SF-TDA LibXC(BHANDHLYP) D3BJ/def2-QZVPP, RIJCOSX, gas
  phase, no PCM. Constrained CNNC; remaining degrees of freedom
  relaxed. Required window 135°, 120°, 105°, 90°.
- Optimizer: constrained Opt. Native BH&HLYP exited 55; the
  published window is LibXC(BHANDHLYP). S0 at 90° was reseeded
  from T1.
- Hardware assumptions: laptop-scale single-molecule DFT; wall time
  is hours per constrained point, not a cluster job
- Locale/timezone: host local time in the private logs; this
  projection uses the dated 2026-08-25 freeze and the 2026-08-27
  window
- Random seeds and nondeterministic operations: none declared. SCF
  and geometry convergence are deterministic to the requested
  thresholds on one machine and one thread count; last digits can
  move with BLAS
- Required environment variables: none committed
- External services: none

## Analysis

Metrics are produced from the committed Bayes projection. This
directory does not rerun ORCA and does not pin an ORCA rerun path.

- Metrics generator: Node, `generate-metrics.mjs`; no extra
  packages
- The Figure 1 renderer uses Python 3.9.6, NumPy 2.0.2, and Pillow
  11.3.0, pinned in `requirements-figure.txt`. Latin type is the
  committed `analysis/hanken-grotesk.ttf`. Axis Δ and φ come from the
  committed `analysis/dejavu-sans.ttf` at the same pixel size. Both
  load with Pillow `ImageFont.truetype`. No host font path and no
  platform-specific FreeType library name.
- The metrics generator has no lockfile and reads only
  `results/bayes-metrics.json`

## What is not in this repository

ORCA `.out` files and scratch from `~/Molecules/hillel-m4-sft` are
not committed. They are large and embed absolute machine paths. The
same choice is recorded in `research/hillel-triplet`. The committed
evidence is `results/bayes-metrics.json`.
