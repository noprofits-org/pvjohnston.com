# Setup-review receipt

- **Gate:** `setup_review`, iteration 3
- **Actor:** `setup-reviewer-muon-05`
- **Decision:** `revise`

## Reviewed artifacts

Reviewed all 347,102 supplied bytes. The 32-artifact setup manifest is 5,380
bytes, SHA-256 `2f238113…e5c0e2f`; it binds the unchanged 19,383-byte protocol
(`501f57ab…7bb855c`), inputs, environment/lock, six schemas, implementation,
tests/fixture, graph (`e50f1247…418d404`), and verifier
(`f8b93115…515f2c`). Also reviewed the 10-event ledger
(`b3f00267…3dfbf`), setup-v3 evidence (`ce58e2b9…e24e9fcd`), and both prior
setup reviews.

## Checks

Confirmed unchanged Understanding protocol and environment; fixed grid, seed,
draw count, and one-call PCG64 contract; separate frame implementations;
labelled counterfactual; no scientific overrides; exclusive result/PNG/metrics
writers and check modes; bounded retry namespace; atomic raw creation;
descriptor-level process logs; and no supplied run, result, metric, or figure.

The v1 atomic-publication and log-lineage blockers are closed. Historical
approvals, normal/retry graph replay, derived integrity flags, and isolated
branch fixtures are substantially implemented, but the following blockers
remain.

## Blocking findings

1. **High — authorization can consume ledger bytes that were never
   replay-verified.** `validate_workflow_ledger()` saves `ledger_before`, runs
   the authoritative verifier, confirms the pathname still matches, and then
   calls `_workflow_records(workflow_path)`, which reopens the pathname. A
   replacement or append between that comparison and the final read makes
   authorization and `event_sha256` derive from different bytes than the
   verifier approved. The same path affects normal execution, retry execution,
   recorded authorization, and historical analysis admission.

2. **High — historical evidence linkage is also reopened without rebinding its
   verified bytes.** After replay, `analysis_admission()` rereads each approval
   snapshot and merely searches for the run-ID substring; it does not recheck
   that read against the event's byte count and SHA-256. Thus the evidence used
   to link an approval to a run need not be the snapshot bytes verified during
   replay.

3. **Medium — the metrics writer/check does not enforce the claimed result
   contract.** `generate-metrics.mjs` performs selective field/type checks but
   does not validate the bound result schema, cross-field derivations, digest
   provenance, or integrity-detail consistency. Its write and `--check` modes
   can therefore accept a malformed or tampered summary that the Python result
   validator would reject.

## Nonblockers

The exhaustive fixture matrix still lacks a distinct negative-raw-lifetime
mutation; the combined finite/nonnegative branch is exercised only with `NaN`.
External PDG availability, cross-host wheels, and self-asserted actor identities
remain operational risks.

## Route

- **Required route:** `setup_review → setup`
- **Validity versus outcome:** Implementation/lineage validity only; no
  survival value, frame-agreement outcome, or canonical quantity was executed
  or inferred.
- **Residual risk:** A concurrent pathname change could authorize execution or
  analysis from evidence different from the replayed evidence.
- **Smallest action:** Make replay return and hash the exact already-verified
  ledger and snapshot bytes, then add a regression that changes each pathname
  after verification but before authorization consumption.

## Independence and retrospective

Fresh independent session and actor confirmed. Review was entirely read-only
and used only supplied immutable bytes—no tools, commands, network, connectors,
mutations, fixes, or substitute computation. Iteration 3 closes the substantive
v1/v2 numerical and lifecycle defects, but fresh tracing exposed an identity
gap at the boundary between authoritative replay and Python consumption.
Approximate review effort: 34 minutes.
