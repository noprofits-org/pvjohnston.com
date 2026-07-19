import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {execFileSync} from "node:child_process";

import {
  availabilityAgreement,
  completeOrdinalMedian,
  directAgreement,
  dossierBootstrap,
  summarizeReliability
} from "./reliability.mjs";
import {
  hashFile,
  verifyCollectionLock
} from "./collection-integrity.mjs";
import {verifyCollectionOutputChecksums} from "./identification-adjudication-packet.mjs";
import {inspectScheduledBundle} from "./scheduled-bundle-integrity.mjs";
import {
  countWords,
  parseAndValidateResponse
} from "./response-validator.mjs";

export const VALIDATOR_CONTRACT_SENSITIVITY_STATUS = "post_hoc_not_preregistered";
export const VALIDATOR_CONTRACT_SENSITIVITY_FILE = "validator-contract-sensitivity.json";
export const EXPECTED_RAW_CHECKSUM_RECORDS = 540;
export const EXPECTED_ANALYSIS_INVOCATIONS = 54;

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
const IDENTIFICATION_LEVELS = Object.freeze(["L0", "L1", "L2"]);
const RUN_IDS = Object.freeze(["01", "02", "03"]);
const PRIMARY_SUMMARY_RELATIVE = "results/1.0.0/summary.json";
const CHECKSUM_MANIFEST_RELATIVE = "data/provenance/collection-output-sha256.txt";
const IDENTIFICATION_ADJUDICATION_RELATIVE = "data/provenance/identification-adjudication.json";

const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const readJson = (file, label) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${label} is not readable JSON: ${error.message}`);
  }
};
const jsonBody = (value) => `${JSON.stringify(value, null, 2)}\n`;
const resultKey = (model, caseId, run) => `${model}\u0000${caseId}\u0000${run}`;

const numericSummary = (values) => {
  const finite = values.filter((value) => Number.isFinite(value)).sort((left, right) => left - right);
  if (finite.length === 0) return {count: 0, mean: null, median: null, minimum: null, maximum: null};
  const middle = Math.floor(finite.length / 2);
  return {
    count: finite.length,
    mean: finite.reduce((sum, value) => sum + value, 0) / finite.length,
    median: finite.length % 2 ? finite[middle] : (finite[middle - 1] + finite[middle]) / 2,
    minimum: finite[0],
    maximum: finite.at(-1)
  };
};

const extractMachineResult = (response) => {
  if (typeof response !== "string") throw new Error("response must be a string");
  const normalized = response.replace(/\r\n?/g, "\n");
  const blocks = [...normalized.matchAll(/^```json[ \t]*\n([\s\S]*?)\n```[ \t]*$/gm)];
  if (blocks.length !== 1) throw new Error(`expected one JSON block, found ${blocks.length}`);
  let result;
  try {
    result = JSON.parse(blocks[0][1]);
  } catch (error) {
    throw new Error(`invalid JSON result: ${error.message}`);
  }
  return {normalized, block: blocks[0], result};
};

const collectDossierIdentifiers = (dossier) => {
  if (!dossier || typeof dossier !== "object" || !Array.isArray(dossier.windows)) {
    throw new Error("dossier.windows must be an array");
  }
  const measureIds = new Set();
  const directionIds = new Map();
  for (const window of dossier.windows) {
    for (const measure of window.measures ?? []) {
      if (typeof measure.evidence_id !== "string" || measure.evidence_id === "") {
        throw new Error("dossier measure evidence_id must be a nonempty string");
      }
      if (measureIds.has(measure.evidence_id)) {
        throw new Error(`duplicate dossier measure evidence ID: ${measure.evidence_id}`);
      }
      measureIds.add(measure.evidence_id);
      for (const direction of measure.directions ?? []) {
        const id = direction?.direction_id;
        if (typeof id !== "string" || id === "") {
          throw new Error(`dossier direction under ${measure.evidence_id} lacks direction_id`);
        }
        if (directionIds.has(id)) throw new Error(`duplicate dossier direction ID: ${id}`);
        directionIds.set(id, {
          window_id: window.window_id,
          measure_index: measure.measure_index,
          measure_evidence_id: measure.evidence_id,
          direction_type: direction.direction_type,
          value: direction.value
        });
      }
    }
  }
  return {measureIds, directionIds};
};

const dossierWithDirectionEvidenceIds = (dossier) => {
  const {measureIds, directionIds} = collectDossierIdentifiers(dossier);
  const adjusted = structuredClone(dossier);
  const firstWindow = adjusted.windows?.[0];
  if (!firstWindow || !Array.isArray(firstWindow.measures) || firstWindow.measures.length === 0) {
    throw new Error("dossier must have at least one measure");
  }
  for (const id of directionIds.keys()) {
    if (!measureIds.has(id)) firstWindow.measures.push({evidence_id: id});
  }
  return adjusted;
};

/**
 * Validate an analysis response under exactly two post hoc interpretations:
 * a nonempty case_note has no word cap, and genuine dossier direction_id
 * values are accepted alongside measure evidence_id values. The frozen
 * validator enforces every other response rule against an in-memory copy.
 */
export function parseAnalysisWithValidatorContractSensitivity({expectedCase, dossier, response}) {
  const extracted = extractMachineResult(response);
  if (typeof extracted.result?.case_note !== "string" || extracted.result.case_note.trim() === "") {
    throw new Error("result.case_note must be a nonempty string");
  }

  const validationResult = structuredClone(extracted.result);
  validationResult.case_note = "Nonempty post hoc validation placeholder.";
  const replacement = `\`\`\`json\n${JSON.stringify(validationResult, null, 2)}\n\`\`\``;
  const transformedResponse = extracted.normalized.slice(0, extracted.block.index)
    + replacement
    + extracted.normalized.slice(extracted.block.index + extracted.block[0].length);

  parseAndValidateResponse({
    task: "analysis",
    expectedCase,
    dossier: dossierWithDirectionEvidenceIds(dossier),
    response: transformedResponse
  });
  return extracted.result;
}

export function diagnoseOriginalValidatorContractIssues(result, dossier) {
  const issues = [];
  const caseNoteWords = countWords(result?.case_note);
  if (typeof result?.case_note === "string" && result.case_note.trim() !== "" && caseNoteWords > 40) {
    issues.push({
      code: "case_note_exceeds_unstated_frozen_limit",
      location: "result.case_note",
      frozen_maximum_words: 40,
      observed_words: caseNoteWords
    });
  }

  const {measureIds, directionIds} = collectDossierIdentifiers(dossier);
  for (const cue of CUE_NAMES) {
    const ids = result?.cues?.[cue]?.evidence_ids;
    if (!Array.isArray(ids)) continue;
    ids.forEach((id, index) => {
      if (measureIds.has(id) || !directionIds.has(id)) return;
      issues.push({
        code: "genuine_direction_id_outside_frozen_measure_id_allowlist",
        location: `result.cues.${cue}.evidence_ids[${index}]`,
        identifier: id,
        dossier_direction: directionIds.get(id)
      });
    });
  }
  return issues;
}

const inspectAnalysisResponses = (experimentDir, verified, checksumState) => {
  const {manifest, matrix} = verified;
  const dossiers = new Map(manifest.cases.map((entry) => [
    entry.case_id,
    readJson(path.join(experimentDir, "data", entry.file), `dossier ${entry.case_id}`)
  ]));
  const records = [];
  for (const slot of matrix.schedule.filter((entry) => entry.task === "analysis")) {
    const bundle = inspectScheduledBundle(experimentDir, verified, slot);
    if (bundle.state !== "complete") {
      throw new Error(`analysis slot ${slot.sequence} is not a complete scheduled bundle`);
    }
    const responsePath = bundle.outcome === "valid" ? bundle.paths.response : bundle.paths.invalidResponse;
    const relative = path.relative(experimentDir, responsePath).split(path.sep).join("/");
    if (!checksumState.recorded_paths.has(relative)) {
      throw new Error(`analysis response is absent from raw checksums: ${relative}`);
    }
    const response = fs.readFileSync(responsePath, "utf8");
    const dossier = dossiers.get(slot.case_id);
    let strictParsed = null;
    let strictError = null;
    try {
      strictParsed = parseAndValidateResponse({
        task: "analysis",
        expectedCase: slot.case_id,
        dossier,
        response
      });
    } catch (error) {
      strictError = error;
    }
    if (bundle.outcome === "valid" && strictError) {
      throw new Error(`strict-valid response no longer validates: ${path.basename(responsePath)}: ${strictError.message}`);
    }
    if (bundle.outcome === "invalid" && !strictError) {
      throw new Error(`strict-invalid response now validates: ${path.basename(responsePath)}`);
    }

    let sensitivityParsed = null;
    let sensitivityError = null;
    if (bundle.outcome !== "command_failed") {
      try {
        sensitivityParsed = parseAnalysisWithValidatorContractSensitivity({
          expectedCase: slot.case_id,
          dossier,
          response
        });
      } catch (error) {
        sensitivityError = error;
      }
    }
    if (strictParsed && sensitivityError) {
      throw new Error(`sensitivity validator is not a strict superset at ${path.basename(responsePath)}: ${sensitivityError.message}`);
    }
    const rescued = bundle.outcome === "invalid" && sensitivityParsed !== null;
    const originalIssues = strictError
      ? diagnoseOriginalValidatorContractIssues(extractMachineResult(response).result, dossier)
      : [];
    if (rescued && originalIssues.length === 0) {
      throw new Error(`response was rescued without either declared interpretation change: ${path.basename(responsePath)}`);
    }
    records.push({
      sequence: slot.sequence,
      model: slot.model,
      case_id: slot.case_id,
      run: slot.run,
      filename: path.basename(responsePath),
      raw_sha256: hashFile(responsePath),
      strict_status: bundle.outcome,
      frozen_validator_first_error: strictError?.message ?? null,
      sensitivity_status: sensitivityParsed ? "valid" : bundle.outcome === "command_failed" ? "command_failed" : "invalid",
      sensitivity_error: sensitivityError?.message ?? null,
      rescued,
      original_issues: originalIssues,
      parsed: sensitivityParsed
    });
  }
  if (records.length !== EXPECTED_ANALYSIS_INVOCATIONS) {
    throw new Error(`read ${records.length} analysis responses, expected ${EXPECTED_ANALYSIS_INVOCATIONS}`);
  }
  return records;
};

const computeSensitivityMetrics = ({verified, records, primarySummary, adjudication}) => {
  const {manifest, matrix, identity} = verified;
  const caseIds = manifest.cases.map((entry) => entry.case_id);
  const modelLabels = Object.keys(matrix.models);
  const providerByModel = new Map(modelLabels.map((model) => [model, matrix.models[model].provider]));
  const providerLabels = [...new Set(providerByModel.values())];
  const roleByCase = new Map(identity.cases.map((entry) => [entry.case_id, entry.probe_role]));
  const primaryCaseIds = caseIds.filter((caseId) => roleByCase.get(caseId) === "target");
  const anchorCaseIds = caseIds.filter((caseId) => roleByCase.get(caseId) !== "target");
  const validRecords = records.filter((record) => record.sensitivity_status === "valid");
  const analysisResults = new Map(validRecords.map((record) => [
    resultKey(record.model, record.case_id, record.run),
    record.parsed
  ]));
  const scoresFor = (model, caseId, cue) => RUN_IDS.map((run) =>
    analysisResults.get(resultKey(model, caseId, run))?.cues?.[cue]?.score ?? null
  );
  const completeModelData = (model, ids) => ids.every((caseId) => RUN_IDS.every((run) => {
    const parsed = analysisResults.get(resultKey(model, caseId, run));
    return parsed && CUE_NAMES.every((cue) => Number.isInteger(parsed.cues?.[cue]?.score));
  }));
  const medianScoreFor = (model, caseId, cue) => completeOrdinalMedian(scoresFor(model, caseId, cue));
  const providersForModels = (models) => [...new Set(models.map((model) => providerByModel.get(model)))];

  const withinModel = {};
  for (const model of modelLabels) {
    const caseUnits = primaryCaseIds.map((caseId) => CUE_NAMES.map((cue) => scoresFor(model, caseId, cue)));
    const units = caseUnits.flat();
    const anchorUnits = anchorCaseIds.map((caseId) => CUE_NAMES.map((cue) => scoresFor(model, caseId, cue))).flat();
    withinModel[model] = {
      complete_three_run_data: completeModelData(model, primaryCaseIds),
      aggregate: summarizeReliability(units),
      availability: availabilityAgreement(units),
      bootstrap_95: dossierBootstrap(caseUnits, 2000, 1701),
      by_cue: Object.fromEntries(CUE_NAMES.map((cue) => [cue,
        directAgreement(primaryCaseIds.map((caseId) => scoresFor(model, caseId, cue)))
      ])),
      anchor: {
        complete_three_run_data: completeModelData(model, anchorCaseIds),
        aggregate: summarizeReliability(anchorUnits),
        availability: availabilityAgreement(anchorUnits)
      }
    };
  }

  const crossCaseUnits = primaryCaseIds.map((caseId) => CUE_NAMES.map((cue) =>
    modelLabels.map((model) => medianScoreFor(model, caseId, cue))
  ));
  const anchorCrossUnits = anchorCaseIds.map((caseId) => CUE_NAMES.map((cue) =>
    modelLabels.map((model) => medianScoreFor(model, caseId, cue))
  ));
  const crossModel = {
    aggregate: summarizeReliability(crossCaseUnits.flat()),
    availability: availabilityAgreement(crossCaseUnits.flat()),
    bootstrap_95: dossierBootstrap(crossCaseUnits, 2000, 1702),
    by_cue: Object.fromEntries(CUE_NAMES.map((cue) => [cue,
      directAgreement(primaryCaseIds.map((caseId) => modelLabels.map((model) => medianScoreFor(model, caseId, cue))))
    ])),
    anchor: {
      aggregate: summarizeReliability(anchorCrossUnits.flat()),
      availability: availabilityAgreement(anchorCrossUnits.flat())
    }
  };

  const pairwiseSystemReliability = [];
  for (let leftIndex = 0; leftIndex < modelLabels.length; leftIndex += 1) {
    for (let rightIndex = leftIndex + 1; rightIndex < modelLabels.length; rightIndex += 1) {
      const left = modelLabels[leftIndex];
      const right = modelLabels[rightIndex];
      const providers = [providerByModel.get(left), providerByModel.get(right)];
      const primaryUnits = primaryCaseIds.map((caseId) => CUE_NAMES.map((cue) => [
        medianScoreFor(left, caseId, cue),
        medianScoreFor(right, caseId, cue)
      ]));
      const anchorUnits = anchorCaseIds.map((caseId) => CUE_NAMES.map((cue) => [
        medianScoreFor(left, caseId, cue),
        medianScoreFor(right, caseId, cue)
      ]));
      pairwiseSystemReliability.push({
        systems: [left, right],
        providers,
        provider_comparison: providers[0] === providers[1] ? "within_provider" : "cross_provider",
        aggregate: summarizeReliability(primaryUnits.flat()),
        availability: availabilityAgreement(primaryUnits.flat()),
        by_cue: Object.fromEntries(CUE_NAMES.map((cue) => [cue,
          directAgreement(primaryCaseIds.map((caseId) => [
            medianScoreFor(left, caseId, cue),
            medianScoreFor(right, caseId, cue)
          ]))
        ])),
        anchor: {
          aggregate: summarizeReliability(anchorUnits.flat()),
          availability: availabilityAgreement(anchorUnits.flat())
        }
      });
    }
  }

  const scheduledAnalysis = records.length;
  const scheduledCueCells = scheduledAnalysis * CUE_NAMES.length;
  let nonNullCueCells = 0;
  for (const record of validRecords) {
    for (const cue of CUE_NAMES) if (Number.isInteger(record.parsed.cues?.[cue]?.score)) nonNullCueCells += 1;
  }
  const repeatableModels = modelLabels.filter((model) => {
    const metric = withinModel[model].aggregate;
    return withinModel[model].complete_three_run_data
      && metric.mean_absolute_difference !== null
      && metric.mean_absolute_difference <= 0.5
      && metric.within_one_agreement >= 0.9
      && metric.ordinal_krippendorff_alpha !== null
      && metric.ordinal_krippendorff_alpha >= 0.67;
  });
  const repeatableProviders = providersForModels(repeatableModels);
  const dispersion = Object.fromEntries(CUE_NAMES.map((cue) => [cue,
    Object.fromEntries(modelLabels.map((model) => {
      const values = primaryCaseIds.map((caseId) => medianScoreFor(model, caseId, cue)).filter((value) => value !== null);
      return [model, values.length ? {
        minimum: Math.min(...values),
        maximum: Math.max(...values),
        span: Math.max(...values) - Math.min(...values)
      } : null];
    }))
  ]));
  const dispersionQualifiers = Object.fromEntries(CUE_NAMES.map((cue) => {
    const systems = repeatableModels.filter((model) => dispersion[cue][model]?.span >= 2);
    return [cue, {systems, providers: providersForModels(systems)}];
  }));
  const nondegenerateCues = CUE_NAMES.filter((cue) =>
    dispersionQualifiers[cue].systems.length >= 2
      && dispersionQualifiers[cue].providers.length === providerLabels.length
  );
  const modelCaseValidRepetitions = Object.fromEntries(modelLabels.map((model) => [model,
    Object.fromEntries(caseIds.map((caseId) => [caseId,
      RUN_IDS.filter((run) => analysisResults.has(resultKey(model, caseId, run))).length
    ]))
  ]));
  const modelCaseCueMedians = Object.fromEntries(modelLabels.map((model) => [model,
    Object.fromEntries(caseIds.map((caseId) => [caseId,
      Object.fromEntries(CUE_NAMES.map((cue) => [cue, medianScoreFor(model, caseId, cue)]))
    ]))
  ]));

  const distributionSummary = (selected) => Object.fromEntries(STATUS_LABELS.map((label) => [label,
    numericSummary(selected.map((record) => record.parsed.status_distribution[label]))
  ]));
  const statusDistribution = {
    overall: distributionSummary(validRecords),
    by_model: Object.fromEntries(modelLabels.map((model) => [model,
      distributionSummary(validRecords.filter((record) => record.model === model))
    ]))
  };
  const suspectedRecognition = validRecords.map((record) => ({
    model: record.model,
    case_id: record.case_id,
    run: record.run,
    level: record.parsed.suspected_recognition.level,
    confidence: record.parsed.suspected_recognition.confidence,
    target_case: primaryCaseIds.includes(record.case_id)
  }));
  const workLevelEvents = suspectedRecognition.filter((entry) => entry.target_case && entry.level === "work");
  const workLevelRecognitionOnTarget = workLevelEvents.length > 0;

  if (adjudication?.status !== "complete" || !Array.isArray(adjudication.judgments)) {
    throw new Error("complete primary identification adjudication is required for L2-stratified sensitivity metrics");
  }
  const adjudicationByOutput = new Map();
  for (const judgment of adjudication.judgments) {
    if (adjudicationByOutput.has(judgment.output)) {
      throw new Error(`duplicate identification adjudication: ${judgment.output}`);
    }
    if (!IDENTIFICATION_LEVELS.includes(judgment.level)) {
      throw new Error(`invalid identification level: ${judgment.level}`);
    }
    adjudicationByOutput.set(judgment.output, judgment);
  }
  const l2Categories = ["repeated_l2", "isolated_l2", "no_l2"];
  const l2Entries = Object.fromEntries(l2Categories.map((category) => [category, []]));
  for (const model of modelLabels) for (const caseId of primaryCaseIds) {
    const levels = RUN_IDS.map((run) => {
      const output = `${model}__${manifest.evidence_condition}__${caseId}__run-${run}.md`;
      return adjudicationByOutput.get(output)?.level ?? null;
    });
    if (!levels.every((level) => IDENTIFICATION_LEVELS.includes(level))) {
      throw new Error(`incomplete identification levels for ${model} ${caseId}`);
    }
    const l2Count = levels.filter((level) => level === "L2").length;
    const category = l2Count >= 2 ? "repeated_l2" : l2Count === 1 ? "isolated_l2" : "no_l2";
    const units = CUE_NAMES.map((cue) => scoresFor(model, caseId, cue));
    l2Entries[category].push({model, case_id: caseId, l2_count: l2Count, units});
  }
  const analysisScoreRepeatabilityByL2Category = Object.fromEntries(l2Categories.map((category) => {
    const selected = l2Entries[category];
    const pooledUnits = selected.flatMap((entry) => entry.units);
    return [category, {
      model_case_pair_count: selected.length,
      case_cue_unit_count: pooledUnits.length,
      pooled_score_repeatability: directAgreement(pooledUnits),
      pooled_score_availability: availabilityAgreement(pooledUnits),
      model_case_pairs: selected.map(({units, ...entry}) => ({
        ...entry,
        score_repeatability: directAgreement(units),
        score_availability: availabilityAgreement(units)
      }))
    }];
  }));
  const identificationGate = primarySummary.preliminary_gates.identification_gate;
  const unexpectedArtifacts = primarySummary.collection_integrity.unexpected_scheduled_artifacts;
  const scheduledIdentification = primarySummary.identification.scheduled;
  const validIdentification = primarySummary.identification.valid_outputs;
  const preliminaryGates = {
    output_gate: validRecords.length === scheduledAnalysis
      && validIdentification === scheduledIdentification
      && nonNullCueCells === scheduledCueCells
      && unexpectedArtifacts.length === 0,
    repeatability_gate: repeatableModels.length >= 2
      && repeatableProviders.length === providerLabels.length,
    dispersion_gate: nondegenerateCues.length >= 4,
    identification_gate: identificationGate,
    analysis_recognition_gate: !workLevelRecognitionOnTarget
  };

  return {
    validity_and_completeness: {
      scope: "analysis task only, matching the frozen primary analyzer",
      scheduled_analysis_invocations: scheduledAnalysis,
      valid_analysis_invocations: validRecords.length,
      output_validity_rate: scheduledAnalysis ? validRecords.length / scheduledAnalysis : null,
      scheduled_cue_cells: scheduledCueCells,
      non_null_cue_cells: nonNullCueCells,
      cue_completeness_rate: scheduledCueCells ? nonNullCueCells / scheduledCueCells : null
    },
    within_model: withinModel,
    cross_model: crossModel,
    pairwise_system_reliability: pairwiseSystemReliability,
    model_case_cue_medians: modelCaseCueMedians,
    model_case_valid_repetitions: modelCaseValidRepetitions,
    cue_dispersion: dispersion,
    cue_dispersion_qualifiers: dispersionQualifiers,
    repeatable_models: repeatableModels,
    repeatable_providers: repeatableProviders,
    nondegenerate_cues: nondegenerateCues,
    status_distribution: statusDistribution,
    suspected_recognition: suspectedRecognition,
    analysis_score_repeatability_by_l2_category: analysisScoreRepeatabilityByL2Category,
    analysis_recognition: {
      work_level_recognition_on_target: workLevelRecognitionOnTarget,
      work_level_events: workLevelEvents
    },
    preliminary_gates: preliminaryGates,
    automatic_expansion_gate: Object.values(preliminaryGates).every((value) => value === true)
  };
};

const strictReferenceFromPrimary = (summary) => ({
  source: PRIMARY_SUMMARY_RELATIVE,
  validity_and_completeness: {
    scope: "analysis task only, matching the frozen primary analyzer",
    scheduled_analysis_invocations: summary.scheduled_analysis_invocations,
    valid_analysis_invocations: summary.valid_analysis_invocations,
    output_validity_rate: summary.output_validity_rate,
    scheduled_cue_cells: summary.scheduled_cue_cells,
    non_null_cue_cells: summary.non_null_cue_cells,
    cue_completeness_rate: summary.cue_completeness_rate
  },
  within_model: summary.within_model,
  cross_model: summary.cross_model,
  pairwise_system_reliability: summary.pairwise_system_reliability,
  model_case_cue_medians: summary.model_case_cue_medians,
  model_case_valid_repetitions: summary.model_case_valid_repetitions,
  cue_dispersion: summary.cue_dispersion,
  cue_dispersion_qualifiers: summary.cue_dispersion_qualifiers,
  repeatable_models: summary.repeatable_models,
  repeatable_providers: summary.repeatable_providers,
  nondegenerate_cues: summary.nondegenerate_cues,
  status_distribution: summary.status_distribution,
  suspected_recognition: summary.suspected_recognition,
  analysis_score_repeatability_by_l2_category:
    summary.identification.analysis_score_repeatability_by_l2_category,
  analysis_recognition: {
    work_level_recognition_on_target: summary.work_level_recognition_on_target,
    work_level_events: summary.suspected_recognition.filter((entry) => entry.target_case && entry.level === "work")
  },
  preliminary_gates: summary.preliminary_gates,
  automatic_expansion_gate: summary.automatic_expansion_gate
});

const reliabilityComparison = (strict, sensitivity) => ({
  validity_and_completeness: {
    valid_analysis_invocations: {
      strict: strict.validity_and_completeness.valid_analysis_invocations,
      sensitivity: sensitivity.validity_and_completeness.valid_analysis_invocations,
      change: sensitivity.validity_and_completeness.valid_analysis_invocations
        - strict.validity_and_completeness.valid_analysis_invocations
    },
    output_validity_rate: {
      strict: strict.validity_and_completeness.output_validity_rate,
      sensitivity: sensitivity.validity_and_completeness.output_validity_rate,
      change: sensitivity.validity_and_completeness.output_validity_rate
        - strict.validity_and_completeness.output_validity_rate
    },
    non_null_cue_cells: {
      strict: strict.validity_and_completeness.non_null_cue_cells,
      sensitivity: sensitivity.validity_and_completeness.non_null_cue_cells,
      change: sensitivity.validity_and_completeness.non_null_cue_cells
        - strict.validity_and_completeness.non_null_cue_cells
    },
    cue_completeness_rate: {
      strict: strict.validity_and_completeness.cue_completeness_rate,
      sensitivity: sensitivity.validity_and_completeness.cue_completeness_rate,
      change: sensitivity.validity_and_completeness.cue_completeness_rate
        - strict.validity_and_completeness.cue_completeness_rate
    }
  },
  within_system: Object.fromEntries(Object.keys(sensitivity.within_model).map((model) => [model, {
    complete_three_run_data: {
      strict: strict.within_model[model].complete_three_run_data,
      sensitivity: sensitivity.within_model[model].complete_three_run_data
    },
    aggregate: {
      strict: strict.within_model[model].aggregate,
      sensitivity: sensitivity.within_model[model].aggregate
    },
    availability: {
      strict: strict.within_model[model].availability,
      sensitivity: sensitivity.within_model[model].availability
    }
  }])),
  named_system_pairs: sensitivity.pairwise_system_reliability.map((entry) => {
    const prior = strict.pairwise_system_reliability.find((candidate) =>
      JSON.stringify(candidate.systems) === JSON.stringify(entry.systems)
    );
    if (!prior) throw new Error(`strict summary lacks named pair ${entry.systems.join(" / ")}`);
    return {
      systems: entry.systems,
      providers: entry.providers,
      aggregate: {strict: prior.aggregate, sensitivity: entry.aggregate},
      availability: {strict: prior.availability, sensitivity: entry.availability}
    };
  }),
  pooled_cross_system: {
    aggregate: {strict: strict.cross_model.aggregate, sensitivity: sensitivity.cross_model.aggregate},
    availability: {strict: strict.cross_model.availability, sensitivity: sensitivity.cross_model.availability}
  },
  repeatability_qualifiers: {
    repeatable_models: {strict: strict.repeatable_models, sensitivity: sensitivity.repeatable_models},
    repeatable_providers: {strict: strict.repeatable_providers, sensitivity: sensitivity.repeatable_providers}
  },
  dispersion: {
    nondegenerate_cues: {strict: strict.nondegenerate_cues, sensitivity: sensitivity.nondegenerate_cues},
    qualifiers: {strict: strict.cue_dispersion_qualifiers, sensitivity: sensitivity.cue_dispersion_qualifiers}
  },
  work_level_recognition_on_target: {
    strict: strict.analysis_recognition.work_level_recognition_on_target,
    sensitivity: sensitivity.analysis_recognition.work_level_recognition_on_target
  },
  status_distribution: {
    strict: strict.status_distribution,
    sensitivity: sensitivity.status_distribution
  },
  suspected_recognition: {
    strict_output_count: strict.suspected_recognition.length,
    sensitivity_output_count: sensitivity.suspected_recognition.length,
    strict_level_counts: Object.fromEntries(["none", "style", "composer", "work"].map((level) => [level,
      strict.suspected_recognition.filter((entry) => entry.level === level).length
    ])),
    sensitivity_level_counts: Object.fromEntries(["none", "style", "composer", "work"].map((level) => [level,
      sensitivity.suspected_recognition.filter((entry) => entry.level === level).length
    ]))
  },
  analysis_score_repeatability_by_l2_category: {
    strict: strict.analysis_score_repeatability_by_l2_category,
    sensitivity: sensitivity.analysis_score_repeatability_by_l2_category
  },
  preliminary_gates: {
    strict: strict.preliminary_gates,
    sensitivity: sensitivity.preliminary_gates
  },
  automatic_expansion_gate: {
    strict: strict.automatic_expansion_gate,
    sensitivity: sensitivity.automatic_expansion_gate
  }
});

export function buildValidatorContractSensitivity(experimentDir) {
  const root = path.resolve(experimentDir);

  // Verification order is deliberate: no raw response is read by this
  // analysis until the collection lock and all 540 raw hashes pass.
  const verified = verifyCollectionLock(root);
  const checksumBefore = verifyCollectionOutputChecksums(root, verified.manifest.dataset_version);
  if (checksumBefore.recorded_paths.size !== EXPECTED_RAW_CHECKSUM_RECORDS) {
    throw new Error(`raw checksum coverage is ${checksumBefore.recorded_paths.size}, expected ${EXPECTED_RAW_CHECKSUM_RECORDS}`);
  }

  const primarySummaryPath = path.join(root, PRIMARY_SUMMARY_RELATIVE);
  const lockPath = path.join(root, "collection-lock.json");
  const lockHashBefore = hashFile(lockPath);
  const adjudicationPath = path.join(root, IDENTIFICATION_ADJUDICATION_RELATIVE);
  const adjudicationHashBefore = hashFile(adjudicationPath);
  const primaryAdjudication = readJson(adjudicationPath, "primary identification adjudication");
  const primaryBefore = fs.readFileSync(primarySummaryPath);
  const primarySummary = JSON.parse(primaryBefore);
  const primaryHashBefore = sha256(primaryBefore);
  const analyzerPath = path.join(root, "scripts", "analyze-results.mjs");
  const strictRecomputed = execFileSync(process.execPath, [analyzerPath, root], {
    maxBuffer: 32 * 1024 * 1024
  });
  const strictRecomputedHash = sha256(strictRecomputed);
  if (strictRecomputedHash !== primaryHashBefore) {
    throw new Error("primary summary differs from a fresh frozen-analyzer replay");
  }

  const records = inspectAnalysisResponses(root, verified, checksumBefore);
  const strictReference = strictReferenceFromPrimary(primarySummary);
  const sensitivity = computeSensitivityMetrics({
    verified,
    records,
    primarySummary,
    adjudication: primaryAdjudication
  });
  const rescued = records.filter((record) => record.rescued).map(({parsed, sensitivity_error: ignored, ...record}) => record);
  const remainingInvalid = records.filter((record) => record.sensitivity_status !== "valid")
    .map(({parsed, ...record}) => record);

  const checksumAfter = verifyCollectionOutputChecksums(root, verified.manifest.dataset_version);
  if (checksumAfter.checksum_manifest_sha256 !== checksumBefore.checksum_manifest_sha256
      || checksumAfter.recorded_paths.size !== checksumBefore.recorded_paths.size) {
    throw new Error("raw collection checksum state changed during sensitivity analysis");
  }
  const primaryAfter = fs.readFileSync(primarySummaryPath);
  const primaryHashAfter = sha256(primaryAfter);
  if (primaryHashAfter !== primaryHashBefore) {
    throw new Error("primary summary changed during sensitivity analysis");
  }
  const lockHashAfter = hashFile(lockPath);
  if (lockHashAfter !== lockHashBefore) {
    throw new Error("collection lock changed during sensitivity analysis");
  }
  const adjudicationHashAfter = hashFile(adjudicationPath);
  if (adjudicationHashAfter !== adjudicationHashBefore) {
    throw new Error("primary identification adjudication changed during sensitivity analysis");
  }
  const {
    analysis_score_repeatability_by_l2_category: strictAnalysisScoreRepeatabilityByL2Category,
    ...inheritedIdentificationSummary
  } = primarySummary.identification;

  const result = {
    schema_version: "1.0.0",
    status: VALIDATOR_CONTRACT_SENSITIVITY_STATUS,
    analysis_kind: "validator_contract_sensitivity",
    disclosure: {
      preregistered: false,
      primary_analysis_replaced: false,
      raw_bytes_changed: false,
      locked_files_changed: false,
      attempt_claims_changed: false,
      primary_summary_changed: false,
      primary_identification_adjudication_changed: false,
      outputs_repaired: false,
      calls_retried: false,
      interpretation: "This analysis changes validation interpretation only. Rescued raw responses remain invalid in the preregistered primary analysis.",
      implementation: "The frozen validator checks every unchanged rule against a temporary in-memory validation copy; reported scores and fields come from the original raw response bytes."
    },
    interpretation_changes: [
      {
        field: "result.case_note",
        frozen_interpretation: "nonempty string with an enforced maximum of 40 words",
        sensitivity_interpretation: "nonempty string with no word cap because the frozen model-facing prompt states the 40-word cap only for cue reasons"
      },
      {
        field: "result.cues.*.evidence_ids",
        frozen_interpretation: "only measure-level evidence_id values are accepted",
        sensitivity_interpretation: "measure-level evidence_id values and genuine direction_id values present in the same frozen dossier are accepted; event_id and unknown identifiers remain invalid"
      }
    ],
    integrity: {
      verification_order: [
        "collection lock",
        "all raw scheduled-output checksums",
        "strict primary-summary replay (the frozen analyzer reads responses only after the preceding checksum verification)",
        "explicit inspection of all 54 original analysis responses",
        "post-analysis raw checksum replay"
      ],
      collection_lock_verified: true,
      collection_lock_sha256_before: lockHashBefore,
      collection_lock_sha256_after: lockHashAfter,
      locked_file_count: Object.keys(verified.lock.files).length,
      raw_checksum_manifest: CHECKSUM_MANIFEST_RELATIVE,
      raw_checksum_manifest_sha256_before: checksumBefore.checksum_manifest_sha256,
      raw_checksum_manifest_sha256_after: checksumAfter.checksum_manifest_sha256,
      raw_checksum_record_count: checksumBefore.recorded_paths.size,
      all_raw_checksums_verified_before_response_read: true,
      all_raw_checksums_verified_after_analysis: true,
      raw_bytes_unchanged: true,
      primary_summary: PRIMARY_SUMMARY_RELATIVE,
      primary_summary_sha256_before: primaryHashBefore,
      primary_summary_sha256_after: primaryHashAfter,
      strict_analyzer_recomputed_sha256: strictRecomputedHash,
      strict_summary_unchanged: primaryHashBefore === primaryHashAfter
        && primaryHashBefore === strictRecomputedHash,
      primary_identification_adjudication_sha256_before: adjudicationHashBefore,
      primary_identification_adjudication_sha256_after: adjudicationHashAfter,
      primary_identification_adjudication_unchanged: adjudicationHashBefore === adjudicationHashAfter,
      source_file_sha256: {
        "scripts/analyze-results.mjs": hashFile(analyzerPath),
        "scripts/lib/reliability.mjs": hashFile(path.join(root, "scripts", "lib", "reliability.mjs")),
        "scripts/lib/response-validator.mjs": hashFile(path.join(root, "scripts", "lib", "response-validator.mjs")),
        "scripts/analyze-validator-contract-sensitivity.mjs": hashFile(path.join(root, "scripts", "analyze-validator-contract-sensitivity.mjs")),
        "scripts/lib/validator-contract-sensitivity.mjs": hashFile(path.join(root, "scripts", "lib", "validator-contract-sensitivity.mjs")),
        "scripts/test-validator-contract-sensitivity.mjs": hashFile(path.join(root, "scripts", "test-validator-contract-sensitivity.mjs")),
        [IDENTIFICATION_ADJUDICATION_RELATIVE]: hashFile(path.join(root, IDENTIFICATION_ADJUDICATION_RELATIVE))
      }
    },
    response_accounting: {
      analysis_responses_read: records.length,
      strict_valid: records.filter((record) => record.strict_status === "valid").length,
      strict_invalid: records.filter((record) => record.strict_status === "invalid").length,
      strict_command_failed: records.filter((record) => record.strict_status === "command_failed").length,
      sensitivity_valid: records.filter((record) => record.sensitivity_status === "valid").length,
      rescued_count: rescued.length,
      remaining_invalid_count: remainingInvalid.length,
      identification_scheduled_inherited: primarySummary.identification.scheduled,
      identification_valid_inherited: primarySummary.identification.valid_outputs,
      all_tasks_scheduled: records.length + primarySummary.identification.scheduled,
      all_tasks_strict_valid: records.filter((record) => record.strict_status === "valid").length
        + primarySummary.identification.valid_outputs,
      all_tasks_sensitivity_valid: records.filter((record) => record.sensitivity_status === "valid").length
        + primarySummary.identification.valid_outputs
    },
    rescued_outputs: rescued,
    remaining_invalid_outputs: remainingInvalid,
    bootstrap: {
      method: "existing dossierBootstrap reliability library",
      replicates: 2000,
      within_system_seed: 1701,
      pooled_cross_system_seed: 1702,
      named_pair_bootstrap: "not computed, matching the frozen analyzer",
      frozen_manifest_case_order: verified.manifest.cases.map((entry) => entry.case_id),
      primary_target_case_order: verified.manifest.cases
        .map((entry) => entry.case_id)
        .filter((caseId) => verified.identity.cases.find((entry) => entry.case_id === caseId).probe_role === "target"),
      anchor_case_order: verified.manifest.cases
        .map((entry) => entry.case_id)
        .filter((caseId) => verified.identity.cases.find((entry) => entry.case_id === caseId).probe_role !== "target")
    },
    identification: {
      treatment: "judgments, counts, confidence summaries, recoverability findings, and gate inherited without reinterpretation; analysis-score strata recomputed",
      source: PRIMARY_SUMMARY_RELATIVE,
      source_sha256: primaryHashBefore,
      inherited_summary: inheritedIdentificationSummary,
      analysis_score_repeatability_by_l2_category: {
        strict_reference: strictAnalysisScoreRepeatabilityByL2Category,
        sensitivity: sensitivity.analysis_score_repeatability_by_l2_category
      }
    },
    strict_reference: strictReference,
    sensitivity,
    metric_changes: reliabilityComparison(strictReference, sensitivity)
  };
  return {result, body: jsonBody(result)};
}

export function writeValidatorContractSensitivity(experimentDir, built, options = {}) {
  const target = options.outputFile ?? path.join(
    path.resolve(experimentDir),
    "results",
    "1.0.0",
    VALIDATOR_CONTRACT_SENSITIVITY_FILE
  );
  const body = built?.body ?? jsonBody(built?.result ?? built);
  fs.mkdirSync(path.dirname(target), {recursive: true});
  if (fs.existsSync(target)) {
    if (fs.readFileSync(target, "utf8") !== body) {
      throw new Error(`refusing to overwrite a different validator-contract sensitivity artifact: ${target}`);
    }
  } else {
    fs.writeFileSync(target, body, {flag: "wx"});
  }
  return {path: target, sha256: hashFile(target), bytes: Buffer.byteLength(body, "utf8")};
}
