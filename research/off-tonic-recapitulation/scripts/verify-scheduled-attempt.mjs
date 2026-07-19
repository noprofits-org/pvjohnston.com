#!/usr/bin/env node
import path from "node:path";

import {verifyCollectionLock} from "./lib/collection-integrity.mjs";
import {scheduledSlotPaths, verifyAttemptClaim} from "./lib/scheduled-bundle-integrity.mjs";

const [experimentArgument, task, model, caseId, run] = process.argv.slice(2);
if (!experimentArgument || !task || !model || !caseId || !run) {
  throw new Error("usage: verify-scheduled-attempt.mjs EXPERIMENT_DIR TASK MODEL CASE_ID RUN");
}

const experimentDir = path.resolve(experimentArgument);
const verified = verifyCollectionLock(experimentDir);
const matches = verified.matrix.schedule.filter((entry) => (
  entry.task === task
  && entry.model === model
  && entry.case_id === caseId
  && entry.run === run
));
if (matches.length !== 1) {
  throw new Error(`scheduled slot did not resolve exactly once: ${task} ${model} ${caseId} ${run}`);
}

const entry = matches[0];
const paths = scheduledSlotPaths(experimentDir, verified.manifest, entry);
verifyAttemptClaim(experimentDir, paths, entry);
process.stdout.write(`verified attempt claim for sequence ${entry.sequence}\n`);
