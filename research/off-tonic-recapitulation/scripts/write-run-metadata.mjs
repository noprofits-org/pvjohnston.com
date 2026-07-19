import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const [
  metadataPath,
  matrixPath,
  manifestPath,
  lockPath,
  promptPath,
  renderedPromptPath,
  dossierPath,
  responsePath,
  stderrPath,
  adapterPath,
  task,
  caseId,
  modelLabel,
  runKind,
  runId,
  startedAt,
  endedAt,
  exitStatus,
  validationStatus,
  validationError
] = process.argv.slice(2);

if ([metadataPath, matrixPath, manifestPath, lockPath, promptPath, renderedPromptPath,
  dossierPath, responsePath, stderrPath, adapterPath, task, caseId, modelLabel,
  runKind, runId, startedAt, endedAt, exitStatus, validationStatus].some((value) => !value)) {
  throw new Error("write-run-metadata.mjs received incomplete arguments");
}

const hashFile = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const matrix = JSON.parse(fs.readFileSync(matrixPath, "utf8"));
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const modelSpec = matrix.models?.[modelLabel];
if (!modelSpec) throw new Error(`model absent from matrix: ${modelLabel}`);

const metadata = {
  schema_version: "2.0.0",
  task,
  case_id: caseId,
  model_label: modelLabel,
  run_kind: runKind,
  run: runId,
  requested_model_spec: modelSpec,
  observed_model_version: null,
  provider_request_id: null,
  invocation: [modelSpec.adapter],
  started_at: startedAt,
  ended_at: endedAt,
  dataset_version: manifest.dataset_version,
  dataset_manifest_sha256: hashFile(manifestPath),
  run_matrix_sha256: hashFile(matrixPath),
  collection_lock_sha256: hashFile(lockPath),
  adapter_sha256: hashFile(adapterPath),
  prompt_template_sha256: hashFile(promptPath),
  rendered_prompt_sha256: hashFile(renderedPromptPath),
  dossier_sha256: hashFile(dossierPath),
  response_file: path.basename(responsePath),
  response_sha256: hashFile(responsePath),
  stderr_file: path.basename(stderrPath),
  stderr_sha256: hashFile(stderrPath),
  command_exit_status: Number(exitStatus),
  validation_status: validationStatus,
  validation_error: validationError || null
};

fs.writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, {flag: "wx"});
