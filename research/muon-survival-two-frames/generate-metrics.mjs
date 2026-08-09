#!/usr/bin/env node

// Plain deterministic projection from the canonical analysis summary and the
// workflow ledger. This replaces graph/hardened-generate-metrics.mjs, the
// atomic-staging generator the workflow trial produced; that version shelled
// out to an uncommitted .venv for validation and could not run in CI. The
// physics metrics are unchanged; the ledger metrics are new and derive from
// workflow.jsonl, which is frozen at the trial's terminal parked state.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const summaryInput = 'research/muon-survival-two-frames/results/summary.json';
const ledgerInput = 'research/muon-survival-two-frames/workflow.jsonl';
const outputPath = resolve(experimentDir, 'metrics.json');
const checkOnly = process.argv.includes('--check');

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

function fail(message) {
  console.error(`generate-metrics: ${message}`);
  process.exit(1);
}

const numberMetric = (value, style, digits, description, unit = '1') => {
  if (typeof value !== 'number' || !Number.isFinite(value)) fail(`invalid numeric metric: ${description}`);
  return { type: 'number', value, format: { style, digits }, description, unit };
};
const integerMetric = (value, description, unit) => {
  if (!Number.isInteger(value)) fail(`invalid integer metric: ${description}`);
  return { type: 'integer', value, description, unit };
};
const booleanMetric = (value, description) => {
  if (typeof value !== 'boolean') fail(`invalid boolean metric: ${description}`);
  return { type: 'boolean', value, description };
};

function build() {
  const result = JSON.parse(readFileSync(resolve(root, summaryInput), 'utf8'));
  if (result.experiment !== 'muon-survival-two-frames' || result.post_type !== 'understanding') {
    fail('result identity mismatch');
  }
  if (result.outcome_kind !== 'understanding-observations-no-verdict') {
    fail('result must not contain a Research verdict');
  }
  const focal = result.focal;
  const diagnostics = result.checks?.diagnostics;
  if (!focal || !diagnostics) fail('result lacks focal values or diagnostics');
  const requiredChecks = [
    'frame_agreement',
    'focal_monte_carlo_within_four_standard_errors',
    'maximum_grid_discrepancy_at_most_threshold',
    'counts_valid_and_monotonic',
    'numeric_shapes_dtypes_units_valid',
    'schema_manifest_provenance_and_hashes_valid',
  ];
  const standardized = diagnostics.focal_binomial_standard_error === 0
    ? (diagnostics.focal_absolute_discrepancy === 0 ? 0 : fail('undefined standardized discrepancy'))
    : diagnostics.focal_absolute_discrepancy / diagnostics.focal_binomial_standard_error;

  const events = readFileSync(resolve(root, ledgerInput), 'utf8')
    .trim().split('\n').map((line) => JSON.parse(line));
  const last = events[events.length - 1];
  const submissions = events.filter((e) => e.type === 'submit');
  const reviews = events.filter((e) => e.type === 'review');
  const wallClockHours = (Date.parse(last.timestamp) - Date.parse(events[0].timestamp)) / 3_600_000;
  const snapshots = events.reduce((n, e) => n + (Array.isArray(e.artifacts) ? e.artifacts.length : 0), 0);

  const metrics = {
    detector_beta: numberMetric(focal.detector.beta, 'fixed', 8, 'Detector-frame beta', '1'),
    detector_gamma: numberMetric(focal.detector.gamma, 'fixed', 8, 'Detector-frame gamma', '1'),
    muon_beta: numberMetric(focal.muon.beta, 'fixed', 8, 'Independently reconstructed muon-frame beta', '1'),
    muon_gamma: numberMetric(focal.muon.gamma, 'fixed', 8, 'Independently reconstructed muon-frame gamma', '1'),
    detector_distance_m: numberMetric(focal.detector.laboratory_distance_m, 'fixed', 1, 'Detector-frame laboratory distance at the focal index', 'm'),
    detector_elapsed_time_s: numberMetric(focal.detector.elapsed_time_s, 'scientific', 6, 'Detector-frame laboratory travel time at the focal index', 's'),
    detector_mean_lifetime_s: numberMetric(focal.detector.mean_lifetime_s, 'scientific', 6, 'Dilated mean lifetime in the detector frame', 's'),
    detector_decay_exponent: numberMetric(focal.detector.decay_exponent, 'fixed', 8, 'Detector-frame dimensionless decay exponent', '1'),
    muon_contracted_distance_m: numberMetric(focal.muon.contracted_distance_m, 'fixed', 6, 'Contracted path in the muon frame at the focal index', 'm'),
    muon_elapsed_time_s: numberMetric(focal.muon.elapsed_time_s, 'scientific', 6, 'Proper elapsed time in the muon frame', 's'),
    muon_mean_lifetime_s: numberMetric(focal.muon.mean_lifetime_s, 'scientific', 6, 'Proper mean lifetime in the muon frame', 's'),
    muon_decay_exponent: numberMetric(focal.muon.decay_exponent, 'fixed', 8, 'Muon-frame dimensionless decay exponent', '1'),
    analytic_survival: numberMetric(focal.detector.survival_probability, 'percent', 3, 'Analytic survival probability at the focal index', 'ratio'),
    empirical_survival: numberMetric(focal.empirical_survival_probability, 'percent', 3, 'Empirical survival from the registered sample at the focal index', 'ratio'),
    counterfactual_survival: numberMetric(focal.counterfactual.survival_probability, 'scientific', 3, 'Same-speed no-lifetime-dilation counterfactual survival', 'ratio'),
    survivor_count: integerMetric(focal.empirical_count, 'Registered-sample survivors at the focal index', 'muons'),
    focal_binomial_standard_error: numberMetric(diagnostics.focal_binomial_standard_error, 'scientific', 6, 'Prospective analytic-probability binomial standard error', 'ratio'),
    focal_standardized_discrepancy: numberMetric(standardized, 'fixed', 3, 'Focal absolute discrepancy in prospective standard-error units', '1'),
    maximum_grid_absolute_discrepancy: numberMetric(diagnostics.maximum_grid_absolute_discrepancy, 'fixed', 6, 'Maximum empirical-versus-analytic discrepancy over the frozen grid', 'ratio'),
  };
  for (const key of requiredChecks) {
    metrics[`pass_${key}`] = booleanMetric(result.checks[key], `Registered fidelity check: ${key}`);
  }
  metrics.all_registered_checks_pass = booleanMetric(result.checks.all_passed, 'Whether every registered fidelity check passed');

  metrics.ledger_events = integerMetric(events.length, 'Events in the append-only workflow ledger', 'events');
  metrics.ledger_submissions = integerMetric(submissions.length, 'Work-packet submissions recorded in the ledger', 'submissions');
  metrics.ledger_reviews = integerMetric(reviews.length, 'Independent reviews recorded in the ledger', 'reviews');
  metrics.ledger_revise_decisions = integerMetric(
    reviews.filter((e) => e.decision === 'revise').length,
    'Reviews that sent work backward for revision', 'reviews',
  );
  metrics.ledger_setup_review_rounds = integerMetric(
    reviews.filter((e) => e.from === 'setup_review').length,
    'Setup-review rounds before execution was approved', 'reviews',
  );
  metrics.ledger_evidence_snapshots = integerMetric(snapshots, 'Immutable evidence snapshots bound by ledger events', 'snapshots');
  metrics.ledger_wall_clock_hours = numberMetric(wallClockHours, 'fixed', 1, 'Elapsed time from ledger initialization to the terminal event', 'h');
  metrics.ledger_terminal_parked = booleanMetric(
    last.type === 'review' && last.decision === 'park',
    'Whether the ledger ends in the terminal parked state',
  );

  return {
    schema_version: 1,
    experiment: 'muon-survival-two-frames',
    provenance: {
      generated_at: result.generated_at,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [
        { path: summaryInput, sha256: sha256(summaryInput) },
        { path: ledgerInput, sha256: sha256(ledgerInput) },
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

// CI reaches this generator through verify-metrics, so chain the figure
// renderer here: a stale committed Figure 2 fails the same check that guards
// the metrics projection.
try {
  execFileSync(
    process.execPath,
    [resolve(experimentDir, 'src/render_figure_v2.mjs'), ...(checkOnly ? ['--check'] : [])],
    { stdio: 'inherit' },
  );
} catch (error) {
  process.exit(error.status ?? 1);
}
