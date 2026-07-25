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
// None of these is untidiness. Every one of them can already put a wrong
// reference in front of a reader, in one of two ways.
//
// Two keys resolve to DIFFERENT WORKS, so citeproc can name the wrong paper:
//
//   Jacquemin2009  two different papers — J. Chem. Theory Comput. 4(1), 123
//                  (2008), doi 10.1021/ct700187z, and 5(9), 2420 (2009),
//                  doi 10.1021/ct900298e. Cited by 2 posts.
//   Jensen2017     two different works — the Wiley book *Introduction to
//                  Computational Chemistry* and the WIREs Comput. Mol. Sci.
//                  article *Atomic orbital basis sets*. Cited by 7 posts.
//
// The other five are one work entered twice or three times, but with metadata
// that DIVERGES, so citeproc's pick still changes the rendered reference:
//
//   Parrish2017    three entries; one records number = {6} for a paper
//                  published in JCTC 13(7). Author lists of 11, 24, and 11.
//   Marques2012    an @article (Lecture Notes in Physics 837, with doi) and an
//                  @book (Springer) — different entry types render differently.
//   Smith2020      materially different author lists; the first entry's list
//                  carries names that are not on the paper.
//   Maroulis1996   "Maroulis, George" vs "Maroulis, G", differing title case,
//                  doi on one entry only.
//   Laurent2013    differing title case and publisher field. Mildest of the
//                  five, and still a divergence.
//
// Resolving either kind means repointing citations in published posts — for the
// first two, deciding per post which work was meant — so it is an editorial
// change and belongs in its own PR. They are listed here so this check can run
// at all, NOT because any of these collisions is acceptable.
const GRANDFATHERED = {
  Jacquemin2009: 2, // distinct works — see above
  Jensen2017: 3, // distinct works — see above
  Laurent2013: 2, // divergent metadata — see above
  Marques2012: 2, // divergent metadata — see above
  Maroulis1996: 2, // divergent metadata — see above
  Parrish2017: 3, // divergent metadata — see above
  Smith2020: 2, // divergent metadata — see above
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
