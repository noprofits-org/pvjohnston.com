# Post-exposure amended protocol v2: panel-B numeric routes

## Status and parent

This is a disclosed post-exposure protocol version for an **Understanding**
note. It does not replace or edit
`research/muon-survival-two-frames/PREREGISTRATION-v1.md` (19,383 bytes,
SHA-256
`501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`).
It changes only the presentation contract for panel B of the one registered
figure. The explanatory question, model, computation, accepted values, and
scientific checks remain fixed.

This version is deliberately **not executable under workflow graph v1**. The
current graph has no reviewed edge for a post-exposure analysis-presentation
change that reuses an already admitted raw run. Its mandatory
`amended_setup -> amended_setup_review -> execute -> run_review` route requires
a new run contract and run lineage, whereas this amendment forbids another
production execution. Under the current written contracts, amendment review
should therefore choose `park`, not reinterpret validation of the old run as a
new execution.

## Same registered question and boundary

The question remains: How do time dilation in the detector frame and length
contraction in the muon frame give the same survival probability for an
idealized 3.00 GeV/c muon traveling 15.0 km?

The dependency order, assumed audience, fixed-momentum decay-only model, and
hard boundary in preregistration v1 are unchanged. This is not a new
hypothesis, novelty claim, contribution, falsifier, verdict, scientific curve,
or atmospheric-muon calculation.

## Results already exposed

The following v1 observations were exposed before this amendment. They are
copied from the immutable analysis handoff, not recalculated here.

- At 15,000 m the detector route reported beta
  `0.9993803712573206`, gamma `28.410999360495726`, laboratory time
  `5.006563638704876e-05 s`, dilated mean lifetime
  `6.24184286271212e-05 s`, exponent `0.8020970326909981`, and survival
  `0.4483876938726324`.
- The muon route reported beta `0.9993803712573205`, gamma
  `28.410999360495726`, contracted distance `527.964532668177 m`, proper
  elapsed time `1.762192021188205e-06 s`, proper mean lifetime
  `2.1969811e-06 s`, exponent `0.8020970326909982`, and survival
  `0.44838769387263233`.
- The registered sample reported 44,859 survivors of 100,000, empirical
  survival `0.44859`, focal absolute discrepancy
  `0.0002023061273676019`, analytic-probability binomial standard error
  `0.0015726924996839495`, and discrepancy
  `0.1286367979806972` standard-error units.
- The maximum grid discrepancy was `0.0018888456407246679`. Counts were
  100,000 at 0 km, 44,859 at 15 km, and 34,317 at 20 km and were monotonically
  nonincreasing.
- The same-speed no-lifetime-dilation counterfactual reported exponent
  `22.788378282839467` and survival `1.268040311737765e-10` at 15 km.
- Maximum frame-probability and nonzero-exponent relative differences were
  `3.050187851621567e-16` and `2.4002610167691026e-16`; all six aggregate and
  all 40 detailed registered checks were reported true.

These exposed values create a confirmation-bias risk: a renderer could choose
rounding, layout, or annotations that make the agreement look cleaner than the
stored result. The controls below bind every printed value directly to the
unchanged canonical JSON, require both stored exponents to remain separately
visible, and prohibit scientific or stochastic regeneration.

## Defect and affected predecessor lineage

The exposed 1,200 by 630 PNG at
`images/muon-survival-two-frames-hero.png` (65,124 bytes, SHA-256
`d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285`)
shows coincident exponent markers and symbolic formulas in panel B but does
not print the different frame-specific distances and times. Independent
analysis review found that presentation incomplete against the frozen figure
purpose.

The v1 presentation lineage is therefore superseded for publication, not
erased:

- `research/muon-survival-two-frames/src/render_figure.py` (6,001 bytes,
  SHA-256
  `240598a07744765bb2381a7150e38074dbcad9af1425d0f95a1d30860dac1c24`)
  remains the immutable v1 renderer.
- The v1 PNG remains byte-preserved at commit
  `32b34366d4d59bedcca41a085da54293ae4f5471` and by the digest above. A future v2 renderer may install one
  reader-facing canonical PNG at the same path only after preserving this Git
  object; it must not claim the new bytes are the v1 image.
- `research/muon-survival-two-frames/workflow/analysis-v1.md` (10,699 bytes,
  SHA-256
  `9d6bef1d10fe70ab2665039bf60444fee8fb6d52d9a5d280fe4e2e726ee030d2`)
  and its v1 analysis snapshot remain incomplete predecessor evidence rather
  than an approved analysis lineage.
- `research/muon-survival-two-frames/results/summary.json` (77,185 bytes,
  SHA-256
  `26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0`)
  and `research/muon-survival-two-frames/metrics.json` (6,586 bytes, SHA-256
  `b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8`)
  are exposed predecessor outputs. Their scientific values are held fixed, but
  they remain outside an accepted active analysis lineage until a lawful fresh
  analysis review can audit them.
- No post prose or bibliography entry exists, so none is quarantined.

The admitted raw predecessor remains immutable evidence:
`research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy`
(800,128 bytes, SHA-256
`6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229`)
and `runs/run-001/run-manifest.json` (3,935 bytes, SHA-256
`63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a`).
Event 25 superseded its active graph lineage by routing to amendment; this
protocol neither mutates nor silently re-admits it.

## Exact changed presentation decision

Only panel B changes. A lawful v2 renderer must consume the unchanged
`results/summary.json` and visibly print two independently formatted routes at
the 15.0 km focal point:

1. Detector row: laboratory distance `15.0 km`, laboratory travel time
   `50.06563638704876 microseconds`, dilated mean lifetime
   `62.4184286271212 microseconds`, and stored exponent
   `0.8020970326909981` as
   `t_D / (gamma tau_0)`.
2. Muon row: contracted distance `527.964532668177 m`, proper elapsed time
   `1.762192021188205 microseconds`, proper mean lifetime
   `2.1969811 microseconds`, and stored exponent
   `0.8020970326909982` as `t_M / tau_0`.

The differing distances and times, both mean lifetimes, and both unaltered
stored exponents must be legible in the PNG itself. The two exponent markers
must remain aligned on the common dimensionless axis; their equality is the
registered relative-tolerance statement, not a replacement of either stored
value by a shared hand-entered value. Labels must identify detector and muon
frames, and any equation typography must preserve the two distinct routes.

Panel A, the two-horizontal-panel layout, 1,200 by 630 PNG dimensions, palette,
analytic detector and muon curves, registered empirical curve, and exact label
`same-speed, no-lifetime-dilation counterfactual` are unchanged. The eventual
caption still states that the Monte Carlo is an implementation check of the
assumed exponential law and that the two frames are descriptions of one proper
time, not two causal mechanisms.

## Decisions held fixed

All v1 scientific and operational choices remain unchanged: PDG central
values and source digests; exact speed of light; momentum; grid and focal
index; fixed proper-lifetime law; PCG64 seed `20260808`; draw count; draw
operation and order; binary64 arithmetic; independent detector/muon
reconstruction formulas; inclusive survival comparison; counterfactual;
tolerances and all six acceptance checks; scope exclusions; environment pins;
resource ceilings; public-data boundary; and the absence of a Research
hypothesis or verdict.

No raw value, summary value, metric value, schema threshold, result timestamp,
seed, sample size, grid point, source, model term, curve, figure count, or
reader-facing claim may change. No RNG command, production run, resume,
registered retry, registered rerun, new seed, copied sample presented as a new
run, or second canonical output may occur.

## Intended versioned presentation artifacts

If a future graph version adds a reviewed post-exposure analysis-only route,
the narrow implementation would create, without editing v1 artifacts:

- `research/muon-survival-two-frames/src/render_figure_v2.py`;
- `research/muon-survival-two-frames/analysis-presentation-manifest-v2.json`,
  binding this protocol, the immutable run-001 manifest and sample, the
  unchanged summary, the v1 renderer/image, the v2 renderer, and the one
  canonical v2 image;
- focused presentation tests that reject a changed scientific value, a
  missing numeric route, equalized hand-entered exponents, wrong units,
  clipping, wrong dimensions, or mutation of the predecessor bytes;
- one deterministic write command owned by the analyst,
  `research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/render_figure_v2.py`;
- one read-only check command,
  `research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/render_figure_v2.py --check`;
  and
- a versioned analysis-v2 handoff followed by a complete fresh independent
  analysis review, including all numerical, schema, manifest, provenance,
  metrics, allowlist, visual, and reproducibility checks left outstanding by
  the first review.

The experiment engineer would own only the versioned renderer contract,
manifest, and focused tests; the analyst would own v2 rendering. The run
operator would have no work because production reuse is the invariant being
protected.

## Graph-v1 mismatch and stopping rule

Graph v1 cannot represent the intended route. Its `amended_setup` node must
freeze a new exact run contract. Its `execute` node directs the run operator to
run that command and return a receipt with run/shard IDs, timestamps, exit
states, raw-output hashes, and completeness. The workflow guide additionally
requires a new output namespace for each run and states that an approved
amended protocol receives a new run identifier.

A command that only runs
`src/validate_run.py --run-id run-001` would verify predecessor bytes but would
not execute a new run or create the required raw lineage. Calling its receipt a
new execution would be ceremonial. Creating `run-002`, copying or hard-linking
the old sample into it, or invoking the RNG would respectively disguise reuse
or violate this protocol's no-reroll boundary. Having the run operator invoke a
renderer would violate the role boundary.

Therefore the exact graph-v1 action after independent amendment review is
`park`. Approval is not requested because there is no contract-valid downstream
path. Work may resume only in a separate workflow using a new, reviewed graph
version that provides an analysis-only amendment route while preserving this
ledger, or after a separate shared-workflow change is merged and a fresh
workflow is initialized. This post branch must not change the shared graph or
workflow implementation.
