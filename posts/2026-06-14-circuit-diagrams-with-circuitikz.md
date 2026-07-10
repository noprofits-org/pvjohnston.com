---
title: Schematics that compile — circuit diagrams in pure TikZ
date: 2026-06-14
author: Peter Johnston
bibliography: bib/bibliography.bib
csl: bib/style.csl
tags: tikz, circuitikz, electronics, haskell, hakyll, rendering
description: Teaching the build-time TikZ pipeline to draw electrical schematics with circuitikz, demonstrated with four classic circuits — an RC filter, a series RLC, an inverting op-amp, and a full-wave bridge rectifier.
---

A while back I [rebuilt this blog's TikZ pipeline](/posts/2026-06-14-rich-tikz-with-dvisvgm.html)
so diagrams compile from source at build time — `lualatex` renders a fenced
`tikzpicture` block, `dvisvgm` turns it into inline SVG, and the figure in the
Markdown *is* the figure on the page. That worked for field plots and `pgfplots`
charts, but one obvious thing was still missing: **circuit diagrams**. This post
adds them, and shows them off.

## The one-line backend change

Drawing schematics by hand in raw TikZ — battery symbols, resistor zig-zags,
op-amp triangles — is miserable. [`circuitikz`](https://github.com/circuitikz/circuitikz)
is the package that does it properly: components become path operations, so a
resistor between two points is just `to[R=$R$]`.[@CircuiTikZ] (TikZ also ships a
native circuit library, documented in the manual.[@TikzDevCircuits]) Teaching the
pipeline to use it took two small edits to the `Blog.TikZ` module:

```haskell
-- 1. load the package in the LaTeX preamble each diagram is wrapped in
"\\usepackage[american]{circuitikz}"

-- 2. let a block open its own circuitikz environment (used verbatim,
--    instead of being wrapped in a bare tikzpicture)
let opensOwnPicture =
      any (`isInfixOf` tikzCode) ["\\begin{tikzpicture}", "\\begin{circuitikz}"]
```

That's it. Because `circuitikz` builds on TikZ and the renderer already shells
out to `lualatex` + `dvisvgm`, no new tool was needed — only the package (already
present in CI's `texlive-latex-extra`). The four diagrams below are each compiled
on every build from the `circuitikz` source shown beneath them.

## 1 · An RC low-pass filter

The canonical first filter: a resistor in series, a capacitor to ground, output
across the capacitor. At low frequencies the capacitor is a high impedance and
the output follows the input; at high frequencies it shorts the signal to
ground.[@NilssonRiedel2019]

```tikzpicture
\begin{circuitikz}[scale=1.1, transform shape]
\draw (0,0) node[ground]{} to[sV=$v_\text{in}$] ++(0,3) coordinate(t);
\draw (t) to[R=$R$, o-o] ++(3,0) coordinate(o);
\draw (o) to[C=$C$] (o |- 0,0) -- (0,0);
\draw (o) to[short,-o] ++(1.2,0) node[right]{$v_\text{out}$};
\end{circuitikz}
```

Its transfer function and $-3\,\text{dB}$ corner frequency are

$$H(j\omega) = \frac{1}{1 + j\omega RC}, \qquad f_c = \frac{1}{2\pi RC}.$$

## 2 · A series RLC circuit

Add an inductor and the circuit gains a resonance: inductive and capacitive
reactances cancel at one frequency, leaving only $R$. It is the textbook
second-order system.[@NilssonRiedel2019]

```tikzpicture
\begin{circuitikz}[scale=1.2, transform shape]
\draw (0,0) to[sV=$v_\text{in}$] ++(0,3) to[R=$R$] ++(2.4,0) to[L=$L$] ++(2.4,0) to[C=$C$] ++(0,-3) -- (0,0);
\end{circuitikz}
```

It resonates at $\omega_0$ with quality factor $Q$:

$$\omega_0 = \frac{1}{\sqrt{LC}}, \qquad Q = \frac{1}{R}\sqrt{\frac{L}{C}}.$$

## 3 · An inverting op-amp amplifier

The active example. The op-amp drives its inverting input to match the grounded
non-inverting input — the **virtual ground** — so the current through $R_\text{in}$
must flow on through $R_f$, fixing the gain by a ratio of two resistors
.[@HorowitzHill2015]

```tikzpicture
\begin{circuitikz}[scale=1.2, transform shape]
\draw (0,0) node[op amp] (A) {};
\draw (A.+) -- ++(-0.7,0) node[ground]{};
\draw (A.-) -- ++(-1,0) coordinate(s);
\draw (s) to[R=$R_\text{in}$, o-] ++(-2.4,0) node[left]{$V_\text{in}$};
\draw (s) -- ++(0,2) coordinate(t) to[R=$R_f$] (t -| A.out) -- (A.out);
\draw (A.out) to[short,-o] ++(1.4,0) node[right]{$V_\text{out}$};
\end{circuitikz}
```

$$\frac{V_\text{out}}{V_\text{in}} = -\frac{R_f}{R_\text{in}}.$$

## 4 · A full-wave bridge rectifier

The showcase. Four diodes in a diamond steer either polarity of the AC input the
same way through the load: whichever way $v_\text{ac}$ swings, two diodes
conduct and the load always sees current top-to-bottom, so the output never
reverses.[@HorowitzHill2015]

```tikzpicture
\begin{circuitikz}[scale=1.25, transform shape]
\coordinate (L) at (0,0); \coordinate (R) at (3,0);
\coordinate (P) at (1.5,1.5); \coordinate (N) at (1.5,-1.5);
\draw (L) to[D] (P); \draw (N) to[D] (L);
\draw (R) to[D] (P); \draw (N) to[D] (R);
\draw (L) -- ++(-1.6,0) coordinate(sa);
\draw (sa) to[sV=$v_\text{ac}$] (sa|-N) -- (R|-N) -- (R);
\draw (P) to[short,-*] ++(1.8,0) coordinate(op) node[right]{$+$};
\draw (N) -| (op|-N) to[short,-*] (op|-N);
\draw (op) to[R=$R_L$] (op|-N);
\end{circuitikz}
```

After smoothing, the average output of an ideal full-wave rectifier is

$$V_\text{dc} = \frac{2\,V_\text{peak}}{\pi}.$$

## Why build-time matters

None of these are images. Each is text — a dozen lines of `circuitikz` — that the
build compiles into vector SVG. That means they version-control as diffs, restyle
with the page, scale without blurring, and can never drift out of sync with a
caption, because there is no binary to forget to re-export. The same pipeline now
covers field plots, chemical structures, 3D vector fields, and schematics; the
only thing each new domain needs is the right LaTeX package in the preamble.

## References
