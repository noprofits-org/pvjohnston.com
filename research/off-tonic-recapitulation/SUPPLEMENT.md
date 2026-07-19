# Supplemental work record: construction of the off-tonic reliability pilot

This is the operator-side construction record for the off-tonic
LLM-reliability pilot. The preregistration specifies what the experiment is
intended to measure; this supplement records how the apparatus and corpus were
actually made, what evidence was accepted, what failed, what was corrected,
and what remains unavailable. It is deliberately more detailed than the
model-facing materials because the experiment would not be reproducible or
auditable without that separation.

Nothing in this document is model-facing. Composer names, work identities,
source keys, edition metadata, and source measure coordinates are confined to
provenance. The dossiers in `data/cases/` retain only opaque case IDs,
window-relative measures, tonic-D symbolic evidence, and preregistered
structural fields.

## Executive outcome

The scan task requested three schema-3.0.0 dossiers. The protocol's stop rule
allowed only two to be produced:

| Case | Authority | Result | Exact second-part time |
| --- | --- | --- | --- |
| `CASE-6U43` | C. P. E. Bach Wq 48/3/iii, 1742 first edition | completed, regenerated, reverse-checked, validated | elapsed 63 qn; total 147 qn |
| `CASE-8JQJ` | Benda Sonata No. 2/iii, 1757 first edition | completed, regenerated, reverse-checked, validated | elapsed 72 qn; total 141 qn |
| `CASE-Z3F9` | Clementi Op. 10 No. 3/i, BnF early print | stopped before encoding: mandatory W3 contains textual `dimi:` not representable without loss | not promoted to a dossier |

The resulting corpus therefore contains five validated dossiers: three
previously extracted from pinned DCML sources and the two completed scan
dossiers. It does not contain a guessed sixth dossier. The absent Clementi case
is a documented schema exclusion, not missing work silently treated as data.

No model calls were made. `data/manifest.json`, `run-matrix.json`, prompts, and
`outputs/` were not changed. The collection freeze still happens later.

## People and agent roles

Peter Johnston is the human operator. Two supervised agent roles contributed
to the repository on 2026-07-18:

- an operator-session agent (Claude) acquired and pinned sources, repaired the
  design after adversarial review, established initial concordances, and built
  the three DCML/Mozart dossiers;
- a researcher agent (OpenAI Codex) designed the v2 protocol and software, then
  performed the present scan transcription, compiler, correction logs, reverse
  rendering, and audits.

These are not independent raters. The scan dossiers had one transcription
operator. Modern editions and OMR provided legibility checks, not independent
extractions. The absence of a second independent human pass is carried as a
limitation in each audit rather than obscured by describing agent sessions as
independent evidence.

## Design history

### Superseded v1

An earlier experiment asked whether a six-cue model rubric supported a
continuum of off-tonic recapitulation. That design was abandoned before corpus
construction because every possible result had a deflationary interpretation:
training-data familiarity, model dependence, and encoding artifacts could not
be separated from the proposed music-theoretical claim.

### v2 reliability redesign

The researcher agent reframed the pilot around questions a six-case sample can
answer: same-input test-retest stability within a model, cross-model
reliability, and elicited identification of purportedly anonymized repertoire.
The continuum claim was deferred. The v2 work produced the preregistration,
statistical analysis plan, two prompt families, response and case schemas,
runner, validator, analyzer, schedule, pinned corpus plan, and six test suites.

The deliberate K. 545 recognition control is central to interpretation. A
silent identification probe is informative only if the apparatus first shows
that it can elicit recognition where recognition is expected.

### Adversarial repair

An adversarial review led to six cross-cutting corrections, committed in
`7e88f77`:

1. Primary reliability gates use the five target cases; the K. 545 anchor is
   reported separately.
2. Common transposition changed from C to D. No pilot source is originally in
   D, so every case is displaced, including the positive recognition control.
3. Repetitions are described as stochastic same-system test-retest trials, not
   independent corroboration.
4. Analysis responses gained a structured, non-naming recognition-suspicion
   field.
5. Claims of genuine blinding were replaced by elicited-identification
   language.
6. A stray 8+8+8+8 window summary was corrected to 8+6+6+6.

The repair also exposed a stale C-transposition path in the DCML extractor.
The extractor, schema fixtures, and generated dossiers were corrected to tonic
D in `4899687`.

## Source acquisition and authority rules

Every authority file is hash-pinned in
`data/provenance/source-manifest.json`. The first-edition Wq 48 and Clementi
files were independently downloaded twice and were byte-identical. DCML
`mozart_piano_sonatas` v2.3 is pinned to commit
`5337257a5318711e6302cfe85c3f1a6ade3c6271`, with per-file hashes.

IMSLP scans were acquired through MediaWiki metadata and mirror file URLs when
the main image host presented a CAPTCHA. Benda's 1757 *Sei sonate* was obtained
from SLUB Dresden and superseded the 1954 MAB score as content authority.

The hierarchy used in this scan phase was strict:

1. first/early edition scan controls notes, rests, accidentals, rhythms,
   barlines, repeats, voltas, dynamics, articulations, and ornaments;
2. an explicitly allowed modern edition may disambiguate a blurred notehead,
   accidental, rest, or duration;
3. expression from the modern edition is excluded unless the same mark is
   independently visible in the authority scan;
4. if neither source nor schema can support a required field without guessing,
   the case stops.

This distinction mattered most for Benda. The MAB editor states that dynamics,
phrasing, fingering, and pedaling were supplied editorially. Those marks could
otherwise directly contaminate the experiment's rhetorical-emphasis cue.

## Protocol constraints applied in this phase

The controlling documents were reread before transcription:

- `PREREGISTRATION.md` for evidence construction and tonic-D masking;
- `data/provenance/EXTRACTION_PROTOCOL.md` for schema 3.0.0, fixed windows,
  exact durations, canonical IDs, voice mapping, and validation;
- `data/provenance/CONCORDANCE.md` for verified coordinates and open items;
- `data/provenance/identity-key.json` for opaque case IDs;
- `data/cases/CASE-DZWT.json` for the exact dossier shape.

The four fixed windows are opening W1 (eight complete measures plus an
optional `-1` pickup), W2 (six complete pre-candidate measures), W3 (candidate
measure plus five), and W4 (the next six). Candidate onset is exact rational
quarter-note time. Repeats are not unfolded; every written volta is counted
once. A required window containing an unsupported notation construct is
excluded rather than shortened or simplified.

## Reproducible transcription architecture

### Why the large JSON was not hand-authored

The model-facing dossiers contain thousands of repeated structural fields and
canonical IDs. Editing them directly would make transposition and regeneration
claims unauditable. The scan transcription therefore has three layers:

1. a compact operator source in the original key;
2. a deterministic compiler that builds schema 3.0.0 in tonic D;
3. a deterministic reverse-renderer that turns the dossier back into a flat
   event table for scan comparison.

The completed compact sources are:

- `data/provenance/transcriptions/CASE-6U43.source.json`;
- `data/provenance/transcriptions/CASE-8JQJ.source.json`.

No `CASE-Z3F9.source.json` exists because the stop occurred before encoding.

### Compact source notation

The operator format has its own `operator_schema_version: 1.0.0`. Each source
stores authority coordinates, original tonic/mode/meter/key signature,
anacrusis decision, candidate, fixed source windows, a physical movement
timeline, and only the selected measures' notation.

Events use short arrays in the original key:

- note: `["n", onset, duration, voice, [pitches], options?]`;
- rest: `["r", onset, duration, voice, options?]`;
- fixed dynamic: `["d", onset, voice, value]`;
- graphical hairpin state: `["h", onset, voice, value]`.

Onsets and durations are integers or fraction strings in quarter-note units.
The compiler expands chords into pitch events, reduces every rational, sorts
canonically, and assigns IDs only after sorting.

### Compiler behavior

`scripts/compile-transcription.mjs`:

- ports `transposition_for_tonic` and `transpose_pitch` from
  `scripts/lib/extract-dcml-mozart.py`;
- selects the preregistered chromatic interval in -5 through +6 semitones and
  the same-direction diatonic displacement that maps the source tonic letter
  to D;
- applies one interval to every note while preserving diatonic spelling;
- transposes the notated key signature;
- expands and canonically orders events and directions;
- assigns `E001...`, `EV0001...`, and `DR0001...` in canonical traversal
  order;
- computes elapsed and total second-part time from the physical written
  timeline, counting each written volta once and never unfolding repeats;
- adds the exact candidate onset to elapsed time;
- validates the compiled object before writing `data/cases/CASE-*.json`;
- supports `--check`, which compares a fresh in-memory result byte-for-byte
  with the committed dossier.

This architecture makes the dossier a build artifact while preserving the
human musical decisions in compact provenance.

### Reverse event table

`scripts/render-case-table.mjs` emits one TSV row for every measure, note,
rest, and direction, with exact rational onset/duration, normalized pitch,
voice, tie, grace status, articulations, ornaments, barlines, key signature,
and volta. `--check` proves that the committed table is reproducible from the
dossier.

The reverse table is not a score engraving and cannot show beaming or layout.
Its purpose is more basic and testable: every encoded event can be traversed
in source order and compared against the corresponding scan bar.

## CASE-6U43: Wq 48/3/iii

### Concordance and movement arithmetic

The authority is the 1742 print on PDF pages 16-17 / plates 13-14. The opening
is a complete 6/8 measure with an onset-zero note and full lower-staff rest; no
pickup was found.

The exposition has 29 measures. The repeat ends m. 29 and part 2 starts m. 30;
the apparent `a)`/`b)` labels in Nagel are ossia references rather than
voltas. Manual traversal yields 44 measures on the first score page and 34 on
the second, for an exact final measure number of 78. The second page's systems
contain 7 + 6 + 6 + 6 + 5 + 4 measures.

The candidate is m. 51 at onset zero. The second part contains m. 30 through
m. 78: 49 bars at 3 quarter notes = 147 qn. M. 51 follows 21 second-part bars:
63 qn elapsed.

Windows are W1 1-8, W2 45-50, W3 51-56, and W4 57-62.

### Transcription decisions

The Nagel and Complete Works scores were consulted only where the first print
was hard to read. All expression arrays were checked in the 1742 plate. No
printed dynamics or articulations occur in the selected windows. One trill at
m. 49 is visible in the authority print and was retained.

Chromatic spellings such as B-sharp, F-double-sharp, and E-sharp were preserved
instead of being simplified. A triplet division in m. 50 begins at 5/3 qn;
simultaneous upper-staff layers are represented as overlapping `V01` events
rather than an inferred third voice.

The movement-wide map is upper staff/layers -> `V01`, lower staff/layers ->
`V02`. Original E major maps to D major by -2 chromatic semitones and -1
diatonic step; four sharps map to two.

### Output profile and hashes

- 26 evidence measures;
- 243 events: 198 notes and 45 rests;
- 0 directions, 1 ornament, 12 non-`none` tie endpoints;
- dossier SHA-256:
  `6c2f30f4545df8fd5e10b41b9f8e64383e4377153ab64d05e62ce58f1af68d07`;
- compact source SHA-256:
  `9abb61acacf5cebee61b39b7bbc398923741269118c5b6f154ffc77d94167d7c`;
- reverse table SHA-256:
  `1a2730422e9a9b2905d198106d9ef7a8c9eb5ed48a0bf21c324c276a39010fee`.

The full bar-level decision record is
`data/provenance/transcriptions/CASE-6U43.corrections.md`; the machine-readable
summary is `data/provenance/audits/CASE-6U43.audit.json`.

## CASE-8JQJ: Benda Sonata No. 2/iii

### Volta mapping and movement arithmetic

The authority is the 1757 SLUB print, PDF pages 18-19 / plates 11-12. The
opening measure begins with a downbeat rest and has no pickup.

Conventional m. 26 has two written exposition endings, and conventional m. 72
has two written final endings. The physical score traversal used for exact
time is:

`1-25, 26a, 26b, 27-71, 72a, 72b`.

This is 74 written bars while retaining conventional numbering through m. 72.
Part 2 begins at m. 27 and contains 45 single bars through m. 71 plus both m.
72 endings: 47 bars = 141 qn. Candidate m. 51 follows mm. 27-50, 24 bars = 72
qn. Candidate onset is zero.

Windows are W1 1-8, W2 45-50, W3 51-56, and W4 57-62. W2 crosses from plate
11 to plate 12; candidate m. 51 begins plate 12 system 2.

### Expression-source firewall

Only three first-edition dynamics occur in the selected windows:

- m. 49: `f` at onset 1;
- m. 50: `p` at onset 2;
- m. 51: anticipatory `f` at onset 1/2 during the opening rest.

Every other MAB dynamic, hairpin, phrase, fingering, accent, and pedal mark was
excluded. Empty expression arrays mean verified absence in the 1757 print.

### Reverse-audit corrections

The Benda reverse pass materially changed the source and is part of the audit
trail, not an unreported cleanup.

Early scratch crops named as if they were individual measures were actually
fixed-width strips. Their measure labels were four bars late around the plate
12 system break. The glyph readings themselves were sound, but the first
source version placed the three dynamics at mm. 53-55. Remapping the system by
paired barlines and musical content moved them to mm. 49-51.

The same bad crop map produced a suspected missing rest at m. 52. Correctly
located, the bar contains a half-note lower chord and no separately printed
final-quarter rest, so no rest was added there.

A separate full-bar enlargement of m. 50 resolved two printed lower-staff
rests and the lower pitch of a final split-staff chord. These were added as
`V02` while the low upper-staff layer remained `V01`. This preserves printed
staff mapping rather than inferring hands.

The SLUB PDF embeds a 1000 x 707 JPEG. The pinned IIIF service reports the same
maximum size, so higher rendering DPI only enlarges pixels. MAB settled
notehead/rest shapes, after which every accepted event and each of the three
dynamics was rechecked in the first print.

### Transposition, output profile, and hashes

Original G major maps to D major by -5 chromatic semitones and -3 diatonic
steps; one sharp maps to two. The fixed voice map is upper staff/layers ->
`V01`, lower staff/layers -> `V02`.

- 26 evidence measures;
- 251 events: 236 notes and 15 rests;
- 3 directions, 8 ornaments, 15 non-`none` tie endpoints;
- dossier SHA-256:
  `5bf1fe6d39a730f697e8bee06156eed76b7262069e704d24bd8fd6fb6c01b945`;
- compact source SHA-256:
  `30f4d5fe6fe758a661760a5b368fa383c8b7026be0a63610fd254ce6caaecafa`;
- reverse table SHA-256:
  `6ac3986a74beeb68d9663e51841e9a72c36d8cec4c8bf054e0d92495e3648c87`.

The full decision and correction record is
`data/provenance/transcriptions/CASE-8JQJ.corrections.md`; the machine-readable
summary is `data/provenance/audits/CASE-8JQJ.audit.json`.

## CASE-Z3F9: Clementi Op. 10 No. 3/i

### Resolved evidence before encoding

The BnF/Longman & Broderip scan has two flats. The opening bass establishes
B-flat and the exposition repeat closes on a B-flat-major tonic sonority, so
the movement is B-flat major rather than G minor. The conflicting catalogue
description concerns a different Artaria/op. 9 publication lineage.

Four semiquavers precede the first complete common-time bar. They total one
quarter note and would be W1 measure `-1`; complete mm. 1-8 would follow.

Plate 13 contains all 50 first-part measures and ends with the repeat plus
`Volti`. Plate 14 begins m. 51 and its systems contain 10 + 8 + 10 + 9 + 9
measures. System 3 therefore starts at m. 69, where the opening thematic
material returns in the subdominant region. The proposed candidate and onset
zero were confirmed.

The mandatory windows would have been W2 63-68, W3 69-74, and W4 75-80. A
full traversal gave a provisional total of 124 measures (50 + 46 + 28), but no
duration rational was promoted because compilation stopped and the total did
not receive a second arithmetic pass.

### Why the case stopped

M. 72, inside mandatory W3, contains clearly printed textual `dimi:`/`dim.`.
It is not a drawn hairpin.

Schema 3.0.0 has fixed dynamic levels and graphical hairpin states, including
`diminuendo_start`, `diminuendo_continue`, and `diminuendo_stop`. It has no
typed value for a textual gradual-dynamic instruction. Mapping the text to a
hairpin changes the source's notational type. Omitting it contradicts the
dossier's `dynamics: complete` claim. Adding the literal text violates the
protocol's prohibition on arbitrary strings and identity-bearing prose.

`EXTRACTION_PROTOCOL.md` requires exclusion if a required window contains a
construct the schema cannot represent without loss. Work therefore stopped
before a compact source, dossier, reverse table, or completed-case audit was
created. The blocker is retained in `CONCORDANCE.md`, the source manifest, and
`CASE-Z3F9.corrections.md`.

Torricella-1783 concordance is **NOT PERFORMED** because no Torricella source is
on disk. Later witnesses explored in scratch space were orientation aids only
and did not supersede the BnF authority.

## Visual, counting, and OMR methods

### Rendering and crop workflow

Authority pages and systems were rendered into gitignored `tmp/` workspaces.
PyMuPDF-based high-DPI renders were used during the session, followed by
ImageMagick 7.1.2-25 for cropping, contrast adjustment, montage, and
pixel-preserving enlargement. The transient PyMuPDF package version was not
captured; that is a reproducibility blemish in the scratch workflow, although
the pinned source files and committed transcription artifacts are sufficient
to regenerate the dossiers.

### Barline detection attempts

Counting measures was the recurring mechanical risk. The sequence of methods
was:

1. full-page visual counting, rejected as too prone to +/-1 errors;
2. column-density detection, rejected because inter-staff whitespace and note
   stems obscure the signal;
3. longest vertical-run detection, useful on modern clean engravings;
4. staff-paired vertical candidates for early prints, useful only as anchors
   because independent staff barlines create false positives;
5. bar-by-bar transcription and musical-content matching, used for final
   numbering.

Three retained helpers in `data/provenance/tools/` record that evolution:
`detect-barlines.py`, `detect-verticals.py`, and
`detect-paired-verticals.py`.

### OMR

Audiveris 5.11.0 was run on full pages, modern editions, isolated systems, and
stitched staff pairs. `data/provenance/tools/musicxml-table.py` converted its
MusicXML into compact event tables.

OMR was useful for locating passages and reading modern noteheads, but it was
not accepted uncritically. Observed failures included missed barlines, merged
adjacent measures, split systems, octave/clef errors, wrong tuplet durations,
and unstable recognition on the Clementi engraving. The Benda m. 52 OMR result,
for example, merged material past the authority barline. The primary scan
always controlled final measure boundaries and expression.

## Validation against EXTRACTION_PROTOCOL steps 1-5

### Step 1: authoritative source comparison

Each of the 26 selected measures in each completed case was checked in source
order. Modern references were consulted only under the declared legibility
policy. Hard spots and every substantive decision are recorded in the two
completed correction logs.

### Step 2: regeneration

The compact sources regenerate the committed dossiers. The final checks are:

```sh
node scripts/compile-transcription.mjs --check
```

Both `CASE-6U43` and `CASE-8JQJ` report reproducible.

### Step 3: reverse rendering

The committed TSVs were generated and checked with:

```sh
node scripts/render-case-table.mjs --case CASE-6U43 --check
node scripts/render-case-table.mjs --case CASE-8JQJ --check
```

The Benda reverse pass found and corrected the crop displacement and m. 50
lower-staff events. Both corrected tables then received a second scan pass.

### Step 4: invariants and exact arithmetic

For each completed dossier, the audit records selected measure, note, rest,
direction, and ornament counts; original and normalized key signatures;
chromatic and diatonic displacement; fixed voice mapping; candidate onset; and
exact elapsed/total time. `scripts/validate-case.mjs` reports 26 valid evidence
measures for both.

Compiler and renderer hashes shared by both audits are:

- compiler:
  `73190e199337e0f697bbe190f40b578c949b2cc1d6cb95f0fc083848c94d2896`;
- reverse renderer:
  `2a6136058b84128b5ebb391fe25388c990b0b270af56663b5ecee758a118a5ce`.

### Step 5: identity scan

The case files were checked for source titles, composer/work strings, source
filenames and URLs, bibliographic metadata, original tonics, source measure
coordinates, and arbitrary text. Only opaque case IDs, tonic D, common schema
enums, window IDs, rational values, pitches, and canonical structural IDs are
present.

The identity key, source maps, measure numbers, correction logs, and audit
configuration remain under `data/provenance/`.

## Test and command record

The final verification set is:

```sh
node scripts/compile-transcription.mjs --check
node scripts/render-case-table.mjs --case CASE-6U43 --check
node scripts/render-case-table.mjs --case CASE-8JQJ --check
node scripts/validate-case.mjs data/cases/CASE-6U43.json
node scripts/validate-case.mjs data/cases/CASE-8JQJ.json
node scripts/test-analyzer.mjs
node scripts/test-case-validator.mjs
node scripts/test-extract-dcml-mozart.mjs
node scripts/test-reliability.mjs
node scripts/test-response-validator.mjs
node scripts/test-runner.mjs
```

Node was v24.8.0. The six existing suites and both dossier validators pass in
the final worktree. No test was weakened or skipped to admit the scan cases.

## Artifact inventory

Committed regeneration and audit artifacts from this phase are:

- `scripts/compile-transcription.mjs`;
- `scripts/render-case-table.mjs`;
- two compact `*.source.json` files;
- two generated schema-3.0.0 dossiers;
- two reverse-rendered TSVs;
- three correction logs, including the stopped case;
- two completed-case audit JSONs;
- updated source manifest and concordance;
- retained scratch-analysis helpers under `data/provenance/tools/`;
- this supplement.

Gitignored `tmp/` contains page renders, system crops, experimental OMR books,
MusicXML, and later-edition orientation material. Those scratch files are not
required to reproduce the model-facing JSON from the committed compact
sources, but their methods and consequential outcomes are recorded here and in
the correction logs.

The implementation landed first in commit `365a490` after the earlier tooling
and preliminary supplement commit `09a4f61`. The final provenance corrections,
audits, and expanded supplement are committed separately so the correction
history is visible.

## What was intentionally not done

- No unsupported Clementi direction was guessed, dropped, or recast as a
  hairpin.
- No MAB-only or Nagel-only expression was encoded.
- No repeat was unfolded in second-part arithmetic.
- No source identity was added to a model-facing case file.
- No status in `data/manifest.json` was advanced.
- No run matrix, prompt, adapter, or output was changed.
- No model was called and no result was collected.
- No claim of independent replication is made.

## Remaining limitations and next gate

The two completed scan dossiers are reproducible encodings, not critical
editions. Schema 3.0.0 intentionally omits clefs, beaming, slurs, tempo text,
layout, and display-only accidental status. Staff-local layers collapse into
movement-wide staff voice IDs. Those omissions are uniform and documented,
but they still constrain what a model can infer.

The greatest empirical limitation is the single transcription operator. The
reverse pass caught meaningful Benda errors, demonstrating why the audit was
necessary, but it is not a substitute for a blind second transcription.

The Clementi exclusion leaves the planned six-case corpus incomplete. It may
be admitted only after an explicit schema/protocol revision that represents
textual gradual dynamics (or changes the completeness claim), followed by a
new freeze. It must not be patched after collection begins.

The next authorized phase is not model collection. It is a human review of
this five-dossier state and the schema blocker, followed by the preregistered
freeze decision: model families and adapters, token-limit checks, manifest
hashes, schedule lock, and tag. Only after those gates may the 108 scheduled
calls begin.
