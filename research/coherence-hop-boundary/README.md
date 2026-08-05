# Coherence–hop boundary

This bundle asks whether Galiana and co-workers' pulse-independent RP-AXE
trajectory reuse remains accurate when most accepted surface hops overlap a
surviving optically prepared electronic coherence. It is an independent
sensitivity benchmark on a fixed two-state BMA[5,5] conical-intersection
model, not a reproduction of the source authors' glycine calculations.

The protocol was frozen in `PREREGISTRATION.md` after explicitly separated
feasibility pilots and before the lineage, convergence, exact-grid, or
confirmatory runs. Pilot seed 1701 never enters the confirmatory estimates.

## Question and boundary

- Post type: research
- Question: at a fixed molecular Hamiltonian and launch packet, can reducing
  the PFM decoherence-rate multiplier produce a finite-lifetime regime in
  which at least half of accepted full-propagation hops precede the
  pump-coherence lifetime, and does RP-AXE remain within all three declared
  error limits there?
- Contribution gate: an adjudicated RP-AXE sensitivity test in a regime where
  most accepted surface hops precede the pump-coherence lifetime, jointly
  scored by electronic population, product-side probability, and nuclear
  centroid against exact dynamics, which is not reported by Galiana et al. or
  Grell et al.
- Contribution type: untested regime
- Hypothesis: lowering the rate multiplier will produce at least one
  finite-lifetime majority-early-hop regime, and RP-AXE will exceed at least
  one declared FP–RP error limit there.
- Falsifier: no declared setting reaches an uncensored early-hop fraction of
  0.5, or every setting that reaches it stays within all three limits: 0.05 in
  upper-state population, 0.05 in product-side probability, and
  0.1 initial nuclear standard deviations in the centroid.
- What this experiment can establish: the sensitivity of FP, RP-AXE, and their
  exact-dynamics errors to an explicitly algorithmic PFM rate multiplier in
  this fixed reduced model and launch distribution.
- What it cannot establish: a new molecular decoherence rate; the accuracy of
  the authors' locally modified SHARC implementation; glycine, LiH, or
  dithiane dynamics; a laboratory pump–probe observable; or a literal
  single-molecule photon-counting trace. There is no explicit laser field or
  detector model here.
- Traceability: **traceable**. Result-bearing prose resolves through the
  validated `metrics.json` projection of the canonical analysis.
- Highest reproduction level: **end-to-end reproducible** in the documented
  pinned environment. The documented command chain produced the canonical
  results, deterministic analysis, figure, and verified metrics projection.
- Archived-evidence or rerun constraints: the upstream papers provide method
  descriptions and supporting PDFs, but no public patch for the authors'
  local SHARC modifications, raw molecular trajectories, or reusable RP-AXE
  implementation was identified. The present bundle therefore follows an
  independently implemented model lineage.

## Source and implementation lineage

The direct source-response anchor is Galiana et al., *Accounting for Electronic
Coherences Induced by Broadband Pulses by Using Pulse-Independent
Trajectories*, J. Chem. Theory Comput. 22 (2026) 1224–1243,
doi:10.1021/acs.jctc.5c01809. Grell et al., *Advances in the Projected Forces
and Momenta Decoherence Method for Attosecond Nonadiabatic Molecular
Dynamics*, Faraday Discuss. (2026), doi:10.1039/D6FD00086J, is the companion
application source. Their public articles and supporting PDFs bound the source
comparison; their molecular code and data are not inputs to this run.

`src/simulate.py` descends from the independent implementation distributed
with the preceding blog experiment at
`downloads/pulse-independent-ci-data.tar.gz`. The frozen base is repository
commit `b527db4` (`b527db4a4f31012f751981f580e27bca763f9e54`) and the archive's
SHA-256 is
`eb8a7ed3e13c0c02a6872da57f23317a541c764d44f060902b0874b8e99e29d0`.
The checked-out ancestor `downloads/pulse-independent-ci.py` has SHA-256
`9a62440a32f99057f699ec9de8c58fc2a19e0bf78f0848fd8826d1b23aa72350`.
Before any new inference, the lineage gate loads that file directly, checks its
bytes, then wraps its hop function at runtime to observe accepted events without
modifying the ancestor. It compares the new `s=1` path on the same small
deterministic input. Accepted-hop trajectory, time, and direction records must
be identical and observable arrays must agree with
`rtol=1e-12` and `atol=1e-12`. The archive checksum remains the provenance
identifier for the complete earlier bundle.

## Frozen design

The Hamiltonian, initial real electronic superposition, Wigner widths, center
`qx,0/(a/2)=0.5`, zero momentum kick, and 20 fs duration are fixed. The only
swept quantity is the dimensionless PFM rate multiplier
`s = [1, 0.5, 0.25, 0.125, 0.10, 0.075, 0.05]`. It multiplies an approximate
algorithmic decoherence rate; it is not a molecular parameter and must not be
interpreted as one.

Each setting uses fresh deterministic seeds 2701–2704 and 4,000 matched Wigner
geometries per seed. The planned production setting is a 0.025 fs nuclear step
with ten electronic substeps. Before the sweep, independent seed 2699 and
4,000 geometries at `s=0.05` compare that setting with 0.0125 fs and twenty
substeps. Any failed convergence criterion promotes the finer setting for all
seven scales; no criterion is relaxed.

One invariant exact wavepacket serves every scale because neither the
Hamiltonian nor launch state changes. The production trace uses a 384 by 384
periodic Fourier grid over `[-96,96)^2`; a 512 by 512 trace audits population,
product probability, centroid, and norm. A failed audit promotes the 512 by
512 trace to the production reference.

The primary decision uses the four-seed mean FP and RP observable series.
Accepted FP hop-event times are concatenated across seeds, and the coherence
lifetime is the first linearly interpolated crossing of `C(0)/e` in the
four-seed mean coherence. The early-hop fraction counts accepted events at or
before that lifetime and divides by every accepted FP event through 20 fs.
Repeated hops remain events. A missing crossing is right-censored; a censored
lifetime or zero accepted events produces a null fraction and cannot qualify
for the majority gate.

The primary nuclear observable is the maximum FP–RP difference in
`P(qx < 0)`. Upper-state population and centroid error are mandatory parts of
the compound robustness decision. Secondary outputs include FP and RP RMSE
against exact dynamics, coherence error, per-seed intervals, proposed,
frustrated, accepted, first, repeat, early, and late hop diagnostics, hop
direction, electronic norm, coefficient/active-state consistency, and energy
drift.

## Run

Run from the repository root in this order. The canonical artifacts were
produced with this sequence; the same sequence is the end-to-end reproduction.

```sh
OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/simulate.py \
  lineage --output research/coherence-hop-boundary/results/lineage.json

OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/simulate.py \
  convergence \
  --lineage research/coherence-hop-boundary/results/lineage.json \
  --output research/coherence-hop-boundary/results/convergence.json

OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/simulate.py \
  exact-audit \
  --lineage research/coherence-hop-boundary/results/lineage.json \
  --convergence research/coherence-hop-boundary/results/convergence.json \
  --output research/coherence-hop-boundary/results/exact.json

OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/simulate.py \
  sweep --workers 4 \
  --lineage research/coherence-hop-boundary/results/lineage.json \
  --convergence research/coherence-hop-boundary/results/convergence.json \
  --exact research/coherence-hop-boundary/results/exact.json \
  --output research/coherence-hop-boundary/results/sweep.json

python3 research/coherence-hop-boundary/src/archive_json.py
python3 research/coherence-hop-boundary/src/archive_json.py --check
```

The archive step stores the complete 146 MB sweep as a deterministic 11 MB
`sweep.json.gz` publication artifact. It preserves the uncompressed JSON byte
for byte; `analyse.py` reads the archive directly. The transient uncompressed
file may be removed after the archive check.

Do not start convergence or production if the lineage gate fails. Inspect the
convergence result before the sweep; the simulator must use the promoted finer
setting everywhere if any registered numerical criterion fails.

Rebuild the canonical analysis from the committed run records, then generate
and check publication metrics:

```sh
OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/analyse.py \
  --figure images/2026-08-04-conical-intersection-outrun-decoherence-hero.png
OPENBLAS_NUM_THREADS=1 python3 research/coherence-hop-boundary/src/analyse.py --check
node research/coherence-hop-boundary/generate-metrics.mjs
node research/coherence-hop-boundary/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

## Data and publication

`PUBLIC_FILES.txt` is the reviewed reader-facing routing allowlist. It includes
the protocol, environment, code, tests, canonical JSON records (with the sweep
deterministically gzip-compressed), analysis, and
metrics projection in the completed bundle. The post figure is routed
by the site's normal image rule and is intentionally absent from this manifest.
Publisher PDFs and supporting files are not redistributed; they are literature
evidence, not executable inputs. `sources.json` records the resulting
software-level reproduction boundary.

No credentials, external services, living subjects, private data, or
laboratory hardware are involved.

## Files

- `PREREGISTRATION.md` — frozen pilot disclosure, confirmation protocol,
  gates, outcomes, and stopping rule.
- `config.json` — machine-readable frozen constants, thresholds, and paths.
- `src/simulate.py`, `src/archive_json.py`, `tests/test_simulate.py`, and
  `tests/test_archive_json.py` — parameter-safe simulator, deterministic sweep
  archiving, artifact controls, and tests.
- `src/analyse.py` and `tests/test_analysis.py` — deterministic analysis and
  checks.
- `results/lineage.json`, `convergence.json`, `exact.json`, `sweep.json.gz`, and
  `analysis.json` — canonical records.
- `generate-metrics.mjs` and `metrics.json` — reader-facing projection.
- `environment.md`, `requirements.txt`, `sources.json`, `PUBLIC_FILES.txt`,
  and `LICENSE` — execution boundary, dependencies, provenance, routing, and
  BSD-3-Clause terms.
