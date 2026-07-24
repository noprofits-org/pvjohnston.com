# Repository agent instructions

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
