# Preregistration: CEPB C=C increment spread

Frozen before the first production calculation. A single timing probe
(trans-2-butene, hand-built geometry, DF-CCSD(T)/cc-pVTZ) was run beforehand to
size the compute budget and was killed before completion; it produced no
retained number and none of its settings are inputs here.

## Source relationship

This is an independent reanalysis-plus-extension of Witkowski, Śmiga, Hirata,
Dral and Grabowski, "Ultrafast Correlation Energy Estimator," *J. Phys. Chem.
A* **129** (2025) 8877–8890, https://doi.org/10.1021/acs.jpca.5c04423 (CC BY).

The source fits 33 bond-type correlation-energy increments to CCSD(T)/CBS
correlation energies of 84 training molecules, under the model (their eq 1)

    E_corr(X) = sum_j n_j(X) * e_j

where `n_j(X)` counts bond type `j` in the dominant Lewis structure of `X` and
`e_j` is the fitted increment, with lone pairs carried as an extra "bond type".
The abstract states the assignment holds "regardless of the bond length, bond
angle, sp-hybridization, pi-electron conjugation, ionicity, noncovalent
interactions, etc.", qualified by "mainly suitable for near-equilibrium
geometries". The source also states that CEPB "fails to differentiate
positional isomers (e.g., butane vs isobutane)" and that for such isomers the
isomerization energy "collapses to the HF reaction energies".

This experiment does not refit the CEPB model, does not reproduce the source's
CBS extrapolation, and does not recompute any published increment. It asks two
questions the source's own framing raises but does not answer numerically.

## Questions, hypotheses, and falsifiers

**Arm A — spread in the source's own data (no new quantum chemistry).**
Question: how far apart are the effective C=C increments implied by the
source's published per-molecule correlation energies, across unsaturated
hydrocarbons of one bond-order class?

For a hydrocarbon with `n_CH` C–H bonds, `n_CC` C–C single bonds and `n_CC2`
C=C double bonds, the effective increment implied by a published correlation
energy is

    e_CC2_eff(X) = [ E_corr(X) - n_CH * e_CH - n_CC * e_CC ] / n_CC2

evaluated with the source's own fitted `e_CH` and `e_CC` at the same basis and
core treatment as `E_corr(X)`.

Hypothesis A: the effective increments are **not** transferable at chemical
accuracy — the spread (maximum minus minimum) across the registered set
exceeds 1.0 kcal/mol.

Falsifier A: the spread is at or below 1.0 kcal/mol, at every basis level for
which the source publishes the needed per-molecule energies. Conjugation- and
ring-independence would then hold within chemical accuracy in the source's own
data, and the criticism dies.

**Arm B — the positional-isomer zero prediction (new quantum chemistry).**
Question: how large is the correlation contribution to C4H8 positional
isomerization, which CEPB sets to exactly zero?

1-butene, cis-2-butene, trans-2-butene and isobutene each contain one C=C, two
C–C and eight C–H bonds, so CEPB assigns them identical correlation energies
and predicts a correlation contribution of exactly zero to every isomerization
among them. None of the four appears in the source's training set or its
18-molecule test set.

Hypothesis B: the correlation contribution is **not** zero at chemical
accuracy — at least one pairwise difference among the four isomers exceeds
1.0 kcal/mol in magnitude.

Falsifier B: all six pairwise correlation-energy differences are below
1.0 kcal/mol in magnitude at the registered level, and remain so under the
registered basis-sensitivity check. The zero prediction is then adequate
within chemical accuracy for this family.

The 1.0 kcal/mol threshold is an operational definition of a chemically
material difference, chosen before any calculation. The source does not claim
chemical accuracy and states no accuracy budget; the threshold is this
experiment's bar, not a restatement of the source's own target, and it is the
same bar used by the research-shelf entry that generated this question.

Both outcomes are publishable. A measured spread bounds how far the
transferability assumption can be pushed; a spread within chemical accuracy
strengthens the source's assignment on molecules it never fitted.

## Amendment 1 — contrast-based primary metric for Arm A

Recorded 2026-08-04, after the raw Arm A quantity above had been evaluated at
CBS during design review and before any contrast value was computed. The
research journal carries the disclosure and the number that was known at the
time; this section states what changes and why, and the post reports both
statistics side by side with their order of derivation.

The objection, raised independently by automated review and by the design
review itself: `e_CC2_eff` as defined above subtracts globally fitted C–H and
C–C increments from a whole-molecule correlation energy, so it attributes the
model's *entire* residual for that molecule to C=C. The attribution error
grows with the number of C–H and C–C bonds, which means a large spread across
molecules of different size does not by itself establish that the C=C
assignment is environment-dependent, and offsetting errors could equally mask
a real variation. The raw statistic is therefore demoted to a secondary,
explicitly descriptive result, reported as what it is: the whole-molecule CEPB
residual expressed per C=C bond.

The primary Arm A metric becomes a contrast in which every other bond class
cancels exactly. Three pairs in the source's published tables differ by
precisely the same bond-count swap, C=C → C–C + 2 C–H:

| contrast | bond-count change |
| --- | --- |
| ethene → ethane | +2 C–H, +1 C–C, −1 C=C |
| 1,4-cyclohexadiene → cyclohexene | +2 C–H, +1 C–C, −1 C=C |
| cyclohexene → cyclohexane | +2 C–H, +1 C–C, −1 C=C |

CEPB assigns every one of them the identical correlation change

    dE_corr(CEPB) = e_CC + 2*e_CH - e_CC2,

independent of ring size, conjugation and substitution. The measured quantity
is `dE_corr(X→Y) = E_corr(Y) - E_corr(X)` from the source's own published
per-molecule energies, and the primary statistic is the spread across the
three contrasts.

Hypothesis A (restated): the three contrasts do **not** share one value at
chemical accuracy — their spread exceeds 1.0 kcal/mol.

Falsifier A (restated): the spread across the three contrasts is at or below
1.0 kcal/mol at every basis level for which the source publishes all six
molecular energies. The swap is then environment-independent within chemical
accuracy in the source's own data, and the criticism dies.

These contrasts are formally isodesmic in bond type but not isogyric-balanced
by an explicit H2 term; because the same swap appears on both sides of every
comparison, the H2 correlation energy the source never states cancels from the
spread and is not needed. Basis-set incompleteness partially cancels within a
contrast but not between contrasts of different molecular size, which is why
the spread is required to hold at every available basis level rather than at
one.

## Frozen computational protocol

**Arm A** is arithmetic on transcribed published values. The source's
per-molecule correlation energies, its fitted increments, and its bond counts
are transcribed into `inputs.json` with checksums before analysis. Bond counts
are taken from the dominant Lewis structure, as the source specifies. Every
transcribed value is recorded with the basis level and core treatment its
source table declares, and increments are only ever combined with molecular
energies carrying the same declared level. Arm A runs at every basis level for
which the source publishes both the increments and all needed per-molecule
energies; the registered molecule set is every unsaturated acyclic and cyclic
hydrocarbon in the source's training and test tables whose Lewis structure
contains at least one C=C bond and only C–C, C=C and C–H bond types. Aromatic
benzene is analysed separately and never pooled into the primary spread,
because its dominant-Lewis-structure bond counts are convention-dependent.

**Arm B** is new computation, at one level throughout:

1. optimize each isomer with frozen-core density-fitted MP2/cc-pVTZ from a
   standard starting structure, to default Psi4 convergence;
2. compute frozen-core density-fitted CCSD(T)/cc-pVTZ at that geometry;
3. record the CCSD(T) correlation energy as
   `E_CCSD(T) - E_HF` at the same basis, taken from Psi4's own
   `CCSD(T) CORRELATION ENERGY` variable; and
4. form all six pairwise differences.

Registered basis-sensitivity check: repeat steps 1–3 at cc-pVDZ. The Arm B
verdict stands only if the sign of every pairwise difference is unchanged
between cc-pVDZ and cc-pVTZ and no pair crosses the 1.0 kcal/mol threshold in
opposite directions between the two bases. Propene and ethene are computed at
the same levels as secondary members of the effective-increment series and do
not enter the Arm B verdict.

The source's own reference level (all-electron CCSD(T), aug-cc-pVTZ /
aug-cc-pVQZ, Helgaker two-point CBS) is not reproduced: aug-cc-pVTZ on C4H8 is
368 basis functions and out of budget on the registered hardware. Arm B
therefore measures whether the zero prediction survives at a consistent
correlated level, not what the source's own protocol would return. This
boundary is stated in the post.

## Method-fidelity gate

The verdict is automatically inconclusive if any of the following occur:

- a geometry optimization fails to converge, or converges to a structure whose
  heavy-atom connectivity differs from the intended isomer;
- any CCSD(T) calculation fails to converge;
- the largest T1 diagnostic across the C4H8 set exceeds 0.02, indicating the
  single-reference treatment is not adequate for the comparison; or
- a transcribed source value fails its recorded checksum, or a transcribed
  molecular energy and increment are found to carry different declared basis
  levels.

## Primary and secondary outputs

Primary: the Arm A effective-increment spread in kcal/mol at each available
basis level; the six Arm B pairwise correlation-energy differences in
kcal/mol at cc-pVTZ; the pass/fail of each falsifier; and the
supported/falsified/inconclusive verdict for each arm, reported separately.

Secondary: per-molecule effective increments; the Arm B cc-pVDZ differences;
T1 diagnostics; total and Hartree-Fock energies; optimized geometries; and the
comparison between the source's regression-fitted C=C increment and the value
implied by ethene alone, which the source reports as differing by about 7%.

No outcome will be used to claim the source's fit is incorrect, to assert what
the authors should have computed, or to infer anything about bond types
outside the C–C / C=C / C–H set.

## Reproducibility and stopping

Runs execute serially. The run stops after the registered molecules and bases.
No threshold, molecule, basis, or level is added after results are inspected.
A failed fidelity gate is reported as inconclusive rather than repaired by
changing the protocol. If the source's published tables turn out not to
contain the per-molecule energies Arm A requires, Arm A is reported as not
executable rather than substituted with recomputed values.
