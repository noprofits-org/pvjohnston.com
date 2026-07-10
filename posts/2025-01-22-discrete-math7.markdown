---
title: Big-O Analysis of an Algorithm Segment
date: 2025-01-22
tags: mathematics, computer science, algorithms, big-O notation, time complexity
---

Today, we're stepping into the world of algorithm analysis to determine the time complexity of a specific code segment. We'll be using Big-O notation to provide an upper bound on the number of operations performed as the input size, *n*, grows.

### Understanding the Problem

We are given a code segment, which is structured as a `while` loop. Inside the loop, we perform some arithmetic operations. Our task is to estimate the number of additions and multiplications (collectively referred to as "operations") using Big-O notation. We're ignoring the comparison step in the while loop, as is conventional. The code segment is:

```haskell
i := 1
t := 0
while i <= n
  t := t + i
  i := 2 * i
```

The variable `i` starts at 1 and is doubled in each iteration, meaning it takes on the values 1, 2, 4, 8, and so on. The variable `t` accumulates a sum. Our goal is to determine how the number of operations grows as *n* increases.

### Analyzing the Loop Iterations

Let's trace the execution of the loop for a bit to get a handle on the pattern:

*   **Iteration 1:** `i = 1`, `t = 0 + 1`, `i` becomes 2 (1 addition, 1 multiplication, where multiplication is `i:=2*i`).
*   **Iteration 2:** `i = 2`, `t = 1 + 2`, `i` becomes 4 (1 addition, 1 multiplication).
*   **Iteration 3:** `i = 4`, `t = 3 + 4`, `i` becomes 8 (1 addition, 1 multiplication).
*   ...

In general, in the *k*-th iteration, we have `i = 2^(k-1)`. The loop continues as long as *i* ≤ *n*. So, the loop will continue as long as *2^(k-1)* ≤ *n*.

### Determining the Number of Iterations

To find the number of iterations, we want to find the largest value of *k* such that *2^(k-1)* ≤ *n*.
Taking the base-2 logarithm of both sides, we have:

*k* - 1 ≤ log₂(n)

*k* ≤ log₂(n) + 1

Since *k* represents the number of iterations, and *k* must be an integer, the maximum number of iterations is approximately log₂(n) + 1, which is a value that is proportional to log₂(n).

### Counting the Operations

Within each iteration of the loop, we perform:

*   One addition: `t := t + i`
*   One multiplication: `i := 2 * i`

Therefore, the number of operations in a single iteration is 2. Since the number of iterations is proportional to log₂(n), the total number of operations is roughly 2 * log₂(n) + 2.

### Big-O Notation

In Big-O notation, we ignore constant factors and lower-order terms. Thus:

O(2 log₂(n) + 2) becomes O(log₂(n)).

Furthermore, the base of a logarithm doesn't matter in Big-O notation since different bases differ by only a constant factor. Therefore, log₂(n) and log(n) (base 10) or even ln(n) all represent the same time complexity. Therefore we can simply say:

O(log₂(n)) becomes O(log n)

### Conclusion

The number of operations performed in this algorithm segment is O(log *n*). This means that the number of operations grows logarithmically with respect to the input *n*. This growth rate is relatively slow, indicating that this algorithm is efficient, especially compared to algorithms with linear or quadratic complexity.