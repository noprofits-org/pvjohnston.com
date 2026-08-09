#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
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
  if (existsSync(outputPath)) fail('refusing to overwrite metrics output');
  writeFileSync(outputPath, expected, { flag: 'wx' });
}
