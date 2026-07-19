#!/usr/bin/env node
import path from "node:path";
import {spawnSync} from "node:child_process";

import {verifyCollectionLock} from "./lib/collection-integrity.mjs";
import {inspectScheduledBundle, writeAttemptClaim} from "./lib/scheduled-bundle-integrity.mjs";

const args = process.argv.slice(2);
if (args.length > 1 || args.includes("-h") || args.includes("--help")) {
  process.stdout.write("usage: collect-schedule.mjs [EXPERIMENT_DIR]\n");
  process.exit(args.length > 1 ? 2 : 0);
}

const experimentDir = path.resolve(args[0] ?? path.join(import.meta.dirname, ".."));
const runner = path.join(experimentDir, "scripts", "run-model.sh");

const stop = (message, status) => {
  process.stderr.write(`${message}\n`);
  process.exit(status);
};

try {
  let verified = verifyCollectionLock(experimentDir);
  const schedule = verified.matrix.schedule;
  const inspected = schedule.map((entry) => inspectScheduledBundle(experimentDir, verified, entry));
  const firstEmpty = inspected.findIndex((item) => item.state === "empty");
  const completedPrefix = firstEmpty === -1 ? inspected.length : firstEmpty;

  if (firstEmpty !== -1) {
    const laterComplete = inspected.findIndex((item, index) => index > firstEmpty && item.state === "complete");
    if (laterComplete !== -1) {
      throw new Error(`completed slot ${laterComplete + 1} follows empty slot ${firstEmpty + 1}; schedule order was violated`);
    }
  }
  const earlierFailure = inspected.findIndex((item, index) => (
    index < completedPrefix - 1 && item.outcome === "command_failed"
  ));
  if (earlierFailure !== -1) {
    throw new Error(`completed calls follow provider failure at sequence ${earlierFailure + 1}`);
  }
  if (completedPrefix > 0 && inspected[completedPrefix - 1].outcome === "command_failed") {
    stop(
      `collection remains stopped at consumed provider-failure slot ${completedPrefix}/${schedule.length}; retry is forbidden`,
      5
    );
  }
  if (completedPrefix === schedule.length) {
    process.stdout.write(`collection complete: ${schedule.length}/${schedule.length} verified bundles\n`);
    process.exit(0);
  }
  if (completedPrefix > 0) {
    process.stdout.write(`resume verified: ${completedPrefix}/${schedule.length} contiguous bundles\n`);
  }

  for (let index = completedPrefix; index < schedule.length; index += 1) {
    const entry = schedule[index];
    const label = `${entry.model} ${entry.task} ${entry.case_id} run-${entry.run}`;
    verified = verifyCollectionLock(experimentDir);
    const before = inspectScheduledBundle(experimentDir, verified, entry);
    if (before.state !== "empty") throw new Error(`slot changed before sequence ${entry.sequence}`);
    writeAttemptClaim(experimentDir, verified.manifest, entry);
    verifyCollectionLock(experimentDir);

    process.stdout.write(`starting ${String(entry.sequence).padStart(3, "0")}/${schedule.length}: ${label}\n`);
    const result = spawnSync(runner, [
      "--task", entry.task,
      "--case", entry.case_id,
      "--model", entry.model,
      "--run", entry.run
    ], {
      encoding: null,
      maxBuffer: 4 * 1024 * 1024
    });

    verified = verifyCollectionLock(experimentDir);
    const after = inspectScheduledBundle(experimentDir, verified, entry);
    if (after.state !== "complete") throw new Error(`runner did not finalize sequence ${entry.sequence}`);
    const expectedRunnerStatus = after.outcome === "valid" ? 0 : 5;
    if (result.status !== expectedRunnerStatus || result.signal !== null) {
      throw new Error(`runner exit disagrees with finalized bundle at sequence ${entry.sequence}`);
    }
    process.stdout.write(`finished ${String(entry.sequence).padStart(3, "0")}/${schedule.length}: ${after.outcome}\n`);
    if (after.outcome === "command_failed") {
      stop(`collection stopped on provider/command failure at sequence ${entry.sequence}; slot is consumed and will not be retried`, 5);
    }
  }

  process.stdout.write(`collection complete: ${schedule.length}/${schedule.length} verified bundles\n`);
} catch (error) {
  stop(`collection integrity stop: ${error.message}`, 4);
}
