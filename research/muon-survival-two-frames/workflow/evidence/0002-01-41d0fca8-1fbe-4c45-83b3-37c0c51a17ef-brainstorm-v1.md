# Brainstorm handoff: version 1

- **Graph state:** `brainstorm`, iteration 1.
- **Actor and role:** `research-brainstormer-muon-trial`, configured
  `research_brainstormer` session.
- **Declared form:** Understanding. No shelf entry, novelty claim,
  contribution sentence, hypothesis, falsifier, publish-the-other-outcome
  commitment, or scientific verdict applies.
- **Parent state:** workflow initialization event 1; no accepted submission or
  review snapshot exists yet.
- **Protocol:**
  `research/muon-survival-two-frames/PREREGISTRATION-v1.md`, 19383 bytes,
  SHA-256
  `501f57ab496229a7e3d2f04ae0a087681718bf0792438edfc6eed0920d7ac377`.
- **Git commit used:** `ba15276d15968082df75061d31a9bf4ab81084e4`.
- **Outcome:** not inspected; no exploratory survival calculation, canonical
  execution, analysis, plot, metric, or post prose was produced.

## Work completed

The packet freezes the explanatory question, assumed audience,
dependency-ordered route, two independent frame reconstructions, explicit
one-proper-time interpretation, same-speed/no-lifetime-dilation
counterfactual, Monte Carlo purpose and boundary, model stopping point,
external-source provenance, digital inputs, exact constants, grid, focal
index, RNG, seed, draw count, comparison semantics, observables, checks,
failure handling, analysis route, environment intent, budgets, figure and
metric contents, artifact expectations, pilot separation, restart/retry
boundary, public-file constraints, and no-human-subject/no-external-dataset
conditions.

All suggested scientific choices were retained. The main role-boundary choice
is that the run operator generates and seals only the registered proper
lifetime sample and provenance; an admitted sample is later analyzed by a
different role. No production reroll or registered analysis rerun is allowed.

## Sources checked

- Particle Data Group 2024 muon listing:
  `https://pdg.lbl.gov/2024/listings/rpp2024-list-muon.pdf`; 135593 bytes;
  SHA-256
  `a3653f756a670b41a215b4a9746e6b5d872fe798a478e233acfc0bc1715eeb03`.
  Verified the listed mass central value and uncertainty and the listed proper
  mean-lifetime average and uncertainty. The protocol freezes only the central
  values and discloses that it does not propagate their uncertainty.
- Particle Data Group 2024 Cosmic Rays review:
  `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmic-rays.pdf`; 2588758
  bytes; SHA-256
  `c8f0620d58d3d61a7b0eae5d2606ce65bbe581a9000c5435299d88ca9ea0125e`.
  Checked only the bounded context around charged-pion production of shower
  muons and muon passage through the atmosphere. No shower or flux quantity
  enters the protocol.

Both PDFs were accessed 2026-08-08 from the exact requested URLs. They are
literature/provenance sources, not an external production dataset, and are not
to be bundled.

## Commands and checks

- Read `AGENTS.md`, `notes/blog-authoring.md`,
  `notes/computational-authoring-workflow.md`, `notes/questions.md`,
  `notes/research-journal.md`, `notes/worktrees.md`, the configured role file,
  and relevant experiment templates in full.
- Ran workflow `status` and experiment-scoped `verify` before authoring;
  state was `brainstorm`, event count 1, and verification passed.
- Ran journal `show` and `verify`; the supplied journal was open and valid.
- Retrieved each exact PDG URL with `curl -fsSL` and hashed the response bytes;
  inspected HTTP content length and modification metadata.
- Inspected the available base interpreter and repository dependency precedents.
  The base has CPython 3.12.3 but no NumPy; the protocol therefore requires a
  fresh locked environment and a hard runtime version check.
- Recomputed the protocol SHA-256 and byte count and scanned it for local home,
  temporary, scratch, mounted-data, and cache paths; none were found.
- No scientific expression was numerically evaluated and no expected survival
  answer was targeted or recorded.

## Unresolved risks

1. `numpy==2.5.1` and `matplotlib==3.11.1` are frozen environment targets but
   are not installed in the base interpreter. Setup must resolve them into a
   hash-locked environment and demonstrate exact runtime rejection on version
   mismatch before approval.
2. The two PDG constants are prospectively transcribed facts. Setup must create
   the machine-readable constants and source manifests, validate units and
   digests, and test that code consumes those files rather than duplicate
   literals.
3. A fixed random sample can genuinely miss either Monte Carlo tolerance. The
   protocol intentionally forbids rerolling, adding draws, or weakening the
   gate; an unexplained failure blocks the intended publication.
4. The right figure panel must show coincident exponents without hiding that
   the component distances, times, and lifetimes differ. Analysis review must
   challenge the visual encoding and rounding directly.
5. The upstream URLs are mutable. Their frozen digests make drift detectable
   but cannot guarantee future availability; the committed constants keep the
   calculation runnable while the source manifest must disclose that limit.

## Exact questions for `question_review`

1. Is Understanding the honest form, with no concealed empirical or novelty
   claim, and is the explanatory question narrow enough to finish at the
   declared model boundary?
2. Does the dependency route make the detector-frame and muon-frame
   reconstructions genuinely independent enough to catch a coding or units
   mistake, while explaining them as one proper-time interval rather than two
   mechanisms?
3. Are the detector-frame and muon-frame equations dimensionally correct, and
   are the pointwise relative-error definitions unambiguous at zero and
   nonzero path?
4. Does the same-speed counterfactual hold speed fixed, omit only lifetime
   dilation, and carry labels strong enough to prevent readers from treating it
   as a physical third frame?
5. Does one PCG64 sample, reused as nested thresholds over the grid, serve only
   as an implementation check of exponential decay? Is the analytic-probability
   binomial standard error and inclusive four-standard-error gate fully frozen?
6. Do the monotonic-count, grid-wide discrepancy, schema, manifest,
   provenance, hash, regeneration, and PNG checks close the material degrees of
   freedom without encoding an expected result?
7. Are the PDG values, units, URLs, access date, byte counts, digests, central-
   value treatment, and strictly bounded use of the cosmic-ray review accurate?
8. Are the run-operator boundary, no-reroll rule, all-or-nothing run namespace,
   one objective infrastructure retry, and no registered analysis rerun
   consistent with the graph's execution and amendment rules?
9. Are the locked environment intent, one-minute/10 MB/no-cost budgets, artifact
   plan, public-data constraints, and no-living-subject statement feasible and
   proportionate?
10. Does the registered two-panel 1200 by 630 PNG do necessary explanatory work
    and comply prospectively with the site's figure and caption rules?

## Stage retrospective

- **Clarified by the handoff:** Separating the immutable proper-lifetime sample
  from later frame reconstruction makes the operator/analyst boundary concrete;
  spelling out the counterfactual prevents it from becoming an implicit model.
- **Useful boundary:** The prohibition on viewing production during setup is
  meaningful even here because the tempting shortcut is to run the tiny script
  while writing it and then tune presentation around the observed sample.
- **Duplication or ceremony:** The source identifiers and hashes appear in both
  the private journal and public protocol. That duplication is defensible for
  recovery versus provenance, but many handoff-template fields are inapplicable
  before the first run.
- **Tempting bypass:** The arithmetic is simple enough that combining setup,
  execution, and analysis feels natural. The independent algebra and seed
  freeze are the parts that justify resisting that shortcut; the value of every
  later full-graph gate remains to be measured by the trial.
- **Preliminary keep/change/remove:** Keep prospective protocol and setup review;
  consider a reduced but independently reviewed lane for tiny Understanding
  demonstrations; later evaluate whether separate run and run-review receipts
  add evidence beyond hashes and deterministic regeneration. Remove nothing on
  this branch.
- **Approximate effort:** about 40 minutes elapsed, dominated by required guide
  reading, exact-source verification, and closing protocol ambiguities rather
  than by the physics.

## Requested transition

Submit this packet to a fresh read-only `independent_reviewer` for
`question_review`. The coordinator should first inspect workflow status,
checkpoint the journal with the explicit next action, verify the ledger and
current evidence, and then invoke the state-changing `submit` command. This
producer does not approve the packet or advance workflow state.
