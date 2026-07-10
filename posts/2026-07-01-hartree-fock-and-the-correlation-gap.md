---
title: "Hartree–Fock and the correlation gap: where the orbital energies come from"
date: 2026-07-01
author: Peter Johnston
tags: quantum chemistry, Hartree-Fock, self-consistent field, molecular orbitals, symmetry, electron correlation
description: A water molecular-orbital diagram quotes orbital energies as if they were just there to be read off. This post derives the ground-state machinery — the Hartree–Fock equations, their self-consistent solution, Koopmans' theorem, and the correlation energy that the mean field leaves behind — that actually computes them.
---

In a [previous post on water](/posts/2026-06-30-reading-water-geometry-orbitals-acidity-spectra.html)
we drew a molecular-orbital diagram for $\mathrm{H_2O}$ and read its levels off
the page. Symmetry sorted the atomic orbitals into $a_1$, $b_2$, and $b_1$ boxes;
filling eight valence electrons from the bottom gave the configuration
$(2a_1)^2(1b_2)^2(3a_1)^2(1b_1)^2$; and we checked the ordering against
photoelectron spectroscopy, which knocks electrons out one at a time and reports
the energy it takes: about **12.6 eV** for $1b_1$, **14.7 eV** for $3a_1$,
**18.5 eV** for $1b_2$, and a deep **32 eV** for $2a_1$.[@Turner1970] The diagram
worked. But we placed those levels *by hand* — by symmetry, by chemical intuition,
and by knowing the answer we were aiming for.

This post is about the machinery that actually computes them. It sits one floor up
from the single-particle problems — particle in a box, harmonic oscillator,
hydrogen atom — worked out in
[the fundamentals post](/posts/fundamentals_of_quantum_chemistry.html), and one
floor down from the excited-state, linear-response methods in
[the post on excited-state frameworks and basis sets](/posts/Maths-Framework-and-Basis-Sets.html).
It is the ground-state self-consistent-field theory of Hartree and Fock: the set
of equations whose eigenvalues *are* the levels on the water diagram. We will
build it from the bottom — the Hamiltonian, the wavefunction we are allowed to
write down, the variational principle that picks the best one, the mean-field
equations that result, and the matrix form a computer actually solves — and then
we will be honest about what it leaves out. Because the most important number in
this whole story is the one Hartree–Fock *cannot* get: the correlation energy, the
gap between the best mean-field answer and the truth.

## 1. The electronic Hamiltonian

Before any energy level means anything, we need a well-defined energy axis, and
that means writing down the operator whose eigenvalues we are after. A molecule is
a collection of nuclei and electrons interacting through Coulomb's law, and the
full Hamiltonian couples the motion of both. The first simplification — the one
that makes "molecular structure" a meaningful idea at all — is the
**Born–Oppenheimer approximation**: nuclei are thousands of times heavier than
electrons, so on the timescale of electronic motion they are effectively frozen.
We clamp the nuclei at fixed positions, solve for the electrons in that static
field, and read the result as a function of where we put the nuclei.

With the nuclei clamped, the nuclear kinetic energy vanishes and the
nuclear–nuclear repulsion becomes a constant we can add at the end. What remains
is the **electronic Hamiltonian** (in atomic units, $\hbar = m_e = e =
4\pi\varepsilon_0 = 1$):

$$
\hat{H}_{\mathrm{elec}}
= \underbrace{-\frac{1}{2}\sum_{i} \nabla_i^2}_{\text{kinetic}}
\;\underbrace{-\sum_{i}\sum_{A} \frac{Z_A}{r_{iA}}}_{\text{electron–nuclear attraction}}
\;+\;\underbrace{\sum_{i<j} \frac{1}{r_{ij}}}_{\text{electron–electron repulsion}} .
$$

The first two sums are *one-electron* operators: each term involves a single
electron $i$ moving in the fixed external field of the nuclei. If those were the
only terms, the problem would factor. Each electron would see the same fixed
potential, the many-electron Schrödinger equation would separate into independent
one-electron equations, and we would be back in the comfortable world of the
hydrogen atom — orbitals, with energies, filled one at a time. The water diagram
*assumes* exactly this picture: independent electrons in orbitals.

The third sum is what wrecks it. The term $1/r_{ij}$ couples every pair of
electrons: where electron $i$ goes depends on where electron $j$ is, instant by
instant. It cannot be split into a sum of one-electron pieces, and it is the
reason the electronic Schrödinger equation has no closed-form solution for any
atom past hydrogen. Everything difficult about quantum chemistry — and everything
in this post — is a strategy for coping with that one term. Hartree–Fock's
strategy is to *approximate* it; the correlation energy of §7 is the price of the
approximation.

## 2. The Slater determinant

Even before we touch the repulsion, the form of the wavefunction is constrained.
Electrons are fermions, and the wavefunction of a many-fermion system must be
**antisymmetric**: swap the full coordinates (space *and* spin) of any two
electrons and $\Psi$ must change sign,

$$
\Psi(\mathbf{x}_1,\dots,\mathbf{x}_i,\dots,\mathbf{x}_j,\dots,\mathbf{x}_N)
= -\,\Psi(\mathbf{x}_1,\dots,\mathbf{x}_j,\dots,\mathbf{x}_i,\dots,\mathbf{x}_N),
$$

where $\mathbf{x} = (\mathbf{r}, \omega)$ bundles position and spin. This is the
Pauli principle in its deepest form, and it has an immediate consequence: set
$\mathbf{x}_i = \mathbf{x}_j$ and antisymmetry forces $\Psi = 0$. Two electrons
cannot occupy the same spin-orbital — not as a rule bolted on afterward, but as
arithmetic.

The simplest wavefunction that builds in antisymmetry automatically is a
determinant. Take $N$ one-electron **spin-orbitals** $\chi_1,\dots,\chi_N$ (each a
spatial orbital times a spin function) and assemble the **Slater determinant**

$$
\Psi_{\mathrm{HF}}(\mathbf{x}_1,\dots,\mathbf{x}_N)
= \frac{1}{\sqrt{N!}}
\begin{vmatrix}
\chi_1(\mathbf{x}_1) & \chi_2(\mathbf{x}_1) & \cdots & \chi_N(\mathbf{x}_1) \\
\chi_1(\mathbf{x}_2) & \chi_2(\mathbf{x}_2) & \cdots & \chi_N(\mathbf{x}_2) \\
\vdots & \vdots & \ddots & \vdots \\
\chi_1(\mathbf{x}_N) & \chi_2(\mathbf{x}_N) & \cdots & \chi_N(\mathbf{x}_N)
\end{vmatrix}.
$$

A determinant changes sign when two rows are swapped — that is exchanging two
electrons, so antisymmetry is automatic — and it vanishes when two columns are
equal — that is two electrons in the same spin-orbital, so Pauli is automatic. The
determinant is not just *a* convenient antisymmetric function; it is the minimal
one, the single-configuration ansatz, and it is the precise mathematical content
of the phrase "each electron is in its own orbital." The water configuration
$(2a_1)^2(1b_2)^2(3a_1)^2(1b_1)^2$ names exactly which spin-orbitals fill the
columns. Hartree–Fock theory is what you get when you insist the wavefunction is a
*single* such determinant and then make it as good as it can be.

## 3. The variational principle

"As good as it can be" needs a yardstick, and the variational principle is the
yardstick. For any normalized trial wavefunction $\Psi$, the expectation value of
the Hamiltonian is an upper bound on the true ground-state energy $E_0$:

$$
E[\Psi] = \frac{\langle \Psi | \hat{H} | \Psi \rangle}{\langle \Psi | \Psi \rangle}
\;\geq\; E_0 .
$$

The proof is one line: expand $\Psi$ in the exact (unknown) eigenstates
$\hat{H}|\Psi_n\rangle = E_n|\Psi_n\rangle$, and since every $E_n \geq E_0$, the
weighted average $E[\Psi]$ cannot dip below $E_0$. Equality holds only when $\Psi$
*is* the ground state. This turns "solve the Schrödinger equation" — a differential
equation we cannot solve — into "minimize a number," which we can attack.

Hartree–Fock applies the principle inside the restricted arena of single
determinants. Among *all* antisymmetric wavefunctions, the true ground state is
some hopelessly complicated object; we are not searching there. We are searching
only over single Slater determinants, asking: of all the ways to choose the
spin-orbitals $\{\chi_i\}$, which determinant has the lowest energy? That lowest
single-determinant energy is the **Hartree–Fock energy** $E_{\mathrm{HF}}$, and
because the determinant is a legitimate trial function, $E_{\mathrm{HF}} \geq E_0$
— always above the truth, by an amount we will name in §7. The minimization is a
variational problem in the orbitals themselves, and carrying it out is what
produces the equations that bear Hartree's and Fock's names.

## 4. The Hartree–Fock equations

Minimizing $E[\Psi_{\mathrm{HF}}]$ with respect to the spin-orbitals, subject to
keeping them orthonormal, yields a set of coupled one-electron eigenvalue
equations [@SzaboOstlund1996]:

$$
\hat{f}\,\chi_i = \varepsilon_i\,\chi_i .
$$

This looks like an ordinary single-particle Schrödinger equation, and that
resemblance is the whole achievement: the intractable many-electron problem has
been recast as a one-electron problem in an effective potential. The operator
$\hat{f}$ is the **Fock operator**,

$$
\hat{f} = \hat{h} + \sum_{j}^{\text{occ}} \big( \hat{J}_j - \hat{K}_j \big),
$$

where $\hat{h} = -\tfrac{1}{2}\nabla^2 - \sum_A Z_A/r_A$ is the bare one-electron
core Hamiltonian — kinetic energy plus attraction to the nuclei — and the sum runs
over all occupied orbitals. The two new operators are where the electron–electron
repulsion has gone, and they are worth dwelling on because one of them is
classical and the other is not.

The **Coulomb operator** $\hat{J}_j$ acts on $\chi_i$ as

$$
\hat{J}_j(\mathbf{x}_1)\,\chi_i(\mathbf{x}_1)
= \left[ \int \frac{|\chi_j(\mathbf{x}_2)|^2}{r_{12}}\, d\mathbf{x}_2 \right]
  \chi_i(\mathbf{x}_1) ,
$$

and it is exactly what intuition expects: electron $i$ feels the smeared-out
electrostatic repulsion of the charge cloud $|\chi_j|^2$ of every other electron.
This is the **mean field**. Each electron no longer tracks the others moment by
moment; it moves in the *average* potential they create. That is the central
approximation of Hartree–Fock, and it is exactly where correlation will leak out —
because real electrons do dodge each other instantaneously, and an average cannot
capture a dodge.

The **exchange operator** $\hat{K}_j$ has no classical analogue at all:

$$
\hat{K}_j(\mathbf{x}_1)\,\chi_i(\mathbf{x}_1)
= \left[ \int \frac{\chi_j^*(\mathbf{x}_2)\,\chi_i(\mathbf{x}_2)}{r_{12}}\, d\mathbf{x}_2 \right]
  \chi_j(\mathbf{x}_1) .
$$

Notice that $\chi_i$ and $\chi_j$ have traded places between the integrand and the
result — the operator is *nonlocal*, mixing the value of the orbital at one point
with its overlap somewhere else. It arises purely from antisymmetry: it is the
determinant's bookkeeping for the fact that you cannot tell electron $i$ from
electron $j$. Its physical effect is real and measurable. Exchange keeps electrons
of *like spin* apart — the "Fermi hole" — which lowers their mutual repulsion and
is a genuine piece of the energy, not a correction. Hartree–Fock treats exchange
*exactly*. What it misses is the analogous correlation between electrons of
*opposite* spin, and the residual same-spin correlation beyond the Fermi hole.
That distinction is the seed of §7.

The eigenvalues $\varepsilon_i$ that come out of $\hat{f}\chi_i =
\varepsilon_i\chi_i$ are the **orbital energies**. These are not an analogy for the
levels on the water diagram — they *are* those levels. When we wrote $1b_1$ at
$-12.6$ eV and $2a_1$ deep below, we were sketching the $\varepsilon_i$ of the
water Fock operator. The rest of this post is about how to compute them and how
much to trust them.

## 5. Roothaan–Hall: the equations a computer solves

The Fock equations are still differential equations in continuous functions. The
move that made quantum chemistry computational, due to Roothaan and independently
Hall, is to expand each molecular orbital as a **linear combination of atomic
orbitals** (LCAO) — a fixed set of $K$ basis functions $\{\phi_\mu\}$ centered on
the atoms:

$$
\psi_i = \sum_{\mu=1}^{K} C_{\mu i}\,\phi_\mu .
$$

Solving for the *orbitals* now means solving for the *coefficients* $C_{\mu i}$ —
finitely many numbers. Substituting this expansion into the Fock equation and
projecting onto each basis function turns the differential equation into a matrix
equation, the **Roothaan–Hall equation** [@Roothaan1951]:

$$
\mathbf{F}\,\mathbf{C} = \mathbf{S}\,\mathbf{C}\,\boldsymbol{\varepsilon} .
$$

Four objects appear, each with a clean meaning. The **overlap matrix**
$S_{\mu\nu} = \int \phi_\mu^* \phi_\nu \, d\mathbf{r}$ records how non-orthogonal
the atomic orbitals are — atomic orbitals on different centers are not orthogonal,
so this is not the identity, and that is why the equation is a *generalized*
eigenproblem rather than a plain one. The **Fock matrix** $F_{\mu\nu} = \int
\phi_\mu^* \hat{f}\, \phi_\nu \, d\mathbf{r}$ is the Fock operator in the basis. The
columns of $\mathbf{C}$ are the orbital coefficients, and the diagonal matrix
$\boldsymbol{\varepsilon}$ holds the orbital energies. The Fock matrix splits into
the one-electron core integrals plus a two-electron part built from the
**density matrix**

$$
P_{\mu\nu} = \sum_{i}^{\text{occ}} n_i\, C_{\mu i}\, C_{\nu i}^{*}
\qquad\Longrightarrow\qquad
F_{\mu\nu} = H^{\text{core}}_{\mu\nu}
  + \sum_{\lambda\sigma} P_{\lambda\sigma}
    \left[ (\mu\nu\,|\,\lambda\sigma) - \tfrac{1}{2}(\mu\lambda\,|\,\nu\sigma) \right],
$$

where $(\mu\nu\,|\,\lambda\sigma)$ are the **two-electron repulsion integrals**
over the basis. (The two bracketed terms are the matrix incarnations of $\hat{J}$
and $\hat{K}$ from §4.) Here we have specialized to the closed-shell (restricted)
case: water's electrons are paired, so each occupied spatial orbital holds two
electrons ($n_i = 2$). That factor of two lives in $\mathbf{P}$, which is why
exchange enters with a one-half — the spin-orbital Fock operator of §4 collapses to
this spatial form once every orbital is doubly occupied.

Here is the knot at the center of the whole method. The Fock matrix $\mathbf{F}$
depends, through $\mathbf{P}$, on the very coefficients $\mathbf{C}$ we are trying
to find. You cannot build the operator without already knowing its eigenvectors.
The escape is iteration: guess a density, build $\mathbf{F}$, solve the
eigenproblem for a new $\mathbf{C}$, build a new density, and repeat until the
density that comes out matches the one that went in. This is the
**self-consistent field** (SCF) procedure, and "self-consistent" is literal — the
field and the orbitals it produces must agree. Figure 1 traces one turn of the
cycle.

```tikzpicture
\begin{tikzpicture}[>=Stealth,
  box/.style={draw, rounded corners=2pt, align=center, fill=blue!7,
              draw=blue!55!black, minimum height=9mm, minimum width=34mm, thick},
  io/.style={draw, align=center, fill=black!6, draw=black!55,
             minimum height=8mm, minimum width=30mm, thick},
  dec/.style={draw, rounded corners=2pt, align=center, fill=green!10,
              draw=green!55!black, minimum height=9mm, minimum width=34mm, thick},
  done/.style={draw, rounded corners=2pt, align=center, fill=green!12,
               draw=green!55!black, minimum height=8mm, minimum width=30mm, thick},
  flow/.style={->, thick, black!70},
]
  \node[io]   (guess) at (0,4.5)  {guess density $\mathbf{P}$};
  \node[box]  (build) at (0,3.0)  {build $\mathbf{F}(\mathbf{P})$\\[1pt]\scriptsize Coulomb + exchange};
  \node[box]  (solve) at (0,1.5)  {solve $\mathbf{FC}=\mathbf{SC}\boldsymbol{\varepsilon}$};
  \node[box]  (newp)  at (0,0.0)  {new $\mathbf{P}=\sum_i^{\mathrm{occ}} \mathbf{c}_i\mathbf{c}_i^{\dagger}$};
  \node[dec]  (conv)  at (0,-2.0) {converged?\\\scriptsize $\Delta\mathbf{P},\Delta E$ small};
  \node[done] (out)   at (5.4,-2.0) {orbitals $\psi_i$, energies $\varepsilon_i$};

  \draw[flow] (guess) -- (build);
  \draw[flow] (build) -- (solve);
  \draw[flow] (solve) -- (newp);
  \draw[flow] (newp)  -- (conv);
  \draw[flow] (conv)  -- node[above,font=\small]{yes} (out);
  \draw[flow] (conv) -- node[below,font=\small,pos=0.55]{no} (-4.2,-2.0)
              -- (-4.2,3.0) -- (build);
\end{tikzpicture}
```

*Figure 1.* The self-consistent-field loop: from a trial density build the Fock
matrix, solve the Roothaan–Hall eigenproblem, form a new density from the occupied
orbitals, and repeat until the density that comes out matches the one that went in.

### Symmetry block-diagonalizes the problem

This is where the water post and this one fuse. The secular problem $\mathbf{F}
\mathbf{C} = \mathbf{S}\mathbf{C}\boldsymbol{\varepsilon}$ is a $K \times K$
eigenproblem, and in general every basis function can mix with every other. But
the Fock operator commutes with every symmetry operation of the molecule: it has
the full $C_{2v}$ symmetry of bent water. A standard result then says that
$\mathbf{F}$ (and $\mathbf{S}$) cannot connect basis functions of *different*
irreducible representations — those matrix elements are exactly zero. If we first
combine the raw atomic orbitals into the **symmetry-adapted** combinations of
§2 of the water post — the $a_1$, $b_2$, and $b_1$ sets — the Fock matrix becomes
**block-diagonal** (Figure 2):

```tikzpicture
\begin{tikzpicture}[>=Stealth, line width=0.8pt]
  \def\n{6}
  \def\s{0.62}
  \draw (0,0) rectangle (\n*\s,\n*\s);
  \foreach \i in {1,...,5} {
    \draw[gray!30,line width=0.4pt] (\i*\s,0) -- (\i*\s,\n*\s);
    \draw[gray!30,line width=0.4pt] (0,\i*\s) -- (\n*\s,\i*\s);
  }
  \fill[blue!18] (0,\n*\s-3*\s) rectangle (3*\s,\n*\s);
  \fill[orange!22] (3*\s,\n*\s-5*\s) rectangle (5*\s,\n*\s-3*\s);
  \fill[green!28] (5*\s,0) rectangle (6*\s,\s);
  \draw (0,0) rectangle (\n*\s,\n*\s);
  \foreach \i in {1,...,5} {
    \draw[gray!30,line width=0.4pt] (\i*\s,0) -- (\i*\s,\n*\s);
    \draw[gray!30,line width=0.4pt] (0,\i*\s) -- (\n*\s,\i*\s);
  }
  \draw[blue!55!black,line width=1.1pt]  (0,\n*\s-3*\s) rectangle (3*\s,\n*\s);
  \draw[orange!65!black,line width=1.1pt] (3*\s,\n*\s-5*\s) rectangle (5*\s,\n*\s-3*\s);
  \draw[green!50!black,line width=1.1pt] (5*\s,0) rectangle (6*\s,\s);
  \node[blue!45!black,font=\bfseries] at (1.5*\s,\n*\s-1.5*\s) {$a_1$};
  \node[orange!60!black,font=\bfseries] at (4*\s,\n*\s-4*\s) {$b_2$};
  \node[green!45!black,font=\bfseries] at (5.5*\s,0.5*\s) {$b_1$};
  \foreach \r/\lab in {1/$a_1$,2/$a_1$,3/$a_1$,4/$b_2$,5/$b_2$,6/$b_1$} {
    \node[font=\scriptsize,anchor=east] at (-0.1,\n*\s-\r*\s+0.5*\s) {\lab};
  }
  \node[font=\small] at (\n*\s/2,-0.55) {Fock matrix $\mathbf{F}$ in symmetry-adapted AOs};
\end{tikzpicture}
```

*Figure 2.* In a symmetry-adapted basis the Fock matrix is block-diagonal: the
$a_1$ ($3\times3$), $b_2$ ($2\times2$), and $b_1$ ($1\times1$) blocks carry no
matrix elements between them, so the secular problem splits into one independent
eigenproblem per irrep.

The big eigenproblem factors into independent small ones — one per irrep — and the
labels on those blocks are *exactly* the $a_1$, $b_2$, $b_1$ labels from the water
diagram. Orbitals of different symmetry do not mix because the off-block elements
are zero; that is not a modeling choice but a consequence of the molecule's shape.

The smallest block makes "solve the eigenproblem" concrete. The $b_1$ block is
$1\times 1$: in a minimal valence description the only function of $b_1$ symmetry
is the oxygen $2p_x$ orbital sticking out of the molecular plane, with no hydrogen
partner to pair with. A $1\times 1$ secular "matrix" is already its own
eigenvalue, $\varepsilon = F_{b_1 b_1}$, and the orbital is the bare atomic orbital
unchanged. That is the algebraic reason $1b_1$ is a **pure, nonbonding** oxygen
lone pair — it has nothing to combine with, so the variational principle leaves it
alone. The "lonely box" of the water post is a one-dimensional block here.

The $a_1$ block is where mixing happens. Take a minimal $a_1$ set — the oxygen
$2s$, the oxygen $2p_z$ along the symmetry axis, and the symmetric hydrogen
combination $\phi_{\mathrm{H}^+} = (1s_A + 1s_B)/\sqrt{2}$. The orbital energies in
this symmetry are the roots $\varepsilon$ of the $3\times 3$ secular determinant

$$
\begin{vmatrix}
F_{ss} - \varepsilon S_{ss} & F_{sz} - \varepsilon S_{sz} & F_{sh} - \varepsilon S_{sh} \\
F_{zs} - \varepsilon S_{zs} & F_{zz} - \varepsilon S_{zz} & F_{zh} - \varepsilon S_{zh} \\
F_{hs} - \varepsilon S_{hs} & F_{hz} - \varepsilon S_{hz} & F_{hh} - \varepsilon S_{hh}
\end{vmatrix} = 0 ,
$$

whose three roots are precisely the bonding $2a_1$, the roughly nonbonding $3a_1$,
and the empty antibonding $4a_1^{*}$ of the diagram. The $b_2$ block is a $2\times
2$ between the oxygen $2p_y$ and the antisymmetric hydrogen combination,
$(1s_A - 1s_B)/\sqrt{2}$, giving the bonding $1b_2$ and its antibonding partner.
The point is not the numbers — those come out of the SCF — but the structure: the
hand-drawn correlation lines of the water MO diagram are the off-diagonal Fock
elements $F_{sz}$, $F_{sh}$, $F_{zh}$ inside one symmetry block, and "which
orbitals mix" is "which functions share a block."

## 6. Koopmans' theorem and the water spectrum

We now have orbital energies $\varepsilon_i$. The water post compared them to
*ionization energies* — the cost of removing an electron — as if the two were the
same thing. **Koopmans' theorem** is the bridge, and it is almost suspiciously
simple [@Koopmans1934]:

$$
\mathrm{IE}_i \approx -\varepsilon_i .
$$

The ionization energy of the electron in orbital $i$ is minus its orbital energy.
This is why the photoelectron spectrum can be read straight off an MO diagram, and
it is the single fact that made the water diagram checkable against experiment.

But the approximation rests on two assumptions that should be stated out loud,
because both are false in detail and the post would be dishonest to hide them.
First, **frozen orbitals**: Koopmans assumes that when you eject an electron, the
remaining $N-1$ electrons do not move — they stay in exactly the orbitals they
occupied in the neutral. In reality the remaining electrons *relax* inward toward
the now-less-shielded nuclei, which lowers the energy of the cation and therefore
*lowers* the true ionization energy below $-\varepsilon_i$. Second, **no
correlation**: $\varepsilon_i$ is a Hartree–Fock quantity, so it inherits the
mean-field error of §7. The neutral, with more electrons, has more correlation
energy than the cation, and that difference works in the *opposite* direction,
*raising* the true IE relative to $-\varepsilon_i$.

The reason Koopmans is useful at all is that these two errors have opposite signs
and, for outer-valence orbitals, they substantially cancel. For deep orbitals the
cancellation fails, because ejecting a tightly bound electron triggers a large
relaxation that the frozen-orbital picture cannot see. Water shows the pattern
cleanly. Lining up representative near-Hartree–Fock orbital energies against the
experimental ionization energies from the water post (Table 1):

| Orbital | Character | $-\varepsilon_i$ (Koopmans) | Experiment | Error |
|:-------:|:----------|:---------------------------:|:----------:|:-----:|
| $1b_1$  | O lone pair ($\perp$ plane) | $\approx 13.8$ eV | 12.6 eV | $+1.2$ |
| $3a_1$  | in-plane lone pair / bonding | $\approx 15.9$ eV | 14.7 eV | $+1.2$ |
| $1b_2$  | O–H bonding | $\approx 19.8$ eV | 18.5 eV | $+1.3$ |
| $2a_1$  | O $2s$, deep bonding | $\approx 36.4$ eV | $\approx 32$ eV | $+4.4$ |

*Table 1.* Koopmans estimates $-\varepsilon_i$, from representative
near-Hartree–Fock orbital energies, against the experimental vertical ionization
energies of water. The overestimate runs a little over an electron-volt across the
outer valence and widens to several eV for the deep $2a_1$.

```tikzpicture
\begin{axis}[
    width=12cm, height=8cm,
    ybar,
    bar width=14pt,
    ylabel={ionization energy (eV)},
    title={Koopmans estimates vs.\ experiment: water valence ionization},
    xmin=0.4, xmax=4.6,
    xtick={1,2,3,4},
    xticklabels={$1b_1$,$3a_1$,$1b_2$,$2a_1$},
    ymin=0, ymax=40,
    grid=major,
    grid style={line width=.2pt, draw=gray!40},
    axis lines=left,
    legend pos=north west,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    nodes near coords,
    every node near coord/.append style={font=\scriptsize, /pgf/number format/.cd, fixed, precision=1}
]
\addplot[fill=blue!55] coordinates {(1,13.8) (2,15.9) (3,19.8) (4,36.4)};
\addplot[fill=red!55] coordinates {(1,12.6) (2,14.7) (3,18.5) (4,32)};
\legend{$-\varepsilon_i$ (Koopmans), Experiment}
\end{axis}
```

*Figure 4.* The same comparison as Table 1, read as a chart: the Koopmans bar sits
a little above experiment for the three outer-valence orbitals, by a nearly
constant margin, then jumps well clear of it for the deep $2a_1$ — the frozen-orbital
approximation surviving well for shallow holes and failing visibly for a deep one.

(The exact $-\varepsilon$ values shift by a few tenths of an eV with the basis set;
these are representative near-HF-limit numbers, and the point is the *pattern*, not
the third digit.) For the three outer orbitals Koopmans lands a little over an
electron-volt high — a consistent overestimate, exactly as the relaxation-versus-
correlation story predicts, with the two errors nearly but not perfectly
cancelling. For the deep $2a_1$ the error blows out to several eV: removing an
electron from an orbital built largely of oxygen $2s$ leaves a compact hole that
the other electrons relax around dramatically, and the frozen-orbital assumption
is simply too crude. The lesson is the right amount of trust: Koopmans gets the
*ordering* right and the outer-valence energies right to about a volt, which is
plenty to assign a spectrum, but it is not a quantitative theory of ionization, and
the deep levels are where it visibly frays.

## 7. The correlation gap

Everything so far has lived inside the single-determinant approximation, and now we
pay for it. The exact nonrelativistic energy of the molecule, at fixed nuclei and
in a given basis, is lower than the Hartree–Fock energy. The difference *defines*
the **correlation energy**:

$$
E_{\mathrm{corr}} = E_{\mathrm{exact}} - E_{\mathrm{HF}} \;<\; 0 .
$$

By construction it is the part of the energy that the mean field cannot reach. The
variational principle of §3 guarantees its sign: since the Hartree–Fock
determinant is just one trial function, $E_{\mathrm{HF}} \geq E_{\mathrm{exact}}$,
so $E_{\mathrm{corr}}$ is never positive. (Strictly, both energies must be taken in
the same one-particle basis; the limiting value uses the Hartree–Fock basis-set
limit and the exact energy in a complete basis.)

```tikzpicture
\begin{tikzpicture}[>=Stealth, line width=1pt,
   lev/.style={line width=1.4pt}]
  \draw[->,gray] (0,-3.8) -- (0,0.8);
  \node[gray,rotate=90,anchor=south,font=\small] at (-0.3,-1.6) {energy (more negative downward)};
  \draw[lev,blue!55!black] (1.2,0.2) -- (4.0,0.2);
  \node[right,font=\small,blue!45!black] at (4.1,0.2) {$E_{\mathrm{HF}}$ (finite basis)};
  \draw[lev,blue!55!black] (1.2,-1.1) -- (4.0,-1.1);
  \node[right,font=\small,blue!45!black] at (4.1,-1.1) {$E_{\mathrm{HF}}$ (basis-set limit)};
  \draw[lev,red!60!black] (1.2,-3.3) -- (4.0,-3.3);
  \node[right,font=\small,red!50!black] at (4.1,-3.3) {$E_{\mathrm{exact}}$ (nonrel., clamped nuclei)};
  \draw[<->,thick,black!55] (0.85,0.2) -- (0.85,-1.1);
  \node[left,font=\scriptsize,align=right] at (0.78,-0.45) {basis-set\\error};
  \draw[<->,thick,black!75] (2.6,-1.1) -- (2.6,-3.3);
  \node[fill=white,font=\small] at (2.6,-2.2) {$E_{\mathrm{corr}}$};
\end{tikzpicture}
```

*Figure 3.* The correlation gap. $E_{\mathrm{HF}}$ sits above the exact
nonrelativistic energy; enlarging the basis lowers $E_{\mathrm{HF}}$ only as far as
the Hartree–Fock limit, and the residual distance down to $E_{\mathrm{exact}}$ is
the correlation energy $E_{\mathrm{corr}}$.

The gap drawn in Figure 3 is small in absolute terms — typically under 1% of the
total electronic energy — but it is decisive in chemistry, because the quantities
we care about are energy *differences* of the same order: bond energies, reaction
barriers, excitation energies. A method that recovers 99% of the energy can still
be useless for a barrier height if the missing 1% varies between reactant and
product. So the correlation energy is not a rounding error to wave away; it is
frequently the whole answer. (Figure 3 is drawn schematically here; a
[follow-up post](/posts/2026-07-04-the-correlation-gap-in-water-measured.html)
computes every line on it for this same water molecule — RHF marched up a
basis-set ladder to its limit, CCSD(T) below it, and the gap measured at
$-0.354$ hartree.)

It helps to split it in two. **Dynamic correlation** is the instantaneous dodging
the mean field smears over: each electron carves out a "Coulomb hole" around itself
that the average potential of §4 ignores. It is the small, ubiquitous, additive
correlation present in every system, and it is the correlation contribution
lurking inside the Koopmans errors of §6. **Static** (or **near-degeneracy**) **correlation** is different in kind: it
appears when a single determinant is qualitatively wrong because two or more
configurations are close in energy and contribute comparably — stretched bonds,
diradicals, transition-metal centers. There, no amount of patching one determinant
helps, because the starting picture itself is broken.

Two broad routes go past Hartree–Fock. The **wavefunction** route keeps the
determinant as a reference and adds others on top. **Møller–Plesset perturbation
theory** treats the fluctuation potential as a perturbation; its second-order
correction, the workhorse MP2, is

$$
E^{(2)} = \sum_{i<j}^{\text{occ}} \sum_{a<b}^{\text{virt}}
  \frac{\big| \langle ij \,\|\, ab \rangle \big|^2}
       {\varepsilon_i + \varepsilon_j - \varepsilon_a - \varepsilon_b},
$$

a sum over excitations of electron pairs from occupied orbitals $i,j$ into virtual
orbitals $a,b$ — note that it is built entirely from the same $\varepsilon$'s and
two-electron integrals we already have. **Configuration interaction** diagonalizes
the Hamiltonian in a space of many determinants; carried to its limit (full CI) in
a given basis it is *exact* for that basis — and combinatorially unaffordable for
all but the smallest systems, which is why it serves mostly as a benchmark.
**Coupled cluster** reorganizes the same idea into an exponential ansatz that
captures dynamic correlation compactly; CCSD(T) — singles, doubles, and a
perturbative treatment of triples — is accurate and affordable enough to be the de
facto **"gold standard"** for well-behaved molecules.[@HelgakerJorgensenOlsen2000]
The **density-functional** route is different in spirit: Kohn–Sham DFT is exact in
principle, folding exchange *and* correlation into a single exchange–correlation
functional of the electron density — but that functional is unknown, and in
practice one chooses among approximations, trading the systematic improvability of
the wavefunction hierarchy for far lower cost.

And that hands off cleanly to where this series goes next. Every method just named
has a linear-response, excited-state sibling: TD-DFT is the response version of
Kohn–Sham, EOM-CCSD the response version of coupled cluster, and CASSCF the way to
handle the static correlation that defeats a single reference — and those are
exactly the methods worked through in
[the post on excited-state frameworks and basis sets](/posts/Maths-Framework-and-Basis-Sets.html).
Ground-state Hartree–Fock is the floor they all stand on.

## The equations read as one piece

Step back and the chain is short and tight. The electronic Hamiltonian (§1) is
honest but unsolvable, wrecked by a single pairwise term. Antisymmetry forces the
wavefunction into a determinant (§2); the variational principle (§3) tells us to
pick the *best* determinant; and "best" turns out to mean the orbitals satisfy the
Fock equations (§4), in which the feared repulsion has been replaced by an average
field plus an exchange term that antisymmetry demands. Cast in a basis, that
becomes a matrix eigenproblem solved self-consistently (§5), and the molecule's
symmetry breaks it into the very blocks — $a_1$, $b_2$, $b_1$ — we had labelled by
hand on the water diagram. The eigenvalues are the orbital energies; Koopmans (§6)
turns them into the ionization energies we measured, well enough for the outer
valence and visibly worse for the deep core. And the gap between this whole
construction and reality (§7) is the correlation energy, the exact price of having
replaced "what the other electrons are doing right now" with "what they do on
average."

That is the one story. The variational principle says *get as low as you can*; the
single determinant says *but only within the mean field*; and the correlation
energy is the distance between those two commands. The water diagram we read off
the page in the previous post was the output of this machine, run once and rounded.
Knowing the machine, the same diagram reads differently: not a set of facts to
memorize, but the converged solution of an eigenvalue problem that the molecule's
own symmetry was kind enough to make small.

## References
