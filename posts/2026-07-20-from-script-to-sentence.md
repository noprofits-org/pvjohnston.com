---
title: "From script to sentence: a traceable Brewster-angle calculation"
date: 2026-07-20
author: Peter Johnston
tags: reproducibility, Hakyll, Pandoc, optics, scientific computing
description: A tiny Fresnel calculation shows how this site now carries computed values from versioned inputs into prose without mistaking traceability for correctness.
post-type: understanding
question: How can a computed physical result travel from a script into a published sentence with an auditable chain of custody?
experiment: traceable-brewster-angle
---

A computed result usually enters an article through copy and paste. The program
prints a value, an author transfers it into Markdown, and the connection between
the two becomes a matter of memory and review. This note asks a narrower
question: **how can a physical calculation travel from a script into a
published sentence with an auditable chain of custody?**

The route here follows one deliberately small optics demonstration from declared
inputs, through canonical output and a typed metrics projection, into this page.
The calculation is simple enough to check independently. That keeps the
infrastructure visible instead of asking a complicated experiment to vouch for
it.

## The publication problem is a broken chain

A saved script does not establish where a published number came from. The
script may have changed after the run; the article may quote an older output;
formatting may hide a copied digit; or the prose may contain a number that no
artifact records at all. These are different failures, but they share one
structural weakness: the sentence does not identify its computational source.

This site's Hakyll build already turns Markdown, citations, equations, and TikZ
into HTML. The traceable-metrics addition gives computed prose one more compiler
input. Table 1 follows the complete path used by this note.

| Stage | Artifact | Responsibility |
| --- | --- | --- |
| Declared model | `inputs.json` | Records chosen indices, sweep bounds, and tolerances |
| Calculation | `calculate.py` | Regenerates the canonical optical output |
| Canonical output | `results.json` | Preserves the richer result before publication formatting |
| Projection | `generate-metrics.mjs` | Derives named, typed, formatted publication values |
| Build input | `metrics.json` | Supplies the only values resolved by metric references |
| Post source | `[name]{.metric}` | Names a result without copying its display value |
| Rendered page | `metric-value` span | Retains the metric name beside the formatted text |

**Table 1.** The one-way path from a declared computational input to rendered
prose. The normal site build begins at the committed projection; a separate
verification step checks the cheaper upstream layers.

This extends the build described in [Anatomy of a Hakyll
site](/posts/2026-06-24-anatomy-of-a-hakyll-site.html). It does not make the
article executable Markdown. The experiment still owns its code and results;
the post receives only a small, validated projection.

## A small optical calculation

Consider a plane wave reaching an ideal boundary from a medium with refractive
index $n_1=$ [incident_refractive_index]{.metric} into one with
$n_2=$ [transmitted_refractive_index]{.metric}. These are chosen model inputs,
not a measurement of a named glass. Snell's law gives the transmitted angle,

$$
\theta_t=\sin^{-1}\!\left(\frac{n_1}{n_2}\sin\theta_i\right).
$$

For s- and p-polarized light, the Fresnel amplitude reflection coefficients are

$$
r_s=\frac{n_1\cos\theta_i-n_2\cos\theta_t}
{n_1\cos\theta_i+n_2\cos\theta_t},
\qquad
r_p=\frac{n_2\cos\theta_i-n_1\cos\theta_t}
{n_2\cos\theta_i+n_1\cos\theta_t}.
$$

The corresponding transmission amplitudes and power fractions are

$$
t_s=\frac{2n_1\cos\theta_i}{n_1\cos\theta_i+n_2\cos\theta_t},
\qquad
t_p=\frac{2n_1\cos\theta_i}{n_2\cos\theta_i+n_1\cos\theta_t},
$$

$$
R_{s,p}=r_{s,p}^2,
\qquad
T_{s,p}=\frac{n_2\cos\theta_t}{n_1\cos\theta_i}t_{s,p}^2.
$$

For this lossless interface, each polarization must satisfy $R+T=1$.
P-polarized reflection vanishes at the Brewster angle,

$$
\theta_B=\tan^{-1}\!\left(\frac{n_2}{n_1}\right),
$$

while s-polarized reflection remains nonzero.[@Jackson1999] This is a useful
demonstration because the closed-form angle predicts where a separately
evaluated numerical sweep should place its minimum, and energy conservation supplies a
second check. It also connects to the longer account of interfaces in
[Refraction is absorption you cannot
see](/posts/2026-07-13-refraction-is-absorption-you-cant-see.html).

The script evaluates the analytic angle, then samples the Fresnel equations from
[sweep_start_angle_deg]{.metric}° through [sweep_stop_angle_deg]{.metric}° in
[sweep_step_angle_deg]{.metric}° steps. Table 2 contains its publication
projection. Every displayed result cell is a metric reference, not a copied
result literal.

| Quantity | Published value |
| --- | --- |
| Refractive-index ratio $n_2/n_1$ | [index_ratio]{.metric} |
| Analytic Brewster angle | [analytic_brewster_angle_deg]{.metric}° |
| Angle of the grid minimum | [grid_minimum_angle_deg]{.metric}° |
| Grid-to-analytic angle difference | [grid_angle_error_deg]{.metric}° |
| Normal-incidence reflectance | [normal_incidence_reflectance]{.metric} |
| P reflectance at the analytic angle | [analytic_p_reflectance]{.metric} |
| S reflectance at the analytic angle | [analytic_s_reflectance]{.metric} |
| Unpolarized reflectance at the analytic angle | [analytic_unpolarized_reflectance]{.metric} |
| Minimum grid P reflectance | [grid_minimum_p_reflectance]{.metric} |
| Largest sampled $|R+T-1|$ | [maximum_energy_balance_error]{.metric} |
| Angles in the sweep | [sweep_sample_count]{.metric} |

**Table 2.** Analytic, numerical, and conservation quantities produced by the
same canonical optical output and formatted by the Hakyll compiler.

The three declared checks are data too. The analytic p-reflectance
[analytic_p_reflectance]{.metric} is compared with a limit of
[analytic_p_reflectance_tolerance]{.metric}, producing
[analytic_null_within_tolerance]{.metric}. The grid error
[grid_angle_error_deg]{.metric}° is compared with
[grid_angle_tolerance_deg]{.metric}°, producing
[grid_angle_within_tolerance]{.metric}. The largest energy residual
[maximum_energy_balance_error]{.metric} is compared with
[energy_balance_tolerance]{.metric}, producing
[energy_balance_within_tolerance]{.metric}. A boolean does not prove the model;
it records whether one named condition held under a visible, committed limit.

## The projection separates value from presentation

`results.json` retains the calculation's native floating-point values. The
metrics generator chooses which of those values the article may quote and gives
each one a type, description, optional unit, and deterministic format. Integers
and booleans render directly. Decimal, percentage, scientific, and raw number
formats are computed by the compiler from the stored numeric value; there is no
second display string that can quietly disagree.

One field has a different role: `generated_at` records when a projection is
written. A fresh non-check write reads the wall clock. Check mode instead reuses
the committed timestamp while recomputing the metric values, formats, and
fingerprints, so its exact byte comparison tests the content without pretending
the original write time can be regenerated.

The Markdown source for the analytic angle contains the literal token
`[analytic_brewster_angle_deg]{.metric}`. Pandoc parses that token as a span.
Hakyll loads this experiment's `metrics.json`, checks the schema and experiment
name, resolves the key, and emits a `metric-value` span carrying the same name in
`data-metric`. A missing file, malformed metric, unsupported format, or unknown
key stops the build.

That is stronger than copy and paste, but deliberately narrower than literate
programming. The post cannot reach into arbitrary runtime state. It can only ask
for a named value from one committed projection.

## Failure is part of the interface

The useful behavior is not only the successful substitution. Four failure
paths define the contract:

1. If an input or calculation change alters the expected canonical result,
   `calculate.py --check` fails until `results.json` is regenerated.
2. If any fingerprinted input changes byte-for-byte—even when an equivalent
   edit leaves the result unchanged—`verify-metrics.mjs` reports the mismatch.
3. If canonical results change without regenerating `metrics.json`, the metrics
   generator's `--check` mode fails.
4. If the post misspells a metric name, Hakyll exits with the post, experiment,
   and unknown key in the error.

The system cannot reliably decide whether an ordinary numeral in English is an
experimental result, a date, a parameter, or part of an equation. It therefore
does not make hand-typed results impossible. The compiler enforces references
that authors use; the authoring policy and review still determine where those
references are required.

## Reproducing the demonstration

The reviewed artifacts are the [declared inputs](/research/traceable-brewster-angle/inputs.json),
the [Python calculation](/research/traceable-brewster-angle/calculate.py), its
[canonical results](/research/traceable-brewster-angle/results.json), the
[metrics generator](/research/traceable-brewster-angle/generate-metrics.mjs),
and the resulting [publication projection](/research/traceable-brewster-angle/metrics.json).
The [environment record](/research/traceable-brewster-angle/environment.md)
states the execution boundary. The [experiment README](/research/traceable-brewster-angle/README.md)
and [reviewed public-file manifest](/research/traceable-brewster-angle/PUBLIC_FILES.txt)
describe the bundle; its metrics conform to the [shared schema](/research/metrics.schema.json)
and its code carries the site's [license](/LICENSE). Code 1 shows the complete
local check.

```sh
python3 research/traceable-brewster-angle/calculate.py --check
node research/traceable-brewster-angle/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
stack test
stack exec site rebuild
node scripts/verify-site.mjs
```

**Code 1.** Recalculate the cheap upstream demonstration in check mode, verify
the publication projection and its fingerprints, test the compiler, rebuild
the site without stale Hakyll state, and inspect the generated links and failure
markers.

The recorded run used arm64 macOS 26.5.2, CPython 3.13.12, and Node.js 24.8.0. Both
scripts use only their language standard libraries. There are no downloads,
random inputs, services, credentials, or living subjects. Because the complete
calculation is cheap, `generate-metrics.mjs --check` reruns it; a larger
experiment could check only the committed analysis and schedule the expensive
rerun separately.

## What the system proves—and where it stops

For this demonstration, the chain is **traceable** because the prose resolves
from validated metrics, **analysis-reproducible** because the committed result
regenerates the same metric values, formats, and fingerprints, and **end-to-end
reproducible in the documented environment** because the committed inputs and
standard-library calculation regenerate that result. A fresh projection write
receives a fresh provenance timestamp. Those labels describe this small
demonstration. They do not automatically apply to another experiment merely
because it uses the same file names.

The optical model stops at a planar, lossless, isotropic, nonmagnetic interface
with real, wavelength-independent indices. It omits absorption, dispersion,
roughness, layered films, finite beams, and measurement uncertainty. The
near-zero p-reflectance is a floating-point evaluation of an analytic null, not
a measurement of perfect darkness.

The publication model has its own boundary. Traceability can establish which
committed calculation supplied a sentence. It cannot establish that the
equations were chosen correctly, the implementation has no bug, the inputs are
appropriate, or the prose interpretation is sound. Those remain scientific and
editorial responsibilities. The gain is smaller but concrete: when a reader
asks where a displayed result came from, the page now has an answer the build
can check. If you see a place where that answer overreaches—or a simpler failure
the chain should catch—I would like to know.

## References
