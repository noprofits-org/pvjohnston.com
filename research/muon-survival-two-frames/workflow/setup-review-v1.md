# Setup-review receipt

- **Gate:** `setup_review`, iteration 1
- **Actor:** `setup-reviewer-muon-03`
- **Decision:** `revise`

## Reviewed artifacts

- `.codex/agents/independent_reviewer.toml` — 4,232 bytes — `a584f9069f557310f37cbfa6f5e1279af4891e15fb3f525739a7a747fdeda561`
- `research/muon-survival-two-frames/workflow.jsonl` — 6,070 bytes — `d5442fd590e4acd99a82620d725d40c61f4e282b9093cb6cfe7ce42c7771f47b`
- `research/muon-survival-two-frames/workflow/evidence/0006-01-3222727d-1b19-48e4-b3e6-f93bb3a65780-setup-v1.md` — 10,778 bytes — `1a27b0ad054c213ed05f821c85639d2d40e53667554150ec16ee71b7a5c75fb4`
- `research/muon-survival-two-frames/workflow/question-review-v2.md` — 4,393 bytes — `51a833efeb30239403e717e1fd5ef444b2ba588773c004a0e38073d51c00bd89`
- `research/muon-survival-two-frames/setup-manifest.json` — 4,266 bytes — `601fc4209f8edbab56a9432171c6fab21370a90414eb2c73dd069ab5e1468d10`

The setup manifest's supplied path/byte/SHA-256 records cover all 25 bound
artifacts: protocol, prospective allowlist, README, constants, sources, inputs,
environment records, dependency lock, six schemas, six source modules, fixture,
tests, `.gitignore`, and package initializer. Directly material code reviewed
included `src/contract.py`, `src/bundle.py`, `src/run.py`,
`src/reconstruct.py`, `src/validate_run.py`, and `tests/test_setup.py`.

## Checks and traces

Constants, units, input digests, fixed grid, focal index, tolerances, seed, draw
count, PCG64 construction, one-call exponential draw, float64 shape, and
unsorted storage trace into manifests and source. Detector and muon routes are
separately implemented; the muon route does not call the detector route, and
the supplied toy test patches that route to fail. Counterfactual and Monte
Carlo labels are appropriate.

The supplied setup-only evidence reports the exact locked environment, clean
`pip check`, 25 verified artifacts, nine passing toy/synthetic tests, no `runs`
directory, no local absolute receipt/manifest paths, and no production
exposure. No canonical quantity was executed, calculated, or inferred in this
review.

## Blocking findings

1. **High — the frozen analysis and fidelity contract is not implemented end
   to end.** No bound analysis entrypoint, canonical-result writer, PNG
   generator, metrics generator, or regeneration/check mode exists; the
   prospective allowlist merely names future `results/summary.json`,
   `metrics.json`, and `generate-metrics.mjs`. `evaluate_checks()` also ignores
   the primitive inputs, actual grid, counterfactual, frame distances,
   elapsed-time arrays, mean lifetimes, and units. Consequently its
   `numeric_shapes_dtypes_units_valid` branch can pass while ignored registered
   derived fields are invalid. The permissive analysis schema does not close
   this gap.

2. **High — unauthorized production namespaces bypass the retry contract.**
   `run.py` and `production_command()` accept every `run-NNN`; `build_spec()`
   does not require `run-001` or evidence of an authorized infrastructure
   retry. Separately, `setup_validation()` checks only whether `runs/run-001`
   is absent before returning `production_absent: true`. Thus `run-002` can be
   produced or remain present without the frozen authorization condition being
   enforced or detected.

3. **High — raw-sample overwrite refusal is not atomic.**
   `_save_array_exclusive()` checks whether the final path exists and then
   calls `os.replace(temporary, path)`. A file appearing between that check and
   `os.replace` is silently overwritten, contradicting the stated immutable,
   overwrite-refusing namespace contract.

4. **Medium — the claimed all-branch tests are incomplete.** The tests exercise
   probability disagreement, one monotonic-count failure,
   maximum-discrepancy failure, and one integrity flag. They do not
   independently fail focal four-standard-error acceptance; exponent, beta,
   gamma, or exact-zero subbranches; count bounds, zero count, dtype, or
   empirical/count equality; numeric validity; or the ignored
   derived-field/counterfactual conditions.

5. **Medium — sealed stdout/stderr are not the process streams.**
   `seal_run_bundle()` writes fixed synthetic log bytes, while `run.py` prints
   its actual message after bundle validation and does not redirect execution
   streams. Exceptions likewise reach the real stderr rather than the sealed
   file. The purported stdout/stderr artifacts therefore do not provide the
   registered execution-log lineage.

## Nonblocking observations

Source-manifest transcription is internally consistent, but the external PDG
PDF bytes were not supplied, so their contents and digests were not
independently reverified. The prospective allowlist is safely inactive, though
it omits several manifest-bound schemas/tests needed for a self-contained
served-bundle verification; editorial review can narrow or complete it. Actor
IDs remain self-asserted rather than authentication.

## Route and scope

- **Route / next node:** `setup_review → setup`
- **Validity versus outcome:** This is an implementation-validity failure only.
  It says nothing about frame agreement, survival probability, Monte Carlo
  behavior, or any scientific outcome.
- **Residual risks:** External-source availability, platform-specific wheel
  availability, unauthenticated retry authorization, and incomplete public
  reproducibility remain after the identified defects.
- **Smallest next action:** Add a setup regression test proving that an
  unapproved `run-002` is rejected and cannot be reported as production-absent,
  then revise the implementation under the existing prospective protocol.

## Independent confirmation and retrospective

Fresh independent session and actor confirmed. Review was entirely read-only
and used only the supplied bytes—no tools, commands, network, connectors,
mutations, fixes, or substitute computation.

- **Clarification:** The protocol clearly distinguishes Understanding checks
  from a scientific verdict.
- **Caught/confirmed:** Confirmed separate frame/RNG implementation; caught
  retry authorization, atomic overwrite, incomplete fidelity checking,
  branch-coverage, and log-lineage defects.
- **Ceremony:** Digest-bound setup review was useful because fluent handoff
  claims exceeded the inspected implementation.
- **Boundaries:** The no-production-exposure and no-reroll boundaries remain
  valuable.
- **Bypass temptation:** The simple arithmetic did not justify running the
  canonical command or inferring expected values.
- **Elapsed effort:** Approximately 24 minutes.
