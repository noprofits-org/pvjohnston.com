# Why some atoms cost more than their neighbors — experiment design

**Question.** Why do chemically related and neighboring atoms take different
amounts of computation, even when we ask the same modest question of each one?

**Form.** `post-type: understanding`. This is a measured demonstration, not a
benchmark of every element and not a claim of new quantum chemistry.

**Audience.** A reader who knows periods, groups, and electron shells but does
not need prior experience running electronic-structure software.

**Status.** Protocol frozen before production. The separate run-and-monitor
session completed all 70 fixed attempts without retries or protocol changes;
the raw JSONL is commit `ca1e5bf`.

## 1. Explanatory route

The post will use three small comparisons rather than sweep the periodic table:

1. **Down a group:** more electrons and basis functions generally cost more.
   Halogens and alkaline earths provide matched open- and closed-shell
   examples.
2. **Across neighboring transition metals:** similar-sized atoms can require
   very different numbers of SCF iterations because their open shells admit
   competing occupations and broken-symmetry solutions.
3. **Across Kr/Rb:** the def2 family changes from an all-electron description
   to an effective core potential (ECP). The explicit electron count drops even
   though atomic number rises, exposing a modeling choice in the timing data.

A four-atom light-element subset then shows how cost changes when the same atom
is treated with a deeper correlation method. These methods are different
approximation families, not a strict ladder of guaranteed accuracy.

## 2. Fixed panel

The number in parentheses is PySCF's `spin = 2S` value.

| Panel | Atoms | UHF/PBE | MP2 | CCSD(T) | Purpose |
| --- | --- | --- | --- | --- | --- |
| Halogens | F(1), Cl(1), Br(1), I(1) | yes | yes | F, Cl | Open-shell size trend; Br/I cross the ECP seam |
| Alkaline earths | Be(0), Mg(0), Ca(0), Sr(0) | yes | yes | Be, Mg | Closed-shell size control; Ca/Sr cross the seam |
| Transition contrast | Cr(6), Mn(5), Fe(4), Zn(0) | yes | no | no | Three neighbors plus a closed-shell endpoint |
| Core boundary | Kr(0), Rb(1) | yes | yes | no | Direct all-electron/ECP contrast |

UHF and PBE run in two separate passes so their timing spread is visible. MP2
and CCSD(T) run once. This is a fixed matrix of 70 jobs: 56 survey jobs, 10 MP2
jobs, and 4 CCSD(T) jobs. There is no adaptive stop rule and no data-dependent
expansion.

## 3. Frozen calculation

- Neutral, isolated atoms at the nominal Hund-rule spin shown above.
- PySCF with `basis='def2-svp'`, spherical functions, point-group symmetry
  disabled, no density fitting, and no frozen core among the explicitly
  represented electrons.
- For Z <= 36, no ECP. For Z >= 37, explicitly set `ecp='def2-svp'`. The
  runner must verify that Kr has 36 explicit electrons and Rb has 9.
- UHF is `UHF`; PBE is `UKS` with `xc='PBE'` and grid level 3; MP2 is
  UHF + UMP2; CCSD(T) is UHF + UCCSD + perturbative triples.
- SCF settings are fixed: `conv_tol=1e-9`, `max_cycle=80`, `init_guess='minao'`.
  CCSD uses `conv_tol=1e-7` and `max_cycle=80`. There is no convergence
  fallback: failure under the common protocol is an observation, not an
  invitation to tune an element individually.
- Each attempt is a fresh, single-threaded subprocess. The reported calculation
  timer begins after Python/PySCF imports and includes molecule construction,
  SCF, and any requested correlation step.
- Parent timeout: 180 s per attempt. `mol.max_memory=3000` MB is an advisory
  PySCF setting, not a hard OS memory limit. FCI is deliberately excluded, so
  this phase does not intentionally drive the laptop into memory exhaustion.

The calculation targets a nominal spin-state solution. Spin alone does not
prove that an unrestricted calculation found the spectroscopic ground term.
The runner records alpha/beta electron counts and UHF/UKS `<S^2>` so the post
can state that boundary plainly.

## 4. Recorded data

One append-only JSONL row per attempt records the protocol version, phase,
panel, element, tier, repeat, basis/ECP choice, basis-function and explicit
electron counts, wall and CPU seconds, peak RSS, SCF iterations and convergence,
`<S^2>`, total energy, correlation convergence where applicable, timestamp,
and outcome. The parent writes timeout, crash, and malformed-output rows when a
child cannot report for itself. The job key includes the protocol version, so
old pilot rows cannot silently become production data.

## 5. What the post may conclude

Expected observations written before production, not hypotheses:

- Cost usually grows down a group, but the ECP can reverse that trend by
  replacing core electrons with an effective potential.
- Transition-metal SCF iteration counts need not vary smoothly with Z.
- Going from mean field or PBE to MP2 and CCSD(T) was expected to raise cost
  sharply even for light atoms.

The post should show all planned atoms, then use the clearest neighboring
contrasts to explain basis size, explicit electron count, occupation, and SCF
difficulty. Do not interpret differences comparable to the survey's
repeat-to-repeat spread. Do not fit textbook scaling exponents from this
heterogeneous panel.

Two figures should be enough:

1. grouped UHF/PBE timings with basis functions, explicit electrons, and SCF
   iterations available for explanation;
2. the method-depth comparison for the four light representatives.

> **Post-run review note.** The second figure was not made. On the four tiny
> atoms, PBE took longer than CCSD(T), while MP2 was comparable to UHF; these
> singleton correlation timings do not expose asymptotic method scaling. The
> post therefore keeps one figure and treats this failed ladder as a boundary,
> not as a cost trend.

This experiment does not price the whole periodic table, establish universal
hardware-independent timings, rank method accuracy, or produce term-resolved
atomic spectroscopy. Those are outside the post's boundary.

## 6. Session boundaries

- **Phase one (this session):** freeze this design; implement and validate the
  environment and runner; perform only tiny noncanonical smoke checks.
- **Run session:** execute the three fixed phases, monitor them, checkpoint each
  phase, and commit the raw JSONL. Do not analyze or draft.
- **Review/write session:** audit the completed rows, generate only the figures
  warranted by the data plus metrics, add citations, and write the
  Understanding post.
