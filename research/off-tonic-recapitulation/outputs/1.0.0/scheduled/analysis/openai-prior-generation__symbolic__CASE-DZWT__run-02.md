# Analysis result

## Run metadata

Analyst model: unknown. Provider/settings: not observable. Tools/external data: unavailable by instruction and not used; analysis used only the embedded dossier.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-DZWT",
  "cues": {
    "tonal_stability": {
      "score": 4,
      "evidence_ids": ["E015", "E016", "E017", "E018"],
      "reason": "Observed: candidate begins with D octaves and tonic-scale pitches under D-major signature. Inference: the home tonic is structurally clear at the return."
    },
    "thematic_correspondence": {
      "score": 4,
      "evidence_ids": ["E001", "E002", "E003", "E004", "E015", "E016", "E017", "E018"],
      "reason": "Observed: candidate measures reproduce the opening pitches, rhythm, register, texture, and dynamic. Inference: this is a strong opening-theme return."
    },
    "preparation_strength": {
      "score": 4,
      "evidence_ids": ["E012", "E013", "E014", "E015"],
      "reason": "Observed: pre-candidate sustains A-C#-G dominant harmony before D arrival. Inference: dominant preparation for the candidate is strong."
    },
    "proportional_location": {
      "score": 3,
      "evidence_ids": ["E015"],
      "reason": "Observed: candidate occurs 159 quarter notes into a 390-quarter-note second part. Inference: this mid-second-part location is compatible with a recapitulatory division."
    },
    "rhetorical_emphasis": {
      "score": 3,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: long dominant tension gives way to the opening texture at piano, without a stronger dynamic accent. Inference: arrival is clear but not maximally emphatic."
    },
    "rotational_continuation": {
      "score": 4,
      "evidence_ids": ["E015", "E016", "E017", "E018", "E019", "E020", "E021", "E022"],
      "reason": "Observed: continuation follows the opening sequence through corresponding later material. Inference: behavior supports recapitulation rather than continued development."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.01,
    "off_tonic_recapitulation": 0.01,
    "tonic_double_return": 0.98
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The candidate is a tonic double return: opening material returns literally in the home tonic after dominant preparation and continues rotationally."
}
```

## Limitations

The dossier gives symbolic windows rather than full-form context, audio, or score layout beyond the sampled evidence. Proportional-location and rhetorical-emphasis judgments are therefore less certain than thematic, tonal, and continuation judgments. No external identity or scholarship was used.