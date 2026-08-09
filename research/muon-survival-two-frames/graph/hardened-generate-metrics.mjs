#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import {
  closeSync,
  constants as fsConstants,
  existsSync,
  fstatSync,
  fsyncSync,
  linkSync,
  lstatSync,
  openSync,
  readFileSync,
  readdirSync,
  unlinkSync,
  writeSync,
} from 'node:fs';
import { basename, dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const args = process.argv.slice(2);
const checkOnly = args.includes('--check');
const fixtureIndex = args.indexOf('--setup-fixture');
const outputIndex = args.indexOf('--output');
const fixtureMode = fixtureIndex >= 0;

function fail(message) {
  throw new Error(message);
}

const maxDerivedOutputBytes = 10 * 1024 * 1024;
const maxDerivedStagesPerTarget = 16;
const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function syncDirectory(path) {
  const descriptor = openSync(path, fsConstants.O_RDONLY | (fsConstants.O_DIRECTORY ?? 0));
  try {
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
}

function lstatMaybe(path) {
  try {
    return lstatSync(path);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

function stagePath(finalPath, digest, nonce, kind) {
  if (!/^[0-9a-f]{64}$/.test(digest) || !/^[0-9a-f]{32}$/.test(nonce) || !['tmp', 'ready'].includes(kind)) {
    fail('derived staging identity is invalid');
  }
  return resolve(dirname(finalPath), `.${basename(finalPath)}.publish-${digest}-${nonce}.${kind}`);
}

function ownedStages(finalPath) {
  const parent = dirname(finalPath);
  const pattern = new RegExp(`^\\.${escapeRegex(basename(finalPath))}\\.publish-([0-9a-f]{64})-([0-9a-f]{32})\\.(tmp|ready)$`);
  const stages = [];
  for (const entry of readdirSync(parent, { withFileTypes: true })) {
    const match = pattern.exec(entry.name);
    if (!match) continue;
    const path = resolve(parent, entry.name);
    const identity = lstatMaybe(path);
    if (!identity) continue;
    if (!entry.isFile() || entry.isSymbolicLink() || !identity.isFile() || identity.isSymbolicLink()
      || identity.uid !== process.geteuid() || identity.size > maxDerivedOutputBytes
      || ![1, 2].includes(identity.nlink)) {
      fail(`unsafe derived-output staging artifact: ${entry.name}`);
    }
    stages.push({ path, digest: match[1], kind: match[3], identity });
  }
  if (stages.length > maxDerivedStagesPerTarget) {
    fail('too many derived-output staging artifacts; manual quarantine is required');
  }
  return stages.sort((left, right) => left.path.localeCompare(right.path));
}

function unlinkSameFile(path, identity) {
  const current = lstatMaybe(path);
  if (!current) return;
  if (current.dev !== identity.dev || current.ino !== identity.ino) {
    fail('derived-output staging artifact changed during cleanup');
  }
  unlinkSync(path);
}

function quarantineStage(finalPath, stage) {
  const quarantine = resolve(
    dirname(finalPath),
    `.${basename(finalPath)}.quarantine-${randomUUID().replaceAll('-', '')}.stage`,
  );
  linkSync(stage.path, quarantine);
  try {
    unlinkSameFile(stage.path, stage.identity);
  } catch (error) {
    try { unlinkSync(quarantine); } catch (cleanupError) {
      if (cleanupError.code !== 'ENOENT') throw cleanupError;
    }
    throw error;
  }
  syncDirectory(dirname(finalPath));
  return quarantine;
}

function writeBuffer(descriptor, payload) {
  let offset = 0;
  while (offset < payload.length) {
    const written = writeSync(descriptor, payload, offset, payload.length - offset);
    if (written <= 0) fail('short derived-output staging write');
    offset += written;
  }
}

function installDerivedBytesAtomic(finalPath, payload) {
  if (!Buffer.isBuffer(payload) || payload.length > maxDerivedOutputBytes) {
    fail('derived output exceeds the registered byte boundary');
  }
  const parent = dirname(finalPath);
  const parentIdentity = lstatMaybe(parent);
  if (!parentIdentity?.isDirectory() || parentIdentity.isSymbolicLink()) {
    fail('derived-output parent must be a real directory');
  }
  const stages = ownedStages(finalPath);
  const finalIdentity = lstatMaybe(finalPath);
  if (finalIdentity) {
    if (finalIdentity.isFile() && !finalIdentity.isSymbolicLink()) {
      for (const stage of stages) {
        if (stage.kind === 'ready' && stage.identity.dev === finalIdentity.dev && stage.identity.ino === finalIdentity.ino) {
          unlinkSameFile(stage.path, stage.identity);
          syncDirectory(parent);
        }
      }
    }
    fail('refusing to overwrite metrics output');
  }

  const expectedDigest = createHash('sha256').update(payload).digest('hex');
  let ready;
  for (const stage of stages) {
    if (stage.kind === 'tmp') {
      quarantineStage(finalPath, stage);
      continue;
    }
    const exact = stage.digest === expectedDigest && readFileSync(stage.path).equals(payload);
    if (exact && !ready) ready = stage;
    else quarantineStage(finalPath, stage);
  }

  let temporary;
  if (!ready) {
    const nonce = randomUUID().replaceAll('-', '');
    const temporaryPath = stagePath(finalPath, expectedDigest, nonce, 'tmp');
    const readyPath = stagePath(finalPath, expectedDigest, nonce, 'ready');
    let descriptor;
    try {
      descriptor = openSync(
        temporaryPath,
        fsConstants.O_WRONLY | fsConstants.O_CREAT | fsConstants.O_EXCL | (fsConstants.O_NOFOLLOW ?? 0),
        0o644,
      );
      const identity = fstatSync(descriptor);
      temporary = { path: temporaryPath, identity };
      writeBuffer(descriptor, payload);
      fsyncSync(descriptor);
      closeSync(descriptor);
      descriptor = undefined;
      linkSync(temporaryPath, readyPath);
      ready = { path: readyPath, identity: lstatSync(readyPath), digest: expectedDigest, kind: 'ready' };
      unlinkSameFile(temporaryPath, identity);
      temporary = undefined;
      syncDirectory(parent);
    } finally {
      if (descriptor !== undefined) closeSync(descriptor);
      if (temporary) unlinkSameFile(temporary.path, temporary.identity);
    }
  }

  try {
    linkSync(ready.path, finalPath);
    syncDirectory(parent);
  } catch (error) {
    if (error.code === 'EEXIST') fail('refusing to overwrite metrics output');
    throw error;
  } finally {
    unlinkSameFile(ready.path, ready.identity);
    syncDirectory(parent);
  }
}

if ((fixtureIndex >= 0) !== (outputIndex >= 0)) fail('setup fixture and output must be supplied together');
const inputPath = fixtureMode
  ? resolve(args[fixtureIndex + 1] ?? '')
  : resolve(experimentDir, 'results/summary.json');
const outputPath = fixtureMode
  ? resolve(args[outputIndex + 1] ?? '')
  : resolve(experimentDir, 'metrics.json');
if (fixtureMode) {
  if (!basename(inputPath).includes('setup-toy') || !basename(outputPath).includes('setup-toy')) {
    fail('setup fixture paths must be visibly named setup-toy');
  }
  if (inputPath === resolve(experimentDir, 'results/summary.json') || outputPath === resolve(experimentDir, 'metrics.json')) {
    fail('setup fixture mode cannot address canonical outputs');
  }
}

const python = resolve(experimentDir, '.venv/bin/python');
const validator = resolve(experimentDir, 'src/validate_result.py');
const validationArgs = [validator, '--input', inputPath];
if (fixtureMode) validationArgs.push('--setup-fixture', '--repository-root', dirname(inputPath));
const inputBytes = execFileSync(python, validationArgs, {
  encoding: null,
  maxBuffer: 10 * 1024 * 1024,
  env: { ...process.env, LC_ALL: 'C', LANG: 'C', TZ: 'UTC' },
});
const result = JSON.parse(inputBytes.toString('utf8'));
if (result.experiment !== 'muon-survival-two-frames' || result.post_type !== 'understanding') fail('result identity mismatch');
if (result.outcome_kind !== 'understanding-observations-no-verdict') fail('result must not contain a Research verdict');
if (!result.generated_at?.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/)) fail('result generation timestamp is invalid');
const focal = result.focal;
const diagnostics = result.checks?.diagnostics;
if (!focal || !diagnostics) fail('result lacks focal values or diagnostics');
const requiredChecks = [
  'frame_agreement',
  'focal_monte_carlo_within_four_standard_errors',
  'maximum_grid_discrepancy_at_most_threshold',
  'counts_valid_and_monotonic',
  'numeric_shapes_dtypes_units_valid',
  'schema_manifest_provenance_and_hashes_valid',
];
for (const key of requiredChecks) if (typeof result.checks[key] !== 'boolean') fail(`missing boolean check ${key}`);

const numberMetric = (value, style, digits, description, unit = '1') => {
  if (typeof value !== 'number' || !Number.isFinite(value)) fail(`invalid numeric metric: ${description}`);
  return { type: 'number', value, format: { style, digits }, description, unit };
};
const booleanMetric = (value, description) => ({ type: 'boolean', value, description });
const standardized = diagnostics.focal_binomial_standard_error === 0
  ? (diagnostics.focal_absolute_discrepancy === 0 ? 0 : fail('undefined standardized discrepancy'))
  : diagnostics.focal_absolute_discrepancy / diagnostics.focal_binomial_standard_error;

const inputDisplayPath = fixtureMode
  ? 'setup-toy/summary.json'
  : relative(root, inputPath);
const metrics = {
  detector_beta: numberMetric(focal.detector.beta, 'fixed', 8, 'Detector-frame beta', '1'),
  detector_gamma: numberMetric(focal.detector.gamma, 'fixed', 8, 'Detector-frame gamma', '1'),
  muon_beta: numberMetric(focal.muon.beta, 'fixed', 8, 'Independently reconstructed muon-frame beta', '1'),
  muon_gamma: numberMetric(focal.muon.gamma, 'fixed', 8, 'Independently reconstructed muon-frame gamma', '1'),
  detector_distance_m: numberMetric(focal.detector.laboratory_distance_m, 'fixed', 1, 'Detector-frame laboratory distance at the focal index', 'm'),
  detector_elapsed_time_s: numberMetric(focal.detector.elapsed_time_s, 'scientific', 6, 'Detector-frame laboratory travel time at the focal index', 's'),
  detector_mean_lifetime_s: numberMetric(focal.detector.mean_lifetime_s, 'scientific', 6, 'Dilated mean lifetime in the detector frame', 's'),
  detector_decay_exponent: numberMetric(focal.detector.decay_exponent, 'fixed', 8, 'Detector-frame dimensionless decay exponent', '1'),
  muon_contracted_distance_m: numberMetric(focal.muon.contracted_distance_m, 'fixed', 6, 'Contracted path in the muon frame at the focal index', 'm'),
  muon_elapsed_time_s: numberMetric(focal.muon.elapsed_time_s, 'scientific', 6, 'Proper elapsed time in the muon frame', 's'),
  muon_mean_lifetime_s: numberMetric(focal.muon.mean_lifetime_s, 'scientific', 6, 'Proper mean lifetime in the muon frame', 's'),
  muon_decay_exponent: numberMetric(focal.muon.decay_exponent, 'fixed', 8, 'Muon-frame dimensionless decay exponent', '1'),
  analytic_survival: numberMetric(focal.detector.survival_probability, 'percent', 3, 'Analytic survival probability at the focal index', 'ratio'),
  empirical_survival: numberMetric(focal.empirical_survival_probability, 'percent', 3, 'Empirical survival from the registered sample at the focal index', 'ratio'),
  counterfactual_survival: numberMetric(focal.counterfactual.survival_probability, 'percent', 3, 'Same-speed no-lifetime-dilation counterfactual survival', 'ratio'),
  survivor_count: { type: 'integer', value: focal.empirical_count, description: 'Registered-sample survivors at the focal index', unit: 'muons' },
  focal_binomial_standard_error: numberMetric(diagnostics.focal_binomial_standard_error, 'scientific', 6, 'Prospective analytic-probability binomial standard error', 'ratio'),
  focal_standardized_discrepancy: numberMetric(standardized, 'fixed', 3, 'Focal absolute discrepancy in prospective standard-error units', '1'),
  maximum_grid_absolute_discrepancy: numberMetric(diagnostics.maximum_grid_absolute_discrepancy, 'fixed', 6, 'Maximum empirical-versus-analytic discrepancy over the frozen grid', 'ratio'),
};
for (const key of requiredChecks) metrics[`pass_${key}`] = booleanMetric(result.checks[key], `Registered fidelity check: ${key}`);
metrics.all_registered_checks_pass = booleanMetric(result.checks.all_passed, 'Whether every registered fidelity check passed');

const projection = {
  schema_version: 1,
  experiment: 'muon-survival-two-frames',
  provenance: {
    generated_at: result.generated_at,
    generator: 'research/muon-survival-two-frames/generate-metrics.mjs',
    inputs: [{ path: inputDisplayPath, sha256: createHash('sha256').update(inputBytes).digest('hex') }],
  },
  metrics,
};
const expected = `${JSON.stringify(projection, null, 2)}\n`;
if (checkOnly) {
  if (!existsSync(outputPath) || readFileSync(outputPath, 'utf8') !== expected) fail('metrics projection is missing or stale');
} else {
  installDerivedBytesAtomic(outputPath, Buffer.from(expected, 'utf8'));
}
