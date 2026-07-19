# Model-system reliability in off-tonic recapitulation analysis

This directory contains a reproducible six-dossier pilot associated with Yoel
Greenberg's 2025 paper, "The Off-Tonic Recapitulation in Context: a Study in
Fuzziness" (doi:10.1111/musa.12251).

The primary experiment does **not** test Greenberg's continuum claim. It tests
whether three frozen CLI model systems can apply one music-analytic rubric
repeatably, whether their ratings agree across provider families, and how often
they recover the identities of canonical works from identity-withheld symbolic
evidence.

The six 0--4 cues are an investigator-authored operational synthesis of
mechanisms discussed around the focal cases. Greenberg did not propose or
validate this rubric, and agreement on it is not evidence of music-theoretical
correctness.

The frozen matrix fixes OpenAI `gpt-5.6-sol` and Anthropic
`claude-fable-5` as frontier systems and OpenAI `gpt-5.5` as an active
prior-generation system. This is a partial 2x2 panel across two provider
families, not three independent provider families: pooled three-system results
give OpenAI two positions and are descriptive rather than causal. The analysis
therefore reports named within-provider and cross-provider system pairs.

## Status

Dataset 1.0.0, the protocol, the three-system matrix, and its 108-call schedule
were frozen at 2026-07-19T17:54:14Z before any real-case output call. All three
adapters passed the separately defined fictional schema preflight under working
OpenAI and Anthropic authentication; no real dossier was used and no response
body was retained. The 41-file collection lock was created and verified at
2026-07-19T17:56:35.630Z. Collection subsequently completed all 108 scheduled
calls from 18:15:05 through 19:54:52 UTC with no retry, timeout, or command
failure. The frozen primary analyzer accepted 103 responses; all 54
identification responses and 49 of 54 analysis responses passed the frozen
output contract.
The automatic-expansion decision was `false`.

The preregistration and statistical-analysis documents retain their frozen,
pre-collection wording by design. [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
records the completed state, artifact hashes, result taxonomy, verification
commands, and distribution boundaries. Gemini was dropped before any Gemini
model request because the available authentication path required a Google
Cloud project.

## Files

- `PREREGISTRATION.md`: pilot hypotheses, metrics, gates, and interpretation.
- `STATISTICAL_ANALYSIS.md`: exact reliability estimands and bootstrap.
- `RUN_MATRIX.md`: exact models, CLI versions, settings, and scheduled calls.
- `prompts/analysis.md`: frozen ordinal-rubric task.
- `prompts/identification.md`: separate repertoire-identification probe.
- `data/manifest.json`: allowed case files and hashes.
- `data/cases/`: six identity-withheld symbolic dossiers.
- `data/provenance/`: operator-only identity and score-source records.
- `collection-lock.json`: frozen hashes of every collection-critical input.
- `scripts/run-model.sh`: isolated runner bound to frozen model adapters.
- `scripts/validate-output.mjs`: task-specific output validation.
- `scripts/analyze-results.mjs`: preregistered reliability summary.
- `scripts/restore-immutable-modes.mjs`: restores the read-only flags required
  by integrity checks after ZIP extraction; it changes no file bytes.
- `results/1.0.0/summary.json`: immutable primary result.
- `results/1.0.0/pairwise-bootstrap-supplement.json`: preregistered
  pair-bootstrap reporting addendum.
- `results/1.0.0/case-status-descriptives.json`: post hoc status descriptives.
- `results/1.0.0/validator-contract-sensitivity.json`: post hoc, prompt-aligned
  validator sensitivity; it does not replace the primary result.
- `REPRODUCIBILITY.md`: completed-run verification and artifact guide.
- `BUNDLE-NOTICE.md`: source exclusions and third-party data notice.
- `outputs/`: versioned, hash-verified Markdown response bundles.

## Isolation boundary

Every invocation runs in a fresh temporary directory. The model receives one
prompt and one case dossier embedded in standard input. It does not receive the
repository, the provenance table, Greenberg's paper, other cases, earlier
responses, or another analyst's labels. The textual prohibition remains in the
prompt because some agent CLIs may technically be able to escape their working
directory; such behavior must be reported as a protocol violation.

The model-facing dossier is a deterministic compact-JSON serialization of the
hash-verified readable case file. This removes non-evidentiary indentation from
the repeated input; each run sidecar hashes the exact rendered prompt.

## Collection interface

After the protocol is frozen, run the collection only through the sequential
schedule orchestrator:

```sh
node research/off-tonic-recapitulation/scripts/collect-schedule.mjs
```

The orchestrator verifies the collection lock and schedule order, writes an
immutable attempt claim for the next slot, and then invokes `run-model.sh`
internally. Do not invoke a scheduled `--run` directly: it would lack the
required claim, so the runner refuses before contacting a model and the
analyzer independently rejects any unclaimed bundle. The lower-
level runner is retained for isolated `--diagnostic NN` troubleshooting, which
is kept outside the scheduled namespace and never replaces a scheduled slot.

Both tasks use runs `01`, `02`, and `03` for every system/case pair, each in a
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
The matrix also freezes a per-call timeout. A timeout kills the adapter process
group, finalizes the slot as `command_failed`, and stops collection without a
retry.

## Freeze sequence

1. Finalize the preregistration, extraction protocol, and score sources.
2. Generate all six symbolic dossiers and inspect them in a separate reverse
   pass.
3. Assign arbitrary opaque case IDs that encode no identity or corpus role, and
   freeze the identity/source records.
4. Validate dossiers, calculate hashes, and freeze `data/manifest.json`.
5. Freeze exact models and hashed adapters in `run-matrix.json`, then generate
   its explicit 108-call schedule.
6. Create and verify `collection-lock.json`.
7. Commit or tag the complete frozen protocol before the first real-case
   outcome call.
8. Run all 54 analysis and 54 identification invocations through
   `scripts/collect-schedule.mjs`.
9. Analyze only after the scheduled matrix is complete and identification has
   been adjudicated against the frozen key.
