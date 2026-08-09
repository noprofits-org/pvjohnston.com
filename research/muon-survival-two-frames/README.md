# One muon, two frames

This directory owns a reviewed, decay-only Understanding demonstration. It
asks how detector-frame time dilation and muon-frame length contraction give
the same survival probability for the stipulated momentum and path. Both are
coordinate descriptions of one proper-time interval, not two causal effects.

The model holds momentum and speed fixed and includes only exponential decay.
It does not model atmospheric production, momentum or height distributions,
energy loss, air, scattering, zenith angle, showers, detector response,
capture, sea-level flux, or a historical experiment. The Monte Carlo is an
implementation check of the assumed decay law, not evidence for relativity.

## Outcome

The canonical run `run-001` executed once on 2026-08-09 under workflow graph
v1 and was admitted on review; the analysis passed every registered check. The
trial then parked at `amendment_review`: the graph had no lawful edge for a
presentation-only correction to panel B of the registered figure
(`AMENDED-PROTOCOL-v2.md` and `WORKFLOW_RETROSPECTIVE.md` record why). The
repository retired the workflow graph shortly afterward, and this experiment
was completed and published under the successor pipeline:

- `workflow.jsonl` and `workflow/` are the frozen trial ledger and receipts.
- `graph/` preserves the retired engine, its state graph, its protocol
  document, and the trial-era hardened metrics generator, as the specimen the
  published note explains. The engine resolves paths against the repository
  layout it was built for, so replay it from a checkout of the retirement
  commit (`567fa4e`).
- `generate-metrics.mjs` is the current plain generator; it derives the
  physics metrics from `results/summary.json` and the ledger metrics from
  `workflow.jsonl`, and runs in CI with `--check`.
- `src/render_figure_v2.mjs` renders the corrected panel-B presentation the
  parked amendment specified, reading every printed value from the unchanged
  canonical summary. Figure 1's v1 PNG is byte-preserved in Git history.

Traceability: traceable and analysis-reproducible from committed outputs with
stock Node.js. Re-executing the run itself requires rebuilding the pinned
Python environment below.

The immutable protocol is `PREREGISTRATION-v1.md`. The sections below are the
graph-era operating contract, preserved as provenance for how `run-001` and
its analysis were actually produced; the workflow authorizations they refer
to no longer gate anything.

## Environment and setup-only verification

The approved Linux x86-64 environment is CPython 3.12.3, NumPy 2.5.1,
Matplotlib 3.11.1, and Node.js 24.18.0. Reconstruct the ignored `.venv` as
documented in `environment.md`; package installation must use
`requirements.lock.txt` with `--require-hashes`.

Before production, these commands are safe because they perform manifest and
environment checks plus only seed-0, at-most-16-draw toy work:

```sh
research/muon-survival-two-frames/.venv/bin/python -m unittest discover \
  -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/verify_setup.py
```

`setup-manifest.json` hash-binds the reviewed protocol, constants, sources,
environment, schemas, implementation, tests, fixtures, workflow graph, and
read-only workflow verifier. `inputs.json`
contains the frozen scientific parameters and digests. No runtime parameter
overrides for seed, draw count, momentum, grid, threshold, or tolerances exist.

## Canonical execution

Do not execute this command until an independent `setup_review` (or
`amended_setup_review`) approves the exact committed setup into `execute`:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

The runner first invokes the hash-bound repository workflow verifier for a
complete replay of experiment identity, graph version and digest, sequence,
roles, transitions, submission/review linkage, evidence snapshots, and the
current authorization. It rejects graph, environment, setup, or namespace
drift, then exclusively creates
`runs/run-001/`. It makes the registered PCG64 exponential draw in one call
and writes only the unsorted float64 proper-lifetime sample plus integrity
metadata. It does not reconstruct survival, calculate the focal example,
plot, generate metrics, or print scientific values.

A complete namespace contains exactly:

- `proper_lifetimes_s.npy`;
- `stdout.log` and `stderr.log`;
- `run-manifest.json`;
- `checksums.sha256`; and
- `COMPLETE.json`, written last.

`stdout.log` and `stderr.log` are the runner process streams captured from
before the draw through sealing; a post-claim exception is captured in the
incomplete namespace. The checksum file covers the sample, logs, and run
manifest. It excludes itself; `COMPLETE.json` binds the checksum file and
manifest and is itself bound by the later run-review receipt. The read-only
integrity command is:

```sh
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/validate_run.py --run-id run-001
```

Any pre-existing run directory is rejected before writing. There is no
same-run resume. An interrupted namespace lacks a valid completion marker and
is preserved for quarantine. Every entry under `runs/` makes setup's
`production_absent` check fail. The only prospectively registered retry is
`run-002`: it is accepted only when the current graph event is a
`run_review --registered-retry--> execute`, `run-001` is preserved and
incomplete, and the same reviewed bytes, seed, draw count, and runner are used.
Every other run ID is rejected. No scientific-check retry and no analysis
rerun are authorized.

## Analysis handoff

`src/reconstruct.py` is the tested numerical analysis contract. It contains
visibly separate detector-frame and muon-frame functions; neither consumes the
other's derived kinematics or arrays. It also provides the explicitly labelled
same-speed/no-lifetime-dilation counterfactual, inclusive nested survivor
counts, and every registered pass/fail branch. Synthetic fixtures exercise the
result, figure, and metrics contracts without touching canonical paths.

After a `run_review --approve--> analyze` event admits the sealed sample, the
analyst supplies that immutable historical event ID and writes the deterministic
canonical result. The run ID and event ID must come from that same approval:
use the `run-001` pair below when the admitted normal run is `run-001`, or the
`run-002` pair only when the prospectively registered retry succeeded and its
approval names `run-002`. The implementation rejects a cross-pair substitution.
The approval remains valid for byte checking after later valid events such as
submission to `analysis_review`; admission never depends on the approval
remaining the ledger's final line.

The independent run-review approval artifact set must contain exactly one
column-zero marker using this literal syntax (with the applicable ID):

```text
- **Admitted run:** `run-001`
```

For a registered retry, replace only the value with `run-002`. A missing,
duplicated, conflicting, malformed, or unregistered marker is rejected.
Incidental prose may discuss either or both registered IDs but does not admit
one; only the sole exact marker binds the immutable event to the command pair.

```sh
# Admitted normal run-001: write, then exact check.
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-001 --run-review-event <approved-event-id>
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-001 --run-review-event <approved-event-id> --check

# Admitted registered-retry run-002: write, then exact check.
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-002 --run-review-event <approved-event-id>
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-002 --run-review-event <approved-event-id> --check
```

After the applicable result pair succeeds, generate and check the single 1200
by 630 PNG and metrics projection:

```sh
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/render_figure.py
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/render_figure.py --check
node research/muon-survival-two-frames/generate-metrics.mjs
node research/muon-survival-two-frames/generate-metrics.mjs --check
```

Each writer refuses to overwrite an existing output; its check mode regenerates
the bytes in memory and requires an exact match. Run and result JSON are checked
against their bound schemas plus strict cross-field invariants. Manifest,
provenance, hash, bundle, and admission flags are derived from those validations
rather than asserted constants. The metrics writer and check mode consume the
exact canonical result bytes returned by the pinned Python validator after full
schema, cross-field, digest-provenance, and integrity-detail validation. These
production commands have not been executed during setup.

Result, PNG, and metrics publication uses the same restart contract. A writer
creates a unique hidden, target-scoped temporary file in the final directory,
flushes and fsyncs it, hard-links it to an immutable `ready` stage, and then
hard-links that complete stage to the final path. The final hard link is atomic
and refuses an existing file, link, or directory; equal existing bytes are not
treated as a successful rewrite. Check mode is read-only.

Rerunning the same writer recovers an interruption before final installation:
an exact `ready` stage is installed, while an interrupted temporary stage or a
mismatched `ready` stage is moved by no-overwrite hard link into a target-scoped
quarantine file. Matching stage names are handled only when they are regular,
non-symlink files owned by the current user and no larger than 10 MB; unsafe
entries fail closed untouched. Recovery considers at most 16 stages per target,
after which manual inspection is required. A successful writer removes its own
temporary and `ready` names, but preserves quarantine evidence. Two writers may
race, yet only one final hard link can succeed and readers see either no final
entry or one complete payload. This derived-output recovery is separate from,
and does not alter, the frozen raw-run namespace and completion-marker rules.

## Sources and publication

`sources.json` records the two PDG URLs, access date, byte counts, hashes,
rights boundary, and acquisition instructions. `constants.json` transcribes
only the reviewed central values; neither PDF is committed or needed at
runtime. `PUBLIC_FILES.txt` is the live routing manifest for the reader-facing
bundle, including the ledger, receipts, and the `graph/` specimen; the
`workflow/evidence/` snapshots are excluded as byte duplicates of the receipts
they mirror, and the sealed raw sample and run logs stay unrouted. Every
committed file remains public even when it is not served by the site.
