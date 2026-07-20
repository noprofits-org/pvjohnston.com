# SIREN convention equivalence under Adam

This directory is the traceable-metrics pilot for the experiment reported in
“Why the two SIREN conventions train differently under Adam.” The experiment
uses analytic K1 functions and contains no downloaded, personal, proprietary,
or sensitive dataset.

The experiment predates the one-directory convention. Its legacy canonical
artifacts remain at their published paths so existing article links do not
break:

- `downloads/siren-convention-adam.py`
- `downloads/conv_equiv.json`
- `downloads/conv_range.json`

`generate-metrics.mjs` derives a typed publication projection from those frozen
records. It also fingerprints the script and both result files.

```sh
node research/siren-convention-adam/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

The Hakyll post binds this directory with
`experiment: siren-convention-adam`. Every Table 1 and Table 2 value, their
derived medians and ratios, and repeated prose claims resolve from
`metrics.json`. Number formatting is derived from each raw value by the site
compiler; the artifact contains no independent display string that could
silently disagree with it.

## Scope of the claim

This pilot is **analysis-reproducible** for the two frozen training sweeps: the
committed JSON records regenerate the publication metrics without rerunning the
20,000-epoch jobs. It is not yet an end-to-end reproduction check.

Three older diagnostics have no frozen result artifact and therefore remain
outside the traceability claim: initialization identity, finite-difference
gradient errors, and the secondary-platform comparison. A current run of the
identity mode on the stated secondary platform still gives machine-precision
agreement but not the exact historical maximum printed in the post. That gap is
recorded rather than silently absorbed into `metrics.json`.

## Environment

The original run used CPython 3.10.12 on aarch64 Linux with NumPy 2.2.6. The
single Python dependency is pinned in `requirements.txt`; operating-system and
architecture details remain documented here and in the post because a Python
requirements file cannot lock them.

## Publication

`PUBLIC_FILES.txt` is the reviewed manifest for a future or explicit
reproduction-bundle step; the normal site build does not consume it. The three
legacy artifacts were already public before this pilot; `metrics.json` adds a
stable, machine-readable projection and is routed by Hakyll. No whole-directory
auto-packaging is used.
