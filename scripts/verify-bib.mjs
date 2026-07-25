// Guards bib/bibliography.bib against duplicate citation keys.
//
// The file is append-only and shared by concurrent sessions
// (notes/blog-authoring.md §4, notes/worktrees.md §3). .gitattributes marks it
// merge=union so two branches appending at the end never conflict; the cost of
// that choice is that nothing stops both branches from appending the same
// source under the same key. This check is the other half of that trade.
//
// Duplicate keys are not loud. Pandoc's citeproc resolves [@key] against one of
// the entries and silently ignores the rest, so a post can cite the wrong
// volume, year, or author list of the right paper and still build green.
//
// Runs without a site build. Source-level only: it does not detect the same
// source appended twice under two different keys, which remains what §4 rule 3
// (grep for the author AND the year before appending) is there to prevent.

import { readFileSync } from 'node:fs';

const bibFile = 'bib/bibliography.bib';

// Keys that were already duplicated when this check was introduced
// (2026-07-24), with the number of entries each currently has. They are
// re-entries of one source by different sessions, not distinct works. Adding
// another copy of one of these fails exactly like a new duplicate; resolving
// one means lowering or deleting its line here.
const GRANDFATHERED = {
  Jacquemin2009: 2,
  Jensen2017: 3,
  Laurent2013: 2,
  Marques2012: 2,
  Maroulis1996: 2,
  Parrish2017: 3,
  Smith2020: 2,
};

// @string, @preamble, and @comment carry no citation key.
const NON_ENTRY_TYPES = new Set(['string', 'preamble', 'comment']);

const source = readFileSync(bibFile, 'utf8');
const errors = [];
const counts = new Map();

for (const match of source.matchAll(/^@([A-Za-z]+)\s*\{\s*([^,\s{}]+)\s*,/gm)) {
  const [, type, key] = match;
  if (NON_ENTRY_TYPES.has(type.toLowerCase())) continue;
  counts.set(key, (counts.get(key) || 0) + 1);
}

if (counts.size === 0) {
  console.error(`verify-bib: no entries parsed from ${bibFile}`);
  process.exit(1);
}

for (const [key, count] of [...counts].sort(([a], [b]) => a.localeCompare(b))) {
  const allowed = GRANDFATHERED[key] || 1;
  if (count > allowed) {
    errors.push(
      key in GRANDFATHERED
        ? `${key}: ${count} entries, ${allowed} grandfathered — do not add more copies of an already-duplicated key`
        : `${key}: ${count} entries — duplicate citation key; keep one entry and cite it, or give the new source its own key`,
    );
  }
}

// Keep the baseline honest: a resolved duplicate must shrink the list above,
// otherwise it silently re-licenses the duplicate for the next session.
for (const [key, allowed] of Object.entries(GRANDFATHERED)) {
  const count = counts.get(key) || 0;
  if (count < allowed) {
    errors.push(
      `${key}: ${count} entries but ${allowed} grandfathered — duplicate resolved; ` +
        `${count > 1 ? `lower it to ${count}` : 'remove the entry'} in scripts/verify-bib.mjs`,
    );
  }
}

// Distinct keys differing only in case are legal BibTeX and near-invisible in
// review; treat them as the collision they are.
const byLowercase = new Map();
for (const key of counts.keys()) {
  const lower = key.toLowerCase();
  if (!byLowercase.has(lower)) byLowercase.set(lower, []);
  byLowercase.get(lower).push(key);
}
for (const [, variants] of byLowercase) {
  if (variants.length > 1) {
    errors.push(`${variants.sort().join(', ')}: keys differ only by case — pick one`);
  }
}

if (errors.length) {
  console.error(`verify-bib: ${errors.length} problem(s) in ${bibFile}`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

const total = [...counts.values()].reduce((sum, count) => sum + count, 0);
console.log(
  `verify-bib: ${total} entries, ${counts.size} unique keys, no new duplicates`,
);
