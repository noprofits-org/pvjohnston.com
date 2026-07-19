# Reconciliation of the Fable 5 read-only survey

Date received and reconciled: 2026-07-19

Status: dated development audit; not an expert music-theory review

The operator supplied a read-only repository survey produced by Claude Fable
5 before the latest pre-freeze work. This record preserves the portions that
remain relevant and identifies conclusions superseded by later artifacts. It
is model-assisted protocol audit, not independent external validation.

## Superseded findings

- The survey's five-dossier, 90-call, and 270-cue-cell conclusions no longer
  describe the development corpus. `CASE-D09B` (Mozart K. 576/i) is now the
  sixth hash-matched dossier, restoring 108 planned calls and 324 analysis cue
  cells.
- Clementi's schema-3.0 stop was valid when made, but schema 3.1 now represents
  textual gradual dynamics. Clementi remains deferred because only mm. 69--71
  have converged to authority-checked events; the other 24 selected measures
  have not completed the required double pass.
- The music-theory worktree is no longer clean. The current dossiers, review
  packet, adapters, and collection machinery are still uncommitted development
  work and must be frozen together before any real-case model call.

## Findings that remain operative

- The launch corpus has a disclosed 2 focal + 3 tonic-anchor + 1 off-tonic
  positive-control balance. K. 545 remains the only clear off-tonic anchor.
  K. 576's source and normalized tonic are both D, so its identity transform
  preserves exact pitch and register; it supports no causal masking claim.
- Wq. 48/3 contains 78 measures under the retained traversal.
- The Benda audit should not be shortened to “73 measures.” It records a
  conventional final measure 72 and 74 physical written bars because 26 and
  72 each have `a` and `b` physical bars.
- The main checkout contains separate uncommitted research work and must not be
  cleaned or moved as part of this experiment freeze.

## Source-preservation action

The survey correctly warned that exact legibility-source files and retrieval
identifiers existed only in the main checkout. The experiment source manifest
now records metadata for the MAB 1954 Benda file, Nagel 1927 Wq. 48 file, and
Farrenc 1861 orientation file, including their SHA-256 hashes and IMSLP file
identifiers. The scans were not copied into this worktree and are not proposed
for publication. The 1742 Wq. 48 file in the main checkout is byte-identical to
the authority copy already preserved in the experiment worktree.

## Scope boundary

The survey also discussed branch cleanup, unrelated physics work, and possible
future merges. Those operations are outside this experiment freeze. No branch
was merged, deleted, or moved during this reconciliation.
