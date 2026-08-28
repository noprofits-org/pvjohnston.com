#!/usr/bin/env node

// Publication metrics for the Hillel M4 same-geometry two-root SF
// rematch. Numbers are flattened from the committed Bayes projection.
// Do not hand-author metrics.json. Do not invent energies or a
// crossing angle: the site interpolant metrics are the stored Bayes
// crossing_phi_deg_s0 and crossing_phi_deg_t1.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const bayesInput = 'research/hillel-m4-sft-tworoot/results/bayes-metrics.json';
const checkOnly = process.argv.includes('--check');

const REQUIRED_PHIS = [90, 105, 120, 135];
const FAMILIES = [
  { id: 's0_relaxed', key: 's0', label: 'S0-relaxed' },
  { id: 't1_relaxed', key: 't1', label: 'T1-relaxed' },
];
const EXPECTED_HASH_FILES = [
  'm4_s0_phi_090.out',
  'm4_s0_phi_105.out',
  'm4_s0_phi_120.out',
  'm4_s0_phi_135.out',
  'm4_t1_phi_090.out',
  'm4_t1_phi_105.out',
  'm4_t1_phi_120.out',
  'm4_t1_phi_135.out',
];

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

function requireSha256(value, label) {
  if (typeof value !== 'string' || !/^[0-9a-f]{64}$/.test(value)) {
    throw new Error(`${label} must be a 64-char lowercase hex SHA-256`);
  }
  return value;
}

function linearZero(x0, y0, x1, y1) {
  if (y0 === 0) return x0;
  if (y1 === 0) return x1;
  if (y0 * y1 > 0) return null;
  return x0 - (y0 * (x1 - x0)) / (y1 - y0);
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
  if (experimentId !== 'hillel-m4-sft-tworoot') {
    throw new Error(`${bayesInput}: experiment/slug must be hillel-m4-sft-tworoot`);
  }

  const conversion = requireFinite(
    bayes.conversion_Eh_to_kJmol,
    'conversion_Eh_to_kJmol',
  );
  assertClose(conversion, 2625.49963831, 'conversion_Eh_to_kJmol', 0);

  const hashes = Array.isArray(bayes.private_output_sha256)
    ? bayes.private_output_sha256
    : [];
  if (hashes.length !== EXPECTED_HASH_FILES.length) {
    throw new Error(`${bayesInput}: expected ${EXPECTED_HASH_FILES.length} private_output_sha256 entries`);
  }
  const hashByFile = {};
  for (const entry of hashes) {
    const file = entry?.file;
    if (!EXPECTED_HASH_FILES.includes(file)) {
      throw new Error(`${bayesInput}: unexpected private hash file ${file}`);
    }
    if (file.includes('/') || file.includes('\\')) {
      throw new Error(`${bayesInput}: private hash file must be a filename only`);
    }
    hashByFile[file] = requireSha256(entry.sha256, `${file} sha256`);
  }
  for (const file of EXPECTED_HASH_FILES) {
    if (!hashByFile[file]) {
      throw new Error(`${bayesInput}: missing private hash for ${file}`);
    }
  }
  requireSha256(
    bayes.private_lab_metrics_sha256,
    'private_lab_metrics_sha256',
  );

  const points = Array.isArray(bayes.points) ? bayes.points : [];
  const byFamily = {};
  for (const family of FAMILIES) {
    byFamily[family.id] = {};
  }
  for (const point of points) {
    const family = point?.geom_family;
    const phi = point?.phi_deg;
    if (!byFamily[family]) {
      throw new Error(`${bayesInput}: unexpected geom_family ${family}`);
    }
    if (!REQUIRED_PHIS.includes(Number(phi))) {
      throw new Error(`${bayesInput}: unexpected phi_deg ${phi}`);
    }
    if (byFamily[family][String(phi)]) {
      throw new Error(`${bayesInput}: duplicate ${family} ${phi}°`);
    }
    byFamily[family][String(phi)] = point;
  }

  const familyData = {};
  const s0S2 = [];
  const t1S2 = [];
  for (const family of FAMILIES) {
    const slots = {};
    for (const phi of REQUIRED_PHIS) {
      const point = byFamily[family.id][String(phi)];
      if (!point) {
        throw new Error(`${bayesInput}: missing ${family.id} point at ${phi}°`);
      }
      if (point.both_assigned !== true) {
        throw new Error(`${family.id} ${phi}°: required window point must be both-assigned`);
      }
      const s0E = requireFinite(point.s0?.E_Eh, `${family.id} ${phi} s0.E_Eh`);
      const t1E = requireFinite(point.t1?.E_Eh, `${family.id} ${phi} t1.E_Eh`);
      const s0s2 = requireFinite(point.s0?.S2, `${family.id} ${phi} s0.S2`);
      const t1s2 = requireFinite(point.t1?.S2, `${family.id} ${phi} t1.S2`);
      const s0Iroot = point.s0?.iroot;
      const t1Iroot = point.t1?.iroot;
      if (!Number.isInteger(s0Iroot) || !Number.isInteger(t1Iroot)) {
        throw new Error(`${family.id} ${phi}°: iroot values must be integers`);
      }
      const deltaE = requireFinite(point.deltaE_kJmol, `${family.id} ${phi} deltaE_kJmol`);
      assertClose((t1E - s0E) * conversion, deltaE, `${family.id} ${phi} ΔE from Eh`, 1e-8);
      s0S2.push(s0s2);
      t1S2.push(t1s2);
      slots[phi] = {
        s0E, t1E, s0s2, t1s2, s0Iroot, t1Iroot, deltaE,
      };
    }
    familyData[family.id] = slots;
  }

  const pairs = Array.isArray(bayes.neighboring_pairs)
    ? bayes.neighboring_pairs
    : [];
  const familyFlags = {};
  for (const family of FAMILIES) {
    const slots = familyData[family.id];
    const familyPairs = pairs.filter((pair) => pair.geom_family === family.id);
    const claimPair = familyPairs.find((pair) => {
      const [a, b] = pairEnds(pair);
      return a === 90 && b === 105;
    });
    if (!claimPair) {
      throw new Error(`${bayesInput}: missing ${family.id} neighboring_pairs 90/105 entry`);
    }
    const pairInterpolant = requireFinite(
      pairInterpolantOf(claimPair),
      `${family.id} 90/105 interpolant`,
    );
    const derivedZero = linearZero(
      90, slots[90].deltaE, 105, slots[105].deltaE,
    );
    if (derivedZero === null) {
      throw new Error(`${family.id} 90/105 pair does not change ΔE sign`);
    }
    assertClose(derivedZero, pairInterpolant, `${family.id} 90/105 derived interpolant`, 1e-8);
    const storedCrossing = requireFinite(
      bayes[`crossing_phi_deg_${family.key}`],
      `crossing_phi_deg_${family.key}`,
    );
    assertClose(storedCrossing, pairInterpolant, `${family.id} stored crossing vs 90/105 interpolant`, 1e-8);

    const usablePairs = familyPairs.filter((pair) => pair.both_assigned === true);
    const signChangePairs = [
      [90, 105],
      [105, 120],
      [120, 135],
    ].filter(([a, b]) => slots[a].deltaE * slots[b].deltaE < 0);
    const familySupported = requireBool(
      bayes[`hypothesis_supported_${family.key}_family`],
      `hypothesis_supported_${family.key}_family`,
    );
    const derivedFamilySupported = signChangePairs.length > 0
      && storedCrossing >= 90
      && storedCrossing <= 135
      && usablePairs.length > 0;
    if (familySupported !== derivedFamilySupported) {
      throw new Error(`hypothesis_supported_${family.key}_family ${familySupported} !== ${derivedFamilySupported}`);
    }
    familyFlags[family.id] = {
      storedCrossing,
      pairInterpolant,
      signChangeCount: signChangePairs.length,
      usablePairCount: usablePairs.length,
      familySupported,
    };
  }

  const s0Flags = familyFlags.s0_relaxed;
  const t1Flags = familyFlags.t1_relaxed;
  const falsifier1 = requireBool(bayes.falsifier_1_no_sign_change, 'falsifier_1_no_sign_change');
  const falsifier2 = requireBool(bayes.falsifier_2_crossing_outside_90_135, 'falsifier_2_crossing_outside_90_135');
  const falsifier3 = requireBool(bayes.falsifier_3_no_neighboring_pair, 'falsifier_3_no_neighboring_pair');
  const hypothesisSupported = requireBool(bayes.hypothesis_supported, 'hypothesis_supported');

  const derivedF1 = s0Flags.signChangeCount === 0 && t1Flags.signChangeCount === 0;
  const derivedF2 = (s0Flags.signChangeCount > 0 && (s0Flags.storedCrossing < 90 || s0Flags.storedCrossing > 135))
    || (t1Flags.signChangeCount > 0 && (t1Flags.storedCrossing < 90 || t1Flags.storedCrossing > 135));
  const derivedF3 = s0Flags.usablePairCount === 0 || t1Flags.usablePairCount === 0;
  if (falsifier1 !== derivedF1) {
    throw new Error(`falsifier_1_no_sign_change ${falsifier1} !== ${derivedF1}`);
  }
  if (falsifier2 !== derivedF2) {
    throw new Error(`falsifier_2_crossing_outside_90_135 ${falsifier2} !== ${derivedF2}`);
  }
  if (falsifier3 !== derivedF3) {
    throw new Error(`falsifier_3_no_neighboring_pair ${falsifier3} !== ${derivedF3}`);
  }
  const derivedSupported = s0Flags.familySupported && t1Flags.familySupported
    && !falsifier1 && !falsifier2 && !falsifier3;
  if (hypothesisSupported !== derivedSupported) {
    throw new Error(`hypothesis_supported ${hypothesisSupported} !== ${derivedSupported}`);
  }

  const assignedS0Min = Math.min(...s0S2);
  const assignedS0Max = Math.max(...s0S2);
  const assignedT1Min = Math.min(...t1S2);
  const assignedT1Max = Math.max(...t1S2);
  assertClose(assignedS0Min, requireFinite(bayes.assigned_s0_s2_min, 'assigned_s0_s2_min'), 'assigned_s0_s2_min');
  assertClose(assignedS0Max, requireFinite(bayes.assigned_s0_s2_max, 'assigned_s0_s2_max'), 'assigned_s0_s2_max');
  assertClose(assignedT1Min, requireFinite(bayes.assigned_t1_s2_min, 'assigned_t1_s2_min'), 'assigned_t1_s2_min');
  assertClose(assignedT1Max, requireFinite(bayes.assigned_t1_s2_max, 'assigned_t1_s2_max'), 'assigned_t1_s2_max');

  const metrics = {
    crossing_phi_deg_s0: num(s0Flags.storedCrossing, 2,
      'Stored Bayes linear interpolant of same-geometry ΔE=E(T1)−E(S0) on the S0-relaxed 90°/105° pair',
      'deg'),
    crossing_phi_deg_t1: num(t1Flags.storedCrossing, 2,
      'Stored Bayes linear interpolant of same-geometry ΔE=E(T1)−E(S0) on the T1-relaxed 90°/105° pair',
      'deg'),
    hypothesis_supported: boolean(hypothesisSupported,
      'Registered hypothesis supported: both families have a both-assigned same-geometry ΔE sign change inside 90–135°'),
    hypothesis_supported_s0_family: boolean(s0Flags.familySupported,
      'S0-relaxed family has a both-assigned same-geometry ΔE sign change inside 90–135°'),
    hypothesis_supported_t1_family: boolean(t1Flags.familySupported,
      'T1-relaxed family has a both-assigned same-geometry ΔE sign change inside 90–135°'),
    falsifier_1_no_sign_change: boolean(falsifier1,
      'Falsifier 1: neither family has a both-assigned same-geometry ΔE sign change on a neighboring pair in 90–135°'),
    falsifier_2_crossing_outside_90_135: boolean(falsifier2,
      'Falsifier 2: a family has a sign change whose interpolant lies outside 90–135°'),
    falsifier_3_no_neighboring_pair: boolean(falsifier3,
      'Falsifier 3: a family has no neighboring both-assigned pair'),
    assigned_s0_s2_min: num(assignedS0Min, 2,
      'Minimum assigned S0 ⟨S²⟩ across the eight same-geometry points'),
    assigned_s0_s2_max: num(assignedS0Max, 2,
      'Maximum assigned S0 ⟨S²⟩ across the eight same-geometry points'),
    assigned_t1_s2_min: num(assignedT1Min, 2,
      'Minimum assigned T1 ⟨S²⟩ across the eight same-geometry points'),
    assigned_t1_s2_max: num(assignedT1Max, 2,
      'Maximum assigned T1 ⟨S²⟩ across the eight same-geometry points'),
  };

  for (const family of FAMILIES) {
    for (const phi of REQUIRED_PHIS) {
      const point = familyData[family.id][phi];
      metrics[`deltae_kjmol_${family.key}_${phi}`] = num(point.deltaE, 2,
        `Same-geometry ΔE=E(T1)−E(S0) on the ${family.label} geometry at CNNC ${phi}°, both-assigned`,
        'kJ/mol');
      metrics[`s0_e_eh_${family.key}_${phi}`] = raw(point.s0E,
        `Assigned SF-S0 total energy on the ${family.label} geometry at CNNC ${phi}°`,
        'Eh');
      metrics[`t1_e_eh_${family.key}_${phi}`] = raw(point.t1E,
        `Assigned SF-T1 total energy on the ${family.label} geometry at CNNC ${phi}°`,
        'Eh');
      metrics[`s0_s2_${family.key}_${phi}`] = num(point.s0s2, 6,
        `Assigned SF-S0 ⟨S²⟩ on the ${family.label} geometry at CNNC ${phi}°`);
      metrics[`t1_s2_${family.key}_${phi}`] = num(point.t1s2, 6,
        `Assigned SF-T1 ⟨S²⟩ on the ${family.label} geometry at CNNC ${phi}°`);
      metrics[`s0_iroot_${family.key}_${phi}`] = integer(point.s0Iroot,
        `Assigned SF-S0 iroot on the ${family.label} geometry at CNNC ${phi}°`);
      metrics[`t1_iroot_${family.key}_${phi}`] = integer(point.t1Iroot,
        `Assigned SF-T1 iroot on the ${family.label} geometry at CNNC ${phi}°`);
    }
  }

  return {
    schema_version: 1,
    experiment: 'hillel-m4-sft-tworoot',
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
