# Preregistration: Hillel M4 SF-TDDFT rematch

Written 2026-08-25 in the private Molecules lab, before the required
CNNC window was scored. This is the publication copy of that freeze.
The hypothesis below is the one that was frozen then; it was not
rewritten after the 90°/105° sign change was seen.

## Intellectual contract

- Post type: research
- Question: does Hillel M4 still show an S0/T1 crossing near 110°
  when S0 and T1 are taken from the SF-TDDFT manifold at the 2024
  electronic-structure level (BH&HLYP-D3(BJ)/def2-QZVPP, Tamm–Dancoff
  spin-flip)?
- Primary source and relationship: independent rematch of Hillel,
  Rough, Barrett, Pietro, and Mermut (2024) SF-TDDFT on one
  molecule that paper did not compute. The 2026-08-22 RKS/UKS
  B3LYP-D3(BJ)/cc-pVDZ note is the prior same-molecule scan, not
  this method. The 2026 HPAS paper is a later method/scaffold from
  the same group, not the molecule under test.
- Contribution sentence and type: an independent ORCA 6.1.1
  SF-TDDFT/TDA BH&HLYP-D3(BJ)/def2-QZVPP constrained CNNC scan of
  4-dimethylamino-4′-nitroazobenzene (Hillel M4), which is not in
  Hillel et al. 2024 and is not the 2026-08-22 RKS/UKS
  B3LYP-D3(BJ)/cc-pVDZ scan. Type: untested regime.
- Hypothesis: M4 still shows a both-converged S0/T1 crossing near
  110° when S0 and T1 are taken from the SF-TDDFT manifold.
- Falsifiers, fixed at the same time:
  1. no both-converged, both-spin-assigned sign change of
     ΔE = E(T1) − E(S0) on the required window;
  2. the linear interpolant of that sign change lies outside
     90–135°;
  3. there is no neighboring both-converged both-assigned pair
     from which an interpolant can be taken.
- Why the other outcome is still publishable: a missing or
  out-of-window crossing would bound the 2024 method on this dye;
  a surviving in-window crossing would mean the RKS/UKS 110.5°
  zero was not an artifact of leaving the 2024 electronic-structure
  level.
- What this experiment can establish: whether ΔE changes sign
  between neighboring both-converged both-assigned points on this
  gas-phase SF-TDA window, and where the stored interpolant sits.
- What it cannot establish: dichloromethane PCM; a
  minimum-energy crossing point; CASSCF/QD-NEVPT2; M2; 4-hydroxyazobenzene;
  or a verdict on the 2024 or 2026 papers themselves.

## Frozen protocol

- Code: independent ORCA 6.1.1 SF-TDA inputs. Hillel et al. 2024
  used ORCA 5.0.3; their geometries, orbitals, and energy tables
  are not imported.
- States: S0 and T1 assigned from the SF-TDDFT manifold by
  ⟨S²⟩ and iroot. A point counts only if both states converged
  and both were assigned.
- Functional/basis/dispersion: BH&HLYP-D3(BJ)/def2-QZVPP,
  Tamm–Dancoff, RIJCOSX, gas phase. No PCM.
- Coordinate: CNNC dihedral constrained; remaining degrees of
  freedom relaxed. Required window: 135°, 120°, 105°, 90°.
- Crossing definition: linear interpolant of
  ΔE = E(T1) − E(S0) on a neighboring both-converged
  both-assigned pair. Conversion 1 Eh = 2625.49963831 kJ/mol.
- Decision rule: hypothesis **supported** if a neighboring pair
  changes sign and the interpolant lies inside 90–135°;
  **falsified** if falsifier 1, 2, or 3 fires; inconclusive if
  the required window is incomplete.
- Exclusions: M2 is not in this queue. 4-hydroxyazobenzene stays
  parked. An unassigned or unconverged point is not a crossing
  bracket.
- Stopping rule: finish the four required angles. Do not open a
  second SF queue, reconverge M2, or start 4-hydroxyazobenzene
  from this freeze.

## Publication boundary

- Rights, privacy, secrets, and public-file review: no credentials
  or private data. Raw ORCA `.out` files stay in the private
  Molecules lab (large, machine paths), the same pattern as
  `research/hillel-triplet`.
- Reproducibility level this design can earn: analysis-reproducible
  from the committed Bayes projection. Not end-to-end in this
  public repository.
- Archived-evidence or future-rerun constraints: the ORCA 6.1.1
  executable used for the canonical run lives on the private-lab
  host. This public repo does not rerun ORCA.

## Amendments

**2026-08-25/27 — LibXC functional, ⟨S²⟩ parser, 90° S0 reseed,
relocate pauses.** Native BH&HLYP constrained Opt exited 55; the
published window uses LibXC(BHANDHLYP). The committed spin
assignment uses a corrected read of the ORCA ⟨S²⟩ lines. S0 at
90° was reseeded from the converged T1 orbitals after the first
S0 attempt. Jobs in the required window were paused and relocated;
the published numbers are the both-converged both-assigned totals
after those interruptions, not a second electronic-structure
method. The hypothesis and the three falsifiers were not rewritten
after the 90°/105° sign change was seen.
