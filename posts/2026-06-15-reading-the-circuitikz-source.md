---
title: Reading the source — the circuitikz behind four schematics
date: 2026-06-15
author: Peter Johnston
bibliography: bib/bibliography.bib
csl: bib/style.csl
tags: tikz, circuitikz, electronics, haskell, hakyll, rendering
description: A follow-up that opens up the four circuits from the previous post and shows the circuitikz source for each — the RC low-pass filter, the series RLC, the inverting op-amp, and the full-wave bridge rectifier — line by line.
---

The [previous post](/posts/2026-06-14-circuit-diagrams-with-circuitikz.html)
taught the build-time TikZ pipeline to draw electrical schematics with
[`circuitikz`](https://github.com/circuitikz/circuitikz) [@CircuiTikZ] and showed
off four classic circuits. It made the point that none of those figures are
images — each is a dozen lines of source the build compiles into vector SVG — but
it left that source mostly implicit. This post is the companion: each diagram,
re-rendered, with the exact `circuitikz` block that produced it printed underneath
and walked through.

The whole vocabulary is small. A component is a path operation: `to[R=$R$]` draws
a resistor between the previous coordinate and the next one and labels it $R$.
Relative moves use `++(dx,dy)`; the `|-` and `-|` operators route an orthogonal
path between two points; `o-o` and `-*` decorate the ends of a segment with open
or filled terminals. That is very nearly all four circuits need. The TikZ manual's
native circuit library covers the same ground with different syntax.[@TikzDevCircuits]

## 1 · An RC low-pass filter

A resistor in series, a capacitor to ground, output taken across the capacitor
.[@NilssonRiedel2019]

```tikzpicture
\begin{circuitikz}[scale=1.1, transform shape]
\draw (0,0) node[ground]{} to[sV=$v_\text{in}$] ++(0,3) coordinate(t);
\draw (t) to[R=$R$, o-o] ++(3,0) coordinate(o);
\draw (o) to[C=$C$] (o |- 0,0) -- (0,0);
\draw (o) to[short,-o] ++(1.2,0) node[right]{$v_\text{out}$};
\end{circuitikz}
```

And the source:

```latex
\begin{circuitikz}[scale=1.1, transform shape]
\draw (0,0) node[ground]{} to[sV=$v_\text{in}$] ++(0,3) coordinate(t);
\draw (t) to[R=$R$, o-o] ++(3,0) coordinate(o);
\draw (o) to[C=$C$] (o |- 0,0) -- (0,0);
\draw (o) to[short,-o] ++(1.2,0) node[right]{$v_\text{out}$};
\end{circuitikz}
```

Read it line by line. The first `\draw` starts at the origin, drops a `ground`
node there, then draws the source `sV` (a sinusoidal voltage source) straight up
three units, naming the top `coordinate(t)`. The second runs the resistor right
across to `coordinate(o)`, with `o-o` putting open terminals on both ends of that
top rail. The third drops the capacitor from `o` down to the point `(o |- 0,0)` —
"the *x* of `o`, the *y* of the origin" — then closes the loop back to the source.
The last line taps the output node off `o` with a short wire ending in an open
terminal. Its transfer function and corner frequency are

$$H(j\omega) = \frac{1}{1 + j\omega RC}, \qquad f_c = \frac{1}{2\pi RC}.$$

## 2 · A series RLC circuit

The whole loop is a single path, which is why this one is the shortest source of
the four.[@NilssonRiedel2019]

```tikzpicture
\begin{circuitikz}[scale=1.2, transform shape]
\draw (0,0) to[sV=$v_\text{in}$] ++(0,3) to[R=$R$] ++(2.4,0) to[L=$L$] ++(2.4,0) to[C=$C$] ++(0,-3) -- (0,0);
\end{circuitikz}
```

The source:

```latex
\begin{circuitikz}[scale=1.2, transform shape]
\draw (0,0) to[sV=$v_\text{in}$] ++(0,3) to[R=$R$] ++(2.4,0) to[L=$L$] ++(2.4,0) to[C=$C$] ++(0,-3) -- (0,0);
\end{circuitikz}
```

One `\draw` chains four components around a rectangle: up through the source,
right through `R=$R$`, right again through the inductor `L=$L$`, down through the
capacitor, and a plain `--` back to the origin to close it. Each `++(dx,dy)` is
relative to wherever the previous component ended, so the loop is described purely
by the deltas — no point is named. It resonates at $\omega_0$ with quality factor
$Q$:

$$\omega_0 = \frac{1}{\sqrt{LC}}, \qquad Q = \frac{1}{R}\sqrt{\frac{L}{C}}.$$

## 3 · An inverting op-amp amplifier

The active example, and the first to use a multi-terminal node — the `op amp`
shape exposes named anchors (`.+`, `.-`, `.out`) you draw to and from
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

The source:

```latex
\begin{circuitikz}[scale=1.2, transform shape]
\draw (0,0) node[op amp] (A) {};
\draw (A.+) -- ++(-0.7,0) node[ground]{};
\draw (A.-) -- ++(-1,0) coordinate(s);
\draw (s) to[R=$R_\text{in}$, o-] ++(-2.4,0) node[left]{$V_\text{in}$};
\draw (s) -- ++(0,2) coordinate(t) to[R=$R_f$] (t -| A.out) -- (A.out);
\draw (A.out) to[short,-o] ++(1.4,0) node[right]{$V_\text{out}$};
\end{circuitikz}
```

The first line places the triangle and names it `A`. The non-inverting input
`A.+` is wired to ground; the inverting input `A.-` runs left to a summing node
`coordinate(s)`. From `s`, the input resistor `R_\text{in}` goes out to the
source terminal (`o-` gives it one open end). The feedback path is the clever
line: from `s` it goes up two units to `coordinate(t)`, through `R_f` to the point
`(t -| A.out)` — "the *y* of `t`, the *x* of `A.out`", i.e. straight above the
output — then down into `A.out`, bridging input and output exactly as the
feedback resistor should. The gain is the resistor ratio set by that loop:

$$\frac{V_\text{out}}{V_\text{in}} = -\frac{R_f}{R_\text{in}}.$$

## 4 · A full-wave bridge rectifier

The showcase — four diodes in a diamond. Here named coordinates pay off, because
every diode and wire is expressed relative to the four corners
.[@HorowitzHill2015]

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

The source:

```latex
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

It opens by naming the diamond's four corners — left `L`, right `R`, positive
apex `P`, negative apex `N` — and then everything is anchored to them. The four
`to[D]` calls lay the diodes so all of them point *toward* the high side (into
`P`, or out of `N`), which is what makes the bridge rectify. The AC source hangs
off the left corner: down the left edge to `(sa|-N)` (below `sa`, level with `N`),
across the bottom rail to `(R|-N)`, and up into `R`. The output taps the top apex
`P` to a node `op` (with `-*`, a filled junction dot), the bottom apex routes
orthogonally with `-|` to meet it, and the load `R_L` spans the two — `op` to
`(op|-N)`, the output rail. After smoothing, the average output of an ideal
full-wave rectifier is

$$V_\text{dc} = \frac{2\,V_\text{peak}}{\pi}.$$

## The point of printing the source

Side by side, the four blocks show the same handful of moves doing all the work:
`to[...]` for components, `++` for relative geometry, `|-` and `-|` for clean
right-angle routing, and named coordinates when a circuit gets a shape worth
holding onto. Because the figure on the page *is* this text run through `lualatex`
and `dvisvgm`, the source above isn't a transcription that could fall out of sync
— it is, character for character, what the build compiled to draw the diagram a
few lines above it. That is the whole argument for schematics that compile.

## References
