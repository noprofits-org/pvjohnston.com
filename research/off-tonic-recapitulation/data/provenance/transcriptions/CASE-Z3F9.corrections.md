# CASE-Z3F9 investigation and blocker log

Status: stopped before encoding, 2026-07-18. No compact transcription, dossier,
reverse table, or completed-case audit was created. This is the required
record of the resolved concordance and the schema blocker.

## Authority

- Source inspected: `clementi_op10_early_edition_bnf.pdf`, PDF pages 14-16,
  engraved plates 13-15.
- A Torricella 1783 source is not present on disk. Concordance with that
  lineage was **NOT PERFORMED**. Later Artaria, Knorr, and Litolff witnesses
  were explored in gitignored scratch space only as orientation aids; none
  superseded the BnF/Longman & Broderip print.

## Resolved structure before the stop

- The two-flat movement is in B-flat major, not G minor. The opening bass
  establishes B-flat and the first part closes at the repeat on a B-flat-major
  tonic sonority. The conflicting G-minor catalogue description refers to a
  different publication/set lineage and is not evidence about this print.
- Four semiquavers precede the first complete common-time bar. They total one
  quarter-note unit and are an anacrusis. W1 would therefore be `-1, 1-8`.
- Plate 13 contains the entire first part and 50 complete measures after the
  pickup. The repeat and `Volti` follow m. 50, so the second part begins at
  m. 51 on plate 14.
- Plate 14 systems were counted as 10 + 8 + 10 + 9 + 9 measures. The third
  system therefore begins at m. 69. Its opening material is the thematic
  return in the subdominant region, confirming the proposed candidate and its
  onset at the beginning of m. 69.
- The fixed source windows would be W2 = 63-68, W3 = 69-74, and W4 = 75-80.
  High-DPI bar crops for all 18 measures were produced and inspected before
  note encoding began.
- A full-movement traversal produced a provisional 124-measure count (50 on
  plate 13, 46 on plate 14, 28 on plate 15). Because the case stopped before
  compilation and a second duration pass, no elapsed/total rational based on
  that count was promoted into a dossier or audit.

## Schema blocker

Source m. 72, inside mandatory W3, contains a clearly printed textual
`dimi:`/`dim.` instruction. The glyph remains legible in the BnF scan and is
not a graphical diminuendo hairpin.

Schema 3.0.0 can encode fixed dynamic levels and graphical hairpin states
(`diminuendo_start`, `diminuendo_continue`, `diminuendo_stop`), but it has no
typed value that identifies a textual gradual-dynamic instruction. Encoding
the text as a hairpin would change the notational evidence; omitting it would
contradict the schema's claim of complete dynamics coverage. Free-form text is
also expressly prohibited by `EXTRACTION_PROTOCOL.md`.

The protocol requires exclusion when a mandatory window contains a construct
that schema 3.0.0 cannot represent without loss. Work therefore stopped on
this case before any source JSON or model-facing JSON was authored. This is a
schema limitation, not an unreadable-source guess.

## Methods tried

- PyMuPDF high-DPI page and system renders, manual bar traversal, annotated
  grids, and per-bar crops established the source coordinates.
- Three vertical/barline detectors were tried. Irregular staff-local barlines
  generated false positives, so automated counts were treated only as aids.
- Audiveris was run on full pages, isolated systems, and stitched staff pairs.
  It was useful for orientation but unstable on the early engraving and was
  never treated as authoritative notation.
- Later editions helped identify corresponding material, but no later
  expression mark was used to resolve the blocker: the textual `dimi:` is
  visible in the authority scan itself.

Any future inclusion requires either a preregistered schema revision that
represents textual gradual dynamics explicitly or a documented change to the
coverage claim, followed by a new freeze. It must not be silently mapped to a
hairpin under the current protocol.
