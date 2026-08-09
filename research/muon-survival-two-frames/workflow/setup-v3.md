# Setup handoff: version 3

- **Graph state:** `setup`, iteration 3.
- **Actor and role:** `experiment-engineer-muon-trial`, configured
  `experiment_engineer` session.
- **Revision parent:** `workflow/setup-review-v2.md`, decision `revise`, 4,921
  bytes, SHA-256
  `133c467303f44437be95ebd1a838f51261ebdb65c2630ab6f8f4db0afa46128f`.
- **Protocol:** `PREREGISTRATION-v1.md`, unchanged at 19,383 bytes and SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- **Outcome boundary:** no canonical seed, draw count, full grid, focal
  calculation, run namespace, result, metric, or publication figure was
  executed, created, or inspected. Executed tests used only seed 0 with at most
  16 draws and synthetic temporary paths.
- **Requested gate:** fresh independent `setup_review`.

## Revised binding

The accepted version-2 setup manifest bound 29 files, was 4,924 bytes, and had
SHA-256
`7b31d42a48de0ec7b616ee0364f969775909b9c5ef398d97e14870f172cee1ed`.
The version-3 manifest binds 32 files, is 5,380 bytes, and has SHA-256
`2f23811352b56843a5533f254108bb2befe30287945d24f53366e82a6e5c0e2f`.
The three added bindings are the complete synthetic workflow fixture and the
unchanged shared graph/verifier bytes used by execution admission:

- `tests/workflow_fixture.py`: 6,183 bytes,
  `38bd59f2574b85370e0ba61e8d948bf9c3267ac9b30acc072753e0af277242a0`;
- `research/workflow.graph.v1.json`: 12,050 bytes,
  `e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404`;
- `scripts/research-workflow.mjs`: 79,852 bytes,
  `f8b931150fe5c31f574fa6303cd1d9b629ad02b0e05233025288e30275515f2c`.

| Material artifact | Version 2 SHA-256 | Version 3 SHA-256 |
| --- | --- | --- |
| `inputs.json` | `da290f0ce43c12f788d923623bc7dc092285719d6d1716d76447a0fc013cc02f` | `c80d63efc7efb9ac430aa787ec5fa5518cb3238e99cb159174302b2249968169` |
| `schemas/analysis-result.schema.json` | `ecc41038045a1c1110d9a8a8d69b973bf25834310a38063a59ece912dd55c982` | `be5fb5fe7bdbbb5fcf1d8d6c3df80ece526ed21ed24e5ee8ba8d2c92c43c6eec` |
| `schemas/inputs.schema.json` | `0d8c72dd6f1b3081fb2cd3513051534e879358db7f7199c6a732c9337eec0e80` | `0190b2c580cbd5df1bb7aeac9572bc12d898feff2ec45d7093c9a2592e1a7edd` |
| `schemas/run-manifest.schema.json` | `3f315b170a3ddb18393a584919568d76c27bd45317f2cfe04559422a823482ac` | `23908b4594a3baa066e223f52bc972d214b069ed264cc3600e34121ebe7e9396` |
| `src/analyze.py` | `b90a8da6508a8dca73461eebdca53e6e134671dae44e78eb8491a25475d06743` | `eb65352951dd2ba11fcd9dca022263778a53d07776c9d254eb42907904356b4c` |
| `src/bundle.py` | `607188d612ab921c92b658134985695bec92f5bb50ead78f759e2f28c75d03de` | `0f81c227593f6545d8527fabc8589518c3886d6c00c13ed8f1e15de73338d9bc` |
| `src/contract.py` | `2b6c6aab3e68fff4d524bd91a3428a0d7c3f6370330693e3bb5691d22a471471` | `4d70e01de6116854db28f7004429f3ef14e9b28dd44a99192ce11b097b3a434b` |
| `src/reconstruct.py` | `f892f4c9aacaca6de1668aad92953a500f4b7b644d5bd75d44a6111d89adaec8` | `962f01c6bb94458ddedec008e5e5f4215170cb0475b992bc72d5a728c650e6c4` |
| `src/render_figure.py` | `8b99133bbd70877885437b33de5791ff28025f88a3b9f4c3e015ee49f8456ccc` | `aec14d05ca3ae44cf1b4077e43df2148661dafbd0d341b0cb31103d7131762fc` |
| `src/run.py` | `947b4163bf9b5889d0c2dbd667b77bb3e6b8f56ea9ea5375558cc15462f67ec3` | `eec8ce19b3229ca2e6a4d1a42afa7aefc8e1d34a006314ecb38bd20f83bfc731` |
| `tests/test_pipeline.py` | `cec6cf3dd13de6e4f14358532d85f3cab05887bf433131f1cbe0604d59c49cfd` | `6bef4333480980a4ef814d621506193b5df0bbe7fc012039a93c490a56182d10` |
| `tests/test_setup.py` | `4ca0d4a90f96ecd15ca532f2ba73a25670fd88beef81be28c2a9c99eb5b71e58` | `52b4eaac72f9e6b4dcb87e5037c7a61b2a21afed4d663e29bc3397af5a4e1335` |

The complete repository-relative sizes and digests are authoritative in
`setup-manifest.json`.

## Review blockers mapped to fixes

| Setup-review-v2 blocker | Version-3 fix and evidence |
| --- | --- |
| 1. Result check admission failed after analysis submission. | `analysis_admission()` first requires a complete successful graph/evidence replay, then locates the unique requested historical event ID anywhere in the immutable ledger. It verifies `run_review --approve--> analyze`, submission linkage through replay, and the snapshot that names the run, and hashes the exact event line. A full synthetic ledger advances through `analyze -> analysis_review`; the earlier approval still validates and its sequence is proved older than the final event. |
| 2. Run authorization checked a minimal event shape rather than the graph. | `validate_workflow_ledger()` invokes the repository's read-only verifier whose exact bytes and graph are now input- and setup-manifest-bound. That verifier checks experiment, schema/graph version and digest, sequence, UUIDs/timestamps, owning branch, roles, allowed transitions, journal IDs, submission/review linkage, asserted actor separation, evidence snapshots, replay state, active receipt drift, and orphan snapshots. Authorization then applies the frozen current-edge and namespace rules. Complete normal/retry fixtures pass; the previous underspecified one-line review event fails graph replay. Recorded authorization now also binds graph version/digest and submission sequence. |
| 3. Schema, manifest, provenance, and hashes were asserted. | The bounded Draft-2020-12 validator now executes the keywords used by the bound schemas. Run validation applies the run-manifest and completion schemas, exact runtime contract, artifact inventory, recorded authorization/lineage, checksums, completion links, and raw-array validation before deriving separate `schema_valid`, `manifest_valid`, `provenance_valid`, and `hashes_valid` results. Analysis derives its six integrity flags from those results, resolved digest records, and the validated admission. It performs a provisional result-schema validation before setting the schema flag, revalidates the final result, and every write/check plus publication render validates the bound result schema, array lengths, frozen primitives/grid, all frame/counterfactual derivations, focal projection, counts, check structure, and resolvable provenance. No production flag is a literal success assertion. |
| 4. Failure branches remained coupled or representative. | The focal four-standard-error fixture now fails while monotonic counts and the relaxed grid-discrepancy branch pass. The upper-bound fixture is monotonic while its bound detail fails. Lower bound, zero count, monotonicity, dtype, and empirical equality each have their own mutation and detail assertion. Separate loops mutate every detector field, every muon field, every counterfactual field and label, every unit in all four namespaces, each primitive, the grid, raw dtype/finite validity, each frame-agreement subcheck, and each integrity flag. |

The iteration-1 atomic raw creation and real descriptor-level stdout/stderr
repairs remain unchanged in behavior and continue to pass their race,
success-lineage, failure-traceback, and tamper regressions.

## Commands and results

The final bounded setup-only pass ran:

```sh
research/muon-survival-two-frames/.venv/bin/python -m pip install --dry-run --require-hashes -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python -m pip check
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/verify_setup.py
research/muon-survival-two-frames/.venv/bin/python -m unittest discover -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
research/muon-survival-two-frames/.venv/bin/python -m compileall -q research/muon-survival-two-frames/src research/muon-survival-two-frames/tests
node --check research/muon-survival-two-frames/generate-metrics.mjs
node scripts/research-workflow.mjs status --experiment muon-survival-two-frames
node scripts/research-workflow.mjs verify --experiment muon-survival-two-frames
```

All exited zero. Setup verification reported 32 matching artifacts, exact
CPython 3.12.3, pip 26.2.1, NumPy 2.5.1, Matplotlib 3.11.1, Node 24.18.0,
zero run namespaces, and `production_absent: true`. All 21 toy/synthetic tests
passed in 0.866 seconds test time and 1.32 seconds wall time, with 97,980 KiB
peak RSS and zero socket messages. The suite exercised the result, PNG, and
metrics writers only in temporary `setup-toy` paths. Compile, Node syntax,
workflow verification, canonical-output absence, and `git diff --check` passed.
The real graph remained at `setup`, iteration 3, with nine events and eight
snapshots.

The first verification attempt stopped before tests because the new schema
validator eagerly formatted an impossible empty-set error message. The one
focused correction made that branch conditional. A diagnostic synthetic run
also exposed alias-preserving in-place test mutations; the corrected tests
replace the targeted arrays so only the intended bindings are exercised. The
complete rerun above then passed. Neither failure touched a canonical path or
scientific value.

## Execution, replay, and regeneration contract

The exact normal production command remains implemented and unexecuted:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

It requires the current fully replayed setup approval and an empty `runs/`
namespace. The only fresh attempt remains `run-002`, requiring a fully replayed
current `registered_retry` event and preserved incomplete `run-001`. There is
no same-run resume or other run ID. Recorded authorization remains verifiable
after later valid events because it binds and relocates the immutable event.

The canonical analysis command and its `--check` companion retain the approving
run-review event argument frozen in `inputs.json`. The check command remains
usable after submission to analysis review. Result, figure, and metrics writers
remain exclusive, and their check modes regenerate exact bytes. No choice,
threshold, seed, draw, grid point, or output path changed.

## Residual risk and focused review

No protocol ambiguity or setup blocker is known. Residual nonblocking risks
remain external PDG availability, cross-host wheel availability, self-asserted
actors, the metrics generator's absent help mode, and the operational dependency
on the exact hash-bound Node workflow verifier. A future shared workflow update
would intentionally invalidate setup and require review rather than silently
changing execution admission.

The fresh reviewer should focus on:

1. Does delegating replay to the exact hash-bound repository verifier establish
   every requested graph/event property without a second partial implementation?
2. Does historical event lookup preserve later check-mode validity while still
   rejecting a different, duplicated, malformed, or unlinked approval?
3. Are all six integrity flags causally derived from concrete validations, and
   does the two-phase result-schema check avoid circular assertion?
4. Do the decoupled focal/count fixtures and exhaustive per-field mutations
   close the remaining coverage finding?

## Gate retrospective and handoff

The third review caught two lifecycle issues that ordinary numerical tests
would not: replay authority and post-submission regeneration. Reusing the
repository verifier was clearer and smaller than maintaining a subtly divergent
Python graph engine. The schema/provenance gate also converted descriptive
booleans into actual checks. Exhaustively mutating every field is disproportionate
to the arithmetic, but it exposed shared-array aliasing in the tests and made
the contract inspectable. The temptation was to treat the earlier event-shape
fixture as enough because the graph CLI also runs elsewhere; the gate correctly
required the production admission path itself to call the authoritative replay.

Approximate iteration-3 engineering and verification effort was 34 minutes.
Keep graph-backed admission and historical immutable approvals; change the
shared template to provide a reusable schema/provenance validator; defer any
test-matrix reduction to a future reduced, still-reviewed Understanding lane.

Journal session: `20260809T045452Z-one-muon-two-frames-7ed9`. Next action: the
coordinator verifies this receipt and manifest, checkpoints the journal,
submits only `workflow/setup-v3.md`, commits and pushes the durable handoff, and
supplies the immutable snapshot and all 32 bound artifacts to a fresh read-only
`setup_review`. This producer does not submit, review, transition, commit, or
push.
