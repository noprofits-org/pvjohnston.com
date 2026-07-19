#!/usr/bin/env node

import fs from "node:fs";
import {collectEvidenceIds, validateCase} from "./lib/case-validator.mjs";

const [casePath] = process.argv.slice(2);
if (!casePath) {
  throw new Error("usage: validate-case.mjs CASE_JSON (use - for stdin)");
}

const body = casePath === "-" ? fs.readFileSync(0, "utf8") : fs.readFileSync(casePath, "utf8");
let dossier;
try {
  dossier = JSON.parse(body);
} catch (error) {
  throw new Error(`invalid JSON in ${casePath}: ${error.message}`);
}

validateCase(dossier);
process.stdout.write(`valid: ${dossier.case_id} (${collectEvidenceIds(dossier).size} evidence measures)\n`);

