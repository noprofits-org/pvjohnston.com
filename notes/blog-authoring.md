# Blog authoring conventions

The single source of truth for producing a note on pvjohnston.com. Read this
before drafting and follow it so every post comes out consistently. Every new
post declares one of two forms before drafting:

- **Research** asks a falsifiable question and reports a computer experiment.
- **Understanding** explains how a scientific or technical object works by
  connecting its representations, mathematics, and physical meaning.

The shared pipeline is **question → form → draft → bib → figures → branch →
verify → PR → merge → auto-deploy**. Research inserts **contribution gate →
hypothesis → experiment** before drafting. Understanding inserts **scope →
explanatory route → computational demonstrations** instead.

**Every experiment and computational demonstration is performed on a computer
and involves no living subjects.** Acceptable procedures include simulations,
calculations, benchmarks, software tests, and analyses of existing digital
artifacts or published datasets. Do not recruit, observe, survey, interview,
expose, or intervene on people, animals, plants, microorganisms, or any other
living subjects. Existing recordings, texts, images, measurements, and datasets
may be analysed, provided the post creates no new interaction with a living
subject.

---

## The stance — exploration in the open, not exposé

This is the governing voice of the site, and it outranks the vocabulary of every
section below it. Words like *falsification*, *gap*, *target*, and *friction*
appear throughout this document as names for an intellectual move; none of them
licenses a tone. Where a rule sounds adversarial, this section is what it
actually means.

**We are outsiders learning in public by running experiments.** The honest
description of nearly every post is the same: *we did not fully understand
something, so we tried to test it on a computer; here is exactly what we ran,
here is what came out, here is what we currently think it means, and here is
where we might be wrong.* The last clause is not modesty for show — it is
literally our epistemic position, and the writing must carry it. Write for a
reader who knows the subject better than we do and is in a position to tell us
what we missed. A post is an invitation to be corrected, not a conclusion
delivered to an audience.

**We test claims — most often our own. We do not catch people.** When a
published number does not reproduce on our setup, the finding is *"it did not
reproduce for us, under these conditions,"* never *"the authors were wrong."*
The overwhelmingly likely cause of a discrepancy is something on our side — a
library version, a dtype, an accumulator, a misread spec, a benchmark we set up
differently — and the prose must reach for that before it reaches for the
source's competence. A number that refuses to reconcile is an open question we
raise with our hands up, not a verdict we are qualified to hand down. This is
not only courtesy; it is calibration. We are usually the ones who are wrong, and
writing that assumes so ages well.

**Novelty is "new to us," not "missed by them."** The `contribution:` sentence
(§0) records what this post contains that its source did not — nothing more. It
does not assert that the authors overlooked something, could not see it, or
should have run it. "Unknown to us" is the scope we can defend; "unknown to the
field" is a claim we are almost never positioned to make, so we do not make it or
imply it. If a result turns out to be genuinely new, that is for others to say;
our job is to report plainly what we did and let reproducibility carry the
weight. Cleverness is not a deliverable — a post that reads as a display of how
clever the author is has left the stance, whatever its numbers say.

**Concretely — banned and required framings.** These are testable, like the
Results banned-word rule (§2):

| Don't write | Write instead |
| --- | --- |
| "The authors are wrong / got this wrong" | "This did not reproduce for us under [conditions]" |
| "The paper fails to / neglects to / should have" | "We could not find X in the source, so we ran it ourselves" |
| "We caught / exposed / debunked" | "We tested it, and here is what we found" |
| "This proves the claim is false" | "Our stated hypothesis was falsified; here is our setup" |
| "Obviously / clearly / trivially / of course" | say the thing plainly, or show it |
| any claim the finding is new to the field | "new to us; if this is already known, tell us" |

**Close by inviting correction, and mean it.** A post may end by naming what
would change our mind and where a knowledgeable reader should push. That is not a
rhetorical flourish; it is the reason to publish at all. The verdict language
this guide requires (*supported / falsified / inconclusive*, §2) is a verdict on
**our own hypothesis and our own experiment** — never a grade on the source.

---

## 0. Before you draft — choose the form

Every post starts with a concrete question. Choose the form by asking what an
honest answer requires:

| Form | The question asks | The post owes the reader |
| --- | --- | --- |
| **Research** | Is this claim true under a stated test? | A novel contribution, falsifier, executable experiment, results, and verdict |
| **Understanding** | How does this object or mechanism work? | A bounded scope, a dependency-ordered explanation, reproducible demonstrations, and a clear account of where the model stops |

Do not attach a decorative hypothesis to an explanation. Do not label an
untested claim an Understanding note to escape the contribution gate. The form
follows the intellectual job.

### Research notes — the question and what it contributes

**The bottleneck is not writing. It is question supply.** Nobody finds a novel
question on demand at 9pm, and a post that starts from a *topic* instead of a
*question* will restate what is already known — fluently, and pointlessly. That
is the machine that produces triviality, and no amount of structure downstream
will stop it. Real labs do not invent a hypothesis on the day they write; they
keep a backlog of things that do not add up, and pull from it.

So `notes/questions.md` is the research shelf. **No Research note gets drafted
unless its question was sitting on the shelf first.** Entries come from three
places, all three already proven here:

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
| **Falsification** | a published claim does not hold up under our stated test |
| **Decay** | a result was true and quietly stopped being true |
| **Unplotted line** | the analysis the source's own data supports, that the source never ran |
| **Quantification** | someone wrote "negligible" and never measured it |
| **Untested regime** | it holds at X — does it hold at Y? |
| **Composition** | two known results nobody has connected |
| **Negative result** | expected X, measured not-X |

These name the intellectual move, not a tone. **Falsification** is a verdict on
*our* hypothesis and *our* run — not on the author — and every type here is
something we probe with our hands up, framed as the stance section requires.

The site's research contributions came from friction with a *specific
source*, not from choosing a subject: the unplotted regression in "a citation, a
slot, and the line nobody plots" (the source's own data, the author's own error
method), and the Neumaier decay in the temperature-zero note (a number that
refused to reconcile). Neither came from a hook. Anomalies and standing are where
the questions live; go there deliberately.

**What is not novelty:** "I explained a known thing well." Kramers-Kronig has
been understood since 1926. A good explanation of it contributes nothing to
collective knowledge, however well it reads. Exposition is not a lesser post
here, but it is not Research. Declare it as Understanding and satisfy that
form's separate contract.

**Anchor the hypothesis to a recent primary source — a journal article from this
year or last.** This is the single most reliable way to find a question that is
actually open, and it follows directly from the rule above. A settled result can
only be *explained*; a live one can be *contributed to*. Kramers-Kronig has had a
century of scrutiny and every accessible gap in it is closed. A paper from six
months ago has unpriced claims, unreleased code, and mechanisms asserted but not
measured — because that is what the edge of a literature looks like. Both of this
site's measured research contributions came from 2025–2026 sources. Canonical,
settled sources remain appropriate for Understanding notes because those notes
do not claim to extend the literature.

Recency is necessary, not sufficient: a modern paper still has to yield a
`contribution:` sentence, and "recent" is not a synonym for "unexamined."

**Name the source before you inherit its question.** A **direct source-response
post** is one whose contribution depends on a particular paper's open question,
untested regime, claim, data, or method. In such a post, a citation halfway
through the Introduction is necessary but not sufficient: the reader should not
have to infer the intellectual handoff from phrases such as "their published
test" or from a late Methods disclaimer.

Before Methods, three surfaces must agree:

- **Headline:** name the source author or a recognizable short paper title and
  state the relationship — testing an open regime, reanalysing data, checking a
  claim, or extending a method. Use the full paper title when it remains
  readable; otherwise use the author in the headline and give the full title in
  the Abstract.
- **Description:** identify the work as an independent benchmark, reproduction,
  reanalysis, falsification, or extension. Do not describe only the new result
  while hiding what prompted it.
- **First Abstract paragraph:** give the authors, year, full paper title, and
  citation, then state exactly what this post does in relation to it. Do not use
  "their," "the source paper," or a method acronym before naming the source.

Methods then records the implementation lineage precisely: whether the source
authors' program, code, or data were used; what was independently implemented;
and what could not be reproduced at the software level. This attribution does
not imply collaboration, endorsement, or a call to the authors' program.

**Provenance test:** read only the headline, description, and first Abstract
paragraph. A reader must be able to name the source, identify the relationship
to it, and tell whether the experiment is an independent implementation. If any
of those still has to be inferred, the opening is not ready.

**Where the gaps hide in a modern paper.** Read for friction, not for topic —
these are places a literature is still *open*, not places its authors erred (the
stance section governs how any of them gets written up):

| Look at | What it yields |
| --- | --- |
| "Future work", "remains an open problem" | open questions the authors flagged for follow-up |
| Hedged mechanisms: "suggests", "likely", "attributed to" | a cause asserted from a citation and never measured |
| Two tables that were never joined | an **unplotted line** — the analysis their own data supports |
| "negligible", "no meaningful difference", "comparable" | an unquantified null |
| Spec in the text vs the code they cite or release | a reimplementation hazard; acute when the code is unreleased |
| A headline number with no tabulated case behind it | an unsourced claim |

Prefer a source whose data or code you can actually reach, and check whether the
code is released before committing — an unreleased repository does not block the
question, but it *bounds* what you may claim, and that boundary belongs in
Methods (§2) from the start rather than being discovered late.

**The honest failure mode.** When the research shelf is empty, no Research note
ships that day. A gate that cannot fail is not a gate, and the only other way
this resolves is stamping it to protect a streak — which produces precisely the trivial
restatement this section exists to prevent. Breaking the streak is the cheaper
loss.

### Understanding notes — scope and explanatory route

An Understanding note does not claim novelty and does not need a hypothesis.
Before drafting, write down:

1. the one explanatory question the note will answer;
2. the reader's assumed starting point;
3. the sequence of representations or mechanisms that makes the answer legible;
4. the boundary beyond which the explanation no longer reaches; and
5. which figures or calculations will be generated on a computer.

The standard is synthesis, not discovery. The note must connect ideas that are
usually taught apart, make every mathematical step inspectable, and show the
object in more than one useful representation. A collection of definitions is
not enough. Neither is a plot gallery without a causal or mathematical route
through it.

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
post-type: research                              # research or understanding
contribution: X, which is not in [source].        # required; Research only
contribution-type: decay                          # required; Research only
experiment: experiment-slug                       # any post with generated results; see §7
og-image: /images/YYYY-MM-DD-post-slug-hero.png   # optional; see §5
---
```

An Understanding note replaces the two contribution fields with its explanatory
question:

```yaml
post-type: understanding
question: What physical signal does a chord make, and what does a Fourier transform reveal about it?
```

- **Title:** quote if it contains a colon or other YAML-significant punctuation.
  For direct source-response posts, it also names the source author or a
  recognizable short source title (§0).
- **Description:** says how the post relates to its anchor source when that
  relationship is direct (§0); it cannot report only the result.
- **Links:** use site-relative URLs for other notes in this repository.
- **`post-type`:** required for every new post. Older posts without the field
  predate this distinction; do not bulk-migrate them.
- **`contribution` / `contribution-type`:** written *before* drafting, not after
  (§0) and present only on Research notes. They are not rendered — they exist so
  the gate leaves an artifact in the file, where a reviewer can check it against
  what the post actually did.
- **`experiment`:** the lowercase directory name under `research/` that owns
  the post's generated metrics. Required whenever a post reports locally
  generated results under the traceability contract (§7).
- **`question`:** required on Understanding notes. It is not rendered; it keeps
  the explanation bounded during drafting and review.

## 2. Structure — form and voice

### Research notes — IMRaD

**Every Research note uses the IMRaD skeleton**, in this order, as `##` headers:

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
- **The experiment must run on a computer without living subjects.** Methods
  must identify the executable computational procedure and its digital inputs.
  A design that requires recruiting, observing, surveying, interviewing,
  exposing, or intervening on a living subject is out of scope for this blog,
  not a future implementation detail.
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
  only after you have tried; it is a last resort, not a shrug. Report the
  discrepancy as the stance section requires — *did not reproduce for us*,
  attributed to our conditions first — and keep the verdict a verdict on our own
  hypothesis, never a grade on the source.
- **Conclusion** points **forward, not back**. State what changed in what we
  know, and name the next experiment. Do *not* tie back to the problem that
  opened the note — that is circularity, and it is what an essay does. A post
  with no next step probably opened nothing. The next step goes on the shelf
  (§0).

Research notes do not drop Methods or Results. If the intellectual job does not
require them, change the declared form to Understanding and satisfy that form's
contract instead.

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

### Understanding notes — dependency order

Understanding notes have no fixed section names beyond a final `## References`.
Their headings follow the dependency chain of the explanation: begin with the
physical or technical object, introduce each representation when it becomes
useful, and end at the declared boundary. The reader should never need a concept
that the note has not yet built.

Every Understanding note includes these elements, wherever they fit naturally:

- an opening paragraph that names the explanatory question and the route through
  it, without manufacturing a hook or knowledge gap;
- equations worked far enough that each plotted quantity can be reconstructed;
- computer-generated demonstrations that expose the same object in two or more
  representations when that comparison does real explanatory work;
- a short reproducibility section naming the interpreter, libraries, exact
  procedure, and digital inputs used to make the demonstrations;
- a section that states **where the model stops** — what the mathematics or
  physical representation does not establish; and
- a bare `## References` heading at the end.

An Understanding note has observations, explanations, and limitations, not
Results, Discussion, or a verdict. Never call a generated example evidence for a
perceptual, historical, or cultural claim. If the post begins testing such a
claim, it has become Research and must pass the Research gate.

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

**Every figure, table, code block, and audio player gets a numbered caption, and
every one is referenced by number somewhere in the prose.** No exceptions — an
uncaptioned or unreferenced element is a bug.

- **Numbering** runs independently per type, in document order: Figure 1, 2, 3…;
  Table 1, 2…; Code 1, 2…; Audio 1, 2…. A post can have Figure 1, Table 1,
  Code 1, and Audio 1.
- **Format:** the caption label is **bold** for all four types, followed by a
  full sentence (not a bare label):
  - Figures — `**Figure 1.** Sentence describing what it shows.` directly
    **below** the `<figure>`.
  - Tables — `**Table 1.** Sentence describing the table.` directly **below**
    the table.
  - Code blocks — `**Code 1.** Sentence describing what the code does.` directly
    **below** the fenced block.
  - Audio — keep the complete `<audio>` element on one source line, with a
    useful fallback sentence and direct file link between its tags; put
    `**Audio 1.** Sentence describing what the listener will hear.` directly
    **below** the player. For example:

    ```html
    <audio controls preload="none" src="/downloads/clip.wav">Your browser cannot play this audio; <a href="/downloads/clip.wav">download the WAV file</a>.</audio>
    ```

    Do not wrap the element across source lines: Pandoc can otherwise consume
    the following Markdown as raw HTML.
  - (Older posts used italic `*Figure N.*` / `*Table N.*` — that was a mistake;
    bold is the standard. Normalize when touching an old post.)
- **Cross-reference:** point to each numbered element at least once in the body
  by its number — "(Figure 1)", "as Table 2 shows", "the loop in Code 1". If
  there's no natural place to reference it, it probably doesn't belong in the
  post.
- Figure 1 is still the hero / OG card (§5).

## 7. Experiment artifacts and traceable metrics

**The promise is traceability, not magic.** A metric reference proves that the
rendered prose matches the committed metrics projection. The normal site build
does not rerun the experiment and does not by itself prove correctness,
freshness, or end-to-end reproducibility. Do not write that hand-typed results
are impossible: the compiler can enforce references, but it cannot reliably
classify every numeral in natural-language prose.

Use these cumulative labels only when the corresponding evidence exists. Before
the first one is earned, write **not yet established**. **Archived evidence** is
an additional constraint note, not a competing level; it may coexist with any
of the three when a paid API, hardware boundary, rights restriction, or missing
upstream input prevents a future full rerun.

| Label | Earned when |
| --- | --- |
| **Traceable** | result-bearing prose resolves from a validated `metrics.json` |
| **Analysis-reproducible** | committed outputs can regenerate the analysis and metrics |
| **End-to-end reproducible** | documented inputs and environment can rerun the experiment and regenerate its outputs |

### One directory owns each new experiment

Start from `research/_TEMPLATE/` and create `research/<experiment-slug>/`. Keep
the executable code, native dependency lock or precise environment record,
source manifest, canonical results, generated `metrics.json`, cheap metrics
generator, and public-bundle allowlist together. `metrics.json` is a small
publication projection; it does not replace the experiment's richer outputs.

The post declares the binding:

```yaml
experiment: example-experiment
```

Reference a generated result with Pandoc's bracketed-span syntax:

```markdown
The accepted count was [accepted]{.metric}, or [acceptance_rate]{.metric}.
```

The metric name is not fallback prose. At build time it becomes a
`metric-value` span carrying a `data-metric` identifier. For a metric reference,
a missing experiment binding, file, or metric—or an invalid type, unsupported
format, or malformed span—is a hard Hakyll build error. An `experiment:` field
that points to a missing or invalid artifact also fails. Metric references work
in normal prose, emphasis, captions, and tables; do not place them inside math,
code, TikZ, raw HTML, title, description, or other front matter. Phase one
therefore forbids experiment-result numerals in front matter. Summarize the
conclusion there without quoting the measurement.

Use metric references for **experiment-produced quantitative claims** in any
new note bound to an experiment. In Research notes this includes repetitions of
the same result in the Abstract, Results, Discussion, and Conclusion. In
Understanding notes it includes generated demonstration values while keeping
the demonstration distinct from perceptual, cultural, or historical evidence.
Literal dates, software versions, seeds, declared parameters, dimensions,
equation constants, and clearly attributed external values remain ordinary
prose. Apply this convention prospectively; do not bulk-convert the archive.

Every number metric stores a typed raw value plus a deterministic formatting
rule (`fixed`, `scientific`, `percent`, or `raw`). It never stores arbitrary
display text. The generator owns derivation from canonical outputs and supports
`--check`. `node scripts/verify-metrics.mjs` verifies each declared source
fingerprint and confirms that its generator reproduces the committed
projection. Expensive training, simulation, model calls, and data acquisition
stay out of the normal site build; a later end-to-end job may rerun them on an
appropriate schedule.

### Publication is an allowlist

This GitHub repository is public: committing a file is already publication,
even when Hakyll does not route it onto the website. Credentials, private data,
and secrets must never be committed; excluding them from a bundle is not a
confidentiality control. Hakyll publishes validated `metrics.json` files and the
shared schema automatically. Other site/download artifacts need explicit
routing. `PUBLIC_FILES.txt` is currently the reviewed manifest for an explicit
or future reproduction-bundle step; the normal build does not consume it.

Publish a curated, stable reader-facing bundle by default when the reviewed
manifest and bundle step exist, but never package an entire research directory
automatically. The manifest excludes nonredistributable sources, oversized
artifacts, caches, scratch work, and sensitive transcripts. For excluded
computational inputs, where applicable, record durable acquisition
instructions, version or DOI, access date, checksum, license, and the resulting
reproducibility limit. Literature citations remain in the shared bibliography.
A URL plus checksum can verify retrieved bytes; it cannot guarantee that the URL
will remain available.

## 8. Deploy flow

`.github/workflows/deploy.yml` builds the Hakyll site with Stack and publishes to
GitHub Pages on **push to `main`** (also PR-to-main and manual dispatch). So:

1. Work on a feature branch (`post/<slug>`), never commit straight to `main`.
2. **Verify before merge:** `stack test && stack exec site rebuild && node scripts/verify-metrics.mjs && node scripts/verify-site.mjs` must succeed;
   check the post renders, citations resolve, figures load, and the card meta is
   right.
3. Open a PR into `main`; merge triggers the deploy.

The verification script rejects missing internal assets/links and any generated
`tikz-error` box, because a green Hakyll exit alone does not prove every diagram
compiled.

**If you author in a sandbox and cannot run the build,** the orchestrator/human
runs §8's build + verify before merge — but a missing citation will not fail the
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
`site` binary, and Hakyll's cache does not know when compiler semantics change.
After any change under `lib/`, run `stack test` and use `site rebuild` so cached
posts cannot retain old formatting or validation behavior. The full pre-merge
sequence above deliberately uses `stack test && stack exec site rebuild`.

## 9. Per-post checklist

**Before drafting — every post:**

- [ ] `post-type:` declares `research` or `understanding`
- [ ] One concrete question is written in front matter or on the research shelf
- [ ] Every planned experiment or demonstration is executable on a computer and involves no living subjects

**Before drafting — Research only (§0):**

- [ ] The question came off `notes/questions.md`; it was not invented today
- [ ] Anchored to a recent primary source (journal article, this year or last) — not a settled result (§0)
- [ ] Checked whether the source's code/data is released; if not, the claim boundary is already written into Methods
- [ ] For a direct source-response post, recorded the source's full title and classified the relationship: independent benchmark, reproduction, reanalysis, falsification, or extension (§0)
- [ ] `contribution:` sentence written, naming what this post has that its sources do not
- [ ] `contribution-type:` set to one of §0's seven; "explained a known thing well" is not on the list
- [ ] The hypothesis has a falsifier, written down before the experiment ran
- [ ] You would publish the other outcome

**Before drafting — Understanding only (§0):**

- [ ] `question:` states the explanatory question
- [ ] Audience, dependency order, generated demonstrations, and stopping point are written down
- [ ] The planned synthesis connects representations or mechanisms rather than collecting definitions

**After drafting — every post:**

- [ ] **Stance check:** no "the authors were wrong", no gotcha/exposé/"debunk" framing, no claim the finding is new to the field, no cleverness-for-its-own-sake; discrepancies read as "did not reproduce for us" and the post invites correction (stance section)
- [ ] Front matter complete; title quoted if needed; links relative
- [ ] Every external source cited as `[@key]` in ACS style — no inline links, no footnotes, no exceptions (§3)
- [ ] Source's own BibTeX/DOI used where it publishes one; entry type matches Table 0
- [ ] New bib entries appended, keys unique & de-duped
- [ ] Every `[@key]` grep-verified against `bib/bibliography.bib`; markers after punctuation; post ends with `## References`
- [ ] If the post has a figure: Figure 1 at 1200×630 in house style, `<figure>` + alt text, `og-image` set (§5 — figures are optional)
- [ ] Every figure, table, code block, and audio player has a numbered caption (Figure/Table/Code/Audio N) and is referenced by number in the prose; each `<audio>` element stays on one source line and contains fallback text plus a direct file link
- [ ] Cross-links to the rest of the series, each pointing at the `.html` target (no `/posts/…-slug.md`)
- [ ] Branch, build, verification, PR, and merge complete

**After drafting — Research only:**

- [ ] Direct source-response provenance passes the headline + description + first-Abstract-paragraph test: source, relationship, and independent status are explicit (§0)
- [ ] IMRaD sections present and in order (§2)
- [ ] Introduction funnels known → predicted → **gap** → hypothesis; no hook
- [ ] Methods states interpreter/arch/versions/seeds precisely enough to re-run
- [ ] Methods states whether source program/code/data were used and what was independently implemented
- [ ] Methods identifies the computational procedure and digital inputs; no living subjects were recruited, observed, surveyed, interviewed, exposed, or acted upon
- [ ] `experiment:` names its `research/<slug>/` owner; result-bearing prose uses `[metric_name]{.metric}` and no experiment result is quoted in front matter (§7)
- [ ] The metrics generator passes `--check`; source fingerprints pass `node scripts/verify-metrics.mjs`; the post claims only the reproducibility label it has earned (§7)
- [ ] Public research files come from an explicit reviewed allowlist; rights, privacy, secrets, and size exceptions are documented (§7)
- [ ] Anything not run first-hand is declared as such in Methods and attributed at each use
- [ ] No untested equivalence claims ("reproduces X's semantics exactly" is a claim — test it)
- [ ] **Results passes the printed-output test sentence by sentence** (§2); no banned words; captions clean
- [ ] Any discrepancy with a source was chased through your own Methods before being reported unresolved, and written as "did not reproduce for us" — not as an author error (stance section)
- [ ] Discussion states the verdict — supported / falsified / inconclusive — in those words
- [ ] Conclusion points forward and names the next experiment; that next step is now on the shelf

**After drafting — Understanding only:**

- [ ] Opening names the question and explanatory route without a manufactured gap or hypothesis
- [ ] Headings follow conceptual dependency order; no IMRaD labels or verdict
- [ ] Equations are sufficient to reconstruct every plotted quantity
- [ ] Reproducibility note names the computer environment, procedure, and digital inputs
- [ ] If the note quotes a generated demonstration, `experiment:` names its owner; metric references, generator checks, fingerprints, and the earned reproducibility label follow §7
- [ ] Every generated example is described as a demonstration, not perceptual or cultural evidence
- [ ] A section explicitly states where the physical or mathematical model stops
