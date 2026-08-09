# Analysis iteration 2 handoff

- **Gate:** `analyze`, iteration 2
- **Incoming review:** `workflow/analysis-review-v1.md`, SHA-256
  `70d40817c1bf8960d599d89179b4fad4eaca814c04c20ac84340ff5de27df316`
- **Incoming event:** sequence 23, event ID
  `26c4b4ac-2af0-4ba7-b493-63fa77b01fd0`, decision `revise`
- **Disposition:** stopped before mutation because the requested renderer change
  cannot pass the currently frozen lineage checks without changing an
  implementation/provenance contract after exposure

## Requested presentation correction

Independent analysis review asked panel B to visibly show the two numeric
routes to the shared exponent: the detector-frame 15.0 km path and laboratory
travel time against the dilated mean lifetime, and the muon-frame contracted
path and proper travel time against the proper mean lifetime. The request does
not dispute or change a scientific value, result, threshold, input, seed, grid,
or model. It is an implementation of the already frozen figure description.

No renderer or artifact was changed in this iteration because the repository's
current integrity chain makes even that presentation-only delta inconsistent.

## Exact unchanged byte identities

| Repository-relative artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `research/muon-survival-two-frames/src/render_figure.py` | 6,001 | `240598a07744765bb2381a7150e38074dbcad9af1425d0f95a1d30860dac1c24` |
| `research/muon-survival-two-frames/setup-manifest.json` | 5,548 | `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619` |
| `research/muon-survival-two-frames/runs/run-001/run-manifest.json` | 3,935 | `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a` |
| `research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy` | 800,128 | `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229` |
| `research/muon-survival-two-frames/results/summary.json` | 77,185 | `26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0` |
| `research/muon-survival-two-frames/metrics.json` | 6,586 | `b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8` |
| `images/muon-survival-two-frames-hero.png` | 65,124 | `d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285` |

The sealed run manifest binds `setup-manifest.json` at exactly 5,548 bytes and
SHA-256 `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619`.
That setup manifest in turn binds the canonical renderer at exactly 6,001
bytes and SHA-256
`240598a07744765bb2381a7150e38074dbcad9af1425d0f95a1d30860dac1c24`.

## Integrity conflict

1. Editing `src/render_figure.py` while retaining the current setup manifest
   makes `verify_setup_manifest()` reject the renderer byte count or SHA-256.
   The required canonical `analyze.py --check` path calls that verifier while
   reconstructing the recorded run specification.
2. Updating `setup-manifest.json` to record the revised renderer makes the
   manifest's own digest differ from the setup-manifest digest sealed into
   `run-001/run-manifest.json`. The recorded-run builder digests the current
   canonical setup manifest, and run-bundle validation then rejects the new
   specification because its lineage differs from the immutable run lineage.
3. Editing the sealed run manifest would mutate raw execution evidence.
   Changing `run.py`, `contract.py`, or `analyze.py` to bypass or reinterpret
   the comparison would change the reviewed runner or implementation contract
   after exposure. Silently substituting another renderer or command would
   violate the frozen canonical figure command and provenance promise.

Those alternatives are outside an analyst's `revise` authority. They would
make a passing check ceremonial rather than preserve the accepted execution
lineage.

## Work performed and unchanged scope

Only read-only Git, journal, workflow, hash, manifest, and source inspection
was performed. No canonical analysis, renderer, metrics, production, RNG,
retry, rerun, resume, repair, or stochastic command ran. No v1 PNG was copied
because no replacement generation began. No raw, summary, metrics, image,
protocol, input, constants, environment, schema, setup manifest, runner,
validator, post, bibliography, or workflow-ledger byte changed. This receipt
is the sole worktree addition. No transition, commit, or push was performed.

## Exact question for review

Does this presentation-only correction require routing through `amend` because
the canonical renderer is hash-bound into the setup manifest and accepted run
lineage, or may a narrowly authorized, versioned analysis-only provenance layer
be introduced under `revise`—preserving the original setup manifest, accepted
execution evidence, v1 renderer/image, and unchanged scientific result—without
invalidating the accepted execution contract?

Until that route is explicitly reviewed, the smallest honest action is to
preserve every v1 byte and refrain from generating a v2 image.
