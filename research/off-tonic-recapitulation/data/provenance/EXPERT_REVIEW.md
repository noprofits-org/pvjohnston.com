# Expert review packet: unverified pilot dossiers

Status: **pre-collection review packet; no music-theory expert has verified
these dossiers**. Prepared 2026-07-19 by a Codex research agent under operator
supervision.

This packet is designed so that a later reader with music-theory training can
audit all six launch dossiers and the deferred, incomplete Clementi concordance
without trusting the experiment's labels or extraction agents. It separates
mechanical facts from interpretive judgments and records material source
questions that must be resolved or disclosed before the collection lock is
frozen.

## What this packet does and does not establish

Mechanically established:

- each completed dossier validates against schema 3.1.0 and its
  semantic invariants;
- each Mozart dossier regenerates byte-for-byte from the pinned DCML commit
  and its strict operator configuration, while the C. P. E. Bach and Benda
  dossiers regenerate byte-for-byte from their retained compact
  transcriptions;
- the pinned source hashes, measure-count coordinates, exact candidate onset,
  voice map, transposition, and elapsed/total second-part durations are exposed
  in the corresponding audit JSON;
- a retained, deterministic reverse event table exists for each launch case and is
  reproducible from the model-facing dossier; and
- the authority-score pages containing every selected measure have been
  located.

Not established:

- that the candidate is correctly classified as a tonic or off-tonic formal
  return;
- that the fixed windows are the best music-theoretical evidence for the
  question;
- line-by-line agreement between every encoded event and its authority score;
- for the Mozart cases, completeness relative to the NMA where the pinned DCML
  symbolic source differs from it; or
- independent replication, expert agreement, or musicological ground truth.

Model agents from the OpenAI and Anthropic families contributed to protocol
construction, source acquisition, dossier construction, transcription, or
read-only audit. OpenAI Codex performed the event-level scan transcription and
reverse comparison described below. Every tested provider family is therefore
represented in protocol and evidence development. Fresh, tools-disabled outcome contexts do
not receive the construction transcripts, but the overlap means the evaluation
is not independent of protocol development. The matrix contains two OpenAI
systems and one Anthropic system: it is a partial 2x2
provider-by-generation-role panel, pooled results give OpenAI two of three
system positions, and its system and generation comparisons are descriptive,
not causal.

The experiment may therefore describe these as operator-selected anchors and
machine-validated dossiers, not expert-verified examples.

## Pinned sources and evidence paths

The four Mozart cases use DCML's *Annotated Mozart Sonatas*, release v2.3, commit
`5337257a5318711e6302cfe85c3f1a6ade3c6271`. The DCML corpus data are licensed
CC BY-NC-SA 4.0. The corpus says its MuseScore files were corrected to conform
to the Neue Mozart-Ausgabe (NMA) content-wise, not layout-wise.

The visual reference is `pdf/NMA_vol2.pdf` within that pinned repository,
SHA-256
`fd165fcf84905700c23947bc5fc58b7b61275b42cfb2e7068cbc2109401800d6`.
The PDF page numbers below match the printed score-page numbers. The pinned
MuseScore, notes TSV, and measures TSV hashes are in `source-manifest.json` and
each case audit.

The NMA pages visibly bear a 1986 Bärenreiter copyright notice. The review
workflow may inspect the locally pinned file, but the post should publish page
coordinates and hashes rather than reproducing page images unless the right to
do so is separately confirmed. The DCML corpus licence should not be assumed
to cover republication of NMA page images.

`data/sources/dcml/` is an operator-local, ignored source checkout rather than
part of this website repository's Git history. A fresh reviewer must clone the
repository named in `source-manifest.json`, check out the exact commit above,
and verify the listed hashes. Point `DCML_MOZART_ROOT` at that checkout when
running the extractor test if it is stored elsewhere.

The two focal cases were transcribed event by event by an OpenAI Codex research
agent, under human operator supervision, from public-domain first-edition
scans. `CASE-6U43` uses the 1742 first edition of C. P. E. Bach's Wq 48,
PDF pp. 16-17 / engraved plates 13-14, SHA-256
`b9e20b14f79973fedc7f1aa6efacdca7cd3c7d818e711d13fb3dd5d186be68ef`.
`CASE-8JQJ` uses Benda's 1757 *Sei sonate*, PDF pp. 18-19 / engraved plates
11-12, SHA-256
`34aab7ccd253df6585f3afaade5bbafca3f2f72f6ae1b647ca8653f96aced350`.
Modern editions were consulted only for glyph legibility; every admitted note,
rest, ornament, and expression mark was rechecked in the named first print.
The retained `.source.json`, correction log, audit JSON, and reverse table form
the reproducibility record. No music-theory-trained human performed an
event-level transcription or independent verification pass.

For every case, compare these four artifact layers:

1. authority-score page: visual notation and printed measure number;
2. for Mozart, `data/sources/dcml/MS3/WORK.mscx` and the corresponding `notes/`
   and `measures/` TSVs; for C. P. E. Bach and Benda, the retained compact
   `.source.json`: pinned symbolic intermediary in the original pitch;
3. `data/cases/CASE-ID.json`: identity-withheld dossier normalized to tonic D;
4. `data/provenance/transcriptions/CASE-ID.reverse-rendered.tsv`: flat,
   window-ordered rendering of every dossier measure, note, rest, and
   direction.

The reverse tables remain in tonic D. Use the inverse of the disclosed
chromatic and diatonic interval when comparing their pitch spellings with the
authority score; onset, duration, voice, tie, grace, articulation, ornament,
and barline fields require no pitch conversion. For K. 576 the inverse is the
identity transform.

## Case map

| Case | Operator role | Source to common tonic | Candidate | W1 | W2 | W3 | W4 | Visual pages | Current state |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CASE-6U43` / C. P. E. Bach Wq 48/3/iii | ambiguous focal return | E major to D major: -2 chromatic semitones, -1 diatonic step | first-edition m. 51, onset 0 | mm. 1-8 | mm. 45-50 | mm. 51-56 | mm. 57-62 | 1742 print PDF pp. 16-17 / plates 13-14 | Codex agent transcription, regenerated and reverse-checked; no music-theory-trained human event pass |
| `CASE-8JQJ` / Benda 1757 Sonata No. 2/iii | ambiguous focal return | G major to D major: -5 chromatic semitones, -3 diatonic steps | first-edition m. 51, onset 0 | mm. 1-8 | mm. 45-50 | mm. 51-56 | mm. 57-62 | 1757 print PDF pp. 18-19 / plates 11-12 | Codex agent transcription, regenerated and reverse-checked; no music-theory-trained human event pass |
| `CASE-D09B` / K. 576/i | tonic-return anchor | D major to D major: identity transform, 0 chromatic semitones and 0 diatonic steps | NMA m. 99, onset 0; DCML `mc=101` | pickup plus mm. 1-8 (`mc=1-9`) | mm. 93-98 (`mc=95-100`) | mm. 99-104 (`mc=101-106`) | mm. 105-110 (`mc=107-112`) | NMA pp. 148 and 151 | generated, unverified; exact source pitch and register survive normalization |
| `CASE-DZWT` / K. 570/i | tonic-return anchor | B-flat major to D major: +4 chromatic semitones, +2 diatonic steps | NMA m. 133, onset 0; DCML `mc=133` | mm. 1-8 (`mc=1-8`) | mm. 127-132 (`mc=127-132`) | mm. 133-138 (`mc=133-138`) | mm. 139-144 (`mc=139-144`) | NMA pp. 132 and 137 | generated, unverified; two NMA dynamic corrections are explicit |
| `CASE-Q2R9` / K. 333/i | tonic-return anchor | B-flat major to D major: +4 chromatic semitones, +2 diatonic steps | pickup in NMA m. 93 at quarter-note onset 3, leading into m. 94; DCML `mc=95` | pickup `mn=0` plus mm. 1-8 (`mc=1-9`) | mm. 87-92 (`mc=89-94`) | mm. 93-98 (`mc=95-100`) | mm. 99-104 (`mc=101-106`) | NMA pp. 48 and 52 | generated, unverified |
| `CASE-VT57` / K. 545/i | off-tonic-return anchor and identification positive control | C major to D major: +2 chromatic semitones, +1 diatonic step | NMA m. 42, onset 0; DCML `mc=42` | mm. 1-8 (`mc=1-8`) | mm. 36-41 (`mc=36-41`) | mm. 42-47 (`mc=42-47`) | mm. 48-53 (`mc=48-53`) | NMA pp. 122 and 124 | generated, unverified |

For K. 333, `mc` is DCML's continuous measure-count coordinate and `mn` is
the printed/NMA measure number. The opening pickup and a split at the first
ending account for the offset. The dossier's candidate onset is the final
quarter-note beat of NMA m. 93, not the downbeat of m. 94.

K. 576 is the only source already in the common tonic. Its identity transform
preserves exact pitch and register, so identity withholding is weaker for this
target than for the five displaced sources. It remains subject to the same
target-case recognition gates and must not be removed or replaced if a model
identifies it. The pilot makes no causal claim about transposition or masking.

The position covariate uses exact notated time rather than a rounded measure
fraction:

| Case | Second-part boundary | Candidate elapsed / total quarter notes |
| --- | --- | --- |
| `CASE-6U43` | Wq 48/3/iii m. 30, onset 0 | 63 / 147 |
| `CASE-8JQJ` | Benda Sonata No. 2/iii m. 27, onset 0 | 72 / 141 |
| `CASE-D09B` | K. 576 `mc=60`, the final eighth-note continuation of printed m. 58 after the intrameasure repeat boundary | 241/2 / 613/2 |
| `CASE-DZWT` | K. 570 `mc=80`, NMA m. 80 onset 0 (p. 136) | 159 / 390 |
| `CASE-Q2R9` | K. 333 `mc=65`, the one-quarter continuation of printed m. 63 after the repeat boundary (NMA pp. 50-51) | 120 / 408 |
| `CASE-VT57` | K. 545 `mc=29`, NMA m. 29 onset 0 (p. 123) | 52 / 180 |

Each written measure and written volta is counted once; repeats are not
unfolded. The K. 333 split is particularly important: `mc=64` contains the
first three quarter-note beats of printed m. 63 and `mc=65` contains its final
quarter-note beat on the second-part side of the repeat boundary.

The current launch artifacts are bound for expert review by these hashes:

| Case | Dossier SHA-256 | Reverse-table SHA-256 |
| --- | --- | --- |
| `CASE-6U43` | `8cb1446f4d625fc1203608e80602a2f5b733e43db3b439dcedd072ca98c4fa91` | `1a2730422e9a9b2905d198106d9ef7a8c9eb5ed48a0bf21c324c276a39010fee` |
| `CASE-8JQJ` | `135484af663bb92f279bed6e26bc9ff03db2607391021e6b0d5ef7444754df1d` | `6ac3986a74beeb68d9663e51841e9a72c36d8cec4c8bf054e0d92495e3648c87` |
| `CASE-D09B` | `5dbb6b1bc7e4b300757a67c4c03fae5afe603f317b8a4b13fb813b0aac4b27f5` | `731d97f4eee4696034584f6373eb3cc60d8aed5bba3e648b2daf95b24879d1bf` |
| `CASE-DZWT` | `508ba29752932e92772781a975b313f7d1f99b63a603c79e026c51a019aee17c` | `7e9c87c6c60dc1efdf010aa3a3dffe88b26811bd81a52fe0303d184ab595794f` |
| `CASE-Q2R9` | `4901ea3fc205f5d1fac19eb6cd04ee00d98ad4de4fb014e65d5695f1877047cb` | `6cea2e2857e25cebc6e21c2c7b0e34ad55e9fae6e7584bb5e6175c9234fe26c9` |
| `CASE-VT57` | `bce90cdd3869b6db306804cc8fd274f1f1c23ff1f8effa9a5efe82a44ece1118` | `f90605d59eb4278efed531fa8741efbbb51fba170beca2cdfce8b5c5eb65d76d` |

## Deferred Clementi coordinate correction and authority chain

`CASE-Z3F9` retains Clementi, Op. 10 No. 3/i because Brownell directly discusses
its subdominant recapitulation. Greenberg does not work through this movement
as a case study. The earlier internal bar count was not reliable enough to
freeze; the corrected concordance is:

- notation authority: the Longman & Broderip BnF scan, PDF pp. 14-16,
  engraved plates 13-15;
- coordinate-only witness: Brownell thesis Example 3.8, which copies
  Torricella 1783 mm. 67-74; it is not the notation or expression authority;
- movement: B-flat major, common time, with a one-quarter-note opening pickup;
- second part: actual m. 46, onset 0;
- candidate: thematic pickup in actual m. 70 at quarter-note onset 3, with the
  full opening-theme downbeat in m. 71;
- fixed windows: W1 = pickup plus mm. 1-8, W2 = 64-69, W3 = 70-75, and
  W4 = 76-81; and
- exact second-part position: 99 / 296 quarter notes.

The previous provisional candidate m. 69 and its derived window labels are
superseded and must not be cited. The BnF scan remains authoritative for notes,
rests, articulation, ornament, and expression; Brownell's copied,
Torricella-derived excerpt establishes the external measure concordance and
connection to the source literature.
The post should cite Brownell's example and describe the concordance rather
than reproduce that copied excerpt unless its reuse rights are confirmed.

No corrected compact transcription, dossier, reverse table, or completed-case
audit has been promoted. Only actual mm. 69-71 have converged to JSON-safe
events. The other 24 evidence measures retain unresolved octave, layer, tie,
rest, or BnF-mark checks itemized in `CASE-Z3F9.corrections.md`. Do not advance
`CASE-Z3F9` beyond selected-but-unencoded until a complete event double pass
converges and the resulting artifacts match these coordinates and pass the
same source-to-table review required of the other cases.

## K. 570 source-score corrections

The pinned NMA visibly prints `p` at K. 570/i m. 1 (W1) and again at m. 133
(the start of W3). Neither mark is present at those coordinates in the pinned
DCML `MS3/` or `reviewed/` MuseScore data. The experiment now treats the pinned
NMA as the expression authority and repairs those two omissions through the
required, validated `source_score_corrections` array in `K570-1.json`:

- `COR-K570-M001-P`: global `p`, m. 1 onset 0, printed NMA p. 132;
- `COR-K570-M133-P`: global `p`, m. 133 onset 0, printed NMA p. 137.

The extractor verifies the NMA PDF hash, constrains each correction to a
selected source measure and supported typed direction, copies the correction
verbatim into the audit, and emits `DR0001` at W1 m. 0 and `DR0002` at W3 m. 0.
The corrected dossier therefore has two directions and regenerates from the
pinned symbolic source plus its explicit operator correction layer.

This resolves the known machine-representation omission; it does not confer
expert verification. A reviewer should confirm both printed marks, their
placement and scope, and whether this correction protocol is an acceptable
basis for the rhetorical-emphasis cue. The audit remains
`generated_unverified` pending the full source-score review.

No equivalent fixed-dynamic discrepancy was observed on the selected NMA
pages for K. 333, K. 545, or K. 576. K. 576's three encoded `f` directions are
visible at the opening pickup, m. 97 onset 0, and m. 98 onset 5/2. These are
visual triage results, not complete event-by-event verification.

## Representation limits that an expert should evaluate

Schema 3.1.0 retains notes, notated rests, stable voices, meter, key
signatures, supported fixed dynamics, graphical hairpins, typed textual
`crescendo`/`diminuendo` directions, articulations, ornaments, repeats, voltas,
and barlines. It intentionally omits slurs, clefs, beaming, tempo,
display-only accidental status, layout, editorial prose, and arbitrary text
directions outside the fixed enum. Chord-level articulations and ornaments
from the DCML source are copied to every constituent note event.

These choices are not neutral for every rubric item. In particular, omitted
slurs, beaming, tempo, layout, and unsupported free-text expression can affect
judgments of opening-theme correspondence, rhetorical emphasis, continuity, and a
candidate's perceptual salience. The post should describe the six cue scores as
the study's operationalization, not as a published or expert-validated scale.

## Expert checklist

Review each case independently and record `pass`, `fail`, `uncertain`, or
`not_reviewed` in a copy of `EXPERT_REVIEW_TEMPLATE.json`.

### Source and coordinates

- Confirm that the authority-score movement, key, meter, and printed measure
  numbering match the case map.
- Confirm every W1, W2, W3, and W4 boundary and the candidate onset.
- Confirm the notated second-part boundary and the elapsed/total-duration
  arithmetic in the audit JSON; do not unfold repeats.
- For K. 333, explicitly adjudicate the m. 93 beat-four pickup and m. 94
  downbeat rather than treating `mc` as a printed measure number.
- For Clementi, confirm the BnF bar traversal independently, confirm Brownell
  Example 3.8's copied Torricella numbering, and verify the corrected m. 70
  beat-four pickup/m. 71 downbeat rather than the superseded m. 69 label.

### Event fidelity

- Compare every notehead's pitch spelling and octave after reversing the fixed
  transposition.
- Compare onset, written duration, voice/layer, notated rests, grace status,
  ties, ornaments, articulations, key and meter state, repeats, voltas, and
  barlines.
- Record every mismatch with an authority page/measure and the dossier
  `evidence_id` or event/direction ID.
- Review both K. 570 `source_score_corrections` separately from note fidelity
  and confirm the corresponding direction rows in the reverse table.

### Music-theory judgment

- Judge whether the exact candidate onset in W3 is the claimed
  formal/thematic return; do not assume it falls at the measure downbeat.
- Judge the tonic status at the exact candidate onset without relying on the
  operator role label.
- Judge whether the windows expose enough context for the six cue ratings.
- Identify any omitted notation that could materially change a cue score.
- State whether K. 545 is a suitable positive identification control and
  whether its recognizability changes how the analysis should be framed.

### Reporting discipline

- Distinguish source-transcription errors from disagreements about formal
  interpretation.
- Distinguish a model's exact identification from evidence of memorization or
  training-data provenance; the former does not prove the latter.
- Recommend changed claims as well as changed data. A valid expert response
  may conclude that the data are faithful but the experiment cannot support a
  proposed interpretation.
- Evaluate whether every tested provider family's participation in protocol
  development is disclosed prominently enough and whether it narrows any
  claim.

## Structured criticism

Copy `EXPERT_REVIEW_TEMPLATE.json`, verify its prefilled artifact hashes,
replace its blank review fields, and submit the completed file with an issue or
pull request. Use one issue object per atomic finding. Preserve the reviewed
dossier and reverse-table SHA-256 values in each case review so later revisions
cannot be mistaken for the reviewed artifacts. Clementi is explicitly scoped
to deferred coordinates only because no dossier or reverse table exists.
The stable locator is the tuple of `case_id`, authority page and measure,
window-relative measure, evidence/event/direction ID, and JSON Pointer. Use
`source_fidelity`, `candidate_coordinate`, `formal_interpretation`,
`representation_omission`, `provenance`, `licensing`, or `reporting_claim` as
the issue type. Preserve disagreements rather than overwriting an earlier
review; multiple completed review files are welcome.

## Reproduction checks

From `research/off-tonic-recapitulation/`:

```text
node scripts/validate-case.mjs data/cases/CASE-6U43.json
node scripts/validate-case.mjs data/cases/CASE-8JQJ.json
node scripts/validate-case.mjs data/cases/CASE-D09B.json
node scripts/validate-case.mjs data/cases/CASE-DZWT.json
node scripts/validate-case.mjs data/cases/CASE-Q2R9.json
node scripts/validate-case.mjs data/cases/CASE-VT57.json
node scripts/compile-transcription.mjs --case CASE-6U43 --check
node scripts/compile-transcription.mjs --case CASE-8JQJ --check
node scripts/render-case-table.mjs --case CASE-6U43 --check
node scripts/render-case-table.mjs --case CASE-8JQJ --check
node scripts/render-case-table.mjs --case CASE-D09B --check
node scripts/render-case-table.mjs --case CASE-DZWT --check
node scripts/render-case-table.mjs --case CASE-Q2R9 --check
node scripts/render-case-table.mjs --case CASE-VT57 --check
node scripts/test-extract-dcml-mozart.mjs
```

Passing these commands confirms reproducibility and structural validity. It
does not resolve the open visual or interpretive judgments above.
