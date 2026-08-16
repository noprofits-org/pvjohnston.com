#!/usr/bin/env node

// Projects the publication metrics for the acceptor-strength ladder from the
// committed canonical results. Do not hand-author metrics.json.
//
// Three rungs with a fixed para-methoxy donor and increasing acceptor strength:
// CN < DCV < TCF. Two functionals are projected side by side: CAM-B3LYP and
// B3LYP. CAM-B3LYP keys carry the `_cam` suffix and B3LYP keys `_b3lyp`.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const frontierInput = 'research/meo-acceptor-ladder/results/frontier_orbitals.json';
const checkOnly = process.argv.includes('--check');

const ACCEPTORS = ['CN', 'DCV', 'TCF'];           // weak -> strong acceptor
const ACCEPTOR_STRENGTH = { CN: 1, DCV: 2, TCF: 3 };
const FUNCTIONALS = { cam: 'cam-b3lyp', b3lyp: 'b3lyp' };

const statesInput = (acc, fn) =>
  `research/meo-acceptor-ladder/results/states_meo-${acc.toLowerCase()}_${FUNCTIONALS[fn]}_def2-tzvp.json`;

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

const num = (value, digits, description, unit) => ({
  type: 'number',
  value,
  format: { style: 'fixed', digits },
  description,
  ...(unit ? { unit } : {}),
});

function loadFrontier() {
  const doc = JSON.parse(readFileSync(resolve(root, frontierInput), 'utf8'));
  const table = {};
  for (const rec of doc.molecules) {
    const fnKey = rec.functional === 'cam-b3lyp' ? 'cam' : 'b3lyp';
    const acc = rec.acceptor;
    if (ACCEPTOR_STRENGTH[acc] !== rec.acceptor_strength) {
      throw new Error(`${frontierInput}: acceptor_strength for ${acc} is `
        + `${rec.acceptor_strength}, expected ${ACCEPTOR_STRENGTH[acc]}`);
    }
    table[`${acc}_${fnKey}`] = rec;
  }
  for (const acc of ACCEPTORS) {
    for (const fn of Object.keys(FUNCTIONALS)) {
      if (!table[`${acc}_${fn}`]) {
        throw new Error(`${frontierInput}: no record for ${acc}/${fn}`);
      }
    }
  }
  return table;
}

function s1(acc, fn) {
  const run = JSON.parse(readFileSync(resolve(root, statesInput(acc, fn)), 'utf8'));
  const states = [...run.states].sort((a, b) => a.energy_eV - b.energy_eV);
  if (!states.length) throw new Error(`${statesInput(acc, fn)}: no states`);
  const dom = states[0].dominant?.[0];
  const hl = dom?.from === 'HOMO' && dom?.to === 'LUMO';
  return {
    energy_eV: states[0].energy_eV,
    hl_weight_pct: hl ? dom.weight_pct : 0,
    character: dom ? `${dom.from}→${dom.to}` : 'unknown',
    character_detail: dom ? `${dom.from}→${dom.to} (${dom.weight_pct.toFixed(1)}%)` : 'unknown',
  };
}

function build(generatedAt) {
  const F = loadFrontier();
  const metrics = {};
  const fnName = { cam: 'CAM-B3LYP', b3lyp: 'B3LYP' };

  for (const fn of Object.keys(FUNCTIONALS)) {
    for (const acc of ACCEPTORS) {
      const r = F[`${acc}_${fn}`];
      const tag = `${acc} (${fnName[fn]}/def2-TZVP)`;
      metrics[`homo_${acc.toLowerCase()}_${fn}`] = num(r.homo_eV, 2,
        `Kohn-Sham HOMO energy of MeO-Ph-${tag}`, 'eV');
      metrics[`homo1_${acc.toLowerCase()}_${fn}`] = num(r.homo_minus_1_eV, 2,
        `Kohn-Sham HOMO-1 energy of MeO-Ph-${tag}`, 'eV');
      metrics[`lumo_${acc.toLowerCase()}_${fn}`] = num(r.lumo_eV, 2,
        `Kohn-Sham LUMO energy of MeO-Ph-${tag}`, 'eV');
      metrics[`gap_${acc.toLowerCase()}_${fn}`] = num(r.gap_eV, 2,
        `Kohn-Sham HOMO-LUMO gap of MeO-Ph-${tag}`, 'eV');
      metrics[`s1_${acc.toLowerCase()}_${fn}`] = num(s1(acc, fn).energy_eV, 2,
        `Lowest TD-DFT vertical excitation energy of MeO-Ph-${tag}`, 'eV');
      metrics[`s1_character_${acc.toLowerCase()}_${fn}`] = {
        type: 'string',
        value: s1(acc, fn).character_detail,
        description: `Dominant amplitude character of S1 for MeO-Ph-${tag}`,
      };
    }

    // Signed changes from the weakest acceptor (CN) to the strongest (TCF).
    const d = (q) => F[`TCF_${fn}`][q] - F[`CN_${fn}`][q];
    metrics[`d_homo_${fn}`] = num(d('homo_eV'), 2,
      `HOMO change from MeO-Ph-CN to MeO-Ph-TCF (${fnName[fn]})`, 'eV');
    metrics[`d_homo1_${fn}`] = num(d('homo_minus_1_eV'), 2,
      `HOMO-1 change from MeO-Ph-CN to MeO-Ph-TCF (${fnName[fn]})`, 'eV');
    metrics[`d_lumo_${fn}`] = num(d('lumo_eV'), 2,
      `LUMO change from MeO-Ph-CN to MeO-Ph-TCF (${fnName[fn]})`, 'eV');
    metrics[`gap_close_${fn}`] = num(-d('gap_eV'), 2,
      `Amount the gap closes from MeO-Ph-CN to MeO-Ph-TCF (${fnName[fn]})`, 'eV');
    metrics[`d_s1_${fn}`] = num(
      s1('CN', fn).energy_eV - s1('TCF', fn).energy_eV, 2,
      `Red shift of S1 from MeO-Ph-CN to MeO-Ph-TCF (${fnName[fn]})`, 'eV');
    metrics[`s1_hl_weight_min_${fn}`] = num(
      Math.min(...ACCEPTORS.map((a) => s1(a, fn).hl_weight_pct)), 0,
      `Smallest dominant HOMO -> LUMO amplitude weight of S1 across the three acceptors (${fnName[fn]}); 0 when the lowest state is not HOMO -> LUMO`,
      '%');
  }

  // Cross-functional teaching points, quoted for MeO-Ph-CN where both gaps and
  // the excitation are on the figure.
  metrics.gap_functional_spread_cn = num(
    F.CN_cam.gap_eV - F.CN_b3lyp.gap_eV, 2,
    'CAM-B3LYP minus B3LYP Kohn-Sham gap for MeO-Ph-CN, the same molecule and geometry',
    'eV');
  metrics.gap_minus_s1_cn_cam = num(
    F.CN_cam.gap_eV - s1('CN', 'cam').energy_eV, 2,
    'CAM-B3LYP Kohn-Sham gap of MeO-Ph-CN minus its own TD-DFT S1 excitation energy',
    'eV');

  const inputs = [{ path: frontierInput, sha256: sha256(frontierInput) }];
  for (const fn of Object.keys(FUNCTIONALS)) {
    for (const acc of ACCEPTORS) {
      inputs.push({ path: statesInput(acc, fn), sha256: sha256(statesInput(acc, fn)) });
    }
  }

  return {
    schema_version: 1,
    experiment: 'meo-acceptor-ladder',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs,
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
