# Tier 2: prepared for a team with more compute (NOT RUN by us)

Nothing in this directory has been run by us, and no claim is made from it.

## What it is for
- SCS-CC2/def2-TZVP//PBE0/6-31G(d) ΔEST, E(S1), E(T1), f, μF (the paper's headline method), for all 57 structures.
- ADC(2)/def2-TZVP for the structures too large for the M1 (2b/2c optional on M1; 2d-2k, 3, 4d-4k, 5,
  6a-6k, 7a-7f, 8a-8c, 13-23).
- kF from SI Eq. S1-S2: kF = 2 E_F^2 f / c^3 (a.u.), f = (2/3) E_F μF^2. We checked these equations against
  SI Table 1 for 12 rows (2a-2f, 2i-2k, 6e, 7f, 13). All reproduce within the printed rounding.

## Layout
- `turbomole/<id>/coord` - SI geometry in Bohr (Turbomole $coord)
- `turbomole/ricc2_blocks.template` - $ricc2/$excitations data groups (SCS-CC2 job A; ADC(2) job B).
  Documented assumptions: SCS cos=1.2, css=1/3; frozen core = define default; $cbas def2-TZVP.
- `../expected/published_SI_tables_1-3.csv` - the numbers a rerun should be compared against.

## Expected outputs to commit per structure
`turbomole/<id>/{control,dscf.out|ridft.out,ricc2.out}` plus a parsed `results/<id>.json` with S1/T1
energies (eV), ΔEST (meV), f, μF and kF. Compare against the CSV; the same ±50 meV tolerance applies.

## Size guide (def2-TZVP basis functions; from xyz/basis_counts.json)
Largest: 6k 2532, 4k 2520, 4j 2310, 8c 2232. SCS-CC2 excited states at this size are cluster jobs.
The paper itself notes that SCS-CC2 failed to converge for 6i-6k (SI Table 2 caption).
