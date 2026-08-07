# Preregistration: H2+ force-weight response

Status: frozen before any force-weight sweep output was generated.

## Question and contribution

Rana et al. introduced a molecular-potential fitting strategy that subtracts
the exact nuclear-repulsion energy, fits the remaining electronic energy, and
restores the exact term afterward. A prior experiment in this repository
compared energy-only training with one energy-plus-force loss at force weight
lambda = 1. On a minimal-basis analytic H2+ curve, adding force labels moved
the first tested parity cutoff inward from 3.0 to 2.0 bohr, opposite to the
registered prediction.

This experiment asks: **is that inward shift a monotonic response to the force
loss weight, or does the crossover flatten or move outward again at high
weight?**

- Post type: research.
- Contribution type: quantification.
- Contribution: a matched force-loss-weight dose-response and 0.25-bohr
  bracket of the bond-distance crossover for exact nuclear-repulsion
  subtraction on H2+, which is not in Rana et al. or the lambda = 1 precursor.
- Relationship to the source: an independent extension. No source program,
  code, or data are used. The analytic H2+ model and neural-network experiment
  are implemented in this repository.

## Hypothesis, falsifier, and verdict rule

Let C(lambda) be the smallest tested lower bond-distance cutoff R_min for which
the median paired ratio

    RMSE(direct total-energy fit) / RMSE(Coulomb-subtracted fit)

is at most one. A smaller C means that the direct fit reaches parity earlier as
the repulsive wall is removed.

The hypothesis is that increasing positive force weight moves C monotonically
inward, and that at least one weight above lambda = 1 moves it farther inward
than the lambda = 1 result. Operationally, the hypothesis is supported only if

1. C(0.01), C(0.1), C(1), C(10), and C(100) are nonincreasing in that order;
   and
2. either C(10) or C(100) is strictly smaller than C(1).

The hypothesis is falsified if either condition fails. A flat response above
lambda = 1 therefore falsifies the continuing-dose-response prediction, as
does any outward reversal. A missing crossing through 3.5 bohr is ordered as
greater than 3.5 bohr for this rule, not discarded.

The verdict is inconclusive instead if a method-fidelity gate below fails. All
three outcomes will be reported.

## Frozen system and data

The reference is the same closed-form, minimal-basis LCAO-MO H2+ ground-state
curve used by the precursor:

- Slater exponent zeta = 1;
- 401 geometrically spaced distances from 0.15 to 20.0 bohr;
- total potential V(R) = E_el(R) + 1/R;
- analytic dV/dR and dE_el/dR;
- conversion 1 hartree = 219474.6313632 cm^-1.

This deliberately small one-electron model is not a quantitative ab initio H2+
benchmark. It isolates the numerical consequence of moving an exact 1/R term
inside or outside an otherwise matched fit.

## Frozen model and training protocol

Two schemes are compared:

- Scheme A fits total V(R) and dV/dR directly.
- Scheme B fits E_el(R) and dE_el/dR, then restores exact 1/R and -1/R^2
  contributions before the total-energy prediction is scored.

For every fold and scheme, distance, energy, and slope targets are standardized
from the training partition exactly as in the precursor. The loss is

    L = MSE(standardized energy) + lambda * MSE(standardized slope).

The force weights are frozen at

    lambda in {0, 0.01, 0.1, 1, 10, 100}.

Lambda = 0 is the energy-only baseline. The positive panel spans four decades
and includes the previously tested lambda = 1 exactly.

The lower-distance cutoffs are frozen at

    R_min in {0.15, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50,
              2.75, 3.00, 3.25, 3.50} bohr.

The isolated 0.15-bohr point retains the near-wall control. The 0.25-bohr grid
from 1.0 through 3.5 brackets the two precursor crossovers and permits an
outward reversal beyond 3.0 bohr to be observed.

Every fit uses the precursor's architecture and optimization:

- one hidden layer with 15 tanh units and a linear readout;
- float64 throughout;
- Xavier-uniform weights and zero biases;
- full-batch Adam (beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8);
- 20,000 steps with a cosine learning-rate schedule from 1e-3 to 1e-5;
- retain the checkpoint with the lowest training objective, including the
  parameters after the final update;
- five fixed stratified folds from permutation seed 70220;
- five initialization seeds 11, 29, 47, 71, and 101;
- bit-identical initial parameters for Schemes A and B within each seed;
- pooled out-of-fold total-energy RMSE in cm^-1 for every seed.

The six weights may run in parallel processes, but each weight retains the same
25-network batch shape used by the precursor. BLAS/OpenMP thread counts are
fixed at one per process, and the registered production command uses two worker
processes. Process scheduling cannot mix parameters or reductions between
weights.

## Primary and secondary outputs

Primary outputs are, for each lambda:

1. the median of the five paired A/B out-of-fold RMSE ratios at every cutoff;
2. C(lambda), including the adjacent tested interval that brackets parity; and
3. the two frozen hypothesis conditions and resulting verdict.

If adjacent tested ratios bracket one, a log-ratio linear interpolation is
reported as a secondary descriptive estimate only. It does not enter the
verdict because linearity between cutoffs is not established.

Secondary outputs are the per-seed ratios, median Scheme A and Scheme B RMSEs,
the near-wall ratio at 0.15 bohr as a function of lambda, whether a ratio rises
back above one after its first crossing, and wall-clock runtime.

## Method-fidelity gates

The scientific verdict is inconclusive if any of these gates fails:

1. the analytic H2+ integral, derivative, dissociation-limit, bound-minimum,
   and repulsive-wall self-tests;
2. finite-difference agreement for the unbatched analytic training gradients;
3. agreement between batched and unbatched objectives and gradients;
4. exact equality of all regenerated lambda = 0 and lambda = 1 per-seed RMSEs
   at the overlapping cutoffs 0.15, 1.00, 1.50, 2.00, and 3.00 bohr with the
   committed precursor results, under its pinned CPython and NumPy versions;
5. completeness and finiteness of every registered result; or
6. deterministic re-derivation of the full analysis from the canonical result
   artifact.

The overlap gate tests implementation continuity; it does not treat the old
outcomes as new evidence.

## Scope, stopping, and publication

No architecture, seed, fold, distance, lambda, optimizer, step count, decision
threshold, or gate will be changed after output is viewed. There is no adaptive
extension. If a crossing lies outside the registered grid, it is reported as
bounded rather than followed with more cutoffs. If the sweep exceeds three
wall-clock hours, the current lambda finishes, the run stops cleanly, and the
result is reported incomplete and therefore inconclusive rather than resumed
with a reduced panel.

The experiment can establish the force-weight response for this fixed analytic
curve, network, standardization, optimizer, folds, and seeds. It cannot
establish that the same response holds for larger networks, other force/energy
normalizations, ab initio curves, many-atom potentials, or molecular dynamics.
