# Crash-resistant research journal

Deep research produces valuable state before it produces repository files:
sources already ruled out, candidate questions, environment pins, failed
controls, exact commands, intermediate numbers, and the reason for a pivot.
That state must not live only in an agent transcript.

`scripts/research-log.mjs` writes an append-only JSONL journal under the
repository's **Git common directory**:

```text
<git-common-dir>/research-journal/<session>.jsonl
```

Every worktree for this repository therefore sees the same journals. The logs
survive agent crashes, branch deletion, and worktree removal, while staying out
of commits and public history. Each record is appended with one write and
`fsync` before the command returns. A recovery read ignores an incomplete final
record but rejects corruption anywhere earlier in the file. The next append
removes only that incomplete tail and writes a `recovery` event before the new
record; `repair` can perform the same recovery explicitly.

The journal protects against a process or worktree failure. It is not an
off-machine backup; export important completed evidence into the tracked
research bundle before publication.

## Start and recover

Start before the first literature search or exploratory command:

```bash
node scripts/research-log.mjs start \
  --title "MACE-POLAR heterofragment dissociation" \
  --question "Do separated charged fragments approach the isolated-energy sum?"
```

The command prints the generated session ID. Pass it explicitly on subsequent
commands, or set `RESEARCH_SESSION_ID` in the shell running the work:

```bash
export RESEARCH_SESSION_ID="<printed-session-id>"
```

After a crash or context loss:

```bash
node scripts/research-log.mjs list
node scripts/research-log.mjs show --session "<session-id>"
node scripts/research-log.mjs verify --session "<session-id>"
node scripts/research-log.mjs repair --session "<session-id>" # optional; append also repairs
```

`list` is reconstructed from the append-only files; there is no mutable
"current session" pointer that can be lost or accidentally shared by concurrent
agents.

## What to record

Record a source as soon as it changes the viable question:

```bash
node scripts/research-log.mjs source \
  --session "$RESEARCH_SESSION_ID" \
  --source "https://doi.org/..." \
  --title "Paper title" \
  --finding "The proposed broad audit was already performed on 1,000 frames."
```

Record pivots separately from observations:

```bash
node scripts/research-log.mjs decision \
  --session "$RESEARCH_SESSION_ID" \
  --decision "Drop the broad label audit; test separated-fragment consistency." \
  --reason "The label audit is occupied, while this composition test is absent."
```

Checkpoint immediately after any expensive run, surprising result, fixed
control, or meaningful batch of source work:

```bash
node scripts/research-log.mjs checkpoint \
  --session "$RESEARCH_SESSION_ID" \
  --summary "Medium float64 result plateaus from 24 to 32 angstrom." \
  --result "D(24)=-0.175445 eV; D(32)=-0.176307 eV" \
  --command "python probe.py --model M --dtype float64" \
  --artifact "/absolute/or/repo-relative/path/to/output.jsonl" \
  --next "Confirm with the large checkpoint in float64."
```

Use `--stdin` instead of `--summary` or `--message` for multiline text. Do not
put credentials, tokens, private data, or huge raw outputs in the journal.
Store large outputs as artifacts and log their path plus checksum.

Close a completed or abandoned investigation:

```bash
node scripts/research-log.mjs close \
  --session "$RESEARCH_SESSION_ID" \
  --summary "Pilot complete; protocol frozen." \
  --next "Create the tracked preregistration and input panel."
```

Use `resume` before adding to a closed session.

## Checkpoint cadence

The durability rule is simple: **write the result before starting the next
step**. During deep research, a journal should receive a record:

1. before the first search or probe;
2. after each source that kills, narrows, or supports a direction;
3. at every pivot and protocol decision;
4. immediately after a command produces an interpretable result;
5. before delegation, context compaction, branch/worktree changes, or a long
   follow-up command; and
6. at handoff or completion, with one explicit next action.

This bounds a crash loss to the currently running step rather than the whole
session.
