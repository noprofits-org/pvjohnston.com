<!-- DRAFT v2 (STOKES) — reframed per Peter's ruling: the two-level picture is
     EARNED for this dye; benzene added as symmetry contrast. Remaining
     TODO(...) markers await: benzene manifold + its metric keys, final
     figure(s), post-ready Table 1 variant from KRAMERS. Do not publish with
     markers present. Checkpoint of canonical inputs: commit 601903d. -->
---
title: "One dye, one transition: how DCDHF-Me2 earns the two-level picture"
date: 2026-08-13
author: Peter Johnston
tags: spectroscopy, TD-DFT, excited states, push-pull chromophores, single-molecule spectroscopy, computational chemistry
description: The blinking-to-absorption note modeled a fluorescent dye as two levels and named what that hides. Computing the actual excited-state manifold of DCDHF-Me2 — a push-pull dye engineered for single-molecule imaging — gives a sharper answer than we planned. Its visible absorption is essentially one transition, and the rest of the manifold lives in the deep UV; benzene, the dye's own parent ring, shows the opposite arrangement for a reason symmetry makes plain.
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
excited states." Those sentences are promissory notes, and this note pays
them down for one specific, real molecule. We expected to find the hidden
states crowding the band. What we found instead is the more interesting
answer: for this dye the two-level idealization is not a convenient fiction
that ignores nearby states — it is *earned*, and the reasons trace back to
what the molecule was designed for.

The route: introduce the molecule and why it is the right example (§2), get
its geometry onto defensible footing (§3), compute the singlet excitation
manifold with time-dependent density functional theory (§4), set benzene —
the dye's own parent ring — beside it as the symmetry contrast (§5), and then
read both manifolds against the two-level picture (§6).

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

A push-pull dye is also where the two-level picture should work best: the
lowest excitation is an intense charge-transfer transition from donor to
acceptor — that is the design goal of the molecule. The [push-pull
chromophores note](/posts/2026-07-05-push-pull-chromophores-charge-transfer.html)
worked through that charge-transfer state on smaller analogs. The question
here is how many neighbors that transition really has, and how much of the
molecule's absorption strength they carry.

## 3. Getting the geometry right: the force-field twist and the planar minimum

The inherited starting structure is a force-field object, not a quantum
mechanical one: built in Avogadro and pre-optimized with the UFF force field,
then exported explicitly for subsequent QM optimization — which is how the
2025 workflow used it.[@Hanwell2012; @Rappe1992] How far that starting point
sits from the DFT minimum turns out to be worth a section: UFF places the
dimethylaniline ring [uff_interring_twist_deg]{.metric}° from coplanar with
the acceptor plane. At the B3LYP/def2-SVP minimum the twist is
[opt_interring_twist_deg]{.metric}° — a change of
[interring_twist_change_deg]{.metric}° — and the amine nitrogen, seeded
slightly pyramidal, flattens into the ring plane entirely.

The chemistry of the planarization is the same push-pull story as the
spectrum: the amine lone pair is being drawn into the π system by the
acceptor on the far side of the ring, planar nitrogen maximizes that
conjugation, and two methyl groups are not enough steric hindrance to resist
it. The optimization step is not a formality for a dye like this — it is what
restores the donor–acceptor conjugation the spectrum depends on.

Because an optimizer's "converged" cannot distinguish a planar minimum from a
planar saddle point — a trap this repository's own tooling has hit before on
aniline — we interrogated the stationary point along the two coordinates that
could plausibly be unstable: rigid single-point displacements of the
inter-ring twist (±10°, ±20°) and of the amine nitrogen out of its
substituent plane (±0.15 Å), at the optimization level of theory. The energy
rises for every displacement — by 0.44 and 1.52 kcal/mol along the twist and
by 2.84 kcal/mol for the amine — and, because the optimized structure is
exactly planar, each ± pair is mirror-equivalent and must agree by symmetry:
the largest observed pair split is 0.51 microhartree, which validates the
displacement construction itself. This rules out the two specific
instabilities that motivated the check. It is not a frequency calculation,
and no true minimum is claimed.

One caveat belongs beside the planarity result rather than buried in methods:
B3LYP is known to favor planarizing amine donors, and the excitation spectra
below — including CAM-B3LYP's — are computed at the B3LYP geometry.

## 4. The computed manifold: one state owns the band

At the planar geometry we computed the [n_states_computed]{.metric} lowest
singlet excitations with full-response TD-DFT (no Tamm–Dancoff
approximation)[@Casida1995] at def2-TZVP, using CAM-B3LYP as the primary
functional — range-separated hybrids are the standard guard against the
charge-transfer failures of global hybrids[@Yanai2004Coulomb; @Laurent2013] —
with B3LYP[@Becke1993Exchange] alongside as the sensitivity check, in
Psi4.[@Smith2020]

The answer to the title question is: **one**. The lowest excitation sits at
[band_center_nm]{.metric} nm ([band_center_ev]{.metric} eV) and is a nearly
pure HOMO→LUMO promotion carrying an oscillator strength of
[lowest_bright_f]{.metric} — [f_fraction_in_lowest_bright]{.metric} of all
the absorption strength in the computed window. Of
[n_states_computed]{.metric} computed states, [n_bright_states]{.metric}
clear the f ≥ 0.01 brightness convention, but within ±0.35 eV of that lowest
bright transition — the empirical band width this site's earlier TD-DFT notes
applied to their stick spectra — sits exactly
[n_states_under_band]{.metric} state: S₁ itself. The gap to the next state of
any kind is [s1_s2_gap_ev]{.metric} eV ([lowest_two_bright_gap_ev]{.metric}
eV to the next *bright* state — here the same state, S₂), and the rest of the
manifold begins another electron-volt above that: real, several of its states
genuinely bright, and all of it in the deep UV between 4.5 and 6.2 eV where
no visible-band measurement will conflate it with S₁ (Table 1, Figure 1).

B3LYP tells the same story shifted red: lowest bright state at
[band_center_nm_b3lyp]{.metric} nm, S₁–S₂ gap 0.51 eV, still no second state
within the band window. The 0.315 eV blue shift from B3LYP to CAM-B3LYP is
itself diagnostic: it is the signature of substantial charge-transfer
character in S₁, the same signature the push-pull note measured at 0.42 eV
for para-nitroaniline.

<!-- TODO(STOKES): Table 1 — paste post-ready CAM-B3LYP table variant
     (requested from KRAMERS: no Δr / no auto-Character columns, generated
     not hand-stripped). Caption: **Table 1.** The twelve computed singlet
     states of DCDHF-Me2 at CAM-B3LYP/def2-TZVP... referenced above. -->

<!-- TODO(STOKES): Figure 1 — final generated figure (single- or two-panel
     pending benzene). Insert tikz verbatim; caption names the
     [broadening_fwhm_ev_cosmetic]{.metric} eV envelope as display-only. -->

## 5. The contrast: benzene's band is a degenerate pair

<!-- TODO(STOKES): benzene manifold + metric keys pending from KRAMERS.
     Structure agreed: benzene's strongly allowed band is a
     symmetry-degenerate E1u pair — two bright states splitting the strength
     ~50/50 — against DCDHF-Me2's one state at 74%. Mechanism sentence:
     benzene's sixfold symmetry makes the pair degenerate; donor–acceptor
     substitution destroys that symmetry and funnels the strength into one
     state. MUST state plainly: benzene's band is at ~7 eV, deep UV — the
     comparison is about how many transitions share one apparent band, not
     about visible color. Note benzene re-run under the same Psi4 1.9.1
     environment as the dye (cross-environment numbers are not a
     comparison). Lineage point: benzene is literally the parent ring of the
     dye's donor half — the same ring the push-pull note walked through the
     aniline/nitrobenzene/pNA series. -->

## 6. Why the idealization is earned, not lucky

<!-- TODO(STOKES): write after benzene numbers land, but the argument is
     fixed: (a) oscillator strength is budgeted — f = 1.12 in S1 is near the
     practical ceiling for a chromophore this size, and a molecule engineered
     for single-molecule brightness is a molecule engineered to concentrate
     its transition strength into one state; (b) attribute design goals
     accurately: Lu et al. optimized brightness and photostability, not
     "two-levelness" — the isolated S1 is a consequence, not the stated aim;
     (c) the UV manifold is exactly where the previous note's excluded
     channels live (excited-state absorption from S1, two-photon-accessible
     states); (d) close the loop to PR #75: the approximation holds for this
     dye because dyes like it were selected to make it hold. -->

## 7. Reproducibility

<!-- TODO(STOKES): finalize once benzene lands and the harness reconciliation
     commit exists. Facts to carry: Psi4 1.9.1 (conda env psi4_19), Python
     3.10.17, numpy 2.2.5; 6 threads / 6 GB; two-stage run_all.sh (optimize:
     B3LYP/def2-SVP gau_tight; excite: full-RPA TD-DFT, 12 singlets,
     def2-TZVP per functional); UFF start from the 2025 SI; canonical outputs
     + stationary check under research/dcdhf-me2-transitions/; checkpoint
     commit 601903d. Solver facts (do not lump): TD eigensolver iteration cap
     is a hard 60 in 1.9.1 — both the kwarg and the global option are
     silently ignored; unconverged roots raise TDSCFConvergenceError (loud);
     r_convergence 1e-5 takes effect; results record requested vs effective
     side by side. -->

## 8. Where the model stops

These are vertical electronic excitations of isolated molecules in vacuum,
twelve states deep. Nothing here has vibrational structure: any envelope
drawn in the figure is a display convention of
[broadening_fwhm_ev_cosmetic]{.metric} eV, not a computed line shape, and a
real absorption band's width is dominated by vibronic progressions and
solvent broadening this calculation does not attempt. Solvent shifts of
charge-transfer states are large and absent here — both functionals sit blue
of the dye's experimental solution band, as vertical gas-phase numbers
should be expected to. We can say nothing about states above the computed
window. And one diagnostic deserves its own disclaimer: the automated
charge-transfer classifier in our harness labels S₁ by the distance between
hole and particle centroids, a metric that understates charge transfer when
both frontier orbitals delocalize over the same conjugated backbone — for
S₁ we trust the functional-shift signature instead, and the per-state
classifier column stays in the experiment directory rather than in Table 1.

## References
