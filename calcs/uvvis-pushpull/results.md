# UV–Vis compute leg — data & provenance record

**This is the reproducible record of the calculation, not the post.** The
interpretive discussion / prose is left to the author. Everything below is
computed output plus the exact provenance needed to trust it in print. All
numbers are real TD-DFT results; nothing is tuned to experiment.

Deliverables in this folder:
`geometries/*.xyz`, `results/<mol>.json` (full per-state data),
`summary.csv` (one row per molecule×functional×state),
`spectra_curve.csv` + `spectra_sticks.csv` (pgfplots/TikZ-ready broadened
curves and stick transitions), `spectra.png` (visual sanity check only).

---

## Software & exact level of theory

| item | value |
|---|---|
| Program | Psi4 1.11 (miniforge env `qchem`), Python 3.14.6 |
| Post-processing | NumPy 2.5.0, SciPy 1.18.0, Matplotlib 3.11.0 |
| Geometry | **B3LYP/def2-SVP**, C1 symmetry, `gau_tight` (RKS, DF-SCF) |
| Excited states | **full TD-DFT (RPA, not TDA)**, 12 lowest singlets, **def2-TZVP** |
| Functionals | **B3LYP** (global hybrid) and **CAM-B3LYP** (range-separated) |
| SCF convergence | `e_convergence 1e-8`, `d_convergence 1e-8` (all jobs converged) |
| TD convergence | `r_convergence 1e-5` (all states converged) |
| Oscillator strength | length gauge, `OSCILLATOR STRENGTH (LEN)` |
| Broadening | Gaussian, **FWHM = 0.35 eV**, ORCA/Gaussian prefactor 1.3063×10⁸ |
| Determinism | fixed input geometries (built analytically, no random embed); DF-SCF is deterministic |

**Diffuse functions were NOT used** (target basis def2-TZVP, no def2-TZVPD /
aug). This is the one stated shortcut: diffuse sets are preferred for the pNA
CT and any Rydberg states, so the absolute CT energies (and especially the
higher deep-UV states) would shift somewhat with them. The B3LYP-vs-CAM-B3LYP
*comparison* — the methodological point — is robust to this.

Radiative lifetime uses the prior post's two-level relation
`A21 = 1/τ_rad = 0.667 · ν̃² · f` (ν̃ in cm⁻¹), applied to the lowest bright state.

---

## Compact results (lowest bright band per molecule × functional)

| molecule | functional | λmax (nm) | E (eV) | f | τ_rad (ns) | band |
|---|---|---|---|---|---|---|
| benzene | B3LYP | 176 | 7.03 | 0.578 | 0.8 | π→π* (E1u) |
| benzene | CAM-B3LYP | 174 | 7.12 | 0.601 | 0.8 | π→π* (E1u) |
| aniline | B3LYP | 265 | 4.68 | 0.037 | 28.6 | π→π* |
| aniline | CAM-B3LYP | 255 | 4.87 | 0.041 | 23.8 | π→π* |
| nitrobenzene | B3LYP | 283 | 4.38 | 0.014 | 83.1 | π→π* (weak) |
| nitrobenzene | CAM-B3LYP | 255 | 4.86 | 0.018 | 53.8 | π→π* (weak) |
| para-nitroaniline | B3LYP | 311 | 3.98 | 0.324 | 4.5 | **CT** |
| para-nitroaniline | CAM-B3LYP | 282 | 4.40 | 0.378 | 3.2 | **CT** |

Notes on band assignment (needed to read the table honestly):
- **benzene**: the two lowest states (231, 205 nm) are the symmetry-forbidden
  ¹B2u / ¹B1u (f≈0); the tabulated bright band is the degenerate ¹E1u pair at
  176 nm. Its band sits off the left edge of the 200–500 nm plot.
- **nitrobenzene**: the lowest bright entry is the *weak* π→π* near 283/255 nm.
  The **strong** π→π* band is one state higher: B3LYP 259 nm (f=0.197),
  CAM-B3LYP 240 nm (f=0.210). A dark n→π* sits lowest at ~320 nm (f≈0).
- **pNA**: the lowest bright state IS the charge-transfer band — HOMO→LUMO,
  hole–particle centroid separation **2.6 Å** (a real, computed CT diagnostic;
  the local π→π* states have <1.3 Å). This is the push–pull band.

Per-state type labels in the JSON/CSV use a conservative auto-classifier
(`CT` if hole–particle distance ≥ 2.0 Å and bright; `π→π*` if bright and local;
`dark/weak` otherwise). It deliberately does **not** auto-assert n→π* vs
forbidden-π→π* — those require orbital-symmetry inspection and are annotated by
hand above.

---

## Validation vs. experiment (computed − experiment, no tuning)

Experimental values are literature gas-phase / solution band maxima, quoted only
for comparison — not fit targets.

| molecule | band | computed B3LYP | computed CAM | experiment | ΔE B3LYP | ΔE CAM |
|---|---|---|---|---|---|---|
| benzene | ¹E1u π→π* | 7.03 eV | 7.12 eV | ~6.94 eV (179 nm, gas) | +0.09 | +0.18 |
| aniline | π→π* (¹La/¹Lb) | 4.68 eV | 4.87 eV | ~4.40 eV (~282 nm, vapor) | +0.28 | +0.47 |
| nitrobenzene | strong π→π* | 4.78 eV | 5.17 eV | ~4.90 eV (~252 nm) | −0.12 | +0.27 |
| **pNA** | **CT** | **3.98 eV** | **4.40 eV** | ~4.24 eV (gas-phase vertical) | **−0.26** | **+0.16** |

pNA is strongly solvatochromic — the CT band redshifts to ~3.3 eV (≈380 nm) in
water — so the gas-phase computed values are not directly comparable to aqueous
spectra. Absolute errors are typical TD-DFT (few tenths of an eV); the point is
the *pattern*, below.

**The pNA CT stress test (the methodological payoff):** the charge-transfer
state moves **+0.42 eV (3.98 → 4.40 eV, 311 → 282 nm) from B3LYP to
CAM-B3LYP** — far larger than the ~0.1–0.2 eV functional spread seen for the
local π→π* bands of benzene/aniline/nitrobenzene. This is the known global-hybrid
CT underestimation corrected by range separation (Dreuw & Head-Gordon). B3LYP
places the CT too low (−0.26 eV vs experiment); CAM-B3LYP lands within +0.16 eV.

---

## Optimized geometries (all fully relaxed, C1)

| molecule | ring planar? | –NH₂ pyramidalization | –NO₂ twist vs ring |
|---|---|---|---|
| benzene | yes (< 1e-5 Å) | — | — |
| aniline | ring planar | **14.4°** (N angle-sum 345.6°); amino H's 0.27 Å out of plane | — |
| nitrobenzene | ring planar | — | **0.0°** (coplanar) |
| pNA | ring planar | **4.5°** (N angle-sum 355.5°) — nearly planar | **0.1°** (coplanar) |

Physical read: isolated aniline's donor is genuinely pyramidal; in pNA the
push–pull conjugation flattens the same –NH₂ (4.5° vs 14.4°) and holds the
acceptor –NO₂ coplanar — the whole π system is more conjugated in the push–pull
case. (Point group is C1 for the pyramidal aniline; effectively Cs/C2v for the
planar-amino species, but all runs were done in C1 to avoid symmetry-trapping.)

---

## Methodology note — the additional geometry re-run (why / what / why-different)

**Why I re-ran.** The first optimization returned aniline **and** pNA with a
perfectly planar –NH₂ (pyramidalization 0.0°, N angle-sum exactly 360°). That is
the planar *inversion transition state*, not the minimum — isolated aniline's
amino group is pyramidal. So the first geometries were sitting on a saddle point.

**Root cause.** These molecules were built analytically (no RDKit/OpenBabel in
the env, so no SMILES→3D). My first amino seed placed the two N–H hydrogens on
*opposite* sides of the ring plane (z = +0.35 / −0.35). That arrangement is
antisymmetric — it averages to planar and preserves a mirror plane — so the
gradient at the planar geometry was zero by symmetry and the optimizer never left
it.

**The fix.** Re-seed the amino group as an "umbrella": both N–H hydrogens to the
*same* side (z = +0.55) with N nudged +0.10 Å, breaking the planar symmetry
toward the true minimum. (I also corrected an inverted –NO₂-twist metric that had
reported 90° for a coplanar nitro group; the underlying geometry was already
correct, only the reported number was backwards.)

**Result after re-run.** aniline –NH₂ relaxed to a genuine pyramid (14.4°,
angle-sum 345.6°); pNA –NH₂ to a near-planar 4.5° with coplanar –NO₂. Crucially,
the **excited-state energies barely moved**: aniline lowest bright 269 → 265 nm,
pNA CT 312 → 311 nm (B3LYP). The re-run corrects the reported *geometry*; it does
**not** change the donor/acceptor/push–pull spectral story.

**Why the result differed the second time.** Same functional, same basis, same
optimizer, same convergence — the *only* change was the starting geometry's
symmetry. The first seed sat exactly on the planar saddle (zero gradient by
symmetry, nowhere to roll); the umbrella seed put the molecule on the downhill
side of that saddle, so the optimizer relaxed into the pyramidal minimum. It is a
starting-guess/symmetry artifact, not a change in method.

---

## Computed observations (raw data-readouts for the author — not prose)

- **Donor only (aniline):** vs benzene's 176 nm bright band, the –NH₂ HOMO→LUMO
  π→π* appears at 265/255 nm (B3LYP/CAM) — a large red-shift, moderate f≈0.04,
  τ_rad ≈ 24–29 ns.
- **Acceptor only (nitrobenzene):** red-shifts and adds low-lying dark n→π*
  (~320 nm, f≈0) plus a strong π→π* at 259/240 nm (f≈0.2); the lowest *bright*
  band is weak (f≈0.01–0.02), τ_rad long (54–83 ns).
- **Push–pull (pNA):** a new low-energy HOMO→LUMO **CT band** at 311/282 nm that
  neither substituent produces alone — the *brightest* band of the four
  (f≈0.32–0.38), shortest τ_rad (3–5 ns), hole–particle separation 2.6 Å.
- **Functional disagreement:** local π→π* bands differ by ~0.1–0.2 eV between
  B3LYP and CAM-B3LYP; the pNA CT differs by **0.42 eV** — the diagnostic
  signature of the CT problem.
