# Environment

This records the frozen execution boundary for the confirmatory experiment.
`requirements.txt` pins every direct third-party Python dependency used by the
simulator, analysis, and figure layer. The Python standard library supplies the
remaining functionality.

- Operating system: Linux
- Architecture: x86_64
- Interpreter: CPython 3.12.9
- Numerical package: NumPy 2.2.5
- Analysis and figure packages: Matplotlib 3.10.8; Pillow 12.1.0
- Dependency installation: `python3 -m pip install -r
  research/coherence-hop-boundary/requirements.txt`
- Hardware assumptions: CPU execution; enough memory for two-state 512 by 512
  complex wavepacket arrays; no GPU or laboratory hardware
- Parallelism: independent scale/seed replicates may use worker threads;
  `OPENBLAS_NUM_THREADS=1` is required so each worker's array reductions remain
  single-threaded
- Locale/timezone: no numerical input depends on locale or civil time;
  generated provenance timestamps use UTC
- Required environment variables: `OPENBLAS_NUM_THREADS=1`; no secret values
- External services and models: none

## Determinism

The confirmatory Wigner samples and hopping draws are fixed by seeds 2701,
2702, 2703, and 2704. The independent numerical-convergence run uses seed 2699.
Pilot seed 1701 is excluded from confirmation. Each replicate constructs its
random stream from its declared seed rather than from worker order, and output
records are sorted by the frozen rate-scale order and seed. Changing
`--workers` may change wall time but must not change a canonical result.

The exact split-operator propagation contains no stochastic operation. The
lineage gate checks the bytes of the inherited archive and compares the
parameterized `s=1` path with its archived ancestor before any confirmatory
run. Floating-point results outside this pinned platform may differ in their
last bits; scientific equivalence is governed by the frozen numerical and
grid-audit tolerances, not byte identity across platforms.

## Intended reproduction

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r research/coherence-hop-boundary/requirements.txt
export OPENBLAS_NUM_THREADS=1
python3 -m unittest discover -s research/coherence-hop-boundary/tests -v
```

Then run the lineage, convergence, exact-audit, sweep, analysis, and metrics
commands in `README.md` in order. At protocol freeze, those commands had not
been completed and traceability was **not yet established**. The canonical run
subsequently completed that command chain and repository verification, earning
the **end-to-end reproducible** claim for this pinned environment.

The source authors' locally modified SHARC program and molecular inputs are
not part of this environment. The only inherited executable input is the
repository archive identified and checksummed in `sources.json`.
