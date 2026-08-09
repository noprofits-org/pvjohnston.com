# Repository agent instructions

`main` is the live site: `.github/workflows/deploy.yml` builds and publishes on
every push to it. Several sessions may run against this repository at once and
cannot see each other. The pipeline is deliberately small:

**branch → write → cheap checks → PR → CI → merge → auto-deploy.**

Safety lives in the automated checks and in branch hygiene, not in process
documents. If a rule here can't be enforced by a script or by git, it had
better be earning its keep.

## Writing a post

1. Read `notes/blog-authoring.md` — the editorial contract: post forms,
   structure, citations, figures, captions, and traceable metrics. It governs
   what a post *is*, not how many approvals it needs.
2. Never author on `main` or in the primary checkout. Make a worktree:

   ```sh
   primary=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
   trees=$(dirname "$primary")/pvjohnston-worktrees

   git -C "$primary" fetch origin
   git -C "$primary" worktree add -b post/<slug> "$trees/<slug>" origin/main
   ```

   Check `git worktree list` and `git branch -vv` first — any worktree or
   branch you did not create is presumed live and is not yours to touch.
3. A `post/<slug>` branch touches its own files: `posts/<its-slug>.md`,
   `images/<its-slug>-*.png`, `research/<its-experiment-slug>/**`, appends to
   `bib/bibliography.bib`, and **its own entry in `notes/questions.md`** —
   adding or updating the question it answers in the same PR is normal, not a
   separate change. Unrelated shared infrastructure (`css/`, `templates/`,
   `lib/`, `app/`, `scripts/`, `.github/`, `index.html`, the standalone
   `*.markdown` pages) gets its own `feature/` or `fix/` branch.
4. Run the cheap checks in the worktree — they need no build and take seconds:
   `node scripts/verify-bib.mjs`, `node scripts/verify-metrics.mjs`, grep every
   `[@key]` against `bib/bibliography.bib`, confirm the bare `## References`,
   confirm internal post links end in `.html`.
5. Open a PR into `main`. CI runs the full build and verification on every PR —
   opening the PR *is* a legitimate way to run the expensive checks. Merge
   deploys.
6. Leave the session clean: worktrees you created are committed or removed, no
   stashes, no branches you can't account for, primary checkout on `main`.

`notes/worktrees.md` has the concurrency details and the close-out checklist.

## Experiments

Generated results are traceable, not vibes. Each post's experiment lives in one
directory — copy `research/_TEMPLATE/` to `research/<experiment-slug>/` — with
its code, environment record, canonical results, `metrics.json` plus its
generator, and a `PUBLIC_FILES.txt` allowlist. The post binds it with
`experiment: <slug>` and cites generated numbers as `[name]{.metric}`, which
the build resolves from `metrics.json` and fails on when missing. That is the
whole traceability contract; `notes/blog-authoring.md` §7 has the details.

This repository is public: committing a file is publishing it, and
`PUBLIC_FILES.txt` additionally routes what it lists onto the live site.
Never commit credentials, private data, or secrets.

For an experiment whose outcome you could be tempted to tune, freeze a short
`PREREGISTRATION.md` (hypothesis, falsifier, protocol) before the canonical
run. It is one file you write for yourself, not a review gate.

## The shared bibliography

`bib/bibliography.bib` is append-only and written by concurrent sessions. It is
marked `merge=union` in `.gitattributes`, so appended entries from two branches
both survive a merge — safe only while nobody reformats, reorders, or rewrites
existing entries. Before appending, grep for the author **and** the year;
`node scripts/verify-bib.mjs` blocks duplicate keys but cannot detect one
source added twice under two different keys.

After any local merge that touched the bib, check the append joint before
pushing — a local union merge has dropped a closing brace there before, and
verify-bib does not parse deeply enough to catch it:

```sh
awk '{n += gsub(/\{/,"") - gsub(/\}/,"")} END {exit n != 0}' bib/bibliography.bib
```
