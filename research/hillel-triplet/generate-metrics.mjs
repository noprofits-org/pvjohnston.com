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
  throw new Error(`M4 point at ${point.cnnc_deg}° has no gap`);
}

function bothConverged(point) {
  return point.s0_converged === true && point.t1_converged === true;
}

function pointAt(points, deg) {
  const found = points.find((p) => p.cnnc_deg === deg);
  if (!found) throw new Error(`missing M4 point at ${deg}°`);
  return found;
}

function parseCsv(path) {
  const text = readFileSync(resolve(root, path), 'utf8').trim();
  const [headerLine, ...lines] = text.split('\n');
  const headers = headerLine.split(',');
  return lines.map((line) => {
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
    const row = {};
    headers.forEach((h, i) => { row[h] = cells[i] ?? ''; });
    return row;
  });
}

function assertClose(actual, expected, label, tol = 1e-9) {
  if (Math.abs(actual - expected) > tol) {
    throw new Error(`${label}: ${actual} !== ${expected}`);
  }
}

function build(generatedAt) {
  const result = JSON.parse(readFileSync(resolve(root, resultInput), 'utf8'));
  if (result.experiment !== 'hillel-triplet') {
    throw new Error(`${resultInput}: experiment must be hillel-triplet`);
  }
  if (result.eh_to_kjmol !== 2625.4996) {
    throw new Error(`${resultInput}: eh_to_kjmol must be 2625.4996`);
  }

  const m4 = result.molecules.M4;
  const m2 = result.molecules.M2;
  const m0 = result.molecules.M0;
  const m1 = result.molecules.M1;
  const m3 = result.molecules.M3;
  const points = m4.points;

  const p120 = pointAt(points, 120);
  const p105 = pointAt(points, 105);
  const p60 = pointAt(points, 60);
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

  if (m2.crossings_deg.length !== 0) {
    throw new Error('M2 crossings_deg must be empty');
  }
  if (m2.gaps_kjmol['120'] * m2.gaps_kjmol['105'] > 0 === false) {
    throw new Error('M2 120/105 gaps must share a sign');
  }

  const m4CsvRows = parseCsv(m4Csv);
  const csv120 = m4CsvRows.find((r) => r.cnnc_deg === '120');
  const csv105 = m4CsvRows.find((r) => r.cnnc_deg === '105');
  const csv60 = m4CsvRows.find((r) => r.cnnc_deg === '60');
  assertClose(Number(csv120.gap_kjmol), gap120, 'm4_summary.csv 120 gap');
  assertClose(Number(csv105.gap_kjmol), gap105, 'm4_summary.csv 105 gap');
  assertClose(Number(csv60.gap_kjmol), gap60, 'm4_summary.csv 60 gap');
  assertClose(Number(csv60.s0_eh), m4.s0_60_eh, 'm4_summary.csv 60 Eh');

  const controlRows = parseCsv(controlsCsv);
  const c0 = controlRows.find((r) => r.molecule === 'M0');
  const c1 = controlRows.find((r) => r.molecule === 'M1');
  const c2 = controlRows.find((r) => r.molecule === 'M2');
  const c3 = controlRows.find((r) => r.molecule === 'M3');
  assertClose(Number(c0.crossing_upper_deg), m0.crossings_deg[0], 'M0 upper');
  assertClose(Number(c0.crossing_lower_deg), m0.crossings_deg[1], 'M0 lower');
  assertClose(Number(c1.crossing_upper_deg), m1.crossings_deg[0], 'M1 upper');
  assertClose(Number(c1.crossing_lower_deg), m1.crossings_deg[1], 'M1 lower');
  assertClose(Number(c3.crossing_upper_deg), m3.crossings_deg[0], 'M3 upper');
  assertClose(Number(c3.crossing_lower_deg), m3.crossings_deg[1], 'M3 lower');
  assertClose(Number(c2.gap_120_kjmol), m2.gaps_kjmol['120'], 'M2 gap 120');
  assertClose(Number(c2.gap_105_kjmol), m2.gaps_kjmol['105'], 'M2 gap 105');

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
    m2_gap_120: num(m2.gaps_kjmol['120'], 2,
      'M2 S0−T1 gap at CNNC 120°, both-converged',
      'kJ/mol'),
    m2_gap_105: num(m2.gaps_kjmol['105'], 2,
      'M2 S0−T1 gap at CNNC 105°, both-converged',
      'kJ/mol'),
    m0_crossing_upper_deg: num(m0.crossings_deg[0], 1,
      'M0 trans-side both-converged S0/T1 crossing',
      'deg'),
    m0_crossing_lower_deg: num(m0.crossings_deg[1], 1,
      'M0 cis-side both-converged S0/T1 crossing',
      'deg'),
    m0_cis_zero_a_deg: num(m0.cis_side_zeros_deg[0], 1,
      'M0 additional both-converged zero on the cis-side continuation',
      'deg'),
    m0_cis_zero_b_deg: num(m0.cis_side_zeros_deg[1], 1,
      'M0 second additional both-converged zero on the cis-side continuation',
      'deg'),
    m1_crossing_upper_deg: num(m1.crossings_deg[0], 1,
      'M1 trans-side both-converged S0/T1 crossing',
      'deg'),
    m1_crossing_lower_deg: num(m1.crossings_deg[1], 1,
      'M1 cis-side both-converged S0/T1 crossing (45° bracket; S0 90/75 unconverged)',
      'deg'),
    m3_crossing_upper_deg: num(m3.crossings_deg[0], 1,
      'M3 trans-side both-converged S0/T1 crossing',
      'deg'),
    m3_crossing_lower_deg: num(m3.crossings_deg[1], 1,
      'M3 cis-side both-converged S0/T1 crossing',
      'deg'),
    m4_loose_105_60_zero_deg: num(loose105_60, 1,
      'Linear zero of the M4 gap between both-converged 105° and 60°; not a tight crossing (90/75 unconverged)',
      'deg'),
    m4_s0_60_eh: raw(m4.s0_60_eh,
      'M4 RKS S0 electronic energy at CNNC 60° after the 2026-08-22 reconvergence',
      'Eh'),
    m4_s0_rel_180: num(pointAt(points, 180).s0_rel_kjmol, 2,
      'M4 S0 energy at 180° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_180: num(pointAt(points, 180).t1_rel_kjmol, 2,
      'M4 T1 energy at 180° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_165: num(pointAt(points, 165).s0_rel_kjmol, 2,
      'M4 S0 energy at 165° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_165: num(pointAt(points, 165).t1_rel_kjmol, 2,
      'M4 T1 energy at 165° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_150: num(pointAt(points, 150).s0_rel_kjmol, 2,
      'M4 S0 energy at 150° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_150: num(pointAt(points, 150).t1_rel_kjmol, 2,
      'M4 T1 energy at 150° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_135: num(pointAt(points, 135).s0_rel_kjmol, 2,
      'M4 S0 energy at 135° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_135: num(pointAt(points, 135).t1_rel_kjmol, 2,
      'M4 T1 energy at 135° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_120: num(p120.s0_rel_kjmol, 2,
      'M4 S0 energy at 120° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_120: num(p120.t1_rel_kjmol, 2,
      'M4 T1 energy at 120° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_105: num(p105.s0_rel_kjmol, 2,
      'M4 S0 energy at 105° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_105: num(p105.t1_rel_kjmol, 2,
      'M4 T1 energy at 105° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_90: num(pointAt(points, 90).s0_rel_kjmol, 2,
      'M4 S0 energy at 90° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_90: num(pointAt(points, 90).t1_rel_kjmol, 2,
      'M4 T1 energy at 90° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_75: num(pointAt(points, 75).s0_rel_kjmol, 2,
      'M4 S0 energy at 75° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_75: num(pointAt(points, 75).t1_rel_kjmol, 2,
      'M4 T1 energy at 75° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_60: num(p60.s0_rel_kjmol, 2,
      'M4 S0 energy at 60° relative to trans-S0', 'kJ/mol'),
    m4_t1_rel_60: num(p60.t1_rel_kjmol, 2,
      'M4 T1 energy at 60° relative to trans-S0', 'kJ/mol'),
    m4_s0_rel_45: num(pointAt(points, 45).s0_rel_kjmol, 2,
      'M4 S0 energy at 45° relative to trans-S0 (unconverged upper bound)', 'kJ/mol'),
    m4_t1_rel_45: num(pointAt(points, 45).t1_rel_kjmol, 2,
      'M4 T1 energy at 45° relative to trans-S0', 'kJ/mol'),
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
    m4_s0_unconverged_count: integer(points.filter((p) => p.s0_converged === false).length,
      'M4 S0 points that were run and did not converge',
      'points'),
    m4_s0_not_run_count: integer(m4.s0_not_run_deg.length,
      'M4 S0 points that were not run after the cis-side cut',
      'points'),
    m2_crossing_count: integer(m2.crossings_deg.length,
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
