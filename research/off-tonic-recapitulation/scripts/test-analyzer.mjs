import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import {spawnSync} from "node:child_process";
import {writePassedPreflightReceipt} from "./test-helpers/preflight-receipt.mjs";

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
      window("W1", "opening", 8),
      window("W2", "pre_candidate", 6),
      window("W3", "candidate", 6),
      window("W4", "continuation", 6)
    ]
  };
};

const buildRenderedPrompt = (matrix, manifest, task, caseId) => {
  const entry = manifest.cases.find((item) => item.case_id === caseId);
  const dossier = JSON.parse(fs.readFileSync(path.join(experimentDir, "data", entry.file), "utf8"));
  const prompt = fs.readFileSync(path.join(experimentDir, matrix.tasks[task].prompt), "utf8");
  return prompt.replace("{{CASE_ID}}", caseId).replace(
    "{{DOSSIER}}",
    `--- BEGIN FILE: ${entry.file} ---\n${JSON.stringify(dossier)}\n--- END FILE: ${entry.file} ---`
  );
};

const analysisResponse = (caseId, caseIndex) => {
  const cueValues = Object.fromEntries(cues.map((cue, cueIndex) => [cue, {
    score: (caseIndex + cueIndex) % 5,
    evidence_ids: ["E001"],
    reason: "The encoded event is observed; the score is a fixture inference."
  }]));
  const payload = {
    schema_version: "2.1.0",
    analyst_model: "fixture-model",
    case_id: caseId,
    cues: cueValues,
    status_distribution: {
      not_recapitulation: 0.2,
      off_tonic_recapitulation: 0.4,
      tonic_double_return: 0.4
    },
    suspected_recognition: {level: "none", confidence: 0},
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
    schema_version: "2.1.0",
    analyst_model: "fixture-model",
    case_id: caseId,
    identification
  };
  return `# Identification probe result\n\n## Run metadata\n\nFixture metadata.\n\n## Machine-readable result\n\n${fence}json\n${JSON.stringify(payload, null, 2)}\n${fence}\n\n## Limitations\n\nSynthetic fixture only.\n`;
};

try {
  fs.cpSync(sourceDir, experimentDir, {recursive: true});
  // The source tree is frozen after collection, but this fixture builds its
  // own manifest and must create a fresh lock for those synthetic inputs.
  fs.rmSync(path.join(experimentDir, "collection-lock.json"), {force: true});

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
      provider: model === "model-b" ? "fixture-provider-two" : "fixture-provider-one",
      model_id: `${model}-1`,
      generation_role: model === "model-c" ? "prior_generation_active_not_deprecated" : "frontier",
      experimental_unit: "fixture CLI model system",
      cli: "fixture-cli",
      cli_version: "1.0.0",
      authentication: "local fixture",
      decoding_settings: "deterministic",
      tool_access: "none",
      adapter: adapterRelative,
      adapter_sha256: hashFile(adapterPath),
      preflight_status: "passed_no_outcome_2026-07-18",
      preflight_receipt: null
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
  for (const model of models) {
    modelSpecs[model].preflight_receipt = writePassedPreflightReceipt({
      experimentDir,
      matrix,
      modelLabel: model,
      date: "2026-07-18"
    });
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
    const claimDir = path.join(
      experimentDir,
      "outputs",
      manifest.dataset_version,
      "scheduled",
      ".claims",
      slot.task
    );
    fs.mkdirSync(outputDir, {recursive: true});
    fs.mkdirSync(claimDir, {recursive: true});
    const base = `${slot.model}__symbolic__${slot.case_id}__run-${slot.run}`;
    const claimPath = path.join(claimDir, `${base}.attempt.json`);
    const responsePath = path.join(outputDir, `${base}.md`);
    const stderrPath = path.join(outputDir, `${base}.stderr.txt`);
    const metadataPath = path.join(outputDir, `${base}.run.json`);
    const markerPath = path.join(outputDir, `${base}.complete.json`);
    const claim = {
      schema_version: "1.0.0",
      sequence: slot.sequence,
      task: slot.task,
      model: slot.model,
      case_id: slot.case_id,
      run: slot.run,
      collection_lock_sha256: hashFile(lockPath),
      claimed_at: "2026-07-18T00:59:59Z"
    };
    fs.writeFileSync(claimPath, `${JSON.stringify(claim, null, 2)}\n`, {mode: 0o444});
    fs.chmodSync(claimPath, 0o444);
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
  const makeModelUnrepeatable = (model) => {
    const originals = [];
    for (const slot of matrix.schedule.filter((entry) => entry.task === "analysis" && entry.model === model)) {
      const outputDir = path.join(experimentDir, "outputs", manifest.dataset_version, "scheduled", "analysis");
      const base = `${slot.model}__symbolic__${slot.case_id}__run-${slot.run}`;
      const responsePath = path.join(outputDir, `${base}.md`);
      const metadataPath = path.join(outputDir, `${base}.run.json`);
      const markerPath = path.join(outputDir, `${base}.complete.json`);
      const originalResponse = fs.readFileSync(responsePath);
      const originalMetadata = fs.readFileSync(metadataPath);
      const originalMarker = fs.readFileSync(markerPath);
      originals.push({responsePath, metadataPath, markerPath, originalResponse, originalMetadata, originalMarker});

      const score = slot.run === "02" ? 4 : 0;
      const response = originalResponse.toString().replace(/"score": [0-4]/g, `"score": ${score}`);
      fs.writeFileSync(responsePath, response);
      const metadata = JSON.parse(originalMetadata);
      metadata.response_sha256 = hashFile(responsePath);
      fs.writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`);
      const marker = JSON.parse(originalMarker);
      marker.metadata_sha256 = hashFile(metadataPath);
      marker.response_sha256 = hashFile(responsePath);
      fs.writeFileSync(markerPath, `${JSON.stringify(marker, null, 2)}\n`);
    }
    return () => {
      for (const original of originals) {
        fs.writeFileSync(original.responsePath, original.originalResponse);
        fs.writeFileSync(original.metadataPath, original.originalMetadata);
        fs.writeFileSync(original.markerPath, original.originalMarker);
      }
    };
  };
  const baseline = analyze();
  assert.equal(baseline.schema_version, "2.1.0");
  assert.equal(baseline.valid_analysis_invocations, 54);
  assert.equal(baseline.non_null_cue_cells, 324);
  assert.equal(baseline.collection_integrity.scheduled_slot_status_counts.analysis.valid, 54);
  assert.equal(baseline.collection_integrity.scheduled_slot_status_counts.identification.valid, 54);
  assert.deepEqual(baseline.collection_integrity.unexpected_scheduled_artifacts, []);
  assert.equal(baseline.repeatable_models.length, 3);
  assert.deepEqual(baseline.repeatable_providers, ["fixture-provider-one", "fixture-provider-two"]);
  assert.equal(baseline.nondegenerate_cues.length, 6);
  assert.equal(baseline.pairwise_system_reliability.length, 3);
  const withinProviderPair = baseline.pairwise_system_reliability.find(
    (entry) => entry.provider_comparison === "within_provider"
  );
  assert.deepEqual(withinProviderPair.systems, ["model-a", "model-c"]);
  assert.deepEqual(withinProviderPair.providers, ["fixture-provider-one", "fixture-provider-one"]);
  assert.equal(
    baseline.pairwise_system_reliability.filter((entry) => entry.provider_comparison === "cross_provider").length,
    2
  );
  assert.equal(baseline.identification.level_counts.L0, 52);
  assert.equal(baseline.identification.level_counts.L2, 2);
  assert.deepEqual(baseline.identification.target_l2_events, []);
  assert.equal(baseline.identification.positive_control.sensitivity_detected, true);
  assert.deepEqual(baseline.identification.positive_control.l2_by_provider, {
    "fixture-provider-one": 2,
    "fixture-provider-two": 0
  });
  assert.deepEqual(
    baseline.identification.positive_control.providers_with_any_l2,
    ["fixture-provider-one"]
  );
  const baselineStrata = baseline.identification.analysis_score_repeatability_by_l2_category;
  assert.equal(baselineStrata.repeated_l2.model_case_pair_count, 0);
  assert.equal(baselineStrata.isolated_l2.model_case_pair_count, 0);
  assert.equal(baselineStrata.no_l2.model_case_pair_count, 15);
  assert.equal(baselineStrata.no_l2.case_cue_unit_count, 90);
  assert.equal(baselineStrata.no_l2.pooled_score_repeatability.pairs, 270);
  assert.equal(baselineStrata.no_l2.pooled_score_repeatability.exact_agreement, 1);
  assert.equal(baseline.model_case_cue_medians["model-a"]["CASE-A001"].tonal_stability, 0);
  assert.equal(baseline.model_case_cue_medians["model-c"]["CASE-A002"].thematic_correspondence, 2);
  assert.equal(baseline.work_level_recognition_on_target, false);
  assert.equal(baseline.identification.gate, true);
  assert.equal(baseline.preliminary_gates.output_gate, true);
  assert.equal(baseline.preliminary_gates.analysis_recognition_gate, true);
  assert.equal(baseline.automatic_expansion_gate, true);

  const restoreModelBRepeatability = makeModelUnrepeatable("model-b");
  const sameProviderRepeatability = analyze();
  assert.deepEqual(sameProviderRepeatability.repeatable_models, ["model-a", "model-c"]);
  assert.deepEqual(sameProviderRepeatability.repeatable_providers, ["fixture-provider-one"]);
  assert.equal(sameProviderRepeatability.preliminary_gates.repeatability_gate, false);
  assert.equal(sameProviderRepeatability.preliminary_gates.dispersion_gate, false);
  assert.deepEqual(sameProviderRepeatability.nondegenerate_cues, []);
  assert.equal(sameProviderRepeatability.automatic_expansion_gate, false);
  restoreModelBRepeatability();

  const originalAdjudication = fs.readFileSync(adjudicationPath);
  const sameProviderLeakage = JSON.parse(originalAdjudication);
  for (const model of ["model-a", "model-c"]) {
    sameProviderLeakage.judgments.find((judgment) =>
      judgment.output === `${model}__symbolic__CASE-A001__run-01.md`
    ).level = "L2";
  }
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(sameProviderLeakage, null, 2)}\n`);
  const sameProviderLeakageSummary = analyze();
  assert.equal(sameProviderLeakageSummary.identification.target_l2_events.length, 2);
  assert.deepEqual(sameProviderLeakageSummary.identification.compromised_target_dossiers, []);
  const sameProviderTarget = sameProviderLeakageSummary.identification.target_case_l2_summary.find(
    (entry) => entry.case_id === "CASE-A001"
  );
  assert.deepEqual(sameProviderTarget.models_with_any_l2, ["model-a", "model-c"]);
  assert.deepEqual(sameProviderTarget.l2_by_provider, {
    "fixture-provider-one": 2,
    "fixture-provider-two": 0
  });
  assert.deepEqual(sameProviderTarget.providers_with_any_l2, ["fixture-provider-one"]);
  assert.equal(sameProviderTarget.identity_recoverable, false);
  assert.equal(
    sameProviderLeakageSummary.identification.analysis_score_repeatability_by_l2_category.isolated_l2.model_case_pair_count,
    2
  );
  assert.equal(
    sameProviderLeakageSummary.identification.analysis_score_repeatability_by_l2_category.no_l2.model_case_pair_count,
    13
  );
  assert.equal(sameProviderLeakageSummary.identification.gate, false);

  const crossProviderLeakage = structuredClone(sameProviderLeakage);
  crossProviderLeakage.judgments.find((judgment) =>
    judgment.output === "model-b__symbolic__CASE-A001__run-01.md"
  ).level = "L2";
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(crossProviderLeakage, null, 2)}\n`);
  const crossProviderLeakageSummary = analyze();
  assert.equal(crossProviderLeakageSummary.identification.compromised_target_dossiers.length, 1);
  const crossProviderTarget = crossProviderLeakageSummary.identification.compromised_target_dossiers[0];
  assert.deepEqual(
    crossProviderTarget.providers_with_any_l2,
    ["fixture-provider-one", "fixture-provider-two"]
  );
  assert.equal(crossProviderTarget.identity_recoverable, true);
  assert.equal(
    crossProviderLeakageSummary.identification.analysis_score_repeatability_by_l2_category.isolated_l2.model_case_pair_count,
    3
  );

  const repeatedLeakage = JSON.parse(originalAdjudication);
  for (const runId of ["01", "02"]) {
    repeatedLeakage.judgments.find((judgment) =>
      judgment.output === `model-b__symbolic__CASE-A001__run-${runId}.md`
    ).level = "L2";
  }
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(repeatedLeakage, null, 2)}\n`);
  const repeatedLeakageSummary = analyze();
  assert.equal(repeatedLeakageSummary.identification.compromised_target_dossiers.length, 1);
  assert.deepEqual(
    repeatedLeakageSummary.identification.compromised_target_dossiers[0].providers_with_any_l2,
    ["fixture-provider-two"]
  );
  assert.equal(repeatedLeakageSummary.identification.compromised_target_dossiers[0].identity_recoverable, true);
  assert.equal(
    repeatedLeakageSummary.identification.analysis_score_repeatability_by_l2_category.repeated_l2.model_case_pair_count,
    1
  );
  assert.equal(
    repeatedLeakageSummary.identification.analysis_score_repeatability_by_l2_category.isolated_l2.model_case_pair_count,
    0
  );
  assert.equal(
    repeatedLeakageSummary.identification.analysis_score_repeatability_by_l2_category.no_l2.model_case_pair_count,
    14
  );
  fs.writeFileSync(adjudicationPath, originalAdjudication);

  const sameProviderProbe = JSON.parse(originalAdjudication);
  sameProviderProbe.judgments.find((judgment) =>
    judgment.output === "model-a__symbolic__CASE-A006__run-02.md"
  ).level = "L0";
  sameProviderProbe.judgments.find((judgment) =>
    judgment.output === "model-c__symbolic__CASE-A006__run-01.md"
  ).level = "L2";
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(sameProviderProbe, null, 2)}\n`);
  const sameProviderProbeSummary = analyze();
  assert.deepEqual(sameProviderProbeSummary.identification.positive_control.models_with_any_l2, [
    "model-a",
    "model-c"
  ]);
  assert.deepEqual(
    sameProviderProbeSummary.identification.positive_control.providers_with_any_l2,
    ["fixture-provider-one"]
  );
  assert.equal(sameProviderProbeSummary.identification.positive_control.sensitivity_detected, false);
  assert.equal(sameProviderProbeSummary.identification.gate, false);

  const crossProviderProbe = structuredClone(sameProviderProbe);
  crossProviderProbe.judgments.find((judgment) =>
    judgment.output === "model-b__symbolic__CASE-A006__run-01.md"
  ).level = "L2";
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(crossProviderProbe, null, 2)}\n`);
  const crossProviderProbeSummary = analyze();
  assert.deepEqual(
    crossProviderProbeSummary.identification.positive_control.providers_with_any_l2,
    ["fixture-provider-one", "fixture-provider-two"]
  );
  assert.equal(crossProviderProbeSummary.identification.positive_control.sensitivity_detected, true);

  const insensitiveProbe = JSON.parse(originalAdjudication);
  for (const judgment of insensitiveProbe.judgments) {
    if (judgment.level === "L2") judgment.level = "L0";
  }
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(insensitiveProbe, null, 2)}\n`);
  const insensitiveProbeSummary = analyze();
  assert.equal(insensitiveProbeSummary.identification.positive_control.sensitivity_detected, false);
  assert.equal(insensitiveProbeSummary.identification.gate, false);
  fs.writeFileSync(adjudicationPath, originalAdjudication);

  const invalidIdentificationDir = path.join(
    experimentDir,
    "outputs",
    manifest.dataset_version,
    "scheduled",
    "identification"
  );
  const invalidIdentificationBase = "model-b__symbolic__CASE-A001__run-03";
  const validIdentificationPath = path.join(invalidIdentificationDir, `${invalidIdentificationBase}.md`);
  const invalidIdentificationPath = path.join(invalidIdentificationDir, `${invalidIdentificationBase}.invalid.md`);
  const invalidIdentificationMetadataPath = path.join(
    invalidIdentificationDir,
    `${invalidIdentificationBase}.run.json`
  );
  const invalidIdentificationMarkerPath = path.join(
    invalidIdentificationDir,
    `${invalidIdentificationBase}.complete.json`
  );
  const originalIdentificationResponse = fs.readFileSync(validIdentificationPath);
  const originalIdentificationMetadata = fs.readFileSync(invalidIdentificationMetadataPath);
  const originalIdentificationMarker = fs.readFileSync(invalidIdentificationMarkerPath);
  fs.unlinkSync(validIdentificationPath);
  fs.writeFileSync(invalidIdentificationPath, "invalid identification fixture\n");
  const invalidIdentificationMetadata = JSON.parse(originalIdentificationMetadata);
  invalidIdentificationMetadata.response_file = path.basename(invalidIdentificationPath);
  invalidIdentificationMetadata.response_sha256 = hashFile(invalidIdentificationPath);
  invalidIdentificationMetadata.validation_status = "invalid";
  invalidIdentificationMetadata.validation_error = "synthetic invalid response";
  fs.writeFileSync(
    invalidIdentificationMetadataPath,
    `${JSON.stringify(invalidIdentificationMetadata, null, 2)}\n`
  );
  const invalidIdentificationMarker = JSON.parse(originalIdentificationMarker);
  invalidIdentificationMarker.metadata_sha256 = hashFile(invalidIdentificationMetadataPath);
  invalidIdentificationMarker.response_file = path.basename(invalidIdentificationPath);
  invalidIdentificationMarker.response_sha256 = hashFile(invalidIdentificationPath);
  fs.writeFileSync(
    invalidIdentificationMarkerPath,
    `${JSON.stringify(invalidIdentificationMarker, null, 2)}\n`
  );
  const incompleteAdjudication = JSON.parse(originalAdjudication);
  incompleteAdjudication.judgments = incompleteAdjudication.judgments.filter(
    (judgment) => judgment.output !== path.basename(validIdentificationPath)
  );
  fs.writeFileSync(adjudicationPath, `${JSON.stringify(incompleteAdjudication, null, 2)}\n`);
  const invalidIdentificationSummary = analyze();
  assert.equal(
    invalidIdentificationSummary.collection_integrity.scheduled_slot_status_counts.identification.invalid,
    1
  );
  assert.equal(invalidIdentificationSummary.identification.valid_outputs, 53);
  assert.equal(invalidIdentificationSummary.identification.adjudicated_outputs, 53);
  assert.equal(invalidIdentificationSummary.identification.analysis_score_repeatability_by_l2_category, null);
  assert.equal(invalidIdentificationSummary.identification.gate, false);
  assert.equal(invalidIdentificationSummary.preliminary_gates.output_gate, false);
  assert.equal(invalidIdentificationSummary.automatic_expansion_gate, false);
  fs.unlinkSync(invalidIdentificationPath);
  fs.writeFileSync(validIdentificationPath, originalIdentificationResponse);
  fs.writeFileSync(invalidIdentificationMetadataPath, originalIdentificationMetadata);
  fs.writeFileSync(invalidIdentificationMarkerPath, originalIdentificationMarker);
  fs.writeFileSync(adjudicationPath, originalAdjudication);

  const targetDir = path.join(experimentDir, "outputs", manifest.dataset_version, "scheduled", "analysis");
  const targetBase = "model-a__symbolic__CASE-A001__run-01";
  const metadataPath = path.join(targetDir, `${targetBase}.run.json`);
  const markerPath = path.join(targetDir, `${targetBase}.complete.json`);
  const responsePath = path.join(targetDir, `${targetBase}.md`);
  const stderrPath = path.join(targetDir, `${targetBase}.stderr.txt`);
  const claimPath = path.join(
    experimentDir,
    "outputs",
    manifest.dataset_version,
    "scheduled",
    ".claims",
    "analysis",
    `${targetBase}.attempt.json`
  );
  const originalMetadata = fs.readFileSync(metadataPath);
  const originalMarker = fs.readFileSync(markerPath);
  const originalResponse = fs.readFileSync(responsePath);
  const originalStderr = fs.readFileSync(stderrPath);
  const originalClaim = fs.readFileSync(claimPath);

  const workRecognitionResponse = originalResponse.toString().replace(
    '"level": "none"',
    '"level": "work"'
  );
  assert.notEqual(workRecognitionResponse, originalResponse.toString());
  fs.writeFileSync(responsePath, workRecognitionResponse);
  const workRecognitionMetadata = JSON.parse(originalMetadata);
  workRecognitionMetadata.response_sha256 = hashFile(responsePath);
  fs.writeFileSync(metadataPath, `${JSON.stringify(workRecognitionMetadata, null, 2)}\n`);
  const workRecognitionMarker = JSON.parse(originalMarker);
  workRecognitionMarker.metadata_sha256 = hashFile(metadataPath);
  workRecognitionMarker.response_sha256 = hashFile(responsePath);
  fs.writeFileSync(markerPath, `${JSON.stringify(workRecognitionMarker, null, 2)}\n`);
  const workRecognition = analyze();
  assert.equal(workRecognition.collection_integrity.scheduled_slot_status_counts.analysis.valid, 54);
  assert.equal(workRecognition.work_level_recognition_on_target, true);
  assert.equal(workRecognition.preliminary_gates.analysis_recognition_gate, false);
  assert.equal(workRecognition.automatic_expansion_gate, false);
  fs.writeFileSync(responsePath, originalResponse);
  fs.writeFileSync(metadataPath, originalMetadata);
  fs.writeFileSync(markerPath, originalMarker);

  fs.unlinkSync(claimPath);
  const missingClaim = analyze();
  const missingClaimSlot = missingClaim.collection_integrity.slots.find((slot) =>
    slot.task === "analysis" && slot.model === "model-a" && slot.case_id === "CASE-A001" && slot.run === "01"
  );
  assert.equal(missingClaimSlot.status, "partial");
  assert.ok(missingClaimSlot.issues.includes("missing attempt claim"));
  assert.equal(missingClaim.preliminary_gates.output_gate, false);
  assert.equal(missingClaim.automatic_expansion_gate, false);
  fs.writeFileSync(claimPath, originalClaim, {mode: 0o444});
  fs.chmodSync(claimPath, 0o444);

  fs.chmodSync(claimPath, 0o644);
  const tamperedClaim = JSON.parse(originalClaim);
  tamperedClaim.model = "model-b";
  fs.writeFileSync(claimPath, `${JSON.stringify(tamperedClaim, null, 2)}\n`);
  fs.chmodSync(claimPath, 0o444);
  const invalidClaim = analyze();
  const invalidClaimSlot = invalidClaim.collection_integrity.slots.find((slot) =>
    slot.task === "analysis" && slot.model === "model-a" && slot.case_id === "CASE-A001" && slot.run === "01"
  );
  assert.equal(invalidClaimSlot.status, "partial");
  assert.ok(invalidClaimSlot.issues.some((issue) => issue.includes("attempt claim model mismatch")));
  assert.equal(invalidClaim.preliminary_gates.output_gate, false);
  assert.equal(invalidClaim.automatic_expansion_gate, false);
  fs.chmodSync(claimPath, 0o644);
  fs.writeFileSync(claimPath, originalClaim);
  fs.chmodSync(claimPath, 0o444);

  for (const file of [responsePath, metadataPath, markerPath, stderrPath, claimPath]) fs.unlinkSync(file);
  const absent = analyze();
  const absentSlot = absent.collection_integrity.slots.find((slot) =>
    slot.task === "analysis" && slot.model === "model-a" && slot.case_id === "CASE-A001" && slot.run === "01"
  );
  assert.equal(absentSlot.status, "absent");
  assert.deepEqual(absentSlot.issues, []);
  assert.equal(absent.collection_integrity.scheduled_slot_status_counts.analysis.absent, 1);
  assert.equal(absent.preliminary_gates.output_gate, false);
  fs.writeFileSync(responsePath, originalResponse);
  fs.writeFileSync(metadataPath, originalMetadata);
  fs.writeFileSync(markerPath, originalMarker);
  fs.writeFileSync(stderrPath, originalStderr);
  fs.writeFileSync(claimPath, originalClaim, {mode: 0o444});
  fs.chmodSync(claimPath, 0o444);

  fs.unlinkSync(metadataPath);
  const missing = analyze();
  assert.equal(missing.collection_integrity.scheduled_slot_status_counts.analysis.partial, 1);
  assert.equal(missing.collection_integrity.scheduled_slot_status_counts.analysis.valid, 53);
  assert.equal(missing.preliminary_gates.output_gate, false);
  assert.equal(missing.model_case_cue_medians["model-a"]["CASE-A001"].tonal_stability, null);
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
