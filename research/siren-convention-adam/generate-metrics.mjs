#!/usr/bin/env node

// Produce the publication projection for the SIREN/Adam experiment from its
// two frozen result tables.  This is intentionally cheap: CI can run --check
// without re-running 20,000-epoch training jobs.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const checkOnly = process.argv.includes('--check');

if (process.argv.length > 3 || (process.argv.length === 3 && !checkOnly)) {
  console.error('usage: node research/siren-convention-adam/generate-metrics.mjs [--check]');
  process.exit(2);
}

const sourcePaths = [
  'downloads/siren-convention-adam.py',
  'downloads/conv_equiv.json',
  'downloads/conv_range.json',
];

const readJson = (path) => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

const fixed = (digits) => ({ style: 'fixed', digits });
const scientific = (digits) => ({ style: 'scientific', digits });

function numberMetric(value, format, description, unit = undefined) {
  return {
    type: 'number',
    value,
    format,
    description,
    ...(unit === undefined ? {} : { unit }),
  };
}

function integerMetric(value, description, unit = undefined) {
  return {
    type: 'integer',
    value,
    description,
    ...(unit === undefined ? {} : { unit }),
  };
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
}

function lrName(lr) {
  const known = new Map([
    [1e-5, '1e_5'],
    [1e-4, '1e_4'],
    [1e-3, '1e_3'],
  ]);
  const name = known.get(lr);
  if (!name) throw new Error(`unexpected equivalence learning rate ${lr}`);
  return name;
}

function buildMetrics(generatedAt) {
  const equivalence = readJson('downloads/conv_equiv.json');
  const range = readJson('downloads/conv_range.json');
  const metrics = {};

  const expectedEquivalenceLearningRates = [1e-5, 1e-4, 1e-3];
  for (const lr of expectedEquivalenceLearningRates) {
    const matches = equivalence.filter((row) => row.lr === lr);
    if (matches.length !== 1) {
      throw new Error(`expected exactly one equivalence result at learning rate ${lr}; found ${matches.length}`);
    }
  }
  if (equivalence.length !== expectedEquivalenceLearningRates.length) {
    throw new Error(`found ${equivalence.length} equivalence rows; expected ${expectedEquivalenceLearningRates.length}`);
  }

  for (const row of equivalence) {
    const lr = lrName(row.lr);
    const prefix = `equiv_lr_${lr}`;
    metrics[`${prefix}_official_mse`] = numberMetric(
      row.official,
      fixed(4),
      `Official-convention normalized test MSE at learning rate ${row.lr}`,
      'normalized test MSE',
    );
    metrics[`${prefix}_described_mse`] = numberMetric(
      row.described,
      fixed(4),
      `Described-convention normalized test MSE at learning rate ${row.lr}`,
      'normalized test MSE',
    );
    metrics[`${prefix}_scaled_mse`] = numberMetric(
      row.described_scaled,
      fixed(4),
      `Hidden-rate-scaled described-convention normalized test MSE at learning rate ${row.lr}`,
      'normalized test MSE',
    );
    metrics[`${prefix}_relative_difference`] = numberMetric(
      Math.abs(row.described_scaled - row.official) / Math.abs(row.official),
      scientific(1),
      `Relative difference between official and hidden-rate-scaled described runs at learning rate ${row.lr}`,
      'ratio',
    );
  }

  const byConvention = new Map();
  for (const convention of ['described', 'official']) {
    const summaries = [];
    for (const rep of [0, 1, 2, 3]) {
      const rows = range.filter((row) => row.conv === convention && row.rep === rep);
      if (rows.length !== 9) {
        throw new Error(`${convention} repetition ${rep} has ${rows.length} rows; expected 9`);
      }
      const inRange = rows.filter((row) => row.lr <= 1e-3);
      const aboveRange = rows.filter((row) => row.lr > 1e-3);
      const fits = rows.filter((row) => row.test < 1e-3);
      if (!fits.length) throw new Error(`${convention} repetition ${rep} never reaches the fit threshold`);

      const summary = {
        bestInRange: Math.min(...inRange.map((row) => row.test)),
        bestAboveRange: Math.min(...aboveRange.map((row) => row.test)),
        firstFitLr: Math.min(...fits.map((row) => row.lr)),
      };
      summaries.push(summary);

      const prefix = `range_${convention}_rep${rep}`;
      metrics[`${prefix}_best_in_range`] = numberMetric(
        summary.bestInRange,
        scientific(1),
        `${convention} repetition ${rep} best normalized test MSE at learning rates no greater than 1e-3`,
        'normalized test MSE',
      );
      metrics[`${prefix}_best_above_range`] = numberMetric(
        summary.bestAboveRange,
        scientific(1),
        `${convention} repetition ${rep} best normalized test MSE at learning rates above 1e-3`,
        'normalized test MSE',
      );
      metrics[`${prefix}_first_fit_lr`] = numberMetric(
        summary.firstFitLr,
        scientific(2),
        `${convention} repetition ${rep} lowest learning rate with normalized test MSE below 1e-3`,
        'learning rate',
      );
    }
    byConvention.set(convention, summaries);
    metrics[`range_${convention}_median_best_in_range`] = numberMetric(
      median(summaries.map((item) => item.bestInRange)),
      scientific(1),
      `${convention} median best normalized test MSE at learning rates no greater than 1e-3`,
      'normalized test MSE',
    );
    metrics[`range_${convention}_median_best_above_range`] = numberMetric(
      median(summaries.map((item) => item.bestAboveRange)),
      scientific(1),
      `${convention} median best normalized test MSE at learning rates above 1e-3`,
      'normalized test MSE',
    );
  }

  const officialFirstFits = byConvention.get('official').map((item) => item.firstFitLr);
  const describedFirstFits = byConvention.get('described').map((item) => item.firstFitLr);
  metrics.range_official_common_first_fit_count = integerMetric(
    officialFirstFits.filter((lr) => lr === officialFirstFits[0]).length,
    'Repetitions sharing the official convention first-fit learning rate',
    'repetitions',
  );
  const firstFitRatios = describedFirstFits.map((lr, index) => lr / officialFirstFits[index]);
  const tenfoldRatios = firstFitRatios.filter((ratio) => ratio === 10);
  if (tenfoldRatios.length !== 3) {
    throw new Error(`expected three tenfold first-fit ratios, found ${tenfoldRatios.length}`);
  }
  const commonRatio = tenfoldRatios[0];
  const outlierRatio = firstFitRatios.find((ratio) => ratio !== commonRatio);
  if (outlierRatio === undefined) throw new Error('expected one non-modal first-fit ratio');

  metrics.range_described_tenfold_gap_count = integerMetric(
    tenfoldRatios.length,
    'Repetitions where the described first-fit learning rate is ten times the official rate',
    'repetitions',
  );
  metrics.range_common_first_fit_ratio = integerMetric(
    commonRatio,
    'Common described-to-official first-fit learning-rate ratio',
    'ratio',
  );
  metrics.range_outlier_first_fit_ratio = numberMetric(
    outlierRatio,
    fixed(2),
    'Described-to-official first-fit learning-rate ratio in the non-tenfold repetition',
    'ratio',
  );
  metrics.range_median_first_fit_ratio = integerMetric(
    median(firstFitRatios),
    'Median described-to-official first-fit learning-rate ratio',
    'ratio',
  );
  const unscaledAtOneEminusFive = equivalence.find((row) => row.lr === 1e-5);
  if (!unscaledAtOneEminusFive) {
    throw new Error('missing equivalence result at learning rate 1e-5');
  }
  metrics.equiv_lr_1e_5_unscaled_absolute_difference = numberMetric(
    Math.abs(unscaledAtOneEminusFive.described - unscaledAtOneEminusFive.official),
    fixed(3),
    'Absolute normalized-MSE difference between unscaled conventions at learning rate 1e-5',
    'normalized test MSE',
  );

  return {
    schema_version: 1,
    experiment: 'siren-convention-adam',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: sourcePaths.map((path) => ({ path, sha256: sha256(path) })),
    },
    metrics,
  };
}

const existing = existsSync(outputPath)
  ? JSON.parse(readFileSync(outputPath, 'utf8'))
  : null;
const generatedAt = checkOnly && existing?.provenance?.generated_at
  ? existing.provenance.generated_at
  : new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const expectedText = `${JSON.stringify(buildMetrics(generatedAt), null, 2)}\n`;

if (checkOnly) {
  if (!existing) {
    console.error(`${relative(root, outputPath)} is missing; run the generator without --check`);
    process.exit(1);
  }
  const actualText = readFileSync(outputPath, 'utf8');
  if (actualText !== expectedText) {
    console.error(`${relative(root, outputPath)} is stale; regenerate it`);
    process.exit(1);
  }
  console.log(`metrics check: ${Object.keys(existing.metrics).length} SIREN/Adam metrics are current`);
} else {
  writeFileSync(outputPath, expectedText);
  console.log(`wrote ${relative(root, outputPath)}`);
}
