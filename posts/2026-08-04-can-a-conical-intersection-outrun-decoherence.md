---
title: "Can a conical intersection outrun decoherence? Extending Galiana et al.'s pulse-independent trajectories"
date: 2026-08-04
author: Peter Johnston
tags: molecular photodynamics, surface hopping, electronic coherence, conical intersections, reproducibility
description: An independent sensitivity benchmark extends Galiana et al.'s pulse-independent-trajectory test into a regime where most surface hops overlap surviving optical coherence.
post-type: research
contribution: An adjudicated RP-AXE sensitivity test in a regime where most accepted surface hops precede the pump-coherence lifetime, jointly scored by electronic population, product-side probability, and nuclear centroid against exact dynamics, which is not reported by Galiana et al. or Grell et al.
contribution-type: untested regime
experiment: coherence-hop-boundary
og-image: /images/2026-08-04-conical-intersection-outrun-decoherence-hero.png
---

## Abstract

Joachim Galiana and co-workers' 2026 paper, *Accounting for Electronic
Coherences Induced by Broadband Pulses by Using Pulse-Independent
Trajectories*, proposes reusing expensive nuclear paths while repropagating the
electronic state prepared by each new broadband pulse.[@Galiana2026PulseIndependent]
This post is an independent sensitivity benchmark of the regime that paper
leaves open: a molecular wavepacket near a conical intersection, where most
accepted surface hops occur before its initial electronic coherence decays. I
parameterized the projected-forces-and-momenta decoherence rate in the same
two-state BMA[5,5] model used in the preceding benchmark, then compared full
propagation with RP-AXE trajectory reuse and exact grid dynamics. This is an
independent implementation from published equations; it does not call the
authors' locally modified SHARC program or use their glycine trajectories.

Across the seven predeclared rate scales,
[majority_regime_count]{.metric} produced a majority of accepted hops before
the coherence lifetime. The first was
$s=$[majority_onset_rate_scale]{.metric}, with an early-hop fraction of
[majority_onset_early_hop_fraction]{.metric}; its maximum FP--RP errors were
[majority_onset_upper_population_error]{.metric} in upper population,
[majority_onset_product_probability_error]{.metric} in product probability,
and [majority_onset_centroid_x_sigma_error]{.metric}$\sigma_x$ in the nuclear
centroid. The registered hypothesis was supported. The exact reference,
however, placed RP-AXE closer than FP for all three observables at the slowest
damping setting, making this a trajectory-equivalence boundary rather than a
simple RP-AXE accuracy failure.

## Introduction

Few-femtosecond ultraviolet pulses can prepare a molecule in a coherent
superposition of electronic states. The nuclei then move while the amplitudes
interfere, decohere, and sometimes cross between potential-energy surfaces.
That coupled motion is the computational object behind pump--probe spectra and
optical control proposals: changing the pump can change the initial electronic
coefficients, which can change the active surface, which can change the nuclear
path.[@Grell2025PFM; @Galiana2026PulseIndependent]

Trajectory surface hopping makes this calculation affordable by replacing the
nuclear wavepacket with an ensemble of classical paths, each carried on one
active electronic surface.[@Tully1990SurfaceHopping; @Faraji2024Photoinduced]
It also creates a reuse opportunity. Galiana and co-workers' **RP-AXE** method
first propagates an all-excited-state ensemble without pump-generated
coherence. For each proposed pulse, it then evolves only the electronic
coefficients along those frozen paths and combines the branches with
pulse-dependent weights.[@Galiana2026PulseIndependent] Grell and co-workers
subsequently used that construction to scan broadband-pulse parameters in
glycine.[@Grell2026PFMAdvances]

The approximation has a physical seam. Repropagation is exact when no surface
hop changes the active potential. It can remain accurate when hopping begins
after the initial coherence is gone. In Galiana and co-workers' three-state
glycine example, more than 90% of hops occur after 3 fs, when the relevant
initial coherences have almost disappeared. They explicitly identify a
wavepacket prepared at or near a conical intersection—where hopping and
surviving coherence overlap—as a case still needing a test.[@Galiana2026PulseIndependent]

I previously moved and kicked a BMA[5,5] packet toward its conical intersection
in [an independent trajectory benchmark](/posts/2026-07-18-when-pulse-independent-trajectories-lose-nuclear-accuracy.html).
The nuclear-centroid error crossed its declared tolerance, but neither control
made a majority of accepted hops occur within the coherence lifetime. Pushing
the packet faster added late hops and shortened that lifetime at the same time.
The unresolved question therefore came off the blog's research shelf: **can a
fixed conical-intersection model sustain a majority of hops before decoherence,
and does RP-AXE remain accurate if it can?**

The present experiment changes the other side of that race. A dimensionless
multiplier $s$ slows or restores the projected-forces-and-momenta damping rate
while the Hamiltonian, launch distribution, and optical preparation remain
fixed. This is an algorithmic sensitivity dial, not a new molecular parameter.
**Hypothesis.** Lowering $s$ will produce at least one finite-lifetime regime in
which at least half of accepted full-propagation hops occur before the
coherence falls to $1/e$, and RP-AXE will exceed at least one of the declared
population, product, or centroid error limits there. **Falsifier.** The
hypothesis is falsified if no predeclared setting reaches that half-hop boundary
or if every setting that reaches it remains within all three limits. I would
publish either outcome: robustness would extend the method's tested range;
failure would locate a concrete validation boundary.

## Computational Methods

The confirmatory calculations ran on x86-64 Linux with CPython 3.12.9 and NumPy
2.2.5, with `OPENBLAS_NUM_THREADS=1`. The simulator uses NumPy and the Python
standard library; the analysis and 1200 × 630 publication figure additionally
use Matplotlib 3.10.8 and Pillow 12.1.0. Declared random seeds fix every Wigner
sample and hopping draw. The executable code, pinned requirements,
preregistration, canonical JSON outputs (with the sweep deterministically
gzip-compressed), metrics generator, and public-file
allowlist live under `research/coherence-hop-boundary/`. No living subject was
recruited, observed, exposed, or acted upon.

The trajectory code descends from the independent implementation published
with the preceding post. I parameterized and instrumented that code rather than
using the source authors' program. Galiana and Grell, with their co-workers, report
OpenMolcas calculations and a local modification of SHARC; I found supporting
PDFs but no public patch, raw trajectory archive, or reusable implementation
linked from either 2026 paper.[@Galiana2026PulseIndependent;
@Grell2026PFMAdvances] I did not run their glycine, LiH, or dithiane
calculations. The present result is therefore a model sensitivity test, not a
software-level reproduction of those molecular calculations.

### Fixed molecular model

The molecular Hamiltonian is the two-state, two-mode linear-vibronic-coupling
model for the bis(methylene) adamantyl cation, BMA[5,5], used by Mannouch and
Kelly and derived from the conical-intersection model of Ryabinkin,
Joubert-Doriol, and Izmaylov.[@MannouchKelly2024Coherence;
@Ryabinkin2014GeometricPhase] In mass-weighted atomic units,

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
$a=31.05$, and $c=8.092\times10^{-5}$. Every regime starts from the
published real diabatic superposition
$\sqrt{0.8}\,|\psi_1\rangle+\sqrt{0.2}\,|\psi_2\rangle$ and the same
minimum-uncertainty Wigner distribution. Its center is fixed at
$q_{x,0}/(a/2)=0.5$, $q_{y,0}=0$, with zero mean momentum. The computation
therefore represents one reduced molecular Hamiltonian through an ensemble of
sampled nuclear paths. It is not a simulated single-molecule photon-counting
trace, explicit laser field, or detector response.

Exact references use second-order split-operator propagation in the global
diabatic basis on periodic two-dimensional Fourier grids over
$[-96,96)^2$. The production candidate is a $384^2$ grid with a 0.025 fs step through
20 fs; a separately run $512^2$ grid audits the upper-state population,
fixed-side probability $P(q_x<0)$, nuclear centroid, and norm. The coarser grid
is accepted only if its maximum differences from the finer trace are at most
$2\times10^{-4}$ in upper population, 0.005 in product probability, and
$0.01\sigma_x$ in centroid, while the finer maximum norm error remains below
$10^{-10}$; otherwise the $512^2$ result becomes the production reference.
Because the Hamiltonian and launch state do not change with $s$, one converged
exact trace serves every trajectory regime.

### Decoherence stress dial and trajectory pair

Both full propagation (**FP**) and RP-AXE use the projected forces and momenta
method with momentum injection, **TSH-PFMi**.[@Grell2025PFM] For the two-mode
model, the implementation evaluates the published rate

$$
\Gamma_{\mathrm{PFM}}
= \frac{\pi^2}{8\omega}|\Delta p|\,|\Delta F|
+ |\Delta p|\sqrt{\frac{\pi^2 2\omega}{8}},
\qquad \omega=\sqrt{\omega_x\omega_y},
$$

then damps the inactive adiabatic amplitude over one electronic step by
$\exp(-s\Gamma_{\mathrm{PFM}}\Delta t)$. I apply the same $s$ to FP, the
incoherent AXE base paths, and the coherent coefficients repropagated along
those paths. The values $s=1,0.5,0.25,0.125,0.10,0.075,$ and $0.05$ were
frozen after a separate seed-1701 feasibility pilot. That pilot is not included
in the confirmatory estimates. The final run uses fresh seeds 2701--2704 and
4,000 matched Wigner geometries per seed and setting. The AXE construction
propagates one pure lower- and one pure upper-state path for each geometry.

Nuclei use velocity Verlet. Electronic amplitudes are advanced analytically in
the diabatic basis, with density-flux hopping probabilities evaluated in the
adiabatic basis and accepted hops rescaled isotropically. The planned production
setting is a 0.025 fs nuclear step, ten electronic substeps, and 20 fs total
time. Before the confirmatory sweep, an independent seed-2699 run with
$s=0.05$ compares that setting with a 0.0125 fs step and twenty substeps. The
production setting is accepted only if the early-hop fraction changes by at
most 0.02, the coherence lifetime by at most 0.15 fs, the maximum population
and product time-series differences by at most 0.02, the centroid difference
by at most $0.03\sigma_x$, and both the majority-hop and robustness
classifications remain unchanged. A failure promotes the finer setting for
every final regime; none of the criteria may be relaxed after seeing the gate.

Before that numerical gate, an $s=1$ lineage test compares the newly
parameterized path with the archived implementation under the same small
deterministic input. It requires identical accepted-hop records and observable
series within floating-point tolerance. This isolates code-refactoring drift
from the new rate control.

### Outcomes and decision rule

The full ensemble records the upper-adiabatic coefficient population, coherence
amplitude

$$
C(t)=\left\langle 2|c_-^*(t)c_+(t)|\right\rangle,
$$

$P(q_x<0)$, and $\langle q_x\rangle$. The coherence lifetime $\tau_{1/e}$
is the first linearly interpolated crossing of $C(0)/e$. The **early-hop
fraction** is the number of accepted FP hop events at or before $\tau_{1/e}$
divided by all accepted FP hop events through 20 fs. A trace without a crossing
is reported as right-censored and cannot qualify as a majority-early-hop
regime. The primary nuclear outcome is the maximum-in-time absolute FP--RP
difference in $P(q_x<0)$. Upper-population and centroid differences are
mandatory components of the compound decision, with limits 0.05, 0.05, and
$0.1\sigma_x$, respectively.

The four seeds are pooled for each declared setting, and their separate values
and 95% intervals remain in the canonical output. Secondary analyses report
FP and RP root-mean-square error against exact dynamics, coherence-amplitude
error, early and late hop counts, proposed and frustrated events, hop direction,
and the fraction of hopping trajectories with a first or repeated hop. The raw
run records retain electronic norm, coefficient-versus-active-state consistency,
energy drift, and runtime. These
event diagnostics test whether a majority event fraction was manufactured by
repeated hopping; they do not replace the predeclared event-based outcome.

## Results

The lineage comparison reported a largest observable-array difference of
[lineage_max_observable_difference]{.metric}. The trajectory convergence run
reported an early-hop-fraction difference of
[convergence_difference_early_hop_fraction]{.metric} against the registered
0.02 limit; every other registered numerical and classification criterion was within
their limits. The promotion rule selected a
[production_nuclear_dt_fs]{.metric} fs nuclear step with
[production_electronic_substeps]{.metric} electronic substeps. The exact-grid
audit selected [exact_production_grid_n]{.metric} points per coordinate axis
and reported a fine-grid maximum norm error of
[exact_fine_max_norm_error]{.metric}.

Figure 1 plots every scale against the registered half-hop boundary and the
three normalized FP--RP error limits.

<figure>
  <img src="/images/2026-08-04-conical-intersection-outrun-decoherence-hero.png" alt="Three curves rise as the early-hop fraction increases: population and product errors cross their tolerance near one half, while the normalized nuclear-centroid error rises much higher.">
</figure>

**Figure 1.** Maximum FP--RP errors normalized by their registered tolerances versus the accepted-event early-hop fraction; the vertical dotted line is the majority boundary, the horizontal dashed line is one tolerance unit, and A, B, and C mark the largest population, product-probability, and centroid ratios, respectively.

The seven pooled scale-level outputs are listed in Table 1. The analysis
recorded [majority_regime_count]{.metric} majority-early-hop settings. The
adjacent settings $s=0.10$ and $s=0.075$ had early-hop fractions of
[s_0_10_early_hop_fraction]{.metric} and
[s_0_075_early_hop_fraction]{.metric}, respectively.

| $s$ | $\tau_{1/e}$ (fs) | Early events | $\max|\Delta P_+|$ | $\max|\Delta P(q_x<0)|$ | $\max|\Delta\langle q_x\rangle|/\sigma_x$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | [s_1_coherence_lifetime_fs]{.metric} | [s_1_early_hop_fraction]{.metric} | [s_1_max_upper_population_error]{.metric} | [s_1_max_product_probability_error]{.metric} | [s_1_max_centroid_x_sigma_error]{.metric} |
| 0.5 | [s_0_5_coherence_lifetime_fs]{.metric} | [s_0_5_early_hop_fraction]{.metric} | [s_0_5_max_upper_population_error]{.metric} | [s_0_5_max_product_probability_error]{.metric} | [s_0_5_max_centroid_x_sigma_error]{.metric} |
| 0.25 | [s_0_25_coherence_lifetime_fs]{.metric} | [s_0_25_early_hop_fraction]{.metric} | [s_0_25_max_upper_population_error]{.metric} | [s_0_25_max_product_probability_error]{.metric} | [s_0_25_max_centroid_x_sigma_error]{.metric} |
| 0.125 | [s_0_125_coherence_lifetime_fs]{.metric} | [s_0_125_early_hop_fraction]{.metric} | [s_0_125_max_upper_population_error]{.metric} | [s_0_125_max_product_probability_error]{.metric} | [s_0_125_max_centroid_x_sigma_error]{.metric} |
| 0.10 | [s_0_10_coherence_lifetime_fs]{.metric} | [s_0_10_early_hop_fraction]{.metric} | [s_0_10_max_upper_population_error]{.metric} | [s_0_10_max_product_probability_error]{.metric} | [s_0_10_max_centroid_x_sigma_error]{.metric} |
| 0.075 | [s_0_075_coherence_lifetime_fs]{.metric} | [s_0_075_early_hop_fraction]{.metric} | [s_0_075_max_upper_population_error]{.metric} | [s_0_075_max_product_probability_error]{.metric} | [s_0_075_max_centroid_x_sigma_error]{.metric} |
| 0.05 | [s_0_05_coherence_lifetime_fs]{.metric} | [s_0_05_early_hop_fraction]{.metric} | [s_0_05_max_upper_population_error]{.metric} | [s_0_05_max_product_probability_error]{.metric} | [s_0_05_max_centroid_x_sigma_error]{.metric} |

**Table 1.** Pooled coherence lifetimes, accepted-event early-hop fractions, and maximum FP--RP differences for every predeclared PFM-rate scale.

At $s=0.075$, the event record contained [s_0_075_accepted]{.metric}
accepted hops. Of the first accepted hops,
[s_0_075_early_first_hop_fraction]{.metric} occurred by the coherence lifetime;
the corresponding fraction among repeated hops was
[s_0_075_early_repeat_hop_fraction]{.metric}. At $s=0.05$, the accepted count
was [s_0_05_accepted]{.metric}, with
[s_0_05_early_first_hop_fraction]{.metric} of first hops and
[s_0_05_early_repeat_hop_fraction]{.metric} of repeated hops early.

Table 2 lists the exact-reference RMSEs for the majority settings.

| $s$ | Method | $P_+$ RMSE | $P(q_x<0)$ RMSE | Centroid RMSE ($\sigma_x$) |
| ---: | :--- | ---: | ---: | ---: |
| 0.075 | FP | [s_0_075_full_rmse_exact_upper_population]{.metric} | [s_0_075_full_rmse_exact_product_probability]{.metric} | [s_0_075_full_rmse_exact_centroid_x_sigma]{.metric} |
| 0.075 | RP-AXE | [s_0_075_reprop_axe_rmse_exact_upper_population]{.metric} | [s_0_075_reprop_axe_rmse_exact_product_probability]{.metric} | [s_0_075_reprop_axe_rmse_exact_centroid_x_sigma]{.metric} |
| 0.05 | FP | [s_0_05_full_rmse_exact_upper_population]{.metric} | [s_0_05_full_rmse_exact_product_probability]{.metric} | [s_0_05_full_rmse_exact_centroid_x_sigma]{.metric} |
| 0.05 | RP-AXE | [s_0_05_reprop_axe_rmse_exact_upper_population]{.metric} | [s_0_05_reprop_axe_rmse_exact_product_probability]{.metric} | [s_0_05_reprop_axe_rmse_exact_centroid_x_sigma]{.metric} |

**Table 2.** Root-mean-square errors against the selected exact wavepacket trace for FP and RP-AXE in the majority-early-hop settings.

## Discussion

The hypothesis was **supported**. Slowing the algorithmic PFM rate created
[majority_regime_count]{.metric}
finite-lifetime settings with a majority of accepted hops inside the coherence
window, and both settings exceeded every member of the compound FP--RP error
criterion. At the onset setting, every normalized error exceeded one tolerance
unit (Figure 1). In the two settings where hopping and the prepared coherence
substantially overlapped, trajectory reuse was no longer interchangeable with
a fresh coherent trajectory ensemble.

That verdict is deliberately about equivalence to FP, not accuracy in the
abstract. At $s=0.05$, FP's selected numerical-grid-reference RMSEs were
[s_0_05_full_rmse_exact_upper_population]{.metric},
[s_0_05_full_rmse_exact_product_probability]{.metric}, and
[s_0_05_full_rmse_exact_centroid_x_sigma]{.metric}$\sigma_x$ for population,
product probability, and centroid. RP-AXE's corresponding errors were smaller:
[s_0_05_reprop_axe_rmse_exact_upper_population]{.metric},
[s_0_05_reprop_axe_rmse_exact_product_probability]{.metric}, and
[s_0_05_reprop_axe_rmse_exact_centroid_x_sigma]{.metric}$\sigma_x$ (Table 2).
Calling the FP--RP separation an RP-AXE failure would therefore get the most
important comparison backward. Under this algorithmic stress test, the FP
reference itself moves farther from the exact wavepacket for these observables.

One possible reading is that freezing the AXE paths partially regularizes a
surface-hopping error that grows when decoherence is artificially slowed. That
is an inference, not a measured mechanism: the experiment does not separate
active-surface sampling error from the PFM approximation, and $s$ has no claim
to be a physical environmental rate. What the exact trace does establish here
is narrower and more useful. A validation that treats FP as ground truth can
detect loss of trajectory equivalence while misidentifying which approximation
is closer to quantum dynamics.

Repeated hopping did not manufacture the registered majority. In both majority
settings, first hops were more concentrated inside the coherence window than
repeat hops; the later repeats diluted the all-event fraction. The conclusion
also remains bounded to one two-state, two-mode Hamiltonian, one coherent launch,
four stochastic seeds, and operational error limits chosen before confirmation.
There is no explicit pulse, detector, molecular electronic-structure
calculation, or source-author software in the loop. The canonical outputs are
traceable through the validated metric projection and end-to-end reproducible
in the pinned environment, but they do not reproduce Galiana and co-workers'
glycine calculation.[@Galiana2026PulseIndependent]

## Conclusion

This run separates loss of FP--RP trajectory equivalence from loss of quantum
accuracy: crossing the registered reuse boundary did not make RP-AXE the less
accurate approximation to the exact trace.

The next useful experiment is a matched-lifetime comparison between PFM and a
different decoherence law on the same Hamiltonian. If the exact-reference
ranking follows coherence lifetime rather than the PFM construction, the
boundary is likely tied to timescale overlap; if it changes with the damping
law, the algorithm is part of the effect. After that, the same adjudication
should move to a molecular Hamiltonian with an explicit optical preparation.
Those tests would change my interpretation; corrections to the present
implementation or a known treatment of this regime would, too.

## References
