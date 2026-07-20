---
title: "Extending Villatoro et al.'s SIREN benchmark: the momentum control"
date: 2026-07-19
author: Peter Johnston
tags: neural networks, SIREN, initialization, optimization, momentum, reproducibility
post-type: research
description: An independent extension of Villatoro, Geraci, and Schiavazzi's 2026 multi-fidelity SIREN benchmark tests heavy-ball momentum, preserving the omega_0 squared hidden-step factor while moving the stability boundary up by about 1+beta and closing the K1 accuracy gap at one tested rate.
contribution: A measured momentum control on the SIREN convention gap — the isolated omega_0 squared factor and the linear-regime shared-to-hidden balance survive beta up to 0.99, the stability boundary and best tested rate move up by approximately 1+beta, and the described convention reaches the official convention's error floor — none of which is in my SGD note or in Villatoro et al.
contribution-type: untested regime
---

## Abstract

Villatoro, Geraci, and Schiavazzi's 2026 article, *Assessing the Performance of
Correlation-Based Multi-Fidelity Neural Emulators*, benchmarks SIREN on a set
of multi-fidelity tasks but does not test heavy-ball momentum.[@Villatoro2026]
This independent reimplementation extends that written K1 specification and
[yesterday's SGD control](/posts/2026-07-18-the-sgd-control-900-on-the-hidden-stack.html)
with heavy-ball momentum, whose update is linear in the gradient and should
therefore preserve plain SGD's $\omega_0^2 = 900$ convention factor on the
isolated hidden stack. It does — the $\times 900$
hidden-rate reparameterization tracks the official convention to
$6.4\times10^{-16}$ relative over $200$ isolated steps at $\beta=0.9$, and the
common-rate displacement ratio reaches $900.006$ in the small-step limit. The
shared-to-hidden displacement balance is likewise unchanged by momentum in the
linear regime: at $\text{lr}=10^{-12}$ the described convention's ratio moves
from $5729$ to $5704$ as $\beta$ goes from $0$ to $0.9$, with both parameter
groups' velocities amplified by $10.0$. All three declared falsifiers fired.
F1 and F2 were evaluated at settings where displacements had saturated at the
output scale — a protocol error recorded below — while F3 fired because one
official repetition selected a different rate on the numerical error floor.
The stable boundary moves *up* by a factor of $1.995 \approx 1+\beta$, not down
by $1/(1-\beta)$, and at the best tested rate the described
convention now reaches normalized test MSE $3.4\times10^{-29}$ to
$1.9\times10^{-28}$ — the eight-to-nine-order accuracy gap measured under
plain SGD is gone, though the described convention reaches that floor at
exactly one tested learning-rate grid point.

## Introduction

The two circulating SIREN parameterizations represent the same function and
train differently, and the difference is set by the optimizer. The described
convention draws hidden weights from $\mathcal{U}(\pm\sqrt{6/n})$ and applies
$\sin(Wx+b)$; the official implementation draws from
$\mathcal{U}(\pm\sqrt{6/n}/\omega_0)$ and applies
$\sin(\omega_0(Wx+b))$.[@Sitzmann2020; @SirenOfficial] Under Adam the hidden
function-space steps differ by
[a factor of $\omega_0=30$](/posts/2026-07-17-why-the-two-siren-conventions-train-differently.html);
under plain SGD the
[isolated hidden stack returns $\omega_0^2=900$](/posts/2026-07-18-the-sgd-control-900-on-the-hidden-stack.html),
while on the full K1 task of Villatoro et al. the shared first layer, readout,
and affine branch dominate the displacement so strongly that both conventions
select the same global learning rate at $0.05$-decade resolution — with best
tested errors eight to nine orders of magnitude apart.[@Villatoro2026]

That SGD note tested the optimizer at $\beta=0$ and nothing else, and its
Conclusion queued the obvious next perturbation. Momentum's update,

$$
v \leftarrow \beta v + g, \qquad \theta \leftarrow \theta - \text{lr}\cdot v,
$$

remains **linear in the gradient**, so every argument that produced the $900$
should pass through the velocity accumulation untouched. The same linearity
says the accumulation multiplies every parameter group by the same factor —
$1/(1-\beta)$ for a persistent gradient — so the shared-to-hidden balance
should not move either. What the linear picture does *not* fix is the
trajectory: whether accumulated velocity changes which convention trains, at
which global rate, to what error, over twenty thousand epochs. None of that has
been measured, here or in the source.

**Hypothesis.** Because momentum is linear in the gradient and accumulates
identically across parameter groups: (i) the isolated hidden-stack factor
stays $\omega_0^2=900$ and the $\times 900$ hidden-rate reparameterization
stays exact at machine precision; (ii) the full-network shared-to-hidden
balance and the common best tested global rate carry over from plain SGD, with
the stable window shifted down by roughly $1/(1-\beta)$. **Falsifiers, fixed
before running:** F1 — the isolated common-rate displacement ratio after $200$
steps at $\text{lr}=10^{-8}$, $\beta=0.9$ falls outside $[800,1000]$, or the
reparameterized trajectory departs by more than $10^{-10}$ relative; F2 — the
described convention's shared-to-hidden ratio at that same setting differs
from its $\beta=0$ value by more than a factor of $2$; F3 — the two
conventions select different best tested rates on a $0.05$-decade momentum
grid over three repetitions. Any firing was publishable; all three fired, and
what they measured is part of the story.

## Computational Methods

All numbers were produced on CPython 3.10.12, aarch64 Linux, NumPy 2.2.6, no
other dependency. This was a computer-only numerical experiment using
synthetic inputs and deterministic code; it involved no living subjects and
no human or animal data. Model, task, data, seeds, and manual backprop are those of
the SGD note without change: K1 from Villatoro et al., eq. (4), fit by their
multi-fidelity architecture with the exact low-fidelity function, the
nonlinear branch a SIREN of three hidden layers of sixteen units,
$\omega_0=30$, $c=6$, $N_H=32$ Sobol' samples plus the two boundary points,
errors reported as normalized test MSE with denominator
$20.0631$.[@Villatoro2026] Both conventions in a repetition start from one
parameter draw; the matched official parameterization divides hidden weights
*and* biases by $\omega_0$, the same declared idealization as before — the
official repository rescales weights alone.[@Sitzmann2020; @SirenOfficial]
The analytic gradients were re-checked against central finite differences,
with worst-case relative errors of $1.3\times10^{-6}$ (described) and
$4.4\times10^{-8}$ (official); the two conventions' initial outputs agree to
$1.776\times10^{-15}$ on a maximum output magnitude of $11.0036$.

The single change is the update (Code 1): full-batch heavy-ball momentum with
coefficient $\beta$, primary value $\beta=0.9$, run for $20{,}000$ epochs in
the sweeps. Setting $\beta=0$ reproduces the SGD script's update exactly and
is measured through the same code path wherever a plain-SGD reference is
quoted.

```python
V = {k: np.zeros_like(v) for k, v in P.items()}
for t in range(1, epochs + 1):
    yh, cache = forward(P, u_tr, official, keep=True)
    g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
    for k in P:
        if isolate and k not in HIDDEN:      # freeze shared parameters
            continue
        gk = g[k].reshape(P[k].shape)
        V[k] = beta * V[k] + gk              # heavy-ball velocity
        step = hidden_lr if (hidden_lr is not None and k in HIDDEN) else lr
        P[k] -= step * V[k]
```

**Code 1.** The heavy-ball update and the isolation switch. `beta=0` recovers
plain SGD; `hidden_lr` applies a separate rate to hidden weights and biases,
which is how the $\times 900$ reparameterization check is run.

The protocol — hypothesis, the three falsifiers, and their exact settings —
was written into the script header before any run. The declared measurements
are: the common-rate displacement ratio after $1$ and $200$ steps at
$\text{lr}=10^{-9}$ through $10^{-6}$, full network and isolated stack; the
$200$-step isolated reparameterization trajectory at $10^{-6}$ and $10^{-8}$;
the $200$-step shared-only / hidden-only / full decomposition at
$\text{lr}=10^{-8}$ for $\beta\in\{0,0.5,0.9,0.99\}$ with per-group final
velocity max-norms; a half-decade sweep from $10^{-8}$ to $10$; and a
$0.05$-decade refined sweep over the stable decade indicated by the broad
sweep, three repetitions, data seeds $1544$–$1546$ and parameter seeds
$7000$–$7002$ as before. Two diagnostics were added **after** falsifiers F1
and F2 fired at their declared settings and are labeled post hoc throughout:
the same ratio measurement at $\text{lr}=10^{-12}$ through $10^{-10}$, and
the same decomposition at $\text{lr}=10^{-12}$. Regularization penalties stay
fixed at zero; the ratio, trajectory, and decomposition measurements use one
initialization (seed $7000$). I used neither the source authors' program nor
their data: their code remains unreleased, K1 is a closed-form test case printed
in the paper, and every number describes my independent NumPy reimplementation
of their written specification.

Code 2 gives the exact invocations used to regenerate the diagnostics and all
seven JSON outputs from the `downloads` directory.

```bash
python3 siren-convention-momentum.py identity
python3 siren-convention-momentum.py gradcheck
python3 siren-convention-momentum.py ratio
python3 siren-convention-momentum.py traj 1e-6
python3 siren-convention-momentum.py traj 1e-8
python3 siren-convention-momentum.py decompose 1e-8 200
python3 siren-convention-momentum.py decompose 1e-12 200
python3 siren-convention-momentum.py sweep:1
python3 siren-convention-momentum.py refine:3 -3.5
```

**Code 2.** Exact commands for the initialization and gradient checks, declared
and post-hoc diagnostics, broad sweep, and three-repetition refined sweep.

The script is
[siren-convention-momentum.py](/downloads/siren-convention-momentum.py); raw
outputs are
[momentum_ratio.json](/downloads/momentum_ratio.json),
[momentum_ratio_posthoc.json](/downloads/momentum_ratio_posthoc.json),
[momentum_traj.json](/downloads/momentum_traj.json),
[momentum_decomposition.json](/downloads/momentum_decomposition.json),
[momentum_decomposition_1e-12.json](/downloads/momentum_decomposition_1e-12.json),
[momentum_sweep.json](/downloads/momentum_sweep.json), and
[momentum_refined_sweep.json](/downloads/momentum_refined_sweep.json).

## Results

Table 1 lists the isolated-stack displacement ratio at a common learning rate,
$\beta=0.9$. After one step the ratio is $899.86$ at $\text{lr}=10^{-8}$.
After $200$ steps it is $202.37$ at the declared F1 setting, with the official
displacement at $4.359$ and the described displacement at
$2.154\times10^{-2}$ against a maximum test-output magnitude of $11.0036$; the
described displacement scales as $2.154\times10^{-6} \to 2.154\times10^{-5}
\to 2.154\times10^{-4}$ across the post-hoc rates. In the post-hoc small-rate
runs the $200$-step ratio is $900.006$ at $10^{-12}$.

| run | $\text{lr}$ | steps | isolated ratio | official $\max\lvert\Delta y\rvert$ |
| --- | ---: | ---: | ---: | ---: |
| declared | $10^{-8}$ | $1$ | $899.86$ | $1.01\times10^{-2}$ |
| declared | $10^{-9}$ | $200$ | $703.32$ | $1.515$ |
| declared | $10^{-8}$ | $200$ | $202.37$ | $4.359$ |
| declared | $10^{-7}$ | $200$ | $23.34$ | $5.015$ |
| post hoc | $10^{-10}$ | $200$ | $898.22$ | $1.935\times10^{-1}$ |
| post hoc | $10^{-11}$ | $200$ | $900.04$ | $1.938\times10^{-2}$ |
| post hoc | $10^{-12}$ | $200$ | $900.006$ | $1.938\times10^{-3}$ |

**Table 1.** Isolated hidden-stack displacement ratio (official / described)
at a common learning rate under $\beta=0.9$, with the official convention's
absolute displacement at the listed step count; the declared F1 setting is
$\text{lr}=10^{-8}$ for $200$ steps.

On the isolated stack, the described convention at hidden rate
$900\times\text{lr}$ tracks the official convention at $\text{lr}$ with a
maximum per-step output difference of $3.11\times10^{-14}$ over $200$ steps at
$\text{lr}=10^{-6}$; the final difference is $2.75\times10^{-14}$, relative
$2.6\times10^{-15}$. At $10^{-8}$ the maximum and final difference are both
$4.44\times10^{-15}$, relative $6.4\times10^{-16}$.

Table 2 gives the $200$-step decomposition at the post-hoc linear-regime rate.
Across $\beta = 0, 0.5, 0.9, 0.99$ the described shared-to-hidden ratio is
$5729$, $5726$, $5704$, $5622$; the hidden convention factor is $900.001$,
$900.002$, $900.006$, $899.948$; and the full-network ratio stays at $1.157$.
Between $\beta=0$ and $\beta=0.9$ the final velocity max-norms grow by factors
of $10.031$ (shared, described) and $9.993$ (hidden, described). At the
declared F2 setting, $\text{lr}=10^{-8}$, the described shared-to-hidden
ratio is $1100.3$ at $\beta=0$ and $166.5$ at $\beta=0.9$ — a factor of
$6.61$ — while the shared-group displacements reach $2.48$ to $6.04$ and the
residual of the additive reconstruction reaches $3.80$ (official, $\beta=0.9$)
against a full displacement of $5.47$.

| $\beta$ | S/h described | S/h official | hidden factor | velocity amp. (shared, hidden) |
| ---: | ---: | ---: | ---: | ---: |
| $0$ | $5729.3$ | $6.366$ | $900.001$ | — |
| $0.5$ | $5726.1$ | $6.362$ | $900.002$ | $2.001$, $2.000$ |
| $0.9$ | $5703.9$ | $6.338$ | $900.006$ | $10.031$, $9.993$ |
| $0.99$ | $5622.3$ | $6.247$ | $899.948$ | $87.56$, $86.39$ |

**Table 2.** Post-hoc $200$-step decomposition at $\text{lr}=10^{-12}$:
shared-to-hidden maximum-displacement ratio per convention, the hidden-stack
convention factor, and the described convention's final velocity max-norm
amplification relative to $\beta=0$.

In the broad sweep at $\beta=0.9$, both conventions' lowest error on the
half-decade grid occurs at $\text{lr}=10^{-3}$ — $4.7\times10^{-8}$
(described) and $4.2\times10^{-29}$ (official) — and both first return
non-finite error at $3.16\times10^{-3}$. Table 3 summarizes the refined
$0.05$-decade sweep. All six convention-repetition pairs first return
non-finite error at $1.412538\times10^{-3}$. The best tested rate is
$1.258925\times10^{-3}$ — the last finite grid point — in five of six pairs;
in repetition 0 the official convention's minimum sits at
$1.0\times10^{-3}$ with $4.17\times10^{-29}$, and its error at
$1.258925\times10^{-3}$ is $6.03\times10^{-29}$. At the shared rate
$10^{-3}$ the described errors are $4.7\times10^{-8}$, $8.4\times10^{-8}$,
and $2.9\times10^{-6}$; at $1.258925\times10^{-3}$ they are
$1.9\times10^{-28}$, $3.4\times10^{-29}$, and $6.8\times10^{-29}$. The
plain-SGD reference values from the SGD note are a best tested rate of
$6.309573\times10^{-4}$ and a first non-finite rate of
$7.079458\times10^{-4}$ in all six pairs; the momentum-to-SGD ratio is
$1.9953$ for the boundary and $1.9953$ for the modal best rate, with
$1+\beta=1.9$ and a grid step of $1.122$.

| Convention | rep | best tested lr | normalized test MSE | first non-finite lr |
| --- | ---: | ---: | ---: | ---: |
| official | 0 | $1.000000\times10^{-3}$ | $4.1739\times10^{-29}$ | $1.412538\times10^{-3}$ |
| official | 1 | $1.258925\times10^{-3}$ | $2.3473\times10^{-29}$ | $1.412538\times10^{-3}$ |
| official | 2 | $1.258925\times10^{-3}$ | $4.0529\times10^{-29}$ | $1.412538\times10^{-3}$ |
| described | 0 | $1.258925\times10^{-3}$ | $1.9158\times10^{-28}$ | $1.412538\times10^{-3}$ |
| described | 1 | $1.258925\times10^{-3}$ | $3.4399\times10^{-29}$ | $1.412538\times10^{-3}$ |
| described | 2 | $1.258925\times10^{-3}$ | $6.8100\times10^{-29}$ | $1.412538\times10^{-3}$ |

**Table 3.** Lowest finite normalized test MSE and first non-finite rate on
the $0.05$-decade momentum grid from $3.16\times10^{-4}$ through
$3.16\times10^{-3}$, per convention and repetition, $\beta=0.9$.

## Discussion

**Overall verdict: falsified as registered.** All three falsifiers fired. The
first two exposed bad regime choices in the protocol rather than failures of
the linear mechanism, while the third recorded a different selected grid point
in one repetition on the numerical error floor.

**Verdict on the mechanism (clause i): supported — with a protocol failure to
report first.** Falsifier F1 fired as declared: the common-rate ratio at
$\text{lr}=10^{-8}$, $200$ steps is $202.37$, outside $[800,1000]$. The chase
went through my own Methods before anywhere else, and the explanation is in
Table 1's last column: at the declared setting the official convention's
$200$-step displacement is $4.36$ on a test-output scale of $11$ — the
premise that both displacements are small, which the $900$ prediction
requires, does not hold at the setting I pre-registered. The described
displacement scales exactly linearly across four decades while the official
displacement saturates, and at rates where both are small the ratio returns
to $900.006$. The sharper statement of the same mechanism — that a
$\times 900$ hidden rate makes the described convention *identical* to the
official one — held at machine precision, $6.4\times10^{-16}$ relative over
$200$ steps, which is the no-$\varepsilon$ exactness the SGD note measured,
now with velocity in the loop. F2 is the same story in a different
measurement: its declared setting produces shared displacements of $2.5$ to
$6.0$ and an additive-reconstruction residual as large as $70\%$ of the full
displacement, so the quantity it varies with $\beta$ is not a linear-regime
balance at all. In the regime where the decomposition reconstructs — Table 2 —
the balance moves by less than $2\%$ from $\beta=0$ to $\beta=0.9$ and both
groups' velocities amplify by $10.0$, the $1/(1-\beta)$ factor, together. The
lesson is recorded: a falsifier pinned to a specific $(\text{lr}, n)$ needs
the same regime check as any other number, *before* registration. Declaring
the criteria badly cost a post-hoc label on the diagnostics; it did not change
what the mechanism does.

**Verdict on the window direction: falsified.** I predicted the stable window
would shift down by roughly $1/(1-\beta)=10$, reasoning from the asymptotic
velocity amplification. It moved up by $1.9953$ — within half a grid step of
$1+\beta=1.9$. The failure of my prediction is elementary: for a quadratic
mode with curvature $L$, the heavy-ball recurrence $x_{t+1} = x_t -
\text{lr}(\beta v_t + L x_t)$, $v_{t+1}=\beta v_t + Lx_t$ has its divergence
threshold at $\text{lr}\,L = 2(1+\beta)$, against $2$ for gradient descent —
the boundary rises even as the effective step on persistent gradients grows.
Both measured numbers — the boundary ratio and the modal best-rate ratio,
each $1.9953$ — are consistent with that bound at the grid's resolution. The
$1/(1-\beta)$ intuition answers a different question than the one stability
asks.

**The unpredicted result is Table 3's error column.** Under plain SGD the
described convention was effectively untrainable at one global rate on K1:
best tested errors of $4.8\times10^{-6}$ to $1.0\times10^{-5}$ against the
official convention's $10^{-14}$–$10^{-15}$. With $\beta=0.9$ the described
convention reaches $3.4\times10^{-29}$ to $1.9\times10^{-28}$ — the official
floor, within an order — and F3's best-rate criterion fired in one repetition
of three, by two $0.05$-decade grid steps, between errors that both sit on that
floor. I read that firing as floor noise rather than a resolved gap, and the
identical first non-finite rate in all six pairs supports the reading, but
the criterion as declared fired and is reported as fired. The equalization is
narrow, though. At the shared rate $10^{-3}$, two grid steps below the
described convention's best tested rate, the
conventions are still twenty orders apart; the described convention reaches
its floor at exactly one tested grid point, the last finite point, while the
official convention stays below $2.5\times10^{-27}$ across the entire
$0.6$-decade finite grid.
Momentum has not removed the convention hazard; it has compressed it into
extreme rate sensitivity at the edge of stability. A practitioner tuning the
described parameterization under heavy-ball momentum on a task like K1 will
find a sharp optimum hard against the divergence boundary, and a coarser grid
than $0.05$ decades would miss it entirely — the half-decade broad sweep did,
returning $4.7\times10^{-8}$ as its apparent best.

**Limits.** One task, whose exactly linear cross-correlation lets the affine
branch carry the fit; one architecture; heavy-ball momentum without a Nesterov
arm; $\beta=0.9$ alone in the sweeps; one initialization for the ratio,
trajectory, and decomposition measurements and three for the sweeps; a
$0.05$-decade grid whose floor comparisons sit within an order of magnitude of
each other; and a reimplementation of an unreleased specification. The
quadratic stability argument is exact for a quadratic mode and heuristic here;
I have not decomposed which mode fails at $1.412538\times10^{-3}$.

## Conclusion

The momentum control closes the loop the SGD note opened: the convention
factor $\omega_0^2=900$ and the shared-dominated balance both pass through
heavy-ball momentum untouched where the linear argument applies. All three
declared falsifiers fired: F1 and F2 measured displacement saturation rather
than mechanism failure, while F3 recorded different best grid points in one
repetition on the numerical error floor. What momentum does change sits at the
trajectory level — the stable boundary rises by about $1+\beta$ at this grid's
resolution, and the described
convention recovers the official error floor at exactly one tested grid point.
Two experiments follow. First,
the size of that recovered-rate region as a function of $\beta$: if it scales with
the gap between the heavy-ball and gradient-descent stability bounds, it
should close as $\beta\to0$ and widen toward $1+\beta$ — a measurable curve,
with the first point already measured at $\beta=0.9$. Second, the
[nonlinear cross-correlation test](/posts/2026-07-18-the-sgd-control-900-on-the-hidden-stack.html)
already on the shelf gains a momentum arm: on a K-case where the affine branch
cannot carry the fit, does the described convention's single-tested-point
recovery survive, or does the hazard return in full? Both go on the shelf.

## References
