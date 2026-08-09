# Setup-review receipt

- **Gate:** `setup_review`, iteration 4
- **Actor:** `setup-reviewer-muon-06`
- **Decision:** `revise`

## Reviewed artifacts

- `.codex/agents/independent_reviewer.toml` — SHA-256
  `a584f9069f557310f37cbfa6f5e1279af4891e15fb3f525739a7a747fdeda561`
- `notes/computational-authoring-workflow.md` — SHA-256
  `798c5a1e7f443fdbfe81c5cf30b6a20ef21f158027daa0fe08addc731a68afed`
- `notes/blog-authoring.md` — SHA-256
  `d512c6ffc45f3775002e4eb22531667cb4eda879994e17d2e8a2f030cec457c7`
- `research/muon-survival-two-frames/workflow.jsonl` — SHA-256
  `d7742afea3840f948eae88561ce6f0606b3b1812ca283446b4b6b7db2da11cb7`
- `research/muon-survival-two-frames/workflow/setup-v4.md` and its evidence
  snapshot — SHA-256
  `dbf9db13bcf40b394b25ca95dc8fa96754c3aac28b521079c0d441460e5c5149`
- Prior setup reviews v1/v2/v3 — SHA-256
  `5a00feedb7b16c194ec9b02042ee3e8898b06b9c78cfb8d2d994fbe238145944`,
  `133c467303f44437be95ebd1a838f51261ebdb65c2630ab6f8f4db0afa46128f`,
  and `d4ab02dbb5471ee3f719395a6b66f48ee472168d3de40377721bc7aa2adf7383`.
- `research/muon-survival-two-frames/setup-manifest.json` — SHA-256
  `23d4dc17f8f753c5dbe3a23ac2da38e615b1510732e403e4f18dcd16377673bd`;
  reviewed every one of its 33 exact path/size/digest records and the supplied
  corresponding bytes.

## Blocking findings

1. **High — metrics still do not consume a fully validated result contract.**
   `validate_analysis_result()` checks check-field names/types and aggregate
   consistency, but does not recompute the six pass booleans, detail values, or
   diagnostic values. `generate-metrics.mjs` directly projects those unchecked
   booleans and diagnostics. A finite but false standard error, discrepancy,
   detail value, or mutually consistent pass/all-passed mutation can therefore
   reach `metrics.json`. The regression only removes a detail field; it does
   not mutate a detail value, diagnostic, pass flag, analysis-admission
   identity, or `source_run.run_id`. The validator also does not bind the
   admission record back to the replayed ledger or semantically bind
   `source_run.run_id` to its manifest/completion records.

2. **High — exact-byte replay remains incomplete for the verifier and graph.**
   `validate_workflow_ledger()` hashes `graph_path` and `workflow_cli_path`,
   then later invokes those pathnames. Unlike the ledger, receipts, and
   snapshots, their exact captured bytes are not staged or consumed.
   Replacement between hashing and subprocess open can therefore make
   authorization depend on verifier/graph bytes that were never hash-approved.
   The new replacement tests cover ledger and snapshot paths only.

3. **Medium — the registered retry lacks an exact downstream analysis
   contract.** The protocol permits admitted `run-002`, and the implementation
   can accept it, but `inputs.json` and `README.md` freeze analysis/check
   commands only for `run-001`. An infrastructure retry that succeeds cannot
   follow the documented exact analysis command without an undocumented
   substitution.

4. **Medium — the prospective public README is stale.** `README.md` says setup
   iteration 3 is current although the bound submission is iteration 4. It is
   listed in the prospective publication allowlist and setup manifest.

## Nonblocking observations

The supplied suite contains 25 test methods, and the receipt plus coordinator
report consistently state 25/25 passed. The 33-artifact count matches the
manifest, and `setup_validation()` rejects every entry under `runs/`,
supporting the reported `production_absent=true`. These execution claims were
not independently rerun under the assignment's no-tools constraint. Prior
atomic publication, stream capture, historical-ledger consumption,
bound-snapshot consumption, and negative-lifetime coverage defects appear
repaired.

## Route and scope

- **Required route:** `setup_review → setup`; no redesign or post-exposure
  amendment is warranted.
- **Validity versus outcome:** These are implementation, lineage, retry, and
  publication-contract failures only. No production quantity or scientific
  outcome was calculated or assessed.
- **Residual risks:** External PDG availability, cross-host wheel
  availability, installed-environment byte integrity, filesystem races at
  remaining pathname boundaries, and self-asserted actor identity.
- **Smallest next action:** Recompute and verify all registered checks,
  details, diagnostics, admission linkage, and run identity inside
  `validate_analysis_result()`, then add a metrics write/check regression that
  mutates one diagnostic and one pass/admission field while preserving schema
  shape.

## Independence and effort

Fresh read-only reviewer session, distinct from the producer, as confirmed by
the coordinator. The review used only supplied immutable bytes and no tools,
commands, network, production calculations, repository changes, workflow
transition, or prior artifact authorship. Actor strings remain
non-authenticating. Approximate review effort: 42 minutes.
