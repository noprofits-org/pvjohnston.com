# Six-dossier pilot corpus

Status: **six selected dossiers encoded, validated, and frozen as dataset 1.0.0
at 2026-07-19T17:54:14Z**. The collection lock was created and verified at
2026-07-19T17:56:35.630Z. Real-case collection is authorized only from the
pre-outcome Git commit containing it.

## Selection rule

The pilot uses six eighteenth-century solo-keyboard sonata or binary-sonata
movements. It includes two distinct ambiguity mechanisms discussed by Greenberg,
three ordinary tonic returns, and one clear off-tonic return. Controls are
calibration anchors, not a representative sample or musicologist ground truth.
This 2+3+1 balance is an explicit pre-collection revision, not the originally
planned 2+2+2 balance.

## Cases

1. C. P. E. Bach, Wq 48/3/iii, m. 51: focal case in which primary-theme pitches
   return while the tonic is brief and unstable.
2. Benda, 1757 Sonata No. 2 in G/iii, m. 51: focal case in which thematic return
   begins off tonic and moves gradually toward tonic.
3. Mozart, K. 570/i, m. 133: ordinary tonic-return anchor.
4. Mozart, K. 333/i, pickup m. 93 into m. 94: ordinary tonic-return anchor. The
   selected DCML/NMA event onset resolves the pickup numbering.
5. Mozart, K. 545/i, m. 42: clear subdominant-return anchor and preregistered
   positive identification control.
6. Mozart, K. 576/i, m. 99: ordinary tonic-return anchor. The pinned NMA,
   DCML score/timeline, and published analysis converge on the principal-theme
   recapitulation at printed m. 99 (`mc=101` in the split DCML timeline).

## Matching logic

K. 570 (1789) and K. 545 (1788) form a same-composer, same-medium, near-date
tonic/off-tonic contrast. K. 333 and K. 576 add two ordinary tonic-return
anchors but do not restore balance: K. 545 is the sole clear off-tonic control.
The focal cases are earlier (1741 and 1757), so the controls cannot support a
historical prevalence claim.

## Deferred Clementi replication

Clementi, Op. 10 No. 3/i was removed from the initial collection before any
outcome call because 24 of its 27 required evidence measures had not completed
an authority-based event double pass. Its corrected pickup in m. 70 and full
theme in m. 71 remain source-linked to Brownell's Torricella-derived excerpt,
but Greenberg does not work through the movement as a case study. The source,
coordinate correction, and partial transcription record remain in provenance
for a future replication; they are not promoted or silently discarded.

## Leakage risk

K. 545 is the intended identification-sensitivity anchor because its opening is
canonical, but its recognizability in the transformed dossier is not assumed as
an established fact. The probe must demonstrate sensitivity before
non-identification of the other cases can support any claim
about withheld identity, and even then the result is bounded elicitation, not
proven blinding. It is excluded from the target zero-L2 gate and from the
primary reliability gate (which uses the five target cases) but remains in the
analysis matrix as a disclosed sensitivity anchor. The C. P. E. Bach and Benda passages
also carry contamination risk because Greenberg analyzes them directly. An exact
identification is a finding, not a response to discard. Identification probes
run in separate fresh contexts on the same dossier representation as analysis.
K. 576 begins in D major, so common-tonic D normalization applies an identity
transform: exact pitch classes and register survive in that dossier, unlike in
the other five. This makes its masking weaker and is disclosed as a
case-specific leakage risk. The same strict target-recognition rules still
apply, and K. 576 remains a target rather than a positive control; its inclusion
cannot support a causal claim about masking or transposition.

## Window feasibility

Greenberg reproduces Benda iii, bars 48--62. To apply one mechanical rule to all
six cases while retaining the full focal progression, the opening window uses
eight measures and each contextual window uses six: pre-candidate 45--50,
candidate 51--56, and continuation 57--62. This rule was fixed from score
coverage before any dossier encoding or model output.

## Required source audit

- Pin public-domain first-edition scans and file hashes for C. P. E. Bach Wq.
  48/3 and Benda's 1757 Sonata No. 2. Retain the 1783 Clementi lineage as a
  future-replication source rather than initial-collection data.
- Pin DCML release v2.3 and repository commit for all four Mozart cases.
- Verify every candidate onset and the required 8+6+6+6 measure windows.
- Resolve K. 333's pickup numbering using score event onset rather than prose.
- Resolve K. 576's opening pickup and intrameasure repeat split: W1 is `mc=1-9`,
  the second part begins at `mc=60`, and printed m. 99 is `mc=101`.
- Confirm each movement has enough measures for the fixed windows.
- Record licensing separately for source score, derived symbolic events, and
  published pilot data.
- Do not substitute the public Mutopia/PDMX Benda G-major movement: its
  exposition ends at bar 16, whereas the focal 1757 movement's exposition ends
  at bar 26.
