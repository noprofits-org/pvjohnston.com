import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";

const sourceDir = path.resolve(import.meta.dirname, "..");
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-runner-test."));
const experimentDir = path.join(tempRoot, "experiment");
const datasetVersion = "runner-fixture-v1";
const caseIds = ["CASE-A001", "CASE-A002", "CASE-A003", "CASE-A004", "CASE-A005", "CASE-A006"];

const hash = (body) => crypto.createHash("sha256").update(body).digest("hex");
const hashFile = (file) => hash(fs.readFileSync(file));
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const rational = (numerator, denominator = 1) => ({numerator, denominator});

const run = (args, expectedStatus = 0) => {
  const result = spawnSync(args[0], args.slice(1), {encoding: "utf8"});
  if (result.status !== expectedStatus) {
    throw new Error(
      `command ${args.join(" ")} returned ${result.status}\nstdout: ${result.stdout}\nstderr: ${result.stderr}`
    );
  }
  return result;
};

const makeDossier = (caseId) => {
  let nextEvidence = 1;
  let nextEvent = 1;
  const makeMeasure = (measureIndex) => ({
    measure_index: measureIndex,
    evidence_id: `E${String(nextEvidence++).padStart(3, "0")}`,
    notated_duration_qn: rational(4),
    meter: {beats: 4, beat_type: 4},
    key_signature: {fifths: 0},
    left_barline: "regular",
    right_barline: "regular",
    volta: "none",
    events: [{
      event_id: `EV${String(nextEvent++).padStart(4, "0")}`,
      event_type: "note",
      onset_qn: rational(0),
      duration_qn: rational(4),
      voice_id: "V01",
      pitch: {step: "C", alter: 0, octave: 4},
      tie: "none",
      grace: "none",
      articulations: [],
      ornaments: []
    }],
    directions: []
  });
  const makeWindow = (windowId, role, count) => ({
    window_id: windowId,
    role,
    measures: Array.from({length: count}, (_, index) => makeMeasure(index))
  });
  return {
    schema_version: "3.0.0",
    case_id: caseId,
    condition: "symbolic",
    encoding: {
      common_tonic: "D",
      home_mode: "major",
      duration_unit: "quarter_note",
      measure_numbers: "window_relative",
      pitch_system: "scientific_pitch_diatonic_spelling",
      coverage: {
        notes: "complete",
        rests: "complete",
        voices: "complete",
        meter: "complete",
        key_signatures: "complete",
        dynamics: "complete",
        articulations: "complete",
        ornaments: "complete",
        repeats_and_barlines: "complete"
      }
    },
    candidate_return: {
      window_id: "W3",
      measure_index: 0,
      onset_qn: rational(0),
      second_part_elapsed_qn: rational(40),
      second_part_total_qn: rational(80)
    },
    windows: [
      makeWindow("W1", "opening", 8),
      makeWindow("W2", "pre_candidate", 6),
      makeWindow("W3", "candidate", 6),
      makeWindow("W4", "continuation", 6)
    ]
  };
};

const adapterSource = (analystModel, invalid = false) => [
  "#!/usr/bin/env node",
  "import fs from 'node:fs';",
  "const prompt = fs.readFileSync(0, 'utf8');",
  invalid
    ? "process.stdout.write('deliberately invalid fixture output\\n');"
    : "const caseId = prompt.match(/\"case_id\":\\s*\"(CASE-[A-Z0-9]{4})\"/)?.[1];",
  ...(invalid ? [] : [
    "if (!caseId) throw new Error('case ID not found in rendered prompt');",
    "const isAnalysis = prompt.startsWith('# Frozen analysis instructions');",
    "const fence = String.fromCharCode(96).repeat(3);",
    "const cueNames = ['tonal_stability','thematic_correspondence','preparation_strength','proportional_location','rhetorical_emphasis','rotational_continuation'];",
    "const cues = Object.fromEntries(cueNames.map((name) => [name, {score: 2, evidence_ids: ['E001'], reason: 'Observed E001; the inference is fixture-only.'}]));",
    `const common = {schema_version: '2.1.0', analyst_model: '${analystModel}', case_id: caseId};`,
    "const result = isAnalysis ? {...common, cues, status_distribution: {not_recapitulation: 0.2, off_tonic_recapitulation: 0.4, tonic_double_return: 0.4}, suspected_recognition: {level: 'none', confidence: 0}, case_note: 'A deterministic runner fixture.'} : {...common, identification: {recognition_level: 'none', composer: null, work: null, movement: null, confidence: 0, evidence_ids: ['E001'], reason: 'No specific identity is supported by this fixture.'}};",
    "const title = isAnalysis ? '# Analysis result' : '# Identification probe result';",
    "process.stdout.write(title + '\\n\\n## Run metadata\\n\\nDeterministic local fixture.\\n\\n## Machine-readable result\\n\\n' + fence + 'json\\n' + JSON.stringify(result, null, 2) + '\\n' + fence + '\\n\\n## Limitations\\n\\nThis is a deterministic integration fixture.\\n');"
  ])
].join("\n") + "\n";

const assertBundle = ({task, model, caseId, runKind, runId, valid}) => {
  const kindDirectory = runKind === "scheduled" ? "scheduled" : "diagnostic";
  const idLabel = runKind === "scheduled" ? `run-${runId}` : `diagnostic-${runId}`;
  const base = `${model}__symbolic__${caseId}__${idLabel}`;
  const outputDir = path.join(experimentDir, "outputs", datasetVersion, kindDirectory, task);
  const responseName = `${base}${valid ? "" : ".invalid"}.md`;
  const responsePath = path.join(outputDir, responseName);
  const metadataPath = path.join(outputDir, `${base}.run.json`);
  const stderrPath = path.join(outputDir, `${base}.stderr.txt`);
  const markerPath = path.join(outputDir, `${base}.complete.json`);

  for (const file of [responsePath, metadataPath, stderrPath, markerPath]) {
    assert.equal(fs.existsSync(file), true, `missing bundle member ${file}`);
  }

  const metadata = readJson(metadataPath);
  assert.equal(metadata.schema_version, "2.0.0");
  assert.equal(metadata.task, task);
  assert.equal(metadata.case_id, caseId);
  assert.equal(metadata.model_label, model);
  assert.equal(metadata.run_kind, runKind);
  assert.equal(metadata.run, runId);
  assert.equal(metadata.dataset_version, datasetVersion);
  assert.equal(metadata.command_exit_status, 0);
  assert.equal(metadata.validation_status, valid ? "valid" : "invalid");
  assert.equal(metadata.response_file, responseName);
  assert.equal(metadata.response_sha256, hashFile(responsePath));
  assert.equal(metadata.stderr_sha256, hashFile(stderrPath));
  assert.equal(metadata.collection_lock_sha256, hashFile(path.join(experimentDir, "collection-lock.json")));

  const marker = readJson(markerPath);
  assert.equal(marker.schema_version, "1.0.0");
  assert.equal(marker.metadata_file, path.basename(metadataPath));
  assert.equal(marker.metadata_sha256, hashFile(metadataPath));
  assert.equal(marker.response_file, responseName);
  assert.equal(marker.response_sha256, hashFile(responsePath));
  assert.equal(marker.stderr_file, path.basename(stderrPath));
  assert.equal(marker.stderr_sha256, hashFile(stderrPath));
  assert.equal((fs.statSync(markerPath).mode & 0o222), 0, "completion marker should be read-only");

  return {outputDir, responsePath, metadataPath, stderrPath, markerPath};
};

try {
  fs.cpSync(sourceDir, experimentDir, {
    recursive: true,
    filter: (source) => {
      const relative = path.relative(sourceDir, source);
      return !["data/sources", "outputs", "tmp"].some((excluded) => (
        relative === excluded || relative.startsWith(`${excluded}${path.sep}`)
      ));
    }
  });
  fs.rmSync(path.join(experimentDir, "collection-lock.json"), {force: true});

  const caseDir = path.join(experimentDir, "data", "cases");
  fs.mkdirSync(caseDir, {recursive: true});
  const cases = caseIds.map((caseId) => {
    const relative = `cases/${caseId}.json`;
    const body = `${JSON.stringify(makeDossier(caseId), null, 2)}\n`;
    fs.writeFileSync(path.join(experimentDir, "data", relative), body);
    return {case_id: caseId, file: relative, sha256: hash(body)};
  });

  const manifestPath = path.join(experimentDir, "data", "manifest.json");
  const manifest = readJson(manifestPath);
  Object.assign(manifest, {
    dataset_version: datasetVersion,
    dataset_status: "frozen",
    randomization_seed: 117,
    frozen: "2026-07-18T00:00:00Z",
    cases,
    prompt_sha256: Object.fromEntries(["analysis", "identification"].map((task) => [
      task,
      hashFile(path.join(experimentDir, "prompts", `${task}.md`))
    ]))
  });
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

  const identity = {
    schema_version: "1.0.0",
    status: "frozen",
    cases: caseIds.map((caseId, index) => ({
      case_id: caseId,
      role: index < 2 ? "focal" : index < 4 ? "tonic_control" : "off_tonic_control",
      probe_role: index === 0 ? "positive_control" : "target",
      composer: `Fixture Composer ${index + 1}`,
      work: `Fixture Work ${index + 1}`,
      movement: "first",
      candidate_measure: index + 10,
      accepted_aliases: {composer: [], work: [], movement: []}
    }))
  };
  fs.writeFileSync(
    path.join(experimentDir, "data", "provenance", "identity-key.json"),
    `${JSON.stringify(identity, null, 2)}\n`
  );

  const sourceManifest = {
    schema_version: "1.0.0",
    status: "frozen",
    access_date: "2026-07-18",
    sources: [],
    cases: caseIds.map((caseId, index) => ({case_id: caseId, source_id: `SRC-${index + 1}`}))
  };
  fs.writeFileSync(
    path.join(experimentDir, "data", "provenance", "source-manifest.json"),
    `${JSON.stringify(sourceManifest, null, 2)}\n`
  );

  const adapterDir = path.join(experimentDir, "scripts", "adapters");
  fs.mkdirSync(adapterDir, {recursive: true});
  const modelDefinitions = [
    ["mock-a", false],
    ["mock-b", true],
    ["mock-c", false]
  ];
  const models = {};
  for (const [model, invalid] of modelDefinitions) {
    const adapterRelative = `scripts/adapters/${model}.mjs`;
    const adapterPath = path.join(experimentDir, adapterRelative);
    fs.writeFileSync(adapterPath, adapterSource(model, invalid), {mode: 0o755});
    fs.chmodSync(adapterPath, 0o755);
    models[model] = {
      provider: "fixture",
      model_id: `${model}-v1`,
      cli: "local fixture adapter",
      cli_version: "1.0.0",
      decoding_settings: "deterministic fixture",
      tool_access: "none",
      adapter: adapterRelative,
      adapter_sha256: hashFile(adapterPath)
    };
  }

  const matrixPath = path.join(experimentDir, "run-matrix.json");
  const matrix = readJson(matrixPath);
  Object.assign(matrix, {
    matrix_status: "frozen",
    dataset_manifest_sha256: hashFile(manifestPath),
    schedule_seed: 991,
    models,
    schedule: []
  });
  fs.writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  run([process.execPath, path.join(experimentDir, "scripts", "generate-schedule.mjs"), "--write", experimentDir]);
  assert.equal(readJson(matrixPath).schedule.length, 108);

  const runner = path.join(experimentDir, "scripts", "run-model.sh");
  fs.chmodSync(runner, 0o755);
  run([process.execPath, path.join(experimentDir, "scripts", "create-collection-lock.mjs"), "--write", experimentDir]);
  run([process.execPath, path.join(experimentDir, "scripts", "verify-collection-lock.mjs"), experimentDir]);

  const successful = run([
    runner, "--task", "analysis", "--case", "CASE-A001", "--model", "mock-a", "--run", "01"
  ]);
  const scheduledBundle = assertBundle({
    task: "analysis", model: "mock-a", caseId: "CASE-A001", runKind: "scheduled", runId: "01", valid: true
  });
  assert.equal(successful.stdout.trim(), scheduledBundle.responsePath);
  assert.equal(
    scheduledBundle.outputDir,
    path.join(experimentDir, "outputs", datasetVersion, "scheduled", "analysis")
  );

  const duplicate = run([
    runner, "--task", "analysis", "--case", "CASE-A001", "--model", "mock-a", "--run", "01"
  ], 4);
  assert.match(duplicate.stderr, /Refusing to overwrite existing run/);

  const invalid = run([
    runner, "--task", "identification", "--case", "CASE-A002", "--model", "mock-b", "--run", "02"
  ], 5);
  assert.match(invalid.stderr, /Run retained as .*\.invalid\.md \(invalid\)/);
  const invalidBundle = assertBundle({
    task: "identification", model: "mock-b", caseId: "CASE-A002", runKind: "scheduled", runId: "02", valid: false
  });
  assert.equal(fs.existsSync(invalidBundle.responsePath.replace(".invalid.md", ".md")), false);
  assert.match(readJson(invalidBundle.metadataPath).validation_error, /unexpected heading sequence/);

  const diagnostic = run([
    runner, "--task", "identification", "--case", "CASE-A003", "--model", "mock-c", "--diagnostic", "07"
  ]);
  const diagnosticBundle = assertBundle({
    task: "identification", model: "mock-c", caseId: "CASE-A003", runKind: "diagnostic", runId: "07", valid: true
  });
  assert.equal(diagnostic.stdout.trim(), diagnosticBundle.responsePath);
  assert.equal(diagnosticBundle.responsePath.includes(`${path.sep}diagnostic${path.sep}`), true);
  assert.equal(diagnosticBundle.responsePath.includes(`${path.sep}scheduled${path.sep}`), false);

  process.stdout.write("runner integration test passed\n");
} finally {
  fs.rmSync(tempRoot, {recursive: true, force: true});
}
