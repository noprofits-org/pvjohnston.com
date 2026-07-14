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

// Guard against a build that silently drops the post pipeline, without
// hard-coding an exact count that has to be bumped on every new post.
if (postFiles.length === 0) {
  errors.push('no published posts found in _site/posts — the post pipeline produced nothing');
}

for (const file of htmlFiles) {
  const html = readFileSync(file, 'utf8');
  const label = file.slice(root.length + 1);

  if (html.includes('class="tikz-error"')) {
    errors.push(`${label}: contains a failed TikZ diagram`);
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
