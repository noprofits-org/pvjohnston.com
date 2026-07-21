#!/usr/bin/env node

// Project the canonical force-training sweep in results.json into typed,
// deterministically formatted values used by the accompanying post. Check mode
// also reruns the cheap analysis verifier (no retraining) before comparing
// metrics byte for byte.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const resultsPath = resolve(experimentDir, 'results.json');
const metricsPath = resolve(experimentDir, 'metrics.json');
const verifierPath = resolve(experimentDir, 'verify_analysis.py');
const arguments_ = process.argv.slice(2);
const checkOnly = arguments_.length === 1 && arguments_[0] === '--check';

if (!(arguments_.length === 0 || checkOnly)) {
  console.error('usage: node research/coulomb-force-training/generate-metrics.mjs [--check]');
  process.exit(2);
}

if (checkOnly) {
  const verify = spawnSync('python3', [verifierPath, '--check'], {
    cwd: root,
    encoding: 'utf8',
    timeout: 20_000,
  });
  if (verify.error || verify.status !== 0) {
    const detail = verify.error?.message || verify.stderr || verify.stdout;
    console.error(`analysis check failed${detail ? `: ${detail.trim()}` : ''}`);
    process.exit(1);
  }
}

if (!existsSync(resultsPath)) {
  console.error('results.json is missing; run run_experiment.py first');
  process.exit(1);
}

const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
const fixed = (digits) => ({ style: 'fixed', digits });

function numberMetric(value, format, description, unit) {
  return { type: 'number', value, format, description, ...(unit ? { unit } : {}) };
}

function sha256(repositoryPath) {
  return createHash('sha256').update(readFileSync(resolve(root, repositoryPath))).digest('hex');
}

const CUTOFF_KEYS = ['0.15', '0.25', '0.40', '0.70', '1.00', '1.50', '2.00', '3.00'];
const CUTOFF_SLUG = { '0.15': '015', '0.25': '025', '0.40': '040', '0.70': '070',
  '1.00': '100', '1.50': '150', '2.00': '200', '3.00': '300' };

function buildMetrics(generatedAt) {
  const derived = results.derived;
  const metrics = {};

  for (const loss of ['energy', 'energy_force']) {
    const pc = derived[loss].per_cutoff;
    const lossLabel = loss === 'energy' ? 'energy-only' : 'energy-plus-force';
    for (const key of CUTOFF_KEYS) {
      const slug = CUTOFF_SLUG[key];
      const name = loss === 'energy' ? `ratio_energy_${slug}` : `ratio_force_${slug}`;
      metrics[name] = numberMetric(
        pc[key].median_ab_ratio,
        fixed(2),
        `Median paired A/B out-of-fold energy-RMSE ratio at R_min = ${key} bohr under the ${lossLabel} loss`,
        'ratio',
      );
    }
  }

  metrics.energy_crossover_bohr = numberMetric(
    derived.energy.crossover_cutoff,
    fixed(1),
    'Smallest cutoff at which the median A/B ratio falls to at most one under the energy-only loss',
    'bohr',
  );
  metrics.force_crossover_bohr = numberMetric(
    derived.energy_force.crossover_cutoff,
    fixed(1),
    'Smallest cutoff at which the median A/B ratio falls to at most one under the energy-plus-force loss',
    'bohr',
  );

  const e015 = derived.energy.per_cutoff['0.15'];
  metrics.rmse_a_energy_015_cm = numberMetric(
    e015.median_rmse_a_cm,
    fixed(0),
    'Median out-of-fold RMSE of the direct total-energy fit (Scheme A) at R_min = 0.15 bohr under the energy-only loss',
    'cm^-1',
  );
  metrics.rmse_b_energy_015_cm = numberMetric(
    e015.median_rmse_b_cm,
    fixed(0),
    'Median out-of-fold RMSE of the Coulomb-subtraction fit (Scheme B) at R_min = 0.15 bohr under the energy-only loss',
    'cm^-1',
  );

  const inputPaths = [
    'research/coulomb-force-training/h2plus_model.py',
    'research/coulomb-force-training/run_experiment.py',
    'research/coulomb-force-training/verify_analysis.py',
    'research/coulomb-force-training/results.json',
  ];
  return {
    schema_version: 1,
    experiment: 'coulomb-force-training',
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
