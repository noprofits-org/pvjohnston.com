import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

import {hashFile} from "./lib/collection-integrity.mjs";
import {
  buildReportingAddenda,
  REPORTING_ADDENDUM_FILES
} from "./lib/reporting-addenda.mjs";

const experimentDir = path.resolve(import.meta.dirname, "..");
const summaryPath = path.join(experimentDir, "results", "1.0.0", "summary.json");
const lockPath = path.join(experimentDir, "collection-lock.json");
const checksumPath = path.join(experimentDir, "data", "provenance", "collection-output-sha256.txt");
const reportingSourcePaths = {
  reporting_addenda_builder_sha256: path.join(experimentDir, "scripts", "build-reporting-addenda.mjs"),
  reporting_addenda_library_sha256: path.join(experimentDir, "scripts", "lib", "reporting-addenda.mjs"),
  reporting_addenda_test_sha256: path.join(experimentDir, "scripts", "test-reporting-addenda.mjs")
};
const protectedHashesBefore = {
  summary: hashFile(summaryPath),
  lock: hashFile(lockPath),
  checksums: hashFile(checksumPath)
};
assert.equal(
  protectedHashesBefore.summary,
  "e915df4256e2ff493581d62610e952a4fac95d7f8f1032a0afa28eee919eb383",
  "primary-summary fixture hash changed"
);

const first = buildReportingAddenda(experimentDir);
const second = buildReportingAddenda(experimentDir);
assert.deepEqual(second, first, "reporting addenda must build deterministically");
for (const artifact of Object.values(first)) {
  for (const [field, sourcePath] of Object.entries(reportingSourcePaths)) {
    assert.equal(artifact.provenance[field], hashFile(sourcePath), `${field} provenance mismatch`);
  }
}

assert.equal(first.pairwiseBootstrap.artifact_kind, "preregistered_reporting_addendum");
assert.equal(first.pairwiseBootstrap.preregistered_scope.repetitions, 2000);
assert.equal(first.pairwiseBootstrap.preregistered_scope.seed, 1702);
assert.equal(first.pairwiseBootstrap.pairs.length, 3);
const pairBySystems = new Map(first.pairwiseBootstrap.pairs.map((entry) => [entry.systems.join("|"), entry]));
const frontierAnthropic = pairBySystems.get("openai-frontier|anthropic-frontier");
const frontierPrior = pairBySystems.get("openai-frontier|openai-prior-generation");
const anthropicPrior = pairBySystems.get("anthropic-frontier|openai-prior-generation");
assert.equal(frontierAnthropic.complete_paired_units, 12);
assert.equal(frontierAnthropic.observed.pairs, 12);
assert.equal(frontierAnthropic.provider_comparison, "cross_provider");
assert.deepEqual(frontierAnthropic.bootstrap_95.ordinal_krippendorff_alpha, {
  defined_replicates: 1837,
  defined_fraction: 0.9185,
  lower_95: 0.32386363636363635,
  upper_95: 1
});
assert.equal(frontierPrior.complete_paired_units, 30);
assert.equal(frontierPrior.observed.pairs, 30);
assert.equal(frontierPrior.provider_comparison, "within_provider");
assert.deepEqual(frontierPrior.bootstrap_95.ordinal_krippendorff_alpha, {
  defined_replicates: 2000,
  defined_fraction: 1,
  lower_95: 0.774169835234474,
  upper_95: 0.981817610062893
});
assert.equal(anthropicPrior.complete_paired_units, 12);
assert.equal(anthropicPrior.observed.pairs, 12);
assert.equal(anthropicPrior.provider_comparison, "cross_provider");
assert.deepEqual(anthropicPrior.bootstrap_95.ordinal_krippendorff_alpha, {
  defined_replicates: 1837,
  defined_fraction: 0.9185,
  lower_95: 0.29641812865497086,
  upper_95: 1
});
for (const pair of first.pairwiseBootstrap.pairs) {
  for (const interval of Object.values(pair.bootstrap_95)) {
    assert.equal(interval.defined_fraction, interval.defined_replicates / 2000);
    assert.ok(interval.defined_replicates >= 0 && interval.defined_replicates <= 2000);
  }
}

assert.equal(first.caseStatus.artifact_kind, "post_hoc_descriptive");
assert.equal(first.caseStatus.provenance.collection_output_record_count, 540);
assert.equal(first.caseStatus.provenance.strictly_valid_analysis_count, 49);
assert.equal(first.caseStatus.provenance.invalid_analysis_responses_parsed, 0);
assert.ok(first.caseStatus.interpretation_boundary.includes(
  "Pooled means and counts weight each valid run equally, are system/provider-unbalanced, and change composition where Anthropic responses are invalid."
));
const expectedCaseCounts = {
  "CASE-6U43": {"openai-frontier": 3, "anthropic-frontier": 3, "openai-prior-generation": 3},
  "CASE-8JQJ": {"openai-frontier": 3, "anthropic-frontier": 1, "openai-prior-generation": 3},
  "CASE-D09B": {"openai-frontier": 3, "anthropic-frontier": 1, "openai-prior-generation": 3},
  "CASE-DZWT": {"openai-frontier": 3, "anthropic-frontier": 3, "openai-prior-generation": 3},
  "CASE-Q2R9": {"openai-frontier": 3, "anthropic-frontier": 2, "openai-prior-generation": 3},
  "CASE-VT57": {"openai-frontier": 3, "anthropic-frontier": 3, "openai-prior-generation": 3}
};
const expectedConsensus = {
  "CASE-6U43": "tonic_double_return",
  "CASE-8JQJ": "off_tonic_recapitulation",
  "CASE-D09B": "tonic_double_return",
  "CASE-DZWT": "tonic_double_return",
  "CASE-Q2R9": "tonic_double_return",
  "CASE-VT57": "off_tonic_recapitulation"
};
for (const entry of first.caseStatus.cases) {
  const expectedCounts = expectedCaseCounts[entry.case_id];
  assert.ok(expectedCounts, `unexpected case ${entry.case_id}`);
  const total = Object.values(expectedCounts).reduce((sum, value) => sum + value, 0);
  assert.equal(entry.pooled.valid_analysis_count, total);
  assert.equal(entry.pooled.argmax_consistency.unanimous, true);
  assert.equal(entry.pooled.argmax_consistency.consensus_label, expectedConsensus[entry.case_id]);
  assert.equal(entry.pooled.argmax_consistency.matching_count, total);
  assert.equal(entry.pooled.argmax_consistency.matching_fraction, 1);
  for (const [model, count] of Object.entries(expectedCounts)) {
    assert.equal(entry.by_system[model].valid_analysis_count, count);
    assert.deepEqual(entry.by_system[model].unique_argmax_labels_present, [expectedConsensus[entry.case_id]]);
  }
}

for (const [kind, filename] of Object.entries(REPORTING_ADDENDUM_FILES)) {
  const target = path.join(experimentDir, "results", "1.0.0", filename);
  assert.ok(fs.existsSync(target), `generated reporting addendum is missing: ${target}`);
  const diskBody = fs.readFileSync(target, "utf8");
  assert.equal(diskBody, `${JSON.stringify(first[kind], null, 2)}\n`,
    `generated reporting addendum is stale or nondeterministically formatted: ${target}`);
  assert.deepEqual(JSON.parse(diskBody), first[kind]);
}

assert.deepEqual({
  summary: hashFile(summaryPath),
  lock: hashFile(lockPath),
  checksums: hashFile(checksumPath)
}, protectedHashesBefore, "reporting addendum build changed a protected primary input");

process.stdout.write("reporting addendum tests passed\n");
