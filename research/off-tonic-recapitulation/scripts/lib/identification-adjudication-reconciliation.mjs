import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import {
  hashFile,
  safeRelative,
  verifyCollectionLock
} from "./collection-integrity.mjs";
import {verifyCollectionOutputChecksums} from "./identification-adjudication-packet.mjs";

export const EXPECTED_IDENTIFICATION_JUDGMENTS = 54;
export const IDENTIFICATION_RECONCILIATION_FILE = "identification-adjudication-reconciliation.json";

const ARTIFACTS = Object.freeze({
  checksumManifest: "data/provenance/collection-output-sha256.txt",
  packet: "data/provenance/adjudication/identification-scorer-packet.json",
  filenameMap: "data/provenance/adjudication/identification-scorer-filename-map.json",
  identityKey: "data/provenance/adjudication/identification-scorer-key.json",
  scorerAlpha: "data/provenance/adjudication/scorer-alpha.json",
  scorerBeta: "data/provenance/adjudication/scorer-beta.json",
  adjudication: "data/provenance/identification-adjudication.json",
  reconciliation: `data/provenance/adjudication/${IDENTIFICATION_RECONCILIATION_FILE}`
});

const LEVELS = Object.freeze({
  L2: "Uniquely correct work or catalogue identifier and movement.",
  L1: "Correct composer or work family, but not a unique work and movement.",
  L0: "Incorrect, broad style resemblance only, or abstention."
});
const ALLOWED_LEVELS = new Set(Object.keys(LEVELS));
const JUDGMENT_KEYS = Object.freeze(["judgment_id", "level", "reason"]);
const PACKET_KEYS = Object.freeze(["judgment_id", "case_id", "composer", "work", "movement"]);
const IDENTITY_KEYS = Object.freeze(["case_id", "canonical_identity", "accepted_aliases"]);
const IDENTITY_FIELDS = Object.freeze(["composer", "work", "movement"]);
const compareText = (left, right) => left < right ? -1 : left > right ? 1 : 0;
const jsonBody = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");

const readJson = (file, label) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${label} is not readable JSON: ${error.message}`);
  }
};

const exactKeys = (value, expected, location) => {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${location} must be an object`);
  }
  const actual = Object.keys(value).sort(compareText);
  const wanted = [...expected].sort(compareText);
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    throw new Error(`${location} keys differ: ${JSON.stringify(actual)}`);
  }
};

const assertRegularFile = (file, label, {readOnly = false} = {}) => {
  const stat = fs.lstatSync(file);
  if (!stat.isFile()) throw new Error(`${label} must be a regular file`);
  if (readOnly && (stat.mode & 0o222) !== 0) throw new Error(`${label} must be read-only`);
};

const expectedJudgmentIds = () => Array.from(
  {length: EXPECTED_IDENTIFICATION_JUDGMENTS},
  (_, index) => `J-${String(index + 1).padStart(4, "0")}`
);

const assertExactIds = (actualIds, expectedIds, label) => {
  const actual = [...actualIds];
  const unique = new Set(actual);
  if (unique.size !== actual.length) throw new Error(`${label} contains a duplicate judgment_id`);
  const missing = expectedIds.filter((id) => !unique.has(id));
  const extras = actual.filter((id) => !expectedIds.includes(id));
  if (missing.length || extras.length || actual.length !== expectedIds.length) {
    const details = [];
    if (missing.length) details.push(`missing ${missing.slice(0, 3).join(", ")}`);
    if (extras.length) details.push(`extra ${extras.slice(0, 3).join(", ")}`);
    throw new Error(`${label} must contain the exact ${expectedIds.length} judgment IDs${details.length ? ` (${details.join("; ")})` : ""}`);
  }
};

const artifactPath = (experimentDir, relative) => path.join(
  experimentDir,
  ...safeRelative(relative).split("/")
);

const reducedIdentityKey = (identity) => identity.cases
  .map((entry) => ({
    case_id: entry.case_id,
    canonical_identity: Object.fromEntries(IDENTITY_FIELDS.map((field) => [field, entry[field]])),
    accepted_aliases: Object.fromEntries(IDENTITY_FIELDS.map((field) => [field, [...entry.accepted_aliases[field]]]))
  }))
  .sort((left, right) => compareText(left.case_id, right.case_id));

const expectedFilenameRecords = ({lockHash, manifest, matrix}) => matrix.schedule
  .filter((slot) => slot.task === "identification")
  .map((slot) => {
    const basename = `${slot.model}__${manifest.evidence_condition}__${slot.case_id}__run-${slot.run}.md`;
    return {
      basename,
      case_id: slot.case_id,
      order_hash: sha256(`${lockHash}${basename}`)
    };
  })
  .sort((left, right) => compareText(left.order_hash, right.order_hash)
    || compareText(left.basename, right.basename));

const validatePacketArtifacts = ({experimentDir, verified, checksumState}) => {
  const {lock, manifest, matrix, identity} = verified;
  const lockPath = path.join(experimentDir, "collection-lock.json");
  const lockHash = hashFile(lockPath);
  const expectedRecords = expectedFilenameRecords({lockHash, manifest, matrix});
  if (expectedRecords.length !== EXPECTED_IDENTIFICATION_JUDGMENTS) {
    throw new Error(`frozen schedule has ${expectedRecords.length} identification slots, expected ${EXPECTED_IDENTIFICATION_JUDGMENTS}`);
  }

  const paths = Object.fromEntries(["packet", "filenameMap", "identityKey"].map((kind) => [
    kind,
    artifactPath(experimentDir, ARTIFACTS[kind])
  ]));
  for (const [kind, file] of Object.entries(paths)) {
    assertRegularFile(file, `adjudication ${kind} artifact`, {readOnly: true});
  }

  const packet = readJson(paths.packet, "identification scorer packet");
  const filenameMap = readJson(paths.filenameMap, "identification scorer filename map");
  const identityKey = readJson(paths.identityKey, "identification scorer key");
  const ids = expectedJudgmentIds();

  if (!Array.isArray(packet) || packet.length !== EXPECTED_IDENTIFICATION_JUDGMENTS) {
    throw new Error(`identification scorer packet must contain exactly ${EXPECTED_IDENTIFICATION_JUDGMENTS} entries`);
  }
  assertExactIds(packet.map((entry) => entry?.judgment_id), ids, "identification scorer packet");
  packet.forEach((entry, index) => {
    exactKeys(entry, PACKET_KEYS, `identification scorer packet[${index}]`);
    const expected = expectedRecords[index];
    if (entry.judgment_id !== ids[index]) {
      throw new Error(`identification scorer packet order mismatch at ${ids[index]}`);
    }
    if (entry.case_id !== expected.case_id) {
      throw new Error(`identification scorer packet case mismatch at ${entry.judgment_id}`);
    }
    for (const field of IDENTITY_FIELDS) {
      if (entry[field] !== null && (typeof entry[field] !== "string" || entry[field].trim() === "")) {
        throw new Error(`identification scorer packet ${entry.judgment_id}.${field} must be null or a nonempty string`);
      }
    }
  });

  exactKeys(filenameMap, ids, "identification scorer filename map");
  ids.forEach((id, index) => {
    const expected = expectedRecords[index].basename;
    if (filenameMap[id] !== expected) {
      throw new Error(`identification scorer filename map mismatch at ${id}`);
    }
    const rawRelative = `outputs/${manifest.dataset_version}/scheduled/identification/${expected}`;
    if (!checksumState.recorded_paths.has(rawRelative)) {
      throw new Error(`masked filename map output is absent from raw checksums: ${expected}`);
    }
  });
  const invalidIdentification = [...checksumState.recorded_paths].filter((relative) => (
    relative.startsWith(`outputs/${manifest.dataset_version}/scheduled/identification/`)
      && relative.endsWith(".invalid.md")
  ));
  if (invalidIdentification.length) {
    throw new Error("automatic identification reconciliation requires 54 valid outputs and found an invalid response");
  }

  const expectedKey = reducedIdentityKey(identity);
  if (JSON.stringify(identityKey) !== JSON.stringify(expectedKey)) {
    throw new Error("identification scorer key does not exactly match the frozen reduced identity key");
  }
  identityKey.forEach((entry, index) => {
    exactKeys(entry, IDENTITY_KEYS, `identification scorer key[${index}]`);
    exactKeys(entry.canonical_identity, IDENTITY_FIELDS, `identification scorer key[${index}].canonical_identity`);
    exactKeys(entry.accepted_aliases, IDENTITY_FIELDS, `identification scorer key[${index}].accepted_aliases`);
  });

  if (checksumState.recorded_paths.size !== matrix.schedule.length * 5) {
    throw new Error(`raw checksum coverage is ${checksumState.recorded_paths.size}, expected ${matrix.schedule.length * 5}`);
  }

  return {
    filenameMap,
    ids,
    hashes: {
      [ARTIFACTS.packet]: hashFile(paths.packet),
      [ARTIFACTS.filenameMap]: hashFile(paths.filenameMap),
      [ARTIFACTS.identityKey]: hashFile(paths.identityKey)
    },
    lockedFileCount: Object.keys(lock.files).length
  };
};

const validateScorer = (file, label, expectedIds) => {
  assertRegularFile(file, label);
  const scorer = readJson(file, label);
  if (!Array.isArray(scorer) || scorer.length !== EXPECTED_IDENTIFICATION_JUDGMENTS) {
    throw new Error(`${label} must contain exactly ${EXPECTED_IDENTIFICATION_JUDGMENTS} judgments`);
  }
  scorer.forEach((entry, index) => {
    exactKeys(entry, JUDGMENT_KEYS, `${label}[${index}]`);
    if (typeof entry.judgment_id !== "string") throw new Error(`${label}[${index}].judgment_id must be a string`);
    if (!ALLOWED_LEVELS.has(entry.level)) throw new Error(`${label} has invalid level at ${entry.judgment_id}`);
    if (typeof entry.reason !== "string" || entry.reason.trim() === "") {
      throw new Error(`${label} has an empty reason at ${entry.judgment_id}`);
    }
  });
  assertExactIds(scorer.map((entry) => entry.judgment_id), expectedIds, label);
  return new Map(scorer.map((entry) => [entry.judgment_id, entry]));
};

const validateExistingAdjudication = (file, intended) => {
  const existing = readJson(file, "identification adjudication");
  exactKeys(existing, ["schema_version", "status", "levels", "judgments"], "identification adjudication");
  if (existing.schema_version !== "1.0.0") throw new Error("identification adjudication schema mismatch");
  if (JSON.stringify(existing.levels) !== JSON.stringify(LEVELS)) {
    throw new Error("identification adjudication level definitions differ from the frozen scoring levels");
  }
  if (existing.status === "development") {
    if (!Array.isArray(existing.judgments) || existing.judgments.length !== 0) {
      throw new Error("development identification adjudication must have no judgments");
    }
  } else if (existing.status === "complete") {
    if (jsonBody(existing) !== jsonBody(intended)) {
      throw new Error("refusing to replace a different completed identification adjudication");
    }
  } else {
    throw new Error(`identification adjudication has unsupported status: ${existing.status}`);
  }
  return fs.readFileSync(file, "utf8");
};

export function buildIdentificationAdjudicationReconciliation(experimentDir, options = {}) {
  const verified = verifyCollectionLock(experimentDir);
  const checksumState = verifyCollectionOutputChecksums(experimentDir, verified.manifest.dataset_version);
  const packetState = validatePacketArtifacts({experimentDir, verified, checksumState});
  const scorerFiles = {
    alpha: options.scorerAlphaFile ?? artifactPath(experimentDir, ARTIFACTS.scorerAlpha),
    beta: options.scorerBetaFile ?? artifactPath(experimentDir, ARTIFACTS.scorerBeta)
  };
  const alpha = validateScorer(scorerFiles.alpha, "scorer-alpha", packetState.ids);
  const beta = validateScorer(scorerFiles.beta, "scorer-beta", packetState.ids);
  const disagreements = packetState.ids
    .filter((id) => alpha.get(id).level !== beta.get(id).level)
    .map((id) => ({
      judgment_id: id,
      scorer_alpha_level: alpha.get(id).level,
      scorer_beta_level: beta.get(id).level
    }));
  if (disagreements.length) {
    throw new Error(
      `automatic finalization refused: ${disagreements.length} scorer level disagreement(s): ${disagreements.slice(0, 5).map((entry) => entry.judgment_id).join(", ")}`
    );
  }

  const judgments = packetState.ids.map((id) => ({
    output: packetState.filenameMap[id],
    level: alpha.get(id).level,
    reason: alpha.get(id).reason
  }));
  const adjudication = {
    schema_version: "1.0.0",
    status: "complete",
    levels: {...LEVELS},
    judgments
  };
  const adjudicationBody = jsonBody(adjudication);
  const adjudicationPath = options.adjudicationFile ?? artifactPath(experimentDir, ARTIFACTS.adjudication);
  const sourceAdjudicationBody = validateExistingAdjudication(adjudicationPath, adjudication);
  const reconciliation = {
    schema_version: "1.0.0",
    status: "complete",
    reconciliation_method: "deterministic_unanimous_level_join",
    inputs: {
      collection_lock_sha256: hashFile(path.join(experimentDir, "collection-lock.json")),
      collection_lock_file_count: packetState.lockedFileCount,
      collection_output_checksum_manifest_sha256: hashFile(artifactPath(experimentDir, ARTIFACTS.checksumManifest)),
      collection_output_record_count: checksumState.recorded_paths.size,
      packet_artifact_sha256: packetState.hashes,
      scorer_artifact_sha256: {
        [ARTIFACTS.scorerAlpha]: hashFile(scorerFiles.alpha),
        [ARTIFACTS.scorerBeta]: hashFile(scorerFiles.beta)
      }
    },
    agreement: {
      expected_judgment_count: EXPECTED_IDENTIFICATION_JUDGMENTS,
      scorer_alpha_judgment_count: alpha.size,
      scorer_beta_judgment_count: beta.size,
      matching_level_count: EXPECTED_IDENTIFICATION_JUDGMENTS,
      disagreement_count: 0,
      disagreement_judgment_ids: []
    },
    finalization: {
      output: ARTIFACTS.adjudication,
      output_sha256: sha256(adjudicationBody),
      filename_map: ARTIFACTS.filenameMap,
      reason_selection_rule: "For every unanimous level, copy the reason verbatim from scorer-alpha.json."
    },
    reviewer_disclosure: {
      music_theory_expert_reviewer: false,
      method: "Two independent Codex-agent factual scoring passes under human operator supervision; no music-theory expert validation."
    }
  };

  return {
    adjudication,
    adjudicationBody,
    reconciliation,
    reconciliationBody: jsonBody(reconciliation),
    sourceAdjudicationBody,
    scorerFiles
  };
}

const writeExactOrRefuse = (file, body, {readOnly = false} = {}) => {
  if (fs.existsSync(file)) {
    if (fs.readFileSync(file, "utf8") !== body) throw new Error(`refusing to overwrite a different artifact: ${file}`);
    return;
  }
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, body, {flag: "wx", mode: readOnly ? 0o444 : 0o644});
  if (readOnly) fs.chmodSync(file, 0o444);
};

export function writeIdentificationAdjudicationReconciliation(experimentDir, result, options = {}) {
  const adjudicationPath = options.adjudicationFile ?? artifactPath(experimentDir, ARTIFACTS.adjudication);
  const reconciliationPath = options.reconciliationFile ?? artifactPath(experimentDir, ARTIFACTS.reconciliation);
  const currentAdjudicationBody = fs.readFileSync(adjudicationPath, "utf8");
  if (currentAdjudicationBody !== result.sourceAdjudicationBody
      && currentAdjudicationBody !== result.adjudicationBody) {
    throw new Error("identification adjudication changed after reconciliation validation");
  }
  if (fs.existsSync(reconciliationPath)
      && fs.readFileSync(reconciliationPath, "utf8") !== result.reconciliationBody) {
    throw new Error(`refusing to overwrite a different artifact: ${reconciliationPath}`);
  }

  if (currentAdjudicationBody !== result.adjudicationBody) {
    const temporary = `${adjudicationPath}.reconcile-${process.pid}`;
    try {
      fs.writeFileSync(temporary, result.adjudicationBody, {flag: "wx", mode: 0o644});
      fs.renameSync(temporary, adjudicationPath);
    } finally {
      if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
    }
  }
  writeExactOrRefuse(reconciliationPath, result.reconciliationBody, {readOnly: true});

  return {
    adjudication: adjudicationPath,
    reconciliation: reconciliationPath
  };
}
