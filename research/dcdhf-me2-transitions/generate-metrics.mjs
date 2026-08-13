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
const stationaryInput = 'research/dcdhf-me2-transitions/results/stationary_check.json';
const checkOnly = process.argv.includes('--check');

const PRIMARY_MOLECULE = 'dcdhf-me2';
const CONTRAST_MOLECULE = 'benzene';
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

// Existing keys are NOT renamed when a second molecule joins: the unprefixed
// keys keep meaning DCDHF-Me2 under CAM-B3LYP, and benzene gets its own
// `benzene_` prefixed keys. A silent rename would break every span already
// drafted against these names, and the metrics build fails on missing keys.
function pick(summary, molecule, functional) {
  const entry = summary.molecules?.[molecule];
  if (!entry) {
    throw new Error(
      `no results for molecule "${molecule}" in ${input}; ` +
      `found: ${Object.keys(summary.molecules ?? {}).join(', ') || '(none)'}`);
  }
  const run = entry.runs.find((r) => r.functional === functional);
  if (!run) {
    throw new Error(
      `no run for ${molecule}/${functional} in ${input}; ` +
      `found: ${entry.runs.map((r) => r.functional).join(', ') || '(none)'}`);
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
  const primary = pick(summary, PRIMARY_MOLECULE, PRIMARY_FUNCTIONAL);
  const secondary = pick(summary, PRIMARY_MOLECULE, SECONDARY_FUNCTIONAL);
  const benzene = pick(summary, CONTRAST_MOLECULE, PRIMARY_FUNCTIONAL);
  const geom = summary.molecules[PRIMARY_MOLECULE].geometry;
  if (!geom?.optimized) {
    throw new Error(`${input} has no optimized geometry; run the optimize stage first`);
  }
  const stationary = JSON.parse(readFileSync(resolve(root, stationaryInput), 'utf8'));
  const twist20 = stationary.twist_scan.find((s) => s.displacement_deg === 20.0);
  const twist10 = stationary.twist_scan.find((s) => s.displacement_deg === 10.0);
  const pyr = stationary.pyramidalization_scan.find((s) => s.displacement_ang === 0.15);
  if (!twist20 || !twist10 || !pyr) {
    throw new Error(`${stationaryInput} is missing an expected displacement; ` +
      `re-run check_stationary.py with the default scan points`);
  }
  const worstSplit = Math.max(
    ...stationary.symmetry_pairs.map((p) => p.energy_split_microhartree));

  const bgap = benzene.state_gaps;
  if (bgap?.lowest_bright_f_share === undefined) {
    throw new Error(
      `${CONTRAST_MOLECULE} has fewer than two bright states, so the ` +
      `degenerate-pair contrast cannot be stated; check results before drafting`);
  }

  const band = primary.band_occupancy;
  const manifold = primary.manifold;

  return {
    schema_version: 1,
    experiment: 'dcdhf-me2-transitions',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [
        { path: input, sha256: sha256(input) },
        { path: stationaryInput, sha256: sha256(stationaryInput) },
      ],
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
        geom.start.interring_twist_deg, 1,
        'Twist between the dimethylaniline and dihydrofuran ring planes in the UFF starting structure',
        'degrees'),
      opt_interring_twist_deg: num(
        geom.optimized.interring_twist_deg, 1,
        'Twist between the dimethylaniline and dihydrofuran ring planes at the B3LYP/def2-SVP minimum',
        'degrees'),
      interring_twist_change_deg: num(
        geom.delta_interring_twist_deg, 1,
        'Change in inter-ring twist from the UFF starting structure to the B3LYP/def2-SVP minimum',
        'degrees'),
      // Benzene's ring stays regular under optimization, which is what makes
      // the degeneracy claim checkable rather than assumed: a broken D6h would
      // show up here first as a spread in the C-C bond lengths.
      benzene_cc_bond_spread_ang: num(
        summary.molecules[CONTRAST_MOLECULE].geometry.optimized.cc_bond_spread_ang, 5,
        'Spread between longest and shortest C-C bond at benzene\'s B3LYP/def2-SVP minimum',
        'A'),

      // --- results the prose leans on, which must not be hand-typed
      s1_s2_gap_ev_b3lyp: num(
        secondary.state_gaps.s1_s2_gap_eV, 2,
        'Energy gap from S1 to S2 under B3LYP/def2-TZVP, showing the isolated lowest state is not an artefact of functional choice',
        'eV'),
      functional_shift_ev: num(
        primary.band_occupancy.band_center_eV - secondary.band_occupancy.band_center_eV, 3,
        'Blue shift of the lowest bright state from B3LYP to CAM-B3LYP, the signature of charge-transfer character',
        'eV'),

      // Stationary-point evidence. These are the numbers behind the claim that
      // the planar structure is a minimum along the tested coordinates, so
      // they belong in the projection rather than typed into prose.
      stationary_twist20_rise_kcal: num(
        twist20.delta_E_kcal_per_mol, 2,
        'Energy rise on rigidly twisting the donor ring 20 degrees from the planar minimum',
        'kcal/mol'),
      stationary_twist10_rise_kcal: num(
        twist10.delta_E_kcal_per_mol, 2,
        'Energy rise on rigidly twisting the donor ring 10 degrees from the planar minimum',
        'kcal/mol'),
      stationary_pyramid_rise_kcal: num(
        pyr.delta_E_kcal_per_mol, 2,
        'Energy rise on displacing the amine nitrogen 0.15 A out of its substituent plane',
        'kcal/mol'),
      stationary_worst_pair_split_uhartree: num(
        worstSplit, 2,
        'Largest energy split between mirror-related displacement pairs, the self-test on the displacement construction',
        'microhartree'),

      // --- benzene, the contrast case: one apparent band, two degenerate
      // transitions sharing the strength, versus the dye's single dominant one
      benzene_n_states_under_band: int(
        benzene.band_occupancy.n_states_under_band,
        `States within +/-${benzene.band_occupancy.band_halfwidth_eV} eV of benzene's lowest bright transition (CAM-B3LYP)`,
        'states'),
      benzene_n_bright_under_band: int(
        benzene.band_occupancy.n_bright_under_band,
        "Bright states within the same window of benzene's lowest bright transition (CAM-B3LYP)",
        'states'),
      benzene_band_center_ev: num(
        benzene.band_occupancy.band_center_eV, 2,
        "Vertical excitation energy of benzene's lowest bright state (CAM-B3LYP/def2-TZVP)",
        'eV'),
      benzene_lowest_two_bright_gap_ev: num(
        bgap.lowest_two_bright_gap_eV, 3,
        "Splitting between benzene's two lowest bright states, degenerate under D6h symmetry",
        'eV'),
      benzene_lowest_bright_f_share: pct(
        bgap.lowest_bright_f_share, 0,
        "Share of the two lowest bright states' combined oscillator strength carried by the lower one (benzene; 50% = an even split)"),

      // The same quantity for the dye, so the contrast is one comparison of
      // like with like rather than two numbers a reader must relate.
      lowest_bright_f_share: pct(
        primary.state_gaps.lowest_bright_f_share, 0,
        "Share of the two lowest bright states' combined oscillator strength carried by the lower one (DCDHF-Me2, CAM-B3LYP)"),

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
