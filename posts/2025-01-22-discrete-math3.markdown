---
title: Tiling a 10x10 Checkerboard with Straight Tetrominoes - An Impossibility Proof
date: 2025-01-22
tags: mathematics, tiling, tetrominoes, combinatorics, proof by coloring
---

Today, we tackle a classic puzzle in recreational mathematics: can we tile a standard 10x10 checkerboard using straight tetrominoes? A straight tetromino is a shape made of four squares arranged in a 1x4 or 4x1 rectangle. The answer, as we'll show, is no. And the way to prove this is a clever use of coloring.

### Understanding the Problem

We have a 10x10 checkerboard, which consists of 100 squares. A straight tetromino covers exactly 4 squares. If we could tile the board, we would need exactly 100 / 4 = 25 straight tetrominoes. This is a necessary but not sufficient condition for tiling to be possible. The fact that we need an integer amount of tiles does not prove that such a tile exists.

### The Coloring Strategy

Here's the clever part: We introduce a special coloring scheme to demonstrate that a tiling is impossible. We'll color the board in a way that highlights the inability of straight tetrominoes to cover the squares evenly.

Imagine coloring the 10x10 checkerboard in a pattern of 4 colors, let's say A, B, C, and D, in the following repeating pattern:

ABCDABCDAB
CDABCDABCD
ABCDABCDAB
CDABCDABCD
ABCDABCDAB
CDABCDABCD
ABCDABCDAB
CDABCDABCD
ABCDABCDAB
CDABCDABCD

Essentially, we're coloring the board in such a way that every row contains the sequence "ABCD" two and a half times, and each column contains this sequence two and a half times too.

### Analyzing the Coloring

Let's count how many squares of each color there are:

* **Color A:** 25 squares
* **Color B:** 25 squares
* **Color C:** 25 squares
* **Color D:** 25 squares

Now, let's consider how a straight tetromino covers these colored squares. Regardless of its orientation (horizontal or vertical), a straight tetromino will always cover exactly one square of each of the four colors.

### The Impossibility Proof

Let's assume, for the sake of contradiction, that it *is* possible to tile the 10x10 checkerboard with 25 straight tetrominoes. If such a tiling were possible, then those 25 tetrominoes would cover exactly 25 squares of color A, 25 squares of color B, 25 squares of color C, and 25 squares of color D. This agrees with our above color count, and looks promising at first glance.

However, the tiling process must fill the entire board. Now let's analyze the positions of our tetrominoes. A single horizontal tetromino can only ever cover one row (because the tetromino is 4 spaces long). A single vertical tetromino can only ever cover one column.

Now let's look at any given row. This row contains 2.5 of the ABCD pattern. Any horizontal tetromino we place will always be aligned with this pattern and thus cover exactly one square of each color. However, there must be another tetromino to cover the remaining 0.5 of the ABCD pattern. This new tetromino must be vertical, and it must be contained entirely within a set of columns. A vertical tetromino cannot be used to complete a row because it will have to span across a column and not stay within a single row. The same logic holds for a column; a vertical tetromino cannot be used to complete a column.

Since there must be the same number of tiles that are horizontal as vertical (as each one contains all four colors), the rows and columns must both be divisible by 4. However, a row has 10 squares which is not divisible by 4, and a column has 10 squares which is also not divisible by 4. Therefore, it is impossible to tile a 10x10 checkerboard using straight tetrominoes.

### Conclusion

Through this clever coloring argument, we've demonstrated that it is impossible to tile a 10x10 checkerboard using only straight tetrominoes. This proof highlights the power of introducing clever auxiliary structures (like our coloring) to reveal an underlying impossibility that might not be obvious at first glance. The key takeaway is that even though the numbers initially suggest the possibility of a tiling, the coloring scheme unveils the fundamental obstruction caused by the 2.5 copies of our ABCD pattern in every row and column.

This is yet another fascinating example of how mathematics helps us uncover elegant solutions to seemingly simple problems!