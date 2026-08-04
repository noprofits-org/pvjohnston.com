# Preregistration: SMX conformer thermochemistry

Frozen before the first sulfamethoxazole GFN2-xTB calculation.

## Source relationship

This is an independent thermochemistry-sensitivity analysis of Blackmon and
Closser, "Determination of ground-state structure and electronic excitations of
sulfamethoxazole using density functional theory" (2026),
https://doi.org/10.1016/j.comptc.2026.115931.

The source reports four aqueous ground-state minima, A-D, separated by
0.202 kJ/mol and assigns 298 K Boltzmann populations from electronic energies
only. It states that same-level frequency calculations confirmed all four
minima, but neither thermal corrections nor the frequencies are reported.

This experiment does not reproduce Q-Chem, PCM, the excited-state calculations,
or the development state-following implementation. It asks whether an
independent low-cost thermochemistry model changes the population conclusion
when its correction is added to the source's electronic energies.

## Question, hypothesis, and falsifier

Question: Does the source's nearly uniform A-D population remain nearly uniform
after an independently calculated 298.15 K thermochemical correction?

Hypothesis: the near-uniform ensemble is robust. Under both registered
thermochemistry arms:

1. the maximum absolute conformer-population change from the source electronic
   baseline is less than 10.0 percentage points; and
2. the effective conformer count, `1 / sum(p_i^2)`, is at least 3.5.

The hypothesis is supported if both arms pass both gates, falsified if both arms
fail at least one gate, and inconclusive if the arms disagree.

The thresholds are operational definitions of a material population change,
not universal physical constants. They were selected before calculation because
the source baseline is approximately 25% per conformer.

## Frozen computational protocol

Inputs are the A-D Cartesian coordinates and electronic energies transcribed
from the source supplement. Each structure is neutral and closed-shell.

For each conformer and each thermochemistry arm:

1. optimize from the source geometry with GFN2-xTB 6.7.1, ALPB water, tight
   optimization, SCC accuracy 0.2, and one thread;
2. calculate the numerical Hessian on the optimized structure at 298.15 K;
3. retain the xTB electronic energy and thermochemical free-energy correction;
4. form the primary composite free energy as
   `source_DFT_electronic_energy + xTB_thermochemical_correction`; and
5. calculate normalized Boltzmann populations at 298.15 K.

Registered arms:

- `rrho`: rotor cutoff `sthr = 0 cm^-1`;
- `mrrho50`: rotor cutoff `sthr = 50 cm^-1`.

Fixed xTB thermostatistical settings are `imagthr = -20 cm^-1`, frequency scale
1.0, and 298.15 K. Both arms begin from the same source coordinates and are run
independently. The native all-xTB free energies and population ordering are
secondary method-sensitivity results and do not determine the primary verdict.

## Method-fidelity gate

The primary verdict is automatically inconclusive if any of these occur:

- a run fails or does not terminate normally;
- an optimized structure has a mode below -20 cm^-1;
- either arm fails to retain four distinguishable minima; or
- the two thermochemistry arms do not produce the same optimized geometry for a
  given starting conformer within 0.02 angstrom heavy-atom aligned RMSD.

For the distinct-minima check, every optimized A-D pair must have heavy-atom
aligned RMSD of at least 0.10 angstrom in both arms. Atom order is fixed by the
source article's numbering; the second sulfonyl oxygen in the rendered B and C
coordinate lists is moved ahead of the hydrogens to restore that common order,
without changing any coordinate. These thresholds are identity checks, not
accuracy claims.

## Primary and secondary outputs

Primary outputs, separately for `rrho` and `mrrho50`:

- thermochemical correction for A-D;
- composite relative free energy for A-D;
- composite 298.15 K population for A-D;
- maximum absolute population shift in percentage points;
- effective conformer count;
- pass/fail of each decision gate; and
- the supported/falsified/inconclusive verdict.

Secondary outputs:

- optimized coordinates and harmonic frequencies;
- number and value of modes below -20 cm^-1;
- heavy-atom RMSDs used by the identity gate;
- native GFN2-xTB relative electronic and free energies; and
- the sign-consistency audit of the source's relaxed-state energy table.

No outcome will be used to infer an excited-state pathway, pH effect, explicit
solvent effect, experimental conformer abundance, or Q-Chem error.

## Reproducibility and stopping

The four conformers run serially. `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, and xTB `--parallel` are all fixed to 1. Heavy work must
not start while another quantum-chemistry process is active on the machine.

The run stops after the two registered arms. No threshold, method, conformer,
temperature, or rotor cutoff will be added after inspecting results. A failed
fidelity gate is reported as inconclusive rather than repaired by changing the
protocol.
