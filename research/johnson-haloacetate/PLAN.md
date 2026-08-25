# PLAN excerpt — Johnson-haloacetate

Frozen before any torsion. Full hypothesis, falsifier, and gate are in
`PREREGISTRATION.md`. Dated binding-scheme notes are in `JOURNAL.md`.

## Question

Does carboxylate oxygen charge oscillate with CX3 rotation, with larger
amplitude for CCl3COO− than for CF3COO−?

## Source relationship

Johnson et al., *Chem. Sci.* **2025**, *16*, 2382–2390, reported
DDEC6/MP2/aug-cc-pVQZ charges in which CCl3 withdraws more from the
carboxylate oxygens than CF3, proposed carboxylate π → σ*(C–X)
hyperconjugation, cited ESI Table S2 bond-length signs, and invited
geometry/bond rotation studies. This plan takes that invitation. It is
not a rebuttal.

## Protocol (binding)

- Psi4 1.11, B3LYP-D3(BJ)/aug-cc-pVDZ, charge −1, singlet, gas phase.
- Binding charges: MBIS. Löwdin reported only. Hirshfeld not in build.
- Rematch first: CH3COO−, CF3COO−, CClF2COO−, CCl3COO−.
- Then relaxed φ = X–Cα–C–O scan, frozen dihedral 5-4-1-2, 0–120° by
  15°, on CF3COO− (M1) and CCl3COO− (M3).
- Inspect with `angle` as the abscissa.

## Gate, before any torsion

Pass if rematch r(C–C) is CCl3 > CF3 > acetate, rematch Δ(C–X)
(oop−ip) is CCl3 > CF3, and rematch MBIS q(O) and q(COO) are more
negative for CF3 than for CCl3.

## Decision

Amplitude = max−min on both-converged points, separately for q(O) and
q(COO). Score falsifier 2 on q(O). Disclose q(COO) alongside.
