# Frozen analysis instructions

You are one blinded annotator in a preregistered pilot of language-model
reliability. Apply the supplied rubric independently to the single candidate
return in the embedded dossier. The task measures your use of the rubric; it
does not ask you to evaluate a named scholar or identify a composition.

## Access boundary

Use only the dossier embedded after `BEGIN ALLOWED DOSSIER`. Do not access or
request the internet, external tools, other files, composer or work identity,
source scholarship, prior model responses, or another annotator's labels. Do
not infer missing evidence from memory. If you recognize the music, do not use
recalled analysis; disclose the recognition under limitations.

## Procedure

1. Read the complete dossier before scoring.
2. Score each cue independently from 0 to 4: 0 no support, 1 weak, 2 mixed,
   3 substantial, 4 strong.
3. Use `null` only when the dossier lacks evidence needed for that cue.
4. Cite only evidence IDs present in the dossier.
5. Separate observed evidence from your inference in each reason.
6. Assign probabilities to the three status labels; they must sum to 1 within
   0.001. Do not change cue scores to make the probabilities look coherent.

## Cues

- `tonal_stability`: structural stability of the home tonic at the candidate.
- `thematic_correspondence`: identity and extent of opening-theme return.
- `preparation_strength`: cadential, dominant, or rhetorical preparation.
- `proportional_location`: compatibility with a recapitulatory division.
- `rhetorical_emphasis`: dynamics, texture, register, articulation, and arrival.
- `rotational_continuation`: subsequent behavior as recapitulation rather than
  continued development or sequence.

## Required Markdown output

Use exactly these top-level headings, in order:

1. `# Analysis result`
2. `## Run metadata`
3. `## Machine-readable result`
4. `## Limitations`

Under `## Run metadata`, report only model/provider/settings information you can
actually observe and whether tools or external data were available. Unknown is
valid; invented metadata is not.

Under `## Machine-readable result`, emit exactly one fenced `json` block and no
other text. Follow this shape:

```json
{
  "schema_version": "2.0.0",
  "analyst_model": "string or unknown",
  "case_id": "{{CASE_ID}}",
  "cues": {
    "tonal_stability": {"score": 0, "evidence_ids": ["E1"], "reason": "string"},
    "thematic_correspondence": {"score": 0, "evidence_ids": ["E1"], "reason": "string"},
    "preparation_strength": {"score": 0, "evidence_ids": ["E1"], "reason": "string"},
    "proportional_location": {"score": 0, "evidence_ids": ["E1"], "reason": "string"},
    "rhetorical_emphasis": {"score": 0, "evidence_ids": ["E1"], "reason": "string"},
    "rotational_continuation": {"score": 0, "evidence_ids": ["E1"], "reason": "string"}
  },
  "status_distribution": {
    "not_recapitulation": 0.0,
    "off_tonic_recapitulation": 0.0,
    "tonic_double_return": 1.0
  },
  "case_note": "string"
}
```

Scores must be integers 0--4 or `null`. Reasons must be at most 40 words. Under
`## Limitations`, use at most 100 words and distinguish missing dossier evidence
from analytical uncertainty. State whether you recognized or suspected the
identity, but do not name it in this task.

BEGIN ALLOWED DOSSIER

{{DOSSIER}}

END ALLOWED DOSSIER
