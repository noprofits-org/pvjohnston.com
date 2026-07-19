import fs from "node:fs";
import path from "node:path";
import {isDeepStrictEqual} from "node:util";
import {
  availabilityAgreement,
  completeOrdinalMedian,
  directAgreement,
  dossierBootstrap,
  summarizeReliability
} from "./lib/reliability.mjs";
import {hashFile, sha256, verifyCollectionLock} from "./lib/collection-integrity.mjs";
import {parseAndValidateResponse} from "./lib/response-validator.mjs";

const experimentDir = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, ".."));
const {lock, manifest, matrix, identity} = verifyCollectionLock(experimentDir);

const cueNames = [
  "tonal_stability",
  "thematic_correspondence",
  "preparation_strength",
  "proportional_location",
  "rhetorical_emphasis",
  "rotational_continuation"
];
const statusLabels = ["not_recapitulation", "off_tonic_recapitulation", "tonic_double_return"];
const identificationLevels = ["L0", "L1", "L2"];
const runIds = ["01", "02", "03"];
const caseIds = manifest.cases.map((entry) => entry.case_id);
const modelLabels = Object.keys(matrix.models);
const caseEntries = new Map(manifest.cases.map((entry) => [entry.case_id, entry]));
const dossiers = new Map(manifest.cases.map((entry) => [
  entry.case_id,
  JSON.parse(fs.readFileSync(path.join(experimentDir, "data", entry.file), "utf8"))
]));
const manifestPath = path.join(experimentDir, "data", "manifest.json");
const matrixPath = path.join(experimentDir, "run-matrix.json");
const lockPath = path.join(experimentDir, "collection-lock.json");
const currentHashes = {
  manifest: hashFile(manifestPath),
  matrix: hashFile(matrixPath),
  lock: hashFile(lockPath)
};

const resultKey = (model, caseId, run) => `${model}\u0000${caseId}\u0000${run}`;
const baseName = ({model, case_id: caseId, run}) =>
  `${model}__${manifest.evidence_condition}__${caseId}__run-${run}`;

const renderedPromptHash = (task, caseId) => {
  const entry = caseEntries.get(caseId);
  const dossierBody = fs.readFileSync(path.join(experimentDir, "data", entry.file), "utf8");
  const prompt = fs.readFileSync(path.join(experimentDir, matrix.tasks[task].prompt), "utf8");
  const rendered = prompt.replace("{{CASE_ID}}", caseId).replace(
    "{{DOSSIER}}",
    `--- BEGIN FILE: ${entry.file} ---\n${dossierBody}\n--- END FILE: ${entry.file} ---`
  );
  return sha256(rendered);
};

const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const existing = (file) => fs.existsSync(file);
const isoDate = (value) => typeof value === "string" && !Number.isNaN(Date.parse(value));
const addMismatch = (issues, condition, message) => {
  if (!condition) issues.push(message);
};

function inspectScheduledSlot(slot) {
  const outputDir = path.join(
    experimentDir,
    "outputs",
    manifest.dataset_version,
    "scheduled",
    slot.task
  );
  const base = baseName(slot);
  const files = {
    marker: path.join(outputDir, `${base}.complete.json`),
    metadata: path.join(outputDir, `${base}.run.json`),
    response_valid: path.join(outputDir, `${base}.md`),
    response_invalid: path.join(outputDir, `${base}.invalid.md`),
    stderr: path.join(outputDir, `${base}.stderr.txt`)
  };
  const present = Object.fromEntries(Object.entries(files).map(([name, file]) => [name, existing(file)]));
  const artifactCount = Object.values(present).filter(Boolean).length;
  const record = {
    sequence: slot.sequence,
    task: slot.task,
    model: slot.model,
    case_id: slot.case_id,
    run: slot.run,
    base,
    status: "absent",
    issues: [],
    response_file: null,
    parsed: null
  };
  if (artifactCount === 0) return record;

  const responsePaths = [files.response_valid, files.response_invalid].filter(existing);
  if (!present.marker || !present.metadata || !present.stderr || responsePaths.length !== 1) {
    record.status = "partial";
    if (!present.marker) record.issues.push("missing completion marker");
    if (!present.metadata) record.issues.push("missing run metadata");
    if (!present.stderr) record.issues.push("missing stderr artifact");
    if (responsePaths.length === 0) record.issues.push("missing response artifact");
    if (responsePaths.length > 1) record.issues.push("both valid and invalid response artifacts are present");
    return record;
  }

  const responsePath = responsePaths[0];
  record.response_file = path.basename(responsePath);
  let marker;
  let metadata;
  try {
    marker = readJson(files.marker);
  } catch (error) {
    record.status = "partial";
    record.issues.push(`unreadable completion marker: ${error.message}`);
    return record;
  }
  try {
    metadata = readJson(files.metadata);
  } catch (error) {
    record.status = "partial";
    record.issues.push(`unreadable run metadata: ${error.message}`);
    return record;
  }

  const issues = record.issues;
  addMismatch(issues, marker.schema_version === "1.0.0", "wrong completion-marker schema version");
  addMismatch(issues, isoDate(marker.completed_at), "invalid completion timestamp");
  addMismatch(issues, marker.metadata_file === path.basename(files.metadata), "marker metadata filename mismatch");
  addMismatch(issues, marker.metadata_sha256 === hashFile(files.metadata), "marker metadata hash mismatch");
  addMismatch(issues, marker.response_file === path.basename(responsePath), "marker response filename mismatch");
  addMismatch(issues, marker.response_sha256 === hashFile(responsePath), "marker response hash mismatch");
  addMismatch(issues, marker.stderr_file === path.basename(files.stderr), "marker stderr filename mismatch");
  addMismatch(issues, marker.stderr_sha256 === hashFile(files.stderr), "marker stderr hash mismatch");

  const modelSpec = matrix.models[slot.model];
  const adapterPath = path.join(experimentDir, modelSpec.adapter);
  const promptPath = path.join(experimentDir, matrix.tasks[slot.task].prompt);
  const caseEntry = caseEntries.get(slot.case_id);
  const dossierPath = path.join(experimentDir, "data", caseEntry.file);
  addMismatch(issues, metadata.schema_version === "2.0.0", "wrong run-metadata schema version");
  addMismatch(issues, metadata.task === slot.task, "metadata task mismatch");
  addMismatch(issues, metadata.case_id === slot.case_id, "metadata case mismatch");
  addMismatch(issues, metadata.model_label === slot.model, "metadata model mismatch");
  addMismatch(issues, metadata.run_kind === "scheduled", "metadata run kind is not scheduled");
  addMismatch(issues, metadata.run === slot.run, "metadata run ID mismatch");
  addMismatch(issues, metadata.dataset_version === manifest.dataset_version, "metadata dataset version mismatch");
  addMismatch(issues, isDeepStrictEqual(metadata.requested_model_spec, modelSpec), "metadata model specification mismatch");
  addMismatch(issues, metadata.dataset_manifest_sha256 === currentHashes.manifest, "metadata manifest hash mismatch");
  addMismatch(issues, metadata.run_matrix_sha256 === currentHashes.matrix, "metadata matrix hash mismatch");
  addMismatch(issues, metadata.collection_lock_sha256 === currentHashes.lock, "metadata collection-lock hash mismatch");
  addMismatch(issues, metadata.adapter_sha256 === hashFile(adapterPath), "metadata adapter hash mismatch");
  addMismatch(issues, metadata.prompt_template_sha256 === hashFile(promptPath), "metadata prompt hash mismatch");
  addMismatch(issues, metadata.rendered_prompt_sha256 === renderedPromptHash(slot.task, slot.case_id), "metadata rendered-prompt hash mismatch");
  addMismatch(issues, metadata.dossier_sha256 === hashFile(dossierPath), "metadata dossier hash mismatch");
  addMismatch(issues, metadata.response_file === path.basename(responsePath), "metadata response filename mismatch");
  addMismatch(issues, metadata.response_sha256 === hashFile(responsePath), "metadata response hash mismatch");
  addMismatch(issues, metadata.stderr_file === path.basename(files.stderr), "metadata stderr filename mismatch");
  addMismatch(issues, metadata.stderr_sha256 === hashFile(files.stderr), "metadata stderr hash mismatch");
  addMismatch(issues, isoDate(metadata.started_at) && isoDate(metadata.ended_at), "invalid run timestamps");
  addMismatch(issues, Number.isInteger(metadata.command_exit_status), "invalid command exit status");

  if (issues.length > 0) {
    record.status = "partial";
    return record;
  }

  const response = fs.readFileSync(responsePath, "utf8");
  let parsed = null;
  let validationError = null;
  try {
    parsed = parseAndValidateResponse({
      task: slot.task,
      expectedCase: slot.case_id,
      dossier: dossiers.get(slot.case_id),
      response
    });
  } catch (error) {
    validationError = error;
  }

  if (metadata.validation_status === "command_failed") {
    if (metadata.command_exit_status === 0 || responsePath !== files.response_invalid) {
      record.status = "partial";
      record.issues.push("command-failed metadata conflicts with exit status or response filename");
    } else {
      record.status = "command_failed";
      if (!validationError) record.issues.push("command output happened to satisfy the response schema");
    }
    return record;
  }
  if (metadata.validation_status === "invalid") {
    if (metadata.command_exit_status !== 0 || responsePath !== files.response_invalid) {
      record.status = "partial";
      record.issues.push("invalid metadata conflicts with exit status or response filename");
    } else if (!validationError) {
      record.status = "partial";
      record.issues.push("response now validates although metadata labels it invalid");
    } else {
      record.status = "invalid";
      record.issues.push(validationError.message);
    }
    return record;
  }
  if (metadata.validation_status !== "valid") {
    record.status = "partial";
    record.issues.push(`unknown validation status: ${metadata.validation_status}`);
    return record;
  }
  if (metadata.command_exit_status !== 0 || responsePath !== files.response_valid) {
    record.status = "partial";
    record.issues.push("valid metadata conflicts with exit status or response filename");
    return record;
  }
  if (validationError) {
    record.status = "invalid";
    record.issues.push(`independent response validation failed: ${validationError.message}`);
    return record;
  }
  record.status = "valid";
  record.parsed = parsed;
  return record;
}

const schedule = matrix.schedule.map((entry) => ({...entry}));
const expectedFilesByTask = new Map(["analysis", "identification"].map((task) => [task, new Set()]));
for (const slot of schedule) {
  const base = baseName(slot);
  for (const suffix of [".complete.json", ".run.json", ".md", ".invalid.md", ".stderr.txt"]) {
    expectedFilesByTask.get(slot.task).add(`${base}${suffix}`);
  }
}
const unexpectedScheduledArtifacts = [];
for (const task of ["analysis", "identification"]) {
  const taskDir = path.join(experimentDir, "outputs", manifest.dataset_version, "scheduled", task);
  if (!fs.existsSync(taskDir)) continue;
  for (const entry of fs.readdirSync(taskDir, {withFileTypes: true})) {
    if (!expectedFilesByTask.get(task).has(entry.name)) {
      unexpectedScheduledArtifacts.push(path.posix.join(task, entry.name));
    }
  }
}

const slotRecords = schedule.map(inspectScheduledSlot);
const countsFor = (task) => {
  const counts = {absent: 0, partial: 0, command_failed: 0, invalid: 0, valid: 0};
  for (const record of slotRecords.filter((item) => item.task === task)) counts[record.status] += 1;
  return counts;
};
const slotStatusCounts = {
  analysis: countsFor("analysis"),
  identification: countsFor("identification")
};

const analysisRecords = slotRecords.filter((record) => record.task === "analysis");
const identificationRecords = slotRecords.filter((record) => record.task === "identification");
const validAnalysis = analysisRecords.filter((record) => record.status === "valid");
const validIdentification = identificationRecords.filter((record) => record.status === "valid");
const analysisResults = new Map(validAnalysis.map((record) => [
  resultKey(record.model, record.case_id, record.run),
  record.parsed
]));
const scoresFor = (model, caseId, cue) => runIds.map((run) =>
  analysisResults.get(resultKey(model, caseId, run))?.cues?.[cue]?.score ?? null
);
const completeModelData = (model) => caseIds.every((caseId) => runIds.every((run) => {
  const parsed = analysisResults.get(resultKey(model, caseId, run));
  return parsed && cueNames.every((cue) => Number.isInteger(parsed.cues?.[cue]?.score));
}));

const withinModel = {};
for (const model of modelLabels) {
  const caseUnits = caseIds.map((caseId) => cueNames.map((cue) => scoresFor(model, caseId, cue)));
  const units = caseUnits.flat();
  withinModel[model] = {
    complete_three_run_data: completeModelData(model),
    aggregate: summarizeReliability(units),
    availability: availabilityAgreement(units),
    bootstrap_95: dossierBootstrap(caseUnits, 2000, 1701),
    by_cue: Object.fromEntries(cueNames.map((cue) => [cue,
      directAgreement(caseIds.map((caseId) => scoresFor(model, caseId, cue)))
    ]))
  };
}

const crossCaseUnits = caseIds.map((caseId) => cueNames.map((cue) =>
  modelLabels.map((model) => completeOrdinalMedian(scoresFor(model, caseId, cue)))
));
const crossModel = {
  aggregate: summarizeReliability(crossCaseUnits.flat()),
  availability: availabilityAgreement(crossCaseUnits.flat()),
  bootstrap_95: dossierBootstrap(crossCaseUnits, 2000, 1702),
  by_cue: Object.fromEntries(cueNames.map((cue) => [cue,
    directAgreement(caseIds.map((caseId) => modelLabels.map((model) => completeOrdinalMedian(scoresFor(model, caseId, cue)))))
  ]))
};

const scheduledAnalysis = analysisRecords.length;
const scheduledIdentification = identificationRecords.length;
const cueCells = scheduledAnalysis * cueNames.length;
let nonNullCueCells = 0;
for (const record of validAnalysis) {
  for (const cue of cueNames) if (Number.isInteger(record.parsed.cues?.[cue]?.score)) nonNullCueCells += 1;
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
const dispersion = Object.fromEntries(cueNames.map((cue) => [cue,
  Object.fromEntries(modelLabels.map((model) => {
    const values = caseIds.map((caseId) => completeOrdinalMedian(scoresFor(model, caseId, cue))).filter((value) => value !== null);
    return [model, values.length ? {
      minimum: Math.min(...values),
      maximum: Math.max(...values),
      span: Math.max(...values) - Math.min(...values)
    } : null];
  }))
]));
const nondegenerateCues = cueNames.filter((cue) =>
  repeatableModels.filter((model) => dispersion[cue][model]?.span >= 2).length >= 2
);
const modelCaseValidRepetitions = Object.fromEntries(modelLabels.map((model) => [model,
  Object.fromEntries(caseIds.map((caseId) => [caseId,
    runIds.filter((run) => analysisResults.has(resultKey(model, caseId, run))).length
  ]))
]));

const numericSummary = (values) => {
  const finite = values.filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
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
const distributionSummary = (records) => Object.fromEntries(statusLabels.map((label) => [label,
  numericSummary(records.map((record) => record.parsed.status_distribution[label]))
]));
const statusDistributionSummary = {
  overall: distributionSummary(validAnalysis),
  by_model: Object.fromEntries(modelLabels.map((model) => [model,
    distributionSummary(validAnalysis.filter((record) => record.model === model))
  ]))
};
const confidenceSummary = {
  overall: numericSummary(validIdentification.map((record) => record.parsed.identification.confidence)),
  by_model: Object.fromEntries(modelLabels.map((model) => [model,
    numericSummary(validIdentification.filter((record) => record.model === model)
      .map((record) => record.parsed.identification.confidence))
  ])),
  by_recognition_level: Object.fromEntries(["none", "style_only", "specific_candidate"].map((level) => [level,
    numericSummary(validIdentification.filter((record) => record.parsed.identification.recognition_level === level)
      .map((record) => record.parsed.identification.confidence))
  ]))
};

const identificationRepeatability = (responses, byOutput) => {
  const summarize = (selectedModels) => {
    const triplets = [];
    for (const model of selectedModels) for (const caseId of caseIds) {
      const labels = runIds.map((run) => {
        const response = responses.get(resultKey(model, caseId, run));
        return response ? byOutput.get(response.filename)?.level ?? null : null;
      });
      if (labels.every((level) => identificationLevels.includes(level))) triplets.push(labels);
    }
    const pairs = triplets.flatMap((labels) => [[labels[0], labels[1]], [labels[0], labels[2]], [labels[1], labels[2]]]);
    return {
      complete_case_triplets: triplets.length,
      pairwise_comparisons: pairs.length,
      exact_pairwise_agreement: pairs.length
        ? pairs.filter(([left, right]) => left === right).length / pairs.length
        : null,
      unanimous_cases: triplets.filter((labels) => new Set(labels).size === 1).length,
      by_category: Object.fromEntries(identificationLevels.map((level) => [level, {
        run_count: triplets.flat().filter((value) => value === level).length,
        pairwise_matches: pairs.filter(([left, right]) => left === level && right === level).length,
        unanimous_cases: triplets.filter((labels) => labels.every((value) => value === level)).length
      }]))
    };
  };
  return {
    overall: summarize(modelLabels),
    by_model: Object.fromEntries(modelLabels.map((model) => [model, summarize([model])]))
  };
};

const validIdentificationByName = new Map(validIdentification.map((record) => [record.response_file, {
  ...record,
  filename: record.response_file
}]));
const validIdentificationByResultKey = new Map(validIdentification.map((record) => [
  resultKey(record.model, record.case_id, record.run),
  {...record, filename: record.response_file}
]));
const adjudicationPath = path.join(experimentDir, "data", "provenance", "identification-adjudication.json");
const adjudication = readJson(adjudicationPath);
let identificationSummary = {
  status: "pending_adjudication",
  scheduled: scheduledIdentification,
  valid_outputs: validIdentification.length,
  adjudicated_outputs: 0,
  confidence: confidenceSummary,
  level_counts: null,
  l2_events: null,
  target_l2_events: null,
  compromised_target_dossiers: null,
  positive_control: null,
  repeatability_by_category: null,
  gate: false
};
if (adjudication.status === "complete") {
  const byOutput = new Map();
  for (const judgment of adjudication.judgments ?? []) {
    if (byOutput.has(judgment.output)) throw new Error(`duplicate identification adjudication: ${judgment.output}`);
    if (!identificationLevels.includes(judgment.level)) throw new Error(`invalid identification level: ${judgment.level}`);
    if (typeof judgment.reason !== "string" || judgment.reason.trim() === "") {
      throw new Error(`missing adjudication reason: ${judgment.output}`);
    }
    byOutput.set(judgment.output, judgment);
  }
  for (const name of byOutput.keys()) {
    if (!validIdentificationByName.has(name)) throw new Error(`adjudication has no valid output: ${name}`);
  }
  for (const name of validIdentificationByName.keys()) {
    if (!byOutput.has(name)) throw new Error(`valid identification output lacks adjudication: ${name}`);
  }

  const levelCounts = {L0: 0, L1: 0, L2: 0};
  const l2Events = [];
  for (const response of validIdentificationByName.values()) {
    const judgment = byOutput.get(response.filename);
    levelCounts[judgment.level] += 1;
    if (judgment.level === "L2") l2Events.push({
      filename: response.filename,
      model: response.model,
      case_id: response.case_id,
      run: response.run,
      reason: judgment.reason
    });
  }

  const identityByCase = new Map(identity.cases.map((entry) => [entry.case_id, entry]));
  const positiveControlId = identity.cases.find((entry) => entry.probe_role === "positive_control").case_id;
  const targetCaseIds = caseIds.filter((caseId) => identityByCase.get(caseId).probe_role === "target");
  const targetL2Events = l2Events.filter((event) => targetCaseIds.includes(event.case_id));
  const compromisedTargets = [];
  for (const caseId of targetCaseIds) {
    const events = targetL2Events.filter((item) => item.case_id === caseId);
    const countByModel = Object.fromEntries(modelLabels.map((model) => [model,
      events.filter((item) => item.model === model).length
    ]));
    const modelsWithL2 = modelLabels.filter((model) => countByModel[model] > 0);
    if (modelLabels.some((model) => countByModel[model] >= 2) || modelsWithL2.length >= 2) {
      compromisedTargets.push({case_id: caseId, l2_by_model: countByModel});
    }
  }
  const positiveEvents = l2Events.filter((event) => event.case_id === positiveControlId);
  const positiveByModel = Object.fromEntries(modelLabels.map((model) => [model,
    positiveEvents.filter((event) => event.model === model).length
  ]));
  const positiveModelsWithAny = modelLabels.filter((model) => positiveByModel[model] > 0);
  const positiveSensitive = modelLabels.some((model) => positiveByModel[model] >= 2)
    || positiveModelsWithAny.length >= 2;
  const fullyAdjudicated = byOutput.size === scheduledIdentification
    && validIdentification.length === scheduledIdentification;

  identificationSummary = {
    status: "complete",
    scheduled: scheduledIdentification,
    valid_outputs: validIdentification.length,
    adjudicated_outputs: byOutput.size,
    confidence: confidenceSummary,
    level_counts: levelCounts,
    l2_events: l2Events,
    target_l2_events: targetL2Events,
    compromised_target_dossiers: compromisedTargets,
    positive_control: {
      case_id: positiveControlId,
      l2_by_model: positiveByModel,
      models_with_any_l2: positiveModelsWithAny,
      sensitivity_detected: positiveSensitive
    },
    repeatability_by_category: identificationRepeatability(validIdentificationByResultKey, byOutput),
    gate: fullyAdjudicated
      && !unexpectedScheduledArtifacts.some((artifact) => artifact.startsWith("identification/"))
      && targetL2Events.length === 0
      && compromisedTargets.length === 0
      && positiveSensitive
  };
}

const outputGate = slotStatusCounts.analysis.valid === scheduledAnalysis
  && slotStatusCounts.identification.valid === scheduledIdentification
  && nonNullCueCells === cueCells
  && unexpectedScheduledArtifacts.length === 0;
const summary = {
  schema_version: "2.0.0",
  dataset_version: manifest.dataset_version,
  collection_integrity: {
    lock_created_at: lock.created_at,
    scheduled_slot_status_counts: slotStatusCounts,
    unexpected_scheduled_artifacts: unexpectedScheduledArtifacts,
    slots: slotRecords.map(({parsed, ...record}) => record)
  },
  scheduled_analysis_invocations: scheduledAnalysis,
  valid_analysis_invocations: validAnalysis.length,
  scheduled_cue_cells: cueCells,
  non_null_cue_cells: nonNullCueCells,
  output_validity_rate: scheduledAnalysis ? validAnalysis.length / scheduledAnalysis : null,
  cue_completeness_rate: cueCells ? nonNullCueCells / cueCells : null,
  status_distribution: statusDistributionSummary,
  within_model: withinModel,
  cross_model: crossModel,
  cue_dispersion: dispersion,
  model_case_valid_repetitions: modelCaseValidRepetitions,
  identification: identificationSummary,
  repeatable_models: repeatableModels,
  nondegenerate_cues: nondegenerateCues,
  preliminary_gates: {
    output_gate: outputGate,
    repeatability_gate: repeatableModels.length >= 2,
    dispersion_gate: nondegenerateCues.length >= 4,
    identification_gate: identificationSummary.gate
  }
};
summary.automatic_expansion_gate = Object.values(summary.preliminary_gates).every((value) => value === true);

process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
