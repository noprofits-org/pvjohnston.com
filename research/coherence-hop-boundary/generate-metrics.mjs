#!/usr/bin/env node

// Deterministic publication projection of results/analysis.json.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const input = 'research/coherence-hop-boundary/results/analysis.json';
const inputPath = resolve(root, input);
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
const errorInfo = {
  upper_population: ['upper_population', 4, 'upper-state population', 'probability'],
  product_probability: ['product_probability', 4, 'product-side probability', 'probability'],
  centroid_x_sigma: ['centroid_x_sigma', 3, 'nuclear centroid', 'initial sigma_x'],
  coherence_amplitude: ['coherence_amplitude', 4, 'coherence amplitude', 'amplitude'],
};

function addNumber(metrics, key, value, digits, description, unit) {
  if (value !== null && Number.isFinite(value)) metrics[key] = fixed(value, digits, description, unit);
}

function addPercent(metrics, key, value, digits, description) {
  if (value !== null && Number.isFinite(value)) metrics[key] = percent(value, digits, description);
}

function build(generatedAt) {
  const analysis = JSON.parse(readFileSync(inputPath, 'utf8'));
  if (analysis.experiment !== 'coherence-hop-boundary') {
    throw new Error('analysis experiment identifier does not match coherence-hop-boundary');
  }
  const metrics = {};
  const regimes = analysis.regimes;
  const first = regimes[0];
  const majority = regimes.filter((r) => r.outcomes.classifications.majority_early_hop);
  const nonrobust = majority.filter((r) => !r.outcomes.classifications.compound_robust);
  const finiteEarly = regimes.filter((r) => Number.isFinite(r.outcomes.early_hop_fraction));
  const maxEarly = finiteEarly.length ? finiteEarly.reduce((best, r) => (
    r.outcomes.early_hop_fraction > best.outcomes.early_hop_fraction ? r : best
  )) : null;

  metrics.rate_scale_count = integer(regimes.length, 'Number of predeclared PFM-rate scales', 'scales');
  metrics.seed_count_per_scale = integer(first.seeds.length, 'Independent confirmatory seeds per PFM-rate scale', 'seeds');
  metrics.geometry_count_per_seed = integer(first.geometry_count_per_seed, 'Matched Wigner geometries per seed and PFM-rate scale', 'geometries');
  metrics.confirmatory_replicate_count = integer(
    regimes.reduce((sum, r) => sum + r.seeds.length, 0),
    'Total scale-by-seed confirmatory trajectory replicates', 'replicates',
  );
  addPercent(metrics, 'majority_early_hop_threshold', analysis.declared.majority_early_hop_threshold, 0,
    'Accepted-event early-hop fraction defining a majority regime');
  addNumber(metrics, 'upper_population_tolerance', analysis.declared.error_tolerances.upper_population, 2,
    'Compound-robustness limit for maximum FP-RP upper-state population error', 'probability');
  addNumber(metrics, 'product_probability_tolerance', analysis.declared.error_tolerances.product_probability, 2,
    'Compound-robustness limit for maximum FP-RP product-side probability error', 'probability');
  addNumber(metrics, 'centroid_tolerance_sigma', analysis.declared.error_tolerances.centroid_x_sigma, 2,
    'Compound-robustness limit for maximum FP-RP centroid error', 'initial sigma_x');

  metrics.lineage_gate_passed = boolean(analysis.lineage_gate.passed, 'Whether the frozen-code lineage comparison passed');
  if ('accepted_events_identical' in analysis.lineage_gate) {
    metrics.lineage_accepted_events_identical = boolean(
      analysis.lineage_gate.accepted_events_identical,
      'Whether accepted-hop records were identical in the lineage comparison',
    );
  }
  if (Number.isFinite(analysis.lineage_gate.max_abs_observable_difference)) {
    metrics.lineage_max_observable_difference = scientific(
      analysis.lineage_gate.max_abs_observable_difference, 3,
      'Largest observable-array difference in the lineage comparison',
    );
  }

  const convergence = analysis.convergence_gate;
  metrics.convergence_coarse_accepted = boolean(convergence.coarse_setting_accepted,
    'Whether the planned trajectory setting passed every convergence criterion');
  metrics.convergence_gate_passed = boolean(convergence.passed,
    'Whether the trajectory convergence gate selected a valid production setting');
  addNumber(metrics, 'production_nuclear_dt_fs', convergence.production_dt_fs, 4,
    'Nuclear time step selected by the convergence gate', 'fs');
  metrics.production_electronic_substeps = integer(convergence.production_electronic_substeps,
    'Electronic substeps selected per nuclear step', 'substeps');
  const convergenceUnits = {
    early_hop_fraction: 'ratio', coherence_lifetime_fs: 'fs',
    full_upper_population: 'probability', full_product_probability: 'probability',
    full_centroid_x_sigma: 'initial sigma_x',
  };
  for (const [key, value] of Object.entries(convergence.differences)) {
    addNumber(metrics, `convergence_difference_${key}`, value, key === 'coherence_lifetime_fs' ? 3 : 4,
      `Absolute planned-versus-fine convergence difference for ${key.replaceAll('_', ' ')}`,
      convergenceUnits[key]);
  }
  metrics.convergence_majority_classification_unchanged = boolean(
    convergence.classification_unchanged.majority_early_hop,
    'Whether the majority-early-hop classification was unchanged by time-step refinement',
  );
  metrics.convergence_robustness_classification_unchanged = boolean(
    convergence.classification_unchanged.compound_robust,
    'Whether the compound-robustness classification was unchanged by time-step refinement',
  );

  const exact = analysis.exact_grid_gate;
  metrics.exact_coarse_grid_accepted = boolean(exact.coarse_grid_accepted,
    'Whether the 384-by-384 exact grid passed every predeclared audit criterion');
  metrics.exact_grid_gate_passed = boolean(exact.passed,
    'Whether the selected exact reference passed the mandatory norm gate');
  metrics.exact_production_grid_n = integer(exact.production_grid_n,
    'Selected exact-grid points per coordinate axis', 'grid points');
  for (const [key, value] of Object.entries(exact.maximum_time_series_differences)) {
    addNumber(metrics, `exact_grid_difference_${key}`, value, 6,
      `Maximum 384-versus-512 exact-grid difference for ${key.replaceAll('_', ' ')}`,
      key === 'centroid_x_sigma' ? 'initial sigma_x' : key === 'coherence_amplitude' ? 'amplitude' : 'probability');
  }
  metrics.exact_fine_max_norm_error = scientific(exact.fine_max_norm_error, 3,
    'Maximum absolute norm error on the 512-by-512 exact grid');

  metrics.majority_regime_count = integer(analysis.hypothesis.majority_regime_count,
    'Number of uncensored PFM-rate scales with at least half of accepted hops early', 'scales');
  metrics.nonrobust_majority_regime_count = integer(analysis.hypothesis.nonrobust_majority_regime_count,
    'Number of majority-early-hop scales exceeding at least one robustness limit', 'scales');
  metrics.majority_regime_reached = boolean(analysis.hypothesis.majority_regime_reached,
    'Whether any uncensored scale reached the accepted-event majority boundary');
  metrics.all_required_gates_passed = boolean(analysis.hypothesis.all_required_gates_passed,
    'Whether lineage, convergence, and exact-grid requirements permit adjudication');
  metrics.hypothesis_supported = boolean(analysis.hypothesis.supported,
    'Whether the predeclared hypothesis verdict is supported');
  metrics.hypothesis_falsified = boolean(analysis.hypothesis.falsified,
    'Whether the predeclared hypothesis verdict is falsified');
  metrics.hypothesis_inconclusive = boolean(analysis.hypothesis.inconclusive,
    'Whether the predeclared hypothesis verdict is inconclusive');
  if (maxEarly) {
    addNumber(metrics, 'max_early_hop_rate_scale', maxEarly.pfm_rate_scale, 3,
      'PFM-rate scale with the largest pooled accepted-event early-hop fraction', 'rate multiplier');
    addPercent(metrics, 'max_early_hop_fraction', maxEarly.outcomes.early_hop_fraction, 1,
      'Largest pooled accepted-event early-hop fraction across the sweep');
    addNumber(metrics, 'max_early_hop_coherence_lifetime_fs', maxEarly.outcomes.coherence_lifetime_fs, 3,
      'Pooled coherence lifetime at the scale with the largest early-hop fraction', 'fs');
    metrics.max_early_hop_accepted_events = integer(maxEarly.event_diagnostics.accepted,
      'Accepted FP hop events at the scale with the largest early-hop fraction', 'events');
    for (const [errorKey, [metricKey, digits, prose, unit]] of Object.entries(errorInfo)) {
      addNumber(metrics, `max_early_hop_${metricKey}_error`,
        maxEarly.outcomes.max_fp_rp_errors[errorKey].value, digits,
        `Maximum pooled FP-RP ${prose} error at the scale with the largest early-hop fraction`, unit);
    }
  }
  if (majority.length) {
    addNumber(metrics, 'majority_onset_rate_scale', majority[0].pfm_rate_scale, 3,
      'First predeclared descending PFM-rate scale reaching the majority boundary', 'rate multiplier');
    addPercent(metrics, 'majority_onset_early_hop_fraction', majority[0].outcomes.early_hop_fraction, 1,
      'Accepted-event early-hop fraction at the first predeclared scale reaching a majority');
    for (const [errorKey, [metricKey, digits, prose, unit]] of Object.entries(errorInfo)) {
      addNumber(metrics, `majority_onset_${metricKey}_error`,
        majority[0].outcomes.max_fp_rp_errors[errorKey].value, digits,
        `Maximum pooled FP-RP ${prose} error at the first majority-early-hop scale`, unit);
    }
  }

  for (const [key, result] of Object.entries(analysis.exploratory_spearman_early_hop_vs_error)) {
    addNumber(metrics, `exploratory_spearman_early_hop_vs_${key}`, result.rho, 3,
      `Exploratory Spearman association between pooled early-hop fraction and maximum ${key.replaceAll('_', ' ')} error across seven scales`);
    metrics[`exploratory_spearman_${key}_n`] = integer(result.n,
      `Number of uncensored PFM-rate scales in the exploratory ${key.replaceAll('_', ' ')} Spearman association`, 'scales');
  }

  for (const regime of regimes) {
    const slug = SCALE_SLUGS.get(regime.pfm_rate_scale);
    if (!slug) throw new Error(`unexpected PFM-rate scale ${regime.pfm_rate_scale}`);
    const prefix = `s_${slug}`;
    const label = `PFM-rate scale ${regime.pfm_rate_scale}`;
    addNumber(metrics, `${prefix}_rate_scale`, regime.pfm_rate_scale, 3, label, 'rate multiplier');
    addNumber(metrics, `${prefix}_coherence_lifetime_fs`, regime.outcomes.coherence_lifetime_fs, 3,
      `Pooled C(0)/e coherence lifetime at ${label}`, 'fs');
    addPercent(metrics, `${prefix}_early_hop_fraction`, regime.outcomes.early_hop_fraction, 1,
      `Pooled fraction of accepted FP hop events at or before the coherence lifetime at ${label}`);
    metrics[`${prefix}_lifetime_censored`] = boolean(
      regime.outcomes.classifications.coherence_lifetime_censored,
      `Whether the pooled coherence lifetime is right-censored at ${label}`,
    );
    metrics[`${prefix}_majority_early_hop`] = boolean(regime.outcomes.classifications.majority_early_hop,
      `Whether ${label} reaches the accepted-event majority boundary`);
    metrics[`${prefix}_compound_robust`] = boolean(regime.outcomes.classifications.compound_robust,
      `Whether all three mandatory FP-RP errors remain within tolerance at ${label}`);
    metrics[`${prefix}_nonrobust_majority`] = boolean(regime.outcomes.classifications.nonrobust_majority,
      `Whether ${label} is both majority-early-hop and outside the compound robustness limits`);

    for (const [errorKey, [metricKey, digits, prose, unit]] of Object.entries(errorInfo)) {
      const error = regime.outcomes.max_fp_rp_errors[errorKey];
      addNumber(metrics, `${prefix}_max_${metricKey}_error`, error.value, digits,
        `Maximum pooled FP-RP ${prose} error at ${label}`, unit);
      addNumber(metrics, `${prefix}_time_of_max_${metricKey}_error_fs`, error.time_fs, 3,
        `Time of the maximum pooled FP-RP ${prose} error at ${label}`, 'fs');
      for (const method of ['full', 'reprop_axe']) {
        addNumber(metrics, `${prefix}_${method}_rmse_exact_${metricKey}`,
          regime.rmse_to_exact[method][errorKey], digits,
          `${method === 'full' ? 'FP' : 'RP-AXE'} RMSE to exact ${prose} at ${label}`, unit);
      }
    }

    for (const [field, interval] of Object.entries(regime.intervals_95)) {
      const digits = field.includes('lifetime') ? 3 : field.includes('centroid') ? 3 : 4;
      const unit = field.includes('lifetime') ? 'fs' : field.includes('accepted_hops') ? 'events'
        : field.includes('centroid') ? 'initial sigma_x'
        : field.includes('fraction') ? 'ratio' : field.includes('coherence') ? 'amplitude' : 'probability';
      for (const bound of ['mean', 'lower', 'upper', 'half_width']) {
        addNumber(metrics, `${prefix}_${field}_seed_${bound}`, interval[bound], digits,
          `${bound.replace('_', ' ')} of the seed-level 95% interval for ${field.replaceAll('_', ' ')} at ${label}`, unit);
      }
    }

    const events = regime.event_diagnostics;
    for (const key of ['proposed', 'frustrated', 'accepted', 'accepted_early', 'accepted_late',
      'trajectory_count',
      'unique_hopping_trajectories', 'first_hop_events', 'repeat_hop_events', 'recrossing_events',
      'trajectories_with_repeats', 'trajectories_with_recrossing']) {
      if (events[key] !== null) metrics[`${prefix}_${key}`] = integer(events[key],
        `${key.replaceAll('_', ' ')} in pooled FP event diagnostics at ${label}`, key.includes('trajector') ? 'trajectories' : 'events');
    }
    for (const [direction, counts] of Object.entries(events.directions)) {
      for (const key of ['proposed', 'frustrated', 'accepted']) {
        metrics[`${prefix}_${direction}_${key}`] = integer(counts[key],
          `${direction.replaceAll('_', ' ')} ${key} events at ${label}`, 'events');
      }
    }
    for (const [period, counts] of Object.entries(events.timing)) {
      for (const key of ['proposed', 'frustrated', 'accepted', 'first_accepted', 'repeat_accepted']) {
        if (counts[key] !== null) metrics[`${prefix}_${period}_${key}`] = integer(
          counts[key], `${period} ${key} FP hop events at ${label}`, 'events',
        );
      }
    }
    addPercent(metrics, `${prefix}_acceptance_fraction`, events.acceptance_fraction, 1,
      `Accepted fraction of proposed FP hop events at ${label}`);
    addPercent(metrics, `${prefix}_unique_first_fraction`, events.unique_first_fraction_of_accepted, 1,
      `Unique first-hop events as a fraction of accepted FP events at ${label}`);
    addPercent(metrics, `${prefix}_repeat_fraction`, events.repeat_fraction_of_accepted, 1,
      `Repeat hops as a fraction of accepted FP events at ${label}`);
    addPercent(metrics, `${prefix}_recrossing_fraction`, events.recrossing_fraction_of_accepted, 1,
      `Recrossing hops as a fraction of accepted FP events at ${label}`);
    addPercent(metrics, `${prefix}_hopping_trajectory_fraction`, events.hopping_trajectory_fraction, 1,
      `Fraction of FP trajectories with at least one accepted hop at ${label}`);
    addPercent(metrics, `${prefix}_repeat_hopping_trajectory_fraction`, events.repeat_hopping_trajectory_fraction, 1,
      `Fraction of FP trajectories with at least one repeated accepted hop at ${label}`);
    addPercent(metrics, `${prefix}_recrossing_trajectory_fraction`, events.recrossing_trajectory_fraction, 1,
      `Fraction of FP trajectories with at least one recrossing event at ${label}`);
    addPercent(metrics, `${prefix}_early_first_hop_fraction`, events.early_first_hop_fraction, 1,
      `Fraction of first accepted FP hops occurring at or before the coherence lifetime at ${label}`);
    addPercent(metrics, `${prefix}_early_repeat_hop_fraction`, events.early_repeat_hop_fraction, 1,
      `Fraction of repeated accepted FP hops occurring at or before the coherence lifetime at ${label}`);

    for (const seed of regime.per_seed) {
      const seedPrefix = `${prefix}_seed_${seed.seed}`;
      addNumber(metrics, `${seedPrefix}_coherence_lifetime_fs`, seed.coherence_lifetime_fs, 3,
        `Seed ${seed.seed} coherence lifetime at ${label}`, 'fs');
      addPercent(metrics, `${seedPrefix}_early_hop_fraction`, seed.early_hop_fraction, 1,
        `Seed ${seed.seed} accepted-event early-hop fraction at ${label}`);
      metrics[`${seedPrefix}_accepted_hops`] = integer(seed.accepted_hops,
        `Seed ${seed.seed} accepted FP hop events at ${label}`, 'events');
      for (const [errorKey, [metricKey, digits, prose, unit]] of Object.entries(errorInfo)) {
        addNumber(metrics, `${seedPrefix}_max_${metricKey}_error`, seed.max_fp_rp_errors[errorKey].value,
          digits, `Seed ${seed.seed} maximum FP-RP ${prose} error at ${label}`, unit);
      }
    }
  }

  return {
    schema_version: 1,
    experiment: 'coherence-hop-boundary',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [{ path: input, sha256: sha256(inputPath) }],
    },
    metrics,
  };
}

const existing = existsSync(outputPath) ? JSON.parse(readFileSync(outputPath, 'utf8')) : null;
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
