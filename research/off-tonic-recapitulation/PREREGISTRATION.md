# Preregistration: reliability and leakage in LLM music analysis

## Stage

This document defines a six-dossier feasibility pilot. It does not preregister a
full corpus study. The pilot must be frozen in Git before the first model call,
and its thresholds must not change after any output is viewed.

Status: **development; not approved for model collection**.

## Primary research question

How repeatable and cross-model-reliable are applications of one explicit
music-analytic rubric by current language models, and how much identification
of the underlying works can be elicited from the purportedly anonymized
dossiers?

## Contribution

A repeated, cross-family measurement of whether LLMs can apply an ordinal
music-analytic rubric consistently to identical evidence, together with a
direct probe of how much identification of anonymized canonical-repertoire
dossiers can be elicited from model training or musical fingerprints. The probe
measures elicited identification only; a probe that elicits nothing does not
demonstrate that the model lacks the memorized material.

Every outcome changes the justified use of LLM annotators:

- High repeatability and cross-model reliability, with little identification,
  supports testing the rubric at larger scale.
- High repeatability but low cross-model reliability demonstrates stable,
  model-specific analytical conventions.
- Low within-model repeatability argues against single-run LLM annotation.
- Successful identification demonstrates that anonymized canonical repertoire
  is not necessarily blinded and that recalled scholarship may contaminate an
  ostensibly evidence-only task.

## Interpretation boundary

The pilot measures model behavior. It does not measure historical or modern
listener perception, agreement among trained music theorists, or the truth of
Greenberg's continuum claim. Model agreement may reflect correlated training
data or shared conventions and will be described only as model agreement.

The continuum-versus-categories question is not a primary pilot outcome. It may
be explored in a later, adequately sized corpus only if this pilot passes its
measurement gates. Six cases cannot establish a population distribution.

## Pilot corpus

The unit of analysis is one candidate return in one movement. The pilot contains
exactly six dossiers:

1. Two ambiguous focal returns discussed by Greenberg (2025).
2. Two ordinary tonic double-return controls.
3. Two clearly off-tonic-return controls.

Controls must be selected before model output, using published analyses or a
mechanical inclusion rule. Matching should prioritize date, genre,
instrumentation, movement type, and formal context. The operator-only
provenance table records identities, sources, selection reasons, and any known
published classification. None of that table is model-facing.

The pilot is a feasibility sample, not a representative sample. Focal/control
status will not be used as ground truth for model accuracy.

## Evidence construction

The pilot uses only the `symbolic` condition. Score-image analysis is deferred
until the symbolic pilot is complete.

Each dossier contains a standardized transcription of four windows fixed before
encoding:

- the first eight complete measures as opening primary-theme material;
- the six complete measures immediately before the candidate-containing measure;
- the candidate-containing measure and the next five complete measures;
- the following six complete measures as continuation.

An opening anacrusis is retained as relative measure `-1` but does not count
toward the eight. The shorter six-measure contextual windows are the longest
uniform rule supported by the focal Benda passage through bar 62; they were
fixed from source availability before any model output.

The model-facing representation may contain pitches, onset positions,
durations, voices, key and time signatures, dynamics, articulations, barlines,
and relative locations. Every notation channel has an explicit coverage flag:
an empty array means verified absence, not failure to encode. It must not
contain composer, title, catalogue number,
date, absolute measure number, corpus role, Roman-numeral analysis, cadence
labels, formal-function labels, or prose adapted from Greenberg. All cases are
transposed mechanically to the common tonic D — major-mode movements to D major
and minor-mode movements to D minor — while retaining mode, interval structure,
and notated spelling relationships. D is preregistered because no pilot source
is notated in D: every case, including the C major positive control, is
therefore displaced from its source key. Relative measure numbers begin at zero within each window. Candidate
onset and second-part elapsed/total durations use reduced integer-pair rational
quarter-note units; no floating-point location estimate is permitted.

The extraction and transposition procedure, software version, and any manual
corrections must be recorded. A dossier's selection of the candidate and its
window boundaries remains an operator decision; the pilot therefore tests
rubric application to supplied candidates, not automatic discovery of returns.

## Analytical rubric

Each candidate receives six ordinal scores from 0 to 4. Zero means the supplied
evidence gives no support; four means strong support.

1. `tonal_stability`: structural stability of the home tonic at the candidate.
2. `thematic_correspondence`: identity and extent of opening-theme return.
3. `preparation_strength`: cadential, dominant, or rhetorical preparation.
4. `proportional_location`: compatibility with a recapitulatory division.
5. `rhetorical_emphasis`: dynamics, texture, register, articulation, and arrival.
6. `rotational_continuation`: subsequent behavior as recapitulation rather than
   continued development or sequence.

The analysis prompt also requests a probability distribution across
`not_recapitulation`, `off_tonic_recapitulation`, and `tonic_double_return`.
Those probabilities are secondary and do not supply an accuracy score.

Each analysis response additionally records a `suspected_recognition` level
(`none`, `style`, `composer`, or `work`) with a confidence, without naming any
suspected identity; naming is reserved for the separate identification probe.
These flags are tabulated as disclosed recognition signals alongside probe
results.

## Identification probe

Identification and analysis are separate tasks in fresh model contexts. Each
identification invocation receives exactly one dossier and asks whether the
model can identify the composer, work, and movement. It must distinguish a
specific identification from stylistic resemblance and report confidence.

The operator scores identification against an alias-aware hidden key as `L2`
(uniquely correct work or catalogue identifier and movement), `L1` (correct
composer or work family but not a unique work and movement), or `L0` (incorrect
or abstention). A dossier is compromised if one model produces L2 in at least
two of its three probes, or if at least two model families produce L2 at least
once. Every isolated L2 remains a disclosed leak event and triggers review.

K. 545 is preregistered as the one positive identification control because its
opening and return are unusually canonical. It is excluded from the target-case
zero-L2 elicited-identification gate and from the primary reliability gate. Probe sensitivity is demonstrated only if at least one
model produces L2 in two of three K. 545 probes, or at least two model families
produce L2 once. The other five dossiers are target cases. Failure to detect the
positive control makes a clean target result inconclusive rather than proving
successful blinding.

## Run matrix

Use exactly three independently developed model families. For the analysis
task, run each model on each dossier three times in a fresh context:

`3 models x 6 cases x 3 repetitions = 54 analysis invocations`.

Fresh-context repetitions share the same weights and the same input. They are
same-input test-retest measurements of response stability, not independent
corroboration by independent raters, and every reliability statistic is
interpreted accordingly.

For the identification task, run each model on each dossier three times in a
fresh context. Repetition distinguishes stable recognition from a lucky or
hallucinated guess:

`3 models x 6 cases x 3 repetitions = 54 identification invocations`.

The exact provider, callable model identifier, dated version where available,
CLI version, decoding settings, adapter hash, and planned collection window
must be frozen in `run-matrix.json` and summarized in `RUN_MATRIX.md`. A frozen
108-call schedule defines every scheduled slot. The runner selects the hashed
adapter for a model label; the operator cannot supply an arbitrary command. Use
the most deterministic supported setting, but retain three
analysis repetitions because nominal temperature zero does not guarantee
repeatability. Do not substitute a model after collection begins.

## Primary outcomes

### 1. Output validity

Report the fraction of scheduled invocations that return schema-valid output
without repair. A countable bundle requires a completion marker, sidecar, and
response whose hashes and frozen input identifiers all agree. Failed, partial,
tampered, and malformed responses are distinct outcomes, not missing runs. The
runner retains them. Do not silently rerun; diagnostics occupy a separate
namespace and never replace a scheduled result.

### 2. Within-model repeatability

For each model, treat the three fresh-context repetitions as same-input
test-retest ratings and the 30 target case-cue combinations (five target cases
x six cues) as units. K. 545 is the disclosed recognizable anchor: its six
case-cue units receive the identical computation but are reported separately
and enter no primary reliability statistic or gate. Report:

- ordinal Krippendorff's alpha using squared ordinal distance;
- the proportion of within-unit repetition pairs with exact agreement;
- the proportion within one scale point;
- mean and median absolute pairwise difference.

Also report exact agreement, within-one agreement, and absolute differences
separately for each cue. Do not calculate cue-level alpha from only six cases.
Add dossier-clustered bootstrap intervals by resampling all six cues of a
dossier together. Use 2,000 replicates with seed 1701 for within-model results
and 1702 for cross-model results. Report how many replicates yield defined alpha
and do not report an alpha interval when the observed alpha is undefined. Alpha
and its interval remain descriptive at this sample size and may be undefined
when ratings have no variance; report undefined values rather than replacing
them.

Missingness is part of repeatability. For every model, report how many
case-cue units contain zero, one, two, or three scored repetitions and the
pairwise agreement of score-available versus `null`. Mixed null/scored units
must not disappear from the report.

### 3. Cross-model reliability

For each model-case-cue, take the median of its three valid repetitions. Treat
the three model medians as raters across the 30 target case-cue units (K. 545
reported separately) and report the same aggregate measures as above. Report cue-stratified direct agreement and
absolute differences, but not cue-level alpha. Low cross-model reliability does
not block a larger reliability study when models are internally repeatable:
stable model-specific interpretations are a substantive result.

### 4. Identification leakage

Score every probe against an alias-aware hidden key as `L2` (uniquely correct
work/catalogue and movement), `L1` (correct composer or work family but not a
unique work and movement), or `L0` (incorrect or abstention). A dossier is
compromised if one model produces L2 in at least two of its three probes, or if
at least two model families produce L2 at least once. Every isolated L2 remains
a disclosed leak event. Additionally, tabulate the `suspected_recognition`
flags from analysis responses by model and case; a `work`-level flag on a
target case triggers the same review as an isolated L2, even though the
analysis task never names identities. Also compare repeatability descriptively between
compromised, isolated-leak, and unidentified model-case pairs; the pilot is not
powered for an inferential comparison.

## Go/no-go rule for a full corpus

Proceed to a larger reliability study only if all of the following hold:

1. All 54 scheduled analysis invocations and all 54 identification invocations
   are schema-valid without repair, and all 324 scheduled cue cells are
   non-null. Any failure or `null` triggers dossier/prompt review and a separately
   versioned pilot rather than automatic expansion.
2. At least two of the three models achieve all three aggregate repeatability
   criteria, computed over the 30 target case-cue units from all 15 scheduled
   target-case analysis responses: mean absolute pairwise difference at most
   0.50, within-one agreement at least 90%, and ordinal alpha at least 0.67.
   K. 545 responses are excluded from this gate and reported separately.
3. The instrument is non-degenerate among reliable models: for at least four of
   six cues, at least two models that pass criterion 2 each span at least two
   scale points across their five target-case medians.
4. None of the five target dossiers receives L2. An isolated target L2 triggers
   review and a separately versioned pilot; reproducible L2 additionally
   compromises its dossier under the repeated-identification rule. Separately,
   the K. 545 positive control must meet the sensitivity rule above. Its expected
   L2 results are reported but do not count as target leakage.

These are feasibility thresholds, not evidence that the rubric is correct. One
isolated L2 identification, one malformed output, one mixed null/scored unit, or
borderline repeatability triggers revision and a separately versioned repeat of
the pilot rather than automatic expansion. Fewer than two repeatable models
stops the full matrix. A
compromised dossier stops any blinding claim and requires a new representation
or a pivot to a contamination study. High within-model but low cross-model
reliability does not stop expansion because model-specific stability is itself
the finding.

## Missingness and exclusions

A cue may be `null` only when the dossier lacks evidence needed for that cue.
Missing values are retained and reported. No case, cue, model, or repetition may
be excluded because it weakens reliability. Technical invocations that never
reach the model remain failed scheduled outcomes. Any troubleshooting call uses
a two-digit diagnostic identifier in a separate directory and is excluded from
primary analysis. A new scheduled attempt requires a separately versioned pilot;
no scheduled slot is replaced.

## Stop rules

Stop before collection if score provenance is unresolved, any dossier embeds a
published interpretation, the six cases cannot be transformed consistently, or
the exact model matrix and analysis implementation are not frozen. Stop the
full-corpus plan if the pilot misses any go/no-go criterion. The runner and
analyzer must both verify `collection-lock.json`, which pins the dossiers,
identity/source manifests, prompts, adapters, schemas, validators, and analysis
implementation. Do not revise a threshold after viewing an output.

## Deferred exploratory analysis

Only after the pilot passes may a larger preregistration define a sampling
frame, sample-size justification, distance metric, cluster-tendency statistic,
candidate clustering models, resampling procedure, and continuum decision rule.
No continuum or clustering result from these six cases will appear as a finding.
