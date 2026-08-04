# CEPB C=C increment spread

This bundle tests the transferability claim of the correlation-energy-per-bond
(CEPB) model of Witkowski, Śmiga, Hirata, Dral, and Grabowski two ways: by
reanalyzing the source's own published per-molecule correlation energies
(Arm A), and by computing new frozen-core DF-CCSD(T) correlation energies for
the four C₄H₈ positional isomers that CEPB assigns identical correlation
energies (Arm B).

The protocol was frozen in `PREREGISTRATION.md` before the first production
calculation. Amendment 1, recorded before any contrast value was computed,
replaced the raw effective-increment statistic with a bond-count-cancelling
contrast as the primary Arm A metric; the amendment and the research journal
disclose that the raw CBS spread had already been hand-evaluated when the
amendment was recorded.

## Question and boundary

- Post type: research
- Question: how far apart are the correlation-energy changes of the identical
  bond-count swap C=C → C–C + 2 C–H across the source's own published data,
  and how large is the correlation contribution to C₄H₈ positional
  isomerization that CEPB sets to exactly zero?
- Hypothesis: transferability fails at chemical accuracy — the Arm A contrast
  spread exceeds 1.0 kcal/mol, and at least one Arm B pairwise difference
  exceeds 1.0 kcal/mol in magnitude.
- Falsifiers: Arm A spread at or below 1.0 kcal/mol at every published basis
  level; all six Arm B pairwise differences below 1.0 kcal/mol at both bases.
- Inconclusive conditions: basis levels disagreeing about a threshold, a sign
  change between the Arm B bases, or any method-fidelity gate failing.
- Registered outcome: **both arms inconclusive.** Arm A because the contrast
  spread is 0.51 kcal/mol at CBS but 1.78 and 2.45 kcal/mol at aug-cc-pVQZ
  and aug-cc-pVTZ, so the levels disagree about the threshold; Arm B because
  the cis-2-butene − 1-butene pair changed sign between cc-pVDZ and cc-pVTZ.
- What this experiment can establish: the internal consistency of the swap's
  price in the source's own published tables, and the size of the pairwise
  C₄H₈ correlation splits at frozen-core DF-CCSD(T)/cc-pVTZ and cc-pVDZ.
- What it cannot establish: what the source's own all-electron
  aug-cc-pVTZ/aug-cc-pVQZ + CBS protocol would return for the butenes; the
  behavior of any bond type outside C–H, C–C, C=C; or any claim that the
  source's fit is incorrect.
- Traceability: source transcription, protocol, raw Psi4 outputs, canonical
  analysis, and reader-facing metrics are linked by SHA-256 fingerprints.
- Highest reproduction level: end-to-end reproducible on linux-x86_64 with
  the committed explicit conda lock; analysis-reproducible from the committed
  run records everywhere (`analyze.py --check` byte-compares the committed
  `results.json`).

## Source relationship

The source paper is:

M. Witkowski, S. Śmiga, S. Hirata, P. O. Dral, and I. Grabowski, "Ultrafast
Correlation Energy Estimator," *The Journal of Physical Chemistry A* **129**
(2025) 8877–8890, https://doi.org/10.1021/acs.jpca.5c04423 (CC BY).

CEPB estimates a molecule's correlation energy as a sum of fitted bond-type
increments over its dominant Lewis structure. This is an independent
reanalysis-plus-extension: Arm A is arithmetic on the source's published
values, transcribed and frozen in `inputs.json`; Arm B is new quantum
chemistry on molecules in neither the source's training nor test set. Nothing
here reruns, refits, or re-extrapolates any calculation of the source's.

## Method

Arm A forms, at each of the source's three published levels (CBS,
aug-cc-pVQZ, aug-cc-pVTZ), the measured correlation change of the three
published pairs realizing the swap C=C → C–C + 2 C–H (ethene → ethane,
1,4-cyclohexadiene → cyclohexene, cyclohexene → cyclohexane), the single
CEPB-predicted change, the spread across the three measured values (primary),
and the raw effective C=C increments (secondary, descriptive).

Arm B optimizes each isomer at frozen-core DF-MP2 and computes frozen-core
DF-CCSD(T) at that geometry, at cc-pVTZ (registered) and cc-pVDZ
(sensitivity), forming all six pairwise correlation-energy differences.
Fidelity gates: convergence, heavy-atom connectivity, and a 0.02 T1 ceiling.

## Run

Arm B production (skips molecule/basis pairs whose committed results exist;
`--force` recomputes and overwrites them):

```sh
OMP_NUM_THREADS=1 conda run -n research \
  python research/cepb-increment-spread/run_armb.py --basis cc-pVTZ
OMP_NUM_THREADS=1 conda run -n research \
  python research/cepb-increment-spread/run_armb.py --basis cc-pVDZ
```

Rebuild and check the analysis from the committed run records, without
rerunning quantum chemistry:

```sh
python3 research/cepb-increment-spread/analyze.py
python3 research/cepb-increment-spread/analyze.py --check
```

Generate and verify publication metrics:

```sh
node research/cepb-increment-spread/generate-metrics.mjs
node research/cepb-increment-spread/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

## Result

Both registered verdicts are **inconclusive**, reported without repair per
the frozen stopping rule.

| Arm A contrast spread (kcal/mol) | CBS | aug-cc-pVQZ | aug-cc-pVTZ |
| --- | ---: | ---: | ---: |
| spread across the three swaps | 0.51 | 1.78 | 2.45 |
| deviation from CEPB (range) | −3.66 to −4.17 | −3.78 to −5.56 | −3.94 to −6.39 |

| Arm B max pairwise split (kcal/mol) | cc-pVDZ | cc-pVTZ |
| --- | ---: | ---: |
| isobutene − trans-2-butene | −1.357 | −1.329 |
| sign-flipping pair (cis-2-butene − 1-butene) | +0.168 | −0.329 |

Stable findings: all three Arm A contrasts miss the CEPB prediction in the
same direction (a systematic offset in the swap's price, not an environment
dependence), and isobutene is the most strongly correlated C₄H₈ isomer at
both bases while CEPB predicts all four identical.

## Post-hoc diagnostic

The committed 1-butene structures optimized to the planar anti skeleton of
the committed starting structure, whose symmetry a gradient-following
optimizer preserves. After the registered analysis was complete, a
frozen-core DF-MP2/cc-pVDZ harmonic-frequency calculation on the committed
cc-pVDZ 1-butene structure (`diagnostics/check_1butene_minimum.py`) found one
imaginary torsional mode: that stationary point is a saddle, not a minimum.
This diagnostic is outside the frozen protocol, changes no registered number
or verdict, and is reported as a post-hoc caveat in the post's Discussion.

## Files

- `PREREGISTRATION.md` — frozen questions, thresholds, protocol, amendment,
  fidelity gates, outputs, and stopping rule.
- `inputs.json` — the frozen transcription of the source's increments and
  per-molecule correlation energies, with declared levels and bond counts.
- `run_armb.py` — restartable serial Psi4 runner for Arm B.
- `runs/` — per-molecule, per-basis Psi4 output, optimized geometry, and
  canonical run record for the six computed molecules.
- `analyze.py` — deterministic analysis of both arms; `--check` byte-compares
  the committed result.
- `results.json` — canonical detailed output and the registered verdicts.
- `diagnostics/` — the post-hoc 1-butene frequency check and its outputs.
- `generate-metrics.mjs` and `metrics.json` — fingerprinted reader-facing
  projection.
- `sources.json`, `environment.md`, `conda-linux-64.lock`, and
  `PUBLIC_FILES.txt` — provenance, execution boundary, lock, and publication
  allowlist.
