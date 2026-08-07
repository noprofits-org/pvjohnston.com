#!/usr/bin/env node

// Project the canonical force-weight sweep into typed values used by the
// accompanying post. Check mode first runs the independent analysis verifier,
// then requires the committed projection to match byte for byte.

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
  console.error(
    'usage: node research/coulomb-force-weight-response/generate-metrics.mjs [--check]',
  );
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
const scientific = (digits) => ({ style: 'scientific', digits });

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
  return createHash('sha256')
    .update(readFileSync(resolve(root, repositoryPath)))
    .digest('hex');
}

const DOSE_SLUG = new Map([
  [0, '0'],
  [0.01, '001'],
  [0.1, '01'],
  [1, '1'],
  [10, '10'],
  [100, '100'],
]);

function cutoffSlug(value) {
  return value.toFixed(2).replace('.', '');
}

function buildMetrics(generatedAt) {
  const metrics = {};

  for (const record of results.records) {
    const lambda = record.lambda_force;
    const slug = DOSE_SLUG.get(lambda);
    if (!slug) {
      throw new Error(`unregistered force weight: ${lambda}`);
    }
    const derived = record.derived;
    const bracket = derived.first_parity_bracket_bohr;
    const nearWall = derived.per_cutoff['0.15'];

    metrics[`crossover_lambda_${slug}_bohr`] = numberMetric(
      derived.first_parity_cutoff_bohr,
      fixed(2),
      `First tested cutoff at which the median energy A/B ratio is at most one for lambda = ${lambda}`,
      'bohr',
    );
    metrics[`crossover_lower_lambda_${slug}_bohr`] = numberMetric(
      bracket.lower_bohr,
      fixed(2),
      `Lower endpoint of the first parity bracket for lambda = ${lambda}`,
      'bohr',
    );
    metrics[`crossover_upper_lambda_${slug}_bohr`] = numberMetric(
      bracket.upper_bohr,
      fixed(2),
      `Upper endpoint of the first parity bracket for lambda = ${lambda}`,
      'bohr',
    );
    metrics[`crossover_interpolated_lambda_${slug}_bohr`] = numberMetric(
      derived.interpolated_first_parity_bohr,
      fixed(3),
      `Descriptive log-ratio interpolation inside the first parity bracket for lambda = ${lambda}; not used for the verdict`,
      'bohr',
    );
    metrics[`crossing_count_lambda_${slug}`] = integerMetric(
      derived.crossings.length,
      `Number of forward and reverse median-energy parity crossings for lambda = ${lambda}`,
    );
    metrics[`reverse_crossing_lambda_${slug}`] = booleanMetric(
      derived.has_reverse_crossing,
      `Whether the median energy A/B curve crosses from at most one back above one for lambda = ${lambda}`,
    );
    derived.crossings.forEach((crossing, index) => {
      const number = index + 1;
      metrics[`crossing_${number}_lower_lambda_${slug}_bohr`] = numberMetric(
        crossing.lower_bohr,
        fixed(2),
        `Lower endpoint of parity crossing ${number} for lambda = ${lambda}`,
        'bohr',
      );
      metrics[`crossing_${number}_upper_lambda_${slug}_bohr`] = numberMetric(
        crossing.upper_bohr,
        fixed(2),
        `Upper endpoint of parity crossing ${number} for lambda = ${lambda}`,
        'bohr',
      );
    });
    metrics[`nearwall_energy_ratio_lambda_${slug}`] = numberMetric(
      nearWall.median_energy_ab_ratio,
      scientific(2),
      `Median paired energy-RMSE A/B ratio at R_min = 0.15 bohr for lambda = ${lambda}`,
      'ratio',
    );
    metrics[`nearwall_force_ratio_lambda_${slug}`] = numberMetric(
      nearWall.median_force_ab_ratio,
      scientific(2),
      `Median paired held-out total-force-RMSE A/B ratio at R_min = 0.15 bohr for lambda = ${lambda}`,
      'ratio',
    );
    metrics[`nearwall_energy_rmse_a_lambda_${slug}_cm`] = numberMetric(
      nearWall.median_energy_rmse_a_cm,
      scientific(2),
      `Median direct-fit energy RMSE at R_min = 0.15 bohr for lambda = ${lambda}`,
      'cm^-1',
    );
    metrics[`nearwall_energy_rmse_b_lambda_${slug}_cm`] = numberMetric(
      nearWall.median_energy_rmse_b_cm,
      scientific(2),
      `Median Coulomb-subtracted energy RMSE at R_min = 0.15 bohr for lambda = ${lambda}`,
      'cm^-1',
    );
    metrics[`nearwall_force_rmse_a_lambda_${slug}_hartree_per_bohr`] = numberMetric(
      nearWall.median_force_rmse_a_hartree_per_bohr,
      scientific(3),
      `Median direct-fit total-force RMSE at R_min = 0.15 bohr for lambda = ${lambda}`,
      'hartree/bohr',
    );
    metrics[`nearwall_force_rmse_b_lambda_${slug}_hartree_per_bohr`] = numberMetric(
      nearWall.median_force_rmse_b_hartree_per_bohr,
      scientific(3),
      `Median Coulomb-subtracted total-force RMSE at R_min = 0.15 bohr for lambda = ${lambda}`,
      'hartree/bohr',
    );
  }

  for (const endpoint of results.controls.optimization_sensitivity.endpoints) {
    const doseSlug = DOSE_SLUG.get(endpoint.lambda_force);
    const cutoff = cutoffSlug(endpoint.cutoff_bohr);
    const prefix = `audit_lambda_${doseSlug}_cutoff_${cutoff}`;
    metrics[`${prefix}_primary_ratio`] = numberMetric(
      endpoint.primary_median_energy_ab_ratio,
      fixed(4),
      `Median energy A/B ratio after 20,000 steps at lambda = ${endpoint.lambda_force}, R_min = ${endpoint.cutoff_bohr} bohr`,
      'ratio',
    );
    metrics[`${prefix}_extended_ratio`] = numberMetric(
      endpoint.audit_median_energy_ab_ratio,
      fixed(4),
      `Median energy A/B ratio after 40,000 steps at lambda = ${endpoint.lambda_force}, R_min = ${endpoint.cutoff_bohr} bohr`,
      'ratio',
    );
    metrics[`${prefix}_same_side`] = booleanMetric(
      endpoint.same_side_of_parity,
      `Whether the 20,000- and 40,000-step ratios remain on the same side of parity at lambda = ${endpoint.lambda_force}, R_min = ${endpoint.cutoff_bohr} bohr`,
    );
  }

  metrics.crossover_sequence_nonincreasing = booleanMetric(
    results.hypothesis.crossover_sequence_nonincreasing,
    'Whether the registered first-parity cutoff sequence is nonincreasing with force weight',
  );
  metrics.high_weight_strictly_inward = booleanMetric(
    results.hypothesis.high_weight_strictly_inward_of_lambda_1,
    'Whether lambda = 10 or 100 has a first-parity cutoff strictly inward of lambda = 1',
  );
  metrics.no_positive_weight_reverse_crossing = booleanMetric(
    results.hypothesis.no_positive_weight_reverse_crossing,
    'Whether every positive-weight curve avoids a reverse parity crossing',
  );
  metrics.optimization_audit_passed = booleanMetric(
    results.controls.optimization_sensitivity.passed,
    'Whether every registered 40,000-step audit endpoint remains on the same side of parity as its 20,000-step result',
  );
  metrics.audit_flip_count = integerMetric(
    results.controls.optimization_sensitivity.endpoints.filter(
      (endpoint) => !endpoint.same_side_of_parity,
    ).length,
    'Number of registered endpoints whose parity classification changed at 40,000 steps',
  );
  metrics.audit_endpoint_count = integerMetric(
    results.controls.optimization_sensitivity.endpoints.length,
    'Number of endpoints in the registered 40,000-step optimization audit',
  );
  metrics.verdict_inconclusive = booleanMetric(
    results.verdict === 'inconclusive',
    'Whether the frozen scientific verdict is inconclusive',
  );
  metrics.legacy_overlap_passed = booleanMetric(
    results.controls.legacy_overlap.passed,
    'Whether all lambda = 0 and lambda = 1 predecessor results were reproduced exactly',
  );
  metrics.legacy_overlap_comparison_count = integerMetric(
    results.controls.legacy_overlap.comparison_count,
    'Number of exact predecessor-result comparisons',
  );
  metrics.legacy_maximum_absolute_difference_cm = numberMetric(
    results.controls.legacy_overlap.maximum_absolute_difference_cm,
    fixed(1),
    'Largest absolute difference from a predecessor energy RMSE',
    'cm^-1',
  );
  metrics.completeness_passed = booleanMetric(
    results.controls.completeness.passed,
    'Whether every registered energy and force result is finite and complete',
  );
  metrics.runtime_within_ceiling = booleanMetric(
    results.runtime.within_ceiling,
    'Whether the full production and audit run stayed within the registered three-hour ceiling',
  );
  metrics.total_runtime_minutes = numberMetric(
    results.runtime.total_wall_seconds / 60,
    fixed(1),
    'Total wall time for the primary sweep and optimization audit',
    'minutes',
  );

  const inputPaths = [
    'research/coulomb-force-weight-response/PREREGISTRATION.md',
    'research/coulomb-force-weight-response/run_experiment.py',
    'research/coulomb-force-weight-response/verify_analysis.py',
    'research/coulomb-force-weight-response/results.json',
    'research/coulomb-force-training/h2plus_model.py',
    'research/coulomb-force-training/run_experiment.py',
    'research/coulomb-force-training/results.json',
  ];

  return {
    schema_version: 1,
    experiment: 'coulomb-force-weight-response',
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
