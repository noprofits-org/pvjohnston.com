# Preregistration v1: One muon, two frames

This is a prospective protocol. It was written before canonical execution and
before any production survival result was inspected. The registered form is
**Understanding**. It deliberately contains no novelty claim, contribution
sentence, hypothesis, falsifier, or scientific verdict.

## Intellectual contract

- **Working title:** “One muon, two frames.”
- **Post type:** understanding.
- **Explanatory question:** How do time dilation in the detector frame and
  length contraction in the muon frame give the same survival probability for
  an idealized 3.00 GeV/c muon traveling 15.0 km?
- **Assumed audience:** A reader who knows algebra, the exponential decay law,
  and the qualitative meanings of time dilation and length contraction, but
  who has not yet connected those ideas through proper time. Four-vectors are
  not assumed.
- **Source relationship:** The Particle Data Group supplies the muon mass,
  proper mean lifetime, and tightly bounded atmospheric-shower context. This is
  an independently implemented textbook-scale demonstration, not a
  reproduction of a PDG calculation or a historical experiment.

The explanation must proceed in this dependency order:

1. Define exponential survival in terms of elapsed proper time,
   \(P=\exp(-\Delta\tau/\tau_0)\), and distinguish a mean lifetime from a
   deterministic death time.
2. Convert the stipulated momentum and muon mass into \(\gamma\) and \(\beta\)
   without yet evaluating a survival probability.
3. In the detector frame, obtain the laboratory travel time and compare it with
   the dilated mean lifetime.
4. Independently, in the muon frame, contract the path, obtain the elapsed
   proper time, and compare it with the proper mean lifetime.
5. Put the two dimensionless decay exponents side by side and explain that they
   are coordinate descriptions of one proper-time interval, not two causal
   mechanisms.
6. Compare the analytic survival curve with one registered Monte Carlo sample
   from the assumed exponential law.
7. Add a clearly labelled same-speed counterfactual that removes lifetime
   dilation while holding the speed fixed.
8. Stop at the fixed-momentum, decay-only boundary and name the omitted physics.

The computation may demonstrate algebraic frame agreement, the consequences
of exponential decay under the stated idealization, and a population-level
implementation check. It cannot establish relativity independently, validate
the exponential law experimentally, predict atmospheric-muon flux, or say
that 3.00 GeV/c or 15.0 km is typical.

## Model and source boundary

The model is one free muon moving inertially along a straight laboratory path
at constant speed. Momentum is fixed, and decay is the only removal process.
Muon charge is irrelevant to the model. The calculation uses no production
height or energy distribution, energy loss, air density, scattering,
zenith-angle distribution, pion or kaon shower simulation, CORSIKA, detector
acceptance, capture, measured sea-level flux, or historical-experiment data.

The Particle Data Group cosmic-ray review may support only the bounded context
that charged-pion decays contribute shower muons and that sufficiently
energetic muons can reach ground. Its shower and flux statements do not enter
the calculation. This model stops before every transport, shower, atmosphere,
and detector question.

The external sources were accessed 2026-08-08:

- `https://pdg.lbl.gov/2024/listings/rpp2024-list-muon.pdf`, SHA-256
  `a3653f756a670b41a215b4a9746e6b5d872fe798a478e233acfc0bc1715eeb03`,
  135593 bytes. The registered central values are
  \(m_\mu c^2=105.6583755\) MeV and
  \(\tau_0=2.1969811\) microseconds. The listing reports uncertainties of
  0.0000023 MeV and 0.0000022 microseconds, respectively.
- `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmic-rays.pdf`, SHA-256
  `c8f0620d58d3d61a7b0eae5d2606ce65bbe581a9000c5435299d88ca9ea0125e`,
  2588758 bytes. This source is context only and is not a computational input.

The setup must transcribe the two registered central values into a committed,
machine-readable constants file and record the source URLs, access date,
digests, units, and acquisition commands in a source manifest. The speed of
light is the exact SI value 299792458 m/s. Source uncertainty propagation is
outside this explanatory demonstration; the post must say that it uses PDG
central values rather than imply that the quoted input precision governs the
scope of the result. No PDF is bundled.

## Pilot boundary

No scientific feasibility pilot is needed. Setup may run unit tests and timing
smoke tests only on deterministic toy arrays or on at most 16 exponential draws
from PCG64 seed 0. Those fixtures must use visibly nonproduction paths, must not
use seed 20260808, must not enter `runs/run-001/`, and must not be quoted,
plotted, projected into metrics, or used to alter any frozen choice.

The canonical seed, 100000-draw sample, 3.00 GeV/c momentum, 15.0 km focal
point, and full distance grid may not be executed before setup review approves
the protocol implementation, tests, environment, and exact command. Discovering
a need to inspect those values during setup blocks approval rather than creating
a “pilot.”

## Frozen inputs and deterministic controls

- Momentum: exactly 3.00 GeV/c as a stipulated demonstration value; represent
  it internally as 3000.0 MeV/c.
- Laboratory grid: integer indices \(i=0,\ldots,200\), with
  \(L_i=100i\) m. This is 0--20 km inclusive in 0.1 km increments without a
  floating-point endpoint convention.
- Main explanatory index: \(i=150\), or 15.0 km.
- Production draw count: exactly 100000.
- Bit generator: `numpy.random.PCG64`.
- Production seed: exactly 20260808.
- Generator construction: `numpy.random.Generator(numpy.random.PCG64(20260808))`.
- Draw operation: one call to `Generator.exponential(scale=tau0_s,
  size=100000)`, retained as a one-dimensional float64 array in draw order.
- There is one production sample and one production seed. Never reroll, choose
  among seeds, append a seed, or extend the sample after seeing any production
  value.
- All numerical derivations use IEEE-754 binary64. Grid order and artifact
  serialization order are ascending in \(i\); Monte Carlo draw order is never
  sorted in the sealed raw artifact.

There is no external dataset, paid service, credential, network call during
execution, living subject, or newly collected observation.

## Frozen frame reconstructions

The analyst must implement two visibly separate functions that share only the
registered primitive inputs. One function may not call the other or consume
the other's derived \(\beta\), \(\gamma\), elapsed time, exponent, or survival
array.

### Detector-frame route

Using MeV units for energy and mass-energy,

\[
E=\sqrt{(pc)^2+(m_\mu c^2)^2},\qquad
\gamma_D=\frac{E}{m_\mu c^2},\qquad
\beta_D=\frac{pc}{E}.
\]

For every laboratory path \(L_i\), reconstruct

\[
t_D(L_i)=\frac{L_i}{\beta_D c},\qquad
\tau_D=\gamma_D\tau_0,\qquad
x_D(L_i)=\frac{t_D(L_i)}{\tau_D},\qquad
P_D(L_i)=e^{-x_D(L_i)}.
\]

### Muon-frame route

Independently compute

\[
r=\frac{pc}{m_\mu c^2},\qquad
\gamma_M=\sqrt{1+r^2},\qquad
\beta_M=\sqrt{1-\gamma_M^{-2}}.
\]

Then reconstruct the contracted path, proper elapsed time, exponent, and
survival as

\[
L'_i=\frac{L_i}{\gamma_M},\qquad
t_M(L_i)=\frac{L'_i}{\beta_Mc},\qquad
x_M(L_i)=\frac{t_M(L_i)}{\tau_0},\qquad
P_M(L_i)=e^{-x_M(L_i)}.
\]

The explanation must identify \(t_M=\Delta\tau=t_D/\gamma\). Time dilation and
length contraction are alternative coordinate routes to this invariant elapsed
proper time.

### Same-speed no-dilation counterfactual

Hold \(\beta=\beta_D\) and the laboratory path fixed, but replace the dilated
mean lifetime with \(\tau_0\):

\[
x_{\mathrm{no\ dil}}(L_i)=\frac{L_i/(\beta_Dc)}{\tau_0},\qquad
P_{\mathrm{no\ dil}}(L_i)=e^{-x_{\mathrm{no\ dil}}(L_i)}.
\]

Every artifact, legend, caption, and prose use must label this as a
**same-speed, no-lifetime-dilation counterfactual**. It is not a third frame, a
second physical model of atmospheric muons, or evidence against a Newtonian
theory.

## Monte Carlo implementation check

The run operator generates and seals only the registered proper-lifetime
sample, its manifest, logs, and hashes. The run operator does not calculate
survival curves, inspect scientific values, analyze, tune, plot, or draft.

After run review admits that sample, the analyst converts each grid path to the
proper-time threshold from the independently reconstructed muon-frame route.
At each grid point, a draw survives when
`proper_lifetime_s >= proper_elapsed_time_s`; the inclusive comparison is
frozen even though equality has zero probability in the continuous model.
Counts are obtained from the same 100000 draws at every grid point and divided
by 100000 for empirical survival. The Monte Carlo is a population-level
implementation check of the assumed exponential law. It is not independent
evidence for special relativity.

## Frozen observables and acceptance checks

The canonical rich result must retain the primitive inputs, both independently
derived \(\beta\) and \(\gamma\) values, the full grid, both frame-specific
distances/times/lifetimes/exponents/probabilities, the counterfactual curve,
empirical counts and probabilities, the focal-point values, and every check
below. No additional scientific curve or seed is authorized.

All comparisons are inclusive at their stated threshold:

1. For all 201 grid points,
   `abs(P_D - P_M) / max(abs(P_D), abs(P_M)) <= 1e-12`. For every nonzero
   path, apply the same relative check to \(x_D\) and \(x_M\); at zero path,
   require both exponents to be exactly zero. Also require separately derived
   \(\beta\) and \(\gamma\) values to agree to relative tolerance 1e-12.
2. At index 150, let \(P=P_D\), \(\hat P=C/100000\), and define the
   prospective binomial standard error as
   \(s=\sqrt{P(1-P)/100000}\), using the analytic rather than empirical
   probability. Require \(|\hat P-P|\leq4s\).
3. Require `max(abs(empirical_survival - P_D)) <= 0.01` over the complete
   frozen grid.
4. Require exactly 201 integer counts, each in `[0, 100000]`, the zero-distance
   count equal to 100000, and successive counts monotonically nonincreasing.
5. Require all primitive and derived numeric values to be finite, all sampled
   proper lifetimes to be nonnegative, array shapes/dtypes/units to match their
   schemas, every manifest link and provenance digest to resolve, and every
   recorded artifact SHA-256 to verify byte for byte.
6. Require deterministic regeneration of the canonical result, figure, and
   `metrics.json` from the admitted raw sample; require the metrics generator
   `--check`, repository metrics validation, workflow verification, public-file
   manifest validation, and PNG dimension check to pass.

These are implementation and fidelity checks, not a Research hypothesis or
verdict. A failed check is retained and reported to review. It blocks
publication of the intended demonstration and may not be repaired by changing
the seed, adding draws, loosening a tolerance, deleting a grid point, or
choosing a different output. An independently identified implementation defect
after exposure follows the amendment route; otherwise the workflow parks.

## Analysis route and uncertainty boundary

The preregistered analysis is deterministic:

1. Validate and hash the admitted run manifest and raw sample without modifying
   them.
2. Reconstruct the detector-frame and muon-frame arrays independently.
3. Reconstruct the same-speed counterfactual.
4. Calculate nested survival counts from the sealed lifetime sample.
5. Evaluate all frozen checks, including the analytic-probability binomial
   standard error at 15.0 km and the grid-wide maximum absolute discrepancy.
6. Write one canonical JSON result in fixed key/grid order.
7. Generate the one registered PNG and the typed metrics projection only from
   that canonical JSON; check-mode regeneration must byte-check or
   value-and-rendering-check every output as appropriate.

The binomial standard error quantifies Monte Carlo sampling variation under
the assumed law; it is not an uncertainty on relativity. PDG input
uncertainties, momentum spread, path uncertainty, and model discrepancy are
not propagated. No confidence interval, parameter fit, hypothesis test,
post-hoc sensitivity, or atmospheric inference is planned.

## Registered figure and metrics

Generate exactly one reader-facing figure at
`images/muon-survival-two-frames-hero.png`. It must be a 1200 by 630 pixel PNG
with two horizontal panels, the site's high-contrast palette, no clipping, and
only axis labels, tick labels, legend entries, panel labels, and lettered
callouts inside the plot area.

- **Left panel:** analytic survival versus laboratory path over the frozen
  grid, the empirical survival from the one registered sample, and the clearly
  labelled same-speed/no-lifetime-dilation counterfactual. The two analytic
  frame reconstructions must both be present or explicitly encoded as
  coincident; the graphic must not suggest two causal effects.
- **Right panel:** the dimensionless exponent at 15.0 km. Use two aligned rows
  or markers for \(t_D/(\gamma\tau_0)\) and \(t_M/\tau_0\), with lettered
  callouts whose caption identifies the detector-frame laboratory distance and
  time and the muon-frame contracted distance and proper time. The equality
  must be visible without rounding one result toward the other.

The eventual numbered caption carries explanations and generated values; it
must describe the Monte Carlo as an implementation check and the no-dilation
curve as a counterfactual. Alt text must state the conceptual comparison.

The metrics projection is frozen by name, not by expected value. It should
include the two derived kinematic factors; detector and muon-frame times,
distances, lifetimes, and exponents at 15.0 km; analytic, empirical, and
counterfactual survival there; the survivor count; the prospective binomial
standard error and standardized discrepancy; the maximum grid discrepancy;
and typed pass/fail fields for every registered check. The post must use metric
spans for any generated quantitative claim.

## Environment and resource budget

The intended locked environment is Linux x86-64, CPython 3.12.3,
`numpy==2.5.1`, and `matplotlib==3.11.1`. NumPy owns all production random
number generation and numeric arrays; Matplotlib is analysis-only. The
experiment engineer must create a hash-locked dependency record, reject a
Python or NumPy version mismatch at runtime, record actual OS/architecture and
package versions in the run manifest, and eliminate locale/timezone-dependent
serialization. Publication metrics use the repository's Node.js tooling; the
setup receipt must record its exact version.

The canonical production command to be implemented and reviewed is:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

It must finish in less than 60 seconds on one ordinary x86-64 CPU core, use no
GPU, require less than 256 MB peak resident memory, make no network request,
and cost no money. The deterministic analysis and figure command should also
finish in less than 60 seconds. All generated outputs for this experiment,
including the PNG but excluding the untracked virtual environment, must total
less than 10 MB.

## Run identity, integrity, and restart boundary

The only normal production namespace is
`research/muon-survival-two-frames/runs/run-001/`. It is append-only and may
not pre-exist. The raw lifetime array, stdout, stderr, run manifest, completion
record, and checksums remain immutable after completion. The manifest binds the
run ID to protocol, constants, source manifest, implementation, environment,
command, seed, draw count, timestamps, hardware, exit state, and artifact
digests. Self-referential checksum files are excluded from their own digest.

There is no useful same-run resume: sample creation is all-or-nothing. An
interrupted or partially written run is preserved and quarantined. One
`registered_retry` with a fresh run ID is prospectively authorized only for an
objective infrastructure failure before a valid completion record exists,
such as process termination or filesystem I/O failure. It must use identical
protocol, code, constants, environment, command arguments, PCG64 seed, and draw
count, so it cannot create a new random sample. It may not overwrite or borrow
from the failed namespace. A retry for a failed scientific/fidelity check or
after choosing between complete outputs is forbidden.

No `registered_rerun` is authorized. Analysis and figure regeneration consume
the same admitted raw sample and do not rerun production. Any post-exposure
change to protocol, code contract, inputs, environment definition, grid, seed,
draw count, thresholds, exclusions, stopping rule, or figure content requires
the explicit amendment route and independent review.

## Expected artifacts and publication boundary

Setup should implement schemas, tests, code, environment lock, source and input
manifests, and exact commands under the experiment directory. Execution should
add a single run namespace. Analysis should add a canonical rich result,
check-mode regeneration code, `metrics.json`, its generator, and the registered
PNG. Small handoff and review receipts live under `workflow/` and refer to
larger artifacts by repository-relative path, byte size, and SHA-256.

The eventual `PUBLIC_FILES.txt` is an explicit allowlist reviewed after the
artifacts exist. It may include only the stable reader-facing protocol,
environment/source manifests, code, canonical summary, metric projection, and
other small reproducibility files needed to rerun or audit the demonstration.
It must exclude the virtual environment, caches, temporary files, full logs,
workflow-private scratch, and any redundant source PDF. The raw lifetime sample
may be omitted from the served bundle because the registered seed and locked
environment regenerate it; if omitted, that choice and its reproduction effect
must be explicit. Every committed file is public regardless of serving.

The design can earn **end-to-end reproducible** only if a clean locked
environment regenerates the sealed sample, canonical result, metrics, and PNG
with all hashes and checks passing. Before that evidence exists, the status is
**not yet established**. No living subject, private data, credential, paid
resource, restricted dataset, or nonredistributable input is involved.

## Stopping and amendment rules

Production stops after the single registered sample and its integrity records
are complete. Analysis stops after the prespecified arrays, checks, canonical
JSON, one PNG, and metric projection are generated. There is no adaptive sample
size, extra seed, extra grid, second figure, atmospheric extension, or
result-driven diagnostic.

None at freeze. Before result exposure, independent question or setup review
may require a new prospective version. After any production exposure, this
file remains immutable: a scientific or setup change requires a separately
versioned amendment packet, amendment review, amended setup, and amended setup
review. A changed explanatory question starts a new workflow.
