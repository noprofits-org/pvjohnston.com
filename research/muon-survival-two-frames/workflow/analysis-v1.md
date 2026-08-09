# Analysis handoff receipt

- **Gate:** `analyze`, iteration 1
- **Role:** configured `analyst`, distinct from the run operator and run reviewer
- **Requested gate:** `analysis_review`
- **Graph state at handoff:** still `analyze`; this analyst recorded no workflow transition
- **Post form:** Understanding
- **Outcome kind:** `understanding-observations-no-verdict`
- **Admitted run:** `run-001`
- **Admitting review event:** sequence 21, event ID
  `4cd15a35-b91f-494e-b98c-c10333f4f6e5`

## Frozen input and admission binding

The worktree was clean at commit
`511179dd580adead746fa626a532539edd381430` before exposure. The workflow
verified at `analyze`, iteration 1, with 21 events and 20 immutable evidence
snapshots. Event 21 is a `run_review --approve--> analyze` event and its sole
column-zero admission marker names `run-001`. No other run was considered.

| Repository-relative input | Bytes | SHA-256 |
| --- | ---: | --- |
| `research/muon-survival-two-frames/workflow.jsonl` | 21,954 | `506c94b72d3aa0c54efb84a23f0e18fc9d5036cfbf4c80e3b705c17122856bbc` |
| `research/muon-survival-two-frames/workflow/run-review-v1.md` | 4,675 | `9d7c6cca7e63616c052e5f2ed22c47f62873307c9f99f50efc057f951a2fd81b` |
| `research/muon-survival-two-frames/workflow/evidence/0021-01-4cd15a35-b91f-494e-b98c-c10333f4f6e5-run-review-v1.md` | 4,675 | `9d7c6cca7e63616c052e5f2ed22c47f62873307c9f99f50efc057f951a2fd81b` |
| `research/muon-survival-two-frames/PREREGISTRATION-v1.md` | 19,383 | `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377` |
| `research/muon-survival-two-frames/inputs.json` | 5,338 | `8e2d98f35f86678a7a018a13562ee4c9aa7b900a11ee58deb8b2007de4f82de1` |
| `research/muon-survival-two-frames/constants.json` | 686 | `62b7812bd19b50a189cf6b515f09b376d1f2be7334ccd44deb515063b7c56e87` |
| `research/muon-survival-two-frames/sources.json` | 2,105 | `dc11e517d7927efb19efec490cbd8668ee205ea397282cd2356b3d188d14707f` |
| `research/muon-survival-two-frames/environment.json` | 1,172 | `d27e216c106d13c513247aa78e3eb15186db516e47672b6f5acb0028a1ad0904` |
| `research/muon-survival-two-frames/setup-manifest.json` | 5,548 | `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619` |
| `research/muon-survival-two-frames/runs/run-001/run-manifest.json` | 3,935 | `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a` |
| `research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy` | 800,128 | `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229` |
| `research/muon-survival-two-frames/runs/run-001/COMPLETE.json` | 584 | `65adac211e77e676c13e1b37ea1be69391c711a2fb63b452ae0c0bf283874c77` |

The canonical result also records the admitting event-line SHA-256
`7671a6a1877106b405062f3f7d4d0f090b0a2945e333babd9a3bc5a7b18bd6d1`.
All 33 setup-manifest byte records verified immediately before analysis.

## Exact canonical commands

The following writers ran exactly once, in this order, from the repository
root:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-001 --run-review-event 4cd15a35-b91f-494e-b98c-c10333f4f6e5
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/render_figure.py
node research/muon-survival-two-frames/generate-metrics.mjs
```

Each exited 0. Each documented read-only check then ran and exited 0:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/analyze.py --run-id run-001 --run-review-event 4cd15a35-b91f-494e-b98c-c10333f4f6e5 --check
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/render_figure.py --check
node research/muon-survival-two-frames/generate-metrics.mjs --check
```

The check modes reread the same sealed sample and regenerated only in memory.
No production runner, RNG, retry, rerun, resume, repair, or alternative seed was
invoked.

## Canonical outputs

| Repository-relative output | Bytes | SHA-256 | Contract |
| --- | ---: | --- | --- |
| `research/muon-survival-two-frames/results/summary.json` | 77,185 | `26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0` | Canonical JSON; full schema and cross-field validation passed |
| `images/muon-survival-two-frames-hero.png` | 65,124 | `d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285` | PNG, RGBA, non-interlaced, exactly 1200 by 630 pixels |
| `research/muon-survival-two-frames/metrics.json` | 6,586 | `b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8` | Typed projection of the exact summary bytes |
| `research/muon-survival-two-frames/PUBLIC_FILES.txt` | 1,789 | `d1e4378422e957e6762f3e3062632e78b14769323783c71d5157ea59722be4d6` | Final reader-facing allowlist; entries equal the prospective inventory |

The three canonical scientific/publication outputs total 148,895 bytes. With
the complete six-file raw namespace they total 953,984 bytes, below the 10 MB
registered ceiling. The live allowlist excludes the external PDG PDFs, sealed
sample and logs, workflow receipts, caches, virtual environment, and normally
routed image. The raw sample remains public in Git but is not served as part of
the reader bundle; regenerating it requires the registered seed and locked
environment.

The metrics projection fingerprints `summary.json` with SHA-256
`26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0`
and carries the same generation timestamp, `2026-08-09T08:54:19Z`.

## Understanding observations

At the registered 15,000 m focal path:

- The detector route gives
  `beta=0.9993803712573206`, `gamma=28.410999360495726`, laboratory time
  `5.006563638704876e-05 s`, dilated mean lifetime
  `6.24184286271212e-05 s`, exponent `0.8020970326909981`, and survival
  `0.4483876938726324`.
- The independently reconstructed muon route gives
  `beta=0.9993803712573205`, `gamma=28.410999360495726`, contracted distance
  `527.964532668177 m`, proper elapsed time `1.762192021188205e-06 s`, proper
  mean lifetime `2.1969811e-06 s`, exponent `0.8020970326909982`, and survival
  `0.44838769387263233`.
- The one registered sample gives 44,859 survivors of 100,000, or `0.44859`.
  Its absolute focal discrepancy from the analytic probability is
  `0.0002023061273676019`; the prospectively defined analytic-probability
  binomial standard error is `0.0015726924996839495`, so the discrepancy is
  `0.1286367979806972` standard-error units.
- The same-speed, no-lifetime-dilation counterfactual has exponent
  `22.788378282839467` and survival `1.268040311737765e-10` at the focal path.
  It is a counterfactual, not a third frame.
- Across the 201-point 0--20 km grid, the maximum empirical-versus-analytic
  absolute discrepancy is `0.0018888456407246679`. Counts are integer,
  bounded, and monotonically nonincreasing: 100,000 at zero distance, 44,859
  at the focal path, and 34,317 at 20 km.
- The two analytic probabilities have maximum relative difference
  `3.050187851621567e-16`; the nonzero-path exponents have maximum relative
  difference `2.4002610167691026e-16`; beta relative difference is
  `1.1109113772450672e-16`; gamma relative difference is exactly zero.

These are observations from the frozen explanatory demonstration. They are
not a hypothesis, confirmatory verdict, independent test of relativity, or
atmospheric-muon-flux result. The Monte Carlo is an implementation check of the
assumed exponential law.

## Registered checks

All six registered top-level gates pass, and all 40 recorded detail fields are
true:

| Gate | Result |
| --- | --- |
| Frame probability, exponent, beta, gamma, and zero-path agreement | pass |
| Focal Monte Carlo discrepancy at most four analytic binomial SE | pass |
| Maximum grid absolute discrepancy at most 0.01 | pass |
| Count dtype, bounds, zero-distance value, monotonicity, and projection | pass |
| Numeric finiteness, shapes, dtypes, units, primitives, derived fields, and raw nonnegativity | pass |
| Result/run schemas, manifests, admission, provenance, bundle, and byte hashes | pass |

`checks.all_passed` and the projected `all_registered_checks_pass` metric are
both `true`. Original-resolution visual inspection confirms the registered
figure has two horizontal panels and legible A/B callouts: the left panel has
both coincident analytic frame curves, the empirical decay-law check, and the
explicit same-speed/no-lifetime-dilation counterfactual; the right panel has
aligned detector and muon exponent markers. No clipping or missing label was
observed.

## Deviations, post-hoc work, and reproducibility boundary

- **Protocol deviations:** none.
- **Analysis deviations:** none.
- **Post-hoc diagnostics or curves:** none.
- **Failed checks:** none.
- **Registered rerun:** none authorized and none requested or executed.
- **Amendment question:** none arose.
- **Raw mutation:** none; the six sealed run hashes remained unchanged.

The committed raw output supports deterministic regeneration of the analysis,
figure, and metrics, so this packet provides evidence for Traceable and
Analysis-reproducible status. End-to-end reproducibility remains not yet
established because the protocol requires a clean locked-environment
regeneration of the production sample and all derived bytes, and no production
rerun is authorized here.

Limitations are the frozen fixed-momentum, straight-path, decay-only model; no
production or momentum distribution, transport, atmosphere, energy loss,
scattering, detector response, capture, or flux calculation; no propagation of
PDG input uncertainty, momentum spread, path uncertainty, or model discrepancy;
and the run receipt's unavailable peak-RSS measurement. The Monte Carlo
standard error describes sampling under the assumed law, not uncertainty on
relativity.

## Questions for independent analysis review

1. Do the independent detector and muon reconstructions, focal projections,
   and registered gate derivations agree with the frozen protocol and schema?
2. Does the figure communicate coincident coordinate descriptions rather than
   two causal mechanisms, and is the counterfactual label sufficiently explicit?
3. Does `metrics.json` trace every planned quantitative field to the exact
   canonical result with appropriate types, units, and formatting?
4. Is the reader-facing allowlist acceptable, including its explicit omission
   of the served raw sample and its associated reproduction boundary?
5. Does review agree that no outcome-aware change, post-hoc diagnostic,
   atmospheric-flux claim, rerun, or amendment is present or needed?

The analyst did not author the post, edit the bibliography, transition the
workflow, commit, or push.
