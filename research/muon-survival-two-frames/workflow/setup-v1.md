# Setup handoff: version 1

- **Graph state:** `setup`, iteration 1.
- **Actor and role:** `experiment-engineer-muon-trial`, configured
  `experiment_engineer` session.
- **Accepted parent:** `question-review-v2.md`, substantive
  `question_review --approve--> setup`; accepted brainstorm lineage is
  `brainstorm-v2.md`.
- **Protocol:** `research/muon-survival-two-frames/PREREGISTRATION-v1.md`,
  19,383 bytes, SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- **Outcome:** not inspected. No canonical sample, survival calculation,
  focal calculation, full-grid calculation, figure, metric, or post prose was
  produced.
- **Requested gate:** independent `setup_review`.

## Implementation inventory

`research/muon-survival-two-frames/setup-manifest.json` contains the complete
25-file reviewed setup inventory with repository-relative paths, byte sizes,
and per-file SHA-256 values. It is 4,266 bytes with SHA-256
`601fc4209f8edbab56a9432171c6fab21370a90414eb2c73dd069ab5e1468d10`.
Key bindings are:

- `inputs.json`: 2,543 bytes,
  `2559e87370bd4f50903b557645b8f30ac640430c5d1b7ec4739aed68cbc4ac62`;
- `constants.json`: 686 bytes,
  `62b7812bd19b50a189cf6b515f09b376d1f2be7334ccd44deb515063b7c56e87`;
- `sources.json`: 2,105 bytes,
  `dc11e517d7927efb19efec490cbd8668ee205ea397282cd2356b3d188d14707f`;
- `environment.json`: 1,172 bytes,
  `d27e216c106d13c513247aa78e3eb15186db516e47672b6f5acb0028a1ad0904`;
- `requirements.lock.txt`: 1,314 bytes,
  `1cf5dcf8ff7f0d797b1adaaf473ae652dcbf031ca072cbb92fe6700ba1a0c782`;
- `src/contract.py`: 13,576 bytes,
  `012d178c7f89612ea4d23a3d66e41dadb34229ba90604c007551c006b8490ceb`;
- `src/bundle.py`: 14,341 bytes,
  `a35e2b4bde88467b732fd320521c2d91851ff43f42961610216db8d8d68a293e`;
- `src/run.py`: 3,159 bytes,
  `e626c9b12465f7a5c7f192f40c8cdceb57131ef9d27d24267985998ebd8b11cf`;
- `src/validate_run.py`: 756 bytes,
  `f898b9cdde19a36af4a1533b297e190692aaa221edbd372346517fe91c325e5a`;
- `src/reconstruct.py`: 12,325 bytes,
  `85610ce539a19d9d6f58f22b7116dbb4e5e58492eeb91a434c83bfdcd9bd96fb`;
- `tests/test_setup.py`: 7,953 bytes,
  `aee6526559830e18b325bf47269453fa6bcbbd961e7f771efabe420b92334e0e`.

The environment is CPython 3.12.3 on Linux x86-64 with pip 26.2.1, NumPy
2.5.1, Matplotlib 3.11.1, and Node.js 24.18.0. The lock pins all twelve selected
Python wheels, including pip and every transitive dependency, to observed
SHA-256 values and forbids source distributions. The setup host required the
documented, digest-pinned PyPA bootstrap because its system interpreter lacks
`ensurepip`; the isolated environment itself is ignored.

The copied preregistration, environment, source, and public-manifest example
placeholders were removed only after real prospective replacements existed.
`PUBLIC_FILES.prospective.txt` is intentionally not the live site-routing
filename. Metrics and workflow role examples remain for their later owners.

## Protocol-to-code traceability

| Frozen choice | Implementation and setup evidence |
| --- | --- |
| PDG central values and exact speed of light | `constants.json`, `sources.json`, schemas, and strict checks in `src/contract.py` |
| Momentum, integer grid, focal index, RNG, seed, one-call draw, count, thresholds | `inputs.json` plus literal fail-closed validation in `src/contract.py`; no CLI override exists |
| Exact environment and deterministic serialization | Hash-locked requirements, `environment.json`, `canonical_json_bytes`, `LC_ALL=C`, and `TZ=UTC` |
| One unsorted float64 proper-lifetime sample only | `src/run.py` delegates one call to `Generator(PCG64).exponential`; it performs no reconstruction or plotting |
| New and immutable run namespace | Exclusive directory/file creation, temporary-to-final sample rename, overwrite refusal, fixed inventory, checksums, and last-written completion marker in `src/bundle.py` |
| Schema, manifest, provenance, and hash checks | Six draft-2020-12 schemas, 25-file setup manifest, strict manifest loaders, `src/validate_run.py`, and tamper tests |
| Independent detector and muon routes | Separate functions in `src/reconstruct.py`; the muon route is tested while the detector function is patched to fail if called |
| Counterfactual and Monte Carlo meaning | Explicit counterfactual label and inclusive population-count implementation in `src/reconstruct.py` |
| All registered checks and Understanding form | Generic dimension-injected evaluator tests every pass/fail branch on synthetic arrays and assembles `understanding-observations-no-verdict` |
| Model and publication boundary | `README.md`, source exclusions, no network imports in the runner, and prospective rather than live public allowlist |

## Commands and results

Setup-only commands executed from the repository root:

```sh
research/muon-survival-two-frames/.venv/bin/python -m pip install --dry-run --require-hashes -r research/muon-survival-two-frames/requirements.lock.txt
research/muon-survival-two-frames/.venv/bin/python -m pip check
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/verify_setup.py
research/muon-survival-two-frames/.venv/bin/python -m unittest discover -s research/muon-survival-two-frames/tests -p 'test_*.py' -v
research/muon-survival-two-frames/.venv/bin/python -m compileall -q research/muon-survival-two-frames/src research/muon-survival-two-frames/tests
node scripts/research-workflow.mjs status --experiment muon-survival-two-frames
node scripts/research-workflow.mjs verify --experiment muon-survival-two-frames
```

All exited zero. Nine tests covered exact manifest/environment checks,
deterministic JSON, seed-0 reproducibility and the 16-draw ceiling, new-run
refusal, bundle sealing and tamper detection, independently implemented frame
agreement, exact zero-path handling, inclusive survival, invalid paths and
lifetimes, all synthetic acceptance branches, and schema parsing. Setup
verification reported 25 bound artifacts and confirmed the canonical namespace
absent. Workflow verification remained at `setup` with five events and four
snapshots.

The timed toy suite took 0.22 seconds wall time and 51,840 KiB peak RSS. A
NumPy/Matplotlib import smoke took 0.24 seconds and 54,768 KiB peak RSS. Both
reported zero socket messages. The production sample itself is about 0.8 MB;
with small JSON/log overhead, the run is expected to remain well below one
minute, 256 MB RSS, and 10 MB generated output. The analyst must separately
measure the registered figure/analysis command; setup did not generate it.

## Exact production and restart contract

The exact normal command, implemented but **not executed**, is:

```sh
research/muon-survival-two-frames/.venv/bin/python research/muon-survival-two-frames/src/run.py --run-id run-001
```

A complete run contains exactly the raw `.npy` sample, stdout, stderr,
`run-manifest.json`, `checksums.sha256`, and last-written `COMPLETE.json`.
Checksums cover sample, logs, and manifest; completion binds manifest and
checksum bytes; later run-review evidence binds completion. A directory that
already exists is never opened for writing. There is no same-run resume.
Incomplete output is preserved and quarantined. One new-ID retry is allowed
only after the graph records the prospectively authorized objective
pre-completion infrastructure failure; the frozen runner supplies the same
seed and draw count. No scientific retry or registered analysis rerun exists.

## Known limitations and focused review questions

No blocking scientific ambiguity was encountered. Setup review should focus on:

1. Does the literal protocol-to-input validation close every production degree
   of freedom without making a legitimate fresh-ID infrastructure retry look
   like a same-run resume?
2. Are the raw-array, manifest, checksum, and last-written completion contracts
   sufficient to establish byte-level admission without OS-level read-only
   permissions? Hash checks catch later mutation, while filesystem permissions
   are not treated as authentication.
3. Are the detector and muon implementations genuinely independent enough,
   including their separate beta/gamma derivations and zero-path branch?
4. Do the synthetic tests cover every registered pass/fail and boundary branch
   without accidentally evaluating a canonical quantity?
5. Are the schemas and custom strict validators mutually faithful? No external
   JSON-Schema engine was added; schema documents are parsed and the production
   fields are enforced directly.
6. Is the platform-specific one-wheel-per-package hash lock an acceptable
   implementation of the approved Linux x86-64 boundary, including the
   documented pip bootstrap?
7. Does the prospective allowlist contain only plausible later public files
   while correctly remaining inactive until editorial review?

Residual nonblocking risks are upstream PDF disappearance, the absence of a
setup-stage Matplotlib rendering memory measurement (figure generation belongs
to analysis), and reliance on workflow review—not actor authentication—to
authorize a fresh retry ID. Any required scientific or frozen-choice change
before exposure should route `setup_review --redesign--> brainstorm`; an
implementation defect should route `setup_review --revise--> setup`.

## Gate retrospective and handoff

The accepted protocol made the producer/operator/analyst split unusually
clear: the runner could be made smaller because survival, the focal point, the
grid, plotting, and prose were all explicitly forbidden here. The independent
question review materially confirmed the two-route interpretation and exposed
dependency availability as a setup-review obligation. Hashing a large setup
inventory, mirroring schemas with strict validators, and documenting a tiny
all-or-nothing retry were disproportionate to the arithmetic but useful for an
honest end-to-end workflow acceptance test. The strongest boundary was the ban
on using the tempting canonical command as a setup smoke test; seed-0 toys
found the same implementation defects without exposure.

Approximate role effort was 21 minutes. Keep the independent setup gate and
immutable run contract; change the template to provide a standard sealed-run
helper and hash-lock recipe; remove no gate during this trial, but consider a
reduced reviewed lane for tiny Understanding notes after the retrospective is
complete.

Journal session: `20260809T045452Z-one-muon-two-frames-7ed9`. Next action: the
coordinator verifies this receipt and setup manifest, leaves a fresh checkpoint,
submits only `workflow/setup-v1.md`, commits and pushes the durable handoff, and
gives the exact submitted snapshot plus bound setup bytes to a fresh read-only
`setup_review`. This producer does not submit, review, transition, commit, or
push.
