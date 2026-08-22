# Environment

The canonical Psi4 run was performed on a local Apple Silicon machine in
the private Molecules lab. This public repository records that boundary
and does not rerun Psi4. The analysis projection (crossings, gaps, figures,
metrics) is regenerated from the committed summary tables on whatever host
checks out the post branch.

- Operating system and version (canonical run): macOS on Apple Silicon
- Architecture (canonical run): arm64
- Quantum-chemistry executable: Psi4 1.11 at
  `/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4`
- Method: RKS S0 / UKS T1, B3LYP-D3(BJ)/cc-pVDZ, optking frozen CNNC,
  gas phase, no PCM
- Optimizer: continuation 180° → 0° in 15° steps; default maxiter 150 on
  the first pass; reconvergence maxiter 300 on selected M4 S0 points
- Hardware assumptions: laptop-scale single-molecule DFT; wall time is
  hours per surface, not a cluster job
- Locale/timezone: host local time in the private logs; this projection
  uses the dated 2026-08-22 reconvergence note
- Random seeds and nondeterministic operations: none declared. SCF and
  geometry convergence are deterministic to the requested thresholds on
  one machine and one thread count; last digits can move with BLAS
- Required environment variables: none committed. The private lab used
  the `qchem` conda environment
- External services: none

## Analysis / plotting

Figures and metrics are produced from the committed summary tables. This
directory does not rerun Psi4 and does not pin a Psi4 rerun path.

- Canonical analysis host: the same Apple Silicon `qchem` conda environment
- Interpreter: Python 3.14.6 from conda-forge
- Plotting: matplotlib 3.11.0, pinned in `requirements.txt`
- Metrics generator: Node, `generate-metrics.mjs`; no extra Python
  packages
- No lockfile. `requirements.txt` records the plotting pin only.

## What is not in this repository

Psi4 output logs and scratch from `~/Molecules/hillel-triplet` are not
committed. They are large and embed absolute machine paths. The same
choice is recorded in `research/bmn-frontier-orbitals`. The committed
evidence is `results/results.json` plus the M0–M4 summary CSVs.
