---
title: "Does Hillel M4 still show an S0/T1 crossing near 110° under Hillel 2024 SF-TDDFT?"
date: 2026-08-27
author: Peter Johnston
tags: computational chemistry, azobenzene, SF-TDDFT, push-pull chromophores, intersystem crossing
description: An independent rematch of Hillel, Rough, Barrett, Pietro, and Mermut (2024) SF-TDDFT on 4-dimethylamino-4′-nitroazobenzene. The 2026-08-22 RKS/UKS note found a both-converged crossing at 110.5°. This note asks whether that crossing remains when S0 and T1 are taken from the SF-TDDFT manifold at the 2024 electronic-structure level.
post-type: research
contribution: an independent ORCA 6.1.1 SF-TDDFT/TDA BH&HLYP-D3(BJ)/def2-QZVPP constrained CNNC scan of 4-dimethylamino-4′-nitroazobenzene (Hillel M4), which is not in Hillel et al. 2024 and is not the 2026-08-22 RKS/UKS B3LYP-D3(BJ)/cc-pVDZ scan.
contribution-type: untested regime
experiment: hillel-m4-sft
status: supported
og-image: /images/2026-08-27-does-hillel-m4-still-cross-under-sf-tddft-og.png
---

## Abstract

Hillel, Rough, Barrett, Pietro, and Mermut (2024), in *A cautionary tale of basic azo photoswitching in dichloromethane finally explained*, computed 4-phenylazopyridine (AzPy) and its N-protonated form (AzPyH+) with spin-flip time-dependent density functional theory (SF-TDDFT, Tamm–Dancoff) at BH&HLYP-D3(BJ)/def2-QZVPP in ORCA and found that protonation removes the crossing between the electronic ground state (S0) and the lowest triplet (T1) along the azo CNNC twist.[@Hillel2024] They wrote that this loss “would likely be observed for quaternized azopyridine derivatives and the wider class of push-pull azobenzenes.” That sentence was not a calculation on a classic NMe2/NO2 azobenzene.

This note is an independent rematch of that 2024 electronic-structure method on one molecule, 4-dimethylamino-4′-nitroazobenzene (M4). It is not a rebuttal of the 2024 paper or of Hillel, Barrett, Pietro, and Mermut (2026) on HPAS.[@Hillel2026] A prior note on this site asked the same 2024 sentence at RKS/UKS B3LYP-D3(BJ)/cc-pVDZ; on that grid M4 has a both-converged S0/T1 sign change whose interpolant is 110.5° ([published RKS/UKS note](/posts/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing.html)). The registered hypothesis here is that M4 still shows a both-converged S0/T1 crossing near 110° when S0 and T1 are taken from the SF-TDDFT manifold.

The required window (135°, 120°, 105°, 90°) is both-converged and both-assigned at every point. $\Delta E = E(\mathrm{T1})-E(\mathrm{S0})$ changes sign between 90° ([deltae_kjmol_90]{.metric} kJ/mol) and 105° ([deltae_kjmol_105]{.metric} kJ/mol). The linear interpolant is [crossing_phi_deg]{.metric}°. The 105°/120° pair does not change sign ([deltae_kjmol_105]{.metric} and [deltae_kjmol_120]{.metric} kJ/mol). The registered hypothesis was **supported**.

## Introduction

Azobenzene and its derivatives change shape around the N=N azo bond, from a trans isomer (the two rings opposite, CNNC dihedral 180°) toward a cis isomer (the rings on the same side, 0°). That torsion is the **CNNC dihedral**. Two electronic states sit on that path. The **electronic ground state (S0)** is the closed-shell singlet. The **lowest triplet (T1)** is the lowest state with two unpaired electrons of the same spin. A **crossing** is a geometry on the CNNC path where those two states have the same energy. In this note that is operational: $\Delta E = E(\mathrm{T1})-E(\mathrm{S0})$ changes sign between neighbouring grid points that both converged and were both spin-assigned. If the surfaces meet, a thermally moving molecule can change spin at that geometry and continue on T1; if they never meet, that multistate rotation path is closed.

Hillel, Rough, Barrett, Pietro, and Mermut computed AzPy and its N-protonated form AzPyH+ with SF-TDDFT (Tamm–Dancoff) at BH&HLYP-D3(BJ)/def2-QZVPP in ORCA and found that protonation removes that crossing.[@Hillel2024] They wrote that the same loss “would likely be observed for quaternized azopyridine derivatives and the wider class of push-pull azobenzenes.” That sentence is a generalization, not a calculation on a classic NMe2/NO2 azobenzene. The same group later studied a different push-pull scaffold, the tautomerizable dye HPAS: SF-TDDFT was spin-contaminated near the twist, and a CASSCF/QD-NEVPT2 treatment of deprotonated HPAS found no S0/T1 crossing.[@Hillel2026] It is not a scan of 4-dimethylamino-4′-nitroazobenzene, and it is not a rematch of the 2024 electronic-structure method on that dye.

A prior note on this site asked the 2024 sentence at a different level: RKS S0 and UKS T1 at B3LYP-D3(BJ)/cc-pVDZ. On that gas-phase 15° grid, M4 has a both-converged sign change whose interpolant is 110.5°, between 120° and 105° ([published RKS/UKS note](/posts/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing.html)). That note did not run SF-TDDFT. The 2024 method, and the 110.5° zero, are therefore still an untested pairing.

The gap is that pairing. We could not find a published SF-TDDFT CNNC scan of 4-dimethylamino-4′-nitroazobenzene at the 2024 electronic-structure level. The hypothesis, frozen 2026-08-25 before the required window was scored and not rewritten afterward: **M4 still shows a both-converged S0/T1 crossing near 110° when S0 and T1 are taken from the SF-TDDFT manifold.** Three falsifiers were fixed at the same time. (1) $\Delta E$ does not change sign on the required window. (2) The linear interpolant of a sign change lies outside 90–135°. (3) There is no neighbouring both-converged both-assigned pair from which an interpolant can be taken. Either outcome is publishable. A surviving in-window crossing would mean the RKS/UKS 110.5° zero was not an artifact of leaving the 2024 method; a miss would bound that method on this dye.

## Computational Methods

This is an independent implementation. The source authors' geometries, orbitals, and energy tables were not imported. The run uses ORCA 6.1.1; Hillel *et al.* 2024 used ORCA 5.0.3.[@Hillel2024; @Neese2025ORCA6] **S0** and **T1** are assigned from the SF-TDDFT manifold (Tamm–Dancoff) by $\langle S^2\rangle$ and iroot. The functional, dispersion, and basis are LibXC(BHANDHLYP) with D3(BJ) and def2-QZVPP.[@Grimme2011; @Weigend2005Balanced] The Coulomb fit is RIJCOSX. The CNNC dihedral was constrained and the remaining degrees of freedom were relaxed. The required window is 135°, 120°, 105°, and 90°. The run is gas-phase; no polarizable continuum was applied. No minimum-energy crossing point was located. CASSCF/QD-NEVPT2 was not run. M2 was not reconverged. 4-hydroxyazobenzene was not started.

A point counts only if both assigned states converged and both were spin-assigned. A crossing is the linear interpolant of $\Delta E = E(\mathrm{T1})-E(\mathrm{S0})$ on a neighbouring pair that meets that test. Conversion is 1 Eh = 2625.49963831 kJ/mol. The environment record is `research/hillel-m4-sft/environment.md`.

The protocol changed after the freeze, and those changes are dated in `research/hillel-m4-sft/PREREGISTRATION.md`. Native BH&HLYP constrained Opt exited 55; the published window uses LibXC(BHANDHLYP). The committed spin assignment uses a corrected read of the ORCA $\langle S^2\rangle$ lines. S0 at 90° was reseeded from the converged T1 orbitals after the first S0 attempt. Jobs in the required window were paused and relocated; the published numbers are the both-converged both-assigned totals after those interruptions, not a second electronic-structure method. The hypothesis and the three falsifiers were not rewritten after the 90°/105° pair was seen.

Raw ORCA `.out` files stay in the private Molecules lab. They are large and carry host paths, and they are treated as scratch in the same way as the Hillel-triplet Psi4 logs. What is committed is the Bayes projection in `research/hillel-m4-sft/results/bayes-metrics.json`. The reproducibility label this directory has earned is **analysis-reproducible**. It is not end-to-end reproducible from this public repository.

## Results

All four required CNNC points are both-converged and both-spin-assigned. Table 1 lists assigned SF-S0 and SF-T1 totals after the constrained optimizations.

| CNNC (deg) | SF-S0 $E$ (Eh) | SF-S0 $\langle S^2\rangle$ | SF-S0 iroot | SF-T1 $E$ (Eh) | SF-T1 $\langle S^2\rangle$ | SF-T1 iroot | $\Delta E$ (kJ/mol) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 135 | [s0_e_eh_135]{.metric} | [s0_s2_135]{.metric} | [s0_iroot_135]{.metric} | [t1_e_eh_135]{.metric} | [t1_s2_135]{.metric} | [t1_iroot_135]{.metric} | [deltae_kjmol_135]{.metric} |
| 120 | [s0_e_eh_120]{.metric} | [s0_s2_120]{.metric} | [s0_iroot_120]{.metric} | [t1_e_eh_120]{.metric} | [t1_s2_120]{.metric} | [t1_iroot_120]{.metric} | [deltae_kjmol_120]{.metric} |
| 105 | [s0_e_eh_105]{.metric} | [s0_s2_105]{.metric} | [s0_iroot_105]{.metric} | [t1_e_eh_105]{.metric} | [t1_s2_105]{.metric} | [t1_iroot_105]{.metric} | [deltae_kjmol_105]{.metric} |
| 90 | [s0_e_eh_90]{.metric} | [s0_s2_90]{.metric} | [s0_iroot_90]{.metric} | [t1_e_eh_90]{.metric} | [t1_s2_90]{.metric} | [t1_iroot_90]{.metric} | [deltae_kjmol_90]{.metric} |

**Table 1.** Assigned SF-S0 and SF-T1 totals on the required CNNC window after the constrained optimizations. $\Delta E = E(\mathrm{T1})-E(\mathrm{S0})$. LibXC(BHANDHLYP)-D3(BJ)/def2-QZVPP, SF-TDA, RIJCOSX, gas phase.

<figure>
  <img src="/images/2026-08-27-does-hillel-m4-still-cross-under-sf-tddft-og.png" alt="M4 S0/T1 gap ΔE versus constrained CNNC angle φ at 90, 105, 120, and 135 degrees, with the sole interpolant crossing marked between 90 and 105 degrees.">
</figure>

**Figure 1.** M4 S0/T1 gap versus constrained CNNC angle φ. The four both-converged, both-assigned points from the Bayes metrics file (ORCA 6.1.1 SF-TDA, LibXC BHANDHLYP, D3BJ/def2-QZVPP): φ = 90° (ΔE = [deltae_kjmol_90]{.metric} kJ/mol), 105° ([deltae_kjmol_105]{.metric}), 120° ([deltae_kjmol_120]{.metric}), 135° ([deltae_kjmol_135]{.metric}), with ΔE = E(T1) − E(S0). Adjacent both-converged neighbors are joined by straight segments only. The only sign change is on the 90–105 pair; that pair’s linear interpolant is [crossing_phi_deg]{.metric}° and is the sole crossing mark. The 105–120 and 120–135 pairs stay positive and are not marked as crossings. 110° is not marked.

The 90°/105° pair changes sign (Figure 1). The linear interpolant of that pair is [crossing_phi_deg]{.metric}°. The 105°/120° pair does not change sign ([deltae_kjmol_105]{.metric} and [deltae_kjmol_120]{.metric} kJ/mol). The 120°/135° pair does not change sign ([deltae_kjmol_120]{.metric} and [deltae_kjmol_135]{.metric} kJ/mol).

## Discussion

The registered hypothesis was **supported**. Falsifier 1 is [falsifier_1_no_sign_change]{.metric}. Falsifier 2 is [falsifier_2_crossing_outside_90_135]{.metric}. Falsifier 3 is [falsifier_3_no_neighboring_pair]{.metric}. The hypothesis-supported flag is [hypothesis_supported]{.metric}. M4 has a both-converged, both-assigned S0/T1 sign change between 90° and 105°, and the stored interpolant sits inside 90–135°.

That is as far as the verdict goes. It is a verdict on our hypothesis and this window. It is not a statement that Hillel *et al.* were wrong, and it is not a rebuttal of the 2026 HPAS paper. The 2024 calculation is SF-TDDFT on AzPy and AzPyH+; the 2026 calculation is CASSCF/QD-NEVPT2 on a tautomerizable hydroxyquinoline azo dye after SF-TDDFT had failed; this calculation is SF-TDA LibXC(BHANDHLYP)-D3(BJ)/def2-QZVPP on 4-dimethylamino-4′-nitroazobenzene.[@Hillel2024; @Hillel2026] Different scaffold in the source papers, same dye as the 2026-08-22 note, different electronic-structure level than that note. If a knowledgeable reader has already seen this crossing on M4 at a comparable SF-TDDFT level, we would rather be told.

The B3LYP 120°/105° pair that decided the 2026-08-22 note does not change sign under SF ([deltae_kjmol_120]{.metric} and [deltae_kjmol_105]{.metric} kJ/mol). The SF sign change is the 90°/105° pair. The interpolant therefore sits closer to 90° than the RKS/UKS 110.5° zero did. That is a movement of the zero on a coarser, four-point window, not a second method on the same 15° grid.

The limits that would overturn or shrink this reading are mostly on our side. The published functional is LibXC(BHANDHLYP) after native Opt exit 55, not the native BH&HLYP keyword. The program is ORCA 6.1.1, not 5.0.3. The 90° S0 point was reseeded from T1. Jobs were paused and relocated. The committed $\langle S^2\rangle$ assignment uses a corrected parser. The run is gas-phase; dichloromethane, the solvent of the 2024 experiments, is absent. We did not locate a minimum-energy crossing point, and we did not run CASSCF/QD-NEVPT2 on M4. A solvent model, a native-functional repair, a located MECP, or a denser window could move or remove the 90°/105° zero. That would be a different experiment, and we would treat a discrepancy as something to chase through our own setup first.

## Conclusion

Under ORCA 6.1.1 SF-TDA LibXC(BHANDHLYP) D3BJ/def2-QZVPP (RIJCOSX, gas phase), constrained-CNNC M4 has a both-converged, spin-assigned sign change of $\Delta E = E(\mathrm{T1})-E(\mathrm{S0})$ between 90° ([deltae_kjmol_90]{.metric} kJ/mol) and 105° ([deltae_kjmol_105]{.metric} kJ/mol); the linear interpolant is [crossing_phi_deg]{.metric}°, inside 90–135°.

The next experiment on the shelf is not a repair of this window, not a second SF queue, not a reconvergence of M2, and not a start of 4-hydroxyazobenzene. Those remain parked. If the right next calculation is a different one, that is information we do not have, and we would like to be told.

## References
