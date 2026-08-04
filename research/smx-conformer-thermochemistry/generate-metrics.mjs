#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const checkOnly = process.argv.includes('--check');
const inputPaths = [
  'research/smx-conformer-thermochemistry/PREREGISTRATION.md',
  'research/smx-conformer-thermochemistry/inputs.json',
  'research/smx-conformer-thermochemistry/run_experiment.py',
  'research/smx-conformer-thermochemistry/verify_analysis.py',
  'research/smx-conformer-thermochemistry/results.json',
];

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

const fixed = (value, digits, description, unit) => ({
  type: 'number',
  value,
  format: { style: 'fixed', digits },
  description,
  ...(unit ? { unit } : {}),
});

const percent = (value, digits, description) => ({
  type: 'number',
  value,
  format: { style: 'percent', digits },
  description,
  unit: 'ratio',
});

const boolean = (value, description) => ({
  type: 'boolean',
  value,
  description,
});

function build(generatedAt) {
  const result = JSON.parse(
    readFileSync(resolve(root, 'research/smx-conformer-thermochemistry/results.json'), 'utf8'),
  );
  const source = result.source_preflight;
  const rrho = result.analysis.rrho;
  const mrrho = result.analysis.mrrho50;
  const signMismatchCount = source.relaxation_energy_sign_audit
    .filter((row) => row.printed_sign_opposes_stated_formula).length;
  const metrics = {};

  for (const conformer of ['A', 'B', 'C', 'D']) {
    const key = conformer.toLowerCase();
    metrics[`source_population_${key}`] = percent(
      source.electronic_populations[conformer],
      1,
      `Source electronic-energy Boltzmann population of conformer ${conformer} at 298.15 K`,
    );
    metrics[`rrho_population_${key}`] = percent(
      rrho.composite_populations[conformer],
      1,
      `Composite source-DFT plus pure-RRHO population of conformer ${conformer} at 298.15 K`,
    );
    metrics[`mrrho50_population_${key}`] = percent(
      mrrho.composite_populations[conformer],
      1,
      `Composite source-DFT plus 50 cm^-1 modified-RRHO population of conformer ${conformer} at 298.15 K`,
    );
  }

  metrics.rrho_max_population_shift_pp = fixed(
    rrho.maximum_absolute_population_shift_pp,
    1,
    'Maximum absolute conformer-population change from the source baseline in the pure-RRHO arm',
    'percentage points',
  );
  metrics.mrrho50_max_population_shift_pp = fixed(
    mrrho.maximum_absolute_population_shift_pp,
    1,
    'Maximum absolute conformer-population change from the source baseline in the 50 cm^-1 modified-RRHO arm',
    'percentage points',
  );
  metrics.rrho_effective_conformer_count = fixed(
    rrho.effective_conformer_count,
    2,
    'Effective conformer count in the pure-RRHO composite population',
    'conformers',
  );
  metrics.mrrho50_effective_conformer_count = fixed(
    mrrho.effective_conformer_count,
    2,
    'Effective conformer count in the 50 cm^-1 modified-RRHO composite population',
    'conformers',
  );
  metrics.rrho_arm_passed = boolean(
    rrho.arm_passed,
    'Whether the pure-RRHO arm passed both preregistered robustness gates',
  );
  metrics.mrrho50_arm_passed = boolean(
    mrrho.arm_passed,
    'Whether the 50 cm^-1 modified-RRHO arm passed both preregistered robustness gates',
  );
  metrics.method_fidelity_passed = boolean(
    result.fidelity.passed,
    'Whether every preregistered run, minimum, arm-consistency, and distinct-conformer fidelity check passed',
  );
  metrics.hypothesis_supported = boolean(
    result.verdict.hypothesis_supported,
    'Whether the preregistered near-uniform-population hypothesis was supported',
  );
  metrics.hypothesis_falsified = boolean(
    result.verdict.hypothesis_falsified,
    'Whether the preregistered near-uniform-population hypothesis was falsified',
  );
  metrics.result_inconclusive = boolean(
    result.verdict.result_inconclusive,
    'Whether the preregistered result was inconclusive',
  );
  metrics.source_relaxation_sign_mismatch_count = {
    type: 'integer',
    value: signMismatchCount,
    description: 'Rows whose printed relaxation-energy sign opposes the source table footnote formula',
    unit: 'rows',
  };

  return {
    schema_version: 1,
    experiment: 'smx-conformer-thermochemistry',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: inputPaths.map((path) => ({ path, sha256: sha256(path) })),
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
const expected = `${JSON.stringify(build(generatedAt), null, 2)}\n`;

if (checkOnly) {
  if (!existing || readFileSync(outputPath, 'utf8') !== expected) {
    console.error(`${relative(root, outputPath)} is missing or stale`);
    process.exit(1);
  }
} else {
  writeFileSync(outputPath, expected);
}
