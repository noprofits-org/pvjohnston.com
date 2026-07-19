import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import {spawnSync} from "node:child_process";

const sourceDir = path.resolve(import.meta.dirname, "..");
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-analyzer-test."));
const experimentDir = path.join(tempRoot, "experiment");
const hash = (body) => crypto.createHash("sha256").update(body).digest("hex");
const hashFile = (file) => hash(fs.readFileSync(file));
const fence = String.fromCharCode(96).repeat(3);
const caseIds = ["CASE-A001", "CASE-A002", "CASE-A003", "CASE-A004", "CASE-A005", "CASE-A006"];
const models = ["model-a", "model-b", "model-c"];
const runs = ["01", "02", "03"];
const cues = [
  "tonal_stability",
  "thematic_correspondence",
  "preparation_strength",
  "proportional_location",
  "rhetorical_emphasis",
  "rotational_continuation"
];

const run = (command, args) => {
  const result = spawnSync(command, args, {encoding: "utf8", maxBuffer: 5 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return result;
};

const rational = (numerator, denominator = 1) => ({numerator, denominator});
const buildDossier = (caseId, pitchOffset) => {
  let evidence = 1;
  let event = 1;
  const makeMeasure = (measureIndex) => ({
    measure_index: measureIndex,
    evidence_id: `E${String(evidence++).padStart(3, "0")}`,
    notated_duration_qn: rational(4),
    meter: {beats: 4, beat_type: 4},
    key_signature: {fifths: 0},
    left_barline: "regular",
    right_barline: "regular",
    volta: "none",
    events: [{
      event_id: `EV${String(event++).padStart(4, "0")}`,
      event_type: "note",
      onset_qn: rational(0),
      duration_qn: rational(4),
      voice_id: "V01",
      articulations: [],
      pitch: {step: ["C", "D", "E", "F", "G", "A"][pitchOffset], alter: 0, octave: 4},
      tie: "none",
      grace: "none",
      ornaments: []
    }],
    directions: []
  });
  const window = (windowId, role, count) => ({
    window_id: windowId,
    role,
    measures: Array.from({length: count}, (_, index) => makeMeasure(index))
  });
  return {
    schema_version: "3.0.0",
    case_id: caseId,
    condition: "symbolic",
    encoding: {
      common_tonic: "C",
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
      window("W1", "opening", 8),
      window("W2", "pre_candidate", 6),
      window("W3", "candidate", 6),
      window("W4", "continuation", 6)
    ]
  };
};

const buildRenderedPrompt = (matrix, manifest, task, caseId) => {
  const entry = manifest.cases.find((item) => item.case_id === caseId);
  const dossierBody = fs.readFileSync(path.join(experimentDir, "data", entry.file), "utf8");
  const prompt = fs.readFileSync(path.join(experimentDir, matrix.tasks[task].prompt), "utf8");
  return prompt.replace("{{CASE_ID}}", caseId).replace(
    "{{DOSSIER}}",
    `--- BEGIN FILE: ${entry.file} ---\n${dossierBody}\n--- END FILE: ${entry.file} ---`
  );
};

const analysisResponse = (caseId, caseIndex) => {
  const cueValues = Object.fromEntries(cues.map((cue, cueIndex) => [cue, {
    score: (caseIndex + cueIndex) % 5,
    evidence_ids: ["E001"],
    reason: "The encoded event is observed; the score is a fixture inference."
  }]));
  const payload = {
    schema_version: "2.0.0",
    analyst_model: "fixture-model",
    case_id: caseId,
    cues: cueValues,
    status_distribution: {
      not_recapitulation: 0.2,
      off_tonic_recapitulation: 0.4,
      tonic_double_return: 0.4
    },
    case_note: "Deterministic fixture result."
  };
  return `# Analysis result\n\n## Run metadata\n\nFixture metadata.\n\n## Machine-readable result\n\n${fence}json\n${JSON.stringify(payload, null, 2)}\n${fence}\n\n## Limitations\n\nSynthetic fixture only.\n`;
};

const identificationResponse = (caseId, recognized) => {
  const identification = recognized ? {
    recognition_level: "specific_candidate",
    composer: "Fixture Composer",
    work: "Fixture Work",
    movement: "First movement",
    confidence: 0.9,
    evidence_ids: ["E001"],
    reason: "The opening event supports the fixture candidate."
  } : {
    recognition_level: "none",
    composer: null,
    work: null,
    movement: null,
    confidence: 0,
    evidence_ids: ["E001"],
    reason: "The fixture provides no specific identification."
  };
  const payload = {
    schema_version: "2.0.0",
    analyst_model: "fixture-model",
    case_id: caseId,
    identification
  };
  return `# Identification probe result\n\n## Run metadata\n\nFixture metadata.\n\n## Machine-readable result\n\n${fence}json\n${JSON.stringify(payload, null, 2)}\n${fence}\n\n## Limitations\n\nSynthetic fixture only.\n`;
};

try {
  fs.cpSync(sourceDir, experimentDir, {recursive: true});

  const cases = [];
  for (const [index, caseId] of caseIds.entries()) {
    const relative = `cases/${caseId}.json`;
    const body = `${JSON.stringify(buildDossier(caseId, index), null, 2)}\n`;
    fs.writeFileSync(path.join(experimentDir, "data", relative), body);
    cases.push({case_id: caseId, file: relative, sha256: hash(body)});
  }

  const manifestPath = path.join(experimentDir, "data", "manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  Object.assign(manifest, {
    dataset_version: "test-1",
    dataset_status: "frozen",
    randomization_seed: 1701,
    frozen: "2026-07-18T00:00:00Z",
    cases
  });
  for (const task of ["analysis", "identification"]) {
    manifest.prompt_sha256[task] = hashFile(path.join(experimentDir, "prompts", `${task}.md`));
  }
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

  const adapterDir = path.join(experimentDir, "scripts", "adapters");
  fs.mkdirSync(adapterDir, {recursive: true});
  const modelSpecs = {};
  for (const model of models) {
    const adapterRelative = `scripts/adapters/${model}.sh`;
    const adapterPath = path.join(experimentDir, adapterRelative);
    fs.writeFileSync(adapterPath, `#!/bin/sh\n# ${model} fixture adapter\nexit 0\n`);
    fs.chmodSync(adapterPath, 0o755);
    modelSpecs[model] = {
      provider: "fixture-provider",
      model_id: `${model}-1`,
      cli: "fixture-cli",
      cli_version: "1.0.0",
      decoding_settings: "deterministic",
      tool_access: "none",
      adapter: adapterRelative,
      adapter_sha256: hashFile(adapterPath)
    };
  }

  const matrixPath = path.join(experimentDir, "run-matrix.json");
  const matrix = JSON.parse(fs.readFileSync(matrixPath, "utf8"));
  matrix.matrix_status = "frozen";
  matrix.dataset_manifest_sha256 = hashFile(manifestPath);
  matrix.schedule_seed = 1703;
  matrix.models = modelSpecs;
  matrix.schedule = [];
  for (const task of ["analysis", "identification"]) for (const model of models) {
    for (const caseId of caseIds) for (const runId of runs) {
      matrix.schedule.push({
        sequence: matrix.schedule.length + 1,
        task,
        model,
        case_id: caseId,
        run: runId
      });
    }
  }
  fs.writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  const identityPath = path.join(experimentDir, "data", "provenance", "identity-key.json");
  const identity = {
    schema_version: "1.0.0",
    status: "frozen",
    cases: caseIds.map((caseId, index) => ({
      case_id: caseId,
      role: index < 2 ? "focal" : index < 4 ? "tonic_control" : "off_tonic_control",
      probe_role: index === 5 ? "positive_control" : "target",
      composer: `Fixture Composer ${index + 1}`,
      work: `Fixture Piece ${index + 1}`,
      movement: "First movement",
      candidate_measure: "1",
      accepted_aliases: {}
    }))
  };
  fs.writeFileSync(identityPath, `${JSON.stringify(identity, null, 2)}\n`);

  const sourceManifestPath = path.join(experimentDir, "data", "provenance", "source-manifest.json");
  const sourceManifest = {
    schema_version: "1.0.0",
    status: "frozen",
    sources: [],
    cases: caseIds.map((caseId) => ({case_id: caseId}))
  };
  fs.writeFileSync(sourceManifestPath, `${JSON.stringify(sourceManifest, null, 2)}\n`);

  const createLock = path.join(experimentDir, "scripts", "create-collection-lock.mjs");
  run(process.execPath, [createLock, "--write", experimentDir]);
  const lockPath = path.join(experimentDir, "collection-lock.json");

  const judgments = [];
  for (const slot of matrix.schedule) {
    const outputDir = path.join(experimentDir, "outputs", manifest.dataset_version, "scheduled", slot.task);
    fs.mkdirSync(outputDir, {recursive: true});
    const base = `${slot.model}__symbolic__${slot.case_id}__run-${slot.run}`;
    const responsePath = path.join(outputDir, `${base}.md`);
    const stderrPath = path.join(outputDir, `${base}.stderr.txt`);
    const metadataPath = path.join(outputDir, `${base}.run.json`);
    const markerPath = path.join(outputDir, `${base}.complete.json`);
    const caseIndex = caseIds.indexOf(slot.case_id);
    const recognized = slot.task === "identification"
      && slot.case_id === "CASE-A006"
      && slot.model === "model-a"
      && ["01", "02"].includes(slot.run);
    const response = slot.task === "analysis"
      ? analysisResponse(slot.case_id, caseIndex)
      : identificationResponse(slot.case_id, recognized);
    fs.writeFileSync(responsePath, response);
    fs.writeFileSync(stderrPath, "");

    const entry = manifest.cases.find((item) => item.case_id === slot.case_id);
    const modelSpec = matrix.models[slot.model];
    const metadata = {
      schema_version: "2.0.0",
      task: slot.task,
      case_id: slot.case_id,
      model_label: slot.model,
      run_kind: "scheduled",
      run: slot.run,
      requested_model_spec: modelSpec,
      observed_model_version: null,
      provider_request_id: null,
      invocation: [modelSpec.adapter],
      started_at: "2026-07-18T01:00:00Z",
      ended_at: "2026-07-18T01:00:01Z",
      dataset_version: manifest.dataset_version,
      dataset_manifest_sha256: hashFile(manifestPath),
      run_matrix_sha256: hashFile(matrixPath),
      collection_lock_sha256: hashFile(lockPath),
      adapter_sha256: hashFile(path.join(experimentDir, modelSpec.adapter)),
      prompt_template_sha256: hashFile(path.join(experimentDir, matrix.tasks[slot.task].prompt)),
      rendered_prompt_sha256: hash(buildRenderedPrompt(matrix, manifest, slot.task, slot.case_id)),
      dossier_sha256: hashFile(path.join(experimentDir, "data", entry.file)),
      response_file: path.basename(responsePath),
      response_sha256: hashFile(responsePath),
      stderr_file: path.basename(stderrPath),
      stderr_sha256: hashFile(stderrPath),
      command_exit_status: 0,
      validation_status: "valid",
      validation_error: null
    };
    fs.writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`);
    const marker = {
      schema_version: "1.0.0",
      completed_at: "2026-07-18T01:00:02Z",
      metadata_file: path.basename(metadataPath),
      metadata_sha256: hashFile(metadataPath),
      response_file: path.basename(responsePath),
      response_sha256: hashFile(responsePath),
      stderr_file: path.basename(stderrPath),
      stderr_sha256: hashFile(stderrPath)
    };
    fs.writeFileSync(markerPath, `${JSON.stringify(marker, null, 2)}\n`);
    if (slot.task === "identification") {
      judgments.push({
        output: path.basename(responsePath),
        level: recognized ? "L2" : "L0",
        reason: recognized ? "Positive-control fixture match." : "Fixture abstention."
      });
    }
  }

  const adjudicationPath = path.join(experimentDir, "data", "provenance", "identification-adjudication.json");
  const adjudication = JSON.parse(fs.readFileSync(adjudicationPath, "utf8"));
  adjudication.status = "complete";
  adjudication.judgments = judgments;
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(adjudication, null, 2)}\n`);

  const diagnosticDir = path.join(experimentDir, "outputs", manifest.dataset_version, "diagnostic", "analysis");
  fs.mkdirSync(diagnosticDir, {recursive: true});
  fs.writeFileSync(path.join(diagnosticDir, "diagnostic-only.md"), "ignored diagnostic");

  const analyzer = path.join(experimentDir, "scripts", "analyze-results.mjs");
  const analyze = () => JSON.parse(run(process.execPath, [analyzer, experimentDir]).stdout);
  const baseline = analyze();
  assert.equal(baseline.valid_analysis_invocations, 54);
  assert.equal(baseline.non_null_cue_cells, 324);
  assert.equal(baseline.collection_integrity.scheduled_slot_status_counts.analysis.valid, 54);
  assert.equal(baseline.collection_integrity.scheduled_slot_status_counts.identification.valid, 54);
  assert.deepEqual(baseline.collection_integrity.unexpected_scheduled_artifacts, []);
  assert.equal(baseline.repeatable_models.length, 3);
  assert.equal(baseline.nondegenerate_cues.length, 6);
  assert.equal(baseline.identification.level_counts.L0, 52);
  assert.equal(baseline.identification.level_counts.L2, 2);
  assert.deepEqual(baseline.identification.target_l2_events, []);
  assert.equal(baseline.identification.positive_control.sensitivity_detected, true);
  assert.ok(baseline.identification.repeatability_by_category.overall.pairwise_comparisons > 0);
  assert.equal(baseline.identification.gate, true);
  assert.equal(baseline.preliminary_gates.output_gate, true);
  assert.equal(baseline.automatic_expansion_gate, true);

  const originalAdjudication = fs.readFileSync(adjudicationPath);
  const isolatedLeakage = JSON.parse(originalAdjudication);
  isolatedLeakage.judgments.find((judgment) =>
    judgment.output === "model-b__symbolic__CASE-A001__run-01.md"
  ).level = "L2";
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(isolatedLeakage, null, 2)}\n`);
  const isolatedLeakageSummary = analyze();
  assert.equal(isolatedLeakageSummary.identification.target_l2_events.length, 1);
  assert.deepEqual(isolatedLeakageSummary.identification.compromised_target_dossiers, []);
  assert.equal(isolatedLeakageSummary.identification.gate, false);
  fs.writeFileSync(adjudicationPath, originalAdjudication);

  const insensitiveProbe = JSON.parse(originalAdjudication);
  for (const judgment of insensitiveProbe.judgments) {
    if (judgment.level === "L2") judgment.level = "L0";
  }
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(insensitiveProbe, null, 2)}\n`);
  const insensitiveProbeSummary = analyze();
  assert.equal(insensitiveProbeSummary.identification.positive_control.sensitivity_detected, false);
  assert.equal(insensitiveProbeSummary.identification.gate, false);
  fs.writeFileSync(adjudicationPath, originalAdjudication);

  const targetDir = path.join(experimentDir, "outputs", manifest.dataset_version, "scheduled", "analysis");
  const targetBase = "model-a__symbolic__CASE-A001__run-01";
  const metadataPath = path.join(targetDir, `${targetBase}.run.json`);
  const markerPath = path.join(targetDir, `${targetBase}.complete.json`);
  const originalMetadata = fs.readFileSync(metadataPath);
  const originalMarker = fs.readFileSync(markerPath);

  fs.unlinkSync(metadataPath);
  const missing = analyze();
  assert.equal(missing.collection_integrity.scheduled_slot_status_counts.analysis.partial, 1);
  assert.equal(missing.collection_integrity.scheduled_slot_status_counts.analysis.valid, 53);
  assert.equal(missing.preliminary_gates.output_gate, false);
  fs.writeFileSync(metadataPath, originalMetadata);

  const tamperedMetadata = JSON.parse(originalMetadata);
  tamperedMetadata.model_label = "model-b";
  fs.writeFileSync(metadataPath, `${JSON.stringify(tamperedMetadata, null, 2)}\n`);
  const tamperedMarker = JSON.parse(originalMarker);
  tamperedMarker.metadata_sha256 = hashFile(metadataPath);
  fs.writeFileSync(markerPath, `${JSON.stringify(tamperedMarker, null, 2)}\n`);
  const tampered = analyze();
  assert.equal(tampered.collection_integrity.scheduled_slot_status_counts.analysis.partial, 1);
  const tamperedSlot = tampered.collection_integrity.slots.find((slot) =>
    slot.task === "analysis" && slot.model === "model-a" && slot.case_id === "CASE-A001" && slot.run === "01"
  );
  assert.ok(tamperedSlot.issues.includes("metadata model mismatch"));
  assert.equal(tampered.preliminary_gates.output_gate, false);
  fs.writeFileSync(metadataPath, originalMetadata);
  fs.writeFileSync(markerPath, originalMarker);

  fs.writeFileSync(path.join(targetDir, "unexpected.md"), "unexpected scheduled artifact");
  const unexpected = analyze();
  assert.deepEqual(unexpected.collection_integrity.unexpected_scheduled_artifacts, ["analysis/unexpected.md"]);
  assert.equal(unexpected.preliminary_gates.output_gate, false);

  process.stdout.write("analyzer integration test passed\n");
} finally {
  fs.rmSync(tempRoot, {recursive: true, force: true});
}
