import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import {hashFile, safeRelative, verifyCollectionLock} from "./collection-integrity.mjs";
import {parseAndValidateResponse} from "./response-validator.mjs";
import {inspectScheduledBundle} from "./scheduled-bundle-integrity.mjs";

export const ADJUDICATION_ARTIFACT_FILES = Object.freeze({
  packet: "identification-scorer-packet.json",
  filenameMap: "identification-scorer-filename-map.json",
  identityKey: "identification-scorer-key.json"
});

const CHECKSUM_MANIFEST = path.posix.join(
  "data",
  "provenance",
  "collection-output-sha256.txt"
);

const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
const readJson = (file, label) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${label} is not readable JSON: ${error.message}`);
  }
};
const compareText = (left, right) => left < right ? -1 : left > right ? 1 : 0;
const relativePosix = (root, file) => path.relative(root, file).split(path.sep).join("/");

const assertSameStringSet = (actual, expected, label) => {
  const actualSorted = [...actual].sort(compareText);
  const expectedSorted = [...expected].sort(compareText);
  if (JSON.stringify(actualSorted) !== JSON.stringify(expectedSorted)) {
    const actualSet = new Set(actualSorted);
    const expectedSet = new Set(expectedSorted);
    const missing = expectedSorted.filter((item) => !actualSet.has(item));
    const extra = actualSorted.filter((item) => !expectedSet.has(item));
    const details = [];
    if (missing.length) details.push(`missing ${missing.slice(0, 3).join(", ")}`);
    if (extra.length) details.push(`extra ${extra.slice(0, 3).join(", ")}`);
    throw new Error(`${label} file set mismatch${details.length ? ` (${details.join("; ")})` : ""}`);
  }
};

const listRegularFiles = (directory) => {
  if (!fs.existsSync(directory)) throw new Error(`collection output directory is missing: ${directory}`);
  const files = [];
  const visit = (current) => {
    for (const entry of fs.readdirSync(current, {withFileTypes: true})) {
      const file = path.join(current, entry.name);
      if (entry.isDirectory()) {
        visit(file);
      } else if (entry.isFile()) {
        files.push(file);
      } else {
        throw new Error(`collection output contains a non-regular entry: ${file}`);
      }
    }
  };
  visit(directory);
  return files;
};

export function verifyCollectionOutputChecksums(experimentDir, datasetVersion) {
  if (typeof datasetVersion !== "string" || !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(datasetVersion)) {
    throw new Error("unsafe dataset version for collection checksum verification");
  }

  const checksumPath = path.join(experimentDir, ...CHECKSUM_MANIFEST.split("/"));
  const body = fs.readFileSync(checksumPath, "utf8");
  if (!body.endsWith("\n")) throw new Error("collection output checksum manifest must end with a newline");
  const lines = body.slice(0, -1).split("\n");
  if (lines.length === 0 || lines.some((line) => line === "")) {
    throw new Error("collection output checksum manifest contains an empty record");
  }

  const scheduledPrefix = `outputs/${datasetVersion}/scheduled/`;
  const recorded = new Map();
  for (const [index, line] of lines.entries()) {
    const match = line.match(/^([0-9a-f]{64})  ([A-Za-z0-9._/-]+)$/);
    if (!match) throw new Error(`malformed collection output checksum at line ${index + 1}`);
    const relative = safeRelative(match[2]).replaceAll("\\", "/");
    if (!relative.startsWith(scheduledPrefix)) {
      throw new Error(`collection output checksum path is outside the scheduled corpus: ${relative}`);
    }
    if (recorded.has(relative)) throw new Error(`duplicate collection output checksum path: ${relative}`);
    recorded.set(relative, match[1]);
  }

  const scheduledRoot = path.join(experimentDir, "outputs", datasetVersion, "scheduled");
  const actualFiles = listRegularFiles(scheduledRoot);
  const actualRelatives = actualFiles.map((file) => relativePosix(experimentDir, file));
  assertSameStringSet(actualRelatives, recorded.keys(), "collection output checksum manifest");

  for (const relative of actualRelatives) {
    const expected = recorded.get(relative);
    const actual = hashFile(path.join(experimentDir, ...relative.split("/")));
    if (actual !== expected) throw new Error(`collection output checksum mismatch: ${relative}`);
  }

  return {
    checksum_manifest_sha256: hashFile(checksumPath),
    recorded_paths: new Set(recorded.keys())
  };
}

const assertIdentityField = (value, location) => {
  if (typeof value !== "string" || value.trim() === "") throw new Error(`${location} must be a nonempty string`);
};

const makeReducedIdentityKey = (identity) => identity.cases
  .map((entry) => {
    for (const field of ["composer", "work", "movement"]) {
      assertIdentityField(entry[field], `identity ${entry.case_id}.${field}`);
      if (!Array.isArray(entry.accepted_aliases?.[field])
          || entry.accepted_aliases[field].some((alias) => typeof alias !== "string" || alias.trim() === "")) {
        throw new Error(`identity ${entry.case_id}.accepted_aliases.${field} must be an array of nonempty strings`);
      }
    }
    return {
      case_id: entry.case_id,
      canonical_identity: {
        composer: entry.composer,
        work: entry.work,
        movement: entry.movement
      },
      accepted_aliases: {
        composer: [...entry.accepted_aliases.composer],
        work: [...entry.accepted_aliases.work],
        movement: [...entry.accepted_aliases.movement]
      }
    };
  })
  .sort((left, right) => compareText(left.case_id, right.case_id));

const expectedBundlePaths = (experimentDir, bundle) => {
  const response = bundle.outcome === "valid" ? bundle.paths.response : bundle.paths.invalidResponse;
  return [
    bundle.paths.attempt,
    response,
    bundle.paths.metadata,
    bundle.paths.stderr,
    bundle.paths.marker
  ].map((file) => relativePosix(experimentDir, file));
};

export function buildIdentificationAdjudicationArtifacts(experimentDir) {
  const verified = verifyCollectionLock(experimentDir);
  const {lock, manifest, matrix, identity} = verified;
  const checksumState = verifyCollectionOutputChecksums(experimentDir, manifest.dataset_version);
  const dossiers = new Map(manifest.cases.map((entry) => [
    entry.case_id,
    readJson(path.join(experimentDir, "data", ...safeRelative(entry.file).split("/")), `dossier ${entry.case_id}`)
  ]));

  const expectedRawPaths = [];
  const identificationRecords = [];
  let identificationSlots = 0;
  for (const slot of matrix.schedule) {
    const bundle = inspectScheduledBundle(experimentDir, verified, slot);
    if (bundle.state !== "complete") {
      throw new Error(`scheduled slot ${slot.sequence} has not terminated in a complete bundle`);
    }
    expectedRawPaths.push(...expectedBundlePaths(experimentDir, bundle));
    if (slot.task !== "identification") continue;
    identificationSlots += 1;
    if (bundle.outcome !== "valid") continue;

    const response = fs.readFileSync(bundle.paths.response, "utf8");
    const parsed = parseAndValidateResponse({
      task: "identification",
      expectedCase: slot.case_id,
      dossier: dossiers.get(slot.case_id),
      response
    });
    identificationRecords.push({
      response_basename: path.basename(bundle.paths.response),
      case_id: slot.case_id,
      composer: parsed.identification.composer,
      work: parsed.identification.work,
      movement: parsed.identification.movement
    });
  }

  if (matrix.schedule.length !== 108) throw new Error(`expected 108 terminated slots, received ${matrix.schedule.length}`);
  if (identificationSlots !== 54) throw new Error(`expected 54 identification slots, received ${identificationSlots}`);
  if (identificationRecords.length !== 54) {
    throw new Error(`valid identification coverage is ${identificationRecords.length}/54; packet creation requires exact coverage`);
  }
  assertSameStringSet(
    checksumState.recorded_paths,
    expectedRawPaths,
    "scheduled bundle/checksum manifest"
  );

  const collectionLockHash = hashFile(path.join(experimentDir, "collection-lock.json"));
  const ordered = identificationRecords
    .map((record) => ({
      ...record,
      order_hash: sha256(`${collectionLockHash}${record.response_basename}`)
    }))
    .sort((left, right) => compareText(left.order_hash, right.order_hash)
      || compareText(left.response_basename, right.response_basename));

  const packet = [];
  const filenameMap = {};
  ordered.forEach((record, index) => {
    const judgmentId = `J-${String(index + 1).padStart(4, "0")}`;
    packet.push({
      judgment_id: judgmentId,
      case_id: record.case_id,
      composer: record.composer,
      work: record.work,
      movement: record.movement
    });
    filenameMap[judgmentId] = record.response_basename;
  });

  return {
    packet,
    filenameMap,
    identityKey: makeReducedIdentityKey(identity)
  };
}

const jsonBody = (value) => `${JSON.stringify(value, null, 2)}\n`;

export function writeIdentificationAdjudicationArtifacts(experimentDir, artifacts) {
  const targetDirectory = path.join(experimentDir, "data", "provenance", "adjudication");
  fs.mkdirSync(targetDirectory, {recursive: true});
  const values = {
    packet: artifacts.packet,
    filenameMap: artifacts.filenameMap,
    identityKey: artifacts.identityKey
  };
  const written = {};
  for (const [kind, filename] of Object.entries(ADJUDICATION_ARTIFACT_FILES)) {
    const target = path.join(targetDirectory, filename);
    const body = jsonBody(values[kind]);
    if (fs.existsSync(target)) {
      if (fs.readFileSync(target, "utf8") !== body) {
        throw new Error(`refusing to overwrite a different adjudication artifact: ${target}`);
      }
    } else {
      fs.writeFileSync(target, body, {flag: "wx", mode: 0o444});
      fs.chmodSync(target, 0o444);
    }
    written[kind] = target;
  }
  return written;
}
