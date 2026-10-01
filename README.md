# pvjohnston.com

Peter V. Johnston, Ph.D. — [Quantum-chemistry calculations and construction software](https://pvjohnston.com/about.html).

Start with [One dye, one transition](https://pvjohnston.com/posts/2026-08-13-dcdhf-me2-transitions.html) and [How the acceptor closes the gap](https://pvjohnston.com/posts/2026-08-16-how-the-acceptor-closes-the-gap.html).

Then test a photoswitching claim: [Does Hillel’s push-pull sentence hold?](https://pvjohnston.com/posts/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing.html).

## What lives here

- Personal landing page, selected work, and printable résumé
- 90 posts covering chemistry, physics, mathematics, art, software, automation, and systems
- BibTeX/CSL citations and MathJax with `mhchem`
- Build-time TikZ/circuitikz → inline SVG rendering
- Typed experiment metrics resolved from generated, fingerprint-verified research artifacts
- RSS, Atom, sitemap, social metadata, drafts, syntax highlighting, and print styles
- Reproducible calculation artifacts for selected science posts

Nonprofit/watchdog articles remain in [`noprofits-org/blog`](https://github.com/noprofits-org/blog) at [blog.noprofits.org](https://blog.noprofits.org).

## Local development

Prerequisites: Haskell Stack, Node.js, LuaLaTeX with
TikZ/pgfplots/circuitikz/mhchem, and `dvisvgm`.

```sh
stack test
stack exec site rebuild
node scripts/verify-metrics.mjs
node scripts/verify-site.mjs
stack exec site watch
```

Draft posts are excluded unless preview mode is enabled:

```sh
PREVIEW_DRAFTS=1 stack exec site watch
```

To compile the site without TeX Live (diagrams stay as source, same as PR CI):

```sh
SKIP_TIKZ=1 stack exec site rebuild
```

## Authoring

Posts live in `posts/` as Markdown with YAML front matter. See [`notes/blog-authoring.md`](notes/blog-authoring.md) for citations, figures, captions, and verification conventions.

## Deployment

Pull requests run `.github/workflows/ci.yml`: Stack tests plus a Hakyll `site build` with `SKIP_TIKZ=1`, so TeX Live is not installed and TikZ diagrams are left as source. A new push on the same PR cancels the in-flight CI run.

Pushes to `main` (and manual `workflow_dispatch`) run `.github/workflows/deploy.yml`: the full TeX Live / dvisvgm pipeline, then publish `_site` through GitHub’s native Pages deployment. Deploy concurrency is serialized and never cancelled mid-publish. The custom domain is written to `_site/CNAME` by that workflow.

## License

BSD-3-Clause.
