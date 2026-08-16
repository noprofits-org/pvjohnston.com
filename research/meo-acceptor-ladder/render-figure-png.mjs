#!/usr/bin/env node

// Render the inline-SVG figure in results/figure_frontier_levels.html to a PNG
// using Google Chrome headless. The PNG is the hero image referenced by the
// post's front-matter `figure:` field.

import { existsSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const htmlPath = resolve(experimentDir, 'results/figure_frontier_levels.html');
const pngPath = resolve(experimentDir, '..', '..', 'images',
                        '2026-08-16-how-the-acceptor-closes-the-gap-figure.png');

if (!existsSync(htmlPath)) {
  console.error(`${htmlPath} does not exist; run make-figure.mjs first`);
  process.exit(1);
}

const snippet = readFileSync(htmlPath, 'utf8');

// Wrap the snippet in a minimal page that supplies the CSS variables the
// snippet references, with the same values used by the live site.
const page = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
:root {
  --accent: #465C9B;
  --terracotta: #B76842;
  --offwhite: #f8f7f4;
  --border: #e0ddd4;
  --border-strong: #c8c4b8;
  --text: #1f1f1f;
  --faint: #7a7a7a;
  --muted: #8a8a8a;
  --slate: #5a5a5a;
}
body {
  margin: 0;
  padding: 40px;
  background: var(--offwhite);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  box-sizing: border-box;
}
</style>
</head>
<body>
${snippet}
</body>
</html>
`;

const tmpDir = mkdtempSync(resolve(tmpdir(), 'fig-render-'));
const tmpHtml = resolve(tmpDir, 'figure.html');
writeFileSync(tmpHtml, page);

const chrome = process.env.CHROME_BIN || '/usr/bin/google-chrome';

// 1100 x 660 matches the donor-post hero PNG dimensions.
execFileSync(chrome, [
  '--headless',
  '--disable-gpu',
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--hide-scrollbars',
  `--window-size=1100,660`,
  `--screenshot=${pngPath}`,
  `file://${tmpHtml}`,
], { stdio: 'inherit' });

console.log(`wrote ${pngPath}`);
