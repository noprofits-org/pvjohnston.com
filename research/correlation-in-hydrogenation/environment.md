# Environment

The full run depends on the native psi4 build, so the environment is pinned by
an explicit conda lock rather than by `pip`. The analysis gate
(`calculate.py --check`) and the metrics projection use only the Python and
Node standard libraries.

- Operating system and version: Ubuntu 24.04.4 LTS (Linux 7.0.0-28-generic)
- Architecture: x86_64
- Interpreter/compiler and version: CPython 3.10.13; psi4 1.9.1
- Dependency manager and version: conda 25.3.1; see `conda-linux-64.lock`
- Hardware assumptions: any x86_64 CPU; ~2 GB RAM (psi4 memory set to 2 GB);
  no GPU. The largest single points are CCSD(T)/cc-pVTZ on ethane- and
  methanol-sized closed-shell molecules — minutes each; the whole set is
  well under an hour on a laptop.
- Locale/timezone: UTC
- Random seeds and nondeterministic operations: none. SCF, geometry
  optimization, and CCSD(T) are deterministic at the tight convergence
  thresholds in `inputs.json`. Threaded BLAS can reorder floating-point
  reductions, so set `OMP_NUM_THREADS=1` to avoid changes in threaded
  floating-point reduction order.
- Required environment variables (names only; never commit values or secrets):
  `OMP_NUM_THREADS` (set to 1), `PSI_SCRATCH` (optional scratch path).
- External services, models, and dated version identifiers: none. Every number
  is produced locally by psi4 1.9.1; there are no experimental or literature
  inputs.

## Reproduce

```
conda create --name correlation-in-hydrogenation \
  --file research/correlation-in-hydrogenation/conda-linux-64.lock
OMP_NUM_THREADS=1 conda run -n correlation-in-hydrogenation \
  python3 research/correlation-in-hydrogenation/calculate.py     # writes results.json (< 1 h, CPU)
node research/correlation-in-hydrogenation/generate-metrics.mjs  # writes metrics.json
node scripts/verify-metrics.mjs                                  # verifies fingerprints + projection
```
