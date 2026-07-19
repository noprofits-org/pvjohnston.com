# Identification probe result

The dossier supports a specific candidate identification with high confidence.

## Run metadata

Case: CASE-Q2R9  
Analyst: GPT-5 Codex  
Evidence basis: Embedded symbolic dossier only

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5 Codex",
  "case_id": "CASE-Q2R9",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata in D major, K. 311 (284c)",
    "movement": "I. Allegro con spirito",
    "confidence": 0.94,
    "evidence_ids": ["E001", "E002", "E003", "E016", "E017", "E018"],
    "reason": "The distinctive ornamented D-major opening melody and broken-chord accompaniment match K. 311's first movement. E016 recreates the opening pickup from E001 at the designated return, followed by near-literal correspondence between E017–E018 and E002–E003, consistent with the sonata-form recapitulation."
  }
}
```

## Limitations

The identification is inferred solely from symbolic pitch, rhythm, texture, and formal recurrence. Instrumentation and tempo markings are absent, and no independent source comparison was permitted. The catalogue assignment is therefore a strong candidate rather than externally verified identification.