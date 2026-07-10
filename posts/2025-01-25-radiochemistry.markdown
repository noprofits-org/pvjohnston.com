---
title: Unraveling Radioactive Decay - A Journey Through Half-Lives
date: 2025-01-27
tags: chemistry, radiochemistry, nuclear chemistry, mathematics, half-life
---

Radioactive decay is a fundamental process in nuclear physics and chemistry, describing the spontaneous transformation of unstable atomic nuclei.[@Wikipedia_RadioactiveDecay_2023] A central concept in understanding this phenomenon is the *half-life* ($t_{1/2}$), which represents the time required for half of the radioactive atoms in a sample to decay. This post will delve into the intricacies of half-life calculations, exploring the underlying principles and applying them to various problems.

## The Nature of Radioactive Decay

Radioactive decay follows first-order kinetics, meaning the rate of decay is directly proportional to the number of radioactive atoms present. This leads to an exponential decay law. Mathematically, this is expressed as:

$N_t = N_0 e^{-\lambda t}$

Where:

*   $N_t$ is the number of radioactive atoms at time *t*.
*   $N_0$ is the initial number of radioactive atoms.
*   $\lambda$ is the decay constant, representing the probability of decay per unit time.

The relationship between the decay constant ($\lambda$) and the half-life ($t_{1/2}$) is crucial:

$\lambda = \frac{\ln 2}{t_{1/2}} \approx \frac{0.693}{t_{1/2}}$

This equation highlights the inverse relationship between the decay constant and the half-life: a larger decay constant implies a shorter half-life, meaning the substance decays more rapidly.

## Balancing Nuclear Equations (Brief Review)

Before we dive into calculations, let's briefly revisit balancing nuclear equations. Remember the conservation laws:

*   **Conservation of mass number (A):** The sum of mass numbers on both sides of the equation must be equal.
*   **Conservation of atomic number (Z):** The sum of atomic numbers on both sides of the equation must be equal.

For example: $\ce{^{238}_{92}U -> ^{234}_{90}Th + ^{4}_{2}He}$ (alpha decay)

## Half-Life Calculations: Worked Examples

Now, let's apply these concepts to some problems.

**Problem 1: Decay of Actinium-225**

Actinium-225 ($\ce{^{225}_{89}Ac}$) has a half-life of 10.0 days. If a sample initially contains 2.00 mg of Actinium-225, how much will remain after 30.0 days?

*   $N_0$ = 2.00 mg
*   $t_{1/2}$ = 10.0 days
*   $t$ = 30.0 days

First, we can use the following equation:

$N_t = N_0 \left(\frac{1}{2}\right)^{\frac{t}{t_{1/2}}}$

$N_t = 2.00 \text{ mg} \times \left(\frac{1}{2}\right)^{\frac{30.0}{10.0}} = 2.00 \text{ mg} \times \left(\frac{1}{2}\right)^3 = 0.250 \text{ mg}$

**Problem 2: Determining Half-Life of a New Isotope**

A newly discovered radioactive isotope decays from 5.00 g to 1.25 g in 12.0 hours. What is its half-life?

$N_t = N_0 \left(\frac{1}{2}\right)^{\frac{t}{t_{1/2}}}$

$\frac{1.25 \text{ g}}{5.00 \text{ g}} = \left(\frac{1}{2}\right)^{\frac{12.0}{t_{1/2}}}$

$\frac{1}{4} = \left(\frac{1}{2}\right)^{\frac{12.0}{t_{1/2}}}$

$2 = \frac{12.0}{t_{1/2}}$

$t_{1/2} = 6.0 \text{ hours}$

**Problem 3: Activity and Decay Constant**

A sample of strontium-90 ($\ce{^{90}_{38}Sr}$) has an activity of 500 decays per second. If the decay constant of strontium-90 is 2.44 x 10⁻² year⁻¹, how many strontium-90 atoms are present in the sample?

Activity is defined as: $A = \lambda N$

We need to convert the decay constant to s⁻¹:

$\lambda = 2.44 \times 10^{-2} \text{ year}^{-1} \times \frac{1 \text{ year}}{3.154 \times 10^7 \text{ s}} = 7.74 \times 10^{-10} \text{ s}^{-1}$

$N = \frac{A}{\lambda} = \frac{500 \text{ s}^{-1}}{7.74 \times 10^{-10} \text{ s}^{-1}} = 6.46 \times 10^{11} \text{ atoms}$

## Challenge Problem: Mixture of Isotopes

A sample contains two radioactive isotopes: X with a half-life of 5 days and Y with a half-life of 15 days. Initially, the sample contains twice as many atoms of X as of Y. After 30 days, what is the ratio of the number of atoms of X to the number of atoms of Y?

Let $N_Y(0) = N$. Then $N_X(0) = 2N$.

$N_X(30) = 2N \left(\frac{1}{2}\right)^{\frac{30}{5}} = 2N \left(\frac{1}{2}\right)^6 = \frac{2N}{64} = \frac{N}{32}$

$N_Y(30) = N \left(\frac{1}{2}\right)^{\frac{30}{15}} = N \left(\frac{1}{2}\right)^2 = \frac{N}{4}$

$\frac{N_X(30)}{N_Y(30)} = \frac{N/32}{N/4} = \frac{4}{32} = \frac{1}{8}$

The ratio of X to Y after 30 days is 1:8.

## Conclusion

Understanding half-life is crucial for applications in various fields, from dating archaeological artifacts to medical treatments using radioisotopes. By grasping the underlying principles and practicing calculations, we can unlock the secrets of radioactive decay and its profound implications.

## References
