#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {parseAndValidateResponse} from "./lib/response-validator.mjs";
import {
  PREFLIGHT_TASKS,
  PREFLIGHT_SOURCE_FILES,
  SYNTHETIC_CASE_ID,
  makePreflightContract,
  makeSyntheticDossier,
  renderSyntheticPrompt,
  safeRelative,
  sha256
} from "./lib/synthetic-preflight.mjs";

const scriptPath = fileURLToPath(import.meta.url);
const scriptDir = path.dirname(scriptPath);
const defaultExperimentDir = path.resolve(scriptDir, "..");

const usage = () => {
  process.stderr.write(
    "usage: run-synthetic-preflight.mjs --model LABEL [--experiment-dir DIR] [--timeout-seconds N]\n"
  );
};

const parseArguments = (argv) => {
  const options = {
    experimentDir: defaultExperimentDir,
    timeoutSeconds: 1200,
    modelLabel: null
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--model") options.modelLabel = argv[++index];
    else if (argument === "--experiment-dir") options.experimentDir = argv[++index];
    else if (argument === "--timeout-seconds") options.timeoutSeconds = Number(argv[++index]);
    else if (argument === "--help" || argument === "-h") {
      usage();
      process.exit(0);
    } else {
      usage();
      throw new Error(`unknown argument: ${argument}`);
    }
  }
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(options.modelLabel ?? "")) {
    throw new Error("--model must be a safe model label from run-matrix.json");
  }
  if (!Number.isSafeInteger(options.timeoutSeconds)
      || options.timeoutSeconds < 1
      || options.timeoutSeconds > 3600) {
    throw new Error("--timeout-seconds must be an integer from 1 through 3600");
  }
  options.experimentDir = path.resolve(options.experimentDir);
  return options;
};

const hashFile = (file) => sha256(fs.readFileSync(file));
const isoNow = () => new Date().toISOString();
const byteLength = (value) => Buffer.byteLength(value ?? "", "utf8");

const classifySpawnError = (error) => {
  if (!error) return null;
  if (error.code === "ETIMEDOUT") return "timeout";
  if (error.code === "ENOBUFS") return "output_limit";
  return "spawn_error";
};

const classifyValidationError = (error) => {
  const message = String(error?.message ?? "");
  if (/unexpected heading sequence/.test(message)) return "heading_contract";
  if (/JSON block|invalid JSON result/.test(message)) return "json_block_contract";
  if (/wrong keys|missing |extra /.test(message)) return "exact_key_contract";
  if (/case mismatch/.test(message)) return "case_id_contract";
  if (/evidence ID|evidence_ids/.test(message)) return "evidence_reference_contract";
  if (/probabilit|sum to 1/.test(message)) return "probability_contract";
  if (/word|nonempty string/.test(message)) return "text_contract";
  return "response_contract";
};

const runOneTask = ({adapterPath, dossier, experimentDir, matrix, task, timeoutSeconds}) => {
  const {promptRelative, promptBody, rendered} = renderSyntheticPrompt({
    experimentDir,
    matrix,
    task,
    dossier
  });
  const stageDir = fs.mkdtempSync(path.join(os.tmpdir(), `off-tonic-preflight-${task}.`));
  const startedAt = isoNow();
  const monotonicStart = process.hrtime.bigint();
  let result;
  try {
    result = spawnSync(adapterPath, [], {
      cwd: stageDir,
      input: rendered,
      encoding: "utf8",
      timeout: timeoutSeconds * 1000,
      maxBuffer: 16 * 1024 * 1024,
      windowsHide: true
    });
  } finally {
    fs.rmSync(stageDir, {recursive: true, force: true});
  }
  const endedAt = isoNow();
  const durationMs = Number((process.hrtime.bigint() - monotonicStart) / 1_000_000n);
  const response = typeof result.stdout === "string" ? result.stdout : "";
  const stderr = typeof result.stderr === "string" ? result.stderr : "";
  const commandError = classifySpawnError(result.error);
  let validationStatus = "not_run";
  let failureCode = commandError;

  if (!commandError && result.status === 0) {
    try {
      parseAndValidateResponse({
        task,
        expectedCase: SYNTHETIC_CASE_ID,
        dossier,
        response
      });
      validationStatus = "valid";
    } catch (error) {
      validationStatus = "invalid";
      failureCode = classifyValidationError(error);
    }
  } else if (!failureCode) {
    failureCode = "adapter_command_failed";
  }

  return {
    task,
    status: !failureCode && validationStatus === "valid" ? "passed" : "failed",
    started_at: startedAt,
    ended_at: endedAt,
    duration_ms: durationMs,
    command_exit_status: result.status,
    command_signal: result.signal,
    validation_status: validationStatus,
    failure_code: failureCode,
    prompt_template: promptRelative,
    prompt_template_sha256: sha256(promptBody),
    rendered_prompt_sha256: sha256(rendered),
    rendered_prompt_bytes: byteLength(rendered),
    response_sha256: sha256(response),
    response_bytes: byteLength(response),
    stderr_sha256: sha256(stderr),
    stderr_bytes: byteLength(stderr)
  };
};

const writeReceipt = ({receiptDir, modelLabel, receipt}) => {
  fs.mkdirSync(receiptDir, {recursive: true});
  const stamp = receipt.started_at.replaceAll(/[-:.]/g, "");
  const name = `${modelLabel}__synthetic-schema__${stamp}__pid-${process.pid}.receipt.json`;
  const receiptPath = path.join(receiptDir, name);
  const body = `${JSON.stringify(receipt, null, 2)}\n`;
  fs.writeFileSync(receiptPath, body, {flag: "wx", mode: 0o444});
  fs.chmodSync(receiptPath, 0o444);
  return {receiptPath, receiptSha256: sha256(body)};
};

const main = () => {
  const options = parseArguments(process.argv.slice(2));
  const matrixPath = path.join(options.experimentDir, "run-matrix.json");
  const matrixBody = fs.readFileSync(matrixPath);
  const matrix = JSON.parse(matrixBody);
  if (matrix.matrix_status !== "development") {
    throw new Error("synthetic preflight must run before the model matrix is frozen");
  }
  const model = matrix.models?.[options.modelLabel];
  if (!model) throw new Error(`model label is absent from run-matrix.json: ${options.modelLabel}`);
  if (model.tool_access !== "none") throw new Error("synthetic preflight requires a no-tools model adapter");

  const adapterRelative = safeRelative(model.adapter, `matrix.models.${options.modelLabel}.adapter`);
  const adapterPath = path.join(options.experimentDir, adapterRelative);
  if ((fs.statSync(adapterPath).mode & 0o111) === 0) throw new Error("model adapter is not executable");
  const adapterSha256 = hashFile(adapterPath);
  if (model.adapter_sha256 !== adapterSha256) {
    throw new Error("model adapter hash differs from run-matrix.json; update the development matrix before preflight");
  }

  for (const task of PREFLIGHT_TASKS) {
    safeRelative(matrix.tasks?.[task]?.prompt, `matrix.tasks.${task}.prompt`);
  }

  const dossier = makeSyntheticDossier();
  const startedAt = isoNow();
  const tasks = PREFLIGHT_TASKS.map((task) => runOneTask({
    adapterPath,
    dossier,
    experimentDir: options.experimentDir,
    matrix,
    task,
    timeoutSeconds: options.timeoutSeconds
  }));
  const endedAt = isoNow();
  const passed = tasks.every((task) => task.status === "passed");

  const sourceFiles = Object.fromEntries(PREFLIGHT_SOURCE_FILES.map((relative) => [
    relative,
    path.join(options.experimentDir, relative)
  ]));
  const receipt = {
    schema_version: "1.0.0",
    receipt_kind: "synthetic_response_contract_preflight",
    status: passed ? "passed" : "failed",
    started_at: startedAt,
    ended_at: endedAt,
    model: {
      label: options.modelLabel,
      provider: model.provider,
      requested_model_id: model.model_id,
      generation_role: model.generation_role,
      experimental_unit: model.experimental_unit,
      cli: model.cli,
      cli_version: model.cli_version,
      tool_access: model.tool_access,
      adapter: adapterRelative,
      adapter_sha256: adapterSha256
    },
    protocol: {
      matrix_contract_sha256: sha256(JSON.stringify(makePreflightContract(matrix, options.modelLabel))),
      dossier_schema_version: dossier.schema_version,
      response_schema_version: "2.1.0",
      synthetic_case_id: SYNTHETIC_CASE_ID,
      synthetic_dossier_sha256: sha256(JSON.stringify(dossier)),
      source_file_sha256: Object.fromEntries(
        Object.entries(sourceFiles).map(([relative, full]) => [relative, hashFile(full)])
      )
    },
    retention: {
      rendered_prompt_body_retained: false,
      response_body_retained: false,
      stderr_body_retained: false,
      real_case_material_accessed: false
    },
    tasks
  };
  const {receiptPath, receiptSha256} = writeReceipt({
    receiptDir: path.join(options.experimentDir, "data", "provenance", "preflight-receipts"),
    modelLabel: options.modelLabel,
    receipt
  });

  const receiptRelative = path.relative(options.experimentDir, receiptPath).split(path.sep).join("/");
  process.stdout.write(`${JSON.stringify({path: receiptRelative, sha256: receiptSha256})}\n`);
  if (!passed) {
    process.stderr.write("Synthetic response-contract preflight failed; only the metadata receipt was retained.\n");
    process.exitCode = 5;
  }
};

try {
  main();
} catch (error) {
  process.stderr.write(`Synthetic preflight setup failed: ${error.message}\n`);
  process.exitCode = 3;
}
