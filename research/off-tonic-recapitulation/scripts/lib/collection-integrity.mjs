import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {validateCase} from "./case-validator.mjs";
import {
  PREFLIGHT_SOURCE_FILES,
  PREFLIGHT_TASKS,
  SYNTHETIC_CASE_ID,
  makePreflightContract,
  makeSyntheticDossier,
  renderSyntheticPrompt
} from "./synthetic-preflight.mjs";

export const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
export const hashFile = (file) => sha256(fs.readFileSync(file));

export const safeRelative = (relative) => {
  if (typeof relative !== "string" || relative === "" || path.isAbsolute(relative)) {
    throw new Error(`unsafe relative path: ${relative}`);
  }
  const pieces = relative.replaceAll("\\", "/").split("/");
  if (pieces.includes("") || pieces.includes(".") || pieces.includes("..")) {
    throw new Error(`unsafe relative path: ${relative}`);
  }
  return relative;
};

const exactKeys = (value, expected, location) => {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`${location} must be an object`);
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    throw new Error(`${location} keys differ: ${JSON.stringify(actual)}`);
  }
};

const assertNoTbd = (value, location) => {
  if (value === null || value === undefined || value === "") throw new Error(`${location} is incomplete`);
  if (typeof value === "string" && /\bTBD\b|development/i.test(value)) throw new Error(`${location} is not frozen`);
};

const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));

const assertSha256 = (value, location) => {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    throw new Error(`${location} must be a lowercase SHA-256 hash`);
  }
};

const assertTimestamp = (value, location) => {
  if (typeof value !== "string" || Number.isNaN(Date.parse(value))) {
    throw new Error(`${location} must be an ISO timestamp`);
  }
};

const validatePassedPreflightReceipt = ({experimentDir, label, matrix, spec, lockedFiles, receiptFiles}) => {
  exactKeys(spec.preflight_receipt, ["path", "sha256"], `model ${label}.preflight_receipt`);
  const receiptRelative = safeRelative(spec.preflight_receipt.path);
  if (!receiptRelative.startsWith("data/provenance/preflight-receipts/")
      || !receiptRelative.endsWith(".receipt.json")) {
    throw new Error(`model ${label} preflight receipt must be under data/provenance/preflight-receipts`);
  }
  if (receiptFiles.has(receiptRelative)) throw new Error(`duplicate preflight receipt: ${receiptRelative}`);
  receiptFiles.add(receiptRelative);
  assertSha256(spec.preflight_receipt.sha256, `model ${label}.preflight_receipt.sha256`);
  const receiptPath = path.join(experimentDir, receiptRelative);
  if (hashFile(receiptPath) !== spec.preflight_receipt.sha256) {
    throw new Error(`preflight receipt hash mismatch: ${label}`);
  }

  const receipt = readJson(receiptPath);
  exactKeys(receipt, [
    "schema_version",
    "receipt_kind",
    "status",
    "started_at",
    "ended_at",
    "model",
    "protocol",
    "retention",
    "tasks"
  ], `preflight receipt ${label}`);
  if (receipt.schema_version !== "1.0.0"
      || receipt.receipt_kind !== "synthetic_response_contract_preflight"
      || receipt.status !== "passed") {
    throw new Error(`model ${label} does not have a passed synthetic response-contract receipt`);
  }
  assertTimestamp(receipt.started_at, `preflight receipt ${label}.started_at`);
  assertTimestamp(receipt.ended_at, `preflight receipt ${label}.ended_at`);
  if (Date.parse(receipt.ended_at) < Date.parse(receipt.started_at)) {
    throw new Error(`preflight receipt ${label} ends before it starts`);
  }
  const receiptDate = receipt.ended_at.slice(0, 10);
  if (spec.preflight_status !== `passed_no_outcome_${receiptDate}`) {
    throw new Error(`model ${label} preflight status date does not match its receipt`);
  }

  exactKeys(receipt.model, [
    "label",
    "provider",
    "requested_model_id",
    "generation_role",
    "experimental_unit",
    "cli",
    "cli_version",
    "tool_access",
    "adapter",
    "adapter_sha256"
  ], `preflight receipt ${label}.model`);
  const modelMatches = {
    label,
    provider: spec.provider,
    requested_model_id: spec.model_id,
    generation_role: spec.generation_role,
    experimental_unit: spec.experimental_unit,
    cli: spec.cli,
    cli_version: spec.cli_version,
    tool_access: spec.tool_access,
    adapter: spec.adapter,
    adapter_sha256: spec.adapter_sha256
  };
  for (const [key, expected] of Object.entries(modelMatches)) {
    if (receipt.model[key] !== expected) throw new Error(`preflight receipt ${label} model mismatch: ${key}`);
  }

  exactKeys(receipt.protocol, [
    "matrix_contract_sha256",
    "dossier_schema_version",
    "response_schema_version",
    "synthetic_case_id",
    "synthetic_dossier_sha256",
    "source_file_sha256"
  ], `preflight receipt ${label}.protocol`);
  const expectedContractHash = sha256(JSON.stringify(makePreflightContract(matrix, label)));
  if (receipt.protocol.matrix_contract_sha256 !== expectedContractHash) {
    throw new Error(`preflight receipt ${label} does not match the frozen model/task contract`);
  }
  if (receipt.protocol.dossier_schema_version !== "3.1.0"
      || receipt.protocol.response_schema_version !== "2.1.0"
      || receipt.protocol.synthetic_case_id !== SYNTHETIC_CASE_ID) {
    throw new Error(`preflight receipt ${label} has the wrong synthetic protocol version`);
  }
  const syntheticDossier = makeSyntheticDossier();
  const syntheticHash = sha256(JSON.stringify(syntheticDossier));
  if (receipt.protocol.synthetic_dossier_sha256 !== syntheticHash) {
    throw new Error(`preflight receipt ${label} has the wrong synthetic dossier hash`);
  }
  exactKeys(
    receipt.protocol.source_file_sha256,
    PREFLIGHT_SOURCE_FILES,
    `preflight receipt ${label}.protocol.source_file_sha256`
  );
  for (const relative of PREFLIGHT_SOURCE_FILES) {
    const recorded = receipt.protocol.source_file_sha256[relative];
    assertSha256(recorded, `preflight receipt ${label}.protocol.source_file_sha256.${relative}`);
    if (recorded !== hashFile(path.join(experimentDir, relative))) {
      throw new Error(`preflight receipt ${label} source changed after preflight: ${relative}`);
    }
  }

  exactKeys(receipt.retention, [
    "rendered_prompt_body_retained",
    "response_body_retained",
    "stderr_body_retained",
    "real_case_material_accessed"
  ], `preflight receipt ${label}.retention`);
  if (Object.values(receipt.retention).some((value) => value !== false)) {
    throw new Error(`preflight receipt ${label} retained prohibited content or accessed real case material`);
  }

  if (!Array.isArray(receipt.tasks) || receipt.tasks.length !== PREFLIGHT_TASKS.length) {
    throw new Error(`preflight receipt ${label} must contain both task receipts`);
  }
  const taskKeys = [
    "task",
    "status",
    "started_at",
    "ended_at",
    "duration_ms",
    "command_exit_status",
    "command_signal",
    "validation_status",
    "failure_code",
    "prompt_template",
    "prompt_template_sha256",
    "rendered_prompt_sha256",
    "rendered_prompt_bytes",
    "response_sha256",
    "response_bytes",
    "stderr_sha256",
    "stderr_bytes"
  ];
  receipt.tasks.forEach((taskReceipt, index) => {
    const task = PREFLIGHT_TASKS[index];
    exactKeys(taskReceipt, taskKeys, `preflight receipt ${label}.tasks[${index}]`);
    if (taskReceipt.task !== task
        || taskReceipt.status !== "passed"
        || taskReceipt.command_exit_status !== 0
        || taskReceipt.command_signal !== null
        || taskReceipt.validation_status !== "valid"
        || taskReceipt.failure_code !== null) {
      throw new Error(`preflight receipt ${label} did not pass ${task}`);
    }
    assertTimestamp(taskReceipt.started_at, `preflight receipt ${label}.${task}.started_at`);
    assertTimestamp(taskReceipt.ended_at, `preflight receipt ${label}.${task}.ended_at`);
    if (!Number.isSafeInteger(taskReceipt.duration_ms) || taskReceipt.duration_ms < 0) {
      throw new Error(`preflight receipt ${label}.${task}.duration_ms is invalid`);
    }
    if (taskReceipt.prompt_template !== matrix.tasks[task].prompt
        || taskReceipt.prompt_template_sha256 !== hashFile(path.join(experimentDir, matrix.tasks[task].prompt))) {
      throw new Error(`preflight receipt ${label}.${task} prompt mismatch`);
    }
    const {rendered} = renderSyntheticPrompt({
      experimentDir,
      matrix,
      task,
      dossier: syntheticDossier
    });
    if (taskReceipt.rendered_prompt_sha256 !== sha256(rendered)
        || taskReceipt.rendered_prompt_bytes !== Buffer.byteLength(rendered, "utf8")) {
      throw new Error(`preflight receipt ${label}.${task} rendered prompt mismatch`);
    }
    for (const key of ["prompt_template_sha256", "rendered_prompt_sha256", "response_sha256", "stderr_sha256"]) {
      assertSha256(taskReceipt[key], `preflight receipt ${label}.${task}.${key}`);
    }
    for (const key of ["rendered_prompt_bytes", "response_bytes", "stderr_bytes"]) {
      const minimum = key === "stderr_bytes" ? 0 : 1;
      if (!Number.isSafeInteger(taskReceipt[key]) || taskReceipt[key] < minimum) {
        throw new Error(`preflight receipt ${label}.${task}.${key} is invalid`);
      }
    }
  });

  lockedFiles.add(receiptRelative);
};

export function validateFrozenInputs(experimentDir) {
  const manifestPath = path.join(experimentDir, "data", "manifest.json");
  const matrixPath = path.join(experimentDir, "run-matrix.json");
  const identityPath = path.join(experimentDir, "data", "provenance", "identity-key.json");
  const sourceManifestPath = path.join(experimentDir, "data", "provenance", "source-manifest.json");
  const manifestBody = fs.readFileSync(manifestPath);
  const manifest = JSON.parse(manifestBody);
  const matrix = readJson(matrixPath);
  const identity = readJson(identityPath);
  const sourceManifest = readJson(sourceManifestPath);

  if (manifest.dataset_status !== "frozen") throw new Error("dataset manifest is not frozen");
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(manifest.dataset_version ?? "")) throw new Error("invalid dataset version");
  assertNoTbd(manifest.dataset_version, "dataset_version");
  if (manifest.pilot_case_count !== 6 || !Array.isArray(manifest.cases) || manifest.cases.length !== 6) {
    throw new Error("pilot manifest must contain exactly six cases");
  }
  if (typeof manifest.frozen !== "string" || Number.isNaN(Date.parse(manifest.frozen))) throw new Error("manifest frozen timestamp is invalid");

  const caseIds = new Set();
  const caseFiles = new Set();
  const lockedFiles = new Set([
    "data/manifest.json",
    "run-matrix.json",
    "data/provenance/identity-key.json",
    "data/provenance/source-manifest.json"
  ]);
  for (const entry of manifest.cases) {
    exactKeys(entry, ["case_id", "file", "sha256"], "manifest case entry");
    if (!/^CASE-[A-Z0-9]{4}$/.test(entry.case_id)) throw new Error(`invalid case ID: ${entry.case_id}`);
    if (caseIds.has(entry.case_id)) throw new Error(`duplicate case ID: ${entry.case_id}`);
    caseIds.add(entry.case_id);
    const relative = path.posix.join("data", safeRelative(entry.file));
    if (caseFiles.has(relative)) throw new Error(`duplicate case file: ${relative}`);
    caseFiles.add(relative);
    const full = path.join(experimentDir, relative);
    if (hashFile(full) !== entry.sha256) throw new Error(`case hash mismatch: ${relative}`);
    const dossier = readJson(full);
    validateCase(dossier);
    if (dossier.case_id !== entry.case_id) throw new Error(`manifest/dossier case mismatch: ${relative}`);
    lockedFiles.add(relative);
  }

  const taskNames = ["analysis", "identification"];
  exactKeys(matrix.tasks, taskNames, "matrix tasks");
  for (const task of taskNames) {
    exactKeys(matrix.tasks[task], ["prompt", "repetitions_per_case"], `matrix task ${task}`);
    if (matrix.tasks[task].repetitions_per_case !== 3) throw new Error(`${task} must have three repetitions`);
    const promptRelative = safeRelative(matrix.tasks[task].prompt);
    const promptFull = path.join(experimentDir, promptRelative);
    if (manifest.prompt_sha256?.[task] !== hashFile(promptFull)) throw new Error(`prompt hash mismatch: ${task}`);
    const prompt = fs.readFileSync(promptFull, "utf8");
    if (prompt.split("{{DOSSIER}}").length !== 2 || prompt.split("{{CASE_ID}}").length !== 2) {
      throw new Error(`prompt placeholders are invalid: ${task}`);
    }
    lockedFiles.add(promptRelative);
  }

  if (matrix.matrix_status !== "frozen") throw new Error("run matrix is not frozen");
  if (matrix.dataset_manifest_sha256 !== sha256(manifestBody)) throw new Error("matrix does not pin manifest");
  if (!Number.isSafeInteger(matrix.schedule_seed)) throw new Error("matrix schedule seed is not frozen");
  if (!Number.isSafeInteger(matrix.call_timeout_seconds)
      || matrix.call_timeout_seconds < 1
      || matrix.call_timeout_seconds > 3600) {
    throw new Error("matrix call timeout must be an integer from 1 through 3600 seconds");
  }
  const modelLabels = Object.keys(matrix.models ?? {});
  if (modelLabels.length !== 3 || new Set(modelLabels).size !== 3) throw new Error("matrix must contain exactly three models");
  const modelKeys = [
    "provider",
    "model_id",
    "generation_role",
    "experimental_unit",
    "cli",
    "cli_version",
    "authentication",
    "decoding_settings",
    "tool_access",
    "adapter",
    "adapter_sha256",
    "preflight_status",
    "preflight_receipt"
  ];
  const receiptFiles = new Set();
  const modelIdentityKeys = new Set();
  const providersByLabel = new Map();
  const rolesByLabel = new Map();
  for (const label of modelLabels) {
    if (!/^[a-z0-9][a-z0-9._-]*$/.test(label)) throw new Error(`invalid model label: ${label}`);
    const spec = matrix.models[label];
    exactKeys(spec, modelKeys, `model ${label}`);
    for (const key of modelKeys) assertNoTbd(spec[key], `model ${label}.${key}`);
    if (spec.tool_access !== "none") throw new Error(`model ${label} must have tool_access none`);
    if (!["frontier", "prior_generation_active_not_deprecated"].includes(spec.generation_role)) {
      throw new Error(`model ${label} has an invalid generation role`);
    }
    if (typeof spec.provider !== "string" || spec.provider.trim() === ""
        || typeof spec.model_id !== "string" || spec.model_id.trim() === "") {
      throw new Error(`model ${label} must have non-empty provider and model IDs`);
    }
    const modelIdentityKey = `${spec.provider}\u0000${spec.model_id}`;
    if (modelIdentityKeys.has(modelIdentityKey)) {
      throw new Error(`duplicate provider/model ID: ${spec.provider}/${spec.model_id}`);
    }
    modelIdentityKeys.add(modelIdentityKey);
    providersByLabel.set(label, spec.provider);
    rolesByLabel.set(label, spec.generation_role);
    if (!/^passed_no_outcome_[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(spec.preflight_status)) {
      throw new Error(`model ${label} has not passed a dated no-outcome preflight`);
    }
    const adapterRelative = safeRelative(spec.adapter);
    const adapterFull = path.join(experimentDir, adapterRelative);
    if (hashFile(adapterFull) !== spec.adapter_sha256) throw new Error(`adapter hash mismatch: ${label}`);
    if ((fs.statSync(adapterFull).mode & 0o111) === 0) throw new Error(`adapter is not executable: ${label}`);
    lockedFiles.add(adapterRelative);
    validatePassedPreflightReceipt({experimentDir, label, matrix, spec, lockedFiles, receiptFiles});
  }

  const providerCounts = new Map();
  for (const provider of providersByLabel.values()) {
    providerCounts.set(provider, (providerCounts.get(provider) ?? 0) + 1);
  }
  if (providerCounts.size !== 2
      || [...providerCounts.values()].toSorted((left, right) => left - right).join(",") !== "1,2") {
    throw new Error("matrix must contain exactly two providers with model-system multiplicities 2+1");
  }
  const frontierLabels = modelLabels.filter((label) => rolesByLabel.get(label) === "frontier");
  const priorGenerationLabels = modelLabels.filter(
    (label) => rolesByLabel.get(label) === "prior_generation_active_not_deprecated"
  );
  if (frontierLabels.length !== 2 || priorGenerationLabels.length !== 1) {
    throw new Error("matrix must contain exactly two frontier systems and one active prior-generation system");
  }
  const priorProvider = providersByLabel.get(priorGenerationLabels[0]);
  if (!frontierLabels.some((label) => providersByLabel.get(label) === priorProvider)) {
    throw new Error("active prior-generation system must share a provider with one frontier system");
  }

  const scheduledSlots = new Set();
  for (const task of taskNames) for (const model of modelLabels) for (const caseId of caseIds) {
    for (const run of ["01", "02", "03"]) scheduledSlots.add(`${task}\u0000${model}\u0000${caseId}\u0000${run}`);
  }
  if (!Array.isArray(matrix.schedule) || matrix.schedule.length !== scheduledSlots.size) {
    throw new Error(`matrix schedule must contain ${scheduledSlots.size} calls`);
  }
  if (scheduledSlots.size !== 108) throw new Error("matrix must contain exactly 108 scheduled calls");
  const observedSlots = new Set();
  matrix.schedule.forEach((entry, index) => {
    exactKeys(entry, ["sequence", "task", "model", "case_id", "run"], `schedule entry ${index + 1}`);
    if (entry.sequence !== index + 1) throw new Error(`schedule sequence mismatch at ${index + 1}`);
    const slot = `${entry.task}\u0000${entry.model}\u0000${entry.case_id}\u0000${entry.run}`;
    if (!scheduledSlots.has(slot)) throw new Error(`unexpected schedule slot: ${slot}`);
    if (observedSlots.has(slot)) throw new Error(`duplicate schedule slot: ${slot}`);
    observedSlots.add(slot);
  });

  if (identity.status !== "frozen" || !Array.isArray(identity.cases) || identity.cases.length !== 6) {
    throw new Error("identity key must be frozen with six cases");
  }
  const identityIds = new Set();
  let positiveControls = 0;
  for (const entry of identity.cases) {
    for (const key of ["case_id", "role", "probe_role", "composer", "work", "movement", "candidate_measure", "accepted_aliases"]) {
      if (!(key in entry)) throw new Error(`identity entry missing ${key}`);
    }
    if (!caseIds.has(entry.case_id) || identityIds.has(entry.case_id)) throw new Error(`identity case mismatch: ${entry.case_id}`);
    identityIds.add(entry.case_id);
    if (!['focal', 'tonic_control', 'off_tonic_control'].includes(entry.role)) throw new Error(`invalid corpus role: ${entry.case_id}`);
    if (!['target', 'positive_control'].includes(entry.probe_role)) throw new Error(`invalid probe role: ${entry.case_id}`);
    if (entry.probe_role === "positive_control") positiveControls += 1;
    for (const key of ["composer", "work", "movement", "candidate_measure"]) assertNoTbd(entry[key], `identity ${entry.case_id}.${key}`);
    if (!entry.accepted_aliases || typeof entry.accepted_aliases !== "object") throw new Error(`invalid aliases: ${entry.case_id}`);
  }
  if (positiveControls !== 1) throw new Error("identity key must designate exactly one positive control");

  if (sourceManifest.status !== "frozen" || !Array.isArray(sourceManifest.cases) || sourceManifest.cases.length !== 6) {
    throw new Error("source manifest must be frozen with six case records");
  }
  const sourceCaseIds = new Set(sourceManifest.cases.map((entry) => entry.case_id));
  if (sourceCaseIds.size !== 6 || [...caseIds].some((id) => !sourceCaseIds.has(id))) {
    throw new Error("source manifest case IDs do not match dossiers");
  }

  for (const relative of [
    "data/schema/case.schema.json",
    "data/provenance/EXTRACTION_PROTOCOL.md",
    "data/provenance/IDENTIFICATION_SCORING.md",
    "PREREGISTRATION.md",
    "STATISTICAL_ANALYSIS.md",
    "SYNTHETIC_PREFLIGHT.md",
    "scripts/build-prompt.mjs",
    "scripts/collect-schedule.mjs",
    "scripts/invoke-adapter.mjs",
    "scripts/run-model.sh",
    "scripts/validate-output.mjs",
    "scripts/write-run-metadata.mjs",
    "scripts/write-completion-marker.mjs",
    "scripts/verify-collection-lock.mjs",
    "scripts/verify-scheduled-attempt.mjs",
    "scripts/lib/case-validator.mjs",
    "scripts/lib/collection-integrity.mjs",
    "scripts/lib/scheduled-bundle-integrity.mjs",
    "scripts/lib/response-validator.mjs",
    "scripts/lib/synthetic-preflight.mjs",
    "scripts/run-synthetic-preflight.mjs",
    "scripts/analyze-results.mjs",
    "scripts/lib/reliability.mjs"
  ]) {
    if (!fs.existsSync(path.join(experimentDir, relative))) throw new Error(`missing locked protocol file: ${relative}`);
    lockedFiles.add(relative);
  }

  return {manifest, matrix, identity, sourceManifest, lockedFiles: [...lockedFiles].sort()};
}

export function buildCollectionLock(experimentDir) {
  const state = validateFrozenInputs(experimentDir);
  const files = Object.fromEntries(state.lockedFiles.map((relative) => [relative, hashFile(path.join(experimentDir, relative))]));
  return {
    schema_version: "1.0.0",
    dataset_version: state.manifest.dataset_version,
    created_at: new Date().toISOString(),
    files
  };
}

export function verifyCollectionLock(experimentDir) {
  const lockPath = path.join(experimentDir, "collection-lock.json");
  const lock = readJson(lockPath);
  exactKeys(lock, ["schema_version", "dataset_version", "created_at", "files"], "collection lock");
  if (lock.schema_version !== "1.0.0") throw new Error("unsupported collection-lock schema");
  if (Number.isNaN(Date.parse(lock.created_at))) throw new Error("invalid collection-lock timestamp");
  const state = validateFrozenInputs(experimentDir);
  if (lock.dataset_version !== state.manifest.dataset_version) throw new Error("collection-lock dataset version mismatch");
  const expectedFiles = state.lockedFiles;
  const actualFiles = Object.keys(lock.files).sort();
  if (JSON.stringify(expectedFiles) !== JSON.stringify(actualFiles)) throw new Error("collection-lock file set mismatch");
  for (const relative of expectedFiles) {
    if (!/^[0-9a-f]{64}$/.test(lock.files[relative] ?? "")) throw new Error(`invalid locked hash: ${relative}`);
    if (hashFile(path.join(experimentDir, relative)) !== lock.files[relative]) throw new Error(`locked file changed: ${relative}`);
  }
  return {lock, ...state};
}
