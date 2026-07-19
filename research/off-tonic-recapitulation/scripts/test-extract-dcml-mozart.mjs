#!/usr/bin/env node

import assert from "node:assert/strict";
import {spawnSync} from "node:child_process";
import {mkdtempSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {validateCase} from "./lib/case-validator.mjs";

const experimentRoot = resolve(import.meta.dirname, "..");
const extractor = join(experimentRoot, "scripts", "extract-dcml-mozart.mjs");
const sourceRoot = resolve(process.env.DCML_MOZART_ROOT ?? "/private/tmp/dcml-mozart-piano-sonatas");
const temporary = mkdtempSync(join(tmpdir(), "off-tonic-mozart-extractor-"));

const cases = [
  {
    case_id: "CASE-T333",
    work: "K333-1",
    candidate_mc: 95,
    candidate_onset_qn: {numerator: 3, denominator: 1},
    second_part_mc: 65,
    second_part_onset_qn: {numerator: 0, denominator: 1},
    expected: {opening: 9, elapsed: 120, total: 408, events: 442, rests: 37},
  },
  {
    case_id: "CASE-T545",
    work: "K545-1",
    candidate_mc: 42,
    candidate_onset_qn: {numerator: 0, denominator: 1},
    second_part_mc: 29,
    second_part_onset_qn: {numerator: 0, denominator: 1},
    expected: {opening: 8, elapsed: 52, total: 180, events: 465, rests: 49},
  },
  {
    case_id: "CASE-T570",
    work: "K570-1",
    candidate_mc: 133,
    candidate_onset_qn: {numerator: 0, denominator: 1},
    second_part_mc: 80,
    second_part_onset_qn: {numerator: 0, denominator: 1},
    expected: {opening: 8, elapsed: 159, total: 390, events: 212, rests: 25},
  },
];

try {
  for (const fixture of cases) {
    const {expected, ...config} = fixture;
    const configPath = join(temporary, `${config.work}.json`);
    const auditPath = join(temporary, `${config.work}.audit.json`);
    writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);
    const result = spawnSync(process.execPath, [
      extractor,
      "--config", configPath,
      "--source-root", sourceRoot,
      "--audit-out", auditPath,
    ], {encoding: "utf8", maxBuffer: 64 * 1024 * 1024});
    assert.equal(result.status, 0, result.stderr);
    const dossier = JSON.parse(result.stdout);
    validateCase(dossier);
    const audit = JSON.parse(readFileSync(auditPath, "utf8"));

    assert.equal(dossier.windows[0].measures.length, expected.opening);
    assert.deepEqual(dossier.candidate_return.second_part_elapsed_qn, {numerator: expected.elapsed, denominator: 1});
    assert.deepEqual(dossier.candidate_return.second_part_total_qn, {numerator: expected.total, denominator: 1});
    assert.ok(dossier.windows.every((window) => window.measures.every((measure) => measure.key_signature.fifths === 0)));
    assert.equal(audit.checks.all_source_chords_reconciled_with_notes_table, true);
    assert.equal(audit.checks.selected_schema_unsupported_constructs, 0);
    assert.equal(audit.checks.selected_event_count, expected.events);
    assert.equal(audit.checks.selected_rest_count, expected.rests);
    assert.match(audit.dossier_sha256, /^[0-9a-f]{64}$/);

    const repeated = spawnSync(process.execPath, [
      extractor,
      "--config", configPath,
      "--source-root", sourceRoot,
    ], {encoding: "utf8", maxBuffer: 64 * 1024 * 1024});
    assert.equal(repeated.status, 0, repeated.stderr);
    assert.equal(repeated.stdout, result.stdout, `${config.work} extraction is not byte-deterministic`);
  }

  // K333 MC 150 contains the corpus's only hairpin. A nearby legal window
  // verifies that represented directions survive extraction and validation.
  const directionConfig = {
    case_id: "CASE-HAIR",
    work: "K333-1",
    candidate_mc: 139,
    candidate_onset_qn: {numerator: 0, denominator: 1},
    second_part_mc: 65,
    second_part_onset_qn: {numerator: 0, denominator: 1},
  };
  const directionPath = join(temporary, "hairpin.json");
  writeFileSync(directionPath, `${JSON.stringify(directionConfig)}\n`);
  const directionRun = spawnSync(process.execPath, [
    extractor,
    "--config", directionPath,
    "--source-root", sourceRoot,
  ], {encoding: "utf8", maxBuffer: 64 * 1024 * 1024});
  assert.equal(directionRun.status, 0, directionRun.stderr);
  const directionDossier = JSON.parse(directionRun.stdout);
  validateCase(directionDossier);
  const directionValues = directionDossier.windows
    .flatMap((window) => window.measures)
    .flatMap((measure) => measure.directions)
    .map((direction) => direction.value);
  assert.ok(directionValues.includes("crescendo_start"));
  assert.ok(directionValues.includes("crescendo_stop"));

  const invalid = {...cases[1]};
  delete invalid.expected;
  invalid.candidate_onset_qn = {numerator: 1, denominator: 3};
  const invalidPath = join(temporary, "invalid.json");
  writeFileSync(invalidPath, `${JSON.stringify(invalid)}\n`);
  const rejected = spawnSync(process.execPath, [
    extractor,
    "--config", invalidPath,
    "--source-root", sourceRoot,
  ], {encoding: "utf8"});
  assert.notEqual(rejected.status, 0);
  assert.match(rejected.stderr, /candidate onset does not coincide with a notated note/);

  process.stdout.write("DCML Mozart extractor tests passed\n");
} finally {
  rmSync(temporary, {recursive: true, force: true});
}
