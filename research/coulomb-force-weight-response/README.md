# H2+ force-weight response

This experiment tests whether the inward bond-distance crossover measured when
force labels were added to a Coulomb-subtracted H2+ neural-potential fit is a
monotonic response to the standardized force-loss weight.

## Question and boundary

- Post type: research.
- Question: is the inward Coulomb-subtraction crossover shift monotonic in the
  force-loss weight, or does it flatten or move outward at high weight?
- Research falsifier: the registered crossover sequence is flat above lambda =
  1, contains an outward step, or contains a reverse parity crossing.
- What this experiment can establish: the energy- and force-error response for
  one analytic H2+ curve, one 15-unit tanh network, six standardized-coordinate
  loss weights, fixed folds and seeds, and a 0.25-bohr crossover grid.
- What it cannot establish: the response for ab initio curves, different loss
  normalizations or optimizers, larger networks, many-atom potentials, or
  molecular dynamics.
- Traceability: preregistration, deterministic source, raw per-seed results,
  independently rebuilt analysis, typed publication metrics, and the figure
  source are committed together.
- Highest reproduction level: end-to-end reproducible on linux-x86_64 from the
  explicit Conda and Python package locks; analysis-reproducible with the Python
  standard library alone.
- Archived-evidence or rerun constraints: none; the analytic curve and all code
  are committed, and the calculation needs only CPU NumPy.

The protocol and its pre-outcome amendments are frozen in
`PREREGISTRATION.md`. The experiment is an independent extension of Rana et
al., *Artificial Neural Networks Fitting of Potential Energy Curves and
Surfaces: The 1/R Conundrum* (2025), and of the repository's lambda = 1
precursor. No program, code, or data from Rana et al. are used.

## Implementation lineage

`run_experiment.py` imports the validated trainer and analytic curve from
`research/coulomb-force-training/` without modifying them. Each scalar lambda
retains the predecessor's exact 25-row seed-by-fold batch. Separate spawned
processes parallelize weights without changing a network's operation order.
The wrapper adds held-out force scoring, the fine cutoff panel, exact comparison
to the complete committed lambda = 0/1 subgrid, and the registered 40,000-step
optimization-sensitivity audit.

## Preflight and run

Recreate the production Linux environment, then run the cheap analytic,
gradient, batch-consistency, and process-isolation checks:

```sh
conda create --prefix /tmp/coulomb-force-weight-env \
  --file research/coulomb-force-weight-response/environment-linux-64.lock
/tmp/coulomb-force-weight-env/bin/python -m pip install --no-deps \
  -r research/coulomb-force-weight-response/requirements-lock.txt
/tmp/coulomb-force-weight-env/bin/python \
  research/coulomb-force-weight-response/run_experiment.py --check
```

`requirements.txt` contains the smaller direct-dependency set for a compatible
pip/venv rerun when exact production-environment reconstruction is unnecessary.

The frozen production command uses two scalar-lambda workers and writes
`results.json` after the registered run ends, including an incomplete,
inconclusive artifact if the wall-clock ceiling stops the panel:

```sh
/usr/bin/time -v /tmp/coulomb-force-weight-env/bin/python \
  research/coulomb-force-weight-response/run_experiment.py --workers 2
```

Rebuild the analysis without NumPy or retraining:

```sh
python3 research/coulomb-force-weight-response/verify_analysis.py --check
```

## Generate publication metrics

After the production result exists:

```sh
node research/coulomb-force-weight-response/generate-metrics.mjs
node research/coulomb-force-weight-response/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

The accompanying post binds this directory with
`experiment: coulomb-force-weight-response`.

## Result

The 20,000-step primary first-parity cutoffs were 3.00, 1.50, 1.50, 1.75,
2.00, and 2.00 bohr at lambda = 0, 0.01, 0.1, 1, 10, and 100. That sequence was
not monotonically inward, and lambda = 100 crossed parity three times.

The registered 40,000-step audit changed the parity classification at three of
six endpoints: lambda = 0 at 2.75 bohr, lambda = 1 at 1.75 bohr, and lambda =
100 at 2.00 bohr. The optimization-sensitivity gate therefore failed, making
the frozen scientific verdict **inconclusive**. This precedence matters: the
fixed-budget primary pattern contradicts the monotonic hypothesis, but the
experiment did not establish a training-budget-stable crossover sequence.

The production and audit run completed in 4,244.81 seconds (70.7 minutes),
inside the registered three-hour ceiling. All 160 predecessor comparisons were
bit-exact, every registered result was finite and complete, and the independent
standard-library verifier accepted the canonical artifact.

## Files and publication

- `PREREGISTRATION.md` freezes the question, panel, controls, gates, and verdict
  rule before the first outcome.
- `run_experiment.py` is the deterministic production wrapper.
- `verify_analysis.py` independently re-derives the analysis from raw RMSEs
  using the Python standard library.
- `results.json` is the canonical raw and derived result artifact, including
  the registered optimization audit.
- `generate-metrics.mjs` and `metrics.json` own the typed publication
  projection.
- `make_figure.py` generates the reader-facing figure from `results.json`.
- `sources.json`, `environment.md`, and `requirements.txt` record provenance.
- `environment-linux-64.lock` and `requirements-lock.txt` reproduce the actual
  production package set.
- `PUBLIC_FILES.txt` is the reviewed reader-facing allowlist.

The bundle contains no credentials, private data, third-party datasets, model
weights, or paid-service output.
