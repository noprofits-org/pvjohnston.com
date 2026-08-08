# Periodic compute cost

Why do chemically related and neighboring atoms take different amounts of
computation when they receive the same finite-basis electronic-structure probe?
This experiment supports an Understanding post with a fixed 14-atom panel.

## Question and boundary

- Post type: understanding.
- Question: why can related or neighboring atoms have different computational
  costs under the same protocol?
- Demonstration: compare the represented electron/basis size with the measured
  solver path, focusing on the Kr/Rb effective-core-potential boundary and the
  Cr/Mn/Fe/Zn PBE sequence.
- What this can establish: calculation wall time, represented size, and
  convergence behavior for the committed jobs on the recorded laptop.
- What this cannot establish: intrinsic or hardware-independent prices for
  elements, asymptotic method scaling, term-resolved atomic ground states, or
  why any particular SCF attempt failed.
- Traceability: the post values resolve from generated `metrics.json`; the raw
  attempts and deterministic summary are committed.
- Highest reproduction level: analysis-reproducible. `analyze.py --check`
  regenerates the summary and figure from the JSONL under the pinned plotting
  dependency. The full protocol is rerunnable, but subsecond timings are
  machine- and load-dependent rather than byte-identical scientific outputs.
- External inputs: none. `sources.json` records that boundary; literature stays
  in the shared bibliography.

`design.md` is the frozen protocol, and `PROMPT.md` is the completed production
handoff. The production JSONL has 70 unique fixed attempts and SHA-256
`01bc2b04195bd24aa1629e825abb8e8b09b6bda6918fdc19db6c081eb7b65579`.

## Local setup

The phase-one calculation environment is stored in the ignored `.venv` and
pinned in `requirements.lock.txt`. Activate it only if desired; the run commands
call its interpreter directly.

## Check the job matrix

```sh
research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --dry-run --phase all
```

## Run

The completed production session ran `survey`, `correlation`, and `deep`
separately. Every phase appends to
`research/periodic-compute-cost/results/runs.jsonl` and skips completed job keys
on restart. `PROMPT.md` contains the journal and close-out sequence.

No external dataset is used. Inputs are the element table and protocol embedded
in the committed runner.

## Analyze and draw Figure 1

Install the analysis-only dependency into a disposable or existing virtual
environment, then generate or check both derived artifacts:

```sh
python3 -m pip install -r research/periodic-compute-cost/requirements-analysis.txt
python3 research/periodic-compute-cost/analyze.py
python3 research/periodic-compute-cost/analyze.py --check
```

The script validates the complete job matrix and the committed canonical run's
observed nonconvergence rows before writing `results/summary.json` and the
1200 x 630 post figure. Successful survey timings are the median of two fixed
repeats. MP2 and CCSD(T) timings are single attempts. The two PBE failures
remain censored at the 80-cycle boundary; they are not converted into completed
timings. A fresh rerun with different scientific outcomes requires review and
a new canonical artifact rather than silently replacing the publication source.

## Generate publication metrics

```sh
node research/periodic-compute-cost/generate-metrics.mjs
node research/periodic-compute-cost/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`metrics.json` is a typed publication projection, not a replacement for the
richer summary or raw rows. `PUBLIC_FILES.txt` is the reviewed reader-facing
allowlist; it deliberately omits the completed session prompt and the ignored
virtual environment.
