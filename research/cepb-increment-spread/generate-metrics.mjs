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
  'research/cepb-increment-spread/PREREGISTRATION.md',
  'research/cepb-increment-spread/inputs.json',
  'research/cepb-increment-spread/run_armb.py',
  'research/cepb-increment-spread/analyze.py',
  'research/cepb-increment-spread/results.json',
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

const boolean = (value, description) => ({
  type: 'boolean',
  value,
  description,
});

// Arm A levels and Arm B bases, with the short suffixes the post uses.
const LEVELS = [
  ['cbs', 'cbs', 'CBS'],
  ['aug-cc-pvqz', 'qz', 'aug-cc-pVQZ'],
  ['aug-cc-pvtz', 'tz', 'aug-cc-pVTZ'],
];
const BASES = [
  ['cc-pVDZ', 'dz'],
  ['cc-pVTZ', 'tz'],
];
const CONTRASTS = [
  ['ethene -> ethane', 'ethene_ethane', 'ethene to ethane'],
  ['1,4-cyclohexadiene -> cyclohexene', 'cyclohexadiene_cyclohexene',
    '1,4-cyclohexadiene to cyclohexene'],
  ['cyclohexene -> cyclohexane', 'cyclohexene_cyclohexane',
    'cyclohexene to cyclohexane'],
];
const PAIRS = [
  ['1-butene vs cis-2-butene', 'cis2butene_minus_1butene',
    'cis-2-butene minus 1-butene'],
  ['1-butene vs trans-2-butene', 'trans2butene_minus_1butene',
    'trans-2-butene minus 1-butene'],
  ['1-butene vs isobutene', 'isobutene_minus_1butene',
    'isobutene minus 1-butene'],
  ['cis-2-butene vs trans-2-butene', 'trans2butene_minus_cis2butene',
    'trans-2-butene minus cis-2-butene'],
  ['cis-2-butene vs isobutene', 'isobutene_minus_cis2butene',
    'isobutene minus cis-2-butene'],
  ['trans-2-butene vs isobutene', 'isobutene_minus_trans2butene',
    'isobutene minus trans-2-butene'],
];

function build(generatedAt) {
  const result = JSON.parse(
    readFileSync(resolve(root, 'research/cepb-increment-spread/results.json'), 'utf8'),
  );
  const metrics = {};

  for (const [level, suffix, label] of LEVELS) {
    const arm = result.arm_a[level];
    for (const [key, slug, prose] of CONTRASTS) {
      metrics[`swap_${slug}_${suffix}`] = fixed(
        arm.contrasts[key].measured_kcal_per_mol,
        2,
        `Measured correlation-energy change of the ${prose} swap from the source's published ${label} energies`,
        'kcal/mol',
      );
    }
    metrics[`cepb_swap_${suffix}`] = fixed(
      arm.cepb_predicted_contrast_kcal_per_mol,
      2,
      `CEPB-predicted correlation-energy change of the C=C to C-C + 2 C-H swap at ${label}`,
      'kcal/mol',
    );
    metrics[`swap_spread_${suffix}`] = fixed(
      arm.primary_contrast_spread_kcal_per_mol,
      2,
      `Spread across the three measured swap values at ${label} (primary Arm A statistic)`,
      'kcal/mol',
    );
    const deviations = CONTRASTS.map(
      ([key]) => arm.contrasts[key].deviation_from_cepb_kcal_mol,
    );
    const byMagnitude = [...deviations].sort((a, b) => Math.abs(a) - Math.abs(b));
    metrics[`swap_dev_nearest_${suffix}`] = fixed(
      byMagnitude[0],
      2,
      `Smallest-magnitude deviation of a measured swap from the CEPB prediction at ${label}`,
      'kcal/mol',
    );
    metrics[`swap_dev_farthest_${suffix}`] = fixed(
      byMagnitude[byMagnitude.length - 1],
      2,
      `Largest-magnitude deviation of a measured swap from the CEPB prediction at ${label}`,
      'kcal/mol',
    );
    metrics[`raw_spread_${suffix}`] = fixed(
      arm.secondary_effective_increment_spread_kcal_per_mol,
      2,
      `Spread of the raw effective C=C increment across the seven-molecule set at ${label} (secondary, descriptive statistic)`,
      'kcal/mol',
    );
    metrics[`arm_a_gate_passed_${suffix}`] = boolean(
      arm.primary_gate_passed,
      `Whether the Arm A contrast spread stayed at or below the registered threshold at ${label}`,
    );
  }

  for (const [basis, suffix] of BASES) {
    const arm = result.arm_b[basis];
    for (const [key, slug, prose] of PAIRS) {
      metrics[`pair_${slug}_${suffix}`] = fixed(
        arm.pairwise_differences[key].difference_kcal_per_mol,
        3,
        `CCSD(T) correlation-energy difference, ${prose}, at ${basis}`,
        'kcal/mol',
      );
    }
    metrics[`armb_max_abs_${suffix}`] = fixed(
      arm.max_absolute_difference_kcal_per_mol,
      3,
      `Largest pairwise C4H8 correlation-energy difference magnitude at ${basis}`,
      'kcal/mol',
    );
    metrics[`armb_max_t1_${suffix}`] = fixed(
      arm.max_t1_diagnostic,
      4,
      `Largest T1 diagnostic across the four C4H8 isomers at ${basis}`,
    );
  }

  const signsConsistent = PAIRS.every(([key]) => {
    const dz = result.arm_b['cc-pVDZ'].pairwise_differences[key].difference_hartree;
    const tz = result.arm_b['cc-pVTZ'].pairwise_differences[key].difference_hartree;
    return (dz > 0) === (tz > 0);
  });
  metrics.armb_signs_consistent = boolean(
    signsConsistent,
    'Whether every pairwise difference kept its sign between cc-pVDZ and cc-pVTZ',
  );
  metrics.armb_t1_gate_passed = boolean(
    Object.values(result.arm_b).every((arm) => arm.t1_gate_passed),
    'Whether the largest T1 diagnostic stayed at or below the registered ceiling at both bases',
  );
  metrics.arm_a_inconclusive = boolean(
    result.verdicts.arm_a.value === 'inconclusive',
    'Whether the registered Arm A verdict is inconclusive',
  );
  metrics.arm_b_inconclusive = boolean(
    result.verdicts.arm_b.value === 'inconclusive',
    'Whether the registered Arm B verdict is inconclusive',
  );

  return {
    schema_version: 1,
    experiment: 'cepb-increment-spread',
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
