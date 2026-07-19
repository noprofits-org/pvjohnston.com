# Source concordance log (operator-only)

Verification of claimed candidate coordinates against pinned sources.
Method: measure arithmetic on a clean modern edition cross-checked against the
first-edition scan at system level; programmatic barline counts (vertical-run
detection) validated by zoomed visual inspection. Date: 2026-07-18. Verifier:
operator session (Claude) — a second independent pass is still preferred per
EXTRACTION_PROTOCOL.

## Benda, 1757 Sonata No. 2 in G, movement iii — VERIFIED

- Movement located: MAB edition printed pp. 17–19 (PDF 29–31, "Allegro
  moderato", 3/4, G); first edition SLUB scan pp. 18–19 (plates 11–12,
  "Allegro."). Sonata III's title bleeds through plate 12 verso, confirming
  these plates end Sonata II.
- Exposition: 26 measures including the volta measure (per-system MAB counts
  5+5+4+3+5+3+volta), matching the "exposition ends at bar 26" selection note
  and the first edition's repeat placement (plate 11, system 4).
- Candidate m. 51: MAB p. 19 system 1 = mm. 48–52; the m. 50 cadence bar is
  followed by the m. 1 theme figure over sharp-inflected bass (the G-sharp
  harmonization) at m. 51. Matches the claim. First-edition location: plate 12,
  system 2 region (system-level check; exact bar pinned at transcription).
- Windows: movement extends past m. 68, so 45–50 / 51–56 / 57–62 all exist.
  m. 1 begins with a downbeat rest — no anacrusis; W1 = mm. 1–8.

## C. P. E. Bach, Wq. 48/3, movement iii — VERIFIED at system level; ONE OPEN ITEM

- Movement located: first edition PDF pp. 16–17 (plates 13–14, "Presto", 6/8,
  E major; opening matches the paper's Ex. 1 incipit). Nagel edition PDF
  pp. 15–16.
- Candidate m. 51: Nagel p. 15 contains mm. 1–44 (systems of 7,7,8,7,8,7);
  m. 51 = p. 16 system 1, final bar, preceded by the sharp-inflected vi
  cadence in bars 5–6 of that system. Consistent with the claim under both
  readings of the exposition boundary.
- OPEN: exposition end is 29 or 32 (start-repeat stands at the head of p. 15
  system 5; the two systems detected with an extra vertical line may hide
  voltas). This changes `second_part_fraction` and MUST be resolved during
  note-level transcription before the dossier is hashed.

## Clementi, Op. 10 No. 3, movement i — LOCATED; VERIFICATION OPEN

- Movement located: BnF/Longman & Broderip scan, "SONATA III", Presto, common
  time, two flats, beginning scan p. 14 (plate 13); part 1 ends with a repeat
  at the foot of plate 13 ("Volti").
- OPEN: m. 69 candidate not yet verified — this print's barlines do not span
  the grand staff, so the automated count failed; needs a manual per-system
  count (or transcription-time count). Key/mode of the movement (G minor vs
  B-flat major) to be recorded from the opening tonic at the same time.
- OPEN: concordance of this Longman & Broderip text against the Torricella
  1783 lineage (required by the source manifest) not yet performed.

## Mozart K. 333 / K. 545 / K. 570 — BLOCKED

- DCML corpus files are hash-pinned in the source manifest but not yet
  downloaded locally; the K. 333 pickup reconciliation (notated m. 93 upbeat
  vs extractor event onset) runs when the extractor lane lands.

## Stray-reference fix

- PILOT_CORPUS.md's window summary previously read 8+8+8+8; corrected to
  8+6+6+6 (opening eight, then three six-measure windows), matching
  PREREGISTRATION and EXTRACTION_PROTOCOL.
