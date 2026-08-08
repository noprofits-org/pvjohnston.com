# The compute cost of the periodic table — experiment design

**Question.** How much compute does it take to understand the periodic table
of elements — and how does that cost scale with atomic number?

**Form.** `post-type: understanding`. The post explains how the cost of
quantum-chemical "understanding" is structured, using a sweep over the
elements as the computational demonstration. No contribution gate applies,
but the demonstrations must be reproducible and the scope bounded (below).

**Status.** Designed, not yet run. `PROMPT.md` in this directory is the
handoff to the session that runs it.

---

## 1. Making the question well-posed

"Understand an atom" is not one task. Quantum chemistry is a ladder of
theories, each a stricter notion of understanding with a different formal
price:

| Tier | Method | What it buys | Formal cost in basis size N |
| --- | --- | --- | --- |
| Mean field | UHF | Each electron in the average field of the rest | ~N⁴ |
| Density functional | UKS/PBE | Correlation via an approximate functional | ~N³–N⁴ |
| Perturbative correlation | MP2 | Leading correction to mean field | ~N⁵ |
| Coupled cluster | CCSD | Infinite-order pair correlation | ~N⁶ |
| "Gold standard" | CCSD(T) | Perturbative triples on CCSD | ~N⁷ |
| Exact within the basis | FCI | Every determinant the basis supports | exponential |

The experiment runs **the same probe at every tier for every element**: the
ground-state energy of the neutral, isolated atom at Hund's-rule spin
multiplicity, in a fixed basis-set family. The measured variable is not the
energy — it is the wall time, CPU time, and peak memory the probe consumes,
plus whether it converges at all.

The plot is therefore a *family* of curves (one per tier), atomic number on
x, cost on log-y. The answer to the title question is the family itself:
"understanding" is priced per tier, and the tiers scale differently.

**Hydrogen anchors the ladder at zero.** H is analytically solvable — its
Schrödinger equation costs a page of algebra and no floating point. The
numerics in this experiment exist entirely because of electron number two.
The post should open there.

## 2. Scope and bounds

- Elements Z = 1–54 (H through Xe). Lanthanides are excluded: f-shell
  near-degeneracies make single-reference methods unreliable in ways that
  would contaminate a timing study with method-failure noise.
- Non-relativistic Hamiltonian for Z ≤ 36; scalar-relativistic effects for
  Z ≥ 37 enter only implicitly through the basis family's effective core
  potentials (next section). The post must state this bound on the word
  "understand": past krypton, even our best tier is not the full physics.
- Isolated atoms only. No molecules, no chemistry — this measures the cost
  of the atoms themselves.
- Everything runs on the one laptop (11th-gen i7-1165G7, 8 hardware
  threads, 16 GB RAM). The wall for each tier is *this machine's* wall,
  which is the point of the experiment.

## 3. Protocol

### Software

PySCF in a fresh pinned venv (pip on linux/x86_64; record exact versions in
`environment.md` per `research/_TEMPLATE/environment.example.md`). PySCF is
chosen because HF, DFT, MP2, CCSD, CCSD(T), and FCI all sit behind one API,
so the probe differs across tiers only in the method call.

### The probe, per (element, tier)

1. Build the atom: neutral, spin = number of unpaired electrons from the
   table in §6, basis **def2-SVP** for all tiers except FCI.
2. Run UHF. Correlated tiers (MP2, CCSD, CCSD(T)) run on top of the
   converged UHF reference; their recorded cost **includes** the UHF step,
   because that is what the tier costs a user.
3. FCI runs in def2-SVP too, no frozen core. Its determinant space grows
   combinatorially in electrons × orbitals; it is *expected* to die around
   Z ≈ 12–14, and the death is data.
4. If SCF fails to converge: one retry with a documented fallback (level
   shift and/or second-order SCF), and both attempts' iteration counts and
   outcomes are recorded. A convergence failure after fallback is recorded
   as `converged: false`, not silently skipped.

### Timing hygiene

- Every run is a **fresh subprocess** — no JIT/cache warmth bleeding
  between elements, and a hard timeout can kill it cleanly.
- Single-threaded: `OMP_NUM_THREADS=1` (and MKL/OpenBLAS equivalents), so
  wall time ≈ CPU time and the numbers are about the algorithm, not the
  scheduler. Record both anyway; a persistent gap flags I/O or paging.
- `mol.max_memory = 4000` (MB) inside PySCF; hard timeout **900 s** per
  run enforced by the parent process.
- Runs with wall < 60 s are repeated 3×; the median is the headline number
  and all repeats are kept in the raw log. Slower runs execute once.
- Record the machine state once per sweep (CPU model, governor, AC power,
  load average) — a laptop that thermally throttles mid-sweep would bend
  the curves.

### Stop rule

Per tier, ascend Z until **two consecutive elements fail** (timeout, memory
cap, or unconverged-after-fallback), then stop that tier. Cheap tiers (HF,
DFT) are expected to finish all 54; expensive tiers die where they die —
the last surviving Z per tier is a headline result.

### Recorded per run (JSONL, append-only, resumable)

`Z`, symbol, tier, basis, spin, `n_basis_functions`, `n_electrons`
(explicit, i.e. after any ECP), wall seconds, CPU seconds, peak RSS,
SCF iteration count, converged flag, fallback-used flag, total energy
(Hartree), timestamp, repeat index, and outcome
(`ok | timeout | oom | unconverged`).

## 4. Predictions — what the curves should show

Stated before running, so the run can confirm or surprise:

1. **A staircase, not a slope.** Basis-function count jumps at each new
   shell (row of the table) rather than growing smoothly with Z, so cost
   vs Z should be piecewise with visible steps at Z = 3, 11, 19, 37.
2. **A cliff at Z = 37.** The def2 family replaces core electrons with an
   effective core potential from rubidium onward. Explicit electron count
   *drops* at Z = 37 (Rb carries 9 explicit electrons; Kr carries 36), so
   rubidium should cost **less** than krypton. If observed, this is the
   post's best moment: the field affords heavy elements by approximating
   the core away, and the cost curve shows the seam.
3. **Difficulty ≠ size.** Transition metals (Sc–Zn, and especially Cr and
   Fe) should show inflated SCF iteration counts and fallback activations
   relative to their basis size — convergence pathology, not arithmetic.
   Plotting iterations vs Z separately from time vs Z separates "big"
   from "annoying."
4. **Empirical exponents undershoot formal ones.** Fitting
   log(time) ~ α·log(N_basis) per tier should give α below the textbook
   exponent (7 for CCSD(T), etc.), because at laptop scale prefactors,
   integral evaluation, and Python overhead dominate. The gap between
   formal and measured α is the honest laptop-scale answer, and the reason
   to plot cost against **N_basis** as well as against Z.
5. **FCI hits an exponential wall near Z ≈ 12–14**; CCSD(T) survives well
   past it; HF and DFT finish the whole sweep in minutes each.

Any prediction that fails is not a bug in the experiment — it is the more
interesting result and gets reported as such.

## 5. Analysis and figures

- **Fig. 1 (headline):** wall time vs Z, log-y, one line per tier, failure
  points marked where each tier dies. Annotate the Z=37 cliff if present.
- **Fig. 2:** wall time vs N_basis, log–log, with per-tier fitted slopes α
  against the formal exponents.
- **Fig. 3:** SCF iterations (and fallback events) vs Z — the difficulty
  map, expected to spike in the d-block.
- **Fig. 4 (optional):** peak memory vs Z per tier; memory, not time, is
  what actually kills FCI.
- Metrics for the post go through `generate-metrics.mjs` →
  `metrics.json` per `research/metrics.schema.json`; headline metrics:
  last surviving Z per tier, total sweep CPU-hours, fitted α per tier.

## 6. Hund's-rule spin table (unpaired electrons, Z = 1–54)

Ground-state configurations including the standard Aufbau exceptions
(Cr, Cu, Nb, Mo, Ru, Rh, Pd, Ag). Value is 2S = number of unpaired
electrons; PySCF `spin` takes exactly this number.

| Z | El | 2S | Z | El | 2S | Z | El | 2S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | H | 1 | 19 | K | 1 | 37 | Rb | 1 |
| 2 | He | 0 | 20 | Ca | 0 | 38 | Sr | 0 |
| 3 | Li | 1 | 21 | Sc | 1 | 39 | Y | 1 |
| 4 | Be | 0 | 22 | Ti | 2 | 40 | Zr | 2 |
| 5 | B | 1 | 23 | V | 3 | 41 | Nb | 5 |
| 6 | C | 2 | 24 | Cr | 6 | 42 | Mo | 6 |
| 7 | N | 3 | 25 | Mn | 5 | 43 | Tc | 5 |
| 8 | O | 2 | 26 | Fe | 4 | 44 | Ru | 4 |
| 9 | F | 1 | 27 | Co | 3 | 45 | Rh | 3 |
| 10 | Ne | 0 | 28 | Ni | 2 | 46 | Pd | 0 |
| 11 | Na | 1 | 29 | Cu | 1 | 47 | Ag | 1 |
| 12 | Mg | 0 | 30 | Zn | 0 | 48 | Cd | 0 |
| 13 | Al | 1 | 31 | Ga | 1 | 49 | In | 1 |
| 14 | Si | 2 | 32 | Ge | 2 | 50 | Sn | 2 |
| 15 | P | 3 | 33 | As | 3 | 51 | Sb | 3 |
| 16 | S | 2 | 34 | Se | 2 | 52 | Te | 2 |
| 17 | Cl | 1 | 35 | Br | 1 | 53 | I | 1 |
| 18 | Ar | 0 | 36 | Kr | 0 | 54 | Xe | 0 |

The runner must sanity-check this table at build time: electron count
minus 2S must be even for every element, and the UHF ⟨S²⟩ of each
converged run should be recorded so gross spin contamination is visible.

## 7. Known caveats to carry into the post

- **Open-shell atoms in UHF symmetry-break.** Atoms with partially filled
  p or d shells have degenerate ground terms; single-determinant UHF picks
  one component and may break spherical symmetry. Fine for a *timing*
  study, but the energies are not term-resolved spectroscopy, and the post
  must say so.
- **One basis family, one code.** The measured curves are def2-SVP + PySCF
  curves. The *shapes* (staircase, cliff, exponents, walls) are the claim;
  the absolute seconds are not.
- **DFT tier is one functional (PBE).** The point of the tier is cost
  structure, not functional quality.
- **This is pedagogy with measurements, not novel research** — which is
  exactly what the Understanding form is for. The site's Research bar
  (novel contribution) is deliberately not claimed. If the Z=37 cliff or
  the empirical-exponent gap turns out unexpectedly rich, a follow-up
  question can go on the shelf in `notes/questions.md` afterward.

## 8. Stretch goals (only if the main sweep is comfortable)

- A second HF sweep in def2-TZVP to separate "more electrons" from "bigger
  basis per electron."
- A frozen-core FCI track to show how far the wall moves when the core is
  bought off.
- Cost per electron (time / Z) as a fifth figure — is understanding an
  electron getting cheaper or dearer as atoms grow?
