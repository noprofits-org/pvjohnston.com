---
title: "Three exact solutions and one inequality: quantum chemistry's ground floor, computed"
date: 2025-04-22
author: Peter Johnston
tags: quantum chemistry, particle in a box, harmonic oscillator, hydrogen atom, uncertainty principle, psi4
description: The particle in a box, the harmonic oscillator, and the hydrogen atom are the only systems in quantum chemistry you can solve with pen and paper — which makes them the only place you can hold your numerics fully accountable. Every figure here is computed, every number is checked against its closed form, and a psi4 basis ladder shows the one atom where Hartree–Fock is the whole answer.
---

*Rebuilt July 2026.* The original version of this post was an early draft in
lab-report form, and several of its tables reported numbers its own code never
produced. This rewrite keeps the subject and the URL, redoes every
calculation, and holds each number against the closed-form answer — the same
standard the posts that now stand on this one are held to:
[the Hartree–Fock machinery](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html)
one floor up, and
[the correlation gap, measured](/posts/2026-07-04-the-correlation-gap-in-water-measured.html)
above that.

Quantum mechanics hands chemistry exactly three systems worth solving with pen
and paper: a particle trapped between hard walls, a particle on a spring, and
one electron bound to one proton. Everything else — every molecule, every
spectrum, every reaction barrier — is approximation layered on top of what
these three teach. The box teaches that confinement quantizes energy. The
oscillator teaches that motion never stops, even at absolute zero. The
hydrogen atom teaches what an orbital actually is. And running through all
three is one inequality, Heisenberg's, which is less a fourth topic than the
grammar the other three are written in.

There is a second reason to compute these systems, and it is the working rule
of this post. Because the exact answers exist in closed form
[@GriffithsSchroeter2018], these are the only problems where a numerical
method can be
graded against truth rather than against another approximation. Every
expectation value below is computed twice — once by numerical integration on
a grid, once from the analytic formula — and the two are shown side by side.
Where a grid is too short or an integration rule too crude, the failure is
displayed rather than hidden. That habit is cheap here and priceless later,
where no closed form will be waiting.

All numerics are NumPy/SciPy on a laptop; the hydrogen-atom ladder in §4 uses
psi4 1.11 [@Smith2020Psi4]. The pattern for every expectation value is three
lines:

```python
import numpy as np
x = np.linspace(0, L, 20001)
psi = np.sqrt(2/L) * np.sin(n*np.pi*x/L)
x_mean = np.trapezoid(x * psi**2, x)      # <x> = ∫ x |ψ|² dx
```

## 1. The equation and the rule

The time-independent Schrödinger equation in one dimension,

$$
-\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} + V(x)\,\psi = E\,\psi ,
$$

is an eigenvalue problem: the potential $V(x)$ goes in, and out come the
allowed energies $E_n$ and their wavefunctions $\psi_n(x)$. The Born rule
gives $|\psi(x)|^2$ its meaning as a probability density, which obliges every
wavefunction to be normalized, $\int |\psi|^2\,dx = 1$, and makes every
measurable prediction an integral:

$$
\langle A \rangle = \int \psi^*\hat{A}\,\psi\,dx ,
\qquad
\Delta A = \sqrt{\langle A^2\rangle - \langle A\rangle^2} .
$$

Those integrals are where theory meets numerics. On a computer, $\psi$ is an
array, the integral is a quadrature rule, and the domain is finite — three
approximations before any physics happens. The three systems below are chosen
because each one changes $V(x)$ in the simplest possible way (walls, a
parabola, a Coulomb well) and because for each, every integral above has a
closed form to grade the array against.

## 2. The particle in a box: confinement quantizes

Take $V = 0$ between hard walls at $x=0$ and $x=L$, infinite outside. The
wavefunction must vanish at both walls, and that boundary condition alone does
all the work: only sine waves that fit an integer number of half-wavelengths
into the box survive,

$$
\psi_n(x) = \sqrt{\tfrac{2}{L}}\,\sin\!\Big(\tfrac{n\pi x}{L}\Big),
\qquad
E_n = \frac{n^2\pi^2\hbar^2}{2mL^2},
\qquad n = 1, 2, 3, \ldots
$$

Nothing about this is dynamical. Quantization falls out of geometry — a
continuous energy would require a wave that fails to vanish at a wall. For an
electron in a box the size of a small conjugated molecule, $L = 1$ nm, the
computed levels are $E_1 = 0.376$ eV, $E_2 = 1.504$ eV, $E_3 = 3.384$ eV:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={position $x$ (nm)},
    ylabel={energy (eV) $+$ scaled $\psi_n$},
    title={Particle in a box: the first three states},
    xmin=-0.05, xmax=1.05,
    ymin=0, ymax=4.3,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, domain=0:1, samples=200]
    {0.35*sqrt(2)*sin(deg(pi*x)) + 0.3760};
\addplot[thick, color=orange!80!black, domain=0:1, samples=200]
    {0.35*sqrt(2)*sin(deg(2*pi*x)) + 1.5041};
\addplot[thick, color=red, domain=0:1, samples=200]
    {0.35*sqrt(2)*sin(deg(3*pi*x)) + 3.3843};
\addplot[dashed, color=blue!60, domain=0:1] {0.3760};
\addplot[dashed, color=orange!60, domain=0:1] {1.5041};
\addplot[dashed, color=red!60, domain=0:1] {3.3843};
\draw[thick, black] (axis cs:0,0) -- (axis cs:0,4.3);
\draw[thick, black] (axis cs:1,0) -- (axis cs:1,4.3);
\legend{$n=1$, $n=2$, $n=3$}
\end{axis}
```

*Figure 1.* Wavefunctions of an electron in a 1 nm box, each drawn at the
height of its energy level (dashed lines; $\psi$ scaled by $0.35$ for
visibility). The state $n$ has $n-1$ interior nodes, and the energy climbs as
$n^2$ — the gaps widen going up, the opposite of the hydrogen atom's
crowding-together in §4.

The probability densities show where the electron actually is:

```tikzpicture
\begin{axis}[
    width=12cm, height=7cm,
    xlabel={position $x$ (nm)},
    ylabel={$|\psi_n(x)|^2$ (nm$^{-1}$)},
    title={Where the electron is: probability densities},
    xmin=-0.05, xmax=1.05,
    ymin=0, ymax=2.3,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, fill=blue!15, domain=0:1, samples=200]
    {2*sin(deg(pi*x))^2} \closedcycle;
\addplot[thick, color=orange!80!black, domain=0:1, samples=200]
    {2*sin(deg(2*pi*x))^2};
\addplot[thick, color=red, domain=0:1, samples=300]
    {2*sin(deg(3*pi*x))^2};
\addplot[dashed, thick, color=black!60] coordinates {(0.5,0) (0.5,2.3)};
\legend{$n=1$ (area $=1$), $n=2$, $n=3$}
\end{axis}
```

*Figure 2.* Probability densities for the same three states. Every curve
encloses unit area; the dashed line marks $\langle x\rangle = L/2$, the same
for all three by symmetry. The $n$-th state splits its probability into $n$
lobes separated by nodes where the electron is never found.

Now the accountability check. The closed forms for this system are
$\langle x\rangle = L/2$ and
$\langle x^2\rangle = L^2\big(\tfrac{1}{3} - \tfrac{1}{2n^2\pi^2}\big)$;
the numerics are trapezoidal integration on a 20 001-point grid:

| State | $E_n$ (eV) | $\Delta x$, grid (nm) | $\Delta x$, exact (nm) |
|:-----:|:----------:|:---------------------:|:----------------------:|
| $n=1$ | $0.3760$ | $0.180756$ | $0.180756$ |
| $n=2$ | $1.5041$ | $0.265835$ | $0.265835$ |
| $n=3$ | $3.3843$ | $0.278755$ | $0.278755$ |

*Table 1.* Position uncertainty of an electron in a 1 nm box: numerical
integration against the closed form, agreeing to all six digits shown. All
states sit at $\langle x\rangle = 0.5$ nm exactly.

Two physical readings of that last column. First, $\Delta x$ *grows* with
$n$ — higher states spread their probability more evenly across the box.
Second, it grows toward a ceiling: a uniform distribution on $[0, L]$ has
$\Delta x = L/\sqrt{12} \approx 0.2887$ nm, and $n=3$ is already within 4% of
it. High quantum numbers wash out the lobes and recover the classical
answer — the correspondence principle, visible in a table.

The chemistry hiding in this toy: the $n=1 \to 2$ gap for our 1 nm box is
$1.13$ eV, a photon of about $1100$ nm. Stretch or shrink the box and the gap
scales as $1/L^2$ — which is, to first crudeness, why lengthening the
conjugated backbone of a dye red-shifts its absorption
[@atkins2010physical]. One boundary condition, one visible consequence.

## 3. The harmonic oscillator: motion never stops

Replace the walls with a spring, $V(x) = \tfrac{1}{2}m\omega^2x^2$ — the
universal small-oscillation limit of any potential minimum, which is why this
model underwrites every vibrational spectrum. The solutions are Gaussians
dressed with Hermite polynomials,

$$
\psi_n(x) = N_n\,H_n(\alpha x)\,e^{-\alpha^2x^2/2},
\qquad
\alpha = \sqrt{\tfrac{m\omega}{\hbar}},
\qquad
E_n = \hbar\omega\big(n + \tfrac{1}{2}\big) .
$$

The spectrum is a ladder with even rungs $\hbar\omega$ apart, and the bottom
rung is not at zero: $E_0 = \tfrac{1}{2}\hbar\omega$. For the numbers below
the particle is an electron and $\omega = 5\times10^{14}\ \mathrm{s^{-1}}$,
giving $\hbar\omega = 0.329$ eV — about $2650\ \mathrm{cm^{-1}}$, so this
artificial oscillator happens to sit right in the vibrational infrared,
between a C–H and an O–H stretch.

```tikzpicture
\begin{axis}[
    width=12cm, height=8.5cm,
    xlabel={position $x$ (\AA)},
    ylabel={energy (eV) $+$ scaled $\psi_n$},
    title={Harmonic oscillator: four states in the well},
    xmin=-16, xmax=16,
    ymin=0, ymax=1.75,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, domain=-16:16, samples=300]
    {0.8*0.34242*exp(-0.5*(0.20782*x)^2) + 0.1646};
\addplot[thick, color=orange!80!black, domain=-16:16, samples=300]
    {0.8*0.24213*2*(0.20782*x)*exp(-0.5*(0.20782*x)^2) + 0.4937};
\addplot[thick, color=red, domain=-16:16, samples=300]
    {0.8*0.12107*(4*(0.20782*x)^2 - 2)*exp(-0.5*(0.20782*x)^2) + 0.8228};
\addplot[thick, color=violet, domain=-16:16, samples=300]
    {0.8*0.049424*(8*(0.20782*x)^3 - 12*(0.20782*x))*exp(-0.5*(0.20782*x)^2) + 1.1519};
\addplot[dashed, thick, color=black, domain=-16:16, samples=300] {0.0071072*x^2};
\legend{$n=0$, $n=1$, $n=2$, $n=3$}
\end{axis}
```

*Figure 3.* Harmonic-oscillator wavefunctions (scaled) drawn at their energy
levels inside the parabolic potential (dashed). The ground state is a pure
Gaussian sitting $\tfrac{1}{2}\hbar\omega = 0.165$ eV above the bottom of the
well — the zero-point energy. Note the tails leaking past the classical
turning points, where the potential exceeds the state's total energy.

That non-negotiable $0.165$ eV floor is not a technicality. Zero-point energy
is why helium never freezes at atmospheric pressure, and its dependence on
mass ($\omega \propto 1/\sqrt{\mu}$) is why deuteration slows C–H bond
cleavage — the kinetic isotope effect is zero-point arithmetic.

**Where the old draft went wrong — and how to catch it.** The previous
version of this post tabulated $\Delta x\cdot\Delta p = \hbar/2$ for *every*
oscillator state and offered it as a computational verification of the
uncertainty principle. It was nothing of the sort: the code had computed
$\Delta p := \hbar/(2\Delta x)$ — momentum uncertainty *defined* by the
relation it claimed to verify. The correct procedure computes
$\langle p^2\rangle$ independently from the wavefunction's curvature,
$\langle p^2 \rangle = \hbar^2\!\int |d\psi/dx|^2\,dx$, and the exact answer
for eigenstates is

$$
\Delta x\,\Delta p = \big(n + \tfrac{1}{2}\big)\hbar ,
$$

which touches the Heisenberg floor only at $n=0$. Both computed columns now
match their closed forms:

| State | $\Delta x$ (Å) | $\Delta p$ (kg m s$^{-1}$) | $\Delta x\,\Delta p / \hbar$, grid | exact |
|:-----:|:--------------:|:--------------------------:|:----------------------------------:|:-----:|
| $n=0$ | $3.4025$ | $1.5497\times10^{-25}$ | $0.500000$ | $0.5$ |
| $n=1$ | $5.8932$ | $2.6842\times10^{-25}$ | $1.500000$ | $1.5$ |
| $n=2$ | $7.6081$ | $3.4653\times10^{-25}$ | $2.500000$ | $2.5$ |
| $n=3$ | $9.0021$ | $4.1002\times10^{-25}$ | $3.500000$ | $3.5$ |

*Table 2.* Position and momentum uncertainties for the oscillator, with
$\langle p^2\rangle$ computed from the numerical derivative of $\psi$ on a
40 001-point grid. The product climbs the ladder as $(n+\tfrac{1}{2})\hbar$;
only the ground state is a minimum-uncertainty state. Both $\Delta x$ and
$\Delta p$ match $\sqrt{(n+\tfrac{1}{2})\hbar/m\omega}$ and
$\sqrt{(n+\tfrac{1}{2})\hbar m\omega}$ to the digits shown.

The lesson generalizes beyond this bug. A verification that assumes its
conclusion will pass with flying colors on any input, which is exactly what
makes it worse than no verification at all. The fix was not better physics —
it was refusing to let one uncertainty be derived from the other.

Why is only $n=0$ minimum-uncertainty? Because the Gaussian is the unique
shape that saturates Heisenberg's inequality, and the oscillator's ground
state *is* a Gaussian — a fact §5 returns to from the other direction.

## 4. The hydrogen atom: the one atom solved exactly

Swap the parabola for the Coulomb well, $V(r) = -e^2/4\pi\epsilon_0 r$, and
the problem becomes three-dimensional and real: this is an actual atom, and
the last one for which the Schrödinger equation surrenders a closed form. The
ground state is

$$
\psi_{1s}(r) = \frac{1}{\sqrt{\pi a_0^3}}\,e^{-r/a_0},
\qquad
E_1 = -\tfrac{1}{2}\,E_h = -13.606\ \mathrm{eV},
$$

with $a_0 = 0.5292$ Å the Bohr radius. The density $|\psi_{1s}|^2$ peaks at
the nucleus, but the electron is not most likely to be *found* at the
nucleus: the probability of a radius $r$ carries the volume of the shell at
that radius, $P(r) = 4\pi r^2|\psi_{1s}|^2$, and the shell volume vanishes at
$r=0$. The competition between the growing $r^2$ and the dying exponential
puts the peak exactly at $a_0$:

```tikzpicture
\begin{axis}[
    width=12cm, height=7.5cm,
    xlabel={radius $r$ (\AA)},
    ylabel={$P(r)$ (\AA$^{-1}$)},
    title={Hydrogen 1s: radial probability density},
    xmin=0, xmax=4,
    ymin=0, ymax=1.15,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, fill=blue!12, domain=0:4, samples=300]
    {26.993*x^2*exp(-3.77945*x)} \closedcycle;
\addplot[dashed, thick, color=red] coordinates {(0.52918,0) (0.52918,1.15)};
\addplot[dashed, thick, color=black!60] coordinates {(0.79377,0) (0.79377,1.15)};
\legend{$P(r)$, most probable $r = a_0$, $\langle r\rangle = \tfrac{3}{2}a_0$}
\end{axis}
```

*Figure 4.* The radial probability density of the hydrogen 1s state. The most
probable radius is exactly the Bohr radius (red dashed), but the *mean*
radius sits at $1.5\,a_0 = 0.794$ Å (grey dashed) — the long exponential tail
drags the average outward. Two different questions, two different answers,
one distribution.

**Numerics held accountable.** The closed forms are
$\langle r\rangle = \tfrac{3}{2}a_0 = 0.7938$ Å and
$\langle r^2\rangle = 3a_0^2 = 0.8401$ Å². Here is what a grid does to them,
from careless to careful:

| Grid | Rule | $\int P\,dr$ | $\langle r\rangle$ (Å) | $\langle r^2\rangle$ (Å²) |
|:-----|:----:|:------------:|:----------------------:|:-------------------------:|
| $r_{\max}=5a_0$, 100 pts | sum | $0.9973$ | $0.7880$ | $0.8185$ |
| $r_{\max}=5a_0$, 100 pts | trapezoid | $0.9972$ | $0.7877$ | $0.8178$ |
| $r_{\max}=20a_0$, 100 pts | trapezoid | $0.9999$ | $0.7939$ | $0.8402$ |
| $r_{\max}=20a_0$, 1000 pts | trapezoid | $1.0000$ | $0.7938$ | $0.8401$ |
| exact | — | $1$ | $0.7938$ | $0.8401$ |

*Table 3.* Grid convergence of the 1s radial moments. Truncating at $5a_0$
quietly discards 0.3% of the electron and 2.7% of $\langle r^2\rangle$ — the
$r^2$ weight amplifies exactly the tail the truncation removed. The
integration *rule* matters far less than the *domain*: the worst error here
is a boundary decision, not a quadrature decision. (Renormalizing a truncated
grid, as the old draft did, hides the missing norm but not the biased
moments.)

Now point research-grade machinery at the same atom. Psi4 solving hydrogen
with unrestricted Hartree–Fock is a deliberately overqualified tool — and
that is the point, because for a *one-electron* system Hartree–Fock's
mean-field approximation is no approximation at all. There is no second
electron to average over: the correlation energy is identically zero, and the
only thing separating the computed energy from the exact
$-\tfrac{1}{2}\,E_h$ is the finite basis set. Hydrogen is the one atom where
the basis-set error is the *whole* error, in its purest laboratory form:

| Basis | Functions | $E$ ($E_h$) | Error (m$E_h$) |
|:------|:---------:|:-----------:|:--------------:|
| STO-3G | 1 | $-0.466582$ | $33.42$ |
| 6-31G | 2 | $-0.498233$ | $1.767$ |
| cc-pVDZ | 5 | $-0.499278$ | $0.722$ |
| cc-pVTZ | 14 | $-0.499810$ | $0.190$ |
| cc-pVQZ | 30 | $-0.499946$ | $0.054$ |
| cc-pV5Z | 55 | $-0.499995$ | $0.0055$ |
| exact | $\infty$ | $-0.500000$ | $0$ |

*Table 4.* UHF/psi4 energies for the hydrogen atom up the basis ladder
[@Dunning1989], converging monotonically — as the variational principle
guarantees — toward the exact nonrelativistic, clamped-nucleus value of
$-0.5\,E_h$.

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={basis functions},
    ylabel={error vs.\ exact (m$E_h$)},
    title={Hydrogen: the whole error is the basis},
    xmode=log, ymode=log,
    log ticks with fixed point,
    xtick={1,2,5,14,30,55},
    xticklabels={1,2,5,14,30,55},
    xmin=0.8, xmax=70,
    ymin=0.003, ymax=60,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, mark=*, mark size=2.2pt, color=blue] coordinates {
    (1,33.4182) (2,1.7671) (5,0.7216) (14,0.1902) (30,0.0544) (55,0.0055)
};
\node[anchor=west, font=\small] at (axis cs:1.1,33.4182) {STO-3G};
\node[anchor=west, font=\small] at (axis cs:2.2,1.7671) {6-31G};
\node[anchor=west, font=\small] at (axis cs:5.5,0.7216) {cc-pVDZ};
\node[anchor=west, font=\small] at (axis cs:15.4,0.1902) {cc-pVTZ};
\node[anchor=west, font=\small] at (axis cs:33,0.0544) {cc-pVQZ};
\node[anchor=south, font=\small] at (axis cs:55,0.0070) {cc-pV5Z};
\end{axis}
```

*Figure 5.* Basis-set error of the hydrogen-atom UHF energy against basis
size, both axes logarithmic. Four orders of magnitude of error retired in
six rungs. With no correlation energy in the problem, this entire descent is
the one-electron basis doing its only job: shaping a single orbital.

Three readings of this ladder. **First, the minimal basis misses by
chemistry-sized amounts.** STO-3G's error is $0.91$ eV — about $88$ kJ/mol,
bond-strength territory, on the simplest system in existence. **Second, most
of a big basis is spectator here.** cc-pV5Z carries 55 functions, but a
$^2S$ atom can only use the $s$-type ones — the $p$, $d$, $f$, $g$
polarization functions cannot mix into a spherically symmetric state, and
the ladder narrows only because each rung also deepens the $s$ set (2, 3, 4,
then 5 $s$-functions from cc-pVDZ to cc-pV5Z). **Third, the last few
micro-hartrees are the cusp.** The exact 1s orbital has a kink at the
nucleus — $e^{-r/a_0}$ comes to a point at $r=0$ — while every Gaussian is
smooth there, so a finite sum of Gaussians can chase the cusp but never
land it [@HelgakerJorgensenOlsen2000]. Readers of
[the correlation-gap post](/posts/2026-07-04-the-correlation-gap-in-water-measured.html)
have met this enemy before: the electron–electron cusp of the Coulomb hole
is what makes correlation energies crawl toward the basis limit. Same
mathematical villain, different pair of particles.

That is also the bridge out of this post. Add one more electron — helium —
and the closed forms stop. Hartree–Fock becomes an approximation with a gap
below it, and everything in the two posts upstairs becomes necessary. The
hydrogen atom is where "orbital" is a fact; everywhere else it is a very
good idea.

## 5. The inequality: localization has a price

The uncertainty principle,

$$
\Delta x \cdot \Delta p \geq \frac{\hbar}{2},
$$

has been present in every table so far — the box states, the oscillator
ladder, the hydrogen moments all obey it with room to spare. The clean way
to see it *saturated* is the Gaussian wavepacket
$\psi(x) \propto e^{-x^2/4\sigma^2}$, for which the computed uncertainties
(momentum again via the derivative, $\hbar = 1$) come out $\Delta x = \sigma$
and $\Delta p = 1/2\sigma$ exactly — product $\tfrac{1}{2}\hbar$, for every
$\sigma$ on the grid, to six digits. Narrow the packet and its momentum
spread widens in exact compensation:

```tikzpicture
\begin{axis}[
    width=12cm, height=7.5cm,
    xlabel={$x$ or $p$ ($\hbar=1$ units)},
    ylabel={probability density},
    title={The trade: narrow in position, wide in momentum},
    xmin=-6, xmax=6,
    ymin=0, ymax=1.75,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, domain=-6:6, samples=200]
    {0.7979*exp(-2*x^2)};
\addplot[thick, dashed, color=blue, domain=-6:6, samples=200]
    {0.3989*exp(-0.5*x^2)};
\addplot[thick, color=red, domain=-6:6, samples=200]
    {0.19947*exp(-0.125*x^2)};
\addplot[thick, dashed, color=red, domain=-6:6, samples=200]
    {1.5958*exp(-8*x^2)};
\legend{$|\psi(x)|^2$\, $\sigma=0.5$, $|\phi(p)|^2$\, $\sigma=0.5$,
        $|\psi(x)|^2$\, $\sigma=2$, $|\phi(p)|^2$\, $\sigma=2$}
\end{axis}
```

*Figure 6.* Two Gaussian wavepackets in position space (solid) and their
momentum-space densities (dashed), same color per packet. The narrow position
packet (blue) owns the broad momentum distribution; the wide one (red) owns
the sharp one. The product $\Delta x\,\Delta p$ is $\hbar/2$ for both — the
inequality's floor, reachable only by this shape.

Where does the trade come from? Not from measurement disturbing anything —
from Fourier analysis. A wavefunction sharply peaked in position must be
built by superposing many momentum components; the interference that
localizes it *is* the momentum spread. Averaging plane waves whose
wavenumbers span a width $2s$ around a carrier $k_0$ gives
$\overline{\cos kx} = \cos(k_0x)\,\mathrm{sinc}(sx)$ — a wavetrain confined
to an envelope of width $\sim 1/s$:

```tikzpicture
\begin{axis}[
    width=12cm, height=7.5cm,
    xlabel={position $x$},
    ylabel={amplitude (curves offset)},
    title={Localization is superposition},
    xmin=-20, xmax=20,
    ymin=-4, ymax=1.6,
    ytick=\empty,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=south east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, domain=-20:20, samples=600]
    {cos(deg(5*x))*sin(deg(0.3*(x+0.001)))/(0.3*(x+0.001))};
\addplot[thick, color=red, domain=-20:20, samples=600]
    {cos(deg(5*x))*sin(deg(1.5*(x+0.001)))/(1.5*(x+0.001)) - 2.5};
\legend{narrow $k$-spread ($s=0.3$), wide $k$-spread ($s=1.5$)}
\end{axis}
```

*Figure 7.* Superpositions of plane waves with the same carrier wavenumber
but different spreads $s$ (curves offset vertically). The wide spread of
momentum components (red) buys a tightly localized packet; the narrow spread
(blue) leaves the wave extended. It is the *spread* of contributing
wavenumbers that localizes, not their count — the packet width scales as
$1/s$, Fourier's version of $\Delta x\,\Delta p \sim \hbar$.

And this inequality is why the hydrogen atom of §4 exists at all. Classically
the electron should spiral into the nucleus; quantum mechanically, squeezing
it into a region $\sigma$ costs kinetic energy
$\sim \hbar^2/2m\sigma^2$ while the Coulomb well only pays back
$\sim e^2/4\pi\epsilon_0\sigma$. Minimizing the sum lands, up to a factor of
order one, on $\sigma \approx a_0$ and $E \approx -\tfrac{1}{2}E_h$ — the
Bohr radius as the equilibrium point of the uncertainty trade. The atom is a
standoff between Heisenberg and Coulomb, and the 1s orbital is the treaty.

## 6. What the ground floor carries

Each toy in this post is a load-bearing column under the rest of the series.
The box's boundary-condition quantization and node-counting reappear whenever
a wavefunction is confined — and its sine functions are the simplest example
of a *basis* in which harder problems get expanded. The oscillator's ladder
is the working model for every vibrational spectrum and every zero-point
correction, and its ground state introduced the Gaussian that basis-set
builders would later adopt wholesale. The hydrogen 1s is the template for
every atomic orbital in every basis set — Slater functions imitate its cusp,
Gaussians approximate it in bulk, and the residual few micro-hartrees in
Table 4 are the honest price of that convenience. The inequality is the
reason atoms have size.

The rule of the post carries further than the physics. Every number here had
a closed form waiting to grade it, and the grading caught real errors — a
circular momentum "verification," a truncated grid renormalized into false
agreement. One floor up, in
[the Hartree–Fock machinery](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html),
the exact answers stop coming, and the habits formed where truth was
available — convergence tables, independent cross-checks, suspicion of
too-perfect agreement — are the only part of this post that survives the
climb.

## References
