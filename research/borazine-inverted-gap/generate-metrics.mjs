import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const dir = dirname(fileURLToPath(import.meta.url));
const prefix = 'research/borazine-inverted-gap/';
const paths = ['results/JOURNAL-2026-09-30.md', 'results/2b-adc2-stopped.pyscf.txt', 'results/2b-adc2-stopped.time.txt', 'results/2a_adc2_def2-tzvp.json', 'results/2b_eomccsd_def2-svp.json', 'results/1_eomccsd_def2-tzvp.json', 'results/11_eomccsd_def2-tzvp.json', 'results/1_eomccsd_def2-svp.json', 'results/11_eomccsd_def2-svp.json'];
const texts = paths.map(path => readFileSync(resolve(dir, path), 'utf8'));
const [journal, log, timing, aText] = texts;
const a = JSON.parse(aText);
const [bEomGap, borazineTzvp, boroxineTzvp, borazineSvp, boroxineSvp] = texts.slice(4).map(text => {
  const result = JSON.parse(text);
  const gap = 1000 * (Math.min(...result.singlets_eV) - Math.min(...result.triplets_eV));
  if (!Number.isFinite(gap) || Math.abs(gap - result.dEST_meV) > 1e-8) throw new Error(`${result.id} EOM gap disagrees with the result JSON`);
  return gap;
});
const aLine = journal.split('\n').find(line => line.startsWith('- 2a_adc2_def2-tzvp | done |'));
const bLine = journal.split('\n').find(line => line.startsWith('- 2b_adc2_def2-tzvp | failed |'));
const aRun = Object.fromEntries(aLine.split(' | ').slice(2).map(field => field.split('=')));
const bRun = Object.fromEntries(bLine.split(' | ').slice(2).map(field => field.split('=')));
const bo = Number(log.match(/Number of Active Occupied Orbitals: (\d+)/)[1]);
const bv = Number(log.match(/Number of Active Virtual Orbitals: (\d+)/)[1]);
const ao = a.nelec / 2 - a.frozen_core, av = a.nao - a.nelec / 2;
const ratio = (bo * bv / (ao * av)) ** 2;
const cpu = timing.match(/([\d.]+) user\s+([\d.]+) sys/);
const rows = [
  ['b_eom_gap_mev', bEomGap, 1, 'meV', '2b EOM-CCSD/def2-SVP gap from the lowest singlet and triplet energies; exploratory'],
  ['a1_borazine_gap_mev', borazineTzvp, 1, 'meV', 'Borazine EOM-CCSD/def2-TZVP gap for frozen Amendment 1'],
  ['a1_boroxine_gap_mev', boroxineTzvp, 1, 'meV', 'Boroxine EOM-CCSD/def2-TZVP control gap for frozen Amendment 1'],
  ['borazine_svp_gap_mev', borazineSvp, 1, 'meV', 'Borazine EOM-CCSD/def2-SVP gap for comparison with Amendment 1'],
  ['boroxine_svp_gap_mev', boroxineSvp, 1, 'meV', 'Boroxine EOM-CCSD/def2-SVP control gap for comparison with Amendment 1'],
  ['borazine_basis_shift_mev', borazineSvp - borazineTzvp, 0, 'meV', 'Decrease in the borazine EOM-CCSD gap from def2-SVP to def2-TZVP; no basis-set-limit claim'],
  ['b_occupied', bo, 0, 'orbitals', '2b active occupied orbitals from the RADC log'],
  ['b_virtual', bv, 0, 'orbitals', '2b active virtual orbitals from the RADC log'],
  ['b_core', Number(log.match(/Number of Frozen Occupied Orbitals: (\d+)/)[1]), 0, 'orbitals', '2b frozen core orbitals'],
  ['a_occupied', ao, 0, 'orbitals', '2a occupied orbitals less frozen core'],
  ['a_virtual', av, 0, 'orbitals', '2a basis functions less occupied orbitals'],
  ['a_hours', Number(aRun.wall_s) / 3600, 1, 'hours', '2a completed ADC wall time'],
  ['a_rss_gb', Number(aRun.peak_rss_bytes) / 1e9, 0, 'GB', '2a peak RSS in decimal GB'],
  ['doubles_ratio', ratio, 1, 'ratio', 'Squared ratio of occupied times virtual dimensions; storage scaling model'],
  ['estimated_gb', Number(aRun.peak_rss_bytes) / 1e9 * ratio, 0, 'GB', 'Planning estimate from 2a peak RSS scaled by doubles space; not a measured requirement'],
  ['mp2_eh', Number(log.match(/MP2 correlation energy of reference state \(a.u.\) = ([-\d.]+)/)[1]), 8, 'hartree', '2b MP2 reference correlation energy; not an excitation gap'],
  ['b_seconds', Number(bRun.wall_s), 0, 'seconds', '2b stopped ADC wall time'],
  ['b_hours', Number(bRun.wall_s) / 3600, 1, 'hours', '2b stopped ADC wall time'],
  ['b_cpu_hours', (Number(cpu[1]) + Number(cpu[2])) / 3600, 1, 'hours', '2b user plus system CPU time'],
  ['b_rss_gb', Number(bRun.peak_rss_bytes) / 1e9, 2, 'GB', '2b peak RSS from macOS time'],
  ['b_footprint_gb', Number(timing.match(/(\d+)\s+peak memory footprint/)[1]) / 1e9, 2, 'GB', 'Final macOS time peak memory footprint; distinct from RSS'],
];
if (rows.some(([, value]) => !Number.isFinite(value))) throw new Error('Non-finite resource metric');
const output = resolve(dir, 'metrics.json');
const check = process.argv.includes('--check');
const existing = existsSync(output) ? JSON.parse(readFileSync(output, 'utf8')) : null;
const expected = JSON.stringify({schema_version: 1, experiment: 'borazine-inverted-gap', provenance: {
  generated_at: check && existing ? existing.provenance.generated_at : new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
  generator: prefix + 'generate-metrics.mjs', inputs: paths.map((path, i) => ({path: prefix + path, sha256: createHash('sha256').update(texts[i]).digest('hex')})),
}, metrics: Object.fromEntries(rows.map(([name, value, digits, unit, description]) => [name, {type: 'number', value, format: {style: 'fixed', digits}, description, unit}]))}, null, 2) + '\n';
if (check) {
  if (!existing || readFileSync(output, 'utf8') !== expected) throw new Error('metrics.json is missing or stale');
} else writeFileSync(output, expected);
