# Identification scoring protocol

Freeze `identity-key.json` with the six randomized case IDs before collection.
For each case, list normalized composer, work, catalogue, movement, and accepted
aliases. The key is operator-only and never enters a model prompt.

After all 54 identification probes are immutable, compare each response with
the frozen key and add one judgment to `identification-adjudication.json`:

```json
{
  "output": "MODEL__symbolic__CASE-XXXX__run-01.md",
  "level": "L0",
  "reason": "Brief factual explanation of the match or mismatch."
}
```

Use `L2` only when both a uniquely identifying work or catalogue designation
and the movement are correct. Use `L1` when the composer or work family is
correct but the response does not uniquely identify the work and movement. Use
`L0` for an incorrect answer, broad style resemblance, or abstention.

Set adjudication `status` to `complete` only after every valid scheduled output
has exactly one judgment. The analyzer rejects missing, duplicate, unknown, or
invalid levels. Identification scoring is factual adjudication, not a judgment
of whether the model's musical reasoning was good.

