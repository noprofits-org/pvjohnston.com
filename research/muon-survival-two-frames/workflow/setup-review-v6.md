# Setup-review receipt

- **Gate:** `setup_review`, iteration 6
- **Actor:** `setup-reviewer-muon-08`
- **Decision:** `revise`

## Artifact inventory

Reviewed the reviewer definition (`a584f906…eda561`), computational workflow
(`798c5a1e…8afed`), authoring guide (`d512c6ff…57c7`), workflow ledger
(`559ee50b…903fb`), setup-v6 snapshot (`5c2dbb45…0944fd`), setup-review-v5
(`9165f1e1…91cd27`), and setup manifest (`4fe3d8bb…d645e`) covering
all 33 exact path/size/digest records. Focused bytes included protocol
`501f57ab…377`, `src/analyze.py` `31b76513…6a84`, `src/contract.py`
`0e39a47f…61991`, pipeline tests `f5848e8a…b1e40`, workflow fixture
`4478a1e4…5fc49`, graph `e50f1247…8d404`, and verifier
`f8b93115…515f2c`.

## Blocking findings

1. **High — submitted tests are state-dependent and no longer replayable at
   the reviewed gate.** `WorkflowFixture.__init__()` copies the current
   16-event ledger, whose state is `setup_review` with submission 16 pending.
   `approve_setup()` then appends a new `setup → setup_review` submission,
   although replay requires the next event to originate from `setup_review`.
   Thus workflow-backed tests could pass before submission 16, as reported,
   but the exact submitted artifact set cannot reproduce those tests during
   review or later stages.

2. **Medium — canonical derived-output publication is exclusive, not atomic or
   restart-safe.** `write_bytes_exclusive()` opens the final result/PNG path
   directly before writing; the metrics generator likewise writes directly to
   its final path with `wx`. Interruption can expose a partial final artifact
   that subsequent commands refuse to replace. No quarantine or recovery
   contract exists for these derived outputs.

## Nonblocking observations

The registered analysis route now imports `validate_digest_record` and reaches
`main → registered_analysis_spec → validate_run_bundle/analysis_admission →
derive_integrity_flags → build_analysis_result` for both registered run IDs.
Admission consumes hash-bound snapshot bytes, requires one exact column-zero
admitted-run marker, rejects missing, duplicate, conflicting, malformed, and
unregistered markers plus both cross-pairs, while ignoring incidental prose.
Protocol choices, independent frame reconstruction, failure branches,
raw-to-result-to-metrics recomputation, schemas, provenance, hashes,
normal/retry authorization, no-resume rule, budget, and toy/production
separation are otherwise coherent. Coordinator-reported 28/28 timing, 33
entries, zero sockets/namespaces, and `production_absent=true` were not
independently executed under the no-tools review constraint.

## Route and scope

- **Required route:** `setup_review → setup`; no redesign, park, or
  post-exposure back-edge.
- **Validity versus outcome:** Findings concern fixture durability and artifact
  publication integrity only. They say nothing about frame agreement, survival
  probability, novelty, a hypothesis, or a verdict.
- **Residual risks:** PDG availability, cross-host wheel availability,
  installed-environment byte integrity, untested filesystem semantics, and
  self-asserted actor identity.
- **Smallest next action:** Seed workflow fixtures from a stable synthetic
  ledger independent of live graph state, then implement staged-and-atomically
  installed derived outputs with interruption/recovery tests; rerun the bounded
  suite on the resubmitted bytes.

## Independence and effort

Fresh read-only reviewer, coordinator-confirmed distinct from producers and all
prior reviewers. No tools, filesystem access, network, calculations, edits, or
workflow transition were used. Actor IDs remain non-authenticating.
Approximate effort: 55 minutes.
