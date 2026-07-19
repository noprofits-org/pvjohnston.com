import assert from "node:assert/strict";
import {collectEvidenceIds, countWords, parseAndValidateResponse} from "./lib/response-validator.mjs";

const fence = String.fromCharCode(96).repeat(3);
const caseId = "CASE-A001";
const dossier = {
  schema_version: "3.0.0",
  case_id: caseId,
  windows: ["W1", "W2", "W3", "W4"].map((windowId, windowIndex) => ({
    window_id: windowId,
    measures: [0, 1].map((relativeMeasure) => ({
      evidence_id: `E${windowIndex * 2 + relativeMeasure + 1}`,
      relative_measure: relativeMeasure
    }))
  }))
};

const cueNames = [
  "tonal_stability",
  "thematic_correspondence",
  "preparation_strength",
  "proportional_location",
  "rhetorical_emphasis",
  "rotational_continuation"
];

const analysisResult = () => ({
  case_note: "The supplied evidence supports a deliberately cautious summary.",
  status_distribution: {
    tonic_double_return: 0.2,
    not_recapitulation: 0.3,
    off_tonic_recapitulation: 0.5
  },
  cues: Object.fromEntries([...cueNames].reverse().map((cue, index) => [cue, {
    reason: "Observed notes support this inference.",
    evidence_ids: [`E${index + 1}`],
    score: index === 0 ? null : index % 5
  }])),
  case_id: caseId,
  analyst_model: "test-model",
  schema_version: "2.0.0"
});

const identificationResult = (overrides = {}) => ({
  identification: {
    reason: "The dossier does not support a specific identification.",
    evidence_ids: ["E1"],
    confidence: 0.1,
    movement: null,
    work: null,
    composer: null,
    recognition_level: "none",
    ...overrides
  },
  case_id: caseId,
  analyst_model: "test-model",
  schema_version: "2.0.0"
});

const markdown = (task, result, limitations = "No material limitation beyond the supplied dossier.") => {
  const title = task === "analysis" ? "# Analysis result" : "# Identification probe result";
  return `${title}\n\n## Run metadata\n\nTest fixture.\n\n## Machine-readable result\n\n${fence}json\n${JSON.stringify(result, null, 2)}\n${fence}\n\n## Limitations\n\n${limitations}\n`;
};

const accept = (task, result, limitations) => parseAndValidateResponse({
  task,
  expectedCase: caseId,
  dossier,
  response: markdown(task, result, limitations)
});

const reject = (task, result, pattern, limitations) => {
  assert.throws(() => accept(task, result, limitations), pattern);
};

assert.deepEqual([...collectEvidenceIds(dossier)], ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]);
assert.equal(countWords("one two-three four's five’s"), 4);
assert.deepEqual(accept("analysis", analysisResult()), analysisResult());
assert.deepEqual(accept("identification", identificationResult()), identificationResult());

const extraTopLevel = analysisResult();
extraTopLevel.unexpected = true;
reject("analysis", extraTopLevel, /extra unexpected/);

const missingCue = analysisResult();
delete missingCue.cues.tonal_stability;
reject("analysis", missingCue, /missing tonal_stability/);

const extraCueKey = analysisResult();
extraCueKey.cues.tonal_stability.extra = true;
reject("analysis", extraCueKey, /extra extra/);

const badScore = analysisResult();
badScore.cues.tonal_stability.score = 2.5;
reject("analysis", badScore, /integer from 0 to 4 or null/);

const badEvidence = analysisResult();
badEvidence.cues.tonal_stability.evidence_ids = ["E999"];
reject("analysis", badEvidence, /unknown evidence ID E999/);

const duplicateEvidence = analysisResult();
duplicateEvidence.cues.tonal_stability.evidence_ids = ["E1", "E1"];
reject("analysis", duplicateEvidence, /duplicate evidence ID E1/);

const badDistribution = analysisResult();
badDistribution.status_distribution.tonic_double_return = 0.3;
reject("analysis", badDistribution, /do not sum to 1/);

const longReason = analysisResult();
longReason.cues.tonal_stability.reason = Array(41).fill("word").join(" ");
reject("analysis", longReason, /exceeds 40 words/);

const longCaseNote = analysisResult();
longCaseNote.case_note = Array(41).fill("word").join(" ");
reject("analysis", longCaseNote, /exceeds 40 words/);

reject("identification", identificationResult({composer: "Mozart"}), /none identification must not name/);
reject("identification", identificationResult({
  recognition_level: "style_only",
  composer: "Mozart",
  work: "Piano Sonata",
  movement: null
}), /style_only identification must not name/);
reject("identification", identificationResult({
  recognition_level: "specific_candidate",
  composer: "Mozart",
  work: null,
  movement: "i"
}), /specific_candidate identification must name a work/);

const validSpecific = identificationResult({
  recognition_level: "specific_candidate",
  composer: "Mozart",
  work: "K. 545",
  movement: "i",
  confidence: 0.8
});
assert.deepEqual(accept("identification", validSpecific), validSpecific);

const longIdentificationReason = identificationResult();
longIdentificationReason.identification.reason = Array(61).fill("word").join(" ");
reject("identification", longIdentificationReason, /exceeds 60 words/);

reject("analysis", analysisResult(), /exceeds 100 words/, Array(101).fill("word").join(" "));

const wrongHeadings = markdown("analysis", analysisResult()).replace("## Run metadata", "## Metadata");
assert.throws(() => parseAndValidateResponse({task: "analysis", expectedCase: caseId, dossier, response: wrongHeadings}), /unexpected heading sequence/);

const extraJsonBlock = `${markdown("analysis", analysisResult())}\n${fence}json\n{}\n${fence}\n`;
assert.throws(() => parseAndValidateResponse({task: "analysis", expectedCase: caseId, dossier, response: extraJsonBlock}), /expected one JSON block, found 2/);

const proseInMachineSection = markdown("analysis", analysisResult()).replace(
  "## Machine-readable result\n\n",
  "## Machine-readable result\n\nUnexpected prose.\n\n"
);
assert.throws(() => parseAndValidateResponse({task: "analysis", expectedCase: caseId, dossier, response: proseInMachineSection}), /must contain only one fenced json block/);

const duplicateDossierEvidence = structuredClone(dossier);
duplicateDossierEvidence.windows[1].measures[0].evidence_id = "E1";
assert.throws(() => collectEvidenceIds(duplicateDossierEvidence), /duplicate dossier evidence ID: E1/);

process.stdout.write("response validator tests passed\n");
