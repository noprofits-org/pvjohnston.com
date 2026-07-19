import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import {
  EXPECTED_ANALYSIS_INVOCATIONS,
  EXPECTED_RAW_CHECKSUM_RECORDS,
  VALIDATOR_CONTRACT_SENSITIVITY_FILE,
  buildValidatorContractSensitivity,
  parseAnalysisWithValidatorContractSensitivity,
  writeValidatorContractSensitivity
} from "./lib/validator-contract-sensitivity.mjs";
import {verifyCollectionLock} from "./lib/collection-integrity.mjs";
import {verifyCollectionOutputChecksums} from "./lib/identification-adjudication-packet.mjs";

const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const experimentDir = path.resolve(import.meta.dirname, "..");
const summaryPath = path.join(experimentDir, "results", "1.0.0", "summary.json");
const summaryBefore = fs.readFileSync(summaryPath);
const rawManifestPath = path.join(experimentDir, "data", "provenance", "collection-output-sha256.txt");
const rawManifestBefore = fs.readFileSync(rawManifestPath);

const built = buildValidatorContractSensitivity(experimentDir);
const expectedRescued = [
  "anthropic-frontier__symbolic__CASE-8JQJ__run-02.invalid.md",
  "anthropic-frontier__symbolic__CASE-8JQJ__run-03.invalid.md",
  "anthropic-frontier__symbolic__CASE-D09B__run-02.invalid.md",
  "anthropic-frontier__symbolic__CASE-D09B__run-03.invalid.md",
  "anthropic-frontier__symbolic__CASE-Q2R9__run-01.invalid.md"
].sort();
assert.deepEqual(
  built.result.rescued_outputs.map((entry) => entry.filename).sort(),
  expectedRescued,
  "the five known strict-invalid analysis responses must be the only rescued outputs"
);
assert.equal(built.result.status, "post_hoc_not_preregistered");
assert.equal(built.result.response_accounting.analysis_responses_read, EXPECTED_ANALYSIS_INVOCATIONS);
assert.equal(built.result.response_accounting.strict_valid, 49);
assert.equal(built.result.response_accounting.strict_invalid, 5);
assert.equal(built.result.response_accounting.sensitivity_valid, 54);
assert.equal(built.result.response_accounting.remaining_invalid_count, 0);
assert.equal(built.result.response_accounting.all_tasks_strict_valid, 103);
assert.equal(built.result.response_accounting.all_tasks_sensitivity_valid, 108);
assert.equal(built.result.integrity.raw_checksum_record_count, EXPECTED_RAW_CHECKSUM_RECORDS);
assert.equal(built.result.integrity.raw_bytes_unchanged, true);
assert.equal(built.result.integrity.strict_summary_unchanged, true);
assert.deepEqual(built.result.integrity.verification_order, [
  "collection lock",
  "all raw scheduled-output checksums",
  "strict primary-summary replay (the frozen analyzer reads responses only after the preceding checksum verification)",
  "explicit inspection of all 54 original analysis responses",
  "post-analysis raw checksum replay"
]);
assert.equal(built.result.disclosure.raw_bytes_changed, false);
assert.equal(built.result.disclosure.locked_files_changed, false);
assert.equal(built.result.disclosure.attempt_claims_changed, false);
assert.equal(built.result.disclosure.primary_summary_changed, false);
assert.equal(built.result.disclosure.primary_identification_adjudication_changed, false);
assert.equal(built.result.disclosure.outputs_repaired, false);
assert.equal(built.result.disclosure.calls_retried, false);

const sensitivity = built.result.sensitivity;
assert.equal(sensitivity.validity_and_completeness.output_validity_rate, 1);
assert.equal(sensitivity.validity_and_completeness.cue_completeness_rate, 1);
assert.deepEqual(
  Object.values(sensitivity.within_model).map((entry) => entry.complete_three_run_data),
  [true, true, true]
);
assert.deepEqual(sensitivity.repeatable_models, [
  "openai-frontier",
  "anthropic-frontier",
  "openai-prior-generation"
]);
assert.deepEqual(sensitivity.repeatable_providers, ["OpenAI", "Anthropic"]);
assert.deepEqual(sensitivity.nondegenerate_cues, ["tonal_stability", "preparation_strength"]);
assert.equal(sensitivity.preliminary_gates.output_gate, true);
assert.equal(sensitivity.preliminary_gates.repeatability_gate, true);
assert.equal(sensitivity.preliminary_gates.dispersion_gate, false);
assert.equal(sensitivity.preliminary_gates.analysis_recognition_gate, false);
assert.equal(sensitivity.automatic_expansion_gate, false);
assert.equal(sensitivity.preliminary_gates.identification_gate,
  built.result.strict_reference.preliminary_gates.identification_gate);
assert.deepEqual(sensitivity.analysis_recognition.work_level_events,
  built.result.strict_reference.analysis_recognition.work_level_events);

assert.deepEqual(sensitivity.status_distribution.overall, {
  not_recapitulation: {
    count: 54,
    mean: 0.06761111111111112,
    median: 0.03,
    minimum: 0.002,
    maximum: 0.33
  },
  off_tonic_recapitulation: {
    count: 54,
    mean: 0.28868518518518516,
    median: 0.05,
    minimum: 0.001,
    maximum: 0.985
  },
  tonic_double_return: {
    count: 54,
    mean: 0.6437037037037037,
    median: 0.85,
    minimum: 0.001,
    maximum: 0.997
  }
});
for (const model of ["openai-frontier", "anthropic-frontier", "openai-prior-generation"]) {
  for (const label of ["not_recapitulation", "off_tonic_recapitulation", "tonic_double_return"]) {
    assert.equal(sensitivity.status_distribution.by_model[model][label].count, 18);
  }
}
const recognitionCounts = Object.fromEntries(["none", "style", "composer", "work"].map((level) => [level,
  sensitivity.suspected_recognition.filter((entry) => entry.level === level).length
]));
assert.equal(sensitivity.suspected_recognition.length, 54);
assert.deepEqual(recognitionCounts, {none: 14, style: 36, composer: 0, work: 4});

assert.deepEqual(sensitivity.within_model["anthropic-frontier"].bootstrap_95.ordinal_krippendorff_alpha, {
  defined_replicates: 2000,
  defined_fraction: 1,
  lower_95: 0.6629492974416522,
  upper_95: 0.9001595100634863
});
assert.deepEqual(sensitivity.cross_model.bootstrap_95.ordinal_krippendorff_alpha, {
  defined_replicates: 2000,
  defined_fraction: 1,
  lower_95: 0.6936281063611895,
  upper_95: 0.9002264827004945
});

const l2Strict = built.result.identification.analysis_score_repeatability_by_l2_category.strict_reference;
const l2Sensitivity = built.result.identification.analysis_score_repeatability_by_l2_category.sensitivity;
assert.equal(Object.hasOwn(built.result.identification.inherited_summary,
  "analysis_score_repeatability_by_l2_category"), false);
assert.deepEqual(l2Strict, built.result.strict_reference.analysis_score_repeatability_by_l2_category);
assert.deepEqual(l2Sensitivity, sensitivity.analysis_score_repeatability_by_l2_category);
assert.deepEqual(l2Strict.repeated_l2.pooled_score_repeatability, {
  pairs: 36,
  exact_agreement: 0.8333333333333334,
  within_one_agreement: 1,
  mean_absolute_difference: 0.16666666666666666,
  median_absolute_difference: 0
});
assert.deepEqual(l2Sensitivity.repeated_l2.pooled_score_repeatability, {
  pairs: 54,
  exact_agreement: 0.8148148148148148,
  within_one_agreement: 1,
  mean_absolute_difference: 0.18518518518518517,
  median_absolute_difference: 0
});
assert.deepEqual(l2Strict.no_l2.pooled_score_repeatability, {
  pairs: 186,
  exact_agreement: 0.7634408602150538,
  within_one_agreement: 1,
  mean_absolute_difference: 0.23655913978494625,
  median_absolute_difference: 0
});
assert.deepEqual(l2Sensitivity.no_l2.pooled_score_repeatability, {
  pairs: 216,
  exact_agreement: 0.7685185185185185,
  within_one_agreement: 1,
  mean_absolute_difference: 0.23148148148148148,
  median_absolute_difference: 0
});
assert.deepEqual(l2Sensitivity.repeated_l2.pooled_score_availability, {
  scored_repetitions_per_unit: {zero: 0, one: 0, two: 0, three: 18, other: 0},
  pairwise_availability_agreement: 1,
  mixed_availability_units: 0
});
assert.deepEqual(l2Sensitivity.no_l2.pooled_score_availability, {
  scored_repetitions_per_unit: {zero: 0, one: 0, two: 0, three: 72, other: 0},
  pairwise_availability_agreement: 1,
  mixed_availability_units: 0
});

for (const rescued of built.result.rescued_outputs) {
  assert.ok(rescued.original_issues.length >= 1, `${rescued.filename} must record its original issue(s)`);
  assert.equal(rescued.strict_status, "invalid");
  assert.equal(rescued.sensitivity_status, "valid");
  assert.match(rescued.raw_sha256, /^[0-9a-f]{64}$/);
}

const verified = verifyCollectionLock(experimentDir);
const checksumState = verifyCollectionOutputChecksums(experimentDir, verified.manifest.dataset_version);
assert.equal(checksumState.recorded_paths.size, EXPECTED_RAW_CHECKSUM_RECORDS);

const bendaDossier = JSON.parse(fs.readFileSync(
  path.join(experimentDir, "data", "cases", "CASE-8JQJ.json"),
  "utf8"
));
const bendaInvalidPath = path.join(
  experimentDir,
  "outputs",
  "1.0.0",
  "scheduled",
  "analysis",
  "anthropic-frontier__symbolic__CASE-8JQJ__run-03.invalid.md"
);
const bendaInvalid = fs.readFileSync(bendaInvalidPath, "utf8");
assert.equal(
  parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: bendaInvalid
  }).case_id,
  "CASE-8JQJ",
  "genuine dossier direction IDs and a nonempty long case_note must validate"
);

const rewriteMachineResult = (response, mutate) => {
  const match = response.match(/^```json[ \t]*\n([\s\S]*?)\n```[ \t]*$/m);
  assert.ok(match, "fixture response must contain a JSON block");
  const result = JSON.parse(match[1]);
  mutate(result);
  const replacement = `\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\``;
  return response.slice(0, match.index) + replacement + response.slice(match.index + match[0].length);
};

const emptyCaseNote = rewriteMachineResult(bendaInvalid, (result) => {
  result.case_note = "";
});
assert.throws(
  () => parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: emptyCaseNote
  }),
  /case_note must be a nonempty string/
);

const unknownDirection = rewriteMachineResult(bendaInvalid, (result) => {
  result.cues.preparation_strength.evidence_ids = ["E012", "DR9999"];
});
assert.throws(
  () => parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: unknownDirection
  }),
  /unknown evidence ID DR9999/
);

const eventIdentifier = rewriteMachineResult(bendaInvalid, (result) => {
  result.cues.preparation_strength.evidence_ids = ["EV0001"];
});
assert.throws(
  () => parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: eventIdentifier
  }),
  /unknown evidence ID EV0001/
);

const invalidProbability = rewriteMachineResult(bendaInvalid, (result) => {
  result.status_distribution.not_recapitulation = 0.9;
});
assert.throws(
  () => parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: invalidProbability
  }),
  /status probabilities do not sum to 1/
);

const longCueReason = rewriteMachineResult(bendaInvalid, (result) => {
  result.cues.tonal_stability.reason = Array(41).fill("word").join(" ");
});
assert.throws(
  () => parseAnalysisWithValidatorContractSensitivity({
    expectedCase: "CASE-8JQJ",
    dossier: bendaDossier,
    response: longCueReason
  }),
  /reason exceeds 40 words \(41\)/
);

const generatedPath = path.join(
  experimentDir,
  "results",
  "1.0.0",
  VALIDATOR_CONTRACT_SENSITIVITY_FILE
);
assert.equal(fs.readFileSync(generatedPath, "utf8"), built.body,
  "checked-in generated sensitivity result must match a fresh deterministic build");

const writerFixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), "validator-contract-writer-test."));
try {
  const writerTarget = path.join(writerFixtureRoot, VALIDATOR_CONTRACT_SENSITIVITY_FILE);
  const firstWrite = writeValidatorContractSensitivity(experimentDir, built, {outputFile: writerTarget});
  const secondWrite = writeValidatorContractSensitivity(experimentDir, built, {outputFile: writerTarget});
  assert.equal(firstWrite.sha256, secondWrite.sha256, "identical writer replay must be idempotent");
  const different = structuredClone(built.result);
  different.status = "intentionally_different_test_fixture";
  assert.throws(
    () => writeValidatorContractSensitivity(experimentDir, {result: different}, {outputFile: writerTarget}),
    /refusing to overwrite a different validator-contract sensitivity artifact/
  );
} finally {
  fs.rmSync(writerFixtureRoot, {recursive: true, force: true});
}
assert.deepEqual(fs.readFileSync(summaryPath), summaryBefore,
  "sensitivity analysis must not alter the primary summary");
assert.equal(sha256(summaryBefore), built.result.integrity.primary_summary_sha256_before);
assert.deepEqual(fs.readFileSync(rawManifestPath), rawManifestBefore,
  "sensitivity analysis must not alter the raw checksum manifest");

process.stdout.write("validator-contract sensitivity tests passed\n");
