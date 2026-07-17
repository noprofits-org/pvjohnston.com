---
title: "How slowly must you pump an anomalous soliton?"
date: 2026-07-17
author: Peter Johnston
tags: topological pumping, solitons, nonlinear dynamics, adiabaticity, cold atoms, numerical methods
description: A new anomalous soliton pump is quantized only in the adiabatic limit, and the paper says only that its parameter must be varied "sufficiently slowly". Measured, the anomalous pump needs a 4.7x slower ramp than the normal one — and above that threshold it still leaves the quantized value at 7 of 17 periods.
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
$T \approx 5600$ for the anomalous one — a factor of $4.7$, which supports the
hypothesis that routing a soliton through a branch point costs adiabaticity. The
larger effect is not the threshold. Above it the normal pump never leaves a
$\pm 0.15$ band around $-1$ across 28 periods, while the anomalous pump leaves the
band around $-2$ at 7 of 17 periods, reaching $-3.41$ at $T = 9600$, with a scatter
$7.1$ times larger. "Slowly enough" is therefore not a sufficient instruction for
the anomalous pump: particular periods fail well above the threshold.

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
error accumulates as $T\,\delta t^2$ and reaches $\sim 10^{-1}$ by $T \sim 10^4$,
which is not small compared to the quantity being measured. All results below use
4th-order Yoshida composition,[@Yoshida1990] error $\sim T\,\delta t^4$, at
$\delta t = 0.03$, and every reported value was checked against $\delta t = 0.04$,
$0.02$ and $0.01$. Norm is conserved to $\lesssim 10^{-10}$ throughout. The centre
of mass on a ring is the Resta phase estimator,[@Resta1998] unwrapped along the
trajectory; the Resta amplitude $|z|$ is recorded at every sample so that a
displacement is only reported while the state is still localized.

**Not done here.** The paper's continuous Gross–Pitaevskii model, its supercell
Chern analysis, and its stability analysis were not reproduced. The instantaneous
branch structure was not traced through the branch point, which needs
pseudo-arclength continuation; all statements below come from time evolution only.

Every number below is reproducible from
[soliton-pump-code.tar.gz](/downloads/soliton-pump-code.tar.gz), which needs
nothing but NumPy.

## Results

Time evolution reproduces three of the paper's four reported displacements
(Table 2). The fourth, case 3, was not reproduced at any period tested: at
$T = 9600$ it converges to $-19.3$ under $\delta t = 0.04$, $0.02$ and $0.01$.

| Case | $g$ | $g_{12}$ | $m_0$ | Paper | Measured | At |
| --- | --- | --- | --- | --- | --- | --- |
| normal | 1 | 1 | 1 | $-1$ | $-0.9928 \pm 0.0561$ | mean over $T \in [1200, 12000]$ |
| case 1 | $-1$ | 0 | 1 | $0$ | $-0.0003$ to $+0.0016$ | every $T \in [400, 12800]$ |
| case 2 | 1 | 0 | 1 | $-2$ | $-1.9921$ | $T = 6400$ |
| case 3 | 1 | 0 | 1.3 | $-3$ | $-19.33$ | $T = 9600$ |

**Table 2.** Pumped displacement in unit cells from direct time evolution,
against the values reported in the source's Fig. 2a.

The displacement of the normal pump first enters a $\pm 0.15$ band around $-1$ at
$T = 1200$. Across the 28 periods tested from $T = 1200$ to $T = 12000$, none lies
outside that band; the largest deviation is $0.124$ at $T = 7600$, and the standard
deviation is $0.0561$.

The displacement of the anomalous case 2 first enters a $\pm 0.15$ band around $-2$
at $T = 5600$. Across the 17 periods tested from $T = 5600$ to $T = 12000$, 7 lie
outside that band — $T = 8400$, $8800$, $9200$, $9600$, $10000$, $10400$ and
$10800$. The largest deviation is $1.410$, at $T = 9600$, where the displacement is
$-3.41$. The standard deviation over the same range is $0.3983$ (Table 3).

| | Normal | Anomalous (case 2) |
| --- | ---: | ---: |
| First period inside the $\pm 0.15$ band | $1200$ | $5600$ |
| Periods tested at or above it | 28 | 17 |
| Of those, outside the band | **0** | **7** |
| Largest deviation above it | $0.124$ | $1.410$ |
| Mean displacement above it | $-0.9928$ | $-2.0859$ |
| Standard deviation above it | $0.0561$ | $0.3983$ |

**Table 3.** Behaviour of the pumped displacement at and above the first period
that reaches the quantized value, $\pm 0.15$ band, 4th-order integration at
$\delta t = 0.03$.

The ratio of first-in-band periods, anomalous to normal, is $5600/1200 = 4.67$.

At $T = 9600$ the anomalous displacement takes the values $-3.7606$, $-3.7585$ and
$-3.7574$ under $\delta t = 0.04$, $0.02$ and $0.01$ respectively. Under
second-order Strang splitting at the same three step sizes the same quantity takes
the values $-0.2694$, $-0.2542$ and $-2.7950$.

Perturbing the initial soliton by a relative $10^{-12}$, $10^{-10}$ and $10^{-8}$,
with three random directions each, changes the displacement by $0.0000$ in every
instance, for the normal case at $T = 3200$, $6400$ and $12800$ and for the
anomalous case at $T = 3200$. For the anomalous case at $T = 6400$ the same holds
at $10^{-12}$ and $10^{-10}$; the $10^{-8}$ run was not completed.

The Resta amplitude $|z|$ of the evolving state has a minimum over the cycle of
$0.9702$–$0.9722$ for the normal case and $0.9112$–$0.9591$ for the anomalous case,
across all periods tested. Its value at $T = 25600$ for the normal case falls from
$0.9726$ to $0.9676$ over the cycle, with the participation ratio going from $7.226$
to $7.318$ cells.

## Discussion

**Verdict: the hypothesis is supported.** The pre-registered falsifier required the
two thresholds to agree within a factor of about 2; the measured ratio is $4.67$.
Routing a soliton through the intersite-soliton branch point costs roughly five
times the pump period that following a single Wannier function costs. The mechanism
proposed in the Introduction survives: the protecting scale for the anomalous
transition is not the band gap — which in this model is pinned at $2$ for the whole
cycle, and at $\theta = \pi$ both bands are exactly flat — but the splitting between
soliton branches at the point where they nearly touch, and that scale is set by the
nonlinearity and is much smaller.

**The threshold is the less useful half of the answer.** A factor of five in
required pump time is a nuisance; an experimentalist absorbs it. What does not
absorb is the second column of Table 3. Above its threshold the normal pump is
quantized in the operationally meaningful sense — pick any period you like above
$T \approx 1200$ and you get $-1$ to within 12%, 28 times out of 28. The anomalous
pump is not: 7 of 17 periods above its threshold miss $-2$, one of them by 70%, and
the scatter is $7.1$ times larger. Quantization means the answer does not depend on
the knob. For the anomalous pump, at these periods, it does.

So "vary $\theta$ sufficiently slowly" is not a sufficient instruction, and that is
the practical content of this note. The paper proposes realizing this in a $^7$Li
condensate with interactions tuned through a Feshbach resonance. An experimenter
following its guidance would choose a period long enough to look adiabatic and might
land on $T \approx 9600$, where the model returns $-3.41$ rather than $-2$ — and
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
composition, converged to three decimals. And the excursions are **not** sensitive
dependence: a $10^{-8}$ perturbation of the initial soliton moves the displacement
by exactly zero, so whatever selects $-3.41$ at $T = 9600$ is a smooth, deterministic
function of the period and not an amplified perturbation. Nor is it delocalization:
$|z|$ never falls below $0.91$, so the object being tracked is a soliton throughout.

**Limits.** One lattice size, one norm, one $L = 60$ ring; the periods are a grid
of 400, so a narrower excursion between grid points would have been missed, and the
$\pm 0.15$ band is a choice. Case 3 was not reproduced at all, which is unexplained
and might indicate that the $m_0 = 1.3$ soliton I track is not the branch the
authors follow — their own text notes that case 3's parameter window is narrow
($0 \le g_{12} \le 0.01$).

## Conclusion

The anomalous soliton pump costs about five times the pump period of the normal one
to reach its quantized displacement, and that number did not exist before: the
source states only that its parameter was varied "sufficiently slowly", in a paper
that proposes the effect for cold-atom experiment and cites three separate studies
of pumping breakdown without asking the question of its own mechanism.

What changed in what we know is smaller than the threshold and more awkward. Above
threshold the two pumps are not the same kind of object. The normal pump's
displacement is flat in the pump period, which is what quantization is supposed to
mean. The anomalous pump's is not — it wanders out to $-3.41$ at $T = 9600$ and back
to $-1.98$ at $T = 12000$, deterministically, with the integrator converged and the
soliton intact. A quantity that depends on the knob is not quantized, whatever the
instantaneous branch does.

The next experiment is to find out what sets those periods. The obvious candidate is
a resonance between the pump frequency $2\pi/T$ and an internal mode of the soliton
near the branch point — the frequency splitting between the soliton branches that
nearly touch at $\theta = \pi$. That splitting is computable from the Jacobian of the
stationary problem, which this note already builds, and the prediction is sharp
enough to be worth failing: the excursion periods should sit where an integer
multiple of $2\pi/T$ matches that splitting. If they do, the anomalous pump has a
usable design rule — a list of periods to avoid rather than a threshold to exceed.
That goes on the shelf.

## References
