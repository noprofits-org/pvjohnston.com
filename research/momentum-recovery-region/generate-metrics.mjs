#!/usr/bin/env node

// Project the canonical beta sweep (results/stage1.json, results/stage2.json)
// into the typed values used by the accompanying post. Implements the frozen
// recovery, width, and verdict rules from PREREGISTRATION.md. Check mode
// requires the committed projection to match byte for byte.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const stage1Path = resolve(experimentDir, 'results/stage1.json');
const stage2Path = resolve(experimentDir, 'results/stage2.json');
const metricsPath = resolve(experimentDir, 'metrics.json');
const arguments_ = process.argv.slice(2);
const checkOnly = arguments_.length === 1 && arguments_[0] === '--check';

if (!(arguments_.length === 0 || checkOnly)) {
  console.error(
    'usage: node research/momentum-recovery-region/generate-metrics.mjs [--check]',
  );
  process.exit(2);
}

for (const path of [stage1Path, stage2Path]) {
  if (!existsSync(path)) {
    console.error(`${relative(root, path)} is missing; run src/run_sweep.py first`);
    process.exit(1);
  }
}

const stage1 = JSON.parse(readFileSync(stage1Path, 'utf8'));
const stage2 = JSON.parse(readFileSync(stage2Path, 'utf8'));
const THRESHOLD = stage1.floor_threshold;
const BETAS = stage1.betas;
const REPS = stage1.reps;

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

const BETA_SLUG = new Map([[0, '0'], [0.3, '03'], [0.6, '06'], [0.9, '09'], [0.99, '099']]);

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

// Median normalized test MSE over reps at one grid point; null when any rep
// diverged (a divergent rep makes the point not recovered, never excluded).
function medianTest(rows, conv, lr) {
  const vals = rows.filter((r) => r.conv === conv && r.lr === lr).map((r) => r.test);
  if (vals.length !== REPS.length || vals.some((v) => v === null)) return null;
  return median(vals);
}

function recoveredLrs(rows, beta, threshold) {
  const lrs = [...new Set(rows.filter((r) => r.beta === beta).map((r) => r.lr))].sort((a, b) => a - b);
  return lrs.filter((lr) => {
    const m = medianTest(rows.filter((r) => r.beta === beta), 'described', lr);
    return m !== null && m <= threshold;
  });
}

function firstDivergence(rows, beta, conv) {
  const lrs = [...new Set(rows.filter((r) => r.beta === beta).map((r) => r.lr))].sort((a, b) => a - b);
  return lrs.find((lr) => rows.some((r) => r.beta === beta && r.conv === conv && r.lr === lr && r.test === null)) ?? null;
}

function buildMetrics(generatedAt) {
  const metrics = {};
  const counts = new Map();
  const refinedWidths = new Map();
  const boundaries = new Map();

  for (const beta of BETAS) {
    const slug = BETA_SLUG.get(beta);
    if (!slug) throw new Error(`unregistered beta: ${beta}`);
    const rows1 = stage1.rows.filter((r) => r.beta === beta);

    const recovered = recoveredLrs(stage1.rows, beta, THRESHOLD);
    counts.set(beta, recovered.length);
    metrics[`recovered_points_beta_${slug}`] = integerMetric(
      recovered.length,
      `Stage-1 grid points where the described convention's median normalized test MSE over 3 reps is at most 1e-24, beta = ${beta}`,
      'points',
    );
    if (recovered.length) {
      metrics[`recovered_top_lr_beta_${slug}`] = numberMetric(
        Math.max(...recovered),
        scientific(4),
        `Highest recovered stage-1 learning rate (upper edge of the recovery region), beta = ${beta}`,
        'learning rate',
      );
    }

    for (const [sens, tag] of [[1e-20, '1e20'], [1e-28, '1e28']]) {
      metrics[`recovered_points_beta_${slug}_at_${tag}`] = integerMetric(
        recoveredLrs(stage1.rows, beta, sens).length,
        `Sensitivity: stage-1 recovered count at threshold ${sens.toExponential(0)}, beta = ${beta}`,
        'points',
      );
    }

    const bestByLr = [...new Set(rows1.map((r) => r.lr))]
      .map((lr) => ({ lr, m: medianTest(rows1, 'described', lr) }))
      .filter((x) => x.m !== null);
    const best = Math.min(...bestByLr.map((x) => x.m));
    const bestLr = bestByLr.find((x) => x.m === best).lr;
    metrics[`described_best_beta_${slug}`] = numberMetric(
      best,
      scientific(2),
      `Best median normalized test MSE of the described convention on the stage-1 grid, beta = ${beta}`,
      'normalized MSE',
    );
    metrics[`described_best_lr_beta_${slug}`] = numberMetric(
      bestLr,
      scientific(4),
      `Stage-1 learning rate at which the described convention's best median normalized test MSE occurs, beta = ${beta}`,
      'learning rate',
    );

    const officialFinite = rows1.filter((r) => r.conv === 'official' && r.test !== null).map((r) => r.test);
    metrics[`official_median_beta_${slug}`] = numberMetric(
      median(officialFinite),
      scientific(2),
      `Median normalized test MSE over finite official-convention stage-1 points, beta = ${beta}`,
      'normalized MSE',
    );
    metrics[`official_best_beta_${slug}`] = numberMetric(
      Math.min(...officialFinite),
      scientific(2),
      `Best normalized test MSE over official-convention stage-1 points, beta = ${beta}`,
      'normalized MSE',
    );

    const boundary = firstDivergence(stage1.rows, beta, 'described');
    boundaries.set(beta, boundary);
    if (boundary !== null) {
      metrics[`boundary_beta_${slug}`] = numberMetric(
        boundary,
        scientific(4),
        `Lowest stage-1 learning rate at which any described-convention rep diverged, beta = ${beta}`,
        'learning rate',
      );
    }
    const officialBoundary = firstDivergence(stage1.rows, beta, 'official');
    if (officialBoundary !== null) {
      metrics[`boundary_official_beta_${slug}`] = numberMetric(
        officialBoundary,
        scientific(4),
        `Lowest stage-1 learning rate at which any official-convention rep diverged, beta = ${beta}`,
        'learning rate',
      );
    }

    const window = stage2.windows[String(beta)];
    if (window) {
      const rows2 = stage2.rows.filter((r) => r.beta === beta);
      const refined = recoveredLrs(stage2.rows, beta, THRESHOLD);
      refinedWidths.set(beta, refined.length * stage2.step_decades);
      metrics[`refined_recovered_points_beta_${slug}`] = integerMetric(
        refined.length,
        `Stage-2 (0.01-decade) grid points where the described convention's median normalized test MSE over 3 reps is at most 1e-24, beta = ${beta}`,
        'points',
      );
      metrics[`refined_width_beta_${slug}_decades`] = numberMetric(
        refined.length * stage2.step_decades,
        fixed(2),
        `Refined recovery-region width for beta = ${beta} (recovered count x 0.01 decades)`,
        'decades',
      );
      const windowBottom = 10 ** window[0];
      metrics[`refined_width_censored_beta_${slug}`] = booleanMetric(
        refined.some((lr) => Math.abs(lr - windowBottom) / windowBottom < 1e-9),
        `Whether the refined recovery region reaches the bottom of its stage-2 window for beta = ${beta}, so the measured width is a lower bound`,
      );
      const best2 = Math.min(
        ...[...new Set(rows2.map((r) => r.lr))]
          .map((lr) => ({ lr, m: medianTest(rows2, 'described', lr) }))
          .filter((x) => x.m !== null)
          .map((x) => x.m),
      );
      metrics[`refined_described_best_beta_${slug}`] = numberMetric(
        best2,
        scientific(2),
        `Best median normalized test MSE of the described convention on the stage-2 grid, beta = ${beta}`,
        'normalized MSE',
      );
      const refinedBoundary = firstDivergence(stage2.rows, beta, 'described');
      if (refinedBoundary !== undefined && refinedBoundary !== null) {
        metrics[`refined_boundary_beta_${slug}`] = numberMetric(
          refinedBoundary,
          scientific(4),
          `Lowest stage-2 (0.01-decade) learning rate at which any described-convention rep diverged, beta = ${beta}`,
          'learning rate',
        );
      }
    }

    // Largest finite excursion anywhere on either grid, per convention: the
    // size of the instability band below the divergence boundary.
    const allRows = [...stage1.rows, ...stage2.rows].filter((r) => r.beta === beta);
    for (const [conv, tag] of [['described', 'described'], ['official', 'official']]) {
      const finite = allRows.filter((r) => r.conv === conv && r.test !== null).map((r) => r.test);
      if (!finite.length) continue;
      metrics[`${tag}_worst_finite_beta_${slug}`] = numberMetric(
        Math.max(...finite),
        scientific(2),
        `Largest finite normalized test MSE of the ${conv} convention on any tested rate, beta = ${beta}`,
        'normalized MSE',
      );
    }
  }

  const boundary0 = boundaries.get(0);
  if (boundary0 !== null) {
    for (const beta of BETAS) {
      const boundary = boundaries.get(beta);
      if (boundary === null) continue;
      const slug = BETA_SLUG.get(beta);
      metrics[`boundary_ratio_beta_${slug}`] = numberMetric(
        boundary / boundary0,
        fixed(3),
        `Described-convention divergence boundary at beta = ${beta} relative to beta = 0; the heavy-ball prediction is 1 + beta = ${1 + beta}`,
        'ratio',
      );
    }
  }

  // Verdict, per the frozen decision rule in PREREGISTRATION.md.
  const countSeq = BETAS.map((b) => counts.get(b));
  const nondecreasing = countSeq.every((c, i) => i === 0 || c >= countSeq[i - 1]);
  const recoversAboveHalf = [0.6, 0.9, 0.99].every((b) => counts.get(b) >= 1);
  const allEqual = countSeq.every((c) => c === countSeq[0]);
  let verdict;
  if (allEqual && countSeq[0] === 0) {
    verdict = 'falsified';
  } else if (allEqual) {
    const widthSeq = BETAS.map((b) => refinedWidths.get(b) ?? 0);
    const widthsNondecreasing = widthSeq.every((w, i) => i === 0 || w >= widthSeq[i - 1]);
    const widthsAllEqual = widthSeq.every((w) => w === widthSeq[0]);
    if (widthsAllEqual) verdict = 'inconclusive';
    else verdict = widthsNondecreasing ? 'supported' : 'falsified';
  } else {
    verdict = nondecreasing && recoversAboveHalf ? 'supported' : 'falsified';
  }

  metrics.width_monotone_nondecreasing = booleanMetric(
    nondecreasing,
    'Whether stage-1 recovered counts are nondecreasing in beta',
  );
  metrics.recovers_each_beta_above_half = booleanMetric(
    recoversAboveHalf,
    'Whether the described convention recovers at at least one tested rate for every beta in {0.6, 0.9, 0.99}',
  );
  metrics.verdict_supported = booleanMetric(
    verdict === 'supported',
    'Whether the frozen decision rule returns supported',
  );
  metrics.verdict_falsified = booleanMetric(
    verdict === 'falsified',
    'Whether the frozen decision rule returns falsified',
  );
  metrics.verdict_inconclusive = booleanMetric(
    verdict === 'inconclusive',
    'Whether the frozen decision rule returns inconclusive',
  );
  metrics.stage1_training_count = integerMetric(
    stage1.rows.length,
    'Total stage-1 trainings (5 betas x 2 conventions x 35 rates x 3 reps)',
    'trainings',
  );
  metrics.stage2_training_count = integerMetric(
    stage2.rows.length,
    'Total stage-2 refinement trainings',
    'trainings',
  );

  const inputPaths = [
    'research/momentum-recovery-region/PREREGISTRATION.md',
    'research/momentum-recovery-region/src/run_sweep.py',
    'research/momentum-recovery-region/results/stage1.json',
    'research/momentum-recovery-region/results/stage2.json',
  ];

  return {
    schema_version: 1,
    experiment: 'momentum-recovery-region',
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
