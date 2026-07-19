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
import {scheduledSlotPaths, verifyAttemptClaim} from "./lib/scheduled-bundle-integrity.mjs";

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
const providerByModel = new Map(modelLabels.map((model) => [model, matrix.models[model].provider]));
const providerLabels = [...new Set(providerByModel.values())];
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
  const dossier = JSON.parse(fs.readFileSync(path.join(experimentDir, "data", entry.file), "utf8"));
  const prompt = fs.readFileSync(path.join(experimentDir, matrix.tasks[task].prompt), "utf8");
  const rendered = prompt.replace("{{CASE_ID}}", caseId).replace(
    "{{DOSSIER}}",
    `--- BEGIN FILE: ${entry.file} ---\n${JSON.stringify(dossier)}\n--- END FILE: ${entry.file} ---`
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
  const scheduledPaths = scheduledSlotPaths(experimentDir, manifest, slot);
  const base = scheduledPaths.base;
  const files = {
    marker: scheduledPaths.marker,
    metadata: scheduledPaths.metadata,
    response_valid: scheduledPaths.response,
    response_invalid: scheduledPaths.invalidResponse,
    stderr: scheduledPaths.stderr
  };
  const present = Object.fromEntries(Object.entries(files).map(([name, file]) => [name, existing(file)]));
  const artifactCount = Object.values(present).filter(Boolean).length;
  const claimPresent = existing(scheduledPaths.attempt);
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
  if (artifactCount === 0 && !claimPresent) return record;

  record.status = "partial";
  if (!claimPresent) {
    record.issues.push("missing attempt claim");
  } else {
    try {
      verifyAttemptClaim(experimentDir, scheduledPaths, slot);
    } catch (error) {
      record.issues.push(`invalid attempt claim: ${error.message}`);
    }
  }
  if (artifactCount === 0) {
    record.issues.push("attempt claim exists without a scheduled bundle");
    return record;
  }

  const responsePaths = [files.response_valid, files.response_invalid].filter(existing);
  if (!present.marker || !present.metadata || !present.stderr || responsePaths.length !== 1) {
    if (!present.marker) record.issues.push("missing completion marker");
    if (!present.metadata) record.issues.push("missing run metadata");
    if (!present.stderr) record.issues.push("missing stderr artifact");
    if (responsePaths.length === 0) record.issues.push("missing response artifact");
    if (responsePaths.length > 1) record.issues.push("both valid and invalid response artifacts are present");
    return record;
  }
  if (record.issues.length > 0) return record;

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
const completeModelData = (model, ids) => ids.every((caseId) => runIds.every((run) => {
  const parsed = analysisResults.get(resultKey(model, caseId, run));
  return parsed && cueNames.every((cue) => Number.isInteger(parsed.cues?.[cue]?.score));
}));

// Primary reliability uses only target cases; the disclosed recognizable
// anchor (probe_role "positive_control") is computed identically but reported
// separately and enters no gate.
const roleByCase = new Map(identity.cases.map((entry) => [entry.case_id, entry.probe_role]));
const primaryCaseIds = caseIds.filter((caseId) => roleByCase.get(caseId) === "target");
const anchorCaseIds = caseIds.filter((caseId) => roleByCase.get(caseId) !== "target");
if (primaryCaseIds.length === 0) throw new Error("no target cases in identity key");
const medianScoreFor = (model, caseId, cue) => completeOrdinalMedian(scoresFor(model, caseId, cue));
const modelCaseCueMedians = Object.fromEntries(modelLabels.map((model) => [model,
  Object.fromEntries(caseIds.map((caseId) => [caseId,
    Object.fromEntries(cueNames.map((cue) => [cue, medianScoreFor(model, caseId, cue)]))
  ]))
]));

const withinModel = {};
for (const model of modelLabels) {
  const caseUnits = primaryCaseIds.map((caseId) => cueNames.map((cue) => scoresFor(model, caseId, cue)));
  const units = caseUnits.flat();
  const anchorUnits = anchorCaseIds.map((caseId) => cueNames.map((cue) => scoresFor(model, caseId, cue))).flat();
  withinModel[model] = {
    complete_three_run_data: completeModelData(model, primaryCaseIds),
    aggregate: summarizeReliability(units),
    availability: availabilityAgreement(units),
    bootstrap_95: dossierBootstrap(caseUnits, 2000, 1701),
    by_cue: Object.fromEntries(cueNames.map((cue) => [cue,
      directAgreement(primaryCaseIds.map((caseId) => scoresFor(model, caseId, cue)))
    ])),
    anchor: {
      complete_three_run_data: completeModelData(model, anchorCaseIds),
      aggregate: summarizeReliability(anchorUnits),
      availability: availabilityAgreement(anchorUnits)
    }
  };
}

const crossCaseUnits = primaryCaseIds.map((caseId) => cueNames.map((cue) =>
  modelLabels.map((model) => medianScoreFor(model, caseId, cue))
));
const anchorCrossUnits = anchorCaseIds.map((caseId) => cueNames.map((cue) =>
  modelLabels.map((model) => medianScoreFor(model, caseId, cue))
));
const crossModel = {
  aggregate: summarizeReliability(crossCaseUnits.flat()),
  availability: availabilityAgreement(crossCaseUnits.flat()),
  bootstrap_95: dossierBootstrap(crossCaseUnits, 2000, 1702),
  by_cue: Object.fromEntries(cueNames.map((cue) => [cue,
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
    const primaryUnits = primaryCaseIds.map((caseId) => cueNames.map((cue) => [
      medianScoreFor(left, caseId, cue),
      medianScoreFor(right, caseId, cue)
    ]));
    const anchorUnits = anchorCaseIds.map((caseId) => cueNames.map((cue) => [
      medianScoreFor(left, caseId, cue),
      medianScoreFor(right, caseId, cue)
    ]));
    pairwiseSystemReliability.push({
      systems: [left, right],
      providers,
      provider_comparison: providers[0] === providers[1] ? "within_provider" : "cross_provider",
      aggregate: summarizeReliability(primaryUnits.flat()),
      availability: availabilityAgreement(primaryUnits.flat()),
      by_cue: Object.fromEntries(cueNames.map((cue) => [cue,
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
const providersForModels = (models) => [...new Set(models.map((model) => providerByModel.get(model)))];
const repeatableProviders = providersForModels(repeatableModels);
const dispersion = Object.fromEntries(cueNames.map((cue) => [cue,
  Object.fromEntries(modelLabels.map((model) => {
    const values = primaryCaseIds.map((caseId) => medianScoreFor(model, caseId, cue)).filter((value) => value !== null);
    return [model, values.length ? {
      minimum: Math.min(...values),
      maximum: Math.max(...values),
      span: Math.max(...values) - Math.min(...values)
    } : null];
  }))
]));
const dispersionQualifiers = Object.fromEntries(cueNames.map((cue) => {
  const systems = repeatableModels.filter((model) => dispersion[cue][model]?.span >= 2);
  return [cue, {systems, providers: providersForModels(systems)}];
}));
const nondegenerateCues = cueNames.filter((cue) =>
  dispersionQualifiers[cue].systems.length >= 2
  && dispersionQualifiers[cue].providers.length === providerLabels.length
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

const analysisScoreRepeatabilityByL2Category = (responses, byOutput) => {
  const categories = ["repeated_l2", "isolated_l2", "no_l2"];
  const entries = Object.fromEntries(categories.map((category) => [category, []]));
  for (const model of modelLabels) for (const caseId of primaryCaseIds) {
    const levels = runIds.map((run) => {
      const response = responses.get(resultKey(model, caseId, run));
      return response ? byOutput.get(response.filename)?.level ?? null : null;
    });
    if (!levels.every((level) => identificationLevels.includes(level))) {
      throw new Error(`incomplete identification levels for ${model} ${caseId}`);
    }
    const l2Count = levels.filter((level) => level === "L2").length;
    const category = l2Count >= 2 ? "repeated_l2" : l2Count === 1 ? "isolated_l2" : "no_l2";
    const units = cueNames.map((cue) => scoresFor(model, caseId, cue));
    entries[category].push({model, case_id: caseId, l2_count: l2Count, units});
  }
  return Object.fromEntries(categories.map((category) => {
    const selected = entries[category];
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
  target_case_l2_summary: null,
  compromised_target_dossiers: null,
  positive_control: null,
  analysis_score_repeatability_by_l2_category: null,
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
  const summarizeCaseL2 = (caseId, eventPool) => {
    const events = eventPool.filter((item) => item.case_id === caseId);
    const countByModel = Object.fromEntries(modelLabels.map((model) => [model,
      events.filter((item) => item.model === model).length
    ]));
    const countByProvider = Object.fromEntries(providerLabels.map((provider) => [provider,
      events.filter((item) => providerByModel.get(item.model) === provider).length
    ]));
    const modelsWithL2 = modelLabels.filter((model) => countByModel[model] > 0);
    const providersWithL2 = providerLabels.filter((provider) => countByProvider[provider] > 0);
    const identityRecoverable = modelLabels.some((model) => countByModel[model] >= 2)
      || providersWithL2.length === providerLabels.length;
    return {
      case_id: caseId,
      l2_by_model: countByModel,
      models_with_any_l2: modelsWithL2,
      l2_by_provider: countByProvider,
      providers_with_any_l2: providersWithL2,
      identity_recoverable: identityRecoverable
    };
  };
  const targetCaseL2Summary = targetCaseIds.map((caseId) => summarizeCaseL2(caseId, targetL2Events));
  const compromisedTargets = targetCaseL2Summary.filter((entry) => entry.identity_recoverable);
  const positiveEvents = l2Events.filter((event) => event.case_id === positiveControlId);
  const positiveByModel = Object.fromEntries(modelLabels.map((model) => [model,
    positiveEvents.filter((event) => event.model === model).length
  ]));
  const positiveByProvider = Object.fromEntries(providerLabels.map((provider) => [provider,
    positiveEvents.filter((event) => providerByModel.get(event.model) === provider).length
  ]));
  const positiveModelsWithAny = modelLabels.filter((model) => positiveByModel[model] > 0);
  const positiveProvidersWithAny = providerLabels.filter((provider) => positiveByProvider[provider] > 0);
  const positiveSensitive = modelLabels.some((model) => positiveByModel[model] >= 2)
    || positiveProvidersWithAny.length === providerLabels.length;
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
    target_case_l2_summary: targetCaseL2Summary,
    compromised_target_dossiers: compromisedTargets,
    positive_control: {
      case_id: positiveControlId,
      l2_by_model: positiveByModel,
      models_with_any_l2: positiveModelsWithAny,
      l2_by_provider: positiveByProvider,
      providers_with_any_l2: positiveProvidersWithAny,
      sensitivity_detected: positiveSensitive
    },
    analysis_score_repeatability_by_l2_category: fullyAdjudicated
      ? analysisScoreRepeatabilityByL2Category(validIdentificationByResultKey, byOutput)
      : null,
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
const workLevelRecognitionOnTarget = validAnalysis.some((record) =>
  primaryCaseIds.includes(record.case_id)
  && record.parsed.suspected_recognition.level === "work"
);
const summary = {
  schema_version: "2.1.0",
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
  suspected_recognition: validAnalysis.map((record) => ({
    model: record.model,
    case_id: record.case_id,
    run: record.run,
    level: record.parsed.suspected_recognition.level,
    confidence: record.parsed.suspected_recognition.confidence,
    target_case: primaryCaseIds.includes(record.case_id)
  })),
  work_level_recognition_on_target: workLevelRecognitionOnTarget,
  within_model: withinModel,
  cross_model: crossModel,
  pairwise_system_reliability: pairwiseSystemReliability,
  model_case_cue_medians: modelCaseCueMedians,
  cue_dispersion: dispersion,
  cue_dispersion_qualifiers: dispersionQualifiers,
  model_case_valid_repetitions: modelCaseValidRepetitions,
  identification: identificationSummary,
  repeatable_models: repeatableModels,
  repeatable_providers: repeatableProviders,
  nondegenerate_cues: nondegenerateCues,
  preliminary_gates: {
    output_gate: outputGate,
    repeatability_gate: repeatableModels.length >= 2
      && repeatableProviders.length === providerLabels.length,
    dispersion_gate: nondegenerateCues.length >= 4,
    identification_gate: identificationSummary.gate,
    analysis_recognition_gate: !workLevelRecognitionOnTarget
  }
};
summary.automatic_expansion_gate = Object.values(summary.preliminary_gates).every((value) => value === true);

process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
