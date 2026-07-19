---
title: "Repeatable, but not blind: a frozen LLM pilot on off-tonic recapitulation"
date: 2026-07-19
author: Peter Johnston
tags: music theory, machine learning, large language models, reproducibility
description: Three frozen command-line model systems repeatedly scored identity-withheld sonata-form dossiers. The pilot measured stability, cross-system agreement, output validity, and elicited repertoire identification before deciding whether the design should expand.
contribution: A frozen, provider-aware test of repeated LLM music-analytic ratings paired with elicited identity probes, which is not in Greenberg's music-theoretical study.
contribution-type: composition
og-image: /images/2026-07-19-repeatable-but-not-blind-hero.png
---

## Abstract

Large language models can assign consistent labels without supplying either an independent judgment or a blind one. I tested that distinction in a frozen pilot derived from recent work on the fuzzy boundary of off-tonic recapitulation. Three command-line model systems from two providers scored six identity-withheld symbolic dossiers three times and separately attempted to identify each work, for 108 scheduled calls. The analysis rubric, corpus, prompts, model adapters, randomized schedule, validity rules, and automatic-expansion gates were fixed before collection. This study had no music-theory-trained human validator; its outcomes concern output validity, test–retest stability, cross-system agreement, and elicited identification, not analytical correctness. Under the frozen validator, 103 of 108 responses passed the complete output contract. The two complete OpenAI analysis arms had ordinal Krippendorff α values of 0.871 and 0.892 across the five-case primary set; the incomplete Anthropic arm had an available-case α of 0.837. Exact work-and-movement identification occurred in six of nine probes for the target Mozart K. 576 dossier and three of nine probes for the separate K. 545 sensitivity anchor. The automatic-expansion gate and its five preliminary component gates returned false. A post hoc prompt-aligned interpretation accepted five complete responses rejected by two unstated validator constraints and restored complete provider-spanning repeatability, but automatic expansion remained false. The pilot was repeatable under both analyses, in different scopes, but it was not blind to every target identity.

<figure>
  <img src="/images/2026-07-19-repeatable-but-not-blind-hero.png" alt="Three-panel experimental summary. Panel A shows high ordinal test-retest reliability for two complete OpenAI systems and an incomplete Anthropic primary arm, with complete Anthropic reliability under a post hoc prompt-aligned sensitivity. Panel B shows that all five primary gates failed and only output validity and repeatability passed post hoc, leaving automatic expansion false. Panel C shows six exact identifications for target Mozart K. 576 and three for the separate K. 545 sensitivity anchor, with zero for the other four dossiers.">
</figure>

**Figure 1.** Frozen and post hoc audit summary. (A) Ordinal test–retest α with descriptive 95% dossier-bootstrap intervals; the asterisk marks the Anthropic available-case primary result. (B) Preliminary feasibility gates and the unchanged no-expansion decision. (C) Exact work-and-movement matches among nine probes per dossier; K. 545 was the separate sensitivity anchor and was excluded from primary reliability statistics.

## Introduction

An off-tonic recapitulation begins a recapitulatory rotation away from the home tonic. Greenberg's recent study argues that difficult mid-eighteenth-century examples make the category itself fuzzy: thematic return, tonal return, preparation, and subsequent continuation need not coincide at a single unambiguous point.[@Greenberg2025] That claim creates an attractive annotation problem, but converting it into a model task introduces a different question. Before asking a language model to extend a music-theoretical analysis, one must determine whether the same model applies the proposed rubric consistently and whether an identity-withheld score remains identifiable.

Machine-readable corpora make controlled symbolic comparison possible. The annotated Mozart sonatas corpus, for example, provides expert-labelled scores, harmony, cadences, and phrases under a documented data model.[@Hentschel2021] Such source annotation does not validate a new six-cue rubric, nor does removing a title make a canonical passage unfamiliar to a model. Reliability, identity suppression, and music-theoretical validity are separate properties.

The experiment therefore composes two established ideas in model-assisted humanities work: repeated ordinal coding and a direct repertoire-identification probe. Krippendorff's framework distinguishes reliability from validity; repeated agreement can establish the former without the latter.[@Krippendorff2018] Here the repeated outputs are **test–retest samples from one stochastic model system**, not independent raters. Cross-system comparisons are also descriptive because the panel contains three systems but two providers.

The pre-results hypothesis was deliberately strict: **the six-dossier, three-system pilot would satisfy every frozen feasibility gate and qualify for automatic expansion**. Its falsifier was any false gate—invalid or missing output, failure to obtain repeatability across both provider families, inadequate cue dispersion, exact identification of any target work and movement, a work-level analysis self-report on a target, or failure of the separate K. 545 sensitivity anchor. The other outcome was publishable: a failed gate would identify what had to change before a larger run.

## Experimental Methods

### Corpus and rubric

The frozen dataset 1.0.0 contained two focal cases selected from Greenberg, three ordinary tonic-return anchors, and one off-tonic K. 545 dossier used as an identification-sensitivity anchor (Table 1).[@Greenberg2025] The Mozart symbolic sources came from the annotated sonata corpus described by Hentschel and co-workers.[@Hentschel2021] K. 545 was excluded from primary reliability and target-identity gates but retained as the separate required identification-sensitivity condition. The five-case primary set consequently contained no clear off-tonic control and could not support a tonic-versus-off-tonic, category-sensitivity, prevalence, or continuum claim.

| Opaque ID | Work and movement | Candidate | Frozen role | Primary reliability |
| --- | --- | ---: | --- | --- |
| `CASE-6U43` | C. P. E. Bach, Prussian Sonata in E major, Wq 48/3, iii | m. 51 | Focal | Included |
| `CASE-8JQJ` | Georg Benda, Keyboard Sonata No. 2 in G major, iii | m. 51 | Focal | Included |
| `CASE-DZWT` | Mozart, Piano Sonata in B-flat major, K. 570, i | m. 133 | Tonic anchor | Included |
| `CASE-Q2R9` | Mozart, Piano Sonata in B-flat major, K. 333, i | pickup in m. 93 into m. 94 | Tonic anchor | Included |
| `CASE-D09B` | Mozart, Piano Sonata in D major, K. 576, i | m. 99 | Tonic anchor | Included |
| `CASE-VT57` | Mozart, Piano Sonata in C major, K. 545, i | m. 42 | Off-tonic identification-sensitivity anchor | Excluded |

**Table 1.** The frozen corpus combined five primary dossiers with one separately analysed K. 545 identification-sensitivity anchor.

Each identity-withheld dossier encoded selected musical events, measure positions, metre, home key, and opening/candidate/post-candidate windows. The investigator-authored rubric assigned integer scores from 0 to 4 for tonal stability, thematic correspondence, preparation strength, proportional location, rhetorical emphasis, and rotational continuation. Greenberg did not propose or validate this rubric. The analysis response also distributed probability among `not_recapitulation`, `off_tonic_recapitulation`, and `tonic_double_return`, and disclosed a self-assessed recognition level. That disclosure is a model report, not evidence about training data or memorization.

Window construction was fixed before encoding: the first eight complete measures, with an opening anacrusis retained separately when present; six complete measures before the supplied candidate; the candidate-containing measure plus five; and six continuation measures. Candidate location was an operator decision, so the task tested ratings of supplied candidates rather than automatic discovery. Composer, title, catalogue number, absolute measure number, date, formal labels, and source prose were removed. All pitch material was mechanically normalized to tonic D while preserving mode, intervals, spelling relations, timing, register displacement, and encoded expression. Five dossiers received a nonzero transposition. K. 576 was already in D major and therefore received the identity transform, leaving exact source pitch and register intact.

Clementi's Sonata in B-flat major, Op. 10 No. 3, i remained a deferred replication case rather than a launch dossier. Greenberg does not work through this movement. Brownell's thesis reproduces mm. 67–74 from a Torricella 1783 copy and served as the case-specific coordinate witness; the BnF Longman and Broderip early print remained the notation authority.[@Brownell2010] A schema revision could represent the previously blocked event, but event convergence was established for mm. 69–71 rather than the complete required context. Adding it without source verification would have replaced a known design limitation with an unverified transcription. No music-theory-trained human reviewed the launch events or the six-cue scores. The two scan-derived focal dossiers were transcribed and reverse-checked by Codex agents under human operator supervision; the Mozart dossiers were compiled from pinned machine-readable sources.

### Systems, prompts, and freeze

The panel consisted of OpenAI `gpt-5.6-sol` through Codex CLI 0.144.6 (`openai-frontier`), Anthropic `claude-fable-5` through Claude Code 2.1.215 (`anthropic-frontier`), and OpenAI `gpt-5.5` through Codex CLI 0.144.6 (`openai-prior-generation`). The last label means an active prior-generation system in this panel, not a legacy or deprecated product state. Generation-role labels were checked against the providers' official model guides on the freeze date.[@OpenAIModels2026; @AnthropicModels2026]

This was a partial $2 \times 2$ provider-by-generation-role panel: OpenAI supplied frontier and prior-generation positions, while Anthropic supplied a frontier position. It was not three provider families, and it cannot estimate a causal provider or generation effect. The two OpenAI–Anthropic pairs share the same Anthropic system; the pooled three-system statistic gives OpenAI two of three positions.

All calls used fresh noninteractive contexts with tools, session reuse, and model fallback disabled. The OpenAI systems used high reasoning and low verbosity; the Anthropic system used high effort and adaptive thinking. The CLIs did not expose a common temperature or sampling seed, so provider defaults were part of each tested system. Model agents from both provider families had participated in protocol construction or read-only audit, but the outcome contexts received no repository, provenance file, earlier response, or external tool. The experiment is not external model validation.

The protocol was frozen at 2026-07-19 17:54:14 UTC. The dataset manifest SHA-256 was `6a027698775083ed275e0149685ec23cc07dea9d4f7f19b2a40b6c7d2eb246bb`; a 41-file collection lock followed at 17:56:35 UTC, and pre-outcome commit `eafb4496a44941271d0b4b67eadce8c6457a581d` preserved the blinded design. Seed `20260719` generated one randomized sequence containing all $2\ \text{tasks} \times 3\ \text{systems} \times 6\ \text{cases} \times 3\ \text{runs}=108$ slots. Each adapter passed a fictional-dossier schema preflight after the final prompt hashes were set. The collector ran on arm64 Darwin 25.5.0; the validator and analyzer used Node.js 24.8.0. The per-call timeout was 1200 s. The actual first call began at 18:15:05 UTC and the final call ended at 19:54:52 UTC on 2026-07-19.

The analysis and identification tasks were run separately. The second task requested composer, work, and movement guesses without showing the identity key. A deterministic masked packet reduced each valid guess to those structured fields. The frozen plan assigned alias-aware scoring to the operator; implementation instead used two separately run Codex adjudicators, neither with access to the other judgment set. They assigned `L2` for an exact composer/work/movement match, `L1` for a partial match, and `L0` otherwise, and agreed on all 54 levels. This disclosed operational deviation was factual, model-assisted alias adjudication, not independent human scoring or music-theory expert review.

### Frozen estimands and gates

Within-system repeatability treated each of the $5\ \text{target cases} \times 6\ \text{cues}=30$ case-cue combinations as a unit with three fresh-context ratings. Reported statistics were ordinal Krippendorff α, exact agreement, agreement within one scale point, mean absolute difference (MAD), and median absolute difference.[@Krippendorff2018] Coincidences used ordered within-unit pairs weighted by $1/(m_u-1)$; ordinal distance was the squared cumulative empirical marginal mass between category endpoints after subtracting half the mass at each endpoint. α was undefined with fewer than two coincidences or zero expected disagreement. A system passed when all 15 target responses were valid and non-null, MAD was at most 0.50, within-one agreement was at least 0.90, and α was at least 0.67. The repeatability gate required at least two passing systems spanning both providers; automatic expansion required that gate and every other frozen gate to pass.

Availability was analysed separately from score agreement. “Availability agreement” is the fraction of pairwise comparisons in which both entries were scored or both were unavailable; mixed scored/unavailable pairs reduce it. Within-system availability compared repetitions, while named-pair and pooled availability compared system medians.

For cross-system summaries, each system's median required all three repetitions for a case-cue unit; a median was null if any repetition was unavailable. Named OpenAI–Anthropic pairs were primary cross-provider descriptions, the OpenAI–OpenAI pair was a within-provider description, and the provider-unbalanced three-system statistic was secondary. Two thousand dossier-block bootstrap replicates used seed 1701 within systems and seed 1702 across systems. These intervals are resampling-sensitivity summaries over a nonrandom six-dossier convenience corpus, not population confidence intervals.

The remaining frozen gates required all 108 responses and 324 analysis cue cells to be valid and non-null; at least four of six cues to span two scale points in two repeatable systems across both providers; zero target `L2` events; no target work-level recognition self-report; and detection of the separate K. 545 anchor by either two runs of one system or at least one run from each provider. Invalid scheduled outputs could not be repaired or retried.

The raw namespace contained 540 files: one claim plus four finalized bundle files for each slot. All bytes were hash-bound before substantive scoring. A whitespace check then incidentally printed several response or stderr lines before the raw Git commit, primarily run-metadata declarations. The complete hash manifest preceded that exposure, commit `16304af52c0b1cf6b50cbdbec2dff0c81e25a05f` verified byte-for-byte against it, and the commit preceded substantive scoring and analysis. The raw Git commit did not precede every display of response text.

## Results

### Primary preregistered outcomes

All 108 scheduled slots terminated with no timeout, command failure, partial bundle, or retry. Figure 1 summarizes the reliability, gate, and identification patterns, and Table 2 gives validity separately for analysis and identification.

| System | Analysis valid | Identification valid | Combined valid |
| --- | ---: | ---: | ---: |
| OpenAI frontier | 18/18 (100.0%) | 18/18 (100.0%) | 36/36 (100.0%) |
| Anthropic frontier | 13/18 (72.2%) | 18/18 (100.0%) | 31/36 (86.1%) |
| OpenAI prior-generation | 18/18 (100.0%) | 18/18 (100.0%) | 36/36 (100.0%) |
| Total | 49/54 (90.7%) | 54/54 (100.0%) | 103/108 (95.4%) |

**Table 2.** Frozen-contract validity counts are tabulated by system and task.

Within-system results over the 30 primary case-cue units are reported in Table 3. The Anthropic statistic used 42 available rating pairs; its 95% α interval was defined in 1978 of 2000 bootstrap replicates. Each complete OpenAI arm used 90 rating pairs and had 2000 defined α replicates.

| System | Valid target calls | Complete three-run data | Ordinal α (bootstrap 95%) | Exact | Within one | MAD | Availability agreement |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| OpenAI frontier | 15/15 | Yes | 0.871 (0.706–0.944) | 0.778 | 1.000 | 0.222 | 1.000 |
| Anthropic frontier | 10/15 | No | 0.837 (0.318–1.000) | 0.762 | 1.000 | 0.238 | 0.600 |
| OpenAI prior-generation | 15/15 | Yes | 0.892 (0.851–0.926) | 0.778 | 1.000 | 0.222 | 1.000 |

**Table 3.** Within-system test–retest statistics use available ordinal pairs, while validity and availability columns retain missing scheduled responses.

The separately scoped K. 545 anchor had complete three-run data in all systems. Within-system α values were 0.979, 1.000, and 0.873 for OpenAI frontier, Anthropic frontier, and OpenAI prior-generation, respectively; exact agreement was 0.889, 1.000, and 0.556, and every pair was within one point. Anchor α was 0.638 for OpenAI frontier / Anthropic frontier, 0.832 for Anthropic frontier / OpenAI prior-generation, 0.793 for the OpenAI pair, and 0.758 for the provider-unbalanced three-system summary; all anchor medians were available.

The identification task returned 54 valid responses and 54 adjudications. The aggregate counts were 38 `L0`, 7 `L1`, and 9 `L2`. Table 4 locates the levels by case and distributes exact matches by system.

| Case | Probe role | L0 | L1 | L2 | L2: OpenAI frontier / Anthropic frontier / OpenAI prior |
| --- | --- | ---: | ---: | ---: | --- |
| C. P. E. Bach Wq 48/3/iii | Target | 9 | 0 | 0 | 0 / 0 / 0 |
| Benda Sonata No. 2/iii | Target | 9 | 0 | 0 | 0 / 0 / 0 |
| Mozart K. 570/i | Target | 7 | 2 | 0 | 0 / 0 / 0 |
| Mozart K. 333/i | Target | 6 | 3 | 0 | 0 / 0 / 0 |
| Mozart K. 576/i | Target | 2 | 1 | 6 | 2 / 2 / 2 |
| Mozart K. 545/i | Sensitivity anchor | 5 | 1 | 3 | 1 / 0 / 2 |
| Total | — | 38 | 7 | 9 | 3 / 2 / 4 |

**Table 4.** Masked adjudication counts list partial and exact identity matches for all valid identification outputs.

The structured analysis responses contained two target work-level recognition self-reports: OpenAI frontier on Wq 48/3/iii run 02 at confidence 0.78 and OpenAI frontier on K. 576/i run 01 at confidence 0.72. The frozen gate values are listed in Table 5.

| Gate | Frozen requirement | Printed outcome | Pass |
| --- | --- | --- | --- |
| Output | 108/108 valid; 324/324 cue cells non-null | 103/108 valid; 294/324 cue cells non-null | No |
| Repeatability | At least two complete passing systems spanning both providers | Two complete passing systems; provider set `{OpenAI}` | No |
| Dispersion | At least four of six cues qualified across passing systems and both providers | 0/6 qualified | No |
| Target identification | Zero target `L2` events | 6 target `L2` events, all K. 576/i | No |
| Analysis recognition | Zero target work-level self-reports | 2 target work-level self-reports | No |
| K. 545 sensitivity | Two `L2` runs in one system or one in each provider | OpenAI prior-generation 2/3; OpenAI frontier 1/3 | Yes |
| Automatic expansion | Every required gate passes | `false` | No |

**Table 5.** Frozen gate inputs and Boolean outcomes are reproduced from the deterministic analysis summary.

### Preregistered reporting addendum

The locked primary analyzer implemented the frozen estimands but omitted the pre-specified named-pair bootstrap output from its printed schema. After collection, a separate reporting script applied the frozen dossier-resampling rule, 2000 replicates, and seed 1702 without changing the locked analyzer, raw responses, or primary summary. Table 6 reports that addendum.

The named-system comparisons appear in Table 6. The pairwise calculations used a system median when all three repetitions for that case-cue unit were present. The provider-unbalanced pooled three-system statistic used 54 rating pairs and returned α = 0.841 (bootstrap 95% 0.698–0.950), exact agreement 0.722, within-one agreement 0.981, MAD 0.296, and availability agreement 0.600.

| Named systems | Relation | Units with both medians | Ordinal α (pair-bootstrap 95%; defined replicates) | Exact | Within one | MAD | Availability agreement |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| OpenAI frontier / Anthropic frontier | Cross-provider | 12/30 | 0.791 (0.324–1.000; 1837/2000) | 0.750 | 1.000 | 0.250 | 0.400 |
| Anthropic frontier / OpenAI prior-generation | Cross-provider | 12/30 | 0.786 (0.296–1.000; 1837/2000) | 0.667 | 0.917 | 0.417 | 0.400 |
| OpenAI frontier / OpenAI prior-generation | Within-provider | 30/30 | 0.884 (0.774–0.982; 2000/2000) | 0.733 | 1.000 | 0.267 | 1.000 |

**Table 6.** Named pair reliability and availability are reported with pair-specific dossier-block bootstrap intervals and the number of replicates in which α was defined.

### Post hoc descriptives and sensitivity checks

For each valid analysis response, Table 7 counts the status with the largest printed probability. Ties did not occur.

| Case | Valid analyses | Not recapitulation | Off-tonic recapitulation | Tonic double return |
| --- | ---: | ---: | ---: | ---: |
| C. P. E. Bach Wq 48/3/iii | 9 | 0 | 0 | 9 |
| Benda Sonata No. 2/iii | 7 | 0 | 7 | 0 |
| Mozart K. 570/i | 9 | 0 | 0 | 9 |
| Mozart K. 333/i | 8 | 0 | 0 | 8 |
| Mozart K. 576/i | 7 | 0 | 0 | 7 |
| Mozart K. 545/i | 9 | 0 | 9 | 0 |

**Table 7.** Maximum-probability status counts are post hoc descriptives over the 49 analysis responses that passed the frozen validator.

The five invalid outputs were all Anthropic frontier analysis responses. Each was complete, parseable, returned with exit status zero, and had empty standard error. Table 8 groups the two prompt–validator mismatches found in the immutable responses; one response had both findings, so the finding counts overlap. No response was repaired or retried.

| Contract finding | Outputs affected | Cases and runs | Prompt–validator relation |
| --- | ---: | --- | --- |
| `case_note` exceeded the unstated 40-word validator cap | 4 | Benda runs 02 (43 words) and 03 (58); K. 576 run 02 (43); K. 333 run 01 (43) | The model-facing prompt capped cue reasons, not `case_note` |
| Genuine dossier `direction_id` rejected by the measure-ID allowlist | 2 | Benda run 03 (`DR0002`, `DR0003`); K. 576 run 03 (`DR0003`) | The prompt requested dossier evidence identifiers; the validator admitted measure `E###` identifiers but excluded direction IDs |
| Overlap between findings | 1 | Benda run 03 | Both findings occurred in one response |
| Unique frozen-invalid outputs | 5 | Three dossiers | Invalid in the primary analysis |
| Prompt-aligned alternative interpretation | 5/5 accepted | Analysis 54/54; cue cells 324/324; combined 108/108 | Post hoc; primary records unchanged |

**Table 8.** The invalid-output audit preserves the frozen contract classifications and gives the completed post hoc prompt-aligned sensitivity count.

Under the post hoc interpretation in Table 8, the Anthropic within-system result was α = 0.815 (bootstrap 95% 0.663–0.900), exact agreement 0.778, within-one agreement 1.000, and MAD 0.222. All three systems across both providers met the repeatability thresholds. The pooled three-system result was α = 0.809 (0.694–0.900), exact agreement 0.689, within-one agreement 0.978, and MAD 0.333. Pair α was 0.761 for OpenAI frontier / Anthropic frontier, 0.770 for Anthropic frontier / OpenAI prior-generation, and 0.884 for the OpenAI pair; each pair had 30/30 system medians. Tonal stability and preparation strength qualified for the dispersion rule, for 2/6 cues against the required 4/6. In this sensitivity, the output and repeatability gates were true; the dispersion, target-identification, and analysis-recognition gates were false; automatic expansion was false.

## Discussion

The preregistered hypothesis was **falsified for automatic expansion**. This verdict does not depend on a borderline coefficient. The output, cross-provider repeatability, cue-dispersion, target-identification, and analysis-recognition gates all failed, while the separate identification-sensitivity condition passed.

The title's two clauses describe different findings. “Repeatable” applies narrowly to the two complete OpenAI systems: both crossed the frozen α, MAD, and within-one thresholds on all 15 target responses. It does not convert the Anthropic available-case α into a pass. Five invalid responses removed complete three-run medians from three target dossiers, so the two systems satisfying the complete-data gate came from one provider family. Reliability computed on available values has to be read beside availability, especially for the cross-provider pairs, which retained 12 of 30 shared medians.

“Not blind” is also narrow and observable. All three systems exactly named Mozart K. 576/i in two of three probes, producing six `L2` target events. The K. 545 sensitivity anchor produced two exact matches in the OpenAI prior-generation system and one in the OpenAI frontier system. K. 576 was also the only target for which normalization to D was an identity transform, so its original pitch and register survived; with one confounded case, the association cannot isolate a transposition effect. The outcome establishes that this elicitation protocol recovered some dossier identities. It does not establish memorization, training-set inclusion, or the route by which a system reached a guess. The model's separate recognition flag is likewise self-report, not provenance evidence.

The target identification pattern is more consequential for this design than the consistent status pattern in Table 7. Every valid response assigned the same maximum-probability status within a case, including off-tonic for Benda and tonic for Wq 48/3. Without an expert validator, those are stable outputs from the specified rubric—not correctness judgments about the works, confirmation of Greenberg's analysis, or evidence for a fuzzy continuum. Exact identity recovery also makes it impossible to maintain a strong identity-suppression claim for K. 576. A subsequent study must either change the representation, treat familiarity as an explicit factor, or pivot from nominal blindness to a contamination-sensitivity design.

The corpus bounds the musical inference in a second way. K. 545 was deliberately separated as the probe-sensitivity anchor, leaving two focal cases and three tonic anchors in the primary set. A reliability coefficient over that set cannot compare tonic and off-tonic returns. Clementi should remain in the research program because it can restore an off-tonic primary anchor and connect the extension to the source literature, but the missing source verification must be completed before it enters a frozen dataset. Retaining an unresolved case would not compensate for the current imbalance.

The invalid-output audit separates model behaviour from contract design. Four responses crossed a 40-word `case_note` cap that the model-facing prompt did not state. Two cited genuine `direction_id` values present in their frozen dossiers, but the validator's evidence allowlist admitted only measure-level identifiers; one response did both. These outputs violated the frozen validator and must remain invalid in the primary analysis. The post hoc prompt-aligned interpretation accepted the same five immutable responses, restored complete cross-provider repeatability, and changed the output and repeatability gates to true. It did not change the experiment's decision: cue dispersion still reached 2/6 rather than 4/6, and the two identity-related gates still failed. The contrast is evidence for revising the validator before dataset 2.0, not retroactively repairing dataset 1.0.0.

Several limits are structural. The panel is provider-unbalanced: two OpenAI systems and one Anthropic system form a partial $2 \times 2$, not three independent provider replications. The two cross-provider comparisons share the Anthropic arm. The six dossiers are a convenience set, three primary cases come from the same Mozart corpus, provider serving stacks and unexposed defaults are part of each system, and agents from both provider families helped construct or audit the protocol. No music-theory-trained human checked event selection, rubric validity, or model scores. The experiment supports claims about the test–retest repeatability, cross-system agreement, frozen-contract validity, and elicited identification of these frozen CLI systems; it supports no claim of music-theoretical correctness.

The provenance deviation also narrows the reproducibility claim. The raw bytes were hash-bound before incidental response text appeared, and the committed snapshot preceded substantive adjudication and analysis. It would be inaccurate to say that the raw commit preceded every on-screen response line. Recording that sequence matters because a blind-analysis claim is procedural, not something a checksum alone can supply.

Domain review remains possible even without claiming it happened. A music theorist can inspect the focal events at Wq 48/3/iii m. 51 and Benda Sonata No. 2/iii m. 51, the tonic anchors at K. 570/i m. 133, K. 333/i mm. 93–94, and K. 576/i m. 99, and the K. 545/i m. 42 sensitivity anchor. The repository's `research/off-tonic-recapitulation/data/cases/`, `data/provenance/transcriptions/`, frozen prompts, identity adjudication, and immutable output bundles provide case IDs and evidence identifiers for line-by-line criticism. The most useful expert response would identify a specific measure, event, cue definition, or score-source discrepancy so it can become a versioned correction rather than an appeal to authority.

### Data and Code Availability

The public [dataset 1.0.0 analysis-reproduction bundle](/downloads/off-tonic-recapitulation-1.0.0.zip) contains all 540 hash-verified raw artifacts, dossiers, prompts, frozen inputs, adjudication, analyzers, tests, and machine-readable primary, addendum, descriptive, and sensitivity results; its [SHA-256 record](/downloads/off-tonic-recapitulation-1.0.0.sha256) is published beside it. The primary summary includes the full target and K. 545 anchor reliability tables, cue-stratified direct measures, score-availability bins, recognition rows by system and case, and L2-stratified repeatability comparisons that are abridged in the article. The archive excludes score/source PDFs, source images, and scratch files, and includes an expert-review packet plus a third-party data notice.

## Conclusion

The next experiment is not a larger version of this one. Dataset 2.0 should first complete expert-readable source verification for Clementi or another primary off-tonic anchor, revise and preflight the output contract, choose a representation that either reduces identity recovery or models familiarity explicitly, and re-freeze a provider-balanced system panel. A music-theory expert should be able to audit each event and cue before collection, even if public expert feedback remains the practical review route. The next question for the research shelf is whether those changes preserve the observed test–retest stability while restoring complete cross-provider data and making identity risk an explicit experimental variable.

## References
