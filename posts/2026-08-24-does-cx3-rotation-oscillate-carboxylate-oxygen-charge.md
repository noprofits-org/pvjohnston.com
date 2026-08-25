---
title: "Does Johnson's invited CX3 rotation oscillate carboxylate oxygen charge more for CCl3 than for CF3?"
date: 2026-08-24
author: Peter Johnston
tags: computational chemistry, haloacetates, MBIS, hyperconjugation, torsion scan
description: An independent B3LYP-D3(BJ)/aug-cc-pVDZ rematch and relaxed CX3 rotation of CF3COO− and CCl3COO−, taking the geometry/bond-rotation invitation in Johnson et al. 2025. Binding charges are MBIS.
post-type: research
contribution: A relaxed CX3 rotation of CF3COO− and CCl3COO− at B3LYP-D3(BJ)/aug-cc-pVDZ, which is not in Johnson 2025, falsifies our registered hypothesis that MBIS carboxylate oxygen charge oscillates with a larger amplitude for CCl3 than for CF3.
contribution-type: untested regime
experiment: johnson-haloacetate
og-image: /images/2026-08-24-does-cx3-rotation-oscillate-carboxylate-oxygen-charge-fig1.png
---

## Abstract

Johnson, Gregory, Robertson, Gresham, Nelson, Craig, Prescott, Page,
Webber, and Wanless (2025), in *The inductive effect does not explain
electron density in haloacetates: are our textbooks wrong?*, reported
DDEC6/MP2/aug-cc-pVQZ charges in which CCl3 withdraws more from the
carboxylate oxygens than CF3, proposed carboxylate π → σ*(C–X)
hyperconjugation, cited ESI Table S2 bond-length signs, and invited
geometry/bond rotation studies.[@Johnson2025] This note is an independent
relaxed CX3 scan, at B3LYP-D3(BJ)/aug-cc-pVDZ with MBIS charges, of that
invitation: we ask whether carboxylate oxygen charge oscillates with
CX3 rotation, with larger amplitude for CCl3COO− than for CF3COO−.

The registered hypothesis was that Hirshfeld and MBIS oxygen charges
(and the COO sum) oscillate with the X–Cα–C–O dihedral, with
peak-to-peak amplitude larger for CCl3COO− than for CF3COO−. On the
both-converged 0–120° grids the MBIS $q(\mathrm{O})$ amplitudes are
[amp_q_o_cf3]{.metric} e (CF3) and [amp_q_o_ccl3]{.metric} e (CCl3).
The $q(\mathrm{COO})$ amplitudes are [amp_q_coo_cf3]{.metric} e and
[amp_q_coo_ccl3]{.metric} e. After the scan we scored falsifier 2 on
$q(\mathrm{O})$; [q_o_amp_ccl3_gt_cf3]{.metric}. The hypothesis is
**falsified** (not supported). That is a verdict on our hypothesis and
this scan, not a grade on Johnson et al.

## Introduction

Haloacetate ions, $\mathrm{CX_3COO^-}$, are a standard classroom
example of the inductive effect: a more electronegative $\mathrm{CX_3}$
group is expected to withdraw electron density from the carboxylate
and to lower $\mathrm{p}K_\mathrm{a}$. Johnson, Gregory, Robertson,
Gresham, Nelson, Craig, Prescott, Page, Webber, and Wanless computed
gas-phase trihaloacetates at MP2/aug-cc-pVQZ and partitioned the
density with DDEC6.[@Johnson2025] They reported the opposite order for
the carboxylate oxygen charges: CCl3 withdraws more than CF3. They
attributed that pattern to carboxylate $\pi \rightarrow \sigma^*(\mathrm{C{-}X})$
hyperconjugation, noted that ESI Table S2 shows a larger in-plane
versus out-of-plane C–X length difference for CCl3 than for CF3, and
wrote that further computational work including geometry/bond rotation
studies could help elucidate the role of that hyperconjugation.

That sentence is an invitation, not a published rotation. We could not
find a relaxed $\mathrm{CX_3}$ scan of CF3COO− and CCl3COO− that asks
whether the carboxylate oxygen charge moves with the torsion, or
whether that motion is larger for CCl3. The 2025 minima and the ESI
bond-length signs are the nearest published neighbours, and they are
not a scan. That is the untested regime.

The hypothesis, frozen 2026-08-23 before any rematch energy or
torsion: **On a relaxed CX3 rotation, Hirshfeld and MBIS oxygen
charges (and the COO sum) oscillate with the X–Cα–C–O dihedral.
Peak-to-peak amplitude is larger for CCl3COO− than for CF3COO−.
Acetate is the flat control.** Amplitude is $\max-\min$ on
both-converged points, reported separately for $q(\mathrm{O})$ and
$q(\mathrm{COO})$. The falsifier, fixed at the same time: (1)
$q(\mathrm{O})$ is flat vs dihedral on both haloacetates, or (2) CF3
amplitude $\ge$ CCl3 amplitude. Either outcome is publishable. A
larger CCl3 swing would be the first same-footing rotation bound we
have for the 2025 invitation; a miss would mean this independent scan
did not exhibit the predicted CCl3 $>$ CF3 oxygen-charge amplitude.

## Computational Methods

This is an independent implementation. The source authors' MP2
geometries, orbitals, DDEC6 charges, and energy tables were not
imported, and none of their program was used.[@Johnson2025] Psi4 1.11
was the executable.[@Smith2020Psi4] Each ion is charge $-1$, singlet,
gas-phase. No polarizable continuum was applied. The functional,
dispersion, and basis are B3LYP-D3(BJ)/aug-cc-pVDZ.[@Becke1993Exchange;
@Lee1988; @Grimme2011; @Dunning1989; @Kendall1992; @Woon1993] Binding
charges are **MBIS**.[@Verstraelen2016] **Löwdin** charges are reported
only and are not binding.[@Lowdin1950] **Hirshfeld** partitioning is
not compiled into this Psi4 build.[@Hirshfeld1977]

Four ions were rematched first, before any torsion: CH3COO−, CF3COO−,
CClF2COO−, and CCl3COO−. The rematch geometry inequalities were:
$r(\mathrm{C{-}C})$ satisfies CCl3 $>$ CF3 $>$ acetate, and
$\Delta(\mathrm{C{-}X})$ (out-of-plane minus in-plane) satisfies
CCl3 $>$ CF3. CClF2 is mixed-halogen and is not used for the
$\Delta(\mathrm{C{-}X})$ comparison. Before the first rematch energy,
Hirshfeld was already unavailable in this Psi4 build, so gate (3)
required both MBIS and Löwdin $q(\mathrm{O})$ and $q(\mathrm{COO})$ to
be more negative for CF3 than for CCl3; if both failed, the scan would
not run.

After rematch charges were known, and before any torsion, Löwdin on
aug-cc-pVDZ reversed the CF3/CCl3 oxygen-charge order and is
ill-defined on this basis relative to MBIS. Löwdin was demoted; binding
became MBIS-only; the both-must-pass / if-both-fail-stop pair was
vacated. That amendment is dated 2026-08-24 in
`research/johnson-haloacetate/JOURNAL.md`. The frozen hypothesis and
falsifier were not rewritten.

The scan is a relaxed $\phi = \mathrm{X{-}C_\alpha{-}C{-}O}$
continuation. Optking froze dihedral 5-4-1-2. The remaining degrees of
freedom were relaxed. The grid is 0–120° in
[scan_step_deg]{.metric}° steps on CF3COO− (M1) and CCl3COO− (M3).
The published abscissa is the frozen target `angle`. A hopping realized
dihedral is not used as the $x$ coordinate. Published $q(\mathrm{O})$
is the arithmetic mean of the two carboxylate oxygen MBIS charges, not
one selected atom. The frozen dihedral uses atom 2 as the constraint;
both oxygens still enter the mean. $q(\mathrm{COO})$ is the
carboxylate-group sum. Amplitude is $\max-\min$ on points with
optking True and a clean exit. Energies are converted with
[eh_to_kcal]{.metric} kcal mol$^{-1}$ $E_\mathrm{h}^{-1}$. The 120°
minus 0° difference is an overlay check on the same conversion. It is
not the amplitude.

The canonical executable was
`/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/psi4` on local
Apple Silicon; the environment record is
`research/johnson-haloacetate/environment.md`. Raw Psi4 logs stay in
the private Molecules lab. They are large and carry host paths, and
they are treated as scratch in the same way as the Hillel-triplet
logs. What is committed is the rematch table and the two scan CSVs in
`research/johnson-haloacetate/`. The reproducibility label this
directory has earned is **analysis-reproducible**. It is not
end-to-end reproducible from this public repository.

## Results

Table 1 lists the rematch gate. Table 2 lists the scan amplitudes,
signed $120^\circ-0^\circ$ charge differences, and energy ranges. Figure 1 plots MBIS
$q(\mathrm{O})$ and $q(\mathrm{COO})$ versus the frozen target angle.
Figure 2 plots the relative electronic energy.

| Ion | $r(\mathrm{C{-}C})$ (Å) | $\Delta(\mathrm{C{-}X})$ (Å) | MBIS $q(\mathrm{O})$ (e) | MBIS $q(\mathrm{COO})$ (e) | Converged |
| --- | ---: | ---: | ---: | ---: | --- |
| CH3COO− | [r_cc_acetate]{.metric} | — | — | — | yes |
| CF3COO− | [r_cc_cf3]{.metric} | [delta_cx_cf3]{.metric} | [rematch_q_o_cf3]{.metric} | [rematch_q_coo_cf3]{.metric} | yes |
| CClF2COO− | [r_cc_cclf2]{.metric} | — | — | — | yes |
| CCl3COO− | [r_cc_ccl3]{.metric} | [delta_cx_ccl3]{.metric} | [rematch_q_o_ccl3]{.metric} | [rematch_q_coo_ccl3]{.metric} | yes |

**Table 1.** Rematch B3LYP-D3(BJ)/aug-cc-pVDZ optimizations.
$\Delta(\mathrm{C{-}X})$ is out-of-plane minus in-plane. A dash is a
quantity that is not in the committed rematch table: acetate has no
C–X pair of that kind, and CClF2 is mixed. All
[rematch_n_converged]{.metric} of [rematch_n_ions]{.metric}
optimizations formally converged. The predeclared inequalities evaluate
to [rematch_cc_order_pass]{.metric} for $r(\mathrm{C{-}C})$,
[rematch_delta_cx_pass]{.metric} for $\Delta(\mathrm{C{-}X})$,
[rematch_q_o_pass]{.metric} for MBIS $q(\mathrm{O})$, and
[rematch_q_coo_pass]{.metric} for MBIS $q(\mathrm{COO})$.

[n_scan_converged]{.metric} of [n_scan_points]{.metric} scan points
converged (optking True and a clean exit).

<figure>
  <img src="/images/2026-08-24-does-cx3-rotation-oscillate-carboxylate-oxygen-charge-fig1.png" alt="Two-panel plot of MBIS carboxylate oxygen charge and carboxylate-group charge versus frozen CX3 dihedral for CF3COO− and CCl3COO−, each series shown as a deviation from its mean.">
</figure>

**Figure 1.** MBIS $q(\mathrm{O})$ (left) and $q(\mathrm{COO})$
(right) versus frozen $\phi$ for CF3COO− (circles) and CCl3COO−
(squares), each series as a deviation from its own mean. Absolute
scan-mean $q(\mathrm{O})$ is [mean_q_o_cf3]{.metric} e (CF3) and
[mean_q_o_ccl3]{.metric} e (CCl3); scan-mean $q(\mathrm{COO})$ is
[mean_q_coo_cf3]{.metric} e and [mean_q_coo_ccl3]{.metric} e.
B3LYP-D3(BJ)/aug-cc-pVDZ. Solid lines join 15° neighbours. All plotted
points converged.

| Quantity | CF3COO− | CCl3COO− |
| --- | ---: | ---: |
| $q(\mathrm{O})$ amplitude (e) | [amp_q_o_cf3]{.metric} | [amp_q_o_ccl3]{.metric} |
| $q(\mathrm{COO})$ amplitude (e) | [amp_q_coo_cf3]{.metric} | [amp_q_coo_ccl3]{.metric} |
| signed $q(\mathrm{O})$ $120^\circ-0^\circ$ (e) | [repeat_q_o_cf3]{.metric} | [repeat_q_o_ccl3]{.metric} |
| signed $q(\mathrm{COO})$ $120^\circ-0^\circ$ (e) | [repeat_q_coo_cf3]{.metric} | [repeat_q_coo_ccl3]{.metric} |
| $E$ range ($E_\mathrm{h}$) | [barrier_eh_cf3]{.metric} | [barrier_eh_ccl3]{.metric} |
| $E$ range (kcal/mol) | [barrier_kcal_cf3]{.metric} | [barrier_kcal_ccl3]{.metric} |
| $E(120^\circ)-E(0^\circ)$ (kcal/mol) | [overlay_kcal_cf3]{.metric} | [overlay_kcal_ccl3]{.metric} |

**Table 2.** Peak-to-peak MBIS amplitudes, signed $120^\circ-0^\circ$
charge differences, and electronic-energy ranges on the both-converged
scan. Conversion is [eh_to_kcal]{.metric} kcal mol$^{-1}$
$E_\mathrm{h}^{-1}$. The largest of the four charge amplitudes is
[max_charge_amp]{.metric} e.

<figure>
  <img src="/images/2026-08-24-does-cx3-rotation-oscillate-carboxylate-oxygen-charge-fig2.png" alt="Relative electronic energy versus frozen CX3 dihedral for CF3COO− and CCl3COO−, each series referenced to its own scan minimum, in kilocalories per mole.">
</figure>

**Figure 2.** Electronic energy versus frozen $\phi$, relative to each
ion's scan minimum. CF3COO− circles; CCl3COO− squares.
B3LYP-D3(BJ)/aug-cc-pVDZ. Solid lines join 15° neighbours.

The $q(\mathrm{O})$ comparison CCl3 amplitude $>$ CF3 amplitude
evaluates to [q_o_amp_ccl3_gt_cf3]{.metric}. The $q(\mathrm{COO})$
comparison evaluates to [q_coo_amp_ccl3_gt_cf3]{.metric}. The
hypothesis-supported flag, scored on $q(\mathrm{O})$ after the scan, is
[hypothesis_supported]{.metric}. Absolute overlay checks are
[overlay_kcal_cf3_abs]{.metric} kcal/mol (CF3) and
[overlay_kcal_ccl3_abs]{.metric} kcal/mol (CCl3).

## Discussion

The registered hypothesis is **falsified** (not supported). On this
grid the CCl3 $q(\mathrm{O})$ amplitude is not larger than the CF3
$q(\mathrm{O})$ amplitude: [amp_q_o_ccl3]{.metric} e versus
[amp_q_o_cf3]{.metric} e. Falsifier 2, scored on oxygen charge,
fires. $q(\mathrm{COO})$ is the other way around —
[amp_q_coo_ccl3]{.metric} e versus [amp_q_coo_cf3]{.metric} e — and is
disclosed here rather than substituted for the named question after
the split was seen. The largest of the four amplitudes is
[max_charge_amp]{.metric} e. Oscillation, if any, is at that scale.
The signed $120^\circ-0^\circ$ overlay on the CCl3 $q(\mathrm{O})$
series is [repeat_q_o_ccl3]{.metric} e; that endpoint difference is
not the peak-to-peak amplitude. We falsified the hypothesis we
registered. Johnson et al. invited this rotation; they did not publish
this amplitude.

After both grids were in hand, on 2026-08-24, we did not pick one
after seeing they split. The question named oxygen charge, so
falsifier 2 is scored on $q(\mathrm{O})$. $q(\mathrm{COO})$ is
disclosed alongside. That call is post-scan and is dated in
`research/johnson-haloacetate/JOURNAL.md`. It is not a silent edit to
the frozen falsifier.

That is as far as the verdict goes. It is a verdict on our hypothesis
and our scan. It is not a statement that Johnson et al. were wrong, and
it is not a claim that hyperconjugation is absent at their
DDEC6/MP2/aug-cc-pVQZ minima.[@Johnson2025] Different method, different
charge scheme, different question. This scan does not test a
$\mathrm{p}K_\mathrm{a}$ mechanism. If a knowledgeable reader has
already seen a larger CCl3 oxygen-charge swing on a comparable
rotation, we would rather be told.

The rematch gate was met before the torsion: $r(\mathrm{C{-}C})$ and
$\Delta(\mathrm{C{-}X})$ run CCl3 $>$ CF3, and MBIS $q(\mathrm{O})$ and
$q(\mathrm{COO})$ are more negative for CF3. That is the same
qualitative charge order Johnson et al. reported at their level, on a
different functional, basis, and partition.[@Johnson2025] It is a gate,
not a reproduction of their table.

The binding-scheme amendment belongs here, not in Results. After
rematch charges were known, and before any torsion, Löwdin on
aug-cc-pVDZ reversed the CF3/CCl3 oxygen-charge order and sat near
zero while MBIS sat near [rematch_q_o_cf3]{.metric} e /
[rematch_q_o_ccl3]{.metric} e.[@Lowdin1950; @Verstraelen2016] Hirshfeld
is absent from this Psi4 build.[@Hirshfeld1977] The binding scheme was
restricted to MBIS-only on 2026-08-24. The frozen hypothesis and
falsifier were not rewritten. A reader who would have kept Löwdin as
binding should treat that as a post-observation gate edit and stop
there.

The limits that would overturn or shrink this reading are mostly on
our side. The method is B3LYP-D3(BJ)/aug-cc-pVDZ, not MP2/aug-cc-pVQZ.
The partition is MBIS, not DDEC6. The run is gas-phase. The grid is
[scan_step_deg]{.metric}°. The energy ranges are
[barrier_kcal_cf3]{.metric} and [barrier_kcal_ccl3]{.metric} kcal/mol;
a surface that flat can move last-digit charges with grid, optimizer,
or BLAS. Acetate was rematched and not scanned, so the “acetate flat”
clause of the hypothesis was not tested on a torsion. A DDEC6 or
Hirshfeld scan at the 2025 level, or a finer $\phi$ grid, could move
the amplitudes. That would be a different experiment, and we would
treat a discrepancy as something to chase through our own setup first.

## Conclusion

Under B3LYP-D3(BJ)/aug-cc-pVDZ, MBIS, and gas phase, the CX3 rotation
does not move carboxylate oxygen charge with a larger amplitude for
CCl3COO− than for CF3COO−. The hypothesis we registered is not
supported. Oscillation, if any, is [max_charge_amp]{.metric} e.

The next experiment on the shelf is not a repair of this scan. The
useful follow-up is the same relaxed $\phi$ grid with DDEC6 at
MP2/aug-cc-pVQZ, or with Hirshfeld in a Psi4 build that has it, so
that the charge scheme and the wavefunction sit on the footing Johnson
et al. actually used.[@Johnson2025] Neither has been started. If the
right next calculation is a different one, that is information we do
not have, and we would like to be told.

## References
