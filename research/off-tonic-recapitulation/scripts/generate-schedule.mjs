import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const write = args.includes("--write");
const experimentDir = path.resolve(args.find((arg) => arg !== "--write") ?? path.join(import.meta.dirname, ".."));
const manifestPath = path.join(experimentDir, "data", "manifest.json");
const matrixPath = path.join(experimentDir, "run-matrix.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const matrix = JSON.parse(fs.readFileSync(matrixPath, "utf8"));
if (!Number.isSafeInteger(matrix.schedule_seed)) throw new Error("set an integer schedule_seed first");
if (!Array.isArray(manifest.cases) || manifest.cases.length !== 6) throw new Error("manifest must contain six cases");
if (Object.keys(matrix.models ?? {}).length !== 3) throw new Error("matrix must contain three models");

let state = matrix.schedule_seed >>> 0;
const random = () => {
  state = (state + 0x6D2B79F5) >>> 0;
  let value = state;
  value = Math.imul(value ^ (value >>> 15), value | 1);
  value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
  return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
};
const slots = [];
for (const task of Object.keys(matrix.tasks)) for (const model of Object.keys(matrix.models)) {
  for (const {case_id: caseId} of manifest.cases) for (const run of ["01", "02", "03"]) {
    slots.push({task, model, case_id: caseId, run});
  }
}
for (let index = slots.length - 1; index > 0; index -= 1) {
  const selected = Math.floor(random() * (index + 1));
  [slots[index], slots[selected]] = [slots[selected], slots[index]];
}
const schedule = slots.map((entry, index) => ({sequence: index + 1, ...entry}));
if (write) {
  matrix.schedule = schedule;
  fs.writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  process.stdout.write(`${matrixPath}\n`);
} else {
  process.stdout.write(`${JSON.stringify(schedule, null, 2)}\n`);
}
