---
title: "Why the two SIREN conventions train differently under Adam"
date: 2026-07-17
author: Peter Johnston
tags: neural networks, SIREN, initialization, optimization, adam, reproducibility
description: The two circulating SIREN conventions are the same function at initialization to machine precision, but not the same optimization problem. Under Adam, their hidden-layer steps differ in function space.
post-type: research
contribution: A measurement showing the two Sitzmann SIREN conventions are not interchangeable under Adam, falsifying the equivalence claim in my own note of earlier today.
contribution-type: falsification
experiment: siren-convention-adam
---

## Abstract

Earlier today I wrote that the two circulating SIREN conventions "are numerically
equivalent, because the implementation's division by $\omega_0$ exists to cancel
its own multiplication by $\omega_0$." The first half of that sentence is
supported and the second half is the reason it is wrong. The cancellation is a
statement about the forward pass, and it holds: instantiated from a common seed,
the two conventions are the same function at initialization to one part in
$10^{16}$. Adam does not act on the forward pass. It acts
on the parameters, and the two conventions store the same function in parameters
that differ by a factor of $\omega_0$, so at equal learning rate the official
convention moves its hidden layers $\omega_0$ times further per step. I measure
this on the K1 test case of Villatoro et al.: reproducing the official
convention from the described one requires scaling the hidden layers' learning
rate by $30$ and nothing else, which matches to
[equiv_lr_1e_5_relative_difference]{.metric} relative at
$\text{lr}=10^{-5}$. The consequence is an order-of-magnitude gap in the learning
rate at which each convention first fits K1 —
[range_official_rep0_first_fit_lr]{.metric} for the official convention in
[range_official_common_first_fit_count]{.metric} of four repetitions, against
[range_described_rep0_first_fit_lr]{.metric} in
[range_described_tenfold_gap_count]{.metric} repetitions and
[range_described_rep2_first_fit_lr]{.metric} in the fourth for the described
one. The two conventions are the same network and a different
optimization problem.

## Introduction

A SIREN's initialization exists to hold each sinusoidal unit's pre-activation at
a standard deviation near one, where $\sin(\cdot)$ is a nonlinearity rather than
the identity.[@Sitzmann2020] Two conventions implement that scaling. The paper
describes drawing hidden weights from $\mathcal{U}(\pm\sqrt{6/n})$ and applying
$\sin(W x + b)$; the official implementation draws from
$\mathcal{U}(\pm\sqrt{6/n}/\omega_0)$ and applies $\sin(\omega_0 (W x +
b))$.[@Sitzmann2020; @SirenOfficial] The $\div\omega_0$ and the $\times\omega_0$
cancel, both land at a pre-activation scale of $\sqrt{6/n}$, and I took that to
settle the matter in
[this morning's note](/posts/2026-07-17-the-siren-that-was-a-straight-line.html),
which treated the difference as bookkeeping and went looking for the real defect
elsewhere. The phrase I used was "numerically equivalent."

That conclusion has a gap in it, and the gap is the word *equivalent* doing work
in a domain it was never checked against. The cancellation argument is about
$W$ and $\omega_0 W'$ producing the same pre-activation. It says nothing about
what happens when a gradient-based optimizer subsequently moves $W$ and $W'$,
and Adam — the optimizer Villatoro et al. use[@Villatoro2026] — is a rule in
parameter space, not function space. Its update
$\theta \leftarrow \theta - \text{lr}\cdot\hat m/(\sqrt{\hat v}+\varepsilon)$ is
normalized by the gradient's own second moment, so its step size is set by
`lr` and is almost independent of how large the gradient is. Rescale a weight
and its gradient rescales inversely; the ratio $\hat m/\sqrt{\hat v}$ does not
notice. The step stays the same size in parameter space and therefore changes
size in function space.

If that reasoning holds, the two conventions are not interchangeable under
training. The official convention stores hidden weights $\omega_0$ times smaller
and multiplies them back up in the forward pass, so an Adam step of a given size
on its stored weights is an $\omega_0$-times-larger step on the product that the
network actually computes. **Hypothesis.** The two conventions differ under Adam
by exactly a per-layer learning-rate factor of $\omega_0$ on the hidden layers,
and by nothing else — the first layer and the readout are common to both
conventions and are unscaled. It predicts that the described convention, given a
hidden-layer learning rate of $\omega_0\lambda$ and $\lambda$ everywhere else,
reproduces the official convention trained at $\lambda$.

**Falsifier**, fixed before running: the two conventions train to the same test
error at the same learning rate, or the per-layer rescaling fails to reproduce
one from the other. Either outcome returns the difference to bookkeeping and
leaves this morning's sentence standing. I would have published that; it is the
cheaper result.

## Computational Methods

All results were produced on CPython 3.10.12, aarch64 Linux, with NumPy 2.2.6
and no other dependency. Gradients are hand-derived and were checked against
central finite differences before any training run, with worst-case relative
errors of $9.9\times10^{-8}$ (described) and $1.5\times10^{-8}$ (official) over
sampled parameters; that check is not part of the published script.

The task is **K1** from Villatoro et al., their eq. (4) — the Forrester
pair,[@Villatoro2026] with

$$y_L(x) = 0.5(6x-2)^2\sin(12x-4) + 10x - 10, \qquad y_H(x) = (6x-2)^2\sin(12x-4)$$

on $x\in[0,1]$. I use their multi-fidelity architecture with the **exact** LF
function rather than an LF surrogate, and no coordinate encoding — the paper's
own best-performing K1 configuration. The high-fidelity prediction is
$\hat y_H = F_l(x, y_L) + F_{nl}(x, y_L)$, an affine branch with bias plus a
nonlinear branch, and $F_{nl}$ is the SIREN: three hidden layers of sixteen
units, $\omega_0 = 30$, $c = 6$. Training sets are Sobol' samples of size 32 with
the boundary points appended; test sets are 32 independent uniform draws. Errors
are test MSE normalized by $\|y_H\|^2_{L^2([0,1])} = 20.0631$, computed by
quadrature. Optimization is full-batch Adam for 20,000 epochs on
$\sum(\hat y_H - y_H)^2$.

Both conventions are instantiated from **one** parameter draw, with the official
convention obtained by dividing the described convention's hidden weights and
biases by $\omega_0$ (Code 1). This is what makes the comparison a comparison:
the two are the same function by construction, not merely the same in
distribution. One idealization is declared here: the official repository
divides only its *weights* by $\omega_0$ — biases keep the framework's default
initialization — so the exact same-function property is a property of this
construction, not of the repository's code.

```python
def to_official(P):
    """Same function, official parameterization."""
    Q = {k: v.copy() for k, v in P.items()}
    for l in range(1, NHID):
        Q[f"W{l}"] = P[f"W{l}"] / OMEGA     # forward pass multiplies by OMEGA
        Q[f"b{l}"] = P[f"b{l}"] / OMEGA     # first layer and readout: untouched
    return Q

# Adam, per parameter tensor. `step` is OMEGA*lr for hidden W,b under the
# rescaling test, and lr for every other tensor.
m[k] = b1*m[k] + (1-b1)*g[k]
v[k] = b2*v[k] + (1-b2)*g[k]**2
P[k] -= step * (m[k]/(1-b1**t)) / (np.sqrt(v[k]/(1-b2**t)) + eps)
```

**Code 1.** The reparameterization under test and the Adam update it interacts
with. Dividing the stored hidden weights by $\omega_0$ leaves the forward pass
unchanged and leaves the Adam step size in parameter space unchanged, which is
the entire content of the experiment.

The complete NumPy-only script used for the experiment is available as
[siren-convention-adam.py](/downloads/siren-convention-adam.py). The frozen raw
records behind Table 1 and Table 2 are available as
[conv_equiv.json](/downloads/conv_equiv.json) and
[conv_range.json](/downloads/conv_range.json), respectively. On a second
platform (arm64 macOS, CPython 3.13.12, NumPy 2.4.4) the initialization remains
equal to machine precision and every $\lambda = 10^{-5}$ training figure
reproduces to the precision printed here, while the $\lambda \ge 10^{-4}$
trainings move by 4–15% and the
rescaled-run agreement at $10^{-3}$ becomes $0.42$ — the trajectory divergence
discussed below, seeded by platform rounding instead of $\varepsilon$.

Three deviations from the paper's protocol are declared here rather than
discovered later. I fix the regularization penalties at zero, where the paper
searches $\lambda \in \{0, 10^{-5}, 10^{-3}, 1\}$ jointly with the learning
rate. I use a deterministic log-spaced learning-rate grid where the paper uses
Hyperopt's stochastic search over $\log([10^{-5}, 10^{-3}])$. And I use 20,000
epochs, a number the paper does not state anywhere — neither epochs nor batch
size appear in its text. Each of these bounds what follows, and the third is not
recoverable from the publication. **I did not run the authors' code**, which
remains unreleased, so every number below describes my reimplementation of their
written specification and not their experiments.

The generated [publication metrics](/research/siren-convention-adam/metrics.json)
make the frozen equivalence and learning-rate-sweep values cited throughout the
post machine-resolvable. This first traceability pass covers the result values
in Tables 1 and 2 and their repeated prose claims. The initialization,
finite-difference, and
secondary-platform diagnostics predate a frozen output artifact and are not
presented as traceable metrics.

## Results

At initialization, over 32 test inputs, the maximum absolute difference between
the two conventions' outputs is $1.776\times10^{-15}$, against a maximum output
magnitude of $11.0036$ — a ratio of $1.6\times10^{-16}$.

After 20,000 epochs from that common initialization, the two conventions reach
normalized test MSEs of [equiv_lr_1e_5_official_mse]{.metric} (official) and
[equiv_lr_1e_5_described_mse]{.metric} (described) at $\lambda = 10^{-5}$,
[equiv_lr_1e_4_official_mse]{.metric} and
[equiv_lr_1e_4_described_mse]{.metric} at $10^{-4}$, and
[equiv_lr_1e_3_official_mse]{.metric} and
[equiv_lr_1e_3_described_mse]{.metric} at $10^{-3}$. The described convention
trained with its hidden-layer learning rate multiplied by 30 returns
[equiv_lr_1e_5_scaled_mse]{.metric}, [equiv_lr_1e_4_scaled_mse]{.metric} and
[equiv_lr_1e_3_scaled_mse]{.metric} at the same three values of $\lambda$,
differing from the official convention by
[equiv_lr_1e_5_relative_difference]{.metric},
[equiv_lr_1e_4_relative_difference]{.metric} and
[equiv_lr_1e_3_relative_difference]{.metric} relative (Table 1).

| $\lambda$ | official | described | described, hidden lr $\times 30$ | relative difference |
| --- | --- | --- | --- | --- |
| $10^{-5}$ | [equiv_lr_1e_5_official_mse]{.metric} | [equiv_lr_1e_5_described_mse]{.metric} | [equiv_lr_1e_5_scaled_mse]{.metric} | [equiv_lr_1e_5_relative_difference]{.metric} |
| $10^{-4}$ | [equiv_lr_1e_4_official_mse]{.metric} | [equiv_lr_1e_4_described_mse]{.metric} | [equiv_lr_1e_4_scaled_mse]{.metric} | [equiv_lr_1e_4_relative_difference]{.metric} |
| $10^{-3}$ | [equiv_lr_1e_3_official_mse]{.metric} | [equiv_lr_1e_3_described_mse]{.metric} | [equiv_lr_1e_3_scaled_mse]{.metric} | [equiv_lr_1e_3_relative_difference]{.metric} |

**Table 1.** Normalized test MSE after 20,000 epochs at learning rate $\lambda$,
from a common initialization. The final column is the relative difference between
the official convention and the described convention with its hidden-layer
learning rate multiplied by 30.

Across a grid of nine learning rates spanning $10^{-5}$ to $10^{-1}$ and four
repetitions, the lowest learning rate at which each convention reaches a
normalized test MSE below $10^{-3}$ is
[range_official_rep0_first_fit_lr]{.metric} for the official convention in
[range_official_common_first_fit_count]{.metric} of four repetitions, and
[range_described_rep0_first_fit_lr]{.metric},
[range_described_rep1_first_fit_lr]{.metric},
[range_described_rep2_first_fit_lr]{.metric},
[range_described_rep3_first_fit_lr]{.metric} for the described convention
(Table 2).

| Convention | rep | best, lr $\in [10^{-5}, 10^{-3}]$ | best, lr $> 10^{-3}$ | lowest lr reaching $<10^{-3}$ |
| --- | --- | --- | --- | --- |
| described | 0 | [range_described_rep0_best_in_range]{.metric} | [range_described_rep0_best_above_range]{.metric} | [range_described_rep0_first_fit_lr]{.metric} |
| described | 1 | [range_described_rep1_best_in_range]{.metric} | [range_described_rep1_best_above_range]{.metric} | [range_described_rep1_first_fit_lr]{.metric} |
| described | 2 | [range_described_rep2_best_in_range]{.metric} | [range_described_rep2_best_above_range]{.metric} | [range_described_rep2_first_fit_lr]{.metric} |
| described | 3 | [range_described_rep3_best_in_range]{.metric} | [range_described_rep3_best_above_range]{.metric} | [range_described_rep3_first_fit_lr]{.metric} |
| official | 0 | [range_official_rep0_best_in_range]{.metric} | [range_official_rep0_best_above_range]{.metric} | [range_official_rep0_first_fit_lr]{.metric} |
| official | 1 | [range_official_rep1_best_in_range]{.metric} | [range_official_rep1_best_above_range]{.metric} | [range_official_rep1_first_fit_lr]{.metric} |
| official | 2 | [range_official_rep2_best_in_range]{.metric} | [range_official_rep2_best_above_range]{.metric} | [range_official_rep2_first_fit_lr]{.metric} |
| official | 3 | [range_official_rep3_best_in_range]{.metric} | [range_official_rep3_best_above_range]{.metric} | [range_official_rep3_first_fit_lr]{.metric} |

**Table 2.** Normalized test MSE on K1 at $N_H = 32$, by convention and
repetition, partitioned at the top of the learning-rate range Villatoro et al.
search. Median best-in-range values are
[range_described_median_best_in_range]{.metric} (described) and
[range_official_median_best_in_range]{.metric} (official); median best above
the range are [range_described_median_best_above_range]{.metric} and
[range_official_median_best_above_range]{.metric}.

## Discussion

**Verdict: the hypothesis is supported, and this morning's equivalence claim is
falsified.** The falsifier was fixed without a numerical tolerance, which
leaves the $\lambda = 10^{-3}$ row — rescaled agreement of only
[equiv_lr_1e_3_relative_difference]{.metric} — for an
adversary to point at, so the adjudication call goes here rather than passing
silently. I adjudicate at $\lambda = 10^{-5}$, where Adam's $\varepsilon$
perturbs least: the unrescaled pair differ by
[equiv_lr_1e_5_unscaled_absolute_difference]{.metric} in normalized MSE, so the
conventions do not train alike, and the rescaled pair agree to four decimal
places, so the rescaling does reproduce one from the other — neither branch of
the falsifier fired, and the degradation at larger $\lambda$ has a mechanism,
below.

The two conventions are the same function at initialization to sixteen digits,
which is the strongest form the cancellation argument could take
and is exactly what that argument predicts. They are nonetheless a different
optimization problem, and the difference is a per-layer learning rate: rescaling
the hidden layers by $\omega_0$ and leaving the first layer and readout alone
reproduces one convention from the other to
[equiv_lr_1e_5_relative_difference]{.metric} relative. Nothing
else needed adjusting.

The agreement degrades as $\lambda$ grows —
[equiv_lr_1e_5_relative_difference]{.metric} at $10^{-5}$,
[equiv_lr_1e_4_relative_difference]{.metric} at $10^{-4}$, and
[equiv_lr_1e_3_relative_difference]{.metric} at $10^{-3}$ — and the mechanism for
that is visible in Adam's own denominator. The equivalence is exact only as
$\varepsilon \to 0$: the official convention's gradients are $\omega_0$ times
larger, so its $\sqrt{\hat v}$ is too, and the fixed $\varepsilon = 10^{-8}$ is
relatively 30 times smaller for it. That is a tiny perturbation, and 20,000
epochs of a non-convex problem is an efficient machine for turning tiny
perturbations into large ones. The pattern is the ordinary trajectory divergence
of two nearly-identical runs, not a second mechanism.

**What this changes for someone reimplementing a SIREN.** The two conventions
are usually presented as a documentation wart — the paper says one thing, the
repository does another, they agree anyway, pick either. They do agree, and
picking either still changes the learning rate you need by an order of
magnitude. On K1 the official convention first fits at
[range_official_rep0_first_fit_lr]{.metric}
[range_official_common_first_fit_count]{.metric} times out of four; the
described convention first fits at [range_described_rep0_first_fit_lr]{.metric}
in [range_described_tenfold_gap_count]{.metric} repetitions and
[range_described_rep2_first_fit_lr]{.metric} in the fourth. A learning rate
tuned for one convention and inherited by the other is not a tuned learning
rate. This is the same class of hazard as the specification defect I measured
this morning, arriving through a different door: there, taking the initializer
from one convention and the activation from the other produced a linear network;
here, taking a *hyperparameter* from one convention and the parameterization
from the other produces an untrained one.

**Where I will not go, though the data is sitting right there.** Both
conventions solve K1 to machine precision, but only at learning rates above the
top of the range Villatoro et al. search with Hyperopt. The lowest in-range
errors in these runs are [range_described_rep2_best_in_range]{.metric}
(described) and [range_official_rep0_best_in_range]{.metric} (official). It is tempting to
read that as an explanation for the paper's conclusion that SIREN
underperforms.[@Villatoro2026] It is not one, for a reason that is my fault
rather than theirs: I fixed the regularization penalties at zero, and on K1 the
correlation is exactly linear — the paper states $y_H = 2y_L - 20x + 20$ — so
the affine branch alone can represent $y_H$ perfectly and the SIREN's only job
is to stay out of the way. Penalizing the nonlinear branch is how that
configuration is supposed to reach the $10^{-26}$ the paper reports, and I
switched that penalty off. My in-range numbers measure my own protocol, not
theirs.

**The dry fit.** This is not the experiment I set out to run. The question on the
shelf was whether the specification degeneracy costs accuracy once the learning
rate is tuned, and I ran a large sweep across three schemes, three sample sizes,
four repetitions, and nine learning rates. That sweep is confounded by the
$\lambda = 0$ choice above and I am not reporting its headline. It earned its
keep anyway, by printing something I had asserted could not happen — the two
Sitzmann conventions, which I had just called equivalent in print, separating
materially in test error. Chasing that is this note.

**Limits.** One task, one architecture, one optimizer, $N_H = 32$, four seeds.
The factor measured here is [range_common_first_fit_ratio]{.metric} in
[range_described_tenfold_gap_count]{.metric} repetitions of four and
[range_outlier_first_fit_ratio]{.metric} in the fourth, not the $30$ the
mechanism predicts, and the learning-rate grid is
spaced by $\sqrt{10}$ — so $10$ and $30$ are one grid step apart and this
experiment does not resolve them. The dilution has an obvious candidate
in the shared, unscaled first layer and readout, which is testable and untested.
No measurement here bears on SGD, but the mechanism's prediction there is
larger, not null: its step *is* proportional to the gradient, which is $\omega_0$ times larger
for the official convention, and that step lands on a parameter the forward
pass multiplies by $\omega_0$ again — a predicted effective factor of
$\omega_0^2 = 900$ on the hidden layers, exact for SGD with no $\varepsilon$
caveat. Invariance would require the gradient to shrink with the stored weight;
it grows instead.

## Conclusion

The two SIREN conventions are the same network. Under Adam they are not the same
experiment, because Adam's step is a fixed size in parameter space and the two
conventions park the same function at coordinates a factor $\omega_0$ apart. The
cancellation argument that makes them equivalent in the forward pass is silent
about this and I read the silence as agreement.

What changed: a difference that the literature files under documentation, and
that I filed under bookkeeping this morning, is an order-of-magnitude shift in
the learning rate a reimplementer needs —
[range_common_first_fit_ratio]{.metric}-fold in
[range_described_tenfold_gap_count]{.metric} seeds of four,
[range_outlier_first_fit_ratio]{.metric}-fold in the fourth — measured on a
published benchmark.

The next experiment is the one that would pin the factor down. The mechanism
predicts $30$ on the hidden layers and the measurement returned
[range_median_first_fit_ratio]{.metric} in the median;
the candidate explanation is the first layer and the readout, which both
conventions share unscaled and which therefore dilute the effect by an amount
set by how much of the fitting they do. Freezing them and re-running the
learning-rate sweep separates the two — if the isolated hidden stack returns
$30$, the dilution is quantified rather than asserted. That goes on the shelf,
along with the SGD control, which the same argument says must come back larger,
not null — SGD's step is proportional to the $\omega_0$-times-larger gradient
and lands on a weight the forward pass scales by $\omega_0$ again, so the
predicted factor there is $\omega_0^2$.

## References
