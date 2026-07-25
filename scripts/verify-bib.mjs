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
// (2026-07-24), with the number of entries each currently has. Adding another
// copy of one of these fails exactly like a new duplicate; resolving one means
// lowering or deleting its line here.
//
// Five are the same work re-entered by different sessions, so which entry
// citeproc picks does not change what the reader sees. TWO ARE NOT, and are
// live citation bugs rather than untidiness:
//
//   Jacquemin2009  two different papers — J. Chem. Theory Comput. 4(1), 123
//                  (2008), doi 10.1021/ct700187z, and 5(9), 2420 (2009),
//                  doi 10.1021/ct900298e. Cited by 2 posts.
//   Jensen2017     two different works — the Wiley book *Introduction to
//                  Computational Chemistry* and the WIREs Comput. Mol. Sci.
//                  article *Atomic orbital basis sets*. Cited by 7 posts.
//
// Those two need distinct keys and their citations repointed, which is an
// editorial change to published posts and belongs in its own PR. They are
// listed here so this check can run at all — not because the collision is
// acceptable.
const GRANDFATHERED = {
  Jacquemin2009: 2, // distinct works — see above
  Jensen2017: 3, // distinct works — see above
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

// Leading whitespace before @ is legal BibTeX and the file already contains one
// such entry (` @misc{wiki:bbo,`); an anchored /^@/ would silently skip it, so a
// duplicate of an indented entry would pass unnoticed.
for (const match of source.matchAll(/^[ \t]*@([A-Za-z]+)\s*\{\s*([^,\s{}]+)\s*,/gm)) {
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
