---
title: No Small Perfect Cubes as Sums of Two Cubes
date: 2025-01-22
tags: mathematics, number theory, perfect cubes, Fermat's Last Theorem
---

Today, we're diving into a fascinating corner of number theory to explore a specific problem: proving that there are no positive perfect cubes less than 1000 that can be expressed as the sum of the cubes of two positive integers. This statement, while seemingly simple, touches upon concepts related to Fermat's Last Theorem and provides a good exercise in proof by exhaustion and careful consideration of cases.

Essentially, we want to show that for perfect cubes *z*³ < 1000, there are no positive integers *x* and *y* such that *x*³ + *y*³ = *z*³.

### Understanding the Problem

First, let's list the positive perfect cubes less than 1000. These are:

1³ = 1
2³ = 8
3³ = 27
4³ = 64
5³ = 125
6³ = 216
7³ = 343
8³ = 512
9³ = 729
10³ = 1000 (which is not included as it is not less than 1000)

We aim to demonstrate that none of these cubes can be represented as a sum of two other positive integer cubes.

### Strategy: Proof by Exhaustion

Our approach will be to test each of the listed perfect cubes, checking if they can be expressed as the sum of two smaller perfect cubes. Since *x* and *y* are positive integers, we only need to check values up to the cube root of *z*³. We can systematically check possible combinations.

### Case Analysis

**Important note**: We don't need to consider cases where *x* = *y* because we are searching for _distinct_ positive integer solutions. So for the case where x=1, we will not consider y=1 for example.

**Case 1: z³ = 1**

We're looking for *x*³ + *y*³ = 1. Since both *x* and *y* must be positive integers, there are no possible combinations that will add to 1.

**Case 2: z³ = 8**

We're looking for *x*³ + *y*³ = 8. The only possibilities are with *x* and *y* both less than 2. Therefore, the only value of x or y that is possible is 1. However, 1³ + 1³ = 2 which does not equal 8.

**Case 3: z³ = 27**

We're looking for *x*³ + *y*³ = 27. We can try combinations using only 1 and 2 for *x* and *y* (since 3^3 = 27):
* 1³ + 1³ = 2 (not 27)
* 1³ + 2³ = 9 (not 27)
* 2³ + 1³ = 9 (not 27, same as above)
* 2³ + 2³ = 16 (not 27)

**Case 4: z³ = 64**

We're looking for *x*³ + *y*³ = 64. We can try combinations using only 1, 2, and 3 for *x* and *y*.
* Combinations of 1³ + *y*³ are too small
* 2³ + 1³ = 9 (not 64)
* 2³ + 2³ = 16 (not 64)
* 2³ + 3³ = 35 (not 64)
* 3³ + 1³ = 28 (not 64)
* 3³ + 2³ = 35 (not 64)
* 3³ + 3³ = 54 (not 64)

**Case 5: z³ = 125**

We're looking for *x*³ + *y*³ = 125. We can try combinations using 1, 2, 3 and 4.
* Combinations with 1 are too small
* 2³ + 1³, 2³ + 2³, 2³ + 3³, 2³ + 4³ are all not 125
* 3³ + 1³, 3³ + 2³, 3³ + 3³, 3³ + 4³ are all not 125
* 4³ + 1³, 4³ + 2³, 4³ + 3³, 4³ + 4³ are all not 125

**Case 6: z³ = 216**

We're looking for *x*³ + *y*³ = 216. We can try combinations up to 5.
* Combinations using 1 are too small
* We already know from previous cases that combinations of x,y <= 4 do not equal the cube being tested.
* 5³ + 1³ = 126 (not 216)
* 5³ + 2³ = 133 (not 216)
* 5³ + 3³ = 152 (not 216)
* 5³ + 4³ = 189 (not 216)
* 5³ + 5³ = 250 (not 216)

**Case 7: z³ = 343**

We're looking for *x*³ + *y*³ = 343. We can try combinations up to 6.
* Combinations using 1 are too small
* We already know from previous cases that combinations of x,y <= 5 do not equal the cube being tested.
* 6³ + 1³ = 217 (not 343)
* 6³ + 2³ = 224 (not 343)
* 6³ + 3³ = 243 (not 343)
* 6³ + 4³ = 301 (not 343)
* 6³ + 5³ = 331 (not 343)
* 6³ + 6³ = 432 (not 343)

**Case 8: z³ = 512**

We're looking for *x*³ + *y*³ = 512. We can try combinations up to 7.
* Combinations using 1 are too small
* We already know from previous cases that combinations of x,y <= 6 do not equal the cube being tested.
* 7³ + 1³ = 344 (not 512)
* 7³ + 2³ = 351 (not 512)
* 7³ + 3³ = 370 (not 512)
* 7³ + 4³ = 407 (not 512)
* 7³ + 5³ = 468 (not 512)
* 7³ + 6³ = 419 (not 512)
* 7³ + 7³ = 686 (not 512)

**Case 9: z³ = 729**

We're looking for *x*³ + *y*³ = 729. We can try combinations up to 8.
* Combinations using 1 are too small
* We already know from previous cases that combinations of x,y <= 7 do not equal the cube being tested.
* 8³ + 1³ = 513 (not 729)
* 8³ + 2³ = 520 (not 729)
* 8³ + 3³ = 547 (not 729)
* 8³ + 4³ = 576 (not 729)
* 8³ + 5³ = 631 (not 729)
* 8³ + 6³ = 704 (not 729)
* 8³ + 7³ = 643 (not 729)
* 8³ + 8³ = 1024 (not 729)

### Conclusion

By systematically checking every perfect cube less than 1000, we have demonstrated that none of them can be expressed as the sum of two positive integer cubes. We tested each case, exhausting all possibilities and confirming that no such representation exists. This exercise showcases a straightforward yet effective approach to proving statements within a limited domain.

This result is consistent with a special case of Fermat's Last Theorem for the exponent 3. Specifically, it confirms that there are no positive integer solutions for a³ + b³ = c³ where c < 10. While we didn't invoke the full theorem here, this specific instance highlights a related and interesting property of perfect cubes.

This exploration offers a satisfying illustration of how we can approach and solve number theory problems with careful, systematic thinking.