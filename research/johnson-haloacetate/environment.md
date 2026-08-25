# Environment

The canonical Psi4 run was performed on a local Apple Silicon machine in
the private Molecules lab. This public repository records that boundary
and does not rerun Psi4. The analysis projection (amplitudes, barriers,
figures, metrics) is regenerated from the committed rematch and scan
tables on whatever host checks out the post branch.

- Operating system and version (canonical run): macOS on Apple Silicon
- Architecture (canonical run): arm64
- Quantum-chemistry executable: Psi4 1.11 at
  `/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4`
- Method: B3LYP-D3(BJ)/aug-cc-pVDZ, charge −1, singlet, gas phase, no
  PCM. Binding charges: MBIS. Frozen dihedral 5-4-1-2; remaining degrees
  of freedom relaxed.
- Optimizer: rematch unconstrained optimizations of four ions; then a
  0° → 120° continuation in 15° steps on CF3COO− and CCl3COO−
- Hardware assumptions: laptop-scale single-ion DFT; wall time is
  minutes to an hour per ion, not a cluster job
- Locale/timezone: host local time in the private logs; this projection
  uses the dated 2026-08-24 rematch and scan notes
- Random seeds and nondeterministic operations: none declared. SCF and
  geometry convergence are deterministic to the requested thresholds on
  one machine and one thread count; last digits can move with BLAS
- Required environment variables: none committed. The private lab used
  the `qchem` conda environment
- External services: none

## Analysis / plotting

Figures and metrics are produced from the committed CSVs. This
directory does not rerun Psi4 and does not pin a Psi4 rerun path.

- Canonical analysis host: the same Apple Silicon `qchem` conda environment
- Interpreter: Python 3 from conda-forge on the lab host; the committed
  figure script runs on CPython 3.12 with matplotlib 3.11.0
- Plotting: matplotlib 3.11.0, pinned in `requirements.txt`
- Metrics generator: Node, `generate-metrics.mjs`; no extra Python
  packages
- No lockfile. `requirements.txt` records the plotting pin only.

## What is not in this repository

Psi4 output logs and scratch from `~/Molecules/johnson-haloacetate` are
not committed. They are large and embed absolute machine paths. The same
choice is recorded in `research/hillel-triplet`. The committed evidence
is `rematch/summary.csv` plus the M1 and M3 scan CSVs.
