# Setup-review receipt

- **Gate:** `setup_review`, iteration 5
- **Actor:** `setup-reviewer-muon-07`
- **Decision:** `revise`

## Exact artifact inventory

- `.codex/agents/independent_reviewer.toml` — 4,232 bytes — SHA-256
  `a584f9069f557310f37cbfa6f5e1279af4891e15fb3f525739a7a747fdeda561`
- `notes/computational-authoring-workflow.md` — 38,159 bytes — SHA-256
  `798c5a1e7f443fdbfe81c5cf30b6a20ef21f158027daa0fe08addc731a68afed`
- `notes/blog-authoring.md` — 51,664 bytes — SHA-256
  `d512c6ffc45f3775002e4eb22531667cb4eda879994e17d2e8a2f030cec457c7`
- `research/muon-survival-two-frames/workflow.jsonl` — 14,535 bytes —
  SHA-256
  `539af70a33e9258a1f6c6894ae5004ea225c66c419689617e84d2e7b89738b79`
- `workflow/evidence/0014-01-5014d608-3971-41d5-ab20-0f796ab8fdc6-setup-v5.md`
  — 9,516 bytes — SHA-256
  `f0ba7bebf3b53a92ed3993d32241146265953bda88fd1f4abdbbf461eadf8258`
- Prior setup reviews v1 through v4 — SHA-256
  `5a00feedb7b16c194ec9b02042ee3e8898b06b9c78cfb8d2d994fbe238145944`,
  `133c467303f44437be95ebd1a838f51261ebdb65c2630ab6f8f4db0afa46128f`,
  `d4ab02dbb5471ee3f719395a6b66f48ee472168d3de40377721bc7aa2adf7383`,
  and `bb7b0c74b0dd7ec0c6f7512d19ed7432943278048b2639b937284e87a8ac51b6`.
- `setup-manifest.json` — 5,547 bytes — SHA-256
  `a9d4679f276ef51f4532b6413e099ffc0a5e96cf6b4256c9bba7790566a1395f`;
  reviewed all 33 exact path/size/digest records and their corresponding
  supplied bytes, including protocol `501f57ab…7bb855c`, graph
  `e50f1247…418d404`, and verifier `f8b93115…515f2c`.

## Blocking findings

1. **High — canonical analysis cannot execute.** `derive_integrity_flags()`
   calls `validate_digest_record()`, but `src/analyze.py` does not import that
   name. `registered_analysis_spec()` necessarily reaches this call for both
   `run-001` and `run-002`, causing `NameError` before result generation. The
   26 supplied tests bypass this path by constructing `AnalysisSpec` directly,
   so the green suite does not detect the failure.

2. **High — admitted-run identity remains ambiguous.**
   `analysis_admission()` accepts a run when its ID occurs anywhere as a
   substring in any approval snapshot. It does not require a unique structured
   admitted-run field or reject evidence mentioning both registered IDs. A
   retry review will naturally mention preserved `run-001` while admitting
   `run-002`, allowing either downstream command pair to authenticate against
   the same approval. Existing tests use single-ID toy receipts and do not test
   `run-001`/`run-002` cross-selection.

## Nonblocking observations

Raw-to-metrics recomputation, raw-derived empirical arrays, full
check/detail/diagnostic comparison, schema/hash provenance, captured
ledger/snapshot/graph/verifier consumption, registered-retry commands,
toy/production separation, exclusive output creation, process-stream capture,
and README status are materially implemented. The supplied suite contains 26
bounded methods, and the 33-entry manifest plus all-namespace absence check
support the coordinator's artifact-count and `production_absent=true` report.
Pass timing and zero socket messages were coordinator-reported rather than
independently executed under the review's no-tools constraint.

## Route and scope

- **Required route:** `setup_review → setup`; neither redesign nor park is
  warranted.
- **Validity versus outcome:** These are execution and admission-lineage
  validity defects only. They say nothing about frame agreement, survival
  probability, Monte Carlo observations, novelty, a hypothesis, or a
  scientific verdict.
- **Residual risks:** External PDG availability, cross-host wheel availability,
  installed-environment byte integrity, filesystem semantics outside the
  tested races, and self-asserted actor identity.
- **Smallest next action:** Import `validate_digest_record`, add a test
  exercising `registered_analysis_spec()` through `derive_integrity_flags()`,
  then require one exact structured admitted-run ID in run-review evidence and
  test both cross-pair substitutions before resubmission.

## Independence and effort

Fresh read-only reviewer session, distinct from producers and prior reviewers
as coordinator-confirmed. The review used no tools, commands, filesystem
access, network, calculations, edits, workflow transition, or prior artifact
authorship. Actor labels remain non-authenticating. Approximate effort: 47
minutes.
