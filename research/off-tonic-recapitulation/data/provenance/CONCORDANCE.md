# Source concordance log (operator-only)

Verification of candidate coordinates and movement arithmetic against pinned
sources. Source names, keys, and measure numbers in this file are provenance
and must not enter `data/cases/*.json`.

Method: high-DPI PyMuPDF renders; manual bar-by-bar traversal of the authority
scan; staff-paired barline detection as an orientation aid; comparison with a
clean edition only where explicitly allowed for legibility; deterministic
regeneration and reverse-event-table review for completed dossiers. Date:
2026-07-18. Verifier: researcher agent (OpenAI Codex), under human operator
supervision. No music-theory-trained human performed an event-level
transcription or independent verification pass.

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
- Dossier: `CASE-8JQJ`, schema 3.1.0, deterministic compilation and reverse
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
- Dossier: `CASE-6U43`, schema 3.1.0, deterministic compilation and reverse
  table both pass. The selected 1742 measures have no printed dynamics or
  articulations; the one encoded trill is visible in the authority print.

## Clementi, Op. 10 No. 3, movement i — STRUCTURE RECONCILED; TRANSCRIPTION OPEN

- Authority: Longman & Broderip BnF scan, PDF pages 14-16 / plates 13-15,
  common time with two flats. The movement is in B-flat major.
- Secondary concordance: Brownell (2010), Example 3.8, reproduces mm. 67-74
  with the caption “Copied from Torricella, Vienna, 1783.” It is a copied
  excerpt rather than the complete Torricella source and therefore establishes
  coordinates only; it does not supersede the BnF authority.
- Pickup: four semiquavers (one quarter-note unit) precede m. 1. W1 contains
  measure `-1` plus complete mm. 1-8.
- Correction chronology: the first pass counted 50 measures on plate 13. The
  correct system counts are 8 + 10 + 9 + 9 + 9 = 45, so part 2 begins at
  m. 46. The inherited crop labels were consequently five too high.
- Brownell mm. 67-74 match the BnF sequence exactly: textual `dim.`/`dimi:` at
  m. 67, `pp` at m. 68, a rest/cadential bar at m. 69, the return pickup at
  m. 70 onset `3/1`, and the first full thematic bar at m. 71.
- Corrected windows: W2 = 64-69; W3 = 70-75; W4 = 76-81.
- Full traversal: 119 measures (45 + 46 + 28). Part 2 contains m. 46-119 =
  296 quarter-note units; candidate elapsed time is 24 complete bars plus
  three quarter notes = 99 quarter-note units.
- Schema status: 3.1.0 now represents the source-faithful textual diminuendo
  without converting it to a hairpin. The original schema stop remains in the
  correction history because it was correct under 3.0.0.
- Event status: no dossier has been promoted. Only actual mm. 69-71 have
  converged to JSON-safe events; 24 of 27 evidence measures still require a
  complete authority-based double pass. OMR and later editions remain
  legibility aids only.

## Mozart K. 333 / K. 545 / K. 570 / K. 576 — COMPLETED IN THE SYMBOLIC LANE

The four DCML dossiers, extraction configurations, audit JSONs, and reverse
tables are deterministically generated and validated. For K. 333, the notated
m. 63 repeat split and the beat-four return pickup were reconciled to the
pinned DCML coordinates before extraction.

K. 576/i was admitted as the pre-freeze sixth-slot replacement after the
selected Clementi dossier failed its lossless event-verification gate:

- Authority: pinned DCML v2.3 symbolic files plus `pdf/NMA_vol2.pdf`, SHA-256
  `fd165fcf84905700c23947bc5fc58b7b61275b42cfb2e7068cbc2109401800d6`.
- Source and coordinate check: the NMA footnote on printed p. 148 explicitly
  pairs opening mm. 1-4 with recapitulatory mm. 99-102, and printed p. 151
  shows the principal-theme return at m. 99. Published analyses independently
  place the recapitulation and primary-theme group at m. 99.
- DCML mapping: the opening eighth-note pickup is `mc=1`; printed mm. 1-8 are
  `mc=2-9`. The exposition's printed m. 58 is split at the repeat: `mc=59`
  holds its first five eighth notes and `mc=60` its final eighth on the
  second-part side. Printed m. 99 is therefore `mc=101`.
- Candidate: printed m. 99 / `mc=101`, onset `0/1`.
- Windows: W1 = pickup plus printed mm. 1-8 (`mc=1-9`); W2 = printed mm.
  93-98 (`mc=95-100`); W3 = printed mm. 99-104 (`mc=101-106`); W4 = printed
  mm. 105-110 (`mc=107-112`). Selected pages are NMA pp. 148 and 151.
- Exact position: the second part begins at `mc=60`; candidate elapsed time is
  `241/2` qn and total second-part time is `613/2` qn. Written repeats are not
  unfolded.
- Expression check: the three extracted `f` directions are visible at the
  opening pickup, printed m. 97 onset 0, and printed m. 98 onset `5/2` qn.
  No additional fixed dynamic is visible in the selected NMA measures.
- Result: `CASE-D09B`, schema 3.1.0, passes strict extraction, validation, and
  reverse-table reproducibility with no source-score correction layer. Its
  audit remains `generated_unverified` pending independent expert review.

## Stray-reference fix

`PILOT_CORPUS.md` formerly summarized the windows as 8+8+8+8. It was corrected
to 8+6+6+6, matching the preregistration and extraction protocol.
