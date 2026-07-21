---
title: "Does force training move where Coulomb subtraction helps an H2+ neural potential?"
date: 2026-07-21
author: Peter Johnston
tags: quantum chemistry, neural networks, potential energy curves, H2+, force training, reproducibility
description: A matched neural-network experiment on the one-electron H2+ curve asks whether adding force labels moves the bond-distance cutoff at which subtracting the exact nuclear repulsion stops helping the fit. Force labels sharpen the advantage against the repulsive wall but move the crossover inward, the opposite of the predicted direction.
post-type: research
contribution: A matched energy-versus-energy-plus-force measurement of how force labels move the bond-distance cutoff at which exact 1/R subtraction stops helping an H2+ neural-network fit, which is not reported by Rana et al. or by my energy-only note.
contribution-type: untested regime
experiment: coulomb-force-training
og-image: /images/2026-07-21-does-force-training-move-the-coulomb-subtraction-crossover-hero.png
---

## Abstract

Rana, Manoj, Lourderaj, and Sathyamurthy, in *Artificial Neural Networks
Fitting of Potential Energy Curves and Surfaces: The 1/R Conundrum* (*J. Comput.
Chem.* **46**, 2025, e70220), fit molecular potentials by subtracting the exact
nuclear repulsion, fitting the smoother electronic energy, and restoring the
exact term afterward.[@Rana2025Conundrum] A companion note here measured, on the
one-electron H$_2^+$ curve, that this decomposition helps a small network only
on a fitting domain that reaches the short-range repulsive wall, and stops
helping once the domain begins beyond the minimum. That experiment fit energies
alone. Because the subtracted term is $1/R$ while the nuclear contribution to the
force is the steeper $1/R^2$, a natural question is whether training on forces as
well as energies moves the cutoff at which subtraction stops paying. I refit an
analytic minimal-basis LCAO H$_2^+$ curve with matched folds, seeds, and
budgets, under an energy-only loss and under an energy-plus-force loss, for a
direct total-energy target (Scheme A) and an electronic-energy target with exact
$1/R$ restoration (Scheme B). The energy-only crossover cutoff is
[energy_crossover_bohr]{.metric}~$a_0$. Under the energy-plus-force loss the
crossover is [force_crossover_bohr]{.metric}~$a_0$. The predeclared hypothesis —
that force labels push the crossover to a larger cutoff — was falsified: the
crossover moved to a smaller cutoff. Adding force labels widened the subtraction
advantage against the wall, where the median direct-fit error ran to
[ratio_force_015]{.metric} times the subtraction-fit error, while moving the
crossover inward — indicating that the range over which subtraction helps is set
by the energy target's short-range curvature rather than extended by the force
channel.

## Introduction

A neural network that fits a molecular potential energy curve must reproduce a
function that is smooth over most of its domain but rises steeply as two nuclei
approach, because the nuclear repulsion diverges as $1/R$. Behler and Parrinello
established the template of representing a potential energy surface with a neural
network,[@Behler2007] and a recurring practical difficulty is that this $1/R$
wall dominates the target's dynamic range and forces the network to spend
capacity on a term whose functional form is already known exactly. Rana and
co-workers named this the $1/R$ conundrum and proposed a direct remedy: at fixed
nuclei a potential separates as

$$
V(\mathbf R) = E_{\mathrm{el}}(\mathbf R) + V_{\mathrm{NN}}(\mathbf R),
\qquad
V_{\mathrm{NN}} = \sum_{A<B}\frac{Z_A Z_B}{R_{AB}},
$$

so one can subtract the exact $V_{\mathrm{NN}}$, fit the smoother electronic
energy $E_{\mathrm{el}}$, and add the exact term back afterward.[@Rana2025Conundrum]

A preceding note in this series
([where Coulomb subtraction helps](/posts/2026-07-18-where-coulomb-subtraction-helps.html))
took the one-electron H$_2^+$ curve as a controlled setting and asked not whether
the decomposition works but *where* it helps a small network. Its answer was a
crossover in bond distance: subtracting $1/R$ is a strong conditioning choice
when a single fit must cover the repulsive wall, and the advantage disappears
once the fitted domain starts beyond the equilibrium separation, where the
electronic energy and the total potential are comparably smooth targets. That
experiment fit energies only.

Potentials, though, are rarely fit for their own sake; the quantity that drives
dynamics is the force, $-\nabla V$. Fitting energies and forces together is
standard practice — Pukrittayakamee and co-workers fit a surface and its
gradients simultaneously with feed-forward networks,[@Pukrittayakamee2009] and
gradient labels are now understood to carry most of the information about a
potential's shape.[@Christensen2020Gradients] This is where the energy-only
crossover leaves a gap. The subtracted term is $V_{\mathrm{NN}} = 1/R$, but its
contribution to the force is $-\mathrm{d}(1/R)/\mathrm{d}R = 1/R^2$, which is
steeper still and concentrated even more tightly against the wall. If the
network in the direct scheme must now also reproduce that $1/R^2$ force, one
would predict its disadvantage near the wall to grow, so that the electronic-fit
scheme keeps its edge over a wider range of domains — the crossover should move
to a larger cutoff. Whether it actually does is not something either the parent
note or Rana et al. measured, because neither trained on forces.

I therefore state the hypothesis before the experiment: **under an
energy-plus-force loss the crossover cutoff — the smallest fitting-domain lower
bound at which subtracting $1/R$ no longer improves the fit — is larger than
under an energy-only loss.** The falsifier, fixed in advance, is that the first
cutoff at which the direct scheme matches or beats the subtraction scheme is
unchanged or moves to a smaller cutoff once force labels are added. Either
outcome is worth reporting: a crossover that moves would separate a specific
force-channel effect from the energy conditioning the parent note found, and a
crossover that does not move would show the conditioning benefit is a property of
the energy target alone.

## Computational Methods

**Reference curve.** The H$_2^+$ potential is generated analytically, not with an
electronic-structure package. Each proton carries one $1s$ Slater function with
exponent $\zeta = 1$; the symmetric (bonding, $1s\sigma_g$) molecular-orbital
energy follows from the closed-form two-centre integrals over $1s$
functions,[@atkins2010physical]

$$
S = e^{-R}\!\left(1 + R + \tfrac{R^2}{3}\right),\quad
J = \tfrac1R - e^{-2R}\!\left(1 + \tfrac1R\right),\quad
K = e^{-R}(1 + R),
$$

$$
E_{\mathrm{el}}(R) = -\tfrac12 - \frac{J + K}{1 + S},
\qquad
V(R) = E_{\mathrm{el}}(R) + \frac1R,
$$

in hartree, with $R$ the internuclear distance in bohr. This minimal-basis model
is deliberately crude: its minimum sits at $R_e = 2.49\,a_0$ with a binding
energy of $0.065$ hartree, further out and shallower than the exact H$_2^+$
values, and it is **not** the UHF/aug-cc-pV5Z curve of the parent note. It is
used here as a self-contained target with the qualitative structure the question
needs — a $1/R$ repulsive wall, a bound minimum, and dissociation to $-\tfrac12$
hartree — so that the two loss functions are compared on one and the same curve.
The analytic derivative $\mathrm{d}V/\mathrm{d}R$, used to build force labels, is
verified against complex-step differentiation to a maximum relative error below
$10^{-10}$ across the grid, and the tabulated integral values are checked at
$R = 2\,a_0$. The curve is evaluated at 401 geometrically spaced distances from
$0.15$ to $20\,a_0$.

**Two schemes.** Scheme A fits the total potential $V(R)$ directly. Scheme B fits
the electronic energy $E_{\mathrm{el}}(R) = V - 1/R$ and restores the exact $1/R$
term — and, under force training, the exact $1/R^2$ nuclear force — before the
prediction is scored. Both schemes are always scored on the total potential.

**Two losses.** The energy-only loss is the mean squared error of the
standardised value target. The energy-plus-force loss adds the mean squared error
of the standardised slope, $L = \mathrm{MSE}(\text{value}) + \lambda\,
\mathrm{MSE}(\text{slope})$, with $\lambda = 1$ fixed in advance. Each scheme
standardises and differentiates its own target: Scheme A trains on $V$ and
$\mathrm{d}V/\mathrm{d}R$, Scheme B on $E_{\mathrm{el}}$ and
$\mathrm{d}E_{\mathrm{el}}/\mathrm{d}R$, and the exact nuclear terms enter Scheme
B only at scoring. Slopes are expressed in each target's standardised coordinates
so the two error channels are comparable.

**Network and optimisation.** Both schemes use a one-hidden-layer network with 15
$\tanh$ units and a linear readout, float64 arithmetic, Xavier-uniform weights,
and zero biases. The single input $R$ is standardised from the training-fold mean
and standard deviation; each target is standardised from its own training-fold
moments and returned to hartree before scoring. Optimisation is full-batch Adam
$(0.9, 0.999, 10^{-8})$ for 20,000 steps with cosine learning-rate decay from
$10^{-3}$ to $10^{-5}$ and no regularisation; the checkpoint with the lowest
training objective is retained. This matched, paired construction follows the
comparison discipline of the earlier neural-network notes in this series
([why the two SIREN conventions train differently](/posts/2026-07-17-why-the-two-siren-conventions-train-differently.html)).

**Gradients.** The network is small enough that the value and slope gradients with
respect to every weight are written analytically, including the mixed
second-derivative terms the slope loss introduces. They are checked against
central finite differences to a maximum relative error below $10^{-5}$ before the
sweep runs, and a batched trainer that fits all 25 networks of a cutoff at once is
checked against the unbatched reference on random inputs.

**Cutoffs, folds, seeds, and the metric.** For each lower cutoff $R_{\min}$ in
$\{0.15, 0.25, 0.40, 0.70, 1.00, 1.50, 2.00, 3.00\}\,a_0$, only points with
$R \ge R_{\min}$ are retained; each cutoff defines its own fit and evaluation
domain. Five stratified folds are assigned once on the full ordered grid with a
seed-70220 permutation inside each consecutive five-point block and preserved
across cutoffs. Five initialisation seeds (11, 29, 47, 71, 101) are used; within a
fold and seed, Schemes A and B and the two losses all start from bit-identical
weights. Every eligible point receives one out-of-fold prediction; the primary
metric is the pooled out-of-fold energy RMSE in cm$^{-1}$. Per seed the paired
ratio is $\mathrm{RMSE}_A/\mathrm{RMSE}_B$; the reported value at each cutoff is
the median over the five seeds. The crossover cutoff is the smallest $R_{\min}$
whose median ratio is at most one.

**First-hand scope.** Every number here is generated by the committed NumPy code;
no program, code, or data from Rana et al. was used, and this is an independent
controlled test on a different H$_2^+$ curve, not a numerical reproduction of
their tables. The experiment runs on a computer with no living subjects. It is
end-to-end reproducible: the deterministic, seeded sweep regenerates the results
table, and the metrics projection is regenerated and fingerprint-verified from
it.

## Results

Table 1 lists the median paired A/B out-of-fold energy-RMSE ratio at every cutoff
under both losses, and Figure 1 plots them.

| $R_{\min}$ (bohr) | energy-only A/B | energy+force A/B |
| --- | --- | --- |
| 0.15 | [ratio_energy_015]{.metric} | [ratio_force_015]{.metric} |
| 0.25 | [ratio_energy_025]{.metric} | [ratio_force_025]{.metric} |
| 0.40 | [ratio_energy_040]{.metric} | [ratio_force_040]{.metric} |
| 0.70 | [ratio_energy_070]{.metric} | [ratio_force_070]{.metric} |
| 1.00 | [ratio_energy_100]{.metric} | [ratio_force_100]{.metric} |
| 1.50 | [ratio_energy_150]{.metric} | [ratio_force_150]{.metric} |
| 2.00 | [ratio_energy_200]{.metric} | [ratio_force_200]{.metric} |
| 3.00 | [ratio_energy_300]{.metric} | [ratio_force_300]{.metric} |

**Table 1.** Median paired A/B out-of-fold energy-RMSE ratio at each fitting-domain
lower cutoff, under the energy-only and energy-plus-force losses. A value above
one is a cutoff at which the median direct-fit (Scheme A) RMSE exceeds the median
Coulomb-subtraction (Scheme B) RMSE.

Under the energy-only loss the median ratio ran from [ratio_energy_015]{.metric}
at $R_{\min} = 0.15\,a_0$ to [ratio_energy_300]{.metric} at $3.00\,a_0$, first at
or below one at a cutoff of [energy_crossover_bohr]{.metric}~$a_0$. Under the
energy-plus-force loss the median ratio ran from [ratio_force_015]{.metric} at
$0.15\,a_0$ to [ratio_force_300]{.metric} at $3.00\,a_0$, first at or below one at
[force_crossover_bohr]{.metric}~$a_0$ (Figure 1). At $R_{\min} = 0.15\,a_0$ under
the energy-only loss the median Scheme A RMSE was [rmse_a_energy_015_cm]{.metric}
cm$^{-1}$ and the median Scheme B RMSE was [rmse_b_energy_015_cm]{.metric}
cm$^{-1}$.

<figure>
  <img src="/images/2026-07-21-does-force-training-move-the-coulomb-subtraction-crossover-hero.png" alt="Log-log plot of the median A/B out-of-fold energy-RMSE ratio against the fitting-domain lower cutoff. Both curves start far above one at the shortest cutoff, with the energy-plus-force curve higher, and both fall below one at the largest cutoffs, the energy-plus-force curve dropping below one at a smaller cutoff than the energy-only curve.">
</figure>

**Figure 1.** Median paired A/B out-of-fold energy-RMSE ratio versus fitting-domain
lower cutoff for the energy-only loss (dark circles) and the energy-plus-force
loss (light squares); the dashed line marks a ratio of one. **A** marks the
shortest cutoff, $R_{\min} = 0.15\,a_0$; **B** marks the smallest cutoff at which
the energy-plus-force ratio is at most one, $R_{\min} = 2.00\,a_0$; **C** marks
the smallest cutoff at which the energy-only ratio is at most one,
$R_{\min} = 3.00\,a_0$.

## Discussion

The predeclared hypothesis was **falsified**. Force training did move the
crossover, but in the direction the registered falsifier named: the smallest
cutoff at which the direct fit caught the subtraction fit fell from
[energy_crossover_bohr]{.metric}~$a_0$ under the energy-only loss to
[force_crossover_bohr]{.metric}~$a_0$ under the energy-plus-force loss. The range
of domains over which subtracting $1/R$ helps did not widen when force labels
were added; it narrowed.

The reasoning behind the hypothesis was not entirely wrong — it accounted for one
half of the picture and missed the other. Against the wall, adding forces did make
the direct scheme much worse relative to subtraction: at $R_{\min} = 0.15\,a_0$ the
median ratio rose from [ratio_energy_015]{.metric} under energy-only training to
[ratio_force_015]{.metric} under energy-plus-force training. A network asked to
reproduce the $1/R^2$ nuclear force directly, on a domain that reaches the wall,
pays a steep price that the subtraction scheme sidesteps by restoring that force
exactly. That is the $1/R^2$ intuition, and it holds. What the intuition missed is
what happens past the minimum. On the wider domains the direct scheme improved
*faster* under force labels than the subtraction scheme did, so the two curves in
Figure 1 crossed sooner rather than later. The gradient information that hurts the
direct fit at the wall helps it once the wall is excluded, because a smooth total
potential and its smooth force are then an easier joint target than the electronic
energy plus a restored term. The location of the crossover is governed by the
energy target's short-range curvature; the force channel sharpens the contrast at
the wall without extending the reach of the subtraction advantage.

Two consistency checks are worth stating and one caution. First, the energy-only
near-wall errors here — Scheme A [rmse_a_energy_015_cm]{.metric} cm$^{-1}$ and
Scheme B [rmse_b_energy_015_cm]{.metric} cm$^{-1}$ at $R_{\min} = 0.15\,a_0$ — sit
close to the values the parent note reported from an independent UHF/aug-cc-pV5Z
curve (about 26,270 and 569 cm$^{-1}$). I read that as an incidental agreement
rather than a reproduction: both fits are dominated by the shared $1/R$ wall
shape, and the two curves differ everywhere else. Second, and for the same reason,
the *absolute* crossover location differs from the parent note, whose energy-only
crossover fell between $0.7$ and $2.0\,a_0$; this cruder minimal-basis curve has
its minimum further out at $2.49\,a_0$ and is shallower, so its crossover sits
further out too. That difference is a property of the curve I chose here, not a
disagreement with the parent measurement. The caution is that Scheme B is handed
the exact $1/R^2$ force at scoring, an advantage a real system with only
approximate forces would not enjoy; the comparison here isolates the conditioning
question and is not a claim about production force fields.

For someone fitting a small potential with energies and forces, the practical
reading is narrow and, I think, useful: subtracting the known nuclear repulsion is
most valuable exactly when a single fit must span the repulsive wall, and adding
force labels raises that value rather than lowering it. But the benefit does not
carry to domains that begin past the minimum simply because forces are in the
loss — there the direct fit is at least as good. None of this establishes how the
effect behaves away from the assumptions made here, and the next section names
where I think it is most likely to break.

## Conclusion

On this one-electron H$_2^+$ curve, the cutoff at which subtracting the exact
$1/R$ stops helping a small network is set by the energy target, and adding force
labels sharpens the subtraction advantage against the repulsive wall while moving
the crossover inward. The value of subtracting a known singular term is a
short-range, energy-conditioning effect that force training amplifies locally and
does not extend in range.

The falsified hypothesis leaves a sharper question. The crossover moved inward at a
single force weight, $\lambda = 1$; whether that inward shift is monotonic in
$\lambda$, or whether at large force weight the direct scheme's near-wall failure
ever re-extends the range over which subtraction wins, is unmeasured. The next
experiment sweeps the force weight $\lambda$ across several decades on this same
curve and tracks the crossover cutoff as a function of it, with a finer cutoff grid
so the crossover is bracketed rather than snapped to a grid point. A curve whose
high- and low-fidelity branches force the nonlinear part of the network to carry
the fit, rather than an affine branch, would test whether the effect survives when
the direct scheme cannot lean on a smooth total potential.

## References
