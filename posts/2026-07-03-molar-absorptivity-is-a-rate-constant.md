---
title: "Molar absorptivity is a rate constant in disguise"
date: 2026-07-03
author: Peter Johnston
tags: spectroscopy, quantum chemistry, molar absorptivity, Beer-Lambert, Einstein coefficients, transition dipole, fluorescence
description: The molar absorptivity in Beer's law looks like a static property of a molecule — a number you read off a table, like a melting point. It is not. The integrated absorption band is proportional to the same transition dipole that fixes the spontaneous-emission rate, so an absorption measurement quietly measures a lifetime. This post follows the chain from Beer's law to the Einstein coefficients and shows why weak absorbers are always slow emitters.
---

Open any table of UV–visible data and the molar absorptivity $\varepsilon$ sits
there looking like a fixed fact about a molecule — $\varepsilon_{\max} \approx
5\times10^{4}\ \mathrm{L\,mol^{-1}\,cm^{-1}}$ for this dye, $\approx 15$ for that
carbonyl $n\to\pi^{*}$ band — reported to a couple of significant figures and
filed next to the melting point and the density. It enters
Beer's law as a proportionality constant,

$$A = \varepsilon\, c\, \ell,$$

and the whole apparatus feels thermodynamic: dissolve a known concentration $c$,
set a known path length $\ell$, read the absorbance $A$, and the constant that
links them is a *property* of the substance. Nothing in that sentence mentions
time. Nothing seems to be happening.

The claim of this post is that $\varepsilon$ is not a static property at all. It
is a **rate constant**, seen through a steady-state window. The same molecular
quantity that sets how strongly a compound absorbs also sets how fast its
excited state radiates — they are literally proportional — so when you measure an
absorption spectrum you have, without touching a clock, measured a lifetime. The
argument runs through the Einstein coefficients, and it ends somewhere useful: it
explains why the faint transitions are always the long-lived ones, why $n\to\pi^{*}$
bands are both weak *and* slow, and why phosphorescence lasts. The transition
dipole matrix element that the [Hartree–Fock post](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html)
and the [excited-state post](/posts/Maths-Framework-and-Basis-Sets.html) keep
returning to is the single number underneath all of it.

## 1. Beer's law is already a rate law — in space

Start by taking Beer's law more seriously than usual. The logarithm and the
base-10 are a spectroscopist's convention; strip them off and look at the light
itself. A monochromatic beam of intensity $I$ enters a thin slab of thickness
$dx$ containing $\mathcal{N}$ absorbers per unit volume, each presenting an
absorption **cross section** $\sigma$ (an effective area, in $\mathrm{cm^2}$). The
fraction of the beam removed in that slab is the fraction of the slab's face
"blocked" by absorbers, $\sigma\mathcal{N}\,dx$, so

$$\frac{dI}{dx} = -\,\sigma\,\mathcal{N}\, I .$$

This is a first-order rate equation — not in time, but in distance. Its solution
is the exponential $I(x) = I_0\,e^{-\sigma \mathcal{N} x}$, the Beer–Lambert law
in its natural form, and matching it to the base-10 version fixes the conversion
between the microscopic cross section and the tabulated molar absorptivity:

$$\sigma = \frac{\ln 10}{N_A}\,(10^{3})\,\varepsilon \approx
3.82\times10^{-21}\ \varepsilon \quad (\sigma\ \text{in }\mathrm{cm^2},\
\varepsilon\ \text{in } \mathrm{L\,mol^{-1}\,cm^{-1}}).$$

```tikzpicture
\begin{tikzpicture}[>=Stealth]
  % slab
  \fill[blue!7] (0,0) rectangle (6,2.6);
  \draw[blue!55!black,thick] (0,0) rectangle (6,2.6);
  \foreach \x/\y in {0.9/0.6, 1.7/1.9, 2.6/1.1, 3.4/2.0, 4.1/0.7, 4.9/1.6, 5.4/1.0, 1.3/1.4, 3.9/1.5, 2.2/0.4} {
    \fill[blue!55!black] (\x,\y) circle (1.6pt);
  }
  \node[align=center,font=\scriptsize] at (3,-0.4) {slab: $\mathcal{N}$ absorbers per unit volume, cross section $\sigma$};
  % incoming beam
  \draw[->,red!70!black,line width=2pt] (-2.0,1.3) -- (0,1.3);
  \node[red!60!black,font=\small,above] at (-1.5,1.35) {$I_0$};
  % outgoing (thinner)
  \draw[->,red!70!black,line width=1.1pt] (6,1.3) -- (8.0,1.3);
  \node[red!60!black,font=\small,above] at (7.4,1.35) {$I$};
  % slab thickness
  \draw[<->,black!60] (0,-0.05) -- (6,-0.05);
  \draw[dashed,black!35] (4.3,0) -- (4.3,2.6);
  \draw[dashed,black!35] (4.7,0) -- (4.7,2.6);
  \node[font=\scriptsize] at (7.0,2.4) {$\dfrac{dI}{dx} = -\sigma\mathcal{N}\,I$};
\end{tikzpicture}
```

*Figure 1.* Beer's law read as spatial first-order decay. Each slab of thickness
$dx$ removes a fixed *fraction* $\sigma\mathcal{N}\,dx$ of whatever light reaches
it, so the intensity falls exponentially with depth. The molar absorptivity is
the cross section $\sigma$ in disguise: $\sigma \approx 3.82\times10^{-21}\,
\varepsilon$. For a strong band ($\varepsilon \approx 10^{4}$) this is
$\sim\!4\times10^{-17}\ \mathrm{cm^2}$ — the geometric footprint of a small
molecule, which is why strong chromophores absorb "as if solid."

So far this only relocates the constant: $\varepsilon$ is a cross section. A cross
section still smells geometric, like a target area. The kinetic content is one
step further in, and to reach it we have to ask what the absorption event *is*.

## 2. Absorption is a transition, and transitions have rates

A molecule does not "block" light like a painted disk. It absorbs a photon by
undergoing a **transition** from its ground state $|1\rangle$ to an excited state
$|2\rangle$, and — this is the whole point — that transition happens at a *rate*.
Quantum mechanically the rate is Fermi's golden rule: a molecule bathed in
radiation makes upward transitions at a rate proportional to the squared
transition dipole matrix element $|\boldsymbol{\mu}_{12}|^2 = |\langle 2
|\hat{\boldsymbol{\mu}}| 1\rangle|^2$ and to the spectral energy density of the
field at the resonance frequency. Tie the cross section to that picture and the
disguise slips: the rate of photon absorption *per molecule* is

$$\text{(absorption rate per molecule)} = \sigma \times \Phi_{\text{photon}},$$

where $\Phi_{\text{photon}}$ is the incident photon flux (photons per area per
time). Read left to right, $\sigma$ — and therefore $\varepsilon$ — is the
*constant of proportionality between a driving field and a transition rate*. That
is exactly what a rate constant is. Beer's law is a steady-state readout of it: in
the cuvette, every molecule in the beam is being driven upward at rate
$\sigma\Phi$, and the attenuation of the beam is just the bookkeeping of photons
disappearing into those transitions. The spatial exponential of §1 is the shadow,
on the length axis, of a genuine temporal rate.

The clean way to make this quantitative is Einstein's 1917 accounting of matter in
equilibrium with radiation.[@Einstein1917]

## 3. Einstein's three coefficients

Consider the two levels $|1\rangle$ and $|2\rangle$, separated by $h\nu$, in a
bath of radiation with spectral energy density $\rho(\nu)$. Einstein wrote down
three elementary processes, each with its own rate (Figure 2):

- **Stimulated absorption**, $1\to2$, at rate $B_{12}\,\rho(\nu)$ per molecule in
  $|1\rangle$. This is what an absorption spectrum measures.
- **Stimulated emission**, $2\to1$, at rate $B_{21}\,\rho(\nu)$ per molecule in
  $|2\rangle$ — the process behind the laser.
- **Spontaneous emission**, $2\to1$, at rate $A_{21}$ per molecule in $|2\rangle$,
  *independent of the field*. This one happens in the dark.

```tikzpicture
\begin{tikzpicture}[>=Stealth]
  \draw[line width=1.4pt,black] (-1.2,0) -- (1.2,0) node[right,font=\small] {$|1\rangle$};
  \draw[line width=1.4pt,black] (-1.2,3) -- (1.2,3) node[right,font=\small] {$|2\rangle$};
  \node[left,font=\scriptsize,align=right] at (-1.3,1.5) {$h\nu$};
  % absorption (up)
  \draw[->,blue!60!black,line width=1.3pt] (-0.8,0.1) -- (-0.8,2.9);
  \node[blue!50!black,font=\scriptsize,align=center] at (-0.8,-0.55) {$B_{12}\rho$\\absorption};
  % stimulated emission (down)
  \draw[->,orange!70!black,line width=1.3pt] (0.05,2.9) -- (0.05,0.1);
  \node[orange!65!black,font=\scriptsize,align=center] at (0.05,3.55) {$B_{21}\rho$\\stim.\ emission};
  % spontaneous emission (down, wavy)
  \draw[->,red!65!black,line width=1.3pt,decorate,decoration={snake,amplitude=0.6pt,segment length=5pt,post length=4pt}] (0.9,2.9) -- (0.9,0.1);
  \node[red!60!black,font=\scriptsize,align=center] at (1.35,-0.55) {$A_{21}$\\spontaneous};
  % relation box
  \node[draw,rounded corners=2pt,fill=black!5,align=center,font=\small] at (5.6,1.5)
    {$B_{12}=B_{21}$\\[3pt]$\dfrac{A_{21}}{B_{21}}=\dfrac{8\pi h\nu^{3}}{c^{3}}$};
\end{tikzpicture}
```

*Figure 2.* Einstein's three radiative processes between two levels. Detailed
balance at thermal equilibrium — populations set by Boltzmann, $\rho(\nu)$ set by
Planck — forces the two relations on the right. The upward rate constant $B_{12}$
(what absorption measures) and the field-free downward rate $A_{21}$ (the
spontaneous-emission rate, an inverse lifetime) are not independent: fix one and
you have fixed the other.

The magic is that these three constants are not independent. Demand that a gas of
these molecules sit in thermal equilibrium with blackbody radiation — populations
following Boltzmann, $\rho(\nu)$ following Planck — and the algebra only closes if

$$B_{12} = B_{21}, \qquad\qquad \frac{A_{21}}{B_{21}} = \frac{8\pi h \nu^{3}}{c^{3}}.$$

Read the second relation slowly. On the left, $A_{21}$ is a **rate**: it has units
of inverse seconds, and its reciprocal $\tau_{\text{rad}} = 1/A_{21}$ is the
**natural radiative lifetime**, the mean time an isolated excited molecule waits
before emitting a photon with no field present. On the right sits $B_{21} = B_{12}$
— the absorption coefficient — times a bundle of fundamental constants and the
transition frequency. Nothing else. **The spontaneous-emission rate is the
absorption strength times $8\pi h\nu^3/c^3$.** Measure how strongly a molecule
absorbs and you have measured how fast it emits.

This is the crux, and it is worth stating without the hedging: $\varepsilon$ and
$1/\tau_{\text{rad}}$ are the same physics. One is dressed as an equilibrium
constant in Beer's law; the other is nakedly a rate. Einstein's relation is the
dictionary between the two costumes.

## 4. The bridge in laboratory units

To use this, we need $B_{12}$ in terms of the tabulated $\varepsilon$, and $A_{21}$
in terms of the radiative lifetime. Both are standard. The integrated intensity of
an absorption band — not the peak height, the *area* under $\varepsilon$ plotted
against wavenumber — is what is proportional to $B_{12}$, and hence to the squared
transition dipole:[@MullikenRieke1941; @Hilborn1982]

$$\int_{\text{band}} \varepsilon(\tilde{\nu})\, d\tilde{\nu}
\;\propto\; B_{12} \;\propto\; |\boldsymbol{\mu}_{12}|^{2}.$$

It is convenient to package the area as a dimensionless **oscillator strength**
$f$, normalized so that a single classical electron oscillating freely has $f=1$:

$$f = 4.32\times10^{-9} \int_{\text{band}} \varepsilon(\tilde{\nu})\,
d\tilde{\nu}
\qquad (\varepsilon\ \text{in } \mathrm{L\,mol^{-1}\,cm^{-1}},\ \tilde\nu\ \text{in } \mathrm{cm^{-1}}).$$

The same oscillator strength fixes the Einstein $A$ coefficient, and therefore the
radiative lifetime. For a non-degenerate two-level system the relation works out
to a strikingly simple form:[@Hilborn1982]

$$A_{21} = \frac{1}{\tau_{\text{rad}}}
= 0.667\;\tilde{\nu}^{2}\, f
\qquad (A_{21}\ \text{in } \mathrm{s^{-1}},\ \tilde\nu\ \text{in } \mathrm{cm^{-1}}).$$

Chain the two together and the absorption spectrum predicts the emission lifetime
outright — with no adjustable parameters, only the band area and the transition
frequency. This is the content of the Strickler–Berg relation, the tool
fluorescence spectroscopists use daily to turn a UV–vis band into an expected
lifetime.[@StricklerBerg1962] As a sanity check, a fully allowed transition ($f
\approx 1$) in the near-UV ($\tilde\nu = 40{,}000\ \mathrm{cm^{-1}}$, i.e. 250 nm)
gives

$$\tau_{\text{rad}} = \frac{1}{0.667 \times (40{,}000)^2 \times 1} \approx 0.9\ \text{ns},$$

exactly the nanosecond radiative lifetime that strongly fluorescent dyes are known
to have. The number that looked like a tabulated constant, $\varepsilon$, has
turned into a clock reading.

## 5. Weak absorbers are slow emitters — the same fact twice

Now the payoff, and it is the most useful thing in the post. Because
$\tau_{\text{rad}} \propto 1/f \propto 1/\!\int\!\varepsilon\, d\tilde\nu$, a
molecule's absorption strength and its radiative rate are *inversely* locked. A
transition cannot be both faint and fast, or both intense and slow — the transition
dipole that makes it one makes it the other. Line up representative transitions
across eight orders of magnitude in intensity and the lifetimes march in lockstep
the other way (Table 1):

| Transition type | $\tilde\nu$ / cm$^{-1}$ | $f$ | $\varepsilon_{\max}$ / M$^{-1}$cm$^{-1}$ | $\tau_{\text{rad}}$ |
|:----------------|:----------------------:|:---:|:---------------------------------------:|:-------------------:|
| Allowed $\pi\to\pi^{*}$ (strong) | 40,000 | $1$ | $5\times10^{4}$ | $\approx 0.9$ ns |
| Allowed $\pi\to\pi^{*}$ (moderate) | 35,000 | $10^{-1}$ | $1\times10^{4}$ | $\approx 12$ ns |
| $n\to\pi^{*}$ (carbonyl) | 34,000 | $10^{-4}$ | $\approx 15$ | $\approx 13\ \mu$s |
| Laporte-forbidden $d$–$d$ | 20,000 | $10^{-5}$ | $\approx 5$ | $\approx 0.4$ ms |
| Spin-forbidden (phosphor.) | 20,000 | $10^{-6}$ | $\approx 0.1$ | $\approx 4$ ms |
| Spin- *and* parity-forbidden | 20,000 | $10^{-8}$ | $\approx 10^{-3}$ | $\approx 0.4$ s |

*Table 1.* Representative literature magnitudes for $f$ and $\varepsilon_{\max}$
across transition types; $\tau_{\text{rad}}$ is computed from $f$ and $\tilde\nu$
with the two-level relation of §4. The molar absorptivity spans eight decades and
the radiative lifetime spans the same eight decades in the opposite direction —
because both are set by the one matrix element $|\boldsymbol{\mu}_{12}|^{2}$.

```tikzpicture
\begin{axis}[
    width=12cm, height=8.5cm,
    xmode=log, ymode=log,
    xlabel={molar absorptivity $\varepsilon_{\max}$ (M$^{-1}$cm$^{-1}$)},
    ylabel={radiative lifetime $\tau_{\mathrm{rad}}$ (s)},
    title={Absorption strength and emission lifetime are one axis},
    xmin=1e-4, xmax=1e6, ymin=1e-10, ymax=1e1,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
]
\addplot[only marks, mark=*, mark size=3pt, color=blue!60!black] coordinates {
    (5e4, 9.4e-10) (1e4, 1.22e-8) (15, 1.30e-5) (5, 3.75e-4) (0.1, 3.7e-3) (1e-3, 3.75e-1)
};
\addplot[dashed, red!55!black, line width=1pt, domain=1e-3:1e5, samples=2] {5e-6/x};
\node[font=\scriptsize, anchor=west] at (axis cs:5e4,9.4e-10) {allowed $\pi\pi^{*}$};
\node[font=\scriptsize, anchor=west] at (axis cs:15,1.30e-5) {$n\pi^{*}$};
\node[font=\scriptsize, anchor=west] at (axis cs:0.1,3.7e-3) {spin-forbidden};
\node[font=\scriptsize, anchor=east] at (axis cs:1e-3,3.75e-1) {phosphorescent};
\end{axis}
```

*Figure 3.* The same data as Table 1 on log–log axes. Strong and weak absorbers
fall on a single descending band (guide line $\tau_{\text{rad}} \propto
1/\varepsilon$): the brighter a molecule looks in a UV–vis spectrum, the faster its
excited state radiates. There is no separate "kinetic" measurement to be made —
the absorption spectrum already contains it.

This unifies a set of facts usually taught separately. The carbonyl $n\to\pi^{*}$
band is weak *because* the transition dipole is small (poor spatial overlap between
the in-plane oxygen lone pair and the $\pi^{*}$ cloud); the *same* small dipole is
why singlet carbonyls are comparatively slow to fluoresce. **Phosphorescence** —
the long afterglow — is emission from a spin-forbidden triplet, whose transition
dipole is tiny because it borrows intensity only weakly through spin–orbit
coupling; that tiny dipole shows up in absorption as a nearly invisible band and in
emission as a lifetime of milliseconds to seconds. The **Laporte rule** that keeps
$d$–$d$ bands of octahedral complexes faint ($\varepsilon$ of order 1–10, which is
why many transition-metal solutions are only palely colored) is, by the same
proportionality, the reason those excited states are long-lived. Faintness and
sluggishness are not two properties that happen to correlate. They are one number,
$|\boldsymbol{\mu}_{12}|^2$, reported twice.

## 6. Closing the loop back to the lab

One honest caveat keeps the argument from overreaching. $\tau_{\text{rad}}$ is the
*radiative* lifetime — the lifetime an excited molecule would have if emitting a
photon were its only way down. Real excited states also decay non-radiatively
(internal conversion, intersystem crossing, quenching), and those channels only
shorten the observed lifetime. The relationship is clean:

$$\tau_{\text{obs}} = \Phi_{\text{fl}}\,\tau_{\text{rad}},$$

where $\Phi_{\text{fl}}$ is the fluorescence quantum yield.[@LakowiczPrinciples2006]
Absorption fixes $\tau_{\text{rad}}$; a separate measurement of the observed decay
or the quantum yield supplies the rest. Far from weakening the claim, this closes a
practical loop that working photophysicists rely on: measure the absorption band
(get $\tau_{\text{rad}}$), measure the actual fluorescence decay (get
$\tau_{\text{obs}}$), and their ratio hands you the quantum yield without ever
needing an absolute-intensity standard. The static-looking spectrum was carrying
kinetic information the whole time. And the *same* transition dipole runs on into
the optical response — the refractive index and the electro-optic coefficient of a
poled material — which is the subject of
[the companion post on molar absorptivity and the Pockels effect](/posts/2026-07-03-one-matrix-element-absorptivity-and-the-pockels-effect.html).

So the next time $\varepsilon$ appears as a lookup value — a fixed number beside a
compound's name — it is worth remembering what it actually is. Beer's law presents
it as an equilibrium constant, a target area, a property. Einstein's relations
expose it as a rate: the probability per unit time, per unit driving field, that
the molecule makes the electronic jump. The transition dipole
$\langle 2|\hat{\boldsymbol{\mu}}|1\rangle$ computed in the ground-state and
excited-state posts of this series is the quantity that sets it, and it sets the
absorption and the emission with a single value. Molar absorptivity is not a
property a molecule *has*. It is a rate at which something *happens*, measured in a
cuvette that never lets on that a clock was running.

## References
