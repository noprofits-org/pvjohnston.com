#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const arguments_ = process.argv.slice(2);
const checkOnly = arguments_.length === 1 && arguments_[0] === '--check';

if (!(arguments_.length === 0 || checkOnly)) {
  console.error(
    'usage: node research/periodic-compute-cost/generate-metrics.mjs [--check]',
  );
  process.exit(2);
}

const inputPaths = [
  'research/periodic-compute-cost/design.md',
  'research/periodic-compute-cost/environment.md',
  'research/periodic-compute-cost/requirements.lock.txt',
  'research/periodic-compute-cost/requirements-analysis.txt',
  'research/periodic-compute-cost/probe_one.py',
  'research/periodic-compute-cost/sweep.py',
  'research/periodic-compute-cost/results/runs.jsonl',
  'research/periodic-compute-cost/analyze.py',
  'research/periodic-compute-cost/results/summary.json',
];

const sha256 = (repositoryPath) => createHash('sha256')
  .update(readFileSync(resolve(root, repositoryPath)))
  .digest('hex');

const integer = (value, description, unit) => ({
  type: 'integer',
  value,
  description,
  ...(unit ? { unit } : {}),
});

const fixed = (value, digits, description, unit) => ({
  type: 'number',
  value,
  format: { style: 'fixed', digits },
  description,
  ...(unit ? { unit } : {}),
});

const percent = (percentage, digits, description) => ({
  type: 'number',
  value: percentage / 100,
  format: { style: 'percent', digits },
  description,
  unit: 'ratio',
});

function buildMetrics(generatedAt) {
  const summaryPath = resolve(experimentDir, 'results/summary.json');
  const summary = JSON.parse(readFileSync(summaryPath, 'utf8'));
  if (
    summary.schema_version !== 1
    || summary.experiment !== 'periodic-compute-cost'
    || summary.protocol_id !== 'periodic-compute-cost-phase1-v1'
  ) {
    throw new Error('unexpected summary identity');
  }
  if (summary.source.sha256 !== sha256(summary.source.path)) {
    throw new Error('summary source fingerprint does not match runs.jsonl');
  }
  if (
    summary.counts.atoms !== 14
    || summary.counts.jobs !== 70
    || summary.counts.ok !== 66
    || summary.counts.unconverged !== 4
  ) {
    throw new Error('canonical production outcome counts changed');
  }

  const atoms = new Map(summary.atoms.map((atom) => [atom.symbol, atom]));
  const atom = (symbol) => {
    const record = atoms.get(symbol);
    if (!record) throw new Error(`missing atom summary: ${symbol}`);
    return record;
  };
  const ecp = summary.contrasts.kr_to_rb_ecp_boundary;
  const transition = summary.contrasts.transition_pbe;
  const method = summary.contrasts.light_method_timing;

  const metrics = {
    atom_count: integer(
      summary.counts.atoms,
      'Number of atoms in the fixed representative panel',
      'atoms',
    ),
    job_count: integer(
      summary.counts.jobs,
      'Number of fixed production attempts',
      'attempts',
    ),
    ok_job_count: integer(
      summary.counts.ok,
      'Number of production attempts with an ok outcome',
      'attempts',
    ),
    unconverged_job_count: integer(
      summary.counts.unconverged,
      'Number of production attempts that reached the SCF cycle cap',
      'attempts',
    ),
    max_successful_survey_repeat_range: percent(
      summary.contrasts.successful_survey_repeat_timing.maximum.relative_range_percent,
      1,
      'Largest repeat-to-repeat wall-time range relative to the pair median among successful survey pairs',
    ),
    kr_explicit_electrons: integer(
      atom('Kr').explicit_electrons,
      'Explicit electrons in the all-electron krypton calculation',
      'electrons',
    ),
    rb_explicit_electrons: integer(
      atom('Rb').explicit_electrons,
      'Explicit electrons in the rubidium calculation with the def2 effective core potential',
      'electrons',
    ),
    kr_basis_functions: integer(
      atom('Kr').basis_functions,
      'Spherical def2-SVP basis functions in the krypton calculation',
      'basis functions',
    ),
    rb_basis_functions: integer(
      atom('Rb').basis_functions,
      'Spherical def2-SVP basis functions in the rubidium calculation',
      'basis functions',
    ),
    rb_uhf_time_decrease: percent(
      ecp.wall_time_decrease_percent.UHF,
      1,
      'Kr-to-Rb decrease in median UHF calculation wall time',
    ),
    rb_pbe_time_decrease: percent(
      ecp.wall_time_decrease_percent.PBE,
      1,
      'Kr-to-Rb decrease in median PBE calculation wall time',
    ),
    rb_mp2_time_decrease: percent(
      ecp.wall_time_decrease_percent.MP2,
      1,
      'Kr-to-Rb decrease in MP2 calculation wall time',
    ),
    transition_basis_functions: integer(
      atom('Cr').basis_functions,
      'Spherical def2-SVP basis functions shared by Cr, Mn, Fe, and Zn',
      'basis functions',
    ),
    cr_pbe_cycles: integer(transition.Cr.scf_cycles, 'PBE SCF cycles for chromium', 'cycles'),
    mn_pbe_cycles: integer(transition.Mn.scf_cycles, 'PBE SCF cycles for manganese', 'cycles'),
    fe_pbe_cycles: integer(transition.Fe.scf_cycles, 'PBE SCF cycles attempted for iron', 'cycles'),
    zn_pbe_cycles: integer(transition.Zn.scf_cycles, 'PBE SCF cycles for zinc', 'cycles'),
    fe_pbe_unconverged_attempt_count: integer(
      atom('Fe').tiers.PBE.outcome === 'unconverged' ? atom('Fe').tiers.PBE.attempts : 0,
      'Fixed iron PBE attempts that reached the SCF cycle cap without convergence',
      'attempts',
    ),
    i_pbe_cycles: integer(
      summary.contrasts.iodine_pbe.scf_cycles,
      'PBE SCF cycles attempted for iodine',
      'cycles',
    ),
    i_pbe_unconverged_attempt_count: integer(
      atom('I').tiers.PBE.outcome === 'unconverged' ? atom('I').tiers.PBE.attempts : 0,
      'Fixed iodine PBE attempts that reached the SCF cycle cap without convergence',
      'attempts',
    ),
    light_method_atom_count: integer(
      Object.keys(method.atoms).length,
      'Number of light atoms with UHF, PBE, MP2, and CCSD(T) timings',
      'atoms',
    ),
    ccsd_t_over_uhf_min: fixed(
      method.ccsd_t_over_uhf_minimum,
      2,
      'Smallest CCSD(T)-to-UHF wall-time ratio in the light-atom subset',
      'ratio',
    ),
    ccsd_t_over_uhf_max: fixed(
      method.ccsd_t_over_uhf_maximum,
      2,
      'Largest CCSD(T)-to-UHF wall-time ratio in the light-atom subset',
      'ratio',
    ),
    pbe_slower_than_ccsd_t_count: integer(
      method.pbe_slower_than_ccsd_t_count,
      'Light-atom cases in which PBE took longer than CCSD(T)',
      'atoms',
    ),
  };

  return {
    schema_version: 1,
    experiment: 'periodic-compute-cost',
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

let expected;
try {
  expected = `${JSON.stringify(buildMetrics(generatedAt), null, 2)}\n`;
} catch (error) {
  console.error(`periodic-compute-cost metric generation failed: ${error.message}`);
  process.exit(1);
}

if (checkOnly) {
  if (!existing || readFileSync(outputPath, 'utf8') !== expected) {
    console.error(`${relative(root, outputPath)} is missing or stale`);
    process.exit(1);
  }
  console.log('periodic-compute-cost: metrics.json is reproducible');
} else {
  writeFileSync(outputPath, expected);
  console.log(`wrote ${relative(root, outputPath)}`);
}
