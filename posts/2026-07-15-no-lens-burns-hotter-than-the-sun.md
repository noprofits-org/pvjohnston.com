---
title: "No lens burns hotter than the sun: étendue and the second law"
date: 2026-07-15
author: Peter Johnston
tags: optics, photonics, thermodynamics, etendue, concentration, nonimaging optics, radiometry
description: Give me a perfect lens of any size and I still cannot heat a target past about 5800 K with sunlight. The limit is not engineering, and it is not diffraction — it is Liouville's theorem wearing an optics costume, and it hands back the solar constant as a receipt.
---

Here is a bet I will take every time. Hand someone a flawless lens — no aberration, no
absorption, any diameter they like — point it at the sun, and ask them to melt a
tungsten pin at the focus. Tungsten melts at 3695 K, so they will manage it. Now ask
them to push the pin to 8000 K. They cannot. Not with a bigger lens, not with a stack
of lenses, not with a mirror the size of a county. No arrangement of transparent glass
and shiny metal will take a sunlit target above roughly 5800 K — the temperature of the
sun's own surface — and the reason has nothing to do with the quality of the optics. It
is a conservation law, and it is the same one that governs a gas in a box.

## The quantity that refuses to shrink

The relevant bookkeeping is **étendue** (French for "extent"), the measure of how
much *spread* a bundle of light has — spread in space and spread in angle, together.
For a beam crossing an area $dA$ into a cone of solid angle $d\Omega$ at angle
$\theta$ from the surface normal, in a medium of refractive index $n$,

$$
G = n^2 \!\int\!\!\!\int \cos\theta \; dA \; d\Omega .
$$

The $\cos\theta$ is the usual projected-area factor; the $n^2$ will matter later, and
will matter in an unexpected direction. The essential claim is this: in any lossless
optical system built from lenses, mirrors, and prisms, **étendue is conserved**. You
can trade its two halves against each other freely — squeeze the beam down in area
and it fans out in angle, exactly in compensation — but you cannot reduce the
product. Real systems, with scattering and imperfect surfaces, only ever make it
worse. Étendue is a ratchet.

This is not an empirical rule of thumb about lenses. It is **Liouville's theorem**,
imported. Geometric optics is a Hamiltonian system: rays obey equations of motion in
which the transverse position $x$ and the optical direction cosine
$p_x = n\sin\theta_x$ are canonically conjugate — position and momentum, in everything
but name. Liouville says a Hamiltonian flow preserves phase-space volume, so the volume
a ray bundle occupies in $(x, y, p_x, p_y)$ is invariant along the system. That volume
*is* the étendue. A lens is a canonical transformation: it can shear the bundle, rotate
it, stretch one axis and compress the other — but not shrink it, for the same reason a
piston cannot compress a gas's phase-space volume without dissipating something.

The immediately useful corollary is the **radiance theorem**. Radiance $L$ is the
power per unit *projected* area per unit solid angle (W·m⁻²·sr⁻¹) — so the power
carried by a bundle is $L$ times the bundle's étendue *without* the $n^2$, and
dividing power by the $G$ defined above gives the **basic radiance** $L/n^2$. Power is
conserved in a lossless system and $G$ is conserved, so $L/n^2$ is conserved too, and
in air it is just $L$. No passive optic makes light brighter. A lens gathers more
power onto a smaller spot — but only by making the cone steeper, and the radiance at
the focus is exactly the radiance at the source. You cannot form an image of the sun
that is brighter, per unit solid angle, than the sun.

## The number falls out

Now the punchline is arithmetic. The sun's surface is a decent blackbody at
$T_\odot \approx 5778$ K, so it emits $\sigma T_\odot^4 \approx 6.3 \times 10^7$
W·m⁻² — 63 megawatts per square metre. From Earth, the sun subtends a half-angle of
$\theta_\odot \approx 0.2666° = 4.65\times10^{-3}$ rad. Sunlight arrives here at the
same radiance it left with, but crammed into that tiny cone, so the flux we receive
is diluted by $\sin^2\theta_\odot$:

$$
E_\oplus = \sigma T_\odot^4 \sin^2\theta_\odot .
$$

Evaluate it and you get about 1368 W·m⁻² — the solar constant, returned as a receipt
(Code 1). The solar constant is not an independent fact about the sky. It is the
sun's surface emittance, geometrically watered down by the fact that the sun is small
in our field of view.

A concentrator's job is to undo that dilution: take light arriving over an aperture
$A_\text{in}$ within a cone $\theta_\odot$ and deliver it to a receiver $A_\text{out}$
within a wider cone $\theta_\text{out}$. Conserve étendue and the **concentration
ratio** is capped at

$$
C = \frac{A_\text{in}}{A_\text{out}} \le \frac{n^2 \sin^2\theta_\text{out}}{\sin^2\theta_\odot} .
$$

The receiver cannot accept light from more than a hemisphere, so
$\sin\theta_\text{out} \le 1$, and in air $n = 1$:

$$
C_\text{max} = \frac{1}{\sin^2\theta_\odot} \approx 46{,}000 .
$$

Multiply: $46{,}000 \times 1368\ \text{W·m}^{-2} = 6.3 \times 10^7$ W·m⁻². The best
possible concentrator delivers, at its focus, precisely the flux at the sun's
surface — not one watt more. A receiver in equilibrium with that flux radiates back
at $\sigma T^4$ and settles at $T = T_\odot$. That is the whole argument. The
geometry hands you the second law: had the optics been able to beat the étendue
limit, you could have heated a target above 5778 K using nothing but light from a
5778 K body, then run a heat engine between the two and extracted work from a
spontaneous cold-to-hot flow. **Clausius forbids it, and so does Liouville.** Two
arguments from unrelated starting points converging on the same number is how you
know the constraint is real and not an artifact of the model.

```python
import numpy as np

sigma  = 5.670374e-8      # Stefan-Boltzmann, W m^-2 K^-4
T_sun  = 5778.0           # K, effective photospheric temperature
th_sun = np.deg2rad(0.2666)  # solar angular radius

M_sun = sigma * T_sun**4              # 6.32e7 W/m^2 leaving the photosphere
E_top = M_sun * np.sin(th_sun)**2     # 1368 W/m^2 -> the solar constant
C_max = 1 / np.sin(th_sun)**2         # 46200 -> ideal 3D concentration

assert np.isclose(C_max * E_top, M_sun)   # concentration only undoes dilution
```

**Code 1.** Four lines of radiometry: the solar constant is the sun's surface
emittance diluted by $\sin^2\theta_\odot$, the ideal concentration limit is the
reciprocal of that same factor, and their product returns the photospheric flux
exactly — the assertion is the second law, written as an identity.

## Where the real hardware sits

Knowing the ceiling tells you how badly ordinary optics underperforms, and why. A
parabolic dish — an *imaging* concentrator, which forms a picture of the sun at its
focus — tops out around a factor of four below the ideal, near a 45° rim angle $\phi$.
Two effects squeeze it from opposite sides. Open the dish toward the hemisphere the
étendue limit wants filled and obliquity punishes you twice over: the rim zone's edge
rays arrive at grazing incidence, where a flat absorber barely counts them, and the
image that zone forms is smeared across the focal plane by $1/\cos\phi$, forcing a
receiver bigger than the sun's image needs to be — together, a $\cos^2\phi$ penalty
that runs to zero as $\phi \to 90°$. Close the dish down instead and the smear goes
away, but the focused cone narrows to a sliver of the angular acceptance the receiver
was willing to give you, wasting most of the étendue budget — a $\sin^2\phi$ penalty.
The product $\sin^2\phi\,\cos^2\phi$ peaks in between at 45°, at a quarter of the
ideal. The image-forming requirement is what sets that trap: nobody asked for a picture
of the sun, only for its energy in one place.

Dropping that requirement is the founding move of **nonimaging optics**. A
[compound parabolic concentrator](https://en.wikipedia.org/wiki/Compound_parabolic_concentrator)
— the Winston cone — makes no image at all; it is a light funnel whose walls are
shaped so that, in the two-dimensional trough case, *every* ray entering within the
acceptance angle reaches the exit, hitting the étendue limit exactly. The rotationally
symmetric 3D cone is very slightly worse — it turns back a small fraction of skew
rays that arrive inside the acceptance angle — but it still lands within a few percent
of the ideal, close enough that the limit is a design target rather than a distant
asymptote. Run the trick backwards and you have a horn antenna: étendue does not care
which way the photons travel. The two-dimensional case, meanwhile, explains the trough
collectors in the desert. A trough concentrates in one axis only, so its limit is
$1/\sin\theta_\odot \approx 215$, not 46,000 — the price of not tracking the sun in
two axes is two orders of magnitude of ceiling, paid up front.

The étendue budget is quietly everywhere else in photonics, too. It is why you cannot
couple a broad LED efficiently into a single-mode fibre no matter how clever the lens
— the fibre's étendue (core area times numerical aperture squared) is a fixed, small
box, and the LED's emission does not fit in it. It is why an interferometer's
Jacquinot throughput advantage over a slit spectrometer is quoted in étendue rather
than in area.

## Two loopholes, one of which is real

The limit invites cheating, and the attempts are instructive. **Immersion** looks
promising: put the absorber in a high-index medium and the $n^2$ in the étendue
integral hands you a factor of $n^2 \approx 3.1$ more concentration for sapphire
($n \approx 1.76$). It works — and it buys you nothing thermally, because the blackbody
radiance *inside* a medium of index $n$ is itself $n^2$ times larger. The extra flux
you deliver is exactly the extra flux the absorber now re-radiates, and the equilibrium
temperature does not move. The loophole closes itself, using the same refractive index
that [refraction turns out to be a causal side effect of](/posts/2026-07-13-refraction-is-absorption-you-cant-see.html):
the $n$ that bends the light and the $n$ that sets the density of optical states are
the same $n$, and the thermodynamics knows it.

The real escape is to stop using a thermal source. A laser has absurd radiance not
because it is hot but because it is *not in equilibrium* — its light occupies a
single mode, the smallest étendue a beam can have, and its brightness temperature can
run to $10^9$ K while the gain medium sits at room temperature. Nothing is violated;
the second law constrains what you can do with 5778 K blackbody radiation, and a
laser simply is not that. Which is the honest statement of the whole result: the
ceiling is not on lenses. It is on sunlight. So the flawless lens of any diameter
still cannot take the tungsten pin past 5800 K — but not because the glass is bad.
The bundle of rays you started with already had all the spread it was ever going to
have, and no amount of glass will talk it out of it.
