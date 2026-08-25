# PLAN excerpt — Johnson-haloacetate

Frozen 2026-08-23. Full hypothesis and falsifier are in
`PREREGISTRATION.md`. Dated binding-scheme notes and the post-scan
q(O) scoring call are in `JOURNAL.md`.

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

## Protocol

- Psi4 1.11, B3LYP-D3(BJ)/aug-cc-pVDZ, charge −1, singlet, gas phase.
- Intended charges at freeze: Hirshfeld and MBIS. Amendments in
  `JOURNAL.md`.
- Rematch first: CH3COO−, CF3COO−, CClF2COO−, CCl3COO−.
- Then relaxed φ = X–Cα–C–O scan, frozen dihedral 5-4-1-2, 0–120° by
  15°, on CF3COO− (M1) and CCl3COO− (M3).
- Inspect with `angle` as the abscissa.

## Gate and decision

See `PREREGISTRATION.md` for the frozen falsifier and `JOURNAL.md` for
the rematch-gate amendments and the post-scan scoring of falsifier 2.
Amplitude = max−min on both-converged points, separately for q(O) and
q(COO).
