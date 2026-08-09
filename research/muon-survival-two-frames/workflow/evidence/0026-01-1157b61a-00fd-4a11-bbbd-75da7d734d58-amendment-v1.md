# Post-exposure protocol amendment, version 1

- **Actor and role:** `research-brainstormer-muon-amendment-01`, configured
  `research_brainstormer`
- **Originating review:** event 25,
  `67b69527-ac4f-41cb-ae25-d9a0e8ef6d91`, decision `amend`;
  `workflow/analysis-review-v2.md`, 4,914 bytes, SHA-256
  `14e1b5d514ccf50e149a36d1710de821e3576584ff789a75085c6db0d15b90b4`
- **Requested gate:** `amendment_review`
- **Recommended graph decision:** `park`

## Exposed evidence and defect

The exposed v1 result reports analytic survival `0.4483876938726324`,
empirical survival `0.44859` (44,859/100,000), and no-dilation
counterfactual survival `1.268040311737765e-10` at 15 km. Detector and muon
exponents are `0.8020970326909981` and `0.8020970326909982`; maximum frame
probability relative difference is `3.050187851621567e-16`; maximum grid
discrepancy is `0.0018888456407246679`; all registered checks were reported
true. `AMENDED-PROTOCOL-v2.md` discloses the remaining exposed detector/muon
times, distances, lifetimes, counts, and Monte Carlo diagnostics.

The v1 PNG, 65,124 bytes and SHA-256
`d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285`,
shows aligned symbolic exponent routes but omits the visible numeric
frame-specific distances and times required by analysis review. This is a
presentation/provenance defect, not a disputed scientific value.

## Old and proposed protocols

- Old: `research/muon-survival-two-frames/PREREGISTRATION-v1.md`, 19,383
  bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- Proposed: `research/muon-survival-two-frames/AMENDED-PROTOCOL-v2.md`,
  11,184 bytes, SHA-256
  `52c45cc459eb218b0b494243216a1a78532f786c7411a9fd3d73d91bf6890fa0`.

The sole changed decision is panel-B presentation. It must print the detector
route (15.0 km, `5.006563638704876e-05 s`,
`6.24184286271212e-05 s`, exponent `0.8020970326909981`) and muon route
(`527.964532668177 m`, `1.762192021188205e-06 s`, `2.1969811e-06 s`,
exponent `0.8020970326909982`) directly from unchanged canonical JSON while
retaining two aligned exponent markers.

Every scientific and stochastic decision remains fixed: question, form,
sources, constants, model and exclusions, momentum, grid, focal point, frame
formulae, counterfactual, seed, generator, one 100,000-draw sample, thresholds,
checks, environment, resource bounds, and no-verdict Understanding contract.
No RNG rerun, new seed, new sample, extra curve, threshold change, or broader
claim is allowed.

## Superseded and preserved lineage

- The v1 renderer and image are superseded for reader-facing presentation but
  remain immutable predecessor evidence. The image is byte-preserved at commit
  `32b34366d4d59bedcca41a085da54293ae4f5471` and by the digest above.
- `workflow/analysis-v1.md` and its evidence snapshot remain an incomplete,
  unapproved predecessor analysis. The unchanged `results/summary.json`
  (`26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0`)
  and `metrics.json`
  (`b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8`)
  remain quarantined
  from an accepted active analysis lineage pending a lawful complete review.
- No prose or bibliography exists.
- Raw `run-001` is not overwritten or deleted. Its sample
  (`6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229`)
  and run manifest
  (`63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a`)
  remain immutable
  predecessor evidence. Event 25 superseded its active graph lineage; this
  packet does not silently re-admit it.

## Confirmation-bias controls

Both exposed exponent values must be printed independently from the canonical
result, rather than replaced by a hand-entered shared value. A versioned
presentation manifest must bind old and new renderers/images, unchanged raw and
summary digests, and focused tests must reject any scientific-value, unit,
dimension, label, or predecessor-byte change. A fresh reviewer must repeat all
nonvisual analysis checks that remain outstanding. The original figure stays
recoverable by immutable Git object and digest.

This remains the same question because it changes only whether the registered
two coordinate routes are numerically legible. It adds no mechanism,
population, uncertainty model, evidentiary claim, or outcome-dependent
scientific choice.

## Blocking graph mismatch

The narrow intended implementation would add a versioned v2 renderer,
presentation manifest, and focused tests; the analyst alone would regenerate
the one canonical PNG from unchanged `summary.json`. The run operator would do
nothing.

Graph v1 cannot represent that route. `amended_setup` must freeze a new exact
run contract; `execute` requires a run receipt with run/shard IDs, timestamps,
exit states, raw-output hashes, and completeness; the workflow guide requires
a new output namespace and run identifier for an amended protocol. Running
only `validate_run.py --run-id run-001` is a predecessor validation, not a new
execution. Creating or copying `run-002` would reroll or disguise reuse, and
having the run operator render would violate its role. Calling any of these a
compliant execution would be ceremonial.

Accordingly, amendment review should `park`. A future solution requires a
separately reviewed graph version with an analysis-only post-exposure amendment
lane, followed by versioned renderer setup review, analyst regeneration, and
fresh analysis review. This post branch must not edit shared workflow
machinery or invent that missing edge.

## Journal and review challenge

- **Brainstormer checkpoint:** journal session
  `20260809T045452Z-one-muon-two-frames-7ed9`, event
  `e2a449de-6ebf-459a-a05a-046c7b30fcd4`.
- **Amendment review must challenge:** whether any written contract actually
  permits unchanged-run re-admission through `execute`; whether the v2 scope is
  strictly presentation-only; whether all exposed and superseded bytes are
  disclosed; and whether `park` is required rather than a no-op.
- **Next action:** coordinator checkpoints the journal, submits this packet,
  and gives a fresh read-only amendment reviewer the exact graph, guides,
  protocol versions, review evidence, and predecessor digests. No setup,
  execution, analysis, or rendering begins first.
