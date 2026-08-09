---
title: How this notebook is made
description: How pvjohnston.com turns questions into computational artifacts, traceable prose, checked static pages, and published notes—with AI assisting along the way.
---

<article class="method-page">
<header class="method-hero">
<div class="method-shell">
<div class="method-eyebrow"><span aria-hidden="true">●</span> Open process · Current live workflow</div>
<h1>How this notebook is made</h1>
<p class="method-lede">A published note is the last visible artifact in a much longer chain. Questions are bounded before prose, computations keep their own evidence, generated values travel into sentences by name, and the resulting site has to survive mechanical checks and review before it reaches <code>main</code>.</p>
<p class="method-intro">This is both a reader’s colophon and my own map of the machinery. It describes the system that is live now—not a future ideal—and distinguishes what the tooling can verify from the scientific judgment it cannot replace. The archive grew into this contract over time, so older notes may predate some of its layers.</p>

<ol class="method-overview" aria-label="A note's path from question to publication">
<li><span class="method-step-number">01</span><strong>Question</strong><small>A shelf entry or bounded explanation</small></li>
<li><span class="method-step-number">02</span><strong>Form</strong><small>Research or Understanding</small></li>
<li><span class="method-step-number">03</span><strong>Evidence</strong><small>Inputs, code, outputs, checks</small></li>
<li><span class="method-step-number">04</span><strong>Prose</strong><small>Markdown, citations, metric names</small></li>
<li><span class="method-step-number">05</span><strong>Build</strong><small>Pandoc, Hakyll, MathJax, SVG</small></li>
<li><span class="method-step-number">06</span><strong>Gate</strong><small>Tests, verification, PR review</small></li>
<li><span class="method-step-number">07</span><strong>Publish</strong><small>Static HTML on GitHub Pages</small></li>
</ol>
</div>
</header>

<div class="method-shell method-body">
<nav class="method-contents" aria-label="On this page">
<span>On this page</span>
<a href="#question">1. Choose the question</a>
<a href="#workspace">2. Isolate the work</a>
<a href="#evidence">3. Own the evidence</a>
<a href="#sentence">4. Move results into prose</a>
<a href="#publishing">5. Compile the note</a>
<a href="#verification">6. Verify and deploy</a>
<a href="#ai">7. Where AI fits</a>
<a href="#limits">8. Know the limits</a>
</nav>

<div class="method-content">
<section id="question" class="method-section">
<div class="method-section-head"><span>01</span><div><p>Intellectual contract</p><h2>Start with the question, not the draft</h2></div></div>
<p>A topic can always produce fluent prose. It cannot by itself tell me what the note contributes, what evidence it needs, or where it should stop. Every new note therefore declares one of two forms before drafting.</p>

<div class="method-form-grid">
<article class="method-form-card method-form-research">
<div class="method-card-label">Research</div>
<h3>Does a claim survive a stated test?</h3>
<p>A Research question must already be waiting on the research question shelf. Before prose, I name the recent primary source, write the contribution in one sentence, state a hypothesis and its falsifier, and commit to reporting the other outcome.</p>
<ul>
<li>Produces an executable computer experiment</li>
<li>Uses Methods, Results, Discussion, and Conclusion</li>
<li>Ends <em>supported</em>, <em>falsified</em>, or <em>inconclusive</em></li>
</ul>
</article>
<article class="method-form-card method-form-understanding">
<div class="method-card-label">Understanding</div>
<h3>How does an object or mechanism work?</h3>
<p>An Understanding note names one explanatory question, the reader’s starting point, the order in which the ideas depend on one another, any computer-generated demonstrations, and the boundary where the model stops.</p>
<ul>
<li>Claims synthesis rather than novelty</li>
<li>Follows conceptual dependency order</li>
<li>Does not manufacture a hypothesis or verdict</li>
</ul>
</article>
</div>

<aside class="method-principle">
<strong>The shared stance</strong>
<p>I am an outsider learning in public. A discrepancy means “this did not reproduce for me under these conditions,” not “the authors were wrong.” Negative and inconclusive results are publishable; cleverness is not a deliverable; every note should make it easy for a better-informed reader to correct me.</p>
</aside>
</section>

<section id="workspace" class="method-section">
<div class="method-section-head"><span>02</span><div><p>Repository discipline</p><h2>Give each line of work its own room</h2></div></div>
<p>The repository’s default branch is the live site. I do not draft on it. Each post or site change gets a separate Git branch checked out into a sibling <strong>worktree</strong>: another working directory connected to the same repository.</p>

<div class="method-git-flow" role="img" aria-label="Origin main creates an isolated worktree; its branch enters a pull request; an accepted pull request returns to main and deploys">
<div><span>Live baseline</span><strong>origin/main</strong><small>The published starting point</small></div>
<i aria-hidden="true">→</i>
<div><span>Isolated work</span><strong>post/… or feature/…</strong><small>One branch, one owned scope</small></div>
<i aria-hidden="true">→</i>
<div><span>Integration gate</span><strong>Pull request + CI</strong><small>The exact commit is rebuilt</small></div>
<i aria-hidden="true">→</i>
<div><span>Accepted change</span><strong>main → Pages</strong><small>Merge triggers deployment</small></div>
</div>

<div class="method-split-note">
<div>
<h3>The worktree protects files</h3>
<p>Concurrent sessions can work without sharing an uncommitted directory. A post branch owns its post, slug-prefixed figures, experiment bundle, and append-only bibliography entries. Site templates, styles, scripts, and standalone pages travel in their own feature or fix pull requests.</p>
</div>
<div>
<h3>The journal protects thought</h3>
<p>Deep research begins an append-only journal before the first search or exploratory command. Sources, pivots, exact intermediate results, reproduction commands, and the next action are flushed to Git’s shared common directory so they survive a crashed session or removed worktree without entering the public repository.</p>
</div>
</div>
</section>

<section id="evidence" class="method-section">
<div class="method-section-head"><span>03</span><div><p>Computational ownership</p><h2>Keep the experiment larger than the article</h2></div></div>
<p>When a note generates results, one directory under <code>research/</code> owns the computational record. The exact contents depend on the experiment, but the shape is stable: declared inputs and sources, an environment boundary, executable code, canonical results, a publication projection, and an explicit list of files safe to serve.</p>

<div class="method-artifact-grid">
<pre class="method-tree" aria-label="Typical experiment directory"><code>research/&lt;experiment&gt;/
├── README.md
├── inputs.json / sources.json
├── environment.md or lockfile
├── run or analysis code
├── results.json
├── generate-metrics.mjs
├── metrics.json
└── PUBLIC_FILES.txt</code></pre>
<div class="method-artifact-notes">
<div><strong>One exact run boundary</strong><p>The README records what the computation can establish, what it cannot, and the command that produces its canonical artifacts.</p></div>
<div><strong>Rich results stay rich</strong><p><code>results.json</code> or an equivalent artifact preserves more than the handful of values selected for publication.</p></div>
<div><strong>Publication is an allowlist</strong><p><code>PUBLIC_FILES.txt</code> routes the reviewed reader-facing bundle; metrics and the shared schema are standing build inputs. Committing anything is already public, so secrets and private data never enter Git.</p></div>
</div>
</div>

<div class="method-levels" aria-label="Cumulative reproducibility levels">
<div><span>Level 1</span><strong>Traceable</strong><p>Published result prose resolves from a validated metrics artifact.</p></div>
<div><span>Level 2</span><strong>Analysis-reproducible</strong><p>Committed outputs can regenerate the analysis and metrics.</p></div>
<div><span>Level 3</span><strong>End-to-end reproducible</strong><p>Documented inputs and environment can rerun the experiment itself.</p></div>
</div>
<p class="method-smallprint">These levels are cumulative and earned per experiment. A paid service, unavailable hardware, licensing restriction, or disappearing source can impose an additional archived-evidence boundary.</p>
</section>

<section id="sentence" class="method-section">
<div class="method-section-head"><span>04</span><div><p>Traceable prose</p><h2>Move a result by name, not by copy and paste</h2></div></div>
<p>A saved script does not prove which run supplied a sentence. For newer computational notes, the analysis creates a small typed <code>metrics.json</code>. The Markdown asks for a named metric rather than repeating its display value.</p>

<div class="method-metric-chain" aria-label="A canonical result passes through a metric generator and metrics file into a named Markdown reference and rendered HTML">
<div><span>Canonical output</span><strong>results.json</strong></div>
<i aria-hidden="true">→</i>
<div><span>Deterministic projection</span><strong>generate-metrics.mjs</strong></div>
<i aria-hidden="true">→</i>
<div><span>Typed build input</span><strong>metrics.json</strong></div>
<i aria-hidden="true">→</i>
<div><span>Markdown source</span><strong>&#91;result&#93;&#123;.metric&#125;</strong></div>
<i aria-hidden="true">→</i>
<div><span>Rendered page</span><strong>formatted value</strong></div>
</div>

<p>Each metric stores a raw number, integer, or boolean; a description; an optional unit; and a deterministic formatting rule. Its provenance fingerprints the canonical inputs. Hakyll refuses to build when the post names a missing experiment, malformed artifact, or unknown metric.</p>

<aside class="method-example">
<div class="method-card-label">Working example</div>
<h3>Follow one value all the way through</h3>
<p><a href="/posts/2026-07-20-from-script-to-sentence.html">From script to sentence</a> uses a deliberately small Brewster-angle calculation to expose the whole chain. Its <a href="/research/traceable-brewster-angle/README.md">experiment README</a>, <a href="/research/traceable-brewster-angle/results.json">canonical result</a>, <a href="/research/traceable-brewster-angle/generate-metrics.mjs">metrics generator</a>, and <a href="/research/traceable-brewster-angle/metrics.json">publication projection</a> are all reader-facing.</p>
</aside>
</section>

<section id="publishing" class="method-section">
<div class="method-section-head"><span>05</span><div><p>Scientific publishing</p><h2>Compile one source into several reader surfaces</h2></div></div>
<p>The post itself is Markdown with YAML metadata. The build turns that source into the article, its citations and equations, a listing card, feed entries, sitemap metadata, and social metadata. The source remains readable; the output remains static.</p>

<div class="method-stack" aria-label="The site's publishing stack">
<div><span>Authoring</span><strong>Markdown + YAML</strong><p>Structure, metadata, metric references, captions, and links.</p></div>
<div><span>Document model</span><strong>Pandoc</strong><p>Parses the note, citation markers, math, code, tables, and raw HTML.</p></div>
<div><span>Sources</span><strong>BibTeX + CSL</strong><p>Every external source becomes an ACS-style bibliography entry and citation.</p></div>
<div><span>Scientific notation</span><strong>MathJax + mhchem</strong><p>Browser-rendered equations and chemical formulae from inspectable source.</p></div>
<div><span>Diagrams</span><strong>LuaLaTeX + dvisvgm</strong><p>TikZ and circuitikz compile into responsive, namespaced inline SVG.</p></div>
<div><span>Site compiler</span><strong>Hakyll in Haskell</strong><p>Applies templates, resolves metrics, builds listings and feeds, and routes reviewed artifacts.</p></div>
</div>

<p>The same build produces RSS and Atom feeds, a sitemap, syntax-highlighted code, responsive tables, social metadata, and print styles. Figures are optional. When a note needs one, Figure 1 is designed at social-card dimensions and reused as the hero. Every figure, table, code block, and audio example receives a numbered caption and a reference in the prose. Diagram output is cached by source hash, so editing a paragraph does not recompile unchanged LaTeX art.</p>
</section>

<section id="verification" class="method-section">
<div class="method-section-head"><span>06</span><div><p>Mechanical gates</p><h2>Ask several smaller checks, not one magical check</h2></div></div>
<p>No single green command means “the post is correct.” The repository instead gives narrow jobs to narrow checks, then repeats the complete sequence on the pull request’s exact commit.</p>

<div class="method-checks">
<div><code>verify-bib.mjs</code><p>Rejects new duplicate or case-colliding citation keys in the shared append-only bibliography.</p></div>
<div><code>citation self-check</code><p>Greps every citation key against the bibliography and catches internal post links that still point to Markdown instead of HTML.</p></div>
<div><code>stack test</code><p>Exercises the Haskell compiler behavior, including metrics and diagram transformations.</p></div>
<div><code>stack exec site rebuild</code><p>Regenerates the complete static site without trusting stale Hakyll output.</p></div>
<div><code>verify-metrics.mjs</code><p>Checks source fingerprints and proves each cheap generator reproduces its committed projection.</p></div>
<div><code>verify-site.mjs</code><p>Finds missing internal links and assets, failed diagrams, and public-manifest files that were not served.</p></div>
<div><code>GitHub Actions</code><p>Runs the build in a clean Linux environment before a pull request can become the live site.</p></div>
</div>

<div class="method-deploy-line" role="img" aria-label="A feature commit passes through a pull request build, human review, merge to main, and GitHub Pages deployment">
<span>feature commit</span><b aria-hidden="true">→</b><span>PR build</span><b aria-hidden="true">→</b><span>review</span><b aria-hidden="true">→</b><span>merge to main</span><b aria-hidden="true">→</b><span>GitHub Pages</span>
</div>
</section>

<section id="ai" class="method-section">
<div class="method-section-head"><span>07</span><div><p>AI-assisted authoring</p><h2>Use the model broadly; make the record outlive the chat</h2></div></div>
<p>I use AI-assisted sessions throughout this work: to inspect unfamiliar code and literature, sharpen questions, implement and test calculations, diagnose failures, generate alternatives, shape drafts, and review claims. That range is exactly why the repository has become so explicit. A long model conversation is useful working memory, but it is not a durable scientific record.</p>

<div class="method-ai-grid">
<div>
<span>Before a session</span>
<strong>The repository supplies the contract</strong>
<p><code>AGENTS.md</code>, the authoring guide, experiment README, branch boundaries, and current artifacts tell a fresh session how this project works.</p>
</div>
<div>
<span>During a session</span>
<strong>Tools create inspectable evidence</strong>
<p>During deep work, searches and decisions enter the journal; computations leave code and outputs; quantitative claims become generated metrics; checks leave command results.</p>
</div>
<div>
<span>After a session</span>
<strong>Git carries the durable handoff</strong>
<p>The commit and pull request show exactly which files changed. Another context—or a human reader—can inspect those artifacts without trusting the original chat.</p>
</div>
</div>

<aside class="method-principle method-principle-ai">
<strong>Responsibility does not transfer to the model</strong>
<p>I choose what belongs on this site and remain responsible for the question, methods, interpretation, prose, and decision to publish. A separate AI context can provide useful adversarial distance, but it is internal review—not independent scientific peer review. Sources, executable artifacts, and reproducible checks carry evidentiary weight; model confidence does not.</p>
</aside>
</section>

<section id="limits" class="method-section">
<div class="method-section-head"><span>08</span><div><p>Epistemic boundary</p><h2>Know what a clean build cannot tell us</h2></div></div>
<div class="method-boundary-grid">
<div>
<div class="method-card-label">The system can check</div>
<ul>
<li>that required files and internal links exist;</li>
<li>that citations and diagrams compile into the page;</li>
<li>that named metrics resolve and match fingerprinted artifacts;</li>
<li>that the reviewed public bundle is actually served; and</li>
<li>that the same commit passed tests before deployment.</li>
</ul>
</div>
<div>
<div class="method-card-label">The system cannot establish</div>
<ul>
<li>that the scientific question is important;</li>
<li>that the model, inputs, or interpretation are correct;</li>
<li>that every experimental numeral was written as a metric reference;</li>
<li>that an expensive experiment reruns during the normal site build; or</li>
<li>that internal review is external peer review.</li>
</ul>
</div>
</div>
<p>That distinction is not a disclaimer pasted onto the machinery; it is the reason for the machinery. The goal is to make each claim’s support and each experiment’s boundary easier to inspect without pretending that automation can settle the science.</p>
</section>

<footer class="method-footer">
<div>
<div class="method-card-label">Living colophon · August 2026</div>
<h2>The system is part of the work.</h2>
<p>The complete source, publishing code, notes, and selected computational artifacts live in the <a href="https://github.com/noprofits-org/pvjohnston.com">public repository</a>. The detailed conventions are also readable in the repository’s <a href="https://github.com/noprofits-org/pvjohnston.com/blob/main/notes/blog-authoring.md">authoring guide</a>. The publishing pipeline began at <a href="https://noprofits.org">noprofits.org</a> and separated into this personal notebook in July 2026.</p>
</div>
<div class="method-footer-links">
<a href="/writing.html">Read the notes <span aria-hidden="true">→</span></a>
<a href="/posts/2026-07-20-from-script-to-sentence.html">See the traceability example <span aria-hidden="true">→</span></a>
</div>
</footer>
</div>
</div>
</article>
