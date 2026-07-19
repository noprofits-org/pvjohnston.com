# Analysis result

## Run metadata

Model/provider/settings: unknown. Tools/external data: no tools used; external data unavailable by instruction.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-VT57",
  "cues": {
    "tonal_stability": {
      "score": 1,
      "evidence_ids": ["E015", "E016", "E017", "E018"],
      "reason": "Observed: candidate begins and sustains G-centered materials while home is D. Inference: home tonic is not structurally stable at the return, despite shared diatonic context."
    },
    "thematic_correspondence": {
      "score": 4,
      "evidence_ids": ["E001", "E002", "E003", "E004", "E015", "E016", "E017", "E018"],
      "reason": "Observed: W3 closely matches W1 melody, bass figuration, rhythm, and trill placement, transposed. Inference: opening-theme identity is strong, though not at home tonic."
    },
    "preparation_strength": {
      "score": 3,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: pre-candidate closes with D-A-C and F-sharp material before G arrival. Inference: this substantially prepares G, not the home-tonic D."
    },
    "proportional_location": {
      "score": 2,
      "evidence_ids": ["E015"],
      "reason": "Observed: candidate occurs 52 quarters into a 180-quarter second part. Inference: early placement is possible for a recapitulatory division but not strongly confirming."
    },
    "rhetorical_emphasis": {
      "score": 2,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: regular barline, no dynamics, and immediate restored theme after preparation. Inference: thematic arrival is clear, but not strongly marked by notated emphasis."
    },
    "rotational_continuation": {
      "score": 4,
      "evidence_ids": ["E019", "E020", "E021", "E022"],
      "reason": "Observed: after W3 opening-theme return, later measures continue matching opening-continuation behavior transposed. Inference: this behaves like recapitulation rather than ongoing sequence."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.08,
    "off_tonic_recapitulation": 0.86,
    "tonic_double_return": 0.06
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The candidate strongly returns the opening rotation but centered on G rather than the home tonic D, making off-tonic recapitulation the best-supported label."
}
```

## Limitations

The dossier provides symbolic notes, rests, meter, and notated markings, but no broader movement plan, exact exposition close, audio, or score-layout cues beyond the encoded windows. Analytical uncertainty mainly concerns proportional function and rhetorical strength; thematic correspondence and off-tonic centering are much clearer from the supplied evidence.