# Collection completion and incidental unblinding record

Recorded: 2026-07-19T19:57:05Z

## Collection close

The sequential collector began its first scheduled call at
2026-07-19T18:15:05Z and ended its last call at 2026-07-19T19:54:52Z, inside
the frozen collection window. All 108 scheduled slots terminated in order.
Mechanical verification found 103 schema-valid responses, five schema-invalid
responses, no command failures, no empty or partial slots, and no retries. The
five invalid responses were all in the Anthropic frontier analysis arm; all 54
identification responses were schema-valid. No response or stderr body was
deliberately opened while collection was running.

## Raw snapshot sequence

After the collector terminated, the operator:

1. verified the 41-file collection lock and all 108 completed bundles;
2. confirmed that the scheduled namespace contained 540 files--one immutable
   attempt claim and four finalized bundle files per slot;
3. generated `data/provenance/collection-output-sha256.txt`, containing the
   SHA-256 hash of every one of those 540 files; and
4. recorded SHA-256
   `7aa40e37c9948f03ef7689320e07ac42067ea9ed957bdec5fcc7ce97f560f229`
   for the checksum manifest itself.

The raw files and checksum manifest were then committed without modification in
commit `16304af52c0b1cf6b50cbdbec2dff0c81e25a05f` and pushed to the remote
experiment branch. A post-commit checksum verification and collection-lock
verification both passed.

## Incidental partial unblinding before the raw commit

Between steps 4 and the Git commit, the operator ran
`git diff --cached --check` to look for staged whitespace errors. Because raw
model output is intentionally preserved byte for byte, the command emitted
warnings that included the text of lines ending in Markdown hard-break spaces
from some response and stderr files. The captured display consisted primarily
of run-metadata declarations such as analyst, provider, case, settings, and
access-boundary lines. No score table, identification judgment, or aggregate
result was deliberately reviewed or used to make a decision at that point.

This happened only after all 108 slots had terminated, so it did not violate
the frozen full-matrix response embargo or influence collection. It did,
however, violate the narrower operator intention to commit the raw snapshot
before any response-body text appeared on screen. The deviation cannot affect
the raw bytes because the complete 540-file checksum manifest had already been
generated, and the committed files verify against it exactly. Nothing was
reformatted to remove the trailing spaces.

Public reporting must preserve this sequence. It may say that all raw bytes
were hash-bound before incidental exposure and committed before substantive
scoring or analysis; it must not say that the raw Git commit preceded every
display of response text.
