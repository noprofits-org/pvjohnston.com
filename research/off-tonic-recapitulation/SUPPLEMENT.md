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

The scan task initially requested three schema-3.0.0 dossiers. The protocol's
stop rule allowed only two to be produced at that stage. A subsequent,
pre-collection revision to schema 3.1.0 added a closed type for printed textual
gradual dynamics, resolving one Clementi notation blocker without recasting
text as a graphical hairpin. Clementi still failed the required event-level
verification gate, so a pinned symbolic Mozart case replaced it before any
outcome call:

| Case | Authority | Result | Exact second-part time |
| --- | --- | --- | --- |
| `CASE-6U43` | C. P. E. Bach Wq 48/3/iii, 1742 first edition | completed, regenerated, reverse-checked, validated | elapsed 63 qn; total 147 qn |
| `CASE-8JQJ` | Benda Sonata No. 2/iii, 1757 first edition | completed, regenerated, reverse-checked, validated | elapsed 72 qn; total 141 qn |
| `CASE-Z3F9` | Clementi Op. 10 No. 3/i, BnF early print | structure and coordinates reconciled; exact event transcription still awaiting an authority-based double pass | elapsed 99 qn; total 296 qn; not promoted to a dossier |
| `CASE-D09B` | Mozart K. 576/i, pinned DCML/NMA | completed, regenerated, reverse-checked, validated; admitted as the sixth target | elapsed `241/2` qn; total `613/2` qn |

The resulting pre-freeze corpus contains six validated dossiers: four extracted
from pinned DCML sources and two completed scan dossiers. The transparent
balance is two focal cases, three ordinary tonic-return controls, and one clear
off-tonic control. Clementi remains a source-linked future replication with a
fully documented coordinate correction and open event-level verification gate;
it is neither guessed into the corpus nor silently discarded.

No outcome-producing call on a real dossier was made during this
scan-construction phase. Model agents did perform protocol, source, and
transcription work as documented below. Later, separately recorded transport
and response-schema preflights contacted candidate systems using only a
fictional dossier and retained no prompt or response bodies. Collection
manifests, run scheduling, and real-case outputs belong to the later collection
phase. The collection freeze still happens before any such output call.

### Development model matrix and fictional preflights

The later development matrix selected three fixed CLI systems across two
provider families: OpenAI `gpt-5.6-sol` (frontier), Anthropic
`claude-fable-5` (frontier), and OpenAI `gpt-5.5` (active
prior-generation). This is a partial 2x2 provider-by-generation-role panel,
with no Anthropic prior-generation cell. Pooled three-system summaries
therefore give OpenAI two of three system positions; named within-provider and
cross-provider pairs must remain visible, and generation-role comparisons are
descriptive rather than causal.

All three adapters passed both task-shaped schema preflights using only the
fictional `CASE-SYN0` dossier. Anthropic authentication was working for its
successful preflight. The retained receipts contain hashes, byte counts,
timing, validation status, and protocol metadata but no prompt, response, or
stderr bodies. No real dossier was used and no experiment outcome was viewed.
Gemini was dropped before any Gemini model request because the available
authentication route required an explicit Google Cloud project; collection had
not begun, so this was a pre-freeze design change rather than a mid-collection
substitution.

## People and agent roles

Peter Johnston is the human operator. Two supervised agent roles contributed
to the repository on 2026-07-18:

- an operator-session agent (Claude) acquired and pinned sources, repaired the
  design after adversarial review, established initial concordances, and built
  the first three DCML/Mozart dossiers;
- a researcher agent (OpenAI Codex) designed the v2 protocol and software, then
  performed the present scan transcription, compiler, correction logs, reverse
  rendering, audits, and the source-gated K. 576 replacement extraction.

These are not independent raters. The scan dossiers had one transcription
operator. Modern editions and OMR provided legibility checks, not independent
extractions. The absence of a music-theory-trained human event pass is carried as a
limitation in each audit rather than obscured by describing agent sessions as
independent evidence.

The OpenAI and Anthropic families overlap with every tested provider family.
Fresh, noninteractive outcome calls will not receive construction
transcripts, source identities, or tool access, but that context isolation does
not create evaluator independence. Protocol co-development by every tested
provider family is a design limitation to be carried into the final Methods and
Discussion.

## Design history

### Superseded v1

An earlier experiment asked whether a six-cue model rubric supported a
continuum of off-tonic recapitulation. That design was abandoned before corpus
construction because every possible result had a deflationary interpretation:
training-data familiarity, model dependence, and encoding artifacts could not
be separated from the proposed music-theoretical claim.

### v2 reliability redesign

The researcher agent reframed the pilot around questions a six-case sample can
answer: same-input test-retest stability within a system, cross-system
reliability, and elicited identification of identity-withheld repertoire.
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
2. Common normalization changed from C to D. The original six-case selection
   displaced every source, including the positive recognition control. The
   later pre-freeze K. 576 replacement is itself in D and therefore receives an
   explicitly disclosed identity transform; five cases remain displaced.
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
- `data/provenance/EXTRACTION_PROTOCOL.md` for schema 3.1.0, fixed windows,
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
2. a deterministic compiler that builds schema 3.1.0 in tonic D;
3. a deterministic reverse-renderer that turns the dossier back into a flat
   event table for scan comparison.

The completed compact sources are:

- `data/provenance/transcriptions/CASE-6U43.source.json`;
- `data/provenance/transcriptions/CASE-8JQJ.source.json`.

No `CASE-Z3F9.source.json` exists because the stop occurred before encoding;
the case is retained for a future replication rather than the initial run.

### Compact source notation

The operator format has its own `operator_schema_version: 1.0.0`. Each source
stores authority coordinates, original tonic/mode/meter/key signature,
anacrusis decision, candidate, fixed source windows, a physical movement
timeline, and only the selected measures' notation.

Events use short arrays in the original key:

- note: `["n", onset, duration, voice, [pitches], options?]`;
- rest: `["r", onset, duration, voice, options?]`;
- fixed dynamic: `["d", onset, voice, value]`;
- graphical hairpin state: `["h", onset, voice, value]`;
- textual gradual dynamic: `["t", onset, voice, value]`.

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
  `8cb1446f4d625fc1203608e80602a2f5b733e43db3b439dcedd072ca98c4fa91`;
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
  `135484af663bb92f279bed6e26bc9ff03db2607391021e6b0d5ef7444754df1d`;
- compact source SHA-256:
  `30f4d5fe6fe758a661760a5b368fa383c8b7026be0a63610fd254ce6caaecafa`;
- reverse table SHA-256:
  `6ac3986a74beeb68d9663e51841e9a72c36d8cec4c8bf054e0d92495e3648c87`.

The full decision and correction record is
`data/provenance/transcriptions/CASE-8JQJ.corrections.md`; the machine-readable
summary is `data/provenance/audits/CASE-8JQJ.audit.json`.

## CASE-D09B: Mozart K. 576/i

### Selection and coordinate reconciliation

K. 576/i replaced the stopped Clementi case before collection because its
pinned symbolic source passes the same deterministic extraction gate as the
other Mozart dossiers. The case is an ordinary tonic-return target, not a
positive control. The PTNA work analysis places the recapitulation and return
of the principal theme at printed m. 99. The NMA score confirms that location:
printed pp. 148 and 151 show the opening and return, and the critical-report
footnote on p. 148 explicitly pairs opening mm. 1--4 with recapitulation
mm. 99--102.

The DCML timeline includes an opening eighth-note pickup as `mc=1`, so printed
mm. 1--8 map to `mc=2-9`. Printed m. 58 is split at the repeat boundary:
`mc=59` contains its first five eighth notes and `mc=60` its final eighth note
on the second-part side. The second part therefore starts at `mc=60`, while
printed m. 99 maps to candidate `mc=101` at onset 0. The fixed evidence windows
are W1 `mc=1-9`, W2 `mc=95-100` (printed mm. 93--98), W3 `mc=101-106`
(printed mm. 99--104), and W4 `mc=107-112` (printed mm. 105--110). Exact
second-part timing is `241/2` quarter notes elapsed at the candidate and
`613/2` quarter notes total.

### Extraction, normalization, and leakage asymmetry

The deterministic extraction selected 321 events, including 29 rests, and
three fixed dynamic directions. Visual checks locate those dynamics at the
opening pickup, printed m. 97 onset 0, and printed m. 98 onset `5/2`; no source
correction or schema-unsupported construct was required. The dossier validates
against schema 3.1.0 and its reverse-rendered table reproduces exactly.

K. 576 begins in D major. Common-tonic D normalization therefore applies the
identity transform: zero chromatic semitones and zero diatonic steps. Exact
pitch classes and register survive, unlike in the other five dossiers. This
weaker masking is a disclosed case-specific leakage risk, but the strict target
recognition rules are unchanged. K. 576 is not a second recognition control,
and its inclusion supports no causal claim about masking or transposition.

- source commit: `5337257a5318711e6302cfe85c3f1a6ade3c6271`;
- NMA PDF SHA-256:
  `fd165fcf84905700c23947bc5fc58b7b61275b42cfb2e7068cbc2109401800d6`;
- extraction-config SHA-256:
  `1a182b9cf06478a3b8220d369c965fb13c866228007e09ba30a140e3d583a0ac`;
- dossier SHA-256:
  `5dbb6b1bc7e4b300757a67c4c03fae5afe603f317b8a4b13fb813b0aac4b27f5`;
- audit SHA-256:
  `cd01d23584415c084d49b8e4384f68c494b95dee0796acadb43a0b2369cf5e5f`;
- reverse table SHA-256:
  `731d97f4eee4696034584f6373eb3cc60d8aed5bba3e648b2daf95b24879d1bf`.

Its machine-readable audit remains `generated_unverified` until the planned
expert-readable review and collection freeze; machine validation does not
constitute independent musicological verification.

## Deferred CASE-Z3F9 replication: Clementi Op. 10 No. 3/i

### Reconciled structure and source chain

The BnF/Longman & Broderip scan has two flats. The opening bass establishes
B-flat and the exposition repeat closes on a B-flat-major tonic sonority, so
the movement is B-flat major rather than G minor. The conflicting catalogue
description concerns a different Artaria/op. 9 publication lineage.

Four semiquavers precede the first complete common-time bar. They total one
quarter note and would be W1 measure `-1`; complete mm. 1-8 would follow.

The first pass incorrectly counted 50 measures on plate 13. A fresh
staff-paired traversal gives 8 + 10 + 9 + 9 + 9 = 45, so the exposition repeat
closes m. 45 and part 2 begins at m. 46. The original `return-bars/m69.png`
through `m80.png` scratch labels are consequently five measures high: they
show actual mm. 64-75.

Andrew Brownell's 2010 thesis reproduces Op. 10 No. 3/i, mm. 67-74, with the
caption “Copied from Torricella, Vienna, 1783.” That partial, copied excerpt is
not a complete Torricella authority, but it supplies an independent coordinate
witness: textual `dim.`/`dimi:` at m. 67, `pp` at m. 68, a cadential/rest bar
at m. 69, the thematic pickup at m. 70 onset 3 qn, and the first full thematic
bar at m. 71 all match the BnF sequence. This comparison exposed the five-bar
offset.

Greenberg does not analyze this Clementi movement as a worked case. Its
case-specific scholarly connection is Brownell, and the eventual post must not
attribute Brownell's passage analysis or Torricella-derived example to
Greenberg.

The corrected windows are W2 64-69, W3 70-75, and W4 76-81. A complete second
traversal gives 119 measures (45 + 46 + 28). Part 2, mm. 46-119, therefore
contains 74 common-time bars = 296 qn. The candidate follows 24 full part-2
bars plus three beats, so elapsed time is 99 qn.

### Schema correction and remaining stop

Under schema 3.0.0, the original stop was required: the printed textual
`dim.`/`dimi:` at actual m. 67 could neither be mapped to a graphical hairpin
nor omitted without changing or losing evidence. Schema 3.1.0 now adds the
closed `textual_gradual_dynamic` type with normalized `crescendo` and
`diminuendo` values. It preserves notational medium without exposing source
spelling or implying an endpoint or target dynamic.

That revision removes the schema blocker, but it does not make the provisional
OMR transcription trustworthy. Later Artaria, Knorr, and Litolff witnesses are
legibility aids only; observed OMR errors include merged measures, missed
barlines, and octave or staff displacement. Only actual mm. 69-71 have
converged to JSON-safe events. The other 24 evidence measures retain unresolved
octave, layer, tie, rest, or BnF-mark checks and need a bar-by-bar double pass
against the BnF authority. Therefore no compact source, dossier, reverse table,
or completed-case audit has been promoted. The precise open gate is retained
in `CONCORDANCE.md`, the source manifest, and `CASE-Z3F9.corrections.md`.

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
  `6fcef9c228180f7eea2b77647038ef01446ea83fa4d1f62f2064e47d22c26df8`;
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
node scripts/compile-transcription.mjs --case CASE-6U43 --check
node scripts/compile-transcription.mjs --case CASE-8JQJ --check
node scripts/render-case-table.mjs --case CASE-6U43 --check
node scripts/render-case-table.mjs --case CASE-8JQJ --check
node scripts/render-case-table.mjs --case CASE-D09B --check
node scripts/render-case-table.mjs --case CASE-DZWT --check
node scripts/render-case-table.mjs --case CASE-Q2R9 --check
node scripts/render-case-table.mjs --case CASE-VT57 --check
node scripts/validate-case.mjs data/cases/CASE-6U43.json
node scripts/validate-case.mjs data/cases/CASE-8JQJ.json
node scripts/validate-case.mjs data/cases/CASE-D09B.json
node scripts/validate-case.mjs data/cases/CASE-DZWT.json
node scripts/validate-case.mjs data/cases/CASE-Q2R9.json
node scripts/validate-case.mjs data/cases/CASE-VT57.json
node scripts/test-analyzer.mjs
node scripts/test-case-validator.mjs
node scripts/test-collection-orchestrator.mjs
node scripts/test-extract-dcml-mozart.mjs
node scripts/test-reliability.mjs
node scripts/test-response-validator.mjs
node scripts/test-runner.mjs
node scripts/test-synthetic-preflight.mjs
```

Node was v24.8.0. All eight suites, all six dossier validators, both scan
compilers, and all six reverse-render checks pass in the final worktree. No
test was weakened or skipped to admit a case.

## Artifact inventory

Committed regeneration and audit artifacts from this phase are:

- `scripts/compile-transcription.mjs`;
- `scripts/render-case-table.mjs`;
- two compact `*.source.json` files;
- two generated schema-3.1.0 scan dossiers;
- two reverse-rendered TSVs;
- three correction logs, including the stopped case;
- two completed-case audit JSONs;
- the K. 576 extraction configuration, generated dossier, audit JSON, and
  reverse-rendered TSV;
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

- No Clementi event was guessed or promoted, and the printed textual
  diminuendo was neither dropped nor recast as a hairpin.
- No MAB-only or Nagel-only expression was encoded.
- No repeat was unfolded in second-part arithmetic.
- No source identity was added to a model-facing case file.
- No status in `data/manifest.json` was advanced.
- No run matrix, prompt, adapter, or output change was part of this scan phase.
- No model was called and no result was collected in this scan phase.
- No claim of independent replication is made.

## Remaining limitations and freeze gate

The two completed scan dossiers are reproducible encodings, not critical
editions. Schema 3.1.0 intentionally omits clefs, beaming, slurs, tempo text,
layout, and display-only accidental status. Staff-local layers collapse into
movement-wide staff voice IDs. Those omissions are uniform and documented,
but they still constrain what a model can infer.

The greatest empirical limitation is the single agent transcription pass. The
reverse pass caught meaningful Benda errors, demonstrating why the audit was
necessary, but it is not a substitute for a music-theory-trained human or a
blind second transcription.

The initial launch corpus is now complete at six dossiers because K. 576
replaced the unencoded Clementi case before model collection. This preserves the reliability
design but changes the planned 2+2+2 role balance to a disclosed 2+3+1 balance.
Clementi remains a future replication: admission still requires an
authority-based event double pass, deterministic compilation, reverse
comparison, validation, and a separate pre-collection freeze. It must not be
patched into the initial collection after collection begins.

The preregistered freeze decision was recorded at 2026-07-19T17:54:14Z after
expert-readable review of the six-dossier state and deferred Clementi record,
exact model-system and adapter checks, token-limit checks, manifest hashing,
and generation of the seeded 108-call schedule. The 41-file collection lock
was created and verified at 2026-07-19T17:56:35.630Z. No real-case output call
occurred before either timestamp. The Git commit containing this record and
lock is the remaining provenance boundary: calls may begin only from that
committed state and after the planned collection window opens.
