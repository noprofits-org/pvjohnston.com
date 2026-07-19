# Identification probe result

## Run metadata

Case: CASE-VT57  
Assessment: Specific candidate from the allowed dossier only.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5",
  "case_id": "CASE-VT57",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata No. 16 in C major, K. 545",
    "movement": "I. Allegro",
    "confidence": 0.99,
    "evidence_ids": ["E001", "E002", "E005", "E006", "E015", "E018"],
    "reason": "The normalized opening reproduces the movement’s distinctive tonic-triad melody over Alberti bass, followed by its dotted cadential figure and extended scalar passagework. The later thematic return and matching trill figure reinforce K. 545, first movement."
  }
}
```

## Limitations

The dossier uses a common-tonic normalization to D major, whereas K. 545 is originally in C major. Instrumentation and title metadata are withheld, so the identification rests entirely on the highly distinctive pitch, rhythm, accompaniment, and formal-return patterns.