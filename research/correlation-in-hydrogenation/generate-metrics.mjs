#!/usr/bin/env node

// Projects metrics.json from the canonical calculate.py output. Do not
// hand-author metrics.json. `--check` preserves generated_at and byte-compares
// so the site build's verify-metrics gate is deterministic.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const checkOnly = process.argv.includes('--check');

const inputs = [
  'research/correlation-in-hydrogenation/inputs.json',
  'research/correlation-in-hydrogenation/calculate.py',
  'research/correlation-in-hydrogenation/results.json',
];
const resultsPath = 'research/correlation-in-hydrogenation/results.json';

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

const kj1 = (value) => ({ type: 'number', value, format: { style: 'fixed', digits: 1 } });
const pct1 = (value) => ({ type: 'number', value, format: { style: 'percent', digits: 1 } });

function build(generatedAt) {
  const results = JSON.parse(readFileSync(resolve(root, resultsPath), 'utf8'));
  const s = results.summary;

  const metrics = {
    temperature_k: {
      type: 'number', value: s.temperature_k, format: { style: 'fixed', digits: 2 },
      description: 'Temperature of the ideal-gas thermochemistry', unit: 'K',
    },
    chemical_accuracy_threshold_kj: {
      type: 'number', value: s.chemical_accuracy_threshold_kj, format: { style: 'fixed', digits: 3 },
      description: 'Chemical-accuracy threshold (1 kcal/mol) used as the transferability bound',
      unit: 'kJ/mol',
    },
    reaction_count: {
      type: 'integer', value: s.reaction_count,
      description: 'Number of hydrogenation reactions in the frozen set', unit: 'reactions',
    },
    mean_abs_correlation_content_kj: {
      ...kj1(s.mean_abs_correlation_content_kj),
      description: 'Mean absolute correlation contribution to the reaction enthalpies', unit: 'kJ/mol',
    },
    max_abs_correlation_content_kj: {
      ...kj1(s.max_abs_correlation_content_kj),
      description: 'Largest absolute correlation contribution across the reaction set', unit: 'kJ/mol',
    },
    pi_bond_correlation_transferability_gap_kj: {
      ...kj1(s.pi_bond_correlation_transferability_gap_kj),
      description: 'Difference in per-C-C-pi-bond correlation contribution between the acetylene and ethylene rungs',
      unit: 'kJ/mol',
    },
    cc_pi_rungs_within_chemical_accuracy: {
      type: 'boolean', value: s.cc_pi_rungs_within_chemical_accuracy,
      description: 'Whether the two single-C-C-pi-bond reaction residuals agree within the chemical-accuracy comparison scale',
    },
    all_species_true_minima: {
      type: 'boolean', value: s.all_species_true_minima,
      description: 'Whether every optimized species had no imaginary vibrational mode',
    },
  };

  for (const r of results.reactions) {
    metrics[`dh_ccsdt_${r.slug}_kj`] = {
      ...kj1(r.dh_ccsdt_kj),
      description: `CCSD(T) reaction enthalpy at 298.15 K for ${r.equation}`, unit: 'kJ/mol',
    };
    metrics[`correlation_content_${r.slug}_kj`] = {
      ...kj1(r.correlation_content_kj),
      description: `Correlation contribution to the enthalpy (CCSD(T) - HF) for ${r.equation}`, unit: 'kJ/mol',
    };
    metrics[`correlation_fraction_${r.slug}`] = {
      ...pct1(r.correlation_fraction),
      description: `Correlation contribution as a fraction of the CCSD(T) enthalpy for ${r.equation}`,
      unit: 'ratio',
    };
  }

  return {
    schema_version: 1,
    experiment: 'correlation-in-hydrogenation',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: inputs.map((path) => ({ path, sha256: sha256(path) })),
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
