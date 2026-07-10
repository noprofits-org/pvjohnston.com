---
title: "Reading water off the page: geometry, orbitals, acidity, and spectra"
date: 2026-06-30
author: Peter Johnston
tags: water, physical chemistry, molecular orbitals, symmetry, acid-base, spectroscopy
description: Water is the most familiar molecule and one of the strangest. This post builds it up from the bottom — where the atoms sit, what the electrons do, why it is both an acid and a base, and how it talks to light.
---

Water is the molecule we know best and understand least casually. Everyone can
draw it — a fat oxygen with two hydrogen ears — but almost every interesting
property of the substance is hiding in details that the cartoon leaves out: the
exact angle between the bonds, the shape of the orbitals the lone pairs live in,
the fact that pure water is *both* an acid and a base at once, and the reason a
swimming pool is blue when a glassful is not.

This post takes the single molecule $\mathrm{H_2O}$ and reads it off the page
in four passes — **geometry**, **orbitals**, **acid–base behavior**, and
**spectra** — because those four are not separate facts to memorize. Each one
explains the next. The bend gives the dipole; the dipole comes from lone pairs;
the lone pairs are the base sites; and the bonds whose stretches we will see in
the infrared are the same bonds whose faint overtones turn the ocean blue.

## 1. The shape

Two numbers fix the geometry of an isolated water molecule in the gas phase: the
O–H bond length, about **0.958 Å**, and the H–O–H angle, about **104.5°**.[@BenedictGailarPlyler1956]
The molecule is *bent*, and that bend is the whole story.

```tikzpicture
\begin{tikzpicture}[>=Stealth, line width=1pt]
  \coordinate (O) at (0,0);
  \coordinate (H1) at (-1.898,-1.469);
  \coordinate (H2) at (1.898,-1.469);
  % bonds
  \draw (O) -- (H1);
  \draw (O) -- (H2);
  % lone pairs above oxygen
  \foreach \x in {-0.62,-0.42} \fill (\x,0.66) circle (0.05);
  \foreach \x in {0.42,0.62}   \fill (\x,0.66) circle (0.05);
  % atoms
  \filldraw[fill=red!70,draw=black] (O) circle (0.42);
  \filldraw[fill=gray!20,draw=black] (H1) circle (0.30);
  \filldraw[fill=gray!20,draw=black] (H2) circle (0.30);
  \node[white,font=\bfseries] at (O) {O};
  \node[font=\bfseries] at (H1) {H};
  \node[font=\bfseries] at (H2) {H};
  % angle arc + label
  \draw[line width=0.6pt] (-142.25:0.95) arc (-142.25:-37.75:0.95);
  \node[font=\small] at (0,-1.32) {$104.5^{\circ}$};
  % bond-length label
  \node[font=\small, rotate=-37.75, anchor=south] at (0.95,-0.735) {0.958\,\AA};
\end{tikzpicture}
```

The standard explanation is VSEPR. Oxygen brings six valence electrons; two of
them pair with the hydrogens to make bonds, and the remaining four sit as two
**lone pairs**. That is four "electron domains" around the oxygen — two bonds and
two lone pairs — and four domains arrange themselves tetrahedrally. We only *see*
the two O–H bonds, so the molecule looks bent rather than tetrahedral, and the
ideal tetrahedral angle of 109.5° is squeezed down to 104.5° because lone pairs
are fatter than bonds and push harder.

That is the right intuition, but the precise angle is telling you something more
specific. A pure $sp^3$ picture predicts 109.5°; the real 104.5° sits between
109.5° and the 90° you would get from unhybridized $p$ orbitals. The bonds, in
other words, carry *more p-character* than an ideal $sp^3$ hybrid, and the lone
pairs carry correspondingly more s-character. We will see that asymmetry again in
a moment, from a completely different direction, and it will turn out to be
measurable.

One consequence is immediate. Because the molecule is bent, the two O–H bond
dipoles do not cancel — they add to a net **dipole moment of 1.85 D**, pointing
along the symmetry axis with the oxygen as the negative end. A linear water
molecule would be nonpolar, would not hydrogen-bond the way it does, would not
dissolve salt, and would not be a greenhouse gas. Almost everything water *does*
follows from the fact that it does not lie flat.

## 2. The electrons

To go below VSEPR we need the molecular orbitals, and to get those cleanly we use
the molecule's symmetry. Bent water belongs to the point group $C_{2v}$: it has
a two-fold rotation axis (the bisector of the H–O–H angle) and two mirror planes
(the molecular plane and the plane perpendicular to it through the axis). Put the
$C_2$ axis along $z$ and the molecule in the $yz$ plane.

Symmetry sorts the atomic orbitals into a small number of labelled boxes. The two
hydrogen 1s orbitals combine into two **symmetry-adapted** combinations: a
symmetric one (their sum, which is unchanged by every symmetry operation —
label $a_1$) and an antisymmetric one (their difference — label $b_2$). The
oxygen valence orbitals sort themselves too: the $2s$ and $2p_z$ are both
$a_1$; the $2p_y$ is $b_2$; and the $2p_x$, which sticks straight out of
the molecular plane, is $b_1$ — and it is *alone in its box*, because no
hydrogen combination has $b_1$ symmetry.

Orbitals only mix with other orbitals of the same label. So:

- The $a_1$ set — O$\,2s$, O$\,2p_z$, and the symmetric H combination — mix
  into a low bonding orbital ($2a_1$), a roughly nonbonding one ($3a_1$), and
  an empty antibonding one.
- The $b_2$ set — O$\,2p_y$ and the antisymmetric H combination — make a
  bonding orbital ($1b_2$) and an empty antibonding partner.
- The lonely $b_1$ orbital (O$\,2p_x$) has nothing to mix with, so it stays a
  **pure, nonbonding oxygen $p$ orbital** ($1b_1$), perpendicular to the
  molecular plane.

Filling the eight valence electrons from the bottom gives the ground
configuration $(2a_1)^2(1b_2)^2(3a_1)^2(1b_1)^2$:

```tikzpicture
\newcommand{\pair}[2]{%
  \draw[->,line width=0.7pt] (#1-0.12,#2-0.17) -- (#1-0.12,#2+0.17);
  \draw[->,line width=0.7pt] (#1+0.12,#2+0.17) -- (#1+0.12,#2-0.17);
}
\begin{tikzpicture}[line width=0.8pt,
   lev/.style={line width=1.3pt}]
  \draw[->,gray] (-5.4,-3.9) -- (-5.4,2.6);
  \node[gray,rotate=90,anchor=south,font=\small] at (-5.65,-0.7) {energy};
  % --- correlation lines (drawn first, behind) ---
  \draw[dashed,gray!60] (-3.6,-3.0) -- (-0.4,-3.4);
  \draw[dashed,gray!60] (3.6,0.55) -- (0.4,-3.4);
  \draw[dashed,gray!60] (-3.6,-0.25) -- (-0.4,-1.4);
  \draw[dashed,gray!60] (3.6,0.40) -- (0.4,-1.4);
  \draw[dashed,gray!60] (-3.6,0.0) -- (-0.4,0.30);
  \draw[dashed,gray!60] (3.6,0.55) -- (0.4,0.30);
  \draw[dashed,gray!60] (-3.6,0.25) -- (-0.4,0.75);
  % --- oxygen atomic orbitals (left) ---
  \node[font=\bfseries] at (-4,2.35) {O};
  \draw[lev] (-4.4,-3.0) -- (-3.6,-3.0); \node[left,font=\small] at (-4.45,-3.0) {$2s$};
  \draw[lev] (-4.4,-0.25) -- (-3.6,-0.25);
  \draw[lev] (-4.4,0.0) -- (-3.6,0.0);
  \draw[lev] (-4.4,0.25) -- (-3.6,0.25);
  \node[left,font=\small] at (-4.45,0.0) {$2p$};
  % --- hydrogen SALCs (right) ---
  \node[font=\bfseries] at (4,2.35) {2\,H};
  \draw[lev] (3.6,0.55) -- (4.4,0.55); \node[right,font=\small] at (4.45,0.55) {$a_1$};
  \draw[lev] (3.6,0.40) -- (4.4,0.40); \node[right,font=\small] at (4.45,0.40) {$b_2$};
  % --- molecular orbitals (center) ---
  \node[font=\bfseries] at (0,2.45) {H$_2$O};
  \draw[lev] (-0.4,-3.4) -- (0.4,-3.4); \node[below,font=\small] at (0,-3.5) {$2a_1$};
  \pair{0}{-3.4}
  \draw[lev] (-0.4,-1.4) -- (0.4,-1.4); \node[left,font=\small] at (-0.45,-1.4) {$1b_2$};
  \pair{0}{-1.4}
  \draw[lev] (-0.4,0.30) -- (0.4,0.30); \node[left,font=\small] at (-0.45,0.30) {$3a_1$};
  \pair{0}{0.30}
  \draw[lev] (-0.4,0.75) -- (0.4,0.75); \node[right,font=\small] at (0.45,0.75) {$1b_1$ (HOMO)};
  \pair{0}{0.75}
  \draw[lev] (-0.4,1.5) -- (0.4,1.5); \node[right,font=\small] at (0.45,1.5) {$4a_1^{*}$};
  \draw[lev] (-0.4,2.0) -- (0.4,2.0); \node[right,font=\small] at (0.45,2.0) {$2b_2^{*}$};
\end{tikzpicture}
```

Here is where the orbital picture earns its keep, and where the cartoon of "two
identical lone pairs" quietly breaks. In the canonical molecular orbitals above,
the two lone pairs are **not equivalent**. One of them, $1b_1$, is a pure
oxygen $p$ orbital pointing out of the molecular plane. The other, $3a_1$,
lies *in* the plane and is a mix of oxygen $s$ and $p$. They have different
shapes and different energies — and that difference is something you can measure.

Photoelectron spectroscopy shoots photons at water vapor and records the energy
needed to knock each electron out. If the two lone pairs were identical, you
would see a single lone-pair band. Instead you see two clearly separated
ionization energies — about **12.6 eV** for $1b_1$ and **14.7 eV** for
$3a_1$ — followed by $1b_2$ near 18.5 eV and the deep $2a_1$ near 32
eV.[@Turner1970] The spectrum is the receipt: the "two equivalent rabbit-ear
lone pairs" you may have drawn in an organic-chemistry class are a *localized*
description — a perfectly valid mathematical re-mixing of the canonical orbitals
that is handy for thinking about hydrogen bonding — but it is not what the
electrons individually look like, and the photoelectron spectrum knows the
difference. Both pictures describe the same total electron density; only one of
them has orbitals you can ionize one at a time.

## 3. Acid and base at once

Water's most underappreciated trick is that it reacts with itself. In any glass
of pure water, a tiny fraction of the molecules are constantly trading a proton:

$$2\,\mathrm{H_2O} \;\rightleftharpoons\; \mathrm{H_3O^+} + \mathrm{OH^-}$$

One water molecule donates a proton (acting as a Brønsted **acid**, leaving
behind hydroxide $\mathrm{OH^-}$); the other accepts it (acting as a
**base**, becoming hydronium $\mathrm{H_3O^+}$). A substance that is both acid
and base is **amphoteric**, and the proton it accepts lands exactly on one of the
lone pairs from the previous section. The orbital story and the acid–base story
are the same story.

The position of this equilibrium is the **autoionization constant**,

$$K_w = [\mathrm{H_3O^+}][\mathrm{OH^-}] = 1.0\times10^{-14}\quad(\text{at }25\,^{\circ}\mathrm{C}).$$

At 25 °C the two concentrations are equal at $10^{-7}\,\mathrm{M}$, which is
where "neutral = pH 7" comes from. But $K_w$ is an equilibrium constant, and
like any equilibrium it shifts with temperature. Autoionization is endothermic,
so warming water pushes it to the right: more ions, larger $K_w$, smaller
$\mathrm{p}K_w$. Crucially, the *neutral* pH — where $[\mathrm{H_3O^+}] =
[\mathrm{OH^-}]$ — is always $\mathrm{p}K_w/2$, so it slides too:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={Temperature ($^{\circ}$C)},
    ylabel={value},
    title={Water's autoionization shifts with temperature},
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    xmin=-5, xmax=105, ymin=5.5, ymax=15.5,
    xtick={0,25,50,75,100},
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, mark=*, mark size=2pt, color=blue] coordinates {
    (0,14.94) (25,14.00) (50,13.26) (75,12.70) (100,12.29)
};
\addplot[thick, mark=square*, mark size=2pt, color=red] coordinates {
    (0,7.47) (25,7.00) (50,6.63) (75,6.35) (100,6.14)
};
\legend{$\mathrm{p}K_w$, neutral pH ($=\mathrm{p}K_w/2$)}
\end{axis}
```

So a pot of pure water at 100 °C is perfectly neutral at pH ≈ 6.1, not 7 —
neutrality is about $[\mathrm{H_3O^+}] = [\mathrm{OH^-}]$, not about a magic
number. This is the kind of fact that the "pH 7 is neutral" shorthand quietly
hides.

How acidic *is* water, taken as an acid? It depends entirely on the convention
you use, which is worth stating plainly because the textbooks disagree. In the
autoionization convention above, $\mathrm{p}K_a(\mathrm{H_2O}) = \mathrm{p}K_w =
14.0$. If you instead fold water's own molar concentration (about 55.5 M) into
the constant, you get the often-quoted $\mathrm{p}K_a \approx 15.7$. Both
numbers are "right"; they are answers to slightly different questions, and
arguments about water's pKa are almost always arguments about which one you meant.

There is one more place the simple equation lies, and it is a beautiful lie. We
write the product of autoionization as $\mathrm{H_3O^+}$, but a bare hydronium
ion is not really what floats around in liquid water. The excess proton is shared
and smeared across a little cluster of molecules — the **Eigen** cation
$\mathrm{H_9O_4^+}$ (a hydronium hydrogen-bonded to three more waters) and the
**Zundel** cation $\mathrm{H_5O_2^+}$ (a proton shared equally between two
waters), interconverting on a femtosecond timescale.[@Marx1999] That delocalization
is why protons move through water far faster than any ion has any right to: rather
than a single heavy ion shouldering its way through, a proton hops down a chain of
hydrogen bonds — bond breaks here, forms there — so that the *charge* travels much
farther than any one nucleus does. This is the **Grotthuss mechanism**, and it is
why acids conduct electricity so well. The lone pairs we drew in Section 2 are the
hand-off points.

## 4. Talking to light

Finally, how does water interact with light — and what does that tell us back
about the geometry? A bent triatomic has exactly the right number of moving parts
to be interesting. With $N = 3$ atoms, there are $3N = 9$ degrees of freedom;
subtract three for translation and three for rotation (water is nonlinear), and
$3N - 6 = 3$ **vibrational modes** remain:

```tikzpicture
\newcommand{\skel}{%
  \coordinate (O) at (0,0);
  \coordinate (Ha) at (-1.0,-0.78);
  \coordinate (Hb) at (1.0,-0.78);
  \draw[line width=1pt] (O)--(Ha);
  \draw[line width=1pt] (O)--(Hb);
  \filldraw[fill=red!70,draw=black] (O) circle (0.26);
  \node[white,font=\scriptsize\bfseries] at (O) {O};
  \filldraw[fill=gray!20,draw=black] (Ha) circle (0.18);
  \filldraw[fill=gray!20,draw=black] (Hb) circle (0.18);
}
\begin{tikzpicture}[>=Stealth]
  % --- symmetric stretch ---
  \begin{scope}[xshift=-3.7cm]
    \skel
    \draw[->,line width=0.9pt,blue!60!black] (Ha) -- ++(-0.62,-0.48);
    \draw[->,line width=0.9pt,blue!60!black] (Hb) -- ++(0.62,-0.48);
    \node[align=center,font=\small] at (0,-1.9)
      {$\nu_1$ symmetric stretch\\ $A_1$, 3657\,cm$^{-1}$};
  \end{scope}
  % --- bend ---
  \begin{scope}[xshift=0cm]
    \skel
    \draw[->,line width=0.9pt,blue!60!black] (Ha) -- ++(0.58,-0.16);
    \draw[->,line width=0.9pt,blue!60!black] (Hb) -- ++(-0.58,-0.16);
    \node[align=center,font=\small] at (0,-1.9)
      {$\nu_2$ bend\\ $A_1$, 1595\,cm$^{-1}$};
  \end{scope}
  % --- antisymmetric stretch ---
  \begin{scope}[xshift=3.7cm]
    \skel
    \draw[->,line width=0.9pt,blue!60!black] (Ha) -- ++(-0.62,-0.48);
    \draw[->,line width=0.9pt,blue!60!black] (Hb) -- ++(-0.62,0.48);
    \node[align=center,font=\small] at (0,-1.9)
      {$\nu_3$ antisym.\ stretch\\ $B_2$, 3756\,cm$^{-1}$};
  \end{scope}
\end{tikzpicture}
```

Symmetry labels the modes just as it labelled the orbitals: the symmetric stretch
and the bend keep the molecule's full symmetry ($A_1$), while the antisymmetric
stretch swaps the two bonds ($B_2$). In $C_{2v}$, a vibration is infrared-active
if it changes the dipole moment — which means it must transform like $x$, $y$,
or $z$. Both $A_1$ (like $z$) and $B_2$ (like $y$) qualify, so **all three
modes are infrared-active**.[@BenedictGailarPlyler1956] That is why water vapor is
such a voracious infrared absorber, and — together with its permanent dipole, which
also makes it a strongly absorbing asymmetric-top rotor in the microwave and
far-infrared — why $\mathrm{H_2O}$ is the dominant natural greenhouse gas. The
bend from Section 1 is doing the absorbing.

Now climb up in energy to visible and ultraviolet light, where transitions move
*electrons* rather than nuclei. Water's first electronic absorption promotes a
lone-pair electron (out of that $1b_1$ orbital) and does not switch on until
about 7 eV — roughly 175 nm, deep in the vacuum ultraviolet.[@EisenbergKauzmann1969]
There is simply no electronic transition anywhere in the 400–700 nm visible band.
That is why water is colorless: a glassful has nothing to absorb.

And yet a deep enough body of water is unmistakably blue, and not because of the
sky. The blue is *intrinsic*, and its origin is the one loose end tying this whole
post together. Liquid water absorbs very weakly in the **red**, around 660–700 nm,
through **overtones and combinations of the O–H stretching vibrations** —
the same $\nu_1$ and $\nu_3$ from the diagram above, stacked several quanta
high.[@BraunSmirnov1993] Each individual absorption is feeble, which is why a
glassful looks clear, but over meters of ocean or the depth of a glacier the red
end of sunlight is quietly removed and what comes back to your eye is blue. Water
is, as far as anyone knows, the only common substance whose color comes from
*vibrational* rather than electronic transitions — its color is, quite literally,
the sound of its bonds, shifted up into the visible.

## The molecule reads as one piece

Run back through the four passes and notice that nothing was independent. The bend
(§1) exists because oxygen carries two lone pairs, and those lone pairs are not the
identical ears of the cartoon but two distinct orbitals you can ionize separately
(§2). Those same lone pairs are the base sites that catch a proton during
autoionization, and the structure of the proton they catch is what makes water
conduct (§3). The O–H bonds whose bending and stretching we counted as three
infrared modes are, several overtones up, exactly the bonds whose absorption makes
the ocean blue (§4).

The cartoon of an oxygen with two hydrogen ears is not wrong. It is just the title
page. Everything water does for a living is written in the parts the cartoon leaves
out — the precise angle, the asymmetric lone pairs, the self-ionization, and the
faint red overtones — and once you can read those, the most familiar molecule
stops being familiar in the dull sense and starts being familiar in the way an old
machine is familiar to the person who can take it apart.

## References
