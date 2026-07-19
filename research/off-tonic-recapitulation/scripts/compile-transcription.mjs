#!/usr/bin/env node

import { readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { validateCase } from "./lib/case-validator.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TRANSCRIPTION_DIR = path.join(ROOT, "data", "provenance", "transcriptions");
const CASE_DIR = path.join(ROOT, "data", "cases");

const STEPS = ["C", "D", "E", "F", "G", "A", "B"];
const STEP_INDEX = new Map(STEPS.map((step, index) => [step, index]));
const NATURAL_PC = new Map([["C", 0], ["D", 2], ["E", 4], ["F", 5], ["G", 7], ["A", 9], ["B", 11]]);
const MAJOR_FIFTHS_TO_TONIC = new Map([
  [-7, "Cb"], [-6, "Gb"], [-5, "Db"], [-4, "Ab"], [-3, "Eb"], [-2, "Bb"], [-1, "F"],
  [0, "C"], [1, "G"], [2, "D"], [3, "A"], [4, "E"], [5, "B"], [6, "F#"], [7, "C#"]
]);
const MAJOR_TONIC_TO_FIFTHS = new Map([...MAJOR_FIFTHS_TO_TONIC].map(([fifths, tonic]) => [tonic, fifths]));

const fail = (message) => {
  throw new Error(`compile-transcription: ${message}`);
};

const gcd = (left, right) => {
  let a = Math.abs(left);
  let b = Math.abs(right);
  while (b !== 0) [a, b] = [b, a % b];
  return a;
};

const rational = (numerator, denominator = 1) => {
  if (!Number.isSafeInteger(numerator) || !Number.isSafeInteger(denominator) || denominator === 0) {
    fail(`invalid rational ${numerator}/${denominator}`);
  }
  if (denominator < 0) {
    numerator *= -1;
    denominator *= -1;
  }
  const divisor = gcd(numerator, denominator);
  return { numerator: numerator / divisor, denominator: denominator / divisor };
};

const parseRational = (value, label) => {
  if (Number.isSafeInteger(value)) return rational(value);
  if (typeof value !== "string" || !/^\d+(?:\/\d+)?$/.test(value)) {
    fail(`${label} must be a non-negative integer or fraction string`);
  }
  const [numerator, denominator = "1"] = value.split("/");
  return rational(Number(numerator), Number(denominator));
};

const addRational = (left, right) => rational(
  left.numerator * right.denominator + right.numerator * left.denominator,
  left.denominator * right.denominator
);

const compareRational = (left, right) => (
  left.numerator * right.denominator - right.numerator * left.denominator
);

const spellingParts = (value, label) => {
  const match = /^([A-G])(bb|##|b|#)?$/.exec(value);
  if (!match) fail(`${label} has unsupported spelling ${JSON.stringify(value)}`);
  return { step: match[1], alter: ({ bb: -2, b: -1, "#": 1, "##": 2 })[match[2]] ?? 0 };
};

const parsePitch = (value, label) => {
  const match = /^([A-G])(bb|##|b|#|n)?(-?\d+)$/.exec(value);
  if (!match) fail(`${label} has unsupported scientific pitch ${JSON.stringify(value)}`);
  return {
    step: match[1],
    alter: ({ bb: -2, b: -1, "#": 1, "##": 2, n: 0 })[match[2]] ?? 0,
    octave: Number(match[3])
  };
};

const pitchClass = (spelling) => {
  const { step, alter } = spellingParts(spelling, "source tonic");
  return (NATURAL_PC.get(step) + alter + 12) % 12;
};

// Port of scripts/lib/extract-dcml-mozart.py:transposition_for_tonic.
const transpositionForTonic = (tonic) => {
  const { step } = spellingParts(tonic, "source tonic");
  let chromatic = (2 - pitchClass(tonic) + 12) % 12;
  if (chromatic > 6) chromatic -= 12;

  const possible = [];
  for (let diatonic = -7; diatonic <= 7; diatonic += 1) {
    const target = (STEP_INDEX.get(step) + diatonic + 70) % 7;
    if (target === STEP_INDEX.get("D")) possible.push(diatonic);
  }
  const matchingDirection = possible.filter((interval) => (
    interval === 0 || chromatic === 0 || (interval > 0) === (chromatic > 0)
  ));
  if (matchingDirection.length === 0) fail(`cannot choose diatonic transposition for tonic ${tonic}`);
  matchingDirection.sort((left, right) => Math.abs(left) - Math.abs(right) || left - right);
  return { chromatic, diatonic: matchingDirection[0] };
};

// Port of scripts/lib/extract-dcml-mozart.py:transpose_pitch.
const transposePitch = (source, transposition, label) => {
  const pitch = parsePitch(source, label);
  const sourceMidi = 12 * (pitch.octave + 1) + NATURAL_PC.get(pitch.step) + pitch.alter;
  const absoluteDiatonic = pitch.octave * 7 + STEP_INDEX.get(pitch.step) + transposition.diatonic;
  const targetOctave = Math.floor(absoluteDiatonic / 7);
  const targetStepIndex = ((absoluteDiatonic % 7) + 7) % 7;
  const targetStep = STEPS[targetStepIndex];
  const targetMidi = sourceMidi + transposition.chromatic;
  const targetNatural = 12 * (targetOctave + 1) + NATURAL_PC.get(targetStep);
  const targetAlter = targetMidi - targetNatural;
  if (targetAlter < -4 || targetAlter > 4) fail(`${label} transposes outside the schema accidental range`);
  return { step: targetStep, alter: targetAlter, octave: targetOctave };
};

const transposeKeySignature = (fifths, transposition) => {
  const sourceSpelling = MAJOR_FIFTHS_TO_TONIC.get(fifths);
  if (!sourceSpelling) fail(`source key signature ${fifths} is unsupported`);
  const { step, alter } = spellingParts(sourceSpelling, "source key signature");
  const sourceMidi = 60 + NATURAL_PC.get(step) + alter;
  let sourceOctave = 4;
  if (NATURAL_PC.get(step) + alter >= 12) sourceOctave += 1;
  const absoluteDiatonic = sourceOctave * 7 + STEP_INDEX.get(step) + transposition.diatonic;
  const targetOctave = Math.floor(absoluteDiatonic / 7);
  const targetStep = STEPS[((absoluteDiatonic % 7) + 7) % 7];
  const targetMidi = sourceMidi + transposition.chromatic;
  const targetNatural = 12 * (targetOctave + 1) + NATURAL_PC.get(targetStep);
  const targetAlter = targetMidi - targetNatural;
  const suffix = ({ "-1": "b", 0: "", 1: "#" })[targetAlter];
  const target = suffix === undefined ? null : `${targetStep}${suffix}`;
  if (!target || !MAJOR_TONIC_TO_FIFTHS.has(target)) {
    fail(`transposed key signature ${sourceSpelling} is not representable`);
  }
  return MAJOR_TONIC_TO_FIFTHS.get(target);
};

const flattenTimeline = (segments) => {
  const result = [];
  for (const [index, segment] of segments.entries()) {
    const duration = parseRational(segment.duration_qn, `timeline[${index}].duration_qn`);
    let labels;
    if (Array.isArray(segment.range) && segment.range.length === 2) {
      const [start, end] = segment.range;
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end) {
        fail(`timeline[${index}].range is invalid`);
      }
      labels = Array.from({ length: end - start + 1 }, (_, offset) => String(start + offset));
    } else if (Array.isArray(segment.labels) && segment.labels.length > 0) {
      labels = segment.labels.map(String);
    } else {
      fail(`timeline[${index}] needs a range or labels`);
    }
    for (const label of labels) result.push({ label, duration });
  }
  const duplicates = result.filter((item, index) => result.findIndex((other) => other.label === item.label) !== index);
  if (duplicates.length > 0) fail(`timeline has duplicate label ${duplicates[0].label}`);
  return result;
};

const elapsedAndTotal = (source) => {
  const timeline = flattenTimeline(source.movement.timeline);
  const start = timeline.findIndex((item) => item.label === String(source.movement.second_part_start));
  const candidate = timeline.findIndex((item) => item.label === String(source.candidate.measure));
  if (start < 0) fail(`second-part label ${source.movement.second_part_start} is absent from timeline`);
  if (candidate < start) fail(`candidate label ${source.candidate.measure} precedes or is absent from second part`);
  let elapsed = rational(0);
  let total = rational(0);
  timeline.slice(start).forEach((item, index) => {
    total = addRational(total, item.duration);
    if (start + index < candidate) elapsed = addRational(elapsed, item.duration);
  });
  elapsed = addRational(
    elapsed,
    parseRational(source.candidate.onset_qn, `${source.case_id} candidate onset`)
  );
  return { elapsed, total };
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
    comparison = STEP_INDEX.get(left.pitch.step) - STEP_INDEX.get(right.pitch.step);
    if (comparison !== 0) return comparison;
    comparison = left.pitch.alter - right.pitch.alter;
    if (comparison !== 0) return comparison;
  }
  comparison = compareRational(left.duration_qn, right.duration_qn);
  if (comparison !== 0) return comparison;
  comparison = left.articulations.join("\0").localeCompare(right.articulations.join("\0"));
  if (comparison !== 0 || left.event_type === "rest") return comparison;
  comparison = left.tie.localeCompare(right.tie);
  if (comparison !== 0) return comparison;
  comparison = left.grace.localeCompare(right.grace);
  if (comparison !== 0) return comparison;
  return left.ornaments.join("\0").localeCompare(right.ornaments.join("\0"));
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

const compileEvent = (record, transposition, label) => {
  if (!Array.isArray(record) || record.length < 4) fail(`${label} must be an event array`);
  const [kind, onsetValue, durationValue, voiceId] = record;
  const onset_qn = parseRational(onsetValue, `${label} onset`);
  const duration_qn = parseRational(durationValue, `${label} duration`);
  if (kind === "r") {
    const options = record[4] ?? {};
    return [{
      event_type: "rest",
      onset_qn,
      duration_qn,
      voice_id: voiceId,
      articulations: [...(options.articulations ?? [])].sort()
    }];
  }
  if (kind !== "n" || !Array.isArray(record[4]) || record[4].length === 0) {
    fail(`${label} must use n with pitches or r`);
  }
  const options = record[5] ?? {};
  return record[4].map((pitch, pitchIndex) => ({
    event_type: "note",
    onset_qn,
    duration_qn,
    voice_id: voiceId,
    pitch: transposePitch(pitch, transposition, `${label} pitch ${pitchIndex + 1}`),
    tie: options.tie ?? "none",
    grace: options.grace ?? "none",
    articulations: [...(options.articulations ?? [])].sort(),
    ornaments: [...(options.ornaments ?? [])].sort()
  }));
};

const compileDirection = (record, label) => {
  if (!Array.isArray(record) || record.length !== 4) fail(`${label} must be a four-item direction array`);
  const [kind, onset, voice_id, value] = record;
  const direction_type = ({ d: "dynamic", h: "hairpin", t: "textual_gradual_dynamic" })[kind];
  if (!direction_type) fail(`${label} direction kind must be d, h, or t`);
  return { direction_type, onset_qn: parseRational(onset, `${label} onset`), voice_id, value };
};

const compileMeasure = (source, measure, windowIndex, localIndex, state, transposition) => {
  const label = `${source.case_id} measure ${measure.number}`;
  const meter = measure.meter ?? source.movement.meter;
  const duration = measure.duration_qn ?? String(meter.beats * 4 / meter.beat_type);
  const events = (measure.events ?? []).flatMap((event, index) => (
    compileEvent(event, transposition, `${label} event ${index + 1}`)
  ));
  events.sort(compareEvents);
  for (const event of events) {
    event.event_id = `EV${String(state.nextEvent).padStart(4, "0")}`;
    state.nextEvent += 1;
  }
  const directions = (measure.directions ?? []).map((direction, index) => (
    compileDirection(direction, `${label} direction ${index + 1}`)
  ));
  directions.sort(compareDirections);
  for (const direction of directions) {
    direction.direction_id = `DR${String(state.nextDirection).padStart(4, "0")}`;
    state.nextDirection += 1;
  }
  const result = {
    measure_index: localIndex,
    evidence_id: `E${String(state.nextEvidence).padStart(3, "0")}`,
    notated_duration_qn: parseRational(duration, `${label} duration`),
    meter: { beats: meter.beats, beat_type: meter.beat_type },
    key_signature: { fifths: transposeKeySignature(measure.key_fifths ?? source.movement.key_fifths, transposition) },
    left_barline: measure.left_barline ?? (String(measure.number) === "1" ? "none" : "regular"),
    right_barline: measure.right_barline ?? "regular",
    volta: measure.volta ?? "none",
    events,
    directions
  };
  state.nextEvidence += 1;
  if (windowIndex === 0 && source.movement.anacrusis && localIndex === 0) result.measure_index = -1;
  return result;
};

const compileSource = (source) => {
  if (source.operator_schema_version !== "1.0.0") fail(`${source.case_id} operator schema must be 1.0.0`);
  const transposition = transpositionForTonic(source.movement.tonic);
  const { elapsed, total } = elapsedAndTotal(source);
  const measures = new Map(source.measures.map((measure) => [String(measure.number), measure]));
  if (measures.size !== source.measures.length) fail(`${source.case_id} has duplicate transcribed measures`);
  const state = { nextEvidence: 1, nextEvent: 1, nextDirection: 1 };
  const roles = ["opening", "pre_candidate", "candidate", "continuation"];
  const windows = ["W1", "W2", "W3", "W4"].map((windowId, windowIndex) => {
    const labels = source.windows[windowId].map(String);
    const compiled = labels.map((measureLabel, localIndex) => {
      const measure = measures.get(measureLabel);
      if (!measure) fail(`${source.case_id} ${windowId} references missing measure ${measureLabel}`);
      return compileMeasure(source, measure, windowIndex, localIndex, state, transposition);
    });
    return { window_id: windowId, role: roles[windowIndex], measures: compiled };
  });
  const dossier = {
    schema_version: "3.1.0",
    case_id: source.case_id,
    condition: "symbolic",
    encoding: {
      common_tonic: "D",
      home_mode: source.movement.mode,
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
      onset_qn: parseRational(source.candidate.onset_qn, `${source.case_id} candidate onset`),
      second_part_elapsed_qn: elapsed,
      second_part_total_qn: total
    },
    windows
  };
  validateCase(dossier);
  return dossier;
};

const sourceFiles = async (requestedCase) => {
  const names = (await readdir(TRANSCRIPTION_DIR))
    .filter((name) => name.endsWith(".source.json"))
    .sort();
  const filtered = requestedCase ? names.filter((name) => name.startsWith(`${requestedCase}.`)) : names;
  if (filtered.length === 0) fail(requestedCase ? `no source found for ${requestedCase}` : "no source transcriptions found");
  return filtered.map((name) => path.join(TRANSCRIPTION_DIR, name));
};

const main = async () => {
  const args = process.argv.slice(2);
  const check = args.includes("--check");
  const caseIndex = args.indexOf("--case");
  const requestedCase = caseIndex >= 0 ? args[caseIndex + 1] : null;
  if (caseIndex >= 0 && !requestedCase) fail("--case requires a case ID");
  const allowed = new Set(["--check", "--case", requestedCase]);
  const unexpected = args.filter((arg) => !allowed.has(arg));
  if (unexpected.length > 0) fail(`unexpected argument ${unexpected[0]}`);

  for (const file of await sourceFiles(requestedCase)) {
    const source = JSON.parse(await readFile(file, "utf8"));
    const dossier = compileSource(source);
    const output = `${JSON.stringify(dossier, null, 2)}\n`;
    const outputPath = path.join(CASE_DIR, `${source.case_id}.json`);
    if (check) {
      const existing = await readFile(outputPath, "utf8");
      if (existing !== output) fail(`${path.relative(ROOT, outputPath)} is not reproducible from its source`);
      process.stdout.write(`PASS ${source.case_id} reproducible\n`);
    } else {
      await writeFile(outputPath, output);
      process.stdout.write(`WROTE ${path.relative(ROOT, outputPath)}\n`);
    }
  }
};

await main().catch((error) => {
  process.stderr.write(`${error.stack ?? error}\n`);
  process.exitCode = 1;
});
