#!/usr/bin/env node

import path from "node:path";

import {
  buildValidatorContractSensitivity,
  writeValidatorContractSensitivity
} from "./lib/validator-contract-sensitivity.mjs";

const experimentDir = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, ".."));
const built = buildValidatorContractSensitivity(experimentDir);
const written = writeValidatorContractSensitivity(experimentDir, built);

process.stdout.write(`${JSON.stringify({
  status: built.result.status,
  output: path.relative(experimentDir, written.path).split(path.sep).join("/"),
  sha256: written.sha256,
  bytes: written.bytes,
  rescued_outputs: built.result.response_accounting.rescued_count,
  sensitivity_valid_analysis_outputs: built.result.response_accounting.sensitivity_valid
}, null, 2)}\n`);
