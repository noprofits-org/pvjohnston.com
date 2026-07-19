#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CASE_DIR = path.join(ROOT, "data", "cases");
const TRANSCRIPTION_DIR = path.join(ROOT, "data", "provenance", "transcriptions");

const fail = (message) => {
  throw new Error(`render-case-table: ${message}`);
};

const fraction = ({ numerator, denominator }) => (
  denominator === 1 ? String(numerator) : `${numerator}/${denominator}`
);

const pitch = ({ step, alter, octave }) => {
  const accidental = ({
    "-4": "bbbb", "-3": "bbb", "-2": "bb", "-1": "b",
    0: "", 1: "#", 2: "##", 3: "###", 4: "####"
  })[alter];
  if (accidental === undefined) fail(`unsupported accidental ${alter}`);
  return `${step}${accidental}${octave}`;
};

const clean = (value) => String(value ?? "").replaceAll("\t", " ").replaceAll("\n", " ");

const tableFor = (dossier) => {
  const rows = [[
    "case_id", "window_id", "measure_index", "evidence_id", "record_type",
    "record_id", "onset_qn", "duration_qn", "voice_id", "detail"
  ]];
  for (const window of dossier.windows) {
    for (const measure of window.measures) {
      rows.push([
        dossier.case_id,
        window.window_id,
        measure.measure_index,
        measure.evidence_id,
        "measure",
        "",
        "",
        fraction(measure.notated_duration_qn),
        "",
        `meter=${measure.meter.beats}/${measure.meter.beat_type};key_fifths=${measure.key_signature.fifths};barlines=${measure.left_barline}|${measure.right_barline};volta=${measure.volta}`
      ]);
      for (const event of measure.events) {
        const detail = event.event_type === "note"
          ? `pitch=${pitch(event.pitch)};tie=${event.tie};grace=${event.grace};articulations=${event.articulations.join(",")};ornaments=${event.ornaments.join(",")}`
          : `articulations=${event.articulations.join(",")}`;
        rows.push([
          dossier.case_id,
          window.window_id,
          measure.measure_index,
          measure.evidence_id,
          event.event_type,
          event.event_id,
          fraction(event.onset_qn),
          fraction(event.duration_qn),
          event.voice_id,
          detail
        ]);
      }
      for (const direction of measure.directions) {
        rows.push([
          dossier.case_id,
          window.window_id,
          measure.measure_index,
          measure.evidence_id,
          "direction",
          direction.direction_id,
          fraction(direction.onset_qn),
          "",
          direction.voice_id ?? "",
          `type=${direction.direction_type};value=${direction.value}`
        ]);
      }
    }
  }
  return `${rows.map((row) => row.map(clean).join("\t")).join("\n")}\n`;
};

const main = async () => {
  const args = process.argv.slice(2);
  const check = args.includes("--check");
  const caseIndex = args.indexOf("--case");
  const caseId = caseIndex >= 0 ? args[caseIndex + 1] : null;
  if (!caseId) fail("--case requires a case ID");
  const allowed = new Set(["--check", "--case", caseId]);
  const unexpected = args.filter((arg) => !allowed.has(arg));
  if (unexpected.length > 0) fail(`unexpected argument ${unexpected[0]}`);

  const dossierPath = path.join(CASE_DIR, `${caseId}.json`);
  const dossier = JSON.parse(await readFile(dossierPath, "utf8"));
  if (dossier.case_id !== caseId) fail(`${path.relative(ROOT, dossierPath)} has mismatched case_id`);
  const output = tableFor(dossier);
  const outputPath = path.join(TRANSCRIPTION_DIR, `${caseId}.reverse-rendered.tsv`);
  if (check) {
    const existing = await readFile(outputPath, "utf8");
    if (existing !== output) fail(`${path.relative(ROOT, outputPath)} is not reproducible from the dossier`);
    process.stdout.write(`PASS ${caseId} reverse-render reproducible\n`);
  } else {
    await writeFile(outputPath, output);
    process.stdout.write(`WROTE ${path.relative(ROOT, outputPath)}\n`);
  }
};

await main().catch((error) => {
  process.stderr.write(`${error.stack ?? error}\n`);
  process.exitCode = 1;
});
