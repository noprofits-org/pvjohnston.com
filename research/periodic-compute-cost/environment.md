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

The host lacks the Ubuntu `python3.12-venv` package. Phase one created a
pip-less stdlib venv and installed pip 26.2.1 into it using PyPA's official
`get-pip.py`, then installed the locked packages above. The venv itself is
ignored; it can be reconstructed from `requirements.lock.txt` on a host with
standard venv support or with the same bootstrap procedure.

The production session must append its AC-power state, CPU governor, load
average, and available memory immediately before the first phase. PySCF's
3000 MB `max_memory` value is an advisory library setting, not an OS-enforced
RSS limit.
