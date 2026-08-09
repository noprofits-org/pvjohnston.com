# Locked execution environment

The reviewed production environment is Linux x86-64, CPython 3.12.3, NumPy
2.5.1, and Matplotlib 3.11.1. Publication tooling uses Node.js 24.18.0. The
machine-readable record is `environment.json`; `requirements.lock.txt` pins
every Python package selected for CPython 3.12 on Linux x86-64 to the exact
wheel digest observed during setup.

Create the untracked environment from the repository root with an interpreter
that reports exactly `Python 3.12.3`:

```sh
python3.12 -m venv research/muon-survival-two-frames/.venv
research/muon-survival-two-frames/.venv/bin/python -m pip install \
  --require-hashes \
  -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/verify_setup.py
```

On the setup host, Ubuntu's interpreter lacked `ensurepip`. The isolated venv
was therefore created with `--without-pip`, and pip 26.2.1 was bootstrapped
from PyPA's 2026-08-04 `pip.pyz` (1,759,056 bytes; SHA-256
`91d5fd9f6f25549fd839c60536c6f1b945316ce3588d34a605635b6071c91526`)
before the hash-locked install. The lock itself includes pip 26.2.1 and its
wheel digest, so the resulting package manager is checked with the rest of the
environment. This bootstrap exception changes neither the interpreter nor the
package lock. A host with standard venv support does not need it.

The runner sets the process locale to `C` and timestamps to UTC before writing
artifacts. It rejects any Python or NumPy version other than the registered
ones and verifies the locked Matplotlib installation by package metadata. It
makes no network request and uses no GPU or external service. A fresh run
manifest records the actual OS, architecture, interpreter, packages, command,
and timestamps so that a platform deviation cannot be silent.

The lock is deliberately platform-specific: another architecture or Python
minor version requires prospective setup review (or the amendment route after
exposure), not an unhashed fallback or source build.
