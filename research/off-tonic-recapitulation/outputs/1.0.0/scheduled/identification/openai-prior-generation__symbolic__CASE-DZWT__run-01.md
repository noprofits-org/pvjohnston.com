# Identification probe result

## Run metadata

Case: `CASE-DZWT`  
Allowed source: embedded symbolic dossier only  
Decision: specific candidate

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5 Codex",
  "case_id": "CASE-DZWT",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Ludwig van Beethoven",
    "work": "Piano Sonata No. 7 in D major, Op. 10 No. 3",
    "movement": "III. Menuetto: Allegro",
    "confidence": 0.86,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E005", "E006", "E015"],
    "reason": "D major 3/4 piano minuet opening with p octave D-A, F#-A, D-F#, dominant-seventh descent, and exact return strongly matches Beethoven Op. 10 No. 3, third movement."
  }
}
```

## Limitations

Identification is based only on the embedded symbolic incipit and return structure, without score lookup or audio comparison. Confidence is high but not absolute because the dossier contains short windows rather than the full movement.