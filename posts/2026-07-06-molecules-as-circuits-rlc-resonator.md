---
title: "Molecules as circuits — a chromophore as an RLC resonator"
date: 2026-07-06
author: Peter Johnston
tags: nonlinear optics, electro-optics, chromophores, hyperpolarizability, quantum interference, circuit analogy
description: "An absorption energy gap is a resonant frequency, a transition dipole is charge sloshing across a capacitor, and a linewidth is a resistance — so a dye molecule is literally a driven RLC circuit. This post makes the analogy pay its way, pinning every circuit element to a number from a real chromophore I synthesized, then shows the three places the model quietly stops describing the physics: the hyperpolarizability, the quantum interference in the wiring, and the many-body order that actually sets device performance."
og-image: /images/2026-07-06-molecules-as-circuits-rlc-resonator-hero.png
---

An electrical engineer and a dye chemist almost never share a whiteboard, and
when they do they assume they are drawing different things. They are usually
drawing the same object. An absorption **energy gap** is a resonant frequency.
A **transition dipole** is charge sloshing from one plate of a capacitor to the
other. A **linewidth** is a resistance draining the oscillation. Put those three
identifications together and an absorbing molecule stops being a metaphor for a
circuit and becomes one: a driven, damped **RLC resonator** (Figure 1).

This is more than a mnemonic. The classical **Lorentz model** of light
absorption — the one that still underwrites every refractive index and every
absorption band in a linear-optics textbook — treats a bound electron as a mass
on a spring driven by the oscillating field of light: a driven, damped harmonic
oscillator. A series RLC circuit is *exactly* that oscillator written in
electrical units, with the same second-order equation of motion and the same
resonance. The analogy is an isomorphism, not a resemblance.

<figure>
  <img src="/images/2026-07-06-molecules-as-circuits-rlc-resonator-hero.png" alt="A donor-pi-acceptor chromophore above its equivalent series RLC circuit: the oscillating field drives a resistor, inductor, and capacitor in one loop, with the pi bridge mapped to the inductor and the donor-acceptor pair mapped to the capacitor.">
</figure>

**Figure 1.** A donor–π–acceptor chromophore (top) and its equivalent series
RLC circuit (bottom). Driven by the oscillating electric field of light
$E(\omega)$, the molecule behaves as a driven, damped harmonic oscillator. The
conjugated π-bridge supplies the inductance $L$ — the inertia of the electronic
charge as it slides from donor to acceptor — while the donor and acceptor act as
the plates of a capacitor $C$ that stores the charge-transfer dipole, and the
resistance $R$ sets the absorption linewidth through dephasing and radiative
loss. The absorption band appears at the resonance $\omega_0 = 1/\sqrt{LC}$. The
two design dials of the earlier posts become circuit parameters: lengthening the
conjugated bridge raises $L$, and strengthening the donor and acceptor softens
the HOMO–LUMO gap and so raises $C$ — either one lowers $\omega_0$ and red-shifts
the color.

The [pigments post](/posts/2026-07-04-the-physics-and-chemistry-of-pigments.html)
established that an organic colorant is a conjugated π system whose HOMO–LUMO gap
sits in the visible window, and the
[push–pull post](/posts/2026-07-05-push-pull-chromophores-charge-transfer.html)
computed the two dials that set that gap: lengthen the conjugated bridge, or
strengthen a donor–acceptor pair at its ends. This post does something different.
It takes those same molecules — a family I built and measured in grad
school[@Jin2016; @Johnston2016Thesis] — and asks how far a single equivalent
circuit can carry the whole story: further than you would expect for the color,
and not nearly far enough for everything else that makes the molecules worth
making.

## 1. Color is a resonance

A series RLC circuit driven by a source $E(\omega)$ has one resonant frequency,

$$\omega_0 = \frac{1}{\sqrt{LC}},$$

at which the current amplitude peaks and the circuit absorbs power from the
drive. That resonance is the absorption band. Mapping the molecule onto the loop
takes three assignments (Figure 1). The **inductance $L$** is the *inertia of the
electronic charge* as it accelerates along the conjugated π bridge from the donor
end to the acceptor end — a longer bridge is a longer path with more inertia, a
larger $L$. The **capacitance $C$** is the donor–acceptor pair acting as two
plates that store the separated charge of the excited state; a stronger
donor and a stronger acceptor make that charge easier to separate, a larger $C$.
The **resistance $R$** is every channel that damps the oscillation — radiative
loss and, dominantly in solution, dephasing collisions with the solvent — and it
sets the width of the absorption band, not its position.

Notice what the two synthetic dials became: both of them lower $\omega_0$, one
through $L$ and one through $C$, and the model does not care which you turn. That
is the first honest caveat. A single absorption band gives you only two numbers —
its center $\omega_0$ and its width — so you cannot invert the spectrum to read
$L$ and $C$ separately. Assigning the bridge to $L$ and the end groups to $C$ is
an *interpretation*, motivated by which knob the chemist actually turns, not a
measurement. The circuit is honest about the resonance and agnostic about the
decomposition.

Held to what it can actually predict — turn a knob, watch $\omega_0$ move —
the model earns its keep against real molecules (Figure 2). The five chromophores
share the same push–pull skeleton; what changes is the bridge. Four of them keep
the full-length, ring-locked polyene bridge and cluster tightly between 762 and
788 nm in chloroform. The fifth, **JRD2**, replaces that bridge with a short
diene — barely any tube at all — and its absorption collapses to 630 nm, a
132 nm blue-shift. Shorten the inductive path, raise $\omega_0$, lose the red:
exactly the direction $\omega_0 = 1/\sqrt{LC}$ demands, and a large effect. (I am
not reproducing the structures here; they are drawn in the source
papers.[@Jin2016; @Johnston2016Thesis])

```tikzpicture
\begin{tikzpicture}
\begin{axis}[
    width=14cm, height=9cm,
    xlabel={chromophore (bridge shortens, left to right)},
    ylabel={$\lambda_{\max}$ in \ce{CHCl3} (nm)},
    symbolic x coords={YLD-124, JRD1, JRD5, KRD1, JRD2},
    xtick={YLD-124, JRD1, JRD5, KRD1, JRD2},
    ymin=600, ymax=820,
    enlarge x limits=0.22,
    grid=major,
    grid style={line width=.2pt, draw=gray!30},
    axis lines=left,
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    x tick label style={font=\normalsize},
]
    % shaded band over the four full-bridge chromophores
    \draw[fill=blue!8, draw=blue!25, line width=0.3pt]
        (axis cs:YLD-124,760) rectangle (axis cs:KRD1,792);
    \node[font=\footnotesize, text=blue!45!black, align=center, anchor=south]
        at (axis cs:JRD5,796) {full isophorone-locked CLD bridge\\762--788 nm};

    % connecting line (light) through the four-point plateau, drawn under the
    % markers to guide the eye through the walk
    \addplot[thin, gray!55, forget plot] coordinates {
        (YLD-124,786) (JRD1,788) (JRD5,778) (KRD1,762)
    };

    % the cluster of four
    \addplot[only marks, mark=*, mark size=4pt, color=blue!60!black] coordinates {
        (YLD-124,786) (JRD1,788) (JRD5,778) (KRD1,762)
    };
    % the short-diene cliff
    \addplot[only marks, mark=square*, mark size=4.5pt, color=orange!85!black] coordinates {
        (JRD2,630)
    };

    % the cliff, drawn literally as a vertical dimension line just left of JRD2:
    % the full 132 nm drop from the plateau level (762) down to JRD2 (630)
    \draw[{Stealth[length=5pt]}-{Stealth[length=5pt]}, orange!80!black, line width=0.9pt]
        ([xshift=-16pt]axis cs:JRD2,762) -- ([xshift=-16pt]axis cs:JRD2,632);
    \node[font=\small, text=orange!55!black, align=right, anchor=east]
        at ([xshift=-22pt]axis cs:JRD2,697) {short diene:\\$-132$\,nm};

    % per-point value labels
    \node[font=\footnotesize, anchor=south west] at (axis cs:YLD-124,787) {786};
    \node[font=\footnotesize, anchor=south] at (axis cs:JRD1,789)    {788};
    \node[font=\footnotesize, anchor=south] at (axis cs:JRD5,779)    {778};
    \node[font=\footnotesize, anchor=south east] at (axis cs:KRD1,762) {762};
    \node[font=\footnotesize, anchor=north east, text=orange!55!black] at (axis cs:JRD2,627) {630};

    % KRD1 thiophene nudge note
    \node[font=\footnotesize, text=black!55, anchor=north, align=center]
        at (axis cs:KRD1,757) {thiophene\\bridge};
\end{axis}
\end{tikzpicture}
```

**Figure 2.** Measured absorption maxima $\lambda_{\max}$ (chloroform) across the
real chromophore family, ordered so the conjugated bridge shortens left to right.
The four full-bridge chromophores — YLD-124, JRD1, JRD5, and KRD1 — cluster in a
narrow 762–788 nm band despite substantial changes to their donor, acceptor, and
solubilizing groups: the color is set by the bridge, not the periphery. KRD1,
whose bridge swaps one ring for a thiophene, sits slightly blue of the others.
Truncating the bridge to a short diene (JRD2) drops $\lambda_{\max}$ off a cliff
to 630 nm — the inductive-path length, the $L$ of the circuit, is the dominant
lever on where the band sits.

## 2. The wiring matters as much as the parts

Before leaving the linear circuit, note one property of circuits that has no
analogue in a simple mass-on-a-spring: the behavior depends on the **topology**, not just
the component values. The same resistor wired two different ways gives two
different answers. Molecules have this too, and for conjugated rings it is
dramatic.

Take a bare benzene ring and treat it as a two-terminal electrical element:
inject an electron at one carbon and collect it at another, and ask what fraction
transmits as a function of energy. There are two ways around the ring, two
Feynman paths, and they interfere. Contact the ring at the *para* (1,4) positions
and the two paths are equal in length and interfere constructively — the ring
conducts, and its transmission hits unity on each of benzene's molecular-orbital
resonances. Contact it at the *meta* (1,3) positions and at the midgap energy the
two paths arrive exactly out of phase and cancel: transmission drops to zero at
an energy where the isolated orbitals are perfectly happy to conduct (Figure 3).
Nothing changed but the wiring.

```tikzpicture
\begin{tikzpicture}
\begin{axis}[
    width=14cm, height=8.5cm,
    xlabel={electrode energy $E$ (units of $|\beta|$)},
    ylabel={transmission $T(E)$},
    xmin=-3, xmax=3, ymin=0, ymax=1.05,
    grid=major,
    grid style={line width=.2pt, draw=gray!30},
    axis lines=left,
    legend pos=north east,
    legend style={draw=none, fill=white, fill opacity=0.85},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
]
    \draw[gray!45, line width=0.4pt] (axis cs:-2.0,0) -- (axis cs:-2.0,1.02);
    \draw[gray!45, line width=0.4pt] (axis cs:-1.0,0) -- (axis cs:-1.0,1.02);
    \draw[gray!45, line width=0.4pt] (axis cs:1.0,0) -- (axis cs:1.0,1.02);
    \draw[gray!45, line width=0.4pt] (axis cs:2.0,0) -- (axis cs:2.0,1.02);
    
\addplot[very thick, color=blue] coordinates {(-3.0000,0.00087) (-2.9900,0.00090) (-2.9800,0.00094) (-2.9700,0.00098) (-2.9600,0.00101) (-2.9500,0.00106) (-2.9400,0.00110) (-2.9300,0.00114) (-2.9200,0.00119) (-2.9100,0.00124) (-2.9000,0.00129) (-2.8900,0.00135) (-2.8800,0.00141) (-2.8700,0.00147) (-2.8600,0.00153) (-2.8500,0.00160) (-2.8400,0.00167) (-2.8300,0.00174) (-2.8200,0.00182) (-2.8100,0.00190) (-2.8000,0.00199) (-2.7900,0.00208) (-2.7800,0.00218) (-2.7700,0.00228) (-2.7600,0.00239) (-2.7500,0.00250) (-2.7400,0.00262) (-2.7300,0.00275) (-2.7200,0.00288) (-2.7100,0.00302) (-2.7000,0.00318) (-2.6900,0.00334) (-2.6800,0.00351) (-2.6700,0.00369) (-2.6600,0.00388) (-2.6500,0.00408) (-2.6400,0.00430) (-2.6300,0.00453) (-2.6200,0.00477) (-2.6100,0.00504) (-2.6000,0.00532) (-2.5900,0.00561) (-2.5800,0.00593) (-2.5700,0.00627) (-2.5600,0.00664) (-2.5500,0.00703) (-2.5400,0.00744) (-2.5300,0.00789) (-2.5200,0.00838) (-2.5100,0.00889) (-2.5000,0.00945) (-2.4900,0.01005) (-2.4800,0.01070) (-2.4700,0.01140) (-2.4600,0.01215) (-2.4500,0.01297) (-2.4400,0.01386) (-2.4300,0.01482) (-2.4200,0.01586) (-2.4100,0.01700) (-2.4000,0.01823) (-2.3900,0.01958) (-2.3800,0.02105) (-2.3700,0.02266) (-2.3600,0.02443) (-2.3500,0.02636) (-2.3400,0.02849) (-2.3300,0.03084) (-2.3200,0.03343) (-2.3100,0.03629) (-2.3000,0.03946) (-2.2900,0.04299) (-2.2800,0.04691) (-2.2700,0.05128) (-2.2600,0.05616) (-2.2500,0.06164) (-2.2400,0.06779) (-2.2300,0.07472) (-2.2200,0.08254) (-2.2100,0.09140) (-2.2000,0.10146) (-2.1900,0.11290) (-2.1800,0.12596) (-2.1700,0.14091) (-2.1600,0.15804) (-2.1500,0.17774) (-2.1400,0.20041) (-2.1300,0.22655) (-2.1200,0.25667) (-2.1100,0.29138) (-2.1000,0.33126) (-2.0900,0.37690) (-2.0800,0.42876) (-2.0700,0.48704) (-2.0600,0.55154) (-2.0500,0.62137) (-2.0400,0.69473) (-2.0300,0.76873) (-2.0200,0.83940) (-2.0100,0.90201) (-2.0000,0.95181) (-1.9900,0.98496) (-1.9800,0.99936) (-1.9700,0.99514) (-1.9600,0.97444) (-1.9500,0.94071) (-1.9400,0.89793) (-1.9300,0.84986) (-1.9200,0.79964) (-1.9100,0.74961) (-1.9000,0.70138) (-1.8900,0.65593) (-1.8800,0.61377) (-1.8700,0.57510) (-1.8600,0.53989) (-1.8500,0.50799) (-1.8400,0.47920) (-1.8300,0.45325) (-1.8200,0.42990) (-1.8100,0.40889) (-1.8000,0.38999) (-1.7900,0.37299) (-1.7800,0.35768) (-1.7700,0.34390) (-1.7600,0.33150) (-1.7500,0.32033) (-1.7400,0.31027) (-1.7300,0.30123) (-1.7200,0.29310) (-1.7100,0.28580) (-1.7000,0.27926) (-1.6900,0.27343) (-1.6800,0.26823) (-1.6700,0.26363) (-1.6600,0.25958) (-1.6500,0.25605) (-1.6400,0.25300) (-1.6300,0.25040) (-1.6200,0.24823) (-1.6100,0.24647) (-1.6000,0.24510) (-1.5900,0.24410) (-1.5800,0.24347) (-1.5700,0.24319) (-1.5600,0.24325) (-1.5500,0.24365) (-1.5400,0.24438) (-1.5300,0.24545) (-1.5200,0.24684) (-1.5100,0.24857) (-1.5000,0.25063) (-1.4900,0.25302) (-1.4800,0.25576) (-1.4700,0.25885) (-1.4600,0.26230) (-1.4500,0.26612) (-1.4400,0.27032) (-1.4300,0.27491) (-1.4200,0.27992) (-1.4100,0.28536) (-1.4000,0.29124) (-1.3900,0.29759) (-1.3800,0.30443) (-1.3700,0.31179) (-1.3600,0.31969) (-1.3500,0.32817) (-1.3400,0.33725) (-1.3300,0.34696) (-1.3200,0.35735) (-1.3100,0.36846) (-1.3000,0.38031) (-1.2900,0.39295) (-1.2800,0.40643) (-1.2700,0.42079) (-1.2600,0.43607) (-1.2500,0.45231) (-1.2400,0.46957) (-1.2300,0.48787) (-1.2200,0.50726) (-1.2100,0.52775) (-1.2000,0.54938) (-1.1900,0.57214) (-1.1800,0.59604) (-1.1700,0.62103) (-1.1600,0.64706) (-1.1500,0.67405) (-1.1400,0.70188) (-1.1300,0.73037) (-1.1200,0.75933) (-1.1100,0.78847) (-1.1000,0.81749) (-1.0900,0.84600) (-1.0800,0.87356) (-1.0700,0.89970) (-1.0600,0.92390) (-1.0500,0.94562) (-1.0400,0.96433) (-1.0300,0.97952) (-1.0200,0.99075) (-1.0100,0.99766) (-1.0000,1.00000) (-0.9900,0.99764) (-0.9800,0.99061) (-0.9700,0.97906) (-0.9600,0.96328) (-0.9500,0.94365) (-0.9400,0.92066) (-0.9300,0.89483) (-0.9200,0.86672) (-0.9100,0.83689) (-0.9000,0.80586) (-0.8900,0.77412) (-0.8800,0.74211) (-0.8700,0.71022) (-0.8600,0.67874) (-0.8500,0.64795) (-0.8400,0.61804) (-0.8300,0.58916) (-0.8200,0.56141) (-0.8100,0.53488) (-0.8000,0.50959) (-0.7900,0.48556) (-0.7800,0.46278) (-0.7700,0.44124) (-0.7600,0.42089) (-0.7500,0.40169) (-0.7400,0.38360) (-0.7300,0.36657) (-0.7200,0.35054) (-0.7100,0.33546) (-0.7000,0.32127) (-0.6900,0.30792) (-0.6800,0.29537) (-0.6700,0.28356) (-0.6600,0.27245) (-0.6500,0.26199) (-0.6400,0.25215) (-0.6300,0.24287) (-0.6200,0.23413) (-0.6100,0.22589) (-0.6000,0.21812) (-0.5900,0.21078) (-0.5800,0.20386) (-0.5700,0.19732) (-0.5600,0.19114) (-0.5500,0.18529) (-0.5400,0.17977) (-0.5300,0.17454) (-0.5200,0.16958) (-0.5100,0.16489) (-0.5000,0.16045) (-0.4900,0.15623) (-0.4800,0.15223) (-0.4700,0.14844) (-0.4600,0.14484) (-0.4500,0.14142) (-0.4400,0.13818) (-0.4300,0.13509) (-0.4200,0.13216) (-0.4100,0.12938) (-0.4000,0.12673) (-0.3900,0.12422) (-0.3800,0.12182) (-0.3700,0.11955) (-0.3600,0.11739) (-0.3500,0.11533) (-0.3400,0.11338) (-0.3300,0.11152) (-0.3200,0.10975) (-0.3100,0.10807) (-0.3000,0.10648) (-0.2900,0.10496) (-0.2800,0.10353) (-0.2700,0.10216) (-0.2600,0.10087) (-0.2500,0.09965) (-0.2400,0.09849) (-0.2300,0.09740) (-0.2200,0.09636) (-0.2100,0.09539) (-0.2000,0.09447) (-0.1900,0.09361) (-0.1800,0.09280) (-0.1700,0.09204) (-0.1600,0.09134) (-0.1500,0.09068) (-0.1400,0.09007) (-0.1300,0.08951) (-0.1200,0.08899) (-0.1100,0.08852) (-0.1000,0.08809) (-0.0900,0.08770) (-0.0800,0.08736) (-0.0700,0.08706) (-0.0600,0.08680) (-0.0500,0.08658) (-0.0400,0.08640) (-0.0300,0.08626) (-0.0200,0.08616) (-0.0100,0.08610) (0.0000,0.08608) (0.0100,0.08610) (0.0200,0.08616) (0.0300,0.08626) (0.0400,0.08640) (0.0500,0.08658) (0.0600,0.08680) (0.0700,0.08706) (0.0800,0.08736) (0.0900,0.08770) (0.1000,0.08809) (0.1100,0.08852) (0.1200,0.08899) (0.1300,0.08951) (0.1400,0.09007) (0.1500,0.09068) (0.1600,0.09134) (0.1700,0.09204) (0.1800,0.09280) (0.1900,0.09361) (0.2000,0.09447) (0.2100,0.09539) (0.2200,0.09636) (0.2300,0.09740) (0.2400,0.09849) (0.2500,0.09965) (0.2600,0.10087) (0.2700,0.10216) (0.2800,0.10353) (0.2900,0.10496) (0.3000,0.10648) (0.3100,0.10807) (0.3200,0.10975) (0.3300,0.11152) (0.3400,0.11338) (0.3500,0.11533) (0.3600,0.11739) (0.3700,0.11955) (0.3800,0.12182) (0.3900,0.12422) (0.4000,0.12673) (0.4100,0.12938) (0.4200,0.13216) (0.4300,0.13509) (0.4400,0.13818) (0.4500,0.14142) (0.4600,0.14484) (0.4700,0.14844) (0.4800,0.15223) (0.4900,0.15623) (0.5000,0.16045) (0.5100,0.16489) (0.5200,0.16958) (0.5300,0.17454) (0.5400,0.17977) (0.5500,0.18529) (0.5600,0.19114) (0.5700,0.19732) (0.5800,0.20386) (0.5900,0.21078) (0.6000,0.21812) (0.6100,0.22589) (0.6200,0.23413) (0.6300,0.24287) (0.6400,0.25215) (0.6500,0.26199) (0.6600,0.27245) (0.6700,0.28356) (0.6800,0.29537) (0.6900,0.30792) (0.7000,0.32127) (0.7100,0.33546) (0.7200,0.35054) (0.7300,0.36657) (0.7400,0.38360) (0.7500,0.40169) (0.7600,0.42089) (0.7700,0.44124) (0.7800,0.46278) (0.7900,0.48556) (0.8000,0.50959) (0.8100,0.53488) (0.8200,0.56141) (0.8300,0.58916) (0.8400,0.61804) (0.8500,0.64795) (0.8600,0.67874) (0.8700,0.71022) (0.8800,0.74211) (0.8900,0.77412) (0.9000,0.80586) (0.9100,0.83689) (0.9200,0.86672) (0.9300,0.89483) (0.9400,0.92066) (0.9500,0.94365) (0.9600,0.96328) (0.9700,0.97906) (0.9800,0.99061) (0.9900,0.99764) (1.0000,1.00000) (1.0100,0.99766) (1.0200,0.99075) (1.0300,0.97952) (1.0400,0.96433) (1.0500,0.94562) (1.0600,0.92390) (1.0700,0.89970) (1.0800,0.87356) (1.0900,0.84600) (1.1000,0.81749) (1.1100,0.78847) (1.1200,0.75933) (1.1300,0.73037) (1.1400,0.70188) (1.1500,0.67405) (1.1600,0.64706) (1.1700,0.62103) (1.1800,0.59604) (1.1900,0.57214) (1.2000,0.54938) (1.2100,0.52775) (1.2200,0.50726) (1.2300,0.48787) (1.2400,0.46957) (1.2500,0.45231) (1.2600,0.43607) (1.2700,0.42079) (1.2800,0.40643) (1.2900,0.39295) (1.3000,0.38031) (1.3100,0.36846) (1.3200,0.35735) (1.3300,0.34696) (1.3400,0.33725) (1.3500,0.32817) (1.3600,0.31969) (1.3700,0.31179) (1.3800,0.30443) (1.3900,0.29759) (1.4000,0.29124) (1.4100,0.28536) (1.4200,0.27992) (1.4300,0.27491) (1.4400,0.27032) (1.4500,0.26612) (1.4600,0.26230) (1.4700,0.25885) (1.4800,0.25576) (1.4900,0.25302) (1.5000,0.25063) (1.5100,0.24857) (1.5200,0.24684) (1.5300,0.24545) (1.5400,0.24438) (1.5500,0.24365) (1.5600,0.24325) (1.5700,0.24319) (1.5800,0.24347) (1.5900,0.24410) (1.6000,0.24510) (1.6100,0.24647) (1.6200,0.24823) (1.6300,0.25040) (1.6400,0.25300) (1.6500,0.25605) (1.6600,0.25958) (1.6700,0.26363) (1.6800,0.26823) (1.6900,0.27343) (1.7000,0.27926) (1.7100,0.28580) (1.7200,0.29310) (1.7300,0.30123) (1.7400,0.31027) (1.7500,0.32033) (1.7600,0.33150) (1.7700,0.34390) (1.7800,0.35768) (1.7900,0.37299) (1.8000,0.38999) (1.8100,0.40889) (1.8200,0.42990) (1.8300,0.45325) (1.8400,0.47920) (1.8500,0.50799) (1.8600,0.53989) (1.8700,0.57510) (1.8800,0.61377) (1.8900,0.65593) (1.9000,0.70138) (1.9100,0.74961) (1.9200,0.79964) (1.9300,0.84986) (1.9400,0.89793) (1.9500,0.94071) (1.9600,0.97444) (1.9700,0.99514) (1.9800,0.99936) (1.9900,0.98496) (2.0000,0.95181) (2.0100,0.90201) (2.0200,0.83940) (2.0300,0.76873) (2.0400,0.69473) (2.0500,0.62137) (2.0600,0.55154) (2.0700,0.48704) (2.0800,0.42876) (2.0900,0.37690) (2.1000,0.33126) (2.1100,0.29138) (2.1200,0.25667) (2.1300,0.22655) (2.1400,0.20041) (2.1500,0.17774) (2.1600,0.15804) (2.1700,0.14091) (2.1800,0.12596) (2.1900,0.11290) (2.2000,0.10146) (2.2100,0.09140) (2.2200,0.08254) (2.2300,0.07472) (2.2400,0.06779) (2.2500,0.06164) (2.2600,0.05616) (2.2700,0.05128) (2.2800,0.04691) (2.2900,0.04299) (2.3000,0.03946) (2.3100,0.03629) (2.3200,0.03343) (2.3300,0.03084) (2.3400,0.02849) (2.3500,0.02636) (2.3600,0.02443) (2.3700,0.02266) (2.3800,0.02105) (2.3900,0.01958) (2.4000,0.01823) (2.4100,0.01700) (2.4200,0.01586) (2.4300,0.01482) (2.4400,0.01386) (2.4500,0.01297) (2.4600,0.01215) (2.4700,0.01140) (2.4800,0.01070) (2.4900,0.01005) (2.5000,0.00945) (2.5100,0.00889) (2.5200,0.00838) (2.5300,0.00789) (2.5400,0.00744) (2.5500,0.00703) (2.5600,0.00664) (2.5700,0.00627) (2.5800,0.00593) (2.5900,0.00561) (2.6000,0.00532) (2.6100,0.00504) (2.6200,0.00477) (2.6300,0.00453) (2.6400,0.00430) (2.6500,0.00408) (2.6600,0.00388) (2.6700,0.00369) (2.6800,0.00351) (2.6900,0.00334) (2.7000,0.00318) (2.7100,0.00302) (2.7200,0.00288) (2.7300,0.00275) (2.7400,0.00262) (2.7500,0.00250) (2.7600,0.00239) (2.7700,0.00228) (2.7800,0.00218) (2.7900,0.00208) (2.8000,0.00199) (2.8100,0.00190) (2.8200,0.00182) (2.8300,0.00174) (2.8400,0.00167) (2.8500,0.00160) (2.8600,0.00153) (2.8700,0.00147) (2.8800,0.00141) (2.8900,0.00135) (2.9000,0.00129) (2.9100,0.00124) (2.9200,0.00119) (2.9300,0.00114) (2.9400,0.00110) (2.9500,0.00106) (2.9600,0.00101) (2.9700,0.00098) (2.9800,0.00094) (2.9900,0.00090) (3.0000,0.00087)};
\addplot[very thick, color=orange!85!black] coordinates {(-3.0000,0.00195) (-2.9900,0.00201) (-2.9800,0.00208) (-2.9700,0.00215) (-2.9600,0.00222) (-2.9500,0.00230) (-2.9400,0.00237) (-2.9300,0.00245) (-2.9200,0.00254) (-2.9100,0.00263) (-2.9000,0.00272) (-2.8900,0.00281) (-2.8800,0.00291) (-2.8700,0.00302) (-2.8600,0.00313) (-2.8500,0.00324) (-2.8400,0.00336) (-2.8300,0.00348) (-2.8200,0.00361) (-2.8100,0.00375) (-2.8000,0.00389) (-2.7900,0.00404) (-2.7800,0.00420) (-2.7700,0.00437) (-2.7600,0.00454) (-2.7500,0.00472) (-2.7400,0.00491) (-2.7300,0.00511) (-2.7200,0.00532) (-2.7100,0.00555) (-2.7000,0.00578) (-2.6900,0.00603) (-2.6800,0.00629) (-2.6700,0.00656) (-2.6600,0.00685) (-2.6500,0.00715) (-2.6400,0.00748) (-2.6300,0.00782) (-2.6200,0.00818) (-2.6100,0.00856) (-2.6000,0.00897) (-2.5900,0.00940) (-2.5800,0.00985) (-2.5700,0.01034) (-2.5600,0.01085) (-2.5500,0.01140) (-2.5400,0.01198) (-2.5300,0.01260) (-2.5200,0.01327) (-2.5100,0.01397) (-2.5000,0.01473) (-2.4900,0.01554) (-2.4800,0.01641) (-2.4700,0.01734) (-2.4600,0.01833) (-2.4500,0.01940) (-2.4400,0.02056) (-2.4300,0.02180) (-2.4200,0.02314) (-2.4100,0.02459) (-2.4000,0.02615) (-2.3900,0.02785) (-2.3800,0.02969) (-2.3700,0.03168) (-2.3600,0.03386) (-2.3500,0.03623) (-2.3400,0.03881) (-2.3300,0.04164) (-2.3200,0.04474) (-2.3100,0.04814) (-2.3000,0.05188) (-2.2900,0.05601) (-2.2800,0.06056) (-2.2700,0.06561) (-2.2600,0.07121) (-2.2500,0.07743) (-2.2400,0.08437) (-2.2300,0.09213) (-2.2200,0.10083) (-2.2100,0.11059) (-2.2000,0.12160) (-2.1900,0.13403) (-2.1800,0.14810) (-2.1700,0.16408) (-2.1600,0.18226) (-2.1500,0.20298) (-2.1400,0.22665) (-2.1300,0.25372) (-2.1200,0.28467) (-2.1100,0.32004) (-2.1000,0.36038) (-2.0900,0.40619) (-2.0800,0.45784) (-2.0700,0.51549) (-2.0600,0.57883) (-2.0500,0.64695) (-2.0400,0.71805) (-2.0300,0.78927) (-2.0200,0.85670) (-2.0100,0.91570) (-2.0000,0.96154) (-1.9900,0.99034) (-1.9800,1.00000) (-1.9700,0.99061) (-1.9600,0.96437) (-1.9500,0.92490) (-1.9400,0.87639) (-1.9300,0.82279) (-1.9200,0.76743) (-1.9100,0.71275) (-1.9000,0.66041) (-1.8900,0.61138) (-1.8800,0.56616) (-1.8700,0.52487) (-1.8600,0.48744) (-1.8500,0.45366) (-1.8400,0.42325) (-1.8300,0.39591) (-1.8200,0.37135) (-1.8100,0.34927) (-1.8000,0.32940) (-1.7900,0.31150) (-1.7800,0.29536) (-1.7700,0.28079) (-1.7600,0.26760) (-1.7500,0.25566) (-1.7400,0.24483) (-1.7300,0.23499) (-1.7200,0.22605) (-1.7100,0.21791) (-1.7000,0.21049) (-1.6900,0.20373) (-1.6800,0.19757) (-1.6700,0.19195) (-1.6600,0.18683) (-1.6500,0.18216) (-1.6400,0.17790) (-1.6300,0.17404) (-1.6200,0.17053) (-1.6100,0.16735) (-1.6000,0.16448) (-1.5900,0.16190) (-1.5800,0.15959) (-1.5700,0.15754) (-1.5600,0.15573) (-1.5500,0.15416) (-1.5400,0.15280) (-1.5300,0.15166) (-1.5200,0.15073) (-1.5100,0.15000) (-1.5000,0.14946) (-1.4900,0.14911) (-1.4800,0.14895) (-1.4700,0.14898) (-1.4600,0.14919) (-1.4500,0.14958) (-1.4400,0.15017) (-1.4300,0.15094) (-1.4200,0.15190) (-1.4100,0.15305) (-1.4000,0.15441) (-1.3900,0.15596) (-1.3800,0.15773) (-1.3700,0.15971) (-1.3600,0.16192) (-1.3500,0.16436) (-1.3400,0.16705) (-1.3300,0.16999) (-1.3200,0.17319) (-1.3100,0.17668) (-1.3000,0.18046) (-1.2900,0.18454) (-1.2800,0.18895) (-1.2700,0.19369) (-1.2600,0.19878) (-1.2500,0.20423) (-1.2400,0.21005) (-1.2300,0.21626) (-1.2200,0.22284) (-1.2100,0.22981) (-1.2000,0.23715) (-1.1900,0.24482) (-1.1800,0.25278) (-1.1700,0.26096) (-1.1600,0.26923) (-1.1500,0.27744) (-1.1400,0.28535) (-1.1300,0.29263) (-1.1200,0.29883) (-1.1100,0.30334) (-1.1000,0.30531) (-1.0900,0.30362) (-1.0800,0.29681) (-1.0700,0.28304) (-1.0600,0.26015) (-1.0500,0.22602) (-1.0400,0.17958) (-1.0300,0.12285) (-1.0200,0.06384) (-1.0100,0.01754) (-1.0000,0.00000) (-0.9900,0.01654) (-0.9800,0.05709) (-0.9700,0.10510) (-0.9600,0.14796) (-0.9500,0.18007) (-0.9400,0.20072) (-0.9300,0.21145) (-0.9200,0.21444) (-0.9100,0.21178) (-0.9000,0.20522) (-0.8900,0.19612) (-0.8800,0.18552) (-0.8700,0.17415) (-0.8600,0.16255) (-0.8500,0.15110) (-0.8400,0.14001) (-0.8300,0.12946) (-0.8200,0.11952) (-0.8100,0.11024) (-0.8000,0.10162) (-0.7900,0.09365) (-0.7800,0.08631) (-0.7700,0.07956) (-0.7600,0.07336) (-0.7500,0.06768) (-0.7400,0.06247) (-0.7300,0.05769) (-0.7200,0.05332) (-0.7100,0.04931) (-0.7000,0.04564) (-0.6900,0.04226) (-0.6800,0.03917) (-0.6700,0.03632) (-0.6600,0.03370) (-0.6500,0.03129) (-0.6400,0.02907) (-0.6300,0.02703) (-0.6200,0.02514) (-0.6100,0.02339) (-0.6000,0.02178) (-0.5900,0.02029) (-0.5800,0.01890) (-0.5700,0.01762) (-0.5600,0.01643) (-0.5500,0.01532) (-0.5400,0.01430) (-0.5300,0.01334) (-0.5200,0.01245) (-0.5100,0.01162) (-0.5000,0.01085) (-0.4900,0.01012) (-0.4800,0.00945) (-0.4700,0.00882) (-0.4600,0.00823) (-0.4500,0.00768) (-0.4400,0.00716) (-0.4300,0.00668) (-0.4200,0.00622) (-0.4100,0.00580) (-0.4000,0.00540) (-0.3900,0.00503) (-0.3800,0.00467) (-0.3700,0.00434) (-0.3600,0.00403) (-0.3500,0.00374) (-0.3400,0.00347) (-0.3300,0.00321) (-0.3200,0.00297) (-0.3100,0.00274) (-0.3000,0.00253) (-0.2900,0.00233) (-0.2800,0.00214) (-0.2700,0.00196) (-0.2600,0.00179) (-0.2500,0.00164) (-0.2400,0.00149) (-0.2300,0.00135) (-0.2200,0.00122) (-0.2100,0.00110) (-0.2000,0.00099) (-0.1900,0.00089) (-0.1800,0.00079) (-0.1700,0.00070) (-0.1600,0.00061) (-0.1500,0.00053) (-0.1400,0.00046) (-0.1300,0.00040) (-0.1200,0.00034) (-0.1100,0.00028) (-0.1000,0.00023) (-0.0900,0.00019) (-0.0800,0.00015) (-0.0700,0.00011) (-0.0600,0.00008) (-0.0500,0.00006) (-0.0400,0.00004) (-0.0300,0.00002) (-0.0200,0.00001) (-0.0100,0.00000) (0.0000,0.00000) (0.0100,0.00000) (0.0200,0.00001) (0.0300,0.00002) (0.0400,0.00004) (0.0500,0.00006) (0.0600,0.00008) (0.0700,0.00011) (0.0800,0.00015) (0.0900,0.00019) (0.1000,0.00023) (0.1100,0.00028) (0.1200,0.00034) (0.1300,0.00040) (0.1400,0.00046) (0.1500,0.00053) (0.1600,0.00061) (0.1700,0.00070) (0.1800,0.00079) (0.1900,0.00089) (0.2000,0.00099) (0.2100,0.00110) (0.2200,0.00122) (0.2300,0.00135) (0.2400,0.00149) (0.2500,0.00164) (0.2600,0.00179) (0.2700,0.00196) (0.2800,0.00214) (0.2900,0.00233) (0.3000,0.00253) (0.3100,0.00274) (0.3200,0.00297) (0.3300,0.00321) (0.3400,0.00347) (0.3500,0.00374) (0.3600,0.00403) (0.3700,0.00434) (0.3800,0.00467) (0.3900,0.00503) (0.4000,0.00540) (0.4100,0.00580) (0.4200,0.00622) (0.4300,0.00668) (0.4400,0.00716) (0.4500,0.00768) (0.4600,0.00823) (0.4700,0.00882) (0.4800,0.00945) (0.4900,0.01012) (0.5000,0.01085) (0.5100,0.01162) (0.5200,0.01245) (0.5300,0.01334) (0.5400,0.01430) (0.5500,0.01532) (0.5600,0.01643) (0.5700,0.01762) (0.5800,0.01890) (0.5900,0.02029) (0.6000,0.02178) (0.6100,0.02339) (0.6200,0.02514) (0.6300,0.02703) (0.6400,0.02907) (0.6500,0.03129) (0.6600,0.03370) (0.6700,0.03632) (0.6800,0.03917) (0.6900,0.04226) (0.7000,0.04564) (0.7100,0.04931) (0.7200,0.05332) (0.7300,0.05769) (0.7400,0.06247) (0.7500,0.06768) (0.7600,0.07336) (0.7700,0.07956) (0.7800,0.08631) (0.7900,0.09365) (0.8000,0.10162) (0.8100,0.11024) (0.8200,0.11952) (0.8300,0.12946) (0.8400,0.14001) (0.8500,0.15110) (0.8600,0.16255) (0.8700,0.17415) (0.8800,0.18552) (0.8900,0.19612) (0.9000,0.20522) (0.9100,0.21178) (0.9200,0.21444) (0.9300,0.21145) (0.9400,0.20072) (0.9500,0.18007) (0.9600,0.14796) (0.9700,0.10510) (0.9800,0.05709) (0.9900,0.01654) (1.0000,0.00000) (1.0100,0.01754) (1.0200,0.06384) (1.0300,0.12285) (1.0400,0.17958) (1.0500,0.22602) (1.0600,0.26015) (1.0700,0.28304) (1.0800,0.29681) (1.0900,0.30362) (1.1000,0.30531) (1.1100,0.30334) (1.1200,0.29883) (1.1300,0.29263) (1.1400,0.28535) (1.1500,0.27744) (1.1600,0.26923) (1.1700,0.26096) (1.1800,0.25278) (1.1900,0.24482) (1.2000,0.23715) (1.2100,0.22981) (1.2200,0.22284) (1.2300,0.21626) (1.2400,0.21005) (1.2500,0.20423) (1.2600,0.19878) (1.2700,0.19369) (1.2800,0.18895) (1.2900,0.18454) (1.3000,0.18046) (1.3100,0.17668) (1.3200,0.17319) (1.3300,0.16999) (1.3400,0.16705) (1.3500,0.16436) (1.3600,0.16192) (1.3700,0.15971) (1.3800,0.15773) (1.3900,0.15596) (1.4000,0.15441) (1.4100,0.15305) (1.4200,0.15190) (1.4300,0.15094) (1.4400,0.15017) (1.4500,0.14958) (1.4600,0.14919) (1.4700,0.14898) (1.4800,0.14895) (1.4900,0.14911) (1.5000,0.14946) (1.5100,0.15000) (1.5200,0.15073) (1.5300,0.15166) (1.5400,0.15280) (1.5500,0.15416) (1.5600,0.15573) (1.5700,0.15754) (1.5800,0.15959) (1.5900,0.16190) (1.6000,0.16448) (1.6100,0.16735) (1.6200,0.17053) (1.6300,0.17404) (1.6400,0.17790) (1.6500,0.18216) (1.6600,0.18683) (1.6700,0.19195) (1.6800,0.19757) (1.6900,0.20373) (1.7000,0.21049) (1.7100,0.21791) (1.7200,0.22605) (1.7300,0.23499) (1.7400,0.24483) (1.7500,0.25566) (1.7600,0.26760) (1.7700,0.28079) (1.7800,0.29536) (1.7900,0.31150) (1.8000,0.32940) (1.8100,0.34927) (1.8200,0.37135) (1.8300,0.39591) (1.8400,0.42325) (1.8500,0.45366) (1.8600,0.48744) (1.8700,0.52487) (1.8800,0.56616) (1.8900,0.61138) (1.9000,0.66041) (1.9100,0.71275) (1.9200,0.76743) (1.9300,0.82279) (1.9400,0.87639) (1.9500,0.92490) (1.9600,0.96437) (1.9700,0.99061) (1.9800,1.00000) (1.9900,0.99034) (2.0000,0.96154) (2.0100,0.91570) (2.0200,0.85670) (2.0300,0.78927) (2.0400,0.71805) (2.0500,0.64695) (2.0600,0.57883) (2.0700,0.51549) (2.0800,0.45784) (2.0900,0.40619) (2.1000,0.36038) (2.1100,0.32004) (2.1200,0.28467) (2.1300,0.25372) (2.1400,0.22665) (2.1500,0.20298) (2.1600,0.18226) (2.1700,0.16408) (2.1800,0.14810) (2.1900,0.13403) (2.2000,0.12160) (2.2100,0.11059) (2.2200,0.10083) (2.2300,0.09213) (2.2400,0.08437) (2.2500,0.07743) (2.2600,0.07121) (2.2700,0.06561) (2.2800,0.06056) (2.2900,0.05601) (2.3000,0.05188) (2.3100,0.04814) (2.3200,0.04474) (2.3300,0.04164) (2.3400,0.03881) (2.3500,0.03623) (2.3600,0.03386) (2.3700,0.03168) (2.3800,0.02969) (2.3900,0.02785) (2.4000,0.02615) (2.4100,0.02459) (2.4200,0.02314) (2.4300,0.02180) (2.4400,0.02056) (2.4500,0.01940) (2.4600,0.01833) (2.4700,0.01734) (2.4800,0.01641) (2.4900,0.01554) (2.5000,0.01473) (2.5100,0.01397) (2.5200,0.01327) (2.5300,0.01260) (2.5400,0.01198) (2.5500,0.01140) (2.5600,0.01085) (2.5700,0.01034) (2.5800,0.00985) (2.5900,0.00940) (2.6000,0.00897) (2.6100,0.00856) (2.6200,0.00818) (2.6300,0.00782) (2.6400,0.00748) (2.6500,0.00715) (2.6600,0.00685) (2.6700,0.00656) (2.6800,0.00629) (2.6900,0.00603) (2.7000,0.00578) (2.7100,0.00555) (2.7200,0.00532) (2.7300,0.00511) (2.7400,0.00491) (2.7500,0.00472) (2.7600,0.00454) (2.7700,0.00437) (2.7800,0.00420) (2.7900,0.00404) (2.8000,0.00389) (2.8100,0.00375) (2.8200,0.00361) (2.8300,0.00348) (2.8400,0.00336) (2.8500,0.00324) (2.8600,0.00313) (2.8700,0.00302) (2.8800,0.00291) (2.8900,0.00281) (2.9000,0.00272) (2.9100,0.00263) (2.9200,0.00254) (2.9300,0.00245) (2.9400,0.00237) (2.9500,0.00230) (2.9600,0.00222) (2.9700,0.00215) (2.9800,0.00208) (2.9900,0.00201) (3.0000,0.00195)};
\legend{{\emph{para}\ (1,4)}, {\emph{meta}\ (1,3)}}
\node[font=\small, text=orange!70!black, anchor=north, align=center]
    at (axis cs:0,0.93) {destructive\\interference};
\draw[-{Stealth[length=5pt]}, orange!70!black] (axis cs:0,0.78) -- (axis cs:0,0.06);
\node[font=\small, text=blue!70!black, anchor=south west] at (axis cs:0.15,0.55) {ring conducts};
\end{axis}
\end{tikzpicture}
```

**Figure 3.** Landauer transmission $T(E)$ through a benzene ring contacted at
two carbons, at the Hückel level with wide-band leads. Grey verticals mark
benzene's MO energies ($\pm 1$, $\pm 2\,|\beta|$ — here $\beta$ is the Hückel
resonance integral, not the hyperpolarizability of §3); on resonance transmission
reaches unity. Para (1,4) contacts interfere constructively — the ring conducts
through midgap; meta (1,3) contacts cancel exactly at $E = 0$, a
quantum-interference antiresonance. Same molecule, same orbital energies; only
the contact topology differs — which is why push–pull chromophores are always
built through a linearly conjugated (para-like) path.

This is the **molecular Wheatstone bridge**, and it is the deep reason every
working push–pull chromophore is built through a *linearly conjugated* path from
donor to acceptor. Route the conjugation through a ring the wrong way — meta
rather than para — and you install an antiresonance directly between the two
groups that are supposed to be talking. The donor pushes; the acceptor never
hears it. Keep this figure in mind; it comes back to bite a specific bridge
choice in §4.

## 3. The term the linear circuit cannot see

Everything so far is linear: one drive frequency in, the same frequency out,
amplitude proportional to the field. It explains the color. It explains none of
the reason these particular molecules exist, which is the **first
hyperpolarizability $\beta$** — the molecular origin of the Pockels effect the
[electro-optics post](/posts/2026-07-03-one-matrix-element-absorptivity-and-the-pockels-effect.html)
introduced, the property that lets a voltage steer a light beam. A linear circuit
has, by definition, no $\beta$. Its capacitor stores a charge strictly
proportional to the voltage across it. $\beta$ is what you get when that is no
longer true — when the capacitor's ability to store charge itself depends on the
voltage, a **nonlinear, voltage-tunable capacitor**, which an electrical engineer
calls a varactor. In oscillator language, $\beta$ lives in the *asymmetric,
anharmonic* part of the potential well: a spring that is stiffer in one direction
than the other. A symmetric well gives you $L$, $C$, and color; only an
asymmetric one gives you $\beta$.

The classic two-state model makes the dependence explicit. For a push–pull
molecule with a single dominant charge-transfer transition,[@OudarChemla1977]

$$\beta \;\propto\; \frac{\Delta\mu \, \mu_{ge}^{2}}{E_{ge}^{2}},$$

where $E_{ge}$ is the transition energy (the gap), $\mu_{ge}$ is the transition
dipole (how brightly the ground and excited states are coupled), and $\Delta\mu$
is the *change* in the molecule's permanent dipole on excitation — how far, and
how much, charge actually relocates. Read that formula next to the linear circuit
and the ride-along is clear: to first order the same red-shift that the RLC
attributes to a larger $LC$ product — a smaller $E_{ge}$ — also multiplies
$\beta$, because $E_{ge}$ sits *squared* in the denominator. Push the gap down and
color, brightness, and hyperpolarizability all move together: $\Delta\mu$ up,
$E_{ge}$ down, $\lambda_{\max}$ to the red, $\beta$ up, all riding one lever. But
$\beta$ is bolted *onto* the linear model as its anharmonic correction; it is not
sitting inside $\omega_0 = 1/\sqrt{LC}$ waiting to be read off. The circuit gets
you to the doorstep and no further.

## 4. Balloons, tubes, and a parasitic capacitor

Here is the picture I actually used at the bench, before any of the circuit
language. Think of the donor and acceptor as two **balloons** joined by a
**tube** — the π bridge. Light squeezes the donor balloon; electron density is
pushed down the tube toward the acceptor balloon. What you want, for a large
$\beta$, is a big change in *where the air sits* when you squeeze — and that
change is precisely $\Delta\mu$. A long, open, compliant tube lets a lot of air
move a long way. That is the whole game.

Now put an aromatic ring — a benzene — in the middle of the tube. An aromatic
ring is a **balloon that refuses to deflate**: surrendering its six-electron
aromatic sextet costs too much, so it holds onto its charge instead of passing it
along, and the conjugation stalls into alternating single and double bonds
(**bond-length alternation**). Charge that should have reached the far acceptor
gets parked in the middle. $\Delta\mu$ shrinks, and with it $\beta$. This is the
molecular reason a ring-locked polyene bridge (the "CLD" motif) beats a
thiophene-containing bridge (the "FTC" motif) for hyperpolarizability, all else
equal. And it has a clean circuit translation: **the mid-tube balloon is a
parasitic shunt capacitance**, a capacitor to ground planted partway along the
line that bleeds charge off before it ever reaches the far plate. The balloon
picture, the aromaticity argument, and the shunt capacitor are three vocabularies
for one fact.

That fact drove a real synthetic decision. The bridge in these molecules is built
around **isophorone** — a *non-aromatic*, ring-locked polyene — and not around a
benzene, on purpose. The ring is there for rigidity: locking the bridge geometry
buys thermal stability and cuts the conformational disorder that otherwise smears
out the properties. Isophorone gets that lock *without* paying the aromaticity
toll, because it never had a sextet to protect. It is a braced tube, not a
mid-tube balloon. Choosing it over benzene is the balloon model making a decision
you can hold in your hand.

And it is why you never see **naphthalene** in the bridge, which is the case that
ties this section back to Figure 3. A fused bicyclic aromatic is the worst of
every world at once: a *bigger* balloon, with more aromatic stabilization to
surrender; a *wide, two-dimensional* channel rather than a clean one-dimensional
tube; and — because a fused ring offers several routes between the attachment
points — a set of conjugation paths that includes **cross-conjugated, destructive
ones**. That last is the meta-antiresonance of Figure 3, built *inside* the
bridge instead of at the contacts. Naphthalene is exactly where the balloon model
and the interference figure meet, and they both say the same thing: don't.

The family bears the ordering out (Table 1). KRD1, whose bridge carries the
thiophene, shows the predicted penalty — its measured $\lambda_{\max}$ slips to
762 nm and its computed $\beta$ drops well below the ring-locked members, the
CLD-beats-FTC gap made quantitative. JRD2, with almost no tube left, sits at the
bottom on every column. Read the whole family as a ladder of bridge choices —
isophorone (a braced tube, no balloon) → a lone benzene (one balloon) →
naphthalene (a bigger balloon, a wide channel, and built-in destructive paths) →
a thiophene bridge (a small balloon, a measured $\beta$ penalty) → a truncated
diene (barely any tube) — and each rung is a real molecule with a real number
attached.

| chromophore | bridge | $\lambda_{\max}$ (nm) | computed $\beta$ (10⁻³⁰ esu) | poling $r_{33}/E_p$ ((nm/V)²) |
|---|---|---|---|---|
| YLD-124 | ring-locked polyene | 786 | 460 | 1.4 |
| JRD1 | ring-locked polyene | 788 | 483 | 3.1 |
| JRD5 | ring-locked polyene (carbazole) | 778 | 476 | 2.9 |
| KRD1 | thiophene | 762 | 341 | 1.4 |
| JRD2 | short diene | 630 | 88 | 0.3 |

**Table 1.** The chromophore family behind Figure 2: measured absorption maximum
(chloroform), computed static first hyperpolarizability $\beta$ (LC-BLYP, gas
phase), and the poling efficiency $r_{33}/E_p$ — the electro-optic coefficient
normalized by the applied poling field, a device-level number. The molecular
columns ($\lambda_{\max}$, $\beta$) track together and reward the ring-locked
bridge over thiophene (KRD1) and reward any bridge over none (JRD2). The device
column does *not* simply follow $\beta$: YLD-124 and JRD1 have essentially the
same molecular $\beta$ yet JRD1 poles more than twice as efficiently — the subject
of §5.[@Jin2016; @Johnston2016Thesis]

## 5. The cliff: the circuit ends at one molecule

The last column of Table 1 is where the whole picture — circuit, oscillator,
balloon, and all — walks off the edge of what a single molecule can explain. What
a device delivers is not $\beta$ but the bulk electro-optic response, and to a
good approximation[@DaltonSullivanBale2010]

$$r_{33} \;\propto\; \rho \, N \, \langle \cos^3\theta \rangle \, \beta,$$

where $N$ is the number density of chromophores, $\rho$ accounts for the local
field, and $\langle\cos^3\theta\rangle$ is the **acentric order parameter** — how
well the molecules are lined up, on average, all pointing the same way after
poling. A perfectly isotropic film has $\langle\cos^3\theta\rangle = 0$ and no
electro-optic response *no matter how large $\beta$ is*, because the molecular
nonlinearities cancel in every direction. Order, number density, local field:
these are **many-body, materials properties**. Nothing in a single-molecule
circuit — not $L$, not $C$, not the anharmonic varactor — knows they exist.

The family makes the cliff concrete. YLD-124 and JRD1 have essentially the same
molecular hyperpolarizability (Table 1), and if $\beta$ were the whole story they
would perform identically in a device. JRD1 poles more than **twice** as well.
The entire difference is order: JRD1 carries a bulky, site-isolating substituent
(a TBDPS group) that keeps neighboring chromophores from stacking antiparallel
and cancelling each other out, so more of the molecular $\beta$ survives into the
bulk. Same electronics, same color, same circuit — and a factor of two in the
device, bought entirely by a piece of the physics the circuit cannot see. The
equivalent circuit is a faithful portrait of one molecule in isolation. A working
material is a crowd, and crowds have properties no single member has.

## Where the model earns its keep, and where it stops

The circuit is worth drawing precisely because it fails so cleanly, in three
labeled places. It nails the **linear color**, because there the analogy is an
exact isomorphism — the Lorentz oscillator *is* a series RLC, and
$\omega_0 = 1/\sqrt{LC}$ tracks a real family of molecules across a 158 nm span
(Figures 1 and 2). It gestures honestly at **$\beta$**, as the anharmonic,
voltage-tunable-capacitor correction the linear loop structurally cannot contain,
and the two-state formula plus the balloon picture carry the design intuition the
rest of the way (§§3–4). And it is **blind** to the many-body order that actually
sets device performance — the $\langle\cos^3\theta\rangle$ that separates two
molecules of identical $\beta$ by a factor of two (§5). A good physical model is
not one that explains everything; it is one that tells you exactly where its own
edges are.

Those edges are the itinerary for what comes next. This post kept everything to a
single molecule and a linear response, and every number in it was either measured
or already in hand. The next post picks up the $\beta$ story where the two-state
formula leaves off, recomputing the real family from the wavefunction up — does a
full excited-state calculation reproduce the CLD-beats-thiophene ordering, and
does $\omega_0$ track $L$ and $C$ the way the circuit promised as the bridge
grows? That is a knob-sweep for another machine.

*The circuit analogy here is a teaching device, exact for linear absorption and
deliberately approximate beyond it; the measured and computed numbers are from
the cited work, and any errors in translating them into circuit language are
mine.*

## References
