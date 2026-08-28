# Hillel M4 SF-TDA: same-geometry two-root rematch

Publication projection of a private-lab ORCA 6.1.1 same-geometry
two-root SF-TDA experiment (`~/Molecules/hillel-m4-sft`). This
directory does not contain the raw ORCA `.out` files and does not
rerun ORCA. It binds the research note
`posts/2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root.md`.

## Question and boundary

- Post type: research
- Question: does the M4 SF profile-gap sign change survive a
  same-geometry two-root evaluation?
- Research falsifier: (1) neither family has a both-assigned
  same-geometry ΔE sign change on a neighboring pair in 90–135°;
  (2) a family has a sign change whose interpolant lies outside
  90–135°; (3) a family has no neighboring both-assigned pair.
- What this experiment can establish: the sign of same-geometry
  ΔE = E(T1) − E(S0) on the eight already-published constrained-CNNC
  geometries, scored separately on the S0-relaxed and T1-relaxed
  families, and the stored linear interpolant of each 90°/105° pair.
- What it cannot establish: a located MECP, an evaluated degeneracy,
  PCM, or a denser 90–105° bracket.
- Traceability: traceable
- Highest reproduction level: analysis-reproducible from the
  committed Bayes projection. Not end-to-end in this public
  repository.
- Archived-evidence or rerun constraints: raw ORCA output stays in
  the private Molecules lab (large, host paths), the same scratch
  convention as `research/hillel-m4-sft`. The committed Bayes file
  is a publication copy of the lab dump with absolute host paths
  replaced by relative artifact identifiers; its scientific fields
  are unchanged
  (`0656e7a7eb78597a35b4343e15fd754789e685e465a62d5e833f9ee5553faf0c`,
  9917 bytes). Private output SHA-256 values are recorded in that
  dump by filename only. A private-lab `metrics.json` SHA-256 is
  stored in the dump as a record only; it is not a public path.

## Molecule

| ID | Species | Charge / multiplicity |
|----|---------|------------------------|
| M4 | 4-dimethylamino-4′-nitroazobenzene | 0 / SF-TDA manifold |

Required CNNC window: 135°, 120°, 105°, 90°. Two geometry families:
the published S0-relaxed and T1-relaxed constrained-CNNC opts. One
SF-TDA SP per geometry. No new opts.

## Generate publication metrics

```sh
node research/hillel-m4-sft-tworoot/generate-metrics.mjs
node research/hillel-m4-sft-tworoot/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`generate-metrics.mjs` flattens the committed Bayes keys into
`metrics.json`. It checks that each point's ΔE matches
(E(T1) − E(S0)) × conversion_Eh_to_kJmol and that each family's
90°/105° pair interpolant matches the stored neighboring-pair
value. The site interpolant metrics are the stored
`crossing_phi_deg_s0` and `crossing_phi_deg_t1`, not newly invented
angles.

## Regenerate Figure 1

```sh
python3 -m pip install -r research/hillel-m4-sft-tworoot/requirements-figure.txt
python3 research/hillel-m4-sft-tworoot/analysis/make_deltaE_figure.py
```

The renderer loads the committed `analysis/hanken-grotesk.ttf` with Pillow
`ImageFont.truetype` (pinned in `requirements-figure.txt`) for Latin ticks
and numbers. Axis Δ and φ are not in that Latin-only cmap; they come from
the committed `analysis/dejavu-sans.ttf` at the same pixel size. Coverage
is checked from each TTF cmap before drawing. The renderer does not look
up a host font path or a platform-specific FreeType soname. Lab-side
molecular stills under `frames/` are optional and are not in this repository.
Without them the same command writes the data plot from the committed
Bayes projection (`results/bayes-metrics.json`), leaves any existing still
PNGs in place, and exits 0.
With all eight frames present it also writes the published S0 and T1 stills.

The command updates:

- `images/2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-og.png`
- `images/2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-s0-stills.png`
  (only when frames exist)
- `images/2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-t1-stills.png`
  (only when frames exist)

and an ignored preview beside the renderer. Point labels on the plot are the
stored ΔE values. Linear interpolants of the 90–105 pairs are marked at
ΔE = 0; they are not labeled as an MECP or an evaluated degeneracy. 110°
is unmarked.

## Data and publication

`PUBLIC_FILES.txt` is the routing allowlist. Raw ORCA logs are
excluded. The Hillel papers are literature and are not
redistributed. Literature citations live in `bib/bibliography.bib`.
