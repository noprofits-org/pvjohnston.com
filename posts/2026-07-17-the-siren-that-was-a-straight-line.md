---
title: "The SIREN that was a straight line"
date: 2026-07-17
author: Peter Johnston
tags: multi-fidelity, neural networks, SIREN, initialization, reproducibility, spectral bias
description: A recent paper specifies a SIREN by taking its initialization from one convention and its activation from another. Instantiated literally, every hidden sine sits in its linear regime and the network collapses to a single Fourier layer.
contribution: The measured hidden-layer pre-activation scale of the SIREN specification published in Villatoro et al. (2026) — a quantity the paper never reports, though it rests a conclusion on initialization sensitivity.
contribution-type: quantification
---

## Abstract

SIREN's initialization is not a detail; it is the mechanism that keeps each
sinusoidal unit inside its nonlinear range. Two conventions circulate — the one
described in Sitzmann et al. and the one in the official implementation — and
they are numerically equivalent, because the implementation's division by
$\omega_0$ exists to cancel its own multiplication by $\omega_0$. A recent
*Journal of Computational Physics* study notes that the two "differ", states that
"the network is sensitive to how it is initialized", adopts a third
implementation, and never reports what its own written specification produces. I
measure it. Read literally, that specification draws hidden weights from the
$\div\omega_0$ convention while applying the activation of the convention without
it, leaving hidden pre-activations a factor of $\omega_0$ below variance-preserving:
standard deviation $0.036$ rather than $\approx 1$ at $\omega_0 = 30$, where
$\sin(z)$ departs from $z$ by $0.044\%$. The deficit compounds with depth,
reaching $0.0018$ by the second hidden layer, so the specified network collapses
to one Fourier-feature layer followed by an effectively linear stack. The
implementation the paper cites cannot produce this configuration, since a single
$\omega_0$ feeds both its initializer and its activation. The defect is therefore
in the published text rather than, necessarily, in the published results — which
matters because the code is unreleased, so the text is currently all a
reimplementer has.

## Introduction

A SIREN is a feedforward network whose activation is $\sin(\cdot)$, and its
usefulness rests entirely on a scaling argument.[@Sitzmann2020] Feed a sine unit
a pre-activation of standard deviation $\approx 1$ and it behaves like a
nonlinearity. Feed it one of standard deviation $0.03$ and it behaves like the
identity, because $\sin(z) \to z$ as $z \to 0$. The published initialization
exists to hold that scale at one, layer after layer. Get it wrong and you do not
get a degraded SIREN; you get a linear network wearing a sine costume.

Two conventions are in circulation, and the distinction is bookkeeping rather
than substance. Sitzmann et al. describe drawing hidden weights from
$\mathcal{U}(\pm\sqrt{6/n})$ and applying $\sin(W x + b)$, with $\omega_0$
reserved for the first layer.[@Sitzmann2020] The official implementation instead
applies $\sin(\omega_0 \cdot (W x + b))$ at *every* layer and draws hidden weights
from $\mathcal{U}(\pm\sqrt{6/n}/\omega_0)$.[@SirenOfficial] The division and the
multiplication cancel. Both land at a pre-activation scale of $\sqrt{6/n}$, which
is the entire point of the exercise.

Villatoro, Geraci and Schiavazzi compare MLP, SIREN and Kolmogorov–Arnold
architectures as multi-fidelity emulators, and report that "SIREN networks, though
effective for certain specialized applications, generally underperform relative to
KAN and MLP architectures in multi-fidelity settings."[@Villatoro2026] In setting
SIREN up they record that they "found discrepancies between the official SIREN
Python implementation's initialization of the weights of their network and the
initialization scheme described in [Sitzmann et al.]", assert that "the network is
sensitive to how it is initialized", and adopt a third implementation.[@SirenPytorch]

That is a claim of sensitivity offered as a justification for a choice, with no
measurement attached — and a conclusion about SIREN's merit resting on top of it.
The gap is not that they chose wrongly. It is that the paper never reports the one
number the sensitivity claim is about: the pre-activation scale its own written
specification produces. Their §2.3.2 gives hidden layers as
$\phi_l(x) = \sin(W_l x + b_l)$ — no $\omega_0$, the described convention — while
initializing $W_l \sim \mathcal{U}(\pm\sqrt{c/(\omega_0^2 n_i)})$, which is the
official implementation's convention, the one whose $\div\omega_0$ is supposed to
be cancelled by a multiplication that this forward pass does not perform. They run
at $\omega_0 = 30$.

**Hypothesis.** Instantiated as written, the specification leaves hidden
pre-activations a factor of $\omega_0$ below variance-preserving, placing every
hidden sine in its linear regime and collapsing the network to a single
Fourier-feature layer followed by a linear stack. It predicts a hidden
pre-activation standard deviation of $\approx 1/\omega_0 \approx 0.033$ at
$\omega_0 = 30$, against $\approx 1$ for both Sitzmann conventions.

**Falsifier**, fixed before running: a measured hidden pre-activation standard
deviation of $\approx 1$ under the specified scheme — within a factor of two of
the Sitzmann conventions. The specification would then be sound and the hypothesis
dead.

## Computational Methods

All results were produced on CPython 3.13.12, arm64 macOS, with NumPy 2.4.4 and
no other dependency. No training is involved and no GPU was used: every quantity
below is a property of the network at initialization.

Three schemes were implemented, differing only in the hidden-layer forward pass
and weight distribution, with $c = 6$ throughout and the first layer identical in
all three ($W_0 \sim \mathcal{U}(\pm 1/n)$, $\sin(\omega_0 \cdot W_0 x + b_0)$):

| Scheme | Hidden forward | Hidden weight init |
| --- | --- | --- |
| Sitzmann, as described[@Sitzmann2020] | $\sin(W_l x + b_l)$ | $\mathcal{U}(\pm\sqrt{6/n})$ |
| Sitzmann, official implementation[@SirenOfficial] | $\sin(\omega_0 (W_l x + b_l))$ | $\mathcal{U}(\pm\sqrt{6/n}/\omega_0)$ |
| Villatoro et al., as specified[@Villatoro2026] | $\sin(W_l x + b_l)$ | $\mathcal{U}(\pm\sqrt{6/(\omega_0^2 n)})$ |

**Table 1.** The three initialization schemes compared. The first two differ in
bookkeeping only; the third takes its forward pass from the first and its weight
distribution from the second.

Networks are the paper's $3\times16$ configuration — three hidden layers of
sixteen neurons — on the K1 input domain $x \in [0,1]$. $2\times10^5$ inputs were
propagated forward at initialization and the standard deviation of each hidden
pre-activation recorded (Code 1). Nonlinearity is reported as the mean relative
departure of $\sin(z)$ from $z$, $\mathbb{E}|\sin z - z| / \mathbb{E}|z|$, for $z$
drawn at the measured scale.

```python
import numpy as np
RNG, C, W = np.random.default_rng(0), 6.0, 16
X = RNG.uniform(0, 1, size=(200_000, 1))

def run(scheme, w0, L=4):
    h, stds = X, []
    for l in range(L - 1):
        n_in = h.shape[1]
        if l == 0:
            Wl = RNG.uniform(-1/n_in, 1/n_in, (n_in, W)); z = w0 * (h @ Wl)
        else:
            a = {"described":  np.sqrt(C / n_in),
                 "official":   np.sqrt(C / n_in) / w0,
                 "specified":  np.sqrt(C / (w0**2 * n_in))}[scheme]
            Wl = RNG.uniform(-a, a, (n_in, W))
            z = (w0 if scheme == "official" else 1.0) * (h @ Wl)
            stds.append(z.std())
        h = np.sin(z)
    return stds
```

**Code 1.** Forward propagation at initialization under the three schemes,
recording the standard deviation of each hidden pre-activation.

The complete script, which reproduces every number in the Results section and
requires nothing but NumPy, is available as
[siren-init-scales.py](/downloads/siren-init-scales.py).

This measures the network **as specified in the published text**. The authors'
code is not available — "Data will be shared in a GitHub repository upon
acceptance", and the paper was accepted 2026-06-29 — so whether their
implementation matches their specification was not tested here and cannot be, from
outside. That boundary is load-bearing for the Discussion and is not elided.

## Results

At $\omega_0 = 30$, the first hidden pre-activation has standard deviation
$0.0364$ under the specified scheme, $1.051$ under the described scheme and
$1.052$ under the official implementation (Table 2). The mean relative departure
of $\sin(z)$ from $z$ at those scales is $0.044\%$, $29.8\%$ and $29.8\%$
respectively.

| $\omega_0$ | Sitzmann, described | Sitzmann, official | Villatoro, specified | $\omega_0 \times$ specified |
| --- | --- | --- | --- | --- |
| 5 | 0.800 | 0.865 | 0.160 | 0.799 |
| 10 | 0.949 | 1.046 | 0.105 | 1.053 |
| 20 | 0.944 | 0.914 | 0.055 | 1.095 |
| 30 | 1.051 | 1.052 | **0.036** | 1.092 |

**Table 2.** Standard deviation of the first hidden pre-activation at
initialization, by scheme and $\omega_0$, over $2\times10^5$ inputs. The final
column reports the product of $\omega_0$ and the specified scheme's value.

The specified scheme's standard deviation falls from $0.160$ to $0.036$ across
$\omega_0 \in \{5,10,20,30\}$; its product with $\omega_0$ takes the values
$0.799$, $1.053$, $1.095$ and $1.092$. The two Sitzmann schemes range over
$0.800$–$1.052$ across the same interval.

Standard deviations at successive depths under the specified scheme are $0.0364$
at the first hidden layer and $0.00178$ at the second, at $\omega_0 = 30$
(Table 3).

| Scheme | Hidden layer 1 | Hidden layer 2 |
| --- | --- | --- |
| Sitzmann, described | 1.051 | 0.822 |
| Sitzmann, official | 1.052 | 1.033 |
| Villatoro, specified | 0.0364 | 0.00178 |

**Table 3.** Standard deviation of hidden pre-activations by depth at
$\omega_0 = 30$. The corresponding ratios between layers are $0.78$, $0.98$ and
$0.049$.

The falsifier was not triggered: $0.036$ is a factor of $29$ below the Sitzmann
values, not within a factor of two.

## Discussion

**Verdict: the hypothesis is supported.** The specification, instantiated as
written, places its hidden sines in the linear regime. The product
$\omega_0 \times \sigma$ holding at $\approx 1.05$ across $\omega_0 \ge 10$
identifies the deficit as exactly the missing $\omega_0$ — the initializer divides
by it and the forward pass never multiplies it back. At $\omega_0 = 30$ each
hidden unit is linear to four parts in ten thousand.

**The deficit compounds, which I did not anticipate.** A correctly-scaled SIREN
re-normalizes at every layer: $\sin$ of a unit-scale pre-activation is
arcsine-distributed with standard deviation $\approx 0.707$, and the next layer's
weights restore the scale. Once the sine is linear that restoration stops
happening — the layer passes its input through nearly untouched and then shrinks
it by another factor of $\omega_0$. Hence $0.036 \to 0.0018$, a ratio of $0.049$
against $0.78$ and $0.98$ for the intact schemes. Three hidden layers at
$\omega_0 = 30$ leave the deepest carrying signal at roughly $1/900$ of intended.
What survives is one Fourier-feature layer followed by a stack that is linear to
within a rounding error. The depth is decorative.

**What this does not show.** It would be easy, and wrong, to conclude that the
paper's SIREN results are corrupted. The implementation they cite makes the
degenerate configuration very difficult to reach: `siren-pytorch` computes
`w_std = sqrt(c / dim) / w0` and applies `sin(w0 * x)`, passing a *single* `w0` to
both.[@SirenPytorch] The division cancels the multiplication for any value
whatsoever, and its defaults — $\omega_0 = 30$ on the first layer, $\omega_0 = 1$
on hidden layers — reproduce the described convention exactly. To obtain the
degenerate network from that library you would have to reach past its interface
and set the initializer's $\omega_0$ to $30$ while leaving the activation's at
$1$. Nothing suggests they did.

So the mismatch is between the paper's **prose** and the paper's **library**, and
the most economical explanation is a transcription defect in §2.3.2 rather than a
defect in the experiments. I tested the text. I did not test their code, and I
cannot.

**Why a text defect is still worth a measurement.** Because the code is
unreleased, the text is the only specification anyone has. A reader
reimplementing §2.3.2 as written — the obvious thing to do with a numerical
methods paper — builds a network whose hidden layers are linear, and will
attribute the resulting performance to SIREN. The paper's own conclusion, that
SIREN underperforms in multi-fidelity settings, is precisely the belief that such
a reimplementation would appear to confirm. That is the trap worth marking:
not a wrong result, but a specification that manufactures agreement with a
conclusion for the wrong reason.

The adjacent observation I will not push on. The paper reports that $\omega_0 \in
\{5,10,20\}$ produced "no meaningful difference in predictive performance", which
is surprising given that $\omega_0$ is the canonical frequency knob in the SIREN
literature, and a degenerate network *would* be insensitive to it — $\omega_0$
reaching only the first layer. But the data here cannot distinguish that
explanation from an ordinary null result on smooth low-dimensional targets, and
the correlation is the kind of thing that looks like evidence only after you have
already decided. It is a question, not a finding.

**Limits.** One architecture ($3\times16$), one input domain, initialization only.
Nothing here measures accuracy, and the step from "the hidden stack is linear" to
"the fit is worse" is not free: a linear hidden stack has fewer effective degrees
of freedom, which in the data-scarce regime these emulators inhabit — 8 to 32
high-fidelity samples — could as easily help as hurt.

## Conclusion

A SIREN's initialization and its activation are two halves of one scaling
argument, and the two published conventions differ only in which half carries the
$\omega_0$. Take the initializer from one and the activation from the other and
the halves stop cancelling: hidden pre-activations land at $0.036$ instead of
$1$, the sines go linear, and the error compounds by a further factor of
$\omega_0$ per layer until the network is a Fourier layer with a linear tail. That
is what the specification in Villatoro et al. §2.3.2 describes, and the number has
not been reported before, in a paper that rests a conclusion on initialization
sensitivity while never measuring it.

What changed: a specification that reads like a minor notational variant is a
different network, and the difference is now measured rather than asserted.

The next experiment is the one this cannot reach. Does the degeneracy cost
accuracy, in the multi-fidelity setting and at the sample sizes these emulators
actually face? A preliminary training pilot run here at fixed learning rate
suggested it might not — that the linear hidden stack can *outperform* an intact
SIREN at $\omega_0 = 30$ with 8 to 32 samples, where a genuinely high-frequency
network overfits — but that pilot lacks the per-configuration learning-rate tuning
the paper performs with Hyperopt, and a network that fails to train is
indistinguishable from a network that overfits when the learning rate is held
fixed. So it is reported as a question and not a result. Answering it needs the
tuning, the multi-fidelity architecture, and ideally the authors' repository when
it lands.

## References
