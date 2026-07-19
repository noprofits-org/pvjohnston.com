# Six-dossier pilot corpus

Status: **selected provisionally; score editions and measure concordance remain
to be verified before extraction**.

## Selection rule

The pilot uses six eighteenth-century solo-keyboard sonata or binary-sonata
movements. It includes two distinct ambiguity mechanisms discussed by Greenberg,
two ordinary tonic returns, and two clearly off-tonic returns. Controls are
calibration anchors, not a representative sample or musicologist ground truth.

## Cases

1. C. P. E. Bach, Wq 48/3/iii, m. 51: focal case in which primary-theme pitches
   return while the tonic is brief and unstable.
2. Benda, 1757 Sonata No. 2 in G/iii, m. 51: focal case in which thematic return
   begins off tonic and moves gradually toward tonic.
3. Mozart, K. 570/i, m. 133: ordinary tonic-return anchor.
4. Mozart, K. 333/i, pickup m. 93 into m. 94: ordinary tonic-return anchor. The
   selected DCML/NMA event onset will resolve the pickup numbering.
5. Mozart, K. 545/i, m. 42: clear subdominant-return anchor and preregistered
   positive identification control.
6. Clementi, Op. 10 No. 3/i, m. 69: clear subdominant-return anchor.

## Matching logic

K. 570 (1789) and K. 545 (1788) form a same-composer, same-medium, near-date
tonic/off-tonic contrast. K. 333 and Clementi Op. 10 No. 3 are both B-flat major
solo-keyboard works from approximately 1783. The focal cases are earlier
(1741 and 1757), so the controls cannot support a historical prevalence claim.

## Leakage risk

K. 545 is intentionally recognizable: the identification probe must demonstrate
sensitivity before non-identification of the other cases can support any claim
about withheld identity, and even then the result is bounded elicitation, not
proven blinding. It is excluded from the target zero-L2 gate and from the
primary reliability gate (which uses the five target cases) but remains in the
analysis matrix as a disclosed recognized anchor. The C. P. E. Bach and Benda passages
also carry contamination risk because Greenberg analyzes them directly. An exact
identification is a finding, not a response to discard. Identification probes
run in separate fresh contexts on the same dossier representation as analysis.

## Window feasibility

Greenberg reproduces Benda iii, bars 48--62. To apply one mechanical rule to all
six cases while retaining the full focal progression, the opening window uses
eight measures and each contextual window uses six: pre-candidate 45--50,
candidate 51--56, and continuation 57--62. This rule was fixed from score
coverage before any dossier encoding or model output.

## Required source audit

- Pin public-domain first-edition scans and file hashes for C. P. E. Bach Wq.
  48/3, Benda's 1757 Sonata No. 2, and the 1783 Clementi Op. 10 No. 3 lineage.
- Pin DCML release v2.3 and repository commit for all three Mozart cases.
- Verify every candidate onset and the required 8+6+6+6 measure windows.
- Resolve K. 333's pickup numbering using score event onset rather than prose.
- Confirm each movement has enough measures for the fixed windows.
- Record licensing separately for source score, derived symbolic events, and
  published pilot data.
- Do not substitute the public Mutopia/PDMX Benda G-major movement: its
  exposition ends at bar 16, whereas the focal 1757 movement's exposition ends
  at bar 26.
