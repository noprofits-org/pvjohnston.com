# Setup handoff receipt

- **Gate:** `setup`, iteration 4
- **Actor:** `experiment-engineer-muon-04`
- **Protocol:** `PREREGISTRATION-v1.md`, 19,383 bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- **Input review:** `workflow/setup-review-v3.md`, 3,985 bytes, SHA-256
  `d4ab02dbb5471ee3f719395a6b66f48ee472168d3de40377721bc7aa2adf7383`
- **Scientific exposure:** none; no canonical seed, draw count, path grid,
  focal calculation, run namespace, result, metric, or figure was invoked or
  created.

## Outcome

All three blocking findings in setup review v3 are addressed without changing
the frozen protocol. Authorization and historical analysis admission now use a
single captured byte snapshot: the hash-bound repository verifier replays an
isolated tree made from those exact ledger, source-receipt, and evidence bytes,
and the Python callers consume the already parsed records and already validated
snapshot payloads returned from that replay. They never reopen a pathname to
derive an event or run link after verification.

The metrics writer and `--check` mode now obtain their input as the exact bytes
emitted by the pinned Python result validator. That validator enforces the bound
JSON schema, deterministic serialization, frame/counterfactual derivations,
focal and empirical cross-fields, complete detail/diagnostic shape, digest
provenance, and the production frozen-input contract before Node projects any
field. Setup-fixture mode retains only the preregistered visibly synthetic
exception to frozen production dimensions; its full schema, derivation, and
digest checks use a complete temporary repository fixture.

The noted nonblocking coverage gap is also closed with a finite `-0.25 s`
synthetic raw lifetime. It fails the nonnegative branch while retaining the
registered float64 dtype, independently of the existing `NaN` branch.

## Finding-to-fix traceability

| Review-v3 finding | Bound implementation | Independent setup-only regression |
| --- | --- | --- |
| Ledger pathname could be reopened after replay and consumed as different bytes. | `src/contract.py` captures the ledger once, parses those bytes once, captures every referenced source/snapshot against the event size and SHA-256, stages those exact bytes in a private temporary repository, invokes the exact hash-bound Node verifier there, and returns `VerifiedWorkflowLedger`. Normal, registered-retry, recorded, and historical callers consume only its records. | `test_authorization_consumes_the_exact_replayed_ledger_bytes` replaces the original ledger pathname after authoritative replay in separate normal, recorded-normal, and registered-retry cases. Each authorization remains bound to the replayed event rather than consuming the replacement. The existing complete graph fixtures and underspecified-event rejection remain in force. |
| Historical run-review evidence was reopened without binding the bytes searched for the run ID. | `src/analyze.py` gets the approval snapshot payload from `VerifiedWorkflowLedger.snapshot_bytes`; that payload was size/hash checked before exact replay. It UTF-8 decodes and searches only those returned bytes. | `test_historical_admission_consumes_bound_ledger_and_snapshot_bytes` replaces both the original ledger and approval snapshot after replay. Admission retains the replayed event and bound evidence; the replacement evidence deliberately omits `run-001`. The separate post-analysis-submission regression still proves historical lookup after a later valid event. |
| Metrics write/check accepted a selectively plausible but Python-invalid summary. | New `src/validate_result.py` validates one captured canonical result payload with the pinned environment and writes those same bytes to stdout. `generate-metrics.mjs` consumes only that buffer for projection and input hashing in both modes. Production accepts only the canonical path and enforces frozen inputs; setup accepts only a visible `setup-toy` file inside its supplied temporary root. | The valid synthetic result/PNG/metrics round trip passes. `test_metrics_write_and_check_reject_full_result_contract_tampering` independently removes a required schema field, changes a derived detector time, corrupts generator provenance, and removes an integrity-detail field. Every mutation fails before a new metrics write and also fails `--check`; no rejected output is created. |
| `NaN` was the only raw finite/nonnegative mutation. | No implementation choice changed. | `test_finite_negative_raw_lifetime_fails_nonnegative_branch` injects a distinct finite negative lifetime and verifies only the combined finite/nonnegative fidelity branch fails while dtype remains valid. |

## Bound byte inventory

The prior 32-artifact setup manifest was 5,380 bytes with SHA-256
`2f23811352b56843a5533f254108bb2befe30287945d24f53366e82a6e5c0e2f`.
The revised `setup-manifest.json` binds 33 artifacts, is 5,547 bytes, and has
SHA-256
`23d4dc17f8f753c5dbe3a23ac2da38e615b1510732e403e4f18dcd16377673bd`.
Unlisted entries are byte-identical to setup v3.

| Path | Setup-v3 bytes / SHA-256 | Setup-v4 bytes / SHA-256 |
| --- | --- | --- |
| `PUBLIC_FILES.prospective.txt` | 1,751 / `70909f75e42156f3ca5f47e16b4668a9112675e1f247b4b8a449507e07bb855c` | 1,808 / `0d3f8c8ea43dafa733450af75f26ddec4e1b81420b2404d4c81a88fbaeba0fff` |
| `README.md` | 6,807 / `d0a1fecd350689fcc40e4618ae5b9fdd66e5a155958184eff5eaabba931a5efe` | 7,006 / `1609e11d6eabf587986d2aa4d7299dab466bcc2b040d8ba27475c80e5f708705` |
| `generate-metrics.mjs` | 6,701 / `3608924af45aa675122732551f0530ba822b8cefa783cf401b3bdf3de68363fa` | 7,164 / `9239186df7059557133dae935b62646e62575e3b4ae174922bd00345346f2b87` |
| `src/analyze.py` | 21,894 / `eb65352951dd2ba11fcd9dca022263778a53d07776c9d254eb42907904356b4c` | 22,681 / `6c30b60e2956b7da10f4ea92cbbb607c5de53f9b2ccdbb003ccc936c0139028d` |
| `src/contract.py` | 29,787 / `4d70e01de6116854db28f7004429f3ef14e9b28dd44a99192ce11b097b3a434b` | 34,267 / `3e158fabe81e95f02e914daec184973bcdba38549c8f19471ce4bf2dc100f66a` |
| `src/validate_result.py` | absent | 2,867 / `78a05f4de94ad5fddf139982c8b6a4089d40221d8197adf4971053c06f566f8e` |
| `tests/test_pipeline.py` | 15,769 / `6bef4333480980a4ef814d621506193b5df0bbe7fc012039a93c490a56182d10` | 25,242 / `089fa4c68df7074cc7b009ba9283d2c2d35ed75012911652a8d2e823f852e8de` |
| `tests/test_setup.py` | 16,774 / `52b4eaac72f9e6b4dcb87e5037c7a61b2a21afed4d663e29bc3397af5a4e1335` | 17,191 / `d1fa24b4d06309913b274fede682a8e70470e37e8490c9910a4275bfb9555286` |

The setup-v3 digest shown for `tests/test_setup.py` is reproduced directly from
the durable parent commit. The protocol, constants, sources, environment,
requirements, schemas, graph, verifier, frozen commands, RNG, grid, focal
index, thresholds, and retry policy are unchanged.

## Commands and observed results

The one bounded full setup-only suite was:

```sh
/usr/bin/time -v research/muon-survival-two-frames/.venv/bin/python \
  -m unittest discover -s research/muon-survival-two-frames/tests \
  -p 'test_*.py' -v
```

All 25 tests passed on the first complete run. Python reported 3.144 seconds of
test time; `/usr/bin/time` reported 3.61 seconds wall time, 11.38 seconds user
CPU, 0.51 seconds system CPU, 97,764 KiB maximum resident memory, zero socket
messages, and exit status zero. Every calculation was seed 0 with no more than
16 draws or used closed-form synthetic arrays. Writers addressed temporary
paths containing `setup-toy`; none addressed a production namespace.

The post-suite checks were:

```sh
research/muon-survival-two-frames/.venv/bin/python -m pip install \
  --dry-run --require-hashes \
  -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python -m pip check
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/verify_setup.py
research/muon-survival-two-frames/.venv/bin/python -m compileall -q \
  research/muon-survival-two-frames/src \
  research/muon-survival-two-frames/tests
node --check research/muon-survival-two-frames/generate-metrics.mjs
node scripts/research-workflow.mjs status \
  --experiment muon-survival-two-frames
node scripts/research-workflow.mjs verify \
  --experiment muon-survival-two-frames
git diff --check
```

All exited zero. The lock dry run found every exact hash-pinned requirement
already installed and `pip check` found no broken requirement. Setup validation
reported CPython 3.12.3, pip 26.2.1, NumPy 2.5.1, Matplotlib 3.11.1, Node
24.18.0, 33 matching manifest artifacts, no run namespaces, and
`production_absent: true`. The real workflow verified at `setup`, iteration 4,
with 11 events and 10 snapshots.

## Execution and retry boundary

The frozen normal command remains exactly:

```sh
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/run.py --run-id run-001
```

It was not invoked. A normal attempt still requires the current replayed
`setup_review` or `amended_setup_review` approval into `execute` and an empty
`runs/` namespace. The only fresh infrastructure retry remains `run-002`; it
requires a current replayed `run_review --registered_retry--> execute` event and
the sole preserved incomplete `run-001` namespace. Same-run resume, any other
run ID, a retry after completion, and an analysis rerun remain forbidden. The
atomic run-bundle publication, actual stdout/stderr capture, completion marker,
checksum contract, and failure behavior are unchanged from setup v3.

The canonical analysis, figure, and metrics commands also remain unchanged and
unexecuted. `src/validate_result.py` is an internal admission boundary invoked
by the already frozen metrics commands, not a new scientific command or choice.

## Gate retrospective and reviewer focus

This gate materially clarified that a byte hash is insufficient if a consumer
opens the pathname again after verification. Returning the actual replayed
payload produced a smaller and more auditable trust boundary for authorization,
historical evidence, and downstream projection. The fresh reviewer also caught
that a selective JavaScript projection check was weaker than the canonical
Python result contract; reusing one validator removed duplicated scientific
logic.

The disproportionate part was constructing complete workflow and provenance
fixtures merely to test pathname identity. It was still useful: the fixtures
made the replacement race executable rather than ceremonial. Bypassing full
replay or accepting the Node projection's partial checks would have been
tempting because the projected fields are few, but either shortcut would have
left the exact reported blockers open.

Approximate implementation, fixture, test, manifest, and receipt effort was 50
minutes. No frozen ambiguity arose. Residual nonblocking risks are unchanged:
external PDG availability, cross-host wheel availability, and self-asserted
actor identity. Future test generalization or CLI help text is stylistic and
was deliberately left out of this blocker-only pass.

Focused setup-review questions:

1. Does replaying a private tree assembled from one captured ledger/evidence
   snapshot, then consuming those same in-memory bytes, close the identity gap
   for normal, retry, recorded, and historical admission?
2. Do the pathname-replacement regressions demonstrate that neither event hashes
   nor run linkage can derive from bytes outside that replay?
3. Do metrics write and check now fail closed on schema, derivation, provenance,
   and integrity-detail tampering before producing or accepting a projection?
4. Is the visibly synthetic fixture exception sufficiently separated from the
   canonical path and frozen production validation?
