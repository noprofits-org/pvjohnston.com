# Blog authoring conventions

The single source of truth for producing a note on pvjohnston.com. Read this
before drafting and follow it so every post comes out consistently. Pipeline
order: **question → contribution gate → hypothesis → experiment → draft → bib →
figures → branch → verify → PR → merge → auto-deploy.**

**Every post is an experiment.** There is no second class of post here — no
explainer, no tutorial, no roundup. A note that tests nothing is not published,
however well it reads.

---

## 0. Before you draft — the question, and what it contributes

**The bottleneck is not writing. It is question supply.** Nobody finds a novel
question on demand at 9pm, and a post that starts from a *topic* instead of a
*question* will restate what is already known — fluently, and pointlessly. That
is the machine that produces triviality, and no amount of structure downstream
will stop it. Real labs do not invent a hypothesis on the day they write; they
keep a backlog of things that do not add up, and pull from it.

So `notes/questions.md` is the shelf. **Nothing gets drafted that was not sitting
on the shelf first.** Entries come from three places, all three already proven
here:

- **Anomalies.** Anything that did not reproduce, did not match, or surprised
  you. Log it the moment it happens, *before* you have an explanation — the
  explanation is the post. The Neumaier finding sat for a day underneath the
  sentence "I cannot account for the difference."
- **Standing.** Places where you have a vantage nobody else has: your own
  published work and the methods in it, or data only you can see.
- **Next steps.** Every Conclusion names the next experiment (§2). That sentence
  is a queue entry. This is the loop that makes the blog a research programme
  rather than a series of posts.

**The contribution gate.** Before drafting, write one sentence, and put it in the
post's front matter:

```yaml
contribution: X, which is not in [source].
```

Then name its type from the list below. **If you cannot write that sentence, you
do not have a post** — put the topic back on the shelf and pull another. This
gate is the foundation. Everything else in this document is bookkeeping.

| Type | The move |
| --- | --- |
| **Falsification** | a published claim does not hold |
| **Decay** | a result was true and quietly stopped being true |
| **Unplotted line** | the analysis the source's own data supports, that the source never ran |
| **Quantification** | someone wrote "negligible" and never measured it |
| **Untested regime** | it holds at X — does it hold at Y? |
| **Composition** | two known results nobody has connected |
| **Negative result** | expected X, measured not-X |

Both of this site's genuine contributions came from friction with a *specific
source*, not from choosing a subject: the unplotted regression in "a citation, a
slot, and the line nobody plots" (the source's own data, the author's own error
method), and the Neumaier decay in the temperature-zero note (a number that
refused to reconcile). Neither came from a hook. Anomalies and standing are where
the questions live; go there deliberately.

**What is not novelty:** "I explained a known thing well." Kramers-Kronig has
been understood since 1926. A good explanation of it contributes nothing to
collective knowledge, however well it reads. Exposition is not a lesser post
here — it is not a post here.

**Anchor the hypothesis to a recent primary source — a journal article from this
year or last.** This is the single most reliable way to find a question that is
actually open, and it follows directly from the rule above. A settled result can
only be *explained*; a live one can be *contributed to*. Kramers-Kronig has had a
century of scrutiny and every accessible gap in it is closed. A paper from six
months ago has unpriced claims, unreleased code, and mechanisms asserted but not
measured — because that is what the edge of a literature looks like. Both of this
site's genuine contributions came from 2025–2026 sources; none of its expository
posts could have, because their sources were decades old and there was nothing
left to find.

Recency is necessary, not sufficient: a modern paper still has to yield a
`contribution:` sentence, and "recent" is not a synonym for "unexamined."

**Where the gaps hide in a modern paper.** Read for friction, not for topic:

| Look at | What it yields |
| --- | --- |
| "Future work", "remains an open problem" | gaps the authors named themselves — free targets |
| Hedged mechanisms: "suggests", "likely", "attributed to" | a cause asserted from a citation and never measured |
| Two tables that were never joined | an **unplotted line** — the analysis their own data supports |
| "negligible", "no meaningful difference", "comparable" | an unquantified null |
| Spec in the text vs the code they cite or release | a reimplementation hazard; acute when the code is unreleased |
| A headline number with no tabulated case behind it | an unsourced claim |

Prefer a source whose data or code you can actually reach, and check whether the
code is released before committing — an unreleased repository does not block the
question, but it *bounds* what you may claim, and that boundary belongs in
Methods (§2) from the start rather than being discovered late.

**The honest failure mode.** When the shelf is empty, nothing ships that day. A
gate that cannot fail is not a gate, and the only other way this resolves is
stamping it to protect a streak — which produces precisely the trivial
restatement this section exists to prevent. Breaking the streak is the cheaper
loss.

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
contribution: X, which is not in [source].        # required; see §0
contribution-type: decay                          # required; one of §0's table
og-image: /images/YYYY-MM-DD-post-slug-hero.png   # optional; see §5
---
```

- **Title:** quote if it contains a colon or other YAML-significant punctuation.
- **Links:** use site-relative URLs for other notes in this repository.
- **`contribution` / `contribution-type`:** written *before* drafting, not after
  (§0). They are not rendered — they exist so the gate leaves an artifact in the
  file, where a reviewer can check it against what the post actually did.

## 2. Structure — IMRaD, and voice within it

**Every post uses the IMRaD skeleton**, in this order, as `##` headers:

```
## Abstract
## Introduction
## Computational Methods     (or ## Experimental Methods)
## Results
## Discussion
## Conclusion
## References
```

This is not decoration. We are scientists; the job is to state a hypothesis and
test it, and the format is what keeps us honest about which of those we actually
did. The discipline pays for itself in the Methods and Results sections
specifically: a note that must declare what it ran tends to get run, and a note
that must report what came out tends to catch the thing that didn't reproduce.
Prefer reproducing a published number yourself over quoting it.

- **Abstract** is a real in-body section, distinct from the `description` front
  matter (which is the meta/social card). Don't reuse the same sentences.
- **Introduction** builds the case for the experiment. It is a **funnel, not a
  hook**: what is known (cited) → what that predicts → **the thing that does not
  fit** → therefore the hypothesis → which predicts P. The gap is the
  load-bearing element; it is the reason the experiment exists. If a reader
  reaches Methods without already knowing why you ran it, the Introduction
  failed. Do not open with a contrarian flourish. Open with the state of
  knowledge and walk to the edge of it.
- **The hypothesis must be falsifiable, and its falsifier is stated before
  Results** — in the Introduction or Methods, name the outcome that would kill
  it. Two tests: could it have come out the other way, and **would you have
  published it if it had?** If no outcome would falsify the hypothesis, you have
  an illustration, not an experiment, and §0 has already told you what to do.
- **Methods** must state the environment precisely enough to re-run: interpreter
  or compiler version, architecture, library versions, seeds, exact procedure.
  Write it to be *used* during review, not filed — the 2026-07-16 note's whole
  phantom discrepancy was explained by the version number in its own Methods,
  three paragraphs above, and nobody read it.
- **Anything you did not run yourself must say so, in Methods, in those words,**
  and be attributed at every point of use in Discussion. Reporting someone
  else's result is legitimate; implying you reproduced it is not. If a claim
  needs hardware you don't have, name that as a limitation. Never assert that
  your procedure is equivalent to a source's — *test* the equivalence. The word
  "exactly" is a claim.
- **Results** reports what the machine printed, and nothing else. See below.
- **Discussion** renders the **verdict — supported / falsified / inconclusive, in
  those words** — then relevance (what changes for someone who has to act) and
  limits (what would overturn this). All mechanism, interpretation, and
  speculation lives here. Discrepancies with a source get chased before they get
  reported: check your own Methods first — version, dtype, accumulator, library
  defaults explain most of them. "I cannot account for this" is publishable, but
  only after you have tried; it is a last resort, not a shrug.
- **Conclusion** points **forward, not back**. State what changed in what we
  know, and name the next experiment. Do *not* tie back to the problem that
  opened the note — that is circularity, and it is what an essay does. A post
  with no next step probably opened nothing. The next step goes on the shelf
  (§0).

**There are no exceptions.** Every post is an experiment (see the top of this
document), so every post has Methods and Results. A post that reaches for the
exception is a post that failed §0 and should not be drafted.

**Results are dry.** Every sentence in Results must survive one question: *what
did the machine print?* If the answer is a number, a count, or a range, it is a
result. If the answer is a verdict, it is Discussion. We do not interpret, judge,
confirm, or discuss in Results.

Confirmation is a verdict, so **"confirmed" is a banned word in Results.** So are
*therefore, thus, shows that, which means, matters, worth recording, reconciles,
not marginal, only, merely, artifact*, and any clause beginning *because*.
**Captions are not an exemption** — an interpretive clause in a table caption is
the same violation, better hidden.

This rule previously existed in the abstract form "keep interpretation out of
Results," and it caught nothing: the 2026-07-16 note shipped with a Results
section roughly four-fifths interpretation, written and reviewed by people who
had read that rule the same day. A principle you can nod at and still violate
needs a test. Apply the printed-output test sentence by sentence.

Dry usually means shorter, and often means a table. Prose narrating a
reconciliation is a signal that the reconciliation belongs in Discussion and the
data belongs in a table.

**Voice within the structure.** Prose, not bullet lists. Bold key terms on first
use. Em-dashes are fine and characteristic. The section headers are fixed but the
writing under them is not stiff — ACS research articles read like arguments, not
forms. The argument lives in the Introduction and the Discussion, where it is
allowed to.

## 3. Citations — ACS style, always, no exceptions

Every post is compiled through the Pandoc citation pipeline
(`lib/Blog/Compilers.hs` → `readPandocBiblio` with `bib/style.csl` +
`bib/bibliography.bib`). **`bib/style.csl` is the American Chemical Society
style.** Every external reference in every post goes through it as a `[@key]`
citation resolved against the shared bibliography. There is no second
convention and no "this one's just a blog post" exit.

This rule used to have an escape hatch for "web pages, docs, or tools with no
formal bibliographic identity," which was deleted because it was wrong twice
over. First, ACS specifies formats for exactly these source types — web pages,
software, datasets, preprints, standards — so "no bibliographic identity" is not
a category that exists; it just means you haven't looked up the right ACS format
yet (§4). Second, it invited misclassification: the escape hatch was once used
to inline-link a source that turned out to carry a DOI and ship its own BibTeX
entry. If you are citing it, it has an entry.

**Never mix conventions, and never use markdown footnotes** (`[^1]`) — that
matches neither.

**Marker placement.** Put the `[@key]` marker *after* the sentence punctuation,
and group multiple sources for one sentence into a single bracket at the end of
that sentence (semicolon-separated):

```markdown
…rounds to the nearest representable value.[@IEEE754_2019]
…more accurate than a naïve Python loop.[@Higham2002; @NumpySum]
```

These render as trailing superscripts (`.¹`, `.³ˑ⁵`) under the numeric CSL
style. End the post with a bare `## References` heading and nothing under it —
Pandoc populates the bibliography there at build time; an empty-looking
`## References` in the source is correct, not a stub to fill by hand.

**Internal cross-links to other notes** in this repo stay as site-relative
Markdown links, and **must point at the rendered `.html` target, not the source
`.md`** — Hakyll compiles posts to `.html` and does *not* rewrite the extension
for you, so a `/posts/…-slug.md` link ships as a live 404 (e.g. link to
`/posts/2026-07-04-the-correlation-gap-in-water-measured.html`). These are
navigation, not references, and never go in the bibliography. `relativizeUrls`
turns the leading `/` into a relative `../` at build time — that is expected;
just get the extension right.

## 4. Bibliography (`bib/bibliography.bib`) — append-only

Shared 200 KB+ file, and often edited by another session at the same time.
Rules:

1. **Append only.** Add new `@entries` at the end. Never reformat, reorder, or
   rewrite existing entries.
2. **One writer at a time.** If another agent has uncommitted changes to this
   file, don't touch it — coordinate first.
3. **Key scheme:** for authored works, `AuthorYYYY` with an optional trailing
   word (`Goldberg1991`, `Gregory2009Starvation`, `He2025Nondeterminism`). For
   sources with no clear author or year — standards, vendor docs, tool/library
   doc pages cited via `@misc` — use a short descriptive PascalCase key instead
   (`GccFPMath`, `NumpySum`, `IEEE754_2019`). Before adding, grep the file for
   the author/name AND the year to confirm it isn't already present under a
   different key — common surnames produce false-positive substring matches, so
   verify the actual entry, not just the string.
4. **Every source a post cites gets an entry** (§3). There is no class of source
   that skips the bibliography.
5. **Check whether the source publishes its own citation** before writing one.
   Journals, preprint servers, and an increasing number of research blogs ship a
   BibTeX block or a DOI; use it rather than inventing an entry, and prefer the
   authors' own choice of entry type and venue name.

**ACS formats by source type.** ACS specifies all of these; pick by what the
source *is*, and always include an access date for anything that can change
under you.

| Source | Entry | Required fields beyond title/author |
| --- | --- | --- |
| Journal article | `@article` | `journal`, `year`, `volume`, `pages`, `doi` |
| Book | `@book` | `publisher`, `address`, `year`; `edition` if not 1st |
| Chapter in edited book | `@incollection` | `booktitle`, `editor`, `publisher`, `year`, `pages` |
| Preprint | `@misc` | `eprint`, `archiveprefix`, `year`, `doi` if issued |
| Standard | `@misc` | issuing body as `author`, designation in `title`, `year` |
| Web page / research blog | `@online` | `organization` (site name), `year`, `month`, `url`, `note={accessed YYYY-MM-DD}` |
| Software / repository | `@misc` | `version` if tagged, `url`, `note={accessed …}` |
| Dataset | `@misc` | `publisher` (repository), `doi` or `url`, `year` |
| Thesis | `@phdthesis` / `@thesis` | `school`, `year`, `type` |
| Conference talk / poster | `@inproceedings` | `booktitle` (meeting name), `address`, `year` |

**Table 0.** ACS-mapped BibTeX entry types by source type. A research blog post
that carries a DOI is an `@article` with the blog as `journal` — follow the
source's own citation block when it provides one (rule 5).

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

**Figures are optional and must earn their place.** A post with something to show
makes one; a post whose argument is a table does not manufacture one. Seven
consecutive posts have shipped without a figure and were not worse for it — this
was a mandate that the work quietly voted against, and a rule nobody follows
teaches you to skim the ones that matter.

**If you make one: hero = Figure 1 = the social card.** Author Figure 1 at
**1200×630 (1.91:1 landscape)** so the same asset serves as both the in-post hero
and the OG/Twitter card — no separate variant, no crop. Compose horizontally
(e.g. a left-to-right loop, or side-by-side panels) rather than square. Then set
`og-image` in front matter to that file. Posts without `og-image` fall back to
the generic branded card (`/images/og-image.png`), which is a fine outcome, not a
defect.

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

**If you author in a sandbox and cannot run the build,** the orchestrator/human
runs §7's build + verify before merge — but a missing citation will not fail the
build loudly: a `[@key]` with no matching bib entry silently renders as `[?]`.
So do this build-free self-check before handing off, and call out in your summary
that the build still needs to run:

1. For **every** `[@key]` you used, grep `bib/bibliography.bib` and confirm a
   matching entry exists (`grep '{Higham2002,' bib/bibliography.bib`). New
   entries you appended count; typos and forgotten entries are the failure mode.
2. Confirm the post ends with a bare `## References` heading.
3. Confirm no reference-style inline Markdown links remain in a citation-convention
   post (grep the draft for `](http`), and that every internal `/posts/…` link
   ends in `.html`, not `.md` (grep the draft for `/posts/[^)]*\.md` — it should
   return nothing; the source `.md` extension ships as a 404, see §3).

Note: `stack exec site build` alone is not enough — it runs the **already-compiled**
`site` binary. If `lib/Blog/Site.hs` changed (e.g. a new asset rule), run
`stack build` first or the binary silently omits the new outputs and verify-site
flags phantom missing targets. The full sequence is `stack build && stack exec
site build && node scripts/verify-site.mjs`.

## 8. Per-post checklist

**Before drafting (§0) — if any of these fails, there is no post:**

- [ ] The question came off `notes/questions.md`; it was not invented today
- [ ] Anchored to a recent primary source (journal article, this year or last) — not a settled result (§0)
- [ ] Checked whether the source's code/data is released; if not, the claim boundary is already written into Methods
- [ ] `contribution:` sentence written, naming what this post has that its sources do not
- [ ] `contribution-type:` set to one of §0's seven; "explained a known thing well" is not on the list
- [ ] The hypothesis has a falsifier, written down before the experiment ran
- [ ] You would publish the other outcome

**After drafting:**

- [ ] Front matter complete; title quoted if needed; links relative
- [ ] IMRaD sections present and in order (§2) — no exceptions; every post is an experiment
- [ ] Introduction funnels known → predicted → **gap** → hypothesis; no hook
- [ ] Methods states interpreter/arch/versions/seeds precisely enough to re-run
- [ ] Anything not run first-hand is declared as such in Methods and attributed at each use
- [ ] No untested equivalence claims ("reproduces X's semantics exactly" is a claim — test it)
- [ ] **Results passes the printed-output test sentence by sentence** (§2); no banned words; captions clean
- [ ] Any discrepancy with a source was chased through your own Methods before being reported unresolved
- [ ] Discussion states the verdict — supported / falsified / inconclusive — in those words
- [ ] Conclusion points forward and names the next experiment; that next step is now on the shelf
- [ ] Every external source cited as `[@key]` in ACS style — no inline links, no footnotes, no exceptions (§3)
- [ ] Source's own BibTeX/DOI used where it publishes one; entry type matches Table 0
- [ ] New bib entries appended, keys unique & de-duped
- [ ] Every `[@key]` grep-verified against `bib/bibliography.bib`; markers after punctuation; post ends with `## References`
- [ ] If the post has a figure: Figure 1 at 1200×630 in house style, `<figure>` + alt text, `og-image` set (§5 — figures are optional)
- [ ] Every figure, table, and code block has a numbered caption (Figure/Table/Code N) and is referenced by number in the prose
- [ ] Cross-links to the rest of the series, each pointing at the `.html` target (no `/posts/…-slug.md`)
- [ ] Branch, build, verification, PR, and merge complete
