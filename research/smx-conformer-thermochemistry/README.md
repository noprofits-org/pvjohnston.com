# SMX conformer thermochemistry

This bundle tests whether the nearly uniform conformer populations reported by
Blackmon and Closser remain nearly uniform after an independently calculated
thermochemical correction is added to their electronic energies.

The protocol was frozen in `PREREGISTRATION.md` before the first SMX
calculation. This Codex run was designed and executed without reading the
parallel Claude branch, protocol, journal, or outputs.

## Question and boundary

- Post type: research
- Question: does the source's nearly uniform A-D population remain nearly
  uniform after an independently calculated 298.15 K thermochemical correction?
- Hypothesis: in both the pure-RRHO and 50 cm^-1 modified-RRHO arms, the maximum
  population shift is below 10.0 percentage points and the effective conformer
  count remains at least 3.5.
- Falsifier: both arms fail at least one of those gates.
- Inconclusive conditions: the arms disagree or the preregistered
  method-fidelity gate fails.
- What this experiment can establish: the sensitivity of the source's
  electronic-energy population vector to thermochemical corrections generated
  by the frozen GFN2-xTB/ALPB(water) protocol.
- What it cannot establish: the source authors' unreported Q-Chem
  thermochemistry; experimental conformer populations; explicit-solvent, pH,
  triplet, or excited-state behavior; or equivalence between xTB/ALPB and
  Q-Chem/PCM.
- Traceability: source values, protocol, raw xTB outputs, canonical analysis,
  and reader-facing metrics are linked by SHA-256 fingerprints.
- Highest reproduction level: end-to-end reproducible on osx-arm64 with the
  explicit conda environment; analysis is independently checkable from
  committed xTB outputs without rerunning quantum chemistry. The canonical
  `results.json` serializes floats at 12 significant digits (magnitudes below
  1e-12 clamp to zero) so that the analysis byte-check is
  architecture-independent: regeneration on linux-x86_64 and osx-arm64 differs
  only in last-ulp accumulation noise, ten orders of magnitude below every
  registered decision margin.

## Source relationship

The source paper is:

H. Blackmon and K. D. Closser, "Determination of ground-state structure and
electronic excitations of sulfamethoxazole using density functional theory,"
*Computational and Theoretical Chemistry* **1264** (2026) 115931,
https://doi.org/10.1016/j.comptc.2026.115931.

The article reports four PCM minima within 0.202 kJ/mol and assigns populations
of approximately 25% from electronic energies. Frequencies were used to confirm
minima, but the frequencies and thermal corrections are not reported. This is
an independent extension using source coordinates and electronic energies, not
a reproduction of the Q-Chem calculations.

## Method

Each A-D source geometry is independently optimized with GFN2-xTB 6.7.1 and
ALPB water, followed by a Hessian at 298.15 K. The primary composite free energy
is:

```text
G_composite(i) = E_source_DFT(i) + [G_xTB(i) - E_xTB(i)]
```

Two independently run arms differ only in xTB's low-frequency rotor cutoff:

- `rrho`: 0 cm^-1;
- `mrrho50`: 50 cm^-1.

The xTB-native energy ordering is retained as a secondary sensitivity result.
All work is serial and single-threaded.

## Run

The source-only arithmetic and atom-order gate run without quantum chemistry:

```sh
conda run -n qchem \
  python research/smx-conformer-thermochemistry/run_experiment.py --preflight
```

Run all eight registered conformer/arm calculations serially and write the
canonical result. `--force` is required for a true rerun: this repository ships
the completed run directories, and without it the runner recognizes them as
complete, skips xTB entirely, and only rewrites the analysis. Passing `--force`
deletes each committed run directory and regenerates it from the source
geometry.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
conda run -n qchem \
  python research/smx-conformer-thermochemistry/run_experiment.py --force
```

Without `--force` the same command is an analysis-only rebuild, equivalent to
`--analyze` once every run directory is present.

Rebuild the analysis from committed raw outputs without rerunning xTB:

```sh
conda run -n qchem \
  python research/smx-conformer-thermochemistry/run_experiment.py --analyze
conda run -n qchem \
  python research/smx-conformer-thermochemistry/run_experiment.py --check
conda run -n qchem \
  python research/smx-conformer-thermochemistry/verify_analysis.py
```

Generate and verify publication metrics:

```sh
node research/smx-conformer-thermochemistry/generate-metrics.mjs
node research/smx-conformer-thermochemistry/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

## Result

The preregistered near-uniform-population hypothesis was **falsified**. Every
method-fidelity check passed, but both thermochemistry arms exceeded the
registered 10.0 percentage-point population-shift ceiling:

| Population | Source electronic energy | Pure RRHO | mRRHO50 |
| --- | ---: | ---: | ---: |
| A | 26.26% | 45.94% | 39.01% |
| B | 24.86% | 30.79% | 25.70% |
| C | 24.67% | 12.20% | 17.71% |
| D | 24.21% | 11.07% | 17.58% |
| Maximum absolute shift | - | 19.67 pp | 12.74 pp |
| Effective conformer count | 4.00 | 3.00 | 3.57 |

Pure RRHO failed both registered robustness gates. mRRHO50 retained an effective
count above 3.5 but still failed the population-shift gate. The narrower
conclusion is that the source's approximately 25/25/25/25 electronic-energy
population vector is not robust to thermochemical corrections from this frozen
GFN2-xTB/ALPB(water) protocol. It does not determine the unreported Q-Chem
thermal corrections or experimental conformer populations.

As a separate source audit, all eight relaxation-energy magnitudes recomputed
from the supplement agree with the main-table values to within 0.005 kJ/mol,
but their signs oppose the table footnote's stated
`E_vertical - E_adiabatic` formula.

## Files

- `PREREGISTRATION.md` - frozen question, thresholds, methods, fidelity gate,
  outcomes, and stopping rule.
- `inputs.json` - source attribution and checksums, A-D energies and
  coordinates, constants, arms, and thresholds.
- `run_experiment.py` - restartable serial xTB runner and deterministic
  analysis; `--check` byte-compares the regenerated result.
- `verify_analysis.py` - fast source-arithmetic, sign-audit, geometry, and
  committed-result checks.
- `runs/` - source XYZ, thermostatistical control, raw xTB output, and optimized
  XYZ for every conformer/arm.
- `results.json` - canonical detailed output and preregistered verdict.
- `make-figure.py` - emits the post's Figure 1 TikZ body from `results.json`;
  `--check` fails if the figure committed in the post disagrees with the
  canonical populations, so a regenerated result cannot leave a stale plot.
- `generate-metrics.mjs` and `metrics.json` - fingerprinted reader-facing
  projection.
- `sources.json`, `environment.md`, `conda-osx-arm64-explicit.txt`, and
  `PUBLIC_FILES.txt` - provenance, execution boundary, lock, and publication
  allowlist.
