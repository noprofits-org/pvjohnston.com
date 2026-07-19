import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";
import {writePassedPreflightReceipt} from "./test-helpers/preflight-receipt.mjs";

const sourceDir = path.resolve(import.meta.dirname, "..");
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-collector-test."));
const experimentDir = path.join(tempRoot, "experiment");
const invocationLog = path.join(tempRoot, "adapter-invocations.txt");
const datasetVersion = "collector-fixture-v1";
const sentinel = "RESPONSE_BODY_MUST_NOT_BE_DISPLAYED";
const caseIds = ["CASE-B001", "CASE-B002", "CASE-B003", "CASE-B004", "CASE-B005", "CASE-B006"];

const hash = (body) => crypto.createHash("sha256").update(body).digest("hex");
const hashFile = (file) => hash(fs.readFileSync(file));
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const rational = (numerator, denominator = 1) => ({numerator, denominator});

const run = (command, expectedStatus = 0) => {
  const result = spawnSync(command[0], command.slice(1), {
    encoding: "utf8",
    env: {...process.env, OFF_TONIC_TEST_INVOCATION_LOG: invocationLog}
  });
  if (result.status !== expectedStatus) {
    throw new Error(
      `command ${command.join(" ")} returned ${result.status}\nstdout: ${result.stdout}\nstderr: ${result.stderr}`
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
    schema_version: "3.1.0",
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

const adapterSource = (model, behavior) => [
  "#!/usr/bin/env node",
  "import fs from 'node:fs';",
  `fs.appendFileSync(process.env.OFF_TONIC_TEST_INVOCATION_LOG, '${model}\\n');`,
  "const prompt = fs.readFileSync(0, 'utf8');",
  ...(behavior === "failed" ? [
    `process.stdout.write('${sentinel}: partial provider stdout\\n');`,
    `process.stderr.write('${sentinel}: private provider stderr\\n');`,
    "process.exit(17);"
  ] : behavior === "invalid" ? [
    `process.stdout.write('${sentinel}: deliberately invalid response\\n');`
  ] : [
    "const caseId = prompt.match(/\"case_id\":\\s*\"(CASE-[A-Z0-9]{4})\"/)?.[1];",
    "if (!caseId) throw new Error('case ID not found in rendered prompt');",
    "const isAnalysis = prompt.startsWith('# Frozen analysis instructions');",
    "const fence = String.fromCharCode(96).repeat(3);",
    "const cueNames = ['tonal_stability','thematic_correspondence','preparation_strength','proportional_location','rhetorical_emphasis','rotational_continuation'];",
    "const cues = Object.fromEntries(cueNames.map((name) => [name, {score: 2, evidence_ids: ['E001'], reason: 'Observed E001; this is fixture-only.'}]));",
    `const common = {schema_version: '2.1.0', analyst_model: '${model}', case_id: caseId};`,
    "const result = isAnalysis ? {...common, cues, status_distribution: {not_recapitulation: 0.2, off_tonic_recapitulation: 0.4, tonic_double_return: 0.4}, suspected_recognition: {level: 'none', confidence: 0}, case_note: 'RESPONSE_BODY_MUST_NOT_BE_DISPLAYED fixture.'} : {...common, identification: {recognition_level: 'none', composer: null, work: null, movement: null, confidence: 0, evidence_ids: ['E001'], reason: 'No specific identity is supported by this fixture.'}};",
    "const title = isAnalysis ? '# Analysis result' : '# Identification probe result';",
    "process.stdout.write(title + '\\n\\n## Run metadata\\n\\nFixture.\\n\\n## Machine-readable result\\n\\n' + fence + 'json\\n' + JSON.stringify(result, null, 2) + '\\n' + fence + '\\n\\n## Limitations\\n\\nThis is a deterministic integration fixture.\\n');"
  ])
].join("\n") + "\n";

const pathsFor = (entry) => {
  const base = `${entry.model}__symbolic__${entry.case_id}__run-${entry.run}`;
  const directory = path.join(experimentDir, "outputs", datasetVersion, "scheduled", entry.task);
  const claimDirectory = path.join(experimentDir, "outputs", datasetVersion, "scheduled", ".claims", entry.task);
  return {
    response: path.join(directory, `${base}.md`),
    invalidResponse: path.join(directory, `${base}.invalid.md`),
    metadata: path.join(directory, `${base}.run.json`),
    stderr: path.join(directory, `${base}.stderr.txt`),
    marker: path.join(directory, `${base}.complete.json`),
    attempt: path.join(claimDirectory, `${base}.attempt.json`)
  };
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

  const cases = caseIds.map((caseId) => {
    const relative = `cases/${caseId}.json`;
    const file = path.join(experimentDir, "data", relative);
    const body = `${JSON.stringify(makeDossier(caseId), null, 2)}\n`;
    fs.writeFileSync(file, body);
    return {case_id: caseId, file: relative, sha256: hash(body)};
  });
  const manifestPath = path.join(experimentDir, "data", "manifest.json");
  const manifest = readJson(manifestPath);
  Object.assign(manifest, {
    dataset_version: datasetVersion,
    dataset_status: "frozen",
    frozen: "2026-07-19T00:00:00Z",
    cases,
    prompt_sha256: Object.fromEntries(["analysis", "identification"].map((task) => [
      task,
      hashFile(path.join(experimentDir, "prompts", `${task}.md`))
    ]))
  });
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

  fs.writeFileSync(path.join(experimentDir, "data", "provenance", "identity-key.json"), `${JSON.stringify({
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
  }, null, 2)}\n`);
  fs.writeFileSync(path.join(experimentDir, "data", "provenance", "source-manifest.json"), `${JSON.stringify({
    schema_version: "1.0.0",
    status: "frozen",
    access_date: "2026-07-19",
    sources: [],
    cases: caseIds.map((caseId, index) => ({case_id: caseId, source_id: `SRC-${index + 1}`}))
  }, null, 2)}\n`);

  const adapterDir = path.join(experimentDir, "scripts", "adapters");
  fs.mkdirSync(adapterDir, {recursive: true});
  const definitions = [
    ["mock-a", "valid"],
    ["mock-b", "invalid"],
    ["mock-c", "failed"]
  ];
  const models = {};
  for (const [model, behavior] of definitions) {
    const adapterRelative = `scripts/adapters/${model}.mjs`;
    const adapterPath = path.join(experimentDir, adapterRelative);
    fs.writeFileSync(adapterPath, adapterSource(model, behavior), {mode: 0o755});
    fs.chmodSync(adapterPath, 0o755);
    models[model] = {
      provider: model === "mock-b" ? "fixture-family-two" : "fixture-family-one",
      model_id: `${model}-v1`,
      generation_role: model === "mock-c" ? "prior_generation_active_not_deprecated" : "frontier",
      experimental_unit: "local fixture model system",
      cli: "local fixture adapter",
      cli_version: "1.0.0",
      authentication: "local fixture",
      decoding_settings: "deterministic fixture",
      tool_access: "none",
      adapter: adapterRelative,
      adapter_sha256: hashFile(adapterPath),
      preflight_status: "passed_no_outcome_2026-07-19",
      preflight_receipt: null
    };
  }

  const allSlots = [];
  for (const task of ["analysis", "identification"]) for (const model of Object.keys(models)) {
    for (const caseId of caseIds) for (const runId of ["01", "02", "03"]) {
      allSlots.push({task, model, case_id: caseId, run: runId});
    }
  }
  const prioritized = [
    {task: "analysis", model: "mock-a", case_id: "CASE-B001", run: "01"},
    {task: "identification", model: "mock-b", case_id: "CASE-B002", run: "02"},
    {task: "analysis", model: "mock-c", case_id: "CASE-B003", run: "03"},
    {task: "identification", model: "mock-a", case_id: "CASE-B004", run: "01"},
    {task: "analysis", model: "mock-a", case_id: "CASE-B005", run: "02"}
  ];
  const slotKey = (entry) => `${entry.task}\u0000${entry.model}\u0000${entry.case_id}\u0000${entry.run}`;
  const prioritizedKeys = new Set(prioritized.map(slotKey));
  const schedule = [...prioritized, ...allSlots.filter((entry) => !prioritizedKeys.has(slotKey(entry)))]
    .map((entry, index) => ({sequence: index + 1, ...entry}));
  assert.equal(schedule.length, 108);

  const matrixPath = path.join(experimentDir, "run-matrix.json");
  const matrix = readJson(matrixPath);
  Object.assign(matrix, {
    matrix_status: "frozen",
    dataset_manifest_sha256: hashFile(manifestPath),
    schedule_seed: 557,
    models,
    schedule
  });
  for (const model of Object.keys(models)) {
    models[model].preflight_receipt = writePassedPreflightReceipt({
      experimentDir,
      matrix,
      modelLabel: model,
      date: "2026-07-19"
    });
  }
  fs.writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  const createLock = path.join(experimentDir, "scripts", "create-collection-lock.mjs");
  const collector = path.join(experimentDir, "scripts", "collect-schedule.mjs");
  const runner = path.join(experimentDir, "scripts", "run-model.sh");
  run([process.execPath, createLock, "--write", experimentDir]);
  const collectionLock = readJson(path.join(experimentDir, "collection-lock.json"));
  assert.match(collectionLock.files["scripts/collect-schedule.mjs"], /^[0-9a-f]{64}$/);
  assert.match(collectionLock.files["scripts/lib/scheduled-bundle-integrity.mjs"], /^[0-9a-f]{64}$/);

  const first = run([process.execPath, collector, experimentDir], 5);
  assert.doesNotMatch(`${first.stdout}\n${first.stderr}`, new RegExp(sentinel));
  assert.match(first.stdout, /finished 002\/108: invalid/);
  assert.match(first.stderr, /stopped on provider\/command failure at sequence 3/);
  assert.deepEqual(fs.readFileSync(invocationLog, "utf8").trim().split("\n"), ["mock-a", "mock-b", "mock-c"]);

  for (const [index, outcome] of ["valid", "invalid", "command_failed"].entries()) {
    const paths = pathsFor(schedule[index]);
    const metadata = readJson(paths.metadata);
    assert.equal(metadata.validation_status, outcome);
    assert.equal(fs.existsSync(paths.attempt), true);
    assert.equal((fs.statSync(paths.attempt).mode & 0o222), 0);
  }
  assert.equal(fs.existsSync(pathsFor(schedule[3]).attempt), false);

  const hashesBeforeResume = Object.values(pathsFor(schedule[2]))
    .filter((file) => fs.existsSync(file))
    .map((file) => [file, hashFile(file)]);
  const resumed = run([process.execPath, collector, experimentDir], 5);
  assert.doesNotMatch(`${resumed.stdout}\n${resumed.stderr}`, new RegExp(sentinel));
  assert.match(resumed.stderr, /remains stopped at consumed provider-failure slot 3\/108/);
  assert.equal(fs.readFileSync(invocationLog, "utf8").trim().split("\n").length, 3);
  for (const [file, expectedHash] of hashesBeforeResume) assert.equal(hashFile(file), expectedHash);

  const outOfOrder = schedule[4];
  const rejectedDirectRun = run([runner,
    "--task", outOfOrder.task,
    "--case", outOfOrder.case_id,
    "--model", outOfOrder.model,
    "--run", outOfOrder.run
  ], 4);
  assert.match(rejectedDirectRun.stderr, /Scheduled attempt claim verification failed; no model was contacted/);
  assert.equal(fs.readFileSync(invocationLog, "utf8").trim().split("\n").length, 3);

  const outOfOrderPaths = pathsFor(outOfOrder);
  fs.mkdirSync(path.dirname(outOfOrderPaths.attempt), {recursive: true});
  fs.writeFileSync(outOfOrderPaths.attempt, `${JSON.stringify({
    schema_version: "1.0.0",
    sequence: outOfOrder.sequence,
    task: outOfOrder.task,
    model: outOfOrder.model,
    case_id: outOfOrder.case_id,
    run: outOfOrder.run,
    collection_lock_sha256: hashFile(path.join(experimentDir, "collection-lock.json")),
    claimed_at: new Date().toISOString()
  }, null, 2)}\n`, {mode: 0o444});
  fs.chmodSync(outOfOrderPaths.attempt, 0o444);
  run([runner,
    "--task", outOfOrder.task,
    "--case", outOfOrder.case_id,
    "--model", outOfOrder.model,
    "--run", outOfOrder.run
  ]);
  const rejectedOrder = run([process.execPath, collector, experimentDir], 4);
  assert.match(rejectedOrder.stderr, /schedule order was violated/);
  for (const task of ["analysis", "identification"]) {
    const taskDir = path.join(experimentDir, "outputs", datasetVersion, "scheduled", task);
    assert.equal(fs.readdirSync(taskDir).some((name) => name.endsWith(".attempt.json")), false);
  }

  for (const file of Object.values(outOfOrderPaths)) {
    if (fs.existsSync(file)) fs.rmSync(file, {force: true});
  }
  fs.rmSync(pathsFor(schedule[2]).marker);
  const rejectedPartial = run([process.execPath, collector, experimentDir], 4);
  assert.match(rejectedPartial.stderr, /partial or ambiguous bundle at sequence 3; retry is forbidden/);
  assert.equal(fs.readFileSync(invocationLog, "utf8").trim().split("\n").length, 4);

  const failedSlotPaths = pathsFor(schedule[2]);
  for (const file of [
    failedSlotPaths.response,
    failedSlotPaths.invalidResponse,
    failedSlotPaths.metadata,
    failedSlotPaths.stderr,
    failedSlotPaths.marker
  ]) {
    if (fs.existsSync(file)) fs.rmSync(file, {force: true});
  }
  const rejectedAttemptOnly = run([process.execPath, collector, experimentDir], 4);
  assert.match(rejectedAttemptOnly.stderr, /attempted slot has no complete bundle at sequence 3; retry is forbidden/);
  assert.equal(fs.readFileSync(invocationLog, "utf8").trim().split("\n").length, 4);

  process.stdout.write("collection orchestrator integration test passed\n");
} finally {
  fs.rmSync(tempRoot, {recursive: true, force: true});
}
