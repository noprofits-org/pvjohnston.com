---
title: "When pulse-independent trajectories lose nuclear accuracy: testing Galiana et al.'s open regime"
date: 2026-07-18
author: Peter Johnston
tags: nonadiabatic dynamics, surface hopping, electronic coherence, conical intersections, reproducibility
description: An independent benchmark of the conical-intersection regime left open by Galiana et al. finds that reusing nuclear paths can preserve electronic populations while doubling nuclear-centroid RMSE.
contribution: A measured relationship between coherence-overlapping surface hops and pulse-independent-trajectory error, including the finding that nuclear-centroid error crosses its predeclared tolerance before population error, which is not reported by Galiana et al. or Grell et al.
contribution-type: untested regime
og-image: /images/2026-07-18-pulse-independent-trajectories-hero.png
---

## Abstract

Galiana et al.'s 2026 paper, *Accounting for Electronic Coherences Induced by
Broadband Pulses by Using Pulse-Independent Trajectories*, proposes separating
an expensive nuclear simulation from the broadband pulse that prepares its
electronic state.[@Galiana2026PulseIndependent] Their published glycine test is
favorable: more than 90% of its surface hops occur after the initial electronic
coherences have almost disappeared. I independently tested the complementary
regime on a two-state, two-mode conical-intersection model. Full propagation
(FP) and electronic repropagation on an all-excited-state ensemble (RP-AXE)
used matched Wigner
samples, four seeds, 4,000 geometries per seed, and the projected-forces-and-
momenta decoherence correction. Moving the packet toward the intersection
raised the fraction of successful hops occurring before the coherence fell to
$1/e$ from 7.30% to 26.13%. Across five predeclared launch positions, that
fraction had Spearman correlation $\rho=0.90$ with each maximum FP--RP error.
The nuclear-centroid difference crossed its predeclared
$0.1\sigma_x$ tolerance at a 19.98% early-hop fraction; the upper-state and
product-side population differences remained below 0.05 throughout. Exact
grid dynamics sharpened the split: RP-AXE had the lower electronic-population
RMSE in all nine tested regimes, while FP had the lower product probability
and centroid RMSE in all nine. The preregistered center scan supports the
hypothesis over its reached 7.30--26.13% range; the adaptive kick extension
reached 26.29% without changing the qualitative result. The predeclared
high-overlap test remains inconclusive, because neither translating nor
directionally kicking the packet produced the required 50% early-hop fraction.
Population agreement alone can therefore overstate the quality of reused
nuclear trajectories before their ultimate validity boundary has been located.

## Introduction

Predictive photoinduced-dynamics simulations have to couple electronic and
nuclear motion without making a realistic molecule computationally
inaccessible. Exact wavepacket methods retain nuclear quantum effects but scale
poorly with dimensionality; trajectory surface hopping (TSH) scales much more
gently but replaces the nuclear wavepacket by an ensemble of classical paths
and requires an approximate treatment of decoherence.[@Faraji2024Photoinduced;
@Tully1990SurfaceHopping] Broadband pulses add another dependency. The pulse
can prepare a coherent superposition of electronic states, so changing its
frequency, bandwidth, or polarization can change both the electronic
coefficients and the nuclear forces from the first time step.

Grell and co-workers introduced the projected forces and momenta method with
momentum injection, **TSH-PFMi**, to damp electronic coherence from estimates
of the separating nuclear-wavepacket momenta and forces.[@Grell2025PFM]
In *Accounting for Electronic Coherences Induced by Broadband Pulses by Using
Pulse-Independent Trajectories*, Galiana and co-workers then proposed a way to
reuse the expensive part of that calculation. Their **RP-AXE** construction
first generates an all-excited-state ensemble of nuclear trajectories without
pump-generated coherence. For each new pulse, it repropagates the inexpensive
electronic coefficients along those frozen paths and combines the active-state
branches with pulse-dependent weights.[@Galiana2026PulseIndependent] A 2026
extension uses that construction to scan pulse parameters without recalculating
the glycine trajectories.[@Grell2026PFMAdvances]

The approximation has a clearly stated seam. Repropagation is exact when no
surface hops occur, since changing the electronic coefficients cannot then
change the active potential or nuclear path. It remains plausible when hops
occur after the initial coherence has decayed. In Galiana and co-workers'
three-state glycine calculation, more than 90% of the hops occurred after 3 fs,
when two relevant coherences were already almost gone. The authors explicitly
left wavepackets prepared at or close to a conical intersection for further
testing, since there the active surface may change while the initial coherence
still affects the forces.[@Galiana2026PulseIndependent]

That open regime suggests a measurable control variable: the fraction of
successful FP hops that occur before the initial coherence falls to $1/e$.
**Hypothesis.** FP--RP errors in electronic population, product-side nuclear
probability, and nuclear centroid will increase as this early-hop fraction
increases. The predeclared high-overlap test required a regime with at least
half of all successful hops before the $1/e$ time. RP-AXE would count as robust
there only if its maximum FP differences remained at or below 0.05 in both
populations and $0.1\sigma_x$ in the centroid. **Falsifier.** The hypothesis
would be rejected if all three limits held at an early-hop fraction of at least
0.5, or if the five-position scan had no positive association between the
early-hop fraction and error. I would publish that result too: it would extend
the safe operating range of pulse-independent trajectories into precisely the
regime that their source paper left open.

## Computational Methods

The calculations ran on arm64 macOS 26.5.2 with CPython 3.13.12 and NumPy
2.4.4. The implementation and analysis use NumPy and the Python standard
library. The complete scripts, raw outputs, compact analysis, figures, and
rerun instructions are in
[pulse-independent-ci-data.tar.gz](/downloads/pulse-independent-ci-data.tar.gz).
The preregistration, including a pilot-triggered extension recorded before its
data were generated, is preserved in the repository's question ledger.

### Model and exact dynamics

I used the effective two-dimensional linear-vibronic-coupling model for the
bis(methylene) adamantyl cation, BMA[5,5], employed by Mannouch and Kelly and
derived from the conical-intersection model of Ryabinkin, Joubert-Doriol, and
Izmaylov.[@MannouchKelly2024Coherence; @Ryabinkin2014GeometricPhase] In
mass-weighted atomic units its diabatic Hamiltonian is

$$
\hat H = \frac{\hat p_x^2+\hat p_y^2}{2}
+ \frac{\omega_x^2q_x^2+\omega_y^2q_y^2}{2}\mathbf 1
+ \begin{pmatrix}
-\kappa(q_x) & c q_y\\
c q_y & \kappa(q_x)
\end{pmatrix},
\qquad
\kappa(q_x)=\frac{\omega_x^2 a q_x}{2},
$$

with $\omega_x=7.743\times10^{-3}$, $\omega_y=6.68\times10^{-3}$,
$a=31.05$, and $c=8.092\times10^{-5}$. The published coherent initial
electronic state was
$\sqrt{0.8}\,|\psi_1\rangle+\sqrt{0.2}\,|\psi_2\rangle$. Its nuclear factor
was a minimum-uncertainty Gaussian with the published widths, initially
centered at $(q_x,q_y)=(a/2,0)$ and with zero mean momentum.

The exact solver used second-order split-operator propagation on periodic
Fourier grids in the global diabatic basis. Before the trajectory sweep, I
compared the BMA upper-adiabatic population with the exact curve digitized at
integer femtoseconds from the vector artwork of Mannouch and Kelly Figure 6.
The digitized line is roughly 0.003 population units thick, so it is a
figure-level check rather than a surrogate data table. BMA convergence used
$256^2$, $384^2$, and $512^2$ grids over $[-96,96)^2$, with 0.05 and 0.025 fs
steps through 40 fs. A separate one-dimensional coherent avoided-crossing
model from the same article checked the reported stationary/moving nuclear-
density bifurcation on 2,048- and 4,096-point grids over $[-8,8)$ through
200 fs.[@MannouchKelly2024Coherence]

Exact references for the new regimes used a $384^2$ BMA grid
($\Delta q=0.5$), a 0.025 fs step, and output every 0.025 fs through 20 fs.
The launch-position scan retained the published widths, momentum distribution,
electronic state, and Hamiltonian while changing
$q_{x,0}/(a/2)$ through $1,0.75,0.5,0.25,$ and $0$. The second-stage scan held
$q_{x,0}/(a/2)=0.5$ and added mean momentum toward the intersection at
$0,-0.5,-1,-1.5,$ and $-2$ times the Wigner $p_x$ standard deviation.
During the drafting audit, I added two post hoc $512^2$ checks at the most
displaced center ($q_{x,0}=0$) and the strongest directional kick. They test
the production reference grid outside the original packet center; they were
not part of the preregistered trajectory hypothesis.

### Full and pulse-independent trajectories

Each regime used four predeclared seeds, 1701--1704, and 4,000 matched Wigner
geometries and momenta per seed. The FP ensemble started every trajectory in
the coherent electronic state and sampled its initial active adiabat from the
geometry-dependent adiabatic populations. The AXE ensemble created two paths
per geometry, one on each pure active adiabat. The coherent electronic
coefficients were then propagated along both AXE paths without feeding back
into their coordinates, and the two branches were weighted by their
geometry-dependent initial populations. This is an independent implementation
of RP-AXE, not a call to the authors' program.[@Galiana2026PulseIndependent]

Nuclei were advanced with velocity Verlet. Electronic coefficients were
advanced analytically in the diabatic basis; density-flux hopping probabilities
were evaluated in the adiabatic basis; accepted hops used isotropic momentum
rescaling. Both FP and AXE paths used TSH-PFMi with
$\omega=\sqrt{\omega_x\omega_y}=0.0071918871$, inactive-population threshold
$\eta=10^{-4}$, and the published momentum-injection procedure.[@Grell2025PFM]
The predeclared 0.05 fs/five-substep setting was compared at
$q_{x,0}/(a/2)=0.25$ with 0.025 fs and ten electronic substeps using seed 1701
and 4,000 geometries. Its centroid criterion failed, so every final trajectory
used the finer 0.025 fs nuclear step and ten 0.0025 fs electronic substeps.

For FP I recorded the coefficient-based upper-adiabatic population, the
coherence amplitude

$$
C(t)=\left\langle 2|c_-^*(t)c_+(t)|\right\rangle,
$$

the nuclear centroid $\langle q_x\rangle$, and the fixed-side probability
$P(q_x<0)$. The coherence lifetime is the first interpolated crossing of
$C(0)/e$; the early-hop fraction includes accepted FP hops at or before that
time and excludes frustrated hops. Primary errors are maximum-in-time absolute
FP--RP differences. Centroid errors are divided by the published initial
$\sigma_x=[2\omega_x]^{-1/2}$. Spearman correlations are descriptive across
the five predeclared centers. The kick scan is labeled adaptive and was not
substituted for the original test.

I did not run the authors' locally modified SHARC code, their glycine
trajectories, or their electronic-structure data. No public implementation of
their RP-AXE workflow was used. Results below are for this independently coded
BMA stress test and do not reproduce the glycine calculation.

## Results

The published-model gate returned `passed: true`. On the finest BMA grid, the
upper-population RMSE against the digitized Figure 6 curve was 0.002653 and the
maximum absolute difference was 0.009552 (Figure 1). The $384^2$/0.025 fs and
$512^2$/0.025 fs BMA runs differed by $7.06\times10^{-6}$ in upper population,
$9.96\times10^{-4}$ in $P(q_x<0)$, and $3.98\times10^{-9}$ in centroid over
40 fs. Their maximum norm errors were $9.96\times10^{-14}$ and
$3.88\times10^{-13}$.

<figure>
  <img src="/images/2026-07-18-pulse-independent-baseline.svg" alt="Upper-state population over forty femtoseconds for the split-operator BMA calculation and the digitized exact curve from Mannouch and Kelly Figure 6. The two traces nearly overlap.">
</figure>

**Figure 1.** Upper-adiabatic BMA population from the $512^2$, 0.025 fs
split-operator run and the digitized exact curve from Mannouch and Kelly
Figure 6.[@MannouchKelly2024Coherence]

At 200 fs, the finest one-dimensional calculation placed 0.971077 of the
nuclear probability in $q<-1.5$ and 0.023396 in $q>-1$, the two regions used
to integrate the stationary and moving density branches. The 2,048- and
4,096-point runs at 0.05 fs differed by $3.88\times10^{-5}$ and
$7.38\times10^{-6}$ in those branch probabilities. Their upper populations
differed by $7.87\times10^{-14}$.

The trajectory time-step comparison returned maximum coarse--fine differences
of 0.00776 in FP upper population, 0.00825 in FP product probability, and
$0.03837\sigma_x$ in the FP centroid. The corresponding RP values were
0.00328, 0.00585, and $0.00863\sigma_x$. The stored population and product
flags were true; the $0.03\sigma_x$ centroid flag and aggregate gate were
false. The final sweep contains 36 fine-setting replicates: nine distinct
regimes, four seeds per regime, and 4,000 geometries per seed.

Table 1 gives the pooled FP--RP values for the predeclared center scan. The
coherence lifetime ranged from 2.164 to 2.634 fs. The early-hop fraction ranged
from 0.0730 to 0.2613. Its Spearman correlation with each of the three maximum
errors was 0.90. The maximum coherence-amplitude difference rose from 0.00295
to 0.00664 and had $\rho=1.00$ with the early-hop fraction.

| $q_{x,0}/(a/2)$ | $C(0)/e$ time (fs) | early hops | max $|\Delta P_+|$ | max $|\Delta P(q_x<0)|$ | max $|\Delta\langle q_x\rangle|/\sigma_x$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1.00 | 2.164 | 0.0730 | 0.00495 | 0.01077 | 0.06487 |
| 0.75 | 2.265 | 0.1286 | 0.01096 | 0.01187 | 0.08233 |
| 0.50 | 2.396 | 0.1998 | 0.02019 | 0.01436 | 0.10381 |
| 0.25 | 2.536 | 0.2451 | 0.01912 | 0.01772 | 0.12773 |
| 0.00 | 2.634 | 0.2613 | 0.02186 | 0.01627 | 0.10725 |

**Table 1.** FP--RP-AXE maximum absolute differences for the four-seed pooled
center scan. Each regime contains 16,000 FP trajectories and 32,000 AXE paths.

Figure 2 divides each maximum error by its predeclared tolerance. The centroid
ratios were 0.649, 0.823, 1.038, 1.277, and 1.072 across the center scan. The
largest population and product ratios within that scan were 0.437 and 0.355.

<figure>
  <img src="/images/2026-07-18-pulse-independent-regime-map.svg" alt="Maximum FP versus RP-AXE errors divided by their predeclared tolerances against the percentage of successful hops before the coherence lifetime. Nuclear-centroid values cross the tolerance line near twenty percent, while electronic and product populations remain below it.">
</figure>

**Figure 2.** Maximum FP--RP-AXE differences divided by the predeclared limits
of 0.05 for upper population, 0.05 for $P(q_x<0)$, and $0.1\sigma_x$ for the
centroid. Solid circles are the original center scan; open diamonds are the
adaptive directional-kick scan.

Table 2 lists the adaptive scan at center fraction 0.5. From zero to a
$-2\sigma_{p_x}$ kick, the coherence lifetime changed from 2.396 to 2.127 fs,
the number of accepted FP hops increased from 11,865 to 23,772, and the
early-hop fraction increased from 0.1998 to 0.2629. The early-hop correlations
with population, product, and centroid errors were 0.90; the correlation with
maximum coherence-amplitude error was 1.00. No regime in either scan had an
early-hop fraction of 0.5.

| $-\langle p_x\rangle/\sigma_{p_x}$ | early hops | max $|\Delta P_+|$ | max $|\Delta P(q_x<0)|$ | max $|\Delta\langle q_x\rangle|/\sigma_x$ |
| ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.1998 | 0.02019 | 0.01436 | 0.10381 |
| 0.5 | 0.2349 | 0.02126 | 0.01813 | 0.13011 |
| 1.0 | 0.2493 | 0.02047 | 0.01979 | 0.14228 |
| 1.5 | 0.2548 | 0.02295 | 0.02444 | 0.17224 |
| 2.0 | 0.2629 | 0.02440 | 0.02302 | 0.16882 |

**Table 2.** FP--RP-AXE maximum absolute differences in the adaptive
directional-kick scan.

Against exact grid dynamics, RP-AXE had the lower upper-population RMSE in 9
of 9 regimes. FP had the lower $P(q_x<0)$ RMSE in 9 of 9 and the lower
centroid RMSE in 9 of 9. At center fraction 0.5 without a kick, the
upper-population RMSEs were 0.02765 for FP and 0.01946 for RP-AXE; product
RMSEs were 0.01902 and 0.02639; centroid RMSEs were $0.06361\sigma_x$ and
$0.12582\sigma_x$. At the strongest $-2\sigma_{p_x}$ kick, FP's product and
centroid RMSEs were 0.0492 and $0.247\sigma_x$, respectively. Figure 3 plots the
two time series used for the population and centroid entries. Across the nine
exact runs, the maximum norm error was $6.28\times10^{-14}$. In the separate
per-seed comparison, RP-AXE had the lower population RMSE in 36/36 replicates;
FP had the lower product RMSE in 35/36 and the lower centroid RMSE in 36/36.
The post hoc $384^2$--$512^2$
spot checks returned maximum population differences of
$6.96\times10^{-6}$ and $1.24\times10^{-5}$, product-side differences of
0.00310 and 0.00305, and centroid differences below
$3.4\times10^{-11}\sigma_x$ for the zero-center and strongest-kick regimes,
respectively.

<figure>
  <img src="/images/2026-07-18-pulse-independent-exact-contrast.svg" alt="Two panels compare exact quantum dynamics, full surface hopping, and RP-AXE at center fraction one half. RP-AXE lies closer to the exact electronic population, while full propagation lies closer to the exact nuclear centroid.">
</figure>

**Figure 3.** Exact, FP, and RP-AXE upper population and nuclear centroid for
$q_{x,0}/(a/2)=0.5$ with zero mean momentum. RMSE annotations use the full
20 fs series; centroid RMSE is in units of the initial $\sigma_x$.

Over all trajectory replicates, the maximum electronic norm error was
$1.44\times10^{-15}$, the maximum AXE weight-normalization error was
$1.11\times10^{-16}$, and the largest recorded energy drifts were
$5.63\times10^{-4}\ E_h$ for FP and $6.06\times10^{-4}\ E_h$ for AXE. The
largest difference between coefficient population and active-surface fraction
was 0.01943.

## Discussion

**Verdict: the hypothesis is supported over the reached range, while its
predeclared high-overlap test is inconclusive.** In the original five-center
scan, all three FP--RP errors had a positive Spearman association of 0.90 with
the fraction of hops occurring before the coherence lifetime. The
nuclear-centroid error crossed its declared $0.1\sigma_x$ limit at a 19.98%
early-hop fraction, whereas neither population error approached its 0.05
limit. The experiment did not produce the required 50% early-hop regime, so it
cannot adjudicate the other half of the falsifier or claim an ultimate
breakdown point.

The exact references reveal why the observable choice changes the verdict. At
the central regime in Figure 3, selecting by electronic population alone would
prefer RP-AXE: its RMSE is 30% lower than FP's. The same reused paths have a
product-probability RMSE 39% higher and a centroid RMSE 98% higher than FP.
That ordering persists in all nine regimes. This is consistent with error
cancellation in an electronic marginal: changing the nuclear paths can move a
surface-hopping population toward the exact curve even while moving nuclear
observables away from it. It is not evidence that FP is exact. In the strongest
$-2\sigma_{p_x}$ kick, the FP errors reported above are already substantial
against the grid reference.

The distinction answers the source paper's open question without contradicting
its reported glycine result. Galiana and co-workers tested a regime in which
more than 90% of hops arrived after 3 fs and concluded that the small number of
hops during surviving pump-generated coherence made repropagation a good
approximation.[@Galiana2026PulseIndependent] Here the measured error begins to
appear as that timing overlap grows. Their electronic populations and dipoles
were the appropriate observables for their spectroscopy calculation; this
stress test adds a warning for control studies whose objective depends on a
nuclear coordinate, side probability, or branching outcome.

The adaptive kick also explains why the planned boundary was harder to reach
than moving a packet toward the intersection might suggest. Increasing the
kick nearly doubled the accepted-hop count, but it shortened the $1/e$
coherence lifetime from 2.396 to 2.127 fs and added later hops to the
denominator. The early-hop fraction consequently saturated near 0.26. This
second-stage scan reinforces the trend but does not repair the missing
high-overlap regime; treating it as if it had reached 0.5 would relax the
preregistration after seeing the data.

There are six boundaries on the result. First, the translated and kicked BMA
packets are controlled stress tests, not pulse-prepared distributions for a
specific molecule. Second, $P(q_x<0)$ is a fixed-side nuclear observable, not a
chemically resolved product yield. Third, the four seeds quantify stochastic
TSH variation but the five center values provide a small descriptive
correlation scan. Fourth, the exact comparison includes every approximation in
the independent TSH-PFMi implementation, including classical nuclei and the
absence of nuclear geometric-phase interference near the conical
intersection.[@Ryabinkin2014GeometricPhase] The paired FP--RP comparison is
more specific to trajectory reuse because those approximations are shared.
Fifth, the authors' modified SHARC implementation and glycine data were not
available in this experiment; agreement or disagreement with this code is not
a software-level reproduction. Sixth, AXE uses both initial active-state paths
for every geometry while FP samples one, so the exact-RMSE rankings compare the
two methods as defined rather than equal nuclear-path counts. The 36/36
per-seed electronic ordering is less consistent with a chance seed fluctuation,
but it does not isolate the effect of that larger AXE ensemble.

Within those limits, the practical validation rule is simple: a
pulse-independent method should not be cleared by electronic populations
alone. At minimum, validation should include the nuclear observable that the
control problem is trying to optimize, and it should report how much surface
hopping occurs before the prepared coherence decays. In this model, the first
declared failure appears in the nuclei while the electronic trace still looks
better against exact dynamics.

## Conclusion

Pulse-independent trajectory reuse now has a measured onset rather than a
binary label in this model: nuclear-centroid error exceeds its declared limit
near a 20% early-hop fraction, while electronic and side-population errors stay
below theirs through 26%. The remaining boundary is deliberately unresolved.

The next experiment should change the coupling topology or coherence lifetime,
instead of pushing the packet faster, to create a majority of hops before
$C(0)/e$ without simultaneously swelling the late-hop denominator. Repeating
the FP--RP--exact comparison there would adjudicate the predeclared 50% test;
running the same observable set in the authors' molecular implementation would
then determine whether the BMA ordering transfers beyond this model.

## References
