# Identification probe result

Specific candidate identified with high confidence.

## Run metadata

- Case: CASE-DZWT
- Condition: symbolic
- Analyst model: GPT-5
- Sources used: embedded dossier only

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5",
  "case_id": "CASE-DZWT",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "Wolfgang Amadeus Mozart",
    "work": "Piano Sonata No. 5 in G major, K. 283 (189h)",
    "movement": "I. Allegro",
    "confidence": 0.98,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E005", "E006", "E007", "E008", "E015"],
    "reason": "The normalized opening reproduces the movement’s distinctive 3/4 theme: paired-octave half-note gestures, descending eighth-note line over a sustained dominant seventh, chromatic G-sharp turn, ornamented tonic figure, and exact later return."
  }
}
```

## Limitations

The dossier transposes the home tonic to D, whereas the proposed work is originally in G major. Identification is therefore based on interval, rhythm, texture, harmony, articulation, and formal return rather than absolute pitch. No score or external catalogue was consulted.