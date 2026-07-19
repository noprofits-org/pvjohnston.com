# Identification probe result

The dossier shows a D-major movement in 6/8 that opens forte with both hands in bare octaves: an anacrusis A, then a triadic fanfare D–A–D–F#–D–F#, followed by repeated A's capped with a trilled C#–B–C# turn resolving to a staccato D, further trills on E, and a sequential restatement of the whole figure on E (E–B–E–G–E–G, then repeated B's rising to D#). This horn-call opening in octaves with trill-turn cadences is the signature incipit of the first movement (Allegro) of Mozart's Piano Sonata in D major, K. 576.

The candidate window W3 is a literal restatement of that opening located roughly 40 notated measures into a second part that totals about 102 measures — matching the recapitulation of K. 576/i (development c. mm. 59–98, recapitulation beginning m. 99, movement ending m. 160). Window W2's chromatically rising inner line (B♭→B, C→C#, D→D#) under a sustained high A pedal is consistent with the retransition dominant preparation before that recapitulation.

## Run metadata

- Analyst model: claude-fable-5
- Case: CASE-D09B
- Access: dossier only; no external lookup performed
- Date: 2026-07-19

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "claude-fable-5",
  "case_id": "CASE-D09B",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata in D major, K. 576",
    "movement": "I. Allegro",
    "confidence": 0.65,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E006", "E007", "E010", "E011", "E012", "E016"],
    "reason": "D major 6/8 forte octave-unison hunt-call opening (A pickup, D-A-D-F#-D-F#, repeated A's with trilled C# turn), sequential restatement on E with D#, and a literal return ~40 measures into a ~102-measure second part, matching the K. 576/i recapitulation at m. 99."
  }
}
```

## Limitations

Identification rests on melodic/rhythmic memory of the incipit and proportional fit of the return point, not on external verification; I could not consult a score. The 6/8 D-major octave fanfare idiom also appears in other Classical-era works (e.g., Haydn sonatas, Mozart K. 311 finale), so misattribution is possible. Confidence is moderate rather than high because the dossier covers only four short windows and exact measure numbers are window-relative.
