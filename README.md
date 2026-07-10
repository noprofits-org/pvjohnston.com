# pvjohnston.com

Peter Johnston’s portfolio, résumé, and personal technical notebook. The site is generated with Hakyll and Pandoc and published to [pvjohnston.com](https://pvjohnston.com) through GitHub Pages.

## What lives here

- Personal landing page, selected work, and printable résumé
- 51 migrated posts covering chemistry, physics, mathematics, art, software, automation, and systems
- BibTeX/CSL citations and MathJax with `mhchem`
- Build-time TikZ/circuitikz → inline SVG rendering
- RSS, Atom, sitemap, social metadata, drafts, syntax highlighting, and print styles
- Reproducible calculation artifacts for selected science posts

Nonprofit/watchdog articles remain in [`noprofits-org/blog`](https://github.com/noprofits-org/blog) at [blog.noprofits.org](https://blog.noprofits.org).

## Local development

Prerequisites: Haskell Stack, LuaLaTeX with TikZ/pgfplots/circuitikz/mhchem, and `dvisvgm`.

```sh
stack test
stack exec site build
stack exec site watch
```

Draft posts are excluded unless preview mode is enabled:

```sh
PREVIEW_DRAFTS=1 stack exec site watch
```

## Authoring

Posts live in `posts/` as Markdown with YAML front matter. See [`notes/blog-authoring.md`](notes/blog-authoring.md) for citations, figures, captions, and verification conventions.

## Deployment

Pull requests run the complete test and build pipeline. Pushes to `main` additionally publish `_site` through GitHub’s native Pages deployment. The custom domain is written to `_site/CNAME` by the workflow.

## License

BSD-3-Clause.
