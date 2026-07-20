# Environment

- Operating system: macOS 26.5.2 (Darwin 25.5.0)
- Architecture: arm64
- Calculation interpreter: CPython 3.13.12
- Metrics generator: Node.js 24.8.0
- Third-party dependencies: none
- Locale and timezone dependencies: none
- Random inputs: none
- Wall clock: used only to stamp a newly written `metrics.json`; calculation
  results and the metric payload are deterministic
- External services, models, credentials, or environment variables: none

The calculation uses only Python's standard `json`, `math`, `sys`, and
`pathlib` modules. The projection generator uses only Node.js standard-library
modules.
