# Analysis review, iteration 2

- **Gate:** `analysis_review`, iteration 2
- **Actor:** `analysis-reviewer-muon-13`
- **Decision:** `amend`
- **Independence:** Fresh read-only session, distinct from producers and prior
  reviewers as coordinator-confirmed. No tools, filesystem/network access,
  calculations, edits, or workflow commands were used.

## Reviewed artifacts

- `research/muon-survival-two-frames/workflow/analysis-v2.md` — 4,971 bytes;
  SHA-256
  `7310dc53e6dfa068c2143133bab0c1d76638be20c08388a6cf2120109e0f8796`
- `research/muon-survival-two-frames/PREREGISTRATION-v1.md` — 19,383 bytes;
  SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`
- `research/muon-survival-two-frames/setup-manifest.json` — 5,548 bytes;
  SHA-256
  `faa3b3c470c552125261a1874b8a53ae458e6b4f374dd24ef25260e34a7e9619`
- `research/muon-survival-two-frames/runs/run-001/run-manifest.json` — 3,935
  bytes; SHA-256
  `63fb2d8399f6a3bc8f15d6cc54e75a9270b3e145abc5afd0dcee4276c1817f9a`
- `research/muon-survival-two-frames/runs/run-001/proper_lifetimes_s.npy` —
  800,128 bytes; SHA-256
  `6d21310c0f887a9fdf874d4178214857423d455ab08ef3d6171894f32f9e8229`
- `research/muon-survival-two-frames/results/summary.json` — 77,185 bytes;
  SHA-256
  `26d979a9ceebf573f9c23e8522bfd5ad173b6f537bb2ae44066dd416a5f690b0`
- `research/muon-survival-two-frames/metrics.json` — 6,586 bytes; SHA-256
  `b1fae549ae8c94221f8cb5b9aeeac62a56b8ca1e0f4eec99b37d24e6e7b31ad8`
- `research/muon-survival-two-frames/src/render_figure.py` — 6,001 bytes;
  SHA-256
  `240598a07744765bb2381a7150e38074dbcad9af1425d0f95a1d30860dac1c24`
- `images/muon-survival-two-frames-hero.png` — 65,124 bytes; SHA-256
  `d56cf0a74637fafbf39aff49212bfe6aaef7a40832b47697feac32c754358285`
- Attached original-resolution PNG, visually inspected.

## Blocking findings

1. **Critical — the proposed correction is not lawful under `revise`.** The
   exposed run binds `setup-manifest.json`, which binds the canonical renderer.
   Altering that renderer, its manifest, or the validation interpretation would
   change an accepted implementation contract after exposure. The
   preregistration additionally states that any post-exposure change to the
   implementation contract or figure content requires the amendment route.
2. **High — an analysis-only provenance layer is not prospectively
   authorized.** Introducing a new renderer, command, provenance schema, or
   canonical v2 figure layer now would itself be a newly chosen post-result
   implementation contract. Versioning preserves history but does not make
   that new contract prospective or exempt it from review.
3. **High — the current figure remains presentation-incomplete.** Panel B
   shows coincident exponents and symbolic route labels, but not the differing
   frame-specific distance and time values required by the frozen figure
   description.

## Non-blocking observations

- The requested correction is presentation-only and need not alter the
  explanatory question, raw sample, canonical numerical result, metrics, seed,
  grid, thresholds, or stopping rule.
- The accepted raw execution lineage should remain immutable and may be
  retained as the predecessor lineage during amendment.
- No rerun is presently justified. Whether amended setup can reuse the
  admitted raw sample and regenerate only derived presentation artifacts must
  be explicitly specified and independently approved; this review does not
  invent such an edge or execution rule.

## Required route

`analysis_review -> protocol_amendment`

The amendment should disclose the exposed v1 figure and analysis, preserve the
accepted raw run, quarantine or supersede the affected v1 presentation lineage
without overwriting it, and freeze the exact v2 renderer/provenance/check
contract. It must then pass `amendment_review`, `amended_setup`, and
`amended_setup_review`.

## Validity versus scientific outcome

This decision concerns provenance and post-exposure implementation validity
only. It neither disputes nor approves the reported frame agreement, survival
values, Monte Carlo checks, metrics, or broader scientific outcome. All
nonvisual analysis-review checks remain outstanding.

## Residual risks

- The amendment may accidentally broaden from presentation correction into
  scientific reanalysis.
- Reusing the raw run requires an explicit, reviewable lineage contract.
- Actor identities remain self-asserted.
- The complete numerical, metrics, allowlist, and reproducibility audit has not
  yet received independent approval.

## Smallest next action

Create a narrowly scoped, versioned amendment packet that freezes the
presentation-only change and states exactly which v1 artifacts remain
immutable, which presentation artifacts are superseded, and whether
regeneration consumes the unchanged admitted `run-001` and `summary.json`
without production execution.
