---
title: "One matrix element, two experiments: molar absorptivity and the Pockels effect"
date: 2026-07-03
author: Peter Johnston
tags: nonlinear optics, hyperpolarizability, electro-optics, Pockels effect, transition dipole, molar absorptivity, spectroscopy
description: A companion to the molar-absorptivity post. The absolute height of an absorption band, the refractive index, and the electro-optic coefficient of a poled material are three readouts of one quantity — the transition dipole. Normalizing every spectrum to 1 throws that quantity away. This traces the same matrix element from Beer's law through the two-level model to the Pockels effect, with worked numbers.
---

There is a habit, nearly universal in optical-materials talks, of plotting every
absorption spectrum **normalized to 1**. It makes the slides tidy: a dozen
compounds, all their bands scaled to the same peak height, the eye free to compare
*where* they absorb without the clutter of *how much*. It is also, quietly, the
deletion of the single most physically loaded number on the plot. The height of an
absorption band — the molar absorptivity you scaled away — is a direct readout of
the transition dipole moment, and that same transition dipole sets the refractive
index, the polarizability, and, for a push–pull chromophore, the electro-optic
coefficient that makes it useful in a modulator. Normalize to 1 and you have thrown
away the axis that predicts whether the material does anything.

The [previous post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
made half of this case: molar absorptivity $\varepsilon$ is a rate constant in
disguise, because the integrated band is proportional to $|\boldsymbol{\mu}_{ge}|^2$
and that fixes the Einstein coefficients — a *kinetic* quantity. This post makes
the other half. The very same $|\boldsymbol{\mu}_{ge}|^2$ runs straight into the
*optical* response — linear and nonlinear — so that Beer's law and the Pockels
effect turn out to be two measurements of one matrix element. It is the bridge from
this series' spectroscopy posts to its
[hyperpolarizability posts](/posts/QC-Maths-Framework-for-Hyperpolarizability.html),
and it is why a spectroscopist's instinct — *high molar absorptivity tends to go
with a strong electro-optic response* — is not a coincidence but a theorem.

## 1. The one number every optical spectrum is really measuring

The transition dipole moment between the ground state $|g\rangle$ and an excited
state $|e\rangle$ is the matrix element

$$\boldsymbol{\mu}_{ge} = \langle e | \hat{\boldsymbol{\mu}} | g \rangle,
\qquad \hat{\boldsymbol{\mu}} = -e\sum_i \mathbf{r}_i,$$

the same object that appears in Fermi's golden rule and in the configuration-
interaction and response calculations of the
[excited-state post](/posts/Maths-Framework-and-Basis-Sets.html). Every
oscillator strength, every absorption band, is a measurement of its magnitude.
Recall the packaging from last time: the integrated band gives the oscillator
strength, and the oscillator strength gives $|\boldsymbol{\mu}_{ge}|^2$,

$$f = 4.32\times10^{-9}\!\int_{\text{band}}\!\varepsilon(\tilde\nu)\,d\tilde\nu
\;\propto\; \tilde\nu_{ge}\,|\boldsymbol{\mu}_{ge}|^2 .$$

That is the entire content of an absorption intensity: **height (and width) of the
band $\to |\boldsymbol{\mu}_{ge}|^2$.** When a talk normalizes the band to unit
height, it is discarding exactly this — keeping $\tilde\nu_{ge}$ (where the band
sits) and erasing $|\boldsymbol{\mu}_{ge}|^2$ (how much dipole the transition
carries). We can put a number on it and carry that number all the way to a
modulator. Take a representative *high-performance* donor–acceptor dye — a
Disperse Red / DANS-type push–pull azo chromophore of the sort actually poled into
electro-optic films: a charge-transfer band at $\lambda_{\max}=480$ nm
($\tilde\nu_{ge}\approx20{,}800\ \mathrm{cm^{-1}}$, $E_{ge}=2.58$ eV), peak molar
absorptivity $\varepsilon_{\max}\approx4\times10^{4}\ \mathrm{L\,mol^{-1}\,cm^{-1}}$,
band width $\approx5000\ \mathrm{cm^{-1}}$. Integrating gives $f\approx0.92$ and

$$|\boldsymbol{\mu}_{ge}| \approx 9.7\ \text{D}.$$

Hold onto that 9.7 D. It is the number the normalized plot would have hidden, and
it is about to reappear in three different experiments.

## 2. The linear response is the absorption band, continued

Before the nonlinearity, the *linear* optical response already runs on
$|\boldsymbol{\mu}_{ge}|^2$. Second-order perturbation theory gives the frequency-
dependent polarizability as a sum over excited states,

$$\alpha(\omega) = \frac{2}{\hbar}\sum_{e}
\frac{\tilde\omega_{ge}\,|\boldsymbol{\mu}_{ge}|^2}{\tilde\omega_{ge}^2-\omega^2},$$

and near an isolated, dominant transition this is one term:
$\alpha(\omega)\propto|\boldsymbol{\mu}_{ge}|^2/(\tilde\omega_{ge}^2-\omega^2)$.
The macroscopic refractive index $n(\omega)$ is built from $\alpha(\omega)$, so the
dispersion of $n$ — how the glass bends blue light more than red — is set by the
same transition dipoles that set the absorption. This is not an analogy; it is
Kramers–Kronig. Absorption is the imaginary part of the response and refraction is
the real part, and the two are Hilbert transforms of one another: a single complex
function $\chi(\omega)$ whose strength is $|\boldsymbol{\mu}_{ge}|^2$. **The
refractive-index spectrum is the absorption spectrum continued into the transparent
region.** You cannot scale one to 1 without scaling the other. Already at linear
order, "how much" is not a cosmetic axis — it is the whole amplitude of the
response.

## 3. The nonlinear response: the two-level model

Now push the field harder. Expand the induced molecular dipole in powers of the
local field,

$$\mu_{\text{ind}} = \mu_0 + \alpha E + \tfrac{1}{2}\beta E^2 + \tfrac{1}{6}\gamma E^3 + \cdots,$$

and the first *hyperpolarizability* $\beta$ is the leading nonlinear term — the one
responsible for second-harmonic generation and the linear electro-optic (Pockels)
effect. Like $\alpha$, it has an exact sum-over-states form, a double sum over
excited states weighted by products of transition dipoles. For the donor–acceptor
chromophores that matter in electro-optics, one charge-transfer state dominates so
completely that the sum collapses to a single term — the **two-level model** of
Oudar and Chemla.[@OudarChemla1977; @Oudar1977] Its static value is

$$\beta_0 \;=\; \frac{3\,\Delta\mu_{ge}\,|\boldsymbol{\mu}_{ge}|^2}{E_{ge}^{2}},$$

where $\Delta\mu_{ge} = \mu_{ee}-\mu_{gg}$ is the change in *permanent* dipole
between ground and excited states (Figure 1). Look at what governs it: the
transition dipole squared $|\boldsymbol{\mu}_{ge}|^2$ — the absorption intensity —
in the numerator, and the transition energy squared $E_{ge}^2$ — where the band
sits — in the denominator. A hyperpolarizability is an absorption band read through
a different lens: strong ($|\boldsymbol{\mu}_{ge}|^2$ large) and red ($E_{ge}$
small) is what makes $\beta_0$ big.

```tikzpicture
\begin{tikzpicture}[>=Stealth]
  \draw[line width=1.4pt,black] (-1.6,0) -- (1.6,0) node[right,font=\small] {$|g\rangle$};
  \draw[line width=1.4pt,black] (-1.6,3) -- (1.6,3) node[right,font=\small] {$|e\rangle$};
  % transition dipole (up-down double arrow)
  \draw[<->,blue!60!black,line width=1.4pt] (0,0.15) -- (0,2.85);
  \node[blue!50!black,font=\small,fill=white,inner sep=1pt] at (0,1.5) {$\boldsymbol{\mu}_{ge}$};
  \node[left,font=\scriptsize,align=right] at (-1.7,1.5) {$E_{ge}$};
  % permanent dipoles as horizontal arrows on each level
  \draw[->,black!70,line width=1pt] (-1.3,-0.35) -- (-0.3,-0.35);
  \node[font=\scriptsize] at (-1.55,-0.35) {$\mu_{gg}$};
  \draw[->,red!65!black,line width=1pt] (-1.3,3.35) -- (0.9,3.35);
  \node[font=\scriptsize] at (-1.55,3.35) {$\mu_{ee}$};
  % Delta mu bracket
  \node[red!55!black,font=\small,align=left] at (4.3,1.5)
    {$\Delta\mu_{ge}=\mu_{ee}-\mu_{gg}$\\[4pt]$\beta_0 \propto \dfrac{\Delta\mu_{ge}\,|\boldsymbol{\mu}_{ge}|^2}{E_{ge}^{2}}$};
\end{tikzpicture}
```

*Figure 1.* The two-level model. A single charge-transfer excitation carries a
transition dipole $\boldsymbol{\mu}_{ge}$ (what absorption measures) and a change in
permanent dipole $\Delta\mu_{ge}$ (the donor–acceptor push–pull). The static first
hyperpolarizability is built from both, with the same $|\boldsymbol{\mu}_{ge}|^2$
that sets the molar absorptivity sitting in the numerator.

Put the numbers in. With $|\boldsymbol{\mu}_{ge}|=9.7$ D from the absorption band,
a typical push–pull dipole change $\Delta\mu_{ge}\approx6$ D, and $E_{ge}=2.58$ eV,

$$\beta_0 = \frac{3\,(6\,\text{D})(9.7\,\text{D})^2}{(2.58\,\text{eV})^2}
\approx 1.0\times10^{-28}\ \text{esu} = 99\times10^{-30}\ \text{esu},$$

a strong value, characteristic of an *engineered* electro-optic dye. It is worth
being honest about the scale, because the molecule the two-level model was actually
built on — **para-nitroaniline (PNA)**, the simplest donor–π–acceptor there is, a
single benzene ring with one amino donor and one nitro acceptor[@OudarChemla1977] —
is nothing like this good. PNA is a deliberately weak benchmark: its band is
higher-energy and less intense, and its static $\beta_0$ is only of order
$10\times10^{-30}$ esu, roughly a tenth of the value above. That tenfold gap is not
incidental — it is precisely what decades of chromophore engineering *bought*, and
it was bought by turning the two knobs the formula exposes: pushing
$|\boldsymbol{\mu}_{ge}|^2$ up (a stronger, more intense band) and $E_{ge}$ down (a
redder one). Every factor that went into the number above except $\Delta\mu_{ge}$
came straight off the absorption spectrum — and the dominant, squared factor is
precisely the peak height a normalized plot erases.

## 4. From $\beta$ to the Pockels effect

A single molecule's $\beta$ becomes a device property through two more steps, both
of which preserve the proportionality. First, orientation: a centrosymmetric
arrangement has no net $\beta$ (the second-order response cancels by symmetry), so
the chromophores are **poled** — aligned in a field while the polymer is warm, then
frozen in place. The macroscopic second-order susceptibility is the molecular
$\beta$ times the number density and an orientational average,

$$\chi^{(2)} \propto N\,\langle\cos^3\theta\rangle\,\beta ,$$

and the linear **electro-optic coefficient** — the Pockels coefficient $r$ that
tells you how much the refractive index shifts per volt — is

$$r \;\propto\; \frac{\chi^{(2)}}{n^4} \;\propto\; \frac{N\,\langle\cos^3\theta\rangle\,\beta}{n^4}.$$

This is the number that matters for a modulator: apply a voltage, change $n$ via
$r$, change the optical path length, and you have written an electrical signal onto
a beam of light — the heart of the electro-optic modulators in every long-haul
fiber link.[@DaltonSullivanBale2010] And it descends, factor by factor, from
$\beta$, hence from $|\boldsymbol{\mu}_{ge}|^2$, hence from the absorption intensity.
The spectroscopist's instinct is now a derivation: a molecule with a strong,
low-lying charge-transfer band ($\varepsilon_{\max}$ large, $\lambda_{\max}$ red)
has a large $|\boldsymbol{\mu}_{ge}|^2$ and a small $E_{ge}$, so it has a large
$\beta_0$, so — once poled — it makes a good electro-optic material. The
normalized-to-1 plot in the seminar had, in every one of its curves, silently
discarded the quantity that ranks the compounds for exactly the application they
were presumably being screened for.

At an operating wavelength the static $\beta_0$ is enhanced by dispersion as the
photon energy climbs toward the transition. The two-level Pockels dispersion has a
resonance at the one-photon energy — i.e. at $\lambda_{\max}$ itself:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={operating wavelength (nm)},
    ylabel={$\beta(-\omega;\omega,0)\,/\,\beta_0$ (dispersion enhancement)},
    title={Resonant enhancement of $\beta$ collides with the absorption band},
    xmin=450, xmax=2600, ymin=0, ymax=11,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
]
% absorption band region (shaded, near lambda_max = 480 nm)
\addplot[draw=none, fill=red!12] coordinates {(450,0)(560,0)(560,11)(450,11)} \closedcycle;
\node[red!55!black, font=\scriptsize, rotate=90, anchor=south] at (axis cs:505,5.5) {absorption band ($\lambda_{\max}\!=\!480$ nm)};
% dispersion curve
\addplot[thick, mark=*, mark size=1.6pt, color=blue!60!black] coordinates {
 (2500,1.06) (2200,1.08) (2000,1.10) (1800,1.13) (1600,1.17) (1550,1.18)
 (1400,1.23) (1300,1.28) (1200,1.34) (1100,1.43) (1000,1.56) (900,1.77)
 (800,2.15) (720,2.76) (650,3.96) (600,6.07) (560,10.73)
};
% telecom markers
\addplot[only marks, mark=square*, mark size=2.5pt, color=orange!80!black] coordinates {(1550,1.18) (1300,1.28)};
\node[font=\scriptsize, anchor=west] at (axis cs:1560,2.1) {telecom C-band (1550 nm), 1.3 nm};
\end{axis}
```

*Figure 2.* Two-level dispersion of the Pockels hyperpolarizability
$\beta(-\omega;\omega,0)$ for the $\lambda_{\max}=480$ nm chromophore. In the
transparent telecom window the enhancement over the static value is modest (about
$1.2$–$1.3\times$), but it grows without bound as the operating wavelength
approaches $\lambda_{\max}$ — where the molecule also absorbs. The knob that raises
$\beta$ is the knob that destroys transparency.

## 5. The nonlinearity–transparency trade-off

Figure 2 is the whole design problem in one curve. Everything that makes $\beta$
large pulls the material toward its own absorption band. You can raise $\beta_0$ by
lowering $E_{ge}$ — red-shifting $\lambda_{\max}$ — but the Pockels resonance sits
*at* $\lambda_{\max}$, so a redder chromophore brings its absorption (and optical
loss) closer to your operating wavelength. You can raise $\beta_0$ by increasing
$|\boldsymbol{\mu}_{ge}|^2$ — a stronger band — but that is, by definition, a larger
$\varepsilon$ and more absorption. And you can borrow resonant enhancement by
operating nearer the band, at the cost of the transparency the device needs. This
is the **nonlinearity–transparency trade-off**, and it is not an engineering
nuisance layered on top of the physics; it is the physics. One matrix element,
$|\boldsymbol{\mu}_{ge}|^2$, and one energy, $E_{ge}$, set both the thing you want
(a big electro-optic coefficient) and the thing you must avoid (absorption at the
operating wavelength). Chromophore design is the art of playing that single matrix
element against itself.[@Kanis1994; @Boyd2008]

## 6. Back to the seminar

So the offhand question — *why not show any of the kinetics of absorption for these
materials?* — was not a non-sequitur. It was pointing at the axis the normalization
erased. The peak molar absorptivity of each of those bands was, simultaneously:

- a **rate constant**, fixing the Einstein coefficients and the radiative lifetime
  (the [previous post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html));
- the **amplitude of the linear response**, and hence the refractive-index
  dispersion, through Kramers–Kronig;
- the dominant factor in the **first hyperpolarizability**, and hence in the
  poled-film electro-optic coefficient — the figure of merit for the modulator the
  compounds were likely being screened to become.

All three are $|\boldsymbol{\mu}_{ge}|^2$, read out in different experiments. To
normalize every spectrum to unit height is to keep the one thing that is easy to
see — the color, $\lambda_{\max}$ — and discard the one thing that is hard-won and
decisive: how much dipole the transition actually carries. The spectra looked
comparable because they had been *made* comparable, scaled to hide the very quantity
that distinguished them. A transition dipole is not a detail of an absorption band.
It is the band's whole reason for mattering — in the kinetics, in the refraction,
and in the volt-to-light conversion at the end of the line.

## References
