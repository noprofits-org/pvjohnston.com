import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { extname, join, relative, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const root = resolve('.');
const researchRoot = resolve(root, 'research');
const errors = [];
let checked = 0;
const generatorTimeoutMs = 30_000;

try {
  JSON.parse(readFileSync(join(researchRoot, 'metrics.schema.json'), 'utf8'));
} catch (error) {
  errors.push(`research/metrics.schema.json: invalid JSON (${error.message})`);
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function safeRepositoryPath(path) {
  return typeof path === 'string'
    && path.length > 0
    && !path.startsWith('/')
    && !path.includes('\\')
    && !path.split('/').includes('..')
    && !/\s/.test(path);
}

function generatorCommand(path) {
  switch (extname(path)) {
    case '.mjs':
    case '.js':
      return ['node', path, '--check'];
    case '.py':
      return ['python3', path, '--check'];
    case '.sh':
      return ['bash', path, '--check'];
    default:
      return null;
  }
}

for (const name of readdirSync(researchRoot)) {
  const directory = join(researchRoot, name);
  const metricsPath = join(directory, 'metrics.json');
  if (!statSync(directory).isDirectory() || !existsSync(metricsPath)) continue;

  checked += 1;
  const metricsHashBefore = sha256(metricsPath);
  let document;
  try {
    document = JSON.parse(readFileSync(metricsPath, 'utf8'));
  } catch (error) {
    errors.push(`${relative(root, metricsPath)}: invalid JSON (${error.message})`);
    continue;
  }

  if (document.experiment !== name) {
    errors.push(`${relative(root, metricsPath)}: experiment must match directory name ${name}`);
  }

  const provenance = document.provenance;
  if (!provenance || !Array.isArray(provenance.inputs)) {
    errors.push(`${relative(root, metricsPath)}: missing provenance inputs`);
    continue;
  }

  for (const input of provenance.inputs) {
    if (!input || !safeRepositoryPath(input.path)) {
      errors.push(`${relative(root, metricsPath)}: unsafe provenance input path`);
      continue;
    }
    const inputPath = resolve(root, input.path);
    if (!existsSync(inputPath)) {
      errors.push(`${relative(root, metricsPath)}: missing provenance input ${input.path}`);
      continue;
    }
    const actual = sha256(inputPath);
    if (actual !== String(input.sha256).toLowerCase()) {
      errors.push(`${relative(root, metricsPath)}: SHA-256 mismatch for ${input.path}`);
    }
  }

  if (!provenance.generator || !safeRepositoryPath(provenance.generator)) {
    errors.push(`${relative(root, metricsPath)}: unsafe or missing provenance generator`);
    continue;
  }
  const generatorPath = resolve(root, provenance.generator);
  if (!existsSync(generatorPath)) {
    errors.push(`${relative(root, metricsPath)}: missing generator ${provenance.generator}`);
    continue;
  }
  const command = generatorCommand(provenance.generator);
  if (!command) {
    errors.push(`${relative(root, metricsPath)}: unsupported generator type ${extname(generatorPath)}`);
    continue;
  }
  const result = spawnSync(command[0], command.slice(1), {
    cwd: root,
    encoding: 'utf8',
    timeout: generatorTimeoutMs,
  });
  if (result.error) {
    const timedOut = result.error.code === 'ETIMEDOUT';
    errors.push(
      `${relative(root, metricsPath)}: generator check ${timedOut ? `timed out after ${generatorTimeoutMs / 1000}s` : `could not run (${result.error.message})`}`,
    );
  } else if (result.status !== 0) {
    const detail = (result.stderr || result.stdout || '').trim();
    const signal = result.signal ? ` (signal ${result.signal})` : '';
    errors.push(`${relative(root, metricsPath)}: generator check failed${signal}${detail ? ` (${detail})` : ''}`);
  }
  if (!existsSync(metricsPath)) {
    errors.push(`${relative(root, metricsPath)}: generator check removed metrics.json`);
  } else if (sha256(metricsPath) !== metricsHashBefore) {
    errors.push(`${relative(root, metricsPath)}: generator check modified metrics.json`);
  }
}

if (errors.length) {
  console.error(`verify-metrics: ${errors.length} problem(s)`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`verify-metrics: ${checked} generated metrics artifact(s), inputs and projections current`);
