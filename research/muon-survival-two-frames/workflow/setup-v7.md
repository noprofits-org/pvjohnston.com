# Setup handoff receipt

- **Gate:** `setup`, iteration 7
- **Actor:** `experiment-engineer-muon-07`
- **Durable input:** commit `f9ca37798bf9`
- **Protocol:** unchanged `PREREGISTRATION-v1.md`, 19,383 bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- **Input review:** `workflow/setup-review-v6.md`, 3,749 bytes, SHA-256
  `d00493aea5c18dd4bf9d099c3e3697de8bad192591328c4f6eba5441616fe5ac`
- **Exposure:** none. No canonical seed, draw count, grid, focal calculation,
  run namespace, result, metric, or figure was invoked or created.

## Blocking findings closed

1. Workflow-backed tests no longer inherit the mutable experiment ledger.
   `WorkflowFixture` constructs its own valid three-event prefix (`init`,
   question submission, independent approving question review) ending at
   `setup`, with two synthetic evidence snapshots and no pending submission.
   It never reads or copies the live experiment workflow. A constructor
   invariant test enforces that prefix. The complete suite also passed from an
   exact archive of commit `c0682f9`, whose real experiment ledger is the
   independently verified 16-event, 15-snapshot pending `setup_review` state,
   after overlaying the current setup implementation bytes. Thus both the
   present `setup` state and a deliberately advanced live-ledger surrogate are
   replayable without fixture drift.
2. Result JSON, publication PNG, and Node metrics now use one bounded derived-
   output publication contract. A writer creates a same-directory, exclusive
   hidden temporary file, flushes it, hard-links it to a digest-named ready
   stage, then hard-links ready to the final pathname. The final link is an
   atomic no-overwrite install; an existing file, symlink, or directory is
   always rejected, including equal bytes. A safe exact ready stage resumes the
   interrupted install. Safe partial temporary stages and mismatched/extra
   ready stages are hard-link quarantined and never installed. Stages must
   match the exact target grammar, be regular non-symlinks owned by the current
   UID, be no larger than 10 MiB, and number at most 16; otherwise recovery
   fails closed without touching them. Success removes temporary/ready stages
   and syncs the parent directory. Quarantines remain for inspection. The raw
   run publisher is unchanged.

Python tests cover JSON and PNG stage recovery, partial and mismatched stage
quarantine, pre-existing final refusal, cleanup, a two-writer different-byte
race, and an observer that sees only absence or one whole payload. Node tests
cover the same interruption, recovery, quarantine, no-overwrite, check-mode,
race, and visibility contract through the actual metrics entrypoint. Exactly
one contender wins each race. `src/render_figure.py` changed only to call the
shared publication primitive; figure construction and content are unchanged.

## Bound bytes

The setup-v6 manifest bound 33 artifacts, was 5,547 bytes, and had SHA-256
`4fe3d8bb6f2f640186aed4599bc8f70508dbe892fbd9032fc0494b4e48dd645e`.
The setup-v7 manifest still binds 33 artifacts and is 5,548 bytes, SHA-256
`faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619`.
Unlisted bound entries are byte-identical.

| Path | Setup-v6 bytes / SHA-256 | Setup-v7 bytes / SHA-256 |
| --- | --- | --- |
| `README.md` | 8,272 / `4d60c0b05cb6543713a86e2c9dfa13806b24c9ed15dae214c564a317cd49e7d2` | 9,591 / `40951373db43318220aac61fe7707ea485e38e1ef3bd9f8ca385e2cd355e6885` |
| `generate-metrics.mjs` | 7,164 / `9239186df7059557133dae935b62646e62575e3b4ae174922bd00345346f2b87` | 12,931 / `a86304338ee51160621354a799dabb4ff903eb8b72b5c2024cf66b8e678d0fb8` |
| `src/analyze.py` | 32,603 / `31b76513b51fb242c2d125b514cfe2e9ee76fd7f3f001be1788c251a664b6a84` | 32,617 / `c2b0f410215deb4c078da4220e38e7f641686f23da0a0b63635d9f8b9ae78e42` |
| `src/contract.py` | 37,080 / `0e39a47ff344e6017bcb74cb6b3394b9013b0516adc150ce3b39955147161991` | 44,526 / `30eee0b3716f51c83c7a166c942b5ce9b041c1318a9f06bcc5925a34dd3fe7df` |
| `src/render_figure.py` | 5,987 / `6de4994b9b050d3a9d0fa017d379ccaa2a3c0305beaa62fbdfec95b620d7c2b5` | 6,001 / `240598a07744765bb2381a7150e38074dbcad9af1425d0f95a1d30860dac1c24` |
| `tests/test_pipeline.py` | 38,319 / `f5848e8a73a1ac0a618f11611fb6b6830db45569f48a27fc18706a9183eb1e40` | 49,266 / `206bbda774484a5e083caf338dc941ff95b35c669bdbc9ab37a7bb38c10da4ca` |
| `tests/workflow_fixture.py` | 6,374 / `4478a1e483f98d85eb304c9457ea55de5a566691cc54d8087aa01d837a75fc49` | 7,558 / `9c9fe88e01a0315803732dc45990f422e101ddf721319354f40c3fe5f6079014` |

The protocol, constants, sources, environment, requirements, schemas, graph,
workflow CLI, scientific formulas, RNG, production grid, focal index,
thresholds, run/retry rules, output paths, commands, and figure contract are
unchanged.

## Tests, resources, and exact checks

From the repository root, the current-state bounded suite command was:

```sh
research/muon-survival-two-frames/.venv/bin/python -m unittest discover \
  -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
```

It passed 32/32 tests in 8.042 seconds of test time (8.5 seconds wall). The same
command against the current setup bytes overlaid on the exact `c0682f9`
submitted-state archive passed 32/32 in 7.976 seconds (8.9 seconds wall); before
the overlay, workflow status and verification reported `setup_review`, 16
events, and 15 snapshots. No failure or repair pass occurred.

Post-suite commands all exited zero:

```sh
research/muon-survival-two-frames/.venv/bin/python -m pip install --dry-run \
  --require-hashes -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python -m pip check
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/verify_setup.py
research/muon-survival-two-frames/.venv/bin/python -m compileall -q \
  research/muon-survival-two-frames/src research/muon-survival-two-frames/tests
node --check research/muon-survival-two-frames/generate-metrics.mjs
node scripts/research-workflow.mjs status --experiment muon-survival-two-frames
node scripts/research-workflow.mjs verify --experiment muon-survival-two-frames
git diff --check
```

The lock is fully satisfied; `pip check` reports no broken requirement. Setup
verification reports CPython 3.12.3, pip 26.2.1, NumPy 2.5.1, Matplotlib 3.11.1,
Node 24.18.0, 33 valid manifest records, zero run namespaces, and
`production_absent: true`. Current workflow remains `setup`, iteration 7, with
17 events and 16 snapshots. Exact output-absence and public-path scans pass.

## Retrospective and review focus

The stable synthetic graph seed is useful shared test infrastructure; copying
the live ledger was brittle and obscured whether tests proved the contract or
merely matched today's gate. Atomic no-overwrite publication is also material:
the old direct-final writers could expose a partial derived artifact after an
interruption. The seventh setup loop is disproportionate for the scientific
size of this Understanding note, but these two findings are real pre-exposure
correctness issues. Approximate implementation, testing, and receipt effort was
30 minutes. No frozen-protocol ambiguity arose and bypassing the review was not
considered acceptable.

Residual nonblockers: the hard-link/fsync contract is tested only on the pinned
Linux filesystem environment; unsafe or foreign-owned stage entries require
manual inspection; quarantine retention can require bounded operator cleanup.
Reviewer focus: no live-ledger read in fixtures, both current and advanced-state
replay, exact stage classification, interrupted-ready recovery, partial-stage
quarantine, one-winner races, and immutable existing-final refusal.
