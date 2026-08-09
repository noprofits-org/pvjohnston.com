# Experiment title

Copy this directory to `research/<experiment-slug>/` before running a new
computer experiment. The slug must begin with a lowercase letter and contain
only lowercase letters, digits, and single hyphens.

For an experiment whose outcome you could be tempted to tune, rename and
complete `PREREGISTRATION.example.md` before the canonical run.

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
