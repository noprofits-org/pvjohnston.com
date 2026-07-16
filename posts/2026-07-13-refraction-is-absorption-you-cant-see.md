---
title: "Refraction is absorption you can't see"
date: 2026-07-13
author: Peter Johnston
tags: optics, photonics, chemical physics, dispersion, causality, refractive index
description: A material that absorbed no light at any frequency would have a refractive index of exactly 1 — no lenses, no prisms, no rainbows. Refraction is not the opposite of absorption; it is a causal side effect of it, and the Kramers–Kronig relations say exactly how much.
---

Here is a claim that sounds wrong. A perfectly transparent material — one that
absorbs no light at any frequency, from radio to gamma — would have a refractive
index of exactly 1. It would bend no light, focus nothing, split no rainbow. Glass
would be as optically inert as vacuum. We tend to think of transparency and
absorption as opposites: a good lens is prized for *not* absorbing, a dye for
absorbing hard. But the refractive index that makes the lens a lens is not the
reward for avoiding absorption. It is the shadow that absorption throws onto every
other frequency, and if a material truly absorbed nothing anywhere, it would refract
nothing either. **Refraction is absorption you can't see** — the absorption happening
at colors your light isn't.

## Two halves of one complex number

Start with what a material does to light, written honestly. When an oscillating
field pushes on the charges in a medium, the response has two parts that are always
present together: the charges lag the field a little (a phase shift, which slows the
wave and shows up as the ordinary **refractive index** $n$) and they drain a little
energy from it (absorption). The clean way to carry both is a single complex number.
The refractive index is complex,

$$
\tilde{n}(\omega) = n(\omega) + i\,\kappa(\omega),
$$

where the real part $n$ sets the phase velocity $c/n$ and the imaginary part
$\kappa$ — the **extinction coefficient** — sets how fast the wave dies, related to
the absorption coefficient you actually measure by $\alpha = 2\omega\kappa/c$. Same
information lives in the complex dielectric function $\varepsilon = \varepsilon_1 +
i\varepsilon_2$, or the complex susceptibility $\chi$; the
[molar-absorptivity post](/posts/2026-07-03-molar-absorptivity-is-a-rate-constant.html)
was measuring one slice of exactly this object. The point is that "refraction" and
"absorption" are not two phenomena. They are the real and imaginary parts of one
function of frequency, $\tilde{n}(\omega)$.

And the two parts are not free to be chosen independently. That is the whole story.

## Causality does the forbidding

Why should the real and imaginary parts be tied together? Because of the single most
boring fact in physics: an effect cannot precede its cause. The polarization of the
medium at time $t$ can depend on the field *now* and the field in the *past*, but not
on the field in the future. The material has no way to know what the light is about
to do.

That innocuous constraint — the response function is zero for all times before the
stimulus — has a startlingly rigid consequence when you Fourier-transform it into
frequency. A function that vanishes for $t<0$ has a frequency transform that is
**analytic in the upper half of the complex-frequency plane**: smooth, pole-free,
with no surprises. And for such a function, the real and imaginary parts are locked
together by a pair of integral identities, the **[Kramers–Kronig relations](https://en.wikipedia.org/wiki/Kramers%E2%80%93Kronig_relations)**.
For the refractive index they read

$$
n(\omega) - 1 = \frac{2}{\pi}\,\mathcal{P}\!\!\int_0^\infty
\frac{\Omega\,\kappa(\Omega)}{\Omega^2 - \omega^2}\, d\Omega,
$$

with a companion relation running the other way, and $\mathcal{P}$ the Cauchy
principal value that steps carefully around the pole at $\Omega = \omega$. Rewrite
the kernel in terms of the measured absorption coefficient and it becomes even
starker:

$$
n(\omega) - 1 = \frac{c}{\pi}\,\mathcal{P}\!\!\int_0^\infty
\frac{\alpha(\Omega)}{\Omega^2 - \omega^2}\, d\Omega.
$$

Read that as an equation, not a formula. The left side is the refractive index at
one color $\omega$. The right side is an integral of the absorption over *every*
color $\Omega$. The index at green is a weighted sum of how strongly the material
absorbs at red, at blue, at ultraviolet, at X-ray — everywhere. The principal value
snips out the single point $\Omega = \omega$, so the absorption exactly *at* green
contributes nothing to the index at green. That snip is a formality if green sits
inside an absorption band, where the immediate neighbours dominate the integral — a
case we will come back to. But put green in a transparency window, with the nearest
absorption edge far off in frequency, and the statement is as blunt as it sounds: the
wave is bent by the absorption that isn't there at its own color. This is not a
modeling assumption or a fit to data; it is a theorem, and its premises are thin —
causality, plus linear response, the medium answering in proportion to the field,
which is what weak fields buy you. John Toll made the logic airtight in
[a 1956 paper](https://doi.org/10.1103/PhysRev.104.1760) whose title is the whole
idea: *Causality and the Dispersion Relation: Logical Foundations*.

## Turn the absorption off and the index goes to 1

Now the opening claim falls out in one line. Set $\alpha(\Omega) = 0$ for all
$\Omega$ — a material transparent at every frequency — and the integrand is
identically zero, so $n(\omega) = 1$ everywhere. Take the static limit $\omega \to 0$
and you get the sharpest form,

$$
n(0) - 1 = \frac{c}{\pi}\int_0^\infty \frac{\alpha(\Omega)}{\Omega^2}\, d\Omega,
$$

a sum whose integrand is strictly positive for any *passive* material — one that
absorbs rather than amplifies. Every absorption band anywhere in the spectrum pushes
the low-frequency index *up*, and nothing pushes it down. (A gain medium is the
instructive exception: invert a population and $\alpha$ runs negative across the
pumped band, dragging that stretch of the integral the other way.) The
refractive index of water in the visible — the reason a straw looks bent in a glass —
is a running tab of water's absorption in the infrared (its vibrations) and the
ultraviolet (its electronic transitions), integrated. Glass is transparent in the
visible precisely *because* its electronic absorption sits up in the ultraviolet; but
that same UV absorption, seen from below through this integral, is what gives glass
its $n \approx 1.5$ in the visible. The transparency and the refraction are the same
fact viewed from two frequencies. You cannot have a lens made of a material that is
transparent everywhere, because "transparent everywhere" is a synonym for "$n=1$."

## One oscillator shows the whole trick

The abstract theorem has a completely concrete avatar, and this blog already built
it. The [RLC-resonator post](/posts/2026-07-06-molecules-as-circuits-rlc-resonator.html)
modeled a chromophore as a driven, damped harmonic oscillator — a single Lorentz
line — with complex response

$$
\chi(\omega) \propto \frac{1}{\omega_0^2 - \omega^2 - i\gamma\omega}.
$$

Split it into real and imaginary parts and you get two curves off one denominator:
the imaginary part is a symmetric **Lorentzian absorption peak** centered at
$\omega_0$, and the real part is the S-shaped **dispersion curve** that runs through
zero at resonance. They are not two models glued together; they are two projections
of one complex pole, which is exactly why they satisfy Kramers–Kronig automatically.
The single oscillator is the KK relations in miniature — its dispersion curve is the
transform of its absorption peak. You can watch it happen numerically: hand a
computer only the absorption Lorentzian and let it grind out the principal-value
integral, and the dispersion curve reappears (Code 1).

```python
import numpy as np

w   = np.linspace(0.01, 6.0, 6000)          # frequency grid
w0, g = 3.0, 0.20                            # resonance, linewidth
kappa = g*w / ((w0**2 - w**2)**2 + (g*w)**2) # a Lorentzian absorption

# Kramers-Kronig: recover n-1 from kappa alone (principal-value sum)
n_minus_1 = np.zeros_like(w)
for i, wi in enumerate(w):
    d = w**2 - wi**2
    d[i] = np.inf                            # skip the pole at Omega = wi
    n_minus_1[i] = (2/np.pi) * np.trapezoid(w*kappa/d, w)

# n_minus_1 now traces the S-shaped dispersion curve — never supplied,
# only implied by the absorption band it was transformed from.
```

**Code 1.** A discrete Kramers–Kronig transform: given only a Lorentzian absorption
band `kappa`, the principal-value integral reconstructs the real refractive index
`n_minus_1`, reproducing the dispersion S-curve the [oscillator model](/posts/2026-07-06-molecules-as-circuits-rlc-resonator.html)
draws analytically — a numerical demonstration that the two curves carry the same
information.

## Why the prism works, and why it works backwards near a line

The dispersion curve also settles an old question with a twist. Away from any
absorption band, $n$ rises with frequency — blue bends more than red — which is
**normal dispersion**, the effect that spreads white light through a prism and blurs
cheap lenses into chromatic fringes. Trace it back to the integral and it means
visible light is sitting on the low-frequency skirt of glass's ultraviolet
absorption, climbing toward it. The prism splits sunlight because glass is opaque in
the UV; the color you see is set by the color you don't.

But push right *into* an absorption band and the S-curve does something the textbook
prism never does: $n$ drops as frequency rises. This is **anomalous dispersion**, and
far from being exotic it is mandatory — Kramers–Kronig forces the index to swing down
across every absorption line and recover on the far side. The measurements are old
news — Christiansen found the backward-running index in fuchsine in 1870 and Kundt
mapped it systematically over the two years after — but what they pushed optics toward
at the time was not causality; it was the oscillator models of Sellmeier and Lorentz,
which fit the curves without asking why the two halves should be linked at all. The
causal reading arrived half a century later, with Kronig in 1926 and Kramers in 1927,
both chasing X-ray dispersion. The "anomaly" is just the region where you are looking
at the absorption instead of around it — the one regime where the index at a color
really is set by the absorption at that color, and so the standing exception to this
essay's title — and the same relation governs both sides of the peak. There is even a
conservation law hiding in the integral — a
[sum rule](https://en.wikipedia.org/wiki/Kramers%E2%80%93Kronig_relations#Sum_rules)
fixing the total absorption strength across all frequencies to the number of electrons
present — so a material cannot cheat by having refraction without paying for it in
absorption somewhere on the axis.

## Back to the lens

So the transparent lens is not an escape from absorption; it is a carefully arranged
distance from it. Optical glass is engineered to move its electronic absorptions up
into the ultraviolet and its vibrational ones down into the infrared, leaving the
visible in a clear window between — but the refractive index that does the focusing
is precisely the integrated pull of those out-of-band absorptions, felt from inside
the window. The [transition dipole](/posts/2026-07-08-forbidden-and-allowed-symmetry-selection-rules.html)
that decides how strongly a material grabs a photon and the refractive index that
decides how much it bends the ones it lets pass are, through this one causal integral,
the same quantity read at two frequencies. A perfectly non-absorbing material would be
a perfectly useless one for optics: invisible, yes, but also incapable of forming an
image. Every lens you have ever looked through works because, somewhere out of sight,
it is drinking light.
