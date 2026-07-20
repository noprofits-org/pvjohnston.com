#!/usr/bin/env node

// Turn the canonical Fresnel output into the small typed projection used by
// the post. In --check mode, first rerun the cheap calculation as an end-to-end
// reproducibility check, then compare the projection byte for byte.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const resultsPath = resolve(experimentDir, 'results.json');
const metricsPath = resolve(experimentDir, 'metrics.json');
const calculationPath = resolve(experimentDir, 'calculate.py');
const checkOnly = process.argv.includes('--check');

if (process.argv.length > 3 || (process.argv.length === 3 && !checkOnly)) {
  console.error('usage: node research/traceable-brewster-angle/generate-metrics.mjs [--check]');
  process.exit(2);
}

if (checkOnly) {
  const calculation = spawnSync('python3', [calculationPath, '--check'], {
    cwd: root,
    encoding: 'utf8',
    timeout: 10_000,
  });
  if (calculation.error || calculation.status !== 0) {
    const detail = calculation.error?.message || calculation.stderr || calculation.stdout;
    console.error(`end-to-end calculation check failed${detail ? `: ${detail.trim()}` : ''}`);
    process.exit(1);
  }
}

const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
const fixed = (digits) => ({ style: 'fixed', digits });
const scientific = (digits) => ({ style: 'scientific', digits });
const percent = (digits) => ({ style: 'percent', digits });
const raw = () => ({ style: 'raw' });

function numberMetric(value, format, description, unit) {
  return { type: 'number', value, format, description, ...(unit ? { unit } : {}) };
}

function integerMetric(value, description, unit) {
  return { type: 'integer', value, description, ...(unit ? { unit } : {}) };
}

function booleanMetric(value, description) {
  return { type: 'boolean', value, description };
}

function sha256(repositoryPath) {
  return createHash('sha256').update(readFileSync(resolve(root, repositoryPath))).digest('hex');
}

function buildMetrics(generatedAt) {
  const metrics = {
    incident_refractive_index: numberMetric(
      results.model.incident_refractive_index,
      fixed(1),
      'Incident-medium refractive index used by the ideal model',
      'index',
    ),
    transmitted_refractive_index: numberMetric(
      results.model.transmitted_refractive_index,
      fixed(1),
      'Transmitted-medium refractive index used by the ideal model',
      'index',
    ),
    sweep_start_angle_deg: numberMetric(
      results.model.sweep_start_degrees,
      fixed(0),
      'First incident angle in the numerical sweep',
      'degrees',
    ),
    sweep_stop_angle_deg: numberMetric(
      results.model.sweep_stop_degrees,
      fixed(0),
      'Last incident angle in the numerical sweep',
      'degrees',
    ),
    sweep_step_angle_deg: numberMetric(
      results.model.sweep_step_degrees,
      fixed(1),
      'Incident-angle spacing in the numerical sweep',
      'degrees',
    ),
    index_ratio: numberMetric(
      results.analytic.index_ratio,
      raw(),
      'Ratio of transmitted to incident refractive index',
      'ratio',
    ),
    analytic_brewster_angle_deg: numberMetric(
      results.analytic.brewster_angle_degrees,
      fixed(2),
      'Analytic Brewster angle',
      'degrees',
    ),
    grid_minimum_angle_deg: numberMetric(
      results.sweep.minimum_angle_degrees,
      fixed(1),
      'Angle of minimum p-polarized reflectance on the numerical grid',
      'degrees',
    ),
    grid_angle_error_deg: numberMetric(
      results.sweep.analytic_angle_error_degrees,
      fixed(3),
      'Absolute difference between analytic and grid-minimum angles',
      'degrees',
    ),
    normal_incidence_reflectance: numberMetric(
      results.normal_incidence.reflectance,
      percent(2),
      'Power reflectance at normal incidence',
      'fraction',
    ),
    analytic_p_reflectance: numberMetric(
      results.analytic.p_reflectance,
      scientific(1),
      'P-polarized power reflectance at the analytic Brewster angle',
      'fraction',
    ),
    analytic_s_reflectance: numberMetric(
      results.analytic.s_reflectance,
      percent(2),
      'S-polarized power reflectance at the analytic Brewster angle',
      'fraction',
    ),
    analytic_unpolarized_reflectance: numberMetric(
      results.analytic.unpolarized_reflectance,
      percent(2),
      'Mean s/p power reflectance at the analytic Brewster angle',
      'fraction',
    ),
    grid_minimum_p_reflectance: numberMetric(
      results.sweep.minimum_p_reflectance,
      scientific(1),
      'Minimum p-polarized power reflectance on the numerical grid',
      'fraction',
    ),
    maximum_energy_balance_error: numberMetric(
      results.sweep.maximum_energy_balance_error,
      scientific(1),
      'Maximum absolute R plus T minus one residual across the sweep',
      'fraction',
    ),
    analytic_p_reflectance_tolerance: numberMetric(
      results.criteria.analytic_p_reflectance_max,
      scientific(1),
      'Maximum p-polarized reflectance accepted by the analytic-null check',
      'fraction',
    ),
    grid_angle_tolerance_deg: numberMetric(
      results.criteria.grid_angle_tolerance_degrees,
      fixed(2),
      'Maximum angle error accepted by the grid check',
      'degrees',
    ),
    energy_balance_tolerance: numberMetric(
      results.criteria.energy_balance_error_max,
      scientific(1),
      'Maximum R plus T minus one residual accepted by the energy check',
      'fraction',
    ),
    sweep_sample_count: integerMetric(
      results.sweep.sample_count,
      'Number of incident angles in the numerical sweep',
      'angles',
    ),
    analytic_null_within_tolerance: booleanMetric(
      results.checks.analytic_null_within_tolerance,
      'Whether analytic p reflectance satisfies the declared null tolerance',
    ),
    grid_angle_within_tolerance: booleanMetric(
      results.checks.grid_angle_within_tolerance,
      'Whether the numerical minimum satisfies the declared angle tolerance',
    ),
    energy_balance_within_tolerance: booleanMetric(
      results.checks.energy_balance_within_tolerance,
      'Whether every swept s/p result satisfies the declared energy tolerance',
    ),
  };

  const inputPaths = [
    'research/traceable-brewster-angle/inputs.json',
    'research/traceable-brewster-angle/calculate.py',
    'research/traceable-brewster-angle/results.json',
  ];
  return {
    schema_version: 1,
    experiment: 'traceable-brewster-angle',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: inputPaths.map((path) => ({ path, sha256: sha256(path) })),
    },
    metrics,
  };
}

const existing = existsSync(metricsPath)
  ? JSON.parse(readFileSync(metricsPath, 'utf8'))
  : null;
const generatedAt = checkOnly && existing?.provenance?.generated_at
  ? existing.provenance.generated_at
  : new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const expected = `${JSON.stringify(buildMetrics(generatedAt), null, 2)}\n`;

if (checkOnly) {
  if (!existing) {
    console.error('metrics.json is missing; run the generator without --check');
    process.exit(1);
  }
  if (readFileSync(metricsPath, 'utf8') !== expected) {
    console.error('metrics.json is stale; rerun the generator');
    process.exit(1);
  }
  console.log('generate-metrics.mjs: metrics.json is current');
} else {
  writeFileSync(metricsPath, expected);
  console.log(`wrote ${relative(root, metricsPath)}`);
}
