# Setup handoff: version 2

- **Graph state:** `setup`, iteration 2.
- **Actor and role:** `experiment-engineer-muon-trial`, configured
  `experiment_engineer` session.
- **Revision parent:** `setup-review-v1.md`, decision `revise`, 6,619 bytes,
  SHA-256
  `5a00feedb7b16c194ec9b02042ee3e8898b06b9c78cfb8d2d994fbe238145944`.
- **Protocol:** `research/muon-survival-two-frames/PREREGISTRATION-v1.md`,
  unchanged at 19,383 bytes and SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- **Outcome boundary:** no canonical sample, run namespace, result, metric,
  publication figure, full-grid calculation, or focal calculation was created
  or inspected. All executable setup evidence used seed 0 with at most 16
  draws or synthetic in-memory arrays and temporary nonproduction paths.
- **Requested gate:** fresh independent `setup_review`.

## Revised inventory and binding

The version-1 setup manifest bound 25 files, was 4,266 bytes, and had SHA-256
`601fc4209f8edbab56a9432171c6fab21370a90414eb2c73dd069ab5e1468d10`.
The revised `setup-manifest.json` binds 29 files, is 4,924 bytes, and has
SHA-256
`7b31d42a48de0ec7b616ee0364f969775909b9c5ef398d97e14870f172cee1ed`.
It adds the actual analysis, renderer, metrics generator, and pipeline tests;
the copied metrics `.example` files are superseded and removed.

| Artifact | Version 1 SHA-256 | Version 2 SHA-256 |
| --- | --- | --- |
| `inputs.json` | `2559e87370bd4f50903b557645b8f30ac640430c5d1b7ec4739aed68cbc4ac62` | `da290f0ce43c12f788d923623bc7dc092285719d6d1716d76447a0fc013cc02f` |
| `schemas/analysis-result.schema.json` | `1e56d471fc3428a4e1c110d3d875bf003c94e818021dd9c4cc7fddc7ed3e3170` | `ecc41038045a1c1110d9a8a8d69b973bf25834310a38063a59ece912dd55c982` |
| `schemas/inputs.schema.json` | `15894b217e46d6a951aeb43a7616a0519baf69a6052f9776856daf36c43be3e9` | `0d8c72dd6f1b3081fb2cd3513051534e879358db7f7199c6a732c9337eec0e80` |
| `schemas/run-manifest.schema.json` | `7f694ce84c8eb27d720448b0643ca590d701004bac0bb9818ae0446e3d709a69` | `3f315b170a3ddb18393a584919568d76c27bd45317f2cfe04559422a823482ac` |
| `src/contract.py` | `012d178c7f89612ea4d23a3d66e41dadb34229ba90604c007551c006b8490ceb` | `2b6c6aab3e68fff4d524bd91a3428a0d7c3f6370330693e3bb5691d22a471471` |
| `src/bundle.py` | `a35e2b4bde88467b732fd320521c2d91851ff43f42961610216db8d8d68a293e` | `607188d612ab921c92b658134985695bec92f5bb50ead78f759e2f28c75d03de` |
| `src/reconstruct.py` | `85610ce539a19d9d6f58f22b7116dbb4e5e58492eeb91a434c83bfdcd9bd96fb` | `f892f4c9aacaca6de1668aad92953a500f4b7b644d5bd75d44a6111d89adaec8` |
| `src/run.py` | `e626c9b12465f7a5c7f192f40c8cdceb57131ef9d27d24267985998ebd8b11cf` | `947b4163bf9b5889d0c2dbd667b77bb3e6b8f56ea9ea5375558cc15462f67ec3` |
| `src/validate_run.py` | `f898b9cdde19a36af4a1533b297e190692aaa221edbd372346517fe91c325e5a` | `00db3e7f8c5af1d404eb563b40b6d44421f8fc5cc7047407dd975903a6577383` |
| `tests/test_setup.py` | `aee6526559830e18b325bf47269453fa6bcbbd961e7f771efabe420b92334e0e` | `4ca0d4a90f96ecd15ca532f2ba73a25670fd88beef81be28c2a9c99eb5b71e58` |

The version-1 digests above come from the accepted setup handoff; the complete
version-2 values and byte sizes are authoritative in `setup-manifest.json`.
Newly bound key files are:

- `src/analyze.py`: 8,255 bytes,
  `b90a8da6508a8dca73461eebdca53e6e134671dae44e78eb8491a25475d06743`;
- `src/render_figure.py`: 5,877 bytes,
  `8b99133bbd70877885437b33de5791ff28025f88a3b9f4c3e015ee49f8456ccc`;
- `generate-metrics.mjs`: 6,701 bytes,
  `3608924af45aa675122732551f0530ba822b8cefa783cf401b3bdf3de68363fa`;
- `tests/test_pipeline.py`: 11,064 bytes,
  `cec6cf3dd13de6e4f14358532d85f3cab05887bf433131f1cbe0604d59c49cfd`.

## Review findings mapped to fixes

| Setup-review finding | Bound fix | Independent setup evidence |
| --- | --- | --- |
| 1. Analysis and fidelity contract was not implemented end to end. | `src/analyze.py` admits only an approved `run_review` event, reconstructs every frozen field, and exclusively writes or byte-checks `results/summary.json`; `src/render_figure.py` exclusively writes or byte-checks the exact 1200 by 630 two-panel PNG; `generate-metrics.mjs` exclusively writes or byte-checks the metrics projection. `src/reconstruct.py`, the result schema, inputs, README, and prospective allowlist bind primitives, grid, units, both independent frame routes, counterfactual, derived arrays, checks, and commands. | A synthetic packet traverses result generation, exact result regeneration, PNG dimensions and byte regeneration, and Node metrics generation and byte regeneration in a temporary directory. Mutated primitive, grid, unit, detector distance/time/lifetime/exponent, muon distance/time/lifetime/exponent, counterfactual, and integrity fields each fail. |
| 2. Unauthorized run namespaces bypassed retry registration and setup absence. | `src/contract.py` accepts only `run-001` or `run-002`. Normal execution requires the current approved setup event and an empty `runs/`; `run-002` requires a preserved incomplete `run-001` and the current `run_review --registered-retry--> execute` event. The exact authorizing ledger line is hash-bound in the run manifest. Setup absence enumerates every entry under `runs/`. | Synthetic ledgers independently accept normal and registered-retry events, reject an unapproved retry, reject `run-003`, reject retry after completion, and show that a lone `run-002` makes `production_absent` fail. |
| 3. Raw publication used a check-then-replace race. | `src/bundle.py` opens the final `.npy` path directly with exclusive creation and writes NumPy bytes through that descriptor; no rename can overwrite a competing final path. | A two-thread barrier race proves exactly one writer succeeds and the other receives overwrite refusal. |
| 4. Registered branch coverage was incomplete. | `tests/test_setup.py` independently exercises frame probability, exponent, beta, gamma, exact-zero, focal four-standard-error, maximum discrepancy, count bounds, zero count, monotonicity, count dtype, empirical/count equality, numeric raw validity, all derived-field/unit/counterfactual checks, and every integrity flag. | Sixteen total toy/synthetic tests pass; each named branch is mutated independently rather than inferred from `all_passed`. |
| 5. Sealed logs were fixed bytes rather than process streams. | `src/bundle.py` redirects file descriptors 1 and 2 before the draw and keeps them through sealing. Success logs, failure messages, and tracebacks are the real process streams; manifests hash them and failures remain incomplete. | Success sentinels are captured and hash-tamper detection fails closed; a raised callback captures its stdout, stderr, and traceback and produces no `COMPLETE.json`. |

## Frozen commands, output, and retry contracts

The exact normal production command remains implemented but unexecuted:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

There is no same-run resume. A claimed namespace is immutable; a post-claim
failure is preserved without a completion marker. The only fresh attempt is
`run-002`, after the graph has recorded the registered retry and only while
`run-001` remains incomplete. `run-003` and every other ID are unregistered.
Later validation checks the recorded authorization against the still-present
ledger event even after the graph advances.

After run review, the exact analysis command requires the approving event ID:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-001 --run-review-event <approved-event-id>
```

The paired result `--check`, renderer write/check, and metrics write/check
commands are frozen in `inputs.json` and documented in `README.md`. Production
writers refuse an existing output; check modes reconstruct in memory and
require exact bytes. The setup suite exercised these contracts only under
temporary names containing `setup-toy`.

The run output remains the raw float64 sample, actual stdout/stderr,
authorization-bearing manifest, checksum file, and last-written completion
marker. The result contract reconstructs the registered primitive values and
units, integer grid, detector-frame arrays, muon-frame arrays,
same-speed/no-lifetime-dilation counterfactual, focal fields, survivor counts,
and six registered acceptance checks. It contains Understanding observations,
not a hypothesis, falsifier, novelty claim, contribution claim, or verdict.

## Commands and results

The final setup-only verification used:

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

All required commands exited zero. The lock dry-run found only the twelve
already-installed hash-pinned packages and `pip check` found no broken
requirements. Setup verification reported CPython 3.12.3, pip 26.2.1, NumPy
2.5.1, Matplotlib 3.11.1, Node 24.18.0, 29 matching manifest artifacts, no run
namespaces, and `production_absent: true`. All 16 tests passed in 0.473 seconds
test time and 0.94 seconds wall time, with 97,532 KiB peak RSS and zero socket
messages. Compile, Node syntax, workflow status/verify, `git diff --check`,
canonical-output absence, and the local-absolute-path scan also passed.
Workflow remained `setup`, iteration 2, with seven events and six snapshots.

An extra, non-required invocation of `generate-metrics.mjs --help` returned
nonzero because the small generator has no help parser and therefore tried to
read the deliberately absent canonical result. It wrote nothing. The frozen
write and `--check` modes both pass on synthetic fixtures; adding help text is
nonblocking polish and is not pursued in this revision.

The production sample remains estimated at about 0.8 MB plus small JSON/log
overhead. The setup-only pipeline stayed far below the one-minute and 10 MB
limits. The analyst should record the actual canonical result/figure resources
after admission; setup does not predict them from a production execution.

## Residual risk and focused review

No frozen-protocol ambiguity or dependency blocker remains. Residual
nonblocking risks are external PDG PDF availability, Linux-wheel availability
on a different host, self-asserted rather than authenticated workflow actors,
the intentionally small generator's absent help mode, and editorial selection
of the eventual live public allowlist.

The fresh reviewer should focus on:

1. Does the authorization proof bind the normal run and sole retry to the exact
   graph events without making later read-only validation depend on current
   graph state?
2. Do the result writer, renderer, and metrics check modes cover every frozen
   primitive and derived field without creating another scientific degree of
   freedom?
3. Does direct exclusive `.npy` creation close the overwrite race on the
   approved filesystem boundary?
4. Are file-descriptor-level logs captured early enough and sealed late enough
   to establish success and failure lineage?
5. Do the independent mutation tests genuinely cover each registered failure
   and boundary branch without evaluating canonical quantities?

## Gate retrospective and handoff

This review materially improved the setup: it caught three real integrity
defects (retry admission, raw-file atomicity, and log lineage) and showed that
an analysis skeleton was not meaningful until its future writers and all
registered fields were executable. The producer/reviewer boundary prevented
the engineer from treating plausible prose as evidence. Repeating hashes and
schema/runtime checks was somewhat ceremonial for this tiny calculation, while
the no-production boundary, synthetic fixtures, and independent setup review
were useful. It was tempting to smoke-test the canonical path after wiring the
pipeline; the toy boundary supplied the needed evidence without exposure.

Approximate iteration-2 engineering and verification effort was 30 minutes.
Keep the independent setup gate; change the shared template to provide atomic
bundle/log capture and exclusive writer/check helpers; consider removing
full-size setup ceremony only through a future reduced, still-reviewed lane,
not on this branch.

Journal session: `20260809T045452Z-one-muon-two-frames-7ed9`. Next action: the
coordinator verifies this receipt and manifest, checkpoints the journal,
submits only `workflow/setup-v2.md`, commits and pushes the durable handoff, and
gives the submitted snapshot plus all bound setup bytes to a fresh read-only
`setup_review`. This producer does not submit, review, transition, commit, or
push.
