# Analysis result

## Run metadata

Model/provider/settings: unknown. Tools/external data: not used; dossier-only analysis.

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
      "reason": "Observed D-major key signature and D/A/F# opening sonority at candidate; inference: the return strongly stabilizes the home tonic D."
    },
    "thematic_correspondence": {
      "score": 4,
      "evidence_ids": ["E002", "E003", "E004", "E016", "E017", "E018"],
      "reason": "Observed candidate measures reproduce opening pitches, durations, voices, and ornaments from measures 0-2; inference: opening-theme correspondence is essentially exact, aside from pickup context."
    },
    "preparation_strength": {
      "score": 3,
      "evidence_ids": ["E014", "E015", "E016"],
      "reason": "Observed forte pre-candidate passage and A bass immediately before D at candidate; inference: dominant/rhetorical preparation is substantial, though no explicit cadential formula is fully documented."
    },
    "proportional_location": {
      "score": 3,
      "evidence_ids": ["E016"],
      "reason": "Observed candidate at 120.5 of 306.5 quarter notes into the second part; inference: this mid-second-part placement is compatible with a recapitulatory division."
    },
    "rhetorical_emphasis": {
      "score": 3,
      "evidence_ids": ["E014", "E015", "E016"],
      "reason": "Observed forte lead-in and textural shift to clear two-voice thematic statement at D; inference: arrival is rhetorically marked, despite no new dynamic at the candidate onset."
    },
    "rotational_continuation": {
      "score": 4,
      "evidence_ids": ["E016", "E017", "E018", "E019", "E020", "E021", "E022", "E023"],
      "reason": "Observed candidate and continuation match opening sequence through corresponding later measures; inference: behavior follows recapitulatory rotation rather than ongoing development."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.01,
    "off_tonic_recapitulation": 0.02,
    "tonic_double_return": 0.97
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The dossier supports a tonic double return: the candidate begins on home-tonic material and continues the opening rotation closely."
}
```

## Limitations

The dossier provides symbolic windows only, so broader formal context, full exposition length, and auditory salience are unavailable. Preparation is inferred from local bass/dynamic evidence rather than a fully encoded cadence label. Proportional location is judged from supplied second-part timing only.