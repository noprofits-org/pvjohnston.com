# Johnson-haloacetate: relaxed CX3 rotation of CF3COO− and CCl3COO−

Publication projection of a private-lab Psi4 experiment
(`~/Molecules/johnson-haloacetate`). This directory does not contain the
raw Psi4 logs and does not rerun Psi4. It binds the research note
`posts/2026-08-24-does-cx3-rotation-oscillate-carboxylate-oxygen-charge.md`.

## Question and boundary

- Post type: research
- Question: does carboxylate oxygen charge oscillate with CX3 rotation,
  with larger amplitude for CCl3COO− than for CF3COO−?
- Research falsifier (frozen 2026-08-23): q(O) is flat vs dihedral on
  both haloacetates, or CF3 amplitude ≥ CCl3 amplitude. Post-scan
  scoring of falsifier 2 is in `JOURNAL.md`.
- What this experiment can establish: MBIS q(O) and q(COO) peak-to-peak
  amplitudes on the committed gas-phase B3LYP-D3(BJ)/aug-cc-pVDZ relaxed
  CX3 grid.
- What it cannot establish: DDEC6 or MP2/aug-cc-pVQZ charges, Hirshfeld,
  solvent, or a pKa mechanism.
- Traceability: traceable
- Highest reproduction level: analysis-reproducible from the committed
  rematch and scan tables. Not end-to-end in this public repository.
- Archived-evidence or rerun constraints: raw Psi4 output stays in the
  private Molecules lab (large, host paths), the same scratch convention
  as `research/hillel-triplet`.

## Ions

| ID | Species | Charge / multiplicity | Role |
|----|---------|------------------------|------|
| — | CH3COO− | −1 1 | rematch only |
| M1 | CF3COO− | −1 1 | rematch + scan |
| — | CClF2COO− | −1 1 | rematch only |
| M3 | CCl3COO− | −1 1 | rematch + scan |

## Generate publication metrics

```sh
node research/johnson-haloacetate/generate-metrics.mjs
node research/johnson-haloacetate/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`generate-metrics.mjs` derives rematch gates, peak-to-peak amplitudes,
0°/120° repeats, and energy barriers only from the committed CSVs. It
rejects non-finite numbers.

## Figures

```sh
python3 research/johnson-haloacetate/make_figures.py
```

writes the post PNGs under `images/` from the committed scan CSVs. No
new energies or charges are computed.

## Data and publication

`PUBLIC_FILES.txt` is the routing allowlist. Raw logs are excluded. The
Johnson paper is literature and is not redistributed; its DOI is in
`sources.json`. Literature citations live in `bib/bibliography.bib`.
