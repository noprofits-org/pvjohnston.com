# Environment

## M1

Recorded before the canonical run. Fresh venv at `~/Molecules/ist-borazine/.venv/`,
created with the host `python3 -m venv`; installed with `pip install "pyscf==2.14.*"`.
The exact installed dependency versions below record this pip-wheel environment.

```text
$ sw_vers
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
$ sysctl -n machdep.cpu.brand_string hw.memsize hw.perflevel0.physicalcpu
Apple M1 Pro
34359738368
8
$ ~/Molecules/ist-borazine/.venv/bin/python --version
Python 3.13.12
$ uname -m
arm64
```

- Architecture (`platform.machine()`): arm64
- Memory: 34359738368 bytes (32 GiB); eight performance cores.
- Timezone: America/Los_Angeles; queue timestamps use UTC ISO 8601.
- No random seeds are set by the supplied scripts; floating-point ordering and
  library implementation can affect numerical reproducibility.

### Installed versions

- pyscf==2.14.0
- numpy==2.5.3
- scipy==1.18.1
- h5py==3.16.0
- setuptools==84.0.0
- pip==26.0

### BLAS and threads

NumPy reports Apple Accelerate for BLAS/LAPACK. `otool -L` shows the PySCF
`libcgto.dylib` and `libnp_helper.dylib` linked to Apple Accelerate.
The queue exports `OMP_NUM_THREADS=8`, as requested. This PySCF arm64 wheel
reports `lib.num_threads() == 1`; its explicit thread-setting probe warns
"OpenMP is not available." Accelerate threading is separate and is not measured
by that counter. The anticipated runtime is therefore unverified on this wheel.

### Pre-freeze smoke test

Water only: conventional RHF/def2-SVP converged; density-fitted RADC(2)-ee with
`def2-svp-ri` returned two roots; UADC(2)-ee returned four roots. With
`compute_spin_square=False`, the exact production path
`ua._adc_es.get_spin_square()` returned approximately `[2, 0, 2, 0]`.
The spin-square path worked; no RADC-matching fallback was needed.
Logs and the structured smoke result remain outside the repo in the run directory.
