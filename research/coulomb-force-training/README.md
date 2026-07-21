# coulomb-force-training

Does adding force (energy-gradient) labels move the bond-distance cutoff at
which subtracting the exact nuclear repulsion stops helping a small neural
network fit an H2+ potential?

This experiment owns the traceable metrics for the post
`posts/2026-07-21-does-force-training-move-the-coulomb-subtraction-crossover.md`.
It extends the energy-only experiment of
`posts/2026-07-18-where-coulomb-subtraction-helps.md`, which was prompted by
Rana et al., *J. Comput. Chem.* **46** (2025) e70220.

## Files

- `h2plus_model.py` — analytic minimal-basis LCAO H2+ curve V(R) and exact
  dV/dR, with self-tests (integral values, dissociation limit, minimum,
  derivative vs complex-step).
- `run_experiment.py` — the frozen sweep. Two schemes (A: fit total V;
  B: fit electronic energy and restore exact 1/R), two losses (energy-only,
  energy+force), eight distance cutoffs, five folds, five seeds. Writes
  `results.json`. Verifies analytic gradients against finite differences and
  the batched trainer against the unbatched one before running.
- `verify_analysis.py` — cheap `--check`: re-derives the median A/B ratios and
  crossover cutoffs from the committed RMSE table without retraining.
- `results.json` — canonical per-seed out-of-fold RMSE table and the derived
  per-cutoff medians and crossover cutoffs.
- `generate-metrics.mjs` — projects `metrics.json`; `--check` reruns
  `verify_analysis.py --check` and byte-compares.
- `sources.json`, `environment.md`, `requirements.txt`, `PUBLIC_FILES.txt`.

## Reproducibility

End-to-end reproducible: `run_experiment.py` is deterministic NumPy and
regenerates `results.json` on the recorded interpreter; `generate-metrics.mjs`
regenerates `metrics.json` from it. Analysis-reproducible without retraining
via `verify_analysis.py --check`.
