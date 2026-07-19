# Pilot model-system run matrix

Status: **frozen for dataset 1.0.0 at 2026-07-19T17:54:14Z**. The
108-call schedule was generated with seed `20260719`. Real-case collection is
authorized only from the pre-outcome Git commit containing the verified
collection lock and after the planned collection window opens. The 41-file lock
was created and verified at 2026-07-19T17:56:35.630Z.

The pilot uses three fixed noninteractive CLI model systems across two provider
families. Each experimental system comprises model weights plus the provider's
CLI system prompt, serving stack, safety layer, and any unexposed sampling
defaults. Results therefore support claims about these frozen systems, not
about bare API models in isolation or three independent provider families.

| Label | Generation role | Provider and callable model ID | CLI and version | Frozen inference configuration | Analysis runs | Identification runs |
| --- | --- | --- | --- | --- | ---: | ---: |
| `openai-frontier` | frontier | OpenAI `gpt-5.6-sol` | Codex CLI 0.144.6 | high reasoning; low verbosity; tool-bearing features disabled where exposed; read-only sandbox backstop; provider sampling defaults | 18 | 18 |
| `anthropic-frontier` | frontier | Anthropic `claude-fable-5` | Claude Code 2.1.215 | high effort; adaptive thinking; safe mode; tools/MCP/session persistence/fallback disabled; provider sampling defaults | 18 | 18 |
| `openai-prior-generation` | prior-generation (active) | OpenAI `gpt-5.5` | Codex CLI 0.144.6 | high reasoning; low verbosity; tool-bearing features disabled where exposed; read-only sandbox backstop; provider sampling defaults | 18 | 18 |

Generation-role labels were checked on 2026-07-19 against the official
[OpenAI latest-model guide](https://developers.openai.com/api/docs/guides/latest-model)
and [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview).
“Prior-generation” is a descriptive position in this panel, not an assertion
that OpenAI assigns `gpt-5.5` a legacy or deprecated lifecycle state.

This is a partial 2x2 `provider x generation-role` panel. OpenAI supplies a
frontier and an active prior-generation system; Anthropic supplies a frontier
system, while the Anthropic prior-generation cell is empty. Generation role is
descriptive metadata, not a treatment. The `gpt-5.6-sol`--`gpt-5.5`
within-provider contrast and both OpenAI--`claude-fable-5` cross-provider
contrasts will be reported by named system pair, but none estimates a causal
prior-generation-versus-frontier or provider effect. A pooled
three-system summary also gives OpenAI two of three system positions and must be
labeled provider-unbalanced.

All three adapters passed no-outcome diagnostics under the intended
subscription authentication, and the callable model IDs were echoed or
otherwise verified by their CLIs. The matrix and collection window are frozen.
No provider fallback or `auto`/`latest` routing is allowed.

Pre-collection adapter status on 2026-07-19:

- OpenAI first passed an isolated exact-token transport check whose CLI stderr
  echoed `model: gpt-5.6-sol`. It then passed both schema-aware prompt shapes
  against the fictional `CASE-SYN0` dossier. The retained, hash-bound receipt
  contains only timing, byte-count, validation, and protocol metadata; prompt,
  response, and stderr bodies were discarded. An earlier failed configuration
  attempt exposed one unsupported strict-config field, which was removed before
  these successful checks and before any outcome-bearing call.
- Anthropic authentication succeeded, and `claude-fable-5` passed both
  schema-aware prompt shapes against fictional `CASE-SYN0` with tools, MCP,
  session persistence, and fallback disabled.
- OpenAI `gpt-5.5` passed both schema-aware prompt shapes against fictional
  `CASE-SYN0` through its separately hash-pinned adapter.

A final claims audit removed prompt wording that could imply the probe observes
memorization or training-data provenance. Because that changed both prompt
hashes, all three fictional preflights were rerun; the matrix selects only the
later receipts. Freeze validation recomputes each receipt's rendered-prompt
hash and byte count from the exact synthetic dossier rather than trusting the
recorded fields. Earlier metadata-only receipts remain as superseded diagnostic
history and are not selected by the matrix.

All successful preflights used only the fictional dossier. Their retained
receipts contain validation and transport metadata, not prompt, response, or
stderr bodies; no real dossier was used and no experiment outcome was viewed.
Gemini was dropped from the development matrix before any Gemini model request
because its available authentication path required an explicit Google Cloud
project. It is not an experimental system; the OpenAI prior-generation system
was selected before outcome collection, which had not begun.

Both tasks use three fresh contexts for each of six cases. Fresh contexts are
same-input test-retest repetitions of one stochastic system, not independent
raters. Operators must not reuse a chat, session, cache transcript, or
model-generated working file between calls.

Model agents from the OpenAI and Anthropic families participated in protocol
construction or read-only audit. The scheduled adapters do not expose those
sessions, local files, or tools to the fresh outcome contexts. Nevertheless,
every tested provider family overlaps protocol development. This must be
reported, and no result may be described as external model validation.

Each system entry in `run-matrix.json` must name one executable adapter and pin
its SHA-256 hash. The adapter contains the exact model identifier and all
tool/session/decoding flags. The runner chooses this adapter from the model
label; it does not accept an operator-supplied command.

The explicit 108-call schedule was generated with
`scripts/generate-schedule.mjs --write` after case IDs and adapters were final.
Every `task x model x case x run` slot occurs exactly once. The JSON is the
source of truth; this table is a human-readable summary.

`run-matrix.json` freezes `call_timeout_seconds` at 1200 seconds. The runner
executes each adapter in a separate process group. If that limit is reached, it
kills the group, records exit status 124 in an immutable `command_failed`
bundle, and the schedule collector stops. The consumed slot is not retried;
any later attempt requires a new dataset version.

Run the frozen sequence without opening response bodies. Mechanical validation
status may be monitored, but musical scores, identifications, and prose remain
unread until all 108 scheduled slots have terminated. Stop on an external
service outage rather than changing a model, adapter, or prompt mid-collection.

The planned collection window is 2026-07-19 11:15:00 PDT through 2026-07-20
23:59:59 PDT (`2026-07-19T18:15:00Z` through `2026-07-21T06:59:59Z`), recorded
with timezone `America/Los_Angeles` in `run-matrix.json`. Actual start/end
timestamps belong in the run sidecars, along with CLI authentication class
(never account identity), region if exposed, and any provider-side routing
metadata. The selected IDs are explicit model IDs, not `auto` or `latest`
aliases. Provider serving infrastructure may still change and is part of the
tested system.
