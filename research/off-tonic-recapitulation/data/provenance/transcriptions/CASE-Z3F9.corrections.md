# CASE-Z3F9 investigation and correction log

Status: retained, structurally reconciled, and awaiting a lossless event-level
double pass as of 2026-07-19. No model-facing dossier has been promoted from
the provisional transcription.

## Authority and concordance witnesses

- Notation and expression authority: `clementi_op10_early_edition_bnf.pdf`,
  PDF pages 14-16 / engraved plates 13-15, Longman & Broderip early print.
- Secondary coordinate witness: Andrew Brownell, *The English Piano in the
  Classical Period: Its Music, Performers, and Influences* (DMA thesis, City
  University London, 2010), repository item 12134. Example 3.8 is captioned
  “Sonata Op. 10 No. 3, I, mm. 67-74” and “Copied from Torricella, Vienna,
  1783.” The downloaded accepted manuscript had SHA-256
  `bb639fa524fa67c406489d56e580f846c7668c527c1cfc29b0c43c217798373d`.
- Brownell is a partial copied excerpt, not a scan of the complete Torricella
  edition. It can establish the conventional numbering and concordance of
  mm. 67-74, but it does not replace the BnF print as the authority for any
  selected measure or expression mark.
- Greenberg does not work through this Clementi movement as a case study; the
  case-specific scholarly connection is Brownell. Any publication claim that
  calls Clementi a source-paper example must identify Brownell rather than
  attributing this passage analysis to Greenberg.
- Later Artaria, Knorr, and Litolff witnesses were consulted for notehead,
  register, and voice-layer legibility only. Their expression, articulation,
  phrasing, and other editorial content is excluded unless independently
  visible in the BnF authority.

## Corrected structure

- The movement is in B-flat major, common time. Four semiquavers form a
  one-quarter-note anacrusis before m. 1; W1 is therefore the pickup plus
  complete mm. 1-8.
- The first manual pass incorrectly counted plate 13 as 50 complete measures.
  Its five systems actually contain 8 + 10 + 9 + 9 + 9 = 45 measures. The
  repeat closes m. 45 and part 2 begins at m. 46.
- That five-bar error propagated into the provisional crop labels: files named
  `return-bars/m69.png` through `m80.png` correspond to actual mm. 64-75.
- Brownell's Torricella-derived mm. 67-74 match the BnF passage note for note:
  actual m. 67 carries textual `dim.`/`dimi:`, m. 68 carries `pp`, m. 69 is the
  cadential/rest bar, the return pickup begins at m. 70 onset 3 quarter-note
  units, and the first full thematic bar is m. 71. This independently exposed
  the inherited five-bar offset.
- The corrected fixed windows are W2 = 64-69, W3 = 70-75, and W4 = 76-81.
  Candidate metadata uses m. 70 onset `3/1`, matching the protocol's treatment
  of a thematic pickup inside a complete measure.
- The movement ends at m. 119: 45 measures on plate 13, 46 on plate 14, and
  28 on plate 15. Part 2 therefore comprises m. 46-119 = 74 written bars =
  296 quarter-note units. The candidate follows 24 full part-2 bars plus three
  quarter-note units, so elapsed duration is exactly 99 quarter-note units.

## Schema revision

The original stop was correct under schema 3.0.0: actual m. 67 contains a
printed textual gradual dynamic, while that schema could represent only fixed
levels and graphical hairpins. Mapping the text to a hairpin or omitting it
would have changed or lost source evidence.

Schema 3.1.0 now adds the closed direction type
`textual_gradual_dynamic`, with values `crescendo` and `diminuendo`. The BnF
surface spelling remains in this operator log; the model-facing representation
would carry only the typed `diminuendo` meaning and would not infer an endpoint
or target level. This is the smallest lossless extension needed by the case.

## Partial event convergence

High-resolution BnF crops exist for every corrected window, and Brownell makes
the return neighborhood unusually well corroborated. An independent visual
pass converged only on actual mm. 69-71. These operator-key readings are
retained so the work is not lost, but they are not a dossier and do not imply
that adjacent bars are complete:

- m. 69: `V01` B-flat3+D4 quarter, quarter rest, half rest; `V02`
  B-flat1+B-flat2 quarter, quarter rest, half rest. No printed supported
  direction, articulation, or ornament.
- m. 70: `V01` three quarter-note units of rest, then C5-B-flat4-A-flat4-
  B-flat4 as four semiquavers; `V02` whole rest; printed `f` at onset 3.
- m. 71: `V01` E-flat5, G4, E-flat4, B-flat4 as four quarter notes; `V02`
  whole rest. The printed slur across the upper notes is outside schema 3.1.0;
  no supported articulation, ornament, or direction is printed in the bar.

Exact compact arrays from that partial pass, in the original key, are:

```json
{
  "69": {
    "events": [
      ["n", 0, 1, "V01", ["Bb3", "D4"]],
      ["r", 1, 1, "V01"],
      ["r", 2, 2, "V01"],
      ["n", 0, 1, "V02", ["Bb1", "Bb2"]],
      ["r", 1, 1, "V02"],
      ["r", 2, 2, "V02"]
    ],
    "directions": []
  },
  "70": {
    "events": [
      ["r", 0, 2, "V01"],
      ["r", 2, 1, "V01"],
      ["n", 3, "1/4", "V01", ["C5"]],
      ["n", "13/4", "1/4", "V01", ["Bb4"]],
      ["n", "7/2", "1/4", "V01", ["Ab4"]],
      ["n", "15/4", "1/4", "V01", ["Bb4"]],
      ["r", 0, 4, "V02"]
    ],
    "directions": [["d", 3, "V01", "f"]]
  },
  "71": {
    "events": [
      ["n", 0, 1, "V01", ["Eb5"]],
      ["n", 1, 1, "V01", ["G4"]],
      ["n", 2, 1, "V01", ["Eb4"]],
      ["n", 3, 1, "V01", ["Bb4"]],
      ["r", 0, 4, "V02"]
    ],
    "directions": []
  }
}
```

This block is partial operator provenance only. It must not be copied into a
compact source until the complete 27-measure pass has converged.

## Remaining event-level gate

Later-edition OMR is useful for orientation but is not reliable enough to
promote automatically: it misses barlines, merges or overfills measures, and
occasionally displaces octave or staff assignment. Twenty-four of the 27
evidence measures remain unresolved:

- W1 pickup and mm. 1-8: exact staff/layer assignment in mm. 2-4 and 7-8,
  followed by a complete BnF-only expression/articulation/ornament pass;
- W2 mm. 64-68: layer/rest completion in mm. 64-66 and exact cross-staff pitch,
  voice, and tie encoding in mm. 67-68 (the textual diminuendo at m. 67 and
  `pp` at m. 68 are certain);
- W3 mm. 72-75: exact cross-staff/layer/tie encoding and BnF-only mark pass;
  and
- W4 mm. 76-81: exact polyphonic layers, ties, rests, and BnF-only marks.

Until that complete bar-by-bar double pass converges, the case remains selected
but unencoded. No guessed array may be labelled complete, no unverified dossier
may enter a collection lock, and collection must not be described as a frozen
six-case experiment.
