# Environment

The demonstration uses only the Python standard library, so no dependency
lockfile exists for it; this file records the execution boundary instead.

- Operating system and version: Debian GNU/Linux (kernel 7.0.0-28-generic)
- Architecture: x86_64
- Interpreter/compiler and version: Python 3.12.3 (`python3`)
- Dependency manager and version: none — standard library only (`math`,
  `random`, `json`, `pathlib`)
- Hardware assumptions: none; runs in seconds on one CPU core
- Locale/timezone: not relevant — no dates, locale-dependent formatting, or
  timestamps in any output
- Random seeds and nondeterministic operations: `random.seed(0)` is the only
  randomness; draws are consumed in a fixed order (four example centres, then
  ensembles of 10, 100, and 10,000), so all outputs are bit-reproducible
- Required environment variables: none
- External services, models, and dated version identifiers: none
