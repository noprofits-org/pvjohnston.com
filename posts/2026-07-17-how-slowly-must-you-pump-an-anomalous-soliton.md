---
title: "How slowly must you pump an anomalous soliton?"
date: 2026-07-17
author: Peter Johnston
tags: topological pumping, solitons, nonlinear dynamics, adiabaticity, cold atoms, numerical methods
description: A new anomalous soliton pump is quantized only in the adiabatic limit, and the paper says only that its parameter must be varied "sufficiently slowly". Measured, the anomalous pump needs a 4.3x slower ramp than the normal one — and above that threshold it still misses the quantized value at 9 of 18 periods, once by more than a full unit cell.
contribution: The pump period required for quantized anomalous soliton transport, and its ratio to the normal pump's — a quantity Tao, Wang & Xu (2026) assert as "sufficiently slowly" and never measure, in a mechanism they propose for cold-atom experiment.
contribution-type: quantification
---

## Abstract

A recent *Nature Communications* paper reports an anomalous nonlinear Thouless
pump: a soliton displaced by 0, −2 or −3 unit cells per cycle while the Bloch band
it bifurcates from carries Chern number −1, driven by a transition between Wannier
functions through an intersite-soliton state. The result is a statement about the
adiabatic limit, and the paper's only quantitative claim about how that limit is
approached is that the pump parameter was varied "sufficiently slowly". No pump
period appears anywhere in it. I measure the period. Direct time evolution of the
paper's own discrete model reproduces three of its four reported displacements, and
locates the adiabatic threshold at $T \approx 1200$ for the normal pump and
$T \approx 5200$ for the anomalous one — a factor of $4.3$, which supports the
hypothesis that routing a soliton through a branch point costs adiabaticity. The
larger effect is not the threshold. Above it the normal pump leaves a $\pm 0.15$
band around $-1$ at only 1 of 28 periods, and then by $0.19$; the anomalous pump
leaves the band around $-2$ at 9 of 18 periods, once reaching $+0.35$ — a pump that
should advance the soliton two cells instead moving it essentially nowhere — with a
scatter $13$ times larger. "Slowly enough" is therefore not a sufficient
instruction for the anomalous pump: particular periods fail well above the
threshold, and both pumps fail worst at the same period, $T = 9200$.

## Introduction

Thouless taught us that a filled band transported through a cyclic parameter change
moves by an integer, and that the integer is the Chern number of the band.[@Thouless1983]
Nonlinearity complicates this in a productive way: a soliton, being a single
localized object rather than a filled band, can also be pumped, and its displacement
was found to be quantized too.[@Jurgensen2021] The mechanism was then identified —
the soliton rides an instantaneous Wannier function, so it inherits that Wannier
centre's displacement, which is the Chern number.[@Jurgensen2022] Under that
account a topologically trivial band cannot pump a soliton anywhere, because its
Wannier centre goes nowhere.

Tao, Wang and Xu break that correspondence.[@Tao2026] They exhibit a soliton
displaced by 0, −2 or −3 cells per cycle from a band whose Chern number is −1, and
explain it: near $\theta = \pi$ the soliton can pass through an **intersite-soliton**
state and emerge on a *different* Wannier function, so its displacement counts the
Wannier functions it has hopped between rather than the winding of any one of them.
They then construct a pump that moves a soliton across one cell from a band with
Chern number zero.

Every one of those numbers is a statement about the adiabatic limit. The soliton
must follow the instantaneous solution as $\theta$ turns, and the paper's evidence
that it does is this: "We have directly computed the time evolution based on Eq. (1)
when $\theta$ is varied **sufficiently slowly** and found that the results **closely
resemble** the instantaneous solutions."[@Tao2026] That is the whole of it. **No
pump period appears anywhere in the paper**, and no displacement-versus-rate curve
is plotted.

The gap is conspicuous because the surrounding literature is about exactly this.
The paper cites, and does not use, three studies of how pumping quantization
fails: quantization and its breakdown in a Hubbard–Thouless pump,[@Walter2023]
nonlinear Thouless pumping and transport breakdown,[@Fu2022] and breakdown of
quantization in nonlinear Thouless pumping.[@Tuloup2023] A new pumping mechanism
is introduced and the question those three papers ask is not asked of it.

There is a physical reason to expect the answer to be interesting rather than
routine. The normal pump follows a single Wannier function whose energy is
separated from the rest of the spectrum by the band gap, which in this model never
closes. The anomalous pump is defined by passing **through** a branch point where
distinct soliton solutions become degenerate. Adiabatic following near a
degeneracy is where it is hard, and the band gap is not the protecting scale there.

**Hypothesis.** The anomalous pump requires a substantially slower ramp than the
normal pump to reach its quantized displacement, because it routes the soliton
through an intersite-soliton state at which solution branches nearly touch.

**Falsifier**, fixed before running: the threshold period $T_c$ for quantized
transport is the same, within a factor of $\sim 2$, for the normal case
($g = g_{12} = m_0 = 1$, displacement $-1$) and the anomalous case ($g = 1$,
$g_{12} = 0$, $m_0 = 1$, displacement $-2$). The anomalous mechanism would then
carry no extra adiabaticity cost and the paper's silence would be harmless. I would
publish that outcome: the authors propose a cold-atom realization, experiments have
a finite coherence budget, and a null result is a green light.

## Computational Methods

All results were computed on CPython 3.13.12, arm64 macOS, with NumPy 2.4.4 and no
other dependency. No GPU was used.

**Model.** The paper's discrete model, its Eq. (2), is
$H^{\mathrm{lin}}(k) = (m_z + J_1 \cos k)\sigma_z + J_1' \sin k\,\sigma_y + J_2 \sigma_x$
with $m_z = m_0 + \cos\theta$, $J_1 = J_1' = 1$, $J_2 = \sin\theta$; the dynamics is
its Eq. (1),
$i\,\partial_t \psi_{\sigma j} = \sum H^{\mathrm{lin}}_{\sigma j,\sigma'j'}(\theta)\psi_{\sigma'j'} + V_{\sigma j}\psi_{\sigma j}$
with $V_{\sigma j} = g|\psi_{\sigma j}|^2 + g_{12}|\psi_{\bar\sigma j}|^2$. I use the
paper's $N = \sum_{\sigma j}|\psi_{\sigma j}|^2 = 1.45$ throughout, on a ring of
$L = 60$ unit cells. In real space $H^{\mathrm{lin}}$ is real symmetric, so
stationary solitons are taken real.

**Validation before any experiment.** The paper's code is not available: it cites a
Figshare deposit, but the DOI, the Figshare API and a title search all returned
nothing when checked on 2026-07-16 — the paper is an unedited Article in Press and
the data is presumably embargoed. Nothing here is therefore checked against the
authors' numbers, and the model is instead validated against four facts the paper
states or implies (Table 1).

| Check | Paper | Measured |
| --- | --- | --- |
| Real-space vs $k$-space spectrum | identical | max diff $5\times10^{-15}$ |
| Chern number of band 0 | $+1$ for $-2<m_0<0$; $-1$ for $0<m_0<2$; 0 otherwise | reproduced exactly at 8 values of $m_0$ |
| Wannier centre at $\theta=\pi$ | at $l + 1/2$ | $29.5$ on a 60-cell ring |
| $\chi = \sqrt{N}\,W_0$ at $\theta=\pi$ | "precisely the Wannier function multiplied by $\sqrt N$" | exact: residual $10^{-15}$, $\mu = -1 + 0.3625(g+g_{12})$ to 6 decimals |
| Wannier centre displacement per cycle | $= C = -1$ | $-1.000000$ |

**Table 1.** Independent checks of the reimplemented model against statements in
the source. At $\theta = \pi$ both bands are flat, which makes the fourth check
analytic rather than numerical.

**Initial soliton.** For $g > 0$ the soliton bifurcates from the *top* of band 0
(at $k = \pi$) into the gap, so the seed envelope must be staggered; Newton's method
then converges to $\mu = -0.860$ at $\theta = 0$ from every seed width tried.
Continuing that solution to $\theta = \pi$ reproduces $\sqrt{N}\,W_0$ with overlap
$1.000000$, which is what identifies it as the paper's branch.

**Time evolution.** $\theta(t) = 2\pi t/T$, integrated by split-step with the
nonlinear substep taken exactly (it is a phase rotation, so it preserves
$|\psi|^2$ and hence $V$). Second-order Strang splitting proved inadequate: its
error accumulates as $T\,\delta t^2$, so it is *largest* in exactly the
long-period limit of interest, and reaches $\sim 10^{-1}$ by $T \sim 10^4$. All
results below use 4th-order Yoshida composition,[@Yoshida1990] error
$\sim T\,\delta t^4$. Each pump period is integrated at step sizes
$\delta t = 0.02, 0.01, 0.005, 0.0025$ in turn until two successive sizes agree to
within $0.02$ in displacement; that value is reported and the period marked
converged. Every period in the scans below reached that criterion, the finer
anomalous excursions requiring $\delta t = 0.005$. A first version of this note
tabulated a single under-resolved scan at $\delta t = 0.03$ instead, which
misplaced the excursion values by up to $1.1$ cells; the convergence gate is the
correction. Norm is conserved to $\lesssim 10^{-10}$ throughout. The centre of mass
on a ring is the Resta phase estimator,[@Resta1998] unwrapped along the trajectory;
the Resta amplitude $|z|$ is recorded at every sample so that a displacement is only
reported while the state is still localized.

**Not done here.** The paper's continuous Gross–Pitaevskii model, its supercell
Chern analysis, and its stability analysis were not reproduced. The instantaneous
branch structure was not traced through the branch point, which needs
pseudo-arclength continuation; all statements below come from time evolution only.

Every number below is reproducible from
[soliton-pump-code.tar.gz](/downloads/soliton-pump-code.tar.gz), which needs
nothing but NumPy: `converge.py` runs the convergence-gated scan for each case and
`build_tables.py` rebuilds Tables 2 and 3 from its output.

## Results

Time evolution reproduces three of the paper's four reported displacements
(Table 2). The fourth, case 3, was not reproduced at any period tested: at
$T = 9600$ it takes the values $-19.23$, $-19.30$ and $-19.33$ under
$\delta t = 0.04$, $0.02$ and $0.01$.

| Case | $g$ | $g_{12}$ | $m_0$ | Paper | Measured | At |
| --- | --- | --- | --- | --- | --- | --- |
| normal | 1 | 1 | 1 | $-1$ | $-0.9796 \pm 0.0584$ | mean over $T \in [1200, 12000]$ |
| case 1 | $-1$ | 0 | 1 | $0$ | $-0.0009$ to $+0.0019$ | every $T \in [400, 12000]$ |
| case 2 | 1 | 0 | 1 | $-2$ | $-1.9921$ | $T = 6400$ |
| case 3 | 1 | 0 | 1.3 | $-3$ | $-19.33$ | $T = 9600$ |

**Table 2.** Pumped displacement in unit cells from direct time evolution,
against the values reported in the source's Fig. 2a. Cases normal, 1 and 2 are the
convergence-gated scan; case 3 is the three step sizes quoted above.

The displacement of the normal pump first enters a $\pm 0.15$ band around $-1$ at
$T = 1200$. Across the 28 periods from $T = 1200$ to $T = 12000$, one lies outside
that band: $T = 9200$, at $-0.815$, a deviation of $0.185$. The standard deviation
over the 28 periods is $0.0584$.

The displacement of the anomalous case 2 first enters a $\pm 0.15$ band around $-2$
at $T = 5200$. Across the 18 periods from $T = 5200$ to $T = 12000$, 9 lie outside
that band — $T = 7600$, $8400$, $8800$, $9200$, $9600$, $10000$, $10400$, $10800$
and $11200$. The largest deviation is $2.346$, at $T = 9200$, where the displacement
is $+0.346$; the next two are $-3.76$ at $T = 9600$ and $-3.02$ at $T = 8400$. The
standard deviation over the 18 periods is $0.7865$ (Table 3). The largest deviation
of each pump falls at the same period, $T = 9200$ (Figure 1).

```tikzpicture
\definecolor{ink}{HTML}{1A1D2B}
\definecolor{indigo}{HTML}{465C9B}
\begin{axis}[
    width=16cm, height=9cm,
    xlabel={pump period $T$ (thousands)},
    ylabel={displacement over one cycle (unit cells)},
    xmin=3.6, xmax=12, ymin=-4.5, ymax=1.0,
    xtick={4,5,6,7,8,9,10,11,12},
    ytick={1,0,-1,-2,-3,-4},
    grid=major,
    grid style={line width=.2pt, draw=gray!30},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85, font=\large},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large}
]
\fill[ink!8] (axis cs:3.6,-1.15) rectangle (axis cs:12,-0.85);
\fill[indigo!12] (axis cs:3.6,-2.15) rectangle (axis cs:12,-1.85);
\addplot[dashed, color=ink!55] coordinates {(3.6,-1)(12,-1)};
\addplot[dashed, color=indigo!70] coordinates {(3.6,-2)(12,-2)};
\draw[dashed, color=indigo!60] (axis cs:5.2,-4.5) -- (axis cs:5.2,1.0);
\addplot[thick, color=ink, mark=*, mark size=1.4pt] coordinates {
(3.6,-0.858) (4.0,-1.011) (4.4,-0.985) (4.8,-0.958) (5.2,-0.986) (5.6,-0.993)
(6.0,-0.983) (6.4,-1.007) (6.8,-0.994) (7.2,-1.051) (7.6,-0.897) (8.0,-0.950)
(8.4,-0.971) (8.8,-1.008) (9.2,-0.815) (9.6,-0.990) (10.0,-0.991) (10.4,-0.908)
(10.8,-0.998) (11.2,-1.036) (11.6,-1.019) (12.0,-0.990)
};
\addlegendentry{normal, $-1$}
\addplot[thick, color=indigo, mark=*, mark size=1.4pt] coordinates {
(3.6,-0.371) (4.0,0.593) (4.4,-4.244) (4.8,-0.703) (5.2,-1.935) (5.6,-1.922)
(6.0,-1.986) (6.4,-1.992) (6.8,-2.017) (7.2,-2.022) (7.6,-0.944) (8.0,-1.973)
(8.4,-3.018) (8.8,-2.221) (9.2,0.346) (9.6,-3.757) (10.0,-1.369) (10.4,-1.812)
(10.8,-1.792) (11.2,-1.822) (11.6,-1.998) (12.0,-1.956)
};
\addlegendentry{anomalous, $-2$}
\node[font=\large\bfseries, color=indigo] at (axis cs:5.2,0.65) {A};
\node[font=\large\bfseries] at (axis cs:9.2,0.62) {B};
\node[font=\large\bfseries, color=indigo] at (axis cs:9.28,-3.7) {C};
\end{axis}
```

**Figure 1.** Pumped displacement versus pump period $T$, above each pump's
adiabatic threshold, from the convergence-gated time evolution. Black: the normal
pump ($g=g_{12}=1$), target $-1$. Indigo: the anomalous pump ($g=1$, $g_{12}=0$),
target $-2$. Shaded strips are the $\pm 0.15$ bands around each target; the dashed
horizontal lines are the targets. **A** marks the anomalous threshold $T = 5200$
(the normal threshold, $T = 1200$, is off-scale to the left). **B** marks $T = 9200$,
where both pumps deviate farthest and in the same direction — the normal pump to
$-0.82$, the anomalous pump all the way to $+0.35$, a pump nominally worth two cells
that instead moves the soliton the wrong way. **C** marks the $-3.76$ excursion at
$T = 9600$. Below $T \approx 5200$ the anomalous displacement swings off-scale (it
reaches $+12$ and $-16$) because the soliton is not yet locked to its branch.

| | Normal | Anomalous (case 2) |
| --- | ---: | ---: |
| First period inside the $\pm 0.15$ band | $1200$ | $5200$ |
| Periods at or above it | 28 | 18 |
| Of those, outside the band | **1** | **9** |
| Largest deviation above it | $0.185$ | $2.346$ |
| Mean displacement above it | $-0.9796$ | $-1.8995$ |
| Standard deviation above it | $0.0584$ | $0.7865$ |

**Table 3.** Behaviour of the pumped displacement at and above the first period
that reaches the quantized value, $\pm 0.15$ band, convergence-gated 4th-order
integration. Every period converged; the anomalous excursions required
$\delta t = 0.005$.

The ratio of first-in-band periods, anomalous to normal, is $5200/1200 = 4.33$.

At $T = 9600$ the anomalous displacement takes the values $-3.7606$, $-3.7585$ and
$-3.7574$ under $\delta t = 0.04$, $0.02$ and $0.01$ respectively. Under
second-order Strang splitting at the same three step sizes the same quantity takes
the values $-0.2694$, $-0.2542$ and $-2.7950$.

Perturbing the initial soliton by a relative $10^{-12}$, $10^{-10}$ and $10^{-8}$,
with three random directions each, changes the anomalous displacement by $0.0000$
in every instance, at the excursion periods $T = 8800$ (unperturbed $-2.221$) and
$T = 9600$ (unperturbed $-3.757$).

The Resta amplitude $|z|$ of the evolving state has a minimum over the cycle, taken
across all periods tested, in the range $0.9384$–$0.9722$ for the normal case,
$0.9885$–$0.9978$ for case 1, and $0.8745$–$0.9591$ for the anomalous case 2.

## Discussion

**Verdict: the hypothesis is supported.** The pre-registered falsifier required the
two thresholds to agree within a factor of about 2; the measured ratio is $4.33$.
Routing a soliton through the intersite-soliton branch point costs roughly four
times the pump period that following a single Wannier function costs. The mechanism
proposed in the Introduction survives: the protecting scale for the anomalous
transition is not the band gap — which in this model is pinned at $2$ for the whole
cycle, and at $\theta = \pi$ both bands are exactly flat — but the splitting between
soliton branches at the point where they nearly touch, and that scale is set by the
nonlinearity and is much smaller.

**The threshold is the less useful half of the answer.** A factor of four in
required pump time is a nuisance; an experimentalist absorbs it. What does not
absorb is the second column of Table 3. Above its threshold the normal pump is
quantized in the operationally meaningful sense — of the 28 periods above
$T \approx 1200$, all but one give $-1$ to within 15%, and the exception misses by
$0.19$. The anomalous pump is not: 9 of 18 periods above its threshold miss $-2$,
and the scatter is $13$ times larger. At $T = 9200$ the anomalous displacement is
$+0.35$ — a pump nominally worth $-2$ cells that instead nudges the soliton the
wrong way. Quantization means the answer does not depend on the knob. For the
anomalous pump, at these periods, it does.

The two pumps reach their worst deviation at the same period, $T = 9200$: the normal
pump by $0.19$, the anomalous by $2.35$. A period-selective mechanism therefore acts
on both and is an order of magnitude stronger for the anomalous one — which is what a
resonance between the drive and an internal soliton mode would look like, and is the
thread the next experiment pulls on.

So "vary $\theta$ sufficiently slowly" is not a sufficient instruction, and that is
the practical content of this note. The paper proposes realizing this in a $^7$Li
condensate with interactions tuned through a Feshbach resonance. An experimenter
following its guidance would choose a period long enough to look adiabatic and might
land on $T \approx 9200$, where the model returns $+0.35$ rather than $-2$ — and
would have no way to know, from the paper, that the period was the problem.

**What this does not show.** It does not show the paper is wrong. Its Fig. 2a is a
statement about instantaneous solitons — a branch-following calculation — and I did
not trace those branches; at the one period where the two must agree most cleanly,
$T = 6400$, the time evolution returns $-1.9921$ against the reported $-2$. The
excursions are a property of the *dynamics* at finite period, which is a different
claim from the one the figure makes, and the paper's supporting sentence about time
evolution is too unquantified to be in conflict with anything. It cannot be checked
against the authors' own runs either, since neither the period, the lattice size,
nor the integrator is stated, and the deposited data is not yet reachable.

Two things I expected and did not find, both worth recording because they were
wrong. The large-period degradation I first measured was **my integrator**, not the
model: Strang splitting carries error $\sim T\delta t^2$, so at fixed step size it
gets worse in exactly the limit one is trying to reach, and the $-0.27$ and $-2.80$
it returns at $T = 9600$ are artefacts — the same quantity is $-3.757$ under 4th-order
composition, converged to three decimals. The same error, subtler, forced a rerun of
this note: an earlier version tabulated a single 4th-order scan at $\delta t = 0.03$
and reported the $T = 9600$ excursion as $-3.41$ and the count as 7 of 17. Neither
survived a proper convergence gate — $\delta t = 0.03$ was itself under-resolved for
the sharp excursions, off by $0.35$ there and by $1.1$ at $T = 7600$, and the
converged figures are $-3.76$ and 9 of 18. And the excursions are **not** sensitive
dependence: a $10^{-8}$ perturbation of the initial soliton moves the displacement by
exactly zero *at the excursion periods themselves* ($T = 8800$ and $9600$), so
whatever selects them is a smooth, deterministic function of the period and not an
amplified perturbation. Nor is it delocalization: $|z|$ stays above $0.87$, so the
object being tracked is a soliton throughout.

**Limits.** One lattice size, one norm, one $L = 60$ ring; the periods are a grid
of 400, so a narrower excursion between grid points would have been missed, and the
$\pm 0.15$ band is a choice. Case 3 was not reproduced at all, which is unexplained
and might indicate that the $m_0 = 1.3$ soliton I track is not the branch the
authors follow — their own text notes that case 3's parameter window is narrow
($0 \le g_{12} \le 0.01$).

## Conclusion

The anomalous soliton pump costs about four times the pump period of the normal one
to reach its quantized displacement, and that number did not exist before: the
source states only that its parameter was varied "sufficiently slowly", in a paper
that proposes the effect for cold-atom experiment and cites three separate studies
of pumping breakdown without asking the question of its own mechanism.

What changed in what we know is smaller than the threshold and more awkward. Above
threshold the two pumps are not the same kind of object. The normal pump's
displacement is nearly flat in the pump period, which is what quantization is
supposed to mean — one excursion in 28, and that one small. The anomalous pump's is
not — it swings to $+0.35$ at $T = 9200$ and $-3.76$ at $T = 9600$ and back to
$-1.96$ at $T = 12000$, deterministically, with the integrator converged and the
soliton intact. A quantity that depends on the knob is not quantized, whatever the
instantaneous branch does.

The next experiment is to find out what sets those periods, and the data already
points at it: both pumps deviate most at $T = 9200$, which is the fingerprint of a
period-selective resonance rather than a slow drift. The candidate is a resonance
between the pump frequency $2\pi/T$ and an internal mode of the soliton near the
branch point — the frequency splitting between the soliton branches that nearly touch
at $\theta = \pi$. That splitting is computable from the Jacobian of the stationary
problem, which this note already builds, and the prediction is sharp enough to be
worth failing: the excursion periods should sit where an integer multiple of
$2\pi/T$ matches that splitting. If they do, the anomalous pump has a usable design
rule — a list of periods to avoid rather than a threshold to exceed. That goes on the
shelf.

## References
