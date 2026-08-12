# Ensemble broadening: from one molecule's line to a bulk band

Computational demonstration for the Understanding note
`posts/2026-08-12-from-blinking-to-absorption.md`.

## Question and boundary

- Post type: understanding
- Question: How does the same electronic transition produce blinking photons
  under a microscope and a smooth absorption spectrum in a cuvette?
- Demonstration mechanism: each molecule gets a Lorentzian line (homogeneous
  width γ = 2 cm⁻¹ HWHM) centred at a frequency drawn from a Gaussian
  inhomogeneous distribution (σ = 40 cm⁻¹); averaging the per-molecule spectra
  over growing ensembles shows the discrete lines converging on the smooth
  inhomogeneously broadened band, and the measured FWHM approaching the
  analytic Gaussian limit 2√(2 ln 2)σ.
- What this experiment can establish: that independent-molecule ensemble
  averaging of a fixed microscopic cross section reproduces a smooth bulk band,
  and how fast the average converges with N.
- What it cannot establish: anything about interacting molecules (excitons,
  aggregates), strong-field effects, or the physical origin of the homogeneous
  and inhomogeneous widths — the widths are declared parameters, not derived.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible
- Archived-evidence or rerun constraints: none — standard library Python only

## Run

One command produces both the figure and the canonical results:

```sh
python3 research/from-blinking-to-absorption/src/ensemble_broadening.py
```

It writes `images/2026-08-12-from-blinking-to-absorption-ensemble.svg`
(Figure 2 of the post) and `results/summary.json` (declared parameters plus
the FWHM values measured on the generated curves). `random.seed(0)` makes both
outputs bit-reproducible; `environment.md` records the interpreter.

## Generate publication metrics

```sh
node research/from-blinking-to-absorption/generate-metrics.mjs
node research/from-blinking-to-absorption/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

The post binds this directory with `experiment: from-blinking-to-absorption`
and cites the measured linewidths as `[metric_name]{.metric}` references.

## Data and publication

No external data enters the demonstration — `sources.json` is an empty
manifest. Everything in this directory is listed in `PUBLIC_FILES.txt`;
nothing is excluded.
