---
title: Chemical Kinetics of H₂O₂
date: 2025-01-20
tags: chemistry, mathematics
---

The decomposition of hydrogen peroxide (H₂O₂) into water and oxygen is a classic example of first-order kinetics:

$$\ce{2H2O2 -> 2H2O + O2}$$

The rate of decomposition follows first-order kinetics, which means:

$$\frac{d[H_2O_2]}{dt} = -k[H_2O_2]$$

where:
- $[H_2O_2]$ is the concentration of hydrogen peroxide in $\text{mol}\cdot\text{L}^{-1}$
- $k$ is the rate constant in $\text{s}^{-1}$
- $t$ is time in seconds

The integrated rate law gives us:

$$[H_2O_2]_t = [H_2O_2]_0 e^{-kt}$$

When we plot $\ln([H_2O_2]_t/[H_2O_2]_0)$ versus time, we get a straight line with slope $-k$:

$$\ln\left(\frac{[H_2O_2]_t}{[H_2O_2]_0}\right) = -kt$$

At room temperature ($25^\circ\text{C}$), the half-life ($t_{1/2}$) of this reaction is approximately 24 hours. We can calculate the rate constant using:

$$k = \frac{\ln(2)}{t_{1/2}} = \frac{0.693}{86400\text{ s}} = 8.02 \times 10^{-6}\text{ s}^{-1}$$

This means that in any given second, about 0.0008% of the remaining H₂O₂ molecules decompose.

The activation energy ($E_a$) for this reaction is approximately $75\text{ kJ}\cdot\text{mol}^{-1}$, which we can plug into the Arrhenius equation:

$$k = A e^{-\frac{E_a}{RT}}$$

where:
- $A$ is the pre-exponential factor
- $R$ is the gas constant ($8.314\text{ J}\cdot\text{mol}^{-1}\cdot\text{K}^{-1}$)
- $T$ is temperature in Kelvin

## Experimental Data

Here's some sample data from our H₂O₂ decomposition experiment at 25°C:

| Time (hours) | [H₂O₂] (M) | ln([H₂O₂]/[H₂O₂]₀) |
|-------------|------------|-------------------|
| 0           | 1.000     | 0.000            |
| 6           | 0.813     | -0.207           |
| 12          | 0.661     | -0.414           |
| 18          | 0.538     | -0.620           |
| 24          | 0.437     | -0.827           |
| 30          | 0.356     | -1.033           |

We can visualize this data with a plot:

```tikzpicture
\begin{axis}[
    width= 10cm,
    height=8cm,
    xlabel={Time (hours)},
    ylabel={$\ln\left(\frac{[\ce{H2O2}]_t}{[\ce{H2O2}]_0}\right)$},
    title={First-Order Kinetics of \ce{H2O2} Decomposition},
    grid=major,
    grid style={line width=.2pt, draw=gray!50},
    axis lines=left,
    xmin=0,
    xmax=32,
    ymin=-1.2,
    ymax=0.2,
    legend pos=north east,
    legend style={
        draw=none,
        fill=white,
        fill opacity=0.8
    },
    tick style={color=black},
    every axis label/.style={font=\Large},
    every tick label/.style={font=\Large},
    title style={font=\Large\bfseries},
    scaled ticks=false
]

% Plot experimental data points
\addplot[
    only marks,
    mark=*,
    mark size=2.5pt,
    color=blue
] coordinates {
    (0, 0.000)
    (6, -0.207)
    (12, -0.414)
    (18, -0.620)
    (24, -0.827)
    (30, -1.033)
};

% Plot the linear regression line
\addplot[
    thick,
    color=red,
    domain=0:32
] {-0.0344*x};

\legend{Experimental Data, Linear Fit ($k = 0.0344$ hr$^{-1}$)}
\end{axis}
```


As we can see from both the data and the plot, the relationship between ln([H₂O₂]/[H₂O₂]₀) and time is linear, confirming that this is indeed a first-order reaction.

The slope of this line gives us our rate constant $k$:

$$k = -\text{slope} = -\left(\frac{-1.033}{30\text{ hr}}\right) = 0.0344\text{ hr}^{-1}$$

Converting to SI units:
$$k = 0.0344\text{ hr}^{-1} \times \frac{1\text{ hr}}{3600\text{ s}} = 9.56 \times 10^{-6}\text{ s}^{-1}$$

This experimental value is close to our theoretical calculation from earlier!

This example shows how mathematics helps us understand and predict chemical reactions. The beauty of first-order kinetics lies in its simplicity and wide applicability across different chemical systems.

## A Note on Measurement Units

In chemistry, we often deal with various units. Here are some common ones used in kinetics:

- Concentration: $\text{mol}\cdot\text{L}^{-1}$ or $\text{M}$
- Rate constants: $\text{s}^{-1}$ (first order)
- Temperature: $\text{K}$ or $^\circ\text{C}$
- Energy: $\text{kJ}\cdot\text{mol}^{-1}$

Remember that proper unit analysis is crucial in chemical calculations!
