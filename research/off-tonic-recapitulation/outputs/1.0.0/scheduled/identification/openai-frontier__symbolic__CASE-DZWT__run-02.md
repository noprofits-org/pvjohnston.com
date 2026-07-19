# Identification probe result

Specific candidate supported.

## Run metadata

Case: CASE-DZWT  
Analyst model: GPT-5 (Codex)  
Source: Embedded symbolic dossier only

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5 (Codex)",
  "case_id": "CASE-DZWT",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata in D major, K. 284 (K. 205b)",
    "movement": "II. Rondeau en Polonaise: Andante",
    "confidence": 0.91,
    "evidence_ids": ["E001", "E004", "E005", "E007", "E015", "E018", "E019", "E021"],
    "reason": "The distinctive quiet D-major 3/4 opening in octave doubling, its ornamental scalar continuation over sustained dominant harmony, and its exact later return strongly match the Rondeau en Polonaise from Mozart's K. 284."
  }
}
```

## Limitations

Identification is inferred solely from symbolic pitch, rhythm, texture, and reprise structure. No tempo heading, instrumentation label, score image, or external catalogue comparison was available, so the catalogue attribution remains a high-confidence candidate rather than independently verified recognition.