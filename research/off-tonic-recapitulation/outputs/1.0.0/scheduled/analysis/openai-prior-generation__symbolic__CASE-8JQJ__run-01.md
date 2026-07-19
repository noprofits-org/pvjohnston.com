# Analysis result

## Run metadata

Model/provider/settings: unknown. Tools/external data: not used; only the embedded dossier was available.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-8JQJ",
  "cues": {
    "tonal_stability": {
      "score": 1,
      "evidence_ids": ["E015", "E016", "E017"],
      "reason": "Observed: the candidate begins over B-D#-F#, not home D; D harmony appears later. Inference: home-tonic stability at the candidate onset is weak."
    },
    "thematic_correspondence": {
      "score": 3,
      "evidence_ids": ["E001", "E002", "E003", "E015", "E016", "E017"],
      "reason": "Observed: candidate opening rhythm/texture resembles E001 but pitch-shifted; E016-E017 closely match E002-E003. Inference: the opening theme substantially returns, though not as an exact tonic double return."
    },
    "preparation_strength": {
      "score": 2,
      "evidence_ids": ["E009", "E013", "E014", "E015"],
      "reason": "Observed: pre-candidate material has intensified figuration and dynamics, then drops to p before candidate f. Inference: rhetorical preparation is present, but cadential or dominant preparation is ambiguous."
    },
    "proportional_location": {
      "score": 4,
      "evidence_ids": ["E015"],
      "reason": "Observed: candidate occurs 72 quarter notes into a 141-quarter-note second part. Inference: this near-midpoint placement strongly fits a recapitulatory division."
    },
    "rhetorical_emphasis": {
      "score": 3,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: E014 marks p, while E015 brings f and renewed opening-like texture. Inference: the candidate is rhetorically emphasized as an arrival."
    },
    "rotational_continuation": {
      "score": 2,
      "evidence_ids": ["E017", "E018", "E019", "E020", "E021", "E022"],
      "reason": "Observed: E017-E018 continue opening-correspondent material, then E019-E022 diverge into sequential/continuational patterns. Inference: continuation is mixed between recapitulatory rotation and development."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.15,
    "off_tonic_recapitulation": 0.75,
    "tonic_double_return": 0.1
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The candidate strongly suggests a recapitulatory return by theme, rhetoric, and placement, but its initial harmony is not the home tonic, making off-tonic recapitulation likeliest."
}
```

## Limitations

The dossier gives symbolic windows only, not a complete second-part formal map beyond the excerpted continuation. Cadential function before the candidate is analytically uncertain because the pre-candidate harmony is chromatic and not summarized. Recognition was not used as evidence.