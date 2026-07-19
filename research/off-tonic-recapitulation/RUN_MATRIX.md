# Pilot run matrix

Status: **development; must be frozen before collection**.

The pilot requires three independently developed model families. Complete every
field below and in the normative `run-matrix.json` before freezing collection.

| Label | Provider | Callable model ID/version | CLI and version | Decoding settings | Analysis runs | Identification runs |
| --- | --- | --- | --- | --- | ---: | ---: |
| model-a | TBD | TBD | TBD | TBD | 18 | 18 |
| model-b | TBD | TBD | TBD | TBD | 18 | 18 |
| model-c | TBD | TBD | TBD | TBD | 18 | 18 |

Both tasks use three fresh contexts for each of six cases. Operators must not
reuse a chat, session, cache transcript, or model-generated working file between
calls.

Each model entry in `run-matrix.json` must name one executable adapter and pin
its SHA-256 hash. The adapter contains the exact model identifier and all
tool/session/decoding flags. The runner chooses this adapter from the model
label; it does not accept an operator-supplied command.

After case IDs and adapters are final, set `schedule_seed`, generate the explicit
108-call schedule with `scripts/generate-schedule.mjs --write`, and verify that
every `task x model x case x run` slot occurs exactly once. The JSON is the
source of truth; this table is a human-readable summary.

Record the planned collection window here and actual start/end timestamps in
the run sidecars, along with CLI authentication context, region if exposed, and
any provider-side model alias that could change during
collection. Prefer dated or immutable model identifiers.
