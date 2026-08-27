# Hillel M4 SF-TDDFT: constrained CNNC rematch of M4

Publication projection of a private-lab ORCA 6.1.1 SF-TDDFT experiment
(`~/Molecules/hillel-m4-sft`). This directory does not contain the raw
ORCA `.out` files and does not rerun ORCA. It binds the research note
`posts/2026-08-27-does-hillel-m4-still-cross-under-sf-tddft.md`.

## Question and boundary

- Post type: research
- Question: does 4-dimethylamino-4′-nitroazobenzene (Hillel M4) still
  show a both-converged S0/T1 crossing near 110° when S0 and T1 are
  taken from the SF-TDDFT manifold at the 2024 electronic-structure
  level?
- Research falsifier: (1) no both-converged both-assigned ΔE sign
  change on the required window; (2) the stored interpolant lies
  outside 90–135°; (3) no neighboring both-converged both-assigned
  pair.
- What this experiment can establish: the sign of
  ΔE = E(T1) − E(S0) on the committed gas-phase SF-TDA
  LibXC(BHANDHLYP)-D3(BJ)/def2-QZVPP window, and the stored linear
  interpolant of the 90°/105° pair.
- What it cannot establish: PCM, a located MECP, CASSCF/QD-NEVPT2,
  M2 reconvergence, or a 4-hydroxyazobenzene scan.
- Traceability: traceable
- Highest reproduction level: analysis-reproducible from the
  committed Bayes projection. Not end-to-end in this public
  repository.
- Archived-evidence or rerun constraints: raw ORCA output stays in
  the private Molecules lab (large, host paths), the same scratch
  convention as `research/hillel-triplet`. The Bayes file on this
  branch was reconstructed from the filled note's metric names and
  the registered claim because the private-lab dump was not on the
  authoring host. The lab sha256
  `d46c5c302ffc504f156feb0af95edf11b9a4b4a3efd73d1bbe329b639718ba10`
  is recorded in the reconstruction block; replace the file with the
  lab dump if it is later available and re-run the generator.

## Molecule

| ID | Species | Charge / multiplicity |
|----|---------|------------------------|
| M4 | 4-dimethylamino-4′-nitroazobenzene | 0 / SF-TDA manifold |

Required CNNC window: 135°, 120°, 105°, 90°. No M2. No 4-hydroxy.

## Generate publication metrics

```sh
node research/hillel-m4-sft/generate-metrics.mjs
node research/hillel-m4-sft/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`generate-metrics.mjs` flattens the committed Bayes keys into
`metrics.json`. It checks that each point's ΔE matches
(E(T1) − E(S0)) × conversion_Eh_to_kJmol and that the 90°/105°
pair interpolant matches the stored neighboring-pair value. The
site crossing metric is the stored `crossing_phi_deg`, not a
re-derived angle.

## Data and publication

`PUBLIC_FILES.txt` is the routing allowlist. Raw ORCA logs are
excluded. The Hillel papers are literature and are not
redistributed. Literature citations live in `bib/bibliography.bib`.
