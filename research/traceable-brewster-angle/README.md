# Traceable Brewster-angle demonstration

This deliberately small optics model accompanies “From script to sentence: a
traceable Brewster-angle calculation.” It demonstrates the site's complete
traceable-metrics path without external data or third-party dependencies.

## Question and boundary

- Post type: Understanding
- Question: How can a computed physical result travel from a script into a published sentence with an auditable chain of custody?
- Mechanism exposed: a closed-form Brewster angle, a numerical Fresnel sweep,
  and a separate energy-balance consistency check become typed publication
  metrics.
- What this can establish: that the committed inputs and code regenerate the canonical output and every quoted model setting and generated result.
- What it cannot establish: that the ideal interface represents measured glass, or that the traceability system proves its own code scientifically correct.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible in the documented environment
- Archived-evidence or rerun constraints: none

The interface is idealized as planar, lossless, isotropic, nonmagnetic, and
traversed from a lower to a higher real refractive index. The selected indices
are declared model inputs, not measurements of a particular material.

## Reproduce

```sh
python3 research/traceable-brewster-angle/calculate.py
python3 research/traceable-brewster-angle/calculate.py --check
node research/traceable-brewster-angle/generate-metrics.mjs
node research/traceable-brewster-angle/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`calculate.py` creates the canonical `results.json`. During normal verification,
`generate-metrics.mjs --check` first reruns that cheap calculation in check mode,
then proves that `metrics.json` is the exact current projection. The normal
Hakyll site build reads the committed projection; it does not run arbitrary
experiments.

The projection's `generated_at` field is write-time provenance metadata. A
fresh non-check write stamps the wall clock; `--check` reuses the committed
timestamp while recomputing the metric values, formats, and fingerprints for an
exact comparison.

## Publication

`PUBLIC_FILES.txt` records the reviewed reader-facing set. Hakyll's explicit
route list mirrors the experiment files in that manifest; the build does not
parse the manifest itself. No whole-directory auto-publication is used.
