# The described SIREN convention's momentum recovery region, width vs beta

Question pulled from `notes/questions.md` (next step of the momentum-control
note, `/posts/2026-07-19-the-momentum-control.html`). Protocol frozen in
`PREREGISTRATION.md` on 2026-08-11 before the canonical run.

## Question and boundary

- Post type: research
- Question: as heavy-ball momentum beta varies over {0, 0.3, 0.6, 0.9, 0.99},
  how wide is the set of learning rates at which the described Sitzmann
  convention reaches the official convention's error floor on K1?
- Research falsifier: the width does not vary monotonically with beta, or the
  described convention reaches the floor at no tested rate for some beta > 0.5.
- What this experiment can establish: on K1 with this network, seeds, and
  optimizer, the width of the floor-hitting learning-rate set as a function of
  beta, and the described convention's divergence-boundary shift against the
  1+beta prediction.
- What it cannot establish: other K-cases, architectures, or optimizers; the
  authors' own code (unreleased); that a zero-width set is empty rather than
  narrower than the grid.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible
- Archived-evidence or rerun constraints: none

## Run

One command creates the canonical result artifacts (`results/stage1.json`,
`results/stage2.json`); stage 2's grid is derived from stage 1 by the frozen
rule in `PREREGISTRATION.md`. About 25 minutes on 8 workers.

```sh
cd research/momentum-recovery-region
python3 src/run_sweep.py
```

`make_figure.py` renders the post's figure from the canonical results; it
needs matplotlib (any recent version) and is not part of the result pipeline.

## Generate publication metrics

```sh
node research/momentum-recovery-region/generate-metrics.mjs
node research/momentum-recovery-region/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

## Data and publication

No external data. The model, task, and training loop are vendored from
`downloads/siren-convention-momentum.py` (this repository, own prior work) as
recorded in `sources.json`. `PUBLIC_FILES.txt` is the reviewed allowlist of
reader-facing files; nothing else in this directory is routed to the site.
