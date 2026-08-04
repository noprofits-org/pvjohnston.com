# Environment

The registered Arm B run used the existing `research` conda environment on the
experiment host; `conda-linux-64.lock` records its exact package artifacts.
Arm A and the analysis layer are arithmetic on committed files and need only
the Python standard library; the metrics projection needs only Node.

- Operating system and version: Ubuntu 24.04.4 LTS (Linux 7.0.0-28-generic)
- Architecture: x86_64
- Hardware: 8-core x86_64 laptop ("flexpad"); Psi4 ran with 7 threads and
  9 GB of memory
- Interpreter: CPython 3.10.13
- Dependency manager: conda 25.3.1; see `conda-linux-64.lock`
- Quantum-chemistry package: Psi4 1.9.1 (conda-forge); NumPy 1.26.4
- Methods: frozen-core DF-MP2 optimization and frozen-core DF-CCSD(T) energy,
  cc-pVTZ and cc-pVDZ, energy and density convergence 1e-9
- Random seeds and nondeterministic operations: none in the method; the
  committed results were produced with 7-thread BLAS, which can reorder
  floating-point reductions between runs at the last-digit level, ten orders
  of magnitude below every registered decision margin. The analysis layer is
  deterministic from the committed run records.
- Locale/timezone: Psi4 output records host local time (PDT); result
  generation uses UTC
- Required environment variables: none required; `OMP_NUM_THREADS` limits
  BLAS threading for a stricter rerun, `PSI_SCRATCH` names scratch space
- External services: none. Every Arm B number is produced locally; every
  Arm A number is transcribed from the source's published tables and frozen
  in `inputs.json`.

The source article and its Supporting Information are not required during
execution because the transcribed values are frozen in `inputs.json`; see
`sources.json` for acquisition.

## Reproduce

```sh
conda create --name cepb-increment-spread \
  --file research/cepb-increment-spread/conda-linux-64.lock

OMP_NUM_THREADS=1 conda run -n cepb-increment-spread \
  python research/cepb-increment-spread/run_armb.py --basis cc-pVTZ --force
OMP_NUM_THREADS=1 conda run -n cepb-increment-spread \
  python research/cepb-increment-spread/run_armb.py --basis cc-pVDZ --force

python3 research/cepb-increment-spread/analyze.py
node research/cepb-increment-spread/generate-metrics.mjs
node scripts/verify-metrics.mjs
```

`--force` is what makes this an end-to-end rerun: the repository ships the
completed run directories, and without it the runner recognizes them as
complete and skips every Psi4 call. Passing `--force` deletes nothing on its
own but recomputes and overwrites each molecule/basis record. The full
registered set is under an hour of wall time on the hardware above.

The explicit lock is platform-specific (linux-64). On another platform, pin
Psi4 1.9.1, Python 3.10, and NumPy 1.26, record the solved environment
separately, and describe the run as a cross-platform replication rather than
a byte-identical environment reproduction.
