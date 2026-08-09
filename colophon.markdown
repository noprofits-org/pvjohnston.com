---
title: How this notebook is made
description: How AI agents perform most of the research, engineering, writing, and verification behind pvjohnston.com under human direction — and how every published number stays traceable to a committed artifact.
---

# How this notebook is made

A note on this site is the visible end of a short, checkable pipeline:

**question → branch → experiment → draft → checks → pull request → CI → publish.**

This page explains each step, who does the work, and what the checks can and
cannot prove. It describes the system that is live now. Older notes may predate
parts of it.

## Who does the work

Calling this notebook *AI-assisted* would understate it. In a typical session I
describe a question or a direction that interests me; an AI agent then reads
the repository and the relevant literature, proposes the route, writes and
debugs the code, runs the computations, drafts and revises the prose, and
carries the change to a pull request. I steer at consequential turns, decide
what belongs here, and remain accountable for everything published.

That division of labor is the reason the pipeline is built the way it is. A
long model conversation is useful working memory, but it is not a scientific
record. So the repository — code, sources, results, checks, commits, pull
requests — is the durable record, and everything below exists to keep that
record inspectable.

## From question to draft

Every note declares one of two forms before drafting:

- A **Research** note asks whether a claim survives a stated test. Before
  prose, it names its primary source, states its contribution in one sentence,
  and writes down a hypothesis with the outcome that would falsify it —
  committing to publish that outcome too. It reports in the standard scientific
  structure (Methods, Results, Discussion) and ends with a verdict on its own
  hypothesis: *supported*, *falsified*, or *inconclusive*.
- An **Understanding** note explains how something works. It claims synthesis,
  not novelty: one explanatory question, ideas in dependency order, computed
  demonstrations, and an explicit boundary where the explanation stops.

The stance is the same in both: an outsider learning in public. A discrepancy
means "this did not reproduce for me under these conditions," never "the
authors were wrong," and every note should make it easy for a better-informed
reader to correct me.

## The experiment owns its evidence

When a note generates results, one directory under
[`research/`](https://github.com/noprofits-org/pvjohnston.com/tree/main/research)
owns the computational record: the executable code, a precise environment
record, the canonical outputs, and an explicit allowlist of the files served to
readers.

Published numbers travel from that directory into sentences **by name, not by
copy and paste**. The analysis writes a small typed `metrics.json`; the
Markdown cites a value as a named metric reference; the site build resolves the
name and refuses to build if the metric, its file, or its experiment is
missing. A value cited this way cannot silently drift from the committed
artifact it claims to report. The guarantee covers metric references only — the
build cannot classify every numeral in prose, so a number typed by hand is
still just a number.

Each experiment earns its reproducibility label rather than asserting it:

1. **Traceable** — published result prose resolves from a validated metrics
   artifact.
2. **Analysis-reproducible** — the committed outputs can regenerate the
   analysis and metrics.
3. **End-to-end reproducible** — the documented inputs and environment can
   rerun the experiment itself.

[From script to sentence](/posts/2026-07-20-from-script-to-sentence.html)
walks one small calculation through the whole chain, with every file
reader-facing.

## Build and checks

The source is Markdown with YAML metadata. Pandoc parses it; BibTeX and an ACS
citation style resolve the references; MathJax renders the equations; TikZ
diagrams compile to inline SVG; Hakyll (a Haskell site compiler) assembles the
pages, feeds, and listings.

No single green command means "the post is correct," so several narrow checks
each do one job:

- `verify-bib.mjs` rejects duplicate citation keys in the shared bibliography.
- `verify-metrics.mjs` proves each committed metrics file is reproduced by its
  generator from fingerprinted sources.
- `verify-site.mjs` fails on missing links and assets, failed diagrams, and
  advertised files the site does not actually serve.
- The Haskell test suite and a full clean site build run on every pull
  request's exact commit in CI before it can merge.

Nothing is authored on the live branch. Work happens on a branch, the pull
request rebuilds and re-verifies it from scratch, and merging deploys the
static site to GitHub Pages.

## What the checks cannot establish

The machinery can prove that citations resolve, that named metrics match their
committed artifacts, that links and diagrams work, and that the same commit
passed every test before deployment. It cannot establish that the question was
worth asking, that the model or its interpretation is correct, or that
internal review by another AI context is peer review. Sources, executable
artifacts, and reproducible checks carry the evidentiary weight; confidence —
human or model — by itself does not.

---

The complete source, publishing code, and conventions live in the
[public repository](https://github.com/noprofits-org/pvjohnston.com); the
authoring rules are in
[`notes/blog-authoring.md`](https://github.com/noprofits-org/pvjohnston.com/blob/main/notes/blog-authoring.md).
This notebook separated from [noprofits.org](https://noprofits.org) in July
2026.
