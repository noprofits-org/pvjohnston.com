# Independent amendment review, iteration 1

- **Gate:** `amendment_review`, iteration 1
- **Actor:** `amendment-reviewer-muon-14`
- **Decision:** `park`
- **Independence:** Fresh reviewer session, distinct from the amendment author,
  producers, and prior reviewers as coordinator-confirmed. Review used only the
  attached v1 image and streamed artifacts; no tools, calculations, writes,
  workflow commands, or new scientific outputs were used.

## Reviewed artifacts

- `research/workflow.graph.v1.json` — SHA-256
  `e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404`
- `research/muon-survival-two-frames/PREREGISTRATION-v1.md` —
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- `research/muon-survival-two-frames/AMENDED-PROTOCOL-v2.md` —
  `52c45cc459eb218b0b494243216a1a78532f786c7411a9fd3d73d91bf6890fa0`
- `research/muon-survival-two-frames/workflow/amendment-v1.md` —
  `0d21fab4693951d67cab928c88fa16604af33c5c6f1bb94d546331edc496ffa3`
- `research/muon-survival-two-frames/workflow/analysis-v1.md` —
  `9d6bef1d10fe70ab2665039bf60444fee8fb6d52d9a5d280fe4e2e726ee030d2`
- `research/muon-survival-two-frames/workflow/analysis-review-v1.md` —
  `70d40817c1bf8960d599d89179b4fad4eaca814c04c20ac84340ff5de27df316`
- `research/muon-survival-two-frames/workflow/analysis-v2.md` —
  `7310dc53e6dfa068c2143133bab0c1d76638be20c08388a6cf2120109e0f8796`
- `research/muon-survival-two-frames/workflow/analysis-review-v2.md` —
  `14e1b5d514ccf50e149a36d1710de821e3576584ff789a75085c6db0d15b90b4`
- `research/muon-survival-two-frames/setup-manifest.json` —
  `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619`
- `research/muon-survival-two-frames/runs/run-001/run-manifest.json` —
  `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a`
- `research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy` —
  `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229`
- `research/muon-survival-two-frames/results/summary.json` —
  `26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0`
- `research/muon-survival-two-frames/metrics.json` —
  `b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8`
- `images/muon-survival-two-frames-hero.png` —
  `d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285`
- `research/muon-survival-two-frames/workflow.jsonl` through event 26, as
  streamed.

## Blocking findings

1. **Critical — graph v1 provides no honest downstream route for this
   amendment.** Approval necessarily enters
   `amended_setup -> amended_setup_review -> execute`. The graph and workflow
   contracts require amended setup to freeze a new run contract and execution
   to create a new output namespace, run identity, raw-output hashes, and
   execution receipt. The amendment instead prohibits every new production
   execution, RNG invocation, rerun, copied sample, or second canonical output.
2. **Critical — predecessor validation cannot satisfy `execute`.** Running
   validation against immutable `run-001` would check previously admitted
   evidence; calling that a new execution would mislabel lineage and supply
   none of the required new-run artifacts. Creating `run-002` by copying or
   linking the old sample would disguise reuse. Regenerating it would violate
   the amendment's no-RNG/no-rerun boundary.
3. **High — role substitution cannot repair the missing edge.** Having the run
   operator render or analyze panel B would violate the run-operator contract.
   Having amended setup silently authorize an analysis-only successor would
   invent a graph edge and provenance scheme absent from v1.

## Non-blocking observations

- The proposed scientific scope is narrow and remains the same Understanding
  question.
- The packet adequately discloses exposed values, the incomplete v1
  presentation, old/new protocol digests, superseded presentation artifacts,
  immutable `run-001`, and outstanding nonvisual review.
- Confirmation-bias controls are appropriate: preserve both stored exponents,
  source displayed values from unchanged canonical JSON, bind predecessor and
  successor bytes, and prohibit stochastic or scientific changes.
- The attached image corroborates the stated defect: panel B aligns the
  exponent markers but omits the numeric frame-specific distance and time
  routes.

## Exposed evidence and invalidated lineage

The v1 image, renderer, analysis handoff, summary, and metrics are exposed
predecessor evidence; the presentation/analysis lineage remains unapproved.
The admitted `run-001` sample and manifest remain immutable but were
superseded as the active graph lineage by event 25. They may neither be
silently re-admitted nor represented as newly executed.

## Protocol disposition and required route

- **Protocol v1:** immutable predecessor, not restored to active analysis.
- **Proposed protocol v2:** sufficiently disclosed but not approvable within
  graph v1 because its mandatory successor contract contradicts its
  no-execution invariant.
- **Required route:** `amendment_review -> parked`.

No edge, permission, run, result, or approval is invented. Continuation would
require a separately reviewed graph version and fresh workflow supporting a
post-exposure analysis-only presentation lane while preserving this ledger.

## Validity versus scientific outcome

Parking concerns workflow and provenance validity only. It does not reject or
approve the reported survival probabilities, frame agreement, Monte Carlo
observations, metrics, or all-pass claims. A scientifically tidy outcome cannot
make an invalid lineage admissible.

## Residual risks

- Actor identities remain self-asserted.
- The numerical, metrics, allowlist, and reproducibility audits remain
  incomplete.
- Any future workflow must prevent the new presentation route from silently
  re-admitting quarantined analysis or broadening the explanatory boundary.

## Smallest next action

The coordinator should record `park` against amendment submission event 26,
preserving all predecessor artifacts unchanged.
