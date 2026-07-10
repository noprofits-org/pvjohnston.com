---
title: Proving the Irrationality of ∛2
date: 2025-01-22
tags: mathematics, proof by contradiction, irrational numbers, number theory
---

Today, we're going to explore a fundamental concept in number theory by proving that the cube root of 2 (∛2) is an irrational number. This means that ∛2 cannot be expressed as a ratio of two integers, a/b. We'll achieve this using a classic technique known as proof by contradiction.

### Understanding the Problem

An *irrational number* is a number that cannot be written as a simple fraction (or ratio) of two integers. In contrast, rational numbers can be written as p/q where p and q are integers and q ≠ 0. For example, 1/2, 3, and -5/7 are rational numbers. We aim to prove that the specific number ∛2 does not fit this definition.

### Proof by Contradiction

The core idea of a proof by contradiction is to assume the opposite of what we want to prove and then show that this assumption leads to a logical inconsistency or contradiction. This contradiction then implies that our original assumption must be false, and thus, our intended statement must be true.

Here's how it works for ∛2:

1.  **Assume the opposite:** Let's assume that ∛2 is *rational*. This means we can write ∛2 as a fraction a/b, where *a* and *b* are integers, and *b* is not zero. We can also assume that this fraction is in its simplest form (i.e., *a* and *b* have no common factors other than 1; this is a crucial assumption).

    So we have:

    ∛2 = a/b

2.  **Cube both sides:** Cubing both sides of the equation gives us:

    2 = a³/b³

3.  **Rearrange:** Multiplying both sides by *b*³ gives:

    2b³ = a³

4.  **Analyze the implication:** This means that *a³* is an even number because it is equal to 2 times another integer (*b³*). If *a³* is even, it follows that *a* itself must also be even.

5.  **Represent *a* as an even number:** Since *a* is even, we can write *a* as 2*k*, where *k* is also an integer. Substituting this into the equation 2*b³* = *a³*:

    2b³ = (2k)³

    2b³ = 8k³

6.  **Simplify:** Divide both sides by 2:

    b³ = 4k³

7.  **Another implication:** Now, we see that *b³* is equal to 4 times an integer (*k³*). Therefore, *b³* is even and consequently, *b* is even.

8. **The Contradiction:** We've now shown that *both a* and *b* are even numbers. This means that they have a common factor of 2. However, we initially assumed that a/b was in its simplest form, meaning *a* and *b* should have no common factors other than 1. This creates a contradiction.

9. **Conclusion:** Because our initial assumption that ∛2 is rational leads to a contradiction, that initial assumption must be false. Therefore, we conclude that ∛2 is *irrational*.

### Why This Proof Works

The core of this proof relies on the fact that if the cube of an integer is even, the integer itself must also be even. This property, combined with the assumption that a/b is in its simplest form, allows us to create a logical contradiction, forcing us to conclude that ∛2 must be irrational.

### Final Thoughts

This proof is a classic example of how proof by contradiction can be used to demonstrate properties of numbers. The irrationality of ∛2 is not immediately apparent, but a careful application of logic allows us to see the inherent nature of this fundamental mathematical value. The proof highlights the beauty and power of mathematical reasoning.