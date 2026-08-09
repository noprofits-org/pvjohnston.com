# Setup handoff receipt

- **Gate:** `setup`, iteration 6
- **Actor:** `experiment-engineer-muon-06`
- **Durable input:** commit `3b1c0c5`
- **Protocol:** unchanged `PREREGISTRATION-v1.md`, 19,383 bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- **Input review:** `workflow/setup-review-v5.md`, 4,434 bytes, SHA-256
  `9165f1e10720595f90b11733ecb0ec05be4dfa88f215f0b21a63b491c891cd27`
- **Exposure:** none. No canonical seed, draw count, grid, focal calculation,
  production namespace, result, metric, or figure was invoked or created.

## Outcome and finding traceability

Both review-v5 blockers are closed without changing a scientific choice.

| Finding | Fix | Isolated evidence |
| --- | --- | --- |
| `registered_analysis_spec()` raised `NameError` and was absent from setup integration coverage. | `src/analyze.py` imports `validate_digest_record`. `registered_analysis_spec()` now accepts explicit run/workflow/repository paths plus run-spec and frozen-input loaders, retains production defaults, creates repository-contained source records, and passes the selected repository root to `derive_integrity_flags()`. The CLI `main()` has dependency seams while its production defaults and command syntax remain unchanged. | `test_registered_analysis_entrypoint_uses_real_integrity_plumbing_for_both_runs` drives actual `main → registered_analysis_spec → validate_run_bundle → analysis_admission → derive_integrity_flags → build_analysis_result` plumbing for both registered IDs. It uses separate temporary `setup-toy-analysis-runs/run-001` and `run-002` bundles, a three-point toy grid, 16 deterministic samples, injected toy constants/inputs, and a nonwriting result sink. Both run-ID command branches and write/check dispatch are asserted. |
| Substring search let one retry approval authenticate either registered ID. | Approval evidence must contain exactly one column-zero marker in the exact form shown below. The parser scans only the selected approval event's already captured snapshot bytes, requires one registered marker across the artifact set, and requires equality to the requested/source ID. Incidental prose is ignored. Production permits only `run-001` and `run-002`; `toy-run` is explicitly injected only at the setup-result boundary. `inputs.json` and `README.md` bind the syntax and reviewer expectation. | Normal and registered-retry fixtures both mention `run-001` and `run-002` incidentally yet admit exactly one marker. Both cross substitutions fail. Separate cases reject missing, duplicate, conflicting, malformed, both-ID, unregistered, leading-space, and trailing-text markers. Existing exact-byte historical-evidence tests remain green. |

The exact production marker choices are:

```text
- **Admitted run:** `run-001`
- **Admitted run:** `run-002`
```

Exactly one applicable line is allowed across the immutable approval artifact
set; the two lines above must never appear together. No shared workflow file or
template changed.

## Bound bytes

The setup-v5 manifest bound 33 artifacts, was 5,547 bytes, and had SHA-256
`a9d4679f276ef51f4532b6413e099ffc0a5e96cf6b4256c9bba7790566a1395f`.
The setup-v6 manifest still binds 33 artifacts and is 5,547 bytes, SHA-256
`4fe3d8bb6f2f640186aed4599bc8f70508dbe892fbd9032fc0494b4e48dd645e`.
Unlisted entries are byte-identical.

| Path | Setup-v5 bytes / SHA-256 | Setup-v6 bytes / SHA-256 |
| --- | --- | --- |
| `README.md` | 7,779 / `3ca1e9b81b0444df556e3476a71876e0398289f97b94b65f49d161366e3c96ca` | 8,272 / `4d60c0b05cb6543713a86e2c9dfa13806b24c9ed15dae214c564a317cd49e7d2` |
| `inputs.json` | 5,235 / `a030f11b8badf7561bd9d38211a6d8b1a4c82ab72a7b9e279c63ea9b00b5e445` | 5,338 / `8e2d98f35f86678a7a018a13562ee4c9aa7b900a11ee58deb8b2007de4f82de1` |
| `src/analyze.py` | 28,966 / `83cdedc26f9f2600d8fec273f9a38943789167422c627478ea7e3ae6668f98a6` | 32,603 / `31b76513b51fb242c2d125b514cfe2e9ee76fd7f3f001be1788c251a664b6a84` |
| `src/contract.py` | 36,970 / `cf63f2042e34f2e1b91b4b5d5a3bdf67cde2f730364438729e0cbe2e183b7851` | 37,080 / `0e39a47ff344e6017bcb74cb6b3394b9013b0516adc150ce3b39955147161991` |
| `tests/test_pipeline.py` | 30,043 / `a84f0fba0e7aef0ab110071d06e182b11b50d9c6420b8068a9d5b5c09a84cc13` | 38,319 / `f5848e8a73a1ac0a618f11611fb6b6830db45569f48a27fc18706a9183eb1e40` |
| `tests/workflow_fixture.py` | 6,183 / `38bd59f2574b85370e0ba61e8d948bf9c3267ac9b30acc072753e0af277242a0` | 6,374 / `4478a1e483f98d85eb304c9457ea55de5a566691cc54d8087aa01d837a75fc49` |

The protocol, constants, sources, environment, requirements, schemas, graph,
workflow CLI, RNG, production grid, focal index, thresholds, execution/retry
rules, output paths, and publication-figure contract are unchanged.

## Tests, checks, and resources

The bounded full suite command was:

```sh
/usr/bin/time -v research/muon-survival-two-frames/.venv/bin/python -m unittest discover -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
```

The final run passed all 28 tests in 6.305 seconds of test time and 6.77 seconds
wall time, with 20.36 seconds user CPU, 1.15 seconds system CPU, 95,284 KiB
peak RSS, zero socket messages, and exit zero. An initial run reached both new
entrypoint branches but its final test assertion used two stale aggregate-key
names, producing two `KeyError` subtests. Only those assertion names changed;
the required rerun then passed.

Post-suite checks were:

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

All exited zero. The lock was fully satisfied and `pip check` found no broken
requirement. Setup verification reported CPython 3.12.3, pip 26.2.1, NumPy
2.5.1, Matplotlib 3.11.1, Node 24.18.0, all 33 manifest records, zero run
namespaces, and `production_absent: true`. Workflow status remained `setup`,
iteration 6; verification reported 15 events and 14 snapshots. Final targeted
path and output-absence scans are recorded at handoff.

## Boundary and retrospective

The frozen run command and all four frozen downstream analysis commands remain
byte-identical and unexecuted. The integration test uses no PCG64 call: its
16-value sample is supplied directly to the setup-only runner. It writes only
inside automatically removed temporary roots and sends its result to an
in-memory test sink.

This review materially caught one executable failure that 26 green tests had
missed and one real retry-lineage ambiguity. The useful boundary was requiring
the production entrypoint itself while permitting dependency-injected toy data.
The sixth full setup-review loop is disproportionate for a tiny Understanding
note, but bypassing either finding would have invalidated the later run.
Approximate implementation, testing, manifest, and receipt effort was 30
minutes. No frozen ambiguity arose.

Residual nonblockers are unchanged: external PDG availability, cross-host wheel
availability, installed-environment byte integrity, untested filesystem
semantics, and self-asserted actor identity. Keep the independent pre-exposure
setup gate; add a reusable entrypoint fixture and a structured review-field
helper to shared machinery later, on a separate branch. Reviewer focus: real
integrity-path execution, exact marker cardinality, incidental-mention immunity,
and both cross substitutions.
