import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {spawnSync} from "node:child_process";

import {hashFile, safeRelative} from "./collection-integrity.mjs";

const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const readJson = (file, label) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${label} is not readable JSON: ${error.message}`);
  }
};

const sameJson = (left, right) => JSON.stringify(left) === JSON.stringify(right);
const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};
const validDate = (value) => typeof value === "string" && !Number.isNaN(Date.parse(value));

export function scheduledSlotPaths(experimentDir, manifest, entry) {
  const datasetVersion = manifest.dataset_version;
  const condition = manifest.evidence_condition;
  assert(/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(datasetVersion ?? ""), "unsafe dataset version");
  assert(/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(condition ?? ""), "unsafe evidence condition");
  assert(Number.isSafeInteger(entry.sequence) && entry.sequence > 0, "invalid scheduled sequence");
  assert(["analysis", "identification"].includes(entry.task), "invalid scheduled task");
  assert(/^[a-z0-9][a-z0-9._-]*$/.test(entry.model ?? ""), "invalid scheduled model label");
  assert(/^CASE-[A-Z0-9]{4}$/.test(entry.case_id ?? ""), "invalid scheduled case ID");
  assert(/^0[1-3]$/.test(entry.run ?? ""), "invalid scheduled run number");

  const outputDir = path.join(experimentDir, "outputs", datasetVersion, "scheduled", entry.task);
  const claimDir = path.join(experimentDir, "outputs", datasetVersion, "scheduled", ".claims", entry.task);
  const base = `${entry.model}__${condition}__${entry.case_id}__run-${entry.run}`;
  return {
    outputDir,
    claimDir,
    base,
    response: path.join(outputDir, `${base}.md`),
    invalidResponse: path.join(outputDir, `${base}.invalid.md`),
    metadata: path.join(outputDir, `${base}.run.json`),
    stderr: path.join(outputDir, `${base}.stderr.txt`),
    marker: path.join(outputDir, `${base}.complete.json`),
    attempt: path.join(claimDir, `${base}.attempt.json`),
    runnerLock: path.join(outputDir, `.${base}.lock`)
  };
}

export function writeAttemptClaim(experimentDir, manifest, entry) {
  const paths = scheduledSlotPaths(experimentDir, manifest, entry);
  fs.mkdirSync(paths.claimDir, {recursive: true});
  const claim = {
    schema_version: "1.0.0",
    sequence: entry.sequence,
    task: entry.task,
    model: entry.model,
    case_id: entry.case_id,
    run: entry.run,
    collection_lock_sha256: hashFile(path.join(experimentDir, "collection-lock.json")),
    claimed_at: new Date().toISOString()
  };
  fs.writeFileSync(paths.attempt, `${JSON.stringify(claim, null, 2)}\n`, {flag: "wx", mode: 0o444});
  fs.chmodSync(paths.attempt, 0o444);
  return paths;
}

export const verifyAttemptClaim = (experimentDir, paths, entry) => {
  assert(fs.existsSync(paths.attempt), `missing attempt claim at sequence ${entry.sequence}`);
  const claim = readJson(paths.attempt, "attempt claim");
  assert(claim.schema_version === "1.0.0", `attempt claim schema mismatch at sequence ${entry.sequence}`);
  for (const key of ["sequence", "task", "model", "case_id", "run"]) {
    assert(claim[key] === entry[key], `attempt claim ${key} mismatch at sequence ${entry.sequence}`);
  }
  assert(validDate(claim.claimed_at), `attempt claim timestamp is invalid at sequence ${entry.sequence}`);
  assert(
    claim.collection_lock_sha256 === hashFile(path.join(experimentDir, "collection-lock.json")),
    `attempt claim lock hash mismatch at sequence ${entry.sequence}`
  );
  assert((fs.statSync(paths.attempt).mode & 0o222) === 0, `attempt claim is writable at sequence ${entry.sequence}`);
  return claim;
};

const renderedPromptHash = (experimentDir, entry) => {
  const builder = path.join(experimentDir, "scripts", "build-prompt.mjs");
  const result = spawnSync(process.execPath, [builder, experimentDir, entry.task, entry.case_id], {
    encoding: null,
    maxBuffer: 16 * 1024 * 1024
  });
  assert(
    result.status === 0 && result.signal === null && !result.error,
    `could not reconstruct rendered prompt at sequence ${entry.sequence}`
  );
  return sha256(result.stdout);
};

const responseValidationResult = (experimentDir, entry, dossierPath, responsePath) => {
  const validator = path.join(experimentDir, "scripts", "validate-output.mjs");
  return spawnSync(process.execPath, [validator, entry.task, entry.case_id, dossierPath, responsePath], {
    encoding: null,
    maxBuffer: 4 * 1024 * 1024
  });
};

export function inspectScheduledBundle(experimentDir, verifiedState, entry) {
  const {manifest, matrix} = verifiedState;
  const paths = scheduledSlotPaths(experimentDir, manifest, entry);
  const mainPaths = [paths.response, paths.invalidResponse, paths.metadata, paths.stderr, paths.marker];
  const mainExists = mainPaths.map((file) => fs.existsSync(file));
  const claimExists = fs.existsSync(paths.attempt);
  const lockExists = fs.existsSync(paths.runnerLock);
  const presentCount = mainExists.filter(Boolean).length;

  if (presentCount === 0 && !claimExists && !lockExists) {
    return {state: "empty", paths};
  }
  if (lockExists) throw new Error(`active or stale runner lock at sequence ${entry.sequence}`);
  if (presentCount === 0 && claimExists) {
    verifyAttemptClaim(experimentDir, paths, entry);
    throw new Error(`attempted slot has no complete bundle at sequence ${entry.sequence}; retry is forbidden`);
  }
  if (presentCount > 0 && !claimExists) {
    throw new Error(`scheduled bundle lacks its required attempt claim at sequence ${entry.sequence}`);
  }

  const responseExists = mainExists[0];
  const invalidExists = mainExists[1];
  if (responseExists === invalidExists || !mainExists[2] || !mainExists[3] || !mainExists[4]) {
    throw new Error(`partial or ambiguous bundle at sequence ${entry.sequence}; retry is forbidden`);
  }
  verifyAttemptClaim(experimentDir, paths, entry);

  const responsePath = responseExists ? paths.response : paths.invalidResponse;
  const metadata = readJson(paths.metadata, "run metadata");
  const marker = readJson(paths.marker, "completion marker");
  const modelSpec = matrix.models[entry.model];
  const manifestPath = path.join(experimentDir, "data", "manifest.json");
  const matrixPath = path.join(experimentDir, "run-matrix.json");
  const lockPath = path.join(experimentDir, "collection-lock.json");
  const promptPath = path.join(experimentDir, safeRelative(matrix.tasks[entry.task].prompt));
  const adapterPath = path.join(experimentDir, safeRelative(modelSpec.adapter));
  const caseRecord = manifest.cases.find((candidate) => candidate.case_id === entry.case_id);
  assert(caseRecord, `case is absent from manifest at sequence ${entry.sequence}`);
  const dossierPath = path.join(experimentDir, "data", safeRelative(caseRecord.file));

  assert(metadata.schema_version === "2.0.0", `metadata schema mismatch at sequence ${entry.sequence}`);
  const expectedMetadata = {
    task: entry.task,
    case_id: entry.case_id,
    model_label: entry.model,
    run_kind: "scheduled",
    run: entry.run,
    dataset_version: manifest.dataset_version
  };
  for (const [key, expected] of Object.entries(expectedMetadata)) {
    assert(metadata[key] === expected, `metadata ${key} mismatch at sequence ${entry.sequence}`);
  }
  assert(sameJson(metadata.requested_model_spec, modelSpec), `requested model spec mismatch at sequence ${entry.sequence}`);
  assert(sameJson(metadata.invocation, [modelSpec.adapter]), `invocation mismatch at sequence ${entry.sequence}`);
  assert(validDate(metadata.started_at) && validDate(metadata.ended_at), `metadata timestamp mismatch at sequence ${entry.sequence}`);
  assert(Date.parse(metadata.started_at) <= Date.parse(metadata.ended_at), `metadata time order mismatch at sequence ${entry.sequence}`);

  const expectedHashes = {
    dataset_manifest_sha256: hashFile(manifestPath),
    run_matrix_sha256: hashFile(matrixPath),
    collection_lock_sha256: hashFile(lockPath),
    adapter_sha256: hashFile(adapterPath),
    prompt_template_sha256: hashFile(promptPath),
    rendered_prompt_sha256: renderedPromptHash(experimentDir, entry),
    dossier_sha256: hashFile(dossierPath),
    response_sha256: hashFile(responsePath),
    stderr_sha256: hashFile(paths.stderr)
  };
  for (const [key, expected] of Object.entries(expectedHashes)) {
    assert(metadata[key] === expected, `metadata ${key} mismatch at sequence ${entry.sequence}`);
  }
  assert(metadata.response_file === path.basename(responsePath), `response filename mismatch at sequence ${entry.sequence}`);
  assert(metadata.stderr_file === path.basename(paths.stderr), `stderr filename mismatch at sequence ${entry.sequence}`);

  const outcomes = {
    valid: {command: (status) => status === 0, responseIsInvalid: false, validator: 0},
    invalid: {command: (status) => status === 0, responseIsInvalid: true, validator: "nonzero"},
    command_failed: {command: (status) => Number.isInteger(status) && status !== 0, responseIsInvalid: true, validator: null}
  };
  const expectation = outcomes[metadata.validation_status];
  assert(expectation, `unknown validation status at sequence ${entry.sequence}`);
  assert(expectation.command(metadata.command_exit_status), `command status mismatch at sequence ${entry.sequence}`);
  assert(invalidExists === expectation.responseIsInvalid, `response disposition mismatch at sequence ${entry.sequence}`);
  if (expectation.validator !== null) {
    const validationResult = responseValidationResult(experimentDir, entry, dossierPath, responsePath);
    assert(
      validationResult.signal === null && !validationResult.error && Number.isInteger(validationResult.status),
      `could not re-run response validation at sequence ${entry.sequence}`
    );
    if (expectation.validator === 0) {
      assert(validationResult.status === 0, `valid response no longer validates at sequence ${entry.sequence}`);
    } else {
      assert(validationResult.status !== 0, `invalid response now validates at sequence ${entry.sequence}`);
    }
  }

  assert(marker.schema_version === "1.0.0", `completion marker schema mismatch at sequence ${entry.sequence}`);
  assert(validDate(marker.completed_at), `completion marker timestamp mismatch at sequence ${entry.sequence}`);
  const expectedMarker = {
    metadata_file: path.basename(paths.metadata),
    metadata_sha256: hashFile(paths.metadata),
    response_file: path.basename(responsePath),
    response_sha256: hashFile(responsePath),
    stderr_file: path.basename(paths.stderr),
    stderr_sha256: hashFile(paths.stderr)
  };
  for (const [key, expected] of Object.entries(expectedMarker)) {
    assert(marker[key] === expected, `completion marker ${key} mismatch at sequence ${entry.sequence}`);
  }
  for (const file of [responsePath, paths.metadata, paths.stderr, paths.marker]) {
    assert((fs.statSync(file).mode & 0o222) === 0, `bundle member is writable at sequence ${entry.sequence}`);
  }

  return {state: "complete", outcome: metadata.validation_status, paths, metadata};
}
