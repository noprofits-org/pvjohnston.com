# Environment

The experiment is pure NumPy and has no native or paid dependencies. It is
deterministic: every training is seeded, and rerunning `run_experiment.py`
regenerates `results.json` bit-for-bit on the recorded interpreter.

- Operating system and version: Linux 6.18.5 (Anthropic cloud sandbox)
- Architecture: x86_64
- Interpreter/compiler and version: CPython 3.11.15
- Dependency manager and version: pip; see `requirements.txt`
- Hardware assumptions: any CPU; no GPU, no threads required
- Locale/timezone: UTC
- Random seeds and nondeterministic operations: fold assignment seed 70220;
  initialisation seeds 11, 29, 47, 71, 101. No nondeterministic operations
  (no dropout, no GPU atomics, single-threaded NumPy math).
- Required environment variables (names only; never commit values or secrets):
  none
- External services, models, and dated version identifiers: none. The H2+
  reference curve is generated analytically by `h2plus_model.py`; no
  electronic-structure package is used.

## Reproduce

```
pip install -r research/coulomb-force-training/requirements.txt
python3 research/coulomb-force-training/run_experiment.py          # writes results.json (~40 min, CPU)
node research/coulomb-force-training/generate-metrics.mjs           # writes metrics.json
node scripts/verify-metrics.mjs                                     # verifies fingerprints + projection
```

`run_experiment.py --check` runs the fast gates only (analytic-model self-test,
finite-difference gradient check, batched/unbatched gradient consistency) and
does not train.
