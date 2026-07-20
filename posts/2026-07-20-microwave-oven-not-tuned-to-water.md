---
title: Why a microwave oven is not tuned to water
date: 2026-07-20
author: Peter Johnston
tags: chemical physics, dielectrics, water, electromagnetism, relaxation
description: A microwave oven heats liquid water through dielectric relaxation, not a narrow resonance. A traceable single-Debye calculation separates the dielectric-loss-factor peak from attenuation, quantifies a pure-water baseline, and shows why the same idealized channel is weak in ice.
post-type: understanding
question: How does Debye relaxation turn an oscillating electric field into heat in liquid water, and what does the model predict for dielectric loss and penetration depth at microwave frequencies?
experiment: microwave-debye-relaxation
---

A widely repeated explanation of the microwave oven says that
[oven_frequency_ghz]{.metric} GHz is “the resonant frequency of water.” The
model used here for the dominant microwave response of bulk liquid
water—Debye relaxation—contains no resonance at all. Its dielectric loss factor
peaks at [water_dielectric_loss_peak_frequency_ghz]{.metric} GHz, not
[oven_frequency_ghz]{.metric} GHz, but even that comparison needs care: a
maximum of $\varepsilon''$ is not automatically a maximum of absorbed power or
wave attenuation.[@debye; @Ellison2007]

The explanatory question for this note is: **how does Debye relaxation turn an
oscillating electric field into heat, and what does the model actually predict
for dielectric loss and penetration depth?** The route runs from a collective
time constant, through the complex permittivity it implies, to the loss tangent
and plane-wave penetration depth, and finally to ice, where the same idealized
channel becomes extremely weak.

## A dipole in a crowd

A water molecule carries a permanent electric dipole moment. In a static field,
thermal motion keeps the dipoles mostly randomized, but a slight average
alignment survives. This **orientation polarization** is what makes liquid
water's static relative permittivity so large: the value selected here is
$\varepsilon_s =$ [water_static_relative_permittivity]{.metric} at
[water_temperature_c]{.metric} °C.[@EisenbergKauzmann1969; @atkins2010physical]

The dynamics live in one question: if the field is suddenly switched off, how
fast does that collective alignment decay? Debye represented the relaxation as
a single exponential,

$$
P(t) = P(0)e^{-t/\tau}.
$$

The dominant liquid-water dielectric process is a collective relaxation of the
orientational polarization, coupled to rearrangement of the hydrogen-bond
network; $\tau$ should not be read as the literal turn time of one isolated
molecule. The selected value at [water_temperature_c]{.metric} °C is
[water_relaxation_time_ps]{.metric} ps.[@EisenbergKauzmann1969; @Kutus2021]

An exponential decay is the signature of an overdamped process. A resonance—an
underdamped response with a natural frequency—would ring while it decayed. For
bulk liquid water at [oven_frequency_ghz]{.metric} GHz, the modeled response is
instead a broad classical relaxation. A photon at that frequency carries
[photon_energy_microev]{.metric} $\mu$eV, while $k_BT$ at
[room_temperature_k]{.metric} K is [thermal_energy_mev]{.metric} meV: the
photon energy is lower by a factor of
[thermal_to_photon_energy_ratio]{.metric}. That energy comparison locates the
response in the classical regime; the observed dielectric spectrum, rather
than the comparison alone, is what distinguishes a broad relaxation from a
narrow molecular line.[@Ellison2007]

## From a decay time to a dispersion curve

Take fields proportional to $e^{-i\omega t}$. With that convention, passive
loss has positive imaginary permittivity,
$\hat\varepsilon=\varepsilon'+i\varepsilon''$, and the one-sided response of
the exponential is

$$
\hat{\varepsilon}(\omega)=\varepsilon_\infty+
\frac{\varepsilon_s-\varepsilon_\infty}{1-i\omega\tau}.
$$

Separating real and imaginary parts gives

$$
\varepsilon'(\omega)=\varepsilon_\infty+
\frac{\varepsilon_s-\varepsilon_\infty}{1+\omega^2\tau^2},
\qquad
\varepsilon''(\omega)=
\frac{(\varepsilon_s-\varepsilon_\infty)\omega\tau}
{1+\omega^2\tau^2}.
$$

$\varepsilon'$ is the in-phase response associated with refraction and energy
storage. $\varepsilon''$ is the quadrature component responsible for net work,
with time-averaged volumetric dissipation

$$
\langle p\rangle=\tfrac12\varepsilon_0\omega\varepsilon''|E|^2.
$$

The two parts are one causal response viewed in quadrature, the same structure
explored at optical frequencies in [refraction is absorption you cannot
see](/posts/2026-07-13-refraction-is-absorption-you-cant-see.html).[@Jackson1999]

The one-pole model uses
$\varepsilon_\infty=$ [water_high_frequency_relative_permittivity]{.metric} as
an effective background for processes faster than the dominant relaxation. It
is not the literal infinite-frequency or optical permittivity: reference models
resolve additional faster relaxations and resonances.[@Ellison2007]

The dielectric loss factor $\varepsilon''$ has a single maximum at
$\omega\tau=1$,

$$
f_{\varepsilon'',\mathrm{peak}}=\frac{1}{2\pi\tau}.
$$

For the selected relaxation time, that is
[water_dielectric_loss_peak_frequency_ghz]{.metric} GHz. This is specifically
the **Debye loss-factor peak**. It is not an absorption or attenuation maximum:
$\langle p\rangle$ contains the additional factor $\omega$, while propagation
also depends on $\varepsilon'$ and the frequency-dependent wave number. The
[high_evaluation_frequency_ghz]{.metric} GHz single-Debye extrapolation below
has a smaller $\varepsilon''$ than the peak but a still shorter penetration
depth.

Nor does the loss-factor peak explain the oven frequency. The 2.4–2.5 GHz band,
centered at [oven_frequency_ghz]{.metric} GHz, is internationally designated for
industrial, scientific, and medical applications. In ITU Region 2, 902–928 MHz,
centered at [industrial_frequency_mhz]{.metric} MHz, is designated as well.
Those allocations establish where heating equipment may operate; they do not
identify a molecular resonance.[@ITUIsmBands]

## Putting numbers in

For a homogeneous, nonmagnetic medium and a plane wave, write

$$
k=\frac{\omega}{c}\sqrt{\varepsilon'+i\varepsilon''},\qquad
\alpha=\operatorname{Im}k,\qquad
D_p=\frac{1}{2\alpha}.
$$

The field amplitude decays as $e^{-\alpha z}$, so $D_p$ is the distance over
which transmitted power falls to $1/e$ relative to its value just inside the
material. The complete [standard-library
calculation](/research/microwave-debye-relaxation/calculate.py) validates the
declared inputs and writes canonical JSON. Code 1 shows only its numerical core.

```python
omega_tau = 2 * math.pi * frequency_hz * relaxation_time_s
epsilon = epsilon_infinity + (epsilon_static - epsilon_infinity) / (1 - 1j * omega_tau)
wave_index = cmath.sqrt(epsilon)
alpha = (2 * math.pi * frequency_hz / speed_of_light) * wave_index.imag
power_penetration_depth_m = 1 / (2 * alpha)
```

**Code 1.** Core of the single-Debye evaluation using the declared
$e^{-i\omega t}$ convention. The complete program adds input validation,
canonical output, independent consistency checks, and non-writing `--check`
mode.

Table 1 is the generated publication projection for liquid water. Its final row
is explicitly a one-pole extrapolation, included to expose the difference
between a loss-factor peak and attenuation rather than to claim high-frequency
accuracy.

| $f$ | $\varepsilon'$ | $\varepsilon''$ | $\tan\delta$ | $D_p$ |
| --- | --- | --- | --- | --- |
| [water_0915_frequency_ghz]{.metric} GHz | [water_0915_relative_permittivity_real]{.metric} | [water_0915_relative_permittivity_loss]{.metric} | [water_0915_loss_tangent]{.metric} | [water_0915_penetration_depth_cm]{.metric} cm |
| [oven_frequency_ghz]{.metric} GHz | [water_245_relative_permittivity_real]{.metric} | [water_245_relative_permittivity_loss]{.metric} | [water_245_loss_tangent]{.metric} | [water_245_penetration_depth_cm]{.metric} cm |
| [water_dielectric_loss_peak_frequency_ghz]{.metric} GHz | [water_dielectric_loss_peak_relative_permittivity_real]{.metric} | [water_dielectric_loss_peak_relative_permittivity_loss]{.metric} | [water_dielectric_loss_peak_loss_tangent]{.metric} | [water_dielectric_loss_peak_penetration_depth_cm]{.metric} cm |
| [high_evaluation_frequency_ghz]{.metric} GHz | [water_60_relative_permittivity_real]{.metric} | [water_60_relative_permittivity_loss]{.metric} | [water_60_loss_tangent]{.metric} | [water_60_penetration_depth_cm]{.metric} cm |

**Table 1.** Single-Debye relative permittivity, loss tangent, and $1/e$ power
penetration depth for liquid water at [water_temperature_c]{.metric} °C.

At [oven_frequency_ghz]{.metric} GHz, the model gives
$\tan\delta=$ [water_245_loss_tangent]{.metric}; the corresponding total
dielectric loss angle, $\arctan(\varepsilon''/\varepsilon')$, is
[water_oven_loss_angle_deg]{.metric}°. Moving up to the
$\varepsilon''$ peak makes the modeled penetration depth only
[water_dielectric_loss_peak_penetration_depth_mm]{.metric} mm, and moving to
[high_evaluation_frequency_ghz]{.metric} GHz makes it shorter still. Maximizing
$\varepsilon''$ is therefore not the same engineering objective as depositing
energy through a volume.

At [oven_frequency_ghz]{.metric} GHz, this homogeneous pure-water model gives a
power depth of [water_245_penetration_depth_cm]{.metric} cm; at
[industrial_frequency_mhz]{.metric} MHz it gives
[water_0915_penetration_depth_cm]{.metric} cm. These are **not** penetration
depths for a particular food. Salt, fat, bound water, temperature, geometry,
interfaces, and the cavity field all change the result, and measured depths in
foods can be much shorter. The direction of the comparison does survive in
practice: [industrial_frequency_mhz]{.metric} MHz generally penetrates foods
more deeply than [oven_frequency_ghz]{.metric} GHz and is used in large-scale
processing.[@Tang2015Microwave]

## The ice test

The model makes a sharp phase comparison, but it needs temperature-consistent
inputs. For polycrystalline ice at [ice_temperature_c]{.metric} °C, a measured
relaxation frequency of [ice_relaxation_frequency_khz]{.metric} kHz corresponds
to $\tau=$ [ice_relaxation_time_s]{.metric} s, about
[ice_to_water_relaxation_orders]{.metric} orders of magnitude slower than the
selected liquid-water process.[@Bittelli2004]

Table 2 runs the same calculation for both phases at
[oven_frequency_ghz]{.metric} GHz. The approximate ice values
$\varepsilon_s=$ [ice_static_relative_permittivity]{.metric} and
$\varepsilon_\infty=$ [ice_high_frequency_relative_permittivity]{.metric} are
representative inputs to this idealized comparison, not a complete microwave
model for frozen food.[@EisenbergKauzmann1969]

| Phase | $\varepsilon'$ | $\varepsilon''$ | $\tan\delta$ | $D_p$ |
| --- | --- | --- | --- | --- |
| Liquid water | [water_245_relative_permittivity_real]{.metric} | [water_245_relative_permittivity_loss]{.metric} | [water_245_loss_tangent]{.metric} | [water_245_penetration_depth_cm]{.metric} cm |
| Ice | [ice_245_relative_permittivity_real]{.metric} | [ice_245_relative_permittivity_loss]{.metric} | [ice_245_loss_tangent]{.metric} | [ice_245_penetration_depth_m]{.metric} m |

**Table 2.** Liquid water at [water_temperature_c]{.metric} °C and idealized
ice at [ice_temperature_c]{.metric} °C evaluated at
[oven_frequency_ghz]{.metric} GHz with the same single-Debye equations.

For ice, $\omega\tau=$ [ice_245_omega_tau]{.metric}. The slow orientational
increment therefore contributes negligibly at the oven frequency; faster
polarization still supplies $\varepsilon'\approx$
[ice_245_relative_permittivity_real]{.metric}, while the modeled loss is tiny.
Real frozen food is not pure ice, however. It contains solutes, interfaces, and
unfrozen or newly thawed water, so energy deposition changes sharply across a
thawing portion. Already-thawed regions can heat preferentially and produce
thermal runaway while other regions remain frozen.[@Akkari2006]

Reduced-power defrost modes lower the time-averaged input. Conventional ovens
commonly do that by cycling the magnetron, leaving off periods in which heat can
redistribute; the strategy mitigates the contrast but does not guarantee
uniform thawing.[@USDA2024Microwave; @Akkari2006]

## Where the model stops

The single-relaxation-time model earns its place by being solvable, but its
boundary should be drawn plainly. It does not explain microscopically why the
selected liquid-water time is [water_relaxation_time_ps]{.metric} ps; that value
enters from measurement. Real water has several relaxation components, so
$\varepsilon_\infty=$ [water_high_frequency_relative_permittivity]{.metric} is
only an effective one-pole background and the
[high_evaluation_frequency_ghz]{.metric} GHz row is an extrapolation.[@Ellison2007]

The parameters vary strongly with temperature. Ionic conduction adds a term
$\sigma/(\omega\varepsilon_0)$ in salty material. Food adds bound water, fats,
pores, interfaces, and spatially varying composition. A kitchen oven adds
reflection at the surface, standing-wave cavity modes, finite geometry, and
thermal transport. The ice calculation omits impurities and liquid inclusions,
which can dominate the loss of real frozen material.

Within that boundary, the model answers the opening mechanism question:
microwave heating of liquid water comes from work done against a lagging,
collective polarization. It is a broad relaxation, not a narrow resonance at
the oven frequency. What the model does **not** do is predict the temperature
field in dinner.

## Reproducibility

The reviewed experiment bundle contains the [declared
inputs](/research/microwave-debye-relaxation/inputs.json), [complete
calculation](/research/microwave-debye-relaxation/calculate.py), [canonical
results](/research/microwave-debye-relaxation/results.json), [metrics
generator](/research/microwave-debye-relaxation/generate-metrics.mjs),
[publication projection](/research/microwave-debye-relaxation/metrics.json),
[environment record](/research/microwave-debye-relaxation/environment.md), and
[reviewed public-file
manifest](/research/microwave-debye-relaxation/PUBLIC_FILES.txt). Code 2 checks
the complete chain.

```sh
python3 research/microwave-debye-relaxation/calculate.py --check
node research/microwave-debye-relaxation/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
stack test
stack exec site rebuild
node scripts/verify-site.mjs
```

**Code 2.** Recalculate the canonical result in non-writing check mode, verify
the typed projection and source fingerprints, test and rebuild the site, and
inspect the generated links and failure markers.

The calculation uses only the Python standard library, with no random inputs,
downloads, services, or credentials. In the documented environment it is
end-to-end reproducible: declared inputs regenerate canonical results and the
typed publication projection. The post's generated values resolve from that
projection rather than from copied output. This establishes their chain of
custody, not the correctness of the physical model or its interpretation. If a
reader sees a better parameter set, a missing loss channel, or an overextended
inference, that is exactly where this account should be corrected.

## References
