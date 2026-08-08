---
title: Why some atoms cost more than their neighbors
date: 2026-08-07
author: Peter Johnston
tags: quantum chemistry, periodic table, electronic structure, reproducibility
description: A fixed atomic calculation separates the cost of how an atom is represented from the cost of getting its self-consistent field to settle.
post-type: understanding
question: Why do chemically related and neighboring atoms take different amounts of computation under the same electronic-structure protocol?
experiment: periodic-compute-cost
og-image: /images/2026-08-07-periodic-compute-cost-hero.png
---

This note asks why chemically related and neighboring atoms can take different
amounts of computation under the same electronic-structure protocol. The answer
has two parts: the chosen model decides how much of the atom the computer must
represent, and the iterative solver decides how many times it must work on that
representation. A fixed panel of halogens, alkaline earths, transition metals,
and the Kr/Rb boundary makes those two parts visible without pretending to
price the whole periodic table.

## An atom becomes matrices

Atomic number enters the nuclear potential, but the dominant numerical work is
not proportional to atomic number alone. An electronic-structure program
expands each molecular orbital in a finite set of **basis functions**,

$$
\phi_i(\mathbf r)=\sum_{\mu=1}^{N_{\mathrm{bf}}}C_{\mu i}\chi_\mu(\mathbf r),
$$

then solves a matrix equation of dimension $N_{\mathrm{bf}}$,

$$
\mathbf F[\mathbf P]\mathbf C
=\mathbf S\mathbf C\boldsymbol\varepsilon.
$$

The Fock matrix $\mathbf F$ depends on the density $\mathbf P$ built from the
orbitals in $\mathbf C$, so the program rebuilds and solves until input and
output densities agree. That loop is the **self-consistent field (SCF)**.
Larger bases make those matrices and the work that constructs them larger;
finite-basis SCF is an iterative numerical problem, not a lookup table for an
element.[@HelgakerJorgensenOlsen2000; @Lehtola2020SCF]

A useful bookkeeping approximation is

$$
T_{\mathrm{SCF}}\approx n_{\mathrm{iter}}
\left[T_{\mathrm{build}}(N_e,N_{\mathrm{bf}})
+T_{\mathrm{solve}}(N_{\mathrm{bf}})\right]+T_{\mathrm{fixed}}.
$$

It is not a fitted timing law. It simply separates **work per cycle** from
**number of cycles**, while admitting fixed overhead. For the two survey
repeats here, the plotted time is
$\widetilde T=\operatorname{median}(T_0,T_1)=(T_0+T_1)/2$.
The survey compares **unrestricted Hartree–Fock (UHF)**, which gives the two
spin channels separate orbitals, with **unrestricted Kohn--Sham PBE
(UKS/PBE)**, a density-functional calculation with the same finite basis. Both
close an SCF loop. Figure 1 places the representation counts and their timings
side by side.

<figure>
  <img src="/images/2026-08-07-periodic-compute-cost-hero.png" alt="Two-panel plot of fourteen atoms grouped as halogens, alkaline earths, transition-metal comparisons, and the krypton-rubidium boundary. The left panel compares explicit electrons with basis functions. The right compares UHF and PBE wall time on a logarithmic axis, with iodine and iron marked as PBE attempts that reached the cycle cap.">
</figure>

**Figure 1.** The left panel follows explicit-electron and spherical def2-SVP
basis-function counts; the right follows median two-repeat UHF and PBE
calculation time on a logarithmic axis. **A** marks the Kr/Rb effective-core
seam. **B** and **C** mark I/PBE and Fe/PBE reaching the fixed 80-cycle cap;
their elapsed times are censored failed attempts, not completed timings.

## The core can disappear from the calculation

For an all-electron calculation, $N_e=Z$. With an **effective core potential
(ECP)**,

$$
N_e^{\mathrm{explicit}}=Z-N_{\mathrm{core}}^{\mathrm{ECP}}.
$$

The def2-SVP setup used here is all-electron through Kr, then uses a 28-electron
core for Rb, Sr, and I.[@Weigend2005Balanced] Crossing from Kr to Rb therefore
raised $Z$ from 36 to 37 while the represented electron count fell from
[kr_explicit_electrons]{.metric} to [rb_explicit_electrons]{.metric} and the
basis count fell from [kr_basis_functions]{.metric} to
[rb_basis_functions]{.metric}. Among the repeated survey methods, Rb took
[rb_uhf_time_decrease]{.metric} less wall time at UHF and
[rb_pbe_time_decrease]{.metric} less at PBE. Its single second-order
M{ø}ller–Plesset (MP2) attempt took [rb_mp2_time_decrease]{.metric} less
than Kr's. The largest repeat-to-repeat range among successful survey pairs,
defined as $(T_{\max}-T_{\min})/\widetilde T$, was
[max_successful_survey_repeat_range]{.metric}.

That reversal is not a claim that Rb is intrinsically cheaper than Kr. It says
the code was asked to represent less of Rb explicitly under this basis/ECP
choice. “Cost of an element” already contains a modeling decision before the
solver begins.

## Equal-sized matrices can take unequal paths

Representation size is not enough. Cr, Mn, Fe, and Zn each used
[transition_basis_functions]{.metric} basis functions, but their PBE SCF paths
ended at [cr_pbe_cycles]{.metric}, [mn_pbe_cycles]{.metric},
[fe_pbe_cycles]{.metric}, and [zn_pbe_cycles]{.metric} cycles. Each of the
[fe_pbe_unconverged_attempt_count]{.metric} Fe/PBE attempts reached the cap
without convergence. Each of the [i_pbe_unconverged_attempt_count]{.metric}
I/PBE attempts did the same at [i_pbe_cycles]{.metric} cycles.

SCF equations can possess several stationary solutions and can oscillate or
stall, especially around small gaps and competing occupations.[@Lehtola2020SCF]
Those facts explain why iteration count is a separate cost axis; they do not
diagnose these two failures. UHF converged for both atoms, and the other ECP
atoms converged under PBE. The narrow statement earned here is that these
particular UKS/PBE calculations did not settle under the fixed initial guess,
grid, threshold, and cycle cap.

## A method name is not a stopwatch

PBE, MP2, and CCSD(T) are different approximation families, not consecutive
rungs of one runtime ladder. PBE is a generalized-gradient density functional;
MP2 is second-order many-electron perturbation theory; CCSD(T) adds a
perturbative triples correction to coupled cluster with singles and
doubles.[@Perdew1996PBE; @MollerPlesset1934; @Raghavachari1989]

On the [light_method_atom_count]{.metric} light atoms given all four methods,
CCSD(T) took [ccsd_t_over_uhf_min]{.metric}–[ccsd_t_over_uhf_max]{.metric} times
the UHF wall time. Yet PBE took longer than CCSD(T) in
[pbe_slower_than_ccsd_t_count]{.metric} of those cases. That does not make PBE
the more expensive method in general. At these sizes, the reversal could
reflect grid work, fixed setup, or solver details; this run did not separate
them. The calculation did not earn a scaling exponent, so none is fitted.

## Reproducibility

The fixed panel contained [atom_count]{.metric} neutral atoms and
[job_count]{.metric} fresh, single-threaded attempts. UHF and UKS/PBE ran
twice for every atom; UMP2 ran once for the halogens, alkaline earths, and
Kr/Rb; UCCSD(T) ran once for F, Cl, Be, and Mg. Of those attempts,
[ok_job_count]{.metric} returned `ok` and
[unconverged_job_count]{.metric} reached the SCF cap. Each calculation used
spherical def2-SVP functions, the nominal Hund-rule spin, no point-group
symmetry or density fitting, a `minao` guess, and an 80-cycle SCF limit.

The run used CPython 3.12.3, PySCF 2.13.1, NumPy 2.5.1, and one Intel
i7-1165G7 laptop core per child process. PySCF supplied the UHF, UKS, UMP2, and
UCCSD(T) implementations.[@Sun2020PySCF] The [earlier Hartree–Fock
note](/posts/2026-07-01-hartree-fock-and-the-correlation-gap.html) follows one
SCF loop in more detail.

`sweep.py` embeds the atomic specifications; there is no external computational
dataset. The append-only `results/runs.jsonl` is the canonical output.
`analyze.py` validates the fixed job matrix, writes `results/summary.json`, and
regenerates Figure 1; `generate-metrics.mjs` projects the typed values used in
this post. Running `python3 research/periodic-compute-cost/analyze.py --check`
under Matplotlib 3.11.1 reproduces the committed summary and figure. Running
`node research/periodic-compute-cost/generate-metrics.mjs --check` and
`node scripts/verify-metrics.mjs` checks the projection and its source
fingerprints. That makes the note **analysis-reproducible** from its committed
outputs; it does not make subsecond laptop timings hardware-independent.

## Where the model stops

This probe times one finite-basis energy calculation, not “understanding an
element” in the spectroscopic sense. The nominal spin does not establish the
ground atomic term, the ECP seam changes the model as well as the atom, and no
all-electron Rb control isolates the ECP's causal share. The correlated-method
timings are single attempts on four tiny atoms. The PBE failures were neither
retried nor diagnosed with occupation or stability analyses, so they mean only
that the frozen protocol failed to converge.

A controlled next step would hold the atom fixed while changing its core
treatment, or hold the representation fixed while auditing alternative SCF
occupations. This note stops before either expansion. Its narrower answer is
enough: atomic number does not set computational cost by itself. The
representation fixes the size of each numerical problem; the solver path fixes
how many times that problem is paid for.

## References
