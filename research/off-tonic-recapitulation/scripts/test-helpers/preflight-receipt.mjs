import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  PREFLIGHT_SOURCE_FILES,
  PREFLIGHT_TASKS,
  SYNTHETIC_CASE_ID,
  makePreflightContract,
  makeSyntheticDossier,
  renderSyntheticPrompt
} from "../lib/synthetic-preflight.mjs";

const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const hashFile = (file) => sha256(fs.readFileSync(file));
const fixtureHash = (label) => sha256(`deterministic preflight fixture: ${label}`);

/** Create a metadata-only passed receipt for frozen-input integration tests. */
export function writePassedPreflightReceipt({experimentDir, matrix, modelLabel, date}) {
  const model = matrix.models[modelLabel];
  const timestamp = `${date}T00:00:00.000Z`;
  const syntheticDossier = makeSyntheticDossier();
  const tasks = PREFLIGHT_TASKS.map((task, index) => {
    const {rendered} = renderSyntheticPrompt({experimentDir, matrix, task, dossier: syntheticDossier});
    return {
      task,
      status: "passed",
      started_at: `${date}T00:00:0${index * 2}.000Z`,
      ended_at: `${date}T00:00:0${index * 2 + 1}.000Z`,
      duration_ms: 1000,
      command_exit_status: 0,
      command_signal: null,
      validation_status: "valid",
      failure_code: null,
      prompt_template: matrix.tasks[task].prompt,
      prompt_template_sha256: hashFile(path.join(experimentDir, matrix.tasks[task].prompt)),
      rendered_prompt_sha256: sha256(rendered),
      rendered_prompt_bytes: Buffer.byteLength(rendered, "utf8"),
      response_sha256: fixtureHash(`${modelLabel}:${task}:response`),
      response_bytes: 500,
      stderr_sha256: sha256(""),
      stderr_bytes: 0
    };
  });
  const receipt = {
    schema_version: "1.0.0",
    receipt_kind: "synthetic_response_contract_preflight",
    status: "passed",
    started_at: timestamp,
    ended_at: `${date}T00:00:04.000Z`,
    model: {
      label: modelLabel,
      provider: model.provider,
      requested_model_id: model.model_id,
      generation_role: model.generation_role,
      experimental_unit: model.experimental_unit,
      cli: model.cli,
      cli_version: model.cli_version,
      tool_access: model.tool_access,
      adapter: model.adapter,
      adapter_sha256: model.adapter_sha256
    },
    protocol: {
      matrix_contract_sha256: sha256(JSON.stringify(makePreflightContract(matrix, modelLabel))),
      dossier_schema_version: "3.1.0",
      response_schema_version: "2.1.0",
      synthetic_case_id: SYNTHETIC_CASE_ID,
      synthetic_dossier_sha256: sha256(JSON.stringify(makeSyntheticDossier())),
      source_file_sha256: Object.fromEntries(PREFLIGHT_SOURCE_FILES.map((relative) => [
        relative,
        hashFile(path.join(experimentDir, relative))
      ]))
    },
    retention: {
      rendered_prompt_body_retained: false,
      response_body_retained: false,
      stderr_body_retained: false,
      real_case_material_accessed: false
    },
    tasks
  };
  const relative = `data/provenance/preflight-receipts/${modelLabel}__fixture.receipt.json`;
  const full = path.join(experimentDir, relative);
  fs.mkdirSync(path.dirname(full), {recursive: true});
  const body = `${JSON.stringify(receipt, null, 2)}\n`;
  fs.writeFileSync(full, body);
  return {path: relative, sha256: sha256(body)};
}
