#!/usr/bin/env node

// Publication metrics for the Johnson-haloacetate CX3 scan. Numbers are
// derived from the committed rematch and scan CSVs. Do not hand-author
// metrics.json.
//
// q_o_mbis is the arithmetic mean of the two carboxylate oxygen MBIS
// charges. q_coo_mbis is the carboxylate-group sum. This generator does
// not re-average raw per-atom charges; those atoms are not in the CSVs.
// Amplitude is max−min of the committed column. The signed 120°−0°
// difference is an overlay, not the amplitude.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const rematchCsv = 'research/johnson-haloacetate/rematch/summary.csv';
const m1Csv = 'research/johnson-haloacetate/results/m1_cf3_scan.csv';
const m3Csv = 'research/johnson-haloacetate/results/m3_ccl3_scan.csv';
const checkOnly = process.argv.includes('--check');

// Thermochemical conversion used for the published barriers and the
// 120°−0° overlay. Exposed as a metric so the post does not hard-code it.
const EH_TO_KCAL = 627.509474;

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

const num = (value, digits, description, unit, style = 'fixed') => ({
  type: 'number',
  value,
  format: { style, digits },
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

function parseCsv(path) {
  const text = readFileSync(resolve(root, path), 'utf8').trim();
  const [headerLine, ...lines] = text.split('\n');
  const headers = splitCsvLine(headerLine);
  return {
    headers,
    rows: lines.map((line, index) => {
      const cells = splitCsvLine(line);
      while (cells.length < headers.length) cells.push('');
      if (cells.length !== headers.length) {
        throw new Error(`${path}:${index + 2} has ${cells.length} fields, expected ${headers.length}`);
      }
      const row = {};
      headers.forEach((h, i) => { row[h] = cells[i] ?? ''; });
      return row;
    }),
  };
}

function requireHeaders(path, headers, expected) {
  if (headers.join(',') !== expected.join(',')) {
    throw new Error(`${path}: headers ${headers.join(',')} !== ${expected.join(',')}`);
  }
}

function assertClose(actual, expected, label, tol = 1e-12) {
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

function csvBool(value, label) {
  if (value === 'true') return true;
  if (value === 'false') return false;
  throw new Error(`${label}: expected true/false, got ${value}`);
}

function optionalNumber(value, label) {
  if (value === '') return null;
  const n = Number(value);
  return requireFinite(n, label);
}

function requireCsvNumber(value, label) {
  if (value === '' || value === undefined) {
    throw new Error(`${label}: empty`);
  }
  return requireFinite(Number(value), label);
}

function endpointMinus(a, b, field) {
  if (!a.both || !b.both || a[field] == null || b[field] == null) {
    return null;
  }
  return b[field] - a[field];
}

function peakToPeak(values, label) {
  if (values.length < 2) {
    throw new Error(`${label}: need ≥2 converged points for max−min`);
  }
  const max = Math.max(...values);
  const min = Math.min(...values);
  requireFinite(max, `${label} max`);
  requireFinite(min, `${label} min`);
  return max - min;
}

function mean(values, label) {
  if (values.length === 0) throw new Error(`${label}: empty series`);
  const sum = values.reduce((a, b) => a + b, 0);
  return requireFinite(sum / values.length, `${label} mean`);
}

function parseScan(path, ion) {
  const { headers, rows } = parseCsv(path);
  requireHeaders(path, headers, [
    'ion', 'angle', 'energy_eh', 'q_o_mbis', 'q_coo_mbis',
    'converged_optking', 'converged_exit',
  ]);
  const points = rows.map((row, index) => {
    if (row.ion !== ion) {
      throw new Error(`${path}:${index + 2}: ion ${row.ion} !== ${ion}`);
    }
    const angle = requireCsvNumber(row.angle, `${path} angle`);
    const optking = csvBool(row.converged_optking, `${path} ${angle} optking`);
    const exit = csvBool(row.converged_exit, `${path} ${angle} exit`);
    const both = optking && exit;
    // Number('') is 0. Failed rows may leave energy/charges blank;
    // do not coerce those cells into endpoint or amplitude numbers.
    const energy = both
      ? requireCsvNumber(row.energy_eh, `${path} ${angle} energy`)
      : optionalNumber(row.energy_eh, `${path} ${angle} energy`);
    const qO = both
      ? requireCsvNumber(row.q_o_mbis, `${path} ${angle} q_o`)
      : optionalNumber(row.q_o_mbis, `${path} ${angle} q_o`);
    const qCoo = both
      ? requireCsvNumber(row.q_coo_mbis, `${path} ${angle} q_coo`)
      : optionalNumber(row.q_coo_mbis, `${path} ${angle} q_coo`);
    return { angle, energy, qO, qCoo, optking, exit, both };
  });
  const sorted = [...points].sort((a, b) => a.angle - b.angle);
  for (let i = 0; i < sorted.length; i++) {
    if (sorted[i].angle !== i * 15) {
      throw new Error(`${path}: expected angle ${i * 15}, got ${sorted[i].angle}`);
    }
  }
  if (sorted.length !== 9) {
    throw new Error(`${path}: expected 9 points, got ${sorted.length}`);
  }
  return sorted;
}

function pointAt(points, angle, label) {
  const found = points.find((p) => p.angle === angle);
  if (!found) throw new Error(`${label}: missing angle ${angle}`);
  return found;
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
  requireFinite(EH_TO_KCAL, 'EH_TO_KCAL');

  const rematchParsed = parseCsv(rematchCsv);
  requireHeaders(rematchCsv, rematchParsed.headers, [
    'ion', 'formula', 'r_cc', 'delta_cx_oop_ip', 'q_o_mbis', 'q_coo_mbis',
    'q_o_lowdin', 'q_coo_lowdin', 'converged_optking', 'converged_exit',
  ]);
  if (rematchParsed.rows.length !== 4) {
    throw new Error(`${rematchCsv}: expected 4 ions, got ${rematchParsed.rows.length}`);
  }

  const rematch = {};
  for (const row of rematchParsed.rows) {
    const ion = row.ion;
    rematch[ion] = {
      formula: row.formula,
      rCc: requireFinite(Number(row.r_cc), `${ion} r_cc`),
      deltaCx: optionalNumber(row.delta_cx_oop_ip, `${ion} delta_cx`),
      qO: optionalNumber(row.q_o_mbis, `${ion} rematch q_o`),
      qCoo: optionalNumber(row.q_coo_mbis, `${ion} rematch q_coo`),
      qOLowdin: optionalNumber(row.q_o_lowdin, `${ion} rematch q_o_lowdin`),
      qCooLowdin: optionalNumber(row.q_coo_lowdin, `${ion} rematch q_coo_lowdin`),
      optking: csvBool(row.converged_optking, `${ion} rematch optking`),
      exit: csvBool(row.converged_exit, `${ion} rematch exit`),
    };
  }
  for (const ion of ['acetate', 'cf3', 'cclf2', 'ccl3']) {
    if (!rematch[ion]) throw new Error(`${rematchCsv}: missing ${ion}`);
    if (!rematch[ion].optking || !rematch[ion].exit) {
      throw new Error(`${ion} rematch did not converge`);
    }
  }
  if (rematch.acetate.deltaCx !== null || rematch.acetate.qO !== null
      || rematch.acetate.qCoo !== null) {
    throw new Error('acetate rematch must not invent Δ(C–X) or charges');
  }
  if (rematch.cclf2.deltaCx !== null || rematch.cclf2.qO !== null
      || rematch.cclf2.qCoo !== null) {
    throw new Error('CClF2 rematch Δ(C–X) is mixed; charges were not published');
  }
  if (rematch.cf3.deltaCx === null || rematch.ccl3.deltaCx === null) {
    throw new Error('CF3 and CCl3 rematch must have Δ(C–X)');
  }
  if (rematch.cf3.qO === null || rematch.ccl3.qO === null
      || rematch.cf3.qCoo === null || rematch.ccl3.qCoo === null) {
    throw new Error('CF3 and CCl3 rematch must have MBIS charges');
  }
  for (const ion of ['acetate', 'cf3', 'cclf2', 'ccl3']) {
    if (rematch[ion].qOLowdin === null || rematch[ion].qCooLowdin === null) {
      throw new Error(`${ion} rematch must have Löwdin charges`);
    }
  }

  // Frozen rematch r(C–C) gate: CCl3 > CF3 > acetate. CClF2 sitting
  // between them was observed after rematch and is a diagnostic only.
  const ccOrderPass = rematch.ccl3.rCc > rematch.cf3.rCc
    && rematch.cf3.rCc > rematch.acetate.rCc;
  const ccCclf2Between = rematch.cclf2.rCc > rematch.cf3.rCc
    && rematch.ccl3.rCc > rematch.cclf2.rCc;
  const deltaCxPass = rematch.ccl3.deltaCx > rematch.cf3.deltaCx;
  const rematchQoPass = rematch.cf3.qO < rematch.ccl3.qO;
  const rematchQcooPass = rematch.cf3.qCoo < rematch.ccl3.qCoo;
  const rematchQoLowdinPass = rematch.cf3.qOLowdin < rematch.ccl3.qOLowdin;
  const rematchQcooLowdinPass = rematch.cf3.qCooLowdin < rematch.ccl3.qCooLowdin;
  if (!ccOrderPass) throw new Error('rematch r(C–C) gate failed');
  if (!deltaCxPass) throw new Error('rematch Δ(C–X) gate failed');
  if (!rematchQoPass) throw new Error('rematch MBIS q(O) gate failed');
  if (!rematchQcooPass) throw new Error('rematch MBIS q(COO) gate failed');

  const m1 = parseScan(m1Csv, 'm1_cf3');
  const m3 = parseScan(m3Csv, 'm3_ccl3');
  const scanPoints = [...m1, ...m3];
  const nScan = scanPoints.length;
  const nConverged = scanPoints.filter((p) => p.both).length;
  if (nScan !== 18) throw new Error(`expected 18 scheduled scan points, got ${nScan}`);
  // Unconverged scheduled rows stay in the CSVs and are excluded from
  // max−min. Either ion failing any scheduled point is the registered
  // inconclusive outcome; do not refuse to project that case.
  const scanInconclusive = m1.some((p) => !p.both) || m3.some((p) => !p.both);

  const m1Converged = m1.filter((p) => p.both);
  const m3Converged = m3.filter((p) => p.both);
  const ampQoCf3 = peakToPeak(m1Converged.map((p) => p.qO), 'CF3 q(O)');
  const ampQoCcl3 = peakToPeak(m3Converged.map((p) => p.qO), 'CCl3 q(O)');
  const ampQcooCf3 = peakToPeak(m1Converged.map((p) => p.qCoo), 'CF3 q(COO)');
  const ampQcooCcl3 = peakToPeak(m3Converged.map((p) => p.qCoo), 'CCl3 q(COO)');
  const maxChargeAmp = Math.max(ampQoCf3, ampQoCcl3, ampQcooCf3, ampQcooCcl3);
  const maxQoAmp = Math.max(ampQoCf3, ampQoCcl3);

  const m1_0 = pointAt(m1, 0, 'CF3');
  const m1_120 = pointAt(m1, 120, 'CF3');
  const m3_0 = pointAt(m3, 0, 'CCl3');
  const m3_120 = pointAt(m3, 120, 'CCl3');
  const repeatQoCf3 = endpointMinus(m1_0, m1_120, 'qO');
  const repeatQcooCf3 = endpointMinus(m1_0, m1_120, 'qCoo');
  const repeatQoCcl3 = endpointMinus(m3_0, m3_120, 'qO');
  const repeatQcooCcl3 = endpointMinus(m3_0, m3_120, 'qCoo');
  const overlayEhCf3 = endpointMinus(m1_0, m1_120, 'energy');
  const overlayEhCcl3 = endpointMinus(m3_0, m3_120, 'energy');
  const overlayKcalCf3 = overlayEhCf3 == null ? null : overlayEhCf3 * EH_TO_KCAL;
  const overlayKcalCcl3 = overlayEhCcl3 == null ? null : overlayEhCcl3 * EH_TO_KCAL;
  const scanEndpointsConverged = [
    repeatQoCf3, repeatQcooCf3, repeatQoCcl3, repeatQcooCcl3,
    overlayEhCf3, overlayEhCcl3,
  ].every((value) => value != null);

  const barrierEhCf3 = peakToPeak(m1Converged.map((p) => p.energy), 'CF3 E');
  const barrierEhCcl3 = peakToPeak(m3Converged.map((p) => p.energy), 'CCl3 E');
  const barrierKcalCf3 = barrierEhCf3 * EH_TO_KCAL;
  const barrierKcalCcl3 = barrierEhCcl3 * EH_TO_KCAL;

  const meanQoCf3 = mean(m1Converged.map((p) => p.qO), 'CF3 mean q(O)');
  const meanQoCcl3 = mean(m3Converged.map((p) => p.qO), 'CCl3 mean q(O)');
  const meanQcooCf3 = mean(m1Converged.map((p) => p.qCoo), 'CF3 mean q(COO)');
  const meanQcooCcl3 = mean(m3Converged.map((p) => p.qCoo), 'CCl3 mean q(COO)');

  // Falsifier 2 is scored on q(O): hypothesis needs CCl3 amplitude > CF3.
  // A grid failure is inconclusive, not a silent supported/falsified call.
  const qoAmpCcl3GtCf3 = ampQoCcl3 > ampQoCf3;
  const qcooAmpCcl3GtCf3 = ampQcooCcl3 > ampQcooCf3;
  const hypothesisSupported = !scanInconclusive && qoAmpCcl3GtCf3;

  const metrics = {
    rematch_n_ions: integer(4, 'Number of rematch ions', 'ions'),
    rematch_n_converged: integer(
      Object.values(rematch).filter((r) => r.optking && r.exit).length,
      'Rematch optimizations that formally converged',
      'optimizations',
    ),
    r_cc_acetate: num(rematch.acetate.rCc, 5,
      'Rematch C–C bond length of CH3COO−', 'Å'),
    r_cc_cf3: num(rematch.cf3.rCc, 5,
      'Rematch C–C bond length of CF3COO−', 'Å'),
    r_cc_cclf2: num(rematch.cclf2.rCc, 5,
      'Rematch C–C bond length of CClF2COO−', 'Å'),
    r_cc_ccl3: num(rematch.ccl3.rCc, 5,
      'Rematch C–C bond length of CCl3COO−', 'Å'),
    delta_cx_cf3: num(rematch.cf3.deltaCx, 5,
      'Rematch out-of-plane minus in-plane C–X length for CF3COO−', 'Å'),
    delta_cx_ccl3: num(rematch.ccl3.deltaCx, 5,
      'Rematch out-of-plane minus in-plane C–X length for CCl3COO−', 'Å'),
    rematch_q_o_cf3: num(rematch.cf3.qO, 5,
      'Rematch MBIS q(O) of CF3COO−, arithmetic mean of the two carboxylate oxygens', 'e'),
    rematch_q_o_ccl3: num(rematch.ccl3.qO, 5,
      'Rematch MBIS q(O) of CCl3COO−, arithmetic mean of the two carboxylate oxygens', 'e'),
    rematch_q_coo_cf3: num(rematch.cf3.qCoo, 5,
      'Rematch MBIS carboxylate-group charge of CF3COO−', 'e'),
    rematch_q_coo_ccl3: num(rematch.ccl3.qCoo, 5,
      'Rematch MBIS carboxylate-group charge of CCl3COO−', 'e'),
    rematch_q_o_lowdin_cf3: num(rematch.cf3.qOLowdin, 5,
      'Rematch Löwdin q(O) of CF3COO−, arithmetic mean of the two carboxylate oxygens', 'e'),
    rematch_q_o_lowdin_ccl3: num(rematch.ccl3.qOLowdin, 5,
      'Rematch Löwdin q(O) of CCl3COO−, arithmetic mean of the two carboxylate oxygens', 'e'),
    rematch_q_coo_lowdin_cf3: num(rematch.cf3.qCooLowdin, 5,
      'Rematch Löwdin carboxylate-group charge of CF3COO−', 'e'),
    rematch_q_coo_lowdin_ccl3: num(rematch.ccl3.qCooLowdin, 5,
      'Rematch Löwdin carboxylate-group charge of CCl3COO−', 'e'),
    rematch_q_o_lowdin_pass: boolean(rematchQoLowdinPass,
      'Whether rematch Löwdin q(O) is more negative for CF3 than CCl3'),
    rematch_q_coo_lowdin_pass: boolean(rematchQcooLowdinPass,
      'Whether rematch Löwdin q(COO) is more negative for CF3 than CCl3'),
    rematch_cc_order_pass: boolean(ccOrderPass,
      'Whether rematch r(C–C) satisfies the frozen CCl3 > CF3 > acetate comparison'),
    rematch_cc_cclf2_between: boolean(ccCclf2Between,
      'Observed diagnostic: whether rematch r(C–C) places CClF2 between CF3 and CCl3'),
    rematch_delta_cx_pass: boolean(deltaCxPass,
      'Whether rematch Δ(C–X) satisfies CCl3 > CF3'),
    rematch_q_o_pass: boolean(rematchQoPass,
      'Whether rematch mean-of-two-oxygens MBIS q(O) is more negative for CF3 than CCl3'),
    rematch_q_coo_pass: boolean(rematchQcooPass,
      'Whether rematch MBIS q(COO) is more negative for CF3 than CCl3'),
    n_scan_points: integer(nScan, 'Scan points on the two 0–120° grids', 'points'),
    n_scan_converged: integer(nConverged,
      'Scan points with optking True and a clean exit; unconverged rows stay in the CSVs and are excluded from max−min',
      'points'),
    scan_inconclusive: boolean(scanInconclusive,
      'Registered inconclusive outcome: either ion failed to converge on at least one scheduled grid point'),
    scan_endpoints_converged: boolean(scanEndpointsConverged,
      'Whether both 0° and 120° points on both ions are both-converged with finite charges and energies'),
    scan_step_deg: integer(15, 'Frozen-dihedral step of the relaxed scan', 'deg'),
    eh_to_kcal: raw(EH_TO_KCAL,
      'Conversion used for scan barriers and the 120°−0° overlay',
      'kcal/mol/Eh'),
    amp_q_o_cf3: num(ampQoCf3, 6,
      'Peak-to-peak amplitude of mean-of-two-oxygens MBIS q(O) on both-converged CF3COO− points', 'e'),
    amp_q_o_ccl3: num(ampQoCcl3, 6,
      'Peak-to-peak amplitude of mean-of-two-oxygens MBIS q(O) on both-converged CCl3COO− points', 'e'),
    amp_q_coo_cf3: num(ampQcooCf3, 6,
      'MBIS q(COO) peak-to-peak amplitude on both-converged CF3COO− points', 'e'),
    amp_q_coo_ccl3: num(ampQcooCcl3, 6,
      'MBIS q(COO) peak-to-peak amplitude on both-converged CCl3COO− points', 'e'),
    max_charge_amp: num(maxChargeAmp, 6,
      'Largest of the four MBIS peak-to-peak amplitudes (q(O) and q(COO) on both ions)',
      'e'),
    max_q_o_amp: num(maxQoAmp, 6,
      'Largest of the two MBIS q(O) peak-to-peak amplitudes',
      'e'),
    barrier_eh_cf3: num(barrierEhCf3, 2,
      'CF3COO− electronic-energy range (max−min) on the both-converged scan',
      'Eh', 'scientific'),
    barrier_eh_ccl3: num(barrierEhCcl3, 2,
      'CCl3COO− electronic-energy range (max−min) on the both-converged scan',
      'Eh', 'scientific'),
    barrier_kcal_cf3: num(barrierKcalCf3, 3,
      'CF3COO− electronic-energy range converted with eh_to_kcal',
      'kcal/mol'),
    barrier_kcal_ccl3: num(barrierKcalCcl3, 3,
      'CCl3COO− electronic-energy range converted with eh_to_kcal',
      'kcal/mol'),
    mean_q_o_cf3: num(meanQoCf3, 3,
      'Mean MBIS q(O) on the both-converged CF3COO− scan', 'e'),
    mean_q_o_ccl3: num(meanQoCcl3, 3,
      'Mean MBIS q(O) on the both-converged CCl3COO− scan', 'e'),
    mean_q_coo_cf3: num(meanQcooCf3, 3,
      'Mean MBIS q(COO) on the both-converged CF3COO− scan', 'e'),
    mean_q_coo_ccl3: num(meanQcooCcl3, 3,
      'Mean MBIS q(COO) on the both-converged CCl3COO− scan', 'e'),
    q_o_amp_ccl3_gt_cf3: boolean(qoAmpCcl3GtCf3,
      'Whether the CCl3 q(O) amplitude is larger than the CF3 q(O) amplitude'),
    q_coo_amp_ccl3_gt_cf3: boolean(qcooAmpCcl3GtCf3,
      'Whether the CCl3 q(COO) amplitude is larger than the CF3 q(COO) amplitude'),
    hypothesis_supported: boolean(hypothesisSupported,
      'Whether the registered hypothesis is supported when falsifier 2 is scored on q(O) after the scan and the grid is not inconclusive'),
  };

  // The shared schema has no omitted/null metric form, and resolveMetric
  // treats a missing name as a hard build error. The post therefore does
  // not cite these keys. Emit them only from both-converged endpoints;
  // do not invent a number or coerce a failed overlay to 0.
  if (scanEndpointsConverged) {
    Object.assign(metrics, {
      repeat_q_o_cf3: num(repeatQoCf3, 2,
        'Signed CF3COO− MBIS q(O) difference, 120° minus 0°',
        'e', 'scientific'),
      repeat_q_coo_cf3: num(repeatQcooCf3, 2,
        'Signed CF3COO− MBIS q(COO) difference, 120° minus 0°',
        'e', 'scientific'),
      repeat_q_o_ccl3: num(repeatQoCcl3, 2,
        'Signed CCl3COO− MBIS q(O) difference, 120° minus 0°',
        'e', 'scientific'),
      repeat_q_coo_ccl3: num(repeatQcooCcl3, 2,
        'Signed CCl3COO− MBIS q(COO) difference, 120° minus 0°',
        'e', 'scientific'),
      overlay_kcal_cf3: num(overlayKcalCf3, 2,
        'CF3COO− E(120°)−E(0°) converted with eh_to_kcal',
        'kcal/mol', 'scientific'),
      overlay_kcal_ccl3: num(overlayKcalCcl3, 2,
        'CCl3COO− E(120°)−E(0°) converted with eh_to_kcal',
        'kcal/mol', 'scientific'),
      overlay_kcal_cf3_abs: num(Math.abs(overlayKcalCf3), 2,
        'Absolute CF3COO− E(120°)−E(0°) converted with eh_to_kcal',
        'kcal/mol', 'scientific'),
      overlay_kcal_ccl3_abs: num(Math.abs(overlayKcalCcl3), 2,
        'Absolute CCl3COO− E(120°)−E(0°) converted with eh_to_kcal',
        'kcal/mol', 'scientific'),
    });
  }

  for (const [name, metric] of Object.entries(metrics)) {
    if (metric.type === 'boolean') continue;
    if (!Number.isFinite(metric.value)) {
      throw new Error(`metric ${name} is not finite: ${metric.value}`);
    }
  }

  return {
    schema_version: 1,
    experiment: 'johnson-haloacetate',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [
        { path: rematchCsv, sha256: sha256(rematchCsv) },
        { path: m1Csv, sha256: sha256(m1Csv) },
        { path: m3Csv, sha256: sha256(m3Csv) },
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
