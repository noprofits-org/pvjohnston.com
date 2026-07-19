#!/usr/bin/env node

import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import {existsSync, linkSync, readFileSync, unlinkSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {validateCase} from "./lib/case-validator.mjs";

const usage = () => {
  process.stderr.write([
    "Usage:",
    "  node scripts/extract-dcml-mozart.mjs --config CONFIG.json --source-root DCML_REPO [--out DOSSIER.json] [--audit-out AUDIT.json]",
    "",
    "The strict operator config contains exactly:",
    "  case_id, work, candidate_mc, candidate_onset_qn, second_part_mc, second_part_onset_qn,",
    "  source_score_corrections",
    "where rational values use {\"numerator\":N,\"denominator\":D}.",
    "Allowed works: K333-1, K545-1, K570-1, K576-1.",
    "",
  ].join("\n"));
};

const args = process.argv.slice(2);
const options = new Map();
for (let index = 0; index < args.length; index += 2) {
  const flag = args[index];
  const value = args[index + 1];
  if (!["--config", "--source-root", "--out", "--audit-out"].includes(flag) || value === undefined) {
    usage();
    process.exit(2);
  }
  if (options.has(flag)) {
    process.stderr.write(`Duplicate option: ${flag}\n`);
    process.exit(2);
  }
  options.set(flag, value);
}
if (!options.has("--config") || !options.has("--source-root")) {
  usage();
  process.exit(2);
}

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const helper = resolve(scriptDirectory, "lib", "extract-dcml-mozart.py");
const configPath = resolve(options.get("--config"));
const sourceRoot = resolve(options.get("--source-root"));

let configText;
try {
  configText = readFileSync(configPath, "utf8");
  JSON.parse(configText);
} catch (error) {
  process.stderr.write(`Could not read valid JSON config ${configPath}: ${error.message}\n`);
  process.exit(2);
}

const extracted = spawnSync("python3", [helper, sourceRoot], {
  input: configText,
  encoding: "utf8",
  maxBuffer: 64 * 1024 * 1024,
});
if (extracted.error) {
  process.stderr.write(`Could not start extractor helper: ${extracted.error.message}\n`);
  process.exit(1);
}
if (extracted.status !== 0) {
  process.stderr.write(extracted.stderr || `Extractor helper exited ${extracted.status}\n`);
  process.exit(extracted.status ?? 1);
}

let packageValue;
try {
  packageValue = JSON.parse(extracted.stdout);
  validateCase(packageValue.dossier);
} catch (error) {
  process.stderr.write(`Generated dossier failed validation: ${error.message}\n`);
  process.exit(1);
}

const dossierText = `${JSON.stringify(packageValue.dossier, null, 2)}\n`;
packageValue.audit.dossier_sha256 = createHash("sha256").update(dossierText).digest("hex");
packageValue.audit.generated_by = "scripts/extract-dcml-mozart.mjs";
const auditText = `${JSON.stringify(packageValue.audit, null, 2)}\n`;

const fileTargets = [options.get("--out"), options.get("--audit-out")]
  .filter((target) => target !== undefined)
  .map((target) => resolve(target));
if (new Set(fileTargets).size !== fileTargets.length) {
  process.stderr.write("Dossier and audit outputs must use distinct paths.\n");
  process.exit(2);
}
for (const target of fileTargets) {
  if (existsSync(target)) {
    process.stderr.write(`Could not write extraction output: refusing to overwrite existing file ${target}\n`);
    process.exit(1);
  }
}

const writeAtomic = (target, contents) => {
  const absolute = resolve(target);
  const temporary = `${absolute}.tmp-${process.pid}`;
  writeFileSync(temporary, contents, {encoding: "utf8", flag: "wx"});
  try {
    // An atomic hard-link install refuses EEXIST even if another researcher
    // creates the destination after the preflight check.
    linkSync(temporary, absolute);
  } finally {
    unlinkSync(temporary);
  }
};

try {
  if (options.has("--out")) writeAtomic(options.get("--out"), dossierText);
  else process.stdout.write(dossierText);
  if (options.has("--audit-out")) writeAtomic(options.get("--audit-out"), auditText);
} catch (error) {
  process.stderr.write(`Could not write extraction output: ${error.message}\n`);
  process.exit(1);
}
