# CASE-8JQJ transcription and correction log

Status: complete, agent-transcribed, and reverse-checked, 2026-07-18. This is operator-only
provenance. Source identities and source measure numbers in this file must not
be copied into the model-facing dossier.

## Authority and source hierarchy

- Content authority: `benda_1757_first_edition_slub.pdf`, PDF pages 18-19,
  engraved plates 11-12.
- The 1954 MAB score was used for notehead, accidental, rest, and rhythmic
  legibility only. Its editor expressly supplied dynamics, phrasing, fingering,
  and pedaling; none of that expression layer was copied.
- The embedded SLUB image is only 1000 x 707 pixels. The pinned IIIF manifest
  exposes the same 1000 x 707 maximum, so enlarging it does not add source
  information. Ambiguous noteheads were resolved against MAB and then checked
  back against the first print. Dynamics were accepted only when the 1757
  glyph itself remained visible.

## Structural and volta decisions

- Source m. 1 begins with a notated upper-staff downbeat rest. It is a full
  measure, not an anacrusis.
- Conventional exposition numbering ends with m. 26, but both written endings
  occupy physical notation. The physical traversal is `1-25, 26a, 26b,
  27-71, 72a, 72b`: 74 written bars in all. Each volta is counted once and no
  repeat is unfolded.
- The second part begins with conventional m. 27. Its physical duration is
  mm. 27-71 (45 bars) plus both written forms of m. 72 (2 bars), or 47 bars.
  At 3 quarter notes per bar, `second_part_total_qn = 141`.
- Candidate m. 51 starts after mm. 27-50, exactly 24 written bars into the
  second part, so `second_part_elapsed_qn = 72`. Its onset is `0/1`.
- Source windows are W1 = 1-8, W2 = 45-50, W3 = 51-56, and W4 = 57-62.

## Voice map

The mapping is stable across the movement:

- upper notated staff/layers -> `V01`;
- lower notated staff/layers -> `V02`.

The cross-staff passage at m. 50 was mapped by printed staff position. The
upper staff retains its low chordal layer; the lower staff's printed rests and
the lower note of the final split-staff chord remain `V02`. No hand assignment
or analytical voice-leading was inferred.

## Scan map and correction history

- W1 lies at the opening of plate 11.
- W2 mm. 45-47 are at the end of plate 11; mm. 48-50 occupy the final portion
  of plate 12 system 1.
- Candidate m. 51 begins plate 12 system 2. W3 continues through that system;
  W4 crosses into the following system.
- Early exploratory crops named `orig-m45.png` through `orig-m52-exact.png`
  were fixed-width strips, not bar-anchored crops. Their filenames were
  therefore misleading. A first expression pass consequently attached three
  correctly read glyphs to mm. 53-55. Reverse-table comparison exposed the
  displacement. The system was remapped from paired barlines and musical
  content, and the marks were corrected to m. 49 (`f`, onset 1), m. 50 (`p`,
  onset 2), and m. 51 (`f`, onset 1/2). The misleading files remain only in
  gitignored scratch space; this log preserves the failed path.
- A suspected missing bass rest at m. 52 was also caused by the same bad crop
  label. The correctly mapped first-edition bar shows a half-note chord and no
  separately printed final-quarter rest; no event was invented.

## Hard-to-read spots and final decisions

- M. 48: the nine-part descending division and the lower half-note chord were
  checked against MAB for pitch legibility, then against the 1757 beam and
  barline positions. The first eighth-triplet position is a rest.
- M. 49: only the first two lower-staff quarter notes are printed; the final
  beat is blank rather than carrying an explicit rest. The old `F:` glyph
  above the upper staff is the first-edition forte mark and is encoded at the
  onset of the following quarter-note attack.
- M. 50: low-resolution enlargement makes lower-staff glyphs resemble note
  stems. The primary scan plus MAB resolves a half-measure rest, a dotted-
  eighth rest, and a final sixteenth-note lower pitch split from the upper-
  staff chord. These are encoded explicitly as `V02`; the first-edition `p`
  is retained at onset 2.
- M. 51: the opening-theme figure begins over the sharp-inflected bass chord.
  That first event is the verified candidate onset. The first-edition `f` is
  placed anticipatorily during the opening rest at onset 1/2; it was not taken
  from MAB.
- M. 52: the upper staff contains one eighth rest followed by five eighth
  notes, not a nine-note run. Audiveris merged material across the following
  bar in one MAB pass; the first-print barline controls.
- Mm. 53-62: ornaments, ties, chromatic accidentals, and repeated semiquaver
  figures were checked bar by bar. MAB slurs, hairpins, dynamics, fingerings,
  accents, and pedaling were ignored. Empty arrays therefore mean verified
  absence in the 1757 print, not incomplete extraction.

## Tonic-D normalization

Original tonic G maps to D by -5 chromatic semitones and -3 diatonic steps.
The key signature maps from one sharp to two sharps. The compiler applies that
same interval to every pitch and preserves its diatonic spelling.

## Validation record

1. The 26 selected measures were compared with the first-edition plates;
   MAB was consulted only where the primary pixels could not distinguish a
   notehead, accidental, or rest value.
2. `node scripts/compile-transcription.mjs --case CASE-8JQJ` regenerated the
   dossier, and `--check` reproduced it byte for byte.
3. `node scripts/render-case-table.mjs --case CASE-8JQJ` generated the reverse
   event table. The table-to-scan pass caused the expression remap and m. 50
   lower-staff correction described above; the corrected table was rechecked.
4. Counts, pitches, written durations, transposition, fixed voice mapping,
   candidate onset, all three first-edition dynamics, and the 72/141 duration
   arithmetic were checked.
5. The model-facing JSON was scanned for composer, work, source key, source
   measure numbers, filenames, URLs, and free-form text. None is present.

An OpenAI Codex research agent performed the event-level transcription under
human operator supervision. No music-theory-trained human independently
transcribed or verified it. OMR was a fallible
legibility aid, not an independent extraction, and is not represented as one.
