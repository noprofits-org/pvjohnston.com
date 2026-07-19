# Identification adjudication execution memo

Status: **outcome-blind clarification recorded at 2026-07-19T18:03:41Z**, after
the dataset and 41-file collection lock were frozen but before the planned
collection window, before any scheduled real-case call, and before any response
body was inspected. This memo does not change the frozen L0/L1/L2 definitions,
thresholds, identity key, or expansion gate. It fixes how their factual
comparison will be executed when collection is complete.

## Evidence used for scoring

Score only the parsed `identification.composer`, `identification.work`, and
`identification.movement` fields against the canonical values and accepted
aliases in frozen `identity-key.json`. Do not use the model's
`recognition_level`, confidence, evidence IDs, prose reason, limitations, or
analysis-task familiarity self-report to raise or lower an adjudication level.
Those fields remain reportable model outputs but are not scoring evidence.

## Text comparison

For comparison only, normalize Unicode compatibility characters and case;
remove diacritics; treat typographic dashes as hyphens; translate the musical
symbols `♭` and `♯` to `flat` and `sharp`; ignore periods, commas, and
repeated whitespace; and treat a hyphen surrounded by letters as a space. These
operations may reconcile spelling and punctuation but may not change a name,
catalogue number, key, sonata number, or movement number.

A canonical value or frozen alias that matches after those operations counts as
a field match. An unlisted expansion counts only when it contains the same
unambiguous frozen catalogue identifier (for example the same K/KV or Wq
number) and introduces no conflicting composer, work, key, or movement. Record
the exact equivalence in the judgment reason. If an unlisted title cannot be
resolved by this rule, score conservatively and flag it for the second pass; do
not consult a musical rationale to infer the intended identity.

## Levels and edge cases

- `L2` requires one unambiguous correct work or catalogue designation and the
  correct movement. The composer must be correct or absent, and no structured
  identity field may contradict the frozen key.
- `L1` applies when the composer or work family is correct but unique
  work-and-movement identification is missing. A correct unique work with a
  missing or wrong movement is `L1`. A correct work and movement paired with an
  explicitly wrong composer is capped at `L1` and the contradiction is stated.
- `L0` applies to abstention; only broad style; a wholly incorrect identity; or
  a response with no correct composer or work-family information.
- A list or hedge containing more than one candidate cannot receive `L2`, even
  if one candidate is correct. It may receive `L1` only when the structured
  fields still state a correct composer or work family.
- Null fields never receive credit by implication. A prose reason cannot repair
  an incorrect or missing structured field.

## Execution and audit

After all 54 identification bundles are immutable, perform one complete factual
pass in schedule order and write a brief field-based reason for every valid
output. A separate Codex agent then audits all judgments against this memo and
the frozen key without evaluating musical reasoning. Resolve disagreements by
the rules above; if a string remains genuinely ambiguous, retain both audit
positions and use the lower level for the preregistered gate. Report that this
was model-assisted factual adjudication under human operator supervision, not
music-theory expert review or independent validation.
