---
title: "Does Hillel's 2024 push-pull sentence hold for 4-dimethylamino-4′-nitroazobenzene?"
date: 2026-08-22
author: Peter Johnston
tags: computational chemistry, azobenzene, SF-TDDFT, push-pull chromophores, intersystem crossing
description: An independent RKS/UKS B3LYP-D3(BJ)/cc-pVDZ CNNC torsion scan of an untested 2024 generalization — that push-pull azobenzenes, like protonated AzPyH+, would lose the S0/T1 crossing along the azo twist. The test case is 4-dimethylamino-4′-nitroazobenzene, with azobenzene, AzPy, AzPyH+, and 2-phenylazopyridine as controls.
post-type: research
contribution: an independent RKS/UKS B3LYP-D3(BJ)/cc-pVDZ CNNC torsion scan of 4-dimethylamino-4′-nitroazobenzene (M4) plus azobenzene/AzPy/AzPyH+/2-AzPy controls, which is not in Hillel et al. 2024 or Hillel et al. 2026.
contribution-type: untested regime
experiment: hillel-triplet
status: falsified
og-image: /images/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing-fig1.png
---

## Abstract

Hillel, Rough, Barrett, Pietro, and Mermut (2024), in *A cautionary tale of
basic azo photoswitching in dichloromethane finally explained*, found that
protonation of 4-phenylazopyridine removes the crossing between the electronic
ground state (S0) and the lowest triplet (T1) along the azo CNNC twist — the
geometry coordinate that takes the molecule from trans toward cis — and wrote
that this "would likely" hold for the wider class of push-pull
azobenzenes.[@Hillel2024] The same group (Hillel, Barrett, Pietro, and Mermut,
2026, *On the unexpected mechanism of isomerization in tautomerizable azo
photoswitches*) later reported no S0/T1 crossing on a different push-pull
scaffold after SF-TDDFT failed and CASSCF/QD-NEVPT2 was used.[@Hillel2026]
This note is an independent constrained scan, at RKS/UKS
B3LYP-D3(BJ)/cc-pVDZ, of that untested 2024 sentence: we ask whether a classic
push-pull azobenzene (4-dimethylamino-4′-nitroazobenzene) still shows an
S0/T1 crossing under our conditions, with azobenzene, AzPy, AzPyH+, and
2-phenylazopyridine as controls.

The registered hypothesis was that M4 would match protonated AzPyH+ (M2) and
show no both-converged S0/T1 sign change on the 15° CNNC grid. The linear
zero of $E(\mathrm{S0})-E(\mathrm{T1})$ for M4 between the both-converged
points at 120° ($\Delta =$ [m4_gap_120]{.metric} kJ/mol) and 105°
($\Delta =$ [m4_gap_105]{.metric} kJ/mol) sits at
[m4_crossing_deg]{.metric}°. M2 has no both-converged crossing; its gaps at
those same angles are [m2_gap_120]{.metric} and [m2_gap_105]{.metric} kJ/mol.
The controls azobenzene, AzPy, and 2-AzPy each retain a trans-side crossing
near 115–116°. The hypothesis was **falsified** under these conditions. That
is a verdict on our hypothesis and this scan, not a grade on either Hillel
paper.

## Introduction

Azobenzene and its derivatives change shape around the N=N azo bond, from a
trans isomer (the two rings opposite, CNNC dihedral 180°) toward a cis isomer
(the rings on the same side, 0°). That torsion is the **CNNC dihedral**. Two
electronic states sit on that path. The **electronic ground state (S0)** is
the closed-shell singlet: all electrons paired, the state the molecule
occupies at equilibrium. The **lowest triplet (T1)** is the lowest state with
two unpaired electrons of the same spin (multiplicity three). A **crossing**
is a geometry on the CNNC path where those two states have the same energy,
$E(\mathrm{S0})=E(\mathrm{T1})$. In this note that is operational:
$E(\mathrm{S0})-E(\mathrm{T1})$ changes sign between neighbouring grid points
that both converged. If the surfaces meet, a thermally moving molecule can
change spin at that geometry and continue on T1; if they never meet, that
multistate rotation path is closed. On azobenzene itself, S0 and T1 are known
to meet along the twist.[@Cembran2004]

Hillel, Rough, Barrett, Pietro, and Mermut computed AzPy and its N-protonated
form AzPyH+ with SF-TDDFT and found that protonation removes that
crossing.[@Hillel2024] They attributed the change to an inductive weakening of
the azo bond, and wrote that the same loss of the crossing "would likely be
observed for quaternized azopyridine derivatives and the wider class of
push-pull azobenzenes." That sentence is a generalization, not a calculation
on a push-pull azobenzene. The same group later studied a different
push-pull scaffold, the tautomerizable dye HPAS: SF-TDDFT was spin-contaminated
near the twist, and a CASSCF/QD-NEVPT2 treatment of deprotonated HPAS found no
S0/T1 crossing.[@Hillel2026] It is not a scan of
4-dimethylamino-4′-nitroazobenzene, and it is not a test of the 2024 sentence
at a single-reference DFT level.

The gap is the 2024 sentence itself. We could not find a published CNNC scan
of a classic donor–acceptor azobenzene — here 4-dimethylamino-4′-nitroazobenzene,
the NMe2/NO2 dye labelled **M4** — that asks whether that molecule still
crosses under a transparent RKS/UKS protocol. The 2026 HPAS surface is the
nearest published neighbour, and it is a different molecule treated with a
different method after SF-TDDFT had already failed. That is the untested
regime.

The hypothesis, written before the M4 T1 continuation finished and not
rewritten afterward: **if the 2024 generalization holds at this level of
theory, M4 shows no S0/T1 crossing on the converged CNNC grid, like
protonated AzPyH+ (M2).** The falsifier, fixed at the same time: M4 shows an
S0/T1 crossing between converged points. Either outcome is publishable. A
missing crossing would be the first same-footing control we have for that
sentence on this dye; a surviving crossing would mean the sentence did not
hold under our conditions.

## Computational Methods

This is an independent implementation. The source authors' ORCA/SF-TDDFT
program was not used, and none of their geometries, orbitals, or energy
tables were imported. Psi4 1.11 has no SF-TDDFT in the build we
used.[@Smith2020Psi4] **S0** was computed restricted Kohn–Sham (RKS);
**T1** was unrestricted Kohn–Sham (UKS). The functional, dispersion, and
basis are B3LYP-D3(BJ)/cc-pVDZ.[@Becke1993Exchange; @Lee1988; @Grimme2011;
@Dunning1989] The CNNC dihedral was frozen in optking and the remaining
degrees of freedom were relaxed. Each surface is a continuation from trans
(180°) toward cis (0°) in 15° steps. The run is gas-phase; no polarizable
continuum was applied.

Five molecules share that protocol. **M0** is azobenzene. **M1** is
4-phenylazopyridine (AzPy). **M2** is N-protonated AzPy (AzPyH+). **M3** is
2-phenylazopyridine. **M4** is 4-dimethylamino-4′-nitroazobenzene. Charge and
multiplicity are 1 1 / 1 3 for M2 and 0 1 / 0 3 for the others. The
canonical executable was
`/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4` on local Apple
Silicon; the environment record is
`research/hillel-triplet/environment.md`. Default UKS output in this build
does not print $\langle S^2\rangle$ (`s2` is null). Near 90° the electronic
structure is expected to be multiconfigurational; Hillel *et al.* flag the
same single-reference limit, and so do we.[@Hillel2024; @Hillel2026]

A crossing is the linear zero of $E(\mathrm{S0})-E(\mathrm{T1})$ on
neighbouring points that both converged. Conversion is 1 Eh = 2625.4996
kJ/mol. Unconverged S0 energies are upper bounds: if those points later
dropped, a still-negative gap would stay negative, and a positive gap built
from an unconverged S0 would become less positive or change sign. That is
why an unconverged point is not a crossing bracket.

The protocol changed once after the first surfaces were seen, and that
change is dated in `research/hillel-triplet/PREREGISTRATION.md`. M4 S0 at
90°, 75°, 60°, and 45° hit the 150-iteration cap. The remaining M4 S0
points at 30°, 15°, and 0° were not started. A reconvergence pass with
maxiter 300 was then run on 90°, 75°, and 60°. The hypothesis was not
changed after T1 was seen. On 2026-08-22, 60° reconverged
($E =$ [m4_s0_60_eh]{.metric} Eh). 90° remained unconverged, moving
[m4_rerun_90_delta_e]{.metric} kJ/mol. 75° remained unconverged, dropped
[m4_rerun_75_drop]{.metric} kJ/mol, and kept a gap of
[m4_rerun_75_gap]{.metric} kJ/mol.

The private-lab journal records that M3 T1 at 45° failed. That slip is left
in the record rather than repaired after the fact. M4 T1 converged at all
[m4_t1_converged_count]{.metric} grid angles. S0 at 30°, 15°, and 0° was
not run.

Raw Psi4 logs stay in the private Molecules lab. They are large and carry
host paths, and they are treated as scratch in the same way as the BMN
frontier-orbital logs. What is committed is the summary projection in
`research/hillel-triplet/results/`. The reproducibility label this directory
has earned is **analysis-reproducible**. It is not end-to-end reproducible
from this public repository.

## Results

Table 1 lists both-converged crossings and the 120°/105° gaps that decide
the claim. Table 2 lists the M4 relative energies from 180° through 45°.
Figure 1 plots the M4 gap, the two M2 gaps at those angles, and
the tabulated trans-side zeros. Figure 2 is the M4 S0 and T1 profiles.
Figure 3 puts the M4 profiles beside the M4 and M2 gaps.

| Molecule | Trans-side crossing (deg) | Other both-converged zeros (deg) | $\Delta$ at 120° (kJ/mol) | $\Delta$ at 105° (kJ/mol) |
| --- | ---: | ---: | ---: | ---: |
| M0 azobenzene | [m0_crossing_upper_deg]{.metric} | [m0_crossing_lower_deg]{.metric}; also [m0_cis_zero_a_deg]{.metric}, [m0_cis_zero_b_deg]{.metric} | — | — |
| M1 AzPy | [m1_crossing_upper_deg]{.metric} | — | — | — |
| M2 AzPyH+ | none ([m2_crossing_count]{.metric}) | — | [m2_gap_120]{.metric} | [m2_gap_105]{.metric} |
| M3 2-AzPy | [m3_crossing_upper_deg]{.metric} | [m3_crossing_lower_deg]{.metric} | — | — |
| M4 NMe2/NO2 | [m4_crossing_deg]{.metric} | — | [m4_gap_120]{.metric} | [m4_gap_105]{.metric} |

**Table 1.** Both-converged S0/T1 zeros and the 120°/105° gaps on the
B3LYP-D3(BJ)/cc-pVDZ CNNC grid. A dash is a quantity that is not a
both-converged neighbour zero in the committed projection. M1 has a
loose interpolant at [m1_crossing_lower_deg]{.metric}° that uses a 45°
bracket: S0 at 90° and 75° did not converge. M3 T1 at 45° failed.
M2 S0 did not converge at 180°, 90°, 75°, 60°, 45°, 30°, 15°, or 0°.

<figure>
  <img src="/images/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing-fig1.png" alt="S0 minus T1 energy gap versus CNNC dihedral for M4, with M2 gaps at 120 and 105 degrees and vertical marks at the tabulated trans-side zeros of M0, M1, M3, and M4.">
</figure>

**Figure 1.** S0 − T1 gap versus CNNC dihedral for M4 (circles,
both-converged; crosses, S0 unconverged), M2 at 120° and 105° (squares),
and the tabulated trans-side zeros of M0, M1, M3, and M4 (dotted
verticals). B3LYP-D3(BJ)/cc-pVDZ, RKS S0 / UKS T1.

The M4 claim crossing is the linear zero between 120°
($\Delta =$ [m4_gap_120]{.metric} kJ/mol; S0
[m4_s0_rel_120]{.metric} kJ/mol, T1 [m4_t1_rel_120]{.metric} kJ/mol) and
105° ($\Delta =$ [m4_gap_105]{.metric} kJ/mol; S0
[m4_s0_rel_105]{.metric} kJ/mol, T1 [m4_t1_rel_105]{.metric} kJ/mol). That
zero is [m4_crossing_deg]{.metric}°. M2 at the same two angles is
[m2_gap_120]{.metric} and [m2_gap_105]{.metric} kJ/mol; both are negative.
M4 T1 converged at [m4_t1_converged_count]{.metric} grid angles.
M4 S0 converged from 180° through 105° and again at 60°; it did not
converge at 90°, 75°, or 45° ([m4_s0_unconverged_count]{.metric} unconverged
S0 points in the projection). [m4_s0_not_run_count]{.metric} further S0
angles (30°, 15°, 0°) were not run.

| CNNC (deg) | S0 (kJ/mol) | T1 (kJ/mol) | S0 converged | T1 converged |
| ---: | ---: | ---: | --- | --- |
| 180 | [m4_s0_rel_180]{.metric} | [m4_t1_rel_180]{.metric} | yes | yes |
| 165 | [m4_s0_rel_165]{.metric} | [m4_t1_rel_165]{.metric} | yes | yes |
| 150 | [m4_s0_rel_150]{.metric} | [m4_t1_rel_150]{.metric} | yes | yes |
| 135 | [m4_s0_rel_135]{.metric} | [m4_t1_rel_135]{.metric} | yes | yes |
| 120 | [m4_s0_rel_120]{.metric} | [m4_t1_rel_120]{.metric} | yes | yes |
| 105 | [m4_s0_rel_105]{.metric} | [m4_t1_rel_105]{.metric} | yes | yes |
| 90 | [m4_s0_rel_90]{.metric} | [m4_t1_rel_90]{.metric} | no | yes |
| 75 | [m4_s0_rel_75]{.metric} | [m4_t1_rel_75]{.metric} | no | yes |
| 60 | [m4_s0_rel_60]{.metric} | [m4_t1_rel_60]{.metric} | yes | yes |
| 45 | [m4_s0_rel_45]{.metric} | [m4_t1_rel_45]{.metric} | no | yes |

**Table 2.** M4 energies relative to the trans S0 minimum. The 60° S0
energy after reconvergence is [m4_s0_60_eh]{.metric} Eh, and the
both-converged gap there is [m4_gap_60]{.metric} kJ/mol. The 90° and 75°
S0 values are the still-unconverged reruns.

<figure>
  <img src="/images/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing-fig2.png" alt="M4 ground-state and lowest-triplet torsion profiles versus CNNC dihedral, with letter A at the interpolated S0/T1 crossing between 120 and 105 degrees.">
</figure>

**Figure 2.** M4 S0 (RKS, circles) and T1 (UKS, squares) versus CNNC
dihedral, energies relative to trans S0. Crosses mark unconverged S0
points. **A** is the linear zero between the both-converged 120° and 105°
points.

At 60° the gap is [m4_gap_60]{.metric} kJ/mol, both-converged. The linear
zero of the 105° / 60° pair is [m4_loose_105_60_zero_deg]{.metric}°. That
pair skips the unconverged S0 points at 90° and 75°.

<figure>
  <img src="/images/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing-fig3.png" alt="Two-panel figure: M4 S0 and T1 profiles on the left, and S0 minus T1 gaps for M4 and for M2 at 120 and 105 degrees on the right, with letter A at the M4 crossing.">
</figure>

**Figure 3.** Left: the M4 profiles of Figure 2. Right: M4 S0 − T1 gap
and the M2 gaps at 120° and 105°. **A** is the M4 120°/105° zero.

## Discussion

The registered hypothesis was **falsified**. M4 has a both-converged
S0/T1 sign change between 120° and 105°, at
[m4_crossing_deg]{.metric}°. M2, the protonated control that the 2024
paper reports as having lost its crossing, stays negative at those same
two angles. The 2024 generalization — that the loss of the crossing
"would likely" extend from AzPyH+ to the wider class of push-pull
azobenzenes — did not hold for this dye, at this level of theory, on
this gas-phase grid.[@Hillel2024]

That is as far as the verdict goes. It is a verdict on our hypothesis and
our scan. It is not a statement that Hillel *et al.* were wrong, and it
is not a rebuttal of the 2026 HPAS paper. The 2026 calculation is
CASSCF/QD-NEVPT2 on a tautomerizable hydroxyquinoline azo dye after
SF-TDDFT had failed; this calculation is RKS/UKS B3LYP-D3(BJ)/cc-pVDZ on
4-dimethylamino-4′-nitroazobenzene.[@Hillel2026] Different scaffold,
different method, different question. If a knowledgeable reader has
already seen this crossing on M4 at a comparable level, we would rather
be told.

The controls behave as a same-footing check of the protocol. M0, M1, and
M3 each keep a trans-side crossing near 115–116°, which is the direction
Cembran *et al.* established for azobenzene and Hillel *et al.* reported
for AzPy.[@Cembran2004; @Hillel2024] M2 does not cross between the two
converged neighbours that decide the claim. Several M2 S0 points,
including trans, did not converge; those unconverged S0 energies remain
upper bounds. Most of those M2 gaps are already negative and can only
become more so if S0 drops; the 60° gap is the exception — positive and
unconverged — and reconverging it can only move that cis-side oscillation
toward or through zero. It cannot invent a trans-side crossing we missed
on the both-converged 120°/105° pair.

Two features of the M4 cis side should not be over-read. First, the
105°→60° sign change interpolates to
[m4_loose_105_60_zero_deg]{.metric}°, but 90° and 75° are unconverged S0
upper bounds, so that zero is not a tight second crossing and is not
claimed as an MECP. Second, M0 has extra both-converged zeros at
[m0_cis_zero_a_deg]{.metric}° and [m0_cis_zero_b_deg]{.metric}° on the
cis-side continuation. Those look like path hysteresis of a constrained
optimizer walking downhill from trans, not a second mechanism.

The limits that would overturn or shrink this reading are the obvious
ones, and they are mostly on our side. The method is single-reference DFT
on a coordinate where S0 and T1 approach each other and where Hillel
*et al.* already warn that a single determinant is a poor
description.[@Hillel2024; @Hillel2026] We have no $\langle S^2\rangle$
from the default UKS output. The run is gas-phase; dichloromethane, the
solvent of the 2024 experiments, is absent. The 90° and 75° S0 points
did not converge even at 300 iterations. We did not locate a
minimum-energy crossing point, and we did not run SF-TDDFT or
CASSCF/QD-NEVPT2 on M4. A solvent model, a spin-pure method, or a
located MECP could move or remove the 120°/105° zero. That would be a
different experiment, and we would treat a discrepancy as something to
chase through our own setup first.

## Conclusion

Under RKS/UKS B3LYP-D3(BJ)/cc-pVDZ, the classic NMe2/NO2 azobenzene still
crosses S0 and T1 on the way from trans toward cis. Protonated AzPy, on
the same grid, does not. The 2024 push-pull sentence did not hold for
this dye under these conditions.

The next experiment on the shelf is not a repair of this scan. Optional
reconvergence of M2 S0 at 90°, 75°, and 60° is not needed for the
claim: the claim is decided by the both-converged 120°/105° pair, not
by those unconverged points. The useful follow-up is one of the two
parked calculations — a two-dihedral
scan of 4-hydroxyazobenzene, or an ORCA SF-TDDFT treatment of M4 — so
that the same molecule can be read with the method the 2024 paper
actually used. Neither has been started. If the right next calculation
is a different one, that is information we do not have, and we would
like to be told.

## References
