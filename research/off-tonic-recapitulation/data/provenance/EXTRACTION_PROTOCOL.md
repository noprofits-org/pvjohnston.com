# Symbolic dossier extraction protocol

Status: **frozen for dataset 1.0.0 at 2026-07-19T17:54:14Z**. All six launch
dossiers were regenerated and checked before freeze. Real-case collection
remains prohibited until the randomized schedule, collection lock, and
pre-outcome Git commit are complete.

This protocol defines dossier schema `3.1.0`. A dossier contains only normalized
notation and fixed structural identifiers. It contains no prose or identity
metadata. Structural conformance is necessary but does not establish that a
musical fingerprint is unrecognizable; the separate identification probe tests
that residual risk.

## Source and operator-only provenance

For every score, record outside the model-facing dossier:

- edition, stable URL or repository identifier, access date, licence, and exact
  source-file SHA-256;
- original tonic spelling and mode, source coordinates for the second-part
  boundary and candidate onset, and source-to-window measure mapping;
- extraction program and version, transposition interval, source-to-neutral
  voice map, correction log, and generated dossier SHA-256;
- the exact elapsed and total second-part durations used in the dossier; and
- the verifier, verification date, and unresolved limitations.

Prefer machine-readable scholarly or public-domain editions. If transcription
is necessary, retain both the transcription and a correction log. Verify the
candidate against the pinned source before transformation. Candidate selection
remains an operator decision; this pilot tests rubric application to a supplied
candidate, not automatic discovery of formal returns.

## Fixed windows

Extract four non-overlapping windows in this order:

1. `opening` (`W1`): the first eight complete notated measures;
2. `pre_candidate` (`W2`): the six complete measures immediately before the
   measure containing the candidate onset;
3. `candidate` (`W3`): the complete measure containing the candidate onset and
   the next five complete measures; and
4. `continuation` (`W4`): the next six complete measures after `candidate`.

Number the complete measures from zero independently within each window. Retain
an opening anacrusis, when present, as `W1` measure `-1`; it does not count among
the eight complete opening measures. No other window may contain `-1`.

The candidate is always `W3`, measure `0`. Record its exact onset within that
measure in rational quarter-note units. Exclude a case if any required window is
too short, if the windows overlap, or if a required window contains a notation
construct that schema `3.1.0` cannot represent without loss. Do not shorten or
extend a window case by case.

Compute second-part position from notated time: elapsed duration from the
second-part repeat boundary to the candidate onset, divided by total notated
duration from that boundary to the movement's notated end. Do not unfold
repeats; count each written measure once, including each written volta once.
Store the exact elapsed and total durations as separate reduced rationals. Do
not store a rounded fraction. The total must be positive and elapsed must not
exceed total.

## Canonical model-facing representation

The root object has exactly these fields: `schema_version`, `case_id`,
`condition`, `encoding`, `candidate_return`, and `windows`. Every string is a
fixed enum or a structural ID. Free-form strings are prohibited.

`encoding` declares common tonic D, home mode, quarter-note duration units,
window-relative measure numbers, scientific pitch with diatonic spelling, and
complete coverage of notes, notated rests, voices, meter, key signatures,
dynamics, articulations, ornaments, repeats, and barlines. `complete` means an
empty array is a verified absence in the selected edition, not an omitted
feature.

Every measure contains:

- its fixed relative index and one measure-level citation ID;
- exact notated duration, active meter, and active notated key signature;
- normalized left and right barlines and volta membership;
- typed `note` or `rest` events; and
- typed fixed-dynamic, graphical-hairpin, or textual gradual-dynamic
  directions.

Measure-level evidence IDs are assigned `E001`, `E002`, and so on in canonical
window and measure order, including `-1` first when an anacrusis exists. Event
IDs (`EV0001`...) and direction IDs (`DR0001`...) are likewise assigned in
canonical traversal order. Voice IDs form the contiguous set `V01`...`Vnn`.
These rules prevent identifiers from carrying source or corpus information.

Represent all onset and duration values as objects containing integer
`numerator` and positive integer `denominator`. Fractions must be nonnegative,
reduced to lowest terms, and encode zero only as `0/1`. Complete measures must
equal the duration implied by their meter. The optional anacrusis must be
shorter than a complete measure. Every event must begin within its measure and
end no later than the measure boundary; directions may occur at the boundary.

Represent pitch as diatonic `step`, chromatic `alter`, and scientific-pitch
`octave`. Preserve notated pitch spelling, onset, written duration, voice,
ties, grace-note status, rests, dynamics, articulations, ornaments, repeats,
voltas, and barlines. A fermata or ornament is a notated mark only; do not infer
a sounding duration. Texture and register are recoverable from simultaneous
typed events and must not be summarized in a separate field.

Preserve the notational medium of gradual dynamics. Encode graphical wedges as
typed hairpin states. Encode a printed textual `cresc.`/`crescendo` or
`dim.`/`dimi:`/`diminuendo` instruction as `textual_gradual_dynamic`, with the
normalized semantic value `crescendo` or `diminuendo`. Surface spelling and
punctuation remain operator-only provenance; the typed value does not license
any inferred endpoint or dynamic level. Arbitrary expressive text remains
prohibited.

Within each measure, order events by onset, voice, event type, pitch, written
duration, and remaining enum fields; order directions by onset, type, value,
and voice. Sort articulation and ornament arrays alphabetically. Canonical
ordering is part of the encoding and makes independently generated dossiers
directly comparable.

## Mechanical normalization

Normalize the home tonic to D while preserving mode and every interval. Five
pilot sources require nonzero displacement. K. 576/i is already in D major and
therefore uses the identity transform; provenance and reporting must disclose
that its exact pitch and register survive and that masking is weaker for this
case. The experiment makes no causal claim about transposition or masking.
Choose the chromatic displacement from the source tonic pitch class to D in the
range `-5` through `+6` semitones; use `+6` for the tritone tie. Choose the
diatonic displacement that maps the source tonic letter to D in the same
direction.
Apply that single chromatic-plus-diatonic interval to every note, preserving
spelling. Store the original tonic and the interval only in operator provenance.

Map source voices once for the whole movement. Sort source staves from highest
to lowest and source voice/layer identifiers in their notated order, then assign
contiguous neutral IDs `V01` onward. Preserve that mapping through crossings;
never reorder voices from momentary register. If a source lacks explicit voice
layers, create stable layers in the retained transcription and document the
mapping and every correction in operator provenance.

Carry forward only notated key-signature changes. Do not infer local keys or
tonicizations. Mid-measure meter or key-signature changes are not representable
in schema `3.1.0`; exclude an affected pilot case or revise and freeze a new
schema before collection.

Remove titles, composer names, catalogue numbers, dates, movement and
instrument names, editorial prose, filenames, URLs, bibliographic data,
source-system identifiers, lyrics, and arbitrary text directions. Source data
must be copied through an explicit field allowlist; never serialize unused
source columns into a dossier.

## Prohibited analytical enrichment

Do not add Roman numerals, chord roots, inferred keys, cadence types, phrase
boundaries, formal functions, theme labels beyond the four fixed window roles,
texture labels, corpus roles, expected classifications, or prose descriptions.
A manual correction may repair transcription only; it must not interpret
harmony or form.

## Validation and verification

Before freezing a dossier:

1. run the schema and semantic validator;
2. regenerate the dossier from its pinned source plus operator-only extraction
   configuration and compare canonical output or document why regeneration is
   unavailable for a manual transcription;
3. reverse-render a score or event table and compare it with every source
   measure in the four windows;
4. verify event counts, pitches, written durations, transposition invariants,
   voice mapping, candidate onset, and second-part durations; and
5. scan keys and string values for identity metadata and pilot-specific aliases.

A second independent extraction pass is preferred. If unavailable, retain the
complete manual-check log and report that limitation. Hash the verified dossier
only after all corrections. The prompt builder must revalidate the hashed
dossier before embedding it.
