import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {PREFLIGHT_SOURCE_FILES, makeSyntheticDossier} from "./lib/synthetic-preflight.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const sourceDir = path.resolve(scriptDir, "..");
const runner = path.join(scriptDir, "run-synthetic-preflight.mjs");
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-preflight-test."));
const experimentDir = path.join(tempRoot, "experiment");

const hash = (body) => crypto.createHash("sha256").update(body).digest("hex");
const hashFile = (file) => hash(fs.readFileSync(file));

const fakeAdapter = ({invalid = false}) => `#!/usr/bin/env node
import fs from "node:fs";
const prompt = fs.readFileSync(0, "utf8");
const caseId = prompt.match(/"case_id":"(CASE-[A-Z0-9]{4})"/)?.[1];
if (!caseId) process.exit(7);
if (${invalid}) {
  process.stdout.write("deliberately invalid synthetic fixture response\\n");
  process.exit(0);
}
const analysis = prompt.startsWith("# Frozen analysis instructions");
const fence = String.fromCharCode(96).repeat(3);
const common = {schema_version:"2.1.0",analyst_model:"local-fixture",case_id:caseId};
const cueNames = ["tonal_stability","thematic_correspondence","preparation_strength","proportional_location","rhetorical_emphasis","rotational_continuation"];
const cues = Object.fromEntries(cueNames.map((cue) => [cue,{score:2,evidence_ids:["E001"],reason:"Observed E001; fixture inference is deliberately limited."}]));
const result = analysis
  ? {...common,cues,status_distribution:{not_recapitulation:0.34,off_tonic_recapitulation:0.33,tonic_double_return:0.33},suspected_recognition:{level:"none",confidence:0},case_note:"This is a fictional schema fixture."}
  : {...common,identification:{recognition_level:"none",composer:null,work:null,movement:null,confidence:0,evidence_ids:["E001"],reason:"No identity is supported by the fictional fixture."}};
const title = analysis ? "# Analysis result" : "# Identification probe result";
process.stdout.write(title + "\\n\\n## Run metadata\\n\\nLocal deterministic fixture.\\n\\n## Machine-readable result\\n\\n" + fence + "json\\n" + JSON.stringify(result) + "\\n" + fence + "\\n\\n## Limitations\\n\\nThis is a fictional integration fixture.\\n");
`;

const run = (model, expectedStatus) => {
  const result = spawnSync(process.execPath, [
    runner,
    "--experiment-dir", experimentDir,
    "--model", model,
    "--timeout-seconds", "30"
  ], {encoding: "utf8"});
  if (result.status !== expectedStatus) {
    throw new Error(`preflight returned ${result.status}\nstdout: ${result.stdout}\nstderr: ${result.stderr}`);
  }
  const reference = JSON.parse(result.stdout);
  const receiptPath = path.join(experimentDir, reference.path);
  assert.equal(hashFile(receiptPath), reference.sha256);
  return {receiptPath, receipt: JSON.parse(fs.readFileSync(receiptPath, "utf8")), result};
};

try {
  fs.mkdirSync(path.join(experimentDir, "prompts"), {recursive: true});
  fs.mkdirSync(path.join(experimentDir, "scripts", "adapters"), {recursive: true});
  for (const relative of PREFLIGHT_SOURCE_FILES) {
    const destination = path.join(experimentDir, relative);
    fs.mkdirSync(path.dirname(destination), {recursive: true});
    fs.copyFileSync(path.join(sourceDir, relative), destination);
  }
  for (const task of ["analysis", "identification"]) {
    fs.copyFileSync(
      path.join(sourceDir, "prompts", `${task}.md`),
      path.join(experimentDir, "prompts", `${task}.md`)
    );
  }

  const adapterDefinitions = [
    ["mock-valid", false],
    ["mock-invalid", true]
  ];
  const models = {};
  for (const [label, invalid] of adapterDefinitions) {
    const adapterRelative = `scripts/adapters/${label}.mjs`;
    const adapterPath = path.join(experimentDir, adapterRelative);
    fs.writeFileSync(adapterPath, fakeAdapter({invalid}), {mode: 0o755});
    fs.chmodSync(adapterPath, 0o755);
    models[label] = {
      provider: "fixture",
      model_id: `${label}-v1`,
      generation_role: "frontier",
      experimental_unit: "deterministic local fixture",
      cli: "fixture",
      cli_version: "1.0.0",
      authentication: "none",
      decoding_settings: "deterministic",
      tool_access: "none",
      adapter: adapterRelative,
      adapter_sha256: hashFile(adapterPath),
      preflight_status: "not_run",
      preflight_receipt: null
    };
  }

  const matrix = {
    schema_version: "2.0.0",
    matrix_status: "development",
    dataset_manifest_sha256: null,
    schedule_seed: null,
    tasks: {
      analysis: {prompt: "prompts/analysis.md", repetitions_per_case: 3},
      identification: {prompt: "prompts/identification.md", repetitions_per_case: 3}
    },
    models,
    schedule: []
  };
  fs.writeFileSync(path.join(experimentDir, "run-matrix.json"), `${JSON.stringify(matrix, null, 2)}\n`);

  const synthetic = makeSyntheticDossier();
  assert.equal(synthetic.case_id, "CASE-SYN0");
  assert.equal(synthetic.windows.reduce((total, window) => total + window.measures.length, 0), 26);
  assert.deepEqual(
    synthetic.windows.flatMap((window) => window.measures).map((measure) => measure.evidence_id),
    Array.from({length: 26}, (_, index) => `E${String(index + 1).padStart(3, "0")}`)
  );

  const passed = run("mock-valid", 0);
  assert.equal(passed.receipt.status, "passed");
  assert.deepEqual(passed.receipt.tasks.map((task) => [task.task, task.status, task.validation_status]), [
    ["analysis", "passed", "valid"],
    ["identification", "passed", "valid"]
  ]);
  assert.deepEqual(passed.receipt.retention, {
    rendered_prompt_body_retained: false,
    response_body_retained: false,
    stderr_body_retained: false,
    real_case_material_accessed: false
  });
  assert.equal(passed.receipt.protocol.synthetic_case_id, "CASE-SYN0");
  assert.equal(passed.receipt.protocol.synthetic_dossier_sha256, hash(JSON.stringify(synthetic)));
  assert.equal(passed.receipt.tasks.every((task) => task.response_bytes > 0), true);
  const receiptText = fs.readFileSync(passed.receiptPath, "utf8");
  assert.equal(receiptText.includes("Machine-readable result"), false);
  assert.equal(receiptText.includes("fixture inference is deliberately limited"), false);
  assert.equal((fs.statSync(passed.receiptPath).mode & 0o222), 0);

  const failed = run("mock-invalid", 5);
  assert.equal(failed.receipt.status, "failed");
  assert.deepEqual(failed.receipt.tasks.map((task) => task.validation_status), ["invalid", "invalid"]);
  assert.deepEqual(failed.receipt.tasks.map((task) => task.failure_code), ["heading_contract", "heading_contract"]);
  assert.match(failed.result.stderr, /only the metadata receipt was retained/);
  assert.equal(fs.readFileSync(failed.receiptPath, "utf8").includes("deliberately invalid"), false);

  const retainedFiles = fs.readdirSync(path.join(experimentDir, "data", "provenance", "preflight-receipts"));
  assert.equal(retainedFiles.length, 2);
  assert.equal(retainedFiles.every((file) => file.endsWith(".receipt.json")), true);

  process.stdout.write("synthetic preflight tests passed\n");
} finally {
  fs.rmSync(tempRoot, {recursive: true, force: true});
}
