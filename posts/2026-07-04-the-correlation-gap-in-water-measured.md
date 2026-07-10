---
title: "How much does correlation really cost? The correlation gap in water, measured"
date: 2026-07-04
author: Peter Johnston
tags: quantum chemistry, Hartree-Fock, electron correlation, basis sets, coupled cluster, psi4
description: The Hartree–Fock post drew its correlation-gap figure schematically. This post runs the actual calculations — RHF marched up a basis-set ladder to its limit, MP2 and CCSD(T) below it — and reports what electron correlation costs, in hartrees, for one bent molecule of water.
---

The [previous post on Hartree–Fock](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html)
ended on a picture it never computed. Figure 3 of that post showed three
horizontal lines — a finite-basis Hartree–Fock energy, the Hartree–Fock
*limit* below it, and the exact energy below that — and named the last gap the
**correlation energy**. The lines were schematic. The Koopmans comparison in
its §6 was likewise built from "representative near-Hartree–Fock" orbital
energies, honest about being borrowed. That was the right choice for a post
about *machinery*; but the machinery exists, it runs on a laptop, and water is
small enough that nothing needs to be schematic. So this post runs it.

Everything below was computed with psi4 1.11 [@Smith2020Psi4] on one water
molecule at the experimental equilibrium geometry used throughout this series
— $r_{\mathrm{OH}} = 0.9584$ Å, $\angle_{\mathrm{HOH}} = 104.45°$ — held fixed
in every calculation, so that every energy difference in this post is a
*method* difference, never a geometry difference. All electrons are
correlated (no frozen core). The entire input is short enough to show:

```python
import psi4
water = psi4.geometry("""
0 1
O
H 1 0.9584
H 1 0.9584 2 104.45
""")
for basis in ["sto-3g", "6-31g", "6-31g**",
              "cc-pvdz", "cc-pvtz", "cc-pvqz", "cc-pv5z"]:
    psi4.set_options({"basis": basis})
    print(basis, psi4.energy("scf"))
# and, at the cc-pVXZ bases: psi4.energy("mp2"), psi4.energy("ccsd(t)")
```

## 1. The loop, actually looping

Before the limits and the gaps, it is worth watching the self-consistent-field
cycle of the previous post's Figure 1 actually turn. Starting from psi4's
default superposition-of-atomic-densities guess, RHF/cc-pVDZ converges as
follows — energy change and DIIS error per iteration, on a log scale:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={SCF iteration},
    ylabel={magnitude (hartree)},
    title={One SCF run: water, RHF/cc-pVDZ},
    ymode=log,
    ymin=1e-14, ymax=10,
    xmin=0.5, xmax=12.5,
    xtick={1,2,...,12},
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, mark=*, mark size=2pt, color=blue] coordinates {
    (1,4.4395e-1) (2,5.3286e-2) (3,1.8903e-2) (4,5.7544e-4)
    (5,1.9540e-5) (6,9.2173e-7) (7,2.5346e-8) (8,4.9832e-10)
    (9,3.1690e-11) (10,8.5265e-13) (11,8.5265e-14) (12,1.4211e-13)
};
\addplot[thick, mark=square*, mark size=2pt, color=red] coordinates {
    (1,3.0311e-2) (2,1.7330e-2) (3,2.3039e-3) (4,3.7059e-4)
    (5,6.7227e-5) (6,1.0524e-5) (7,1.4532e-6) (8,3.3990e-7)
    (9,5.7763e-8) (10,4.7617e-9) (11,8.2832e-10) (12,4.9946e-11)
};
\legend{$|\Delta E|$, DIIS error}
\end{axis}
```

*Figure 1.* The SCF loop converging: the energy change per iteration and the
DIIS error both fall roughly geometrically, crossing ten orders of magnitude
in about a dozen turns of the cycle. The $|\Delta E|$ series bottoms out near
$10^{-13}$ hartree — that floor is double-precision arithmetic, not the
physics.

Two things in this trace deserve a sentence each. First, the *rate*: each
iteration multiplies the error by roughly a constant factor, which is what
"the field and the orbitals negotiating toward agreement" looks like
numerically. This speed is not free — the naive fixed-point iteration
described in the previous post can oscillate or converge painfully; practical
codes accelerate it by extrapolating from the history of previous Fock
matrices, Pulay's **DIIS** [@Pulay1980], and that is the quantity plotted in
red. Second, the *floor*: by iteration 11 the energy change hits
$10^{-13}\,E_h$ and stops improving, because we have reached the resolution of
floating-point arithmetic. Every digit this post quotes below sits far above
that floor.

Converged, the run reports $E_{\mathrm{RHF}} = -76.026741\,E_h$ in this basis.
Is that number any good? That depends entirely on the basis — which is the
next section.

## 2. Climbing the basis ladder

The Roothaan–Hall construction expands the unknown orbitals in a finite basis
set, so every Hartree–Fock energy carries a basis-set error on top of the
mean-field approximation. The variational principle promises that *enlarging*
the basis can only lower the energy, and Dunning's correlation-consistent
family — cc-pVDZ, cc-pVTZ, cc-pVQZ, cc-pV5Z [@Dunning1989] — is engineered to
approach the limit systematically, each rung roughly doubling the number of
functions. Here is the whole ladder, from the minimal STO-3G up:

| Basis | Functions | $E_{\mathrm{RHF}}$ ($E_h$) | Above the HF limit (m$E_h$) |
|:------|:---------:|:--------------------------:|:---------------------------:|
| STO-3G   | 7   | $-74.963120$ | $1104.43$ |
| 6-31G    | 13  | $-75.983953$ | $83.60$   |
| 6-31G**  | 25  | $-76.023088$ | $44.46$   |
| cc-pVDZ  | 24  | $-76.026741$ | $40.81$   |
| cc-pVTZ  | 58  | $-76.057082$ | $10.47$   |
| cc-pVQZ  | 115 | $-76.064744$ | $2.80$    |
| cc-pV5Z  | 201 | $-76.066999$ | $0.55$    |
| CBS (Q5 extrapolation) | — | $-76.067548$ | $0$ |

*Table 1.* RHF energies for water across a basis ladder, all at the same fixed
geometry. The last row is the two-point exponential extrapolation of the
cc-pVQZ and cc-pV5Z energies [@Halkier1999], our estimate of the
Hartree–Fock basis-set limit; the previous post's Figure 3 called this line
"$E_{\mathrm{HF}}$ (basis-set limit)" and now it has a value.

The descent is strictly monotonic, exactly as the variational principle
requires — no basis ever overshoots. Three details are worth pulling out.

**The minimal basis is catastrophically far away.** STO-3G sits $1.10\,E_h$
— thirty electron-volts — above the Hartree–Fock limit. That error is *three
times larger* than the entire correlation energy we are about to measure. The
practical moral is old but bears repeating: there is no point paying for a
correlated method inside a minimal basis; the basis error buries the physics
you bought.

**Design beats size.** cc-pVDZ, with 24 functions, lands *below* 6-31G**,
with 25. Where the functions sit matters more than how many there are — the
correlation-consistent exponents were variationally optimized for exactly
this job.

**The returns diminish geometrically.** Each rung of the Dunning ladder cuts
the remaining error by roughly a factor of four while roughly doubling the
basis (and integral cost grows steeply with basis size — formally as the
fourth power of its size for the raw two-electron integral count). From
cc-pVQZ to cc-pV5Z you nearly double the basis to gain $2.2$ m$E_h$. This
near-geometric decay is why a two-point *exponential* extrapolation is the
standard estimate of the Hartree–Fock limit [@Halkier1999], and it is a
luxury specific to the mean field — as §3 shows, the correlation energy is
not nearly so obliging.

## 3. The gap, measured

Now the payoff. At each of the cc-pVDZ, cc-pVTZ, and cc-pVQZ bases we run
CCSD(T) — coupled cluster with singles, doubles, and perturbative triples,
the previous post's "gold standard" [@Raghavachari1989] — alongside RHF in
the *same* basis. Figure 2 is the previous post's schematic Figure 3, redrawn
with every line at its computed value:

```tikzpicture
\begin{axis}[
    width=12cm, height=9cm,
    xlabel={basis functions},
    ylabel={energy (hartree)},
    title={The correlation gap in water, with real numbers},
    xmode=log,
    log ticks with fixed point,
    xtick={7,13,24,58,115,201},
    xticklabels={7,13,24,58,115,201},
    xmin=6, xmax=260,
    ymin=-76.6, ymax=-74.85,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, mark=*, mark size=2.2pt, color=blue] coordinates {
    (7,-74.963120) (13,-75.983953) (24,-76.026741)
    (58,-76.057082) (115,-76.064744) (201,-76.066999)
};
\addplot[thick, mark=square*, mark size=2.2pt, color=red] coordinates {
    (24,-76.243177) (58,-76.345768) (115,-76.391079)
};
\addplot[dashed, thick, color=blue!60!black] coordinates {
    (6,-76.067548) (260,-76.067548)
};
\addplot[dashed, thick, color=red!60!black] coordinates {
    (6,-76.421357) (260,-76.421357)
};
\legend{RHF, CCSD(T), RHF limit (CBS), CCSD(T)/CBS estimate}
\draw[<->, thick, black!75] (axis cs:170,-76.067548) -- (axis cs:170,-76.421357);
\node[fill=white, font=\small, inner sep=1.5pt] at (axis cs:170,-76.244) {$E_{\mathrm{corr}}$};
\end{axis}
```

*Figure 2.* RHF (blue) and CCSD(T) (red) for water across the basis ladder,
each approaching its own limit (dashed lines). The vertical gap between the
two limits is the correlation energy: $E_{\mathrm{corr}} \approx
-0.354\,E_h$. Note that the RHF curve is visually flat past 58 functions
while the CCSD(T) curve is still falling — the two series converge at
genuinely different rates.

The red dashed line is built exactly the way the previous post's aside
prescribed — both energies taken in the same one-particle basis, then each
piece pushed to its own limit. The correlation energy at each rung, with the
extrapolated row [@Halkier1998] at the bottom:

| Basis | $E_{\mathrm{corr}}^{\mathrm{CCSD(T)}}$ (m$E_h$) | Fraction of CBS value |
|:------|:---------------------------:|:----------------:|
| cc-pVDZ | $-216.44$ | 61% |
| cc-pVTZ | $-288.69$ | 82% |
| cc-pVQZ | $-326.33$ | 92% |
| CBS (TQ extrapolation) | $-353.81$ | 100% |

*Table 2.* The correlation energy of water converging with basis. The CBS row
uses the two-point $X^{-3}$ extrapolation of the cc-pVTZ and cc-pVQZ values
[@Halkier1998]; added to the Hartree–Fock limit of Table 1 it gives our best
total, $-76.4214\,E_h$.

Look at the mismatch between the two convergence stories, because it is the
most practically important fact in this post. At cc-pVQZ, Hartree–Fock is
within $2.8$ m$E_h$ of its limit — better than 99.99% converged. The
*correlation energy in the same basis* is only 92% converged, still $27$
m$E_h$ short. Plotting both errors against the cardinal number $X$ of the
basis makes the difference in kind visible:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={cardinal number $X$ of cc-pV$X$Z},
    ylabel={error vs.\ limit (m$E_h$)},
    title={Mean field converges exponentially; correlation crawls as $X^{-3}$},
    ymode=log,
    ymin=0.2, ymax=400,
    xmin=1.6, xmax=5.4,
    xtick={2,3,4,5},
    xticklabels={DZ,TZ,QZ,5Z},
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=south west,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, mark=*, mark size=2.2pt, color=blue] coordinates {
    (2,40.81) (3,10.47) (4,2.80) (5,0.55)
};
\addplot[thick, mark=square*, mark size=2.2pt, color=red] coordinates {
    (2,137.37) (3,65.12) (4,27.47)
};
\legend{RHF error, $E_{\mathrm{corr}}$ error (CCSD(T))}
\end{axis}
```

*Figure 3.* Basis-set errors of the RHF energy (blue) and of the CCSD(T)
correlation energy (red) for water, against the cc-pV$X$Z cardinal number, on
a log scale. The RHF error falls on a near-straight line — exponential
convergence — while the correlation error visibly flattens, decaying only as
$X^{-3}$.

The physical reason is worth stating. Hartree–Fock only needs the basis to
describe the *shape of the orbitals*, a smooth one-electron job that Gaussian
basis sets do superbly. The correlation energy needs the basis to describe
the **Coulomb hole** [@HelgakerJorgensenOlsen2000] — the little kink in the
wavefunction where two electrons meet, a genuine cusp at $r_{12}=0$.
Building a cusp out of smooth products of one-electron Gaussians is brutally
inefficient, and the $X^{-3}$ decay of the error is the price, which is why
correlated calculations lean so heavily on extrapolation.

One honesty note on the anchor. Our extrapolated $E_{\mathrm{corr}} =
-0.3538\,E_h$ is itself a little short of the true correlation energy of
water, which benchmark studies [@HelgakerJorgensenOlsen2000] place near
$-0.37\,E_h$. Most of the shortfall is deliberate economy:
we correlated all ten electrons but used valence-optimized cc-pV$X$Z sets,
which lack the tight functions needed to describe correlation of the oxygen
$1s$ core (that job wants the core-valence cc-pCV$X$Z sets), and CCSD(T)
itself omits a small residue beyond perturbative triples. Neither omission
changes any conclusion here; both are exactly the kind of stated,
budgeted approximation the previous post argued quantum chemistry runs on.

## 4. MP2's discount rate

The previous post introduced second-order Møller–Plesset perturbation theory
[@MollerPlesset1934] through its formula: a sum over double excitations,
built entirely from quantities Hartree–Fock already computed. The formula
promised cheap correlation. Here is how much of it MP2 actually delivers,
next to CCSD and CCSD(T) in the same bases:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    ybar,
    bar width=11pt,
    ylabel={$-E_{\mathrm{corr}}$ (m$E_h$)},
    title={Correlation energy recovered: MP2 vs.\ CCSD vs.\ CCSD(T)},
    xmin=0.35, xmax=3.65,
    xtick={1,2,3},
    xticklabels={cc-pVDZ,cc-pVTZ,cc-pVQZ},
    ymin=0, ymax=390,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north west,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    nodes near coords,
    every node near coord/.append style={font=\scriptsize, /pgf/number format/.cd, fixed, precision=0}
]
\addplot[fill=blue!55] coordinates {(1,204.05) (2,275.16) (3,313.37)};
\addplot[fill=orange!60] coordinates {(1,213.37) (2,280.91) (3,317.08)};
\addplot[fill=red!55] coordinates {(1,216.44) (2,288.69) (3,326.33)};
\legend{MP2, CCSD, CCSD(T)}
\end{axis}
```

*Figure 4.* Correlation energy of water recovered by MP2, CCSD, and CCSD(T)
in three bases (magnitudes; larger is more correlation). MP2 captures the
bulk; the coupled-cluster hierarchy adds the rest in two visible steps.

| Basis | MP2 | CCSD | CCSD(T) | MP2 / CCSD(T) |
|:------|:---:|:----:|:-------:|:-------------:|
| cc-pVDZ | $-204.05$ | $-213.37$ | $-216.44$ | 94.3% |
| cc-pVTZ | $-275.16$ | $-280.91$ | $-288.69$ | 95.3% |
| cc-pVQZ | $-313.37$ | $-317.08$ | $-326.33$ | 96.0% |

*Table 3.* Correlation energies in m$E_h$. MP2's fraction of the CCSD(T)
answer creeps *upward* with basis — the two methods do not approach the
basis-set limit in lockstep.

The headline: for water, a molecule the single determinant describes well,
the cheapest correlated method in the toolbox recovers **about 95% of the
correlation energy**. That is a remarkable return on a formula you can write
in one line. But hold the remaining 5% up against chemical scales before
celebrating: at cc-pVQZ the MP2-to-CCSD(T) difference is $13.0$ m$E_h$, which
is $34$ kJ/mol — several times larger than "chemical accuracy" (the customary
4 kJ/mol), and enough to misplace a reaction barrier entirely. Even the
perturbative-triples correction alone — the difference between CCSD and
CCSD(T), the parenthesis in the name — is worth $9.3$ m$E_h$ ($24$ kJ/mol)
here. The percentages flatter; the leftovers are the size of the chemistry.

## 5. Koopmans, with computed numbers

The previous post's Table 1 compared Koopmans estimates against water's
photoelectron spectrum using representative orbital energies. Running
RHF/cc-pVTZ and reading the converged eigenvalues per irrep gives the real
thing (the four valence orbitals below, plus the oxygen core):

| Orbital | $-\varepsilon_i$, RHF/cc-pVTZ | Experiment | Error |
|:-------:|:----------------------------:|:----------:|:-----:|
| $1b_1$ | $13.73$ eV | $12.62$ eV [@Turner1970] | $+1.1$ |
| $3a_1$ | $15.72$ eV | $14.74$ eV [@Turner1970] | $+1.0$ |
| $1b_2$ | $19.29$ eV | $18.51$ eV [@Turner1970] | $+0.8$ |
| $2a_1$ | $36.60$ eV | $\approx 32.2$ eV [@Turner1970] | $+4.4$ |
| $1a_1$ (O $1s$) | $559.3$ eV | $\approx 539.9$ eV [@Siegbahn1969] | $+19$ |

*Table 4.* Koopmans ionization-energy estimates from computed RHF/cc-pVTZ
orbital energies, against experimental vertical ionization energies (valence:
UV photoelectron spectroscopy; core: X-ray photoemission). The computed
symmetry labels come straight out of the calculation — psi4 assigns the HOMO
to $b_1$, the out-of-plane lone pair, with no hand-placement anywhere.

The pattern the previous post argued from representative numbers survives
contact with computed ones, and sharpens. Outer valence: Koopmans lands about
one electron-volt high, uniformly — relaxation and correlation nearly
cancelling. The deep $2a_1$: the error blows out to $+4.4$ eV as the
frozen-orbital picture starts to fail. And the new row at the bottom is the
trend followed to its extreme: for the oxygen $1s$ core orbital, Koopmans
misses by *nineteen electron-volts*, because ejecting a core electron
triggers a massive relaxation of every other electron toward the suddenly
unshielded nucleus — precisely what frozen orbitals forbid. One approximation,
one dial (how deep the hole), and the error runs smoothly from one volt to
twenty.

## 6. What correlation costs

Collect the totals. For one water molecule at its equilibrium geometry, our
best numbers in this post are

$$
E_{\mathrm{HF}}^{\mathrm{limit}} = -76.0675\,E_h,
\qquad
E_{\mathrm{corr}} \approx -0.354\,E_h,
\qquad
E_{\mathrm{best}} \approx -76.421\,E_h .
$$

As a fraction of the total energy, correlation is **0.46%** — the previous
post's "typically under 1%" made concrete. And here is the comparison that
turns that percentage from reassuring to alarming: $0.354\,E_h$ is about
$930$ kJ/mol, which is *as large as water's entire atomization energy* — the
energy of both O–H bonds combined, roughly $970$ kJ/mol
[@HelgakerJorgensenOlsen2000]. The part of the energy that Hartree–Fock
cannot see, for this well-behaved closed-shell molecule at equilibrium, is
the size of all its chemical bonds put together. "99% of the energy" and
"none of the chemistry" can be the same statement.

That is the quantitative content of the previous post's closing argument, and
it sets the buy-in prices for everything downstream. Mean-field theory:
converges fast with basis, costs little, misses a bond's worth of energy.
MP2: one line of theory, ~95% of the missing piece, but the residue still
dwarfs chemical accuracy. CCSD(T) plus extrapolation: the gold standard, and
even then the last few m$E_h$ — core correlation, higher excitations — have
to be bought separately or consciously waived. Every one of those trade-offs
was invisible in the schematic figure and is a number in this one.

The machinery post ended by saying the water MO diagram now reads as "the
converged solution of an eigenvalue problem." After this post, the figure
next to it reads the same way: not three lines placed by hand, but two
computed limits and a measured gap — $-0.354$ hartree, the exact price, for
this one molecule, of replacing what the electrons are doing with what they
do on average.

## References
