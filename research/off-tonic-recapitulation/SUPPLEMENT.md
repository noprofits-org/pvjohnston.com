# Supplement: how this pilot was built

This document is the work record for the off-tonic LLM-reliability pilot. The
preregistration says *what* is measured; this says *how the apparatus and
corpus were actually produced*, by whom, and with which tools — including
approaches that failed. It is operator-side documentation and is never
model-facing.

Two agent roles appear throughout, both supervised by the human operator
(Peter Johnston): a **researcher agent** (OpenAI Codex) that designed the v2
protocol and builds transcriptions, and an **operator-session agent** (Claude)
that acquired sources, repaired the protocol after adversarial review,
verified concordances, and built the Mozart dossiers. All work landed on the
branch `codex/off-tonic-llm-reliability` on 2026-07-18.

## Phase 0 — v1 scaffold (superseded)

An earlier experiment design ("model-coded fuzziness in off-tonic
recapitulations", v1) lived in the main working tree: a six-cue rubric,
blinded dossiers, a frozen-manifest runner. Its research question — whether
model cue profiles support Greenberg's (2025, doi:10.1111/musa.12251)
continuum claim — was judged unanswerable by its own interpretation boundary:
every outcome had a deflationary reading (correlated training data,
model-dependence, encoding artifacts). The v1 corpus was never built.

## Phase 1 — v2 redesign (researcher agent)

The researcher agent reframed the study around what a six-case pilot *can*
answer: within-model test-retest repeatability, cross-model reliability, and
elicited identification of purportedly anonymized canonical repertoire — with
the continuum question explicitly deferred. Products: PREREGISTRATION.md,
STATISTICAL_ANALYSIS.md (ordinal Krippendorff's alpha with dossier-clustered
bootstrap), RUN_MATRIX.md + run-matrix.json (108-call schedule), both task
prompts, the case schema (3.0.0), the extraction protocol, the six-case
corpus selection (two Greenberg focal cases, two tonic anchors, two off-tonic
anchors with K. 545 as a deliberate positive identification control), the
full runner/validator/analyzer library, and six test suites. The K. 545
positive control is the design's key affordance: sensitivity of the
identification probe must be demonstrated before any non-identification
result means anything.

## Phase 2 — source acquisition (operator session)

- Greenberg's seven focal movements were identified by reading the paper
  (the operator's PDF); only two are in the pilot.
- Scores were fetched from IMSLP via its MediaWiki API + the `s9` mirror
  (the main image server has a CAPTCHA wall; the API's `imageinfo` URLs plus
  the `IMSLP<index>-` filename convention on the mirror bypass it cleanly —
  documented here because it is the reproducible route).
- Every scan was hash-pinned in `data/provenance/source-manifest.json`. Two
  files (Wq. 48 first edition, Clementi Op. 10) were independently fetched
  twice — operator download and agent download — and matched byte-for-byte.
- The researcher agent independently located the Benda 1757 *Sei sonate*
  first edition at SLUB Dresden, which supersedes the 1954 MAB edition as
  content authority. The MAB editor's notes state its dynamics, phrasing,
  and pedaling are editorial additions — a provenance hazard flagged for the
  `rhetorical_emphasis` cue: dossiers must not encode a 1954 editor's
  dynamics as Benda's.
- DCML `mozart_piano_sonatas` v2.3 was cloned at the pinned commit
  (5337257a...) and all twelve pinned file hashes verified.

## Phase 3 — adversarial protocol repair (operator session)

An external adversarial review produced six repairs, all applied across the
preregistration, statistical plan, prompts, schema, validator, analyzer, and
tests (commit `7e88f77`):

1. Primary reliability gates now use only the five target cases (30
   case-cue units); K. 545 is computed identically but reported as a
   separate anchor block and enters no gate.
2. Common transposition tonic changed from C to **D**. Under C, K. 545 —
   originally in C major — would have been presented *untransposed in its
   source key*, defeating the masking rationale for the one case designed to
   be recognizable. No pilot source is notated in D, so under D every case
   is displaced.
3. Fresh-context repetitions are described and analyzed as **same-input
   test-retest stability** of one stochastic system, never as independent
   corroboration.
4. Analysis responses now carry a structured `suspected_recognition` field
   (`none`/`style`/`composer`/`work` + confidence, no naming); flags are
   tabulated beside probe outcomes and a work-level flag on a target case
   triggers the same review as an isolated L2.
5. All "genuinely blinded" claims were replaced by **elicited
   identification** language: a silent probe is an elicitation result, not
   evidence of non-recognition.
6. A stray 8+8+8+8 window reference was corrected to the actual 8+6+6+6
   rule. Response schema bumped to 2.1.0.

A latent bug this surfaced: the DCML extractor (written against the v1
protocol) still transposed to C. First extraction runs produced a K. 545
dossier in its original key. The extractor, schema, validator, and fixtures
were switched to D and the dossiers regenerated (commit `4899687`).

## Phase 4 — source concordance (operator session)

Full log: `data/provenance/CONCORDANCE.md`. Method: measure arithmetic on a
clean modern edition, cross-checked against the first edition at system
level; claimed candidate coordinates verified against both.

- **Benda iii**: exposition = 26 measures including the volta (per-system
  counts 5+5+4+3+5+3+volta in MAB, repeat placement concordant in the 1757
  print); candidate m. 51 confirmed (m. 1 theme figure over G-sharp-inflected
  bass immediately after the m. 50 mediant cadence).
- **Wq. 48/3 iii**: located in both editions (Presto 6/8); exposition
  resolved to 29 measures (end-repeat closes Nagel p. 15 system 4; the a)/b)
  marks are ossia footnotes, not voltas); m. 51 = p. 16 system 1, final bar.
- **Clementi Op. 10 No. 3 i**: movement located (plates 13-15; part 1 =
  plate 13 ending with repeat + "Volti"); m. 69 and the key/mode
  (B-flat major per the corpus CSV vs a G-minor listing that probably
  describes the different Artaria op. 9 publication) left to
  transcription-time resolution.
- **K. 333 pickup**: fully reconciled to DCML coordinates. Notated m. 63 is
  split across the exposition repeat (mc64 = 3/4 bar + end-repeat; mc65 =
  1/4 remainder opening part 2), and the recapitulation's anacrusis is the
  F5-Eb5-D5 group at beat 4 of notated m. 93 (mc95, onset 3 quarter notes;
  a zero-duration grace F5 marks it). Config: candidate_mc 95, onset 3/1,
  second_part_mc 65.

### Measure-counting methods (including failures)

Counting measures in scans was the recurring mechanical problem. What was
tried, in order:

1. **Visual counting on full-page renders** — too error-prone (±1 per
   system).
2. **Naive column-density barline detection** — failed (inter-staff white
   space dilutes column fractions; ossia staves break band detection).
3. **Longest-vertical-run detection per grand-staff system** — reliable on
   clean modern engravings (MAB, Nagel), where barlines are the only
   full-height vertical runs; measure counts per system were then verified
   visually on cropped strips. This produced the Benda and Wq. 48 numbers.
4. **The same detector on 18th-century plates** — failed: those engravings
   draw barlines per staff, not through the system.
5. **Cross-staff alignment intersection** (per-staff vertical candidates
   matched across treble/bass x-positions) — still too noisy on irregular
   engraving; abandoned in favor of transcription-time counting, where
   numbering is a byproduct of measure-by-measure work.

The researcher agent independently wrote three barline detectors in parallel
(captured in `data/provenance/tools/`) and then pivoted to OMR (Audiveris)
with MusicXML post-processing — the approach now in flight for the three
transcription dossiers.

## Phase 5 — Mozart dossier extraction (operator session)

Six opaque case IDs were minted (secrets-random, `CASE-XXXX`) and recorded
with roles in the operator identity key. Strict per-case extraction configs
(`data/provenance/extraction-configs/`) drive the researcher agent's tested
DCML extractor; dossiers were validated by the schema/semantic validator and
their second-part rationals verified by independent hand arithmetic
(K. 545: 45 x 4 = 180 total, 52 elapsed; K. 570: 130 x 3 = 390, 159
elapsed; K. 333: 408 total including the quarter-note repeat fragment and a
3/4 final measure, 120 elapsed to the beat-4 anacrusis). Committed:
`CASE-DZWT` (K. 570), `CASE-Q2R9` (K. 333), `CASE-VT57` (K. 545), each with
an operator audit JSON.

## Phase 6 — transcription delegation (in progress)

The three scan-based dossiers (Wq. 48/3 iii, Benda iii, Clementi Op. 10/3 i)
were delegated to the researcher agent with the brief below. At the time of
writing, the agent has an OMR pipeline running (Audiveris books over the
legibility editions and the BnF Clementi scan, MusicXML conversion via
`musicxml-table.py`) and an in-progress `scripts/compile-transcription.mjs`
implementing the compact-source-to-dossier compiler with tonic-D
transposition. Per-case working directories live under `tmp/omr/` (gitignored;
regenerable from the pinned sources).

### Delegation brief (verbatim)

```
Transcription task: build the three scan-based dossiers for the off-tonic
LLM-reliability pilot.

REPO: /private/tmp/pvjohnston-music-theory (git worktree, branch
codex/off-tonic-llm-reliability — commit to this branch, push to origin).
Work only inside research/off-tonic-recapitulation/.

READ FIRST (these are the authority; do not re-derive protocol from memory):
- PREREGISTRATION.md (evidence construction, tonic-D transposition)
- data/provenance/EXTRACTION_PROTOCOL.md (schema 3.0.0, windows, canonical
  IDs, voice mapping, normalization, validation steps)
- data/provenance/CONCORDANCE.md (verified coordinates + open items)
- data/provenance/identity-key.json (case IDs)
- data/cases/CASE-DZWT.json (a finished, valid dossier — copy its exact shape)

TASK: produce three schema-3.0.0 dossiers from the first-edition scans in
data/sources/operator/, ending with node scripts/validate-case.mjs PASS on
each:

1. CASE-6U43 — C.P.E. Bach Wq 48/3, movement iii ("Presto", 6/8, E major).
   Source: cpe_bach_wq48_1742_first_edition.pdf PDF pages 16-17 (plates
   13-14). The Nagel 1927 edition may be used for legibility cross-check
   ONLY — dynamics/articulation come from the 1742 print. Verified:
   exposition = 29 measures (part 2 starts m. 30); candidate m. 51.
   Windows: W1 = mm. 1-8 (check for anacrusis), W2 = 45-50, W3 = 51-56,
   W4 = 57-62. OPEN, must resolve: exact total measure count (~81-84) —
   it is the denominator of second_part_total_qn.

2. CASE-8JQJ — Benda 1757 Sonata No. 2 in G, movement iii ("Allegro", 3/4).
   Source: benda_1757_first_edition_slub.pdf scan pages 18-19 (plates 11-12).
   The MAB 1954 edition may be used for legibility ONLY — its
   dynamics/phrasing/pedaling are EDITORIAL (editor's own notes admit this);
   encode dynamics only where the 1757 print has them (nearly none).
   Verified: exposition = 26 measures including the volta measure; candidate
   m. 51 (theme over G-sharp harmonization after the iii:PAC at m. 50);
   m. 1 opens with a downbeat rest, no anacrusis. Windows: W1 = 1-8,
   W2 = 45-50, W3 = 51-56, W4 = 57-62. Resolve and record how the volta
   pair maps into measure numbering and the exact total measure count.

3. CASE-Z3F9 — Clementi Op. 10 No. 3, movement i ("Presto", common time,
   two flats). Source: clementi_op10_early_edition_bnf.pdf scan pages 14-16
   (plates 13-15; part 1 = all of plate 13, ends with repeat + "Volti").
   OPEN, must resolve BEFORE encoding: (a) key/mode — pilot-corpus.csv says
   B-flat major; an IMSLP listing says G minor but probably describes the
   different Artaria op. 9 publication; decide from the opening bass and the
   part-1 cadence and record the evidence. (b) Verify the candidate is m. 69
   with a subdominant theme return, counting measures in the print. (c) Then
   fix windows: W1 = 1-8 (+anacrusis if present), W2/W3/W4 = the six-measure
   windows around the verified candidate per EXTRACTION_PROTOCOL. Record the
   Torricella-1783 concordance as NOT PERFORMED (no Torricella source on
   disk) in the source manifest notes.

METHOD (this is the part that keeps it auditable):
- Render high-DPI crops with PyMuPDF into tmp/ (gitignored) as needed.
- Do NOT hand-write the big dossier JSON. Author a compact per-measure
  operator transcription in the ORIGINAL key (one file per case, e.g.
  data/provenance/transcriptions/CASE-XXXX.source.json) plus a compiler
  script (scripts/compile-transcription.mjs) that: applies the tonic-D
  transposition per EXTRACTION_PROTOCOL (reuse/port the logic in
  scripts/lib/extract-dcml-mozart.py), assigns canonical E/EV/DR/V IDs in
  traversal order, computes second_part_elapsed/total from notated durations
  (count each written measure once, voltas once, no repeat unfolding), and
  emits the dossier. Commit transcription sources + compiler: together they
  satisfy the protocol's regeneration requirement.
- Keep a correction log per case (data/provenance/transcriptions/
  CASE-XXXX.corrections.md): every hard-to-read spot, every decision.
- Voice mapping: per EXTRACTION_PROTOCOL — stable movement-wide V01/V02
  from staves, documented in the correction log.
- Verify each dossier measure-by-measure against the scan before declaring
  done (protocol Validation steps 1-5; step 2 = regeneration via the
  compiler; step 3 = reverse-render an event table and compare with the
  scan; note step 5's identity scan).
- Update CONCORDANCE.md with everything resolved; update
  data/provenance/audits/ with an audit JSON per case mirroring the Mozart
  audit shape.

RULES:
- Never write composer/work/key names or measure numbers of the source into
  any model-facing file (data/cases/*.json). Identity stays in provenance.
- Do not touch data/manifest.json status, run-matrix.json, prompts, or
  outputs/. No model calls. The freeze happens later.
- All 6 existing test suites must still pass (node scripts/test-*.mjs).
- Commit in meaningful chunks with clear messages; push the branch when done.
- If a window is unreadable in the scan or the protocol cannot represent
  something (schema limitation), STOP on that case and record the blocker in
  CONCORDANCE.md rather than guessing.
```

## Captured tooling

`data/provenance/tools/` preserves scratch scripts that would otherwise be
lost to the gitignored `tmp/`:

- `detect-barlines.py`, `detect-verticals.py`, `detect-paired-verticals.py`
  (researcher agent): three successive barline-detection attempts on the
  scans, paralleling the operator session's inline versions (documented in
  Phase 4 above).
- `musicxml-table.py` (researcher agent): converts Audiveris MusicXML output
  into a per-measure event table for the transcription pipeline.

The operator session's own throwaway analysis code (contact-sheet builder,
system croppers, the longest-run barline counter and its cross-staff
variant) ran inline; the algorithms and their outcomes are described in
Phase 4, and the successful longest-run method survives in this document
rather than as a script because its per-page parameters were tuned
interactively.

## State at time of writing

- Protocol, statistical plan, prompts, schema, validator, analyzer, runner:
  repaired, tested (6/6 suites), committed, pushed.
- Corpus: 3 of 6 dossiers built and validated (Mozart/DCML); 3 in
  transcription (researcher agent, OMR-assisted).
- Not yet done: transcription completion + verification; the freeze
  (model families, adapters, token-limit check, 108-call schedule,
  collection lock, tag); the 108 scheduled calls; adjudication; the
  preregistered analyzer run; the IMRaD write-up. The preregistration's
  stop rules gate each step.
