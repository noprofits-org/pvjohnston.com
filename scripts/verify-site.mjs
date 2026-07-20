import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';

const root = resolve('_site');
const errors = [];

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const file = join(dir, name);
    return statSync(file).isDirectory() ? walk(file) : [file];
  });
}

function targetExists(base, clean) {
  if (clean === '/' || clean === '') return existsSync(join(base, 'index.html'));
  if (existsSync(base)) return true;
  if (clean.endsWith('/')) return existsSync(join(base, 'index.html'));
  if (!extname(clean)) {
    return existsSync(`${base}.html`) || existsSync(join(base, 'index.html'));
  }
  return false;
}

if (!existsSync(root)) {
  console.error('verify-site: _site does not exist; run the build first');
  process.exit(1);
}

const htmlFiles = walk(root).filter((file) => file.endsWith('.html'));
const postFiles = htmlFiles.filter((file) => dirname(file) === join(root, 'posts'));

const metricFixture = {
  page: 'posts/2026-07-20-from-script-to-sentence.html',
  expected: {
    incident_refractive_index: '1.0',
    transmitted_refractive_index: '1.5',
    sweep_start_angle_deg: '0',
    sweep_stop_angle_deg: '80',
    sweep_step_angle_deg: '0.1',
    index_ratio: '1.5',
    analytic_brewster_angle_deg: '56.31',
    grid_minimum_angle_deg: '56.3',
    grid_angle_error_deg: '0.010',
    normal_incidence_reflectance: '4.00%',
    analytic_p_reflectance: '4.5×10⁻³³',
    analytic_s_reflectance: '14.79%',
    analytic_unpolarized_reflectance: '7.40%',
    grid_minimum_p_reflectance: '1.1×10⁻⁸',
    maximum_energy_balance_error: '5.6×10⁻¹⁶',
    analytic_p_reflectance_tolerance: '1.0×10⁻²⁴',
    grid_angle_tolerance_deg: '0.05',
    energy_balance_tolerance: '1.0×10⁻¹²',
    sweep_sample_count: '801',
    analytic_null_within_tolerance: 'true',
    grid_angle_within_tolerance: 'true',
    energy_balance_within_tolerance: 'true',
  },
};

// Guard against a build that silently drops the post pipeline, without
// hard-coding an exact count that has to be bumped on every new post.
if (postFiles.length === 0) {
  errors.push('no published posts found in _site/posts — the post pipeline produced nothing');
}

const metricPagePath = join(root, metricFixture.page);
if (!existsSync(metricPagePath)) {
  errors.push(`${metricFixture.page}: traceable-metrics fixture page is missing`);
} else {
  const html = readFileSync(metricPagePath, 'utf8');
  const rendered = new Map();
  for (const match of html.matchAll(/<span\b([^>]*)>([^<]*)<\/span>/g)) {
    const attributes = match[1];
    const classes = attributes.match(/\bclass="([^"]*)"/)?.[1].split(/\s+/) || [];
    const metric = attributes.match(/\bdata-metric="([^"]+)"/)?.[1];
    if (classes.includes('metric-value') && metric) rendered.set(metric, match[2]);
  }
  for (const [metric, expected] of Object.entries(metricFixture.expected)) {
    if (!rendered.has(metric)) {
      errors.push(`${metricFixture.page}: missing rendered metric ${metric}`);
    } else if (rendered.get(metric) !== expected) {
      errors.push(
        `${metricFixture.page}: ${metric} rendered as ${JSON.stringify(rendered.get(metric))}, expected ${JSON.stringify(expected)}`,
      );
    }
  }
  for (const metric of rendered.keys()) {
    if (!(metric in metricFixture.expected)) {
      errors.push(`${metricFixture.page}: unexpected rendered metric ${metric}`);
    }
  }
}

for (const file of htmlFiles) {
  const html = readFileSync(file, 'utf8');
  const label = file.slice(root.length + 1);

  if (html.includes('class="tikz-error"')) {
    errors.push(`${label}: contains a failed TikZ diagram`);
  }

  const hasUnresolvedMetric = [...html.matchAll(/class="([^"]*)"/g)]
    .some((match) => match[1].split(/\s+/).includes('metric'));
  if (hasUnresolvedMetric) {
    errors.push(`${label}: contains an unresolved experiment metric`);
  }

  const canonical = html.match(/<link rel="canonical" href="([^"]+)"/);
  if (canonical && !canonical[1].startsWith('https://pvjohnston.com/')) {
    errors.push(`${label}: wrong canonical ${canonical[1]}`);
  }

  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const url = match[1];
    // Skip external (scheme:), protocol-relative (//), and fragment-only (#) links.
    // Everything else is internal — including the ../ and ./ forms that relativizeUrls
    // produces, which the old /-only filter silently skipped.
    if (/^([a-z][a-z0-9+.-]*:|\/\/|#)/i.test(url)) continue;
    const clean = decodeURI(url.split('#')[0].split('?')[0]);
    const base = clean.startsWith('/')
      ? join(root, clean.replace(/^\//, ''))
      : resolve(dirname(file), clean);
    if (!targetExists(base, clean)) {
      errors.push(`${label}: missing internal target ${url}`);
    }
  }
}

if (errors.length) {
  console.error(`verify-site: ${errors.length} problem(s)`);
  for (const error of [...new Set(errors)]) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`verify-site: ${htmlFiles.length} HTML pages, ${postFiles.length} posts, all internal targets present, no TikZ errors`);
