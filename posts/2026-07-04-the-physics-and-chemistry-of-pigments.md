---
title: "The colors on the palette are energy-level gaps: engineering pigments for permanence"
date: 2026-07-04
author: Peter Johnston
tags: pigments, color, chromophores, lightfastness, charge transfer, ligand field, band gap, conjugation, Kubelka-Munk
description: A tube of paint is an electronic-structure problem plus a scattering problem, perceived by an eye. This post builds the mechanism-first taxonomy of color — conjugated π-systems, ligand-field d–d transitions, charge transfer, and semiconductor band gaps — leading with the modern synthetic pigments engineered to fix the lightfastness failures of their historic ancestors, then puts absorption and scattering back together with Kubelka–Munk.
---

A tube labeled cadmium-red-*hue* usually contains no cadmium. The colorant is a
diketopyrrolopyrrole (DPP), a synthetic organic red substituted for cadmium
sulfoselenide because cadmium is toxic and the organic reds that preceded cadmium
pigments — madder, carmine — faded under light. That substitution is this post's
subject. A pigment's color is a HOMO–LUMO gap of a few electron-volts positioned
where the eye can detect it. Its permanence is a separate property, achieved only
by deliberate molecular engineering. Historically, the same color-producing
physics kept yielding pigments that were either vivid and fugitive or permanent
and toxic; the modern synthetic palette is built to avoid both failure modes at
once.

The earlier posts in this series built the machinery for the first of those
claims without pointing it at paint. The
[fundamentals post](/posts/fundamentals_of_quantum_chemistry.html) solved the
particle in a box and found that confining an electron quantizes its energy into
discrete levels whose spacing shrinks as the box grows. The
[water post](/posts/2026-06-30-reading-water-geometry-orbitals-acidity-spectra.html)
and the [Hartree–Fock post](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html)
turned those levels into molecular orbitals with computable energies, and
established that the gap between a filled and an empty orbital is what a
molecule shows to light. A pigment is that abstraction applied to a physical,
purchasable material. This post answers three questions in order — *what is a
pigment*, *what molecular structures make it colored*, and *how does it
physically interact with light* — and returns repeatedly to lightfastness: why
a chromophore that absorbs visible light is also, for the chemical reasons given
in §8, prone to degrading under it.

## 1. Pigment, dye, and lake

The first distinction is not about color at all; it is about solubility, and it is
operational. A **dye** is a colorant that dissolves — its molecules disperse
individually into the medium, bound to a substrate or floating free in solution,
each molecule surrounded by solvent. A **pigment** is a colorant that does *not*
dissolve: it stays as discrete solid particles, suspended in but chemically aloof
from the binder that carries it — gum, oil, acrylic emulsion, egg yolk. The same
chromophore can play either role depending on how it is presented to the medium;
what makes a paint a *pigment* paint is that the colored matter remains a
particulate phase with its own surfaces, its own crystal structure, and its own
refractive index, all of which will matter in §7. The binder's job is to glue
those particles to a surface and to each other, not to take them into solution.
When you thin a tube color, you are diluting a suspension, not a
solution.[@Berns2019; @Christie2014]

A **lake** is the boundary case between dye and pigment: a dye made to behave
like a pigment by precipitating it onto an inert, colorless particulate substrate
— historically aluminum hydroxide, sometimes chalk or a metal salt. The soluble
dye is *adsorbed* or chemically fixed onto the substrate grains, and the
resulting colored solid is ground into a binder exactly like any pigment.
**Madder lake** (the dye alizarin laid down on alumina) and **carmine**
(cochineal's carminic acid, likewise laked) are the canonical examples — deep,
transparent reds and crimsons used throughout historic palettes. They are also,
not coincidentally, among the most **fugitive** colors ever used: the same
molecules that make a brilliant transparent lake photochemically decompose under
light. A lake's chromophore is chemically still the dissolved dye — laking
changes how the colorant is dispersed, not its intrinsic photostability — which
is why lakes fade like the dyes they are made from. This fragility recurs through
the rest of the post as lightfastness.[@Eastaugh2008; @Zollinger2003]

One more boundary, then we set it aside. Not all color is pigmentation. The blue
of a morpho butterfly, the green of a beetle's shell, the flash of an opal — these
are **structural colors**, produced by interference and diffraction from
nanoscale physical architecture, with no light-absorbing molecule involved at all.
Tilt the wing and the color shifts; grind it to powder and the color dies, because
you have destroyed the structure that made it. That is a wave-optics phenomenon,
not a chromophore, and although it shares the visible spectrum with everything
below, it is a different subject. Everything else in this post is about color that
survives grinding: molecules and crystals that *absorb* particular photons.

## 2. What makes a molecule colored

A material has a color in the ordinary sense when it selectively absorbs some of
the visible photons that fall on it and returns the rest. Visible light spans
roughly **400 to 700 nm**, which in energy is about **3.1 down to 1.8 eV** — a
narrow window, and the entire constraint on what can be colored: a substance is
colored if and only if it has an accessible electronic transition — an energy gap
between an occupied and an empty state — that lands *inside* it (Figure 1). A gap
larger than ~3.1 eV absorbs only in the ultraviolet and leaves all visible light
untouched (the material is white, clear, or colorless); a gap smaller than ~1.8 eV
absorbs in the infrared and, if it absorbs *across* the whole visible range, reads
as black, gray, or metallic. Color requires the gap to fall between those two
limits.

```tikzpicture
%% ===== Figure 1 (generated): the visible window =====
\fill[black!7] (-3.0,4.3) rectangle (0.0,5.7);
\draw[black!35] (-3.0,4.3) rectangle (0.0,5.7);
\node[font=\small\bfseries,text=black!55] at (-1.5,5.3500000000000005) {UV};
\node[font=\scriptsize,text=black!50,align=center] at (-1.5,4.72) {gap $>3.1$ eV\\colorless};
\definecolor{sp400}{HTML}{5000FF}
\definecolor{sp410}{HTML}{8700FF}
\definecolor{sp420}{HTML}{7400FF}
\definecolor{sp430}{HTML}{6100FF}
\definecolor{sp440}{HTML}{6A00FF}
\definecolor{sp450}{HTML}{5600FF}
\definecolor{sp460}{HTML}{0000FF}
\definecolor{sp470}{HTML}{002DFF}
\definecolor{sp480}{HTML}{0085FF}
\definecolor{sp490}{HTML}{00EEFF}
\definecolor{sp500}{HTML}{00FFA0}
\definecolor{sp510}{HTML}{00FF4A}
\definecolor{sp520}{HTML}{00FF00}
\definecolor{sp530}{HTML}{00FF00}
\definecolor{sp540}{HTML}{00FF00}
\definecolor{sp550}{HTML}{00FF00}
\definecolor{sp560}{HTML}{9DFF00}
\definecolor{sp570}{HTML}{FFFE00}
\definecolor{sp580}{HTML}{FFB300}
\definecolor{sp590}{HTML}{FF7D00}
\definecolor{sp600}{HTML}{FF4A00}
\definecolor{sp610}{HTML}{FF0000}
\definecolor{sp620}{HTML}{FF0000}
\definecolor{sp630}{HTML}{FF0000}
\definecolor{sp640}{HTML}{FF0000}
\definecolor{sp650}{HTML}{FF0000}
\definecolor{sp660}{HTML}{FF0000}
\definecolor{sp670}{HTML}{FF0000}
\definecolor{sp680}{HTML}{FF0000}
\definecolor{sp690}{HTML}{FF0000}
\definecolor{sp700}{HTML}{FF0000}
\shade[left color=sp400,right color=sp410] (0.000,4.3) rectangle (0.400,5.7);
\shade[left color=sp410,right color=sp420] (0.400,4.3) rectangle (0.800,5.7);
\shade[left color=sp420,right color=sp430] (0.800,4.3) rectangle (1.200,5.7);
\shade[left color=sp430,right color=sp440] (1.200,4.3) rectangle (1.600,5.7);
\shade[left color=sp440,right color=sp450] (1.600,4.3) rectangle (2.000,5.7);
\shade[left color=sp450,right color=sp460] (2.000,4.3) rectangle (2.400,5.7);
\shade[left color=sp460,right color=sp470] (2.400,4.3) rectangle (2.800,5.7);
\shade[left color=sp470,right color=sp480] (2.800,4.3) rectangle (3.200,5.7);
\shade[left color=sp480,right color=sp490] (3.200,4.3) rectangle (3.600,5.7);
\shade[left color=sp490,right color=sp500] (3.600,4.3) rectangle (4.000,5.7);
\shade[left color=sp500,right color=sp510] (4.000,4.3) rectangle (4.400,5.7);
\shade[left color=sp510,right color=sp520] (4.400,4.3) rectangle (4.800,5.7);
\shade[left color=sp520,right color=sp530] (4.800,4.3) rectangle (5.200,5.7);
\shade[left color=sp530,right color=sp540] (5.200,4.3) rectangle (5.600,5.7);
\shade[left color=sp540,right color=sp550] (5.600,4.3) rectangle (6.000,5.7);
\shade[left color=sp550,right color=sp560] (6.000,4.3) rectangle (6.400,5.7);
\shade[left color=sp560,right color=sp570] (6.400,4.3) rectangle (6.800,5.7);
\shade[left color=sp570,right color=sp580] (6.800,4.3) rectangle (7.200,5.7);
\shade[left color=sp580,right color=sp590] (7.200,4.3) rectangle (7.600,5.7);
\shade[left color=sp590,right color=sp600] (7.600,4.3) rectangle (8.000,5.7);
\shade[left color=sp600,right color=sp610] (8.000,4.3) rectangle (8.400,5.7);
\shade[left color=sp610,right color=sp620] (8.400,4.3) rectangle (8.800,5.7);
\shade[left color=sp620,right color=sp630] (8.800,4.3) rectangle (9.200,5.7);
\shade[left color=sp630,right color=sp640] (9.200,4.3) rectangle (9.600,5.7);
\shade[left color=sp640,right color=sp650] (9.600,4.3) rectangle (10.000,5.7);
\shade[left color=sp650,right color=sp660] (10.000,4.3) rectangle (10.400,5.7);
\shade[left color=sp660,right color=sp670] (10.400,4.3) rectangle (10.800,5.7);
\shade[left color=sp670,right color=sp680] (10.800,4.3) rectangle (11.200,5.7);
\shade[left color=sp680,right color=sp690] (11.200,4.3) rectangle (11.600,5.7);
\shade[left color=sp690,right color=sp700] (11.600,4.3) rectangle (12.000,5.7);
\draw[black,line width=0.8pt] (0.0,4.3) rectangle (12.0,5.7);
\shade[left color=black!75,right color=black] (12.0,4.3) rectangle (15.0,5.7);
\draw[black!35] (12.0,4.3) rectangle (15.0,5.7);
\node[font=\small\bfseries,text=white] at (13.5,5.3500000000000005) {IR};
\node[font=\scriptsize,text=black!45,align=center] at (13.5,4.72) {gap $<1.8$ eV\\black};
\node[font=\footnotesize,text=black!55] at (2.400,6.0200000000000005) {$\leftarrow$ larger gap};
\node[font=\footnotesize,text=black!55] at (9.800,6.0200000000000005) {smaller gap $\rightarrow$};
\draw[black!55] (0.000,4.3) -- (0.000,4.14);
\draw[black!55] (4.000,4.3) -- (4.000,4.14);
\draw[black!55] (8.000,4.3) -- (8.000,4.14);
\draw[black!55] (12.000,4.3) -- (12.000,4.14);
\node[font=\small,align=center] at (0.0,3.7199999999999998) {400 nm\\[-1pt]\footnotesize 3.1 eV};
\node[font=\small] at (4.000,3.8) {500 nm};
\node[font=\small] at (8.000,3.8) {600 nm};
\node[font=\small,align=center] at (12.0,3.7199999999999998) {700 nm\\[-1pt]\footnotesize 1.8 eV};
\definecolor{c460abs}{HTML}{0000FF}
\definecolor{c460per}{HTML}{FFE449}
\draw[gray,dash pattern=on 2pt off 2pt] (2.400,4.3) -- (2.400,2.5);
\fill[black] (2.400,4.3) circle (2.2pt);
\node[font=\small] at (2.400,2.28) {$\Delta E\approx2.70$ eV};
\filldraw[fill=c460abs,draw=black!55] (1.220,0.95) rectangle (2.140,1.87);
\node[font=\scriptsize,text=black!70] at (1.680,0.6699999999999999) {absorbs};
\draw[-{Stealth[length=5pt]},thick] (2.220,1.410) -- (2.580,1.410);
\filldraw[fill=c460per,draw=black!55] (2.660,0.95) rectangle (3.580,1.87);
\node[font=\scriptsize,text=black!70] at (3.120,0.6699999999999999) {appears};
\node[font=\small\bfseries] at (3.120,0.32999999999999996) {yellow};
\definecolor{c530abs}{HTML}{00FF00}
\definecolor{c530per}{HTML}{FF65E2}
\draw[gray,dash pattern=on 2pt off 2pt] (5.200,4.3) -- (5.200,2.5);
\fill[black] (5.200,4.3) circle (2.2pt);
\node[font=\small] at (5.200,2.28) {$\Delta E\approx2.34$ eV};
\filldraw[fill=c530abs,draw=black!55] (4.020,0.95) rectangle (4.940,1.87);
\node[font=\scriptsize,text=black!70] at (4.480,0.6699999999999999) {absorbs};
\draw[-{Stealth[length=5pt]},thick] (5.020,1.410) -- (5.380,1.410);
\filldraw[fill=c530per,draw=black!55] (5.460,0.95) rectangle (6.380,1.87);
\node[font=\scriptsize,text=black!70] at (5.920,0.6699999999999999) {appears};
\node[font=\small\bfseries] at (5.920,0.32999999999999996) {magenta};
\definecolor{c605abs}{HTML}{FF2900}
\definecolor{c605per}{HTML}{00CCFB}
\draw[gray,dash pattern=on 2pt off 2pt] (8.200,4.3) -- (8.200,2.5);
\fill[black] (8.200,4.3) circle (2.2pt);
\node[font=\small] at (8.200,2.28) {$\Delta E\approx2.05$ eV};
\filldraw[fill=c605abs,draw=black!55] (7.020,0.95) rectangle (7.940,1.87);
\node[font=\scriptsize,text=black!70] at (7.480,0.6699999999999999) {absorbs};
\draw[-{Stealth[length=5pt]},thick] (8.020,1.410) -- (8.380,1.410);
\filldraw[fill=c605per,draw=black!55] (8.460,0.95) rectangle (9.380,1.87);
\node[font=\scriptsize,text=black!70] at (8.920,0.6699999999999999) {appears};
\node[font=\small\bfseries] at (8.920,0.32999999999999996) {blue};
```

*Figure 1.* The visible window, 1.8–3.1 eV, drawn as the spectrum itself: a
material is colored only if it has an electronic transition whose energy falls
inside this band. A gap larger than 3.1 eV absorbs only ultraviolet light and the
material is colorless; a gap smaller than 1.8 eV absorbs infrared and, if broad,
most of the visible range too, reading black. Inside the window, a gap fixes the
wavelength absorbed, and the eye sees the *complementary* color of what is left:
the three worked examples show a large gap absorbing blue-violet and appearing
yellow, a middling gap absorbing green and appearing magenta, and a smaller gap
absorbing orange and appearing blue. Every swatch here and below is computed from
the CIE 1931 color-matching functions — the perceived color is the eye's integral
over the reflected spectrum, not a hand-picked hue.

So the question of what produces color becomes a question of mechanism: what
physical structures place an electronic energy gap in the 1.8–3.1 eV window.
Four mechanisms matter for pigments,
and they are genuinely different physics, not variations on one idea. Each of
the next four sections covers one mechanism, gives a modern pigment that uses
it, and compares it with a historic pigment that uses the same mechanism but
lacks the engineered permanence.

## 3. Extended conjugated π-systems

This is the organic-chemistry mechanism, and it connects most directly to the
particle in a box. Take a chain or ring system of alternating single and double
bonds — a **conjugated** π-system. The π electrons are not confined to
individual bonds; they delocalize over the whole conjugated framework. That is,
to a first approximation, an electron in a box, where the box length $L$ is the
length of the conjugated path. The
[fundamentals post](/posts/fundamentals_of_quantum_chemistry.html) gave the
levels of that box,

$$
E_n = \frac{n^2 h^2}{8 m L^2},
$$

and the remaining step is to fill them. If the conjugated system holds $N$ π
electrons, they occupy the lowest $N/2$ levels (two per level, by Pauli), so the
highest occupied level is $n = N/2$ and the lowest empty one is $n = N/2 + 1$.
The photon that colors the molecule lifts an electron across that HOMO–LUMO gap:

$$
\Delta E = E_{N/2+1} - E_{N/2}
        = \frac{h^2}{8 m L^2}\,(N+1).
$$

Lengthening the conjugated chain does two things at once: it adds electrons
(raising $N$) and it lengthens the box (raising $L^2$ in the denominator), with
$L$ growing roughly in proportion to $N$. The net effect is
$\Delta E \propto (N+1)/N^2 \approx 1/N$: the gap shrinks as conjugation
extends (Figure 2) — a longer box has a smaller gap. A
short conjugated system absorbs in the ultraviolet and looks colorless;
extending it moves the absorption down through violet, blue, and green, into the
visible as yellow, then orange, then red: longer box, smaller gap, redder color.
This free-electron picture ignores bond alternation, the real shape of the
potential, and electron correlation — the corrections the [Hartree–Fock
post](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html) worked
through — but the trend it predicts is correct, and it is why essentially every
strong organic colorant is a large, flat, conjugated molecule.[@Christie2014;
@nassau2001physics]

```tikzpicture
\draw[-{Stealth[length=6pt]},black!70] (0.1,0.2) -- (0.1,6.5);
\node[font=\small,text=black!70] at (0.1,6.8) {$E$};
\node[font=\bfseries] at (1.25,8.35) {short chain};
\draw[black,line width=1.1pt] (0.650,7.760) -- (0.950,7.240);
\draw[black,line width=0.7pt] (0.650,7.700) -- (0.950,7.300);
\draw[black,line width=0.7pt] (0.950,7.240) -- (1.250,7.760);
\draw[black,line width=1.1pt] (1.250,7.760) -- (1.550,7.240);
\draw[black,line width=0.7pt] (1.250,7.700) -- (1.550,7.300);
\draw[black,line width=0.7pt] (1.550,7.240) -- (1.850,7.760);
\draw[black,line width=1.5pt] (0.35,0.6) -- (2.15,0.6);
\node[font=\small,text=black!80] at (1.25,0.62) {$\uparrow\!\downarrow$};
\draw[black,line width=1.5pt] (0.35,2.2) -- (2.15,2.2);
\node[font=\small,text=black!80] at (1.25,2.22) {$\uparrow\!\downarrow$};
\draw[black!45,line width=1pt,dash pattern=on 3pt off 3pt] (0.35,5.6) -- (2.15,5.6);
\draw[black!45,line width=1pt,dash pattern=on 3pt off 3pt] (0.35,6.3) -- (2.15,6.3);
\node[font=\small,text=black!75,anchor=west] at (2.25,2.2) {HOMO};
\node[font=\small,text=black!75,anchor=west] at (2.25,5.6) {LUMO};
\definecolor{arr0}{HTML}{6A0DAD}
\fill[arr0] (1.25,2.2) circle (2.3pt);
\draw[-{Stealth[length=7pt]},arr0,line width=2pt] (1.25,2.2) -- (1.25,5.6);
\node[font=\small,anchor=west,text=arr0] at (1.53,3.9) {$\Delta E$};
\definecolor{sw0}{HTML}{FBFAF6}
\filldraw[fill=sw0,draw=black!55] (0.75,-1.7) rectangle (1.75,-0.7);
\node[font=\small\bfseries] at (1.25,-2.05) {colorless};
\node[font=\scriptsize,text=black!65] at (1.25,-2.45) {absorbs in the UV};
\draw[-{Stealth[length=6pt]},black!70] (6.699999999999999,0.2) -- (6.699999999999999,6.5);
\node[font=\small,text=black!70] at (6.699999999999999,6.8) {$E$};
\node[font=\bfseries] at (7.85,8.35) {long chain};
\draw[black,line width=1.1pt] (6.050,7.760) -- (6.350,7.240);
\draw[black,line width=0.7pt] (6.050,7.700) -- (6.350,7.300);
\draw[black,line width=0.7pt] (6.350,7.240) -- (6.650,7.760);
\draw[black,line width=1.1pt] (6.650,7.760) -- (6.950,7.240);
\draw[black,line width=0.7pt] (6.650,7.700) -- (6.950,7.300);
\draw[black,line width=0.7pt] (6.950,7.240) -- (7.250,7.760);
\draw[black,line width=1.1pt] (7.250,7.760) -- (7.550,7.240);
\draw[black,line width=0.7pt] (7.250,7.700) -- (7.550,7.300);
\draw[black,line width=0.7pt] (7.550,7.240) -- (7.850,7.760);
\draw[black,line width=1.1pt] (7.850,7.760) -- (8.150,7.240);
\draw[black,line width=0.7pt] (7.850,7.700) -- (8.150,7.300);
\draw[black,line width=0.7pt] (8.150,7.240) -- (8.450,7.760);
\draw[black,line width=1.1pt] (8.450,7.760) -- (8.750,7.240);
\draw[black,line width=0.7pt] (8.450,7.700) -- (8.750,7.300);
\draw[black,line width=0.7pt] (8.750,7.240) -- (9.050,7.760);
\draw[black,line width=1.1pt] (9.050,7.760) -- (9.350,7.240);
\draw[black,line width=0.7pt] (9.050,7.700) -- (9.350,7.300);
\draw[black,line width=0.7pt] (9.350,7.240) -- (9.650,7.760);
\draw[black,line width=1.5pt] (6.949999999999999,0.5) -- (8.75,0.5);
\node[font=\small,text=black!80] at (7.85,0.52) {$\uparrow\!\downarrow$};
\draw[black,line width=1.5pt] (6.949999999999999,1.1) -- (8.75,1.1);
\node[font=\small,text=black!80] at (7.85,1.12) {$\uparrow\!\downarrow$};
\draw[black,line width=1.5pt] (6.949999999999999,1.9) -- (8.75,1.9);
\node[font=\small,text=black!80] at (7.85,1.92) {$\uparrow\!\downarrow$};
\draw[black,line width=1.5pt] (6.949999999999999,3.0) -- (8.75,3.0);
\node[font=\small,text=black!80] at (7.85,3.02) {$\uparrow\!\downarrow$};
\draw[black!45,line width=1pt,dash pattern=on 3pt off 3pt] (6.949999999999999,4.5) -- (8.75,4.5);
\draw[black!45,line width=1pt,dash pattern=on 3pt off 3pt] (6.949999999999999,5.4) -- (8.75,5.4);
\node[font=\small,text=black!75,anchor=west] at (8.85,3.0) {HOMO};
\node[font=\small,text=black!75,anchor=west] at (8.85,4.5) {LUMO};
\definecolor{arr7}{HTML}{005BFF}
\fill[arr7] (7.85,3.0) circle (2.3pt);
\draw[-{Stealth[length=7pt]},arr7,line width=2pt] (7.85,3.0) -- (7.85,4.5);
\node[font=\small,anchor=west,text=arr7] at (8.129999999999999,3.75) {$\Delta E$};
\definecolor{sw7}{HTML}{FFD070}
\filldraw[fill=sw7,draw=black!55] (7.35,-1.7) rectangle (8.35,-0.7);
\node[font=\small\bfseries] at (7.85,-2.05) {colored};
\node[font=\scriptsize,text=black!65] at (7.85,-2.45) {absorbs $\approx$475 nm};
```

*Figure 2.* Particle-in-a-box levels for a short versus a long conjugated chain,
scaled by $E_n \propto n^2/L^2$. Solid levels hold the occupied $\pi$ electrons
(two per level, up to the HOMO); dashed levels are empty, and the arrow is the
photon that lifts an electron across the HOMO–LUMO gap. A short chain is a small
box with a large gap: it absorbs in the ultraviolet and is colorless. Lengthening
the chain adds electrons and lengthens the box together, and the net effect
($\Delta E \propto 1/N$) shrinks the gap until the absorption slides into the
visible — the long chain here absorbs blue light near 475 nm and so appears
orange. This is only the free-electron part of the story; donor and acceptor
substituents tune the gap as well, independently of length, and are taken up in a
later post.

**Modern examples.** The high-performance organic pigments put that delocalized
gap in the visible and make the resulting crystal resistant to light.
**Quinacridone** (a linear five-ring system; the magentas and violets PV19,
PR122, PR202) and the **diketopyrrolopyrrole** (**DPP**) reds and oranges
(PR254 and its family) are compact conjugated chromophores whose molecules lock
together through dense networks of hydrogen bonds, stacking into tight,
insoluble, thermally and photochemically robust crystals. **Perylene** pigments
(PR149, PR179, and relatives) are large polycyclic π-systems with the same
structure. The **phthalocyanines** — copper phthalocyanine blue (PB15) and its
chlorinated green (PG7) — are macrocyclic: a large aromatic ring wrapped around
a metal ion, with a fully allowed π→π* absorption that gives a blue or green of
high tinting strength and near-total fastness. Quinacridones, DPPs, perylenes,
and phthalocyanines carry the top lightfastness ratings artists' pigments are
awarded — ASTM I, blue-wool 7–8 — because the chromophore is chemically the same
kind of object as the fugitive pigments below, engineered into a crystal that
resists the photochemistry that would otherwise degrade it.[@HerbstHunger2004;
@Christie2014] They are the premium tier, not the whole modern palette: the
**azo** pigments — the arylide yellows and naphthol reds that dominate
industrial color by volume, and their tougher **benzimidazolone** relatives,
met again in §6's cadmium-free hues — run on the same conjugated-π mechanism,
with lightfastness ranging from middling to excellent depending on how
tightly the crystal packs.

**Historic precedents.** **Indigo** and **alizarin** run on the same physics and
fail at the point the modern pigments above were engineered to fix. Indigo is an
*indigoid* chromophore — a short, cross-conjugated system whose color comes from
the same delocalized π electrons, tuned by donor and acceptor groups to absorb
in the orange-red and appear blue. **Alizarin**, the red of **madder**, is an
*anthraquinone*: a conjugated three-ring core with hydroxyl and carbonyl groups
arranged to bring the gap into the visible. Mechanistically the absorption is
the story told above. But laid down as lakes on alumina (§1), these molecules
are exposed and mobile; light drives oxidative and photochemical breakdown of
the same π-system that produces the color, and madder lake in particular is
notoriously fugitive in thin films and tints. The mechanism is identical; the
permanence is engineered. Synthetic alizarin and synthetic indigo reproduce the
historic colors, but it is the quinacridones and DPPs — unrelated in structure,
equivalent in physics — that displaced them, by keeping the color and adding the
fastness the old lakes never had.[@Zollinger2003; @HerbstHunger2004]

## 4. Ligand-field d–d transitions

The second mechanism is inorganic, and lives in the partly filled $d$ shell of a
transition-metal ion. A free transition-metal ion has five $d$ orbitals that are
degenerate — all the same energy. Surrounding it with ligands (oxide ions,
water, the framework of a host crystal) breaks that degeneracy: the $d$
orbitals pointing *toward* the negatively charged ligands are pushed up in
energy, those pointing *between* them are lowered, and the set splits into
groups separated by the **crystal-field** (or ligand-field) splitting $\Delta$.
For ions such as Co²⁺, Cr³⁺, and Mn³⁺, $\Delta$ for common oxygen environments
falls in the visible window, so promoting an electron from a lower $d$ orbital
to an upper one — a **$d$–$d$ transition** — absorbs a visible photon and
produces color.

A selection rule governs how these pigments behave in practice, and it reads
directly off the symmetry of the metal site. In a site with a center of
inversion — the oxide octahedron around Cr³⁺ in chromium oxide green and
viridian — a $d$–$d$ transition is, strictly, **forbidden**: both the starting
and ending orbitals are $d$ orbitals, so the transition does not change the
parity (the inversion symmetry) of the electronic state, and the **Laporte
rule** forbids electric-dipole transitions that fail to flip parity. The
transition happens at all only because vibrations momentarily break the
perfect symmetry and "borrow" a little allowed character, so the absorption is
**weak** — low molar absorptivity, hence **low tinting strength**: viridian is
relatively transparent, easily overpowered when mixed. Remove the inversion
center and the rule loosens its grip. Cobalt blue's Co²⁺ sits in a
*tetrahedral* site, which has no inversion center; mixing of $d$ and $p$
character makes its absorption markedly stronger than octahedral chromium's,
though still far short of fully allowed. Site symmetry is a dial running from
forbidden toward allowed — octahedral chromium near one end, tetrahedral
cobalt partway up — and §5 and §6 show transitions the rule does not restrict
at all, sitting at the other end.

**Examples.** **Cobalt blue** is Co²⁺ sitting in the tetrahedral holes of an
aluminate spinel, CoAl₂O₄; the tetrahedral ligand field tunes the $d$–$d$ gap to
a clean blue. **Chromium oxide green** (Cr₂O₃) and its hydrated, more brilliant
relative **viridian** are Cr³⁺ in an oxide octahedron — the same ion that, in a
different host, makes a ruby red. These are excellent, permanent pigments: the
$d$–$d$ chromophore is buried inside a robust oxide lattice and is essentially
immune to light.

Ligand-field color is dominated by inorganic pigments, historic and modern
alike; there is no organic-for-inorganic swap to describe here, because the
mechanism is intrinsically tied to a metal ion. The modern development is in
the *host lattice*: mixed-metal-oxide and spinel pigments engineered to place a
chosen ion in a chosen coordination, dialing in hue, opacity, and durability.
**YInMn blue**, discovered in 2009, is the clearest recent example: Mn³⁺
trapped in an unusual *trigonal-bipyramidal* oxygen coordination inside a
YInO₃-type lattice, which splits its $d$ levels to absorb red and green
strongly and reflect a vivid, durable blue (Figure 3). The trigonal-bipyramidal
site has no center of inversion, so the Laporte rule that makes octahedral
chromium's $d$–$d$ transitions weak is relaxed: the transition becomes
symmetry-allowed, which is why YInMn is an intense, strong-tinting blue rather
than a pale one. It is the symmetry dial that mutes viridian, turned to its
allowed end — the first new inorganic blue chromophore in two centuries,
produced by engineering the ligand field around an existing ion rather than
inventing a new molecule.[@SmithSubramanian2009;
@nassau2001physics]

```tikzpicture
\node[font=\bfseries] at (2.3,9.4) {octahedral};
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (2.30,8.70);
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (2.30,7.70);
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (2.80,8.42);
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (1.80,8.42);
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (2.80,7.98);
\draw[black!45,line width=0.8pt] (2.30,8.20) -- (1.80,7.98);
\filldraw[fill=black!8,draw=black!45] (2.30,8.70) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (2.30,7.70) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (2.80,8.42) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (1.80,8.42) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (2.80,7.98) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (1.80,7.98) circle (5.5pt);
\definecolor{ion2}{HTML}{40826D}
\filldraw[fill=ion2,draw=black] (2.30,8.20) circle (8pt);
\node[font=\scriptsize,text=white] at (2.30,8.20) {Cr};
\draw[black,line width=1.4pt] (1.2499999999999998,4.3) -- (3.3499999999999996,4.3);
\draw[black,line width=1.4pt] (1.2499999999999998,6.2) -- (3.3499999999999996,6.2);
\node[font=\scriptsize,text=black!70,anchor=east] at (1.1699999999999997,4.3) {$t_{2g}$};
\node[font=\scriptsize,text=black!70,anchor=east] at (1.1699999999999997,6.2) {$e_g$};
\draw[{Stealth[length=4pt]}-{Stealth[length=4pt]},black!70] (3.6999999999999997,4.3) -- (3.6999999999999997,6.2);
\node[font=\small,anchor=west,text=black!70] at (3.78,5.25) {$\Delta$};
\draw[-{Stealth[length=4pt]},black!45,line width=0.9pt,dash pattern=on 2pt off 2pt] (1.9499999999999997,4.38) -- (1.9499999999999997,6.12);
\node[font=\scriptsize,text=black!60] at (2.3,3.37) {strength};
\draw[black!35,fill=black!5] (1.2499999999999998,2.95) rectangle (3.3499999999999996,3.21);
\definecolor{mt2}{HTML}{40826D}
\fill[mt2] (1.2499999999999998,2.95) rectangle (1.628,3.21);
\node[font=\tiny,text=black!45,anchor=east] at (1.1899999999999997,3.08) {weak};
\node[font=\tiny,text=black!45,anchor=west] at (3.4099999999999997,3.08) {strong};
\definecolor{pg2}{HTML}{40826D}
\filldraw[fill=pg2,draw=black!55] (1.7249999999999999,1.65) rectangle (2.875,2.8);
\node[font=\small\bfseries] at (2.3,1.29) {Laporte-forbidden};
\node[font=\bfseries] at (7.0,9.4) {tetrahedral};
\draw[black!45,line width=0.8pt] (7.00,8.20) -- (7.00,8.72);
\draw[black!45,line width=0.8pt] (7.00,8.20) -- (6.55,7.90);
\draw[black!45,line width=0.8pt] (7.00,8.20) -- (7.45,7.90);
\draw[black!45,line width=0.8pt] (7.00,8.20) -- (7.00,8.15);
\filldraw[fill=black!8,draw=black!45] (7.00,8.72) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (6.55,7.90) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (7.45,7.90) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (7.00,8.15) circle (5.5pt);
\definecolor{ion7}{HTML}{0047AB}
\filldraw[fill=ion7,draw=black] (7.00,8.20) circle (8pt);
\node[font=\scriptsize,text=white] at (7.00,8.20) {Co};
\draw[black,line width=1.4pt] (5.95,4.4) -- (8.05,4.4);
\draw[black,line width=1.4pt] (5.95,6.0) -- (8.05,6.0);
\node[font=\scriptsize,text=black!70,anchor=east] at (5.87,4.4) {$e$};
\node[font=\scriptsize,text=black!70,anchor=east] at (5.87,6.0) {$t_2$};
\draw[{Stealth[length=4pt]}-{Stealth[length=4pt]},black!70] (8.4,4.4) -- (8.4,6.0);
\node[font=\small,anchor=west,text=black!70] at (8.48,5.2) {$\Delta$};
\draw[-{Stealth[length=5pt]},black!70,line width=1.6pt] (6.65,4.48) -- (6.65,5.92);
\node[font=\scriptsize,text=black!60] at (7.0,3.37) {strength};
\draw[black!35,fill=black!5] (5.95,2.95) rectangle (8.05,3.21);
\definecolor{mt7}{HTML}{0047AB}
\fill[mt7] (5.95,2.95) rectangle (7.105,3.21);
\node[font=\tiny,text=black!45,anchor=east] at (5.890000000000001,3.08) {weak};
\node[font=\tiny,text=black!45,anchor=west] at (8.110000000000001,3.08) {strong};
\definecolor{pg7}{HTML}{0047AB}
\filldraw[fill=pg7,draw=black!55] (6.425,1.65) rectangle (7.574999999999999,2.8);
\node[font=\small\bfseries] at (7.0,1.29) {partly allowed};
\node[font=\bfseries] at (11.7,9.4) {trig.\ bipyramidal};
\draw[black!45,line width=0.8pt] (11.70,8.20) -- (11.70,8.75);
\draw[black!45,line width=0.8pt] (11.70,8.20) -- (11.70,7.65);
\draw[black!45,line width=0.8pt] (11.70,8.20) -- (11.20,8.36);
\draw[black!45,line width=0.8pt] (11.70,8.20) -- (12.20,8.36);
\draw[black!45,line width=0.8pt] (11.70,8.20) -- (11.70,8.25);
\filldraw[fill=black!8,draw=black!45] (11.70,8.75) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (11.70,7.65) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (11.20,8.36) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (12.20,8.36) circle (5.5pt);
\filldraw[fill=black!8,draw=black!45] (11.70,8.25) circle (5.5pt);
\definecolor{ion12}{HTML}{2C4CB0}
\filldraw[fill=ion12,draw=black] (11.70,8.20) circle (8pt);
\node[font=\scriptsize,text=white] at (11.70,8.20) {Mn};
\draw[black,line width=1.4pt] (10.649999999999999,4.3) -- (12.75,4.3);
\draw[black,line width=1.4pt] (10.649999999999999,6.3) -- (12.75,6.3);
\node[font=\scriptsize,text=black!70,anchor=east] at (10.569999999999999,4.3) {lower $d$};
\node[font=\scriptsize,text=black!70,anchor=east] at (10.569999999999999,6.3) {upper $d$};
\draw[{Stealth[length=4pt]}-{Stealth[length=4pt]},black!70] (13.1,4.3) -- (13.1,6.3);
\node[font=\small,anchor=west,text=black!70] at (13.18,5.3) {$\Delta$};
\draw[-{Stealth[length=7pt]},black,line width=2.6pt] (11.35,4.38) -- (11.35,6.22);
\node[font=\scriptsize,text=black!60] at (11.7,3.37) {strength};
\draw[black!35,fill=black!5] (10.649999999999999,2.95) rectangle (12.749999999999998,3.21);
\definecolor{mt12}{HTML}{2C4CB0}
\fill[mt12] (10.649999999999999,2.95) rectangle (12.645,3.21);
\node[font=\tiny,text=black!45,anchor=east] at (10.589999999999998,3.08) {weak};
\node[font=\tiny,text=black!45,anchor=west] at (12.809999999999999,3.08) {strong};
\definecolor{pg12}{HTML}{2C4CB0}
\filldraw[fill=pg12,draw=black!55] (11.125,1.65) rectangle (12.275,2.8);
\node[font=\small\bfseries] at (11.7,1.29) {Laporte-allowed};
```

*Figure 3.* Site symmetry as a dial from forbidden to allowed. Each column is a
ligand field that splits the free ion's five degenerate $d$ orbitals into sets
separated by $\Delta$; the $d$–$d$ transition across $\Delta$ (the arrow) absorbs
a visible photon. The size of $\Delta$ sets the *hue* — chromium oxide's gives
viridian green, YInMn's gives blue. The *strength* of the transition is a
separate axis, set by symmetry, not by the gap: the octahedral site has an
inversion center, so its transition is Laporte-forbidden and stays weak (faint
arrow, low tinting, easily overpowered); the tetrahedral site of cobalt blue has
no inversion center and is partly allowed; the trigonal-bipyramidal site of YInMn
is fully Laporte-allowed and intense (bold arrow, high tinting). A forbidden
transition stays weak and an allowed one stays strong *whatever* the gap — hue
and strength are independent. What "symmetry," "forbidden," and "allowed" mean is
the subject of a later post.

## 5. Charge-transfer transitions

The third mechanism also involves metals, but instead of an electron hopping
between two $d$ orbitals *on the same ion*, the electron jumps *from one site to
another* — from a ligand to a metal, or between two metal ions in different
oxidation states. These **charge-transfer** (CT) transitions are **fully
allowed**: the electron genuinely moves through space, the transition dipole is
large, and the absorption is intense. That is the key difference from §4. A CT
pigment has high molar absorptivity and therefore **high tinting strength and
deep color from a small amount of material** — the reverse of the weak,
forbidden $d$–$d$ pigments of §4.

The clearest examples of charge transfer are historic pigments — Prussian blue
and ultramarine — and both are covered directly below. The modern development
for this mechanism is not a new chromophore but reliable synthetic manufacture
of the same ones, described after the examples.

**Prussian blue** is the classic **intervalence charge transfer** (IVCT). Its
structure is a cyanide-bridged framework holding iron in two oxidation states,
Fe²⁺ and Fe³⁺. A visible photon drives an electron from an Fe²⁺ site, across the
bridging cyanide, onto a neighboring Fe³⁺ — momentarily swapping which iron is
which. That intervalence jump absorbs strongly across the red and gives Prussian
blue its deep, transparent blue with an absorption maximum near 700 nm; in the
Robin–Day scheme it is a Class II mixed-valence solid, valences localized but
coupled enough for the transfer to cost a visible photon's worth of
energy.[@ItayaUchida1986]

**Ultramarine** is the other major example, and its chromophore is often
misidentified: it is **not** the aluminosilicate **sodalite cage** that hosts
it. The cage is colorless. The color comes from **polysulfide radical anions
trapped inside it** — chiefly the **S₃⁻** radical anion, with some **S₂⁻**
contributing — whose electronic transitions absorb in the orange and yield
ultramarine's blue. Strictly, that absorption is an internal transition of the
radical anion rather than a jump between two separate sites, so ultramarine
sits loosely in this section's taxonomy; it is filed here because it behaves
like charge transfer — fully allowed and intense, nothing like a ligand-field
band. The cage isolates and stabilizes these otherwise-reactive radicals;
destroy the cage and the color is lost, but the cage is the host, not the
chromophore.[@FleetLiu2010] The **iron-oxide earths** — yellow **ochre**
(goethite, hydrated FeO(OH)), the **red oxides** (hematite, Fe₂O₃), and the
brown **siennas** and **umbers** (iron oxides with manganese; calcining
"burns" raw sienna's yellow-brown to a red-brown) — round out this mechanism,
their warm colors coming from a combination of O→Fe **ligand-to-metal charge
transfer** and weaker $d$–$d$ absorption on the iron; they are among the most
permanent pigments humans have ever used.

The modern development for this mechanism is reliable manufacture, not a new
chromophore. **Synthetic ultramarine** (made since the 1820s by firing china
clay, sulfur, and soda) reproduces the chromophore of ground lapis lazuli at a
fraction of the cost, with controlled, reproducible color. **Synthetic iron
oxides** (the "Mars" colors) give cleaner, stronger, more consistent earths than
dug ones. The CT chromophore itself is unchanged; what modernized is the supply.

## 6. Semiconductor band-gap absorption

The fourth mechanism looks similar to the others but behaves differently,
because it produces an absorption edge rather than an absorption band. In a
semiconductor, the electronic states are not discrete molecular levels but
continuous **bands** — a filled **valence band** and an empty **conduction
band**, separated by a forbidden **band gap** $E_g$ (Figure 4). A photon with
energy above $E_g$ promotes an electron across the gap and is absorbed; a
photon below $E_g$ has nowhere to put the electron and passes through. A
semiconductor absorbs everything with energy greater than $E_g$, all the way up
— so a band-gap pigment does not have an absorption *band* that rises and
falls, it has a sharp absorption **edge**: a cutoff wavelength below which it
absorbs strongly and above which it is transparent.

Moving the band gap across the visible window changes the color directly. If
$E_g$ is just above the violet end (~3 eV), the material absorbs only the faint
violet and looks pale or white. Lowering $E_g$ to ~2.6 eV means it starts eating
blue, so it reflects everything from green up and looks **yellow**. At ~2.3 eV
it eats blue and green and reflects orange-and-red — **orange**. At ~2.0 eV
only red survives — **red**. The color of a band-gap pigment is set by where
the edge sits, and a single chemical family with a tunable $E_g$ gives the
whole sequence yellow→orange→red (Figure 4). The edge is also why the same gap
energy can name two different colors in this post: the molecular chromophore
marked at $\Delta E \approx 2.1$ eV in Figure 1 absorbs a *band* around 590 nm
and looks blue, while a semiconductor with $E_g \approx 2.0$ eV absorbs
*everything* above the gap and looks red.

```tikzpicture
\definecolor{vbfill}{HTML}{3A5A8F}
\filldraw[fill=vbfill,draw=black!55] (0.6,1.4) rectangle (3.4,2.7);
\node[font=\small,text=white] at (2.0,2.05) {valence band};
\filldraw[fill=black!5,draw=black!55] (0.6,5.0) rectangle (3.4,6.3);
\node[font=\small,text=black!70] at (2.0,5.65) {conduction band};
\draw[{Stealth[length=5pt]}-{Stealth[length=5pt]},black!75] (3.75,2.7) -- (3.75,5.0);
\node[font=\small,anchor=west,text=black!80] at (3.85,3.85) {$E_g$};
\definecolor{absph}{HTML}{6100FF}
\draw[-{Stealth[length=6pt]},absph,line width=2pt] (1.2999999999999998,2.7) -- (1.2999999999999998,5.0);
\node[font=\scriptsize,text=black!70,anchor=west] at (1.5499999999999998,4.15) {$h\nu>E_g$};
\node[font=\scriptsize,text=black!55,anchor=west] at (1.5499999999999998,3.5500000000000003) {absorbed};
\definecolor{trph}{HTML}{FF0000}
\draw[-{Stealth[length=6pt]},trph,line width=2pt,dash pattern=on 3pt off 2pt] (0.09999999999999998,0.7) -- (3.9,0.7);
\node[font=\scriptsize,text=black!70] at (2.0,0.35) {$h\nu<E_g$ passes through};
\definecolor{cd0}{HTML}{FFE800}
\definecolor{cd1}{HTML}{FFDD00}
\definecolor{cd2}{HTML}{FFCF00}
\definecolor{cd3}{HTML}{FFBE00}
\definecolor{cd4}{HTML}{FFAC00}
\definecolor{cd5}{HTML}{FF9600}
\definecolor{cd6}{HTML}{FF7F00}
\definecolor{cd7}{HTML}{FF6600}
\definecolor{cd8}{HTML}{FF4A00}
\definecolor{cd9}{HTML}{FF2A00}
\definecolor{cd10}{HTML}{F70000}
\definecolor{cd11}{HTML}{E20000}
\definecolor{cd12}{HTML}{CB0000}
\definecolor{cd13}{HTML}{B30000}
\definecolor{cd14}{HTML}{9A0000}
\definecolor{cd15}{HTML}{820000}
\definecolor{cd16}{HTML}{6C0000}
\definecolor{cd17}{HTML}{570000}
\definecolor{cd18}{HTML}{450000}
\definecolor{cd19}{HTML}{360000}
\definecolor{cd20}{HTML}{290000}
\definecolor{cd21}{HTML}{1E0000}
\definecolor{cd22}{HTML}{150000}
\definecolor{cd23}{HTML}{0E0100}
\definecolor{cd24}{HTML}{080000}
\shade[left color=cd0,right color=cd1] (5.600,3.9) rectangle (5.933,5.4);
\shade[left color=cd1,right color=cd2] (5.933,3.9) rectangle (6.267,5.4);
\shade[left color=cd2,right color=cd3] (6.267,3.9) rectangle (6.600,5.4);
\shade[left color=cd3,right color=cd4] (6.600,3.9) rectangle (6.933,5.4);
\shade[left color=cd4,right color=cd5] (6.933,3.9) rectangle (7.267,5.4);
\shade[left color=cd5,right color=cd6] (7.267,3.9) rectangle (7.600,5.4);
\shade[left color=cd6,right color=cd7] (7.600,3.9) rectangle (7.933,5.4);
\shade[left color=cd7,right color=cd8] (7.933,3.9) rectangle (8.267,5.4);
\shade[left color=cd8,right color=cd9] (8.267,3.9) rectangle (8.600,5.4);
\shade[left color=cd9,right color=cd10] (8.600,3.9) rectangle (8.933,5.4);
\shade[left color=cd10,right color=cd11] (8.933,3.9) rectangle (9.267,5.4);
\shade[left color=cd11,right color=cd12] (9.267,3.9) rectangle (9.600,5.4);
\shade[left color=cd12,right color=cd13] (9.600,3.9) rectangle (9.933,5.4);
\shade[left color=cd13,right color=cd14] (9.933,3.9) rectangle (10.267,5.4);
\shade[left color=cd14,right color=cd15] (10.267,3.9) rectangle (10.600,5.4);
\shade[left color=cd15,right color=cd16] (10.600,3.9) rectangle (10.933,5.4);
\shade[left color=cd16,right color=cd17] (10.933,3.9) rectangle (11.267,5.4);
\shade[left color=cd17,right color=cd18] (11.267,3.9) rectangle (11.600,5.4);
\shade[left color=cd18,right color=cd19] (11.600,3.9) rectangle (11.933,5.4);
\shade[left color=cd19,right color=cd20] (11.933,3.9) rectangle (12.267,5.4);
\shade[left color=cd20,right color=cd21] (12.267,3.9) rectangle (12.600,5.4);
\shade[left color=cd21,right color=cd22] (12.600,3.9) rectangle (12.933,5.4);
\shade[left color=cd22,right color=cd23] (12.933,3.9) rectangle (13.267,5.4);
\shade[left color=cd23,right color=cd24] (13.267,3.9) rectangle (13.600,5.4);
\draw[black!55,line width=0.8pt] (5.6,3.9) rectangle (13.6,5.4);
\node[font=\bfseries] at (9.6,5.95) {\ce{CdS_{1-x}Se_x}: reflected color};
\node[font=\footnotesize,text=black!60] at (9.6,5.6000000000000005) {more Se $\rightarrow$ smaller $E_g$ $\rightarrow$ edge sweeps red $\rightarrow$};
\draw[black!55] (5.600,3.9) -- (5.600,3.7399999999999998);
\node[font=\scriptsize,align=center] at (5.600,3.4) {$x{=}0.00$\\[-1pt]\footnotesize $E_g{=}2.42$};
\draw[black!55] (7.600,3.9) -- (7.600,3.7399999999999998);
\node[font=\scriptsize,align=center] at (7.600,3.4) {$x{=}0.25$\\[-1pt]\footnotesize $E_g{=}2.19$};
\draw[black!55] (9.600,3.9) -- (9.600,3.7399999999999998);
\node[font=\scriptsize,align=center] at (9.600,3.4) {$x{=}0.50$\\[-1pt]\footnotesize $E_g{=}2.00$};
\draw[black!55] (11.600,3.9) -- (11.600,3.7399999999999998);
\node[font=\scriptsize,align=center] at (11.600,3.4) {$x{=}0.75$\\[-1pt]\footnotesize $E_g{=}1.85$};
\draw[black!55] (13.600,3.9) -- (13.600,3.7399999999999998);
\node[font=\scriptsize,align=center] at (13.600,3.4) {$x{=}1.00$\\[-1pt]\footnotesize $E_g{=}1.74$};
\node[font=\scriptsize,text=black!55] at (5.600,4.4) {};
\node[font=\footnotesize,text=black!60,anchor=south] at (5.600,5.42) {};
\node[font=\scriptsize,text=black!70] at (6.080,4.25) {CdS};
\node[font=\scriptsize,text=white] at (13.040,4.25) {CdSe};
```

*Figure 4.* Left: band-gap absorption produces an *edge*, not a band. Every
photon with energy above $E_g$ has a state to be promoted into and is absorbed;
every photon below $E_g$ passes through. A semiconductor therefore absorbs
*everything* bluer than its cutoff and reflects the rest. Right: the reflected
color that results, computed across the CdS₁₋ₓSeₓ solid solution. Substituting
larger selenium for sulfur narrows $E_g$ continuously (2.42 eV down to 1.74 eV),
sweeping the edge toward the red and dragging the reflected color with it — a
large gap absorbs only blue-violet and leaves yellow; shrinking the gap eats into
green and then orange, carrying the color through orange to red. Pushed to pure
CdSe the edge clears most of the visible and the solid darkens toward black,
which is why the useful cadmium reds sit at intermediate $x$.

**Historic examples.** The **cadmium** pigments are the clearest illustration:
cadmium sulfide (CdS) has a band gap that makes it a bright yellow, and forming
the solid solution **CdS₁₋ₓSeₓ** — substituting larger selenium for sulfur —
narrows the gap continuously, sweeping the edge from yellow through orange to
deep red as $x$ increases (Figure 4). **Vermilion** (mercury(II) sulfide, HgS)
is a band-gap red; **chrome yellow** (lead chromate, PbCrO₄) a band-gap yellow
— in chromate's case an edge built from O→Cr(VI) charge transfer, since Cr⁶⁺
has no $d$ electrons left for a $d$–$d$ band: §5's mechanism in its
solid-state limit. All three are toxic — cadmium, mercury, lead — which is why
this mechanism needed a modern replacement. Toxicity is not their only flaw:
vermilion notoriously blackens in light, converting toward its dark polymorph
metacinnabar, and chrome yellow darkens as light reduces Cr(VI) to Cr(III) —
the slow browning of Van Gogh's sunflowers. Photochemical failure is not an
organic monopoly (§8).

**Modern replacements.** Here the modern work is reformulating away the
toxicity while keeping the band-gap color. **Bismuth vanadate** (BiVO₄, Pigment
Yellow 184) is a non-toxic, lightfast, high-opacity yellow whose band gap of
about 2.4 eV — an O→V(V) charge-transfer edge, like chromate's — puts its
absorption edge near 520 nm, reflecting a clean, strong yellow that
substitutes directly for cadmium and chrome yellows.[@Cooper2015]
The cadmium-free "**hues**" sold today combine this engineering: bismuth
vanadate, benzimidazolone and DPP organics (§3), and inorganic mixed oxides
blended to match the cadmium colors' hue and opacity without the cadmium.

| Mechanism | Physical origin | Selection rule / strength | Historic example | Modern example |
|:----------|:-----------------|:---------------------------|:-------------------|:------------------|
| Conjugated π-system (§3) | HOMO–LUMO gap of delocalized π electrons | Allowed; strength grows with conjugation length | Indigo, alizarin (madder) | Quinacridone, DPP, phthalocyanine |
| Ligand-field $d$–$d$ (§4) | Crystal-field splitting of a transition-metal ion's $d$ orbitals | Laporte-forbidden in centrosymmetric sites; weak, relaxed as site symmetry drops | Cobalt blue, viridian | YInMn blue (Laporte-allowed site) |
| Charge transfer (§5) | Electron transfer between two sites (ligand→metal or metal→metal) | Fully allowed; strong, high tinting strength | Prussian blue, ultramarine, iron oxides | Same chromophores, synthetic manufacture |
| Semiconductor band gap (§6) | Valence-to-conduction-band promotion above $E_g$ | Absorption edge, not a band; strength set by edge position | Cadmium yellows/reds, vermilion, chrome yellow | Bismuth vanadate, cadmium-free hues |

*Table 1.* The four mechanisms that place an electronic energy gap in the
1.8–3.1 eV visible window, compared by physical origin, transition strength,
and representative pigments.

With all four color-producing mechanisms in hand, the next question is how a
pigment's absorbed and unabsorbed light actually reaches the eye.

## 7. Absorption and scattering, together

Everything so far has been about **absorption** — which photons a pigment's
electrons can absorb. But a pigment in a binder does not merely absorb; it also
**scatters**, and the color actually seen is the combination of the two.
Absorption alone cannot explain why the same pigment is opaque in one medium and
transparent in another, why oil deepens color, or why titanium white is white
at all. Absorption and scattering are *independent* physical processes, and
appearance is their product.

**Subtractive perception, stated carefully.** When white light strikes a paint
film, the pigment absorbs some wavelengths and the rest are reflected back out.
The perceived color is the eye's integrated response to that **reflected**
spectrum — the light that was *not* absorbed, weighted across all wavelengths
by the sensitivities of the three cone types. The shorthand "absorbs red, looks
green" is frequently wrong: a pigment that absorbs a band in the green-yellow
looks magenta, and one that absorbs a broad swath looks a muddied mixture. The
perceived hue is the spectrally integrated complement of the absorption, not a
one-word opposite.

**Scattering as a separate contribution.** A pigment particle has a refractive
index; so does the binder around it. Whenever light crosses an interface between
two different refractive indices it bends and partly reflects, and a paint film
is packed with such interfaces — every particle surface. This is
**scattering**: **Mie** scattering when the particles are comparable in size to
the wavelength of light (the usual case for pigments, particle diameters of a
few tenths of a micron), shading toward **Rayleigh** scattering for particles
much smaller than the wavelength. The strength of the scattering is governed by
the **refractive-index contrast** between pigment and binder, $\Delta n =
n_\text{pigment} - n_\text{binder}$: a large contrast scatters light strongly
and makes the film **opaque** (high hiding power, because light is turned back
before it penetrates deep); a small contrast scatters weakly and makes the film
**transparent** (light passes through, and you see whatever is beneath).
Particle size matters too — there is an optimum particle diameter, around half
the wavelength of light, that maximizes scattering, which is why pigment
manufacturers grind to a target size, not merely "fine."

Two consequences follow. First, **why oil saturates color.** Linseed oil has a
refractive index of about 1.48, much higher than air's 1.00. Many pigments have
refractive indices around 1.5–2.0, so dispersing them in oil *lowers* the index
contrast $\Delta n$ relative to the same powder in air — the particles match the
oil more closely than they match air. Less contrast means less scattering at the
surface, so more light penetrates into the film, gets *absorbed* by the
chromophore on the way in and out, and emerges deeper and more saturated. This
is why a dry pigment powder looks pale and chalky but the instant it is wetted
with oil it darkens — the absorption was always there; what changed is that
suppressing the surface scattering let the light reach it. Second, **why
titanium white is such an intensely opaque white.** Rutile TiO₂ has a
refractive index near 2.7, enormous against any binder, giving the largest
$\Delta n$ of any common white pigment. It barely absorbs anything in the
visible (its band gap is in the UV), so it scatters *all* wavelengths almost
equally and intensely — the definition of a brilliant, high-hiding white.
Titanium white is pure scattering with almost no absorption; a saturated
phthalo blue is strong absorption with comparatively modest scattering; most
pigments are somewhere between.

**The quantitative bridge: Kubelka–Munk.** To turn "absorption and scattering
combine" into a number, the standard tool is **Kubelka–Munk** theory, a
two-flux model that treats a paint film as two diffuse light streams — one
toward the viewer, one into the film — coupled by an absorption coefficient $K$
and a scattering coefficient $S$ (Figure 5). Solving the two coupled equations
for an optically thick film (thick enough that the background does not show
through) gives the film's diffuse reflectance $R_\infty$, and the result
inverts into the relation colorist software is built
on:[@KubelkaMunk1931; @Berns2019]

```tikzpicture
\definecolor{film}{HTML}{DCE6F5}
\filldraw[fill=film,draw=black!55,line width=0.8pt] (1.4,1.7) rectangle (6.8,5.1);
\draw[black!70,line width=1.2pt] (1.4,5.1) -- (6.8,5.1);
\filldraw[fill=black!30,draw=black!55] (1.4,1.42) rectangle (6.8,1.7);
\node[font=\scriptsize,text=black!60] at (4.1,1.2) {substrate (hidden: thick film)};
\draw[-{Stealth[length=6pt]},black,line width=1.4pt] (0.4999999999999999,6.3) -- (2.0,5.1499999999999995);
\node[font=\scriptsize,text=black!70,anchor=east] at (0.7,6.3) {incident};
\definecolor{rinf}{HTML}{B8B8B8}
\draw[-{Stealth[length=6pt]},rinf,line width=2.2pt] (2.4,5.1499999999999995) -- (3.9,6.3);
\node[font=\small,text=black!70,anchor=west] at (3.9499999999999997,6.25) {$R_\infty$};
\definecolor{fluxI}{HTML}{2E7D5B}
\definecolor{fluxJ}{HTML}{C77A20}
\draw[-{Stealth[length=6pt]},fluxI,line width=2.4pt] (2.3,2.0) -- (2.3,4.8);
\draw[-{Stealth[length=6pt]},fluxI,line width=2.4pt] (3.0999999999999996,2.0) -- (3.0999999999999996,4.8);
\draw[-{Stealth[length=6pt]},fluxJ,line width=2.4pt] (5.1,4.8) -- (5.1,2.0);
\draw[-{Stealth[length=6pt]},fluxJ,line width=2.4pt] (5.8999999999999995,4.8) -- (5.8999999999999995,2.0);
\node[font=\small,text=fluxI,anchor=east] at (2.15,3.4) {$I\uparrow$};
\node[font=\scriptsize,text=fluxI,anchor=east] at (2.15,3.05) {viewer};
\node[font=\small,text=fluxJ,anchor=west] at (6.05,3.4) {$J\downarrow$};
\node[font=\scriptsize,text=fluxJ,anchor=west] at (6.05,3.05) {into film};
\node[font=\Large] at (10.6,4.4) {$\dfrac{K}{S}=\dfrac{(1-R_\infty)^2}{2R_\infty}$};
\node[font=\scriptsize,text=black!60] at (10.6,3.35) {thick-film diffuse reflectance};
\definecolor{s9}{HTML}{3B3B3B}
\filldraw[fill=s9,draw=black!55] (8.549999999999999,1.3) rectangle (9.65,2.4);
\node[font=\scriptsize,text=black!70,align=center] at (9.1,0.95) {more $K$\\darker};
\definecolor{s12}{HTML}{E8E8E8}
\filldraw[fill=s12,draw=black!55] (11.549999999999999,1.3) rectangle (12.65,2.4);
\node[font=\scriptsize,text=black!70,align=center] at (12.1,0.95) {more $S$\\lighter, opaque};
```

*Figure 5.* Kubelka–Munk's two-flux model: an upward diffuse flux $I$ carries
light back to the viewer and a downward diffuse flux $J$ carries light into the
film, coupled by an absorption coefficient $K$ and a scattering coefficient $S$
per unit thickness. Solving the pair for an optically thick film gives the
diffuse reflectance $R_\infty$ through the relation at right; raising $K$ drives
$R_\infty$ down and the film darkens, while raising $S$ drives it up and the film
lightens and hides more, as the two swatches indicate.

$$
\frac{K}{S} = \frac{(1 - R_\infty)^2}{2\,R_\infty}.
$$

$K$ and $S$ are, to good approximation, additive over the pigments in a
mixture, weighted by concentration. Measuring $R_\infty$ of a masstone and a
tint gives $K/S$, from which the reflectance — and thus the color — of an
arbitrary blend can be predicted; this is what recipe-prediction and computer
color-matching do.

Kubelka–Munk's usefulness comes from several idealizing assumptions, which also
set its limits. It assumes **perfectly diffuse illumination** inside the film;
**isotropic scattering**, collapsing Mie theory's angular detail into a single
scalar $S$; **no separate term for specular surface reflection** off the top of
the film (gloss), which must be subtracted or measured around; and a
**homogeneous, optically thick** layer. It fails for **metallic and pearlescent
paints**, whose effect depends on the directional, anisotropic reflection K–M
discards. It fails for **very strongly absorbing** films, where $K/S$ runs
large, $R$ runs small, and the two-flux approximation loses accuracy. And it
fails for **thin or translucent layers** — glazes, watercolor washes — where the
optically-thick assumption does not hold, requiring the finite-thickness form
of the theory with the substrate included.

## 8. The limits

Three simplifications made earlier in this post are worth stating explicitly.

First, **subtractive complementarity is not exact.** "The color seen is the
complement of the color absorbed" is a useful approximation, but the perceived
hue is the eye's three-cone integral over the entire reflected spectrum (§7),
and absorption bands have width, structure, and overlap. Two pigments with
different spectra can match under one light source and diverge under another —
**metamerism** — which is exactly where the approximation breaks down.

Second, **Kubelka–Munk's idealizations** (§7) mean its predicted reflectances
are engineering-grade, not exact, and degrade precisely where its assumptions
do: gloss, deep shadows, thin glazes, metallics.

Third, **lightfastness.** A chromophore that absorbs visible photons is, by
construction, a molecule that routinely sits in electronically excited states
under illumination, and an excited state is a chemically reactive one. The same
delocalized π electrons that give an organic pigment its color can, once
excited, drive bond cleavage, oxidation, or rearrangement that destroys the
chromophore — the color **fades**. This is the physical price of the §3
mechanism, and it is why the historic lakes were fugitive: madder, carmine, and
the early synthetic dyes laid down as lakes present their reactive chromophores
in an exposed, mobile form, and the light that reveals the color also degrades
it.

Much of the history of synthetic organic pigments is the history of defeating
that fugitivity — taking the same chromophore classes and engineering them into
dense, hydrogen-bonded, insoluble crystals (the quinacridones, DPPs, perylenes,
and phthalocyanines of §3) where the excited molecule is locked in place and
its reactive pathways are sterically and electronically shut down, so a color
that fades in solution holds for centuries in the solid. This does not extend
uniformly across all pigment classes, however: even the best modern organics,
as a class, still tend to trail the great **inorganic** pigments — the iron
oxides, the cobalt and chromium oxides, the cadmiums — on outright permanence,
because a chromophore buried in an oxide lattice or a sulfide crystal is harder
for light to reach than one held in an organic molecule, however well packed.
That advantage is not universal, though: vermilion's blackening and chrome
yellow's browning (§6) are light-driven redox chemistry proceeding in fully
inorganic crystals. And permanence trades against
**toxicity**: the most durable historic
inorganics are heavy-metal compounds — cadmium, cobalt, lead, mercury — and the
reformulations of §6 (bismuth vanadate, the cadmium-free hues) are chasing the
genuinely hard target of matching their color *and* their permanence *without*
their toxicity. No single pigment yet wins on all three of fastness,
non-toxicity, and chroma at once; the palette is a set of engineering
compromises, and knowing the mechanism behind a color is knowing which
compromise it represents.

## The palette read as one piece

The abstractions from the earlier posts in this series correspond directly to
physical pigments. The particle in a box from the [fundamentals
post](/posts/fundamentals_of_quantum_chemistry.html) is a quinacridone crystal:
confining π electrons to a conjugated frame sets the box length, and the box
length sets the gap that is the color. The molecular-orbital energy levels from
the [water](/posts/2026-06-30-reading-water-geometry-orbitals-acidity-spectra.html)
and [Hartree–Fock](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html)
posts — the spacing between a filled level and an empty one — are the hue on
the palette: a HOMO–LUMO gap in an organic pigment, a crystal-field splitting in
a transition-metal oxide, an intervalence jump in Prussian blue, a semiconductor
band edge in cadmium red. Four mechanisms, one requirement — an electronic
energy gap in the 1.8–3.1 eV window (Table 1) — and four different physical
routes to satisfy it.

A tube of paint is two separable problems. It is an **electronic-structure
problem**: which photons the chromophore's energy levels let it absorb,
computed by the same machinery this series has built. And it is a **scattering
problem**: how the particles' refractive index and size return the unabsorbed
light, governed by Mie scattering and summarized by Kubelka–Munk (§7). The two
are independent, and the eye perceives their product. The modern palette applies
the same two-part physics that produced the fugitive lakes and toxic brilliants
of the historic palette, but engineers the chromophore's host — the crystal, the
lattice, the coordination site — to survive the light it is made to be seen by.

## References
