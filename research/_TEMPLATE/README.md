# Experiment title

Copy this directory to `research/<experiment-slug>/` before running a new
computer experiment. The slug must begin with a lowercase letter and contain
only lowercase letters, digits, and single hyphens.

For a computationally heavy, role-separated, or multi-session experiment,
rename and complete `PREREGISTRATION.example.md`, start the research journal,
and initialize the tracked workflow before production work:

```sh
node scripts/research-workflow.mjs init \
  --experiment <experiment-slug> \
  --post-type research \
  --question "<question already ready on notes/questions.md>" \
  --shelf-entry "<notes/questions.md heading>" \
  --journal "<research journal session>" \
  --actor "<stable actor id>"
```

Understanding posts use `--post-type understanding` and omit
`--shelf-entry`. Run initialization and all later mutations from the exact
owning `post/<slug>` branch in its linked worktree. Immediately before each
`submit` or `review`, leave the open research journal on a fresh checkpoint
with an explicit next action; the ledger binds and consumes its event ID.
`workflow/HANDOFF.example.md` and
`workflow/REVIEW.example.md` are small receipt templates;
`workflow/AMENDMENT.example.md` covers a post-exposure protocol change and
`workflow/PULL_REQUEST_RECEIPT.example.md` covers PR/CI evidence. Copy them to versioned
names under `workflow/` instead of overwriting a packet that has already been
submitted. The CLI snapshots those packets under `workflow/evidence/` and
writes the append-only `workflow.jsonl`. It never runs the experiment.

The ledger, receipts, and evidence snapshots are tracked public files. They
contain only repository-relative paths or durable external identifiers plus
sizes and checksums—never local absolute checkout, home, scratch, cache, or
mounted-data paths. Large/raw artifacts and full logs do not belong in workflow
receipts. Actor IDs are self-asserted process labels: the CLI rejects an equal
submission/review string, but the coordinator must establish that the reviewer
is really a different session or person.

After any result exposure, use the `amend` edge through
`protocol_amendment -> amendment_review` for a scientific or setup change.
Approval continues through `amended_setup -> amended_setup_review`, never the
prospective `redesign` edge. `resume` continues only the same incomplete run;
`registered_retry` starts a fresh infrastructure attempt authorized before
execution; and `registered_rerun` starts a fresh analysis-plan rerun authorized
before exposure. After editorial approval, `ready_for_pr` collects PR/CI
evidence for the candidate content commit. `pr_review` creates an
attestation-only descendant, and a human must confirm that the cumulative delta
from the candidate contains only the PR/review receipts, their evidence
snapshots, and corresponding ledger events, then require green CI on the
resulting head. `ready_to_merge` is the successful terminal state and `parked`
is the other terminal. Before merge, run:

```sh
node scripts/research-workflow.mjs verify --experiment <experiment-slug>
```

CI uses `verify --all`, which validates only experiment directories that opted
in by containing `workflow.jsonl`.

Keep every active submitted receipt present and byte-identical. If `status`
reports interrupted workflow-ledger recovery, use
`node scripts/research-workflow.mjs repair --experiment <experiment-slug>`;
never edit the ledger or evidence snapshots by hand. Repair does not cure a
changed active receipt: restore it or take a reviewed backward route and submit
a new version. If a killed process left `workflow/.transition.lock`, inspect it
and use `repair --experiment <experiment-slug> --unlock-stale` only when its
same-host owner process is gone; never delete or replace a live lock by hand.
The lock records its owning post branch. If initialization died before
installing `workflow.jsonl`, the verified unlock runs before ledger loading and
then instructs you to retry `init`.

## Question and boundary

- Post type: research / understanding
- Question:
- Research falsifier (Research only):
- Demonstration mechanism or observation (Understanding only):
- What this experiment can establish:
- What it cannot establish:
- Traceability: not yet established / traceable
- Highest reproduction level: none / analysis-reproducible / end-to-end reproducible
- Archived-evidence or rerun constraints:
- Workflow state: not initialized / active / ready_to_merge / parked

## Run

Document one exact command that creates the canonical result artifacts. Keep
the native dependency lockfile for the chosen ecosystem in this directory; use
`environment.example.md` only when no lockfile can represent the environment.

```sh
# Replace with the real command.
```

## Generate publication metrics

Rename and implement `generate-metrics.example.mjs`, then generate and check
the committed projection:

```sh
node research/<experiment-slug>/generate-metrics.mjs
node research/<experiment-slug>/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

The post binds this directory with `experiment: <experiment-slug>` and cites a
value as `[metric_name]{.metric}`. The site build resolves the value from
`metrics.json` and fails on missing or invalid references.

## Data and publication

For external computational inputs, replace `sources.example.json` with a source
manifest containing durable locations, versions, access dates, checksums,
licenses, and acquisition steps. Literature citations remain in the shared
bibliography.
Rename `PUBLIC_FILES.example.txt` and list only files reviewed for reader-facing
publication. The site build reads this allowlist and routes exactly what it
lists, so a path added here is served on the live site at that path — review
each entry before adding it, and expect `scripts/verify-site.mjs` to fail if an
entry names something that is not a file. Never infer publication safety from
`.gitignore`: this repository is public, so every committed file is already
externally accessible, and secrets or private data must never be committed.

Document exclusions here, including the effect of rights, privacy, secrets,
size, paid APIs, unavailable hardware, or disappearing upstream data on the
reproducibility claim.
