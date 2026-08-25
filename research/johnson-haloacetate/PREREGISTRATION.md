# Preregistration: Johnson-haloacetate CX3 rotation

Written 2026-08-24 in the private Molecules lab, before any torsion energy
or scan charge was inspected. This is the publication copy of that freeze.
The hypothesis below is the one that was frozen then; it was not rewritten
after the scan.

## Intellectual contract

- Post type: research
- Question: does carboxylate oxygen charge oscillate with CX3 rotation,
  with larger amplitude for CCl3COO− than for CF3COO−?
- Primary source and relationship: independent rematch and relaxed CX3
  scan taking the geometry/bond-rotation invitation in Johnson, Gregory,
  Robertson, Gresham, Nelson, Craig, Prescott, Page, Webber, and Wanless
  (2025). The source authors' MP2/aug-cc-pVQZ program, DDEC6 charges, and
  published geometries were not used.
- Contribution sentence and type: a relaxed CX3 rotation of CF3COO− and
  CCl3COO− at B3LYP-D3(BJ)/aug-cc-pVDZ, which is not in Johnson 2025,
  finds that MBIS carboxylate oxygen charge does not oscillate with a
  larger amplitude for CCl3 than for CF3. Type: untested regime.
- Hypothesis: MBIS q(O) and q(COO) oscillate with the frozen CX3 dihedral
  φ; the peak-to-peak amplitude is larger for CCl3COO− than for CF3COO−;
  acetate is flat. Amplitude = max−min on both-converged points, reported
  separately for q(O) and q(COO). We do not pick one after seeing they
  split. The question named oxygen charge, so falsifier 2 is scored on
  q(O). q(COO) is disclosed alongside.
- Falsifier: (1) q(O) is flat on both ions, or (2) the CF3 q(O) amplitude
  is greater than or equal to the CCl3 q(O) amplitude.
- Why the other outcome is still publishable: a larger CCl3 q(O) swing
  would be the first same-footing rotation bound we have for the 2025
  invitation; a miss would mean the invited oscillation did not appear
  under these conditions.
- What this experiment can establish: whether MBIS q(O) and q(COO) on
  this gas-phase B3LYP-D3(BJ)/aug-cc-pVDZ relaxed φ = X–Cα–C–O grid move
  with a larger peak-to-peak amplitude for CCl3COO− than for CF3COO−.
- What it cannot establish: DDEC6 or MP2/aug-cc-pVQZ charges; Hirshfeld
  charges (not in this Psi4 build); a pKa mechanism; solvent; or a
  verdict on Johnson et al. 2025.

## Frozen protocol

- Code: independent Psi4 1.11 implementation. No source input files.
- State: charge −1, singlet, gas phase. No PCM.
- Functional/basis/dispersion: B3LYP-D3(BJ)/aug-cc-pVDZ.
- Binding charges: MBIS. Löwdin is reported only and is not binding.
  Hirshfeld is not in this Psi4 build. See JOURNAL.md for the dated
  Hirshfeld/Löwdin amendments.
- Gate (before any torsion): rematch unconstrained optimizations of
  CH3COO−, CF3COO−, CClF2COO−, and CCl3COO−. Pass if r(C–C) satisfies
  CCl3 > CF3 > acetate, Δ(C–X) (out-of-plane minus in-plane) satisfies
  CCl3 > CF3, and MBIS q(O) and q(COO) are more negative for CF3 than
  for CCl3.
- Scan: relaxed φ = X–Cα–C–O, frozen dihedral 5-4-1-2, 0–120° by 15°
  on CF3COO− (M1) and CCl3COO− (M3). The published abscissa is the
  frozen target `angle`, not a hopping realized-dihedral column.
- Amplitude: max−min on points with optking True and a clean exit,
  separately for q(O) and q(COO).
- Decision rule: hypothesis supported if the CCl3 q(O) amplitude is
  larger than the CF3 q(O) amplitude; **falsified** if falsifier 1 or 2
  fires; inconclusive if either ion fails to converge on the grid.
- Exclusions: a point that does not converge does not enter max−min.
- Stopping rule: rematch all four ions, then run the 15° scan on M1
  and M3.

## Publication boundary

- Rights, privacy, secrets, and public-file review: no credentials or
  private data. Raw Psi4 logs stay in the private Molecules lab (large,
  machine paths), the same pattern as `research/hillel-triplet`.
- Reproducibility level this design can earn: analysis-reproducible from
  committed rematch and scan CSVs. Not end-to-end in this public
  repository.
- Archived-evidence or future-rerun constraints: the Psi4 executable
  used for the canonical run is
  `/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4` on local
  Apple Silicon. This public repo does not rerun Psi4.

## Amendments

**2026-08-24 — binding scheme restricted to MBIS after rematch charges
and before any torsion.** Hirshfeld is absent from this Psi4 1.11 build.
Löwdin on aug-cc-pVDZ reversed the CF3/CCl3 oxygen-charge order and is
ill-defined on this basis relative to MBIS. The binding scheme was
amended to MBIS-only after rematch charges were known and before any
torsion energy or scan charge was seen. The frozen hypothesis and
falsifier were not changed. Dated in JOURNAL.md.
