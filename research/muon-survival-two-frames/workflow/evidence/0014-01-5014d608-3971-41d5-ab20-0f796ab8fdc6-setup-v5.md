# Setup handoff receipt

- **Gate:** `setup`, iteration 5
- **Actor:** `experiment-engineer-muon-05`
- **Durable input:** commit `cb8de31`
- **Protocol:** `PREREGISTRATION-v1.md`, 19,383 bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- **Input review:** `workflow/setup-review-v4.md`, 5,058 bytes, SHA-256
  `bb7b0c74b0dd7ec0c6f7512d19ed7432943278048b2639b937284e87a8ac51b6`
- **Exposure:** none. No canonical seed, draw count, grid, focal calculation,
  run namespace, result, metric, or figure was invoked or created.

## Outcome and review-finding traceability

All four review-v4 blockers are closed without changing the frozen protocol.

| Finding | Implementation | Setup-only evidence |
| --- | --- | --- |
| Metrics could project false details, diagnostics, pass flags, admission identity, or run identity. | `src/analyze.py` captures the exact six-file source bundle, reuses `validate_run_bundle`, binds `source_run.run_id` to manifest/completion IDs and exact paths, reconstructs both frames and the counterfactual, derives empirical arrays from captured raw bytes, replays the immutable approval, derives integrity flags, and requires exact equality with the complete independently recomputed `checks` object. | `test_metrics_write_and_check_reject_full_result_contract_tampering` sends schema, cross-field, diagnostic, consistent detail/pass, consistent pass/all, admission, source-ID, provenance, and raw-derived mutations through both metrics write and `--check`. Every case fails closed and no rejected write creates a candidate. The valid synthetic result/PNG/metrics round trip passes. |
| Hash-approved graph and verifier pathnames were reopened. | `src/contract.py` captures and hash-checks both byte streams, stages them with the captured ledger/evidence, and invokes only the staged CLI and graph. | `test_authorization_executes_captured_graph_and_verifier_bytes` replaces both original pathnames after capture; replay still returns the approved event. Earlier ledger/evidence replacement regressions remain green. |
| Registered retry lacked exact downstream analysis commands. | `inputs.json`, its strict schema, and `README.md` bind exact write/check pairs for `run-001` and prospective `run-002`. Selection must use exactly the run named by the same immutable approving `run_review` event passed to analysis. | Setup validation checks the exact map, aliases, and selection rule. Full toy admission rejects mismatched approval, source, manifest, and completion identities. `run-002` remains absent. |
| Prospective README status was stale. | `README.md` now states only that setup is prospective, pre-production, and requires independent approval; it has no iteration number. | Manifest-bound setup verification passed. |

`src/render_figure.py` has no content or rendering change; it only drops the
obsolete optional-validation argument and calls the now-unconditional full
result validator.

Production validation takes dimensions and thresholds only from bound frozen
inputs. The visibly synthetic exception uses a fixed toy check specification:
three grid points, focal index one, 16 draws, frame tolerance `1e-12`, four
binomial standard errors, and maximum discrepancy `0.5`. It never infers a
threshold from reported checks.

## Frozen downstream selection

`inputs.json` and `README.md` bind these exact pairs:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-001 --run-review-event <approved-event-id>
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-001 --run-review-event <approved-event-id> --check
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-002 --run-review-event <approved-event-id>
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-002 --run-review-event <approved-event-id> --check
```

The immutable approval determines which pair applies; cross-pair substitution
is rejected. The `run-002` pair is prospective and applies only after a graph-
recorded registered retry.

## Bound bytes

The setup-v4 manifest bound 33 artifacts, was 5,547 bytes, and had SHA-256
`23d4dc17f8f753c5dbe3a23ac2da38e615b1510732e403e4f18dcd16377673bd`.
The setup-v5 manifest still binds 33 artifacts and is 5,547 bytes, SHA-256
`a9d4679f276ef51f4532b6413e099ffc0a5e96cf6b4256c9bba7790566a1395f`.
Unlisted entries are byte-identical.

| Path | Setup-v4 bytes / SHA-256 | Setup-v5 bytes / SHA-256 |
| --- | --- | --- |
| `README.md` | 7,006 / `1609e11d6eabf587986d2aa4d7299dab466bcc2b040d8ba27475c80e5f708705` | 7,779 / `3ca1e9b81b0444df556e3476a71876e0398289f97b94b65f49d161366e3c96ca` |
| `inputs.json` | 4,260 / `c80d63efc7efb9ac430aa787ec5fa5518cb3238e99cb159174302b2249968169` | 5,235 / `a030f11b8badf7561bd9d38211a6d8b1a4c82ab72a7b9e279c63ea9b00b5e445` |
| `schemas/inputs.schema.json` | 3,016 / `0190b2c580cbd5df1bb7aeac9572bc12d898feff2ec45d7093c9a2592e1a7edd` | 4,429 / `4ac16d55896987c79b947590ecb0eade9b7a504220fd0a7660c4368b796f7b0d` |
| `src/analyze.py` | 22,681 / `6c30b60e2956b7da10f4ea92cbbb607c5de53f9b2ccdbb003ccc936c0139028d` | 28,966 / `83cdedc26f9f2600d8fec273f9a38943789167422c627478ea7e3ae6668f98a6` |
| `src/contract.py` | 34,267 / `3e158fabe81e95f02e914daec184973bcdba38549c8f19471ce4bf2dc100f66a` | 36,970 / `cf63f2042e34f2e1b91b4b5d5a3bdf67cde2f730364438729e0cbe2e183b7851` |
| `src/render_figure.py` | 6,011 / `aec14d05ca3ae44cf1b4077e43df2148661dafbd0d341b0cb31103d7131762fc` | 5,987 / `6de4994b9b050d3a9d0fa017d379ccaa2a3c0305beaa62fbdfec95b620d7c2b5` |
| `src/validate_result.py` | 2,867 / `78a05f4de94ad5fddf139982c8b6a4089d40221d8197adf4971053c06f566f8e` | 2,835 / `14e223ebe179638ab106b9e211c9b85197da33a3ec090e5c0841ae100087dcf3` |
| `tests/test_pipeline.py` | 25,242 / `089fa4c68df7074cc7b009ba9283d2c2d35ed75012911652a8d2e823f852e8de` | 30,043 / `a84f0fba0e7aef0ab110071d06e182b11b50d9c6420b8068a9d5b5c09a84cc13` |

The protocol, constants, sources, environment, requirements, result/run
schemas, graph, verifier, RNG, production grid, focal index, thresholds, retry
policy, output paths, and publication-figure specification are unchanged.

## Tests, checks, and resources

The single bounded full suite was:

```sh
/usr/bin/time -v research/muon-survival-two-frames/.venv/bin/python -m unittest discover -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
```

All 26 tests passed on the first run: 6.063 seconds Python test time; 6.52
seconds wall, 20.04 seconds user CPU, 1.06 seconds system CPU, 97,724 KiB peak
RSS, zero socket messages, and exit zero. Tests used deterministic synthetic
arrays or seed 0 with at most 16 draws and only temporary `setup-toy` paths.

These post-suite commands all exited zero:

```sh
research/muon-survival-two-frames/.venv/bin/python -m pip install --dry-run --require-hashes -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python -m pip check
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/verify_setup.py
research/muon-survival-two-frames/.venv/bin/python -m compileall -q research/muon-survival-two-frames/src research/muon-survival-two-frames/tests
node --check research/muon-survival-two-frames/generate-metrics.mjs
node scripts/research-workflow.mjs status --experiment muon-survival-two-frames
node scripts/research-workflow.mjs verify --experiment muon-survival-two-frames
git diff --check
```

The lock was fully satisfied and `pip check` found no broken requirement.
Setup verification reported CPython 3.12.3, pip 26.2.1, NumPy 2.5.1,
Matplotlib 3.11.1, Node 24.18.0, 33 matching manifest entries, no run
namespace, and `production_absent: true`. Workflow status remained `setup`,
iteration 5; the ledger had 13 events and 12 snapshots. Targeted scans found
no checkout, home, scratch, cache, or mount absolute path and no run, result,
metric, or
publication-figure output.

## Boundary and retrospective

The frozen execution command remains unchanged and unexecuted:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

Normal execution still requires current setup approval and an empty namespace;
`run-002` still requires recorded registered-retry approval. Resume, atomic
sample publication, real stream sealing, completion, and checksum behavior are
unchanged.

This review materially improved raw-to-metrics and exact-byte lineage. Reusing
the existing reconstruction/check primitives avoided duplicating scientific
formulas. The disproportionate part was rebuilding a complete graph/run fixture
for small tamper cases, though it made the failures real rather than
ceremonial. It was tempting to trust earlier green projection tests; the new
raw-based comparison showed why that was insufficient. Approximate effort was
65 minutes. No frozen ambiguity arose.

Residual nonblockers: external PDG availability, cross-host wheel availability,
installed-environment byte integrity, untested filesystem semantics, and
self-asserted actor identity. Keep exact-byte independent setup review; change
the shared workflow later to provide one reusable pre-production admission
fixture. Reviewer focus: full-check recomputation, staged graph/CLI consumption,
same-event run selection, and the separation of toy from production paths.
