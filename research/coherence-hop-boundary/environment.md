# Environment

This records the frozen execution boundary for the reviewed experiment.
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
  canonical scientific outputs do not record the rerun clock
- Required environment variables: `OPENBLAS_NUM_THREADS=1`; no secret values
- External services and models: none

## Determinism

The archived local-magnitude Wigner samples and hopping draws are fixed by seeds
2701, 2702, 2703, and 2704. Corrective multi-seed fine/finer convergence uses seeds 2687–2694.
Pilot seed 1701, the original seed-2699 convergence run, and review diagnostics
are excluded from the corrective result. Each replicate constructs its random
stream from its declared seed rather than from worker order, and output records
are sorted by frozen setting, rate-scale order, and seed. Changing `--workers`
may change wall time but must not change canonical bytes.

Canonical lineage, corrective convergence, corrected legacy exact and sweep,
and analysis JSON excludes wall-clock runtimes and generation timestamps. The
metrics schema requires a `generated_at` field; the generator reads its fixed
source-date epoch from the corrective amendment in `config.json` instead of the
execution clock. Corrected legacy artifacts retain source hashes, and the
corrective convergence artifact records the hash of its uncompacted source.

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

Then follow the reviewed analysis and artifact commands in `README.md`. The
corrective lineage and eight-pair convergence gate completed, but the gate
failed and correctly blocked exact-audit and production commands. The reviewed
bundle is traceable and reproducible through that stopping point; it does not
claim a completed phase-sensitive production experiment.

The source authors' locally modified SHARC program and molecular inputs are
not part of this environment. The only inherited executable input is the
repository archive identified and checksummed in `sources.json`.
