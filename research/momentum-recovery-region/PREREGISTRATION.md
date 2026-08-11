# Preregistration: the described SIREN convention's momentum recovery region, width vs beta

Frozen 2026-08-11, before the canonical run. Question pulled from
`notes/questions.md` ("How wide is the described convention's momentum recovery
region in beta?"), the next step named by the momentum-control note
(`/posts/2026-07-19-the-momentum-control.html`).

## Intellectual contract

- Post type: research
- Question: as heavy-ball momentum beta varies, how wide is the set of learning
  rates at which the described Sitzmann convention reaches the official
  convention's error floor on K1 — does momentum's rescue of the described
  convention widen into a usable region or stay a knife-edge?
- Primary source and relationship to it: Villatoro, Geraci & Schiavazzi (2026),
  *Assessing the Performance of Correlation-Based Multi-Fidelity Neural
  Emulators*, via my own independent reimplementation (the SGD-control and
  momentum-control notes). This experiment is an extension of that
  reimplementation, not of the authors' code, which is unreleased.
- Contribution sentence and type: the recovery-region width as a function of
  beta in {0, 0.3, 0.6, 0.9, 0.99}, at 0.05-decade resolution with a
  0.01-decade refinement — the curve that says whether momentum's rescue of the
  described convention is usable or a knife-edge — which is not in the
  momentum-control note, the SGD note, or Villatoro et al. Type: quantification.
- Hypothesis: the recovery region widens monotonically (nondecreasing) with
  beta, riding the heavy-ball stability boundary, which the momentum-control
  note measured moving up by ~1+beta (1.995 at beta=0.9 vs the quadratic
  heavy-ball bound 2(1+beta)/L).
- Falsifier (verbatim from the shelf): the width does not vary monotonically
  with beta, or the described convention reaches the floor at no tested rate
  for some beta > 0.5.
- Why the other outcome is still publishable: a non-monotone width curve, or a
  rescue that vanishes at some beta > 0.5, is exactly the knife-edge verdict —
  it tells a practitioner not to rely on momentum to repair the described
  convention, and it falsifies the boundary-riding picture.
- What this experiment can establish: on K1 with this network, these seeds, and
  this optimizer, the width of the floor-hitting learning-rate set as a
  function of beta, and how the described convention's divergence boundary
  moves with beta relative to the 1+beta prediction.
- What it cannot establish: anything about other K-cases, other architectures,
  mini-batch or adaptive optimizers, or the authors' own code (unreleased); a
  zero width at finite grid resolution bounds the width from above, it does not
  prove the set is empty.

## Frozen protocol

- Exact inputs, versions, and acquisition: no external inputs. Model, task,
  data, seeds, initialization, and manual backprop are those of
  `downloads/siren-convention-momentum.py` (my prior work, committed), vendored
  into `src/run_sweep.py` without algorithmic change: K1 (eq. (4) of
  Villatoro et al.), N_H = 32 high-fidelity samples plus both endpoints,
  2000-point uniform test draw, 3 hidden layers of width 16, omega_0 = 30,
  c = 6, 20000 full-batch heavy-ball epochs, update v <- beta*v + g,
  theta <- theta - lr*v. Initialization RNG seeds 7000+rep, data seeds
  1000+17*32+rep, reps {0, 1, 2}. Environment: python3 + numpy on macOS arm64;
  exact versions recorded in `environment.md` at run time.
- Parameters, cases, seeds, repeats, and ordering: stage 1 = beta in
  {0, 0.3, 0.6, 0.9, 0.99} x {described, official} x 35-point grid
  logspace(1e-4, 10^-2.3, 0.05-decade spacing) x 3 reps = 1050 trainings.
  Execution order is arbitrary (multiprocessing); every cell's result depends
  only on its own seeds.
- Controls and ablations: the official convention runs at identical settings
  give the floor reference and the boundary comparison at each beta; beta = 0
  is the plain-SGD control measured by the same code path.
- Primary and secondary metrics: a stage-1 grid point counts as *recovered*
  when the median normalized test MSE over the 3 reps is <= 1e-24 (frozen
  threshold, ~3 orders above the official floor of 1e-28..2.5e-27 measured at
  beta = 0.9; sensitivity at 1e-20 and 1e-28 is recorded). Primary: recovered
  count per beta (width = count x 0.05 decades). Secondary: (a) refined width
  from stage 2; (b) per-beta described divergence boundary (lowest lr with any
  nonfinite rep), its ratio to the beta=0 boundary, against the 1+beta
  prediction {1, 1.3, 1.6, 1.9, 1.99}; (c) official median floor per beta.
- Stage 2 (frozen refinement rule): for each beta with at least one recovered
  stage-1 point, run a 0.01-decade grid from 0.10 decades below the lowest
  recovered lr up to the lowest lr at which any described rep diverged in
  stage 1 (inclusive; if no divergence was observed above the recovery region,
  the window ends 0.15 decades above its lowest recovered point), both
  conventions, same 3 reps. Stage-2 width = recovered count x 0.01 decades.
  A beta with no recovered stage-1 point gets no stage 2 and is recorded as
  zero recovered points at 0.05-decade resolution.
- Decision rule for supported / falsified / inconclusive: **supported** if the
  stage-1 recovered counts are nondecreasing in beta AND each beta in
  {0.6, 0.9, 0.99} has at least one recovered point. **Falsified** otherwise
  (the shelf falsifier). **Inconclusive** only if every stage-1 count is equal
  and the stage-2 widths also cannot separate them at 0.01-decade resolution.
- Exclusions and missing-data handling: none. A nonfinite training result is
  recorded as divergence, never excluded or rerun.
- Stopping rules: the protocol runs once to completion; no re-gridding beyond
  the frozen stage-2 rule and no threshold changes after results are seen.
- Exact production command: `python3 src/run_sweep.py` from this directory
  (single deterministic invocation computing stage 1, then stage 2 by the
  frozen rule).
- Expected raw and derived artifact paths: `results/stage1.json`,
  `results/stage2.json`; `metrics.json` derived by `generate-metrics.mjs`.

## Publication boundary

- Rights, privacy, secrets, and public-file review: no external data, no
  credentials, no living subjects; all artifacts are generated locally from
  committed code. `PUBLIC_FILES.txt` lists code, environment record, canonical
  results, metrics, and this preregistration — reviewed file by file.
- Reproducibility level this design can earn: end-to-end reproducible (one
  documented command reruns the experiment and regenerates its outputs).
- Archived-evidence or future-rerun constraints: none.

## Amendments

None at freeze.
