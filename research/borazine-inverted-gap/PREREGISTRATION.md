# Preregistration (FROZEN 2026-09-28, approved by Peter): does borazine keep an inverted S1/T1 gap at ADC(2)/def2-TZVP?

Drafted 2026-09-28 (PT), before any production calculation. The only calculations run so far were box
timing smoke tests (PySCF/adcc/Psi4 on borazine at def2-SVP and def2-TZVP). They exist to size the job.
They are not results, they are not used below, and they must not be quoted as evidence.

Disclosure, made before freezing: two of those untuned smoke tests happened to print a borazine gap.
DF-ADC(2)/def2-SVP gave ΔEST(1) = −129 meV and EOM-CCSD/def2-SVP gave ΔEST(1) = +118 meV. Both use a
smaller basis than P1 and neither enters any verdict below. We froze this file knowing them.

Peter approved this file on 2026-09-28 (PT). It becomes `research/borazine-inverted-gap/PREREGISTRATION.md`.
From now on any change is a dated amendment. No silent edits.

## Intellectual contract

- Post type: research
- Question: Do we get the published ADC(2)/def2-TZVP sign of ΔEST = E(S1) − E(T1) for borazine (1) and the
  boroxine control (11)? And, if the M1 time allows, for 9, 10, 12 and the fused BN-acenes 2a/2b/2c?
  We compute these on the authors' own PBE0/6-31G(d) geometries with an independent open-source
  implementation (PySCF DF-ADC(2)).
- Primary source and relationship: Shizu, Ishihara, Uratani, Kaji, "Inorganic benzenes with inverted
  singlet-triplet gaps", Commun. Chem. 2026, doi:10.1038/s42004-026-02141-0 (CC BY). We run an independent
  reproduction of their ADC(2) column (SI Tables 1 and 3). We use their geometries but not their program
  (Turbomole). We do not run their headline method, SCS-CC2.
- Contribution (candidate): an independent open-source ADC(2)/def2-TZVP ΔEST for borazine, boroxine and
  9/10/12/2a/2b on the published geometries, plus an EOM-CCSD/def2-SVP cross-check. Neither is
  in the source, which reports Turbomole SCS-CC2 and ADC(2) only.
  Type: untested regime (implementation/method cross-check), or falsification if P1 fails.
- Why the other outcome is publishable: a positive borazine gap at ADC(2) under our settings would be a
  did-not-reproduce-for-us result, reported as such. A negative gap that matches is a plain reproduction
  of one column, with the SCS-CC2 column explicitly untested.
- What this can establish: whether an independent RI-ADC(2) implementation, with the stated settings on
  the published geometries, gives the published ADC(2) signs (and magnitudes within tolerance).
- What it cannot establish: anything about SCS-CC2 (not run), kF values (not run), the real (experimental)
  ordering of S1/T1, or behaviour at relaxed S1 geometries.

## Frozen falsifier (verbatim; do not edit after freeze)

> **P1 (primary).** Method: PySCF DF-ADC(2), def2-TZVP, def2-TZVP-RI auxiliary basis in the ADC step,
> conventional RHF reference, frozen core (PySCF `chemcore`). Geometry: the published PBE0/6-31G(d) S0
> geometry of borazine (SI Table 9), used unchanged. S1 is the lowest singlet root and T1 the lowest
> triplet root, whatever their symmetry or oscillator strength, and ΔEST = E(S1) − E(T1). The hypothesis
> "borazine has an inverted gap at ADC(2)/def2-TZVP" is **falsified if ΔEST(1) ≥ 0 meV**. It is
> **supported and reproduced** if ΔEST(1) < 0 and lies within ±50 meV of the published ADC(2) value of
> −193 meV (−243 to −143 meV). It is **supported, magnitude not reproduced** if ΔEST(1) < 0 but falls
> outside that window.
>
> **P2 (control).** Same settings, boroxine (11, SI Table 53). The control **fails if ΔEST(11) ≤ 0 meV**.
> If the control fails, the whole Tier 1 verdict is **inconclusive**, whatever P1 gives. The control is
> reproduced if ΔEST(11) lies within ±50 meV of the published +279 meV.
>
> **S1 (secondary; applies only to the molecules actually run).** Published ADC(2) ΔEST: 2a +34, 2b +106,
> 2c −21, 9 +26, 10 −47, 12 −160 meV. For each molecule, "reproduced" means |ΔEST(ours) − published| ≤ 50 meV.
> A sign test is carried only where |published| > 50 meV, so it applies to 2b (not reproduced if
> ΔEST(2b) ≤ 0) and 12 (not reproduced if ΔEST(12) ≥ 0). For 2a, 2c, 9 and 10 the sign is declared
> **non-decisive** in advance, because the published value lies inside the tolerance band around zero.

Tolerance reasoning (±50 meV). We expect differences from the published numbers from the following
sources: RI versus exact integrals in the ADC step (a few meV with a matched RI-C auxiliary basis); the
frozen-core definition (our `chemcore` freezes B/N/O 1s, S 1s–2p, Ga/Se 1s–3p with 3d active, which is
meant to match Turbomole's default −3 Eh threshold, but the SI does not state the setting); Davidson
convergence and root targeting (~1 meV); SI rounding (ΔEST given to 1 meV, energies to 0.01 eV); and
implementation differences between PySCF and Turbomole ricc2. We expect these to total well under 50 meV
for a closed-shell valence ππ* state. The band is set wider than we expect so that a sign flip beyond it
cannot be blamed on bookkeeping. The SI itself has ≤13 meV internal rounding inconsistencies (6i ADC(2);
6k SCS-CC2; 7f −78 vs −79 meV between Tables 1 and 2).

## Frozen protocol

- Inputs: `xyz/<id>.xyz`, parsed from SI1.pdf (sha256 2106a4fd…802f), Supplementary Tables 9–65,
  unchanged (Å, 6 decimals). The point groups we detect match the SI at a 1e-4 Bohr tolerance.
- Software: PySCF 2.14.x (pip wheel, osx-arm64) in a fresh venv on the M1. Record the exact versions,
  BLAS, thread count and `platform.machine()` in each result JSON.
- Singlets: RADC(2)-ee, 4 roots. Triplets: UADC(2)-ee on the RHF solution, 8 roots in the Ms=0 manifold.
  Triplets are the roots with ⟨S²⟩ within 0.3 of 2, cross-checked against the RADC singlet list.
  For D3h molecules, 4 roots makes sure that a degenerate E′/E″ pair cannot be split at the cut.
- SCF: conv_tol 1e-10 Eh, conv_tol_grad 1e-7. If SCF or Davidson does not converge, we stop and do not
  report. We rerun once with more roots, never with a different basis.
- Order: 1, 11 (these decide P1/P2), then 9, 10, 12, then 2a, then 2b. Peter approved the multi-day 2b run
  (Tier 1b) on 2026-09-28 because it is the only fused ring with a decisive sign test. 2c is not run.
- Command: `python tier1/run_adc2_pyscf.py <id>` → `tier1/results/<id>_adc2_def2-tzvp.json`.
- Exploratory, outside the falsifier: EOM-CCSD/def2-SVP (`tier1/run_eomccsd_pyscf.py`) on 1, 11, 9, 10,
  12, 2a, 2b; optional ORCA 6.1.1 STEOM-CCSD singlet/triplet for 1 and 11. We will report these as extra
  data and will not let them change the P1/P2 verdict.

## Publication boundary

- SI coordinates are CC BY (redistribution with attribution). Every published number in
  `expected/` is attributed to the SI and is not ours.
- Reproducibility level this design can earn: end-to-end reproducible (open-source code, committed
  inputs). SCS-CC2 stays archived evidence (Turbomole, not run by us).

## Amendments

None at freeze.

## Amendment 1 (2026-09-28, PT), written before any def2-TZVP EOM-CCSD calculation

Why: the exploratory EOM-CCSD/def2-SVP cross-check gave borazine ΔEST = +117.6 meV, the opposite sign to
our ADC(2)/def2-TZVP P1 result (−191.9 meV). That comparison mixes method and basis. This amendment adds
one secondary test to separate them. It does not change P1, P2 or S1, and it cannot change their verdicts.

> **A1 (secondary, method check).** Method: PySCF EOM-EE-CCSD (`eomee_ccsd_singlet` / `eomee_ccsd_triplet`),
> def2-TZVP, conventional RHF reference (conv_tol 1e-10 Eh), frozen core (PySCF `chemcore`), 4 singlet and
> 4 triplet roots. Geometries: the published PBE0/6-31G(d) S0 geometries of borazine (1) and boroxine (11),
> unchanged. S1 and T1 are the lowest singlet and lowest triplet roots, and ΔEST = E(S1) − E(T1).
> Control first: if ΔEST(11) ≤ 0 meV, A1 is **inconclusive**.
> Otherwise: if ΔEST(1) > +50 meV, **ADC(2) and EOM-CCSD disagree in sign for borazine at def2-TZVP**
> (method-driven). If ΔEST(1) < −50 meV, **they agree in sign at def2-TZVP, and the def2-SVP sign flip was
> basis-driven**. If −50 ≤ ΔEST(1) ≤ +50 meV, the EOM-CCSD sign is **non-decisive** at our tolerance.

Budget: about 1 h each on the M1 (box estimate 0.8 h and 6.5 GB for 1; 0.5 h for 11), run after 2b.
Command: `python tier1/run_eomccsd_pyscf.py <id> --basis def2-tzvp` → `tier1/results/<id>_eomccsd_def2-tzvp.json`.
What this cannot establish: which method is right. Neither is the exact answer, and higher-level
(for example EOM-CCSDT or CC3) numbers are outside the Mac budget.
