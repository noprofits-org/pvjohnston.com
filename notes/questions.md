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

## Does anything I report depend on the bits that moved?
- **Observed:** The closing question of the temperature-zero note, unanswered and
  currently rhetorical. It is only a real question against a specific reported
  number — an eval delta, an estimate, a measured constant.
- **Source:** `/posts/2026-07-16-temperature-zero-is-not-determinism.html` (own next step)
- **Type:** quantification
- **Falsifier:** the reported quantity is stable across reruns to more digits than are quoted
- **Status:** observation — needs a concrete target before it is a question
