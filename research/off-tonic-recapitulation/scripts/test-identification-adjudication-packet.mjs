import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import {hashFile} from "./lib/collection-integrity.mjs";
import {
  ADJUDICATION_ARTIFACT_FILES,
  buildIdentificationAdjudicationArtifacts,
  verifyCollectionOutputChecksums,
  writeIdentificationAdjudicationArtifacts
} from "./lib/identification-adjudication-packet.mjs";

const experimentDir = path.resolve(import.meta.dirname, "..");
const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const compareText = (left, right) => left < right ? -1 : left > right ? 1 : 0;
const exactKeys = (value, keys) => assert.deepEqual(Object.keys(value).sort(), [...keys].sort());
const forbiddenKey = /model|provider|(^|_)run($|_)|confidence|recognition_level|evidence|prose|aggregate/i;
const assertMasked = (value) => {
  if (Array.isArray(value)) return value.forEach(assertMasked);
  if (!value || typeof value !== "object") return;
  for (const [key, nested] of Object.entries(value)) {
    assert.doesNotMatch(key, forbiddenKey);
    assertMasked(nested);
  }
};

const artifacts = buildIdentificationAdjudicationArtifacts(experimentDir);
assert.equal(artifacts.packet.length, 54);
assert.equal(Object.keys(artifacts.filenameMap).length, 54);
assert.equal(artifacts.identityKey.length, 6);
assertMasked(artifacts.packet);

for (const entry of artifacts.packet) {
  exactKeys(entry, ["judgment_id", "case_id", "composer", "work", "movement"]);
  assert.match(entry.judgment_id, /^J-[0-9]{4}$/);
  assert.match(entry.case_id, /^CASE-[A-Z0-9]{4}$/);
  for (const field of ["composer", "work", "movement"]) {
    assert.equal(entry[field] === null || typeof entry[field] === "string", true);
  }
}

const matrix = JSON.parse(fs.readFileSync(path.join(experimentDir, "run-matrix.json"), "utf8"));
const manifest = JSON.parse(fs.readFileSync(path.join(experimentDir, "data", "manifest.json"), "utf8"));
const lockHash = hashFile(path.join(experimentDir, "collection-lock.json"));
const expectedBasenames = matrix.schedule
  .filter((slot) => slot.task === "identification")
  .map((slot) => `${slot.model}__${manifest.evidence_condition}__${slot.case_id}__run-${slot.run}.md`)
  .sort((left, right) => compareText(sha256(`${lockHash}${left}`), sha256(`${lockHash}${right}`))
    || compareText(left, right));
assert.equal(expectedBasenames.length, 54);
assert.deepEqual(Object.values(artifacts.filenameMap), expectedBasenames);
assert.deepEqual(
  artifacts.packet.map((entry) => entry.judgment_id),
  Array.from({length: 54}, (_, index) => `J-${String(index + 1).padStart(4, "0")}`)
);
assert.deepEqual(Object.keys(artifacts.filenameMap), artifacts.packet.map((entry) => entry.judgment_id));
for (const [judgmentId, basename] of Object.entries(artifacts.filenameMap)) {
  const packetEntry = artifacts.packet.find((entry) => entry.judgment_id === judgmentId);
  assert.equal(basename.includes(`__${packetEntry.case_id}__`), true);
}
const caseCoverage = new Map();
for (const entry of artifacts.packet) caseCoverage.set(entry.case_id, (caseCoverage.get(entry.case_id) ?? 0) + 1);
assert.deepEqual([...caseCoverage.values()].sort((left, right) => left - right), [9, 9, 9, 9, 9, 9]);

for (const entry of artifacts.identityKey) {
  exactKeys(entry, ["case_id", "canonical_identity", "accepted_aliases"]);
  exactKeys(entry.canonical_identity, ["composer", "work", "movement"]);
  exactKeys(entry.accepted_aliases, ["composer", "work", "movement"]);
  assert.equal("role" in entry, false);
  assert.equal("probe_role" in entry, false);
  assert.equal("candidate_measure" in entry, false);
}

const writeRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-adjudication-write-test."));
try {
  const written = writeIdentificationAdjudicationArtifacts(writeRoot, artifacts);
  assert.deepEqual(Object.keys(written).sort(), Object.keys(ADJUDICATION_ARTIFACT_FILES).sort());
  const firstBodies = Object.fromEntries(Object.entries(written).map(([kind, file]) => [kind, fs.readFileSync(file)]));
  const second = writeIdentificationAdjudicationArtifacts(writeRoot, artifacts);
  for (const kind of Object.keys(written)) {
    assert.deepEqual(fs.readFileSync(second[kind]), firstBodies[kind]);
    assert.equal((fs.statSync(second[kind]).mode & 0o222), 0);
  }
} finally {
  fs.rmSync(writeRoot, {recursive: true, force: true});
}

const tamperRoot = fs.mkdtempSync(path.join(os.tmpdir(), "off-tonic-adjudication-tamper-test."));
const tamperExperiment = path.join(tamperRoot, "experiment");
try {
  fs.cpSync(experimentDir, tamperExperiment, {
    recursive: true,
    filter: (source) => {
      const relative = path.relative(experimentDir, source);
      return !["data/sources", "data/provenance/adjudication", "tmp"].some((excluded) => (
        relative === excluded || relative.startsWith(`${excluded}${path.sep}`)
      ));
    }
  });

  const lockedFile = path.join(tamperExperiment, "data", "provenance", "IDENTIFICATION_SCORING.md");
  const lockedBody = fs.readFileSync(lockedFile);
  fs.appendFileSync(lockedFile, "\nlock tamper\n");
  assert.throws(
    () => buildIdentificationAdjudicationArtifacts(tamperExperiment),
    /locked file changed: data\/provenance\/IDENTIFICATION_SCORING\.md/
  );
  fs.writeFileSync(lockedFile, lockedBody);

  const responseRelative = expectedBasenames[0];
  const rawResponse = path.join(
    tamperExperiment,
    "outputs",
    manifest.dataset_version,
    "scheduled",
    "identification",
    responseRelative
  );
  fs.chmodSync(rawResponse, 0o644);
  fs.appendFileSync(rawResponse, "\nraw-output tamper\n");
  assert.throws(
    () => buildIdentificationAdjudicationArtifacts(tamperExperiment),
    /collection output checksum mismatch:/
  );

  const checksumState = verifyCollectionOutputChecksums(experimentDir, manifest.dataset_version);
  assert.equal(checksumState.recorded_paths.size, 540);
} finally {
  fs.rmSync(tamperRoot, {recursive: true, force: true});
}

process.stdout.write("identification adjudication packet tests passed\n");
