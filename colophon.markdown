---
title: Colophon
description: How pvjohnston.com publishes mathematical, chemical, and technical writing.
---

# Colophon

This site is generated with [Hakyll](https://jaspervdj.be/hakyll/) and Pandoc, then deployed as static HTML on GitHub Pages.

## Scientific publishing pipeline

Every post passes through Pandoc with BibTeX and CSL citation processing. Mathematics is emitted for MathJax, including `mhchem` chemical notation. Fenced TikZ and circuitikz diagrams compile at build time with LuaLaTeX and `dvisvgm`, then enter the page as responsive, namespaced inline SVG.

The build also produces RSS and Atom feeds, a sitemap, syntax-highlighted code, responsive tables, social metadata, and print-ready articles. Diagram output is cached by source hash so prose edits do not recompile unchanged figures.

## Source

The source, publishing code, posts, and reproducible calculation artifacts are available in the [pvjohnston.com repository](https://github.com/noprofits-org/pvjohnston.com). The publishing pipeline began at the noprofits.org blog and was separated in July 2026 so each domain could keep a coherent purpose.
