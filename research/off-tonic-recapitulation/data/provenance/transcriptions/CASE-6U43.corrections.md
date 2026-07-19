# CASE-6U43 transcription and correction log

Status: complete and manually verified, 2026-07-18. This is operator-only
provenance. Source identities and source measure numbers in this file must not
be copied into the model-facing dossier.

## Authority and source hierarchy

- Content authority: `cpe_bach_wq48_1742_first_edition.pdf`, PDF pages 16-17,
  engraved plates 13-14.
- The Nagel 1927 score and the C. P. E. Bach Complete Works rendering were used
  only to resolve blurred noteheads, accidentals, and rhythmic alignment. No
  dynamics, articulation, ornament, slur, or phrasing was admitted merely
  because it appeared in either modern score.
- The 1742 scan was checked again after the modern-edition comparison. The
  selected windows contain no printed dynamics or articulations. The single
  encoded trill is visible in the 1742 plate.

## Structural decisions

- The movement begins on the downbeat. The first upper-staff note is at onset
  zero and the lower staff carries a full-measure rest; there is no anacrusis.
- The first part ends after source m. 29 and the second part begins at source
  m. 30. The `a)` and `b)` signs in the Nagel engraving are ossia references,
  not alternate endings.
- Manual barline traversal gives 44 measures on the first score page and 34 on
  the second, for 78 conventional measures total. The second page's system
  count is 7 + 6 + 6 + 6 + 5 + 4 = 34. This resolves the previously open
  denominator.
- Every measure is 6/8 = 3 quarter-note units. From m. 30 through m. 78 there
  are 49 written measures, so `second_part_total_qn = 49 * 3 = 147`. From the
  beginning of m. 30 through the beginning of candidate m. 51 there are 21,
  so `second_part_elapsed_qn = 21 * 3 = 63`.
- Candidate onset is the first event of source m. 51, hence onset `0/1`.
- Source windows are W1 = 1-8, W2 = 45-50, W3 = 51-56, and W4 = 57-62.

## Voice map

The mapping is fixed for the movement, not reassigned by texture:

- upper notated staff/layers -> `V01`;
- lower notated staff/layers -> `V02`.

Simultaneous notes within one staff become same-onset events with the same
voice ID. Staff-local polyphony is therefore allowed to overlap in the event
table; it is not converted into inferred hands or contrapuntal voices.

## Hard-to-read and normalization decisions

- Opening, mm. 4-7: the tied values and chromatic spellings were checked at
  high magnification. `B#`, `F##`, and `E#` are retained as written rather
  than respelled enharmonically.
- Opening, mm. 7-8: the semiquaver groups and lower-staff rests were checked
  note by note; beaming itself is outside schema 3.0.0, but its durations were
  used to establish the exact onsets.
- Pre-candidate, mm. 45-48: the alternating upper-staff quavers and the rests
  surrounding the lower-staff sustained notes were compared against the first
  print after consulting Nagel for notehead legibility.
- Pre-candidate, m. 49: the terminal ornament is a printed trill in the 1742
  plate. It is not an editorial ornament imported from Nagel.
- Pre-candidate, m. 50: the final beat contains a three-in-the-time-of-two
  division beginning at `5/3`. The longer simultaneous note belongs to the
  same upper staff; the event representation preserves the overlap rather than
  inventing a third movement-wide voice.
- Candidate and continuation, mm. 51-62: ties, rests, and the recurring
  chromatic spellings were checked against plate 14. The apparent repeated
  material was transcribed afresh and not copied mechanically from W1.
- Empty `directions` and articulation arrays mean verified absence in the 1742
  print. Slurs, beaming, clefs, tempo text, and display-only accidentals are
  outside schema 3.0.0 by design and were not encoded.

## Tonic-D normalization

Original tonic E maps to D by -2 chromatic semitones and -1 diatonic step.
The key signature maps from four sharps to two sharps. Every pitch is
transposed by that single chromatic-plus-diatonic interval, preserving source
spelling; no pitch was normalized independently.

## Validation record

1. The 26 selected source measures were traversed in scan order and reconciled
   with `CASE-6U43.source.json`.
2. `node scripts/compile-transcription.mjs --case CASE-6U43` regenerated the
   dossier, and `--check` reproduced it byte for byte.
3. `node scripts/render-case-table.mjs --case CASE-6U43` generated the reverse
   event table; all 26 measure blocks were compared with the two plates.
4. Counts, pitches, durations, ties, the trill, voice IDs, candidate onset,
   transposition, and the 63/147 duration arithmetic were checked.
5. The model-facing JSON was scanned for source identity, source coordinates,
   filenames, URLs, and free-form text. None is present.

There was no second independent human transcription. The retained compact
source, deterministic compiler, reverse table, this decision log, and audit
JSON are the compensating record; this limitation is reported rather than
described as independence.
