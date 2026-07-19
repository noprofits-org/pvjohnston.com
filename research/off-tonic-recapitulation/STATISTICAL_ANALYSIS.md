# Frozen statistical analysis specification

Status: **frozen for dataset 1.0.0 at 2026-07-19T17:54:14Z**. Real-case
collection remains prohibited until the randomized schedule, collection lock,
and pre-outcome Git commit are complete.

## Rating units

For within-system repeatability, one unit is one `case x cue` combination. The
primary analysis uses the 30 target units (five target cases x six cues), each
scheduled to receive three ratings from fresh contexts of the same system. The
coefficient is computed separately for each system across all 30 target units.
K. 545's six units receive the identical computation but are reported
separately as the intended identification-sensitivity anchor and enter no gate.
The primary five-case set therefore has no clear off-tonic control and cannot
support a tonic-versus-off-tonic or category-sensitivity comparison.

Fresh-context repetitions are same-input test-retest measurements of one
stochastic system, not ratings by independent raters; every coefficient is
interpreted as response stability, not corroboration.

For cross-system reliability, first take the median of all three repetitions for
each `system x case x cue`. If any repetition is missing or `null`, that
system's median for the unit is `null`; never average two ordinal categories
into a half-step. The three complete system medians then act as raters of the
same 30 target units, with K. 545 tabulated separately. The pilot's completeness
gate requires this problem to be absent before automatic expansion.

## Direct agreement

For every unit, compare all three unordered rater pairs. Pool pairwise absolute
differences across units and report:

- exact agreement: fraction with difference 0;
- within-one agreement: fraction with difference at most 1;
- mean absolute difference;
- median absolute difference.

The same direct measures are reported separately by cue. No cue-level alpha is
calculated from only five target cases.

For cross-system results, treat the two named cross-provider pairs as the
primary descriptions and report the within-provider pair separately:
`gpt-5.6-sol`--`gpt-5.5` (within provider),
`gpt-5.6-sol`--`claude-fable-5` (cross provider), and
`gpt-5.5`--`claude-fable-5` (cross provider). The two cross-provider pairs share
the same Anthropic system and are not independent replications. Any secondary
pooled three-system statistic is labeled provider-unbalanced because two of its
three system raters are OpenAI systems. Pairwise and pooled summaries are descriptive;
they do not estimate causal provider or generation effects from this partial
2x2 panel.

## Krippendorff's alpha

Use Krippendorff's alpha with the ordinal disagreement function. Coincidences
are accumulated from ordered within-unit rating pairs with weight
`1 / (m_u - 1)`, where `m_u` is the number of present ratings in unit `u`.
Ordinal distance between categories uses the squared cumulative marginal mass
between their endpoints, subtracting half of each endpoint's marginal mass.
Alpha is `1 - D_o / D_e`.

The ordinal distance between categories `c` and `k` is the square of the sum of
empirical category marginals from `c` through `k`, less half the marginal mass
at each endpoint. Return `null` when fewer than two coincidences exist or
expected disagreement is zero. Do not convert an undefined coefficient to perfect agreement; report the
direct measures and lack of category variation.

Implementation: `scripts/lib/reliability.mjs`.

## Bootstrap intervals

Generate 2,000 nonparametric replicates with seed 1701 for within-system results
and 1702 for cross-system results. Resample the five target dossiers with
replacement, carrying all six cues and all ratings for a selected dossier
together. K. 545's separately reported descriptive results carry no interval.
Report the 2.5th and 97.5th empirical quantiles. Report the number and proportion of
replicates with a defined alpha. When observed alpha is undefined, its interval
is also `null`; do not report an interval conditional only on defined bootstrap
draws. These are descriptive resampling-sensitivity summaries, not population
confidence intervals: the five target dossiers are a nonrandom convenience
set, and three are Mozart cases drawn from the same pinned DCML source.

## Repeatability and dispersion gates

A system passes the repeatability gate only if all 15 of its scheduled
target-case analysis responses are valid with no null cue values and its
aggregate results over the 30 target units meet all three criteria:

- mean absolute difference at most 0.50;
- within-one agreement at least 0.90;
- ordinal alpha at least 0.67.

At least two of three systems must pass, and the passing set must span both
provider families. Separately, for at least four of six cues, at least two
passing systems spanning both provider families must each cover at least two
scale points across their five target-case medians. This prevents a
nonrepeatable third system, or two systems from only one provider, from
supplying the dispersion needed for a trivially constant instrument to pass.

Cross-system reliability is an outcome, not a gate. Stable disagreement between
internally repeatable model systems is scientifically interpretable.

## Identification scoring

The identification JSON is structurally validated during collection but not
scored automatically. After all outputs are frozen, an operator compares each
guess against the alias-aware identity key and records `L2`, `L1`, or `L0` under
the rules in `PREREGISTRATION.md`. The adjudication table and all aliases become
part of the published data. An unsuccessful probe means recognition was not
elicited; it does not prove that the model lacked relevant memorized material.

For the five target dossiers, automatic expansion requires zero L2 events. The
single preregistered K. 545 positive control is reported separately and
demonstrates probe sensitivity if at least one system has L2 in two of three
runs or systems from both provider families have L2 at least once. For the
descriptive repeatability comparison,
classify each target `system x case` pair as `repeated_l2` (at least two L2),
`isolated_l2` (exactly one), or `no_l2` (zero), and report the same direct
within-pair score differences without inferential testing.

Analysis responses also carry a `suspected_recognition` flag (`none`, `style`,
`composer`, `work`) with a confidence. Tabulate these by system and case as
disclosed recognition signals next to probe outcomes. A `work`-level flag on a
target case triggers the same review as an isolated L2. A `none` flag is an
elicitation result, not evidence that the model failed to recognize the case.

## Reproducible output

`scripts/analyze-results.mjs` verifies the collection lock and enumerates the
exact frozen schedule. It counts a response only after checking the completion
marker, sidecar, response and stderr hashes, model adapter, frozen input hashes,
and the shared response validator. It classifies absent, partial, failed,
malformed, valid, and unexpected artifacts, then writes a JSON summary to
standard output. Diagnostics are excluded. Raw responses remain unchanged.
