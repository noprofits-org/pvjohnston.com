# Environment

The experiment itself is pure NumPy and has no native or paid dependencies;
`make_figure.py`, which draws the post's figure from the committed
`results.json`, additionally needs Matplotlib. Both are pinned in
`requirements.txt`. The experiment is deterministic: every training is seeded,
and rerunning `run_experiment.py` regenerates `results.json` bit-for-bit.

That claim is now tested across interpreters rather than asserted for one. The
committed `results.json` was first produced under CPython 3.11.15. Re-running
the then-current code under CPython 3.12.3, with the same pinned NumPy,
reproduced its `derived` block bit-for-bit — so the checkpoint correction
recorded below is the only cause of the small numeric differences in this
version of the file, and the interpreter contributed none of them.

The Matplotlib pin records a version compatible with both interpreters and the
NumPy pin. Nothing in `results.json` or `metrics.json` depends on Matplotlib.

- Operating system and version: Linux 6.18.5 (Anthropic cloud sandbox) for the
  original run; Linux 7.0.0 (x86_64 workstation) for the current `results.json`
- Architecture: x86_64
- Interpreter/compiler and version: CPython 3.12.3 produced the current
  `results.json`; CPython 3.11.15 produced the original and reproduces the
  pre-correction values bit-for-bit
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
python3 research/coulomb-force-training/make_figure.py              # redraws the post figure (needs Matplotlib)
```

`run_experiment.py --check` runs the fast gates only (analytic-model self-test,
finite-difference gradient check, batched/unbatched gradient consistency) and
does not train.
