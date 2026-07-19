# Identification probe result

## Run metadata

Analyst model: GPT-5 Codex. Case ID: CASE-VT57. Access used: embedded dossier only.

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
    "confidence": 0.94,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E015", "E016", "E017", "E018"],
    "reason": "Opening Alberti-bass texture and melody match K.545 I after tonic normalization; W3 gives the famous subdominant recapitulation of the opening theme."
  }
}
```

## Limitations

The identification is based only on the encoded symbolic excerpt and normalized pitch context. Catalogue/work title cannot be independently verified here, and the dossier gives no explicit composer metadata.