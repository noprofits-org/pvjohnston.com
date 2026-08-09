---
title: "One muon, two frames, and the workflow that parked itself"
date: 2026-08-09
author: Peter Johnston
tags: special relativity, research process, reproducibility
description: A minimal muon time-dilation calculation was pushed through a preregistered, multi-role research workflow as an acceptance trial. The two frames agreed exactly as they must; the workflow coordinated every step, then parked itself over a figure label. This note explains both machines.
post-type: understanding
question: How does an append-only, reviewed-handoff workflow graph coordinate a computer experiment — and what happened when a minimal muon time-dilation demonstration was pushed through it?
experiment: muon-survival-two-frames
og-image: /images/2026-08-09-muon-survival-two-frames-hero.png
---

This note explains two machines with one demonstration. The first machine is
special relativity's simplest working example: a muon created high in the
atmosphere survives to a detector that a naive calculation — the full
laboratory path at the same speed but with the undilated lifetime — says it
should essentially never reach, and two reference frames give two
different accounts of why it does — time
dilation in one, length contraction in the other — that must and do agree. The
second machine is the research workflow that this site briefly ran: an
append-only ledger of reviewed handoffs between separated roles, built to make
a computer experiment's provenance inspectable. The muon calculation was
deliberately chosen as the smallest possible cargo to push through that
machinery as an acceptance trial. The route through this note follows the
dependency order: first the physics, then the workflow that carried it, then
the ledger's own record of what that cost, and finally the place where the
workflow stopped and what stopping revealed. Neither machine gets a verdict —
this is a description of how each works, with the boundary stated at the end.

## One decay, two descriptions

A muon at fixed momentum decays with proper mean lifetime $\tau_0$; the
Particle Data Group central values used here are
$\tau_0 =$ [muon_mean_lifetime_s]{.metric} and a mass energy of
105.6583755 MeV.[@Navas2024] The demonstration freezes an idealized muon at
3.00 GeV/c momentum traversing [detector_distance_m]{.metric} of atmosphere,
decay-only, with no scattering or energy loss. Survival over a proper time $t$
is exponential:

$$
P = \exp(-t/\tau_0).
$$

Every quantity below reconstructs from the three declared inputs — momentum
$p$, mass energy $mc^2$, and laboratory path $L$ — through
$\gamma\beta = pc/(mc^2)$, $t_D = L/(\beta c)$, $L' = L/\gamma$, and
$t_M = L'/(\beta c)$. The two frames route to the proper time differently.

**Detector frame.** The muon moves at $\beta =$ [detector_beta]{.metric}, so
$\gamma =$ [detector_gamma]{.metric}. The laboratory crossing takes
$t_D =$ [detector_elapsed_time_s]{.metric}. The moving muon's lifetime is
dilated to $\gamma\tau_0 =$ [detector_mean_lifetime_s]{.metric}, and the
dimensionless decay exponent is $t_D/(\gamma\tau_0) =$
[detector_decay_exponent]{.metric}.

**Muon frame.** The muon is at rest and the atmosphere rushes past at the
independently reconstructed $\beta =$ [muon_beta]{.metric}
($\gamma =$ [muon_gamma]{.metric}). The path is contracted to
$L/\gamma =$ [muon_contracted_distance_m]{.metric}, crossed in proper time
$t_M =$ [muon_elapsed_time_s]{.metric} against the undilated lifetime
$\tau_0$. The exponent is $t_M/\tau_0 =$ [muon_decay_exponent]{.metric}.

The two exponents are the same physical quantity computed along two routes —
one proper time, two coordinate descriptions, not two causal mechanisms. At
the eight digits displayed here they coincide —
[detector_decay_exponent]{.metric} against [muon_decay_exponent]{.metric} —
and the stored binary64 values differ by exactly one representable step, at
the sixteenth digit, within the registered relative tolerance; Figure 2
prints both in full.
Analytic survival is [analytic_survival]{.metric}. A registered Monte Carlo
sample of 100,000 proper lifetimes (PCG64, seed 20260808) gives
[survivor_count]{.metric} survivors at the focal distance, an empirical
survival of [empirical_survival]{.metric} — a standardized discrepancy of
[focal_standardized_discrepancy]{.metric} binomial standard errors, an
implementation check of the assumed exponential law rather than independent
physics. The counterfactual with the same speed but no lifetime dilation
survives at [counterfactual_survival]{.metric}: essentially no muon would
arrive. That contrast is the classic Frisch–Smith measurement's logic, run as
an idealized calculation rather than an experiment on real
flux.[@Frisch1963]

<figure>
  <img src="/images/2026-08-09-muon-survival-two-frames-hero.png" alt="Two-panel figure: panel A shows survival probability against laboratory path for the detector frame, muon frame, empirical check, and a rapidly vanishing no-dilation counterfactual; panel B shows the two frame decay exponents as aligned markers on a common dimensionless axis.">
</figure>

**Figure 1.** The registered v1 figure, byte-preserved from the workflow
trial. **A**: analytic survival in both frames (coincident curves), the
empirical decay-law check, and the same-speed no-lifetime-dilation
counterfactual collapsing to zero within a few kilometres. **B**: the two
frame decay exponents as aligned markers on the common dimensionless axis.
Panel B is the panel the workflow's analysis review rejected: it aligns the
exponents but does not print the frame-specific distances and times that make
the two routes different. This note returns to that rejection below.

## The machine that carried it

The calculation above needs about a minute of computer time. The interesting
machinery is what surrounded it: a coordination graph this repository ran as
`research-workflow.mjs`, retired earlier this week and preserved for this note
in the experiment's own directory under
[`graph/`](/research/muon-survival-two-frames/graph/research-workflow.mjs),
together with [its state graph](/research/muon-survival-two-frames/graph/workflow.graph.v1.json)
and [its protocol document](/research/muon-survival-two-frames/graph/computational-authoring-workflow.md).
The design has four load-bearing ideas.

**Roles that cannot see each other's work.** The graph separates a
brainstormer, an experiment engineer, a run operator, an analyst, and
independent reviewers. The run operator executes the frozen command once and
seals the outputs without analyzing, plotting, or tuning; reviewers must
present a different actor identity than the producer they are checking. The
intent is that no single context can both produce a result and certify it.

**An append-only ledger.** Every submission and review appends one JSON event
to [`workflow.jsonl`](/research/muon-survival-two-frames/workflow.jsonl); no
event is ever edited. Each event names the graph node it leaves, the node it
enters, the actor, and a decision — approve, revise, amend, or park. Code 1
shows the trial's terminal event.

```json
{
  "sequence": 27,
  "type": "review",
  "actor": "amendment-reviewer-muon-14",
  "role": "independent_reviewer",
  "from": "amendment_review",
  "to": "parked",
  "decision": "park"
}
```

**Code 1.** Fields from the ledger's final event: an independent amendment
reviewer routes the experiment from `amendment_review` to the terminal
`parked` state. The full event also carries a UUID, a timestamp, the SHA-256
of the governing graph, and the evidence snapshot it binds.

**Evidence bound by hash.** A submission is not prose in a chat window; it is
a small receipt file, snapshotted immutably under
[`workflow/`](/research/muon-survival-two-frames/workflow/setup-review-v7.md)
with its SHA-256 recorded in the ledger event. The approved setup manifest
hash-binds the renderer; the admitted run hash-binds the setup manifest; every
ledger event records the SHA-256 of the graph it obeyed. The chain means a
later reader can verify, not merely trust, which bytes each approval covered.

**Deterministic replay.** The CLI's `verify` command replays the entire ledger
against the graph's rules and every snapshot's hash. Replayed under the
retired engine while preparing this note, this trial's ledger still validates:
[ledger_events]{.metric} events, [ledger_evidence_snapshots]{.metric}
snapshots, terminal state `parked`.

## What the ledger recorded

The ledger is itself a dataset, and this note's metrics derive from it the
same way the physics metrics derive from the run summary. The trial ran
[ledger_wall_clock_hours]{.metric} from initialization to terminal event, in
[ledger_events]{.metric} events: [ledger_submissions]{.metric} submissions
and [ledger_reviews]{.metric} independent reviews, of which
[ledger_revise_decisions]{.metric} sent work backward.

The concentration of those revisions is the striking part. Setup review alone
ran [ledger_setup_review_rounds]{.metric} rounds before execution was
permitted. The findings were real — the trial's own retrospective lists
non-atomic file publication, replay defects, and time-of-check gaps among
them — but nearly all concerned the workflow's own hardening requirements
rather than the muon. The generator that those reviews produced wrote one
small JSON file through a staged, fsynced, hardlink-quarantine protocol, and
is preserved as part of the specimen
([`graph/hardened-generate-metrics.mjs`](/research/muon-survival-two-frames/graph/hardened-generate-metrics.mjs));
it also shelled out to a local Python environment that exists on no other
machine, so the first continuous-integration run would have failed it. The
canonical science under all of this was one 100,000-draw sample, 201 grid
points, and one figure.

Execution itself, by contrast, was clean and brief: one run, sealed and
admitted on review without result inspection, exactly as designed. The
analysis reviews then did the most genuinely scientific work of the trial:
the first rejected panel B of Figure 1 for aligning the two exponents without
printing the frame-specific distances and times — a real fidelity gap between
the figure and its stated purpose.

## The amendment with no edge

Fixing panel B changes no number, no seed, no curve, and no claim. It is a
presentation-only correction: re-render one panel from the unchanged,
already-admitted `results/summary.json`. But the approved setup manifest
hash-bound the v1 renderer, so editing it would break the very chain that made
the run trustworthy, and graph v1's only post-exposure route — amendment,
amendment review, amended setup, re-execution — requires a fresh run lineage.
The [amendment receipt](/research/muon-survival-two-frames/AMENDED-PROTOCOL-v2.md)
that the trial filed is explicit that every available move was unlawful:
rerunning would violate the one-run rule for a change that needs no run;
editing the renderer would violate the hash binding; calling the old run's
validation a "new execution" would satisfy the graph by lying to it. The
independent amendment reviewer agreed and parked the experiment.
The retired CLI's status output for this
experiment still ends: *"Allowed: none; merge or close the parked work
externally."*

That is a workflow-valid stop and an honest one — every actor followed the
rules, and the rules had no edge for a cosmetic fix. The trial's
[retrospective](/research/muon-survival-two-frames/WORKFLOW_RETROSPECTIVE.md)
called this the blocker: the graph could not distinguish a presentation change
from a scientific one, so it priced both at a full new run lineage, and a
figure label became terminal.

## The corrected panel, one script later

This note is published under the repository's successor pipeline — branch,
automated checks, pull request, continuous integration — which replaced the
graph. Under it, the parked correction took one small reviewed script:
[`src/render_figure_v2.mjs`](/research/muon-survival-two-frames/src/render_figure_v2.mjs),
the artifact the amendment receipt named but could not lawfully create. It
keeps the control that mattered — every printed value is read from the
unchanged canonical `results/summary.json` at render time, never typed by
hand — and drops the machinery that did not: no manifest rebinding, no new
run, no state machine. Figure 2 is its output.

<figure>
  <img src="/images/2026-08-09-muon-survival-two-frames-panel-b-v2.svg" alt="Corrected panel B: detector and muon frame route cards each print their distance, elapsed time, mean lifetime, and full-precision stored decay exponent, beside two aligned markers on the common dimensionless exponent axis.">
</figure>

**Figure 2.** The corrected panel-B presentation. **A**: the detector route —
laboratory path, elapsed time, dilated mean lifetime, and its stored exponent.
**B**: the muon route — contracted path, proper time, proper lifetime, and its
stored exponent. **C**: the two markers on the common dimensionless axis,
aligned because the printed sixteen-digit exponents differ only at the final
digit, within the registered relative tolerance. Both stored values are
printed unaltered rather than replaced by a shared rounded value. The muon
route is drawn in orange rather than Figure 1's purple because the v1
blue–purple pair fails a color-vision-deficiency separation check — a defect
[ledger_setup_review_rounds]{.metric} rounds of setup review did not look
for.

## Where the model stops

Each machine has a boundary, and stating them is the point of this note.

The physics demonstration establishes coordinate consistency, not new
physics: one proper time, two bookkeeping routes, an idealized fixed-momentum
muon with decay as the only process. It predicts no real atmospheric flux and
measures nothing; the Monte Carlo checks the implementation, not nature.

The workflow's boundary is subtler. What it can establish is process
integrity: that specific bytes passed specific reviews in a specific order,
that no result was tuned after exposure, that a reader can replay the whole
claim. What it cannot establish is proportion or meaning. Actor identities are
self-asserted labels, so role separation is a discipline the operators chose
to honor, not a fact the ledger can prove. The graph cannot tell a cosmetic
change from a scientific one, which is exactly how a figure label became a
terminal state. And its cost scales with its own machinery rather than with
the science it carries: the ledger's hours were spent almost entirely on the
carrier, not the cargo. This repository retired the graph for that reason;
the values this note reports are the trial's exposed v1 results, published
here with that lineage disclosed rather than under an approved graph
descent. The retirement is a proportionality judgment, not a refutation —
nothing in this note shows the controls failing; it shows them costing more
than a small demonstration can carry. A consequential, adversarial, or
multi-machine experiment could still rationally choose machinery like this,
ideally with the reduced presentation-amendment lane whose absence parked
this trial.

## Reproducibility

The canonical run executed once on 2026-08-09 under the pinned environment in
[`environment.md`](/research/muon-survival-two-frames/environment.md) and
[`requirements.lock.txt`](/research/muon-survival-two-frames/requirements.lock.txt)
(CPython 3.12.3, NumPy 2.5.1, binary64 throughout; PCG64 seed 20260808), via
the frozen command recorded in the experiment
[README](/research/muon-survival-two-frames/README.md). Its sealed sample and
manifests are committed under `runs/run-001/`. From the committed outputs,
stock Node.js regenerates everything this note displays:
`research/muon-survival-two-frames/generate-metrics.mjs` rebuilds
`metrics.json` from `results/summary.json` and `workflow.jsonl`, and
`src/render_figure_v2.mjs` rebuilds Figure 2 from `results/summary.json`.
Both support `--check`, and the metrics generator's check also replays the
figure check, so continuous integration exercises both on every build.
Figure 1 is the byte-preserved v1 PNG and is deliberately not regenerated.

Those are projection- and presentation-level regenerations, and the earned
label is **traceable** — not analysis-reproducible. Regenerating
`results/summary.json` itself from the sealed sample requires the pinned
Python environment plus a restored verifier layout: `src/analyze.py` invokes
the hash-bound workflow verifier at its original repository paths, and no
single commit contains both this experiment and that verifier, because the
trial branch merged after the retirement. The preserved `graph/` copies are
byte-identical to the retired originals, so the restoration is copying two
files back to their old paths in a scratch clone, as the experiment README
describes. The ledger replay reported above ran against the same restored
layout.

## References
