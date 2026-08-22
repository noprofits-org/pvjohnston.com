# Hillel-triplet: RKS/UKS CNNC scan of a classic push-pull azobenzene

Publication projection of a private-lab Psi4 experiment
(`~/Molecules/hillel-triplet`). This directory does not contain the raw
Psi4 logs and does not rerun Psi4. It binds the research note
`posts/2026-08-22-does-push-pull-abolish-the-s0-t1-crossing.md`.

## Question and boundary

- Post type: research
- Question: at RKS/UKS B3LYP-D3(BJ)/cc-pVDZ, does
  4-dimethylamino-4′-nitroazobenzene (M4) lose the S0/T1 crossing along
  CNNC, as the 2024 Hillel *et al.* push-pull sentence would have it?
- Research falsifier: M4 shows an S0/T1 crossing between both-converged
  points.
- What this experiment can establish: the sign of E(S0)−E(T1) on the
  committed gas-phase RKS/UKS grid, and the linear zero between
  both-converged neighbours.
- What it cannot establish: SF-TDDFT or CASSCF surfaces, solvent, a
  located MECP, or `<S²>`.
- Traceability: traceable
- Highest reproduction level: analysis-reproducible from the committed
  summary tables. Not end-to-end in this public repository.
- Archived-evidence or rerun constraints: raw Psi4 output stays in the
  private Molecules lab (large, host paths), the same scratch convention
  as `research/bmn-frontier-orbitals`.

## Molecules

| ID | Species | S0 | T1 |
|----|---------|----|----|
| M0 | azobenzene | 0 1 | 0 3 |
| M1 | 4-phenylazopyridine (AzPy) | 0 1 | 0 3 |
| M2 | AzPyH+ | 1 1 | 1 3 |
| M3 | 2-phenylazopyridine | 0 1 | 0 3 |
| M4 | 4-dimethylamino-4′-nitroazobenzene | 0 1 | 0 3 |

## Generate publication metrics

```sh
node research/hillel-triplet/generate-metrics.mjs
node research/hillel-triplet/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`generate-metrics.mjs` derives the claim crossing from the both-converged
M4 120°/105° pair in `results/results.json` and checks the committed CSVs
against that file.

## Figures

```sh
python3 research/hillel-triplet/make_figures.py
```

writes the three post PNGs under `images/` from the committed projection.
No new energies are computed.

## Data and publication

`PUBLIC_FILES.txt` is the routing allowlist. Raw logs are excluded. The
Hillel papers are literature and are not redistributed; their DOIs are in
`sources.json`. Literature citations live in `bib/bibliography.bib`.
