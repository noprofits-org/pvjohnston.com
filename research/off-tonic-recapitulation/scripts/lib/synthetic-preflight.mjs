import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {validateCase} from "./case-validator.mjs";

export const SYNTHETIC_CASE_ID = "CASE-SYN0";
export const PREFLIGHT_TASKS = Object.freeze(["analysis", "identification"]);
export const PREFLIGHT_SOURCE_FILES = Object.freeze([
  "scripts/run-synthetic-preflight.mjs",
  "scripts/lib/synthetic-preflight.mjs",
  "scripts/lib/case-validator.mjs",
  "scripts/lib/response-validator.mjs"
]);

export const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");

export const safeRelative = (relative, location = "path") => {
  if (typeof relative !== "string" || relative === "" || path.isAbsolute(relative)) {
    throw new Error(`${location} must be a nonempty relative path`);
  }
  const pieces = relative.replaceAll("\\", "/").split("/");
  if (pieces.some((piece) => piece === "" || piece === "." || piece === "..")) {
    throw new Error(`${location} is unsafe: ${relative}`);
  }
  return relative;
};

const rational = (numerator, denominator = 1) => ({numerator, denominator});

/**
 * Build a deliberately fictional, structurally minimal schema-3.1 dossier.
 *
 * The case contains one sustained D per required measure and no expressive
 * directions. It is generated in memory and is never read from data/cases.
 * The 26-measure size is the minimum permitted by the experimental dossier
 * contract (8 + 6 + 6 + 6 measures).
 */
export function makeSyntheticDossier() {
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
      pitch: {step: "D", alter: 0, octave: 4},
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

  const dossier = {
    schema_version: "3.1.0",
    case_id: SYNTHETIC_CASE_ID,
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
      second_part_elapsed_qn: rational(32),
      second_part_total_qn: rational(64)
    },
    windows: [
      makeWindow("W1", "opening", 8),
      makeWindow("W2", "pre_candidate", 6),
      makeWindow("W3", "candidate", 6),
      makeWindow("W4", "continuation", 6)
    ]
  };

  return validateCase(dossier);
}

/**
 * Return the part of the development matrix that must remain identical after
 * its status and receipt references are frozen. This intentionally omits only
 * matrix_status, schedule fields, and the model's preflight status/receipt.
 */
export function makePreflightContract(matrix, modelLabel) {
  const model = matrix.models?.[modelLabel];
  if (!model) throw new Error(`model is absent from matrix: ${modelLabel}`);
  const modelKeys = [
    "provider",
    "model_id",
    "generation_role",
    "experimental_unit",
    "cli",
    "cli_version",
    "authentication",
    "decoding_settings",
    "tool_access",
    "adapter",
    "adapter_sha256"
  ];
  const contractModel = Object.fromEntries(modelKeys.map((key) => [key, model[key]]));
  const tasks = Object.fromEntries(PREFLIGHT_TASKS.map((task) => [task, {
    prompt: matrix.tasks?.[task]?.prompt,
    repetitions_per_case: matrix.tasks?.[task]?.repetitions_per_case
  }]));
  return {
    matrix_schema_version: matrix.schema_version,
    tasks,
    model: contractModel
  };
}

export function renderSyntheticPrompt({experimentDir, matrix, task, dossier}) {
  if (!PREFLIGHT_TASKS.includes(task)) throw new Error(`unsupported preflight task: ${task}`);
  if (dossier?.case_id !== SYNTHETIC_CASE_ID) throw new Error("preflight dossier is not the reserved synthetic case");
  validateCase(dossier);

  const promptRelative = safeRelative(matrix.tasks?.[task]?.prompt, `matrix.tasks.${task}.prompt`);
  const promptPath = path.join(experimentDir, promptRelative);
  const promptBody = fs.readFileSync(promptPath);
  const prompt = promptBody.toString("utf8");
  const dossierMarker = "{{DOSSIER}}";
  const caseMarker = "{{CASE_ID}}";
  if (prompt.split(dossierMarker).length !== 2) {
    throw new Error(`${task} prompt must contain exactly one dossier marker`);
  }
  if (prompt.split(caseMarker).length !== 2) {
    throw new Error(`${task} prompt must contain exactly one case-ID marker`);
  }

  const syntheticRelative = `synthetic-preflight/${SYNTHETIC_CASE_ID}.json`;
  const rendered = prompt.replace(caseMarker, SYNTHETIC_CASE_ID).replace(
    dossierMarker,
    `--- BEGIN FILE: ${syntheticRelative} ---\n${JSON.stringify(dossier)}\n--- END FILE: ${syntheticRelative} ---`
  );

  return {promptRelative, promptPath, promptBody, rendered};
}
