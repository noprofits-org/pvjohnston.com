import fs from "node:fs";
import path from "node:path";

import {hashFile, verifyCollectionLock} from "./collection-integrity.mjs";
import {verifyCollectionOutputChecksums} from "./identification-adjudication-packet.mjs";
import {
  availabilityAgreement,
  dossierBootstrap,
  summarizeReliability
} from "./reliability.mjs";
import {parseAndValidateResponse} from "./response-validator.mjs";
import {scheduledSlotPaths} from "./scheduled-bundle-integrity.mjs";

export const REPORTING_ADDENDUM_FILES = Object.freeze({
  pairwiseBootstrap: "pairwise-bootstrap-supplement.json",
  caseStatus: "case-status-descriptives.json"
});

const CUE_NAMES = Object.freeze([
  "tonal_stability",
  "thematic_correspondence",
  "preparation_strength",
  "proportional_location",
  "rhetorical_emphasis",
  "rotational_continuation"
]);
const STATUS_LABELS = Object.freeze([
  "not_recapitulation",
  "off_tonic_recapitulation",
  "tonic_double_return"
]);
const BOOTSTRAP_REPETITIONS = 2000;
const CROSS_SYSTEM_BOOTSTRAP_SEED = 1702;
const EXPECTED_RAW_RECORDS = 540;
const EXPECTED_VALID_ANALYSES = 49;

const readJson = (file, label) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${label} is not readable JSON: ${error.message}`);
  }
};
const jsonBody = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sameJson = (left, right) => JSON.stringify(left) === JSON.stringify(right);
const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};
const finiteProbability = (value) => typeof value === "number"
  && Number.isFinite(value)
  && value >= 0
  && value <= 1;

const primarySummaryState = (experimentDir, manifest) => {
  const summaryPath = path.join(
    experimentDir,
    "results",
    manifest.dataset_version,
    "summary.json"
  );
  const summary = readJson(summaryPath, "primary summary");
  assert(summary.schema_version === "2.1.0", "unexpected primary-summary schema version");
  assert(summary.dataset_version === manifest.dataset_version, "primary-summary dataset mismatch");
  return {summary, summaryPath, summarySha256: hashFile(summaryPath)};
};

const commonProvenance = (experimentDir, verified, summaryState) => ({
  collection_lock_sha256: hashFile(path.join(experimentDir, "collection-lock.json")),
  primary_summary_sha256: summaryState.summarySha256,
  statistical_analysis_spec_sha256: hashFile(path.join(experimentDir, "STATISTICAL_ANALYSIS.md")),
  frozen_reliability_implementation_sha256: hashFile(path.join(experimentDir, "scripts", "lib", "reliability.mjs")),
  frozen_response_validator_sha256: hashFile(path.join(experimentDir, "scripts", "lib", "response-validator.mjs")),
  reporting_addenda_builder_sha256: hashFile(path.join(experimentDir, "scripts", "build-reporting-addenda.mjs")),
  reporting_addenda_library_sha256: hashFile(path.join(experimentDir, "scripts", "lib", "reporting-addenda.mjs")),
  reporting_addenda_test_sha256: hashFile(path.join(experimentDir, "scripts", "test-reporting-addenda.mjs")),
  locked_file_count: Object.keys(verified.lock.files).length
});

const completeUnitCount = (caseUnits) => caseUnits
  .flat()
  .filter((ratings) => ratings.every((value) => Number.isInteger(value) && value >= 0 && value <= 4))
  .length;

export function buildPairwiseBootstrapSupplement(experimentDir) {
  const verified = verifyCollectionLock(experimentDir);
  const {manifest, matrix, identity} = verified;
  const summaryState = primarySummaryState(experimentDir, manifest);
  const {summary} = summaryState;
  const probeRoleByCase = new Map(identity.cases.map((entry) => [entry.case_id, entry.probe_role]));
  // Preserve the frozen manifest order: the seeded bootstrap maps random
  // indices to this exact case ordering.
  const primaryCaseIds = manifest.cases
    .map((entry) => entry.case_id)
    .filter((caseId) => probeRoleByCase.get(caseId) === "target");
  assert(primaryCaseIds.length === 5, `expected five target cases, received ${primaryCaseIds.length}`);
  assert(Array.isArray(summary.pairwise_system_reliability)
    && summary.pairwise_system_reliability.length === 3, "primary summary must contain three named system pairs");

  const pairs = summary.pairwise_system_reliability.map((summaryPair) => {
    assert(Array.isArray(summaryPair.systems) && summaryPair.systems.length === 2, "invalid named system pair");
    const [left, right] = summaryPair.systems;
    assert(matrix.models[left] && matrix.models[right], `unknown system in named pair: ${left}, ${right}`);
    const providers = [matrix.models[left].provider, matrix.models[right].provider];
    const providerComparison = providers[0] === providers[1] ? "within_provider" : "cross_provider";
    assert(sameJson(summaryPair.providers, providers), `provider mismatch for ${left}--${right}`);
    assert(summaryPair.provider_comparison === providerComparison, `provider relation mismatch for ${left}--${right}`);

    const caseUnits = primaryCaseIds.map((caseId) => CUE_NAMES.map((cue) => [
      summary.model_case_cue_medians?.[left]?.[caseId]?.[cue] ?? null,
      summary.model_case_cue_medians?.[right]?.[caseId]?.[cue] ?? null
    ]));
    const observed = summarizeReliability(caseUnits.flat());
    const availability = availabilityAgreement(caseUnits.flat());
    assert(sameJson(observed, summaryPair.aggregate), `point estimate mismatch for ${left}--${right}`);
    assert(sameJson(availability, summaryPair.availability), `availability mismatch for ${left}--${right}`);
    const completeUnits = completeUnitCount(caseUnits);

    return {
      systems: [left, right],
      model_ids: [matrix.models[left].model_id, matrix.models[right].model_id],
      providers,
      provider_comparison: providerComparison,
      target_case_count: primaryCaseIds.length,
      cues_per_case: CUE_NAMES.length,
      scheduled_case_cue_units: primaryCaseIds.length * CUE_NAMES.length,
      complete_paired_units: completeUnits,
      complete_paired_unit_fraction: completeUnits / (primaryCaseIds.length * CUE_NAMES.length),
      observed,
      availability,
      bootstrap_95: dossierBootstrap(
        caseUnits,
        BOOTSTRAP_REPETITIONS,
        CROSS_SYSTEM_BOOTSTRAP_SEED
      )
    };
  });

  return {
    schema_version: "1.0.0",
    artifact_kind: "preregistered_reporting_addendum",
    dataset_version: manifest.dataset_version,
    status: "complete",
    purpose: "Complete the frozen specification's omitted dossier-clustered bootstrap intervals for all three named system-pair descriptions without changing the frozen analyzer or primary summary.",
    preregistered_scope: {
      specification: "STATISTICAL_ANALYSIS.md, Bootstrap intervals and Direct agreement sections",
      repetitions: BOOTSTRAP_REPETITIONS,
      seed: CROSS_SYSTEM_BOOTSTRAP_SEED,
      resampling_unit: "target dossier",
      carried_observations: "all six case-cue units and both named system medians",
      target_case_ids: primaryCaseIds,
      positive_identification_anchor_excluded: true
    },
    interpretation_boundary: [
      "Intervals are descriptive resampling-sensitivity summaries, not population confidence intervals.",
      "Each cross-provider pair has only twelve complete case-cue units because a three-run median is null when any repetition is invalid.",
      "The two cross-provider pairs share the same Anthropic system and are not independent replications.",
      "Named pair comparisons do not estimate causal provider or generation effects."
    ],
    provenance: commonProvenance(experimentDir, verified, summaryState),
    pairs
  };
}

const uniqueArgmax = (distribution, location) => {
  const values = STATUS_LABELS.map((label) => distribution[label]);
  assert(values.every(finiteProbability), `${location} contains an invalid status probability`);
  const maximum = Math.max(...values);
  const winners = STATUS_LABELS.filter((label) => distribution[label] === maximum);
  assert(winners.length === 1, `${location} does not have a unique argmax`);
  return winners[0];
};

const summarizeStatusRecords = (records, location) => {
  const argmaxCounts = Object.fromEntries(STATUS_LABELS.map((label) => [label, 0]));
  const sums = Object.fromEntries(STATUS_LABELS.map((label) => [label, 0]));
  for (const record of records) {
    for (const label of STATUS_LABELS) sums[label] += record.distribution[label];
    argmaxCounts[record.argmax] += 1;
  }
  return {
    valid_analysis_count: records.length,
    mean_status_probability: Object.fromEntries(STATUS_LABELS.map((label) => [
      label,
      records.length ? sums[label] / records.length : null
    ])),
    argmax_counts: argmaxCounts,
    unique_argmax_labels_present: STATUS_LABELS.filter((label) => argmaxCounts[label] > 0),
    source_runs: records.map((record) => record.run)
  };
};

export function buildCaseStatusDescriptives(experimentDir) {
  const verified = verifyCollectionLock(experimentDir);
  const {manifest, matrix, identity} = verified;
  const summaryState = primarySummaryState(experimentDir, manifest);
  const {summary} = summaryState;
  const checksumState = verifyCollectionOutputChecksums(experimentDir, manifest.dataset_version);
  assert(checksumState.recorded_paths.size === EXPECTED_RAW_RECORDS,
    `expected ${EXPECTED_RAW_RECORDS} checksum-bound raw files, received ${checksumState.recorded_paths.size}`);
  assert(summary.collection_integrity?.scheduled_slot_status_counts?.analysis?.valid === EXPECTED_VALID_ANALYSES,
    `primary summary does not report ${EXPECTED_VALID_ANALYSES} valid analyses`);
  assert(summary.collection_integrity?.unexpected_scheduled_artifacts?.length === 0,
    "primary summary reports unexpected scheduled artifacts");

  const summarySlots = new Map();
  for (const record of summary.collection_integrity?.slots ?? []) {
    assert(!summarySlots.has(record.sequence), `duplicate primary-summary sequence ${record.sequence}`);
    summarySlots.set(record.sequence, record);
  }
  assert(summarySlots.size === matrix.schedule.length, "primary-summary schedule coverage mismatch");
  const dossierByCase = new Map(manifest.cases.map((entry) => [
    entry.case_id,
    readJson(path.join(experimentDir, "data", entry.file), `dossier ${entry.case_id}`)
  ]));

  const parsedRecords = [];
  for (const slot of matrix.schedule) {
    const summarySlot = summarySlots.get(slot.sequence);
    assert(summarySlot, `missing primary-summary sequence ${slot.sequence}`);
    for (const key of ["task", "model", "case_id", "run"]) {
      assert(summarySlot[key] === slot[key], `primary-summary ${key} mismatch at sequence ${slot.sequence}`);
    }
    if (slot.task !== "analysis" || summarySlot.status !== "valid") continue;
    const paths = scheduledSlotPaths(experimentDir, manifest, slot);
    assert(summarySlot.response_file === path.basename(paths.response),
      `primary-summary response filename mismatch at sequence ${slot.sequence}`);
    const parsed = parseAndValidateResponse({
      task: "analysis",
      expectedCase: slot.case_id,
      dossier: dossierByCase.get(slot.case_id),
      response: fs.readFileSync(paths.response, "utf8")
    });
    const distribution = Object.fromEntries(STATUS_LABELS.map((label) => [
      label,
      parsed.status_distribution[label]
    ]));
    parsedRecords.push({
      sequence: slot.sequence,
      model: slot.model,
      case_id: slot.case_id,
      run: slot.run,
      distribution,
      argmax: uniqueArgmax(distribution, `analysis sequence ${slot.sequence}`)
    });
  }
  assert(parsedRecords.length === EXPECTED_VALID_ANALYSES,
    `strict validation produced ${parsedRecords.length}/${EXPECTED_VALID_ANALYSES} expected analyses`);

  const modelLabels = Object.keys(matrix.models);
  const identityByCase = new Map(identity.cases.map((entry) => [entry.case_id, entry]));
  const cases = manifest.cases.map((manifestEntry) => {
    const caseId = manifestEntry.case_id;
    const identityEntry = identityByCase.get(caseId);
    assert(identityEntry, `identity key lacks ${caseId}`);
    const caseRecords = parsedRecords.filter((record) => record.case_id === caseId);
    const pooled = summarizeStatusRecords(caseRecords, `case ${caseId}`);
    const modalCount = Math.max(...Object.values(pooled.argmax_counts));
    const modalLabels = STATUS_LABELS.filter((label) => pooled.argmax_counts[label] === modalCount);
    const unanimous = caseRecords.length > 0 && modalLabels.length === 1 && modalCount === caseRecords.length;
    return {
      case_id: caseId,
      identity: {
        composer: identityEntry.composer,
        work: identityEntry.work,
        movement: identityEntry.movement,
        candidate_measure: identityEntry.candidate_measure
      },
      corpus_role: identityEntry.role,
      probe_role: identityEntry.probe_role,
      by_system: Object.fromEntries(modelLabels.map((model) => [model,
        summarizeStatusRecords(
          caseRecords.filter((record) => record.model === model),
          `case ${caseId}, system ${model}`
        )
      ])),
      pooled: {
        ...pooled,
        argmax_consistency: {
          unanimous,
          consensus_label: unanimous ? modalLabels[0] : null,
          matching_count: unanimous ? modalCount : null,
          valid_analysis_count: caseRecords.length,
          matching_fraction: unanimous ? 1 : null
        }
      }
    };
  });

  return {
    schema_version: "1.0.0",
    artifact_kind: "post_hoc_descriptive",
    dataset_version: manifest.dataset_version,
    status: "complete",
    purpose: "Tabulate case-by-system status probabilities and argmax patterns from only the strictly valid frozen analysis responses.",
    interpretation_boundary: [
      "This table was specified after outcomes were available and is descriptive only.",
      "Corpus roles are design labels, not music-theoretical ground truth or an accuracy reference.",
      "Means condition on strictly valid responses, so system-case cells with invalid responses have smaller n.",
      "Pooled means and counts weight each valid run equally, are system/provider-unbalanced, and change composition where Anthropic responses are invalid.",
      "Status probabilities are secondary model outputs and do not validate the investigator-authored rubric."
    ],
    provenance: {
      ...commonProvenance(experimentDir, verified, summaryState),
      collection_output_checksum_manifest_sha256: checksumState.checksum_manifest_sha256,
      collection_output_record_count: checksumState.recorded_paths.size,
      strictly_valid_analysis_count: parsedRecords.length,
      invalid_analysis_responses_parsed: 0
    },
    status_labels: [...STATUS_LABELS],
    systems: Object.fromEntries(modelLabels.map((model) => [model, {
      provider: matrix.models[model].provider,
      model_id: matrix.models[model].model_id,
      generation_role: matrix.models[model].generation_role
    }])),
    cases
  };
}

export function buildReportingAddenda(experimentDir) {
  return {
    pairwiseBootstrap: buildPairwiseBootstrapSupplement(experimentDir),
    caseStatus: buildCaseStatusDescriptives(experimentDir)
  };
}

export function writeReportingAddenda(experimentDir, artifacts) {
  const datasetVersion = artifacts.pairwiseBootstrap.dataset_version;
  assert(artifacts.caseStatus.dataset_version === datasetVersion, "reporting-addendum dataset mismatch");
  const resultDir = path.join(experimentDir, "results", datasetVersion);
  fs.mkdirSync(resultDir, {recursive: true});
  const written = {};
  for (const [kind, filename] of Object.entries(REPORTING_ADDENDUM_FILES)) {
    const target = path.join(resultDir, filename);
    const body = jsonBody(artifacts[kind]);
    if (fs.existsSync(target)) {
      if (fs.readFileSync(target, "utf8") !== body) {
        throw new Error(`refusing to overwrite a different reporting addendum: ${target}`);
      }
    } else {
      fs.writeFileSync(target, body, {flag: "wx"});
    }
    written[kind] = target;
  }
  return written;
}
