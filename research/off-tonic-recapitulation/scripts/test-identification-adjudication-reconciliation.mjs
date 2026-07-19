import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import {
  EXPECTED_IDENTIFICATION_JUDGMENTS,
  buildIdentificationAdjudicationReconciliation,
  writeIdentificationAdjudicationReconciliation
} from "./lib/identification-adjudication-reconciliation.mjs";

const experimentDir = path.resolve(import.meta.dirname, "..");
const adjudicationDir = path.join(experimentDir, "data", "provenance", "adjudication");
const alphaPath = path.join(adjudicationDir, "scorer-alpha.json");
const betaPath = path.join(adjudicationDir, "scorer-beta.json");
const alpha = JSON.parse(fs.readFileSync(alphaPath, "utf8"));
const beta = JSON.parse(fs.readFileSync(betaPath, "utf8"));
const beforeAdjudication = fs.readFileSync(
  path.join(experimentDir, "data", "provenance", "identification-adjudication.json")
);

const result = buildIdentificationAdjudicationReconciliation(experimentDir);
assert.equal(result.adjudication.status, "complete");
assert.equal(result.adjudication.judgments.length, EXPECTED_IDENTIFICATION_JUDGMENTS);
assert.equal(result.reconciliation.agreement.matching_level_count, EXPECTED_IDENTIFICATION_JUDGMENTS);
assert.equal(result.reconciliation.agreement.disagreement_count, 0);
assert.equal(result.reconciliation.reviewer_disclosure.music_theory_expert_reviewer, false);
assert.match(result.reconciliation.finalization.reason_selection_rule, /scorer-alpha\.json/);
const expectedReasons = new Map(alpha.map((entry) => [entry.judgment_id, entry.reason]));
const filenameMap = JSON.parse(fs.readFileSync(
  path.join(adjudicationDir, "identification-scorer-filename-map.json"),
  "utf8"
));
for (const [index, id] of Object.keys(filenameMap).entries()) {
  const judgment = result.adjudication.judgments[index];
  assert.equal(judgment.output, filenameMap[id]);
  assert.equal(judgment.reason, expectedReasons.get(id));
}

const fixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-reconciliation-test."));
try {
  const fixtureAlpha = path.join(fixtureRoot, "scorer-alpha.json");
  const fixtureBeta = path.join(fixtureRoot, "scorer-beta.json");
  fs.copyFileSync(alphaPath, fixtureAlpha);
  fs.copyFileSync(betaPath, fixtureBeta);

  const disagreement = structuredClone(beta);
  disagreement[0].level = disagreement[0].level === "L2" ? "L1" : "L2";
  fs.writeFileSync(fixtureBeta, `${JSON.stringify(disagreement, null, 2)}\n`);
  assert.throws(
    () => buildIdentificationAdjudicationReconciliation(experimentDir, {
      scorerAlphaFile: fixtureAlpha,
      scorerBetaFile: fixtureBeta
    }),
    /automatic finalization refused: 1 scorer level disagreement/
  );

  const unexpectedKey = structuredClone(beta);
  unexpectedKey[0].confidence = 1;
  fs.writeFileSync(fixtureBeta, `${JSON.stringify(unexpectedKey, null, 2)}\n`);
  assert.throws(
    () => buildIdentificationAdjudicationReconciliation(experimentDir, {
      scorerAlphaFile: fixtureAlpha,
      scorerBetaFile: fixtureBeta
    }),
    /keys differ/
  );

  const missing = beta.slice(0, -1);
  fs.writeFileSync(fixtureBeta, `${JSON.stringify(missing, null, 2)}\n`);
  assert.throws(
    () => buildIdentificationAdjudicationReconciliation(experimentDir, {
      scorerAlphaFile: fixtureAlpha,
      scorerBetaFile: fixtureBeta
    }),
    /must contain exactly 54 judgments/
  );

  const writeAdjudication = path.join(fixtureRoot, "identification-adjudication.json");
  const writeReconciliation = path.join(fixtureRoot, "identification-adjudication-reconciliation.json");
  fs.writeFileSync(writeAdjudication, result.sourceAdjudicationBody);
  const written = writeIdentificationAdjudicationReconciliation(experimentDir, result, {
    adjudicationFile: writeAdjudication,
    reconciliationFile: writeReconciliation
  });
  assert.equal(fs.readFileSync(written.adjudication, "utf8"), result.adjudicationBody);
  assert.equal(fs.readFileSync(written.reconciliation, "utf8"), result.reconciliationBody);
  assert.equal((fs.statSync(written.reconciliation).mode & 0o222), 0);
  writeIdentificationAdjudicationReconciliation(experimentDir, result, {
    adjudicationFile: writeAdjudication,
    reconciliationFile: writeReconciliation
  });
} finally {
  fs.rmSync(fixtureRoot, {recursive: true, force: true});
}

assert.deepEqual(
  fs.readFileSync(path.join(experimentDir, "data", "provenance", "identification-adjudication.json")),
  beforeAdjudication,
  "dry-run and refusal tests must not alter the live adjudication"
);

process.stdout.write("identification adjudication reconciliation tests passed\n");
