# Journal — Johnson-haloacetate

Lab notes for the rematch gate and the relaxed CX3 scan. The frozen
hypothesis is in `PREREGISTRATION.md`. This file records what changed
after that freeze and the claim after the scan.

## 2026-08-24 — rematch complete; binding scheme amended before torsion

All four rematch optimizations formally converged (optking True and a
clean exit): CH3COO−, CF3COO−, CClF2COO−, CCl3COO−. Committed numbers
are in `rematch/summary.csv`.

Gate inequalities from that table, checked before any torsion:

- r(C–C): CCl3 > CClF2 > CF3 > acetate.
- Δ(C–X) oop−ip: CCl3 > CF3. CClF2 is mixed and is not used for this
  comparison. Acetate has no C–X pair of that kind.
- MBIS q(O) and q(COO): CF3 more negative than CCl3.

Löwdin q(O) and q(COO) on the same rematch densities reverse that
CF3/CCl3 order. Löwdin oxygen charges on aug-cc-pVDZ sit near zero
while MBIS oxygen charges sit near −0.7 e; the scheme is ill-defined
on this basis. Hirshfeld is not compiled into this Psi4 1.11 build.

**Amendment (after rematch charges were known, before any torsion):**
the binding charge scheme is MBIS-only. Löwdin remains a reported
diagnostic and is not used to score the hypothesis. The frozen
hypothesis and falsifier were not changed.

No scan energy or scan charge had been generated when this amendment
was written.

## 2026-08-24 — scan complete; claim

Eighteen of eighteen scan points converged (optking True and a clean
exit) on the 0–120° / 15° grids of CF3COO− and CCl3COO−. The published
abscissa is the frozen target `angle`. Derived amplitudes, 0°/120°
repeats, and barriers live in `metrics.json` and are produced only from
the committed CSVs.

**Claim (not rewritten after seeing q(O) and q(COO) split):** under
B3LYP-D3(BJ)/aug-cc-pVDZ, MBIS, gas phase, the CX3 rotation does not
move carboxylate oxygen charge with a larger amplitude for CCl3COO−
than for CF3COO−. The hypothesis is not supported. Oscillation, if any,
is at the 10⁻⁴ e scale. It did not reproduce for us under these
conditions.

This is a claim about our hypothesis and this scan. It is not a claim
that Johnson et al. are wrong, that hyperconjugation is absent at their
DDEC6/MP2/aug-cc-pVQZ minima, or that a pKa mechanism has been tested.
