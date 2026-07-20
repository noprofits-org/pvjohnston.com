#!/usr/bin/env node

// Project the canonical Debye output into typed, deterministically formatted
// values used by the accompanying post. Check mode also reruns the cheap
// standard-library calculation before comparing metrics byte for byte.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const resultsPath = resolve(experimentDir, 'results.json');
const metricsPath = resolve(experimentDir, 'metrics.json');
const calculationPath = resolve(experimentDir, 'calculate.py');
const arguments_ = process.argv.slice(2);
const checkOnly = arguments_.length === 1 && arguments_[0] === '--check';

if (!(arguments_.length === 0 || checkOnly)) {
  console.error('usage: node research/microwave-debye-relaxation/generate-metrics.mjs [--check]');
  process.exit(2);
}

if (checkOnly) {
  const calculation = spawnSync('python3', [calculationPath, '--check'], {
    cwd: root,
    encoding: 'utf8',
    timeout: 10_000,
  });
  if (calculation.error || calculation.status !== 0) {
    const detail = calculation.error?.message || calculation.stderr || calculation.stdout;
    console.error(`end-to-end calculation check failed${detail ? `: ${detail.trim()}` : ''}`);
    process.exit(1);
  }
}

if (!existsSync(resultsPath)) {
  console.error('results.json is missing; run calculate.py first');
  process.exit(1);
}

const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
const fixed = (digits) => ({ style: 'fixed', digits });
const scientific = (digits) => ({ style: 'scientific', digits });

function numberMetric(value, format, description, unit) {
  return { type: 'number', value, format, description, ...(unit ? { unit } : {}) };
}

function integerMetric(value, description, unit) {
  return { type: 'integer', value, description, ...(unit ? { unit } : {}) };
}

function booleanMetric(value, description) {
  return { type: 'boolean', value, description };
}

function sha256(repositoryPath) {
  return createHash('sha256').update(readFileSync(resolve(root, repositoryPath))).digest('hex');
}

function buildMetrics(generatedAt) {
  const constants = results.model.constants;
  const conditions = results.model.conditions;
  const frequencies = results.model.evaluation_frequencies_hz;
  const water = results.model.materials.liquid_water_25_c;
  const ice = results.model.materials.ice_minus_10_c;
  const derivedIce = results.derived_parameters.ice_minus_10_c;
  const rows = results.liquid_water.evaluations;
  const water0915 = rows.industrial_ism_915_mhz;
  const water245 = rows.microwave_oven_245_ghz;
  const waterDielectricLossPeak = rows.dielectric_loss_factor_peak;
  const water60 = rows.high_frequency_60_ghz;
  const ice245 = results.microwave_oven_comparison.ice;
  const energy = results.photon_thermal_comparison;
  const comparison = results.microwave_oven_comparison;

  const metrics = {
    water_temperature_c: integerMetric(
      water.temperature_c,
      'Temperature assigned to the liquid-water Debye parameters',
      '°C',
    ),
    ice_temperature_c: integerMetric(
      ice.temperature_c,
      'Temperature assigned to the ice Debye parameters',
      '°C',
    ),
    room_temperature_k: numberMetric(
      conditions.room_temperature_k,
      fixed(2),
      'Temperature used for the kBT comparison',
      'K',
    ),
    water_static_relative_permittivity: numberMetric(
      water.static_relative_permittivity,
      fixed(1),
      'Selected static relative permittivity of liquid water',
      'relative permittivity',
    ),
    water_high_frequency_relative_permittivity: numberMetric(
      water.high_frequency_relative_permittivity,
      fixed(1),
      'Selected effective one-pole background relative permittivity of liquid water',
      'relative permittivity',
    ),
    water_relaxation_time_ps: numberMetric(
      water.relaxation_time_s * 1e12,
      fixed(1),
      'Selected liquid-water relaxation time',
      'ps',
    ),
    ice_static_relative_permittivity: numberMetric(
      ice.static_relative_permittivity,
      fixed(1),
      'Selected approximate static relative permittivity of ice',
      'relative permittivity',
    ),
    ice_high_frequency_relative_permittivity: numberMetric(
      ice.high_frequency_relative_permittivity,
      fixed(1),
      'Selected approximate high-frequency relative permittivity of ice',
      'relative permittivity',
    ),
    ice_relaxation_frequency_khz: numberMetric(
      ice.relaxation_frequency_hz / 1e3,
      fixed(2),
      'Selected dielectric relaxation frequency of ice at minus 10 degrees Celsius',
      'kHz',
    ),
    ice_relaxation_time_s: numberMetric(
      derivedIce.relaxation_time_s,
      scientific(2),
      'Ice relaxation time derived from the selected relaxation frequency',
      's',
    ),
    industrial_frequency_mhz: numberMetric(
      frequencies.industrial_ism / 1e6,
      fixed(0),
      'Selected industrial ISM evaluation frequency',
      'MHz',
    ),
    oven_frequency_ghz: numberMetric(
      frequencies.microwave_oven_ism / 1e9,
      fixed(2),
      'Selected kitchen-microwave ISM evaluation frequency',
      'GHz',
    ),
    high_evaluation_frequency_ghz: numberMetric(
      frequencies.high_frequency_evaluation / 1e9,
      fixed(0),
      'Selected single-Debye extrapolation frequency above the liquid-water dielectric-loss-factor peak',
      'GHz',
    ),
    speed_of_light_m_per_s: integerMetric(
      constants.speed_of_light_m_per_s,
      'Speed of light used by the attenuation calculation',
      'm/s',
    ),
    planck_constant_j_s: numberMetric(
      constants.planck_constant_j_s,
      scientific(8),
      'Planck constant used by the photon-energy comparison',
      'J s',
    ),
    elementary_charge_c: numberMetric(
      constants.elementary_charge_c,
      scientific(8),
      'Elementary charge used to convert joules to electronvolts',
      'C',
    ),
    boltzmann_constant_j_per_k: numberMetric(
      constants.boltzmann_constant_j_per_k,
      scientific(6),
      'Boltzmann constant used by the thermal-energy comparison',
      'J/K',
    ),
    water_dielectric_loss_peak_frequency_ghz: numberMetric(
      results.liquid_water.dielectric_loss_factor_peak_frequency_hz / 1e9,
      fixed(1),
      'Frequency of the liquid-water Debye dielectric-loss-factor maximum',
      'GHz',
    ),
    photon_energy_microev: numberMetric(
      energy.photon_energy_microelectronvolt,
      fixed(0),
      'Photon energy at the selected oven frequency',
      'μeV',
    ),
    thermal_energy_mev: numberMetric(
      energy.thermal_energy_millielectronvolt,
      fixed(1),
      'kBT at the selected room temperature',
      'meV',
    ),
    photon_to_thermal_energy_ratio: numberMetric(
      energy.photon_to_thermal_energy_ratio,
      scientific(1),
      'Photon energy divided by kBT at the selected oven frequency and temperature',
      'ratio',
    ),
    thermal_to_photon_energy_ratio: numberMetric(
      energy.thermal_to_photon_energy_ratio,
      scientific(1),
      'kBT divided by photon energy at the selected oven frequency and temperature',
      'ratio',
    ),
    photon_energy_orders_below_kbt: numberMetric(
      energy.photon_energy_orders_below_thermal,
      fixed(1),
      'Base-10 orders by which photon energy is below kBT',
      'orders of magnitude',
    ),
    ice_to_water_relaxation_ratio: numberMetric(
      comparison.ice_to_water_relaxation_time_ratio,
      scientific(1),
      'Ice relaxation time divided by liquid-water relaxation time',
      'ratio',
    ),
    ice_to_water_relaxation_orders: numberMetric(
      comparison.relaxation_time_order_difference,
      fixed(1),
      'Base-10 orders separating the selected ice and water relaxation times',
      'orders of magnitude',
    ),
    water_oven_loss_angle_deg: numberMetric(
      water245.loss_angle_degrees,
      fixed(1),
      'Liquid-water dielectric loss angle at the oven frequency',
      'degrees',
    ),
    water_dielectric_loss_peak_penetration_depth_mm: numberMetric(
      waterDielectricLossPeak.power_penetration_depth_m * 1e3,
      fixed(1),
      'Liquid-water 1/e power penetration depth at the Debye dielectric-loss-factor peak',
      'mm',
    ),
    water_0915_frequency_ghz: numberMetric(
      water0915.frequency_hz / 1e9,
      fixed(3),
      'Display frequency for the 915 MHz liquid-water row',
      'GHz',
    ),
    water_0915_relative_permittivity_real: numberMetric(
      water0915.relative_permittivity_real,
      fixed(1),
      'Real relative permittivity of liquid water at 915 MHz',
      'relative permittivity',
    ),
    water_0915_relative_permittivity_loss: numberMetric(
      water0915.relative_permittivity_loss,
      fixed(1),
      'Loss relative permittivity of liquid water at 915 MHz',
      'relative permittivity',
    ),
    water_0915_loss_tangent: numberMetric(
      water0915.loss_tangent,
      fixed(3),
      'Loss tangent of liquid water at 915 MHz',
      'ratio',
    ),
    water_0915_penetration_depth_cm: numberMetric(
      water0915.power_penetration_depth_m * 100,
      fixed(1),
      'Liquid-water 1/e power penetration depth at 915 MHz',
      'cm',
    ),
    water_245_relative_permittivity_real: numberMetric(
      water245.relative_permittivity_real,
      fixed(1),
      'Real relative permittivity of liquid water at 2.45 GHz',
      'relative permittivity',
    ),
    water_245_relative_permittivity_loss: numberMetric(
      water245.relative_permittivity_loss,
      fixed(1),
      'Loss relative permittivity of liquid water at 2.45 GHz',
      'relative permittivity',
    ),
    water_245_loss_tangent: numberMetric(
      water245.loss_tangent,
      fixed(3),
      'Loss tangent of liquid water at 2.45 GHz',
      'ratio',
    ),
    water_245_penetration_depth_cm: numberMetric(
      water245.power_penetration_depth_m * 100,
      fixed(1),
      'Liquid-water 1/e power penetration depth at 2.45 GHz',
      'cm',
    ),
    water_dielectric_loss_peak_relative_permittivity_real: numberMetric(
      waterDielectricLossPeak.relative_permittivity_real,
      fixed(1),
      'Real relative permittivity of liquid water at its Debye dielectric-loss-factor peak',
      'relative permittivity',
    ),
    water_dielectric_loss_peak_relative_permittivity_loss: numberMetric(
      waterDielectricLossPeak.relative_permittivity_loss,
      fixed(1),
      'Loss relative permittivity of liquid water at its Debye dielectric-loss-factor peak',
      'relative permittivity',
    ),
    water_dielectric_loss_peak_loss_tangent: numberMetric(
      waterDielectricLossPeak.loss_tangent,
      fixed(3),
      'Loss tangent of liquid water at its Debye dielectric-loss-factor peak',
      'ratio',
    ),
    water_dielectric_loss_peak_penetration_depth_cm: numberMetric(
      waterDielectricLossPeak.power_penetration_depth_m * 100,
      fixed(2),
      'Liquid-water 1/e power penetration depth at its Debye dielectric-loss-factor peak',
      'cm',
    ),
    water_60_relative_permittivity_real: numberMetric(
      water60.relative_permittivity_real,
      fixed(1),
      'Real relative permittivity of liquid water at 60 GHz',
      'relative permittivity',
    ),
    water_60_relative_permittivity_loss: numberMetric(
      water60.relative_permittivity_loss,
      fixed(1),
      'Loss relative permittivity of liquid water at 60 GHz',
      'relative permittivity',
    ),
    water_60_loss_tangent: numberMetric(
      water60.loss_tangent,
      fixed(3),
      'Loss tangent of liquid water at 60 GHz',
      'ratio',
    ),
    water_60_penetration_depth_cm: numberMetric(
      water60.power_penetration_depth_m * 100,
      fixed(2),
      'Liquid-water 1/e power penetration depth at 60 GHz',
      'cm',
    ),
    ice_245_relative_permittivity_real: numberMetric(
      ice245.relative_permittivity_real,
      fixed(2),
      'Real relative permittivity of ice at 2.45 GHz',
      'relative permittivity',
    ),
    ice_245_relative_permittivity_loss: numberMetric(
      ice245.relative_permittivity_loss,
      scientific(2),
      'Loss relative permittivity of ice at 2.45 GHz',
      'relative permittivity',
    ),
    ice_245_loss_tangent: numberMetric(
      ice245.loss_tangent,
      scientific(0),
      'Loss tangent of ice at 2.45 GHz',
      'ratio',
    ),
    ice_245_penetration_depth_m: numberMetric(
      ice245.power_penetration_depth_m,
      fixed(0),
      'Ice 1/e power penetration depth at 2.45 GHz',
      'm',
    ),
    ice_245_omega_tau: numberMetric(
      ice245.omega_tau,
      scientific(2),
      'Dimensionless omega tau for ice at 2.45 GHz',
      'dimensionless',
    ),
    peak_condition_absolute_tolerance: numberMetric(
      results.criteria.dimensionless_absolute_tolerance,
      scientific(0),
      'Absolute tolerance used by the omega tau peak-condition check',
      'dimensionless',
    ),
    peak_loss_relative_tolerance: numberMetric(
      results.criteria.relative_tolerance,
      scientific(0),
      'Relative tolerance used by the peak-loss identity check',
      'fraction',
    ),
    water_dielectric_loss_peak_condition_within_tolerance: booleanMetric(
      results.checks.water_dielectric_loss_peak_condition_within_tolerance,
      'Whether the computed dielectric-loss-factor peak satisfies omega tau equals one within tolerance',
    ),
    water_dielectric_loss_peak_identity_within_tolerance: booleanMetric(
      results.checks.water_dielectric_loss_peak_identity_within_tolerance,
      'Whether dielectric loss at its peak equals half the dielectric strength within tolerance',
    ),
    water_oven_rows_match: booleanMetric(
      results.checks.water_oven_rows_match,
      'Whether independent liquid-water evaluations at 2.45 GHz match exactly',
    ),
    all_evaluations_physical: booleanMetric(
      results.checks.all_evaluations_physical,
      'Whether every evaluated row has finite, positive loss and attenuation quantities',
    ),
    ice_relaxation_slower_than_water: booleanMetric(
      results.checks.ice_relaxation_slower_than_water,
      'Whether the selected ice relaxation time exceeds the liquid-water value',
    ),
  };

  const inputPaths = [
    'research/microwave-debye-relaxation/inputs.json',
    'research/microwave-debye-relaxation/calculate.py',
    'research/microwave-debye-relaxation/results.json',
  ];
  return {
    schema_version: 1,
    experiment: 'microwave-debye-relaxation',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: inputPaths.map((path) => ({ path, sha256: sha256(path) })),
    },
    metrics,
  };
}

const existing = existsSync(metricsPath)
  ? JSON.parse(readFileSync(metricsPath, 'utf8'))
  : null;
const generatedAt = checkOnly && existing?.provenance?.generated_at
  ? existing.provenance.generated_at
  : new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const expected = `${JSON.stringify(buildMetrics(generatedAt), null, 2)}\n`;

if (checkOnly) {
  if (!existing) {
    console.error('metrics.json is missing; run the generator without --check');
    process.exit(1);
  }
  if (readFileSync(metricsPath, 'utf8') !== expected) {
    console.error('metrics.json is stale; rerun the generator');
    process.exit(1);
  }
  console.log('generate-metrics.mjs: metrics.json is current');
} else {
  writeFileSync(metricsPath, expected);
  console.log(`wrote ${relative(root, metricsPath)}`);
}
