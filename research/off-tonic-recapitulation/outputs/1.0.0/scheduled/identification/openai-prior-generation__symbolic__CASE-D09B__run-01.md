# Identification probe result

## Run metadata

Analyst model: GPT-5. Source boundary: embedded dossier only. Case: CASE-D09B.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5",
  "case_id": "CASE-D09B",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata in D major, K. 576",
    "movement": "I. Allegro",
    "confidence": 0.83,
    "evidence_ids": ["E001", "E002", "E003", "E016", "E017", "E022"],
    "reason": "D-major 6/8 keyboard texture, forte pickup A, opening D-A-D-F#-D-F# octave figure, trill-led continuation, and literal return of the opening strongly match Mozart K. 576, first movement."
  }
}
```

## Limitations

Identification is based only on symbolic incipit and return evidence in the dossier, without score lookup or audio confirmation.