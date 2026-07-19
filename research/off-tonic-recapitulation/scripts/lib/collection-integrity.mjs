import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {validateCase} from "./case-validator.mjs";

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
  if (!Number.isSafeInteger(manifest.randomization_seed)) throw new Error("manifest randomization seed is not frozen");
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
  const modelLabels = Object.keys(matrix.models ?? {});
  if (modelLabels.length !== 3 || new Set(modelLabels).size !== 3) throw new Error("matrix must contain exactly three models");
  const modelKeys = ["provider", "model_id", "cli", "cli_version", "decoding_settings", "tool_access", "adapter", "adapter_sha256"];
  for (const label of modelLabels) {
    if (!/^[a-z0-9][a-z0-9._-]*$/.test(label)) throw new Error(`invalid model label: ${label}`);
    const spec = matrix.models[label];
    exactKeys(spec, modelKeys, `model ${label}`);
    for (const key of modelKeys) assertNoTbd(spec[key], `model ${label}.${key}`);
    if (spec.tool_access !== "none") throw new Error(`model ${label} must have tool_access none`);
    const adapterRelative = safeRelative(spec.adapter);
    const adapterFull = path.join(experimentDir, adapterRelative);
    if (hashFile(adapterFull) !== spec.adapter_sha256) throw new Error(`adapter hash mismatch: ${label}`);
    if ((fs.statSync(adapterFull).mode & 0o111) === 0) throw new Error(`adapter is not executable: ${label}`);
    lockedFiles.add(adapterRelative);
  }

  const scheduledSlots = new Set();
  for (const task of taskNames) for (const model of modelLabels) for (const caseId of caseIds) {
    for (const run of ["01", "02", "03"]) scheduledSlots.add(`${task}\u0000${model}\u0000${caseId}\u0000${run}`);
  }
  if (!Array.isArray(matrix.schedule) || matrix.schedule.length !== scheduledSlots.size) {
    throw new Error(`matrix schedule must contain ${scheduledSlots.size} calls`);
  }
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
    "scripts/build-prompt.mjs",
    "scripts/run-model.sh",
    "scripts/validate-output.mjs",
    "scripts/write-run-metadata.mjs",
    "scripts/write-completion-marker.mjs",
    "scripts/verify-collection-lock.mjs",
    "scripts/lib/case-validator.mjs",
    "scripts/lib/collection-integrity.mjs",
    "scripts/lib/response-validator.mjs",
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
