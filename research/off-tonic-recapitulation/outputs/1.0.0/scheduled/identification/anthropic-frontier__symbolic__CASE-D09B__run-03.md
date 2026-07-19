# Identification probe result

The dossier presents a keyboard texture in D major, 6/8, opening forte with both hands in bare octaves: an upbeat A leading to the arpeggiated figure D–A–D–F#–D–F#, then repeated A's in a dotted rhythm capped by a trilled C# with a two-note termination resolving to D (E001–E004). The idea is immediately sequenced up a step onto E with D# (E006–E007). The pre-candidate window shows a retransition over an A pedal with a chromatically rising inner voice (B♭–B♮, C–C#, D–D#) beneath a sustained high A (E010–E013), and the candidate window is a literal tonic return of the opening about 40 measures into a second part totaling roughly 102 measures, with the continuation diverging toward the subdominant (E024–E027). This "hunting-call" octave incipit, the trill-terminated answer, the dominant-pedal chromatic retransition, and the sonata-form proportions match the first movement (Allegro) of Mozart's Piano Sonata No. 18 in D major, K. 576, with the candidate window corresponding to the recapitulation.

## Run metadata

- Analyst model: claude-fable-5
- Case: CASE-D09B
- Condition: symbolic dossier only; no external lookup performed or available
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
    "work": "Piano Sonata No. 18 in D major, K. 576",
    "movement": "I. Allegro",
    "confidence": 0.7,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E006", "E007", "E010", "E011", "E012", "E013", "E016", "E024"],
    "reason": "D major 6/8 octave hunting-call incipit (A upbeat, D-A-D-F#-D-F#, trilled C# to D), step-up sequence to E with D#, dominant-pedal chromatic retransition, and tonic return ~40 measures into a ~102-measure second part match the K. 576 Allegro recapitulation."
  }
}
```

## Limitations

Identification rests on memory of the K. 576 incipit and formal proportions; no score lookup was possible, so exact note-for-note correspondence is unverified. The octave-unison hunting-call opening is distinctive but not unique to Mozart, and details such as the precise octave spacing or trill terminations could differ from my recollection. Confidence is therefore set at 0.7 rather than higher; this is a supported candidate, not certain recognition.
