---
title: "How electron correlation survives a hydrogenation enthalpy subtraction"
date: 2026-07-23
author: Peter Johnston
tags: quantum chemistry, electron correlation, coupled cluster, hydrogenation, thermochemistry, reproducibility
description: "A worked CCSD(T)−HF calculation shows how large molecular correlation energies mostly cancel in reaction enthalpies, what survives that subtraction, and why the residual should not be assigned to one π bond."
post-type: understanding
question: How does electron correlation survive the subtraction that forms a reaction enthalpy, and why is the surviving term reaction-specific rather than a transferable π-bond property?
experiment: correlation-in-hydrogenation
---

## The question

A [previous note in this series](/posts/2026-07-04-the-correlation-gap-in-water-measured.html)
measured electron correlation as a total energy — the gap between Hartree–Fock
and CCSD(T) for one water molecule. A total correlation energy is large, but
chemistry runs on energy *differences*, where much of it cancels. This post
turns the same subtraction on a reaction and follows it in three steps: form the
reaction enthalpy at each electronic-structure level, cancel the shared thermal
correction, and inspect the small correlation residual that remains.

The worked example uses HF and CCSD(T)/cc-pVTZ single points (frozen core) at
B3LYP/def2-TZVP geometries for [reaction_count]{.metric} closed-shell gas-phase
hydrogenations. For the two reactions that each remove one C–C π bond, the
residual is
[correlation_content_acetylene_hydrogenation_kj]{.metric} kJ/mol
(acetylene → ethylene) and
[correlation_content_ethylene_hydrogenation_kj]{.metric} kJ/mol
(ethylene → ethane). They differ by
[pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol and have opposite
signs. The point is not to localise correlation onto either bond—the calculation
does not do that—but to see why a reaction-level residual cannot automatically
be promoted into a transferable bond property.

## From molecular correlation to a reaction residual

The mean field misses a lot. For a single water molecule the correlation energy
— the difference between the exact non-relativistic energy and the
Hartree–Fock limit — runs to hundreds of kJ/mol, and the
[preceding note](/posts/2026-07-04-the-correlation-gap-in-water-measured.html)
measured it directly by marching a basis-set ladder to its limit and dropping
CCSD(T) below it. That earlier post, and the
[one before it](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html) on
the Hartree–Fock machinery itself, both stopped at a *total* energy of a *single*
system. But no experiment measures the total energy of a molecule; it measures
the energy released or absorbed when one molecule turns into another. The
question that matters for chemistry is therefore not how large correlation is,
but how much of it *survives a reaction*.

When a reaction conserves the number and type of chemical bonds, the large
per-molecule correlation energies on the two sides can cancel substantially.
This is the reasoning behind isodesmic and bond-separation reaction schemes,
which are built so that method error cancels and even modest methods give useful
reaction energies.[@HelgakerJorgensenOlsen2000] A hydrogenation is not
isodesmic—it trades a π bond and an H–H bond for two C–H bonds—so complete
cancellation is not built into the reaction.

"Small," though, is not a number, and "the correlation of one C–C π bond" is a
transferability shortcut that the cancellation argument neither states nor
justifies.
Hydrogenating acetylene to ethylene removes one π bond from a carbon–carbon
triple bond; hydrogenating ethylene to ethane removes the one π bond of a
carbon–carbon double bond. Both reactions hydrogenate exactly one C–C π bond. If
the correlation contribution to a hydrogenation enthalpy were a transferable
per-π-bond quantity, these two reaction-level residuals would be similar.

That comparison gives the explanation a useful scale. Chemical accuracy,
[chemical_accuracy_threshold_kj]{.metric} kJ/mol, is the tolerance within which
the two residuals would behave like the same practical increment. The ammonia
and methanol reactions then show how the same subtraction behaves for N–N and
C–O multiple bonds. Together these examples separate two ideas that are easy to
conflate: correlation can cancel strongly in a reaction while the small
remainder is still not transferable between reactions.

## What cancels, and what remains in the model

**Composite and why the thermal correction cancels.** For each species a
geometry optimisation and harmonic-frequency calculation at B3LYP/def2-TZVP
supplies the geometry and the ideal-gas rigid-rotor/harmonic-oscillator thermal
and zero-point enthalpy correction to [temperature_k]{.metric} K and
1 atm.[@Becke1993Exchange; @Weigend2005Balanced] At that geometry a single
CCSD(T)/cc-pVTZ calculation with frozen core supplies two electronic energies at
once: its converged self-consistent-field total is the Hartree–Fock baseline,
and its CCSD(T) total is the correlated value.[@Raghavachari1989; @Dunning1989]
A reaction enthalpy at each level adds the same B3LYP thermal correction
to the electronic reaction energy, so in the difference

$$
\Delta_{\mathrm{corr}} \;=\; \Delta H_{\mathrm{CCSD(T)}} - \Delta H_{\mathrm{HF}}
$$

the thermal correction cancels exactly, and $\Delta_{\mathrm{corr}}$ is the
correlation part of the electronic reaction energy — no more, no less. This is a
composite recipe (a coupled-cluster energy on a DFT geometry with a DFT thermal
correction) and it is stated plainly rather than hidden: the quantity it isolates
is a correlation *difference*. The thermal layer drops out algebraically. The
common geometry is held fixed between methods, so geometry relaxation does not
enter the subtraction, but that geometry remains part of the model and can
affect the residual.

**The worked reaction set.** Four closed-shell singlet gas-phase hydrogenations
make the cancellation concrete. Two form the C–C comparison, and two provide
multiple-bond context:

| slug | reaction | C–C π bonds | role |
| --- | --- | --- | --- |
| acetylene_hydrogenation | C₂H₂ + H₂ → C₂H₄ | 1 | transferability rung A |
| ethylene_hydrogenation | C₂H₄ + H₂ → C₂H₆ | 1 | transferability rung B |
| ammonia_synthesis | N₂ + 3 H₂ → 2 NH₃ | — (N–N) | triple-bond context |
| methanol_synthesis | CO + 2 H₂ → CH₃OH | — (C–O) | triple-bond context |

The two C–C rungs each hydrogenate one π bond. Their per-π-bond value is therefore
the reaction contribution itself. The ammonia and methanol reactions reduce N–N
and C–O triple bonds, respectively, and provide context rather than additional
C–C comparisons.

## Four hydrogenations as a worked example

Table 1 lists, for each reaction, the CCSD(T) enthalpy at
[temperature_k]{.metric} K, the correlation contribution
ΔH(CCSD(T)) − ΔH(HF), and that contribution as a fraction of the CCSD(T)
enthalpy.

| reaction | ΔH(CCSD(T)) (kJ/mol) | Δcorr (kJ/mol) | Δcorr / ΔH(CCSD(T)) |
| --- | --- | --- | --- |
| C₂H₂ + H₂ → C₂H₄ | [dh_ccsdt_acetylene_hydrogenation_kj]{.metric} | [correlation_content_acetylene_hydrogenation_kj]{.metric} | [correlation_fraction_acetylene_hydrogenation]{.metric} |
| C₂H₄ + H₂ → C₂H₆ | [dh_ccsdt_ethylene_hydrogenation_kj]{.metric} | [correlation_content_ethylene_hydrogenation_kj]{.metric} | [correlation_fraction_ethylene_hydrogenation]{.metric} |
| N₂ + 3 H₂ → 2 NH₃ | [dh_ccsdt_ammonia_synthesis_kj]{.metric} | [correlation_content_ammonia_synthesis_kj]{.metric} | [correlation_fraction_ammonia_synthesis]{.metric} |
| CO + 2 H₂ → CH₃OH | [dh_ccsdt_methanol_synthesis_kj]{.metric} | [correlation_content_methanol_synthesis_kj]{.metric} | [correlation_fraction_methanol_synthesis]{.metric} |

**Table 1.** CCSD(T)/cc-pVTZ hydrogenation enthalpies at [temperature_k]{.metric} K,
the correlation contribution ΔH(CCSD(T)) − ΔH(HF) to each, and that contribution
as a fraction of the CCSD(T) enthalpy. Δcorr carries the sign of
ΔH(CCSD(T)) − ΔH(HF). Across the four reactions the mean absolute correlation
contribution is [mean_abs_correlation_content_kj]{.metric} kJ/mol and the largest
absolute value is [max_abs_correlation_content_kj]{.metric} kJ/mol.

For the two hydrocarbon rungs the correlation contribution is
[correlation_content_acetylene_hydrogenation_kj]{.metric} kJ/mol
(acetylene → ethylene, against a CCSD(T) enthalpy of
[dh_ccsdt_acetylene_hydrogenation_kj]{.metric} kJ/mol) and
[correlation_content_ethylene_hydrogenation_kj]{.metric} kJ/mol
(ethylene → ethane, against [dh_ccsdt_ethylene_hydrogenation_kj]{.metric} kJ/mol).
Each reaction hydrogenates one C–C π bond, and these values are the per-π-bond
contributions. Their difference is
[pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol, against a
chemical-accuracy comparison scale of
[chemical_accuracy_threshold_kj]{.metric} kJ/mol, and the two values carry
opposite signs. The corresponding within-threshold check is
[cc_pi_rungs_within_chemical_accuracy]{.metric}.

For the two context reactions the correlation contribution is
[correlation_content_ammonia_synthesis_kj]{.metric} kJ/mol (N₂ + 3 H₂ → 2 NH₃)
and [correlation_content_methanol_synthesis_kj]{.metric} kJ/mol
(CO + 2 H₂ → CH₃OH), the latter [correlation_fraction_methanol_synthesis]{.metric}
of its CCSD(T) enthalpy. Every optimised species had no imaginary vibrational
mode ([all_species_true_minima]{.metric}).

## Why the residual is reaction-specific

The narrow comparison is straightforward. A reusable per-π-bond increment would
have to describe both C–C rungs within
[chemical_accuracy_threshold_kj]{.metric} kJ/mol. Instead, the residuals sit
[pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol apart and on
opposite sides of zero. On the acetylene rung correlation makes hydrogenation
*less* exothermic
(Δcorr positive); on the ethylene rung it makes hydrogenation slightly more
exothermic (Δcorr negative). These are reaction-level balances. The calculation
does not partition correlation energy among bonds, so their opposite signs do
not establish that the triple bond itself is the cause. What they establish is
narrower: a single per-π-bond increment cannot reproduce both rungs; calibrating
on one would miss the other by
[pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol.

The magnitudes put that difference in perspective. Both hydrocarbon
contributions are small in absolute terms:
[correlation_content_acetylene_hydrogenation_kj]{.metric} and
[correlation_content_ethylene_hydrogenation_kj]{.metric} kJ/mol against CCSD(T)
enthalpies of [dh_ccsdt_acetylene_hydrogenation_kj]{.metric} and
[dh_ccsdt_ethylene_hydrogenation_kj]{.metric} kJ/mol, respectively. Their signed
ratios to the CCSD(T) enthalpies are
[correlation_fraction_acetylene_hydrogenation]{.metric} and
[correlation_fraction_ethylene_hydrogenation]{.metric}. That is the
electron-count cancellation the isodesmic argument predicts; the transferability
mismatch lives inside that small surviving residue, not in the bulk of the
enthalpy. A gap of [pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol
is minor next to the measured reaction enthalpies and decisive next to the
[chemical_accuracy_threshold_kj]{.metric} kJ/mol accuracy target — which is why
the per-bond question needs a number rather than an adjective.

The two non-C–C reactions show that the C–C rungs are, if anything, the
*benign* end of the range. Ammonia synthesis carries
[correlation_content_ammonia_synthesis_kj]{.metric} kJ/mol and methanol
synthesis [correlation_content_methanol_synthesis_kj]{.metric} kJ/mol — the
latter [correlation_fraction_methanol_synthesis]{.metric} of its own CCSD(T)
enthalpy. The methanol-synthesis entry has the largest absolute correlation
contribution in the set, [max_abs_correlation_content_kj]{.metric} kJ/mol. The
spread across the four reactions, from
[correlation_content_acetylene_hydrogenation_kj]{.metric} to
[correlation_content_methanol_synthesis_kj]{.metric} kJ/mol, is the measured
picture: the correlation contribution is a reaction-specific residual, not a
transferable per-bond increment.

This pattern is compatible with the error-cancellation logic of isodesmic
schemes: those schemes conserve bond types, whereas these hydrogenations do
not. The worked values make the distinction concrete: substantial cancellation
does not imply that the remainder belongs to one bond. Holding the geometry fixed
and cancelling the thermal layer isolates an electronic reaction difference,
not a bond-energy partition.

## Where the model stops

The boundaries are worth stating plainly, because they limit what the number
means. The basis is finite: cc-pVTZ is not the complete-basis limit, and the
correlation energy of triple bonds such as N₂ converges notoriously slowly with
basis size, so the *absolute* contributions — especially for ammonia and
methanol — would shift under extrapolation.[@HelgakerJorgensenOlsen2000] The
reference is CCSD(T) itself, with no higher-order or multireference check, so this
measures the correlation that CCSD(T) recovers, not necessarily the exact
correlation. The RRHO thermal correction cancels in the method difference, but
the B3LYP geometry remains part of the model and could shift the correlation
contribution. The worked comparison contains one pair of C–C rungs, not a
statistical sample of C–C π bonds, and it does not partition correlation energy
among atoms or bonds. A basis- and geometry-sensitivity study could test how
stable the [pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol gap is.

## Reproducibility

Every energy was produced locally by psi4 1.9.1 with tight SCF and geometry
thresholds.[@Smith2020Psi4] The run was single-threaded
(`OMP_NUM_THREADS=1`) to avoid changes in threaded floating-point reduction
order, and it used no random seeds. Every optimised species was a true minimum
with no imaginary vibrational mode
([all_species_true_minima]{.metric} across the set).

The pinned conda environment and `calculate.py` regenerate the species and
reaction results. A psi4-free `calculate.py --check` reconstructs every reaction
quantity from the committed per-species energies, and the metrics generator
fingerprints those inputs before projecting the values used here. The
calculation uses no external data, network service, paid service, or living
subjects.

## What to calculate next

Turning the water note's CCSD(T)−HF subtraction from a molecule onto a reaction
gives small correlation residuals for the hydrocarbon hydrogenations. The
residual is [correlation_content_acetylene_hydrogenation_kj]{.metric} kJ/mol for
the acetylene rung and
[correlation_content_ethylene_hydrogenation_kj]{.metric} kJ/mol for the ethylene
rung—a gap of
[pi_bond_correlation_transferability_gap_kj]{.metric} kJ/mol. The calculation
therefore supplies a useful worked warning: a small reaction-level correlation
term is not automatically a transferable bond property.

The comparison also changes the starting C–C bond order along with the rest of
the reaction-level correlation balance. Whether a stable increment emerges
among reactions that all reduce
the same bond order — a family of isolated C–C double bonds hydrogenated to
single bonds, say — is a separate, and answerable, measurement. That would
distinguish a genuine per-bond correlation increment from the change in
starting bond order that this comparison leaves entangled.

## References
