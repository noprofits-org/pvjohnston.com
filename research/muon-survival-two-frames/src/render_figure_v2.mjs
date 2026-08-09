#!/usr/bin/env node

// The v2 presentation renderer that AMENDED-PROTOCOL-v2.md specified but
// workflow graph v1 had no lawful edge to execute. It consumes the unchanged
// canonical results/summary.json and prints both frame routes — distances,
// times, mean lifetimes, and both unaltered stored exponents — next to the
// aligned exponent markers, so every printed value is bound to the committed
// result rather than hand-entered. Emits a deterministic SVG; --check
// verifies the committed image matches a fresh render byte for byte.
//
// Deviations from the v1 presentation, both deliberate and disclosed in the
// post: the output is a standalone corrected panel B (panel A is unchanged in
// the registered v1 PNG), and the muon route is drawn in orange rather than
// v1 purple because the v1 blue/purple pair fails color-vision-deficiency
// separation.

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const root = resolve(experimentDir, '../..');
const outputPath = resolve(root, 'images/2026-08-09-muon-survival-two-frames-panel-b-v2.svg');
const checkOnly = process.argv.includes('--check');

const result = JSON.parse(readFileSync(resolve(experimentDir, 'results/summary.json'), 'utf8'));
if (result.experiment !== 'muon-survival-two-frames') throw new Error('figure input identity mismatch');
const focal = result.focal;

// Shortest round-trip decimal strings, so the printed values are the stored
// binary64 values, not a rounding that makes agreement look cleaner. The
// seconds-to-microseconds conversion shifts the decimal point in the string
// rather than multiplying, so no digit is lost to float rounding.
const full = (v) => String(v);
const micro = (seconds) => {
  const s = full(seconds);
  if (!/^0\.\d+$/.test(s)) throw new Error(`unexpected seconds format: ${s}`);
  const digits = s.slice(2).padEnd(6, '0');
  const head = digits.slice(0, 6).replace(/^0+(?=\d)/, '');
  const tail = digits.slice(6);
  return tail.length ? `${head}.${tail}` : head;
};

const detector = {
  color: '#005ea8',
  title: 'detector frame',
  route: 't_D / (γτ₀)',
  lines: [
    `laboratory path  ${(focal.detector.laboratory_distance_m / 1000).toFixed(1)} km`,
    `elapsed time  ${micro(focal.detector.elapsed_time_s)} µs`,
    `mean lifetime  γτ₀ = ${micro(focal.detector.mean_lifetime_s)} µs`,
    `stored exponent  ${full(focal.detector.decay_exponent)}`,
  ],
  exponent: focal.detector.decay_exponent,
};
const muon = {
  color: '#c25e00',
  title: 'muon frame',
  route: 't_M / τ₀',
  lines: [
    `contracted path  ${full(focal.muon.contracted_distance_m)} m`,
    `elapsed time  ${micro(focal.muon.elapsed_time_s)} µs`,
    `mean lifetime  τ₀ = ${micro(focal.muon.mean_lifetime_s)} µs`,
    `stored exponent  ${full(focal.muon.decay_exponent)}`,
  ],
  exponent: focal.muon.decay_exponent,
};

const W = 1200;
const H = 630;
const axisY = 560;
const axisX0 = 90;
const axisX1 = W - 60;
const expMin = 0.72;
const expMax = 0.88;
const xOf = (e) => axisX0 + ((e - expMin) / (expMax - expMin)) * (axisX1 - axisX0);
const ink = '#111111';
const grid = '#d9d9d9';
const mono = 'DejaVu Sans Mono, Menlo, Consolas, monospace';
const sans = 'DejaVu Sans, Arial, Helvetica, sans-serif';

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

function routeCard(frame, x, y, letter) {
  const lineHeight = 30;
  const parts = [
    `<text x="${x}" y="${y}" font-family="${sans}" font-size="15" font-weight="bold" fill="${ink}">${letter}</text>`,
    `<circle cx="${x + 30}" cy="${y - 5}" r="7" fill="${frame.color}"/>`,
    `<text x="${x + 44}" y="${y}" font-family="${sans}" font-size="19" font-weight="bold" fill="${ink}">${esc(frame.title)}</text>`,
    `<text x="${x + 44}" y="${y + 24}" font-family="${mono}" font-size="15" fill="${ink}">${esc(frame.route)}</text>`,
  ];
  frame.lines.forEach((line, i) => {
    parts.push(`<text x="${x}" y="${y + 58 + i * lineHeight}" font-family="${mono}" font-size="16" fill="${ink}">${esc(line)}</text>`);
  });
  return parts.join('\n');
}

const ticks = [0.72, 0.76, 0.8, 0.84, 0.88];
const tickMarks = ticks.map((t) => [
  `<line x1="${xOf(t)}" y1="120" x2="${xOf(t)}" y2="${axisY}" stroke="${grid}" stroke-width="1"/>`,
  `<line x1="${xOf(t)}" y1="${axisY}" x2="${xOf(t)}" y2="${axisY + 6}" stroke="${ink}" stroke-width="1"/>`,
  `<text x="${xOf(t)}" y="${axisY + 26}" font-family="${sans}" font-size="14" fill="${ink}" text-anchor="middle">${t.toFixed(3)}</text>`,
].join('\n')).join('\n');

const xd = xOf(detector.exponent);
const xm = xOf(muon.exponent);
const yd = 200;
const ym = 420;

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Corrected panel B: both frame routes printed beside aligned decay-exponent markers">
<rect width="${W}" height="${H}" fill="#ffffff"/>
${tickMarks}
<text x="${(axisX0 + axisX1) / 2}" y="${axisY + 54}" font-family="${sans}" font-size="16" fill="${ink}" text-anchor="middle">Dimensionless decay exponent at the focal path</text>
<line x1="${axisX0}" y1="${axisY}" x2="${axisX1}" y2="${axisY}" stroke="${ink}" stroke-width="1.4"/>
<line x1="${xd}" y1="${yd}" x2="${xm}" y2="${ym}" stroke="#777777" stroke-width="1.4"/>
<circle cx="${xd}" cy="${yd}" r="11" fill="${detector.color}" stroke="#ffffff" stroke-width="2"/>
<rect x="${xm - 9}" y="${ym - 9}" width="18" height="18" transform="rotate(45 ${xm} ${ym})" fill="${muon.color}" stroke="#ffffff" stroke-width="2"/>
<text x="${xd}" y="${yd - 22}" font-family="${mono}" font-size="15" fill="${ink}" text-anchor="middle">${esc(full(detector.exponent))}</text>
<text x="${xm}" y="${ym + 36}" font-family="${mono}" font-size="15" fill="${ink}" text-anchor="middle">${esc(full(muon.exponent))}</text>
<text x="${(xd + xm) / 2 + 16}" y="${(yd + ym) / 2 + 5}" font-family="${sans}" font-size="15" font-weight="bold" fill="${ink}">C</text>
${routeCard(detector, 100, 150, 'A')}
${routeCard(muon, 100, 370, 'B')}
</svg>
`;

if (checkOnly) {
  if (readFileSync(outputPath, 'utf8') !== svg) {
    console.error(`${relative(root, outputPath)} is missing or stale`);
    process.exit(1);
  }
} else {
  writeFileSync(outputPath, svg);
}
