#!/usr/bin/env node

// Deterministic publication projection of the reviewed dual-lane analysis.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const input = 'research/coherence-hop-boundary/results/analysis.json';
const config = 'research/coherence-hop-boundary/config.json';
const inputPath = resolve(root, input);
const configPath = resolve(root, config);
const outputPath = resolve(experimentDir, 'metrics.json');
const checkOnly = process.argv.includes('--check');

const sha256 = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
const fixed = (value, digits, description, unit) => ({
  type: 'number', value, format: { style: 'fixed', digits }, description,
  ...(unit ? { unit } : {}),
});
const percent = (value, digits, description) => ({
  type: 'number', value, format: { style: 'percent', digits }, description, unit: 'ratio',
});
const scientific = (value, digits, description, unit) => ({
  type: 'number', value, format: { style: 'scientific', digits }, description,
  ...(unit ? { unit } : {}),
});
const integer = (value, description, unit) => ({
  type: 'integer', value, description, ...(unit ? { unit } : {}),
});
const boolean = (value, description) => ({ type: 'boolean', value, description });
const SCALE_SLUGS = new Map([
  [1, '1'], [0.5, '0_5'], [0.25, '0_25'], [0.125, '0_125'],
  [0.1, '0_10'], [0.075, '0_075'], [0.05, '0_05'],
]);

function addNumber(metrics, key, value, digits, description, unit) {
  if (value !== null && Number.isFinite(value)) metrics[key] = fixed(value, digits, description, unit);
}

function addPercent(metrics, key, value, digits, description) {
  if (value !== null && Number.isFinite(value)) metrics[key] = percent(value, digits, description);
}

function build() {
  const analysis = JSON.parse(readFileSync(inputPath, 'utf8'));
  const frozenConfig = JSON.parse(readFileSync(configPath, 'utf8'));
  const generatedAt = frozenConfig.corrective_amendment?.canonical_metrics_source_date_epoch_utc;
  if (!generatedAt) throw new Error('config is missing the canonical metrics source-date epoch');
  if (analysis.schema_version !== 2 || analysis.publication_status !== 'reframed_after_observable_correction') {
    throw new Error('analysis is not the reviewed schema-2 artifact');
  }
  if (!analysis.hypothesis.inconclusive || analysis.hypothesis.optical_coherence_claim_supported) {
    throw new Error('reviewed optical-coherence verdict must be unsupported and inconclusive');
  }

  const metrics = {};
  const convergence = analysis.convergence_gate;
  const legacyGate = analysis.legacy_convergence_gate;
  const legacy = analysis.legacy_local_magnitude_summary;
  const exact = analysis.exact_grid_gate;
  const regimes = analysis.regimes;

  metrics.optical_coherence_claim_supported = boolean(false,
    'Whether the archived production data support a phase-sensitive optical-coherence claim');
  metrics.corrective_hypothesis_inconclusive = boolean(true,
    'Whether the phase-sensitive corrective experiment is inconclusive');
  metrics.corrective_production_run = boolean(false,
    'Whether the 28-run phase-sensitive corrective production sweep was permitted');
  metrics.lineage_gate_passed = boolean(analysis.lineage_gate.passed,
    'Whether the refactored simulator reproduced the frozen ancestor under the lineage test');
  addNumber(metrics, 'lineage_max_observable_difference',
    analysis.lineage_gate.max_abs_observable_difference, 3,
    'Largest observable-array difference in the lineage comparison');

  metrics.corrective_convergence_passed = boolean(convergence.passed,
    'Whether the eight-paired-seed phase-sensitive fine/finer gate passed');
  metrics.corrective_convergence_seed_pairs = integer(8,
    'Paired seeds in the corrective fine/finer gate', 'seed pairs');
  const scalarNames = {
    early_hop_fraction: ['fraction', 4, 'ratio'],
    coherence_lifetime_fs: ['lifetime', 3, 'fs'],
  };
  for (const [key, [label, digits, unit]] of Object.entries(scalarNames)) {
    const interval = convergence.paired_scalar_95_intervals[key];
    addNumber(metrics, `corrective_${label}_95_max_endpoint`,
      interval.max_abs_interval_endpoint, digits,
      `Maximum absolute endpoint of the paired 95% interval for corrected ${label}`, unit);
  }
  const seriesNames = {
    full_upper_population: ['population', 'probability'],
    full_product_probability: ['product', 'probability'],
    full_centroid_x_sigma: ['centroid', 'initial sigma_x'],
  };
  for (const [key, [label, unit]] of Object.entries(seriesNames)) {
    const envelope = convergence.paired_time_series_95_envelopes[key];
    addNumber(metrics, `corrective_${label}_95_max_endpoint`,
      envelope.max_abs_interval_endpoint, 4,
      `Maximum absolute paired 95% interval endpoint for corrected ${label}`, unit);
    addNumber(metrics, `corrective_${label}_95_max_endpoint_time_fs`,
      envelope.time_fs_of_max_abs_interval_endpoint, 3,
      `Time of the maximum corrected ${label} interval endpoint`, 'fs');
  }
  addNumber(metrics, 'corrective_centroid_limit', convergence.tolerances.full_centroid_x_sigma,
    2, 'Registered centroid convergence limit', 'initial sigma_x');
  for (const [setting, outcome] of [
    ['candidate', convergence.candidate_pooled_outcome],
    ['reference', convergence.reference_pooled_outcome],
  ]) {
    addNumber(metrics, `corrective_${setting}_ensemble_lifetime_fs`,
      outcome.coherence_lifetime_fs, 3,
      `Pooled phase-sensitive ensemble-coherence lifetime for the ${setting} setting`, 'fs');
    addPercent(metrics, `corrective_${setting}_early_hop_fraction`,
      outcome.early_hop_fraction, 1,
      `Pooled accepted-event fraction before phase-sensitive ensemble coherence decays for the ${setting} setting`);
    metrics[`corrective_${setting}_majority`] = boolean(
      outcome.classifications.majority_early_hop,
      `Whether the ${setting} corrected convergence setting reaches the majority boundary`,
    );
  }

  metrics.legacy_convergence_passed = boolean(legacyGate.gate.passed,
    'Whether the archived local-magnitude coarse/fine gate passed');
  addNumber(metrics, 'legacy_convergence_early_fraction_difference',
    legacyGate.accepted_event_fraction_abs_difference, 5,
    'Archived coarse/fine difference in accepted-event fraction before the local-magnitude lifetime', 'ratio');
  addNumber(metrics, 'legacy_convergence_early_fraction_limit',
    legacyGate.limits.accepted_event_fraction, 2,
    'Archived convergence limit for the local-magnitude early-event fraction', 'ratio');
  metrics.legacy_local_magnitude_majority_regime_count = integer(
    legacy.majority_regime_count,
    'Archived rate scales with a local-magnitude early-event majority', 'scales');
  metrics.legacy_local_magnitude_nonrobust_majority_regime_count = integer(
    legacy.nonrobust_majority_regime_count,
    'Archived local-magnitude majority scales outside at least one FP-RP tolerance', 'scales');
  metrics.legacy_local_magnitude_numerically_converged = boolean(
    legacy.numerically_converged,
    'Whether the archived local-magnitude production setting was demonstrated converged');
  metrics.legacy_run_count = integer(
    regimes.reduce((sum, regime) => sum + regime.seeds.length, 0),
    'Archived scale-by-seed trajectory runs', 'runs');
  metrics.legacy_geometry_count_per_seed = integer(regimes[0].geometry_count_per_seed,
    'Archived Wigner geometries per seed and scale', 'geometries');
  metrics.legacy_fp_paths_per_seed = integer(regimes[0].nuclear_paths_per_seed.fp,
    'FP nuclear paths per seed and scale', 'paths');
  metrics.legacy_rp_axe_paths_per_seed = integer(regimes[0].nuclear_paths_per_seed.rp_axe,
    'RP-AXE nuclear paths per seed and scale', 'paths');

  metrics.exact_spatial_grid_audit_passed = boolean(exact.spatial_grid_audit_passed,
    'Whether the archived 384-versus-512 spatial-grid audit passed');
  metrics.exact_timestep_audited = boolean(exact.timestep_audited,
    'Whether the selected exact trace received a timestep audit');
  metrics.exact_box_size_audited = boolean(exact.box_size_audited,
    'Whether the selected exact trace received a box-size audit');
  metrics.exact_selected_grid_n = integer(exact.selected_grid_n,
    'Selected exact spatial-grid points per coordinate', 'grid points');
  metrics.exact_fine_max_norm_error = scientific(exact.fine_max_norm_error, 3,
    'Maximum norm error on the 512-by-512 exact grid');

  for (const regime of regimes) {
    const slug = SCALE_SLUGS.get(regime.pfm_rate_scale);
    if (!slug) throw new Error(`unexpected PFM-rate scale ${regime.pfm_rate_scale}`);
    const prefix = `s_${slug}`;
    const label = `PFM-rate scale ${regime.pfm_rate_scale}`;
    addNumber(metrics, `${prefix}_rate_scale`, regime.pfm_rate_scale, 3, label, 'rate multiplier');
    addNumber(metrics, `${prefix}_local_magnitude_lifetime_fs`,
      regime.outcomes.local_magnitude_lifetime_fs, 3,
      `Pooled mean single-trajectory coherence-magnitude lifetime at ${label}`, 'fs');
    addPercent(metrics, `${prefix}_local_magnitude_early_hop_fraction`,
      regime.outcomes.early_hop_fraction, 1,
      `Archived accepted-event fraction before the local-magnitude lifetime at ${label}`);
    for (const [key, digits, unit] of [
      ['upper_population', 4, 'probability'],
      ['product_probability', 4, 'probability'],
      ['centroid_x_sigma', 3, 'initial sigma_x'],
    ]) {
      addNumber(metrics, `${prefix}_max_${key}_error`,
        regime.outcomes.max_fp_rp_errors[key].value, digits,
        `Maximum archived FP-RP ${key.replaceAll('_', ' ')} difference at ${label}`, unit);
      for (const method of ['full', 'reprop_axe']) {
        addNumber(metrics, `${prefix}_${method}_rmse_selected_exact_${key}`,
          regime.rmse_to_selected_exact[method][key], digits,
          `${method === 'full' ? 'FP' : 'RP-AXE'} RMSE to the selected exact trace for ${key.replaceAll('_', ' ')} at ${label}`,
          unit);
      }
    }
    metrics[`${prefix}_repeat_hop_events`] = integer(regime.event_diagnostics.repeat_hop_events,
      `Repeated accepted FP hops at ${label}`, 'events');
    metrics[`${prefix}_recrossing_events`] = integer(regime.event_diagnostics.recrossing_events,
      `True returns to the trajectory initial active state at ${label}`, 'events');
    addNumber(metrics, `${prefix}_fp_consistency_error_max`,
      regime.fp_coefficient_active_state_inconsistency.maximum, 4,
      `Largest seed-level FP coefficient-versus-active-state inconsistency at ${label}`, 'probability');
  }

  return {
    schema_version: 1,
    experiment: 'coherence-hop-boundary',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [
        { path: input, sha256: sha256(inputPath) },
        { path: config, sha256: sha256(configPath) },
      ],
    },
    metrics,
  };
}

const expected = `${JSON.stringify(build(), null, 2)}\n`;
if (checkOnly) {
  if (!existsSync(outputPath) || readFileSync(outputPath, 'utf8') !== expected) {
    console.error(`${relative(root, outputPath)} is missing or stale`);
    process.exit(1);
  }
} else {
  writeFileSync(outputPath, expected);
}
