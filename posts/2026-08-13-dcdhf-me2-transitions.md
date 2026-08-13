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
the dye's own parent ring — beside it as the symmetry contrast (§5), and
then read both manifolds against the two-level picture (§6).

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
rises for every displacement — by [stationary_twist10_rise_kcal]{.metric} and
[stationary_twist20_rise_kcal]{.metric} kcal/mol along the twist and by
[stationary_pyramid_rise_kcal]{.metric} kcal/mol for the amine — and, because
the optimized structure is exactly planar, each ± pair is mirror-equivalent
and must agree by symmetry: the largest observed pair split is
[stationary_worst_pair_split_uhartree]{.metric} microhartree, which validates
the displacement construction itself. This rules out the two specific
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
the absorption strength in the computed window (Table 1). Of
[n_states_computed]{.metric} computed states, [n_bright_states]{.metric}
clear the f ≥ 0.01 brightness convention, but within ±0.35 eV of the lowest
bright transition — the empirical band width this site's earlier TD-DFT
notes applied to their stick spectra — sits exactly
[n_states_under_band]{.metric} state: S₁ itself. The next state of any kind
is [s1_s2_gap_ev]{.metric} eV away and far weaker, and the manifold's
remaining bright states begin nearly another electron-volt beyond it: real,
several of them genuinely bright, and all of them in the deep UV between 5.1
and 6.2 eV, where no visible-band measurement will conflate them with S₁
(Figure 1).

B3LYP tells the same story shifted red: lowest bright state at
[band_center_nm_b3lyp]{.metric} nm, an S₁–S₂ gap of
[s1_s2_gap_ev_b3lyp]{.metric} eV, and still no second state within the band
window. The [functional_shift_ev]{.metric} eV blue shift from B3LYP to
CAM-B3LYP is itself diagnostic: it is the signature of substantial
charge-transfer character in S₁ — the same signature the push-pull note
measured at 0.42 eV for para-nitroaniline.

| State | E (eV) | λ (nm) | f | Dominant excitation |
|---:|---:|---:|---:|---|
| S1 | 3.32 | 374 | 1.1239 | HOMO→LUMO (96.5%) |
| S2 | 4.21 | 294 | 0.0242 | HOMO-1→LUMO (94.9%) |
| S3 | 4.51 | 275 | 0.0062 | HOMO→LUMO+1 (46.4%); HOMO-2→LUMO (38.6%); HOMO-1→LUMO+1 (6.3%) |
| S4 | 5.11 | 243 | 0.0853 | HOMO-2→LUMO (53.6%); HOMO→LUMO+1 (37.5%) |
| S5 | 5.29 | 235 | 0.1138 | HOMO→LUMO+2 (71.8%); HOMO-3→LUMO (6.1%); HOMO-1→LUMO+2 (5.7%) |
| S6 | 5.46 | 227 | 0.0000 | HOMO→LUMO+3 (46.2%); HOMO-1→LUMO+3 (18.3%); HOMO→LUMO+4 (12.2%); HOMO-1→LUMO+4 (5.9%) |
| S7 | 5.47 | 227 | 0.0810 | HOMO-3→LUMO (81.9%) |
| S8 | 5.62 | 221 | 0.0002 | HOMO-4→LUMO (58.6%); HOMO-5→LUMO (17.4%); HOMO-8→LUMO (14.9%) |
| S9 | 5.98 | 207 | 0.0525 | HOMO→LUMO+5 (61.9%); HOMO-1→LUMO+2 (15.2%); HOMO→LUMO+2 (5.2%); HOMO-2→LUMO+1 (5.1%) |
| S10 | 6.11 | 203 | 0.0043 | HOMO→LUMO+3 (26.4%); HOMO→LUMO+8 (16.0%); HOMO-1→LUMO+3 (10.1%); HOMO-3→LUMO+3 (7.1%) |
| S11 | 6.17 | 201 | 0.0218 | HOMO→LUMO+4 (53.8%); HOMO-1→LUMO+4 (10.3%) |
| S12 | 6.20 | 200 | 0.0023 | HOMO-5→LUMO (39.1%); HOMO-4→LUMO (20.9%); HOMO-4→LUMO+2 (8.9%); HOMO-8→LUMO (8.0%) |

**Table 1.** The twelve computed singlet states of DCDHF-Me2 at
CAM-B3LYP/def2-TZVP: one intense HOMO→LUMO transition, then nothing of
comparable strength anywhere in the window. The generated per-state record in
the experiment directory additionally carries hole–particle distances and an
automated character label, omitted here for a reason given in §8.

## 5. The contrast: benzene's band is a degenerate pair

Benzene earns its place in this note twice over: it is the simplest molecule
whose strongly allowed band is *not* one transition, and it is literally the
parent ring of DCDHF-Me2's donor half — the same ring the [push-pull
note](/posts/2026-07-05-push-pull-chromophores-charge-transfer.html) walked
through the aniline → nitrobenzene → para-nitroaniline series. We recomputed
it with the identical harness, functional, basis, band window, and software
environment as the dye, because numbers imported from a different environment
would not be a comparison.

The symmetry underneath the contrast is measured, not assumed: at the
B3LYP/def2-SVP minimum all six carbon–carbon bonds agree to within
[benzene_cc_bond_spread_ang]{.metric} Å, so the ring's sixfold symmetry
survives an optimization that ran in C1 and was free to break it. On that
frame the manifold arranges itself in the opposite way to the dye's
(Table 2). The two lowest singlets, at 5.46 and 6.15 eV, are
symmetry-forbidden and carry zero oscillator strength — the [selection-rules
note](/posts/2026-07-08-forbidden-and-allowed-symmetry-selection-rules.html)
is about exactly this kind of extinction. The strongly allowed band at
[benzene_band_center_ev]{.metric} eV is an exactly degenerate pair: two
states separated by [benzene_lowest_two_bright_gap_ev]{.metric} eV, splitting
the band's strength down the middle — the lower partner carries
[benzene_lowest_bright_f_share]{.metric} of the pair's total. Under the same
±0.35 eV window that found one state for the dye, benzene holds
[benzene_n_states_under_band]{.metric} states, both bright (Figure 1). And
the pattern repeats one rung up: the next pair, at 7.70 eV, is also exactly
degenerate — dark, but degenerate — because degeneracy here is not numerical
coincidence; it is what a two-dimensional irreducible representation of a
sixfold-symmetric ring enforces.

Figure 1 shows the two manifolds in two measures, because a transition's
oscillator strength prices its dipole strength in units of its energy,

$$f = \tfrac{2}{3}\,\Delta E\,|\boldsymbol{\mu}|^{2},$$

with $\Delta E$ in hartree and $|\boldsymbol{\mu}|^{2}$ in atomic units — so
the two panels rank the same sticks differently, and the difference is
itself the physics.

```tikzpicture
\begin{axis}[
    name=fpanel,
    width=14cm, height=6.4cm,
    ylabel={oscillator strength $f$},
    xmin=2.5, xmax=9.2, ymin=0, ymax=1.502,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title={One apparent band, one transition or two},
    title style={font=\large\bfseries},
    xticklabels={},
    legend pos=north west,
    legend style={draw=none, fill=white, fill opacity=0.85},
]
\addlegendimage{ycomb, very thick, color=blue!65!black, mark=*, mark size=1.4pt}
\addlegendentry{benzene}
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.458,0.0000)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.148,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:7.117,0.0000) -- (axis cs:7.117,0.6006);
\draw[very thick, color=blue!50!white] (axis cs:7.117,0.6006) -- (axis cs:7.117,1.2012);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.117,1.2012)};
\draw[black, thick] (axis cs:7.057,0.6006) -- (axis cs:7.176,0.6006);
\node[font=\small\bfseries, anchor=west] at (axis cs:7.216,0.6006) {A};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.697,0.0000)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.891,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:7.973,0.0000) -- (axis cs:7.973,0.0112);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.973,0.0112)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.994,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:8.447,0.0000) -- (axis cs:8.447,0.0202);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(8.447,0.0202)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(8.689,0.0000)};
\addlegendimage{ycomb, very thick, color=red!70!black, mark=*, mark size=1.4pt}
\addlegendentry{DCDHF-Me2}
\draw[very thick, color=red!70!black] (axis cs:3.318,0.0000) -- (axis cs:3.318,1.1239);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(3.318,1.1239)};
\draw[very thick, color=red!70!black] (axis cs:4.212,0.0000) -- (axis cs:4.212,0.0242);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(4.212,0.0242)};
\draw[very thick, color=red!70!black] (axis cs:4.508,0.0000) -- (axis cs:4.508,0.0062);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(4.508,0.0062)};
\draw[very thick, color=red!70!black] (axis cs:5.112,0.0000) -- (axis cs:5.112,0.0853);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.112,0.0853)};
\draw[very thick, color=red!70!black] (axis cs:5.286,0.0000) -- (axis cs:5.286,0.1138);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.286,0.1138)};
\draw[very thick, color=red!70!black] (axis cs:5.465,0.0000) -- (axis cs:5.465,0.0000);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.465,0.0000)};
\draw[very thick, color=red!70!black] (axis cs:5.473,0.0000) -- (axis cs:5.473,0.0810);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.473,0.0810)};
\draw[very thick, color=red!70!black] (axis cs:5.618,0.0000) -- (axis cs:5.618,0.0002);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.618,0.0002)};
\draw[very thick, color=red!70!black] (axis cs:5.984,0.0000) -- (axis cs:5.984,0.0525);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.984,0.0525)};
\draw[very thick, color=red!70!black] (axis cs:6.113,0.0000) -- (axis cs:6.113,0.0043);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.113,0.0043)};
\draw[very thick, color=red!70!black] (axis cs:6.170,0.0000) -- (axis cs:6.170,0.0218);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.170,0.0218)};
\draw[very thick, color=red!70!black] (axis cs:6.204,0.0000) -- (axis cs:6.204,0.0023);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.204,0.0023)};
\end{axis}
\begin{axis}[
    name=mupanel,
    at={(fpanel.below south west)}, anchor=north west,
    width=14cm, height=6.4cm,
    ylabel={dipole strength $|\mu|^2$ (a.u.)},
    xmin=2.5, xmax=9.2, ymin=0, ymax=17.284,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    xlabel={excitation energy (eV)},
]
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.458,0.0000)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.148,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:7.117,0.0000) -- (axis cs:7.117,3.4445);
\draw[very thick, color=blue!50!white] (axis cs:7.117,3.4445) -- (axis cs:7.117,6.8896);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.117,6.8896)};
\draw[black, thick] (axis cs:7.057,3.4445) -- (axis cs:7.176,3.4445);
\node[font=\small\bfseries, anchor=west] at (axis cs:7.216,3.4445) {B};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.697,0.0000)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.891,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:7.973,0.0000) -- (axis cs:7.973,0.0575);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.973,0.0575)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(7.994,0.0000)};
\draw[very thick, color=blue!65!black] (axis cs:8.447,0.0000) -- (axis cs:8.447,0.0977);
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(8.447,0.0977)};
\addplot[only marks, color=blue!65!black, mark=*, mark size=1.4pt, forget plot] coordinates {(8.689,0.0000)};
\draw[very thick, color=red!70!black] (axis cs:3.318,0.0000) -- (axis cs:3.318,13.8270);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(3.318,13.8270)};
\draw[very thick, color=red!70!black] (axis cs:4.212,0.0000) -- (axis cs:4.212,0.2343);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(4.212,0.2343)};
\draw[very thick, color=red!70!black] (axis cs:4.508,0.0000) -- (axis cs:4.508,0.0560);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(4.508,0.0560)};
\draw[very thick, color=red!70!black] (axis cs:5.112,0.0000) -- (axis cs:5.112,0.6807);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.112,0.6807)};
\draw[very thick, color=red!70!black] (axis cs:5.286,0.0000) -- (axis cs:5.286,0.8785);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.286,0.8785)};
\draw[very thick, color=red!70!black] (axis cs:5.465,0.0000) -- (axis cs:5.465,0.0003);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.465,0.0003)};
\draw[very thick, color=red!70!black] (axis cs:5.473,0.0000) -- (axis cs:5.473,0.6039);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.473,0.6039)};
\draw[very thick, color=red!70!black] (axis cs:5.618,0.0000) -- (axis cs:5.618,0.0014);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.618,0.0014)};
\draw[very thick, color=red!70!black] (axis cs:5.984,0.0000) -- (axis cs:5.984,0.3583);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(5.984,0.3583)};
\draw[very thick, color=red!70!black] (axis cs:6.113,0.0000) -- (axis cs:6.113,0.0290);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.113,0.0290)};
\draw[very thick, color=red!70!black] (axis cs:6.170,0.0000) -- (axis cs:6.170,0.1442);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.170,0.1442)};
\draw[very thick, color=red!70!black] (axis cs:6.204,0.0000) -- (axis cs:6.204,0.0151);
\addplot[only marks, color=red!70!black, mark=*, mark size=1.4pt, forget plot] coordinates {(6.204,0.0151)};
\end{axis}
```

**Figure 1.** Both molecules' computed states in two currencies on one
energy axis at CAM-B3LYP/def2-TZVP, deliberately un-normalized in each
panel. Top: oscillator strength — in dimensionless form, the integrated
molar absorptivity. Bottom: dipole strength $|\boldsymbol{\mu}|^{2}$. All
twelve computed states of each molecule appear in both panels; dark states
are markers on the axis, and no envelope is drawn because line widths are
not computed in this experiment. Benzene's exactly degenerate bright pair
is drawn stacked at 7.12 eV, the lighter segment being the second member;
**A** (top) and **B** (bottom) mark the same physical division seen in the
two measures. The ranking inverts between panels: in oscillator strength
benzene's band total, [benzene_bright_pair_f_total]{.metric}, edges past
the dye's single transition at [lowest_bright_f]{.metric}, while in dipole
strength the dye's [s1_dipole_strength_au]{.metric} a.u. stands at twice
benzene's whole band
([benzene_pair_total_dipole_strength_au]{.metric} a.u.) — because
oscillator strength prices dipole strength in units of transition energy,
and benzene's band sits at twice the energy.

The mechanism of the contrast fits in one sentence: benzene's symmetry
forces its bright transitions into a degenerate pair, and substituting a
donor on one side of the ring and an acceptor on the other does two things
at once — it destroys the symmetry that enforced the degeneracy, and it
creates the low-lying charge-transfer state benzene does not have, which is
where the funneled strength goes.

One thing this comparison is not: benzene's allowed band sits at 7.1 eV —
174 nm, deep vacuum-ultraviolet — so nothing here compares visible colors.
The comparison is about the composition of one apparent band. For benzene it
is two transitions sharing one line; for the dye it is one transition
wearing the whole band.

| State | E (eV) | λ (nm) | f | Dominant excitation |
|---:|---:|---:|---:|---|
| S1 | 5.46 | 227 | 0.0000 | HOMO→LUMO (49.7%); HOMO-1→LUMO+1 (49.7%) |
| S2 | 6.15 | 202 | 0.0000 | HOMO-1→LUMO (49.3%); HOMO→LUMO+1 (49.3%) |
| S3 | 7.12 | 174 | 0.6006 | HOMO-1→LUMO+1 (48.1%); HOMO→LUMO (48.1%) |
| S4 | 7.12 | 174 | 0.6007 | HOMO→LUMO+1 (48.1%); HOMO-1→LUMO (48.1%) |
| S5 | 7.70 | 161 | 0.0000 | HOMO→LUMO+2 (96.9%) |
| S6 | 7.70 | 161 | 0.0000 | HOMO-1→LUMO+2 (96.9%) |
| S7 | 7.89 | 157 | 0.0000 | HOMO-2→LUMO (49.3%); HOMO-3→LUMO+1 (48.7%) |
| S8 | 7.97 | 156 | 0.0112 | HOMO-2→LUMO+1 (49.8%); HOMO-3→LUMO (48.6%) |
| S9 | 7.99 | 155 | 0.0000 | HOMO-3→LUMO (49.5%); HOMO-2→LUMO+1 (48.3%) |
| S10 | 7.99 | 155 | 0.0000 | HOMO-3→LUMO+1 (49.2%); HOMO-2→LUMO (48.6%) |
| S11 | 8.45 | 147 | 0.0202 | HOMO→LUMO+3 (46.1%); HOMO-1→LUMO+4 (46.0%); HOMO-4→LUMO+2 (5.9%) |
| S12 | 8.69 | 143 | 0.0000 | HOMO-1→LUMO+4 (48.4%); HOMO→LUMO+3 (48.4%) |

**Table 2.** The twelve computed singlet states of benzene under the
identical protocol: forbidden states with exactly zero strength, and bright
strength arriving only as a degenerate pair. Every dominant excitation is an
almost exactly equal two-configuration mixture — the orbital-level
fingerprint of a degenerate frame.

## 6. Why the idealization is earned, not lucky

Set side by side under identical conditions, the two molecules answer the
title question in opposite ways. Of the strength shared by its two lowest
bright states, benzene's lower partner carries
[benzene_lowest_bright_f_share]{.metric}; DCDHF-Me2's carries
[lowest_bright_f_share]{.metric}. That number is the post in one line.

The two currencies of Figure 1 sharpen it further. In oscillator strength
the dye's S₁ carries [f_fraction_in_lowest_bright]{.metric} of its
molecule's computed total; in dipole strength it carries
[s1_dipole_strength_share]{.metric} — sharper, because dividing out the
energy weighting removes the head start that benzene's high-energy photons
give its f. The same factor explains the top panel's near-tie: benzene's
band edges past the dye in oscillator strength while carrying half the
dipole strength, paying for smaller dipoles with a photon twice as
energetic. And since oscillator strength is the integrated molar
absorptivity in dimensionless form, the top panel is the same quantity the
[molar absorptivity
note](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html) read as
a rate constant; what this experiment cannot supply is the band width that
would turn that integral into a peak height — the same gap already covered
by the caveat that no line widths are computed here.

It is also not luck. Oscillator strength is a budgeted quantity, and an f of
[lowest_bright_f]{.metric} in a single transition is a large fraction of
what a chromophore this size can carry — a molecule engineered for
single-molecule detection is a molecule engineered to be bright, and bright
means concentrating the available transition strength into the one state the
laser will drive. The DCDHF designers optimized brightness and
photostability;[@Lu2009] an isolated, dominant S₁ is a consequence of those
goals, not their stated aim, but the consequence is what the manifold shows.
Benzene, with no donor, no acceptor, and a symmetry that forbids
favoritism among equivalent directions, spreads the same budget across a
degenerate pair — and one substitution pattern later, on the same ring, the
degeneracy is gone and the funnel exists.

What the two-level model hides is therefore real but relocated. The dye's
higher states — several genuinely bright — sit between 4.5 and 6.2 eV,
which is exactly where the [previous
note](/posts/2026-08-12-from-blinking-to-absorption.html)'s excluded
channels operate: excited-state absorption out of S₁ terminates in this
manifold, and the states its nonlinear section reached with two photons live
here as well. Nothing in the visible band needs them; everything beyond the
two-level picture starts with them.

So the blinking note's idealization, applied to the dye class it was written
about, is not an approximation forced on an unwilling molecule. A
fluorophore engineered for single-molecule brightness behaves like a
two-level system because it was selected to; the approximation and the
design are the same fact read twice.

## 7. Reproducibility

Both molecules ran through the same two-stage pipeline
(`research/dcdhf-me2-transitions/`, driven by `run_all.sh`): geometry
optimization at B3LYP/def2-SVP (C1, `gau_tight`), then full-response TD-DFT
for the 12 lowest singlets at def2-TZVP with CAM-B3LYP and B3LYP, in Psi4
1.9.1 (conda env `psi4_19`, Python 3.10.17, NumPy 2.2.5), on 6 threads with
a 6 GB memory target, on x86_64 Linux. The DCDHF-Me2 starting geometry is
the Avogadro/UFF structure published in the 2025 supporting-information
note; benzene was built and optimized under the same protocol and, unlike
the dye, was recomputed rather than inherited from this site's earlier
push-pull work, because those numbers came from a software environment that
no longer exists on this machine. One solver fact is worth recording: Psi4
1.9.1's TD-DFT eigensolver runs at a fixed ceiling of 60 iterations — both
the driver keyword and the global option that appear to control it are
silently ignored — and an unconverged root raises an exception rather than
passing silently; every state reported here converged at the requested
residual tolerance of 10⁻⁵, and the experiment's results record the
requested and effective solver settings side by side. The rigid-displacement
stationary check of §3, its symmetry-pair self-validation, and the full
per-state records, spectra, metrics, and environment files are in the
experiment directory, and every quoted number above resolves from its
generated `metrics.json`. One reproduction datum: rerunning the stationary
check after the canonical run, to capture its environment record, reproduced
every reported value to the displayed precision.

## 8. Where the model stops

These are vertical electronic excitations of isolated molecules in vacuum,
twelve states deep. Nothing here has vibrational structure: no line widths
are computed anywhere in this experiment, which is why Figure 1 draws bare
sticks, and a real absorption band's width is dominated by vibronic
progressions and solvent broadening this calculation does not attempt.
Solvent shifts of charge-transfer states are large and absent here — both
functionals sit blue of the dye's experimental solution band, as vertical
gas-phase numbers should be expected to. We can say nothing about states
above the computed window, benzene's Rydberg states are poorly served by a
basis without diffuse functions, and the geometry underneath the dye's
spectrum is a stationary point interrogated along two suspect coordinates,
not a frequency-confirmed minimum. Finally, one diagnostic deserves its own
disclaimer: the automated charge-transfer classifier in our harness labels
states by the distance between hole and particle centroids, a metric that
understates charge transfer when both frontier orbitals delocalize over the
same conjugated backbone — for S₁ of the dye we trust the functional-shift
signature instead, and the classifier column stays in the experiment
directory rather than in Table 1.

## References
