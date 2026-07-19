# Frozen identification-probe instructions

You are participating in a preregistered test of how much identification of an
anonymized symbolic music dossier can be elicited from a language model. This
is a separate fresh context from the analytical task.

## Access boundary

Use only the dossier embedded after `BEGIN ALLOWED DOSSIER`. Do not access or
request the internet, external tools, other files, prior responses, or another
annotator's answer. Do not claim to have searched. You may use internal memory
because the purpose of this probe is to detect recognition from model training.

## Procedure

1. Decide whether the evidence supports a specific identification or only a
   broad stylistic resemblance.
2. If you have a candidate identity, give composer, work or catalogue identifier,
   and movement only to the specificity you can support.
3. Report confidence from 0 to 1 and the dossier evidence behind the guess.
4. Do not present a low-confidence guess as recognition.

## Required Markdown output

Use exactly these top-level headings, in order:

1. `# Identification probe result`
2. `## Run metadata`
3. `## Machine-readable result`
4. `## Limitations`

Under `## Machine-readable result`, emit exactly one fenced `json` block and no
other text:

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "string or unknown",
  "case_id": "{{CASE_ID}}",
  "identification": {
    "recognition_level": "none",
    "composer": null,
    "work": null,
    "movement": null,
    "confidence": 0.0,
    "evidence_ids": ["E1"],
    "reason": "string"
  }
}
```

`recognition_level` must be `none`, `style_only`, or `specific_candidate`.
Confidence must be between 0 and 1. A style-only resemblance must not name a
specific work. Keep the reason under 60 words and limitations under 100 words.

BEGIN ALLOWED DOSSIER

{{DOSSIER}}

END ALLOWED DOSSIER
