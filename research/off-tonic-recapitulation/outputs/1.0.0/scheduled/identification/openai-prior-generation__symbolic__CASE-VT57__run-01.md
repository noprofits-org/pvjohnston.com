# Identification probe result

## Run metadata

Analyst model: GPT-5-style Codex session; no external lookup used.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5 Codex",
  "case_id": "CASE-VT57",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata No. 16 in C major, K. 545",
    "movement": "I. Allegro",
    "confidence": 0.92,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E015"],
    "reason": "Opening Alberti-bass theme matches K.545 I after transposition; W3 shows the distinctive second-part thematic return in the subdominant."
  }
}
```

## Limitations

Identification is based only on the embedded symbolic dossier. The pitches appear normalized/transposed, so the named original key is inferred from the recognizable thematic and formal pattern rather than literal key signature alone.