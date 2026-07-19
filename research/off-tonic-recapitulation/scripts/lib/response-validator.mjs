const CUE_NAMES = [
  "tonal_stability",
  "thematic_correspondence",
  "preparation_strength",
  "proportional_location",
  "rhetorical_emphasis",
  "rotational_continuation"
];

const STATUS_LABELS = [
  "not_recapitulation",
  "off_tonic_recapitulation",
  "tonic_double_return"
];

const TASK_HEADINGS = {
  analysis: [
    "# Analysis result",
    "## Run metadata",
    "## Machine-readable result",
    "## Limitations"
  ],
  identification: [
    "# Identification probe result",
    "## Run metadata",
    "## Machine-readable result",
    "## Limitations"
  ]
};

const WORD_PATTERN = /[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu;

const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

const assertObject = (value, location) => {
  if (!isObject(value)) throw new Error(`${location} must be an object`);
};

const assertExactKeys = (value, expected, location) => {
  assertObject(value, location);
  const actual = Object.keys(value);
  const missing = expected.filter((key) => !Object.hasOwn(value, key));
  const extra = actual.filter((key) => !expected.includes(key));
  if (missing.length || extra.length) {
    const details = [];
    if (missing.length) details.push(`missing ${missing.join(", ")}`);
    if (extra.length) details.push(`extra ${extra.join(", ")}`);
    throw new Error(`${location} has wrong keys (${details.join("; ")})`);
  }
};

const assertNonemptyString = (value, location) => {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${location} must be a nonempty string`);
  }
};

const assertNullableNonemptyString = (value, location) => {
  if (value !== null) assertNonemptyString(value, location);
};

export function countWords(value) {
  if (typeof value !== "string") return 0;
  return value.match(WORD_PATTERN)?.length ?? 0;
}

const assertWordLimit = (value, maximum, location) => {
  assertNonemptyString(value, location);
  const words = countWords(value);
  if (words > maximum) throw new Error(`${location} exceeds ${maximum} words (${words})`);
};

export function collectEvidenceIds(dossier) {
  assertObject(dossier, "dossier");
  if (!Array.isArray(dossier.windows) || dossier.windows.length === 0) {
    throw new Error("dossier.windows must be a nonempty array");
  }

  const evidenceIds = new Set();
  for (const [windowIndex, window] of dossier.windows.entries()) {
    assertObject(window, `dossier.windows[${windowIndex}]`);
    if (!Array.isArray(window.measures) || window.measures.length === 0) {
      throw new Error(`dossier.windows[${windowIndex}].measures must be a nonempty array`);
    }
    for (const [measureIndex, measure] of window.measures.entries()) {
      const location = `dossier.windows[${windowIndex}].measures[${measureIndex}]`;
      assertObject(measure, location);
      assertNonemptyString(measure.evidence_id, `${location}.evidence_id`);
      if (evidenceIds.has(measure.evidence_id)) {
        throw new Error(`duplicate dossier evidence ID: ${measure.evidence_id}`);
      }
      evidenceIds.add(measure.evidence_id);
    }
  }
  return evidenceIds;
}

const validateEvidenceReferences = (ids, evidenceIds, location) => {
  if (!Array.isArray(ids)) throw new Error(`${location} must be an array`);
  const seen = new Set();
  for (const [index, id] of ids.entries()) {
    assertNonemptyString(id, `${location}[${index}]`);
    if (seen.has(id)) throw new Error(`duplicate evidence ID ${id} at ${location}`);
    if (!evidenceIds.has(id)) throw new Error(`unknown evidence ID ${id} at ${location}`);
    seen.add(id);
  }
};

const parseMarkdown = (task, response) => {
  const requiredHeadings = TASK_HEADINGS[task];
  if (!requiredHeadings) throw new Error(`unsupported task: ${task}`);
  if (typeof response !== "string") throw new Error("response must be a string");

  const normalized = response.replace(/\r\n?/g, "\n");
  const headingMatches = [...normalized.matchAll(/^#{1,2} .+$/gm)];
  const headings = headingMatches.map((match) => match[0]);
  if (headings.length !== requiredHeadings.length || headings.some((heading, index) => heading !== requiredHeadings[index])) {
    throw new Error(`unexpected heading sequence: ${JSON.stringify(headings)}`);
  }

  const jsonBlocks = [...normalized.matchAll(/^```json[ \t]*\n([\s\S]*?)\n```[ \t]*$/gm)];
  if (jsonBlocks.length !== 1) throw new Error(`expected one JSON block, found ${jsonBlocks.length}`);

  const machineHeading = headingMatches[2];
  const limitationsHeading = headingMatches[3];
  const machineStart = machineHeading.index + machineHeading[0].length;
  const machineSection = normalized.slice(machineStart, limitationsHeading.index).trim();
  const machineBlock = machineSection.match(/^```json[ \t]*\n([\s\S]*?)\n```[ \t]*$/);
  if (!machineBlock) {
    throw new Error("Machine-readable result must contain only one fenced json block");
  }

  let result;
  try {
    result = JSON.parse(machineBlock[1]);
  } catch (error) {
    throw new Error(`invalid JSON result: ${error.message}`);
  }

  const limitationsStart = limitationsHeading.index + limitationsHeading[0].length;
  const limitations = normalized.slice(limitationsStart).trim();
  assertWordLimit(limitations, 100, "Limitations");

  return {result, limitations, headings};
};

const validateCommonResult = (result, expectedCase, dossier, expectedKeys) => {
  assertExactKeys(result, expectedKeys, "result");
  if (result.schema_version !== "2.0.0") throw new Error("wrong result schema version");
  assertNonemptyString(result.analyst_model, "result.analyst_model");
  if (result.case_id !== expectedCase || result.case_id !== dossier.case_id) {
    throw new Error(`case mismatch: expected ${expectedCase}, received ${result.case_id}`);
  }
};

const validateAnalysisResult = (result, expectedCase, dossier, evidenceIds) => {
  validateCommonResult(result, expectedCase, dossier, [
    "schema_version",
    "analyst_model",
    "case_id",
    "cues",
    "status_distribution",
    "case_note"
  ]);

  assertExactKeys(result.cues, CUE_NAMES, "result.cues");
  for (const cue of CUE_NAMES) {
    const location = `result.cues.${cue}`;
    const value = result.cues[cue];
    assertExactKeys(value, ["score", "evidence_ids", "reason"], location);
    if (value.score !== null && (!Number.isInteger(value.score) || value.score < 0 || value.score > 4)) {
      throw new Error(`${location}.score must be an integer from 0 to 4 or null`);
    }
    validateEvidenceReferences(value.evidence_ids, evidenceIds, `${location}.evidence_ids`);
    assertWordLimit(value.reason, 40, `${location}.reason`);
  }

  assertExactKeys(result.status_distribution, STATUS_LABELS, "result.status_distribution");
  const probabilities = STATUS_LABELS.map((label) => result.status_distribution[label]);
  for (const [index, probability] of probabilities.entries()) {
    if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) {
      throw new Error(`result.status_distribution.${STATUS_LABELS[index]} must be a finite number from 0 to 1`);
    }
  }
  const sum = probabilities.reduce((total, probability) => total + probability, 0);
  if (Math.abs(sum - 1) > 0.001) throw new Error("status probabilities do not sum to 1 within 0.001");

  assertWordLimit(result.case_note, 40, "result.case_note");
};

const validateIdentificationResult = (result, expectedCase, dossier, evidenceIds) => {
  validateCommonResult(result, expectedCase, dossier, [
    "schema_version",
    "analyst_model",
    "case_id",
    "identification"
  ]);

  const identification = result.identification;
  assertExactKeys(identification, [
    "recognition_level",
    "composer",
    "work",
    "movement",
    "confidence",
    "evidence_ids",
    "reason"
  ], "result.identification");

  const levels = ["none", "style_only", "specific_candidate"];
  if (!levels.includes(identification.recognition_level)) {
    throw new Error("invalid recognition_level");
  }
  for (const field of ["composer", "work", "movement"]) {
    assertNullableNonemptyString(identification[field], `result.identification.${field}`);
  }
  if (typeof identification.confidence !== "number"
      || !Number.isFinite(identification.confidence)
      || identification.confidence < 0
      || identification.confidence > 1) {
    throw new Error("result.identification.confidence must be a finite number from 0 to 1");
  }

  if (identification.recognition_level === "none"
      && [identification.composer, identification.work, identification.movement].some((value) => value !== null)) {
    throw new Error("none identification must not name a composer, work, or movement");
  }
  if (identification.recognition_level === "style_only"
      && (identification.work !== null || identification.movement !== null)) {
    throw new Error("style_only identification must not name a work or movement");
  }
  if (identification.recognition_level === "specific_candidate" && identification.work === null) {
    throw new Error("specific_candidate identification must name a work");
  }

  validateEvidenceReferences(identification.evidence_ids, evidenceIds, "result.identification.evidence_ids");
  assertWordLimit(identification.reason, 60, "result.identification.reason");
};

export function parseAndValidateResponse({task, expectedCase, dossier, response}) {
  if (typeof expectedCase !== "string" || expectedCase === "") throw new Error("expectedCase is required");
  const parsed = parseMarkdown(task, response);
  const evidenceIds = collectEvidenceIds(dossier);
  if (task === "analysis") {
    validateAnalysisResult(parsed.result, expectedCase, dossier, evidenceIds);
  } else if (task === "identification") {
    validateIdentificationResult(parsed.result, expectedCase, dossier, evidenceIds);
  } else {
    throw new Error(`unsupported task: ${task}`);
  }
  return parsed.result;
}

export {CUE_NAMES, STATUS_LABELS};
