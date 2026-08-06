# Coherence–hop boundary: reviewed artifact bundle

This bundle records a correction to an independent BMA[5,5]
conical-intersection sensitivity experiment motivated by Galiana and
co-workers' RP-AXE trajectory-reuse method. It is not a reproduction of their
glycine calculations or locally modified SHARC program.

## Outcome

The original 28-run sweep stored
`mean(2 * abs(conj(c_minus) * c_plus))`. That is the mean magnitude of
single-trajectory coherence, not a phase-sensitive ensemble density-matrix
element. Its coefficient phases were not archived, so the sweep cannot support
an optical- or pump-generated-coherence conclusion after the fact.

A corrective amendment froze an explicit real adiabatic gauge, stored signed
real and imaginary ensemble components, and required an eight-paired-seed
fine/finer gate before any new production run. Seven checks passed. The
centroid 95% envelope was `0.03860456796330737 sigma_x`, above the unchanged
`0.03 sigma_x` limit. The gate failed, so no corrective exact audit or 28-run
production sweep was performed. The phase-sensitive hypothesis is
**inconclusive**.

The archived sweep is retained under a strict local-magnitude contract as
descriptive FP–RP evidence. Its own coarse/fine early-event difference was
`0.021625746684215907`, above the registered `0.02` tolerance, and the fine
endpoint had no fine/finer audit. It is not presented as numerically converged.

## Two artifact lanes

### Corrective phase-sensitive lane

- `results/lineage.json` checks that the refactored simulator preserves the
  ancestor's dynamics and original local-magnitude diagnostic.
- `results/convergence.json` contains eight candidate and eight finer-reference
  runs with signed ensemble density-matrix components. It is a failed gate,
  not a production result.
- Redundant event copies and per-trajectory event-count arrays were removed
  after the gate. Observable series, accepted-event times, compact counts,
  per-seed comparisons, and every registered gate input remain.
- No corrective `exact` or `sweep` artifact exists because the stopping rule
  prohibited them.

### Archived local-magnitude lane

- `results/legacy-convergence.json` is the recovered original coarse/fine gate.
- `results/exact.json` and `results/sweep.json.gz` are the archived exact audit
  and 28-run sweep, now bound to the mean single-trajectory magnitude
  interpretation.
- Their correction metadata records the original source SHA-256. Wall-clock
  runtimes and generation timestamps were removed deterministically.
- Ordered FP and AXE event sequences were used to distinguish any repeated hop
  from a true return to the trajectory's initial active state.
- The exact reference audits spatial grid resolution and norm, not timestep or
  periodic box size. RP-AXE also uses twice as many nuclear paths as FP, so its
  exact-reference ranking is not an equal-cost comparison.

`results/analysis.json` keeps these lanes separate. `metrics.json` is the
validated reader-facing projection used by the post.

## Frozen question and stopping rule

- Post type: research
- Question: can reducing the PFM decoherence-rate multiplier create a regime
  in which at least half of accepted FP hops precede a phase-sensitive
  ensemble-coherence lifetime, and does RP-AXE remain equivalent to FP there?
- Corrected observable:
  `2 * abs(mean(conj(c_minus) * c_plus))`, reconstructed after pooling stored
  signed components in the gauge documented in `PREREGISTRATION.md`.
- Error limits: 0.05 in upper population, 0.05 in product probability, and
  `0.1 sigma_x` in centroid for the FP–RP decision.
- Mandatory numerical gate: eight paired seeds at `s=0.05`, comparing
  0.0125 fs / twenty electronic substeps with 0.00625 fs / forty substeps.
- Stopping rule: any registered gate failure makes the corrective experiment
  inconclusive and blocks the exact audit and seven-scale production sweep.

The gate failed and that stopping rule was followed.

## Reproduce the reviewed analysis

From the repository root in the pinned environment:

```sh
export OPENBLAS_NUM_THREADS=1

python3 -m unittest discover \
  -s research/coherence-hop-boundary/tests -p 'test_*.py'

python3 research/coherence-hop-boundary/src/review_analysis.py \
  --check \
  --figure images/2026-08-04-conical-intersection-outrun-decoherence-hero.png

node research/coherence-hop-boundary/generate-metrics.mjs --check
node scripts/verify-bib.mjs
node scripts/verify-metrics.mjs
```

The analysis verifies both artifact fingerprint groups, independently
recomputes the corrective convergence gate, checks the source-hash link from
the archived exact and sweep files to the recovered legacy convergence gate,
and validates corrected recrossing labels against event order.

## Reproduce the artifact corrections

The original PR head is permanent commit
[`77a27f6d06058067826b98130921229e31dfdb01`](https://github.com/noprofits-org/pvjohnston.com/commit/77a27f6d06058067826b98130921229e31dfdb01).
It is the direct parent of the corrective commit, but the commands below use
commit-pinned raw GitHub URLs as well, so artifact recovery does not depend on
the object already being present in a shallow local clone. They transform the
legacy artifacts without rerunning production trajectories:

```sh
python3 research/coherence-hop-boundary/src/correct_artifacts.py \
  legacy-convergence \
  --url https://raw.githubusercontent.com/noprofits-org/pvjohnston.com/77a27f6d06058067826b98130921229e31dfdb01/research/coherence-hop-boundary/results/convergence.json \
  --output research/coherence-hop-boundary/results/legacy-convergence.json

python3 research/coherence-hop-boundary/src/correct_artifacts.py \
  legacy-exact \
  --url https://raw.githubusercontent.com/noprofits-org/pvjohnston.com/77a27f6d06058067826b98130921229e31dfdb01/research/coherence-hop-boundary/results/exact.json \
  --output research/coherence-hop-boundary/results/exact.json

python3 research/coherence-hop-boundary/src/correct_artifacts.py \
  legacy-sweep \
  --url https://raw.githubusercontent.com/noprofits-org/pvjohnston.com/77a27f6d06058067826b98130921229e31dfdb01/research/coherence-hop-boundary/results/sweep.json.gz \
  --output research/coherence-hop-boundary/results/sweep.json.gz
```

Each output is deterministic and stores the SHA-256 of its source bytes.

## Reproduce the corrective gate

`simulate.py convergence` returns a nonzero status when the registered gate
fails. That is the expected scientific result here, not a crashed run:

```sh
OPENBLAS_NUM_THREADS=1 python3 \
  research/coherence-hop-boundary/src/simulate.py lineage \
  --output research/coherence-hop-boundary/results/lineage.json

OPENBLAS_NUM_THREADS=1 python3 \
  research/coherence-hop-boundary/src/simulate.py convergence \
  --lineage research/coherence-hop-boundary/results/lineage.json \
  --workers 4 --restart \
  --output research/coherence-hop-boundary/results/convergence.raw.json

python3 research/coherence-hop-boundary/src/correct_artifacts.py convergence \
  --input research/coherence-hop-boundary/results/convergence.raw.json \
  --output research/coherence-hop-boundary/results/convergence.json
```

Do not run `exact-audit` or `sweep` after the failed gate. The raw convergence
file is a resumable working artifact; the compacted result is canonical.

## Determinism and provenance

The registered environment is Linux x86-64, CPython 3.12.9, NumPy 2.2.5, and
`OPENBLAS_NUM_THREADS=1`; plotting uses Matplotlib 3.10.8 and Pillow 12.1.0.
Declared seeds determine Wigner sampling and hopping streams independently of
worker completion order. Canonical scientific artifacts exclude wall-clock
metadata. Deterministic JSON ordering, gzip `mtime=0`, a fixed metrics
source-date epoch, and source hashes make clean transformations byte-stable.

`PUBLIC_FILES.txt` is the reader-facing routing allowlist. No credentials,
external services, living subjects, private data, or laboratory hardware are
involved.

## Files

- `PREREGISTRATION.md` — original protocol, corrective amendment, one fixed
  replication extension, and terminal gate result.
- `config.json` — frozen parameters and thresholds used by the corrective gate;
  its bytes remain unchanged after the run because its hash is embedded in the
  artifact.
- `src/simulate.py` — phase-sensitive simulator and registered gates.
- `src/correct_artifacts.py` — deterministic legacy repair and convergence
  compaction.
- `src/review_analysis.py` — dual-lane reviewed analysis.
- `src/analyse.py` — shared numerical validation and figure functions.
- `tests/` — simulator, analysis, artifact-correction, and deterministic-gzip
  tests.
- `results/` — canonical lineage, corrective convergence, legacy convergence,
  legacy exact, legacy sweep, and reviewed analysis artifacts.
- `generate-metrics.mjs`, `metrics.json`, `environment.md`, `requirements.txt`,
  `sources.json`, `PUBLIC_FILES.txt`, and `LICENSE` — publication and execution
  boundary.
