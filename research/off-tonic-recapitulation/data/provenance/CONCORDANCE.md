# Source concordance log (operator-only)

Verification of candidate coordinates and movement arithmetic against pinned
sources. Source names, keys, and measure numbers in this file are provenance
and must not enter `data/cases/*.json`.

Method: high-DPI PyMuPDF renders; manual bar-by-bar traversal of the authority
scan; staff-paired barline detection as an orientation aid; comparison with a
clean edition only where explicitly allowed for legibility; deterministic
regeneration and reverse-event-table review for completed dossiers. Date:
2026-07-18. Verifier: researcher agent (OpenAI Codex), under human operator
supervision. No second independent human transcription was available.

## Benda, 1757 Sonata No. 2 in G, movement iii — VERIFIED AND ENCODED

- Authority: SLUB first edition, PDF pages 18-19 / plates 11-12. The 1954 MAB
  edition was used only for note/rest legibility. Its dynamics, phrasing,
  fingering, pedaling, and articulations are editorial and were excluded unless
  independently visible in the 1757 print.
- Meter/key/opening: 3/4, G major. Source m. 1 begins with a downbeat rest and
  is a complete measure; no anacrusis.
- Exposition: conventional m. 26 has two written volta bars. The complete
  physical traversal is `1-25, 26a, 26b, 27-71, 72a, 72b`, 74 written bars.
  Conventional numbering resumes at m. 27 after the exposition endings and
  reaches m. 72 at the final pair of endings.
- Second part: m. 27 through the two written forms of m. 72 comprises 47
  physical bars, hence 141 quarter-note units. Candidate m. 51 follows 24
  physical second-part bars, hence elapsed 72 quarter-note units.
- Candidate: m. 51 begins plate 12 system 2. The opening-theme figure returns
  over the sharp-inflected bass immediately after the m. 50 cadence. Candidate
  onset is the barline (`0/1`).
- Windows: W1 = 1-8; W2 = 45-50; W3 = 51-56; W4 = 57-62. W2 mm. 45-47 are on
  plate 11 and mm. 48-50 on plate 12 system 1; W3 begins system 2.
- Expression authority check: the three encoded dynamics are visible in the
  1757 print at m. 49 (`f`, onset 1), m. 50 (`p`, onset 2), and m. 51 (`f`,
  onset 1/2). No MAB-only expression was admitted.
- Dossier: `CASE-8JQJ`, schema 3.0.0, deterministic compilation and reverse
  table both pass. Detailed crop-remapping corrections are retained in
  `transcriptions/CASE-8JQJ.corrections.md`.

## C. P. E. Bach, Wq. 48/3, movement iii — VERIFIED AND ENCODED

- Authority: 1742 first edition, PDF pages 16-17 / plates 13-14. Nagel 1927
  and the C. P. E. Bach Complete Works were used for notehead legibility only;
  expression was checked in the 1742 print.
- Meter/key/opening: 6/8, E major. The first event is on the downbeat; no
  anacrusis.
- Exposition: 29 measures. The repeat closes m. 29 and part 2 begins m. 30.
  The `a)`/`b)` marks in Nagel are ossia references, not voltas.
- Total: 44 measures on the first score page and 34 on the second (second-page
  systems 7 + 6 + 6 + 6 + 5 + 4), giving an exact final measure number of 78.
  The second part therefore contains 49 bars = 147 quarter-note units.
- Candidate: m. 51 is the final bar of the second score-page first system and
  begins at onset `0/1`. It follows 21 second-part bars = 63 quarter-note units.
- Windows: W1 = 1-8; W2 = 45-50; W3 = 51-56; W4 = 57-62.
- Dossier: `CASE-6U43`, schema 3.0.0, deterministic compilation and reverse
  table both pass. The selected 1742 measures have no printed dynamics or
  articulations; the one encoded trill is visible in the authority print.

## Clementi, Op. 10 No. 3, movement i — STRUCTURE RESOLVED; SCHEMA-BLOCKED

- Authority inspected: Longman & Broderip BnF scan, PDF pages 14-16 / plates
  13-15, common time with two flats.
- Key/mode resolved: B-flat major. The opening bass establishes B-flat and the
  first-part repeat closes on a B-flat-major tonic sonority. The G-minor IMSLP
  description concerns a different Artaria/op. 9 publication lineage.
- Pickup resolved: four semiquavers (one quarter-note unit) precede the first
  complete bar. W1 would contain measure `-1` plus complete mm. 1-8.
- Part 1 and candidate resolved: plate 13 contains 50 complete measures and
  ends with the repeat plus `Volti`. Part 2 begins at m. 51. Plate 14 system
  counts are 10 + 8 + 10 + 9 + 9, so system 3 begins at m. 69. The thematic
  return there is in the subdominant region and confirms candidate m. 69 at
  onset `0/1`.
- Fixed windows: W2 = 63-68; W3 = 69-74; W4 = 75-80. All were cropped before
  encoding.
- Provisional full traversal: 124 measures (50 + 46 + 28). This value was not
  promoted to a dossier duration because the case stopped before compilation
  and independent arithmetic recheck.
- **Blocker:** mandatory W3 m. 72 has a clearly printed textual `dimi:`/`dim.`
  instruction. Schema 3.0.0 can encode fixed dynamics and graphical hairpin
  states, but not a typed textual gradual-dynamic instruction. Treating it as
  a hairpin changes the source; omitting it violates complete dynamics
  coverage; free-form text is prohibited. Per `EXTRACTION_PROTOCOL.md`, the
  case was stopped before source JSON or model-facing JSON was written.
- Torricella-1783 concordance: **NOT PERFORMED — no Torricella source is on
  disk.** Later witnesses inspected for orientation did not replace the BnF
  authority.

## Mozart K. 333 / K. 545 / K. 570 — COMPLETED IN THE SYMBOLIC LANE

The three DCML dossiers, extraction configurations, and audit JSONs were built
and validated in the preceding corpus phase. For K. 333, the notated m. 63
repeat split and the beat-four return pickup were reconciled to the pinned
DCML coordinates before extraction. They are unchanged by this scan-based
work.

## Stray-reference fix

`PILOT_CORPUS.md` formerly summarized the windows as 8+8+8+8. It was corrected
to 8+6+6+6, matching the preregistration and extraction protocol.
