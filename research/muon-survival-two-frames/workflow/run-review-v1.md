# Run-review receipt

- **Gate:** `run_review`, iteration 1
- **Actor:** `run-reviewer-muon-11`
- **Decision:** `approve`
- **Blocking findings:** none
- **Accepted IDs:** authorization event
  `971711e0-b446-4d4b-ba08-154396a0b3e0` (sequence 19); normal production
  `run-001`
- **Quarantined IDs:** none

- **Admitted run:** `run-001`

## Reviewed inventory

Control artifacts: reviewer definition `a584f906…da561`; computational workflow
`798c5a1e…afed`; authoring guide `d512c6ff…57c7`; graph
`e50f1247…d404`; preregistration `501f57ab…377`; README
`40951373…6885`; inputs `8e2d98f3…2de1`; constants `62b7812b…e87`;
sources `dc11e517…07f`; environment `d27e216c…904`; setup manifest
`faa3b3c4…619`; workflow ledger `e30a87c3…719`; setup approval
`43df8cbc…508`; run receipt and event-20 snapshot, each
`35e20be3…2074`; and failed reviewer-attempt receipt `b0265767…f9cd`.

Implementation contracts: `src/contract.py` `30eee0b3…e7df`,
`src/bundle.py` `0f81c227…d9bc`, `src/run.py` `eec8ce19…c731`,
`src/validate_run.py` `00db3e7f…7383`, run-manifest schema
`23908b45…9396`, and completion schema `62500517…053c`.

Sealed six-file namespace:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `runs/run-001/proper_lifetimes_s.npy` | 800128 | `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229` |
| `runs/run-001/stdout.log` | 115 | `2f62a24bcc18d083cefee98d98605fa64534c467bd70705e6c520ef4a69f8367` |
| `runs/run-001/stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `runs/run-001/run-manifest.json` | 3935 | `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a` |
| `runs/run-001/checksums.sha256` | 327 | `a66ccf91a5e5deaee8c76c1e005e506b08ee4bed667c17e81160f31ec79bb715` |
| `runs/run-001/COMPLETE.json` | 584 | `65adac211e77e676c13e1b37ea1be69391c711a2fb63b452ae0c0bf283874c77` |

## Exact command evidence

```text
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
Supervisor exit: 0
Manifest start/completion: 2026-08-09T08:35:02Z / 2026-08-09T08:35:02Z
Wall time: 0.073296749 seconds

research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/validate_run.py --run-id run-001
valid=true; schema=true; manifest=true; provenance=true; hashes=true;
file_count=6; sample_dtype=float64; sample_shape=[100000]
```

The coordinator transcript additionally reports all four checksum entries
`OK`, exactly one `run-001` directory, 20 verified workflow events, 19
snapshots, and `run_review` iteration 1.

## Findings and route

- **Completeness/integrity:** complete. Event 19 immutably authorizes normal
  execution; event digest is
  `8c09285d4b2078eeea348916bcb90044987917519ec5a8527df0b20612e1269f`.
  Command, protocol, implementation, environment, and input lineage match.
  PCG64 seed `20260808`, one `Generator.exponential(..., size=100000)` call,
  retained draw order, `float64` shape `[100000]`, byte count, and hash are
  bound without exposing values. Both streams were captured; stderr is empty.
  Nothing is missing.
- **Stopping/retry:** the sole registered sample completed and stopped after
  sealing. No resume is permitted or needed. A registered retry is inadmissible
  after valid completion.
- **Budget:** elapsed time and sealed-output size satisfy the registered limits.
  Cost, network, and GPU use were absent. Peak RSS was not measured, so the
  256 MB ceiling remains an unverified residual rather than a deviation.
- **Deviations:** none evidenced; no retry, resume, amendment, overwrite,
  cherry-picking, or extra analysis occurred.
- **Route:** `run_review → analyze`.
- **Validity versus outcome:** approval admits only sealed raw-sample lineage
  and integrity. No values or scientific outcome were inspected, and no frame
  agreement, survival result, explanatory conclusion, or reproducibility claim
  is approved here.
- **Residual risks:** peak RSS was unavailable; stdout content was represented
  by its sealed size/hash rather than streamed text; actor IDs remain
  self-asserted.
- **Smallest next action:** coordinator records approval; the analyst consumes
  only the admitted immutable sample and resulting approval event.

## Independence and effort

Fresh read-only reviewer distinct from all producers, setup reviewers, and the
failed reviewer-10 attempt, as coordinator-confirmed. It used only immutable
streamed bytes and coordinator-generated read-only command evidence; no tools,
filesystem, network, writes, RNG, calculations, sample inspection, analysis,
or workflow transition. Approximate effort: 70 minutes.
