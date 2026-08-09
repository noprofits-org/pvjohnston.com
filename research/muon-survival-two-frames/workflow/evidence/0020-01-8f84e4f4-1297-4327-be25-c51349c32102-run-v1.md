# Run handoff receipt

- **Gate:** `execute`, iteration 1
- **Actor and role:** `run-operator-muon-01`, configured `run_operator`
- **Requested gate:** `run_review`
- **Graph state at handoff:** still `execute`; this producer recorded no workflow transition
- **Git commit used:** `8d01892e1fb80aeea83c3c19e821f0abd49be094`, equal to the clean upstream tip before execution

## Incoming authorization and frozen lineage

- **Incoming edge:** normal run, event sequence 19,
  `setup_review --approve--> execute`; event ID
  `971711e0-b446-4d4b-ba08-154396a0b3e0`, event SHA-256
  `8c09285d4b2078eeea348916bcb90044987917519ec5a8527df0b20612e1269f`,
  submission sequence 18.
- **Graph:** version 1, SHA-256
  `e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404`.
- **Approval evidence:**
  `research/muon-survival-two-frames/workflow/setup-review-v7.md` and its event-19
  immutable snapshot were byte-identical, 2,915 bytes, SHA-256
  `43df8cbc0b834ffcf7b336765dd93405010697968e76d5e1a66a128d347bc508`.
- **Protocol:** `research/muon-survival-two-frames/PREREGISTRATION-v1.md`, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- **Inputs / setup:** `research/muon-survival-two-frames/inputs.json` SHA-256
  `8e2d98f35f86678a7a018a13562ee4c9aa7b900a11ee58deb8b2007de4f82de1`;
  `research/muon-survival-two-frames/setup-manifest.json` SHA-256
  `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619`;
  33 bound setup records verified before execution.
- **Runner / environment:** `research/muon-survival-two-frames/src/run.py` SHA-256
  `eec8ce19b3229ca2e6a4d1a42afa7aefc8e1d34a006314ecb38bd20f83bfc731`;
  `research/muon-survival-two-frames/environment.json` SHA-256
  `d27e216c106d13c513247aa78e3eb15186db516e47672b6f5acb0028a1ad0904`.
- **Prior run ID:** none. The `runs/` namespace did not exist.
- **New run ID:** `run-001`.

## Exact execution and resource boundary

The following approved command was invoked exactly once from the repository
root, without a timing wrapper or argument change:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

- Supervisor exit: 0; `COMPLETE.json` exit status: 0; the sealed manifest's
  pre-completion `exit_status` field is null as required by its validated
  schema/contract.
- Manifest timestamps: start `2026-08-09T08:35:02Z`, completion
  `2026-08-09T08:35:02Z`. Command-supervisor wall time: 0.073296749 seconds.
- Actual host: Ubuntu 24.04.4 LTS; Linux `7.0.0-28-generic`; x86-64; 11th Gen
  Intel Core i7-1165G7 at 2.80 GHz; 8 logical CPUs.
- Runtime: CPython 3.12.3, NumPy 2.5.1, Matplotlib 3.11.1, pip 26.2.1,
  Node.js 24.18.0.
- The sealed namespace totals 805,089 bytes, below the 10 MB registered output
  budget. Peak RSS is unavailable: preserving the exact command excluded an
  external resource wrapper, so this receipt makes no memory-budget claim.

## Raw bundle inventory

| Repository-relative artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy` | 800,128 | `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229` |
| `research/muon-survival-two-frames/runs/run-001/stdout.log` | 115 | `2f62a24bcc18d083cefee98d98605fa64534c467bd70705e6c520ef4a69f8367` |
| `research/muon-survival-two-frames/runs/run-001/stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `research/muon-survival-two-frames/runs/run-001/run-manifest.json` | 3,935 | `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a` |
| `research/muon-survival-two-frames/runs/run-001/checksums.sha256` | 327 | `a66ccf91a5e5deaee8c76c1e005e506b08ee4bed667c17e81160f31ec79bb715` |
| `research/muon-survival-two-frames/runs/run-001/COMPLETE.json` | 584 | `65adac211e77e676c13e1b37ea1be69391c711a2fb63b452ae0c0bf283874c77` |

The run manifest path is
`research/muon-survival-two-frames/runs/run-001/run-manifest.json`.

## Integrity, completeness, and scope

The documented read-only validator was invoked once and exited 0:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/validate_run.py --run-id run-001
```

It reported exactly six files, `valid=true`, and schema, manifest, provenance,
and hash validity all true. Independent `sha256sum --check` verification passed
for the sample, both captured streams, and run manifest. The completion record
binds the manifest and checksum inventory. The sample metadata matched the
frozen `float64` shape `[100000]`; no sample value was printed or inspected.

There were no deviations, failures, retries, resumes, quarantines, or extra run
namespaces. No survival calculation, reconstruction, analysis command, result,
plot, metric, figure, post prose, or bibliography work occurred. Scientific
outcome: not inspected.

This producer receipt intentionally makes no approval or run-admission claim
and contains no admission marker. If approval is granted, the independent run
review artifact must contain exactly one protocol-required structured marker
for `run-001`.

## Journal handoff

- Pre-execution checkpoint: session
  `20260809T045452Z-one-muon-two-frames-7ed9`, event
  `bca900e5-124f-4104-8326-01c370e87de2`,
  `2026-08-09T08:34:58.409Z`.
- Post-validation checkpoint: event
  `51f06f19-3ea3-409e-9143-32d32f94f26b`,
  `2026-08-09T08:36:30.838Z`.
- **Next action:** independent `run_review` checks admission without scientific
  interpretation; the coordinator alone records the resulting transition.
