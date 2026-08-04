# Environment

- Operating system: Debian GNU/Linux (container)
- Architecture: x86_64
- Indexing and figure-coordinate interpreter: CPython 3.13
- Metrics generator: Node.js 22
- Third-party dependencies: none
- Locale and timezone dependencies: none — all dates are parsed and compared as
  UTC calendar dates taken from the message filenames
- Random inputs or nondeterministic operations: none
- Wall clock: not used; `provenance.generated_at` is a fixed literal so that a
  regeneration is byte-identical to the committed projection
- External services, models, credentials, or environment variables: none
- Hardware assumptions: IEEE 754 binary64 arithmetic

The indexing and figure scripts use only Python's `csv`, `json`, `datetime`,
`collections`, `pathlib`, `os` and `re` standard-library modules. The
projection generator uses only Node.js standard-library modules.
