# PR and CI receipt, version 1

- Coordinator actor (self-asserted process ID):
- PR number and durable URL:
- Candidate content commit reviewed:
- Content-artifact paths and digests:
- Base branch:
- Cheap worktree checks and results:
- Full CI run URL and result:
- Human review status and unresolved threads:
- Changes made after `editorial_review` approval:
- Earlier scientific/editorial approvals affected by those changes:
- Expected cumulative attestation-only descendant delta from the candidate
  (PR/review receipts, evidence snapshots, and ledger events only):
- Public-bundle and rendered-site inspection:
- Residual risks:
- Requested gate: `pr_review`

Keep this receipt small under `research/<experiment-slug>/workflow/`. Use
repository-relative paths or durable external identifiers; never record local
absolute checkout, home, scratch, cache, or mounted-data paths. `ready_for_pr`
submits this receipt; only independent `pr_review` may advance to
`ready_to_merge`. Recording that review creates an attestation-only descendant;
the human integrator must wait for green CI on the resulting head and confirm
that its cumulative delta from the candidate is limited to the PR/review
receipts, evidence snapshots, and ledger events before merge.
