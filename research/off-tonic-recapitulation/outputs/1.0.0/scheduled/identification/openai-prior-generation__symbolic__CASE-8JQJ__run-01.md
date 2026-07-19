# Identification probe result

## Run metadata

Analyst model: unknown  
Case ID: CASE-8JQJ  
Allowed source: embedded dossier only

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-8JQJ",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Johann Sebastian Bach",
    "work": "Partita No. 1 in B-flat major, BWV 825",
    "movement": "Menuet I",
    "confidence": 0.78,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E015", "E016", "E017", "E018"],
    "reason": "The normalized D-major opening matches the distinctive Menuet I contour: upbeat-like A-B-A, high descending G-F#-E-D-C#, ornamented F#-G-A-D, and binary-form return material."
  }
}
```

## Limitations

This identification is based only on the symbolic dossier and memory of musical features. The common-tonic normalization obscures original key, and no external score comparison was used.