# Hash-verified model outputs

Outputs are namespaced by dataset version and run kind:

- `DATASET/scheduled/analysis/MODEL__symbolic__CASE-XXXX__run-NN.md`
- `DATASET/scheduled/identification/MODEL__symbolic__CASE-XXXX__run-NN.md`
- `DATASET/diagnostic/TASK/MODEL__symbolic__CASE-XXXX__diagnostic-NN.md`

The `.md` file is byte-for-byte model stdout. Each invocation also creates a
`.run.json` sidecar, retained stderr, and a `.complete.json` marker written last.
The marker and sidecar bind the response to the frozen model adapter, prompt,
dossier, manifest, matrix, collection lock, timestamps, exit status, and
validation result.

Malformed or failed responses use `.invalid.md`. Files are collision-protected
and made read-only after bundle finalization. Read-only permissions are not
cryptographic immutability; the analyzer independently verifies every hash.
Never edit or replace an output. Scheduled runs are `01`--`03` only. Diagnostic
runs use their separate namespace and are excluded from the primary analysis.
