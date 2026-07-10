---
title: "One donor, one acceptor, one new band: push–pull chromophores and charge transfer"
date: 2026-07-05
author: Peter Johnston
tags: quantum chemistry, TD-DFT, charge transfer, push-pull chromophores, UV-Vis, psi4, CAM-B3LYP
description: Aniline and nitrobenzene each absorb only in the ultraviolet. Bolt the amino donor and the nitro acceptor onto the same ring and a new band appears that neither parent owns — lower in energy and brighter than anything either shows alone. This post computes that emergence with TD-DFT, measures the charge-transfer character directly, and uses it to stress-test two density functionals against a failure mode one of them is famous for.
og-image: /images/push-pull-chromophores-charge-transfer.png
---

Aniline is a benzene ring carrying an amino group; its first absorption
band sits at 265 nm, far into the ultraviolet, and it is feeble. Nitrobenzene
is the same ring carrying a nitro group; its lowest bright band is weaker still.
Neither molecule absorbs anything of consequence past about 330 nm. Now put both
substituents on one ring, *para* to each other — **para-nitroaniline** — and a new
band appears at 311 nm that neither parent molecule owns, carrying an oscillator
strength of 0.32: roughly ten times brighter than aniline's band and twenty times
brighter than nitrobenzene's. Two weak ultraviolet absorbers combine into one
strong near-visible one, and the whole is emphatically not the sum of its parts.

The [pigments post](/posts/2026-07-04-the-physics-and-chemistry-of-pigments.html)
built the rule that color is an electronic energy gap in the 1.8–3.1 eV window,
and its Figure 2 made a promise: conjugation length is only one of the dials that
set an organic chromophore's gap, and the donor/acceptor dial would be "taken up
in a later post." This is that post. The mechanism is the **donor–π–acceptor**
(**D–π–A**, or **push–pull**) architecture, and it is how dye chemists move an
absorption band *without* growing the molecule — the working principle behind
azo dyes, many sunscreen actives, and essentially every organic nonlinear-optical
chromophore. Everything below is computed, not sketched: four molecules through
the same TD-DFT pipeline, with the full data record in the repo
(`calcs/uvvis-pushpull/`).

## 1. The push–pull architecture

The design has three parts. A **donor** group (here –NH₂) holds a high-lying
filled orbital — nitrogen's lone pair, conjugated into the ring — which pushes
the **HOMO** up. An **acceptor** group (here –NO₂) holds a low-lying empty π*
orbital, which pulls the **LUMO** down. A conjugated **π bridge** (here the
benzene ring) lets the two ends talk to each other. Raising the floor and
lowering the ceiling squeezes the HOMO–LUMO gap from both sides at once, which
red-shifts the transition further than either substituent manages alone
(Figure 1).

But the energy gap is only half of the design. Because the donor localizes the
HOMO on one end of the molecule and the acceptor localizes the LUMO on the
other, the HOMO→LUMO excitation physically *moves an electron across the
molecule* — from the amino end to the nitro end. That is an intramolecular
**charge-transfer (CT) transition**, the molecular sibling of the
ligand-to-metal and intervalence transfers that §5 of the pigments post found
in Prussian blue and the iron oxides. The electron traverses a real distance,
the transition dipole is correspondingly large, and — by the machinery of the
[molar absorptivity post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html) —
a large transition dipole means a large oscillator strength and a fast
radiative clock. Push–pull buys a redder *and* brighter band with one design.

## 2. The calculation

Four molecules isolate the two dials: **benzene** (bare bridge), **aniline**
(donor only), **nitrobenzene** (acceptor only), and **para-nitroaniline** (pNA,
donor and acceptor together). Each was built analytically, optimized at
B3LYP/def2-SVP in C1 symmetry with tight convergence, and then run through full
TD-DFT (RPA, not the Tamm–Dancoff approximation) for the twelve lowest singlet
states in the larger def2-TZVP basis,[@Weigend2005Balanced] with two
functionals per molecule: **B3LYP**, a global hybrid,[@Becke1993Exchange] and
**CAM-B3LYP**, its range-separated correction[@Yanai2004Coulomb] — the reason
for running both is §5. Everything ran in psi4 1.11;[@Smith2020Psi4] the core
of the excited-state call is Code 1.

```python
escf, wfn = psi4.energy(func, molecule=m2, return_wfn=True)   # func: b3lyp / cam-b3lyp
res = tdscf_excitations(wfn, states=12, tda=False,            # full RPA, 12 singlets
                        r_convergence=1e-5, maxiter=120)
for st in res:
    e_ev = float(st["EXCITATION ENERGY"]) * HA2EV
    f    = float(st["OSCILLATOR STRENGTH (LEN)"])             # length gauge
```

**Code 1.** The excited-state step, per molecule and functional: converge the
ground-state Kohn–Sham determinant, then solve the full TD-DFT (RPA) equations
for the twelve lowest singlets and read off each state's excitation energy and
length-gauge oscillator strength.

Two derived quantities do the interpretive work. First, each state's dominant
occupied→virtual excitation is located in space by the **hole–particle centroid
separation**: how far, in ångströms, the center of the departing electron
density sits from the center of the arriving density. A local π→π* state moves
the electron nowhere (separation near zero); a CT state moves it across the
molecule. States with separation ≥ 2 Å and appreciable brightness are labeled
CT by a deliberately conservative auto-classifier; subtler assignments (dark
n→π* versus symmetry-forbidden π→π*) are made by hand. Second, each molecule's
lowest bright state gets a **radiative lifetime** from the two-level relation
the [absorptivity post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
derived, $A_{21} = 1/\tau_{\text{rad}} = 0.667\,\tilde\nu^{2} f$ with
$\tilde\nu$ in cm⁻¹.

One stated shortcut: the basis carries **no diffuse functions** (def2-TZVP, not
def2-TZVPD). Diffuse sets are the recommended practice for CT and Rydberg
states, so the absolute energies below — especially the deep-UV states — would
shift somewhat with them. The B3LYP-versus-CAM-B3LYP *comparison*, which is the
methodological point, is robust to this.

## 3. Donor alone, acceptor alone

Table 1 collects the lowest bright band of each molecule under each functional,
and Figure 1 shows the broadened CAM-B3LYP spectra.

| molecule | functional | λmax (nm) | E (eV) | f | τ_rad (ns) | band |
|---|---|---|---|---|---|---|
| benzene | B3LYP | 176 | 7.03 | 0.578 | 0.8 | π→π* (E1u) |
| benzene | CAM-B3LYP | 174 | 7.12 | 0.601 | 0.8 | π→π* (E1u) |
| aniline | B3LYP | 265 | 4.68 | 0.037 | 28.6 | π→π* |
| aniline | CAM-B3LYP | 255 | 4.87 | 0.041 | 23.8 | π→π* |
| nitrobenzene | B3LYP | 283 | 4.38 | 0.014 | 83.1 | π→π* (weak) |
| nitrobenzene | CAM-B3LYP | 255 | 4.86 | 0.018 | 53.8 | π→π* (weak) |
| para-nitroaniline | B3LYP | 311 | 3.98 | 0.324 | 4.5 | **CT** |
| para-nitroaniline | CAM-B3LYP | 282 | 4.40 | 0.378 | 3.2 | **CT** |

**Table 1.** The lowest bright excited state (f ≥ 0.01) of each molecule under
each functional: wavelength, energy, oscillator strength, two-level radiative
lifetime, and band assignment. The push–pull molecule's lowest bright state is
the charge-transfer band — the reddest and by far the brightest entry in the
table, with the shortest radiative lifetime of the three substituted rings.

**The bare bridge sets the baseline.** Benzene's two lowest singlets (computed
at 231 and 205 nm with B3LYP) are the textbook symmetry-forbidden ¹B₂ᵤ and ¹B₁ᵤ
states — oscillator strengths numerically zero — and its first *bright*
absorption is the degenerate ¹E₁ᵤ pair at 176 nm, off the left edge of
Figure 1's window. Experimentally that band sits near 179 nm in the gas phase;[@Hiraya1991Benzene]
the computed values land within 0.1–0.2 eV of it. An
unsubstituted ring is transparent until the deep ultraviolet.

**A donor alone red-shifts, weakly.** Conjugating the amino lone pair into the
ring pushes the HOMO up, and aniline's first π→π* lands at 265 nm (B3LYP) /
255 nm (CAM-B3LYP) — a large shift from 176 nm, but with oscillator strength
only ≈ 0.04, and a correspondingly lazy radiative lifetime of 24–29 ns. The
vapor-phase experiment puts this band near 282 nm.[@Kimura1964Aniline] The
donor moved the gap; it did not produce a strong band.

**An acceptor alone red-shifts differently.** The nitro group drags in its own
low-lying π* and lone-pair states: nitrobenzene's lowest state is a *dark*
n→π* near 320 nm (f ≈ 0), its lowest nominally bright band (283/255 nm) is
weak, f ≈ 0.014–0.018, and its genuinely strong π→π* sits one state higher at
259 nm (B3LYP) / 240 nm (CAM-B3LYP) with f ≈ 0.2 — the band the classic
vapor-and-solution study of nitrobenzene, which observed it near 252 nm,
assigned as intramolecular charge transfer toward the nitro group.[@Nagakura1964Nitrobenzene]
The weak lowest bright state's radiative lifetime stretches to 54–83 ns —
exactly the weak-absorber-is-slow-emitter lockstep the
[absorptivity post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
predicts.

```tikzpicture
\begin{axis}[
    width=13cm, height=8.5cm,
    xlabel={wavelength (nm)},
    ylabel={$\varepsilon$ (L\,mol$^{-1}$\,cm$^{-1}$)},
    title={Computed spectra (CAM-B3LYP, 0.35 eV Gaussian broadening)},
    xmin=200, xmax=400, ymin=0, ymax=31000,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    scaled y ticks=false,
    y tick label style={/pgf/number format/.cd, 1000 sep={\,}}
]
\addplot[thick, color=black!45] coordinates { (200,0) (400,0) };
\addplot[thick, color=blue] coordinates {
(201,273) (204,691) (207,1404) (210,2507) (213,4275) (216,6623) (219,8523)
(222,8705) (225,7004) (228,4481) (231,2322) (234,1023) (237,498) (240,516)
(243,923) (246,1602) (249,2367) (252,2957) (255,3152) (258,2899) (261,2323)
(264,1637) (267,1023) (270,572) (273,289) (276,132) (279,55) (282,21) (285,8)
(288,3) (291,1) (294,0) (400,0)
};
\addplot[thick, color=orange!85!black] coordinates {
(201,957) (204,230) (207,61) (210,17) (213,5) (216,11) (219,70) (222,334)
(225,1189) (228,3218) (231,6753) (234,11200) (237,14940) (240,16320)
(243,14890) (246,11630) (249,8040) (252,5170) (255,3272) (258,2116) (261,1391)
(264,896) (267,548) (270,314) (273,171) (276,90) (279,49) (282,28) (285,17)
(288,11) (291,7) (294,4) (297,2) (300,1) (303,1) (306,0) (400,0)
};
\addplot[very thick, color=green!45!black] coordinates {
(201,1660) (204,540) (207,343) (210,737) (213,1862) (216,3651) (219,5352)
(222,5946) (225,5109) (228,3463) (231,1887) (234,842) (237,317) (240,118)
(243,84) (246,138) (249,254) (252,435) (255,725) (258,1277) (261,2406)
(264,4558) (267,8114) (270,13070) (273,18830) (276,24200) (279,27880)
(282,28940) (285,27220) (288,23350) (291,18360) (294,13310) (297,8935)
(300,5584) (303,3263) (306,1790) (309,926) (312,453) (315,210) (318,93)
(321,39) (324,16) (327,6) (330,2) (333,1) (336,0) (400,0)
};
\legend{benzene, aniline, nitrobenzene, para-nitroaniline}
\node[font=\small\bfseries, text=green!35!black] at (axis cs:315,26000) {CT band};
\draw[-{Stealth[length=5pt]}, green!35!black] (axis cs:305,25000) -- (axis cs:288,24500);
\node[font=\footnotesize, align=center, text=black!70] at (axis cs:239,25200) {benzene $^1$E$_{1u}$ band\\174 nm, off scale};
\draw[-{Stealth[length=5pt]}, black!45] (axis cs:213,23600) -- (axis cs:200.5,21600);
\end{axis}
```

**Figure 1.** Broadened CAM-B3LYP absorption spectra of the four molecules
(Gaussian broadening, FWHM 0.35 eV). Benzene is flat across the whole window —
its first allowed band lies at 174 nm, off the left edge. Aniline (donor only)
and nitrobenzene (acceptor only) each raise structure in the 220–260 nm region
but nothing beyond ~310 nm. Para-nitroaniline's charge-transfer band at 282 nm
is a new feature that neither parent shows: the reddest and strongest band in
the figure, produced by the donor and acceptor acting *together*.

## 4. The band neither parent owns

Para-nitroaniline's lowest bright state is the payoff. It is a nearly pure
HOMO→LUMO excitation (96.6% single-configuration weight with B3LYP), it lands at 311 nm
(B3LYP) / 282 nm (CAM-B3LYP) — to the red of every bright band either parent
molecule has — and it carries f ≈ 0.32–0.38, the largest oscillator strength of
any computed state below 5 eV in the entire four-molecule study. The
hole–particle centroid separation for this state is **2.6 Å**: the excitation
physically relocates an electron by more than a bond length, from the amino end
toward the nitro end. The local π→π* states of the same molecule stay at or
below 1.3 Å on the same diagnostic (B3LYP values). This is charge transfer
measured, not asserted.

The two-level radiative lifetime makes the brightness concrete: 3–5 ns, against
24–29 ns for aniline and 54–83 ns for nitrobenzene. On the
[absorptivity post's](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
inverse lockstep between absorption strength and emission time, the push–pull
band is the fast, strong end of the family — and it is the same transition
dipole, computed from the same wavefunctions, driving both numbers.

The ground-state geometry quietly corroborates the story (Table 2). In
isolated aniline the amino nitrogen is genuinely pyramidal — the lone pair only
partly commits to the ring, and the N–H bonds pucker 14.4° out of plane. In pNA
the *same* group flattens to 4.5°, and the nitro group holds exactly coplanar
with the ring. The push–pull conjugation is strong enough to iron the donor
nearly flat: the molecule pre-organizes its own π system to make the
donor-to-acceptor communication — and hence the CT transition — as strong as
possible.

| molecule | –NH₂ pyramidalization | –NO₂ twist vs ring |
|---|---|---|
| aniline | 14.4° (N angle-sum 345.6°) | — |
| nitrobenzene | — | 0.0° (coplanar) |
| para-nitroaniline | 4.5° (N angle-sum 355.5°) | 0.1° (coplanar) |

**Table 2.** Optimized-geometry diagnostics (B3LYP/def2-SVP, all fully relaxed
in C1). Isolated aniline's donor is genuinely pyramidal; in the push–pull
molecule the same –NH₂ is ironed nearly flat and the acceptor –NO₂ sits
coplanar, maximizing conjugation across the bridge.

## 5. Two functionals, one diagnostic

Why run every molecule twice? Because charge-transfer states are the textbook
failure mode of standard TD-DFT. A global hybrid like B3LYP, with a fixed
fraction of exact exchange, lacks the correct long-range −1/R attraction
between the separated hole and electron, and therefore places CT states too low
— sometimes catastrophically so.[@Dreuw2004] Range-separated functionals like
CAM-B3LYP switch in full exact exchange at long interelectronic distance
precisely to fix this.[@Yanai2004Coulomb] A push–pull molecule computed with
both functionals is therefore a built-in stress test: local states should barely
move between them, and CT states should move a lot.

That is exactly what the data do. Benzene's E₁ᵤ shifts by +0.09 eV from B3LYP
to CAM-B3LYP; aniline's local π→π* by +0.19 eV. Para-nitroaniline's CT band
shifts by **+0.42 eV** (3.98 → 4.40 eV, 311 → 282 nm) — several times the local
states' movement (Figure 2). Nitrobenzene is the instructive middle case: its
low-lying π→π* states already shove density toward the nitro group
(hole–particle separations of 1.9–2.0 Å, just under the CT threshold), and they
shift by 0.39–0.47 eV — functional sensitivity tracks CT character even where
the classifier's label doesn't change. Plotting the B3LYP→CAM-B3LYP shift of
each matched bright state against its hole–particle separation (Figure 3) makes
the pattern plain: states that move the electron under ~1 Å shift by ≲ 0.2 eV,
and states that move it ~2 Å or more shift by 0.3–0.5 eV. The disagreement
between two functionals is itself a CT diagnostic — you can *see* the missing
long-range exchange turning on.

```tikzpicture
\begin{axis}[
    width=13cm, height=8cm,
    xlabel={wavelength (nm)},
    ylabel={$\varepsilon$ (L\,mol$^{-1}$\,cm$^{-1}$)},
    title={The pNA charge-transfer band under two functionals},
    xmin=230, xmax=400, ymin=0, ymax=31000,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    scaled y ticks=false,
    y tick label style={/pgf/number format/.cd, 1000 sep={\,}}
]
\addplot[thick, color=blue] coordinates {
(231,311) (234,754) (237,1576) (240,2688) (243,3761) (246,4371) (249,4276)
(252,3563) (255,2561) (258,1607) (261,897) (264,461) (267,237) (270,143)
(273,122) (276,156) (279,279) (282,583) (285,1227) (288,2424) (291,4383)
(294,7221) (297,10860) (300,14970) (303,19000) (306,22300) (309,24310)
(312,24720) (315,23530) (318,21050) (321,17770) (324,14190) (327,10750)
(330,7756) (333,5341) (336,3521) (339,2227) (342,1355) (345,794) (348,450)
(351,247) (354,131) (357,68) (360,34) (363,17) (366,8) (369,4) (372,2)
(375,1) (378,0) (400,0)
};
\addplot[thick, color=green!45!black] coordinates {
(231,1887) (234,842) (237,317) (240,118) (243,84) (246,138) (249,254)
(252,435) (255,725) (258,1277) (261,2406) (264,4558) (267,8114) (270,13070)
(273,18830) (276,24200) (279,27880) (282,28940) (285,27220) (288,23350)
(291,18360) (294,13310) (297,8935) (300,5584) (303,3263) (306,1790) (309,926)
(312,453) (315,210) (318,93) (321,39) (324,16) (327,6) (330,2) (333,1)
(336,0) (400,0)
};
\addplot[dashed, thick, color=black!70] coordinates { (292,0) (292,31000) };
\legend{B3LYP, CAM-B3LYP}
\node[font=\small, text=black!70, anchor=west] at (axis cs:293,29800) {exp.\ (vapor) 292 nm};
\node[font=\small, text=blue, anchor=west] at (axis cs:318,24500) {311 nm};
\node[font=\small, text=green!35!black, anchor=east] at (axis cs:276,29200) {282 nm};
\draw[{Stealth[length=5pt]}-{Stealth[length=5pt]}, black!75, thick] (axis cs:282,26200) -- (axis cs:311,26200);
\node[font=\small\bfseries, fill=white, inner sep=1.5pt] at (axis cs:296.5,26200) {0.42 eV};
\end{axis}
```

**Figure 2.** Para-nitroaniline's charge-transfer band computed with B3LYP
(blue, 311 nm) and CAM-B3LYP (green, 282 nm). The 0.42 eV disagreement between
the two functionals is several times what the same pair produces for the local
π→π* bands of benzene or aniline — the signature of B3LYP's missing long-range
exchange for charge-separated states. The dashed line marks the vapor-phase
experimental band at 292 nm: B3LYP overshoots to the red (−0.26 eV), CAM-B3LYP
lands slightly blue (+0.16 eV).

```tikzpicture
\begin{axis}[
    width=14cm, height=9cm,
    xlabel={hole--particle centroid separation (\AA)},
    ylabel={$\Delta E$ (CAM-B3LYP $-$ B3LYP) (eV)},
    title={Functional disagreement tracks charge-transfer character},
    xmin=-0.25, xmax=3.6, ymin=0, ymax=0.60,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[only marks, mark=*, mark size=3pt, color=blue] coordinates {
(0.0,0.09) (0.84,0.19)
};
\addplot[only marks, mark=square*, mark size=3pt, color=orange!85!black] coordinates {
(1.91,0.39) (1.96,0.47) (2.08,0.29)
};
\addplot[only marks, mark=triangle*, mark size=4.5pt, color=green!45!black] coordinates {
(2.63,0.42)
};
\draw[gray!55, thin] (axis cs:1.88,0.39) -- (axis cs:1.57,0.35);
\draw[gray!55, thin] (axis cs:2.11,0.29) -- (axis cs:2.34,0.25);
\draw[gray!55, thin] (axis cs:1.96,0.475) -- (axis cs:1.90,0.505);
\node[font=\footnotesize, anchor=west] at (axis cs:0.07,0.095) {benzene $^1$E$_{1u}$};
\node[font=\footnotesize, anchor=west] at (axis cs:0.92,0.185) {aniline $\pi\to\pi^*$};
\node[font=\footnotesize, anchor=east, align=right] at (axis cs:1.55,0.35) {nitrobenzene\\$\pi\to\pi^*$ (strong)};
\node[font=\footnotesize, anchor=south, align=center] at (axis cs:1.90,0.51) {nitrobenzene\\$\pi\to\pi^*$ (weak)};
\node[font=\footnotesize, anchor=west] at (axis cs:2.36,0.24) {aniline CT};
\node[font=\footnotesize\bfseries, anchor=south west] at (axis cs:2.66,0.45) {pNA CT};
\end{axis}
```

**Figure 3.** The B3LYP→CAM-B3LYP energy shift of each bright state, plotted
against that state's hole–particle centroid separation (states matched across
functionals by their dominant orbital transition; separations from the B3LYP
calculation). Spatially local excitations (left) barely feel the functional
change; excitations that move the electron 2 Å or more (right) shift by
0.3–0.5 eV. Nitrobenzene's nominally "local" low states sit in between — their
density already leans toward the nitro group — which is exactly where a
CT-sensitivity diagnostic should place them.

Validation against experiment keeps the comparison honest (Table 3). No number
below was tuned; the experimental values are literature gas-phase or vapor band
maxima [@Hiraya1991Benzene; @Kimura1964Aniline; @Nagakura1964Nitrobenzene;
@Millefiori1977Nitroanilines].

| molecule | band | B3LYP | CAM-B3LYP | experiment | Δ B3LYP | Δ CAM |
|---|---|---|---|---|---|---|
| benzene | ¹E₁ᵤ π→π* | 7.03 eV | 7.12 eV | ~6.94 eV (179 nm, gas) | +0.09 | +0.18 |
| aniline | π→π* | 4.68 eV | 4.87 eV | ~4.40 eV (~282 nm, vapor) | +0.28 | +0.47 |
| nitrobenzene | strong π→π* | 4.78 eV | 5.17 eV | ~4.90 eV (~252 nm) | −0.12 | +0.27 |
| para-nitroaniline | **CT** | 3.98 eV | 4.40 eV | ~4.24 eV (292 nm, vapor) | **−0.26** | **+0.16** |

**Table 3.** Computed vertical excitation energies against experimental band
maxima (computed − experiment in the last two columns). Absolute errors are
typical TD-DFT, a few tenths of an eV either way. The pattern is the point: for
the CT band, B3LYP errs low — the known global-hybrid underestimation — while
CAM-B3LYP lands slightly high, and the two functionals bracket the measurement.

One caution on that table: pNA is strongly solvatochromic. Its CT band slides
from 292 nm in vapor to roughly 380 nm in water, because the enormous
excited-state dipole — the electron has, after all, just crossed the molecule —
is stabilized by polar solvent [@Millefiori1977Nitroanilines;
@Kosenkov2011Solvent]. The gas-phase computed values here are compared to
gas-phase experiment; neither should be matched against an aqueous spectrum.

## 6. The optimizer on a saddle

A methodological embarrassment is worth recording, because it is the kind that
produces quietly wrong papers. The *first* geometry optimization returned
aniline and pNA with perfectly planar amino groups — pyramidalization exactly
0.0°, nitrogen angle-sum exactly 360°. That is not the minimum; it is the
planar *inversion transition state*, the top of the umbrella-flip barrier.

The root cause was the starting guess. The molecules were built analytically,
and the initial amino group placed its two N–H hydrogens symmetrically on
*opposite* sides of the ring plane. That arrangement preserves a mirror
symmetry whose consequence is that the gradient along the pyramidalization
coordinate is zero *by symmetry* at the planar geometry — so the optimizer,
which only ever follows the gradient downhill, converged to the saddle and
reported success. Re-seeding both hydrogens on the *same* side (an "umbrella"
start, symmetry deliberately broken) let the optimization roll off the saddle
into the true pyramidal minimum: 14.4° for aniline, 4.5° for pNA. Same
functional, same basis, same optimizer, same convergence criteria — the only
change was the symmetry of the starting point.

The excited-state story survived the correction almost untouched: aniline's
bright band moved 269 → 265 nm and the pNA CT band 312 → 311 nm (B3LYP). But
the *geometry* claims — Table 2's entire donor-flattening narrative — would
have been silently wrong, with every diagnostic reading a clean 0.0°. An
optimizer converging is not the same thing as an optimizer finding a minimum;
symmetric starting guesses find symmetric stationary points, whatever their
character.

## 7. What this does and does not show

The limits, stated plainly. These are **vertical** excitation energies compared
against experimental band *maxima* — a standard but imperfect pairing, since
vibrational structure shifts a band's maximum away from its vertical energy.
The basis omits diffuse functions, which matter most for exactly the CT and
high-lying states of interest; the absolute numbers would move with a
diffuse-augmented basis, though the two-functional comparison would not. The
calculations are gas-phase, and §5's solvatochromism caution applies to any
comparison with solution data. And the two-level radiative lifetimes inherit
every caveat of the [absorptivity post's](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
idealization — real photophysics adds non-radiative channels that only shorten
the observed lifetime. Within those limits, the qualitative structure — the
emergent CT band, its brightness, its 2.6 Å electron displacement, its
functional sensitivity — is exactly the physics the D–π–A design predicts.

## The dial behind the dye catalog

The [pigments post](/posts/2026-07-04-the-physics-and-chemistry-of-pigments.html)
established that an organic colorant is a conjugated π system whose HOMO–LUMO
gap sits in the visible window, and that lengthening the conjugation shrinks
the gap. This post computed the second dial: keep the bridge fixed and install
a donor and an acceptor at its ends, and the gap closes from both sides while
the transition acquires charge-transfer character — redder *and* brighter, the
two things a dye chemist wants and the particle-in-a-box argument alone cannot
deliver. Para-nitroaniline's 2.6 Å of electron displacement is also why its
excited state carries a huge dipole moment, which is why pNA is the fruit-fly
molecule of organic nonlinear optics — the field the
[Pockels-effect post](/posts/2026-07-03-one-matrix-element-absorptivity-and-the-pockels-effect.html)
introduced through the same transition-dipole matrix element. Push the same
design further — stronger donors, stronger acceptors, longer bridges — and the
CT band walks out of the ultraviolet and into the visible window, where the
azo yellows and reds of the modern palette live. The full data record,
geometries, and scripts for every number in this post are in the repo under
`calcs/uvvis-pushpull/`.

## References
