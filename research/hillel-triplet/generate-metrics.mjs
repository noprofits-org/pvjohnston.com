#!/usr/bin/env node

// Publication metrics for the Hillel-triplet CNNC scan. Numbers are derived
// from the committed results.json projection. Do not hand-author metrics.json.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const resultInput = 'research/hillel-triplet/results/results.json';
const m0Csv = 'research/hillel-triplet/results/m0_summary.csv';
const m1Csv = 'research/hillel-triplet/results/m1_summary.csv';
const m2Csv = 'research/hillel-triplet/results/m2_summary.csv';
const m3Csv = 'research/hillel-triplet/results/m3_summary.csv';
const m4Csv = 'research/hillel-triplet/results/m4_summary.csv';
const controlsCsv = 'research/hillel-triplet/results/controls_summary.csv';
const checkOnly = process.argv.includes('--check');

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

function linearZero(x0, y0, x1, y1) {
  if (y0 === 0) return x0;
  if (y1 === 0) return x1;
  if (y0 * y1 > 0) return null;
  return x0 - (y0 * (x1 - x0)) / (y1 - y0);
}

function gapOf(point) {
  if (typeof point.gap_kjmol === 'number') return point.gap_kjmol;
  if (typeof point.s0_rel_kjmol === 'number' && typeof point.t1_rel_kjmol === 'number') {
    return point.s0_rel_kjmol - point.t1_rel_kjmol;
  }
  throw new Error(`point at ${point.cnnc_deg}° has no gap`);
}

function bothConverged(point) {
  if (point.both_converged === true) return true;
  if (point.both_converged === false) return false;
  return point.s0_converged === true && point.t1_converged === true;
}

function pointAt(points, deg, label = 'grid') {
  const found = points.find((p) => p.cnnc_deg === deg);
  if (!found) throw new Error(`missing ${label} point at ${deg}°`);
  return found;
}

function oneDecimal(value) {
  return Math.round(value * 10) / 10;
}

function deriveNeighborZeros(points, step) {
  const sorted = [...points].sort((a, b) => b.cnnc_deg - a.cnnc_deg);
  const zeros = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const hi = sorted[i];
    const lo = sorted[i + 1];
    if (hi.cnnc_deg - lo.cnnc_deg !== step) continue;
    if (!bothConverged(hi) || !bothConverged(lo)) continue;
    const zero = linearZero(hi.cnnc_deg, gapOf(hi), lo.cnnc_deg, gapOf(lo));
    if (zero === null) continue;
    zeros.push({ deg: zero, hi: hi.cnnc_deg, lo: lo.cnnc_deg });
  }
  return zeros;
}

function requirePair(zeros, hi, lo, label) {
  const found = zeros.filter((z) => z.hi === hi && z.lo === lo);
  if (found.length !== 1) {
    throw new Error(`${label}: expected one both-converged ${hi}/${lo} zero, got ${found.length}`);
  }
  return found[0].deg;
}

function parseCsv(path) {
  const text = readFileSync(resolve(root, path), 'utf8').trim();
  const [headerLine, ...lines] = text.split('\n');
  const headers = splitCsvLine(headerLine);
  return { headers, rows: lines.map((line, index) => {
    const cells = splitCsvLine(line);
    if (cells.length !== headers.length) {
      throw new Error(`${path}:${index + 2} has ${cells.length} fields, expected ${headers.length}`);
    }
    const row = {};
    headers.forEach((h, i) => { row[h] = cells[i] ?? ''; });
    return row;
  }) };
}

function splitCsvLine(line) {
  const cells = [];
  let current = '';
  let quoted = false;
  for (const ch of line) {
    if (ch === '"') {
      quoted = !quoted;
    } else if (ch === ',' && !quoted) {
      cells.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  cells.push(current);
  return cells;
}

function requireHeaders(path, headers, expected) {
  if (headers.join(',') !== expected.join(',')) {
    throw new Error(`${path}: headers ${headers.join(',')} !== ${expected.join(',')}`);
  }
}

function csvFlag(value) {
  if (value === true) return 'true';
  if (value === false) return 'false';
  throw new Error(`non-boolean flag ${value}`);
}

function assertClose(actual, expected, label, tol = 1e-9) {
  if (!Number.isFinite(actual) || !Number.isFinite(expected)
      || Math.abs(actual - expected) > tol) {
    throw new Error(`${label}: ${actual} !== ${expected}`);
  }
}

function validateSharedFields(row, point, label) {
  assertClose(Number(row.cnnc_deg), point.cnnc_deg, `${label} angle`);

  if (typeof point.s0_rel_kjmol === 'number') {
    assertClose(Number(row.s0_rel_kjmol), point.s0_rel_kjmol, `${label} S0`);
  } else if (row.s0_rel_kjmol !== '') {
    throw new Error(`${label}: S0 must be blank`);
  }

  if (typeof point.t1_rel_kjmol === 'number') {
    assertClose(Number(row.t1_rel_kjmol), point.t1_rel_kjmol, `${label} T1`);
  } else if (row.t1_rel_kjmol !== '') {
    throw new Error(`${label}: T1 must be blank`);
  }

  if (Object.hasOwn(row, 's0_converged')) {
    if (row.s0_converged !== csvFlag(point.s0_converged)) {
      throw new Error(`${label}: s0_converged ${row.s0_converged} !== ${point.s0_converged}`);
    }
    if (row.t1_converged !== csvFlag(point.t1_converged)) {
      throw new Error(`${label}: t1_converged ${row.t1_converged} !== ${point.t1_converged}`);
    }
  }
  if (Object.hasOwn(row, 'both_converged')) {
    if (row.both_converged !== csvFlag(point.both_converged)) {
      throw new Error(`${label}: both_converged ${row.both_converged} !== ${point.both_converged}`);
    }
  }

  const expectedGap = typeof point.gap_kjmol === 'number'
    ? point.gap_kjmol
    : (typeof point.s0_rel_kjmol === 'number' && typeof point.t1_rel_kjmol === 'number'
      ? point.s0_rel_kjmol - point.t1_rel_kjmol
      : null);
  if (expectedGap === null) {
    if (row.gap_kjmol !== '') {
      throw new Error(`${label}: gap must be blank`);
    }
  } else {
    assertClose(Number(row.gap_kjmol), expectedGap, `${label} gap`);
  }

  if (Object.hasOwn(row, 's0_eh')) {
    if (typeof point.s0_eh === 'number') {
      assertClose(Number(row.s0_eh), point.s0_eh, `${label} s0_eh`);
    } else if (row.s0_eh !== '') {
      throw new Error(`${label}: s0_eh must be blank`);
    }
  }
}

function validateGridCsv(path, points, molecule) {
  const { headers, rows } = parseCsv(path);
  if (rows.length !== points.length) {
    throw new Error(`${path}: ${rows.length} rows, expected ${points.length} ${molecule} points`);
  }
  const seen = new Set();
  for (const row of rows) {
    const deg = Number(row.cnnc_deg);
    if (!Number.isFinite(deg)) {
      throw new Error(`${path}: non-finite angle ${row.cnnc_deg}`);
    }
    const point = points.find((p) => p.cnnc_deg === deg);
    if (!point) throw new Error(`${path}: no ${molecule} point at ${deg}`);
    if (seen.has(deg)) throw new Error(`${path}: duplicate ${deg}`);
    seen.add(deg);
    validateSharedFields(row, point, `${path} ${deg}`);
  }
  for (const point of points) {
    if (!seen.has(point.cnnc_deg)) {
      throw new Error(`${path}: missing row for ${point.cnnc_deg}`);
    }
  }
  return { headers, rows };
}

function build(generatedAt) {
  let nanRejected = false;
  try {
    assertClose(Number('oops'), 0, 'assertClose-NaN');
  } catch (err) {
    nanRejected = String(err.message).includes('assertClose-NaN');
  }
  if (!nanRejected) {
    throw new Error('assertClose must reject non-finite numbers');
  }

  const result = JSON.parse(readFileSync(resolve(root, resultInput), 'utf8'));
  if (result.experiment !== 'hillel-triplet') {
    throw new Error(`${resultInput}: experiment must be hillel-triplet`);
  }
  if (result.eh_to_kjmol !== 2625.4996) {
    throw new Error(`${resultInput}: eh_to_kjmol must be 2625.4996`);
  }
  const step = result.step_deg;
  if (step !== 15) {
    throw new Error(`${resultInput}: step_deg must be 15`);
  }

  const m4 = result.molecules.M4;
  const m2 = result.molecules.M2;
  const m0 = result.molecules.M0;
  const m1 = result.molecules.M1;
  const m3 = result.molecules.M3;
  const points = m4.points;
  if (points.filter((p) => p.t1_converged).length !== result.grid_deg.length) {
    throw new Error('M4 T1 must converge at every declared grid angle');
  }
  if (typeof m4.trans_s0_eh !== 'number') {
    throw new Error('M4 trans_s0_eh is required to derive cis-side T1 relatives');
  }

  const p120 = pointAt(points, 120, 'M4');
  const p105 = pointAt(points, 105, 'M4');
  const p60 = pointAt(points, 60, 'M4');
  if (!bothConverged(p120) || !bothConverged(p105) || !bothConverged(p60)) {
    throw new Error('M4 120/105/60 must be both-converged in the projection');
  }

  const gap120 = gapOf(p120);
  const gap105 = gapOf(p105);
  const gap60 = gapOf(p60);
  const crossing = linearZero(p120.cnnc_deg, gap120, p105.cnnc_deg, gap105);
  if (crossing === null) {
    throw new Error('M4 120/105 pair does not change gap sign');
  }
  const loose105_60 = linearZero(p105.cnnc_deg, gap105, p60.cnnc_deg, gap60);
  if (loose105_60 === null) {
    throw new Error('M4 105/60 pair does not change gap sign');
  }

  const m4NeighborZeros = deriveNeighborZeros(points, step);
  if (m4NeighborZeros.length !== 1) {
    throw new Error(`M4 must have exactly one both-converged neighbour zero, got ${m4NeighborZeros.length}`);
  }
  if (m4NeighborZeros[0].hi !== 120 || m4NeighborZeros[0].lo !== 105) {
    throw new Error('M4 neighbour zero must be the 120/105 pair');
  }
  assertClose(m4NeighborZeros[0].deg, crossing, 'M4 derived neighbour zero');

  const m0Zeros = deriveNeighborZeros(m0.points, step);
  const m0Upper = requirePair(m0Zeros, 120, 105, 'M0');
  const m0Lower = requirePair(m0Zeros, 75, 60, 'M0');
  const m0CisA = requirePair(m0Zeros, 30, 15, 'M0');
  const m0CisB = requirePair(m0Zeros, 15, 0, 'M0');
  if (m0Zeros.length !== 4) {
    throw new Error(`M0: expected 4 both-converged neighbour zeros, got ${m0Zeros.length}`);
  }
  assertClose(oneDecimal(m0Upper), 115.5, 'M0 120/105 1dp');
  assertClose(oneDecimal(m0Lower), 65.6, 'M0 75/60 1dp');
  assertClose(oneDecimal(m0CisA), 27.8, 'M0 30/15 1dp');
  assertClose(oneDecimal(m0CisB), 8.8, 'M0 15/0 1dp');

  const m1Zeros = deriveNeighborZeros(m1.points, step);
  const m1Upper = requirePair(m1Zeros, 120, 105, 'M1');
  if (m1Zeros.length !== 1) {
    throw new Error(`M1: expected one both-converged neighbour zero, got ${m1Zeros.length}`);
  }
  if (m1Zeros.some((z) => z.deg > 70 && z.deg < 85)) {
    throw new Error('M1 76.5° must not be a derived both-converged zero');
  }
  assertClose(oneDecimal(m1Upper), 115.7, 'M1 120/105 1dp');
  assertClose(m1.loose_interpolant_deg, 76.5, 'M1 loose interpolant');

  const m2Zeros = deriveNeighborZeros(m2.points, step);
  if (m2Zeros.length !== 0) {
    throw new Error(`M2: expected no both-converged neighbour zeros, got ${m2Zeros.length}`);
  }
  const m2p120 = pointAt(m2.points, 120, 'M2');
  const m2p105 = pointAt(m2.points, 105, 'M2');
  if (!bothConverged(m2p120) || !bothConverged(m2p105)) {
    throw new Error('M2 120/105 must be both-converged');
  }
  const m2Gap120 = gapOf(m2p120);
  const m2Gap105 = gapOf(m2p105);
  if (m2Gap120 * m2Gap105 > 0 === false) {
    throw new Error('M2 120/105 gaps must share a sign');
  }
  const m2Unconverged = m2.points.filter((p) => !bothConverged(p)).map((p) => p.cnnc_deg);
  if (JSON.stringify(m2Unconverged) !== JSON.stringify(m2.s0_unconverged_deg)) {
    throw new Error('M2 s0_unconverged_deg does not match both_converged=false points');
  }

  const m3Zeros = deriveNeighborZeros(m3.points, step);
  const m3Upper = requirePair(m3Zeros, 120, 105, 'M3');
  const m3Lower = requirePair(m3Zeros, 75, 60, 'M3');
  if (m3Zeros.length !== 2) {
    throw new Error(`M3: expected 2 both-converged neighbour zeros, got ${m3Zeros.length}`);
  }
  assertClose(oneDecimal(m3Upper), 115.6, 'M3 120/105 1dp');
  assertClose(oneDecimal(m3Lower), 68.5, 'M3 75/60 1dp');
  for (const deg of m3.t1_failed_deg) {
    if (bothConverged(pointAt(m3.points, deg, 'M3'))) {
      throw new Error(`M3 ${deg}° is marked T1-failed but both-converged`);
    }
  }

  const m0Parsed = validateGridCsv(m0Csv, m0.points, 'M0');
  const m1Parsed = validateGridCsv(m1Csv, m1.points, 'M1');
  const m2Parsed = validateGridCsv(m2Csv, m2.points, 'M2');
  const m3Parsed = validateGridCsv(m3Csv, m3.points, 'M3');
  requireHeaders(m0Csv, m0Parsed.headers,
    ['cnnc_deg', 's0_rel_kjmol', 't1_rel_kjmol', 'both_converged', 'gap_kjmol']);
  requireHeaders(m1Csv, m1Parsed.headers,
    ['cnnc_deg', 's0_rel_kjmol', 't1_rel_kjmol', 'both_converged', 'gap_kjmol']);
  requireHeaders(m2Csv, m2Parsed.headers,
    ['cnnc_deg', 's0_rel_kjmol', 't1_rel_kjmol', 'both_converged', 'gap_kjmol']);
  requireHeaders(m3Csv, m3Parsed.headers,
    ['cnnc_deg', 's0_rel_kjmol', 't1_rel_kjmol', 'both_converged', 'gap_kjmol']);

  const m4Parsed = validateGridCsv(m4Csv, points, 'M4');
  requireHeaders(m4Csv, m4Parsed.headers, [
    'cnnc_deg', 's0_rel_kjmol', 't1_rel_kjmol', 's0_converged', 't1_converged',
    'gap_kjmol', 's0_eh', 'note',
  ]);
  for (const deg of [30, 15, 0]) {
    const row = m4Parsed.rows.find((r) => r.cnnc_deg === String(deg));
    const point = pointAt(points, deg, 'M4');
    if (row.s0_rel_kjmol !== '' || row.gap_kjmol !== '' || row.s0_eh !== '') {
      throw new Error(`m4_summary.csv ${deg}: S0 fields must be blank`);
    }
    if (row.s0_converged !== 'false' || row.t1_converged !== 'true') {
      throw new Error(`m4_summary.csv ${deg}: S0 not-run / T1 converged flags`);
    }
    const fromEh = (point.t1_eh - m4.trans_s0_eh) * result.eh_to_kjmol;
    assertClose(fromEh, point.t1_rel_kjmol, `M4 T1 ${deg} rel from Eh`, 0.005);
  }

  const { rows: controlRows } = parseCsv(controlsCsv);
  const c0 = controlRows.find((r) => r.molecule === 'M0');
  const c1 = controlRows.find((r) => r.molecule === 'M1');
  const c2 = controlRows.find((r) => r.molecule === 'M2');
  const c3 = controlRows.find((r) => r.molecule === 'M3');
  assertClose(Number(c0.crossing_upper_deg), oneDecimal(m0Upper), 'controls M0 upper');
  assertClose(Number(c0.crossing_lower_deg), oneDecimal(m0Lower), 'controls M0 lower');
  if (c0.cis_side_zeros_deg !== `${oneDecimal(m0CisA)};${oneDecimal(m0CisB)}`) {
    throw new Error(`controls M0 cis-side zeros: ${c0.cis_side_zeros_deg}`);
  }
  assertClose(Number(c1.crossing_upper_deg), oneDecimal(m1Upper), 'controls M1 upper');
  assertClose(Number(c1.crossing_lower_deg), m1.loose_interpolant_deg, 'controls M1 loose interpolant');
  assertClose(Number(c3.crossing_upper_deg), oneDecimal(m3Upper), 'controls M3 upper');
  assertClose(Number(c3.crossing_lower_deg), oneDecimal(m3Lower), 'controls M3 lower');
  assertClose(Number(c2.gap_120_kjmol), m2Gap120, 'controls M2 gap 120', 0.005);
  assertClose(Number(c2.gap_105_kjmol), m2Gap105, 'controls M2 gap 105', 0.005);

  const metrics = {
    m4_crossing_deg: num(crossing, 1,
      'Linear zero of the M4 S0−T1 gap between both-converged 120° and 105°',
      'deg'),
    m4_gap_120: num(gap120, 2,
      'M4 S0−T1 gap at CNNC 120°, both-converged',
      'kJ/mol'),
    m4_gap_105: num(gap105, 2,
      'M4 S0−T1 gap at CNNC 105°, both-converged',
      'kJ/mol'),
    m4_gap_60: num(gap60, 2,
      'M4 S0−T1 gap at CNNC 60°, both-converged after the 2026-08-22 reconvergence',
      'kJ/mol'),
    m2_gap_120: num(m2Gap120, 2,
      'M2 S0−T1 gap at CNNC 120°, both-converged',
      'kJ/mol'),
    m2_gap_105: num(m2Gap105, 2,
      'M2 S0−T1 gap at CNNC 105°, both-converged',
      'kJ/mol'),
    m0_crossing_upper_deg: num(m0Upper, 1,
      'M0 trans-side both-converged S0/T1 crossing from the 120°/105° neighbour pair',
      'deg'),
    m0_crossing_lower_deg: num(m0Lower, 1,
      'M0 cis-side both-converged S0/T1 crossing from the 75°/60° neighbour pair',
      'deg'),
    m0_cis_zero_a_deg: num(m0CisA, 1,
      'M0 additional both-converged zero on the cis-side continuation (30°/15°)',
      'deg'),
    m0_cis_zero_b_deg: num(m0CisB, 1,
      'M0 second additional both-converged zero on the cis-side continuation (15°/0°)',
      'deg'),
    m1_crossing_upper_deg: num(m1Upper, 1,
      'M1 trans-side both-converged S0/T1 crossing from the 120°/105° neighbour pair',
      'deg'),
    m1_crossing_lower_deg: num(m1.loose_interpolant_deg, 1,
      'M1 loose interpolant using a 45° bracket; S0 at 90° and 75° did not converge; not a both-converged neighbour zero',
      'deg'),
    m3_crossing_upper_deg: num(m3Upper, 1,
      'M3 trans-side both-converged S0/T1 crossing from the 120°/105° neighbour pair',
      'deg'),
    m3_crossing_lower_deg: num(m3Lower, 1,
      'M3 cis-side both-converged S0/T1 crossing from the 75°/60° neighbour pair',
      'deg'),
    m4_loose_105_60_zero_deg: num(loose105_60, 1,
      'Linear zero of the M4 gap between both-converged 105° and 60°; not a tight crossing (90/75 unconverged)',
      'deg'),
    m4_s0_60_eh: raw(m4.s0_60_eh,
      'M4 RKS S0 electronic energy at CNNC 60° after the 2026-08-22 reconvergence',
      'Eh'),
    m4_s0_rel_180: num(pointAt(points, 180, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 180° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_180: num(pointAt(points, 180, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 180° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_165: num(pointAt(points, 165, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 165° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_165: num(pointAt(points, 165, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 165° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_150: num(pointAt(points, 150, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 150° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_150: num(pointAt(points, 150, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 150° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_135: num(pointAt(points, 135, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 135° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_135: num(pointAt(points, 135, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 135° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_120: num(p120.s0_rel_kjmol, 2,
      'M4 S0 energy at 120° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_120: num(p120.t1_rel_kjmol, 2,
      'M4 T1 energy at 120° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_105: num(p105.s0_rel_kjmol, 2,
      'M4 S0 energy at 105° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_105: num(p105.t1_rel_kjmol, 2,
      'M4 T1 energy at 105° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_90: num(pointAt(points, 90, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 90° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_90: num(pointAt(points, 90, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 90° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_75: num(pointAt(points, 75, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 75° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_75: num(pointAt(points, 75, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 75° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_60: num(p60.s0_rel_kjmol, 2,
      'M4 S0 energy at 60° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_60: num(p60.t1_rel_kjmol, 2,
      'M4 T1 energy at 60° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_45: num(pointAt(points, 45, 'M4').s0_rel_kjmol, 2,
      'M4 S0 energy at 45° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_45: num(pointAt(points, 45, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 45° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_30: num(pointAt(points, 30, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 30° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_15: num(pointAt(points, 15, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 15° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_0: num(pointAt(points, 0, 'M4').t1_rel_kjmol, 2,
      'M4 T1 energy at 0° relative to trans-S0', 'kJ/mol'),
    m4_rerun_90_delta_e: num(m4.reruns['90'].delta_e_kjmol, 3,
      'M4 S0 90° reconvergence energy change versus the first unconverged point',
      'kJ/mol'),
    m4_rerun_75_drop: num(m4.reruns['75'].dropped_kjmol, 2,
      'M4 S0 75° reconvergence energy drop versus the first unconverged point',
      'kJ/mol'),
    m4_rerun_75_gap: num(m4.reruns['75'].gap_kjmol, 2,
      'M4 S0−T1 gap at 75° after the still-unconverged S0 rerun',
      'kJ/mol'),
    m4_t1_converged_count: integer(points.filter((p) => p.t1_converged).length,
      'M4 T1 points that converged on the 15° grid',
      'points'),
    m4_s0_unconverged_count: integer(points.filter((p) =>
      p.s0_converged === false && p.s0_not_run !== true && typeof p.s0_rel_kjmol === 'number').length,
      'M4 S0 points that were run and did not converge',
      'points'),
    m4_s0_not_run_count: integer(m4.s0_not_run_deg.length,
      'M4 S0 points that were not run after the cis-side cut',
      'points'),
    m2_crossing_count: integer(m2Zeros.length,
      'Number of both-converged S0/T1 crossings on the M2 grid',
      'crossings'),
    m4_has_claim_crossing: boolean(crossing !== null,
      'Whether M4 has a both-converged S0/T1 sign change between 120° and 105°'),
  };

  return {
    schema_version: 1,
    experiment: 'hillel-triplet',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [
        { path: resultInput, sha256: sha256(resultInput) },
        { path: m0Csv, sha256: sha256(m0Csv) },
        { path: m1Csv, sha256: sha256(m1Csv) },
        { path: m2Csv, sha256: sha256(m2Csv) },
        { path: m3Csv, sha256: sha256(m3Csv) },
        { path: m4Csv, sha256: sha256(m4Csv) },
        { path: controlsCsv, sha256: sha256(controlsCsv) },
      ],
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
