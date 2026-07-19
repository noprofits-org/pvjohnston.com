# Pulse-independent trajectory stress test

This bundle reproduces the experiment accompanying “When pulse-independent
trajectories lose nuclear accuracy.” It contains the exact quantum benchmark,
the independent TSH-PFMi/RP-AXE implementation, every raw JSON result, the
compact joined analysis, and the publication figures.

## Environment

- arm64 macOS 26.5.2
- CPython 3.13.12
- NumPy 2.4.4

The scripts otherwise use only the Python standard library. All model
parameters are in atomic units; reported times are in femtoseconds.

## Files

- `pulse-independent-ci.py`: exact split-operator, FP, and RP-AXE simulations
- `pulse-independent-ci-analyse.py`: joins results and generates SVG figures
- `pulse_ci_baseline.json`: published-model and exact-grid convergence gate
- `pulse_ci_convergence.json`: trajectory time-step gate
- `pulse_ci_sweep.json`: 36 final trajectory replicates
- `pulse_ci_exact_regimes.json`: exact quantum references for nine regimes
- `pulse_ci_exact_spot_checks.json`: post hoc $512^2$ checks at two displaced regimes
- `pulse_ci_analysis.json`: compact metrics and verdict
- `2026-07-18-pulse-independent-*.svg`: publication figures

## Rerun

From the extracted bundle directory:

```sh
python3 pulse-independent-ci.py baseline --progress --output pulse_ci_baseline.json
python3 pulse-independent-ci.py convergence --progress --output pulse_ci_convergence.json
python3 pulse-independent-ci.py sweep --workers 4 --progress --output pulse_ci_sweep.json
python3 pulse-independent-ci.py exact-regimes --progress --output pulse_ci_exact_regimes.json
python3 pulse-independent-ci.py exact-spot-checks \
  --reference pulse_ci_exact_regimes.json \
  --output pulse_ci_exact_spot_checks.json \
  --progress
python3 pulse-independent-ci-analyse.py \
  --baseline pulse_ci_baseline.json \
  --convergence pulse_ci_convergence.json \
  --sweep pulse_ci_sweep.json \
  --exact pulse_ci_exact_regimes.json \
  --exact-spot-checks pulse_ci_exact_spot_checks.json \
  --output pulse_ci_analysis.json \
  --image-dir .
```

The sweep command resumes a partial output file and skips already completed
seed/regime pairs. On the recorded machine, the 36 trajectory replicates used
about 80 aggregate CPU-minutes and the nine exact regime references about two
minutes. Worker count changes wall time, not the declared seeds.

## Scope

This is an independent implementation from published equations. It does not
contain or call the authors’ modified SHARC code, glycine trajectories, or
electronic-structure data. The exact BMA Figure 6 comparison is digitized from
vector artwork at integer femtoseconds and is intentionally treated as a
figure-level validation, not a substitute for tabulated source data.
