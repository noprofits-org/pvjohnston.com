# Analysis result

## Run metadata

Analyst model/provider/settings: unknown. Tools/external data: unavailable and not used; analysis used only the embedded dossier.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-D09B",
  "cues": {
    "tonal_stability": {
      "score": 4,
      "evidence_ids": ["E016", "E017", "E018"],
      "reason": "Observed: candidate begins with D/D octave, then D-A-D-F# pattern in D-major signature. Inference: this strongly establishes the home tonic rather than an off-tonic return."
    },
    "thematic_correspondence": {
      "score": 4,
      "evidence_ids": ["E002", "E003", "E004", "E016", "E017", "E018"],
      "reason": "Observed: candidate measures reproduce the opening pitch/rhythm pattern from E002-E004 essentially exactly. Inference: opening-theme correspondence is strong and extended."
    },
    "preparation_strength": {
      "score": 3,
      "evidence_ids": ["E010", "E011", "E012", "E014", "E015", "E016"],
      "reason": "Observed: pre-candidate material sustains/emphasizes A and includes forte gestures before D entry. Inference: dominant/rhetorical preparation is substantial, though no explicit cadence is encoded."
    },
    "proportional_location": {
      "score": 3,
      "evidence_ids": ["E016"],
      "reason": "Observed: candidate occurs after 120.5 of 306.5 second-part quarter-notes. Inference: about 39% into the second part is compatible with a recapitulatory division."
    },
    "rhetorical_emphasis": {
      "score": 2,
      "evidence_ids": ["E014", "E015", "E016"],
      "reason": "Observed: forte activity precedes the candidate, but E016 has no new dynamic, special barline, or articulation. Inference: arrival is audible structurally but rhetorically mixed."
    },
    "rotational_continuation": {
      "score": 4,
      "evidence_ids": ["E002", "E003", "E004", "E005", "E006", "E007", "E016", "E017", "E018", "E019", "E020", "E021"],
      "reason": "Observed: six candidate measures track the opening sequence through corresponding events. Inference: continuation behaves as recapitulation, not ongoing sequence or development."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.02,
    "off_tonic_recapitulation": 0.02,
    "tonic_double_return": 0.96
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The candidate is best read as a tonic double return: the opening theme returns in the home tonic with strong continuation, despite only moderate rhetorical marking."
}
```

## Limitations

The dossier gives symbolic windows, not a full score context or audio realization. Cadential preparation and rhetorical weight are therefore partly uncertain: dynamics, texture, and pitch content are encoded, but phrase-level hearing and broader formal context are limited. Recognition was not used as evidence.