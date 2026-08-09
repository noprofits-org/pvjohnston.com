# Stage handoff: stage name, version 1

- Graph state:
- Actor and role (self-asserted process ID):
- Parent submission/review snapshots:
- Protocol version and SHA-256:
- Git commit used:
- Work completed:
- Exact commands and exit states:
- Tests or integrity checks:
- Small artifacts submitted directly:
- Large/raw artifacts with repository-relative path or durable external URI,
  size, and SHA-256:
- Deviations, failures, and quarantined outputs:
- Incoming execution edge and frozen authorization (when applicable): normal /
  resume / registered_retry / registered_rerun
- Prior and new run IDs (when applicable):
- Outcome (if known): not inspected / Research supported / Research falsified /
  Research inconclusive / Understanding observations
- Requested review gate:
- Journal checkpoint and explicit next step:

Keep this receipt small under `research/<experiment-slug>/workflow/`. Do not
paste large logs or raw data, and do not record a local absolute checkout, home,
scratch, cache, or mounted-data path. This packet is snapshotted by
`scripts/research-workflow.mjs`; use a new versioned file after a revision.
