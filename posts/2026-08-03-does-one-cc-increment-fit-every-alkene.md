---
title: "Does one C=C increment fit every alkene? Two preregistered tests of Witkowski and co-workers' correlation energy per bond"
date: 2026-08-03
author: Peter Johnston
tags: quantum chemistry, electron correlation, coupled cluster, bond increments, transferability, reproducibility
description: Witkowski, Śmiga, Hirata, Dral and Grabowski estimate molecular correlation energies as a sum of fitted bond-type increments and state that the assignment holds regardless of conjugation or geometry. This note is an independent reanalysis of their published tables plus a new coupled-cluster calculation on the four butene isomers their model cannot distinguish. Both preregistered verdicts came out inconclusive under the frozen decision rules; what survives is a systematic offset in the price of one bond swap and a measurable correlation split among isomers the model assigns identical energies.
post-type: research
contribution: The spread and systematic offset of the C=C → C–C + 2 C–H correlation-energy swap across Witkowski and co-workers' own published tables, and coupled-cluster correlation-energy differences among the four C4H8 positional isomers to which CEPB assigns identical correlation energies — neither of which is in Witkowski et al.
contribution-type: quantification
experiment: cepb-increment-spread
---

## Abstract

Witkowski, Śmiga, Hirata, Dral, and Grabowski, in *Ultrafast Correlation
Energy Estimator* (*J. Phys. Chem. A* **129** (2025) 8877–8890), estimate a
molecule's correlation energy as a sum of fitted bond-type increments —
"correlation energy per bond" (CEPB) — and state that the assignment holds
regardless of bond length, bond angle, hybridization, or π-electron
conjugation.[@Witkowski2025] This note is an independent reanalysis of their
published data plus an independent extension, under a protocol frozen before
the first calculation. Arm A reanalyzes the source's own published
per-molecule correlation energies: three pairs in its tables differ by exactly
the same bond-count swap, C=C → C–C + 2 C–H, so CEPB assigns all three the
same correlation change, and the spread across the three measured changes
tests the transferability claim on the source's own numbers. Arm B is new
quantum chemistry: frozen-core DF-CCSD(T) correlation energies for the four
C₄H₈ positional isomers, which carry identical CEPB bond counts and therefore
identical predicted correlation energies, at two basis sets. Under the
registered decision rules both arms returned **inconclusive**. The Arm A
spread is [swap_spread_cbs]{.metric}\ kcal/mol at the source's CBS reference
level but [swap_spread_qz]{.metric} and [swap_spread_tz]{.metric}\ kcal/mol at
the two finite bases, so the basis levels disagree about the registered
1.0 kcal/mol threshold; in Arm B, one pairwise difference changed sign between
the two bases, which the frozen rule treats as disqualifying. Two findings are
nonetheless stable across everything run here. All three Arm A contrasts lie
on the same side of the CEPB prediction, by [swap_dev_nearest_cbs]{.metric} to
[swap_dev_farthest_cbs]{.metric}\ kcal/mol at CBS — a systematic offset in the
swap's price rather than an environment dependence. And isobutene is the most
strongly correlated C₄H₈ isomer at both bases, separated from trans-2-butene
by [pair_isobutene_minus_trans2butene_dz]{.metric} and
[pair_isobutene_minus_trans2butene_tz]{.metric}\ kcal/mol against a predicted
difference of exactly zero.

## Introduction

The idea that electron correlation is approximately local, and therefore
approximately additive over chemical substructures, is old and productive:
correlation energies of homologous series grow nearly linearly, and pair
theories make the locality precise.[@HelgakerJorgensenOlsen2000] The open
question is never whether such additivity roughly holds but how far it can be
pushed before chemistry pushes back. Two recent papers push it far. Witkowski,
Śmiga, Hirata, Dral, and Grabowski fit 33 bond-type increments to
CCSD(T)-level correlation energies of 84 molecules and estimate any molecule's
correlation energy as the sum over its dominant Lewis structure's bonds — a
scheme they name correlation energy per bond (CEPB) — with the abstract-level
claim that each increment applies "regardless of the bond length, bond angle,
sp-hybridization, π-electron conjugation, ionicity, noncovalent interactions,
etc."[@Witkowski2025] Independently, Vincent and Popelier report that
fragment-level correlation energies at CCSD(T) are transferable within a few
percent and recommend them as machine-learning targets.[@Vincent2026Transferability]
Transferability of correlation increments is, in other words, a live working
assumption in the current literature, not a settled fact.

A one-number-per-bond-type model makes two sharp, parameter-free predictions.
First, any two molecules that differ by the same bond-count change must differ
by the same correlation energy: the swap C=C → C–C + 2 C–H costs
$e_{\mathrm{CC}} + 2e_{\mathrm{CH}} - e_{\mathrm{C=C}}$ wherever it occurs,
whether the C=C sits in ethene, in a conjugated ring, or next to a saturated
ring. Second, molecules with identical bond counts must have identical
correlation energies: the four C₄H₈ positional isomers — 1-butene,
cis-2-butene, trans-2-butene, and isobutene — each carry one C=C, two C–C,
and eight C–H bonds, so CEPB assigns them one correlation energy and predicts
a correlation contribution of exactly zero to every isomerization among them.
The source states this second consequence plainly, noting that CEPB "fails to
differentiate positional isomers" and that such isomerization energies
collapse to the Hartree–Fock values; what it does not do is measure the size
of the resulting error, and its published accuracy statistics are
whole-molecule percentages, which do not answer either question. A
[previous note in this series](/posts/2026-07-23-is-hydrogenation-correlation-transferable.html)
found that reaction-level correlation contributions to hydrogenation change
substantially between reactions whose starting bond orders differ, which left
the sharper within-one-bond-order-class question open — and the source's own
tables contain the data to ask it.

The hypothesis, frozen with its thresholds before any number was computed:
**the transferability fails at chemical accuracy.** Concretely, Arm A predicts
that the three published instances of the C=C → C–C + 2 C–H swap do not share
one value — their spread exceeds 1.0 kcal/mol; Arm B predicts that at least
one pairwise correlation-energy difference among the four C₄H₈ isomers
exceeds 1.0 kcal/mol in magnitude. The falsifiers were fixed in advance: the
hypothesis dies in Arm A if the contrast spread is at or below 1.0 kcal/mol at
every basis level the source publishes, and in Arm B if all six pairwise
differences stay below 1.0 kcal/mol at the registered level and under its
basis-sensitivity check. The 1.0 kcal/mol threshold is this experiment's
operational bar for a chemically material difference, chosen before any
calculation; the source does not claim chemical accuracy and states no
accuracy budget of its own. Either outcome was worth publishing — a spread
within chemical accuracy would strengthen the source's assignment on molecules
it never fitted, and a measured spread would bound how far the assumption can
be pushed. If the registered basis levels disagreed about a threshold, or a
registered method-fidelity gate failed, the result was to be reported as
inconclusive rather than repaired, and both of those rules ended up binding.

## Computational Methods

**Source inputs.** All Arm A quantities are arithmetic on values transcribed
from the source: the fitted bond-type increments (main-text Table 2) and the
per-molecule correlation energies of the training and test sets at three
levels — CBS, aug-cc-pVQZ, and aug-cc-pVTZ (main-text Tables 3 and 4;
Supporting Information Tables S1, S2, S4, S5). Every transcribed value is
all-electron, as those tables declare; the source's frozen-core table covers
only its training set and is not used. The transcription was frozen in the
experiment's `inputs.json` before analysis, with each value carrying its
declared basis level, and increments are only ever combined with molecular
energies of the same declared level. The SHA-256 fingerprint of the frozen
transcription is recorded in the committed metrics provenance. Nothing in
this note reruns, refits, or re-extrapolates any calculation of the source's;
the source authors' code and data were used only as published numbers.

**Arm A.** The registered molecule set is every unsaturated hydrocarbon in
the source's tables whose Lewis structure contains at least one C=C and only
C–C, C=C, and C–H bond types: ethene, cyclopropene, allene, 1,3-butadiene,
cyclobutene, cyclohexene, and 1,4-cyclohexadiene, with methane, ethane, and
cyclohexane as saturated references. Benzene is analysed separately and never
pooled, because dominant-Lewis-structure bond counts are convention-dependent
for an aromatic ring. The originally registered Arm A statistic was the raw
effective increment

$$
e^{\mathrm{eff}}_{\mathrm{C=C}}(X) \;=\;
\frac{E_{\mathrm{corr}}(X) - n_{\mathrm{CH}}\,e_{\mathrm{CH}}
      - n_{\mathrm{CC}}\,e_{\mathrm{CC}}}{n_{\mathrm{C=C}}},
$$

evaluated with the source's own fitted increments. During design review —
with the CBS value of that statistic already hand-evaluated, a fact disclosed
in the research journal and in the preregistration's amendment before any
contrast was computed — an objection was raised independently by an automated
reviewer and by the review itself: this quantity attributes a molecule's
*entire* CEPB residual to its C=C bonds, so its spread grows with molecule
size whether or not the C=C assignment itself varies. The preregistration was
therefore amended before any contrast value existed: the raw statistic was
demoted to a secondary, descriptive result, and the primary Arm A metric
became a contrast in which every other bond class cancels exactly. Three
pairs in the source's tables differ by precisely the swap
C=C → C–C + 2 C–H — ethene → ethane, 1,4-cyclohexadiene → cyclohexene, and
cyclohexene → cyclohexane — and CEPB assigns all three the identical
correlation change $e_{\mathrm{CC}} + 2e_{\mathrm{CH}} - e_{\mathrm{C=C}}$.
The primary statistic is the spread of the three measured changes, required
to clear the threshold at every published basis level. Both statistics are
reported below in the order they were derived.

**Arm B.** New calculations, run with Psi4 1.9.1:[@Smith2020Psi4] each of the
four C₄H₈ isomers (with ethene and propene as secondary members that do not
enter the verdict) was optimized with frozen-core density-fitted
MP2/cc-pVTZ[@MollerPlesset1934; @Dunning1989] from a committed starting
structure, followed by frozen-core density-fitted CCSD(T)[@Raghavachari1989]
at that geometry, with the correlation energy taken from Psi4's
`CCSD(T) CORRELATION ENERGY` variable and all six pairwise differences
formed. The registered basis-sensitivity check repeats the whole procedure at
cc-pVDZ. The Arm B verdict stands only if every pairwise difference keeps its
sign between the two bases and no pair crosses the 1.0 kcal/mol threshold in
opposite directions. Registered method-fidelity gates: every optimization and
CCSD(T) run converges, every optimized structure retains the intended
isomer's heavy-atom connectivity, and the largest T1 diagnostic stays at or
below 0.02.[@Lee1989Diagnostic]

**Boundary.** The source's reference level — all-electron CCSD(T) at
aug-cc-pVTZ and aug-cc-pVQZ with a two-point CBS extrapolation — was not
reproduced: aug-cc-pVTZ on a C₄H₈ isomer is 368 basis functions, out of
budget on the hardware below. Arm B therefore measures whether the
exactly-zero prediction survives at a consistent correlated level, not what
the source's own protocol would return for these molecules. No conformer
search and no frequency confirmation were part of the frozen protocol; each
isomer is represented by the single stationary point reached from its
committed starting structure. One post-hoc diagnostic outside the frozen
protocol is reported as such in the Discussion.

**Environment.** The registered run executed 2026-08-03 on Ubuntu 24.04.4
(x86_64) with CPython 3.10.13, Psi4 1.9.1, and NumPy 1.26.4 from the
committed conda lock, using 7 threads and 9 GB of memory, with energy and
density convergence at 10^−9^; the full registered set is under an hour of
wall time. The analysis layer (`analyze.py`) regenerates deterministically
from the committed run records without rerunning quantum chemistry, and its
`--check` mode byte-compares the committed `results.json`. The experiment
bundle — preregistration with its amendment, frozen inputs, runner, raw Psi4
outputs, canonical results, and fingerprinted metrics — is published under
[`research/cepb-increment-spread/`](/research/cepb-increment-spread/README.md).
The reproducibility level this earns is end-to-end reproducible on
linux-x86_64 from the committed lock, and analysis-reproducible from the
committed outputs elsewhere.

## Results

Every registered method-fidelity gate passed: all twelve optimizations and
CCSD(T) calculations terminated normally, every optimized structure retains
its intended isomer's heavy-atom connectivity, and the largest T1 diagnostic across the C₄H₈ set is
[armb_max_t1_tz]{.metric} at cc-pVTZ and [armb_max_t1_dz]{.metric} at
cc-pVDZ, against the registered ceiling of 0.02.

Table 1 reports the Arm A contrasts. The spread across the three measured
swap values is [swap_spread_cbs]{.metric}\ kcal/mol at CBS,
[swap_spread_qz]{.metric}\ kcal/mol at aug-cc-pVQZ, and
[swap_spread_tz]{.metric}\ kcal/mol at aug-cc-pVTZ, against the registered
threshold of 1.0 kcal/mol: at or below the threshold at CBS, above it at both
finite bases. At every level, all three measured values are more negative
than the CEPB prediction, by [swap_dev_nearest_cbs]{.metric} to
[swap_dev_farthest_cbs]{.metric}\ kcal/mol at CBS, by
[swap_dev_nearest_qz]{.metric} to [swap_dev_farthest_qz]{.metric}\ kcal/mol
at aug-cc-pVQZ, and by [swap_dev_nearest_tz]{.metric} to
[swap_dev_farthest_tz]{.metric}\ kcal/mol at aug-cc-pVTZ.

| ΔE~corr~ for C=C → C–C + 2 C–H (kcal/mol) | CBS | aug-cc-pVQZ | aug-cc-pVTZ |
| --- | ---: | ---: | ---: |
| ethene → ethane | [swap_ethene_ethane_cbs]{.metric} | [swap_ethene_ethane_qz]{.metric} | [swap_ethene_ethane_tz]{.metric} |
| 1,4-cyclohexadiene → cyclohexene | [swap_cyclohexadiene_cyclohexene_cbs]{.metric} | [swap_cyclohexadiene_cyclohexene_qz]{.metric} | [swap_cyclohexadiene_cyclohexene_tz]{.metric} |
| cyclohexene → cyclohexane | [swap_cyclohexene_cyclohexane_cbs]{.metric} | [swap_cyclohexene_cyclohexane_qz]{.metric} | [swap_cyclohexene_cyclohexane_tz]{.metric} |
| CEPB prediction, all rows | [cepb_swap_cbs]{.metric} | [cepb_swap_qz]{.metric} | [cepb_swap_tz]{.metric} |
| spread across the three contrasts | [swap_spread_cbs]{.metric} | [swap_spread_qz]{.metric} | [swap_spread_tz]{.metric} |

**Table 1.** Correlation-energy change of the C=C → C–C + 2 C–H swap in the
three published pairs that realize it, computed from the source's per-molecule
correlation energies at each of its three published levels, with the single
CEPB-predicted value and the spread across the three measured changes.

The secondary, descriptive statistic — the raw effective C=C increment of the
amendment, which assigns each molecule's whole CEPB residual to its C=C
bonds — spans [raw_spread_cbs]{.metric}\ kcal/mol across the seven-molecule
set at CBS, [raw_spread_qz]{.metric}\ kcal/mol at aug-cc-pVQZ, and
[raw_spread_tz]{.metric}\ kcal/mol at aug-cc-pVTZ, with cyclohexene at one
extreme and ethene at the other at every level. Benzene's Kekulé-counted
effective increment falls inside the range spanned by the nonaromatic set at
each level.

Table 2 reports the Arm B pairwise differences. The largest magnitude is
[armb_max_abs_tz]{.metric}\ kcal/mol at cc-pVTZ and
[armb_max_abs_dz]{.metric}\ kcal/mol at cc-pVDZ. Isobutene has the most
negative correlation energy of the four isomers at both bases, and
trans-2-butene the least negative. Five of the six pairs keep their sign
between the two bases; the cis-2-butene − 1-butene pair is
[pair_cis2butene_minus_1butene_dz]{.metric}\ kcal/mol at cc-pVDZ and
[pair_cis2butene_minus_1butene_tz]{.metric}\ kcal/mol at cc-pVTZ.

| ΔE~corr~ (kcal/mol) | cc-pVDZ | cc-pVTZ |
| --- | ---: | ---: |
| cis-2-butene − 1-butene | [pair_cis2butene_minus_1butene_dz]{.metric} | [pair_cis2butene_minus_1butene_tz]{.metric} |
| trans-2-butene − 1-butene | [pair_trans2butene_minus_1butene_dz]{.metric} | [pair_trans2butene_minus_1butene_tz]{.metric} |
| isobutene − 1-butene | [pair_isobutene_minus_1butene_dz]{.metric} | [pair_isobutene_minus_1butene_tz]{.metric} |
| trans-2-butene − cis-2-butene | [pair_trans2butene_minus_cis2butene_dz]{.metric} | [pair_trans2butene_minus_cis2butene_tz]{.metric} |
| isobutene − cis-2-butene | [pair_isobutene_minus_cis2butene_dz]{.metric} | [pair_isobutene_minus_cis2butene_tz]{.metric} |
| isobutene − trans-2-butene | [pair_isobutene_minus_trans2butene_dz]{.metric} | [pair_isobutene_minus_trans2butene_tz]{.metric} |

**Table 2.** Pairwise frozen-core DF-CCSD(T) correlation-energy differences
among the four C₄H₈ positional isomers at the registered basis and its
sensitivity check. CEPB predicts every entry to be exactly zero.

## Discussion

Both registered verdicts are **inconclusive**, and they stay that way. Arm A
is inconclusive because the registered rule required the contrast spread to
sit on one side of the threshold at every published basis level, and the
levels disagree: the spread is within 1.0 kcal/mol at the source's CBS
reference and above it at both finite bases. Arm B is inconclusive because
the frozen rule required every pairwise difference to keep its sign between
cc-pVDZ and cc-pVTZ, and one pair — cis-2-butene − 1-butene — did not. The
preregistration says a failed gate is reported, not repaired, so no goalpost
moves; the paragraphs below interpret the parts of the data that are stable
across every level run here, and say so explicitly when they step beyond the
registered statistics.

The Arm A pattern that survives every level is not the spread but the offset.
The three contrasts agree with each other to [swap_spread_cbs]{.metric}\ kcal/mol
at CBS — comfortably inside chemical accuracy — while all three miss the CEPB
prediction in the same direction, by [swap_dev_nearest_cbs]{.metric} to
[swap_dev_farthest_cbs]{.metric}\ kcal/mol at that level. On
the source's own best numbers, then, the C=C → C–C + 2 C–H swap behaves as if
it has one well-defined price that is systematically different from the price
the fitted increments assign it. That reading *supports* the source's
environment-independence claim for this swap — ring strain, homoconjugation,
and substitution across these three pairs move the measured change by only
half a kilocalorie at CBS — while locating the difficulty somewhere the
whole-molecule error statistics cannot see it: a least-squares fit to total
correlation energies can place increment *combinations* a few kcal/mol away
from the value that reaction differences demand, because whole-molecule
residuals, not reaction residuals, are what the fit minimizes. This is not a
claim that the source's fit is wrong — it is exactly what fitting to totals
optimizes for — but it does mean that anyone forming reaction energies from
CEPB increments inherits an offset of this size wherever this swap appears,
and the source's own caution that reaction energies are harder for the model
than total energies points the same way. The spread's growth from CBS to the
finite bases ([swap_spread_qz]{.metric} and [swap_spread_tz]{.metric}\ kcal/mol),
in step with the contrasts' molecular sizes, reads as basis-set
incompleteness rather than chemistry, which is why the registered
every-level rule — written to be conservative — returned inconclusive rather
than supported.

The amendment deserves its own accounting, with our hands up. The raw
effective-increment spread — [raw_spread_cbs]{.metric}\ kcal/mol at CBS — was
computed before the contrast metric was registered, and the amendment that
demoted it was
recorded with that number known — the research journal and the
preregistration both disclose this. The objection that motivated the
amendment (raised independently by an automated review of a related change)
is confirmed by the data: the raw spread is an order of magnitude larger
than the contrast spread at every level and tracks molecule size, which is
the signature of accumulated C–H and C–C residuals being booked to the C=C
column, not of a variable C=C assignment. Both statistics are reported above
so a reader can weigh the derivation order themselves.

In Arm B, the exactly-zero prediction misses by more than the registered
threshold at both bases: the isobutene − trans-2-butene gap is
[pair_isobutene_minus_trans2butene_dz]{.metric}\ kcal/mol at cc-pVDZ and
[pair_isobutene_minus_trans2butene_tz]{.metric}\ kcal/mol at cc-pVTZ — same
sign, nearly the same magnitude, and isobutene is the most strongly
correlated isomer at both bases. Had the registered statistic been that gap
alone, the hypothesis would have been supported; it is the smallest pair in
the set, cis-2-butene − 1-butene, drifting through zero between the bases
that trips the frozen sign rule. Two readings of that flip are open. It may
be ordinary basis sensitivity of a difference an order of magnitude below
the others. It may also be a geometry artifact on our side: the committed
1-butene starting structure has a planar anti carbon skeleton, a
gradient-following optimizer cannot leave a symmetry plane, and a post-hoc
frozen-core DF-MP2/cc-pVDZ frequency calculation on the committed 1-butene
structure — run after the registered analysis was complete, outside the
frozen protocol, and committed under the experiment's `diagnostics/`
directory — finds an imaginary torsional mode, so the committed 1-butene
point is a saddle of the torsional profile rather than a minimum. The three
other isomers' committed structures are unaffected, and the robust
isobutene − trans-2-butene finding does not involve 1-butene; but the frozen
rule makes no exception for explanations arrived at afterwards, and the Arm B
verdict remains inconclusive.

The limitations are the boundary conditions stated in Methods. Arm B is
frozen-core DF-CCSD(T) at cc-pVTZ and cc-pVDZ on MP2 geometries; the source's
reference is all-electron at augmented bases with a CBS extrapolation, so our
pairwise differences are not predictions of what the source's protocol would
return, and correlation differences of a kilocalorie at these bases can move
toward CBS. Each isomer is one stationary point, not a conformer ensemble,
and for 1-butene demonstrably not the equilibrium one. Arm A inherits the
source's published rounding and its geometry choices, which differ between
its training and test sets. And the contrasts isolate one swap in one bond
family; nothing here measures any of the other 32 increments.

If the sign flip, the offset, or the isobutene separation has an explanation
we have missed — a transcription error on our side, a known basis artifact of
density-fitted CCSD(T) on branched alkenes, or prior literature that has
already priced this swap — we would genuinely like to hear it, and the frozen
bundle is published so that checking us is cheap.

## Conclusion

Within the source's own published data, the C=C → C–C + 2 C–H swap has a
consistent price across three chemical environments at the CBS reference
level — and it is not the price the fitted increments charge. In new
calculations on the four butenes, the correlation energies CEPB declares
identical span more than a kilocalorie per mole at both bases run here, with
isobutene consistently the most correlated. Both registered verdicts are
nonetheless inconclusive under their own frozen rules, and the two stable
findings are narrower than the question this experiment set out to ask: a
systematic offset in one swap's price, and one robust pairwise split the
model sets to zero.

The next experiment is the one the offset points at directly: reprice the
swap. Take the contrast-derived value of $e_{\mathrm{CC}} + 2e_{\mathrm{CH}}
- e_{\mathrm{C=C}}$ measured here from the source's own CBS tables, and test
— by arithmetic on the source's published reaction set, with no new quantum
chemistry — whether that single correction reduces CEPB's errors on the
hydrogenation-type reactions it already reports, without degrading the
total-energy accuracy the model was built for. That question is now on the
research shelf.

## References
