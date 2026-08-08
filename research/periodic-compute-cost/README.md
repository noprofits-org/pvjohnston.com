# Periodic compute cost

This experiment supports an Understanding post about why related or neighboring
atoms can have different computational costs. It uses a fixed 14-atom panel;
see `design.md` for the scientific boundary and `PROMPT.md` for the production
run handoff.

## Local setup

The phase-one environment is stored in `.venv` and pinned in
`requirements.lock.txt`. Activate it only if desired; all documented commands
call its interpreter directly.

## Check the job matrix

```sh
research/periodic-compute-cost/.venv/bin/python \
  research/periodic-compute-cost/sweep.py --dry-run --phase all
```

## Run

The production session runs `survey`, `correlation`, and `deep` separately.
Every phase appends to `research/periodic-compute-cost/results/runs.jsonl` and
skips completed job keys on restart. `PROMPT.md` contains the required journal
and close-out sequence.

No external dataset is used. Inputs are the element table and protocol embedded
in the committed runner. The eventual publication session must create the
metrics projection and a reviewed `PUBLIC_FILES.txt`; phase one deliberately
does neither.
