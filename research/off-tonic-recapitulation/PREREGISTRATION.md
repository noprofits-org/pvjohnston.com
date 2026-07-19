# Preregistration: reliability and elicited identification in LLM music analysis

## Stage

This document defines a six-dossier feasibility pilot. It does not preregister a
full corpus study. The pilot must be frozen in Git before the first
outcome-producing call on a real dossier, and its thresholds must not change
after any real-case output is viewed. Pre-freeze transport and response-schema
checks may contact a model only with the fictional dossier and no-retention
procedure defined in `SYNTHETIC_PREFLIGHT.md`; they are not experiment outcomes.

Status: **frozen for dataset 1.0.0 at 2026-07-19T17:54:14Z**. Real-case
collection remains prohibited until the randomized schedule, collection lock,
and pre-outcome Git commit are complete.

## Primary research question

How repeatable and cross-system-reliable are applications of one explicit
music-analytic rubric by three frozen CLI model systems, and how much
identification of the underlying works can be elicited from identity-withheld
dossiers?

## Contribution

A repeated, cross-system measurement spanning two provider families of whether
LLM systems can apply an ordinal music-analytic rubric consistently to
identical evidence, together
with a direct probe of identity recovery from canonical-repertoire dossiers.
The probe cannot distinguish memorized identity from inference based on musical
fingerprints. It measures elicited identification only; a probe that elicits
nothing does not demonstrate that the system lacks relevant memorized material.

Every outcome changes whether a larger reliability study is warranted:

- High repeatability and cross-system reliability, with little identification,
  supports testing this encoding and investigator-authored rubric at larger
  scale; it does not establish analytical correctness.
- High repeatability but low cross-system reliability demonstrates stable,
  model-system response conventions.
- Low within-system repeatability argues against single-run LLM annotation.
- Successful identification shows that identity withholding did not prevent
  identity recovery and triggers review of whether an ostensibly evidence-only
  analysis may have drawn on information beyond the supplied dossier.

## Interpretation boundary

The pilot measures CLI model-system behavior. It does not measure bare model
weights in isolation, historical or modern listener perception, agreement
among trained music theorists, or the truth of Greenberg's continuum claim.
Agreement may reflect correlated training data or shared conventions and will
be described only as agreement among the tested systems.

The three-system matrix is an incomplete `provider x generation-role` panel:
OpenAI contributes one frontier and one active prior-generation system, while
Anthropic contributes one frontier system and no prior-generation counterpart.
Consequently, a pooled three-system result gives OpenAI two of the three system
positions and is not provider-balanced. Generation-role comparisons and pooled
cross-system summaries are descriptive, not causal estimates of provider or
model-generation effects. Named within-provider and cross-provider system
pairs will be reported so that the imbalance remains visible.

The continuum-versus-categories question is not a primary pilot outcome. It may
be explored in a later, adequately sized corpus only if this pilot passes its
measurement gates. Six cases cannot establish a population distribution.

Model agents from the OpenAI and Anthropic families contributed to protocol
construction or read-only auditing before collection. The outcome calls use
fresh noninteractive contexts with tools and session reuse disabled, so those
construction transcripts are not supplied to the tested systems. This does not
make the evaluation independent: prompts and safeguards were informed by
systems from every tested provider family, and the post must disclose that
development exposure. Results are therefore a transparent measurement of the
frozen systems under a co-developed protocol, not external validation of those
provider families.

## Pilot corpus

The unit of analysis is one candidate return in one movement. The pilot contains
exactly six dossiers:

1. Two ambiguous focal returns discussed by Greenberg (2025).
2. Three ordinary tonic double-return controls.
3. One clearly off-tonic-return control, which is also the positive
   identification control.

This 2+3+1 allocation is a disclosed pre-collection revision from the planned
2+2+2 allocation. The selected Clementi off-tonic case failed the required
source-verification gate, and a fully reproducible Mozart K. 576 tonic-return
case replaced it so that the pilot retained six dossiers and its planned
reliability structure. The replacement improves source reliability at the cost
of class balance; it does not create musicological ground truth or support a
prevalence comparison among the three corpus roles.

Because K. 545 is excluded from the primary reliability gate as the intended
identification-sensitivity anchor, the five-case primary reliability set has
no clear off-tonic control: it contains the two focal cases and three tonic
anchors. The pilot therefore cannot estimate category sensitivity or compare
tonic with off-tonic classes.

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
normalized mechanically to the common tonic D — major-mode movements to D major
and minor-mode movements to D minor — while retaining mode, interval structure,
and notated spelling relationships. Five sources receive a nonzero displacement.
The pre-freeze sixth-slot replacement, K. 576/i, is originally in D major and
therefore receives the identity transform: its exact pitch and register survive.
This disclosed asymmetry weakens identity masking for that target case and
precludes a causal claim about transposition or masking, but it does not change
the preregistered identification probe or target L2 stop rule. Relative measure
numbers begin at zero within each window. Candidate
onset and second-part elapsed/total durations use reduced integer-pair rational
quarter-note units; no floating-point location estimate is permitted.

The extraction and transposition procedure, software version, and any manual
corrections must be recorded. A dossier's selection of the candidate and its
window boundaries remains an operator decision; the pilot therefore tests
rubric application to supplied candidates, not automatic discovery of returns.

## Analytical rubric

The six cues and their 0--4 scales are an investigator-authored operational
synthesis of mechanisms discussed around Greenberg's focal examples. Greenberg
did not propose or validate this rubric. The pilot measures model-system use of
the supplied instrument, not the instrument's music-theoretical validity.

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
or abstention). A dossier is identity-recoverable if one system produces L2 in
at least two of its three probes, or if systems from both provider families
produce L2 at least once. Every isolated L2 remains a disclosed
elicited-identification event and triggers review.

K. 545 is preregistered as the one positive identification control because its
opening and return are unusually canonical. It is excluded from the target-case
zero-L2 elicited-identification gate and from the primary reliability gate.
Probe sensitivity is demonstrated only if at least one system produces L2 in
two of three K. 545 probes, or systems from both provider families produce L2
at least once. The other five dossiers are target cases. Failure to detect the
positive control makes a clean target result inconclusive rather than proving
successful identity suppression.

## Run matrix

Use exactly three pinned model systems across two provider families on their
noninteractive CLI surfaces: OpenAI `gpt-5.6-sol` (frontier), Anthropic
`claude-fable-5` (frontier), and OpenAI `gpt-5.5` (active
prior-generation). The CLI surface, system prompt, safety layer, serving stack,
and unexposed sampling defaults are part of the experimental system. This is a
partial 2x2 panel, with no Anthropic prior-generation cell; it supports
descriptive system comparisons, not a causal frontier-versus-prior-generation
effect. For the analysis task, run each system on each dossier three times in a
fresh context:

`3 systems x 6 cases x 3 repetitions = 54 analysis invocations`.

Fresh-context repetitions share the same weights and the same input. They are
same-input test-retest measurements of response stability, not independent
corroboration by independent raters, and every reliability statistic is
interpreted accordingly.

For the identification task, run each system on each dossier three times in a
fresh context. Repetition distinguishes stable recognition from a lucky or
hallucinated guess:

`3 systems x 6 cases x 3 repetitions = 54 identification invocations`.

The exact provider, callable model identifier, dated or fixed version where available,
CLI version, decoding settings, adapter hash, and planned collection window
must be frozen in `run-matrix.json` and summarized in `RUN_MATRIX.md`. A frozen
108-call schedule defines every scheduled slot. The runner selects the hashed
adapter for a system label; the operator cannot supply an arbitrary command.
The matrix also freezes a per-call timeout. A timeout kills the adapter process
group, finalizes the scheduled slot as a failed invocation, and stops collection
without retrying that slot.
Use the least variable configuration exposed by each CLI and record every
unexposed setting as a provider default. Retain three analysis repetitions
because deterministic decoding is neither uniformly exposed nor guaranteed.
Do not substitute a model or CLI version after collection begins.
Execute the frozen schedule without opening response bodies. The runner may
validate structure and retain failures mechanically, but the operator must not
inspect musical judgments, identifications, or free text until all 108
scheduled slots have terminated. A provider outage stops collection; it does
not justify changing prompts, adapters, thresholds, or models midstream.

## Primary outcomes

### 1. Output validity

Report the fraction of scheduled invocations that return schema-valid output
without repair. A countable bundle requires a completion marker, sidecar, and
response whose hashes and frozen input identifiers all agree. Failed, partial,
tampered, and malformed responses are distinct outcomes, not missing runs. The
runner retains them. Do not silently rerun; diagnostics occupy a separate
namespace and never replace a scheduled result.

### 2. Within-system repeatability

For each system, treat the three fresh-context repetitions as same-input
test-retest ratings and the 30 target case-cue combinations (five target cases
x six cues) as units. K. 545 is the intended identification-sensitivity anchor:
its six
case-cue units receive the identical computation but are reported separately
and enter no primary reliability statistic or gate. Report:

- ordinal Krippendorff's alpha using squared ordinal distance;
- the proportion of within-unit repetition pairs with exact agreement;
- the proportion within one scale point;
- mean and median absolute pairwise difference.

Also report exact agreement, within-one agreement, and absolute differences
separately for each cue. Do not calculate cue-level alpha from only five target
cases.
Add dossier-clustered bootstrap intervals by resampling all six cues of a
dossier together. Use 2,000 replicates with seed 1701 for within-system results
and 1702 for cross-system results. Report how many replicates yield defined alpha
and do not report an alpha interval when the observed alpha is undefined. Alpha
and its interval remain descriptive at this sample size and may be undefined
when ratings have no variance; report undefined values rather than replacing
them.

Missingness is part of repeatability. For every system, report how many
case-cue units contain zero, one, two, or three scored repetitions and the
pairwise agreement of score-available versus `null`. Mixed null/scored units
must not disappear from the report.

### 3. Cross-system reliability

For each system-case-cue, take the median of its three valid repetitions. The
primary cross-provider descriptions are the two named OpenAI--Anthropic pairs,
each reported across the 30 target case-cue units (K. 545 separately). Both
pairs share the same Anthropic system and therefore are descriptive rather than
independent provider replications. Also report a secondary pooled summary that
treats the three system medians as raters; because two medians come from OpenAI
systems, label it provider-unbalanced. Identify the OpenAI
`gpt-5.6-sol`--`gpt-5.5` pair as within-provider and the
`gpt-5.6-sol`--`claude-fable-5` and
`gpt-5.5`--`claude-fable-5` pairs as cross-provider. Report cue-stratified direct
agreement and absolute differences, but not cue-level alpha. Low cross-system reliability does
not block a larger reliability study when systems are internally repeatable:
stable model-system response conventions are a substantive result.

### 4. Elicited identification

Score every probe against an alias-aware hidden key as `L2` (uniquely correct
work/catalogue and movement), `L1` (correct composer or work family but not a
unique work and movement), or `L0` (incorrect or abstention). A dossier is
identity-recoverable if one system produces L2 in at least two of its three
probes, or if systems from both provider families produce L2 at least once.
Every isolated L2 remains a disclosed elicited-identification event.
Additionally,
tabulate the `suspected_recognition`
flags from analysis responses by system and case; a `work`-level flag on a
target case triggers the same review as an isolated L2, even though the
analysis task never names identities. Also compare repeatability descriptively between
repeated-L2, isolated-L2, and no-L2 system-case pairs; the pilot is not
powered for an inferential comparison.

## Go/no-go rule for a full corpus

Proceed to a larger reliability study only if all of the following hold:

1. All 54 scheduled analysis invocations and all 54 identification invocations
   are schema-valid without repair, and all 324 scheduled cue cells are
   non-null. Any failure or `null` triggers dossier/prompt review and a separately
   versioned pilot rather than automatic expansion.
2. At least two of the three systems achieve all three aggregate repeatability
   criteria, computed over the 30 target case-cue units from all 15 scheduled
   target-case analysis responses: mean absolute pairwise difference at most
   0.50, within-one agreement at least 90%, and ordinal alpha at least 0.67.
   The qualifying systems must span both provider families. K. 545 responses
   are excluded from this gate and reported separately.
3. The instrument is non-degenerate among reliable systems: for at least four of
   six cues, at least two systems that pass criterion 2 and span both provider
   families each cover at least two scale points across their five target-case
   medians.
4. None of the five target dossiers receives L2. An isolated target L2 triggers
   review and a separately versioned pilot; reproducible L2 additionally
   compromises its dossier under the repeated-identification rule. Separately,
   the K. 545 positive control must meet the sensitivity rule above. Its expected
   L2 results are reported but do not count against the target zero-L2 gate.

These are feasibility thresholds, not evidence that the rubric is correct. One
isolated L2 identification, one malformed output, one mixed null/scored unit, or
borderline repeatability triggers revision and a separately versioned repeat of
the pilot rather than automatic expansion. Fewer than two repeatable systems,
or qualifying systems drawn from only one provider family, stops the full
matrix. An identity-recoverable dossier stops any identity-suppression claim
and requires a new representation
or a pivot to a contamination study. High within-system but low cross-system
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
