---
title: A citation, a slot, and the line nobody plots
date: 2026-06-18
tags: science, nonlinear-optics
---

A 2024 paper in *Nature Communications* from Andrei Faraon's group at Caltech — ["Dynamic light manipulation via silicon-organic slot metasurfaces"](https://doi.org/10.1038/s41467-024-45544-0) — cites a piece of work I did during my PhD with Wenwei Jin. Getting cited a decade later is a pleasure. As it turns out the citation runs deeper than the authors probably realized, and chasing down *why* is what makes the one claim they hang on our work worth examining.

## What they built

Their device is a tunable metasurface that modulates a free-space beam. They etch silicon into a periodic array of nanobars, leave ~100 nm slots between them, and fill those slots with an organic electro-optic (OEO) polymer — a proprietary material, HLD, from NLM Photonics. Light couples into a *slot mode* confined in the gaps, and because the doped silicon doubles as an electrode, a small voltage produces a large field right where the polymer sits. The Pockels effect shifts the resonance, and the reflected intensity is modulated.

It is a nice idea — the slot does double duty, concentrating the optical field in the OEO material *and* letting the electrodes sit close together for a strong field per volt. They report an in-device electro-optic coefficient of $r_{33}$ = 45.7 pm/V and tuning at modest voltages. Then, in the discussion, they cite us:

> *"Barrier layer protection has the potential to increase the nonlinear coefficient $r_{33}$ by 4–5 times, reducing the tuning voltage down to CMOS-level."*

The "barrier layer protection" is our 2014 paper on a benzocyclobutene (BCB) layer that suppresses leakage current during electric-field poling. The implication is that their 45.7 is low, and that our technique is the lever to fix it.

## The citation runs deeper than they knew

Before I say anything about that claim, an admission that cuts against me: I am not a neutral reader of this material. HLD isn't a stranger to my work — my work is built into it.

Pull the HLD paper (Xu et al., the Diels-Alder crosslinkable binary molecular glasses) and read the device-fabrication section. It uses a benzocyclobutene charge-injection barrier layer, citing our 2014 paper as the method. On poling uncertainty, the authors state that "standard error in $r_{33}$ and poling efficiency were calculated as in reference 5" — reference 5 being, again, our paper. Our structure-function study is in the bibliography too. So when the Caltech group cites our barrier-layer work to point at headroom in HLD, they are pointing at a material our barrier layer helped build and our statistics helped characterize. The citation is more earned than flattering — which is exactly why I want to get the rest of it right.

## The gap is real — and it's a field, not a fudge

So is 45.7 pm/V "low"? Yes. And the honest way to see it is to stop quoting endpoint numbers — their 45.7, HLD's headline "300" — and plot the line between them.

NLM publishes that line. Their data is $r_{33}$ against poling field with a regression through it that climbs about 2.3 pm/V for every V/µm of poling field. Two things fall out of it. At the ~100 V/µm they applied, the line predicts roughly 230 pm/V. And their measured 45.7 sits where that same line crosses only about **20 V/µm**. In other words the device is poling as though it were given a fifth of the field it was nominally given, and recovering that field would lift the coefficient about fivefold — almost exactly the "4–5×" the paper claims.

I want to be clear about that, because it would be cheap to wave the gap away as scatter: it isn't noise. The headroom is real, it is quantified, and it is consistent with the paper's own number. What the line also tells you is the *kind* of gap it is — a poling-field gap. The slot isn't delivering the field to the molecules. Which turns the entire question into a single one: can that field be recovered, and is our barrier layer the way to do it?

## Even the lever may not fit — or fix it

Two problems sit in the way of reaching for our BCB work as that lever, and they stack.

**Mechanism.** BCB does one specific thing: it suppresses bulk charge-injection and leakage current through a film during poling, so the applied field isn't bled off before the chromophores align. But in a 100 nm slot, bulk leakage is probably not the culprit. The paper's *own* reference 41 — on birefringence, dimensionality, and surface influences in organic hybrid electro-optic materials — points where the real limiter likely lives: in a gap this small, the chromophores must order against an enormous surface-to-volume ratio, and *that*, not leakage, is the plausible reason the effective field collapses to ~20 V/µm. A barrier layer does not fix an interface-ordering problem.

**Fabrication.** Even granting that leakage matters, BCB as we built it is a planar film spun between a flat electrode and a micron-thick EO layer — a vertical stack. Their slot is a 100 nm lateral gap between doped-silicon rails. Reproducing a charge-injection barrier in *that* geometry is not a drop-in; it is an unsolved fabrication problem.

```tikzpicture
\begin{tikzpicture}[font=\small, >=stealth, scale=1]
% ---- left: wafer / parallel-plate device ----
\begin{scope}[shift={(0,0)}]
  \fill[gray!35] (0,0) rectangle (4,0.5);          % ITO/glass
  \fill[orange!25] (0,0.5) rectangle (4,0.75);      % BCB
  \fill[yellow!35] (0,0.75) rectangle (4,2.05);     % EO film 1-2 um
  \fill[gray!55] (0,2.05) rectangle (4,2.4);        % gold
  \draw (0,0) rectangle (4,2.4);
  \node[align=center] at (2,0.25) {ITO / glass};
  \node at (2,0.62) {\scriptsize BCB barrier};
  \node[align=center] at (2,1.4) {EO film\\ \scriptsize 1--2 $\mu$m};
  \node at (2,2.22) {\scriptsize gold};
  \draw[->,very thick,blue!60!black] (4.45,2.0) -- (4.45,0.6) node[midway,right]{$E_{\text{pole}}$};
  \node[align=center] at (2,-0.6) {\textbf{Where BCB works}\\[-2pt]\scriptsize planar barrier, vertical field};
\end{scope}
% ---- right: slot device ----
\begin{scope}[shift={(7,0)}]
  \fill[gray!35] (0,0) rectangle (4,0.5);            % substrate
  \fill[blue!12] (0,0.5) rectangle (4,2.4);          % OEO fill
  \fill[gray!55] (0.4,0.5) rectangle (1.4,2.0);      % doped-Si rail / electrode
  \fill[gray!55] (2.6,0.5) rectangle (3.6,2.0);      % doped-Si rail / electrode
  \draw (0,0) rectangle (4,2.4);
  \node at (2,0.25) {Si substrate};
  \node[rotate=90] at (0.9,1.25) {\scriptsize doped Si};
  \node[rotate=90] at (3.1,1.25) {\scriptsize doped Si};
  \node[blue!50!black] at (2,2.2) {\scriptsize OEO};
  \draw[<->] (1.4,1.75) -- (2.6,1.75);
  \node[above] at (2,1.78) {\scriptsize $\sim$100 nm};
  \draw[->,very thick,blue!60!black] (1.45,1.05) -- (2.55,1.05) node[midway,below]{$E_{\text{pole}}$};
  \node[align=center] at (2,-0.6) {\textbf{Where they need it}\\[-2pt]\scriptsize lateral field, 100 nm slot};
\end{scope}
\end{tikzpicture}
```

So "4–5×, to CMOS voltages" is a sound *target* — the line says the headroom is genuinely there. But the lever the paper reaches for has to clear both bars, and it may clear neither: it likely doesn't fit the geometry, and by the paper's own citations it may not address what's actually limiting the poling.

## The part I'm proud of

Here is what lets me say any of this with confidence: the gap is legible at all because the poling was characterized as a *relationship* and published — not collapsed into a hero number. Read 45.7 against NLM's curve and it stops being a disappointment and becomes a data point at low effective field, sitting right where the line says it should. That diagnosis is only possible because somebody plotted the line.

Our own barrier-layer paper held to that standard. The poling analysis ran through the weighted least-squares treatment from *Numerical Recipes*, under three different weighting schemes, specifically to prove the answer didn't depend on the choice — and it didn't. Every figure carried 95% confidence bands. Every discarded device was disclosed, with its reason, the same criteria applied across every architecture. The HLD paper computed its own errors by that method — ours. The rigor is in the literature. What gets lost is the line: by the time a coefficient reaches a spec sheet it is "up to 300," and by the time it reaches a citation it is "4–5× short" — the endpoints quoted, the curve between them left unplotted.

So this isn't a complaint about being cited — it's an invitation. The headroom in their device is real; I'll concede the 4–5× without argument. Whether our barrier layer is the lever to claim it is a different question, and the paper's own references hint the answer is no — the slot's limiter looks like interface and dimensionality, not the bulk leakage BCB was built to stop. If you want to know what these materials actually do, don't quote the endpoints. Plot the line. Read the supporting information — the HLD paper's, and [ours](https://doi.org/10.1063/1.4884829) — and look at the regression, not the record. That line is the thing that makes any single number mean something, and it is the thing almost nobody plots.

<small>The cited work: W. Jin, P. V. Johnston, D. L. Elder, et al., "Benzocyclobutene barrier layer for suppressing conductance in nonlinear optical devices during electric field poling," <em>Appl. Phys. Lett.</em> 104, 243304 (2014). The citing paper: T. Zheng et al., <em>Nat. Commun.</em> 15, 1557 (2024). HLD poling data: NLM Photonics product literature; H. Xu et al., <em>Chem. Mater.</em> 32, 1408 (2020).</small>
