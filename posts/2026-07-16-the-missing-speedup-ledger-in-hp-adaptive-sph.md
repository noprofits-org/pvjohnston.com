---
title: "The missing speedup ledger in h/p-adaptive SPH"
date: 2026-07-16
author: Peter Johnston
tags: fluid dynamics, numerical methods, SPH, performance, reproducibility
description: "Joining two accuracy statements to the paper's timing table puts a number on the benefit of h/p-adaptive SPH: 3.90x and 6.16x speedups for its two explicit equal-accuracy vortex-ring comparisons."
contribution: An equal-accuracy cost ledger for the paper's two explicit vortex-ring resolution matches, which is not in Ricci, Vacondio, and Fourtakas (2026).
contribution-type: quantification
---

## Abstract

An h/p-adaptive smoothed particle hydrodynamics method combines low-order
Lagrangian regions with high-order Eulerian regions and reports computational
savings of up to an order of magnitude. The paper gives the ingredients for a
direct audit of that claim in its three-dimensional vortex-ring case, but leaves
them in two places: the prose identifies two equal-accuracy resolution pairs,
while Table 3 reports their run times. I joined those values and computed the
cost ratio at matched accuracy. The two comparisons return speedups of 3.90 and
6.16, corresponding to runtime reductions of 74.39% and 83.78%. The hypothesis
that at least one explicit pair reaches a tenfold speedup is falsified for this
case. The broader claim remains inconclusive because the paper does not tabulate
an equal-accuracy pair for its finest vortex-ring run or the error-time values
behind its cylinder plot.

## Introduction

Smoothed particle hydrodynamics (SPH) earns its keep where meshes become
awkward: free surfaces, fragmentation, and moving boundaries. Its Lagrangian
particles follow those features naturally, but the standard method pays for
that flexibility with low-order convergence. Ricci, Vacondio, and Fourtakas
combine two descriptions instead. Lagrangian subdomains remain where motion and
interfaces require them; fixed, high-order Eulerian subdomains cover smooth
interior flow. Particle spacing supplies the h-adaptivity and kernel order the
p-adaptivity.[@Ricci2026AdaptiveSPH]

That architecture makes a specific performance prediction. If fourth-order
regions reach a target error on a coarser particle distribution, then the fair
comparison is not two methods at the same resolution. It is the time required
by each method to reach the same accuracy. The paper makes that comparison in
words for a three-dimensional vortex ring: h/p at $R/\Delta x=10$ matches
Lagrangian SPH at $R/\Delta x=20$, and h/p at 20 matches Lagrangian SPH at 40.
It then gives normalized times for all six runs in a separate table and states
that the method can reduce cost by up to an order of magnitude.[@Ricci2026AdaptiveSPH]

The missing quantity is the division between those two pieces of evidence. My
hypothesis was that, if the order-of-magnitude claim is supported by the paper's
explicit vortex-ring matches, at least one matched pair will give
$t_\mathrm{Lagrangian}/t_{h/p} \geq 10$. A maximum below 10 is the predeclared
falsifier. I would have published the opposite result: a measured tenfold gain
would be a useful number that the paper had left implicit.

## Computational Methods

The input data were transcribed from the vortex-ring discussion and Table 3 of
Ricci, Vacondio, and Fourtakas.[@Ricci2026AdaptiveSPH] The two accuracy matches
were accepted exactly as the authors state them:

$h/p(10) \sim \mathrm{Lagrangian}(20)$

and

$h/p(20) \sim \mathrm{Lagrangian}(40)$,

where the number in parentheses is $R/\Delta x$. The normalized Lagrangian run
times at resolutions 10, 20, and 40 were 1.0, 4.1, and 26.2. The corresponding
h/p times were 1.05, 4.25, and 24.1. The normalization baseline was 621 s, the
reported time of the Lagrangian run at resolution 10 on an NVIDIA RTX 4090.

For each matched pair I calculated

$$
S = \frac{t_\mathrm{Lagrangian}}{t_{h/p}}
$$

and

$$
\mathrm{saving} = \left(1 - \frac{1}{S}\right)100\%.
$$

The arithmetic was run with CPython 3.9.6 on arm64 macOS 26.5.1, using
`decimal.Decimal` at 28-digit precision. There was no random sampling and no
seed. Elapsed times were reconstructed by multiplying each normalized time by
621 s; the speedup itself does not depend on that baseline.

The SPH simulations were **not** rerun here. In particular, I did not reproduce
the velocity and vorticity fields from which the authors judged the resolutions
to have matching accuracy. This experiment audits the arithmetic implied by the
published classifications and timings, not the classifications themselves.

## Results

The first time division returned
$4.1/1.05=3.904761904761904761904761905$. The second returned
$26.2/4.25=6.164705882352941176470588235$. The corresponding saved fractions
were 74.39024390243902439024390244% and
83.77862595419847328244274809%.

| Matched comparison | h/p normalized time | Lagrangian normalized time | h/p elapsed time (min) | Lagrangian elapsed time (min) | Speedup | Runtime reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| h/p 10 vs. Lagrangian 20 | 1.05 | 4.10 | 10.87 | 42.44 | 3.90x | 74.39% |
| h/p 20 vs. Lagrangian 40 | 4.25 | 26.20 | 43.99 | 271.17 | 6.16x | 83.78% |

**Table 1.** The paper's two stated equal-accuracy vortex-ring pairs joined to
its reported normalized run times, with elapsed times and cost ratios calculated
from those inputs.

Across the two rows of Table 1, the minimum speedup was 3.9048 and the maximum
was 6.1647. Neither printed ratio reached 10.

## Discussion

The hypothesis is **falsified for the paper's two explicit vortex-ring
comparisons**. Their reported numbers support a four- to sixfold equal-accuracy
speedup, not a tenfold one. That distinction is operationally large: the finer
matched pair reduces a reported 4.52-hour Lagrangian calculation to about 44
minutes, but it does not reduce it to 27 minutes.

The ledger also locates where the saving comes from. At the same resolution,
h/p costs 5.00% more at $R/\Delta x=10$, 3.66% more at 20, and 8.02% less at
40. The methods have roughly comparable same-resolution cost on this GPU. The
gain in Table 1 comes from reaching the authors' accuracy target on the coarser
particle distribution. It is a convergence benefit rather than a cheaper
update at fixed resolution.

This does not falsify every possible reading of the paper's broader “up to an
order of magnitude” statement. First, “an order of magnitude” is sometimes used
loosely for the scale of a tenfold change rather than an exact lower bound of
10. Second, the paper's impulsively started cylinder case includes an error
versus wall-clock plot whose underlying numbers are not tabulated. A pair on
that curve may reach tenfold at a fixed error. Third, the finest h/p vortex-ring
run at resolution 40 has no Lagrangian resolution-80 counterpart in Table 3, so
its equal-accuracy speedup cannot be priced from the reported data.

The accuracy match is also qualitative. The source describes velocity profiles
as “essentially superimposed” and compares the smoothness and position of
vorticity structures, but it does not assign the two matches a common numerical
error tolerance.[@Ricci2026AdaptiveSPH] A stricter threshold could move the
pairing, and repeated timings could move the cost ratios. Table 3 reports one
normalized value per configuration, with no timing variance, and its two- or
three-significant-figure inputs do not justify the long decimal tails printed by
the calculation. The defensible result is the rounded range: 3.90x to 6.16x.

The broader verdict is therefore **inconclusive**, while the narrow one is
falsified. For the explicitly matched vortex-ring evidence, “four- to sixfold”
is both more precise and still a substantial result.

## Conclusion

The demonstrated equal-accuracy budget for this vortex-ring calculation should
be set at roughly one-quarter to one-sixth of the corresponding Lagrangian
runtime. That is the new usable number: 74% to 84% of wall time removed by
trading particle resolution for kernel order.

The next experiment is to obtain the raw error and timing values behind the
cylinder study's Figure 8, declare an error tolerance before pairing runs, and
construct the complete cost-accuracy Pareto frontier. That would decide whether
the unpriced cylinder data contain a genuine tenfold comparison and replace a
headline bound with a curve a practitioner can budget against.

## References
