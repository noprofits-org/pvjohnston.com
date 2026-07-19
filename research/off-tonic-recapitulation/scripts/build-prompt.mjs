import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {validateCase} from "./lib/case-validator.mjs";

const [experimentDir, task, requestedCase] = process.argv.slice(2);
if (!experimentDir || !task || !requestedCase) {
  throw new Error("usage: build-prompt.mjs EXPERIMENT_DIR TASK CASE_ID");
}

const hash = (body) => crypto.createHash("sha256").update(body).digest("hex");
const safeRelative = (relative) => {
  if (typeof relative !== "string" || path.isAbsolute(relative) || relative.split(path.sep).includes("..")) {
    throw new Error(`unsafe relative path: ${relative}`);
  }
  return relative;
};

const manifestPath = path.join(experimentDir, "data", "manifest.json");
const matrixPath = path.join(experimentDir, "run-matrix.json");
const manifestBody = fs.readFileSync(manifestPath);
const manifest = JSON.parse(manifestBody);
const matrix = JSON.parse(fs.readFileSync(matrixPath, "utf8"));

if (manifest.dataset_status !== "frozen") throw new Error("dataset is not frozen");
if (matrix.matrix_status !== "frozen") throw new Error("run matrix is not frozen");
if (matrix.dataset_manifest_sha256 !== hash(manifestBody)) {
  throw new Error("run matrix does not pin the current dataset manifest");
}
if (!matrix.tasks?.[task]) throw new Error(`task not in frozen run matrix: ${task}`);
if (!Array.isArray(manifest.cases) || manifest.cases.length !== manifest.pilot_case_count) {
  throw new Error("frozen manifest does not contain the declared pilot case count");
}

let matched = null;
for (const entry of manifest.cases) {
  if (!entry || typeof entry.case_id !== "string") throw new Error("invalid case manifest entry");
  const relative = entry.file;
  safeRelative(relative);
  const full = path.join(experimentDir, "data", relative);
  const body = fs.readFileSync(full);
  if (entry.sha256 !== hash(body)) throw new Error(`case hash mismatch: ${relative}`);
  const parsed = JSON.parse(body);
  if (parsed.case_id !== entry.case_id) throw new Error(`manifest/dossier case mismatch: ${relative}`);
  if (entry.case_id === requestedCase) matched = {relative, full, body, parsed};
}
if (!matched) throw new Error(`case not present in frozen manifest: ${requestedCase}`);
validateCase(matched.parsed);

const promptRelative = safeRelative(matrix.tasks[task].prompt);
const promptPath = path.join(experimentDir, promptRelative);
const promptBody = fs.readFileSync(promptPath);
if (manifest.prompt_sha256?.[task] !== hash(promptBody)) throw new Error(`prompt hash mismatch: ${task}`);

const dossierMarker = "{{DOSSIER}}";
const caseMarker = "{{CASE_ID}}";
const prompt = promptBody.toString("utf8");
if (prompt.split(dossierMarker).length !== 2) throw new Error("prompt must contain exactly one dossier marker");
if (prompt.split(caseMarker).length !== 2) throw new Error("prompt must contain exactly one case-ID marker");

process.stdout.write(prompt.replace(caseMarker, requestedCase).replace(
  dossierMarker,
  `--- BEGIN FILE: ${matched.relative} ---\n${matched.body.toString("utf8")}\n--- END FILE: ${matched.relative} ---`
));
