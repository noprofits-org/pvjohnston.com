# Environment

- Operating system: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic
- Architecture: x86_64
- Interpreter: CPython 3.12.3
- Dependency manager: pip 26.2.1
- Locked packages: `requirements.lock.txt`
- PySCF: 2.13.1
- NumPy: 2.5.1
- SciPy: 1.18.0
- h5py: 3.16.0
- Hardware: Intel Core i7-1165G7, 4 physical cores / 8 hardware threads,
  15 GiB usable RAM
- Locale: `C.UTF-8`
- Timezone: America/Los_Angeles
- Random seeds: none; the calculations use deterministic initial guesses under
  the pinned software stack, subject to normal floating-point/library behavior
- Required environment variables: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`, `BLIS_NUM_THREADS=1`,
  `VECLIB_MAXIMUM_THREADS=1`
- Network or external services: none during calculation

Immediately before production, the host was on AC power with light load, no
competing PySCF/sweep process, and 7.3 GiB available memory. The three phase
commands completed in 46.76 s, 4.87 s, and 2.26 s of parent-process wall time.
Available memory was still 7.3 GiB afterward. These are run conditions, not a
claim that the subsecond per-calculation timings transfer to other hardware.

The host lacks the Ubuntu `python3.12-venv` package. Phase one created a
pip-less stdlib venv and installed pip 26.2.1 into it using PyPA's official
`get-pip.py`, then installed the locked packages above. The venv itself is
ignored; it can be reconstructed from `requirements.lock.txt` on a host with
standard venv support or with the same bootstrap procedure.

The production handoff required an AC-power, CPU-governor, load, and memory
preflight. Its durable checkpoint retained AC power, qualitative light load,
and available memory, but not the exact governor value or numeric load average;
that omission further limits timing replication. PySCF's 3000 MB `max_memory`
value is an advisory library setting, not an OS-enforced RSS limit.

Post-run analysis uses CPython 3.12.3 and Matplotlib 3.11.1, pinned separately
in `requirements-analysis.txt`; it does not import PySCF or modify the raw
JSONL. The committed figure uses Matplotlib's bundled DejaVu Sans and the Agg
backend. The analysis package was added only after the production calculations,
so `requirements.lock.txt` remains the exact calculation-environment lock.
