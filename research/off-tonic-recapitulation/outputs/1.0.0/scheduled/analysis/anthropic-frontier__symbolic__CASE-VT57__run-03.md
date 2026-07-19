# Analysis result

The candidate at W3 is an exact transposition of the opening theme up a perfect fourth, into G major (the subdominant of the D major home key), prepared by a dominant seventh of G and followed by material that parallels the opening's continuation and works its way back to a D major tonic arrival. The evidence points strongly to an off-tonic (subdominant) recapitulation rather than a tonic double return or continued development.

Key observations from the dossier:

- **Thematic identity**: W1 measure 0 (E001) presents D5–F#5–A5 over a D major broken-chord accompaniment; W3 measure 0 (E015) presents G5–B5–D6 over the same accompaniment pattern on G. The correspondence continues measure-for-measure through E016–E018 (including the trill ornament at the parallel spot, E039 vs. E291).
- **Key at the candidate**: the candidate harmony is G major, not the home tonic D; C naturals (E267, E280, E291) confirm G major rather than D.
- **Preparation**: W2 ends with a sustained D–A–C♮ sonority under a rising melodic approach (E014, events EV0243–EV0245), i.e., a dominant seventh of the candidate key, following a sequential, developmental passage (E009–E013).
- **Continuation**: W4 parallels the opening's scale-run continuation and progresses G → A7 (E025, EV0437/EV0439 over A bass) → D major with D in the bass (E026), regaining the home tonic — recapitulatory tonal adjustment, not ongoing sequence.
- **Location**: the candidate falls at 52 of 180 quarter notes (~29%) into the second part, consistent with a short development preceding a longer recapitulation.

## Run metadata

- Analyst model: claude-fable-5 (Anthropic), running in a Claude Agent SDK session.
- Sampling settings: not observable.
- Tools were available in the harness but none were used; no internet access, external files, or data beyond the embedded dossier were consulted.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "claude-fable-5",
  "case_id": "CASE-VT57",
  "cues": {
    "tonal_stability": {"score": 1, "evidence_ids": ["E015", "E016", "E017"], "reason": "Observed: candidate harmony is G major broken chords with C naturals; home tonic D absent as local tonic. Inference: home-tonic stability is weak at the candidate; local G stability is high."},
    "thematic_correspondence": {"score": 4, "evidence_ids": ["E001", "E002", "E003", "E004", "E015", "E016", "E017", "E018"], "reason": "Observed: W3 measures 0–3 reproduce W1 measures 0–3 exactly, transposed up a fourth, including rhythm, accompaniment figure, and trill placement. Inference: full, extended opening-theme return."},
    "preparation_strength": {"score": 3, "evidence_ids": ["E013", "E014"], "reason": "Observed: sequential liquidation ends on sustained D–A–C-natural sonority with rising melodic approach into the candidate. Inference: strong dominant-seventh preparation of the candidate key, though not of the home tonic."},
    "proportional_location": {"score": 3, "evidence_ids": ["E015"], "reason": "Observed: candidate onset at 52 of 180 quarter notes (~29%) of the second part. Inference: compatible with a recapitulatory division after a short development."},
    "rhetorical_emphasis": {"score": 2, "evidence_ids": ["E014", "E015"], "reason": "Observed: no dynamics or articulation markings anywhere; arrival restores opening texture and accompaniment after a sustained preparatory chord. Inference: moderate textural-registral emphasis; no notated dynamic reinforcement."},
    "rotational_continuation": {"score": 3, "evidence_ids": ["E019", "E021", "E025", "E026"], "reason": "Observed: continuation parallels the opening's scale-run figuration, then moves through an A-based dominant sonority to a D major arrival with D bass. Inference: recapitulatory tonal adjustment regaining the tonic, not ongoing sequence."}
  },
  "status_distribution": {
    "not_recapitulation": 0.09,
    "off_tonic_recapitulation": 0.88,
    "tonic_double_return": 0.03
  },
  "suspected_recognition": {"level": "work", "confidence": 0.6},
  "case_note": "Exact subdominant transposition of the opening theme, prepared by V7 of the candidate key and followed by tonal adjustment back to the home tonic; classic off-tonic (subdominant) recapitulation profile."
}
```

## Limitations

Missing dossier evidence: no dynamics, tempo, or articulation directions anywhere; no exposition second group or movement ending, so the tonal adjustment can only be traced to the D major arrival at the continuation window's end; measure numbers are window-relative, hiding absolute position. Analytical uncertainty: preparation targets the candidate key rather than the home tonic, so a sequence-continuation reading retains small probability; proportional placement supports but cannot confirm a recapitulatory division. The music's melodic and structural profile felt familiar at the work level (reported only via `suspected_recognition`); this self-report was excluded from cue scoring and is not provenance evidence.
