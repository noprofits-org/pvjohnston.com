<!-- DRAFT SKELETON (STOKES) — TD legs still running. Every TODO(...) marker
     must be resolved against results/tables.md, summary.json, and the
     stationary-check verdict before this file goes into a PR. Do not publish
     with markers present. -->
---
title: "One dye, many transitions: the DCDHF-Me2 manifold above the two-level picture"
date: 2026-08-13
author: Peter Johnston
tags: spectroscopy, TD-DFT, excited states, push-pull chromophores, single-molecule spectroscopy, computational chemistry
description: The blinking-to-absorption note modeled a fluorescent dye as two levels and said so. This note pays that promissory note down. We compute the excited-state manifold of DCDHF-Me2 — a push-pull dye built for single-molecule imaging — and count how many electronic transitions actually sit under and around its visible absorption band.
post-type: understanding
question: How many electronic transitions does DCDHF-Me2 have around its visible absorption band, and what does the answer do to the two-level idealization?
experiment: dcdhf-me2-transitions
---

## 1. The promissory note in the two-level model

The [previous note on blinking and
absorption](/posts/2026-08-12-from-blinking-to-absorption.html) modeled a
fluorescent molecule as two electronic states, and was careful to say so
twice: a real dye "does have higher electronic states and can show
excited-state absorption," and the two-level approximation "hides the higher
excited states." Those sentences are promissory notes. This note pays them
down for one specific, real molecule: how many electronic states are actually
there, where do they sit, and how much of the absorption a spectrometer
records belongs to the transition the two-level model keeps.

The route: introduce the molecule and why it is the right example (§2), get
its geometry onto defensible footing (§3), compute the singlet excitation
manifold with time-dependent density functional theory (§4), and then read
that manifold against the two-level picture — what survives, what was hidden,
and what the hiding costs (§5).

## 2. The molecule: a push-pull dye built to be watched one at a time

DCDHF-Me2 is a donor–acceptor chromophore from the dicyanomethylenedihydrofuran
(DCDHF) family developed for single-molecule fluorescence imaging: a
dimethylamino donor conjugated through a phenyl ring to the DCDHF acceptor
head, whose three nitrile groups and ring oxygen make it a strong electron
sink.[@Lu2009] The family was designed precisely for the experiment the
previous note started from — single molecules blinking in a microscope — which
makes it the natural molecule to ask the manifold question about. This site
has computed on it before: the 2025 tooling notes used DCDHF-Me2 as their
demonstration chromophore and shipped its Avogadro-built starting structure in
their [supporting information](/posts/ai-comp-tools-SI.html), which is the
geometry this experiment inherits.

A push-pull dye is also where the two-level picture works *best*: the lowest
excitation is an intense charge-transfer transition from donor to acceptor,
well separated from the rest — that is the design goal of the molecule. The
[push-pull chromophores
note](/posts/2026-07-05-push-pull-chromophores-charge-transfer.html) worked
through that charge-transfer state on smaller analogs. So the question here is
not whether the two-level model was wrong to keep one transition; it is how
many neighbors that transition really has, and how much oscillator strength
they carry.

## 3. Getting the geometry right: the force-field twist and the planar minimum

The inherited starting structure is a force-field object, not a quantum
mechanical one: built in Avogadro and pre-optimized with the UFF force field,
then exported explicitly for subsequent QM optimization — which is how the
2025 workflow used it.[@Hanwell2012; @Rappe1992] How far that starting point sits from the DFT minimum turns out to be
worth a section: UFF places the dimethylaniline ring
[uff_interring_twist_deg]{.metric}° from coplanar with the acceptor plane. At
the B3LYP/def2-SVP minimum the twist is [opt_interring_twist_deg]{.metric}°,
a change of [interring_twist_change_deg]{.metric}° — and the amine nitrogen,
seeded slightly pyramidal, flattens into the ring plane entirely.

The chemistry of the planarization is the same push-pull story as the
spectrum: the amine lone pair is being drawn into the π system by the acceptor
on the far side of the ring, planar nitrogen maximizes that conjugation, and
two methyl groups are not enough steric hindrance to resist it. The
optimization step is not a formality for a dye like this — it is what restores
the donor–acceptor conjugation the spectrum depends on.

<!-- TODO(STOKES): stationary-check paragraph. Insert verdict from
     check_stationary.py output when it lands. Committed wording contract with
     KRAMERS: the six rigid displacements (inter-ring twist ±10°/±20°, amine N
     ±0.15 Å out of plane) rule out the two specific instabilities that
     motivated the check; they are NOT a frequency calculation and no true
     minimum is claimed; the ± pairs are mirror-degenerate by symmetry and any
     ≥1 µHa split voids the check. If any displacement LOWERED the energy:
     stop drafting, talk to KRAMERS and Peter. -->

<!-- TODO(STOKES): one-sentence B3LYP caveat — B3LYP is known to favor
     planarizing amine donors; CAM-B3LYP spectra are computed at the B3LYP
     geometry. Methods-style disclosure, §6. -->

## 4. The computed manifold

<!-- TODO(STOKES): verify against summary.json when it lands. All metric keys
     below are confirmed by KRAMERS as projected; do NOT add
     lowest_two_bright_gap_ev until KRAMERS confirms it exists (it is emitted
     only if ≥2 states clear f ≥ 0.01). -->

At the planar geometry we computed the [n_states_computed]{.metric} lowest
singlet excitations with full-response TD-DFT (no Tamm–Dancoff
approximation)[@Casida1995] at def2-TZVP, using CAM-B3LYP as the primary
functional — range-separated hybrids are the standard guard against the
charge-transfer failures of global hybrids[@Yanai2004Coulomb; @Laurent2013] —
with B3LYP[@Becke1993Exchange] alongside as the sensitivity check, in
Psi4.[@Smith2020]

The lowest bright state sits at [band_center_nm]{.metric} nm
([band_center_ev]{.metric} eV) with oscillator strength
[lowest_bright_f]{.metric}; B3LYP puts it at
[band_center_nm_b3lyp]{.metric} nm. Of the [n_states_computed]{.metric}
computed states, [n_bright_states]{.metric} are bright by the f ≥ 0.01
convention. Within ±0.35 eV of the lowest bright transition — the same
empirical width both this site's earlier TD-DFT notes applied to their stick
spectra — sit [n_states_under_band]{.metric} states,
[n_bright_under_band]{.metric} of them bright, and
[f_fraction_outside_band]{.metric} of the total computed oscillator strength
lies outside that window. Stated without any window convention: the S₁–S₂ gap
is [s1_s2_gap_ev]{.metric} eV and the S₁–S₃ gap is
[s1_s3_gap_ev]{.metric} eV.

<!-- TODO(STOKES): Table 1 — per-state CAM-B3LYP table from results/tables.md
     (state, eV, nm, f, hole–particle distance, dominant assignment, type).
     Caption: **Table 1.** ... referenced from the prose above. B3LYP table
     goes to §6 or stays in the experiment directory — decide when seen. -->

<!-- TODO(STOKES): Figure 1 — insert generated figure_manifold.tikz verbatim
     (do not hand-edit coordinates; regeneration is one command on KRAMERS's
     side). Caption: **Figure 1.** sticks are computed (position, f); the
     envelope is the cosmetic [broadening_fwhm_ev_cosmetic]{.metric} eV FWHM
     convention, carrying no information. Reference from prose. -->

## 5. Reading the manifold against the two-level picture

<!-- TODO(STOKES): the interpretive core — write ONLY after the numbers are
     in. The argument to make, conditional on what the data supports:
     (a) if f_fraction_in_lowest_bright is large: the two-level model keeps
         the state that owns most of the visible response — that is WHY it
         works for this dye — while [n_states_under_band]-1 neighbors sit
         within the empirical band it draws as one line;
     (b) either way: the higher states are exactly where the previous note's
         excluded channels live — excited-state absorption from S1, and the
         two-photon-accessible states of the nonlinear section;
     (c) connect the S1 CT character (hole–particle distance from Table 1)
         back to the push-pull note.
     House stance: no verdict language (Understanding note), no overclaim
     about experimental spectra — these are vertical gas-phase excitations. -->

## 6. Reproducibility

<!-- TODO(STOKES): finalize from research/dcdhf-me2-transitions/environment.md
     and README once the run closes: Psi4 1.9.1 (conda env psi4_19), Python
     3.10.17, numpy 2.2.5; 6 threads / 6 GB; two-stage run via run_all.sh
     (optimize: B3LYP/def2-SVP, gau_tight; excite: TD-DFT def2-TZVP, 12
     singlets, full RPA, per functional); starting geometry
     geometry/dcdhf-me2-uff.xyz lifted from the 2025 SI post; canonical
     outputs under research/dcdhf-me2-transitions/results/. Solver facts,
     CORRECTED per KRAMERS 's verification (do not lump these together):
     (1) the TD eigensolver's iteration limit is a HARD 60 in Psi4 1.9.1 —
     both the maxiter kwarg and the TDSCF_MAXITER global option are silently
     accepted and ignored; it cannot be raised without patching Psi4;
     (2) the reassuring half: an unconverged root raises
     TDSCFConvergenceError, so it fails loudly and cannot reach results/
     unnoticed; (3) r_convergence DOES take effect (1e-5 requested and shown
     in the run header). Results record tdscf_requested vs tdscf_effective
     side by side. Mention check_stationary.py and its scope. -->

## 7. Where the model stops

These are vertical electronic excitations of one molecule in vacuum. Nothing
here has vibrational structure: the envelope drawn in Figure 1 is an empirical
[broadening_fwhm_ev_cosmetic]{.metric} eV convention, not a computed line
shape, and the real band width of a dye like this is dominated by
vibronic progressions and solvent broadening that this calculation does not
attempt — the same honesty boundary the blinking note drew around its own
ensemble demonstration. Solvent shifts of charge-transfer states are large and
are absent here. TD-DFT excitation energies carry functional dependence — the
B3LYP-vs-CAM-B3LYP spread above is the measured size of that sensitivity for
this molecule, not an error bar in the statistical sense. And the geometry
underneath everything is a stationary point interrogated along two suspect
coordinates, not a frequency-confirmed minimum.

<!-- TODO(STOKES): adjust the last sentence to match the actual stationary
     verdict; delete it entirely if the check came back INCONCLUSIVE and we
     rescoped. -->

## References
