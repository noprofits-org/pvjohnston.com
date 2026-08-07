# Environment

- Operating system and version: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic.
- Architecture: x86_64.
- Interpreter/compiler and version: CPython 3.12.3.
- Dependency manager and version: the production run used a temporary Conda
  25.3.1 environment; the same direct Python dependencies can be installed
  from `requirements.txt` with pip in an ordinary virtual environment.
- Exact production solve: `environment-linux-64.lock` records the explicit
  Conda base URLs and builds; `requirements-lock.txt` records every pip-installed
  Python package. Install the second with `--no-deps` after creating the first.
- Numerical dependency: NumPy 2.4.4. Matplotlib 3.11.1 is used only to generate
  the figure and does not affect `results.json`.
- Hardware assumptions: any x86_64 CPU; no GPU. The registered machine has an
  Intel i7-1165G7 (4 physical / 8 logical cores) and 15 GiB RAM.
- Parallelism: two spawned scalar-lambda worker processes, each with OpenMP,
  OpenBLAS, MKL, and NumExpr thread counts forced to one before NumPy import.
- Locale/timezone: result generation is locale-independent; the run journal
  records America/Los_Angeles.
- Random seeds and nondeterministic operations: fold permutation seed 70220;
  initialization seeds 11, 29, 47, 71, and 101. There is no dropout or GPU
  execution. Worker completion order is sorted before serialization.
- Required environment variables: none. The runner sets `OMP_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` to 1.
- External services, models, and dated version identifiers: none.

The wrapper fingerprints the imported predecessor implementation and analytic
model in `results.json`; `verify_analysis.py` rejects a mismatch. Exact legacy
overlap is tested against `research/coulomb-force-training/results.json`, whose
current values were also generated with CPython 3.12.3 and NumPy 2.4.4.
