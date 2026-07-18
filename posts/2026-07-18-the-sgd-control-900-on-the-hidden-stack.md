---
title: "The SGD control: 900 on the hidden stack, no resolved learning-rate gap on K1"
date: 2026-07-18
author: Peter Johnston
tags: neural networks, SIREN, initialization, optimization, sgd, reproducibility
description: Yesterday's Adam note predicted that the two SIREN conventions' hidden function-space steps differ under plain SGD by omega_0 squared. On the isolated stack they do — 899.86 — while a direct displacement decomposition and a 0.05-decade sweep resolve no global learning-rate gap on K1.
contribution: A direct measurement of the two SIREN conventions' SGD hidden-step ratio — omega_0 squared = 900 — and of its absence from K1's best tested global learning rate at 0.05-decade resolution, neither of which is in my Adam note or in Villatoro et al.
contribution-type: untested regime
---

## Abstract

[Yesterday's note](/posts/2026-07-17-why-the-two-siren-conventions-train-differently.html)
showed that, in a matched construction that rescales hidden biases as well as
weights, the two circulating SIREN parameterizations represent the same initial
function to sixteen digits but take hidden-layer Adam steps differing by
$\omega_0=30$, and predicted a plain-SGD factor of $\omega_0^2=900$. On the
**isolated hidden stack** — the first layer, readout, and affine branch frozen —
the single-step function-space displacement ratio is $899.86$ at
$\text{lr}=10^{-8}$; multiplying the described hidden rate by $900$ reproduces
the official convention to $2.7\times10^{-15}$ over $200$ steps, with none of
Adam's $\varepsilon$-seeded drift. A direct full-network decomposition at that
rate measures maximum output displacements of $6.435\times10^{-2}$ from the
shared parameters, $1.128\times10^{-5}$ from the described hidden stack, and
$1.015\times10^{-2}$ from the official hidden stack: shared exceeds the two
hidden displacements by factors of $5707$ and $6.34$, and the full-network ratio
is $1.157$. In a three-repetition sweep from $10^{-4}$ to $10^{-3}$ at
$0.05$-decade spacing, both conventions have their lowest tested error at
$6.31\times10^{-4}$ and first return non-finite error at $7.08\times10^{-4}$.
No global learning-rate gap is resolved on K1, although the official normalized
MSE reaches $5.6\times10^{-15}$ to $1.2\times10^{-14}$ and the described stops at
$4.8\times10^{-6}$ to $1.0\times10^{-5}$. The convention controls the best
tested accuracy after $20{,}000$ epochs; the shared parameters control the
selected global rate.

## Introduction

A SIREN's two conventions store the same sinusoidal network in parameters that
differ by a factor of $\omega_0$: the described convention draws hidden weights
from $\mathcal{U}(\pm\sqrt{6/n})$ and applies $\sin(Wx+b)$, the official
implementation draws from $\mathcal{U}(\pm\sqrt{6/n}/\omega_0)$ and applies
$\sin(\omega_0(Wx+b))$. For the matched-function control below I divide both
hidden weights and hidden biases by $\omega_0$, so the division cancels the
multiplication and a common draw gives the same function. This is one declared
idealization: the official repository rescales only weights, while biases keep
the framework's default initialization, so the exact-equivalence claims below
describe the matched parameterization rather than its literal initialization.[@Sitzmann2020; @SirenOfficial]
Yesterday I showed that this cancellation is a statement about the forward pass
and says nothing about the optimizer, which acts on the parameters: **under Adam,
whose step size is set by the learning rate and is almost independent of gradient
magnitude, the official convention's $\omega_0$-times-smaller hidden weights take
an $\omega_0$-times-larger step in function space.** The measured per-layer factor
needed to reproduce one convention from the other was $\omega_0 = 30$.

Two loose ends were left explicit in that note's Conclusion. The first is the
optimizer. Adam normalizes its step by the gradient's own second moment;
**plain SGD does not** — its step *is* the gradient, scaled by the learning
rate. Rescale a weight down by $\omega_0$ and its gradient scales *up* by
$\omega_0$, so the SGD step on the stored weight is $\omega_0$ times larger, and
that step lands on a weight the forward pass multiplies by $\omega_0$ once more.
The function-space displacement therefore carries two factors of $\omega_0$, not
one: a predicted per-layer factor of $\omega_0^2 = 900$, and — with no
normalizing denominator — no $\varepsilon$ caveat on its exactness. The second
loose end is dilution. The Adam factor was *predicted* to be $30$ and *measured*
at $10$. I attributed that shortfall to the first layer and readout, which are
common to both conventions and unscaled, but never decomposed their contribution.

**Hypothesis.** On the isolated hidden stack — every shared parameter frozen —
the single-step function-space displacement of the official convention exceeds
the described convention's by $\omega_0^2 = 900$ in the small-learning-rate
limit, and rescaling the described convention's hidden learning rate by $900$
reproduces the official convention step for step. **Falsifier**, fixed before
running: the isolated-stack ratio in that limit is not near $900$ — a value near
$\omega_0 = 30$ would put SGD and Adam in the same class and kill the
squared-factor argument, and a value near $1$ would kill the mechanism outright.
Either is publishable; a null on the mechanism I have leaned on twice now is the
more useful result.

## Computational Methods

All numbers were produced on CPython 3.10.12, aarch64 Linux, NumPy 2.2.6, no
other dependency. The model, task, and data are those of the Adam note without
change: **K1** from Villatoro et al., eq. (4) — the Forrester pair — fit by their
multi-fidelity architecture with the exact low-fidelity function and no
coordinate encoding, the nonlinear branch a SIREN of three hidden layers of
sixteen units, $\omega_0 = 30$, $c = 6$.[@Villatoro2026] Training sets are
Sobol' samples of size $N_H=32$ with the two boundary points appended; test sets
are $32$ independent uniform draws. Errors are normalized test MSE,
$\operatorname{MSE}/\|y_H\|^2_{L^2([0,1])}$, with the denominator $20.0631$.
Both conventions in a repetition are instantiated from **one** parameter draw,
the matched official parameterization obtained by dividing the described
convention's hidden weights and biases by $\omega_0$, so the two are the same
function by construction. The hidden-bias division is the deliberate
matched-function idealization declared in the Introduction; it is not a replay
of the repository's default bias initialization.

The optimizer is **full-batch SGD** — no momentum, no normalization,
$\theta \leftarrow \theta - \text{lr}\cdot g$ — for $20{,}000$ epochs. Gradients
are hand-derived and were checked against central finite differences before any
run, with worst-case relative errors of $1.3\times10^{-6}$ (described) and
$4.4\times10^{-8}$ (official) over sampled parameters. The **isolated hidden
stack** freezes $W_0, b_0$ (first layer), $W_o, b_o$ (readout), and the affine
branch, updating only the hidden weights and biases (Code 1); the **single-step
displacement** is $\max|y_{\text{after one step}} - y_{\text{init}}|$ on the
test set, measured from the common initialization at a range of learning rates.

A second one-step measurement at $\text{lr}=10^{-8}$ updates three parameter
groups separately from that same initialization: the hidden stack alone, the
shared parameters alone, and the full network. The shared group comprises the
first layer, readout, and affine branch. I record the maximum and root-mean-square
output displacement, the cosine similarity between the shared-only and
hidden-only displacement vectors, and the residual after their sum is subtracted
from the simultaneous full-network step. The broad learning-rate sweep spans
$10^{-8}$ to $10^{1}$ in half-decade steps. A local sweep resolves its best
finite region from $10^{-4}$ to $10^{-3}$ at $0.05$-decade spacing — $21$ rates
separated by a factor of $10^{0.05}=1.122$ — with three repetitions using
data RNG seeds $1544$, $1545$, and $1546$ and parameter seeds $7000$, $7001$,
and $7002$.

```python
def train(P, official, x_tr, x_te, lr, hidden_lr=None,
          isolate=False, shared_only=False, ...):
    for t in range(1, epochs + 1):
        yh, cache = forward(P, u_tr, official, keep=True)
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
        for k in P:
            if isolate and k not in HIDDEN:     # freeze first layer, readout, affine
                continue
            if shared_only and k in HIDDEN:     # freeze convention-scaled parameters
                continue
            step = hidden_lr if (hidden_lr is not None and k in HIDDEN) else lr
            P[k] -= step * g[k].reshape(P[k].shape)     # plain SGD: no m, v, eps
```

**Code 1.** The full-batch SGD update and the two isolation switches. Setting
`isolate=True` trains the hidden stack alone, while `shared_only=True` freezes
it; `hidden_lr` applies a separate rate to hidden weights and biases, which is
how the $\times 900$ rescaling in the Results is applied.

Three bounds are declared here rather than discovered later. I fix the
regularization penalties at zero, where the paper searches them jointly with the
learning rate; the single-step ratio, decomposition, and rescaling trajectory use
one initialization (seed $7000$), the sweeps three; and **I did not run the
authors' code**, which remains unreleased, so every number describes my
reimplementation of their written specification. The complete script is
[siren-convention-sgd.py](/downloads/siren-convention-sgd.py). Raw outputs for
Table 1, both trajectory rates, the parameter-group decomposition, the broad
sweep, and the local refinement are
[sgd_ratio.json](/downloads/sgd_ratio.json),
[sgd_traj.json](/downloads/sgd_traj.json),
[sgd_decomposition.json](/downloads/sgd_decomposition.json),
[sgd_sweep.json](/downloads/sgd_sweep.json), and
[sgd_refined_sweep.json](/downloads/sgd_refined_sweep.json), respectively.

## Results

At initialization, over $32$ test inputs, the maximum absolute difference
between the two conventions' outputs is $1.776\times10^{-15}$ against a maximum
output magnitude of $11.0036$, a ratio of $1.6\times10^{-16}$.

The single-step function-space displacement ratio, official over described at a
common learning rate, is given in Table 1 for both the full network and the
isolated hidden stack. On the isolated stack it is $899.86$ at
$\text{lr}=10^{-8}$ and $898.03$ at $10^{-7}$, falling to $325.95$ at $10^{-5}$
and $28.71$ at $10^{-4}$. On the full network it stays between $1.14$ and $1.29$
across the same range.

| $\text{lr}$ | isolated hidden stack | full network |
| --- | --- | --- |
| $10^{-8}$ | $899.86$ | $1.157$ |
| $10^{-7}$ | $898.03$ | $1.137$ |
| $10^{-6}$ | $825.96$ | $1.262$ |
| $10^{-5}$ | $325.95$ | $1.285$ |
| $10^{-4}$ | $28.71$ | $1.157$ |

**Table 1.** Single-step function-space displacement ratio (official / described)
from a common initialization, hidden stack isolated versus full network, at
learning rate $\text{lr}$.

The parameter-group measurement at $\text{lr}=10^{-8}$ is given in Table 2. The
two shared-parameter displacement vectors differ by at most $1.776\times10^{-15}$.
The shared-parameter to hidden-stack maximum-displacement ratio is $5707.06$ for the
described convention and $6.3421$ for the official convention; the corresponding
RMS ratios are $3842.12$ and $4.2689$. The cosine similarity between the shared
and hidden vectors is $0.614462$ (described) and $0.614524$ (official). Subtracting
the separately measured shared and hidden vectors from the simultaneous full
step leaves a maximum residual of $1.366\times10^{-7}$ (described) and
$1.231\times10^{-4}$ (official).

| Parameters updated | described $\max|\Delta y|$ | official $\max|\Delta y|$ | official / described |
| --- | --- | --- | --- |
| shared parameters | $6.43543\times10^{-2}$ | $6.43543\times10^{-2}$ | $1.00000$ |
| hidden stack | $1.12763\times10^{-5}$ | $1.01471\times10^{-2}$ | $899.864$ |
| full network | $6.43656\times10^{-2}$ | $7.44662\times10^{-2}$ | $1.15693$ |

**Table 2.** Maximum single-step test-set output displacement from a common
initialization at $\text{lr}=10^{-8}$, by updated parameter group. The shared
group is the first layer, readout, and affine branch.

On the isolated hidden stack, the official convention at learning rate
$10^{-6}$ and the described convention at hidden learning rate $900\times10^{-6}$
produce test-set outputs differing by $1.776\times10^{-15}$ after one step and
$2.665\times10^{-15}$ after $200$ steps, a relative difference of
$3.8\times10^{-16}$; at $\text{lr}=10^{-8}$ the same figures are
$1.776\times10^{-15}$ and $2.665\times10^{-15}$.

The local full-network learning-rate sweep is summarized in Table 3. In all six
convention-repetition pairs the lowest finite normalized test MSE occurs at
$\text{lr}=6.309573\times10^{-4}$, and the first non-finite value occurs at
$7.079458\times10^{-4}$. At the former rate, the described-to-official MSE ratio
is $4.02\times10^8$, $1.48\times10^9$, and $8.52\times10^8$ across the three
repetitions.

| Convention | rep | best tested lr | normalized test MSE | first non-finite lr |
| --- | --- | --- | --- | --- |
| official | 0 | $6.309573\times10^{-4}$ | $1.1963\times10^{-14}$ | $7.079458\times10^{-4}$ |
| official | 1 | $6.309573\times10^{-4}$ | $5.6396\times10^{-15}$ | $7.079458\times10^{-4}$ |
| official | 2 | $6.309573\times10^{-4}$ | $1.2065\times10^{-14}$ | $7.079458\times10^{-4}$ |
| described | 0 | $6.309573\times10^{-4}$ | $4.8062\times10^{-6}$ | $7.079458\times10^{-4}$ |
| described | 1 | $6.309573\times10^{-4}$ | $8.3687\times10^{-6}$ | $7.079458\times10^{-4}$ |
| described | 2 | $6.309573\times10^{-4}$ | $1.0275\times10^{-5}$ | $7.079458\times10^{-4}$ |

**Table 3.** Lowest finite normalized test MSE and first non-finite rate on the
$0.05$-decade local grid from $10^{-4}$ through $10^{-3}$, per convention and
repetition.

## Discussion

**Verdict: the hypothesis is supported.** The falsifier was that the
isolated-stack ratio in the small-learning-rate limit is not near $900$; it is
$899.86$ at $\text{lr}=10^{-8}$, so neither branch of the falsifier fired — the
value is not near $\omega_0 = 30$, which would have collapsed SGD and Adam into
one factor, and not near $1$, which would have denied the mechanism. The linear
regime is where the squared factor is expected to be clean, and the ratio's
descent along Table 1 — $900 \to 826 \to 326 \to 29$ as the learning rate grows
— is the curvature of a finite step entering as the displacement stops being
small; the passage through $\approx 30$ at $\text{lr}=10^{-4}$ is a crossing, not
an Adam-like factor, since it is a point on a monotone decay rather than a
plateau. The exactness has no $\varepsilon$ caveat: the rescaled described
convention tracks the official one to $2.7\times10^{-15}$ for $200$ steps, where
yesterday's Adam agreement degraded from $10^{-5}$ to $0.15$ as the learning rate
rose because Adam's fixed $\varepsilon$ is relatively $\omega_0$ times smaller for
the official convention. SGD has no denominator to seed that drift, and the
trajectory stays at machine precision.

**The network-level search resolves no gap, not nine hundred.** Table 2 makes
the dilution a measurement rather than a scalar inference. At
$\text{lr}=10^{-8}$ the shared parameters move the output by $0.06435$, while the
described hidden stack moves it by $1.128\times10^{-5}$: a directly measured
ratio of $5707$, so the hidden displacement is $0.0175\%$ of the shared one on
this maximum norm. Multiplying that hidden motion by $900$ raises it to $0.01015$
in the official convention, still $6.34$ times below the shared displacement.
The two displacement vectors point broadly together — cosine similarity
$0.6145$ — and their simultaneous full-network ratio is $1.157$. No assumption
that a vector-valued displacement is the scalar sum $S+h$ is needed.

K1 supplies the reason this can happen: its functions obey
$y_H=2y_L-20x+20$, so the affine branch can represent the high-fidelity target
without the SIREN branch. The refined sweep then finds the same best tested
global rate, $6.309573\times10^{-4}$, and the same first non-finite rate,
$7.079458\times10^{-4}$, for both conventions in all three repetitions. That is
a best-rate ratio of one **at $0.05$-decade resolution**, not a claim that the
continuous optima are mathematically identical. Under Adam the analogous
first-fit gap remained ten. SGD dilutes harder for the same reason its isolated
factor is larger: Adam's normalization gives parameters steps of comparable
size, while SGD's gradient-proportional update gives the largest moves to the
shared parameters with the largest gradients.

**What this changes for someone reaching for SGD on a SIREN.** The absent
learning-rate gap hides a large accuracy gap. At the shared best tested rate,
the official convention reaches $5.6\times10^{-15}$ to $1.2\times10^{-14}$,
while the described convention stops at $4.8\times10^{-6}$ to
$1.0\times10^{-5}$ — eight to nine orders of magnitude in normalized MSE. The
described hidden stack is therefore effectively **untrainable with one global
learning rate on K1**. Matching the official hidden-step scale at
$6.309573\times10^{-4}$ would require a described hidden rate of $0.568$, while
the full network is already non-finite at $7.079458\times10^{-4}$. This is not a
claim that the parameterization cannot train under SGD at all: a separate
$\times900$ hidden rate is the exact reparameterization tested on the isolated
stack. It is an incompatibility between the hidden and shared scales under one
global rate. This is the same hazard as the
[specification degeneracy](/posts/2026-07-17-the-siren-that-was-a-straight-line.html)
and the [Adam convention gap](/posts/2026-07-17-why-the-two-siren-conventions-train-differently.html),
arriving through the optimizer instead of the initializer.

**Limits.** One task, one architecture, one optimizer without momentum,
$N_H = 32$; the single-step ratio, decomposition, and rescaling trajectory rest
on one initialization, the sweeps on three. The best-rate ratio of one is bounded
by a $0.05$-decade grid. Because the MSE ratios use official errors near
$10^{-14}$ as their denominator, the absolute error ranges are the more stable
comparison. K1 is the specific reason the dilution is this strong — its
exactly linear correlation lets the affine branch carry the fit — so neither the
full-network ratio nor the common best tested rate is a general claim about SGD.

## Conclusion

The prediction the Adam note left on the shelf holds where the mechanism lives:
on the isolated hidden stack the two SIREN conventions differ under SGD by
$\omega_0^2 = 900$, measured at $899.86$, exact to machine precision with no
$\varepsilon$ caveat. The new dilution ledger is direct: before convention
scaling, the shared maximum output displacement is $5707$ times the hidden one;
after the official convention amplifies the hidden displacement by $900$, the
shared part is still $6.34$ times larger. A $0.05$-decade sweep likewise
resolves no convention-dependent global learning rate on K1 — both conventions
select $6.309573\times10^{-4}$ and fail at the next point — even while their best
tested errors remain eight to nine orders of magnitude apart.

Two experiments follow. First, momentum: its update remains linear in the
gradient, so the isolated $900$ prediction survives, but whether accumulated
velocity changes the full network's shared-to-hidden balance is an untested
regime. Second, the global-rate incompatibility predicts its own test: on a
K-case whose cross-correlation is *nonlinear*, where the affine branch cannot
carry the fit and the SIREN branch must, the convention choice should produce a
resolvable network-level learning-rate gap. Both go on the shelf.

## References
