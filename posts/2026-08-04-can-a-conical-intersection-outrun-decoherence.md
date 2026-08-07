---
title: "Can conical-intersection hops outrun coherence? An independent extension of Galiana et al."
date: 2026-08-04
author: Peter Johnston
tags: molecular photodynamics, surface hopping, electronic coherence, conical intersections, reproducibility
description: An independent sensitivity extension of Galiana et al.'s pulse-independent trajectories separates mean single-trajectory coherence magnitude from phase-sensitive ensemble coherence and stops at a failed convergence gate.
post-type: research
contribution: "A phase-sensitive audit of my own coherence--hop experiment: it identifies the archived observable as only the mean magnitude of single-trajectory coherences, reconstructs true recrossings, and records a corrective fine/finer gate that blocks the optical-coherence claim."
contribution-type: falsification
experiment: coherence-hop-boundary
og-image: /images/2026-08-04-conical-intersection-outrun-decoherence-hero.png
---

## Abstract

Galiana and co-workers' 2026 article, *Accounting for Electronic Coherences
Induced by Broadband Pulses by Using Pulse-Independent Trajectories*, motivates
near-intersection dynamics, where hopping overlaps surviving coherence, as a
stress test for RP-AXE.[@Galiana2026PulseIndependent] I independently
implemented a sensitivity extension in the BMA[5,5] model to test whether
surface hops could occur before pump-generated electronic coherence decayed and
whether RP-AXE remained equivalent to full propagation in that regime. The
first analysis did not measure that coherence. It averaged
$2|c_-^*c_+|$ over trajectories, putting the magnitude inside the ensemble and
therefore removing phase cancellation. The archived coefficient phases were
not retained, so the production runs cannot be repaired after the fact.

This correction gives those runs their narrower interpretation. They describe
mean single-trajectory coherence magnitude, not ensemble optical coherence.
The archived sweep contains
[legacy_local_magnitude_majority_regime_count]{.metric} apparent majority
settings under that definition, but its coarse/fine early-event difference was
[legacy_convergence_early_fraction_difference]{.metric}, above the registered
[legacy_convergence_early_fraction_limit]{.metric} tolerance. It is descriptive,
not a converged confirmation.

I then froze a gauge-defined, phase-sensitive observable and an eight-paired-seed
fine/finer gate. The corrected candidate and reference early-hop fractions at
$s=0.05$ were [corrective_candidate_early_hop_fraction]{.metric} and
[corrective_reference_early_hop_fraction]{.metric}. Their classifications
agreed, but the centroid's 95% interval envelope reached
[corrective_centroid_95_max_endpoint]{.metric}$\sigma_x$ against a
[corrective_centroid_limit]{.metric}$\sigma_x$ limit. The gate failed and the
28-run corrective sweep was not performed. The original optical-coherence
hypothesis is therefore **inconclusive**, not supported.

## Introduction

A broadband pump can prepare amplitudes on several electronic states. The
experimentally relevant electronic coherence is an off-diagonal element of an
ensemble density matrix: trajectories with different phases can cancel even
when each trajectory remains a coherent superposition. Galiana and co-workers
use that pump-generated coherence when motivating pulse-independent
trajectories and identify near-intersection dynamics, where hopping overlaps
surviving coherence, as a useful stress test.[@Galiana2026PulseIndependent]

My initial experiment appeared to supply that test (that manuscript did not
survive the review process, which is why this one reads like a followup to an
experiment that doesn't exist in public—you can
[read it here](https://github.com/noprofits-org/pvjohnston.com/blob/77a27f6d06058067826b98130921229e31dfdb01/posts/2026-08-04-can-a-conical-intersection-outrun-decoherence.md)
if you'd like). It varied a dimensionless multiplier on
projected-forces-and-momenta decoherence in the two-state BMA[5,5] model,
compared full propagation (**FP**) with repropagated AXE trajectories
(**RP-AXE**), and counted accepted hops before a reported $C(0)/e$ lifetime.
The question came from the blog's research shelf after an earlier launch-control
study failed to reach a majority boundary:
**can a fixed conical-intersection model sustain a majority of hops before
decoherence, and does RP-AXE remain equivalent to FP if it can?**

The observable made that question ill-posed. The archived code computed

$$
C_{\mathrm{local}}(t)
=\left\langle 2\left|c_-^*(t)c_+(t)\right|\right\rangle,
$$

whereas phase-sensitive ensemble coherence requires

$$
C_{\mathrm{ens}}(t)
=2\left|\left\langle c_-^*(t)c_+(t)\right\rangle\right|.
$$

The triangle inequality gives
$C_{\mathrm{ens}}\le C_{\mathrm{local}}$. The phase-sensitive
$C_{\mathrm{ens}}$ can decay through phase cancellation;
$C_{\mathrm{local}}$ cannot. Mannouch and Kelly make this distinction
explicit when separating ensemble coherence, relevant to linear spectroscopy,
from a magnitude-inside-ensemble measure that removes pure
dephasing.[@MannouchKelly2024Coherence] A long-lived
$C_{\mathrm{local}}$ trace therefore cannot establish surviving optical or
pump-generated coherence.

The correction had two parts. First, I relabeled and reanalyzed the 28 archived
runs strictly as a local-magnitude sensitivity study. Second, before generating
new production data, I froze a real adiabatic gauge, retained signed real and
imaginary ensemble density-matrix components, and required a multi-seed
fine/finer convergence test. **Corrected hypothesis.** Lowering the PFM-rate
scale will produce at least one setting in which half the accepted FP hops occur
before the phase-sensitive ensemble lifetime and FP--RP separation exceeds at
least one declared tolerance. **Falsifier.** No declared setting reaches that
majority, or every setting that does remains within all three tolerances. A
failed mandatory gate makes the experiment inconclusive before either verdict.

## Computational Methods

All calculations used the two-state, two-mode linear-vibronic-coupling model for
the bis(methylene) adamantyl cation, BMA[5,5], used by Mannouch and Kelly and
derived from Ryabinkin, Joubert-Doriol, and Izmaylov.[@MannouchKelly2024Coherence;
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
$a=31.05$, and $c=8.092\times10^{-5}$. Every run starts from the real
diabatic superposition
$\sqrt{0.8}|\psi_1\rangle+\sqrt{0.2}|\psi_2\rangle$ and a product-ground-state
Wigner distribution centered at $q_x=a/4$, $q_y=0$, with zero mean momentum.
The calculation is a reduced molecular model, not a photon-counting trace,
explicit laser field, or detector simulation.

### Archived local-magnitude lane

The archived sweep used the projected-forces-and-momenta decoherence rate and
momentum-injection procedure from Grell and co-workers' original TSH-PFMi method
and later advances, implemented independently here.[@Grell2025PFM;
@Grell2026PFMAdvances] It applied rate multipliers
$s=1,0.5,0.25,0.125,0.10,0.075,$ and $0.05$, four seeds per scale, and 4,000
matched Wigner geometries per seed. FP propagated one nuclear path per geometry.
RP-AXE propagated pure lower- and upper-state AXE paths, so it used twice as
many nuclear paths. Nuclei used velocity Verlet; the electronic state used an
analytic midpoint two-state propagator; accepted hops used isotropic momentum
rescaling. The stored `coherence_amplitude` field is now bound by an artifact
contract to $C_{\mathrm{local}}$ and excluded from optical-coherence
interpretation.

The archived numerical check compared 0.025 fs with ten electronic substeps
against 0.0125 fs with twenty substeps at $s=0.05$. Changing the number of
substeps also changes random-draw alignment, so the comparison mixes timestep
effects with stochastic path divergence. Its early-event difference exceeded
the frozen tolerance, after which the finer setting was selected without a
fine/finer check. The 28 runs are therefore retained as descriptive evidence
under the local-magnitude definition, not as a converged confirmation.

The selected exact trace came from second-order split-operator propagation in
the global diabatic basis on $[-96,96)^2$. A $384^2$ grid was compared with a
$512^2$ grid at a 0.025 fs step. This audits spatial resolution and norm, but not
the timestep or periodic box. Exact-reference RMSE is secondary for two further
reasons: FP and RP-AXE use unequal nuclear-path counts, and the registered
primary decision concerns FP--RP equivalence rather than either method's
absolute quantum accuracy.

### Corrective phase-sensitive lane

The corrective simulator stores

$$
C_{\mathrm{Re}}(t)=2\operatorname{Re}\left\langle c_-^*c_+\right\rangle,
\qquad
C_{\mathrm{Im}}(t)=2\operatorname{Im}\left\langle c_-^*c_+\right\rangle,
$$

and reconstructs
$C_{\mathrm{ens}}=(C_{\mathrm{Re}}^2+C_{\mathrm{Im}}^2)^{1/2}$ only after
pooling signed components. The explicit real adiabatic gauge uses
$\theta=\operatorname{atan2}(cq_y,\kappa)$,
$|-\rangle=(\cos\frac\theta2,-\sin\frac\theta2)$, and
$|+\rangle=(\sin\frac\theta2,\cos\frac\theta2)$. The local magnitude is retained
only as a secondary upper bound.

At $s=0.05$, eight paired ensemble seeds, 2687--2694, compared a candidate
0.0125 fs nuclear step with twenty electronic substeps against a 0.00625 fs
step with forty substeps. Each run used 4,000 geometries through 20 fs.
Two-sided 95% Student-$t$ intervals were formed from seed-level
candidate-minus-reference differences. The largest absolute interval endpoint
had to remain within 0.02 for early-hop fraction, 0.15 fs for lifetime, 0.02
for upper population and product probability, and $0.03\sigma_x$ for centroid;
pooled majority and robustness classifications also had to match. Four seeds
left the centroid interval too wide, so a frozen amendment added four seeds
once, with no further extension. Any eight-seed failure blocked production.

The **early-hop fraction** is the number of accepted FP hop events at or before
the relevant $C(0)/e$ lifetime divided by all accepted FP hop events through
20 fs, including repeats. A repeat is any accepted event after a trajectory's
first. A recrossing is narrower: a repeated event returning to that
trajectory's initial active state. The original artifact marked every repeat as
a recrossing; the correction reconstructs labels from each ordered event
sequence without changing the registered denominator.

### Environment and implementation lineage

The frozen execution boundary is Linux x86-64 with CPython 3.12.9, NumPy 2.2.5,
and `OPENBLAS_NUM_THREADS=1`; Figure 1 generation and validation additionally
use Matplotlib 3.10.8 and Pillow 12.1.0. The direct third-party dependencies are pinned in
`research/coherence-hop-boundary/requirements.txt`, and the declared seeds above
determine each Wigner-sampling and hopping stream independently of worker order.

At the access date, the cited articles supplied no public patch for the source
authors' locally modified SHARC program, raw molecular trajectory archive, or
reusable RP-AXE implementation. I did not run that program or the authors'
glycine, LiH, or dithiane calculations, and none of their code or molecular data
is an executable input here. The reduced BMA[5,5] FP, TSH-PFMi, and RP-AXE
workflow was implemented independently from the published equations. This
correction refactored my checksum-bound archived implementation at repository
commit `b527db4a4f31012f751981f580e27bca763f9e54`; before the corrective gate, a
lineage comparison required identical accepted-hop records and observable
arrays within `rtol=1e-12` and `atol=1e-12`. This experiment is therefore an
independent sensitivity extension, not a software-level or molecular-data
reproduction of Galiana and co-workers.[@Galiana2026PulseIndependent]

Canonical scientific JSON now excludes wall-clock runtimes and generation
timestamps. The required metric timestamp is pinned to the corrective
preregistration epoch, and gzip output fixes its metadata. The original source
hash of every corrected artifact is retained. The code, preregistration,
requirements, tests, public-file allowlist, and artifacts live under
`research/coherence-hop-boundary/`. No living subject was recruited, observed,
exposed, or acted upon.

## Results

The lineage comparison passed with a largest observable difference of
[lineage_max_observable_difference]{.metric}.

The phase-sensitive convergence gate did not pass. Table 1 reports the pooled
candidate and reference timing outcomes at $s=0.05$. Neither setting reached a
majority.

| Setting | $C_{\mathrm{ens}}(0)/e$ lifetime (fs) | Accepted events before lifetime | Majority? |
| :--- | ---: | ---: | :---: |
| Candidate, 0.0125 fs / 20 | [corrective_candidate_ensemble_lifetime_fs]{.metric} | [corrective_candidate_early_hop_fraction]{.metric} | [corrective_candidate_majority]{.metric} |
| Reference, 0.00625 fs / 40 | [corrective_reference_ensemble_lifetime_fs]{.metric} | [corrective_reference_early_hop_fraction]{.metric} | [corrective_reference_majority]{.metric} |

**Table 1.** Phase-sensitive pooled outcomes in the eight-paired-seed numerical gate. These are convergence runs, not the blocked seven-scale production sweep.

The maximum absolute 95% interval endpoints were
[corrective_fraction_95_max_endpoint]{.metric} for early-hop fraction,
[corrective_lifetime_95_max_endpoint]{.metric} fs for lifetime,
[corrective_population_95_max_endpoint]{.metric} for upper population,
[corrective_product_95_max_endpoint]{.metric} for product probability, and
[corrective_centroid_95_max_endpoint]{.metric}$\sigma_x$ for centroid. The
centroid endpoint occurred at
[corrective_centroid_95_max_endpoint_time_fs]{.metric} fs; its registered limit
was [corrective_centroid_limit]{.metric}$\sigma_x$. The corrective production
run was [corrective_production_run]{.metric}.

Table 2 gives the archived sweep under its corrected local-magnitude scope.
The two smallest rate multipliers cross the half-event line descriptively.

| $s$ | $C_{\mathrm{local}}(0)/e$ lifetime (fs) | Events before lifetime | $\max|\Delta P_+|$ | $\max|\Delta P(q_x<0)|$ | $\max|\Delta\langle q_x\rangle|/\sigma_x$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | [s_1_local_magnitude_lifetime_fs]{.metric} | [s_1_local_magnitude_early_hop_fraction]{.metric} | [s_1_max_upper_population_error]{.metric} | [s_1_max_product_probability_error]{.metric} | [s_1_max_centroid_x_sigma_error]{.metric} |
| 0.5 | [s_0_5_local_magnitude_lifetime_fs]{.metric} | [s_0_5_local_magnitude_early_hop_fraction]{.metric} | [s_0_5_max_upper_population_error]{.metric} | [s_0_5_max_product_probability_error]{.metric} | [s_0_5_max_centroid_x_sigma_error]{.metric} |
| 0.25 | [s_0_25_local_magnitude_lifetime_fs]{.metric} | [s_0_25_local_magnitude_early_hop_fraction]{.metric} | [s_0_25_max_upper_population_error]{.metric} | [s_0_25_max_product_probability_error]{.metric} | [s_0_25_max_centroid_x_sigma_error]{.metric} |
| 0.125 | [s_0_125_local_magnitude_lifetime_fs]{.metric} | [s_0_125_local_magnitude_early_hop_fraction]{.metric} | [s_0_125_max_upper_population_error]{.metric} | [s_0_125_max_product_probability_error]{.metric} | [s_0_125_max_centroid_x_sigma_error]{.metric} |
| 0.10 | [s_0_10_local_magnitude_lifetime_fs]{.metric} | [s_0_10_local_magnitude_early_hop_fraction]{.metric} | [s_0_10_max_upper_population_error]{.metric} | [s_0_10_max_product_probability_error]{.metric} | [s_0_10_max_centroid_x_sigma_error]{.metric} |
| 0.075 | [s_0_075_local_magnitude_lifetime_fs]{.metric} | [s_0_075_local_magnitude_early_hop_fraction]{.metric} | [s_0_075_max_upper_population_error]{.metric} | [s_0_075_max_product_probability_error]{.metric} | [s_0_075_max_centroid_x_sigma_error]{.metric} |
| 0.05 | [s_0_05_local_magnitude_lifetime_fs]{.metric} | [s_0_05_local_magnitude_early_hop_fraction]{.metric} | [s_0_05_max_upper_population_error]{.metric} | [s_0_05_max_product_probability_error]{.metric} | [s_0_05_max_centroid_x_sigma_error]{.metric} |

**Table 2.** Descriptive archived FP--RP results using the mean single-trajectory coherence-magnitude lifetime. They are not measurements of ensemble optical coherence, and the archived numerical gate did not pass.

<figure>
  <img src="/images/2026-08-04-conical-intersection-outrun-decoherence-hero.png" alt="Archived local-magnitude early-event fractions on the horizontal axis and normalized FP minus RP errors on the vertical axis, explicitly labeled as not ensemble optical coherence.">
</figure>

**Figure 1.** Archived maximum FP--RP errors normalized by their registered
tolerances versus the local-magnitude early-event fraction. A marks the maximum
normalized upper-population difference across rate multipliers, B the maximum
normalized product-probability difference, and C the maximum normalized
centroid difference. The horizontal coordinate uses local-magnitude timing, not
ensemble optical coherence.

The recrossing reconstruction found
[s_0_075_recrossing_events]{.metric} true returns among
[s_0_075_repeat_hop_events]{.metric} repeats at $s=0.075$, and
[s_0_05_recrossing_events]{.metric} true returns among
[s_0_05_repeat_hop_events]{.metric} repeats at $s=0.05$. The FP
coefficient-versus-active-state inconsistency rose from a seed maximum of
[s_1_fp_consistency_error_max]{.metric} at $s=1$ to
[s_0_075_fp_consistency_error_max]{.metric} at $s=0.075$ and
[s_0_05_fp_consistency_error_max]{.metric} at $s=0.05$.

Table 3 reports selected-exact RMSE for the two archived local-magnitude
majority settings.

| $s$ | Method | $P_+$ RMSE | $P(q_x<0)$ RMSE | Centroid RMSE ($\sigma_x$) |
| ---: | :--- | ---: | ---: | ---: |
| 0.075 | FP | [s_0_075_full_rmse_selected_exact_upper_population]{.metric} | [s_0_075_full_rmse_selected_exact_product_probability]{.metric} | [s_0_075_full_rmse_selected_exact_centroid_x_sigma]{.metric} |
| 0.075 | RP-AXE | [s_0_075_reprop_axe_rmse_selected_exact_upper_population]{.metric} | [s_0_075_reprop_axe_rmse_selected_exact_product_probability]{.metric} | [s_0_075_reprop_axe_rmse_selected_exact_centroid_x_sigma]{.metric} |
| 0.05 | FP | [s_0_05_full_rmse_selected_exact_upper_population]{.metric} | [s_0_05_full_rmse_selected_exact_product_probability]{.metric} | [s_0_05_full_rmse_selected_exact_centroid_x_sigma]{.metric} |
| 0.05 | RP-AXE | [s_0_05_reprop_axe_rmse_selected_exact_upper_population]{.metric} | [s_0_05_reprop_axe_rmse_selected_exact_product_probability]{.metric} | [s_0_05_reprop_axe_rmse_selected_exact_centroid_x_sigma]{.metric} |

**Table 3.** Descriptive RMSE against the selected exact trace. FP used
[legacy_fp_paths_per_seed]{.metric} nuclear paths per seed and scale; RP-AXE
used [legacy_rp_axe_paths_per_seed]{.metric}. The exact trace passed a spatial
grid audit but not timestep or box-size audits.

## Discussion

The original headline does not survive the observable audit. Averaging
$|c_-^*c_+|$ answers whether individual trajectories retain mixed-state
amplitude on average. It does not answer whether their phases remain aligned
well enough to produce ensemble pump-generated or optical coherence. Because
the archived phases are absent, no reanalysis can move the magnitude outside
the ensemble after the fact.

The corrective gate gives useful but incomplete evidence. At its sole test
scale, both numerical settings put only about a quarter of accepted events
inside the phase-sensitive lifetime, far below the half-event boundary. That
classification is stable across the settings. But the registered centroid
criterion failed, so the protocol does not permit treating either setting as a
production endpoint. The proper verdict is inconclusive: the corrected run
neither supports nor falsifies the seven-scale optical-coherence hypothesis.

The archived sweep still has a legitimate narrower result. As the artificial
PFM damping multiplier falls, the mean single-trajectory magnitude lasts
longer, the fraction of events before that local lifetime rises, and FP and
RP-AXE separate. Figure 1 and Table 2 document that sensitivity. They do not
open the regime discussed by Galiana and co-workers, and the failed archived
coarse/fine criterion prevents an exact claim about a two-regime onset.

FP--RP separation is also not the same as RP-AXE inaccuracy. The selected exact
trace sometimes ranks RP-AXE closer than FP in the stressed settings, but
RP-AXE used twice as many nuclear paths, and the exact calculation was not
audited in timestep or box size. Meanwhile, the growing
coefficient-versus-active-state inconsistency supplies an alternative
explanation: artificially slow PFM damping may stress FP surface-hopping
consistency, moving FP away from both RP and the selected exact trace. The
present artifacts do not isolate that mechanism.

The recrossing defect was bookkeeping, not a change to the primary denominator.
Every accepted event—including repeats—remains in the early-event fraction.
Reconstructing true returns changes only the secondary description of those
events. Removing runtimes and timestamps likewise changes provenance bytes,
not scientific arrays; source hashes preserve the link to the original
artifacts.

## Conclusion

I withdraw the claim that this experiment found conical-intersection hops
outrunning ensemble optical coherence. The archived production sweep measures
mean single-trajectory coherence magnitude and is descriptive because its own
numerical gate missed tolerance. The phase-sensitive corrective experiment
stopped at convergence, as its frozen rule required.

A new attempt should begin with another preregistration, retain signed density-
matrix components in a fixed gauge, and demonstrate a converged trajectory
endpoint before running the seven-scale production sweep. A timestep- and
box-audited exact reference and an equal-cost FP/RP comparison would make the
secondary accuracy ranking more informative. If the gauge construction,
pooling rule, or interpretation here is still incomplete, I would especially
like to know; that would change the next protocol before it creates more data.

## References
