# Brainstorm handoff: version 2

- **Graph state:** `brainstorm`, iteration 2.
- **Actor and role:** `research-brainstormer-muon-trial-v2`, configured
  `research_brainstormer` session.
- **Current durable commit:** `1acdb043fc1ac8f78447497a40337a53f4d84d4b`.
- **Declared form:** Understanding, unchanged.
- **Outcome:** not inspected. No survival calculation, production execution,
  analysis, plot, metric, implementation, or post prose exists.
- **Requested gate:** fresh `question_review` of the unchanged protocol.

## Unchanged scientific packet

No scientific artifact, parameter, equation, threshold, source, environment
intent, scope boundary, figure plan, retry rule, or publication constraint was
changed after the first submission.

- `research/muon-survival-two-frames/PREREGISTRATION-v1.md`: 19383 bytes,
  SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- `research/muon-survival-two-frames/workflow/brainstorm-v1.md`: 9007 bytes,
  SHA-256
  `98385040aeceeeee72d9b3622b703607d2236fd6a40e1155ec35dd3d6fa78119`.

Both current files produce the same digests as commit
`7d4efa19a58a` and current commit `1acdb043fc1a`. The v1 receipt is byte-for-byte
identical to its immutable submission snapshot:

- `research/muon-survival-two-frames/workflow/evidence/0002-01-41d0fca8-1fbe-4c45-83b3-37c0c51a17ef-brainstorm-v1.md`: 9007 bytes,
  SHA-256
  `98385040aeceeeee72d9b3622b703607d2236fd6a40e1155ec35dd3d6fa78119`.

The exact ten scientific and workflow challenges requested for
`question_review` remain those in `workflow/brainstorm-v1.md`. They cover the
Understanding form and stopping boundary, independent and dimensionally sound
frame reconstructions, one-proper-time interpretation, counterfactual labels,
Monte Carlo semantics, frozen checks, PDG provenance, no-reroll/retry rules,
feasibility, and the two-panel figure contract.

## Infrastructure-only back-edge

The first submitted receipt advanced as event 2 to `question_review`. A fresh
read-only reviewer returned `revise` solely because its local sandbox failed
before artifact reads or hashing with:

`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`

The reviewer explicitly made no scientific finding or outcome claim. Its
report is preserved as:

- `research/muon-survival-two-frames/workflow/question-review-v1.md`: 3108
  bytes, SHA-256
  `b619fb6737d05fdb29f1510a7ec71bb0a4cb119e84420df2032a45e776b2bb3d`.
- `research/muon-survival-two-frames/workflow/evidence/0003-01-33df4db5-c7a0-40c2-84a8-3302ae8a0086-question-review-v1.md`: the same
  3108 bytes and SHA-256.

Event 3 records the genuine `question_review --revise--> brainstorm` back-edge.
Current replay has three events, two evidence snapshots, no accepted or stale
lineage, one routed review, and no production exposure. Before this v2 receipt
was created, `workflow.jsonl` had SHA-256
`3ec4a3ff4c7d94558be82ee26ce85e024d2578ee1feb40d8edb79980b3b60e4a`;
the pinned graph digest is
`e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404`.

## Corrective delivery contract

After the coordinator submits this v2 receipt and the CLI creates its immutable
evidence snapshot, give a genuinely fresh read-only reviewer a byte-delimited
stream containing:

1. the submitted v2 evidence-snapshot bytes, byte count, and SHA-256;
2. the unchanged `PREREGISTRATION-v1.md` bytes, byte count, and SHA-256 above;
3. the unchanged v1 receipt and prior infrastructure-only review bytes when
   needed to verify lineage; and
4. the exact `question_review` gate and allowed decisions: `approve`, `revise`,
   or `park`.

The reviewer should inspect and hash the streamed immutable bytes directly and
must not depend on a local repository namespace. It remains read-only, returns
structured findings and one allowed decision, performs no substitute analysis,
and does not invoke the workflow transition. The coordinator saves the report
and records the decision.

## Checks and residual risk

Recovery used journal `list`, `show`, and `verify`, followed by workflow
`status --json` and experiment-scoped `verify`. Direct `cmp` checks established
source-receipt/evidence identity, and `git show | sha256sum` established v1 byte
identity at both relevant commits. The worktree was clean before this one new
receipt.

The only unresolved question-review risks are the substantive ones already
listed in v1; they remain unaudited rather than newly defective. The immediate
operational risk is truncation or delimiter ambiguity in the streamed packet.
The coordinator should include byte counts and SHA-256 values and require the
reviewer to echo them before deciding.

## Retrospective

The graph behaved honestly: inability to inspect bytes could not become an
approval, and the back-edge preserved that fact. For this tiny packet, however,
one stalled reviewer launch, one sandbox namespace failure, a review receipt,
a ledger transition, a durable commit, and this unchanged resubmission added
substantial infrastructure time without changing science. A high-value workflow
improvement would be a preflighted, first-class streamed-evidence mode for
read-only reviewers, with digest verification before the review clock starts.
The CLI message that only small `workflow/` receipts may be submitted was also
learned by rejection rather than made prominent at the initial handoff.

## Next action

The coordinator should inspect status and evidence, leave a fresh journal
checkpoint, submit only this small v2 receipt, commit and push the transition,
then launch the fresh streamed-byte `question_review`. This producer does not
submit, review, commit, or push.
