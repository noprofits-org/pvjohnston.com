# Preregistration: Hillel-triplet CNNC scan

Written 2026-08-18/19 in the private Molecules lab, before the M4 T1
continuation finished. Adapted here as the publication copy of that PLAN.
The hypothesis below is the one that was frozen then; it was not rewritten
after T1 was seen.

## Intellectual contract

- Post type: research
- Question: at RKS/UKS B3LYP-D3(BJ)/cc-pVDZ, does a classic push-pull
  azobenzene (4-dimethylamino-4′-nitroazobenzene, M4) lose the S0/T1 crossing
  along the CNNC twist, as Hillel, Rough, Barrett, Pietro, and Mermut (2024)
  wrote that protonation of AzPy does, and as they said would likely hold for
  the wider class of push-pull azobenzenes?
- Primary source and relationship: independent constrained scan of an untested
  2024 sentence. The source authors' ORCA/SF-TDDFT program is not used. The
  2026 HPAS paper is a later method/scaffold from the same group, not the
  molecule under test.
- Contribution sentence and type: an independent RKS/UKS B3LYP-D3(BJ)/cc-pVDZ
  CNNC torsion scan of 4-dimethylamino-4′-nitroazobenzene (M4) plus
  azobenzene/AzPy/AzPyH+/2-AzPy controls, which is not in Hillel et al. 2024
  or Hillel et al. 2026. Type: untested regime.
- Hypothesis: if the 2024 generalization holds at this level of theory, M4
  shows no S0/T1 crossing on the converged CNNC grid, like protonated AzPyH+
  (M2).
- Falsifier: M4 shows an S0/T1 crossing between converged points.
- Why the other outcome is still publishable: a surviving crossing would bound
  the 2024 sentence at this level of theory; a missing crossing would be the
  first same-footing control we have for that sentence on a classic push-pull
  azobenzene.
- What this experiment can establish: whether a linear zero of E(S0)−E(T1)
  exists between both-converged points on this gas-phase RKS/UKS
  B3LYP-D3(BJ)/cc-pVDZ CNNC grid.
- What it cannot establish: SF-TDDFT or CASSCF/QD-NEVPT2 surfaces; solvent
  (no PCM); a minimum-energy crossing point search; spin contamination
  (`<S²>` is not in the default UKS output); thermal rates; or a verdict on
  the 2024 or 2026 papers themselves.

## Frozen protocol

- Code: independent Psi4 1.11 implementation. No SF-TDDFT.
- States: RKS S0 and UKS T1.
- Functional/basis/dispersion: B3LYP-D3(BJ)/cc-pVDZ.
- Coordinate: CNNC dihedral frozen in optking; all other degrees of freedom
  relaxed. Continuation from trans (180°) toward cis (0°) in 15° steps.
- Molecules:

  | ID | Species | S0 charge/mult | T1 charge/mult |
  |----|---------|----------------|----------------|
  | M0 | azobenzene | 0 1 | 0 3 |
  | M1 | 4-phenylazopyridine (AzPy) | 0 1 | 0 3 |
  | M2 | N-protonated AzPy (AzPyH+) | 1 1 | 1 3 |
  | M3 | 2-phenylazopyridine (2-AzPy) | 0 1 | 0 3 |
  | M4 | 4-dimethylamino-4′-nitroazobenzene | 0 1 | 0 3 |

- Environment: gas phase. No PCM in this run.
- Crossing definition: linear zero of (E_S0 − E_T1) using both-converged
  points only. Conversion 1 Eh = 2625.4996 kJ/mol.
- Decision rule: hypothesis supported if M4 has no both-converged sign
  change on the grid; **falsified** if it has one; inconclusive if the
  trans-side M4 S0 or T1 series needed for the 120°/105° bracket fails.
- Exclusions: a point that does not converge does not count as a crossing
  bracket. Unconverged S0 energies are upper bounds.
- Stopping rule: run the 15° continuation 180→0 for S0 and T1 on M0–M4.

## Publication boundary

- Rights, privacy, secrets, and public-file review: no credentials or
  private data. Raw Psi4 logs stay in the private Molecules lab (large,
  machine paths), the same pattern as `research/bmn-frontier-orbitals`.
- Reproducibility level this design can earn: analysis-reproducible from
  committed summary CSVs / jsonl. Not end-to-end in this public repository.
- Archived-evidence or future-rerun constraints: the Psi4 executable used
  for the canonical run is
  `/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4` on local
  Apple Silicon. This public repo does not rerun Psi4.

## Amendments

**2026-08-21/22 — M4 S0 cis-side cut and reconvergence.** After the first
surfaces were in hand, M4 S0 at 90°, 75°, 60°, and 45° hit the 150-iteration
cap. The remaining M4 S0 points at 30°, 15°, and 0° were not started. A
`reconverge.py` pass with maxiter 300 was run on 90°, 75°, and 60°. The
hypothesis was not changed after T1 was seen. 60° reconverged on
2026-08-22 and is both-converged. 90° and 75° remained unconverged. The
claim crossing remains the 120°/105° both-converged pair only; a 105°→60°
sign change is not treated as a tight second crossing because 90° and 75°
are unconverged upper bounds.
