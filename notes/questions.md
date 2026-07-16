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

## Does anything I report depend on the bits that moved?
- **Observed:** The closing question of the temperature-zero note, unanswered and
  currently rhetorical. It is only a real question against a specific reported
  number — an eval delta, an estimate, a measured constant.
- **Source:** `/posts/2026-07-16-temperature-zero-is-not-determinism.html` (own next step)
- **Type:** quantification
- **Falsifier:** the reported quantity is stable across reruns to more digits than are quoted
- **Status:** observation — needs a concrete target before it is a question
