# How the donor closes the gap: frontier orbitals of para-X-benzylidenemalononitriles

This experiment supports the Understanding post on the para-substituent effect
in a minimal push-pull dye. It computes the frontier-orbital energies and the
lowest vertical excitation for four benzylidenemalononitriles:

| X | name | donor strength (σ_p⁺) |
|---|------|----------------------:|
| H | benzylidenemalononitrile | 0.00 |
| F | 4-fluorobenzylidenemalononitrile | −0.07 |
| NH₂ | 4-aminobenzylidenemalononitrile | −1.30 |
| NMe₂ | 4-(dimethylamino)benzylidenemalononitrile | −1.70 |

The σ_p⁺ values come from Hansch, Leo and Taft (1991).[@Hansch1991]

## Question and boundary

- Post type: understanding
- Question: How does donor strength move the frontier orbitals in a minimal
  push-pull dye, and is para-fluorine a net donor or net acceptor in that
  scaffold?
- Demonstration mechanism: Kohn-Sham HOMO and LUMO energies, and the lowest
  TD-DFT vertical excitation, computed at fixed geometry and level of theory
  across the donor series. The demonstration establishes (a) how the HOMO-LUMO
  gap closes as donor strength increases, and (b) whether the small substituent
  shift from H to F follows the same trend as the larger substituent shifts.
- Outcome (2026-08-16):
  - The gap closes monotonically with donor strength under both CAM-B3LYP and
    B3LYP; the gap-vs-σ_p⁺ linear fit has R² > 0.998 with both functionals.
  - From H to NMe₂ the HOMO rises roughly 2.1–2.5 times as much as the LUMO,
    depending on functional; most of the gap closure comes from destabilizing
    the HOMO.
  - From H to F the gap closes by ≈0.06 eV under both functionals, and the S₁
    excitation red-shifts by a similar amount. Para-fluorine therefore behaves
    as a weak net donor in this scaffold, even though its inductive effect is
    withdrawing.
- What this experiment can establish:
  - The self-consistent Kohn-Sham orbital energies at the stated geometry and
    level of theory, and their systematic dependence on the para substituent.
  - The lowest TD-DFT vertical excitation energy and its dominant orbital
    character under the same conditions.
  - A linear relationship between the Hammett σ_p⁺ constant and the computed
    HOMO-LUMO gap at this level of theory.
- What it cannot establish:
  - Absolute agreement with a measured spectrum. These are gas-phase vertical
    excitations with no solvent model; charge-transfer states are strongly
    solvatochromic.
  - Whether para-F is a net donor in every molecular context. The result is
    specific to this scaffold and this donor/acceptor arrangement.
  - Excited-state energies to better than the typical ~0.2–0.3 eV error of
    TD-DFT for charge-transfer states, which is why two functionals are
    reported.
  - The physical origin of the HOMO rise beyond the qualitative donor–π
    conjugation picture. No decomposition into resonance and field components
    is performed.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible
- Archived-evidence or rerun constraints: Psi4 1.9.1 under the recorded conda
  environment. Each leg is a few CPU-minutes on 8 cores; the optimization and
  each TD-DFT leg are separate commands so a failure in one does not cost the
  others.

## Provenance

The canonical TD-DFT results were produced by this experiment's own
`run_tddft.py` on 2026-08-14, with the level of theory and starting-geometry
protocol documented here. This script is the donor-strength-ladder harness
adapted from `research/dcdhf-me2-transitions/run_tddft.py`; it is kept in this
experiment directory so the BMN series is self-contained.

The Psi4 output logs are not committed (large, regenerable, absolute scratch
paths), so the occupied frontier-orbital energies were parsed from those logs
once and committed as `results/orbital_gaps.json`. The virtual orbital energies
were not recorded anywhere else, so `extract_frontier.py` re-parses the same
logs and cross-checks its occupied energies against `results/orbital_gaps.json`
to 1 meV. The sha256 of each log is stored in `results/frontier_orbitals.json`.

## Pipeline

```
run_all.sh
  ├── build_geometries.py          # analytic starting structures
  ├── run_tddft.py optimize ...    # B3LYP/def2-SVP geometry optimization
  ├── run_tddft.py excite ...      # TD-DFT at def2-TZVP, CAM-B3LYP + B3LYP
  ├── orbital_gaps.py              # parse occupied HOMO/HOMO-1 from logs
  ├── extract_frontier.py          # parse HOMO-1, HOMO, LUMO, LUMO+1 from logs
  ├── make-figure.mjs              # render results/figure_frontier_levels.html
  └── generate-metrics.mjs         # project metrics.json
```

`generate-metrics.mjs --check` verifies that `metrics.json` is byte-identical
to what the generator produces from the committed `results/` files.
`make-figure.mjs --check` does the same for `results/figure_frontier_levels.html`.

## Pre-committed analysis choices

1. **Two functionals are reported side by side.** CAM-B3LYP is the a priori
   better choice for charge-transfer excitations; B3LYP is reported as a
   sensitivity check. Neither is privileged in the metric naming.
2. **The donor-strength axis is −σ_p⁺**, so stronger donors sit to the right.
   This ordering was fixed before any calculation.
3. **The HOMO-LUMO gap is ε(LUMO) − ε(HOMO)** from the Kohn-Sham orbital
   energies at the def2-TZVP wavefunction. It is not the TD-DFT excitation
   energy and is not claimed to be.
4. **S₁ is quoted only when its dominant amplitude is HOMO→LUMO.** The metrics
   generator raises an error if that ever ceases to be true.
