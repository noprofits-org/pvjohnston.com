# Blog authoring conventions

The single source of truth for producing a note on pvjohnston.com. Read this
before drafting and follow it so every post comes out consistently. Pipeline order: **research → draft →
bib → figures → hero/OG → branch → verify → PR → merge → auto-deploy.**

---

## 1. Front matter

YAML only. The template renders the title, date, byline, and tags — do **not**
repeat them as an in-body `# H1`, byline line, or tags line.

```yaml
---
title: "Colon-bearing titles must be quoted"
date: 2026-07-06
author: Peter Johnston
tags: quantum chemistry, spectroscopy      # comma-separated
description: One or two sentences. Used for meta description and social cards.
og-image: /images/YYYY-MM-DD-post-slug-hero.png   # optional; see §5
---
```

- **Title:** quote if it contains a colon or other YAML-significant punctuation.
- **Links:** use site-relative URLs for other notes in this repository.

## 2. Voice

Prose, not bullet lists. Section headers with `##`. Bold key terms on first use.
Em-dashes are fine and characteristic. Lead with a concrete, slightly
contrarian hook. Close by tying back to the series or the concrete problem that
opened the note.

## 3. Citations — two conventions, pick by series

Every post is compiled through the Pandoc citation pipeline
(`lib/Blog/Compilers.hs` → `readPandocBiblio` with `bib/style.csl` +
`bib/bibliography.bib`), so `[@key]` works anywhere. Choose the convention that
fits the kind of note:

- **Science / academic notes** — Pandoc citations: `[@Halkier1999]`, rendered
  into a numbered reference list via the shared bibliography.
- **Software, art, and personal notes** — inline Markdown hyperlinks when a
  formal reference list would add more ceremony than value.

Do **not** use markdown footnotes (`[^1]`) — that matches neither.

## 4. Bibliography (`bib/bibliography.bib`) — append-only

Shared 200 KB+ file, and often edited by another session at the same time.
Rules:

1. **Append only.** Add new `@entries` at the end. Never reformat, reorder, or
   rewrite existing entries.
2. **One writer at a time.** If another agent has uncommitted changes to this
   file, don't touch it — coordinate first.
3. **Key scheme:** `AuthorYYYYword` (e.g. `Gregory2009Starvation`,
   `Tinkelman2006Donations`). Before adding, grep the file for the surname AND
   the year to confirm it isn't already present under a different key — common
   surnames produce false-positive substring matches, so verify the actual
   entry, not just the string.
4. Only add entries when the note uses the academic `[@key]` convention.

## 5. Figures & the hero image

**File & embed.** PNG in `/images/`, named with the post slug
(`2026-07-06-the-overhead-myth-hero.png`). Embed as:

```html
<figure>
  <img src="/images/NAME.png" alt="Detailed, meaningful description of what the figure shows and argues.">
</figure>
```

Alt text is a real sentence describing the concept, not "figure 1."

**House illustration style.** Flat vector, bold uniform midnight outlines,
limited palette, baked-in UPPERCASE condensed-sans labels (the generator drops
free text, so add captions in a type layer afterward). Two proven layouts: a
node-cycle (icons in outlined circles joined by a clockwise arrow ring) or a
two-panel / side-by-side scene with a heading. Personal-site palette:

| Role | Hex |
| --- | --- |
| Outline / ink | `#1a1d2b`, `#232a48` |
| Indigo (fills) | `#465c9b`, lifted `#8fa5e3`, deep `#2f417a` |
| Cream (fills / labels) | `#f5f2ea`, `#fbfaf6` |

Keep explanatory graphics high-contrast and legible in print as well as on
screen.

**Text inside data figures: lettered callouts only, never sentences.** Mark
each feature worth explaining with a bold letter (A, B, C…) placed at the
feature, and define every letter in the numbered caption (§6) — ACS style.
Axis labels, tick text, and legend entries are the only other text allowed in
the plot area; values, names, and explanations all go to the caption. If a
chart clips or piles a heavy tail, mark the overflow bins visually (detached
bars in the lifted teal, tick labels like "≤ −6" / "> 36"), letter them, and
let the caption say what they collect.

**Hero = Figure 1 = the social card.** Author Figure 1 at **1200×630 (1.91:1
landscape)** so the same asset serves as both the in-post hero and the OG/Twitter
card — no separate variant, no crop. Compose horizontally (e.g. a left-to-right
loop, or side-by-side panels) rather than square. Then set `og-image` in front
matter to that file. Posts without `og-image` fall back to the generic branded
card (`/images/og-image.png`), so always set it going forward. (Backfill older
posts by setting `og-image` to a 1200×630 crop/reframe of their existing figure.)

## 6. Captions & numbering (required)

**Every figure, table, and code block gets a numbered caption, and every one is
referenced by number somewhere in the prose.** No exceptions — an uncaptioned or
unreferenced element is a bug.

- **Numbering** runs independently per type, in document order: Figure 1, 2, 3…;
  Table 1, 2…; Code 1, 2…. A post can have Figure 1 and Table 1 and Code 1.
- **Format:** the caption label is **bold** for all three types, followed by a
  full sentence (not a bare label):
  - Figures — `**Figure 1.** Sentence describing what it shows.` directly
    **below** the `<figure>`.
  - Tables — `**Table 1.** Sentence describing the table.` directly **below**
    the table.
  - Code blocks — `**Code 1.** Sentence describing what the code does.` directly
    **below** the fenced block.
  - (Older posts used italic `*Figure N.*` / `*Table N.*` — that was a mistake;
    bold is the standard. Normalize when touching an old post.)
- **Cross-reference:** point to each numbered element at least once in the body
  by its number — "(Figure 1)", "as Table 2 shows", "the loop in Code 1". If
  there's no natural place to reference it, it probably doesn't belong in the
  post.
- Figure 1 is still the hero / OG card (§5).

## 7. Deploy flow

`.github/workflows/deploy.yml` builds the Hakyll site with Stack and publishes to
GitHub Pages on **push to `main`** (also PR-to-main and manual dispatch). So:

1. Work on a feature branch (`post/<slug>`), never commit straight to `main`.
2. **Verify before merge:** `stack build && stack exec site build && node scripts/verify-site.mjs` must succeed;
   check the post renders, citations resolve, figures load, and the card meta is
   right.
3. Open a PR into `main`; merge triggers the deploy.

The verification script rejects missing internal assets/links and any generated
`tikz-error` box, because a green Hakyll exit alone does not prove every diagram
compiled.

## 8. Per-post checklist

- [ ] Front matter complete; title quoted if needed; links relative
- [ ] Voice matches the series and opens with a concrete problem
- [ ] Citations in the correct convention for the series
- [ ] New bib entries appended (science posts only), keys unique & de-duped
- [ ] Figure 1 authored at 1200×630 in house style; `<figure>` + alt text
- [ ] Every figure, table, and code block has a numbered caption (Figure/Table/Code N) and is referenced by number in the prose
- [ ] `og-image` set to the hero
- [ ] Cross-links to the rest of the series
- [ ] Branch, build, verification, PR, and merge complete
