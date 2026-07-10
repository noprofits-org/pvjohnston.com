---
title: No Integer Solutions for 2x² + 5y² = 14
date: 2025-01-22
tags: mathematics, number theory, Diophantine equations, proof by cases
---

Today, we're delving into the realm of Diophantine equations – equations where we're looking for integer solutions. Specifically, we'll prove that there are no integer solutions for the equation 2*x*² + 5*y*² = 14. This seemingly simple equation reveals interesting constraints on possible solutions when we restrict ourselves to integers.

### Understanding the Problem

We're looking for integer values for *x* and *y* that, when substituted into the equation 2*x*² + 5*y*² = 14, make the equation true. If we can show that no such integers exist, then we've proven our statement.

### Proof by Analyzing Cases and Remainders

We'll prove this by carefully considering the possible remainders when *x*² and *y*² are divided by 5 and 2, respectively, and by examining the sizes of the possible terms in the equation. This may not be the most elegant proof, but it is relatively straightforward to follow.

Let's analyze the possible values of 2*x*² mod 5 and 5*y*² mod 2.

#### Analyzing 2*x*² mod 5

1. The possible remainders when an integer is squared and divided by 5 are 0, 1, and 4. These correspond to 0², 1², 2², 3², and 4² mod 5 being congruent to 0, 1, 4, 4, and 1 respectively. So *x*² mod 5 can only be 0, 1, or 4.
2.  Therefore, 2*x*² mod 5 can only be 0, 2, or 8 mod 5. This is equivalent to 0, 2, or 3 mod 5.

#### Analyzing 5*y*² mod 2

1. Any integer y squared is either 0 or 1 when divided by 2. This means that y² mod 2 is either 0 or 1
2. Therefore 5*y*² mod 2 is equal to 5 times 0 mod 2 or 5 times 1 mod 2, meaning it can only equal 0 mod 2 or 5 mod 2. This means it can only be 0 or 1 mod 2.

#### Analyzing the Equation Mod 5

Let's rewrite our equation using modular arithmetic (mod 5):

2*x*² + 5*y*² ≡ 14 (mod 5)

Since 5*y*² is divisible by 5, it is congruent to 0 mod 5. Also, 14 is congruent to 4 mod 5. Therefore, the equation simplifies to:

2*x*² ≡ 4 (mod 5)

From our previous analysis, we know that 2*x*² can only be congruent to 0, 2 or 3 mod 5. However, it must be equal to 4 mod 5, and therefore this equation has no solutions for x and y.

#### An Alternate Proof

We could have instead used the mod 2 test in this way:

2*x*² + 5*y*² ≡ 14 (mod 2)
2*x*² + 5*y*² ≡ 0 (mod 2)
0 + 1*y*² ≡ 0 (mod 2)
y² ≡ 0 (mod 2)

This implies that y must be an even integer. Let's represent y = 2*k*, where k is an integer. Let's plug this back into the original equation:

2x² + 5(2k)² = 14
2x² + 20k² = 14
x² + 10k² = 7

We know that k is an integer. Let's test some integers for k. k=0 is not valid because x² = 7, and this has no integer solutions. k=1, x² = -3, no solutions. k=-1, x² = -3, no solutions. Any other integer value of k will result in x² being a negative integer, which has no solution.

### Conclusion

By exploring the possible remainders (mod 5) we were able to directly show there was no solution for x and y, and by exploring the solution (mod 2) we were able to reach a similar conclusion. The equation 2*x*² + 5*y*² = 14 has no integer solutions. This proof illustrates that even with simple-looking equations, number theory can impose strict limitations on the possible values that the variables can take.