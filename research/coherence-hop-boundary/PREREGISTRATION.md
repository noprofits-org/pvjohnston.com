# Preregistration: coherence–hop boundary

**Protocol status:** the original protocol below is retained as the historical
record, but its coherence observable was superseded by the corrective amendment
at the end of this file before any corrective canonical run. Results from the
original run are not used to adjudicate the corrected question.

Frozen at 2026-08-05T02:43:53Z, after the explicitly disclosed feasibility
pilots below and before implementation, lineage validation, numerical
convergence, exact-grid audit, or any confirmatory trajectory result. The
protocol is derived from the ready question, “Can a conical-intersection model
sustain a majority of hops before decoherence?”, on `notes/questions.md`.

## Source relationship and contribution gate

This is an independent sensitivity extension of Joachim Galiana and
co-workers, “Accounting for Electronic Coherences Induced by Broadband Pulses
by Using Pulse-Independent Trajectories” (2026),
doi:10.1021/acs.jctc.5c01809, with the companion PFM account by Gilbert Grell
and co-workers, “Advances in the Projected Forces and Momenta Decoherence
Method for Attosecond Nonadiabatic Molecular Dynamics” (2026),
doi:10.1039/D6FD00086J.

Contribution: an adjudicated RP-AXE sensitivity test in a regime where most
accepted surface hops precede the pump-coherence lifetime, jointly scored by
electronic population, product-side probability, and nuclear centroid against
exact dynamics, which is not reported by Galiana et al. or Grell et al.

Contribution type: **untested regime**.

The public Galiana article links one supporting-information PDF. The public
Grell article is an open accepted manuscript. At the access date, neither
source linked a public patch for its locally modified SHARC program, raw
molecular trajectory archive, or reusable implementation of the RP-AXE
workflow. This experiment does not call the authors' program or use their
glycine, LiH, or dithiane calculations. It tests an independently implemented
reduced model and cannot be described as a software-level or molecular-data
reproduction.

## Question, hypothesis, and falsifier

Question: at a fixed BMA[5,5] Hamiltonian and launch packet, can slowing the
PFM decoherence algorithm create a finite-lifetime regime in which at least
half of accepted full-propagation hops occur while the initially prepared
electronic coherence survives, and does RP-AXE remain accurate there?

Hypothesis: lowering the PFM rate multiplier produces at least one declared
setting with an uncensored early-hop fraction at or above 0.5, and RP-AXE
exceeds at least one of these maximum-in-time FP–RP error limits in that
setting:

1. upper-adiabatic coefficient population: 0.05;
2. product-side probability `P(qx < 0)`: 0.05; or
3. nuclear centroid: `0.1 sigma_x`.

Falsifier: no declared setting reaches an uncensored early-hop fraction of
0.5, or every setting that reaches it remains at or below all three error
limits. The first outcome says the registered control did not create the
target regime; the second extends the tested robustness of RP-AXE. Both are
publishable.

The hypothesis is supported only if a majority-early-hop setting exists and
at least one of its three errors exceeds its limit. It is falsified by either
falsifier branch. It is inconclusive if the implementation-lineage gate cannot
be passed or a complete final sweep cannot be produced after applying the
registered convergence promotion rule. Thresholds are operational definitions
for this experiment, not universal physical constants.

## Exploratory pilots — excluded from confirmation

All pilots used the archived independent implementation, seed 1701, 1,000
matched Wigner geometries, center fraction 0.5, zero kick, a 0.025 fs nuclear
step, ten electronic substeps, and 20 fs propagation. They were used only to
locate a feasible final range. No pilot event, trajectory, uncertainty, or
error estimate enters the confirmatory result.

First, changing the molecular diabatic coupling through
`c/c0 = 0.125, 0.25, 0.5, 1, 2, 4, 8` yielded early-hop fractions from about
0.188 to 0.244 and did not approach the 0.5 target. This motivated keeping the
Hamiltonian fixed and changing the algorithmic damping rate instead.

A coarse PFM-rate pilot used `s = 0, 0.125, 0.25, 0.5, 1, 2`. Its finite
lifetimes and early-hop fractions were, respectively: at 0.125, 7.1648 fs and
0.48477; at 0.25, 5.0431 fs and 0.41161; at 0.5, 3.4948 fs and 0.30809; at 1,
2.3745 fs and 0.20855; and at 2, 1.6234 fs and 0.11387. The `s=0` trace did not
cross `C(0)/e` by 20 fs and was treated as censored rather than assigned an
early-hop fraction.

The final refinement inspected `s = 0.05, 0.075, 0.10, 0.11`:

| `s` | lifetime (fs) | early-hop fraction | max population error | max product error | max centroid error (`sigma_x`) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.05 | 11.5426 | 0.60561 | 0.13372 | 0.13456 | 0.90857 |
| 0.075 | 9.3210 | 0.55214 | 0.13132 | 0.12970 | 0.85620 |
| 0.10 | 8.0525 | 0.51061 | 0.12051 | 0.11761 | 0.76936 |
| 0.11 | 7.6619 | 0.50528 | 0.11893 | 0.11359 | 0.74083 |

These pilot observations made the hypothesis data-informed. The final scale
grid deliberately retains the source-method value `s=1`, brackets the apparent
transition, uses four fresh seeds, and quadruples the geometry count. The
unregistered `s=0.11` pilot point is not promoted into confirmation.

## Frozen molecular and launch model

The two-state, two-mode BMA[5,5] linear-vibronic-coupling Hamiltonian is fixed
in mass-weighted atomic units by
`omega_x=7.743e-3`, `omega_y=6.68e-3`, `a=31.05`, and `c=8.092e-5`.
The real diabatic initial state has amplitudes `sqrt(0.8)` and `sqrt(0.2)`
(`delta_p=0.6`). The minimum-uncertainty Wigner packet retains the published
widths. Its center is fixed at `qx,0/(a/2)=0.5`, `qy,0=0`, and its mean
momentum is zero in both modes. Duration is 20 fs.

The computation represents a reduced molecular Hamiltonian through an
ensemble of sampled nuclear paths. It does not propagate an explicit laser
field, calculate a detector response, synthesize a photon-count trace, or
claim to be a literal laboratory single-molecule record. The optical element
is the prepared initial electronic coherence.

## Algorithmic stress dial and paired methods

The underlying projected-forces-and-momenta rate `Gamma_PFM` and momentum
injection follow the independent implementation of the published TSH-PFMi
algorithm. The experiment applies

`Gamma_used = s * Gamma_PFM`

to FP, the pure-state AXE base paths, and the coherent coefficients
repropagated along those paths. The dimensionless multiplier `s` is an
**algorithmic sensitivity dial, not a molecular parameter**, fitted lifetime,
or claim about physical solvent coupling.

Confirmatory scales, in fixed order:

`[1, 0.5, 0.25, 0.125, 0.10, 0.075, 0.05]`.

Every scale uses seeds 2701, 2702, 2703, and 2704, with 4,000 matched Wigner
geometries per seed. Pilot seed 1701 and convergence seed 2699 are excluded
from final inference. The AXE construction creates a pure lower- and a pure
upper-state path for every geometry. All random draws are derived solely from
the declared per-run seed; worker scheduling cannot select a different stream.

Nuclei use velocity Verlet. Electronic amplitudes are propagated analytically
in the diabatic basis. Density-flux proposals are evaluated in the adiabatic
basis, and accepted hops use isotropic momentum rescaling. The PFM inactive-
population threshold is `1e-4`.

## Implementation-lineage gate

The immediate ancestor is
`downloads/pulse-independent-ci-data.tar.gz` at repository commit `b527db4`
(`b527db4a4f31012f751981f580e27bca763f9e54`). Its required SHA-256 is
`eb8a7ed3e13c0c02a6872da57f23317a541c764d44f060902b0874b8e99e29d0`.
The directly loaded ancestor `downloads/pulse-independent-ci.py` has SHA-256
`9a62440a32f99057f699ec9de8c58fc2a19e0bf78f0848fd8826d1b23aa72350`.

Before convergence or confirmation, run the new parameterized path at `s=1`
and the archived implementation on one identical small deterministic input.
The ancestor-source checksum must match, accepted-hop records must be
identical, and every compared observable array must pass `rtol=1e-12` and
`atol=1e-12`. Failure blocks all later stages. A correction to parameterization
or instrumentation must be documented and the gate rerun before any
confirmatory data are generated; the gate may not be weakened.

## Independent numerical convergence gate

At `s=0.05`, center fraction 0.5, zero kick, seed 2699, 4,000 geometries, and
20 fs, compare:

- planned production: 0.025 fs nuclear step, ten electronic substeps; and
- fine: 0.0125 fs nuclear step, twenty electronic substeps.

The planned setting is retained only when every criterion passes:

- absolute early-hop-fraction difference at most 0.02;
- absolute coherence-lifetime difference at most 0.15 fs;
- maximum paired FP upper-population series difference at most 0.02;
- maximum paired FP product-probability series difference at most 0.02;
- maximum paired FP centroid series difference at most `0.03 sigma_x`;
- unchanged majority classification (`early-hop fraction >= 0.5`); and
- unchanged compound RP-AXE robustness classification under the three
  declared error limits.

If any criterion fails, the 0.0125 fs/twenty-substep setting is promoted to all
seven confirmatory scales. The final sweep is not interpreted with mixed time
steps, and no tolerance is relaxed.

## Exact-grid audit

The exact reference uses second-order split-operator propagation in the global
diabatic basis on the same invariant Hamiltonian and launch state, periodic
grids over `[-96,96)^2`, a 0.025 fs step, and 20 fs duration. Compare a
384 by 384 production candidate with a 512 by 512 audit trace. The 384-grid
trace is retained only if:

- maximum upper-population difference is at most `2e-4`;
- maximum `P(qx < 0)` difference is at most 0.005;
- maximum centroid difference is at most `0.01 sigma_x`; and
- maximum norm error in the 512-grid trace is below `1e-10`.

Otherwise the 512 by 512 trace becomes the production exact reference. No PFM
multiplier enters exact propagation, so the accepted exact trace is reused for
all seven scales.

## Event, lifetime, and aggregation definitions

An **accepted hop event** is a density-flux hop proposal for which isotropic
momentum rescaling has sufficient kinetic energy and the FP active state
changes. A proposal rejected for insufficient kinetic energy is **frustrated**
and is not accepted. Every accepted state change is an event: repeated and
backward hops by one trajectory remain separate denominator events rather than
being collapsed to one hopping trajectory.

For each scale, FP and RP observable time series are averaged over the four
seeds. Accepted FP event times are concatenated across those seeds. The
coherence amplitude is

`C(t) = mean[2 * abs(conj(c_minus) * c_plus)]`

after PFM damping. The lifetime `tau_1/e` is the first linearly interpolated
crossing of `C(0)/e` in the four-seed mean FP trace. The early-hop fraction is

`count(accepted FP event time <= tau_1/e) / count(all accepted FP events <= 20 fs)`.

The boundary is inclusive. If no crossing occurs by 20 fs, the lifetime is
right-censored and both lifetime and fraction are serialized as censored/null
rather than assigning 20 fs. If there are no accepted FP events, the fraction
is null. Either null case is ineligible for the majority gate.

Per-seed values and 95% intervals are retained as uncertainty descriptions,
but the preregistered decision uses the four-seed aggregate defined above.

## Primary and secondary outcomes

Primary:

1. whether each declared scale has an uncensored early-hop fraction at or
   above 0.5;
2. maximum-in-time absolute FP–RP difference in product-side
   `P(qx < 0)`, the primary nuclear observable; and
3. the compound robustness decision requiring upper-population error at or
   below 0.05, product error at or below 0.05, and centroid error at or below
   `0.1 sigma_x` for every reached majority regime.

The upper-population and centroid errors are therefore mandatory primary
decision components even though product probability is the designated nuclear
outcome.

Secondary:

- FP and RP root-mean-square and maximum errors against the accepted exact
  wavepacket trace for population, product probability, and centroid;
- FP–RP coherence-amplitude error;
- lifetime and error estimates by seed with 95% intervals;
- proposed, frustrated, and accepted hop counts, split by direction and by
  early/late timing;
- first and repeated accepted hops and the fraction of trajectories with each,
  to reveal recrossing inflation of the event denominator;
- electronic norm, coefficient-population versus active-state consistency,
  and energy-drift diagnostics; and
- runtime and complete-run metadata.

Secondary diagnostics cannot replace or redefine the accepted-event primary
outcome after inspection.

## Reproducibility and stopping

The registered environment is Linux x86_64, CPython 3.12.9, NumPy 2.2.5, and
`OPENBLAS_NUM_THREADS=1`; plotting uses Matplotlib 3.10.8 and Pillow 12.1.0.
Declared seeds make Wigner sampling and hopping draws deterministic in this
environment. Results are sorted by frozen scale order and seed, independent of
worker completion order.

Run lineage, convergence, exact audit, then the seven-scale sweep. Stop after
the 28 confirmatory scale/seed replicates. Do not add scales, seeds, launch
conditions, observables, thresholds, or an explicit field after inspecting
confirmatory output. Apply only the registered finer-step and finer-grid
promotion rules. A missing majority regime is a falsifying result, not a
reason to extend the sweep. A lineage failure or unrecoverable incomplete
sweep is reported as inconclusive rather than repaired by relaxing a gate.

At freeze time, claim traceability is **not yet established** because no
canonical `results/analysis.json` or validated `metrics.json` exists. The
intended end state is end-to-end reproducibility after all commands pass,
canonical artifacts are committed, analysis and metrics checks reproduce
them, and the public manifest is verified.

## Corrective protocol amendment: phase-sensitive ensemble coherence

Frozen at 2026-08-05T05:37:38Z after review of the original canonical run and
the explicitly disclosed diagnostic checks below, and before modifying the
simulator or running the corrective lineage, fine/finer convergence, exact-grid,
or 28-replicate production calculations. This amendment supersedes the original
coherence observable, convergence gate, recrossing label, and artifact-timing
policy. The Hamiltonian, launch distribution, PFM-rate scales, production seeds,
geometry count, duration, FP–RP tolerances, and compound decision rule do not
change.

### Reason for amendment and disclosed diagnostics

The original protocol used

`mean[2 * abs(conj(c_minus) * c_plus)]`.

That order of operations retains each trajectory's coherence magnitude before
the ensemble average, so opposite phases cannot cancel. Mannouch and Kelly
distinguish this local-magnitude measure from the ensemble off-diagonal density
matrix whose decay includes pure dephasing. The original observable therefore
cannot adjudicate the article's claim about surviving pump-generated or optical
ensemble coherence.

After finding the mismatch, read-only 250-geometry diagnostics at `s=0.075`
and `s=0.05` indicated that phase-sensitive adiabatic and diabatic definitions
could move the early-hop fractions below 0.5. Those checks establish that the
correction can change the verdict. They make this amendment data-informed and
are not treated as prospective evidence. Their trajectories, event counts, and
estimates are excluded from the corrective canonical results.

### Corrective question, contribution, and decision

Question: at the fixed BMA[5,5] Hamiltonian and launch packet, can lowering the
PFM rate multiplier create a finite-lifetime regime in which at least half of
accepted FP hops occur while a phase-sensitive ensemble electronic coherence
survives, and does RP-AXE remain equivalent to FP there under the three declared
error limits?

Corrective contribution: a gauge-defined, phase-sensitive reassessment of the
RP-AXE trajectory-equivalence boundary, with real and imaginary ensemble
density-matrix elements retained and multi-seed fine/finer convergence, which
is not reported by Galiana et al. or Grell et al.

The original directional hypothesis and falsifier are retained: the hypothesis
is supported only if at least one of the seven unchanged scales has an
uncensored phase-sensitive early-hop fraction at or above 0.5 and exceeds at
least one FP–RP tolerance. It is falsified if no scale reaches 0.5 or every
reached scale remains within all three tolerances. Because the correction was
motivated by diagnostics that suggested the first falsifier branch, the final
article must label the run a corrective confirmation rather than an outcome-
blind preregistration.

Exact wavepacket dynamics remains a secondary comparison. It does not enter the
support/falsification rule, and any FP-versus-RP ranking must be described as a
configured-method ranking rather than an equal-cost accuracy result.

### Primary coherence observable and fixed gauge

For each trajectory, convert the propagated diabatic amplitudes to the
adiabatic basis using the implementation's explicit real gauge

`theta = atan2(c * qy, kappa(qx))`,

`|minus> = (cos(theta/2), -sin(theta/2))`, and

`|plus> = (sin(theta/2), cos(theta/2))`.

The primary ensemble density-matrix element is

`rho_minus_plus(t) = mean[conj(c_minus(t)) * c_plus(t)]`,

with the RP-AXE mean carrying its frozen trajectory weights. Every run must
retain the two signed series

`C_real(t) = 2 * Re(rho_minus_plus(t))` and

`C_imag(t) = 2 * Im(rho_minus_plus(t))`.

The primary amplitude is reconstructed from those stored components,

`C_ens(t) = sqrt(C_real(t)^2 + C_imag(t)^2)`,

before finding the first linearly interpolated `C_ens(0)/e` crossing. For a
four-seed aggregate, average `C_real` and `C_imag` across seeds first and take
the magnitude afterward. Averaging seed-level amplitudes is not permitted.

The principal `atan2` range and the equations above fully specify the gauge.
Crossing its branch cut changes both real eigenvectors by a common sign, leaving
`conj(c_minus) * c_plus` unchanged. A geometry exactly at the conical
intersection uses NumPy's `atan2(0, 0) = 0` convention.

The original quantity is retained only as
`mean_trajectory_coherence_magnitude` and cannot define a lifetime,
classification, or optical-coherence claim. Exact propagation stores the same
signed ensemble density-matrix components and the local-magnitude diagnostic.

### Multi-seed fine/finer convergence gate

The original one-seed coarse/fine comparison failed its early-hop-fraction
tolerance and promoted the fine endpoint without demonstrating its convergence.
The corrective gate therefore tests only the proposed production setting
against a still finer reference at `s=0.05`, with four convergence-only seeds
2691, 2692, 2693, and 2694, 4,000 geometries per seed, and 20 fs duration:

- candidate: 0.0125 fs nuclear step and twenty electronic substeps;
- reference: 0.00625 fs nuclear step and forty electronic substeps.

Changing the substep count changes stochastic draw alignment, so individual
paths are not treated as paired trajectories. Seed-level ensemble estimates are
the paired replication unit. For early-hop fraction and coherence lifetime,
compute the mean candidate-minus-reference difference and its two-sided 95%
Student-t interval across the four seed pairs. For FP upper population, product
probability, and centroid, compute the paired difference series for each seed,
then the 95% interval of the mean difference at every candidate time point.

The candidate is converged only if all of the following hold:

- the largest absolute endpoint of the early-hop-fraction interval is at most
  0.02;
- the largest absolute endpoint of the coherence-lifetime interval is at most
  0.15 fs;
- the largest absolute endpoint over time is at most 0.02 for FP upper
  population and 0.02 for FP product probability;
- the largest absolute endpoint over time is at most `0.03 sigma_x` for the FP
  centroid; and
- pooled candidate and reference runs give the same majority-early-hop and
  compound FP–RP robustness classifications.

All four seeds must yield finite lifetimes and nonempty accepted-event
denominators at both settings. If any requirement fails, the corrected
experiment is inconclusive and the production sweep does not start. The finer
endpoint is not automatically promoted without a further registered comparison.

### Corrected event and artifact semantics

A repeat accepted hop is any accepted event after a trajectory's first. A
recrossing is narrower: a repeated accepted event whose target is the active
state at that trajectory's initialization. The raw event record stores both
labels. Neither changes the primary accepted-event denominator.

Canonical scientific JSON excludes wall-clock runtimes and run-generation
timestamps. Timing may be printed to the terminal but cannot enter an artifact
whose hash authorizes a downstream stage. The metrics schema requires a
`generated_at` field; its canonical value is pinned by the generator as a
source-date epoch and is not read from the rerun wall clock. Given the same
pinned environment and code, a clean rerun must reproduce canonical scientific
bytes independently of worker count and machine speed.

### Corrective run order and stopping

Rerun the implementation-lineage gate after the observer and event-label fixes.
The lineage comparison must still reproduce the ancestor's dynamics, accepted
events, and original local-magnitude diagnostic. Then run the multi-seed
fine/finer gate. Only a passing gate authorizes the exact-grid audit and the
unchanged 28 scale-by-seed production replicates. Stop after those replicates;
do not add scales or production seeds in response to the corrected outcome.

## Fixed replication extension after an imprecise convergence result

Frozen at 2026-08-05T06:31:07Z after the four-seed convergence gate completed
and before running any additional seed. The first gate failed only its centroid
interval criterion: at the worst time, 11.825 fs, the four paired differences
were `0.00215562`, `-0.00519913`, `0.05779717`, and `-0.00143201 sigma_x`.
Their mean, `0.01333041 sigma_x`, and the maximum absolute mean difference over
time, `0.01666676 sigma_x`, were below the unchanged 0.03 tolerance, but the
95% half-width was `0.04740576 sigma_x`, so the upper interval endpoint was
`0.06073617 sigma_x`. The gate correctly blocked production because equivalence
had not been demonstrated.

To distinguish an unresolved stochastic-path interval from a persistent
timestep shift, the replication count is doubled once by adding fresh
convergence-only seeds 2687, 2688, 2689, and 2690. The final convergence set is
therefore the eight pairs 2687–2694. Candidate and reference steps, 4,000
geometries per seed, duration, observables, component-pooling rule, 95%
two-sided Student-t interval, numerical tolerances, and classification
requirements are unchanged. The final interval uses the `n=8` Student-t
critical value 2.365.

This extension is explicitly data-informed by interval width. It has one fixed
stopping point: if the eight-pair gate fails any criterion, the correction is
inconclusive and no further seed, tolerance, or numerical-setting extension is
permitted. A pass validates only the 0.0125 fs/twenty-substep candidate already
named in the amendment; the 0.00625 fs/forty-substep reference is never promoted
without its own registered convergence comparison.

## Corrective run closeout

The eight-pair gate completed after the amendment above. This section records
the terminal result; it does not amend the frozen protocol.

Seven requirements passed. The maximum absolute 95% interval endpoints were
`0.0059556574606134715` for accepted-event fraction,
`0.01731191082246749 fs` for phase-sensitive lifetime,
`0.007088787414513684` for FP upper population, and
`0.00661291190962778` for FP product probability. Candidate and reference gave
the same non-majority and nonrobust classifications.

The FP centroid endpoint was `0.03860456796330737 sigma_x` at `14.2375 fs`,
above the unchanged `0.03 sigma_x` limit. The gate therefore failed. In
accordance with both the amendment and fixed replication extension, the
corrective experiment is inconclusive, no exact-grid audit or 28-run
phase-sensitive production sweep was started, and no additional seed,
tolerance change, or endpoint promotion is permitted within this protocol.

The pre-correction 28-run archive remains available only as descriptive
evidence for mean single-trajectory coherence magnitude. Its production
setting was selected after a coarse/fine early-event difference of
`0.021625746684215907`, which exceeded the original `0.02` tolerance, without a
fine/finer demonstration. It cannot adjudicate the phase-sensitive question.
