# The shelf — open questions and unexplained observations

Nothing gets drafted that was not sitting here first (`blog-authoring.md` §0).
This is a lab notebook, not a content calendar: entries are logged **when the
anomaly happens**, before there is an explanation. The explanation is the post.

Three sources feed it — **anomalies** (didn't reproduce, didn't match,
surprised you), **standing** (your published work, your methods, data only you
can see), and **next steps** (every Conclusion names the next experiment; that
sentence lands here).

An entry is ready to pull when it has a candidate `contribution:` sentence and a
falsifier. Until then it is an observation, which is fine — most entries sit for
a while, and the shelf is supposed to be deeper than the cadence.

Format:

```
## <short handle>
- **Observed:** what actually happened, with the number
- **Source:** what it rubs against (paper, post, doc, your own prior work)
- **Type:** falsification | decay | unplotted line | quantification | untested regime | composition | negative result
- **Contribution (candidate):** X, which is not in [source]
- **Falsifier:** the outcome that would kill it
- **Status:** observation | ready | drafting | published <link>
```

---

## Neumaier decay in the canonical FP-nonassociativity demo
- **Observed:** He's published snippet returns 102 unique sums on CPython 3.13.12
  and would return 258 on ≤3.11 — `sum()` became Neumaier-compensated in 3.12
  (gh-100425). On all-float input the demo's phenomenon vanishes entirely (1
  unique result). It survives only because the source's array literal mixes an
  `int` `1` with floats.
- **Source:** He & Thinking Machines Lab, *Defeating Nondeterminism in LLM Inference* (2025)
- **Type:** decay
- **Status:** published — `/posts/2026-07-16-temperature-zero-is-not-determinism.html`

## Does the Neumaier change silently break other published FP demos?
- **Observed:** Generalizes the above. A large body of teaching material and blog
  writing demonstrates float non-associativity via Python's builtin `sum()`. Any
  of it written pre-2023 and run post-3.12 now measures a compensated
  accumulator. Unknown how many such demos are affected, or how many now print
  something other than what their prose claims.
- **Source:** the corpus of FP-nonassociativity demos; CPython gh-100425
- **Type:** decay (survey)
- **Contribution (candidate):** a measured count of how many widely-circulated
  demos silently changed behaviour at 3.12 — which nobody has enumerated
- **Falsifier:** nearly all such demos avoid builtin `sum` (use numpy/torch/explicit
  loops), making the effect a curiosity rather than a systematic decay
- **Status:** observation — needs a corpus before it is a question

## The unplotted line: divergence rate vs batch size
- **Observed:** He reports a single point — 1,000 completions at temperature zero
  gave 80 unique outputs, diverging at token 103. The *shape* of the relationship
  between batch size and divergence onset is never plotted, though it is the
  paper's own mechanism.
- **Source:** He & Thinking Machines Lab (2025)
- **Type:** unplotted line
- **Contribution (candidate):** divergence onset as a function of batch size,
  which the source asserts a mechanism for but never measures
- **Falsifier:** onset is flat in batch size, or dominated by prompt rather than batch
- **Blocked on:** a GPU. Rentable; not owned. Do not report as first-hand without one.
- **Status:** observation

## SIREN's underperformance in Villatoro et al. may be an initialization artifact
- **Observed:** §2.3.2 records that "the official SIREN Python implementation's
  initialization ... [differs from] the initialization scheme described in [32]",
  states "the network is sensitive to how it is initialized", and then adopts a
  *third* scheme from [35] without measuring what any of it costs. Separately they
  test ω₀ ∈ {5,10,20}, report "no meaningful difference", and then **run at ω₀=30 —
  a value outside the range they tested**. SIREN folklore holds ω₀ is *the*
  critical knob; "insensitive to ω₀" and "sensitive to initialization" are in
  tension. A load-bearing conclusion rests on this: "SIREN networks ... generally
  underperform relative to KAN and MLP."
- **Source:** Villatoro, Geraci & Schiavazzi, *J. Comput. Phys.* **565** (2026) 115170, §2.3.2 / §4
- **Type:** quantification (asserted sensitivity, never measured) → possible falsification
- **Contribution (candidate):** the measured cost of the SIREN paper-vs-repo
  initialization discrepancy in the multi-fidelity setting, and ω₀ sensitivity
  across {5,10,20,30} — neither of which the paper measures, though its
  SIREN-underperforms conclusion depends on both
- **Falsifier:** all three init schemes and all four ω₀ produce statistically
  indistinguishable HF MSE on K1–K4 → the discrepancy is cosmetic, SIREN's
  underperformance is architectural, and the paper's conclusion stands unharmed
- **Publish the other outcome?** Yes — "SIREN really does underperform, and here
  is the sensitivity data proving it isn't the init" is the useful null result
  the paper skipped.
- **Feasibility:** high. 1D closed-form test pair (eq. 4, the Forrester-type
  function), nets of 1×8 to 3×16, CPU-only. Paper's own runs: 180–230 s/train.
- **Status:** published — `/posts/2026-07-17-the-siren-that-was-a-straight-line.html`.
  Mechanism half only. Measured: specified scheme gives hidden pre-activation std
  0.036 vs ≈1 for both Sitzmann conventions at ω₀=30, compounding to 0.0018 by
  layer 2. Narrowed on the way: `siren-pytorch` [35] passes ONE w0 to both its
  initializer and its activation, so the degenerate config is nearly unreachable
  from the library — the defect is in the paper's prose, not necessarily its
  results. Did NOT claim otherwise. The cost half is the next entry.

## Does the SIREN spec degeneracy actually cost accuracy?
- **Observed:** Next step from the post above. A preliminary numpy training pilot
  (3×16, K1 HF, Adam, 15k epochs, **fixed lr=1e-3**, 4 reps) suggested the
  degenerate network *outperforms* both intact schemes at ω₀=30 — e.g. N_H=32:
  specified 5.1e-5 vs described 1.3e-2 vs official 1.6e-1 normalized MSE. Plausible
  reading: a linear hidden stack is fewer effective DOF, which regularizes in the
  8–32-sample regime where a true high-frequency SIREN overfits.
- **Why it is not yet a result:** the pilot is confounded. The paper tunes lr per
  configuration with Hyperopt over log[1e-5,1e-1]; at fixed lr a network that
  *fails to train* is indistinguishable from one that *overfits*, and the intact
  schemes scored >1.0 normalized MSE at ω₀=30, which smells like optimization
  failure rather than overfitting. Not reported in the post for that reason.
- **Source:** own next step; Villatoro et al. (2026) §2.7 (Hyperopt protocol)
- **Type:** quantification
- **Contribution (candidate):** the accuracy cost of the specification degeneracy
  under per-configuration lr tuning — i.e. whether the linear hidden stack helps
  or hurts once the optimizer confound is removed
- **Falsifier:** with lr tuned per config, intact and degenerate schemes reach
  statistically indistinguishable test MSE → the degeneracy is accuracy-neutral
  and the post's finding stays purely a specification defect
- **Needs:** an lr sweep per config (~4×the pilot's compute, still minutes), and
  ideally the MF architecture rather than single-fidelity HF fitting, since the
  paper's SIREN claim is about the MF setting
- **Blocked on (soft):** the authors' repo, to check spec-vs-code. Unreleased as of
  2026-07-16 ("shared upon acceptance"; accepted 2026-06-29).
- **Status:** ready

## Does the NTK mechanism actually predict Table 5?
- **Observed:** §2.4 attributes encoding's benefit to NTK eigenspectrum reshaping
  ("NTK-based analysis [51] *suggests* ... allowing the network to represent
  high-frequency components of F that are otherwise suppressed by spectral bias")
  and confirms only the *outcome*, never the mechanism — no NTK is ever computed.
  §4 makes a further spectral claim qualitatively: KAN good across all frequency
  ranges, MLP preferential for low-frequency, SIREN for high-frequency
  oscillation. Meanwhile **Table 5 is a published 15-case ledger of exactly where
  encoding helped (K3, K4, 2DU, GJG9) and where it hurt or was unnecessary (K1,
  K5)**. The hypothesis predicts that ledger. Nobody has checked whether it does.
  §5 concedes the theory "remains an open problem".
- **Source:** Villatoro, Geraci & Schiavazzi (2026), §2.4 / Table 5 / §5
- **Type:** unplotted line
- **Contribution (candidate):** measured NTK eigenspectra for encoded vs
  unencoded MF networks, tested against the paper's own published help/hurt
  ledger — the mechanism the paper asserts from a citation and never computes
- **Falsifier:** encoding leaves the eigenspectrum statistically unchanged, or
  the spectral shift does not track Table 5's help/hurt column (i.e. it fails to
  predict that encoding *harms* K1 and is unnecessary for K5)
- **Feasibility:** medium. Tiny nets make the NTK Gram cheap; MLP and SIREN are
  straightforward (Jacobian outer products), KAN is not — scope to MLP+SIREN and
  say so.
- **Risk:** the metric choice (effective rank vs eigenvalue decay exponent) is a
  judgement call and must be fixed *before* running, or this becomes curve-fitting.
- **Status:** ready

## How slowly must you pump an anomalous soliton before quantization breaks?
- **Observed:** Tao, Wang & Xu report a new *anomalous* nonlinear Thouless pump —
  a soliton displaced by 0, −2 or −3 unit cells per cycle while the Bloch band it
  comes from has Chern number −1. The mechanism is a transition between Wannier
  functions **by passing through an intersite-soliton state**. Adiabaticity is
  asserted and never quantified: "in the adiabatic limit—where θ is varied very
  slowly", "when θ is varied **sufficiently slowly** ... the results **closely
  resemble** the instantaneous solutions". **No pump period T appears anywhere in
  the paper**, and no displacement-vs-ramp-rate curve is plotted.
- **Why the gap is glaring:** quantization breakdown is an established subfield the
  paper itself cites three times — Walter et al., *Quantization and its breakdown
  in a Hubbard–Thouless pump* (Nat. Phys. 19, 1471, 2023) [10]; Fu et al.,
  *Nonlinear Thouless pumping: solitons and transport breakdown* (PRL 128, 154101,
  2022) [37]; Tuloup et al., *Breakdown of quantization in nonlinear Thouless
  pumping* (New J. Phys. 25, 083048, 2023) [40]. They introduce a new pumping
  mechanism and never ask where *its* quantization breaks.
- **Physical reason to expect a difference:** the anomalous pump routes through an
  intersite-soliton state — a bifurcation where solution branches nearly touch.
  Adiabatic following through a near-degeneracy is exactly where it should be
  fragile. The normal pump (following a single Wannier function) has no such
  passage.
- **Source:** Tao, Wang & Xu, *Nat. Commun.* (2026), doi:10.1038/s41467-026-73460-y
  (Article in Press, accepted 2026-05-13)
- **Type:** unplotted line / quantification
- **Contribution (candidate):** the critical pump period for quantized anomalous
  soliton transport, and whether it exceeds the normal pump's — which the paper
  asserts as "sufficiently slowly" and never measures, in a mechanism it proposes
  for cold-atom experiment
- **Falsifier:** the critical pump period T_c is the same, within a factor of ~2,
  for the normal case (g=g₁₂=m₀=1, displacement −1) and the anomalous case
  (g=1, g₁₂=0, m₀=1, displacement −2). The anomalous mechanism then carries no
  extra adiabaticity cost and the paper's silence is harmless.
- **Publish the other outcome?** Yes — "the anomalous pump is no more fragile than
  the normal one" is directly useful to the experimentalists they are pitching
  (they propose a ⁷Li BEC, 1316 atoms, a_s ≈ −1.43 nm, a = 532 nm, ω_⊥ = 2π×710 Hz),
  since experiments have finite coherence time. A null here is a green light.
- **Stakes:** they argue the effect "can be experimentally observed". Any adiabatic
  protocol has to fit inside a coherence budget. If the anomalous pump needs 10×
  the normal pump's ramp, that is a design constraint nobody has stated.
- **Feasibility:** high, numpy-only. Fully specified discrete model:
  Eq. (2) H^lin(k) = (m_z + J₁cos k)σ_z + J'₁ sin k σ_y + J₂σ_x, with
  m_z = m₀ + cos θ, J₁ = J'₁ = 1, J₂ = sin θ; Eq. (1) DNLS with
  V_σj = g|ψ_σj|² + g₁₂|ψ_σ̄j|²; N = 1.45. ~40–80 sites × 2 components.
  Needs a hand-rolled Newton solver (no scipy) + RK4/split-step integrator.
- **Source data is declared but NOT reachable (checked 2026-07-16).** The paper
  cites Figshare doi:10.6084/m9.figshare.32182566 [65], but the DOI 404s, the
  Figshare API 404s on both the DOI and the article id, and a title search returns
  zero hits — presumably embargoed until the Article in Press becomes final. My
  earlier note that the data "IS released" was wrong. The gate therefore cannot be
  checked against their numbers and must stand on independent validation of the
  model instead (Chern numbers; Wannier centers at l+1/2; the exact flat-band
  solution at theta=pi). Same shape as the SIREN post's unreleased code: declared
  available, not actually reachable.
- **GATE (do this before anything else):** reproduce Fig. 2a's four displacements —
  −1 (black: g=g₁₂=m₀=1), 0 (blue: g=−1, g₁₂=0, m₀=1), −2 (red: g=1, g₁₂=0, m₀=1),
  −3 (gold: g=1, g₁₂=0, m₀=1.3). If the baseline does not reproduce, stop and
  report; a T_c measured against a wrong soliton is worthless.
- **Caveat:** "Article in Press", unedited — "there may be errors present which
  affect the content". Fine for a physics-of-the-model question; would NOT support
  a text-vs-code claim like the SIREN post, since the text is not final.
- **Status:** published — `/posts/2026-07-17-how-slowly-must-you-pump-an-anomalous-soliton.html`.
  **Numbers below are the CONVERGED rerun** (2026-07-17) after a code review (Codex +
  a Claude review) caught that the first version built Table 3 from a single
  under-resolved dt=0.03 scan. H **supported**: T_c = 1200 (normal) vs 5200
  (anomalous), ratio 4.33, outside the factor-of-2 falsifier. Above threshold the
  normal pump leaves the ±0.15 band once in 28 (T=9200, by 0.19); the anomalous pump
  leaves it 9 of 18, worst +0.35 at T=9200 (a −2 pump moving the wrong way), scatter
  13× larger. Both pumps deviate most at T=9200 → resonance fingerprint (next entry).
  Reproduced 3 of 4 displacements (−1, 0, −2); case 3 (−3) not reproduced — see below.
  Lesson recorded: [[reference-numerics-check-the-integrator-first]] — right
  integrator, wrong step size, table built from a coarser scan than the spot-check.

## What sets the anomalous pump's excursion periods?
- **Observed:** Next step from the post above. The anomalous displacement leaves the
  quantized value at specific periods (T = 8400–10800, worst −3.41 at T=9600) and
  returns to −1.98 by T=12000 — deterministic (a 1e-8 initial perturbation moves it
  by 0.0000), dt-converged under 4th-order Yoshida, and with the soliton intact
  (|z| > 0.91 throughout). So it is a smooth function of T with structure, not noise.
- **Candidate mechanism:** a resonance between the pump frequency 2π/T and the
  splitting between the soliton branches that nearly touch at θ=π. That splitting is
  computable from the Jacobian of the stationary problem, which
  `downloads/soliton-pump-code.tar.gz` already builds.
- **Source:** own next step; Tao, Wang & Xu (2026)
- **Type:** unplotted line
- **Contribution (candidate):** the rule that predicts which pump periods fail —
  turning "pump slowly enough" into a list of periods to avoid, which is what an
  experimentalist actually needs
- **Falsifier (fix before running):** the excursion periods show no relation to any
  integer multiple of the branch splitting → the resonance picture is wrong and the
  structure has another origin
- **Needs:** the stationary Jacobian's spectrum near θ=π, and a finer T grid than
  400 to resolve excursion widths
- **Status:** ready

## Why does case 3 (m0=1.3, displacement −3) not reproduce at all?
- **Observed:** From the post above. Every period tested gives values nowhere near
  −3; at T=9600 it converges to −19.33 across dt = 0.04/0.02/0.01, i.e. the soliton
  slides ~19 cells per cycle. Not a convergence failure and not delocalization
  (|z| ≈ 0.95).
- **Likely cause:** the θ=0 branch I seed (staggered envelope, μ = −1.1375,
  participation 6.49) may not be the branch the authors follow. The paper notes case
  3's window is narrow (0 ≤ g12 ≤ 0.01 at m0=1.3), so branch identity matters more here.
- **Type:** falsification (of my own reproduction, first) — resolve before claiming
  anything about the paper
- **Needs:** pseudo-arclength continuation through the branch point to trace which
  instantaneous branch connects to θ=0, rather than naive θ-stepping (which jumps
  branches near θ=π — observed: max|Δx| per step 0.44 at dθ=0.0044)
- **Status:** observation

## Does anything I report depend on the bits that moved?
- **Observed:** The closing question of the temperature-zero note, unanswered and
  currently rhetorical. It is only a real question against a specific reported
  number — an eval delta, an estimate, a measured constant.
- **Source:** `/posts/2026-07-16-temperature-zero-is-not-determinism.html` (own next step)
- **Type:** quantification
- **Falsifier:** the reported quantity is stable across reruns to more digits than are quoted
- **Status:** observation — needs a concrete target before it is a question

## Does the h/p-adaptive SPH speedup reach an order of magnitude at equal accuracy?
- **Observed:** Ricci, Vacondio, and Fourtakas state that their h/p-adaptive SPH
  formulation reduces cost by up to an order of magnitude. In the three-dimensional
  vortex-ring case they identify two equal-accuracy resolution pairs in prose and
  report the corresponding normalized run times in a separate table, but never join
  those values into equal-accuracy speedups.
- **Source:** Ricci, Vacondio, and Fourtakas, *J. Comput. Phys.* **565** (2026)
  115192, Table 3 and the paragraph immediately below it
- **Type:** quantification
- **Contribution (candidate):** an equal-accuracy cost ledger for the paper's two
  explicit vortex-ring resolution matches, which the source's own timing data
  supports but the source never calculates
- **Falsifier:** either matched pair gives a speedup of at least 10 when the reported
  normalized run times are divided
- **Publish the other outcome?** Yes — a measured tenfold saving would make the
  paper's headline claim more concrete rather than less useful.
- **Status:** drafting

## What is the full cost-accuracy Pareto frontier for h/p-adaptive SPH?
- **Observed:** Figure 8 of Ricci, Vacondio, and Fourtakas plots drag-history
  error against normalized wall-clock time for the impulsively started cylinder,
  but the plotted errors are not tabulated and the paper does not report the
  equal-error speedup along the curve.
- **Source:** Ricci, Vacondio, and Fourtakas, *J. Comput. Phys.* **565** (2026)
  115192, Figure 8 and Table 1
- **Type:** unplotted line
- **Contribution (candidate):** a pre-thresholded equal-error Pareto frontier for
  the cylinder runs, including the maximum supported speedup, which is not in
  the source
- **Falsifier:** the h/p curve does not Pareto-dominate the Lagrangian curve at
  the declared error threshold, or its maximum matched speedup remains below 10
- **Status:** observation — needs the authors' raw Figure 8 error values or a
  documented plot-digitization uncertainty model
