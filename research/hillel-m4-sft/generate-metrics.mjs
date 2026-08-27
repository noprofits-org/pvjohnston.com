#!/usr/bin/env node

// Publication metrics for the Hillel M4 SF-TDDFT rematch. Numbers are
// flattened from the committed Bayes projection. Do not hand-author
// metrics.json. Do not invent energies or a crossing angle: the site
// crossing metric is the stored Bayes crossing_phi_deg.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const bayesInput = 'research/hillel-m4-sft/results/bayes-metrics.json';
const checkOnly = process.argv.includes('--check');

const REQUIRED_PHIS = [90, 105, 120, 135];

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

const raw = (value, description, unit) => ({
  type: 'number',
  value,
  format: { style: 'raw' },
  description,
  ...(unit ? { unit } : {}),
});

const integer = (value, description, unit) => ({
  type: 'integer',
  value,
  description,
  ...(unit ? { unit } : {}),
});

const boolean = (value, description) => ({
  type: 'boolean',
  value,
  description,
});

function assertClose(actual, expected, label, tol = 1e-9) {
  if (!Number.isFinite(actual) || !Number.isFinite(expected)
      || Math.abs(actual - expected) > tol) {
    throw new Error(`${label}: ${actual} !== ${expected}`);
  }
}

function requireFinite(value, label) {
  if (!Number.isFinite(value)) {
    throw new Error(`${label} is not finite: ${value}`);
  }
  return value;
}

function requireBool(value, label) {
  if (typeof value !== 'boolean') {
    throw new Error(`${label} must be boolean, got ${value}`);
  }
  return value;
}

function linearZero(x0, y0, x1, y1) {
  if (y0 === 0) return x0;
  if (y1 === 0) return x1;
  if (y0 * y1 > 0) return null;
  return x0 - (y0 * (x1 - x0)) / (y1 - y0);
}

function pointMap(points) {
  if (Array.isArray(points)) {
    const map = {};
    for (const point of points) {
      const phi = point?.phi_deg;
      if (!Number.isFinite(phi)) {
        throw new Error('points[] entry is missing a finite phi_deg');
      }
      map[String(phi)] = point;
    }
    return map;
  }
  if (points && typeof points === 'object') return points;
  throw new Error(`${bayesInput}: points list or object is required`);
}

function pointAt(points, phi) {
  const point = points[String(phi)];
  if (!point) throw new Error(`missing Bayes point at ${phi}°`);
  return point;
}

function pairEnds(pair) {
  if (Array.isArray(pair.pair) && pair.pair.length === 2) {
    return [Number(pair.pair[0]), Number(pair.pair[1])];
  }
  return [Number(pair.phi_a), Number(pair.phi_b)];
}

function pairInterpolantOf(pair) {
  if (typeof pair.interpolated_crossing_phi_deg === 'number') {
    return pair.interpolated_crossing_phi_deg;
  }
  if (typeof pair.interpolant === 'number') return pair.interpolant;
  return null;
}

function build(generatedAt) {
  const bayes = JSON.parse(readFileSync(resolve(root, bayesInput), 'utf8'));
  const experimentId = bayes.experiment ?? bayes.slug;
  if (experimentId !== 'hillel-m4-sft') {
    throw new Error(`${bayesInput}: experiment/slug must be hillel-m4-sft`);
  }

  const conversion = requireFinite(
    bayes.conversion_Eh_to_kJmol,
    'conversion_Eh_to_kJmol',
  );
  const crossing = requireFinite(bayes.crossing_phi_deg, 'crossing_phi_deg');
  const hypothesisSupported = requireBool(
    bayes.hypothesis_supported,
    'hypothesis_supported',
  );
  const falsifier1 = requireBool(
    bayes.falsifier_1_no_sign_change,
    'falsifier_1_no_sign_change',
  );
  const falsifier2 = requireBool(
    bayes.falsifier_2_crossing_outside_90_135,
    'falsifier_2_crossing_outside_90_135',
  );
  const falsifier3 = requireBool(
    bayes.falsifier_3_no_neighboring_pair,
    'falsifier_3_no_neighboring_pair',
  );

  const points = pointMap(bayes.points);
  const extraPhis = Object.keys(points).filter(
    (key) => !REQUIRED_PHIS.includes(Number(key)),
  );
  if (extraPhis.length !== 0) {
    throw new Error(`${bayesInput}: unexpected points ${extraPhis.join(',')}`);
  }

  const byPhi = {};
  for (const phi of REQUIRED_PHIS) {
    const point = pointAt(points, phi);
    const s0E = requireFinite(point.s0?.E_Eh, `${phi} s0.E_Eh`);
    const t1E = requireFinite(point.t1?.E_Eh, `${phi} t1.E_Eh`);
    const s0S2 = requireFinite(point.s0?.S2, `${phi} s0.S2`);
    const t1S2 = requireFinite(point.t1?.S2, `${phi} t1.S2`);
    const s0Iroot = point.s0?.iroot;
    const t1Iroot = point.t1?.iroot;
    if (!Number.isInteger(s0Iroot) || !Number.isInteger(t1Iroot)) {
      throw new Error(`${phi}: iroot values must be integers`);
    }
    const deltaE = requireFinite(point.deltaE_kJmol, `${phi} deltaE_kJmol`);
    assertClose((t1E - s0E) * conversion, deltaE, `${phi} ΔE from Eh`, 1e-8);
    if (point.both_converged !== true || point.both_assigned !== true) {
      throw new Error(`${phi}: required window point must be both-converged and both-assigned`);
    }
    byPhi[phi] = {
      s0E, t1E, s0S2, t1S2, s0Iroot, t1Iroot, deltaE,
    };
  }

  const pairs = Array.isArray(bayes.neighboring_pairs)
    ? bayes.neighboring_pairs
    : [];
  const claimPair = pairs.find((pair) => {
    const [a, b] = pairEnds(pair);
    return a === 90 && b === 105;
  });
  if (!claimPair) {
    throw new Error(`${bayesInput}: missing neighboring_pairs 90/105 entry`);
  }
  const pairInterpolant = requireFinite(
    pairInterpolantOf(claimPair),
    '90/105 interpolant',
  );
  const derivedZero = linearZero(
    90, byPhi[90].deltaE, 105, byPhi[105].deltaE,
  );
  if (derivedZero === null) {
    throw new Error('90/105 pair does not change ΔE sign');
  }
  assertClose(derivedZero, pairInterpolant, '90/105 derived interpolant', 1e-8);
  assertClose(crossing, pairInterpolant, 'stored crossing vs 90/105 interpolant', 1e-8);

  const signChangeCount = [
    [90, 105],
    [105, 120],
    [120, 135],
  ].filter(([a, b]) => byPhi[a].deltaE * byPhi[b].deltaE < 0).length;
  const derivedF1 = signChangeCount === 0;
  const derivedF2 = crossing < 90 || crossing > 135;
  const derivedF3 = pairs.length === 0;
  if (falsifier1 !== derivedF1) {
    throw new Error(`falsifier_1_no_sign_change ${falsifier1} !== ${derivedF1}`);
  }
  if (falsifier2 !== derivedF2) {
    throw new Error(`falsifier_2_crossing_outside_90_135 ${falsifier2} !== ${derivedF2}`);
  }
  if (falsifier3 !== derivedF3) {
    throw new Error(`falsifier_3_no_neighboring_pair ${falsifier3} !== ${derivedF3}`);
  }
  const derivedSupported = !falsifier1 && !falsifier2 && !falsifier3;
  if (hypothesisSupported !== derivedSupported) {
    throw new Error(`hypothesis_supported ${hypothesisSupported} !== ${derivedSupported}`);
  }

  const metrics = {
    crossing_phi_deg: num(crossing, 2,
      'Stored Bayes linear interpolant of ΔE=E(T1)−E(S0) on the 90°/105° pair',
      'deg'),
    hypothesis_supported: boolean(hypothesisSupported,
      'Registered hypothesis supported: both-converged both-assigned S0/T1 sign change inside 90–135°'),
    falsifier_1_no_sign_change: boolean(falsifier1,
      'Falsifier 1: no both-converged both-assigned ΔE sign change on the required window'),
    falsifier_2_crossing_outside_90_135: boolean(falsifier2,
      'Falsifier 2: stored crossing_phi_deg lies outside 90–135°'),
    falsifier_3_no_neighboring_pair: boolean(falsifier3,
      'Falsifier 3: no neighboring both-converged both-assigned pair in the Bayes projection'),
  };

  for (const phi of REQUIRED_PHIS) {
    const point = byPhi[phi];
    metrics[`deltae_kjmol_${phi}`] = num(point.deltaE, 2,
      `ΔE=E(T1)−E(S0) at CNNC ${phi}°, both-converged and both-assigned`,
      'kJ/mol');
    metrics[`s0_e_eh_${phi}`] = raw(point.s0E,
      `Assigned SF-S0 total energy at CNNC ${phi}°`,
      'Eh');
    metrics[`t1_e_eh_${phi}`] = raw(point.t1E,
      `Assigned SF-T1 total energy at CNNC ${phi}°`,
      'Eh');
    metrics[`s0_s2_${phi}`] = num(point.s0S2, 6,
      `Assigned SF-S0 ⟨S²⟩ at CNNC ${phi}°`);
    metrics[`t1_s2_${phi}`] = num(point.t1S2, 6,
      `Assigned SF-T1 ⟨S²⟩ at CNNC ${phi}°`);
    metrics[`s0_iroot_${phi}`] = integer(point.s0Iroot,
      `Assigned SF-S0 iroot at CNNC ${phi}°`);
    metrics[`t1_iroot_${phi}`] = integer(point.t1Iroot,
      `Assigned SF-T1 iroot at CNNC ${phi}°`);
  }

  return {
    schema_version: 1,
    experiment: 'hillel-m4-sft',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [{ path: bayesInput, sha256: sha256(bayesInput) }],
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
