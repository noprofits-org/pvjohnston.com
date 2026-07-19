# Synthetic response-contract preflight

Run this preflight for every selected model after its prompt and adapter are
final, but before freezing `run-matrix.json`. It makes two fresh model calls:
one with the actual analysis-prompt shape and one with the actual
identification-prompt shape.

The embedded `CASE-SYN0` dossier is generated in memory. It is deliberately
fictional: each of the minimum 26 required measures contains one sustained D,
and it has no source, work identity, or published interpretation. The harness
does not read `data/manifest.json`, `data/cases/`, the identity key, or the
source manifest.

```sh
node scripts/run-synthetic-preflight.mjs --model openai-frontier
```

Replace the model label with each exact label in the development matrix. A pass
requires both calls to return the exact heading and JSON contracts enforced by
`scripts/lib/response-validator.mjs`, including valid evidence references. The
harness also rejects an adapter whose current hash differs from the development
matrix or whose declared tool access is not `none`.

Rendered prompts, model responses, and CLI stderr remain transient and are
deleted or discarded after validation. The only persistent artifact is a
read-only JSON receipt in `data/provenance/preflight-receipts/`. It contains
requested-model, hash, byte-count, timing, exit-status, and validation metadata;
it never contains rendered prompt, response, stderr, or real-case content. The
command prints the ready-to-paste `{path, sha256}` reference. It does not edit
the model matrix.

A failed attempt also writes only a metadata receipt and exits with status 5.
Authentication, timeout, command, and response-contract failures are recorded
as coarse codes so that provider text or account information is not retained.
Fix the cause and create a new receipt; attempts are never overwritten.

After a pass, set the model's `preflight_receipt` to the printed path and hash:

```json
{"path": "data/provenance/preflight-receipts/NAME.receipt.json", "sha256": "PRINTED_HASH"}
```

Also record the dated `passed_no_outcome_YYYY-MM-DD` status. The freeze check
validates the receipt's exact schema, model/task contract, synthetic dossier,
source-code hashes, recomputed rendered-prompt hash and byte count, task passes,
date, and content-retention flags, then adds
the receipt to `collection-lock.json`. Any subsequent change to a prompt,
adapter, synthetic dossier generator, or response validator invalidates the
receipt and requires a new preflight before freeze. These calls test transport
and response compliance only; their fictional judgments are not experimental
observations and are not included in the scheduled collection or analysis.

Run the local fixture test without contacting any provider:

```sh
node scripts/test-synthetic-preflight.mjs
```
