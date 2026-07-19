# Identification probe result

## Run metadata

Case: `CASE-VT57`  
Access used: embedded dossier only  
Result: specific candidate

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "GPT-5 Codex",
  "case_id": "CASE-VT57",
  "identification": {
    "recognition_level": "specific_candidate",
    "composer": "George Frideric Handel",
    "work": "Keyboard Suite No. 5 in E major, HWV 430",
    "movement": "Air and Variations, 'The Harmonious Blacksmith'",
    "confidence": 0.94,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E015"],
    "reason": "Opening theme matches Handel's Air: sustained tonic/third/fifth over broken arpeggios, cadential trill/rest pattern, followed by sequential scalar variation figuration and the candidate's parallel return."
  }
}
```

## Limitations

No external lookup or score comparison was used. The dossier is normalized to D, so original key and catalogue details are inferred from repertoire memory rather than directly encoded metadata.