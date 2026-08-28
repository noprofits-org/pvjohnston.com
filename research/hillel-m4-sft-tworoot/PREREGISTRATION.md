# PREREGISTRATION — same-geometry two-root SF evaluation

Frozen 2026-08-27, before any two-root energy is seen. Amendment to hillel-m4-sft;
the 2026-08-25 crossing freeze is unchanged.

## Question
Does the M4 SF profile-gap sign change survive a same-geometry two-root evaluation?

## Hypothesis
ΔE still changes sign between 90° and 105° when S0 and T1 are taken from the same SF manifold on one structure.

## Crossing definition
At each of the eight already-reported constrained-CNNC geometries (S0-relaxed and T1-relaxed at 90°, 105°, 120°, 135°), run one SF-TDA SP. S0 = lowest SF root ⟨S²⟩≈0; T1 = lowest ⟨S²⟩≈2; both from that one calculation. ΔE(φ, geom) = E(T1) − E(S0) at that geometry. A same-geometry sign change is a sign change of ΔE on a neighboring both-assigned pair in 90–135°, scored separately on the S0-relaxed family and on the T1-relaxed family. Linear interpolant of a sign-change pair is recorded; it is not an MECP.

## Falsifiers
1. Neither family has a both-assigned sign change of same-geometry ΔE on a neighboring pair in 90–135° → the profile-gap sign change did not survive as an electronic gap at one geometry.
2. A family has a sign change whose interpolant lies outside 90–135° → that family does not support an in-window same-geometry crossing.
3. A family has no neighboring both-assigned pair → that family is inconclusive.

## Method (binding)
ORCA 6.1.1, `$ORCA`. `%pal nprocs 4`; never `mpirun`. SF-TDA, LibXC(BHANDHLYP) D3(BJ)/def2-QZVPP, RIJCOSX, gas, charge 0, SF ref mult 3, NROOTS 3. Geometries are the eight converged published constrained-CNNC opts. No new opts. No IROOT.

## Publication boundary

- Rights, privacy, secrets, and public-file review: no credentials
  or private data. Raw ORCA `.out` files stay in the private
  Molecules lab (large, machine paths), the same pattern as
  `research/hillel-m4-sft`.
- Reproducibility level this design can earn: analysis-reproducible
  from the committed Bayes projection. Not end-to-end in this
  public repository.
- Archived-evidence or future-rerun constraints: the ORCA 6.1.1
  executable used for the canonical run lives on the private-lab
  host. This public repo does not rerun ORCA.
