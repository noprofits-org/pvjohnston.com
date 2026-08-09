# Workflow retrospective: muon-survival-two-frames

## Trial outcome

This deliberately small Understanding-note trial stopped honestly at the
terminal `parked` state. It did not reach writing, editorial review,
`ready_for_pr`, a draft pull request, CI, human review, or `ready_to_merge`.

The scientific computation itself completed once, within budget, and its
registered checks passed. Publication stopped for a workflow reason. The first
analysis reviewer found that panel B aligned the two dimensionless exponents
but did not visibly print the different frame-specific distances and times.
That presentation-only correction was required by the frozen figure purpose.
The approved setup manifest hash-bound the renderer, and the admitted raw run
hash-bound that setup manifest. After exposure, graph v1 routed the correction
through amendment, but its amendment path requires a new implementation/run
lineage and has no edge for reusing immutable admitted raw evidence solely to
regenerate a derived presentation. Rerunning, copying the sample, treating
validation as execution, or letting the run operator render would each violate
an explicit contract. Independent amendment review therefore chose `park`.

This is a workflow-valid stop, not a scientific verdict. The v1 analysis
handoff reported analytic survival `0.4483876938726324`, empirical survival
`0.44859` from 44,859 of 100,000 simulated lifetimes, and a same-speed
no-lifetime-dilation counterfactual survival
`1.268040311737765e-10` at 15 km. Detector- and muon-frame exponents were
`0.8020970326909981` and `0.8020970326909982`. All six aggregate and 40 detailed
self-checks passed, but the complete independent analysis gate did not approve
the presentation lineage.

## Scale and elapsed effort

The append-only workflow ran from 2026-08-09 04:55:26 UTC to 09:31:48 UTC,
about 4 hours 36 minutes. It ended with 27 workflow events, 26 evidence
snapshots, nine genuine backward edges, and 29 branch commits. The backward
edges were one question revision, six setup revisions, one analysis revision,
and one analysis amendment. The final `park` is a terminal decision, not a
backward edge.

Approximate stage effort was:

| Stage | Approximate elapsed time | Outcome |
| --- | ---: | --- |
| Preflight, protocol, question review | 32 minutes | One infrastructure-driven revision, then approval |
| Setup and setup review | 3 hours 4 minutes | Six revisions, then approval with 32 synthetic tests |
| Canonical execution and run review | 18 minutes | One run, approved without result inspection |
| Analysis and first analysis review | 16 minutes | All checks passed; visual presentation revision required |
| Provenance escalation and amendment review | 25 minutes | Missing graph edge confirmed; parked |

The canonical numerical work itself was tiny: one 100,000-draw sample, 201
grid points, one result, one PNG, and one metrics projection. The surrounding
workflow dominated elapsed effort.

## What the handoffs and gates clarified

- The question handoff kept this an Understanding note: a fixed-momentum,
  decay-only coordinate demonstration with no novelty claim, hypothesis,
  verdict, or real atmospheric-flux prediction.
- The setup handoffs made the executable contract unusually explicit: exact
  environment wheels, one seed and draw operation, immutable namespaces,
  historical review admission, independently reconstructed frame branches,
  schemas, provenance, hashes, and atomic derived publication.
- The run-operator boundary preserved blindness to the outcome. It executed
  the canonical command once, sealed six files, and did not analyze, plot,
  tune, or draft.
- The run review distinguished admissibility from a desirable result and
  admitted exactly `run-001` through an exact evidence marker.
- The analyst handoff exposed every focal value, uncertainty check, full-grid
  discrepancy, counterfactual, figure digest, and metrics digest without
  changing the frozen choices.
- The first analysis review caught a real omission against the user's figure
  request: symbolic routes and aligned exponent markers were not enough to
  show the differing numeric distances and times in the PNG itself.
- The second analysis review caught that a seemingly harmless renderer edit
  would invalidate the accepted manifest/run lineage. The amendment review
  then independently confirmed that graph v1 has no lawful continuation.

## Gates that materially improved the work

The setup reviews were materially useful despite their cost. Across six
iterations they caught incomplete end-to-end analysis, unauthorized run
namespaces, non-atomic raw creation, synthetic rather than real process-stream
capture, historical-approval replay defects, asserted rather than derived
schema/provenance flags, time-of-check/time-of-use gaps, incomplete
raw-to-metrics validation, ambiguous admitted-run identity, state-dependent
fixtures, and non-atomic derived publication. The final setup could replay in
both current and archived workflow states and passed 32 bounded synthetic
tests.

The run review materially protected the one-run rule and exact lineage. The
analysis review materially improved reader-facing fidelity by checking the
actual PNG rather than accepting passing numerical tests. The amendment review
materially protected provenance: it prevented a coordinator convenience from
being mislabeled as a valid execution.

## Gates and steps that felt disproportionate

Seven setup submissions and seven fresh setup reviewers were disproportionate
for a sub-minute, deterministic Understanding demonstration. The findings were
real, but most concerned general workflow machinery rather than the muon
explanation. That is defensible for this first acceptance test of the machinery;
it is not a sustainable default for every tiny note.

The question-review revision was caused by a review-infrastructure identity
failure rather than an intellectual defect. Repeated full evidence streaming
was also expensive because read-only reviewer shell sandboxes could not always
run their checks. Per-transition status, journal, evidence snapshot,
commit, and push operations provided excellent crash recovery but became
ceremonial at this scale.

Most importantly, the full post-exposure amendment loop was disproportionate
and then unusable for a derived-presentation correction. It correctly forbade
silent mutation, but it offered only a new raw-run lineage or a terminal park.
That false choice prevented a scientifically unchanged, independently reviewed
figure correction.

## Useful boundaries and bypass temptations

The most useful boundaries were producer/reviewer separation, run-operator
blindness, analyst ownership of derived outputs, and immutable raw evidence.
The analyst's refusal to edit a hash-bound renderer after exposure was exactly
the behavior the workflow is meant to elicit.

Bypassing a gate was tempting at three points: treating a different actor ID as
independence after a reviewer sandbox failure, editing the renderer because the
change was “only labels,” and calling `validate_run.py` a new execution so the
amendment graph could advance. Each shortcut would have made the audit trail
look complete while weakening its meaning. None was taken.

## CLI and template feedback

- `submit` accepts only small receipts under `workflow/`, while the amendment
  template speaks of a packet containing a new protocol version. The first
  two-artifact submit attempt was rejected without mutation, but the restriction
  should be stated before command execution and in the template.
- The status output is clear about current node, role, iteration, and allowed
  decisions. The append-only evidence snapshots made recovery and historical
  replay straightforward.
- The graph and guide should state explicitly whether amendment approval always
  requires new stochastic/raw execution. Their current combined contracts imply
  that it does, but this becomes apparent only after tracing several sections.
- Reviewer receipts would benefit from a standard field for “no graph-valid
  continuation,” distinct from scientific invalidity.

## Ranked recommendations

### Blocker — change

Add a reviewed post-analysis-only amendment lane. It should accept an immutable
previously admitted run and canonical result, require a versioned derived-output
contract and focused setup review, let only the analyst regenerate the figure
or metrics, and return to full analysis review. It must explicitly prohibit
new RNG, raw mutation, silent re-admission, threshold changes, and scope
expansion. This would preserve the safety gained here without inventing an
`execute` event.

### High value — keep

Keep independent pre-execution setup review, exact-byte raw provenance,
one-run enforcement, producer/reviewer separation, and the run operator's
non-interpretive boundary. Those controls caught substantive defects and
prevented outcome-driven repair.

### High value — change

Create a reduced, still-reviewed lane for tiny Understanding notes. Retain
question/protocol review, one proportionate setup review, blinded execution,
run integrity review, analysis/figure review, and editorial review, but scale
retry, resumability, sharding, and publication-atomicity requirements to the
actual risk and cost. Reviewers should consolidate related setup findings into
one pass where exact submitted evidence permits it.

### Later — remove

Remove the default expectation that every small deterministic Understanding
note implement the full research-grade retry/shard/resume apparatus when it has
one bounded local run and no external data. A documented fail-closed,
start-over-with-review rule is enough for this class of experiment.

### Later — change

Make CLI help and amendment templates name the receipt-only submission rule,
the referenced-protocol digest pattern, and the available post-exposure lanes.
Add a cheap command that emits a gate-scoped reviewer bundle so coordinators do
not repeatedly assemble very large evidence streams.

## Suitability conclusion

The full graph is valuable for consequential Research notes and for validating
new workflow machinery. It is too heavy and currently incomplete for tiny
Understanding notes. A reduced lane should still be independently reviewed and
should keep immutable evidence, blind execution, analysis review, and editorial
review. The reduction should remove unrelated operational ceremony, not
scientific or provenance scrutiny.
