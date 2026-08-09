#!/usr/bin/env node

// Copy to generate-metrics.mjs and replace the example projection with values
// derived from canonical experiment outputs. Preserve generated_at during
// --check so validation is deterministic; do not hand-author metrics.json.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const outputPath = resolve(experimentDir, 'metrics.json');
const input = 'research/example-experiment/results/summary.json';
const checkOnly = process.argv.includes('--check');

const sha256 = (path) => createHash('sha256')
  .update(readFileSync(resolve(root, path)))
  .digest('hex');

function build(generatedAt) {
  const result = JSON.parse(readFileSync(resolve(root, input), 'utf8'));
  return {
    schema_version: 1,
    experiment: 'example-experiment',
    provenance: {
      generated_at: generatedAt,
      generator: relative(root, fileURLToPath(import.meta.url)),
      inputs: [{ path: input, sha256: sha256(input) }],
    },
    metrics: {
      accepted: {
        type: 'integer',
        value: result.accepted,
        description: 'Accepted responses',
        unit: 'responses',
      },
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
