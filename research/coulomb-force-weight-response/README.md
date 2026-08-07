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
- Traceability: not yet established until the production run and metrics
  projection are committed.
- Highest reproduction level: not yet established.
- Archived-evidence or rerun constraints: none; the analytic curve and all code
  are committed, and the calculation needs only CPU NumPy.

The protocol and its pre-outcome amendment are frozen in
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

Create an isolated environment with the pinned requirements, then run the cheap
analytic, gradient, batch-consistency, and process-isolation checks:

```sh
python3 -m venv /tmp/coulomb-force-weight-venv
/tmp/coulomb-force-weight-venv/bin/pip install -r research/coulomb-force-weight-response/requirements.txt
/tmp/coulomb-force-weight-venv/bin/python research/coulomb-force-weight-response/run_experiment.py --check
```

The frozen production command uses two scalar-lambda workers and writes
`results.json` only after the primary panel and convergence audit finish:

```sh
/usr/bin/time -v /tmp/coulomb-force-weight-venv/bin/python \
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

## Files and publication

- `PREREGISTRATION.md` freezes the question, panel, controls, gates, and verdict
  rule before the first outcome.
- `run_experiment.py` is the deterministic production wrapper.
- `verify_analysis.py` independently re-derives the analysis from raw RMSEs
  using the Python standard library.
- `results.json` is the canonical raw and derived result artifact.
- `generate-metrics.mjs` and `metrics.json` own the typed publication
  projection.
- `make_figure.py` generates the reader-facing figure from `results.json`.
- `sources.json`, `environment.md`, and `requirements.txt` record provenance.
- `PUBLIC_FILES.txt` is the reviewed reader-facing allowlist.

The bundle contains no credentials, private data, third-party datasets, model
weights, or paid-service output.
