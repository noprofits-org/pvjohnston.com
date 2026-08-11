# Environment

No ecosystem lockfile covers the interpreter itself; `requirements.txt` pins
the single dependency. Canonical run recorded 2026-08-11.

- Operating system and version: macOS 26.5.2 (25F84)
- Architecture: arm64 (Apple Silicon)
- Interpreter/compiler and version: CPython 3.13.12, `~/.venvs/gwc` virtual
  environment (`python3` on PATH resolves to it)
- Dependency manager and version: none used; numpy 2.4.4 already installed
  (pinned in `requirements.txt`). Figure generation additionally uses
  matplotlib (version recorded in the post's Methods) from a disposable
  project-local venv; no result artifact depends on it.
- Hardware assumptions: 10 CPU cores; the sweep uses 8 worker processes.
  Results are independent of worker count and execution order (every cell is
  seeded); wall time is not.
- Locale/timezone: en_US.UTF-8 / America/Los_Angeles (irrelevant to results)
- Random seeds and nondeterministic operations: all randomness enters through
  `numpy.random.default_rng` with explicit seeds (init 7000+rep, data
  1000+17*32+rep). No unseeded draws. BLAS thread-count differences shift
  roundoff-scale digits only; see the post's Methods.
- Required environment variables (names only): none
- External services, models, and dated version identifiers: none
