# Worktrees, branches, and closing out clean

How concurrent sessions work on this repository without clobbering each other,
and what every session owes `main` before it stops. `notes/blog-authoring.md`
§8 governs the build and deploy sequence; this note governs who may edit what,
from where, and how a session ends.

## Why this exists

`.github/workflows/deploy.yml` publishes the site on every push to `main`.
`main` is therefore the live site, not a scratch branch, and anything sitting
uncommitted on top of it is one careless `git commit -a` away from being
published.

Two or more sessions now routinely run against this repository at the same
time, and they cannot see each other's context. The observed failure modes are
concrete, not hypothetical:

- Work authored on one branch left uncommitted in the tree after a checkout to
  another branch, so a homepage edit ended up sitting on top of the deploy
  branch belonging to nothing.
- A finished branch left behind unpushed and unmerged, invisible to every later
  session that did not think to run `git branch`.
- `bib/bibliography.bib` accumulating the same source twice under one key,
  because two authors each appended without finding the other's entry. Seven
  keys are currently duplicated; `scripts/verify-bib.mjs` now blocks new ones.

The rules below are ordered so the cheap mechanical ones come first. Where a
rule can be enforced by a script or by git itself, it is, because §4 of the
authoring guide has said "one writer at a time" for months and the duplicates
still happened.

## 1. One worktree per line of work

Worktrees live **outside** the checkout, as siblings of it:

```sh
# Resolves the primary checkout from any worktree, and does not assume a
# particular clone location — agents run in containers where $HOME differs.
primary=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
trees=$(dirname "$primary")/pvjohnston-worktrees

git -C "$primary" fetch origin
git -C "$primary" worktree add -b post/<slug> "$trees/<slug>" origin/main
```

- **Outside, always.** A worktree nested inside the repository would be crawled
  by Hakyll as site content and would show up in `git status`. A sibling
  `pvjohnston-worktrees/` directory is the convention; anywhere outside the
  checkout works.
- **Branch from `origin/main`, not local `main`.** A new branch must not
  inherit whatever state the primary checkout happens to be in.
- **Branch names** follow what the merged history already uses: `post/<slug>`
  for a note, `feature/<slug>` for site or tooling work, `fix/<slug>` for a
  repair.
- The primary checkout — the one holding the shared `.git`, resolved above as
  `$primary` — **stays on `main` and stays clean.** It is the integration and verification tree; nothing is authored
  there. Git enforces the other half of this for free — a branch checked out in
  one worktree cannot be checked out in another.

## 2. A branch owns its files

The clobbering to prevent is not two sessions editing one line. It is two
sessions each making a reasonable edit to a shared file for unrelated reasons.

A **`post/<slug>` branch may create or modify only**:

| Path | Notes |
| --- | --- |
| `posts/<its-slug>.md` | the note itself |
| `images/<its-slug>-*.png` | its figures (§5) |
| `research/<its-experiment-slug>/**` | its experiment directory (§7) |
| `bib/bibliography.bib` | append-only, and see §3 below |
| `notes/questions.md` | only the entry for its own question — add or update it in the same PR |

Everything else is shared: `index.html`, `css/`, `templates/`, `lib/`, `app/`,
`scripts/`, `.github/`, and the standalone `*.markdown` pages. A post branch
does not touch them. If writing a note
reveals that a shared file needs to change, that change gets **its own
`feature/` or `fix/` branch and its own PR**, which may of course run in its
own worktree.

This is the rule that would have caught the homepage-card edit riding along on
a research-journal branch: the edit was fine, the vehicle was not.

Two live branches must never both be editing the same shared file. Check before
starting (§5).

## 3. The bibliography

`bib/bibliography.bib` is the one shared file a post branch must write to, so
it gets a mechanism rather than an instruction.

- **`.gitattributes` marks it `merge=union`.** Both sides of a merge keep their
  appended entries instead of raising a conflict. This is correct precisely
  because §4 of the authoring guide makes the file append-only; it would be
  wrong for any file whose existing lines get rewritten. Do not reformat,
  reorder, or rewrite existing entries — union merge cannot save you from that,
  and it will happily keep both versions of whatever you mangled.
- **`node scripts/verify-bib.mjs` blocks duplicate keys.** Union merge's one
  failure mode is two sessions appending the same source under the same key;
  this check catches it before merge. It runs in CI and in the §8 pre-merge
  sequence, needs no build, and takes about a second — run it yourself after
  appending.
- The seven already-duplicated keys are grandfathered in that script with their
  current counts. Adding another copy of one of them fails the check just like
  a new duplicate would.
- §4 rule 3 still applies and is still the actual defence: grep the file for
  the author *and* the year before appending.

## 4. Worktrees author; the primary tree verifies

Each worktree gets its own `.stack-work`, so running the full Hakyll build in
every post worktree means paying a site-library rebuild per note. Don't.

- **In the worktree:** draft, append bib entries, generate figures and
  experiment artifacts, and run the cheap checks — `node
  scripts/verify-bib.mjs`, `node scripts/verify-metrics.mjs`, and the
  build-free self-check in §8 (grep every `[@key]`, confirm the bare
  `## References`, confirm every internal post link ends in `.html` and not
  `.md`).
- **Before merge:** the full §8 checks run once, in the primary checkout or in
  CI on the pull request. The primary checkout uses `stack test && stack exec
  site rebuild && node scripts/verify-metrics.mjs && node
  scripts/verify-site.mjs`; CI uses `site build` on a clean checkout with no
  restored Hakyll store. A PR into `main` triggers the same pipeline the deploy
  uses, so opening the PR is a legitimate way to run it.

This is the §8 "author in a sandbox and cannot run the build" path promoted
from exception to normal practice. It is only safe because of the build-free
self-check: a missing bib entry renders as `[?]` without failing the build, so
skipping the local build never means skipping that grep.

## 5. Before you touch anything shared

Sessions cannot see each other, but git can. From any worktree:

```sh
git worktree list      # who holds which branch, and where
git branch -vv         # every local branch, and whether it is pushed
git status --short     # this tree only
```

Any worktree that exists is presumed live and owned by another session. Any
local branch you did not create is presumed live too, whatever its date.

## 6. Closing out — the session is not over until this passes

Run this before you stop, every time. It is the whole point of the note.

1. **Every worktree you own is clean.** `git worktree list`, then `git status
   --porcelain` in each tree you created — all empty. No "I'll pick this up
   tomorrow" files. Uncommitted work either becomes a commit on its own branch
   or is discarded deliberately. A worktree belonging to another live session
   will legitimately be dirty; §5 says it is not yours to commit or discard, so
   report it and leave it alone.
2. **No stashes.** `git stash list` is empty. A stash is invisible to the next
   session and belongs to nobody.
3. **No orphan branches.** Every branch is either merged and deleted, or pushed
   with an open PR, or — if it is genuinely parked — pushed with a sentence in
   its PR or commit message saying why it still exists. A local unpushed branch
   with no note is the failure this rule names.
4. **Finished worktrees removed.** `git worktree remove
   ../pvjohnston-worktrees/<slug>` then `git worktree prune`, and `git branch
   -d post/<slug>` once it is merged.
5. **The primary checkout is on `main`, pulled, and clean.**

```sh
# Close-out audit. Run from anywhere in the repository.
primary=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")

git worktree list          # inspect: your trees gone, foreign ones noted
git branch -vv             # inspect: every branch merged, pushed, or accounted for
git stash list             # must be empty
git -C "$primary" status --short   # must be empty
```

The last two must produce no output. The first two are read, not matched
against empty: `git branch -vv` always prints at least `main`, and a pushed
branch with an open PR or a branch parked with its reason in a PR or commit
message are both allowed states. What is not allowed is a branch you cannot
account for.
