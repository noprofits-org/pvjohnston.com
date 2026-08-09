# Setup-review receipt

- **Gate:** `setup_review`, iteration 2
- **Actor:** `setup-reviewer-muon-04`
- **Decision:** `revise`

## Reviewed artifacts

Reviewed the supplied 29-file setup manifest and exact bytes. Material
bindings include:

- `workflow.jsonl` — 8,167 bytes — `7700f230…e22f294`
- setup-v2 evidence — 13,338 bytes — `5a4d6816…30f786c`
- setup-review-v1 — 6,619 bytes — `5a00feed…145944`
- `setup-manifest.json` — 4,924 bytes — `7b31d42a…cee1ed`
- `PREREGISTRATION-v1.md` — 19,383 bytes — `501f57ab…7bb855c`
- `inputs.json` — 3,938 bytes — `da290f0c…15cc02f`
- `constants.json` — 686 bytes — `62b7812b…7c56e87`
- environment records and lock — `d27e216c…a202f8`, `33b6f364…63fa`,
  `1cf5dcf8…c782`
- result schema — 5,260 bytes — `ecc41038…55c982`
- `src/analyze.py`, `bundle.py`, `contract.py`, `reconstruct.py`,
  `render_figure.py`, `run.py` — respectively `b90a8da6…06743`,
  `607188d6…d03de`, `2b6c6aab…471471`, `f892f4c9…adaec8`,
  `8b99133b…56ccc`, `947b4163…67ec3`
- `generate-metrics.mjs` — 6,701 bytes — `3608924a…63fa`
- pipeline/setup tests — `cec6cf3d…49cfd`, `4ca0d4a9…b71e58`

The remaining manifest entries comprise the README, prospective allowlist,
sources, five other schemas, validation/setup modules, package initializer,
fixture, and `.gitignore`, with the supplied sizes and full hashes.

## Checks

Confirmed unchanged Understanding protocol; fixed constants and integer grid;
PCG64 seed/draw contract; one float64 exponential call; separate detector/muon
functions; no scientific overrides; locked environment and serialization;
exclusive raw creation; enumeration of all run namespaces; preserved retry
namespace; real descriptor-level success/failure logs; result/PNG/metrics
exclusive writers and byte-check modes; counterfactual labeling; prospective
allowlist; amendment/retry limits; and bounded cost.

## Blockers

1. **High — canonical-result check mode becomes unusable after submission.**
   `src/analyze.py::_analysis_admission()` requires the requested `run_review`
   approval to be the ledger's final event. Once analysis is submitted into
   `analysis_review`, the final event is the analysis submission, so the
   registered `analyze.py --check` command cannot authenticate its historical
   approval. This breaks later read-only regeneration and review.

2. **High — execution authorization is event-shaped, not graph-validated.**
   `authorize_run_request()` checks only sequence numbering and selected fields
   on the final JSON line. The supplied test deliberately obtains authorization
   from a minimal synthetic event lacking experiment identity, graph
   version/hash, actor/role, submission linkage, and normal workflow fields.
   Thus `run-001`/`run-002` are not proven graph-authorized by the runner itself.

3. **Medium — schema/provenance fidelity is asserted rather than checked.**
   `registered_analysis_spec()` sets `schema`, `manifest`, `provenance`, and
   `hashes` flags to `True`; no result is validated against
   `analysis-result.schema.json`. Setup merely parses schemas and checks their
   root declarations.

4. **Medium — v1's independent branch-coverage blocker remains partially
   open.** The focal four-standard-error mutation `[16,0,4]` also fails
   monotonic counts and grid discrepancy; the upper-bound mutation also fails
   monotonicity. Tests use representative derived/unit/counterfactual mutations
   rather than independently exercising every bound field.

## Nonblockers

Atomic raw publication and success/failure stream lineage are materially
repaired. External PDG bytes remain unverified here; actor IDs remain
self-asserted; cross-host wheel availability and the metrics generator's absent
help mode remain operational risks.

## Route

- **Required route / next node:** `setup_review → setup`
- **Validity versus outcome:** Implementation-validity failure only. No
  canonical value, frame-agreement result, survival probability, or Monte Carlo
  outcome was executed or inferred.
- **Residual risk:** Authorization and review lineage could fail or be spoofed
  after graph advancement even if the numerical implementation is correct.
- **Smallest action:** Add a regression proving `analyze.py --check` succeeds
  after an analysis-submission event while binding the immutable historical
  `run_review` approval, then revise its admission validation.

## Independence and retrospective

Fresh independent session and actor confirmed. Review used only supplied bytes
and remained read-only: no tools, commands, network, connectors, mutations,
fixes, or substitute calculations.

The second iteration closed the raw-publication and process-stream defects,
but inspection caught a lifecycle regression hidden by setup-only tests: result
checking works only before the workflow advances. Approximate review effort:
28 minutes.
