# Environment

The registered run uses the existing `qchem` conda environment on the
experiment host. `conda-osx-arm64-explicit.txt` records exact package artifacts
for this platform. Despite the environment name, this experiment invokes xTB,
not the proprietary Q-Chem program.

- Operating system and version: macOS 26.5.2 build 25F84; Darwin 25.5.0
- Architecture: arm64
- Hardware: Apple M1; computations are deliberately serialized
- Interpreter: CPython 3.14.6
- Dependency manager: conda 26.3.2
- Numerical package: NumPy 2.5.0
- Quantum-chemistry executable: xTB 6.7.1 (conda-forge build
  `gfortran_hc17bbfb_5`)
- Solvation and method: GFN2-xTB/ALPB(water)
- Parallelism: xTB `--parallel 1`; `OMP_NUM_THREADS=1`,
  `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and
  `VECLIB_MAXIMUM_THREADS=1`
- Random seeds and nondeterministic operations: none
- Locale/timezone: xTB output records host local time; result generation uses
  UTC
- Required environment variables: the four thread-limit variables above;
  `XTB_BIN` may name the pinned executable when it is not on `PATH`
- External services: none

The source PDF and supplement are not required during execution because their
attributed A-D energies and coordinates are frozen in `inputs.json`.

## Reproduce

```sh
conda create --name smx-conformer-thermochemistry \
  --file research/smx-conformer-thermochemistry/conda-osx-arm64-explicit.txt

OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
conda run -n smx-conformer-thermochemistry \
  python research/smx-conformer-thermochemistry/run_experiment.py --force
```

`--force` is what makes this an end-to-end rerun. The repository ships the
completed run directories, so without it the runner skips every xTB call and
only rebuilds the analysis from the committed outputs.

The explicit lock is platform-specific. On another architecture, pin xTB 6.7.1,
Python 3.14.6, and NumPy 2.5.0, record the solved environment separately, and
describe the run as a cross-platform replication rather than byte-identical
environment reproduction.
