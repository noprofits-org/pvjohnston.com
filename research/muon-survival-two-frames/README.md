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

Current status: revised prospective setup implemented; production has not run
and reproducibility is not yet established. The immutable protocol is
`PREREGISTRATION-v1.md`.

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
environment, schemas, implementation, tests, and fixtures. `inputs.json`
contains the frozen scientific parameters and digests. No runtime parameter
overrides for seed, draw count, momentum, grid, threshold, or tolerances exist.

## Canonical execution

Do not execute this command until an independent `setup_review` (or
`amended_setup_review`) approves the exact committed setup into `execute`:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

The runner first verifies the current workflow authorization and rejects
environment, setup, or namespace drift, then exclusively creates
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
analyst supplies that event ID and writes the deterministic canonical result:

```sh
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-001 --run-review-event <approved-event-id>
```

The result can then be exactly regenerated and checked, followed by the single
1200 by 630 PNG and metrics projection:

```sh
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/analyze.py \
  --run-id run-001 --run-review-event <approved-event-id> --check
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/render_figure.py
research/muon-survival-two-frames/.venv/bin/python \
  research/muon-survival-two-frames/src/render_figure.py --check
node research/muon-survival-two-frames/generate-metrics.mjs
node research/muon-survival-two-frames/generate-metrics.mjs --check
```

Each writer refuses to overwrite an existing output; its check mode regenerates
the bytes in memory and requires an exact match. These production commands have
not been executed during setup.

## Sources and publication

`sources.json` records the two PDG URLs, access date, byte counts, hashes,
rights boundary, and acquisition instructions. `constants.json` transcribes
only the reviewed central values; neither PDF is committed or needed at
runtime. `PUBLIC_FILES.prospective.txt` is deliberately not a live routing
manifest. Editorial review must create the final `PUBLIC_FILES.txt` only after
all listed artifacts exist and have passed publication review. Every committed
file remains public even when it is not served by the site.
