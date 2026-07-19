#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const experimentDir = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, ".."));

const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};

const regularFilesUnder = (root) => {
  const files = [];
  const visit = (directory) => {
    for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
      const target = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(target);
      else {
        assert(entry.isFile(), `immutable-mode target is not a regular file: ${target}`);
        files.push(target);
      }
    }
  };
  visit(root);
  return files.sort();
};

assert(fs.existsSync(path.join(experimentDir, "collection-lock.json")),
  "experiment directory lacks collection-lock.json");
assert(fs.existsSync(path.join(experimentDir, "data", "manifest.json")),
  "experiment directory lacks data/manifest.json");

const scheduledFiles = regularFilesUnder(
  path.join(experimentDir, "outputs", "1.0.0", "scheduled")
);
const receiptFiles = regularFilesUnder(
  path.join(experimentDir, "data", "provenance", "preflight-receipts")
);
const adjudicationDir = path.join(experimentDir, "data", "provenance", "adjudication");
const adjudicationFiles = [
  "identification-adjudication-reconciliation.json",
  "identification-scorer-filename-map.json",
  "identification-scorer-key.json",
  "identification-scorer-packet.json"
].map((name) => path.join(adjudicationDir, name));

assert(scheduledFiles.length === 540,
  `expected 540 scheduled artifacts, found ${scheduledFiles.length}`);
assert(receiptFiles.length === 7,
  `expected 7 preflight receipts, found ${receiptFiles.length}`);
for (const target of adjudicationFiles) {
  assert(fs.statSync(target).isFile(), `missing adjudication artifact: ${target}`);
}

const targets = [...scheduledFiles, ...receiptFiles, ...adjudicationFiles];
assert(new Set(targets).size === 551, "immutable-mode target set is not unique");

for (const target of targets) {
  const mode = fs.statSync(target).mode;
  fs.chmodSync(target, mode & ~0o222);
}
for (const target of targets) {
  assert((fs.statSync(target).mode & 0o222) === 0,
    `failed to restore read-only mode: ${target}`);
}

process.stdout.write(`restored read-only modes for ${targets.length} frozen files\n`);
