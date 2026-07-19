#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import {spawn} from "node:child_process";

const [adapterArgument, promptArgument, responseArgument, stderrArgument, timeoutArgument] = process.argv.slice(2);
const timeoutSeconds = Number(timeoutArgument);
if (!adapterArgument || !promptArgument || !responseArgument || !stderrArgument
    || !Number.isSafeInteger(timeoutSeconds) || timeoutSeconds < 1 || timeoutSeconds > 3600) {
  throw new Error(
    "usage: invoke-adapter.mjs ADAPTER PROMPT RESPONSE STDERR TIMEOUT_SECONDS (1..3600)"
  );
}

const adapterPath = path.resolve(adapterArgument);
const promptPath = path.resolve(promptArgument);
const responsePath = path.resolve(responseArgument);
const stderrPath = path.resolve(stderrArgument);
const input = fs.openSync(promptPath, "r");
const output = fs.openSync(responsePath, "wx");
const errors = fs.openSync(stderrPath, "wx");
let timedOut = false;
let settled = false;

const closeDescriptors = () => {
  for (const descriptor of [input, output, errors]) {
    try {
      fs.closeSync(descriptor);
    } catch {
      // The descriptor may already have been closed during an early spawn failure.
    }
  }
};

const child = spawn(adapterPath, [], {
  cwd: path.dirname(promptPath),
  detached: true,
  stdio: [input, output, errors]
});

const timer = setTimeout(() => {
  timedOut = true;
  try {
    process.kill(-child.pid, "SIGKILL");
  } catch {
    try {
      child.kill("SIGKILL");
    } catch {
      // The process may have exited between the timer firing and the kill.
    }
  }
}, timeoutSeconds * 1000);

child.once("error", (error) => {
  if (settled) return;
  settled = true;
  clearTimeout(timer);
  fs.writeSync(errors, `adapter spawn failed: ${error.message}\n`);
  closeDescriptors();
  process.exitCode = 125;
});

child.once("close", (code, signal) => {
  if (settled) return;
  settled = true;
  clearTimeout(timer);
  if (timedOut) {
    fs.writeSync(errors, `adapter timed out after ${timeoutSeconds} seconds and its process group was killed\n`);
    process.exitCode = 124;
  } else if (Number.isInteger(code)) {
    process.exitCode = code;
  } else {
    fs.writeSync(errors, `adapter ended from signal ${signal ?? "unknown"}\n`);
    process.exitCode = 125;
  }
  closeDescriptors();
});
