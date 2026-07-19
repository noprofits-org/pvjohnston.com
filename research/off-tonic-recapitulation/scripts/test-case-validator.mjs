import assert from "node:assert/strict";
import fs from "node:fs";
import {collectEvidenceIds, validateCase} from "./lib/case-validator.mjs";

const rational = (numerator, denominator = 1) => ({numerator, denominator});

const makeDossier = ({anacrusis = false} = {}) => {
  let nextEvidence = 1;
  let nextEvent = 1;
  let nextDirection = 1;

  const makeMeasure = (measureIndex, pickup = false) => {
    const duration = pickup ? rational(1) : rational(4);
    const events = [{
      event_id: `EV${String(nextEvent++).padStart(4, "0")}`,
      event_type: "note",
      onset_qn: rational(0),
      duration_qn: rational(1),
      voice_id: "V01",
      pitch: {step: "C", alter: 0, octave: 4},
      tie: "none",
      grace: "none",
      articulations: [],
      ornaments: []
    }];
    if (!pickup) {
      events.push({
        event_id: `EV${String(nextEvent++).padStart(4, "0")}`,
        event_type: "rest",
        onset_qn: rational(1),
        duration_qn: rational(3),
        voice_id: "V01",
        articulations: []
      });
    }
    const directions = nextEvidence === 1 ? [{
      direction_id: `DR${String(nextDirection++).padStart(4, "0")}`,
      direction_type: "dynamic",
      onset_qn: rational(0),
      voice_id: null,
      value: "p"
    }] : [];
    return {
      measure_index: measureIndex,
      evidence_id: `E${String(nextEvidence++).padStart(3, "0")}`,
      notated_duration_qn: duration,
      meter: {beats: 4, beat_type: 4},
      key_signature: {fifths: 0},
      left_barline: "regular",
      right_barline: "regular",
      volta: "none",
      events,
      directions
    };
  };

  const makeWindow = (windowId, role, indexes) => ({
    window_id: windowId,
    role,
    measures: indexes.map((index) => makeMeasure(index, index === -1))
  });

  const openingIndexes = anacrusis ? [-1, 0, 1, 2, 3, 4, 5, 6, 7] : [0, 1, 2, 3, 4, 5, 6, 7];
  return {
    schema_version: "3.0.0",
    case_id: "CASE-AB12",
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
      makeWindow("W1", "opening", openingIndexes),
      makeWindow("W2", "pre_candidate", [0, 1, 2, 3, 4, 5]),
      makeWindow("W3", "candidate", [0, 1, 2, 3, 4, 5]),
      makeWindow("W4", "continuation", [0, 1, 2, 3, 4, 5])
    ]
  };
};

const changed = (mutator, options) => {
  const dossier = structuredClone(makeDossier(options));
  mutator(dossier);
  return dossier;
};

const schema = JSON.parse(fs.readFileSync(new URL("../data/schema/case.schema.json", import.meta.url), "utf8"));
assert.equal(schema.properties.schema_version.const, "3.0.0");

const valid = makeDossier();
assert.equal(validateCase(valid), valid);
assert.equal(collectEvidenceIds(valid).size, 26);

const validWithAnacrusis = makeDossier({anacrusis: true});
assert.equal(validateCase(validWithAnacrusis), validWithAnacrusis);
assert.equal(collectEvidenceIds(validWithAnacrusis).size, 27);

assert.throws(
  () => validateCase(changed((dossier) => dossier.windows[1].measures.pop())),
  /expected 6 measures/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.windows[0].measures[1].evidence_id = "E001";
  })),
  /expected canonical ID E002/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.candidate_return.onset_qn = rational(2, 2);
  })),
  /rational must be reduced/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    const event = dossier.windows[2].measures[0].events[1];
    event.onset_qn = rational(3);
    event.duration_qn = rational(2);
  })),
  /event extends beyond the measure/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.encoding.coverage.dynamics = "partial";
  })),
  /expected complete/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.candidate_return.onset_qn = rational(2);
  })),
  /must coincide with a note/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.candidate_return.second_part_elapsed_qn = rational(81);
  })),
  /elapsed duration exceeds total duration/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.composer = "anonymous";
  })),
  /identity or provenance key is prohibited/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.case_id = "CASE-K545";
  })),
  /forbidden identity or provenance text/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.windows[0].measures[0].content = "neutral-looking prose";
  })),
  /unexpected key content/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.windows[0].measures[0].directions[0].voice_id = "V02";
  })),
  /direction refers to unused voice V02/
);

assert.throws(
  () => validateCase(changed((dossier) => {
    dossier.windows[0].measures[0].events[0].articulations = ["tenuto", "accent"];
  })),
  /canonical alphabetical order/
);

process.stdout.write("case validator tests passed\n");
