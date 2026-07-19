# LLM reliability in off-tonic recapitulation analysis

This directory contains a reproducible six-dossier pilot associated with Yoel
Greenberg's 2025 paper, "The Off-Tonic Recapitulation in Context: a Study in
Fuzziness" (doi:10.1111/musa.12251).

The primary experiment does **not** test Greenberg's continuum claim. It tests
whether several model families can apply one music-analytic rubric repeatably,
whether their ratings agree across families, and whether supposedly blinded
canonical repertoire can be identified from anonymized symbolic evidence.

## Status

The protocol is under development. The dataset is not frozen, so the runner
refuses all model calls. No outcome-producing model run is authorized yet.

## Files

- `PREREGISTRATION.md`: pilot hypotheses, metrics, gates, and interpretation.
- `STATISTICAL_ANALYSIS.md`: exact reliability estimands and bootstrap.
- `RUN_MATRIX.md`: exact models, CLI versions, settings, and scheduled calls.
- `prompts/analysis.md`: frozen ordinal-rubric task.
- `prompts/identification.md`: separate repertoire-identification probe.
- `data/manifest.json`: allowed case files, randomized order, and hashes.
- `data/cases/`: six blinded symbolic dossiers.
- `data/provenance/`: operator-only identity and score-source records.
- `collection-lock.json`: frozen hashes of every collection-critical input.
- `scripts/run-model.sh`: isolated runner bound to frozen model adapters.
- `scripts/validate-output.mjs`: task-specific output validation.
- `scripts/analyze-results.mjs`: preregistered reliability summary.
- `outputs/`: versioned, hash-verified Markdown response bundles.

## Isolation boundary

Every invocation runs in a fresh temporary directory. The model receives one
prompt and one case dossier embedded in standard input. It does not receive the
repository, the provenance table, Greenberg's paper, other cases, earlier
responses, or another analyst's labels. The textual prohibition remains in the
prompt because some agent CLIs may technically be able to escape their working
directory; such behavior must be reported as a protocol violation.

## Command-line interface

The runner resolves the only permitted model adapter from `run-matrix.json`:

```sh
research/off-tonic-recapitulation/scripts/run-model.sh \
  --task analysis \
  --case CASE-AB12 \
  --model model-label \
  --run 01
```

Both tasks use runs `01`, `02`, and `03` for every model/case pair, each in a
fresh context. Repeated identification distinguishes stable recognition from a
lucky or hallucinated match.

The output path includes dataset version, scheduled/diagnostic namespace, task,
model label, evidence condition, case ID, and run. A `.run.json` sidecar and
completion marker bind the byte-for-byte Markdown stdout to the model adapter,
dataset, prompt, dossier, timestamps, and validation result.

The runner never overwrites an output. Command failures and malformed responses
are retained with `.invalid.md`. Scheduled slots are never retried in place;
troubleshooting calls use `--diagnostic NN` and are excluded from analysis. A
repeated scheduled collection receives a new dataset version.

## Freeze sequence

1. Finalize the preregistration, extraction protocol, and score sources.
2. Generate and independently inspect all six symbolic dossiers.
3. Randomize opaque case IDs and freeze the identity/source records.
4. Validate dossiers, calculate hashes, and freeze `data/manifest.json`.
5. Freeze exact models and hashed adapters in `run-matrix.json`, then generate
   its explicit 108-call schedule.
6. Create and verify `collection-lock.json`.
7. Commit or tag the complete frozen protocol before the first model call.
8. Run all 54 analysis and 54 identification invocations.
9. Analyze only after the scheduled matrix is complete and identification has
   been adjudicated against the frozen key.
