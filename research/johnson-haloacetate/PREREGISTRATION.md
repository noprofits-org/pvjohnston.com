# Preregistration: Johnson-haloacetate CX3 rotation

Frozen 2026-08-23 in the private Molecules lab, before any rematch
energy or torsion. This is the publication copy of that freeze. Dated
amendments (Hirshfeld unavailable; then Löwdin demoted) live in
`JOURNAL.md`. The bullets below were not rewritten after those
amendments or after the scan.

## Intellectual contract

- Post type: research
- Question: Does carboxylate oxygen charge oscillate with CX3 rotation,
  with larger amplitude for CCl3COO− than for CF3COO−?
- Primary source and relationship: independent rematch and relaxed CX3
  scan taking the geometry/bond-rotation invitation in Johnson, Gregory,
  Robertson, Gresham, Nelson, Craig, Prescott, Page, Webber, and Wanless
  (2025). The source authors' MP2/aug-cc-pVQZ program, DDEC6 charges, and
  published geometries were not used.
- Hypothesis: On a relaxed CX3 rotation, Hirshfeld and MBIS oxygen
  charges (and the COO sum) oscillate with the X–Cα–C–O dihedral.
  Peak-to-peak amplitude is larger for CCl3COO− than for CF3COO−.
  Acetate is the flat control.
- Falsifier:
  1. q(O) is flat vs dihedral on both haloacetates, or
  2. CF3 amplitude ≥ CCl3 amplitude.
- Either outcome is publishable.
- What this experiment can establish: whether oxygen charge and the COO
  sum on a relaxed φ = X–Cα–C–O grid move with a larger peak-to-peak
  amplitude for CCl3COO− than for CF3COO−.
- What it cannot establish: DDEC6 or MP2/aug-cc-pVQZ charges; a pKa
  mechanism; solvent; or a verdict on Johnson et al. 2025.

## Frozen protocol

- Code: independent Psi4 1.11 implementation. No source input files.
- State: charge −1, singlet, gas phase. No PCM.
- Functional/basis/dispersion: B3LYP-D3(BJ)/aug-cc-pVDZ.
- Intended charges at freeze: Hirshfeld and MBIS (and the COO sum).
  Amendments to the binding scheme live in `JOURNAL.md`.
- Gate (before any torsion): rematch unconstrained optimizations of
  CH3COO−, CF3COO−, CClF2COO−, and CCl3COO−. The gate inequalities and
  which charge schemes they bound are in `JOURNAL.md`.
- Scan: relaxed φ = X–Cα–C–O, frozen dihedral 5-4-1-2, 0–120° by 15°
  on CF3COO− (M1) and CCl3COO− (M3). The published abscissa is the
  frozen target `angle`, not a hopping realized-dihedral column.
- Amplitude: max−min on points with optking True and a clean exit,
  separately for q(O) and q(COO).
- Decision rule: hypothesis supported if the CCl3 amplitude is larger
  than the CF3 amplitude; **falsified** if falsifier 1 or 2 fires;
  inconclusive if either ion fails to converge on the grid.
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

See `JOURNAL.md`. Do not read later binding-scheme or scoring notes
back into the frozen bullets above.
