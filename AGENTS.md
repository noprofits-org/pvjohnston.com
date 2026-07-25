# Repository agent instructions

`main` is the live site: `.github/workflows/deploy.yml` publishes on every push
to it. Several sessions run against this repository at once and cannot see each
other. Nothing is authored on `main`, and no session stops without leaving it
clean.

## When you are asked for a new blog post

Do these in order. None of them is optional, and the first two happen before
any drafting.

1. **Read `notes/blog-authoring.md`.** It is the single source of truth for
   post form, structure, citations, figures, captions, and experiment
   artifacts. Declare `post-type: research` or `post-type: understanding`
   before drafting; a Research note additionally needs its question to have
   come off `notes/questions.md` and a `contribution:` sentence written up
   front. If you cannot write that sentence, there is no post.
2. **Make a worktree** — never author in the primary checkout, and never on
   `main`. This resolves the primary checkout from wherever you are, rather
   than assuming a clone location:

   ```sh
   primary=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
   trees=$(dirname "$primary")/pvjohnston-worktrees

   git -C "$primary" fetch origin
   git -C "$primary" worktree add -b post/<slug> "$trees/<slug>" origin/main
   ```

3. **Check who else is working** before touching anything shared:
   `git worktree list` and `git branch -vv`. Any worktree or branch you did not
   create is presumed live.
4. **Stay inside the post's own files.** A `post/<slug>` branch may create or
   modify only `posts/<its-slug>.md`, `images/<its-slug>-*.png`,
   `research/<its-experiment-slug>/**`, and appended entries in
   `bib/bibliography.bib`. Everything else — `index.html`, `notes/questions.md`,
   `css/`, `templates/`, `lib/`, `app/`, `scripts/`, `.github/`, the standalone
   `*.markdown` pages — is shared, and a change to any of it gets its own
   `feature/` or `fix/` branch and its own PR.
5. **Run the cheap checks in the worktree**, not the full build:
   `node scripts/verify-bib.mjs`, `node scripts/verify-metrics.mjs`, plus the
   build-free self-check in §8 of the authoring guide — grep every `[@key]`
   against `bib/bibliography.bib`, confirm the bare `## References`, confirm
   internal post links end in `.html`.
6. **Open a PR into `main`.** The PR runs the same build the deploy uses. The
   full §8 sequence (`stack test && stack exec site rebuild && node
   scripts/verify-metrics.mjs && node scripts/verify-site.mjs`) runs there or in
   the primary checkout — not in every worktree, which would rebuild the site
   library each time.
7. **Close out** per the checklist below.

`notes/worktrees.md` has the full protocol and the reasoning behind it.

## Closing out a session

Not finished until every line passes:

1. Close the research journal if one was opened.
2. `git status --porcelain` is empty in every worktree **you created**
   (`git worktree list`). Another session's worktree may be dirty; report it,
   do not touch it.
3. `git stash list` is empty.
4. No orphan branches: each is merged and deleted, or pushed with an open PR,
   or recorded in the journal with a reason for being parked.
5. Finished worktrees removed (`git worktree remove …`, `git worktree prune`)
   and merged branches deleted.
6. The primary checkout is on `main`, pulled, and clean.

## The shared bibliography

`bib/bibliography.bib` is append-only and written by concurrent sessions. It is
marked `merge=union` in `.gitattributes`, so appended entries from two branches
both survive a merge — which is safe only while nobody reformats, reorders, or
rewrites existing entries. Before appending, grep for the author **and** the
year; `node scripts/verify-bib.mjs` blocks duplicate keys but cannot detect one
source added twice under two different keys.

## Deep research durability

When a task involves literature review, experimental question selection,
multi-step exploratory computation, or a preregistered research run, use the
crash-resistant journal in `scripts/research-log.mjs`.

1. Run `start` before the first search or exploratory command.
2. Record sources that change the viable question with `source`.
3. Record pivots and protocol choices with `decision`.
4. Run `checkpoint` immediately after an interpretable result and **before**
   starting the next command. Include exact numbers, the command or artifact
   path needed to reproduce them, and one explicit next step.
5. Checkpoint before delegating, compacting context, or changing a branch or
   worktree. Run `close` at handoff, abandonment, or completion.
6. On a resumed task, run `list`, `show`, and `verify` before repeating work.

The journal is stored in Git's shared common directory, not a worktree. Never
put secrets or credentials in it. See `notes/research-journal.md` for the
complete workflow.
