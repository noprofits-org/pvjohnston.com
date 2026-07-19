const COVERAGE_FIELDS = [
  "notes",
  "rests",
  "voices",
  "meter",
  "key_signatures",
  "dynamics",
  "articulations",
  "ornaments",
  "repeats_and_barlines"
];

const ARTICULATIONS = new Set([
  "accent",
  "breath_mark",
  "caesura",
  "fermata",
  "marcato",
  "portato",
  "spiccato",
  "staccatissimo",
  "staccato",
  "tenuto"
]);

const ORNAMENTS = new Set([
  "arpeggiate",
  "inverted_mordent",
  "inverted_turn",
  "mordent",
  "trill",
  "turn"
]);

const DYNAMICS = new Set([
  "pppp",
  "ppp",
  "pp",
  "p",
  "mp",
  "mf",
  "f",
  "ff",
  "fff",
  "ffff",
  "fp",
  "sf",
  "sfp",
  "sfz",
  "sffz",
  "rfz"
]);

const HAIRPINS = new Set([
  "crescendo_start",
  "crescendo_continue",
  "crescendo_stop",
  "diminuendo_start",
  "diminuendo_continue",
  "diminuendo_stop"
]);

const LEFT_BARLINES = new Set([
  "none",
  "regular",
  "double",
  "dashed",
  "repeat_start",
  "repeat_both"
]);

const RIGHT_BARLINES = new Set([
  "none",
  "regular",
  "double",
  "dashed",
  "final",
  "repeat_end",
  "repeat_both"
]);

const FORBIDDEN_KEYS = new Set([
  "author",
  "catalog",
  "catalogue",
  "classification",
  "composer",
  "corpus_role",
  "date",
  "doi",
  "edition",
  "expected_classification",
  "file",
  "filename",
  "identity",
  "metadata",
  "movement",
  "scholar",
  "selection_reason",
  "source",
  "title",
  "url",
  "work"
]);

const FORBIDDEN_STRINGS = [
  /\bmozart\b/i,
  /\bbenda\b/i,
  /\bclementi\b/i,
  /\bbach\b/i,
  /\bgreenberg\b/i,
  /\bprussian\b/i,
  /\b(?:piano|keyboard)\s+sonata\b/i,
  /\bwq\.?\s*\d+/i,
  /\bkv?\.?\s*\d{2,}/i,
  /\bop(?:us)?\.?\s*\d+/i,
  /\bdoi\s*:/i,
  /\bimslp\b/i,
  /\bdcml\b/i,
  /https?:\/\//i
];

const STEP_ORDER = new Map(["C", "D", "E", "F", "G", "A", "B"].map((step, index) => [step, index]));

class CaseValidationError extends Error {
  constructor(path, message) {
    super(`invalid dossier at ${path}: ${message}`);
    this.name = "CaseValidationError";
  }
}

const fail = (path, message) => {
  throw new CaseValidationError(path, message);
};

const isPlainObject = (value) => (
  value !== null && typeof value === "object" && !Array.isArray(value)
);

const expectObject = (value, path, keys) => {
  if (!isPlainObject(value)) fail(path, "expected an object");
  const expected = new Set(keys);
  for (const key of keys) {
    if (!Object.hasOwn(value, key)) fail(path, `missing key ${key}`);
  }
  for (const key of Object.keys(value)) {
    if (!expected.has(key)) fail(path, `unexpected key ${key}`);
  }
};

const expectArray = (value, path) => {
  if (!Array.isArray(value)) fail(path, "expected an array");
};

const expectEnum = (value, allowed, path) => {
  if (!allowed.has(value)) fail(path, `unexpected value ${JSON.stringify(value)}`);
};

const expectSafeInteger = (value, path, minimum, maximum) => {
  if (!Number.isSafeInteger(value)) fail(path, "expected a safe integer");
  if (value < minimum || value > maximum) {
    fail(path, `expected an integer from ${minimum} through ${maximum}`);
  }
};

const gcd = (left, right) => {
  let a = Math.abs(left);
  let b = Math.abs(right);
  while (b !== 0) [a, b] = [b, a % b];
  return a;
};

const validateRational = (value, path, {positive = false} = {}) => {
  expectObject(value, path, ["numerator", "denominator"]);
  expectSafeInteger(value.numerator, `${path}.numerator`, positive ? 1 : 0, Number.MAX_SAFE_INTEGER);
  expectSafeInteger(value.denominator, `${path}.denominator`, 1, Number.MAX_SAFE_INTEGER);
  if (gcd(value.numerator, value.denominator) !== 1) fail(path, "rational must be reduced");
  if (value.numerator === 0 && value.denominator !== 1) fail(path, "zero must be encoded as 0/1");
  return value;
};

const compareRational = (left, right) => {
  const a = BigInt(left.numerator) * BigInt(right.denominator);
  const b = BigInt(right.numerator) * BigInt(left.denominator);
  return a < b ? -1 : a > b ? 1 : 0;
};

const sumWithin = (onset, duration, limit) => {
  const totalNumerator = (
    BigInt(onset.numerator) * BigInt(duration.denominator)
    + BigInt(duration.numerator) * BigInt(onset.denominator)
  );
  const totalDenominator = BigInt(onset.denominator) * BigInt(duration.denominator);
  return totalNumerator * BigInt(limit.denominator) <= BigInt(limit.numerator) * totalDenominator;
};

const meterDuration = (meter) => {
  const numerator = meter.beats * 4;
  const divisor = gcd(numerator, meter.beat_type);
  return {numerator: numerator / divisor, denominator: meter.beat_type / divisor};
};

const scanForbiddenIdentity = (value, path = "$") => {
  if (typeof value === "string") {
    for (const pattern of FORBIDDEN_STRINGS) {
      if (pattern.test(value)) fail(path, "contains forbidden identity or provenance text");
    }
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanForbiddenIdentity(item, `${path}[${index}]`));
    return;
  }
  if (!isPlainObject(value)) return;
  for (const [key, item] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.has(key.toLowerCase())) fail(`${path}.${key}`, "identity or provenance key is prohibited");
    scanForbiddenIdentity(item, `${path}.${key}`);
  }
};

const validateStringArray = (value, allowed, path) => {
  expectArray(value, path);
  const seen = new Set();
  let previous = null;
  value.forEach((item, index) => {
    expectEnum(item, allowed, `${path}[${index}]`);
    if (seen.has(item)) fail(`${path}[${index}]`, "duplicate value");
    if (previous !== null && previous.localeCompare(item) > 0) {
      fail(`${path}[${index}]`, "values are not in canonical alphabetical order");
    }
    seen.add(item);
    previous = item;
  });
};

const validatePitch = (pitch, path) => {
  expectObject(pitch, path, ["step", "alter", "octave"]);
  expectEnum(pitch.step, STEP_ORDER, `${path}.step`);
  expectSafeInteger(pitch.alter, `${path}.alter`, -4, 4);
  expectSafeInteger(pitch.octave, `${path}.octave`, -1, 9);
};

const compareEvents = (left, right) => {
  let comparison = compareRational(left.onset_qn, right.onset_qn);
  if (comparison !== 0) return comparison;
  comparison = left.voice_id.localeCompare(right.voice_id);
  if (comparison !== 0) return comparison;
  comparison = (left.event_type === "note" ? 0 : 1) - (right.event_type === "note" ? 0 : 1);
  if (comparison !== 0) return comparison;
  if (left.event_type === "note") {
    comparison = left.pitch.octave - right.pitch.octave;
    if (comparison !== 0) return comparison;
    comparison = STEP_ORDER.get(left.pitch.step) - STEP_ORDER.get(right.pitch.step);
    if (comparison !== 0) return comparison;
    comparison = left.pitch.alter - right.pitch.alter;
    if (comparison !== 0) return comparison;
  }
  comparison = compareRational(left.duration_qn, right.duration_qn);
  if (comparison !== 0) return comparison;
  comparison = left.articulations.join("\u0000").localeCompare(right.articulations.join("\u0000"));
  if (comparison !== 0 || left.event_type === "rest") return comparison;
  comparison = left.tie.localeCompare(right.tie);
  if (comparison !== 0) return comparison;
  comparison = left.grace.localeCompare(right.grace);
  if (comparison !== 0) return comparison;
  return left.ornaments.join("\u0000").localeCompare(right.ornaments.join("\u0000"));
};

const compareDirections = (left, right) => {
  let comparison = compareRational(left.onset_qn, right.onset_qn);
  if (comparison !== 0) return comparison;
  comparison = left.direction_type.localeCompare(right.direction_type);
  if (comparison !== 0) return comparison;
  comparison = left.value.localeCompare(right.value);
  if (comparison !== 0) return comparison;
  return (left.voice_id ?? "").localeCompare(right.voice_id ?? "");
};

const validateVoiceId = (value, path, voices) => {
  if (typeof value !== "string" || !/^V[0-9]{2}$/.test(value) || value === "V00") {
    fail(path, "expected a neutral voice ID V01 through V99");
  }
  voices.add(value);
};

const validateEvent = (event, path, duration, state) => {
  if (!isPlainObject(event)) fail(path, "expected an event object");
  const common = ["event_id", "event_type", "onset_qn", "duration_qn", "voice_id", "articulations"];
  if (event.event_type === "note") {
    expectObject(event, path, [...common, "pitch", "tie", "grace", "ornaments"]);
  } else if (event.event_type === "rest") {
    expectObject(event, path, common);
  } else {
    fail(`${path}.event_type`, "expected note or rest");
  }

  const expectedId = `EV${String(state.nextEvent).padStart(4, "0")}`;
  if (event.event_id !== expectedId) fail(`${path}.event_id`, `expected canonical ID ${expectedId}`);
  state.nextEvent += 1;

  validateRational(event.onset_qn, `${path}.onset_qn`);
  validateRational(event.duration_qn, `${path}.duration_qn`, {positive: true});
  if (compareRational(event.onset_qn, duration) >= 0) fail(`${path}.onset_qn`, "event must begin within the measure");
  if (!sumWithin(event.onset_qn, event.duration_qn, duration)) fail(path, "event extends beyond the measure");
  validateVoiceId(event.voice_id, `${path}.voice_id`, state.voices);
  validateStringArray(event.articulations, ARTICULATIONS, `${path}.articulations`);

  if (event.event_type === "note") {
    validatePitch(event.pitch, `${path}.pitch`);
    expectEnum(event.tie, new Set(["none", "start", "continue", "stop"]), `${path}.tie`);
    expectEnum(event.grace, new Set(["none", "acciaccatura", "appoggiatura", "unspecified"]), `${path}.grace`);
    validateStringArray(event.ornaments, ORNAMENTS, `${path}.ornaments`);
  }
};

const validateDirection = (direction, path, duration, state) => {
  expectObject(direction, path, ["direction_id", "direction_type", "onset_qn", "voice_id", "value"]);
  const expectedId = `DR${String(state.nextDirection).padStart(4, "0")}`;
  if (direction.direction_id !== expectedId) fail(`${path}.direction_id`, `expected canonical ID ${expectedId}`);
  state.nextDirection += 1;

  validateRational(direction.onset_qn, `${path}.onset_qn`);
  if (compareRational(direction.onset_qn, duration) > 0) fail(`${path}.onset_qn`, "direction lies beyond the measure");
  if (direction.voice_id !== null) {
    if (typeof direction.voice_id !== "string" || !/^V[0-9]{2}$/.test(direction.voice_id) || direction.voice_id === "V00") {
      fail(`${path}.voice_id`, "expected null or a neutral voice ID V01 through V99");
    }
    state.directionVoices.add(direction.voice_id);
  }

  if (direction.direction_type === "dynamic") {
    expectEnum(direction.value, DYNAMICS, `${path}.value`);
  } else if (direction.direction_type === "hairpin") {
    expectEnum(direction.value, HAIRPINS, `${path}.value`);
  } else {
    fail(`${path}.direction_type`, "expected dynamic or hairpin");
  }
};

const validateMeasure = (measure, path, expectedIndex, isAnacrusis, state) => {
  expectObject(measure, path, [
    "measure_index",
    "evidence_id",
    "notated_duration_qn",
    "meter",
    "key_signature",
    "left_barline",
    "right_barline",
    "volta",
    "events",
    "directions"
  ]);
  if (measure.measure_index !== expectedIndex) fail(`${path}.measure_index`, `expected ${expectedIndex}`);

  const expectedEvidence = `E${String(state.nextEvidence).padStart(3, "0")}`;
  if (measure.evidence_id !== expectedEvidence) {
    fail(`${path}.evidence_id`, `expected canonical ID ${expectedEvidence}`);
  }
  state.nextEvidence += 1;

  validateRational(measure.notated_duration_qn, `${path}.notated_duration_qn`, {positive: true});
  expectObject(measure.meter, `${path}.meter`, ["beats", "beat_type"]);
  expectSafeInteger(measure.meter.beats, `${path}.meter.beats`, 1, 32);
  expectEnum(measure.meter.beat_type, new Set([1, 2, 4, 8, 16, 32, 64]), `${path}.meter.beat_type`);
  const completeDuration = meterDuration(measure.meter);
  const durationComparison = compareRational(measure.notated_duration_qn, completeDuration);
  if (isAnacrusis && durationComparison >= 0) fail(`${path}.notated_duration_qn`, "anacrusis must be shorter than a complete measure");
  if (!isAnacrusis && durationComparison !== 0) fail(`${path}.notated_duration_qn`, "complete measure duration must match its meter");

  expectObject(measure.key_signature, `${path}.key_signature`, ["fifths"]);
  expectSafeInteger(measure.key_signature.fifths, `${path}.key_signature.fifths`, -7, 7);
  expectEnum(measure.left_barline, LEFT_BARLINES, `${path}.left_barline`);
  expectEnum(measure.right_barline, RIGHT_BARLINES, `${path}.right_barline`);
  expectEnum(measure.volta, new Set(["none", "first", "second", "third"]), `${path}.volta`);

  expectArray(measure.events, `${path}.events`);
  if (measure.events.length === 0) fail(`${path}.events`, "measure must contain at least one note or notated rest");
  let previousEvent = null;
  measure.events.forEach((event, index) => {
    validateEvent(event, `${path}.events[${index}]`, measure.notated_duration_qn, state);
    if (previousEvent && compareEvents(previousEvent, event) > 0) {
      fail(`${path}.events[${index}]`, "events are not in canonical order");
    }
    previousEvent = event;
  });

  expectArray(measure.directions, `${path}.directions`);
  let previousDirection = null;
  measure.directions.forEach((direction, index) => {
    validateDirection(direction, `${path}.directions[${index}]`, measure.notated_duration_qn, state);
    if (previousDirection && compareDirections(previousDirection, direction) > 0) {
      fail(`${path}.directions[${index}]`, "directions are not in canonical order");
    }
    previousDirection = direction;
  });
};

const validateWindow = (window, path, specification, state) => {
  expectObject(window, path, ["window_id", "role", "measures"]);
  if (window.window_id !== specification.windowId) fail(`${path}.window_id`, `expected ${specification.windowId}`);
  if (window.role !== specification.role) fail(`${path}.role`, `expected ${specification.role}`);
  expectArray(window.measures, `${path}.measures`);

  let expectedIndexes = specification.indexes;
  if (specification.allowAnacrusis && window.measures.length === specification.indexes.length + 1) {
    expectedIndexes = [-1, ...specification.indexes];
  }
  if (window.measures.length !== expectedIndexes.length) {
    const expected = specification.allowAnacrusis ? "8 complete measures, with at most one anacrusis" : `${specification.indexes.length} measures`;
    fail(`${path}.measures`, `expected ${expected}`);
  }

  window.measures.forEach((measure, index) => {
    validateMeasure(measure, `${path}.measures[${index}]`, expectedIndexes[index], expectedIndexes[index] === -1, state);
  });
};

export const collectEvidenceIds = (dossier) => {
  const ids = new Set();
  if (!Array.isArray(dossier?.windows)) return ids;
  for (const window of dossier.windows) {
    if (!Array.isArray(window?.measures)) continue;
    for (const measure of window.measures) {
      if (typeof measure?.evidence_id === "string") ids.add(measure.evidence_id);
    }
  }
  return ids;
};

/**
 * Validate one model-facing schema-3 dossier.
 *
 * @returns the unchanged dossier on success
 * @throws {CaseValidationError} on the first violation
 */
export const validateCase = (dossier) => {
  scanForbiddenIdentity(dossier);
  expectObject(dossier, "$", [
    "schema_version",
    "case_id",
    "condition",
    "encoding",
    "candidate_return",
    "windows"
  ]);
  if (dossier.schema_version !== "3.0.0") fail("$.schema_version", "expected 3.0.0");
  if (typeof dossier.case_id !== "string" || !/^CASE-[A-Z0-9]{4}$/.test(dossier.case_id)) {
    fail("$.case_id", "expected CASE- followed by four uppercase letters or digits");
  }
  if (dossier.condition !== "symbolic") fail("$.condition", "expected symbolic");

  expectObject(dossier.encoding, "$.encoding", [
    "common_tonic",
    "home_mode",
    "duration_unit",
    "measure_numbers",
    "pitch_system",
    "coverage"
  ]);
  if (dossier.encoding.common_tonic !== "D") fail("$.encoding.common_tonic", "expected D");
  expectEnum(dossier.encoding.home_mode, new Set(["major", "minor"]), "$.encoding.home_mode");
  if (dossier.encoding.duration_unit !== "quarter_note") fail("$.encoding.duration_unit", "expected quarter_note");
  if (dossier.encoding.measure_numbers !== "window_relative") fail("$.encoding.measure_numbers", "expected window_relative");
  if (dossier.encoding.pitch_system !== "scientific_pitch_diatonic_spelling") {
    fail("$.encoding.pitch_system", "expected scientific_pitch_diatonic_spelling");
  }
  expectObject(dossier.encoding.coverage, "$.encoding.coverage", COVERAGE_FIELDS);
  for (const field of COVERAGE_FIELDS) {
    if (dossier.encoding.coverage[field] !== "complete") fail(`$.encoding.coverage.${field}`, "expected complete");
  }

  expectObject(dossier.candidate_return, "$.candidate_return", [
    "window_id",
    "measure_index",
    "onset_qn",
    "second_part_elapsed_qn",
    "second_part_total_qn"
  ]);
  if (dossier.candidate_return.window_id !== "W3") fail("$.candidate_return.window_id", "expected W3");
  if (dossier.candidate_return.measure_index !== 0) fail("$.candidate_return.measure_index", "expected 0");
  validateRational(dossier.candidate_return.onset_qn, "$.candidate_return.onset_qn");
  validateRational(dossier.candidate_return.second_part_elapsed_qn, "$.candidate_return.second_part_elapsed_qn");
  validateRational(dossier.candidate_return.second_part_total_qn, "$.candidate_return.second_part_total_qn", {positive: true});
  if (compareRational(dossier.candidate_return.second_part_elapsed_qn, dossier.candidate_return.second_part_total_qn) > 0) {
    fail("$.candidate_return.second_part_elapsed_qn", "elapsed duration exceeds total duration");
  }

  expectArray(dossier.windows, "$.windows");
  if (dossier.windows.length !== 4) fail("$.windows", "expected exactly four windows");
  const state = {
    nextEvidence: 1,
    nextEvent: 1,
    nextDirection: 1,
    voices: new Set(),
    directionVoices: new Set()
  };
  const specifications = [
    {windowId: "W1", role: "opening", indexes: [0, 1, 2, 3, 4, 5, 6, 7], allowAnacrusis: true},
    {windowId: "W2", role: "pre_candidate", indexes: [0, 1, 2, 3, 4, 5]},
    {windowId: "W3", role: "candidate", indexes: [0, 1, 2, 3, 4, 5]},
    {windowId: "W4", role: "continuation", indexes: [0, 1, 2, 3, 4, 5]}
  ];
  dossier.windows.forEach((window, index) => validateWindow(window, `$.windows[${index}]`, specifications[index], state));

  const voiceNumbers = [...state.voices].map((voice) => Number(voice.slice(1))).sort((a, b) => a - b);
  voiceNumbers.forEach((number, index) => {
    if (number !== index + 1) fail("$.windows", "voice IDs must form a contiguous sequence beginning with V01");
  });
  for (const voice of state.directionVoices) {
    if (!state.voices.has(voice)) fail("$.windows", `direction refers to unused voice ${voice}`);
  }

  const candidateMeasure = dossier.windows[2].measures[0];
  if (compareRational(dossier.candidate_return.onset_qn, candidateMeasure.notated_duration_qn) >= 0) {
    fail("$.candidate_return.onset_qn", "candidate onset must lie within W3 measure 0");
  }
  const candidateHasNote = candidateMeasure.events.some((event) => (
    event.event_type === "note"
    && compareRational(event.onset_qn, dossier.candidate_return.onset_qn) === 0
  ));
  if (!candidateHasNote) fail("$.candidate_return.onset_qn", "candidate onset must coincide with a note in W3 measure 0");

  return dossier;
};
