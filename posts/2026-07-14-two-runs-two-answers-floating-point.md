---
title: "Two runs, two answers: floating-point sums aren't associative"
date: 2026-07-14
author: Peter Johnston
tags: floating-point, numerical computing, reproducibility, ieee 754, scientific computing, hpc
description: Run the same simulation on four cores and eight and the total energy disagrees in the twelfth digit. That is not a bug in your code — it is floating-point addition refusing to be associative, and the fix is not to make the hardware lie but to know your noise floor.
---

Run the same molecular-dynamics job twice — identical inputs, identical binary,
identical seed — but once on four MPI ranks and once on eight, and the total
energy will disagree. Not wildly: the two numbers match for eleven or twelve
digits and then drift apart in the noise. The instinct is to hunt for a bug — an
uninitialized variable, a race condition, a stray non-deterministic hash. But
there is nothing to fix, because nothing is broken. You have just watched
floating-point addition decline to be associative, and the sooner you accept that
the arithmetic itself is doing this on purpose, the sooner you stop chasing a
ghost.

## The one fact that explains it

In real numbers, addition is associative: $(a+b)+c = a+(b+c)$, always. In IEEE
754 double precision it is not. A `double` stores a 53-bit significand, so every
individual operation produces the exact mathematical result and then **rounds** it
to the nearest representable value.[@IEEE754_2019] Two additions mean two roundings, and *when*
you round changes *what* you get.

The pathological case makes it obvious:

```python
>>> (1e20 + -1e20) + 1.0
1.0
>>> 1e20 + (-1e20 + 1.0)
0.0
```

**Code 1.** The same three numbers, added in two groupings, give answers that
differ by 100%.

In the first line of Code 1 the two large magnitudes cancel exactly, leaving
$1$. In the second, `-1e20 + 1.0` is computed first — but the spacing between
representable doubles near $10^{20}$ is about $2^{14} = 16384$, so the $+1$ falls
entirely below the last bit and vanishes. The intermediate rounds back to
$-10^{20}$, and adding $10^{20}$ gives exactly zero. The $1$ was never lost to a
mistake; it was lost to rounding, at a place that depended only on the order of
operations. This is the canonical example that motivates every careful treatment
of the subject.[@Goldberg1991]

Most real numbers are not $10^{20}$ apart, so the effect is usually tiny — a unit
or two in the last place rather than a total wipeout. But *tiny and
order-dependent* is exactly the property that turns a parallel program
non-deterministic.

## Why parallelism is where it bites

A simulation's energy is a sum over millions of pairwise interactions. Written
mathematically the sum is a single number, $S = \sum_{i=1}^{N} x_i$. Written as
code that has to run on a machine, it is a *sequence* of two-operand additions,
and someone has to choose the sequence.

On one core the choice is boring: add them left to right. Split the work across
$p$ cores and each core sums its own slice, then the slices are combined — a
**reduction**. Now the grouping of the sum is a function of $p$. Four ranks
partition the terms one way, eight ranks another, and because the intermediate
roundings land differently, the final bits differ. The number of cores is an
accident of which machine you grabbed, and you have accidentally made your
physics depend on it.

The size of the disagreement is not mysterious either. For sequential summation
the worst-case rounding error is bounded by

$$|\hat{S} - S| \;\le\; (N-1)\,u \sum_{i=1}^{N} |x_i| \;+\; O(u^2),$$

where $u = 2^{-53} \approx 1.11\times10^{-16}$ is the unit roundoff for binary64.
Divide through by $|S|$ and the relative error is bounded by $(N-1)\,u$ times the
ratio $\sum|x_i| \,/\, |\sum x_i|$ — the **condition number** of the sum.[@Higham2002]
When the terms mostly share a sign that ratio is near $1$ and the error is genuinely
negligible; when there is heavy cancellation (the ratio blows up) the same
reordering that was noise becomes catastrophic. Reproducibility and accuracy are
the same problem wearing different hats.

## The compiler is also reordering behind your back

Even single-threaded, the source you wrote is not the arithmetic that runs. Two
compiler behaviors routinely change the last bits.

The first is the **fused multiply-add**. The expression `a*b + c` can compile to
two rounded operations or to one `fma` instruction that computes $a\cdot b + c$
with a *single* rounding of the exact product. The FMA answer is more accurate,
but it is a *different* number, and whether you get it depends on the compiler,
the optimization level, and whether the target CPU has the instruction. The same
code on x86 and on ARM can differ for this reason alone.

The second is `-ffast-math` (and its umbrella, `-Ofast`). That flag tells the
compiler it may treat floating-point as if it were real arithmetic — reassociate
sums, assume no NaNs or infinities, flush denormals to zero, factor and cancel
freely. It is often a real speedup, and it is also a blanket license to do
exactly the algebra that Code 1 warns against. GCC's own documentation is blunt
that these optimizations can change results; turning them on trades reproducibility for
throughput, and it should be a conscious trade, not a default you inherited from a
Makefile.[@GccFPMath] There is even a third, quieter culprit: the math library. Different
`libm` implementations of `exp`, `sin`, or `pow` are not all correctly rounded, so
linking against a different version — or a vendor-tuned one — can move the last ULP
of every transcendental call in your code.

## So what is the "right" answer?

There isn't a single bit-exact one, and that is the reframing that helps. There is
the exact real-number result $S$, which the hardware cannot represent, and there
is a small cloud of floating-point results that all sit within a few ULP of it.
Every ordering, every core count, every FMA decision picks a different point in
that cloud. Asking "which grouping is correct?" is the wrong question; the cloud's
*width* is the thing to know, because it tells you how many digits mean anything.

This is the same discipline I leaned on in
[the correlation-gap-in-water measurement](/posts/2026-07-04-the-correlation-gap-in-water-measured.md),
where every quoted digit was chosen to sit far above the arithmetic noise floor.
The reason those energies could be reported to microhartree precision is that the
quantities of interest were well-conditioned and the reported digits were nowhere
near the last bit. The non-determinism was still there in the trailing digits — it
is always there — but it lived below the precision anyone claimed.

## What reproducibility actually costs

If you genuinely need **bit-for-bit** results — regulated engineering, a
regression test that diffs raw output, debugging a divergence between two runs —
you can have them, but you pay for each source of freedom. Fix the reduction order
with a deterministic-reduction option (many MPI and BLAS libraries offer one). Pin
the FMA and reassociation flags and forbid `-ffast-math`. Pin the math-library
version. The cost is real: deterministic reductions can't load-balance as freely,
and forbidding FMA leaves both speed and accuracy on the table.

More often the better move is to stop demanding bit-reproducibility and instead
*shrink and characterize* the error. **Pairwise (cascade) summation** groups the
sum as a balanced tree, dropping the error growth from $O(uN)$ to $O(u\log N)$ —
it is why NumPy's `sum` is more accurate than a naïve Python
loop.[@Higham2002; @NumpySum] **Kahan compensated summation** carries a running
correction term and bounds the error at $O(u)$ essentially independent of $N$, for
a few extra flops per element.[@Kahan1965] Neither makes the answer unique across core counts,
but both push the cloud small enough that the disagreement retreats to digits you
were never going to trust anyway.

That is the resolution to the two-core-count puzzle we opened with. The eleven
matching digits are the physics; the disagreement in the twelfth is the ordering
of a sum, and it was always beneath the resolution of the result. The fix is not
to force the hardware to pretend addition is associative — it isn't — but to know
where your noise floor sits and to quote nothing below it. A simulation that
reports only the digits it can defend will never surprise you by disagreeing with
itself, because it never claimed the digits that were free to move.

## References
