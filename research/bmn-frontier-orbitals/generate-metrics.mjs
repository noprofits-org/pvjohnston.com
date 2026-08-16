#!/usr/bin/env node

// Projects the publication metrics for the BMN frontier-orbital note from the
// committed canonical results. Do not hand-author metrics.json.
//
// Two functionals are projected side by side on purpose: the note's point is
// that the absolute gap is strongly functional-dependent while the donor
// trend is not, so the post is expected to quote both throughout. CAM-B3LYP
// keys carry the `_cam` suffix and B3LYP keys `_b3lyp`; neither is privileged
// in the naming, unlike the parent DCDHF experiment where CAM-B3LYP was the
// preregistered adjudicator.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const frontierInput = 'research/bmn-frontier-orbitals/results/frontier_orbitals.json';
const checkOnly = process.argv.includes('--check');

const SUBS = ['h', 'f', 'nh2', 'nme2'];              // weak -> strong donor
const FUNCTIONALS = { cam: 'cam-b3lyp', b3lyp: 'b3lyp' };
// Hammett sigma_p_plus, Hansch/Leo/Taft 1991, embedded in the states records
// by build_geometries.py; re-asserted here so a silently edited results file
// cannot shift the regressions without failing the projection.
const SIGMA = { h: 0.0, f: -0.07, nh2: -1.3, nme2: -1.7 };

const statesInput = (sub, fn) =>
  `research/bmn-frontier-orbitals/results/states_bmn-${sub}_${FUNCTIONALS[fn]}_def2-tzvp.json`;

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

function leastSquares(xs, ys) {
  const n = xs.length;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let sxx = 0, sxy = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    sxx += (xs[i] - mx) ** 2;
    sxy += (xs[i] - mx) * (ys[i] - my);
    syy += (ys[i] - my) ** 2;
  }
  return { slope: sxy / sxx, r2: (sxy * sxy) / (sxx * syy) };
}

function loadFrontier() {
  const doc = JSON.parse(readFileSync(resolve(root, frontierInput), 'utf8'));
  const table = {};
  for (const rec of doc.molecules) {
    const fnKey = rec.functional === 'cam-b3lyp' ? 'cam' : 'b3lyp';
    const sub = rec.substituent.toLowerCase();
    if (Math.abs(rec.sigma_p_plus - SIGMA[sub]) > 1e-9) {
      throw new Error(`${frontierInput}: sigma_p_plus for ${sub} is `
        + `${rec.sigma_p_plus}, expected ${SIGMA[sub]}`);
    }
    table[`${sub}_${fnKey}`] = rec;
  }
  for (const sub of SUBS) {
    for (const fn of Object.keys(FUNCTIONALS)) {
      if (!table[`${sub}_${fn}`]) {
        throw new Error(`${frontierInput}: no record for ${sub}/${fn}`);
      }
    }
  }
  return table;
}

function s1(sub, fn) {
  const run = JSON.parse(readFileSync(resolve(root, statesInput(sub, fn)), 'utf8'));
  const states = [...run.states].sort((a, b) => a.energy_eV - b.energy_eV);
  if (!states.length) throw new Error(`${statesInput(sub, fn)}: no states`);
  const dom = states[0].dominant?.[0];
  // The note frames S1 as the HOMO -> LUMO transition; if the largest
  // amplitude were ever something else, that framing would be wrong and this
  // projection must fail rather than quote a weight for a different pair.
  if (dom?.from !== 'HOMO' || dom?.to !== 'LUMO') {
    throw new Error(`${statesInput(sub, fn)}: S1 dominant amplitude is `
      + `${dom?.from} -> ${dom?.to}, not HOMO -> LUMO`);
  }
  return { energy_eV: states[0].energy_eV, hl_weight_pct: dom.weight_pct };
}

function build(generatedAt) {
  const F = loadFrontier();
  const metrics = {};
  const subName = { h: 'H', f: 'F', nh2: 'NH2', nme2: 'NMe2' };
  const fnName = { cam: 'CAM-B3LYP', b3lyp: 'B3LYP' };

  for (const fn of Object.keys(FUNCTIONALS)) {
    for (const sub of SUBS) {
      const r = F[`${sub}_${fn}`];
      const tag = `${subName[sub]} (${fnName[fn]}/def2-TZVP)`;
      metrics[`homo_${sub}_${fn}`] = num(r.homo_eV, 2,
        `Kohn-Sham HOMO energy of BMN-${tag}`, 'eV');
      metrics[`homo1_${sub}_${fn}`] = num(r.homo_minus_1_eV, 2,
        `Kohn-Sham HOMO-1 energy of BMN-${tag}`, 'eV');
      metrics[`lumo_${sub}_${fn}`] = num(r.lumo_eV, 2,
        `Kohn-Sham LUMO energy of BMN-${tag}`, 'eV');
      metrics[`gap_${sub}_${fn}`] = num(r.gap_eV, 2,
        `Kohn-Sham HOMO-LUMO gap of BMN-${tag}`, 'eV');
      metrics[`s1_${sub}_${fn}`] = num(s1(sub, fn).energy_eV, 2,
        `Lowest TD-DFT vertical excitation energy of BMN-${tag}`, 'eV');
    }

    // Signed rises are kept positive and directions stated in prose, so the
    // rendered spans never fight the sentence around them.
    const d = (q) => F[`nme2_${fn}`][q] - F[`h_${fn}`][q];
    metrics[`d_homo_${fn}`] = num(d('homo_eV'), 2,
      `HOMO rise from BMN-H to BMN-NMe2 (${fnName[fn]})`, 'eV');
    metrics[`d_homo1_${fn}`] = num(d('homo_minus_1_eV'), 2,
      `HOMO-1 rise from BMN-H to BMN-NMe2 (${fnName[fn]})`, 'eV');
    metrics[`d_lumo_${fn}`] = num(d('lumo_eV'), 2,
      `LUMO rise from BMN-H to BMN-NMe2 (${fnName[fn]})`, 'eV');
    metrics[`gap_close_${fn}`] = num(-d('gap_eV'), 2,
      `Amount the gap closes from BMN-H to BMN-NMe2 (${fnName[fn]})`, 'eV');
    metrics[`homo_lumo_shift_ratio_${fn}`] = num(
      d('homo_eV') / d('lumo_eV'), 1,
      `Ratio of the HOMO rise to the LUMO rise from BMN-H to BMN-NMe2 (${fnName[fn]})`);
    metrics[`gap_close_f_${fn}`] = num(
      F[`h_${fn}`].gap_eV - F[`f_${fn}`].gap_eV, 2,
      `Amount the gap closes from BMN-H to BMN-F (${fnName[fn]})`, 'eV');
    metrics[`homo1_drop_f_${fn}`] = num(
      F[`h_${fn}`].homo_minus_1_eV - F[`f_${fn}`].homo_minus_1_eV, 2,
      `Amount the HOMO-1 drops from BMN-H to BMN-F (${fnName[fn]})`, 'eV');
    metrics[`s1_hl_weight_min_${fn}`] = num(
      Math.min(...SUBS.map((s) => s1(s, fn).hl_weight_pct)), 0,
      `Smallest dominant HOMO -> LUMO amplitude weight of S1 across the four donors (${fnName[fn]})`,
      '%');

    const sigmas = SUBS.map((s) => SIGMA[s]);
    for (const [q, key] of [['homo_eV', 'homo'], ['lumo_eV', 'lumo'], ['gap_eV', 'gap']]) {
      const fit = leastSquares(sigmas, SUBS.map((s) => F[`${s}_${fn}`][q]));
      // HOMO and LUMO slopes are reported against donor strength (-sigma),
      // where both are positive; the gap slope is reported against sigma
      // itself, where it is positive. Same fit either way, sign flipped.
      const vsDonor = key !== 'gap';
      metrics[`slope_${key}_${fn}`] = num(vsDonor ? -fit.slope : fit.slope, 2,
        `Least-squares slope of the ${key.toUpperCase()} energy against `
        + (vsDonor ? 'donor strength (-sigma_p_plus)' : 'sigma_p_plus')
        + ` over the four donors (${fnName[fn]})`, 'eV');
      if (key === 'gap') {
        metrics[`r2_gap_${fn}`] = num(fit.r2, 3,
          `Coefficient of determination of the gap-vs-sigma_p_plus fit (${fnName[fn]})`);
      }
    }
  }

  // Cross-functional teaching points, quoted for BMN-H where both gaps and
  // the excitation are on the figure.
  metrics.gap_functional_spread_h = num(
    F.h_cam.gap_eV - F.h_b3lyp.gap_eV, 2,
    'CAM-B3LYP minus B3LYP Kohn-Sham gap for BMN-H, the same molecule and geometry',
    'eV');
  metrics.gap_minus_s1_h_cam = num(
    F.h_cam.gap_eV - s1('h', 'cam').energy_eV, 2,
    'CAM-B3LYP Kohn-Sham gap of BMN-H minus its own TD-DFT S1 excitation energy',
    'eV');

  const inputs = [{ path: frontierInput, sha256: sha256(frontierInput) }];
  for (const fn of Object.keys(FUNCTIONALS)) {
    for (const sub of SUBS) {
      inputs.push({ path: statesInput(sub, fn), sha256: sha256(statesInput(sub, fn)) });
    }
  }

  return {
    schema_version: 1,
    experiment: 'bmn-frontier-orbitals',
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
