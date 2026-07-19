# Analysis result

## Run metadata

Model/provider/settings: unknown. Tools were available in the session but not used. External data and internet access were not used; scoring is based only on the embedded dossier.

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "unknown",
  "case_id": "CASE-VT57",
  "cues": {
    "tonal_stability": {
      "score": 0,
      "evidence_ids": ["E015"],
      "reason": "Observed: candidate begins with G-B-D sonority and G bass, not home D. Inference: the return is locally stable away from the home tonic."
    },
    "thematic_correspondence": {
      "score": 4,
      "evidence_ids": ["E001", "E015", "E002", "E016"],
      "reason": "Observed: opening melodic/bass pattern returns closely transposed at the candidate. Inference: this is a strong opening-theme return, though not in home tonic."
    },
    "preparation_strength": {
      "score": 3,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: pre-candidate material settles on D-A-C with F-sharp above before resolving to G. Inference: this substantially prepares the off-tonic arrival."
    },
    "proportional_location": {
      "score": 3,
      "evidence_ids": ["E015"],
      "reason": "Observed: candidate begins 52 of 180 quarter notes into the second part. Inference: this early-middle location is compatible with a recapitulatory division."
    },
    "rhetorical_emphasis": {
      "score": 2,
      "evidence_ids": ["E014", "E015"],
      "reason": "Observed: texture shifts from running pre-candidate figuration to longer opening-theme values, but no dynamics or special articulation appear. Inference: emphasis is present but limited."
    },
    "rotational_continuation": {
      "score": 4,
      "evidence_ids": ["E015", "E016", "E017", "E018", "E019", "E020"],
      "reason": "Observed: multiple candidate measures continue the opening rotation in transposed form. Inference: subsequent behavior strongly supports recapitulation rather than continued development."
    }
  },
  "status_distribution": {
    "not_recapitulation": 0.13,
    "off_tonic_recapitulation": 0.85,
    "tonic_double_return": 0.02
  },
  "suspected_recognition": {
    "level": "none",
    "confidence": 0.0
  },
  "case_note": "The candidate strongly returns the opening rotation but in G rather than home D, with preparation and continuation supporting an off-tonic recapitulatory reading."
}
```

## Limitations

The dossier provides symbolic events but no audio, score layout, phrase labels, or larger formal map beyond the windows and timing. Dynamics and articulations are complete but mostly absent, limiting rhetorical assessment. Tonal and formal judgments remain analytical inferences from pitch, duration, and proportional placement only.