# How the acceptor closes the gap: frontier orbitals of para-MeO push-pull dyes

This experiment supports the Understanding post on the acceptor-strength effect
in a para-methoxy push-pull dye. It computes the frontier-orbital energies and
the lowest vertical excitation for three molecules with a fixed para-methoxy
donor and increasing acceptor strength:

| acceptor | name |
|----------|------|
| CN | p-methoxybenzonitrile |
| DCV | p-methoxybenzylidenemalononitrile |
| TCF | OMe-substituted DCDHF |

The acceptors are ordered CN < DCV < TCF by increasing acceptor strength.

## Question and boundary

- Post type: understanding
- Question: How does acceptor strength move the frontier orbitals in a
  para-methoxy push-pull dye?
- Demonstration mechanism: Kohn-Sham HOMO and LUMO energies, and the lowest
  TD-DFT vertical excitation, computed at fixed geometry and level of theory
  across the acceptor series. The demonstration establishes how the HOMO-LUMO
  gap closes as acceptor strength increases.
- Outcome (2026-08-16):
  - With the donor fixed as para-methoxy, increasing acceptor strength from CN
    to DCV to TCF lowers the LUMO and closes the HOMO-LUMO gap. The HOMO moves
    much less than the LUMO. Under CAM-B3LYP the gap closes by 2.26 eV from CN
    to TCF; under B3LYP it closes by 2.01 eV. The lowest excitation red-shifts
    with the gap. For CN the lowest excitation is HOMO→LUMO+1; for DCV and TCF
    it is HOMO→LUMO.
- What this experiment can establish:
  - The self-consistent Kohn-Sham orbital energies at the stated geometry and
    level of theory, and their systematic dependence on the acceptor fragment.
  - The lowest TD-DFT vertical excitation energy and its dominant orbital
    character under the same conditions.
- What it cannot establish:
  - Absolute agreement with a measured spectrum. These are gas-phase vertical
    excitations with no solvent model; charge-transfer states are strongly
    solvatochromic.
  - Excited-state energies to better than the typical ~0.2–0.3 eV error of
    TD-DFT for charge-transfer states, which is why two functionals are
    reported.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible
- Archived-evidence or rerun constraints: Psi4 1.9.1 under the recorded conda
  environment. Each leg is a few CPU-minutes on 8 cores; the optimization and
  each TD-DFT leg are separate commands so a failure in one does not cost the
  others.

## Provenance

The canonical TD-DFT results are produced by this experiment's own
`run_tddft.py` with the level of theory and starting-geometry protocol
documented here.

The Psi4 output logs are not committed (large, regenerable, absolute scratch
paths), so the occupied frontier-orbital energies are parsed from those logs
once and committed as `results/orbital_gaps.json`. The virtual orbital energies
are parsed by `extract_frontier.py` and cross-checked against
`results/orbital_gaps.json` to 1 meV. The sha256 of each log is stored in
`results/frontier_orbitals.json`.

## Pipeline

```
run_all.sh
  ├── build_geometries.py          # analytic starting structures
  ├── run_tddft.py optimize ...    # B3LYP/def2-SVP geometry optimization
  ├── run_tddft.py excite ...      # TD-DFT at def2-TZVP, CAM-B3LYP + B3LYP
  ├── orbital_gaps.py              # parse occupied HOMO/HOMO-1 from logs
  ├── extract_frontier.py          # parse HOMO-1, HOMO, LUMO, LUMO+1 from logs
  ├── make-figure.mjs              # render results/figure_frontier_levels.html
  ├── render-figure-png.mjs        # render hero PNG for front matter
  └── generate-metrics.mjs         # project metrics.json
```

`generate-metrics.mjs --check` verifies that `metrics.json` is byte-identical
to what the generator produces from the committed `results/` files.
`make-figure.mjs --check` does the same for `results/figure_frontier_levels.html`.

## Starting structures

Starting structures were built analytically because no force-field toolkit is
available in the environment. The DCV acceptor was twisted 30° about the
aryl-acceptor single bond. The TCF acceptor was started planar because twisting
the rigid dihydrofuran made `gau_tight` stall on displacement criteria. The CN
acceptor in meo-cn is linear and defines no acceptor plane, so its starting
structure is planar; the diagnostic reported is the angle between the aryl plane
and the C(aryl)-C(nitrile) bond vector. The DCV twist ensures that a planar
optimized structure is a result the optimizer reached, not an assumption built
into the input.

## Pre-committed analysis choices

1. **Two functionals are reported side by side.** CAM-B3LYP is the a priori
   better choice for charge-transfer excitations; B3LYP is reported as a
   sensitivity check. Neither is privileged in the metric naming.
2. **The acceptor-strength axis is CN < DCV < TCF**, ordered before any
   calculation.
3. **The HOMO-LUMO gap is ε(LUMO) − ε(HOMO)** from the Kohn-Sham orbital
   energies at the def2-TZVP wavefunction. It is not the TD-DFT excitation
   energy and is not claimed to be.
4. **S₁ is quoted for every molecule.** The metrics generator records the
   dominant amplitude character of the lowest state. For CN it is
   HOMO→LUMO+1; for DCV and TCF it is HOMO→LUMO.
