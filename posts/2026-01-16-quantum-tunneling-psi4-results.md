---
title: "Two barriers, one tunnel: the hydrogen peroxide torsion, recomputed"
date: 2026-01-16
tags: quantum chemistry, tunneling, kinetics, psi4, hydrogen peroxide, torsion
description: The original version of this post validated its H2O2 torsional barrier against the wrong experimental number and reported tunneling corrections from code that assumed its own conclusions. Recomputed from scratch — a fresh MP2/cc-pVTZ relaxed scan, the periodic torsional Schrödinger equation solved on the resulting potential, and transmission through the barrier that actually matters — with the tunneling splitting checked against sixty years of far-infrared spectroscopy.
---

*Rebuilt July 2026.* The original version of this post ("From Mock to
Reality…") documented moving a tunneling workflow from mock data to psi4, and
its two lessons about modern psi4 usage survive below. Its physics did not.
It called its 6.70 kcal/mol barrier the *trans* barrier and validated it
against "the experimental trans barrier of ~7.4 kcal/mol" — but hydrogen
peroxide's big barrier is *cis*; the trans barrier is a factor of seven
smaller. Its WKB and SCT columns were identical because the code aliased
them, and its Eckart transmission was a step function — an implementation
bug reported as a method limitation. This rewrite keeps the subject and the
URL, recomputes everything with scripts small enough to show, and grades the
results against the far-infrared spectroscopy of
Hunt and co-workers [@Hunt1965] rather than against a misremembered number.

Hydrogen peroxide is the smallest molecule with a torsion, and its torsion
is famously strange. The equilibrium structure is *skew*: the two O–H bonds
sit at a dihedral angle near 112°, not planar. Planarity can fail in two
ways — the *cis* structure (dihedral 0°, hydrogens eclipsed) and the *trans*
structure (180°, hydrogens opposed) — and these are both saddle points, with
famously unequal heights. Getting from one equivalent skew well to its
mirror image is a chemical motion with no bond broken, a barrier small
enough to tunnel through, and sixty years of precise spectroscopy to keep a
calculation honest [@Hunt1965].

That last part is the working rule carried over from
[the fundamentals rewrite](/posts/fundamentals_of_quantum_chemistry.html):
every computed number here meets either a closed form, an independent
numerical method, or an experimental value before it gets used. Three
of those checks fail loudly in what follows, and each failure is the
interesting part.

## 1. The potential, computed properly this time

The scan is psi4 1.11 [@Smith2020Psi4], MP2/cc-pVTZ with frozen core: a free
optimization of the skew minimum, then constrained optimizations marching
the H–O–O–H dihedral from 0° to 180° in 10° steps, each point seeded with
the previous point's geometry. Symmetry does the other half: $V(-\varphi) =
V(\varphi)$. Two practical lessons from the original post survive intact.
Modern optking replaced `fixed_dihedral` with `ranged_dihedral`, and setting
a tight range recovers fixed-value scans; and high-symmetry points (0°,
180°) will crash mid-scan with symmetry-projection errors unless the
geometry forces `symmetry c1` with `no_reorient`. The whole loop:

```python
for phi in grid:                      # 0..180 in 10-degree steps, chained
    psi4.set_options({**BASE,        # basis, freeze_core, convergence
        "ranged_dihedral": f"3 1 2 4 {phi-0.01} {phi+0.01}"})
    geom_from_zmat(phi, *seed)        # seeded with the previous geometry
    E = psi4.optimize("mp2")
    seed = internals_of_current()     # r_OO, r_OH, angle for the next point
```

The optimized minimum lands at $\varphi_{\mathrm{eq}} = 114.3°$, with
$r_{\mathrm{OO}} = 1.450$ Å, $r_{\mathrm{OH}} = 0.964$ Å — a couple of
degrees and a few thousandths of an ångström from the CCSD(T) reference
values [@Koput1998]. An eighth-order cosine series fits all nineteen scan
energies with a maximum residual of $0.07\ \mathrm{cm^{-1}}$, and MP2
frequency calculations at both planar structures find exactly one imaginary
mode each — $307.9i\ \mathrm{cm^{-1}}$ at trans, $611.1i\ \mathrm{cm^{-1}}$
at cis — confirming both are true first-order saddle points of the torsion.

```tikzpicture
\begin{axis}[
    width=12cm, height=8.5cm,
    xlabel={dihedral $\varphi$ (degrees)},
    ylabel={$V(\varphi)$ (cm$^{-1}$)},
    title={The H$_2$O$_2$ torsional potential, with its levels},
    xmin=0, xmax=360,
    ymin=0, ymax=1250,
    xtick={0,60,114,180,246,300,360},
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=black, smooth] coordinates {
(0,2669.7) (5,2652.9) (10,2603.3) (15,2522.3) (20,2412.6) (25,2277.4)
(30,2121.0) (35,1947.7) (40,1762.3) (45,1569.8) (50,1375.1)
(55,1182.8) (60,997.1) (65,821.9) (70,660.2) (75,514.4) (80,386.2)
(85,276.6) (90,185.9) (95,114.2) (100,60.7) (105,24.8) (110,5.1)
(115,0.1) (120,8.3) (125,27.5) (130,55.7) (135,90.6) (140,129.8)
(145,171.2) (150,212.4) (155,251.4) (160,286.2) (165,315.3) (170,337.1)
(175,350.7) (180,355.3) (185,350.7) (190,337.1) (195,315.3) (200,286.2)
(205,251.4) (210,212.4) (215,171.2) (220,129.8) (225,90.6) (230,55.7)
(235,27.5) (240,8.3) (245,0.1) (250,5.1) (255,24.8) (260,60.7)
(265,114.2) (270,185.9) (275,276.6) (280,386.2) (285,514.4) (290,660.2)
(295,821.9) (300,997.1) (305,1182.8) (310,1375.1) (315,1569.8)
(320,1762.3) (325,1947.7) (330,2121.0) (335,2277.4) (340,2412.6)
(345,2522.3) (350,2603.3) (355,2652.9) (360,2669.7)
};
\addplot[thick, color=blue]  coordinates {(91.8,158.5) (143.5,158.5)};
\addplot[thick, color=red]   coordinates {(90.9,171.5) (145.0,171.5)};
\addplot[thick, color=blue]  coordinates {(216.5,158.5) (268.2,158.5)};
\addplot[thick, color=red]   coordinates {(215.0,171.5) (269.1,171.5)};
\addplot[thick, color=blue]  coordinates {(79.4,400.0) (280.6,400.0)};
\addplot[thick, color=red]   coordinates {(74.9,517.3) (285.1,517.3)};
\addplot[dashed, color=black!60] coordinates {(0,355.3) (360,355.3)};
\node[font=\footnotesize, anchor=west] at (axis cs:5,320) {trans barrier};
\node[font=\small, anchor=west] at (axis cs:118,600) {$1^-$};
\node[font=\small, anchor=west] at (axis cs:118,455) {$1^+$};
\node[font=\small, anchor=west] at (axis cs:150,120) {$0^\pm$};
\end{axis}
```

*Figure 1.* The computed torsional potential of H$_2$O$_2$ (black; the cis
walls at 0° and 360° continue up to $2670\ \mathrm{cm^{-1}}$, off the top of
the frame) with the four lowest torsional levels from §2 drawn between
their classical turning points — symmetric states in blue, antisymmetric in
red. The ground pair hugs the wells and its two lines nearly coincide
($13\ \mathrm{cm^{-1}}$ apart); the first excited pair straddles the trans
barrier top (dashed) and is split by $117\ \mathrm{cm^{-1}}$.

| | this scan, MP2/cc-pVTZ | experiment-derived [@Hunt1965] |
|:--|:--:|:--:|
| equilibrium dihedral | $114.3°$ | $\approx 112°$ |
| trans barrier (180°) | $355\ \mathrm{cm^{-1}}$ = $1.02$ kcal/mol | $386\ \mathrm{cm^{-1}}$ = $1.10$ kcal/mol |
| cis barrier (0°) | $2670\ \mathrm{cm^{-1}}$ = $7.63$ kcal/mol | $2460\ \mathrm{cm^{-1}}$ = $7.03$ kcal/mol |

*Table 1.* Stationary points of the torsion against the empirical hindering
potential fitted to the far-infrared spectrum. Koput's CCSD(T)/cc-pVQZ
surface puts the trans barrier near $375\ \mathrm{cm^{-1}}$ [@Koput1998] —
our MP2 value is serviceable, a little low.

This table is where the original post went off the rails, so it is worth
being explicit. The **big barrier is cis** — eclipsing the hydrogens costs
lone-pair repulsion — and the **small barrier is trans**. The old post
reported one barrier of 6.70 kcal/mol, called it trans, and matched it
against "~7.4 kcal/mol", a number that belongs to the *cis* barrier. The
agreement it celebrated was a coincidence of two errors. Worse, the
mislabeling propagated: every tunneling quantity downstream was computed as
if the torsion had to cross a 7 kcal/mol wall, when the road from one well
to the other over trans costs one-seventh of that.

## 2. The observable: a splitting, not a rate

What does tunneling actually *do* to this molecule? H$_2$O$_2$ in its
ground state does not "react" — it sits in one skew well, and the well's
mirror image sits $131°$ of dihedral away. Tunneling connects them, and the
signature is not a rate constant but a **level splitting**: each torsional
state of an isolated well becomes a symmetric/antisymmetric pair, separated
by an energy that measures how often the molecule leaks through the wall.
Hunt's far-infrared spectrum resolved exactly this ladder in 1965
[@Hunt1965].

The test is therefore parameter-free: solve the one-dimensional torsional
Schrödinger equation on our computed potential,

$$
-\frac{\hbar^2}{2I}\frac{d^2\psi}{d\varphi^2} + V(\varphi)\,\psi = E\,\psi,
\qquad \psi(\varphi + 2\pi) = \psi(\varphi),
$$

and compare the resulting splittings with the measured ones. The effective
moment of inertia $I$ comes from the scan geometries themselves (two O–H
rotors counter-rotating about the O–O axis; $I = 0.456$ amu Å² at the
minimum, varying by only ±2% along the path). In a periodic plane-wave
basis the Hamiltonian is a small dense matrix — the same eigenvalue-problem
machinery as every post in this series, eight lines of NumPy:

```python
m = np.arange(-80, 81)                       # plane waves e^{im phi}
H = np.diag(B*m.astype(float)**2 + c[0])     # B = hbar^2/2I in cm^-1
for n in range(1, 9):                        # V as a cosine series
    H += 0.5*c[n]*(np.eye(161, k=n) + np.eye(161, k=-n))
levels = np.linalg.eigvalsh(H)
```

| level | computed (cm$^{-1}$) | observed (cm$^{-1}$) [@Hunt1965] |
|:-----:|:--------------------:|:---------------------------------:|
| $0^-$ | $13.0$  | $11.4$  |
| $1^+$ | $241.4$ | $254.2$ |
| $1^-$ | $358.8$ | $370.7$ |
| $2^+$ | $552.0$ | $569.3$ |
| $2^-$ | $753.3$ | $775.9$ |

*Table 2.* Torsional energy levels relative to the $0^+$ ground state, from
the plane-wave solve on the MP2/cc-pVTZ potential, against the far-infrared
values. **Ground-state tunneling splitting: computed $13.0\ \mathrm{cm^{-1}}$,
observed $11.4\ \mathrm{cm^{-1}}$.** The first-excited splitting comes out
$117.4\ \mathrm{cm^{-1}}$ against an observed $116.5\ \mathrm{cm^{-1}}$.

For a rigid one-dimensional model with no adjustable parameters, this is a
startlingly good scorecard, and the errors have honest signs: our trans
barrier is $31\ \mathrm{cm^{-1}}$ too low, so the molecule tunnels a little
too easily and the ground splitting comes out $14\%$ large. Varying $I$
over its full along-path range moves the splitting only between $12.8$ and
$13.3\ \mathrm{cm^{-1}}$ — the barrier, not the moment of inertia, owns the
error budget.

Figure 1 shows *why* the two splittings differ by an order of magnitude.
The ground pair sits at $160\ \mathrm{cm^{-1}}$, less than halfway up a
$355\ \mathrm{cm^{-1}}$ wall — genuine deep tunneling, and the pair's two
lines are nearly indistinguishable. The first excited pair straddles the
barrier top, where "tunneling" is shading into "barely hindered rotation,"
and the pair splits wide open. One more encounter with an old friend: the
tall cis wall is doing real work in this spectrum — it is what keeps the
levels from being free-rotor states — but as a *tunneling* pathway it is
irrelevant, as §3 quantifies.

## 3. Transmission and the honest kappa

The original post's headline was a tunneling correction $\kappa = 3.64$ at
300 K, computed — recall — through the wrong barrier with two of its three
methods secretly the same method. Redo it properly. The semiclassical WKB
transmission through the *computed* trans barrier (Kemble form, barrier
penetration integral evaluated on the fitted potential with the
along-path $I(\varphi)$) and the analytic Eckart transmission
[@Eckart1930] matched to the same barrier height and the psi4 imaginary
frequency:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={energy $E$ (cm$^{-1}$)},
    ylabel={transmission $T(E)$},
    title={Through the trans barrier: WKB vs.\ Eckart},
    ymode=log,
    xmin=0, xmax=500,
    ymin=1e-6, ymax=2,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=south east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, mark=none] coordinates {
(5,1.160e-04) (22,2.211e-04) (38,3.892e-04) (55,6.582e-04) (72,1.083e-03)
(88,1.746e-03) (105,2.768e-03) (122,4.326e-03) (139,6.677e-03)
(155,1.019e-02) (172,1.538e-02) (189,2.296e-02) (205,3.392e-02)
(222,4.951e-02) (239,7.132e-02) (255,1.012e-01) (272,1.409e-01)
(289,1.922e-01) (305,2.556e-01) (322,3.303e-01) (339,4.137e-01)
(356,5.012e-01) (372,5.855e-01) (389,6.651e-01) (406,7.363e-01)
(422,7.969e-01) (439,8.466e-01) (456,8.858e-01) (472,9.160e-01)
(489,9.388e-01)
};
\addplot[thick, color=red, mark=none] coordinates {
(5,2.678e-06) (22,2.419e-05) (38,8.213e-05) (55,2.131e-04) (72,4.796e-04)
(88,9.847e-04) (105,1.892e-03) (122,3.453e-03) (139,6.049e-03)
(155,1.023e-02) (172,1.680e-02) (189,2.683e-02) (205,4.175e-02)
(222,6.332e-02) (239,9.355e-02) (255,1.344e-01) (272,1.874e-01)
(289,2.528e-01) (305,3.294e-01) (322,4.137e-01) (339,5.012e-01)
(356,5.864e-01) (372,6.650e-01) (389,7.340e-01) (406,7.920e-01)
(422,8.393e-01) (439,8.768e-01) (456,9.060e-01) (472,9.285e-01)
(489,9.457e-01)
};
\addplot[dashed, color=black!60] coordinates {(355.3,1e-6) (355.3,2)};
\legend{WKB (computed barrier), Eckart (analytic)}
\end{axis}
```

*Figure 2.* Transmission through the trans barrier on a log scale: WKB on
the fitted potential (blue) and the analytic Eckart barrier matched to the
computed height and imaginary frequency (red). The dashed line marks the
barrier top. Both curves are smooth through $E = V_b$ with
$T(V_b) \approx 0.5$–$0.6$ — *not* a step function. Where the old post's
Eckart jumped from 0 to 1 at the barrier top, the analytic result spreads
that jump over roughly $\hbar\omega^\ddagger \approx 300\ \mathrm{cm^{-1}}$.

Two verification notes, in the spirit of this series. The Eckart curve here
is not trusted because the formula looks right: the script also computes
transmission through the same $\mathrm{sech}^2$ barrier by direct numerical
integration of the Schrödinger equation (Numerov, matched to plane waves on
both sides), and the analytic and numerical values agree to five decimal
places across the energy grid. That check is what caught a factor-of-two
error in my own first implementation of the barrier width — the same class
of bug as the old post's step function, caught the way such bugs have to be
caught, by an independent method rather than by eyeballing plausibility.

With $T(E)$ in hand, the thermal tunneling correction is the Boltzmann
average $\kappa(T) = e^{V_b/k_BT}\!\int_0^\infty T(E)\,
e^{-E/k_BT}\,dE\,/\,k_BT$ [@Kastner2014]:

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={temperature (K)},
    ylabel={$\kappa(T)$},
    title={Tunneling correction for the trans path},
    xmin=100, xmax=500,
    ymin=1.0, ymax=2.5,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries}
]
\addplot[thick, color=blue, mark=*, mark size=1.6pt] coordinates {
(100,2.067) (120,1.636) (140,1.427) (160,1.307) (180,1.233) (200,1.182)
(220,1.147) (240,1.120) (260,1.101) (280,1.085) (300,1.073) (320,1.063)
(340,1.055) (360,1.049) (380,1.043) (400,1.038) (420,1.034) (440,1.031)
(460,1.028) (480,1.025) (500,1.023)
};
\addplot[thick, color=red, mark=square*, mark size=1.5pt] coordinates {
(100,2.355) (120,1.861) (140,1.609) (160,1.461) (180,1.364) (200,1.298)
(220,1.250) (240,1.213) (260,1.185) (280,1.163) (300,1.145) (320,1.130)
(340,1.118) (360,1.107) (380,1.098) (400,1.091) (420,1.084) (440,1.078)
(460,1.073) (480,1.068) (500,1.064)
};
\addplot[thick, dashed, color=black!60] coordinates {
(100,1.818) (120,1.568) (140,1.417) (160,1.319) (180,1.252) (200,1.204)
(220,1.169) (240,1.142) (260,1.121) (280,1.104) (300,1.091) (320,1.080)
(340,1.071) (360,1.063) (380,1.057) (400,1.051) (420,1.046) (440,1.042)
(460,1.039) (480,1.035) (500,1.033)
};
\legend{WKB, Eckart, Wigner}
\end{axis}
```

*Figure 3.* The tunneling correction $\kappa(T)$ for crossing the trans
barrier: WKB on the computed potential, analytic Eckart, and the Wigner
low-order estimate $1 + (\hbar\omega^\ddagger/k_BT)^2/24$. Three genuinely
different methods now agree within ~10% — compare the old post, where two
"different" methods agreed to six digits because they were the same code.

| $T$ (K) | WKB | Eckart | Wigner |
|:--:|:--:|:--:|:--:|
| 100 | $2.07$ | $2.36$ | $1.82$ |
| 200 | $1.18$ | $1.30$ | $1.20$ |
| 300 | $1.07$ | $1.15$ | $1.09$ |
| 500 | $1.02$ | $1.06$ | $1.03$ |

*Table 3.* $\kappa(T)$ for the trans path. At room temperature, tunneling
is a **7–15% correction**, not the old post's factor of 3.64; even at 100 K
it is a factor of ~2, not ~47. A 1D transition-state estimate with the
computed torsional frequency as prefactor puts the classical interwell rate
near $2\times 10^{12}\ \mathrm{s^{-1}}$ at 300 K — the torsion flips on the
picosecond scale, four orders of magnitude faster than the old post's
$1.3\times 10^{8}\ \mathrm{s^{-1}}$, which was computed against the wrong
barrier.

And the cis pathway? Its $\kappa$ is formally enormous at low temperature
(tunneling deep under a tall barrier beats the classical route over it),
but multiplying by the Boltzmann factor of a $2670\ \mathrm{cm^{-1}}$ wall
settles the question: the tunneling-corrected cis flux is $10^{-12}$ of the
trans flux at 100 K and $2\times10^{-5}$ of it at 300 K. Every microscopic
reversal of this molecule's handedness goes through trans. The tall
barrier shapes the spectrum; the short one carries the traffic.

## 4. The autopsy, and the limits

What the original post got wrong compresses to three entries, each with a
general lesson. **The barrier was validated against the wrong experiment**
— cis and trans swapped — and a validation against the wrong number is
worse than none, because it converts an error into a certificate.
**Two methods agreed because they were one method** — the SCT column was
the WKB column under a second name; agreement between methods is evidence
only when the methods are independent. **A broken implementation was
reported as a method limitation** — the step-function "Eckart" — when a
ten-line numerical scattering check would have convicted the code instead
of Carl Eckart.

The rebuilt numbers carry their own stated limits. This is a rigid 1D model:
one torsional coordinate, a moment of inertia frozen per-geometry, no
zero-point adjustment of the other five modes along the path, and an MP2
barrier that sits $31\ \mathrm{cm^{-1}}$ below the empirical one. Those
approximations show up honestly as the 14% overshoot in the ground
splitting. The systematic fix — letting the path curve through all
coordinates and treating deep tunneling variationally — is instanton
territory [@Richardson2009; @Kastner2014], a genuinely different machine.
The point of this rewrite is narrower: with the right barrier labeled by
the right name, a laptop-scale scan plus an eigenvalue problem reproduces
sixty-year-old far-infrared spectroscopy to a few percent, and every claim
in the post is attached to the check that would catch it being wrong.

## References
