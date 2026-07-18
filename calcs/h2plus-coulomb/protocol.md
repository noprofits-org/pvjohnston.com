# H2+ Coulomb-subtraction experiment

Protocol fixed before the ANN fits were run.

## Question

Over what bond-distance range does fitting the electronic energy and restoring
the exact nuclear repulsion improve a neural fit to the total H2+ potential,
compared with fitting the total potential directly?

The experiment maps the useful range of a physically motivated residual. It is
an independent test inspired by Rana et al. (2025), not an attempt to reproduce
their MATLAB tables or adjudicate a claim about their implementation.

## Hypothesis and falsifier

The benefit should be concentrated at short distance, where `1/R` has its
largest curvature. The paired median ratio `RMSE(A) / RMSE(B)` should move toward
1 as the shortest distances are removed.

The hypothesis is falsified if that ratio remains at least 2, with no downward
trend, after every point below `R = 1.5 a0` is removed. That result is still
useful: it would show that residual fitting helps beyond the near-singular wall.

## Electronic-structure data

- H2+ ground electronic state; charge `+1`, multiplicity `2`.
- Psi4 SCF with an unrestricted reference. With one electron, Hartree--Fock is
  exact within the selected finite basis.
- `aug-cc-pV5Z`, density-fitted SCF, float64, two CPU threads.
- 401 geometries, evenly spaced in `log R`, from `0.15` to `20 a0`.
- `V_nn` is checked against `1/R` at every geometry.
- `E_el = V_total - V_nn`; Scheme B does not receive a second quantum calculation.

The `0.15 a0` lower limit is the first pretested distance above Psi4's
too-close-geometry guard for this calculation. No claim is made below it.

## Primary neural fit

- Nested cutoffs: `0.15, 0.25, 0.40, 0.70, 1.00, 1.50, 2.00, 3.00 a0`.
- Five stratified folds assigned once on the complete ordered grid, then
  preserved across cutoffs. Every eligible point receives one out-of-fold
  prediction.
- Five fixed initialization seeds. Scheme A and Scheme B receive bit-identical
  initial weights for every fold and seed.
- Identical positive-R geometries for both targets; neither gets a united-atom
  point or manual short-range enrichment.
- Input: raw `R`, standardized with training-fold moments only.
- Targets: each target standardized with its own training-fold moments and
  unscaled before scoring. Scheme B then restores the exact `1/R` term.
- Network: one hidden layer, 15 `tanh` units, linear output, Xavier-uniform
  weights, zero biases, float64.
- Optimizer: full-batch Adam for 20,000 fixed steps; cosine learning-rate decay
  from `1e-3` to `1e-5`; no dropout or weight decay.
- The checkpoint with the lowest training MSE is retained. Test folds never
  select a checkpoint, seed, hyperparameter, or architecture.

## Outcomes

The primary metric is out-of-fold total-energy RMSE in `cm^-1`, pooled across
all eligible distances for each initialization seed. Secondary metrics are MAE,
maximum absolute error, shortest-distance-quintile RMSE, and an RMSE weighted by
linear `R` rather than by the log-spaced sample count.

The primary contrast is the paired ratio `RMSE(A) / RMSE(B)`: values above 1
favor the Coulomb-subtracted residual, 1 is parity, and values below 1 favor the
direct fit. All five seeds are reported; none is selected.

## Predeclared controls

After the primary result:

1. use `log R` rather than raw `R` as the standardized input;
2. use a common target standard deviation rather than separately scaling the
   two target ranges;
3. repeat with 10 and 20 hidden units;
4. repeat with a constant number of points at every cutoff if the shrinking
   nested data set could explain the trend;
5. compare selected scan points at `aug-cc-pVTZ`, `aug-cc-pVQZ`, and
   `aug-cc-pV5Z` to bound basis-set sensitivity.

If an optimization failure affects more than 5% of fits, the entire paired set
will be rerun at a lower learning rate and longer fixed budget. One target will
never be rescued alone.
