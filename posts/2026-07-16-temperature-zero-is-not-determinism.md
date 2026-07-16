---
title: "Temperature zero is not determinism: your logits depend on who else is in the batch"
date: 2026-07-16
author: Peter Johnston
tags: llm, inference, determinism, reproducibility, floating-point, gpu, numerical computing
description: Enumerating every ordering of a signed sum shows that reordering moves the result by one ulp — far too little to explain why temperature-zero endpoints return different paragraphs. The rest of the story is batch invariance, bfloat16, and argmax.
---

## Abstract

Greedy decoding at temperature zero is a deterministic function of the logits,
yet production language-model endpoints return different completions for
identical prompts. The prevailing explanation attributes this to floating-point
non-associativity combined with concurrent thread scheduling. I test the
arithmetic half of that hypothesis directly by enumerating every ordering of a
small signed array and measuring the spread of achievable sums. Order-dependence
is confirmed — 40,320 orderings produce 275 distinct results — but every one of
those sums lies within $\pm 2^{-52}$ of the exact answer, one ulp at unit scale,
which is far too small to account for divergence at the level of whole
paragraphs. The published
literature locates the true mechanism in the failure of **batch invariance**
rather than in concurrency, and I argue that the gap between a one-ulp
perturbation and a different paragraph is closed by three amplifiers: bfloat16's
coarse precision, the discreteness of argmax, and autoregressive feedback.

## Introduction

Set `temperature=0`, send an identical prompt to an identical model on identical
hardware a thousand times, and you will not get a thousand identical
completions. The standard account of why blames a race: GPUs run thousands of
threads concurrently, floating-point addition is not associative, so whichever
core finishes first changes the sum, and the logits wobble. Call this the
**concurrency hypothesis**. It is repeated widely enough to have become
folklore — documented, and then dismantled, by the source this note leans on
most.[@He2025Nondeterminism]

It is also, on inspection, unable to survive its own prediction. If concurrent
scheduling were reordering the arithmetic, then running the *same* matrix
multiplication on the *same* inputs twice would produce different bits. It does
not. Repeated identical `torch.mm` calls on identical tensors return bitwise
equal results indefinitely.[@He2025Nondeterminism] The typical forward pass of a
transformer contains no operations that require atomic accumulation — there is
usually sufficient parallelism along the batch dimension that reductions stay
within a single core — so it is **run-to-run deterministic**. Something else is
moving the logits.

Two claims are therefore worth separating. The first is arithmetic — that
summation order changes a floating-point result at all — and I test it directly
below, because the magnitude turns out to matter enormously for the argument.
The second is causal — that *concurrency* is what varies the order — and I check
it against the published record. The second does not survive that check: the
alternative — that the reduction order varies with **batch size**, a quantity
set by other users' traffic — is the finding this note is built around.

## Computational Methods

All experiments reported here were run on CPython 3.13.12, aarch64 macOS, using
IEEE 754 binary64 arithmetic with a 53-bit significand (`sys.float_info.mant_dig
= 53`).[@IEEE754_2019] No GPU was used, and no result in this note's Results
section depends on one.

The test array is the eight-element signed set
$\{10^{-10}, 10^{-5}, 10^{-2}, 1\}$ together with its negation, whose exact sum
is identically zero. Two procedures were applied. The first mirrors the sampling
procedure used in the source literature: seed the Mersenne Twister at 42, shuffle
the array, accumulate, and repeat for $n$ trials, counting distinct results. The
second is exhaustive — enumerate all $8! = 40{,}320$ permutations with
`itertools.permutations` and accumulate each, which removes any dependence on
which orderings a sampler happens to visit (Code 1).

Both procedures accumulate left-to-right with `functools.reduce`, and Python's
built-in `sum` is deliberately **not** used. Naive left-to-right accumulation is
the model that corresponds to an uncompensated hardware reduction, which is the
object of interest here; `sum` no longer supplies it. Since CPython 3.12 the
built-in applies **Neumaier compensated summation**,[@CPython312Sum] a technique
whose whole purpose is to cancel the reordering error this experiment exists to
exhibit.[@Higham2002] The distinction is not pedantry — it is the entire content
of the discrepancy reported below.

```python
from itertools import permutations
from functools import reduce

vals = [1e-10, 1e-5, 1e-2, 1.0, -1e-10, -1e-5, -1e-2, -1.0]
sums = {reduce(lambda a, b: a + b, p, 0.0) for p in permutations(vals)}

s = sorted(sums)
print(len(s), s[0], s[-1])   # 275 -2.220446049250313e-16 2.220446049250313e-16
```

**Code 1.** Exhaustive enumeration of every summation order for an array whose
exact sum is zero, counting the distinct floating-point results and their range.

The GPU-side claims discussed in the Discussion section — batch-invariance
failure in `torch.mm`, the completion-divergence experiment on
Qwen3-235B-A22B-Instruct-2507, and the throughput costs of batch-invariant
kernels — were **not** reproduced here and are attributed to their sources
throughout. This is a real limitation of the present note: I am reporting those
results, not verifying them.

## Results

Order-dependence is confirmed, and in multiplicity it is not marginal: across
all 40,320 orderings, 275 distinct sums occur where mathematics admits exactly
one. The
exact answer, $0.0$, is among them but holds no privileged position — it is one
of 275, reachable only by the orderings that happen to cancel cleanly.

The sampled procedure converges toward the exhaustive count from below, as
Table 1 shows, which identifies the sampling artifact directly: any count
obtained from a fixed number of shuffles is a lower bound on the achievable set,
and reports the sampler's coverage as much as the arithmetic.

| Trials $n$ | Distinct sums |
| --- | --- |
| 100 | 39 |
| 1,000 | 145 |
| 10,000 | 258 |
| 100,000 | 275 |
| Exhaustive (40,320) | **275** |

**Table 1.** Distinct floating-point sums recovered from the same eight-element
array as a function of how many random orderings are sampled, against the
exhaustive count. The sampled count is a coverage statistic, not a property of
the arithmetic.

One apparent discrepancy is worth recording, because resolving it sharpens the
argument rather than complicating it. The source that popularized this experiment
reports 102 unique results at $n = 10{,}000$ with seed 42, spanning
$\pm 8.33 \times 10^{-17}$.[@He2025Nondeterminism] Neither figure matches the
$n = 10{,}000$ row of Table 1, which gives 258 unique results across the wider
$\pm 2^{-52}$.

Nothing in the arithmetic, the array, the seed, or the shuffle accounts for the
gap. The accumulator does, and it moved underneath the experiment between
interpreter releases. Run on all-float input under CPython 3.13.12, the built-in
`sum` returns exactly $0.0$ for every one of the 40,320 orderings: compensation
erases the phenomenon outright. It survives in the source's snippet only by an
accident of notation. That snippet writes its array as `[1e-10, 1e-5, 1e-2, 1]`,
where the `1` is an `int` rather than a float, and the mixed int/float path
compensates less completely — leaving 103 achievable results instead of one.

That reconciles both figures. The source's snippet, run verbatim and unmodified
under CPython 3.13.12, returns 102 unique results with a maximum of
$8.326672684688674 \times 10^{-17}$, reproducing its published output exactly, to
the last digit. Through CPython 3.11 the built-in is uncompensated and therefore
numerically identical to `reduce`; by that equivalence the same snippet yields
Table 1's 258 on an older interpreter, though no pre-3.12 interpreter was
available here to confirm it directly. Both counts are correct. They are
measurements of two different accumulators that happen to share a name. And
Table 1's moral applies to the source as well: its 102 is a nearly complete
sample of the 103 orderings its accumulator can actually reach — a coverage
statistic, not a property of floating-point addition.

The published snippet was correct when it was written, and an interpreter upgrade
later made it quietly measure something else. That is, in miniature, the same
hazard this note is about.

The magnitude is the result that matters most, and it cuts against the
hypothesis it was offered to support. Every one of the 275 sums lies in
$[-2^{-52}, +2^{-52}]$; the full spread is $2^{-51}$, or two machine epsilon.
The worst ordering is wrong by one unit in the last place at the scale of the
largest summand — comfortably inside the standard error bound for sequential
summation, which caps the error at a few ulps of $\sum|x_i|$ regardless of how
completely the terms cancel.[@Higham2002; @Goldberg1991] Reordering a sum
perturbs it in the last bit. That is all it does.

## Discussion

The Results section leaves the phenomenon unexplained in both directions. The
mechanism is wrong, and the magnitude is too small.

**The mechanism.** If concurrency is not varying the reduction order, something
else is, and it is the batch size. A matrix multiply is a pile of dot products,
and each dot product is a reduction whose split across cores is chosen for the
shape at hand. With a large batch there is ample parallelism: assign each output
tile to a core and keep the whole reduction local — a data-parallel strategy.
With a batch of one that leaves most of the GPU idle, so the kernel switches to
a **split-K** reduction, chopping the contraction dimension across many cores
and combining partials in a second pass. Same numbers, different
parenthesization. At very small batch sizes the kernel may switch tensor-core
instruction shapes, or abandon tensor cores entirely — each with its own
internal reduction order.[@He2025Nondeterminism] The consequence is that a row's
result depends on how many unrelated rows shared the call:

```python
import torch
torch.set_default_device('cuda')

B = 2048
D = 4096
a = torch.linspace(-1000, 1000, B*D).reshape(B, D)
b = torch.linspace(-1000, 1000, D*D).reshape(D, D)
out1 = torch.mm(a[:1], b)    # one row, batch of 1
out2 = torch.mm(a, b)[:1]    # the same row, batch of 2048
print((out1 - out2).abs().max())  # tensor(1669.2500, device='cuda:0')
```

**Code 2.** The same input row multiplied by the same matrix returns different
values depending only on how many unrelated rows shared the call. Code and
output reproduced verbatim from He and Thinking Machines Lab; not run in the
present work.

Nothing in Code 2 is random, and both lines are individually reproducible
forever. They simply are not the same computation. The same reasoning applies to
the other two reductions in a transformer: **RMSNorm** reduces across features,
and **attention** reduces across the KV dimension, where the split additionally
depends on chunked-prefill boundaries and cache layout — so numerics must be
invariant not only to how many requests are batched but to how each request gets
sliced.[@He2025Nondeterminism] Compose a kernel that is not invariant to batch
size with a serving engine whose batch size varies with load, and you have a
system that is deterministic from the operator's seat and nondeterministic from
yours. Your prompt's neighbors get a vote on your logits.

**The magnitude.** A one-ulp perturbation in binary64 explains nothing about
paragraphs, and this is where the LLM case departs sharply from the
molecular-dynamics one I discussed in
[two runs, two answers](/posts/2026-07-14-two-runs-two-answers-floating-point.html).
There, last-bit noise stayed last-bit noise, safely beneath any digit worth
quoting. Here it is amplified three times over.

First, precision. Serving runs in **bfloat16**, whose 8-bit significand gives a
unit roundoff of $u = 2^{-8} \approx 3.9 \times 10^{-3}$ against $2^{-53}
\approx 1.1 \times 10^{-16}$ for binary64 — coarser by a factor of $2^{45}$,
some thirteen orders of magnitude. The Results section's tidy $\pm 2^{-52}$ is a
best case that inference never operates in.

Second, discreteness. A reduction's output is continuous in its rounding error;
argmax is not. Most perturbations change nothing, because the leading token
leads comfortably. But over hundreds of decoding steps some step is a near-tie,
and there the perturbation decides the token.

Third, feedback. The chosen token is appended to the context and conditions
everything after it, so a single flipped near-tie does not stay local. The
published divergence experiment makes this concrete: 1,000 completions of
Qwen3-235B-A22B-Instruct-2507 at temperature zero yielded 80 unique outputs,
identical for the first 102 tokens and diverging at the 103rd, where 992
completions continued "Queens, New York" and 8 continued "New York
City."[@He2025Nondeterminism] A last-bit difference was converted into a
categorical one by argmax, then into a different document by recursion.

**The cost of fixing it.** The remedy is not exactness but *invariance*: fix each
kernel's reduction strategy independently of batch size, accept a suboptimal
tiling at some shapes, and your row is summed identically whether it is alone or
in a crowd. Implemented as a drop-in operator library, this turns those 80 unique
completions into one.[@BatchInvariantOps] It is not free — the original
demonstration took a vLLM workload from 26 s to 55 s, improving to 42 s with a
better attention kernel, and a subsequent SGLang implementation with CUDA-graph
support reduced the average slowdown to 34.35% from the 61.5% originally
reported.[@He2025Nondeterminism; @SGLang2025Deterministic] A third of throughput
is a real bill, and for most chat traffic it buys nothing anyone will notice.

Where it is cheap at the price is anywhere a number gets reported. A regression
test that diffs raw output is otherwise measuring the queue depth of the serving
cluster. An evaluation reporting a one-point delta is not credible if a rerun
moves it by more. And in reinforcement learning the problem is structural: if
sampler and trainer compute logits under different reduction orders, a nominally
on-policy algorithm is quietly off-policy, and the divergence is arithmetic
rather than statistical — more rollouts will not average it
away.[@He2025Nondeterminism]

## Conclusion

The concurrency hypothesis fails not because its arithmetic is wrong but because
its arithmetic is *insufficient*. Summation order does perturb a result — 275
distinct answers from one array is a vivid demonstration — but it perturbs it by
one ulp, and one ulp is not a paragraph. The hypothesis then compounds the error
by misattributing the reordering to thread scheduling, when the forward pass
uses no atomics and is run-to-run deterministic. What actually varies is batch
size, which is set by strangers, and what turns its one-ulp consequence into a
different completion is the chain of bfloat16 precision, argmax discretization,
and autoregressive feedback.

So `temperature=0` does exactly what it claims: it makes the last step of the
pipeline deterministic. The nondeterminism was never in the sampler. It lives
upstream in the reductions, and it is a property you buy in throughput rather
than a flag you set. Which returns the question to where it belongs — not "how do
I make it stop," but the one I keep arriving at from every direction: does
anything you report actually depend on the bits that moved?

## References
