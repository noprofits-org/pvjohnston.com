# correlation-in-hydrogenation

How does electron correlation survive the subtraction that forms a gas-phase
hydrogenation enthalpy, and why should the surviving term be treated as a
reaction-level residual rather than a bond-local quantity?

This experiment owns the traceable metrics for a forthcoming post and is a
direct sequel to `posts/2026-07-04-the-correlation-gap-in-water-measured.md`.
That post measured correlation energy in a single system; here the same idea is
turned on a *reaction*: the correlation contribution to an enthalpy is
ΔH(CCSD(T)) − ΔH(HF). The two C–C rungs show what happens when that
reaction-level residual is treated as though it were a transferable per-bond
quantity.

## Question and boundary

- Post type: understanding
- Question: how does electron correlation survive a reaction-enthalpy
  subtraction, and why is the remainder reaction-specific rather than a
  transferable π-bond property?
- Demonstration mechanism: compute ΔH(CCSD(T)) − ΔH(HF) for four
  hydrogenations, then compare the two reactions that each remove one C–C π
  bond. The 4.184 kJ/mol (1 kcal/mol) chemical-accuracy scale makes the size of
  the mismatch legible; it is a comparison aid, not a preregistered decision
  rule.
- What this experiment can establish: the correlation contribution (CCSD(T)
  minus HF, cc-pVTZ) to each hydrogenation enthalpy in the frozen set, and
  whether the two single-π-bond C–C rungs share it within chemical accuracy.
- What it cannot establish: complete-basis-set correlation (cc-pVTZ is finite,
  not extrapolated); whether CCSD(T) itself is converged for these multiple
  bonds (no higher-order or multireference check); open-shell or
  transition-state correlation; anharmonic corrections beyond RRHO.
- Traceability: self-contained and fully computational. The reference is
  CCSD(T), not experiment, so there are **no external literature values** to
  verify. The committed `results.json` and generated `metrics.json` make the
  reader-facing values traceable.
- Highest reproduction level: end-to-end reproducible. The full run is
  deterministic given the pinned conda environment; single-threaded BLAS avoids
  changes in floating-point reduction order. The analysis layer is reproducible
  without psi4 via `calculate.py --check`.
- Archived-evidence or rerun constraints: requires psi4 1.9.1 from
  `conda-linux-64.lock`; no network or paid services.

## The frozen reaction set

| slug | reaction | π bonds hydrogenated | role |
| --- | --- | --- | --- |
| `acetylene_hydrogenation` | C₂H₂ + H₂ → C₂H₄ | 1 (C–C) | transferability rung A |
| `ethylene_hydrogenation`  | C₂H₄ + H₂ → C₂H₆ | 1 (C–C) | transferability rung B |
| `ammonia_synthesis`       | N₂ + 3 H₂ → 2 NH₃ | 2 (N–N) | triple-bond context |
| `methanol_synthesis`      | CO + 2 H₂ → CH₃OH | 2 (C–O) | triple-bond context |

All species are closed-shell singlets. The two C–C rungs form the main worked
comparison; the N₂ and CO reactions provide multiple-bond context for the
reaction-level correlation residual.

## Method and why the thermal correction cancels

Geometry and ideal-gas RRHO thermal/ZPE corrections are computed at
B3LYP/def2-TZVP. HF and CCSD(T) energies (cc-pVTZ, frozen core) come from one
CCSD(T) single point per species at the B3LYP geometry — its SCF total is the
HF baseline. Reaction enthalpies at HF and at CCSD(T) share the *same* B3LYP
thermal correction, so the correlation contribution ΔH(CCSD(T)) − ΔH(HF) is
exactly the correlation part of the electronic reaction energy. This composite
(CCSD(T) energy on a DFT geometry with a DFT thermal correction) is stated
plainly here rather than hidden.

## Run

```sh
conda create --name correlation-in-hydrogenation \
  --file research/correlation-in-hydrogenation/conda-linux-64.lock
OMP_NUM_THREADS=1 conda run -n correlation-in-hydrogenation \
  python3 research/correlation-in-hydrogenation/calculate.py     # writes results.json
```

`calculate.py --check` needs no psi4: it re-derives every reaction quantity and
the summary from the committed per-species energies and checks internal
consistency.

## Generate publication metrics

```sh
node research/correlation-in-hydrogenation/generate-metrics.mjs
node research/correlation-in-hydrogenation/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

The post binds this directory with `experiment: correlation-in-hydrogenation`
and cites values inline, e.g. `[pi_bond_correlation_transferability_gap_kj]{.metric}`
or `[correlation_content_acetylene_hydrogenation_kj]{.metric}`.

## Files

- `inputs.json` — methods, conditions, constants, convergence, per-species
  Z-matrices, stoichiometry, and the transferability-comparison rung pair.
- `calculate.py` — per species: optimize + frequencies (B3LYP) and a CCSD(T)
  single point; forms HF, CCSD(T), and correlation reaction enthalpies; writes
  `results.json`. `--check` re-derives arithmetic without psi4.
- `generate-metrics.mjs` — projects `metrics.json`; `--check` byte-compares.
- `conda-linux-64.lock` — explicit conda lock for the psi4 1.9.1 environment.
- `environment.md`, `sources.json`, `PUBLIC_FILES.txt`.
