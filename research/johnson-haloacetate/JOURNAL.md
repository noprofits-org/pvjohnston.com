# Journal — Johnson-haloacetate

Lab notes for the rematch gate, the binding-scheme amendments, and the
relaxed CX3 scan. The 2026-08-23 freeze is in `PREREGISTRATION.md`.
This file is the dated record. Do not read it back into the frozen
bullets.

## 2026-08-24 — before first energy

Hirshfeld is not compiled into this Psi4 1.11 build. Binding charges
for the rematch gate are MBIS and Löwdin. Gate (3) required both
schemes: rematch MBIS and Löwdin q(O) and q(COO) more negative for CF3
than for CCl3. If both fail, do not scan.

The other rematch inequalities, unchanged: r(C–C) satisfies CCl3 > CF3
> acetate; Δ(C–X) (out-of-plane minus in-plane) satisfies CCl3 > CF3.

## 2026-08-24 — rematch finished

All four rematch optimizations formally converged (optking True and a
clean exit): CH3COO−, CF3COO−, CClF2COO−, CCl3COO−. Committed numbers
are in `rematch/summary.csv`.

- r(C–C): CCl3 > CClF2 > CF3 > acetate. Pass.
- Δ(C–X) oop−ip: CCl3 > CF3. Pass. CClF2 is mixed and is not used for
  this comparison. Acetate has no C–X pair of that kind.
- MBIS q(O) and q(COO): CF3 more negative than CCl3. Pass.
- Löwdin q(O) and q(COO): reversed. Fail.

## 2026-08-24 — before any torsion

Löwdin on aug-cc-pVDZ is ill-defined (oxygen charges sit near zero
while MBIS sits near −0.7 e) and reversed the CF3/CCl3 order. Löwdin
is demoted to a reported diagnostic. Binding is MBIS-only.

The "both must pass" / "if both fail, do not scan" pair is vacated:
those two sentences disagreed once one scheme passed and one failed.
The frozen hypothesis and falsifier in `PREREGISTRATION.md` were not
rewritten.

No scan energy or scan charge had been generated when this amendment
was written.

## 2026-08-24 — post-scan, after both grids

Eighteen of eighteen scan points converged (optking True and a clean
exit) on the 0–120° / 15° grids of CF3COO− and CCl3COO−. The published
abscissa is the frozen target `angle`. Derived amplitudes, signed
120°−0° differences, and barriers live in `metrics.json` and are
produced only from the committed CSVs.

We score falsifier 2 on mean q(O) because the frozen question named
oxygen charge. q(COO) is still reported separately and splits the
other way. This adjudication is post-scan. It is not a silent edit to
the frozen falsifier.

**Claim:** under B3LYP-D3(BJ)/aug-cc-pVDZ, MBIS, gas phase, the CX3
rotation does not move carboxylate oxygen charge with a larger
amplitude for CCl3COO− than for CF3COO−. The hypothesis we registered
is not supported. Oscillation, if any, is at the 10⁻⁴ e scale.

This is a claim about our hypothesis and this scan. It is not a claim
that Johnson et al. are wrong, that hyperconjugation is absent at their
DDEC6/MP2/aug-cc-pVQZ minima, or that a pKa mechanism has been tested.
Johnson et al. invited this rotation; they did not publish this
amplitude.
