# Run-and-monitor handoff — periodic-compute-cost

This session runs the fixed representative panel in `design.md`. It does not
change the protocol, analyze the results, make figures, or draft the post.

## Before running

1. Read the repository `AGENTS.md` and this directory's `design.md` in full.
2. Work only in the existing `post/periodic-compute-cost` worktree. Confirm it
   is clean with `git worktree list`, `git branch -vv`, and `git status`. If the
   worktree is missing but the branch exists, attach it with
   `git worktree add <worktree-path> post/periodic-compute-cost` rather than
   trying to create the branch again.
3. Recover the research journal before doing work:

   ```sh
   node scripts/research-log.mjs list
   node scripts/research-log.mjs show --session 20260808T021400Z-compute-cost-of-the-periodic-table-e-f247
   node scripts/research-log.mjs verify --session 20260808T021400Z-compute-cost-of-the-periodic-table-e-f247
   node scripts/research-log.mjs resume --session 20260808T021400Z-compute-cost-of-the-periodic-table-e-f247
   ```

4. Use the existing `.venv` and verify its pinned packages against
   `requirements.lock.txt`. Confirm AC power, a quiet machine, and adequate
   free memory; do not overlap this run with another CPU-heavy experiment.

## Validate the setup

From the worktree root:

```sh
research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --dry-run --phase all
```

The dry run's pending plus already-recorded counts must total exactly 70 unique
jobs, and its spin/ECP parity checks must pass. Run one noncanonical Be/UHF
smoke probe to a temporary location if the environment has changed; do not
append smoke output to `results/runs.jsonl`.

## Production run

Use the same output for all phases; the runner is append-only and resumable.
Run phases separately so each result can be inspected and journaled before the
next long command:

```sh
research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --phase survey

research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --phase correlation

research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --phase deep
```

After each phase, checkpoint exact counts grouped by `outcome` plus the phase
wall time. Then run the next phase. A failed atom is data; do not adjust its
guess, threshold, grid, timeout, memory setting, or method and rerun it. Stop
and report if total elapsed time approaches three hours or the host becomes
memory-constrained.

## Handoff

- Confirm the JSONL has one row for every planned job and no duplicate job keys.
- Record environment changes, if any, in `environment.md`.
- Commit the raw results and any strictly necessary runner correction on
  `post/periodic-compute-cost`. Do not create plots, metrics, or post prose.
- Close the journal with the exact result path and the next step: a separate
  review/write session audits the data before interpreting it.
- Complete the repository close-out checklist. Leave both this worktree and the
  primary checkout clean; do not touch another session's worktree.

## Guardrails

- All changes stay under `research/periodic-compute-cost/**`.
- Thread count is one; timeout is 180 s; PySCF's 3000 MB setting is advisory.
- Do not expand the element panel, add methods, add repeats, or rescue failed
  calculations without a new journaled design decision from the user.
