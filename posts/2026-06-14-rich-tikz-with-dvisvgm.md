---
title: A light wave from Maxwell's equations, rendered in pure TikZ
date: 2026-06-14
author: Peter Johnston
bibliography: bib/bibliography.bib
csl: bib/style.csl
tags: tikz, rendering, haskell, hakyll, electromagnetism, physics
description: Deriving the electromagnetic plane wave from Maxwell's equations, then drawing it with build-time TikZ — and the Haskell pipeline rebuild (lualatex + dvisvgm) that finally renders its transparency.
---

This post is two things at once. It is a small derivation — how a propagating
light wave falls out of Maxwell's equations — and it is the proof that this
blog's diagram pipeline can now draw that wave honestly, transparency and all.
Every figure here is compiled from TikZ source *at build time*: the diagram in
the Markdown **is** the diagram on the page, with no image file checked into the
repository.

## The wave hiding in Maxwell's equations

In a source-free region of vacuum, Maxwell's four equations reduce to a
strikingly symmetric set:[@Maxwell; @Griffiths2018]

$$\nabla \cdot \vec{E} = 0, \qquad \nabla \cdot \vec{B} = 0,$$

$$\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}, \qquad
\nabla \times \vec{B} = \mu_0 \varepsilon_0 \frac{\partial \vec{E}}{\partial t}.$$

The two curl equations couple the fields: a changing magnetic field sources a
circulating electric field, and a changing electric field sources a circulating
magnetic one. Take the curl of Faraday's law and substitute Ampère's law, using
the identity $\nabla \times (\nabla \times \vec{E}) = \nabla(\nabla \cdot \vec{E})
- \nabla^2 \vec{E}$ together with $\nabla \cdot \vec{E} = 0$:

$$\nabla^2 \vec{E} = \mu_0 \varepsilon_0 \frac{\partial^2 \vec{E}}{\partial t^2}.$$

That is the wave equation. Reading off the coefficient, the disturbance
propagates at $c = 1/\sqrt{\mu_0 \varepsilon_0}$ — a speed assembled entirely
from electric and magnetic constants, which is how Maxwell recognized that light
*is* an electromagnetic phenomenon.[@Jackson1999] A plane-wave solution travelling
along $\hat{v}$ is

$$\vec{E} = E_0 \,\hat{z}\,\sin(kx - \omega t), \qquad
\vec{B} = B_0 \,\hat{y}\,\sin(kx - \omega t),$$

with three properties worth seeing rather than just stating: $\vec{E}$ and
$\vec{B}$ are **mutually perpendicular**, both are **transverse** to the
direction of travel, and they oscillate **in phase**. A static picture of those
three facts is exactly the kind of figure that is tedious to fake and easy to
draw if your toolchain cooperates.

## Drawing it: build-time TikZ

The figure below is the test case. It is a 3D electromagnetic plane wave drawn in
a hand-rolled basis: the red sheet is the electric field $\vec{E}$, the blue
sheet the magnetic field $\vec{B}$, perpendicular and in phase, propagating along
$\vec{v}$. The fills are **translucent** — where the two field envelopes cross
you can see through both, and that single visual cue is what carried the whole
toolchain rebuild, because the *old* pipeline threw the transparency away.

```tikzpicture
\begin{tikzpicture}[
  x={(1cm,-0.16cm)}, y={(0.46cm,0.32cm)}, z={(0cm,1cm)},
  >={Stealth[length=3mm]}, line cap=round, line join=round,
  Edge/.style={thick}]
  % faint ground grid on the x-y plane
  \foreach \gx in {0,1,...,8}{\draw[gray!35,line width=.3pt] (\gx,-1.8,0)--(\gx,1.8,0);}
  \foreach \gy in {-1.5,-1,...,1.5}{\draw[gray!35,line width=.3pt] (0,\gy,0)--(8,\gy,0);}
  % axes
  \draw[->,Edge] (0,0,-1.6)--(0,0,2.5) node[anchor=south]{$\vec{E}$};
  \draw[->,Edge] (-0.4,0,0)--(8.7,0,0) node[anchor=west]{$\vec{v}$};
  \draw[->,Edge] (0,-1.9,0)--(0,2.6,0) node[anchor=south west]{$\vec{B}$};
  % E field — red sheet in the x-z plane
  \fill[red,opacity=0.20] plot[variable=\x,domain=0:8,samples=160,smooth] (\x,0,{1.6*sin(\x*90)}) -- (8,0,0) -- (0,0,0) -- cycle;
  \foreach \x in {0,0.2,...,8.01}{\draw[red!65!black,opacity=0.55,line width=.4pt] (\x,0,0)--(\x,0,{1.6*sin(\x*90)});}
  \draw[red!75!black,line width=1pt] plot[variable=\x,domain=0:8,samples=200,smooth] (\x,0,{1.6*sin(\x*90)});
  % B field — blue sheet in the x-y plane
  \fill[blue,opacity=0.20] plot[variable=\x,domain=0:8,samples=160,smooth] (\x,{1.1*sin(\x*90)},0) -- (8,0,0) -- (0,0,0) -- cycle;
  \foreach \x in {0,0.2,...,8.01}{\draw[blue!65!black,opacity=0.55,line width=.4pt] (\x,0,0)--(\x,{1.1*sin(\x*90)},0);}
  \draw[blue!75!black,line width=1pt] plot[variable=\x,domain=0:8,samples=200,smooth] (\x,{1.1*sin(\x*90)},0);
\end{tikzpicture}
```

TikZ is the right tool for this because it is a *programmatic* drawing language —
the two field sheets are `\foreach` loops over $\sin(kx)$, not hand-placed
vertices, so the geometry is the physics.[@Tantau2023] The cost is that TikZ runs
inside TeX, which means the blog has to run TeX during its build.

## The pipeline, and why it had to change

The blog is a Hakyll site: a Haskell program compiles Markdown into the static
HTML you are reading.[@Hakyll] A custom Pandoc filter walks the document, finds
every code block tagged `tikzpicture`, shells out to render it, and splices the
result back into the page. The original filter did this:

> `pdflatex` → PDF → `pdf2svg` → SVG, embedded as a data-URI `<img>`.

It worked for line art and `pgfplots` charts and failed, silently, on anything
richer. Two independent problems:

- **`pdf2svg` is built on Poppler**, which rasterizes or quietly drops the
  PostScript-backed features that make a diagram worth drawing — opacity,
  gradient fills, many `patterns` and `decorations`. The translucent field sheets
  above came out flat and opaque, or vanished entirely.
- **`pdflatex` has fixed memory.** A data-heavy `pgfplots` figure could hit
  `TeX capacity exceeded` and take the whole build down with it.

The fix was two substitutions in the renderer:

- **`lualatex`** instead of `pdflatex` — dynamic memory, so large diagrams stop
  overflowing.
- **`dvisvgm`** (with `mutool` as its PDF backend) instead of `pdf2svg` — it
  preserves transparency and vector detail, and `--no-fonts` converts text to
  paths so the SVG is self-contained.[@Gieseking2023]

The SVG is now embedded **inline** rather than as a data-URI image, so it scales
crisply and inherits page styling. And the filter degrades gracefully: a diagram
that won't compile is logged to the build output and replaced with a small error
box, instead of aborting the entire site.

### The Haskell, concretely

The renderer lives in a `Blog.TikZ` module. Its core is one `IO` action that
writes a standalone LaTeX document into a temp directory, runs the two external
tools, and returns `Either String String` — a diagnostic on failure, the SVG on
success:

```haskell
renderTikz :: String -> IO (Either String String)
renderTikz tikzCode = withSystemTempDirectory "blog-tikz" $ \dir -> do
  -- ... write preamble + body to tikz.tex ...
  (texCode, texOut, texErr) <- readProcessWithExitCode "lualatex"
    ["-halt-on-error", "-interaction=nonstopmode", "-output-directory=" ++ dir, texFile] ""
  case texCode of
    ExitFailure _ -> bail "lualatex" (texOut ++ texErr)
    ExitSuccess -> do
      (svgCode, svgOut, svgErr) <- readProcessWithExitCode "dvisvgm"
        ["--pdf", "--no-fonts", "--output=" ++ svgFile, pdfFile] ""
      case svgCode of
        ExitFailure _ -> bail "dvisvgm" (svgOut ++ svgErr)
        ExitSuccess   -> Right . T.unpack <$> TIO.readFile svgFile
```

Two details earn their keep. First, the filter is **smart about wrapping**: a
block that opens its own `\begin{tikzpicture}` — as the wave above does, to pass
the custom 3D basis in `[x={...}, y={...}, z={...}]` — is used verbatim, while a
bare body (like a lone `pgfplots` `axis`) is auto-wrapped. Second, `inlineSvg` is
a pure function that strips `dvisvgm`'s XML prolog and `DOCTYPE` so the markup is
safe to drop straight into HTML — pure, therefore unit-tested in the base-only
test suite, no TeX required.

## Dependencies

Reproducing the pipeline means two layers of tooling — local (macOS, for
previewing) and CI (Ubuntu, for the real deploy build):

**Local (Homebrew + TeX Live):**

- `brew install dvisvgm mupdf ghostscript` — `mupdf` provides `mutool`, which
  `dvisvgm` uses as its PDF backend (the bundled Ghostscript 10.x turned out to
  be *too new* for `dvisvgm`'s direct PDF reader, so `mutool` is the reliable
  path).
- TeX via `tlmgr install pgfplots mhchem standalone` on top of BasicTeX, which
  already ships `lualatex`.

**CI (`apt`):**

- added `dvisvgm`, `mupdf-tools`, and `texlive-luatex`;
- dropped `pdf2svg`.

A machine with *no* TeX at all still builds the site fine — the filter only
shells out when a post actually contains a `tikzpicture` block, so prose-only
posts never touch the toolchain.

## What the diagram proves

Look again at the figure: where the red and blue sheets overlap, you can see
straight through both. That transparency is the single feature `pdf2svg` used to
discard, and getting it back — without rasterizing, without a checked-in PNG, and
without making TeX-free builds impossible — is the whole point of the rebuild.
The physics earns the picture; the toolchain finally lets the picture be drawn.

*Credit: the electromagnetic-wave figure is adapted from the diagram gallery at
[diagrams.janosh.dev](https://diagrams.janosh.dev/light) (originally a CeTZ/Typst
drawing), ported here to native TikZ.*

## References
