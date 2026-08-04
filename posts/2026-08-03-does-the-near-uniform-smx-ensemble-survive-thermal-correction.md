---
title: "Does Blackmon and Closser's near-uniform sulfamethoxazole ensemble survive a thermal correction?"
date: 2026-08-03
author: Peter Johnston
tags: quantum chemistry, conformers, thermochemistry, sulfamethoxazole, xtb, reproducibility
description: Blackmon and Closser report four solvated sulfamethoxazole minima with 298 K populations of roughly one quarter each, assigned from electronic energies alone. This note is an independent extension that adds a preregistered GFN2-xTB thermochemical correction to their published energies. The near-uniform ensemble does not survive the correction under either registered arm, while the published global minimum keeps its place.
post-type: research
contribution: A preregistered 298.15 K thermochemical correction to the four solvated sulfamethoxazole minima of Blackmon and Closser, and the conformer populations that result from it, which are not in Blackmon and Closser.
contribution-type: unplotted line
experiment: smx-conformer-thermochemistry
---

## Abstract

Blackmon and Closser, in *Determination of Ground-State Structure and
Electronic Excitations of Sulfamethoxazole Using Density Functional Theory*
(*Comput. Theor. Chem.* **1264**, 2026, 115931), optimize sulfamethoxazole to
four unique solvated minima, A–D, spanning 0.202 kJ/mol, and assign 298 K
Boltzmann populations of roughly one quarter each from electronic energies
alone.[@Blackmon2026] Their paper states that frequency calculations confirmed
all four structures as minima, but neither the frequencies nor a thermally
corrected ordering appears in the paper or its supplement. This note adds that
correction independently, under a protocol frozen before the first
calculation: each published geometry is re-optimized with GFN2-xTB in ALPB
water, a harmonic Hessian is computed, and the xTB thermochemical correction
is added to the source's own electronic energies, in two arms that differ only
in the low-frequency rotor cutoff. The preregistered hypothesis — that the
near-uniform ensemble is robust, with no conformer's population moving more
than 10.0 percentage points and the effective conformer count staying at or
above 3.5 in both arms — was falsified. The maximum population shift is
[rrho_max_population_shift_pp]{.metric}\ percentage points in the pure-RRHO
arm and [mrrho50_max_population_shift_pp]{.metric}\ percentage points in the
50 cm^−1^ modified-RRHO arm; conformer A's population moves from
[source_population_a]{.metric} on the source's electronic energies to
[rrho_population_a]{.metric} and [mrrho50_population_a]{.metric} in the two
arms, and the effective conformer count falls from four to
[rrho_effective_conformer_count]{.metric} and
[mrrho50_effective_conformer_count]{.metric}. Conformer A remains the lowest
structure throughout. The corrected populations bound the robustness of the
published electronic-only population vector; they do not determine the
source's unreported same-level thermochemistry.

## Introduction

Conformer populations are equilibrium quantities, so the observable mixture of
a flexible molecule follows from free energies, not electronic energies. For
minima separated by more than a few kJ/mol the distinction rarely changes a
qualitative story, but zero-point and thermal contributions routinely differ
between conformers of one molecule by tenths of a kJ/mol and more — the
treatment of low-frequency torsions alone can move relative free energies by
that much, which is why modified rigid-rotor–harmonic-oscillator schemes exist
at all.[@Grimme2012]

Blackmon and Closser optimize the antibiotic sulfamethoxazole (SMX) to four
unique minima, A–D, in implicit water, and find them separated by
0.202 kJ/mol in total, with A lowest by 0.137 kJ/mol over B.[@Blackmon2026]
Their Table 1 assigns 298 K Boltzmann populations of 26.3, 24.9, 24.7 and
24.2%, and its footnote states that zero-point and thermal corrections are
excluded. Recomputing a Boltzmann factor over the supplement's electronic
energies reproduces those populations — the values enter this note's tables as
[source_population_a]{.metric}, [source_population_b]{.metric},
[source_population_c]{.metric} and [source_population_d]{.metric} — so the
published populations are an electronic-energy projection of a
0.2 kJ/mol-spaced quartet at a temperature where $kT$ is 2.48 kJ/mol. The
paper reports that frequency calculations were run to confirm all four
structures are minima, so same-level frequencies existed; a corrected ordering
is the analysis their own data supports that the paper never prints.

An energy separation this far below the typical conformer-to-conformer spread
of thermal corrections could resolve either way. The corrections could be as
degenerate as the electronic energies — four conformers of one molecule share
most of their vibrational structure, and near-perfect cancellation is a
reasonable default expectation — or they could exceed the electronic span by
an order of magnitude and redraw the ensemble. I therefore state the
hypothesis before the experiment, on the side of the published picture:
**under an independently calculated 298.15 K thermochemical correction, the
near-uniform ensemble is robust — in both registered arms, no conformer's
population moves more than 10.0 percentage points from the source's
electronic-energy baseline, and the effective conformer count
$1/\sum_i p_i^2$ stays at or above 3.5.** The falsifier, fixed in advance:
both arms fail at least one of those gates. If the arms disagree, or any
preregistered method-fidelity check fails, the result is inconclusive rather
than repaired. Either outcome is worth publishing: robustness would bound how
much the near-degeneracy matters for anyone selecting a single SMX conformer
for excited-state work, and a falsification would mean the published
population vector is a property of the electronic surface rather than of the
molecule at temperature.

## Computational Methods

**Source inputs.** The A–D Cartesian coordinates and electronic energies were
transcribed from the source's supplement and frozen, with checksums, in the
experiment's `inputs.json` before any calculation ran. The published relative
energies reproduce from those transcribed values to ±0.002 kJ/mol. The source
authors' program (Q-Chem), their PCM solvation, and their excited-state
calculations were not used or reproduced; nothing in this note reruns any
calculation of theirs. The atom order of the rendered B and C coordinate
lists differs from the article's numbering in the position of one sulfonyl
oxygen; that atom is moved ahead of the hydrogens to restore the common
order, without changing any coordinate.

**Protocol.** The full protocol was frozen in the experiment's
`PREREGISTRATION.md` before the first SMX calculation. For each conformer and
each arm: (1) optimize from the source geometry with GFN2-xTB 6.7.1 in ALPB
water, tight convergence, SCC accuracy 0.2, single-threaded;[@Bannwarth2019;
@Ehlert2021] (2) compute the numerical Hessian on the optimized structure;
(3) retain the thermochemical free-energy correction
$G_\mathrm{xTB} - E_\mathrm{xTB}$ at 298.15 K; (4) form the composite free
energy

$$
G_i \;=\; E_i^{\mathrm{source\ DFT}} \;+\;
\bigl[\,G_i^{\mathrm{xTB}} - E_i^{\mathrm{xTB}}\,\bigr],
$$

and (5) compute normalized Boltzmann populations at 298.15 K. The two arms
differ only in xTB's low-frequency rotor cutoff: `rrho` uses
$s_\mathrm{thr} = 0$ cm^−1^ (pure RRHO) and `mrrho50` uses
$s_\mathrm{thr} = 50$ cm^−1^ (Grimme's modified-RRHO
interpolation).[@Grimme2012] The imaginary-mode threshold is −20 cm^−1^, the
frequency scale factor 1.0. Native all-xTB free energies are retained as a
secondary sensitivity result and do not enter the verdict.

**Method-fidelity gate.** The verdict is automatically inconclusive if any run
terminates abnormally, any optimized structure has a mode below −20 cm^−1^,
any A–D pair of optimized structures falls below 0.10 Å heavy-atom aligned
RMSD in either arm, or the two arms' optimized geometries for one conformer
differ by more than 0.02 Å heavy-atom aligned RMSD.

**Environment.** The registered run executed 2026-07-25 on macOS (Darwin
25.5.0, Apple M1, arm64) with CPython 3.14.6, NumPy 2.5.0, and conda-forge
xTB 6.7.1, serialized to a single thread throughout; the explicit conda lock
is committed. The analysis layer regenerates deterministically from the
committed raw xTB outputs without rerunning quantum chemistry, and its
canonical serialization rounds floats to 12 significant digits so the
regeneration check is architecture-independent; the committed analysis was
re-verified on linux-x86_64. The bars in Figure 1 are emitted from the same
canonical result rather than typed by hand, and a check mode fails if the
committed figure and the canonical populations disagree. The experiment bundle — preregistration, frozen
inputs, raw outputs, runner, analysis, and metrics — is published under
[`research/smx-conformer-thermochemistry/`](/research/smx-conformer-thermochemistry/README.md).
The reproducibility level this earns is end-to-end reproducible on osx-arm64,
and analysis-reproducible from the committed outputs elsewhere.

## Results

Every registered method-fidelity check passed: all eight conformer/arm runs
terminated normally, no optimized structure has a mode below −20 cm^−1^, all
optimized A–D pairs are separated by at least 0.10 Å heavy-atom RMSD in both
arms, and the two arms' optimized geometries agree within 0.02 Å for each
conformer.

Table 1 reports the composite populations. The maximum absolute population
shift from the source baseline is
[rrho_max_population_shift_pp]{.metric}\ percentage points in the `rrho` arm
and [mrrho50_max_population_shift_pp]{.metric}\ percentage points in the
`mrrho50` arm, against the registered ceiling of 10.0. The effective
conformer count is [rrho_effective_conformer_count]{.metric} in the `rrho`
arm and [mrrho50_effective_conformer_count]{.metric} in the `mrrho50` arm,
against the registered floor of 3.5. The `rrho` arm fails both gates; the
`mrrho50` arm fails the shift gate and passes the count gate. Both arms fail
at least one gate.

| Population at 298.15 K | Source electronic | `rrho` | `mrrho50` |
| --- | ---: | ---: | ---: |
| A | [source_population_a]{.metric} | [rrho_population_a]{.metric} | [mrrho50_population_a]{.metric} |
| B | [source_population_b]{.metric} | [rrho_population_b]{.metric} | [mrrho50_population_b]{.metric} |
| C | [source_population_c]{.metric} | [rrho_population_c]{.metric} | [mrrho50_population_c]{.metric} |
| D | [source_population_d]{.metric} | [rrho_population_d]{.metric} | [mrrho50_population_d]{.metric} |

**Table 1.** Boltzmann populations of the four SMX conformers at 298.15 K:
from the source's electronic energies, and from the composite free energies
of the two registered thermochemistry arms.

```tikzpicture
\begin{tikzpicture}[font=\small]
  \begin{axis}[
    width=12.4cm, height=6.4cm,
    ybar, bar width=9pt,
    ymin=0, ymax=50,
    symbolic x coords={A,B,C,D},
    xtick=data,
    axis lines=left,
    ylabel={population (\%)},
    ylabel style={font=\fontsize{6.6}{8}\selectfont},
    xticklabel style={font=\fontsize{6.6}{8}\selectfont},
    yticklabel style={font=\fontsize{6}{7}\selectfont},
    ymajorgrids, grid style={black!12, line width=0.3pt},
    axis line style={black!55, line width=0.35pt},
    tick style={black!55},
    legend style={font=\fontsize{5.8}{7}\selectfont, draw=black!30,
                  at={(0.98,0.95)}, anchor=north east},
    legend cell align=left,
  ]
    \addplot[draw=black!50, fill=black!20, line width=0.2pt]
      coordinates {(A,26.3) (B,24.9) (C,24.7) (D,24.2)};
    \addplot[draw=blue!55!black, fill=blue!35!white, line width=0.2pt]
      coordinates {(A,45.9) (B,30.8) (C,12.2) (D,11.1)};
    \addplot[draw=blue!55!black, fill=blue!70!black, line width=0.2pt]
      coordinates {(A,39.0) (B,25.7) (C,17.7) (D,17.6)};
    \legend{source electronic, rrho, mrrho50}
  \end{axis}
\end{tikzpicture}
```

**Figure 1.** The populations of Table 1 as grouped bars: the source's
electronic-energy baseline in gray, the two composite thermochemistry arms in
blue.

The composite free-energy ordering is A < B < C < D in both arms, with C and D
separated by 0.02 kJ/mol in the `mrrho50` arm and 0.24 kJ/mol in the `rrho`
arm. Conformer A has the lowest composite free energy in both arms. Among the
secondary sensitivity results, the native all-xTB free energies also order the
re-optimized structures A < B < C < D in both arms, matching the source's
electronic ordering, while the native xTB electronic energies alone order them
B < C < A < D, spanning 0.148 kJ/mol.

As a separate audit of the transcribed source data: all eight
relaxation-energy magnitudes recomputed from the supplement's energies agree
with the source's main-table values to within 0.005 kJ/mol, and the
recomputed signs differ from the table footnote's stated
$E_\mathrm{vertical} - E_\mathrm{adiabatic}$ formula in
[source_relaxation_sign_mismatch_count]{.metric} of the eight rows.

## Discussion

The preregistered hypothesis was **falsified**. Both registered arms exceeded
the 10.0-percentage-point ceiling on population shift, and the pure-RRHO arm
additionally dropped the effective conformer count below the registered floor
of 3.5. The registered decision rule reads two failing arms as a falsification
rather than an inconclusive split, and both arms failed.

What this does and does not establish needs stating carefully, in both
directions. The falsified quantity is the *robustness of the published
population vector* to an independently calculated thermochemical correction —
not the source's own thermochemistry. The corrections here are GFN2-xTB
free-energy corrections evaluated on GFN2-xTB re-optimized geometries in ALPB
water; the source's surface is a hybrid-DFT PCM surface, and its harmonic
frequencies, which the paper states were computed, were never published for
comparison. A same-level correction could well land differently in detail.
What the experiment establishes is narrower: the thermochemical term, at a
level of theory routinely used for exactly this purpose, is an order of
magnitude larger than the 0.202 kJ/mol electronic span it is being added to,
and it does not cancel across the quartet. A population statement inherited
from electronic energies spaced at a hundredth of $kT$ has no protection
against a correction of ordinary conformer-to-conformer size, and this one
did not survive it.

In the other direction, the correction *strengthens* the source's central
structural claim. Blackmon and Closser's contribution is the identification
of conformer A as the global minimum against earlier SMX studies that used a
different geometry; in both registered arms A keeps the lowest composite free
energy, by a margin far larger than its published 0.137 kJ/mol electronic
lead. Under this protocol the thermal correction promotes their preferred
structure from first-among-equals to a distinctly dominant conformer. The
rotor-cutoff comparison behaves as expected for corrections dominated by
low-frequency modes: the modified-RRHO arm, which damps the harmonic
entropy of exactly those modes, moves every population in the same direction
as pure RRHO but less far.

The sign audit is reported with our hands up. The recomputed relaxation-energy
magnitudes agree with the source's table to within transcription precision,
and the systematic sign opposition is consistent with the footnote's formula
being stated in the reverse order of the one applied — or with us misreading
which states the footnote's symbols name. It changes nothing in this note's
analysis, which uses only ground-state energies; it is recorded so that a
reader of the supplement is not surprised by it, and we invite correction if
the convention is ours to fix.

The main limitations are the ones the boundary conditions above imply. The
composite free energy mixes two electronic-structure levels, which is a
standard low-cost construction but not a controlled approximation to either
level alone. The corrections are harmonic-based with an empirical rotor
treatment, at 298.15 K only, for the four published minima only — no
conformer search was run, so a fifth minimum, if one exists, is outside the
frozen scope. And the populations are equilibrium statements about an
implicit-solvent model, not predictions of what any experiment on aqueous SMX
would measure.

## Conclusion

The published near-uniform SMX ensemble is a property of the electronic
surface, not a demonstrated property of the molecule at temperature: an
independent thermochemical correction concentrates the ensemble onto the
source's own global minimum in both registered arms. How far it concentrates
depends on the rotor treatment — pure RRHO roughly halves the C and D
populations, while the modified-RRHO arm cuts them by about a quarter.
For anyone using the paper's structures, the practical reading is that
selecting conformer A alone is better supported after thermal correction than
before it, while any workflow that weights all four conformers equally
inherits a population vector this experiment measured to be fragile.

The next experiment is the same-level version of this one: harmonic
frequencies for the four published geometries at a hybrid-DFT level with
implicit water — a calculation within reach of the tools used on this site —
to test whether the concentration of the ensemble survives when the
correction and the electronic energies come from one surface. That question
is now on the research shelf.

## References
