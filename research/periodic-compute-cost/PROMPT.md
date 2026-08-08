# Runner prompt — periodic-compute-cost

Paste or point a fresh session at this file. It executes the experiment
specified in `design.md` in this directory. The design doc is the contract;
this file is the order of operations.

## Standing instructions

1. Read `AGENTS.md` at the repo root and follow it — worktree discipline,
   journal discipline, close-out checklist. Work happens on the existing
   `post/periodic-compute-cost` branch in its worktree
   (`../pvjohnston-worktrees/periodic-compute-cost`); if that worktree is
   gone, recreate it from the branch per the AGENTS.md recipe.
2. Read `research/periodic-compute-cost/design.md` **in full** before
   writing any code. Every protocol decision (basis, spin table, timeouts,
   stop rule, repeat policy, recorded fields) is specified there — do not
   re-derive or silently change them. If a protocol item proves impossible
   as written, log the deviation with `research-log.mjs decision` before
   working around it.
3. Resume the research journal session
   `20260808T021400Z-compute-cost-of-the-periodic-table-e-f247`
   (`node scripts/research-log.mjs resume --session ...`); checkpoint after
   environment setup, after the pilot, after each completed tier, and
   before any context compaction.

## Order of operations

### 1. Environment (checkpoint when done)

- Create a venv under `research/periodic-compute-cost/.venv` (git-ignored;
  add to `.gitignore` inside the experiment dir if needed). Install
  `pyscf` and `numpy` via pip, then freeze: `pip freeze >
  research/periodic-compute-cost/requirements.lock.txt`.
- Copy `research/_TEMPLATE/environment.example.md` to `environment.md` and
  fill it for this machine (Linux x86_64, i7-1165G7, 16 GB, single-thread
  env vars, CPython version, pyscf version). Note AC power and CPU
  governor at sweep time.
- Smoke test: UHF on H and on O (spin 2) completes and matches literature
  ballpark (O UHF/def2-SVP ≈ −74.8 Eh region).

### 2. Runner implementation

Two scripts in this directory:

- `probe_one.py` — child process. Args: symbol, Z, spin, tier, basis.
  Runs the single probe per design §3, prints one JSON object to stdout
  (all fields from design §3 "Recorded per run", including peak RSS from
  `resource.getrusage` and UHF ⟨S²⟩). Never writes files.
- `sweep.py` — parent. Owns the element/spin table (design §6, with the
  parity sanity check), the tier list, the per-run timeout (900 s), the
  repeat policy, and the two-consecutive-failures stop rule. Appends one
  line per run to `results/runs.jsonl`. **Resumable:** on start it reads
  the JSONL and skips (element, tier, repeat) triples already recorded, so
  a killed sweep continues rather than restarts.

Run everything with `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1`.

### 3. Pilot before committing to the sweep

Run tiers UHF and CCSD(T) for Z ∈ {1, 2, 6, 10, 18} only. Check: JSONL
fields all populated, timings plausible, repeats consistent to ~10%.
Checkpoint with the pilot numbers. Only then launch the full sweep.

### 4. Full sweep

Tier order: UHF, PBE, MP2, CCSD, CCSD(T), FCI — cheapest first, so partial
results are useful early. Expect HF/DFT to finish all 54 elements and the
expensive tiers to hit the stop rule; a tier dying is a result, not an
error. The whole sweep may take hours of wall time — run it in the
background, monitor, and checkpoint per tier with: last surviving Z, total
tier wall time, any unconverged elements.

### 5. Analysis

`analyze.py` producing the four figures of design §5 into `results/`
(post-ready copies later go to `images/periodic-compute-cost-*.png` per
authoring guide). Fit α per tier as specified. Then `generate-metrics.mjs`
(copy from `research/_TEMPLATE`) projecting: last surviving Z per tier,
total sweep CPU time, fitted α per tier vs formal exponent — validated
against `research/metrics.schema.json`.

### 6. Wrap up

- Compare outcomes against the five predictions in design §4; record hits
  and misses in the journal — misses are the interesting part.
- Fill `PUBLIC_FILES.txt` (template in `research/_TEMPLATE`).
- Commit on `post/periodic-compute-cost`. Do **not** draft the post unless
  asked; the deliverable of the run session is data, figures, metrics, and
  an updated journal. Close out per AGENTS.md.

## Guardrails

- Nothing here touches shared files: stay inside
  `research/periodic-compute-cost/**` (and later `images/` +
  `posts/` only when drafting is requested).
- The 900 s timeout and 4 GB `max_memory` are hard limits — do not raise
  them to rescue a struggling run; the failure is data.
- If total sweep time is heading past ~6 h, stop, checkpoint, and report
  rather than trimming the protocol silently.
