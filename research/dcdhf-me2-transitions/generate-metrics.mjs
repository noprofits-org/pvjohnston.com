#!/usr/bin/env node

// Projects the publication metrics for the DCDHF-Me2 excited-state manifold
// from the canonical postprocess.py output. Do not hand-author metrics.json.
//
// The primary functional is fixed to CAM-B3LYP here rather than chosen after
// the fact. Range-separated functionals are the a priori correct choice for a
// charge-transfer band in a push-pull dye, so this is a pre-commitment, not a
// selection made once the numbers were visible. B3LYP is projected alongside
// as a sensitivity check, and the post is expected to quote both.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const input = 'research/dcdhf-me2-transitions/results/summary.json';
const checkOnly = process.argv.includes('--check');

const PRIMARY_FUNCTIONAL = 'cam-b3lyp';
const SECONDARY_FUNCTIONAL = 'b3lyp';

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

const pct = (value, digits, description) => ({
  type: 'number',
  value,
  format: { style: 'percent', digits },
  description,
});

const int = (value, description, unit) => ({
  type: 'integer',
  value,
  description,
  ...(unit ? { unit } : {}),
});

function pick(summary, functional) {
  const run = summary.runs.find((r) => r.functional === functional);
  if (!run) {
    throw new Error(
      `no run for functional "${functional}" in ${input}; ` +
      `found: ${summary.runs.map((r) => r.functional).join(', ') || '(none)'}`);
  }
  if (!run.band_occupancy) {
    throw new Error(`run "${functional}" has no bright state, so no band to report`);
  }
  if (!run.state_gaps?.s1_s2_gap_eV || !run.state_gaps?.s1_s3_gap_eV) {
    throw new Error(`run "${functional}" is missing S1-S2/S1-S3 gaps; ` +
      `re-run postprocess.py (fewer than three states computed?)`);
  }
  return run;
}

function build(generatedAt) {
  const summary = JSON.parse(readFileSync(resolve(root, input), 'utf8'));
  const primary = pick(summary, PRIMARY_FUNCTIONAL);
  const secondary = pick(summary, SECONDARY_FUNCTIONAL);
  const geom = summary.geometry;
  if (!geom?.optimized) {
    throw new Error(`${input} has no optimized geometry; run the optimize stage first`);
  }

  const band = primary.band_occupancy;
  const manifold = primary.manifold;

  return {
    schema_version: 1,
    experiment: 'dcdhf-me2-transitions',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [{ path: input, sha256: sha256(input) }],
    },
    metrics: {
      // --- the manifold: the point of the experiment
      n_states_computed: int(
        manifold.n_states,
        'Singlet excited states computed per functional (CAM-B3LYP, full RPA)',
        'states'),
      n_bright_states: int(
        manifold.n_bright,
        'States with oscillator strength >= 0.01 (CAM-B3LYP)',
        'states'),
      n_states_under_band: int(
        band.n_states_under_band,
        `States within +/-${band.band_halfwidth_eV} eV of the lowest bright transition (CAM-B3LYP)`,
        'states'),
      n_bright_under_band: int(
        band.n_bright_under_band,
        `Bright states within +/-${band.band_halfwidth_eV} eV of the lowest bright transition (CAM-B3LYP)`,
        'states'),
      f_fraction_outside_band: pct(
        band.f_fraction_outside_band,
        0,
        'Fraction of total oscillator strength lying outside the apparent absorption band (CAM-B3LYP)'),
      f_fraction_in_lowest_bright: pct(
        manifold.f_fraction_in_lowest_bright,
        0,
        'Fraction of total oscillator strength carried by the lowest bright state alone (CAM-B3LYP)'),

      // --- absolute spacings, independent of the empirical band window above
      s1_s2_gap_ev: num(
        primary.state_gaps.s1_s2_gap_eV, 2,
        'Energy gap from S1 to S2 (CAM-B3LYP/def2-TZVP), independent of any band-width convention',
        'eV'),
      s1_s3_gap_ev: num(
        primary.state_gaps.s1_s3_gap_eV, 2,
        'Energy gap from S1 to S3 (CAM-B3LYP/def2-TZVP), independent of any band-width convention',
        'eV'),

      // Present only when at least two states clear the brightness threshold.
      // This is the gap the band argument turns on when S2 is dark, so it is
      // projected when it exists rather than left in summary.json alone.
      ...(primary.state_gaps.lowest_two_bright_gap_eV !== undefined
        ? {
          lowest_two_bright_gap_ev: num(
            primary.state_gaps.lowest_two_bright_gap_eV, 2,
            'Energy gap between the two lowest states with f >= 0.01 (CAM-B3LYP/def2-TZVP)',
            'eV'),
        }
        : {}),

      // --- band position, primary and sensitivity check
      band_center_nm: num(
        band.band_center_nm, 0,
        'Vertical excitation wavelength of the lowest bright state (CAM-B3LYP/def2-TZVP)', 'nm'),
      band_center_ev: num(
        band.band_center_eV, 2,
        'Vertical excitation energy of the lowest bright state (CAM-B3LYP/def2-TZVP)', 'eV'),
      band_center_nm_b3lyp: num(
        secondary.band_occupancy.band_center_nm, 0,
        'Lowest bright state wavelength under B3LYP, as a functional sensitivity check', 'nm'),
      lowest_bright_f: num(
        manifold.lowest_bright_f, 3,
        'Oscillator strength of the lowest bright state (CAM-B3LYP)'),

      // --- geometry: why the optimization step is not a formality
      uff_interring_twist_deg: num(
        geom.start_uff.interring_twist_deg, 1,
        'Twist between the dimethylaniline and dihydrofuran ring planes in the UFF starting structure',
        'degrees'),
      opt_interring_twist_deg: num(
        geom.optimized.interring_twist_deg, 1,
        'Twist between the dimethylaniline and dihydrofuran ring planes at the B3LYP/def2-SVP minimum',
        'degrees'),
      interring_twist_change_deg: num(
        geom.interring_twist_change_deg, 1,
        'Change in inter-ring twist from the UFF starting structure to the B3LYP/def2-SVP minimum',
        'degrees'),

      // --- honesty about the figure
      broadening_fwhm_ev_cosmetic: num(
        summary.broadening_fwhm_eV_cosmetic, 2,
        'Gaussian FWHM applied by hand for display only; not a computed line shape',
        'eV'),
    },
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
