# Environment

- Operating system: macOS 26.5.2 (Darwin 25.5.0)
- Architecture: arm64
- Calculation interpreter: CPython 3.13.12
- Metrics generator: Node.js 24.8.0
- Third-party dependencies: none
- Locale and timezone dependencies: none
- Random inputs or nondeterministic operations: none
- Wall clock: used only to stamp a newly written `metrics.json`; calculation
  results and the metric payload are deterministic
- External services, models, credentials, or environment variables: none
- Hardware assumptions: IEEE 754 binary64 arithmetic and the documented
  interpreter's standard `math` and `cmath` implementations

The calculation uses only Python's `cmath`, `json`, `math`, `sys`, `pathlib`,
and `typing` standard-library modules. The projection generator uses only
Node.js standard-library modules.
