# Reproducing the dataset 1.0.0 analysis

## Completed state

This is the post-collection guide for the frozen off-tonic recapitulation
pilot. The preregistration and statistical-analysis plan intentionally retain
their pre-collection language. Dataset 1.0.0 was frozen at
2026-07-19T17:54:14Z, the 41-file collection lock was created at
2026-07-19T17:56:35.630Z, and all 108 scheduled calls ran from 18:15:05 through
19:54:52 UTC on 2026-07-19. No call timed out, failed at the command level, or
was retried.

The frozen primary result is a no-go for automatic expansion. It retains five
frozen-contract-invalid Anthropic analysis responses and therefore accepts 103 of 108
scheduled responses. A separately labelled post hoc sensitivity changes only
two prompt–validator interpretations, accepts all five immutable responses,
and still returns a no-go. Neither analysis establishes music-theoretical
correctness because no music-theory-trained human validated the events, rubric,
or model scores.

## Artifact map

- `results/1.0.0/summary.json` is the deterministic preregistered primary
  analysis. It contains validity, target and K. 545 anchor repeatability,
  cue-stratified direct agreement, zero/one/two/three-score availability,
  named target and anchor cross-system comparisons, pooled provider-unbalanced
  summaries, identity adjudication, `suspected_recognition` rows by system and
  case, L2-stratified score repeatability, dispersion, and all frozen gates.
- `results/1.0.0/pairwise-bootstrap-supplement.json` supplies the named-pair
  dossier-bootstrap intervals required by the frozen statistical plan but
  omitted by the locked analyzer's printed schema.
- `results/1.0.0/case-status-descriptives.json` is a post hoc count of the
  maximum-probability status in each strictly valid analysis response. Its
  pooled means are explicitly system- and provider-unbalanced.
- `results/1.0.0/validator-contract-sensitivity.json` is post hoc and does not
  replace the primary result. It accepts a nonempty `case_note` without an
  unstated 40-word cap and admits genuine dossier `direction_id` values beside
  measure `evidence_id` values. Event IDs and unknown identifiers remain
  invalid. It replays within-system, cross-system, missingness, status,
  recognition, L2-stratified, dispersion, and gate calculations from the
  original response bytes.
- `data/provenance/identification-adjudication.json` is the reconciled 54-row
  identification judgment set. The frozen plan called for operator scoring;
  implementation used two independent Codex scoring passes, which agreed on
  every L0/L1/L2 level. This is a disclosed operational deviation, not expert
  music-theory validation.
- `data/provenance/EXPERT_REVIEW.md` and
  `data/provenance/EXPERT_REVIEW_TEMPLATE.json` form an expert-readable review
  packet for versioned measure-, event-, cue-, and source-specific criticism.

Key SHA-256 values are:

| Artifact | SHA-256 |
| --- | --- |
| `data/manifest.json` | `6a027698775083ed275e0149685ec23cc07dea9d4f7f19b2a40b6c7d2eb246bb` |
| `collection-lock.json` | `2efbbcb23fd1178e50297618af083ecc8d1d5b6dbddeb5324b14bab78a13f015` |
| `data/provenance/collection-output-sha256.txt` | `7aa40e37c9948f03ef7689320e07ac42067ea9ed957bdec5fcc7ce97f560f229` |
| `results/1.0.0/summary.json` | `e915df4256e2ff493581d62610e952a4fac95d7f8f1032a0afa28eee919eb383` |
| `results/1.0.0/pairwise-bootstrap-supplement.json` | `83d7260231dbeebfafa53e949bd5572d28606773eacc658f7740fcb3a4294de7` |
| `results/1.0.0/case-status-descriptives.json` | `4abf0bd103f2ccd18f6074a287604717ac89073381e3849bdc7658725ab39f8a` |
| `results/1.0.0/validator-contract-sensitivity.json` | `b9bb81cbce9460ccb9c653cad883728211995dc4c0672ae097c028db59d5ab2c` |
| `data/provenance/identification-adjudication.json` | `da8412bbaa9b55a09ae12348b1b4eab72d9ff446d6c17998a4e24d608bb623f1` |

## Verification

Use Node.js 24.8.0 or a compatible Node 24 release. From this directory:

```sh
node scripts/restore-immutable-modes.mjs
node scripts/verify-collection-lock.mjs
node scripts/test-analyzer.mjs
node scripts/test-reporting-addenda.mjs
node scripts/test-validator-contract-sensitivity.mjs
```

ZIP extraction restores Git-tracked files as writable even though the frozen
collection and masked-adjudication artifacts were made read-only during the
experiment. The first command reapplies those mode bits to an exact, asserted
551-file set; it changes no bytes and is idempotent. The analyzer deliberately
refuses writable attempt claims and adjudication packet files.

The complete test suite is:

```sh
node scripts/restore-immutable-modes.mjs
for test_file in scripts/test-*.mjs; do node "$test_file"; done
```

The analyzer test independently recreates the primary summary and requires a
byte-for-byte match. The addendum and sensitivity tests rebuild their artifacts
and pin source hashes, numerical values, raw checksums, and protected primary
hashes. The full suite contains 12 test programs.

## Distribution boundary

The public ZIP is an **analysis-reproduction bundle**, not a dossier-source
reconstruction bundle. It contains all 540 raw collection artifacts, including
hidden attempt claims, plus dossiers, prompts, frozen inputs, adjudication,
results, analyzers, and tests. It excludes `data/sources/`, every score or
source PDF/image, and every `tmp/` scratch directory. The source manifest keeps
stable repositories, pinned revisions, page coordinates, and hashes so an
expert can audit the source chain separately.

Five frozen-invalid run sidecars preserve low-sensitivity absolute temporary
filesystem paths in their recorded stack traces. They contain no credential,
email address, account identity, provider request identifier, or token. They
remain byte-for-byte unchanged because redaction would break the collection
hash record.

See `BUNDLE-NOTICE.md` for third-party data attribution and licensing scope.
