#!/usr/bin/env node

// Publication projection for the ensemble-broadening demonstration. Derives
// every metric from results/summary.json; do not hand-author metrics.json.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const input = 'research/from-blinking-to-absorption/results/summary.json';
const checkOnly = process.argv.includes('--check');

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

function build(generatedAt) {
  const result = JSON.parse(readFileSync(resolve(root, input), 'utf8'));
  return {
    schema_version: 1,
    experiment: 'from-blinking-to-absorption',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [{ path: input, sha256: sha256(input) }],
    },
    metrics: {
      single_molecule_fwhm: {
        type: 'number',
        value: result.fwhm_cm1.single_molecule,
        format: { style: 'fixed', digits: 1 },
        description: 'FWHM of the single-molecule Lorentzian line measured on the plotted grid',
        unit: 'cm^-1',
      },
      ensemble_fwhm: {
        type: 'number',
        value: result.fwhm_cm1.ensemble_10000,
        format: { style: 'fixed', digits: 1 },
        description: 'FWHM of the averaged spectrum of the 10,000-molecule ensemble',
        unit: 'cm^-1',
      },
      gaussian_limit_fwhm: {
        type: 'number',
        value: result.fwhm_cm1.gaussian_limit,
        format: { style: 'fixed', digits: 1 },
        description: 'Analytic FWHM of the inhomogeneous Gaussian distribution, 2*sqrt(2 ln 2)*sigma',
        unit: 'cm^-1',
      },
      fwhm_gaussian_deviation: {
        type: 'number',
        value: result.fwhm_gaussian_deviation,
        format: { style: 'percent', digits: 1 },
        description: 'Relative deviation of the ensemble FWHM from the analytic Gaussian limit',
        unit: 'ratio',
      },
    },
  };
}

const existing = existsSync(outputPath)
  ? JSON.parse(readFileSync(outputPath, 'utf8'))
  : null;
const generatedAt = checkOnly && existing?.provenance?.generated_at
  ? existing.provenance.generated_at
  : new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const expected = `${JSON.stringify(build(generatedAt), null, 2)}\n`;

if (checkOnly) {
  if (!existing || readFileSync(outputPath, 'utf8') !== expected) {
    console.error(`${relative(root, outputPath)} is missing or stale`);
    process.exit(1);
  }
} else {
  writeFileSync(outputPath, expected);
}
