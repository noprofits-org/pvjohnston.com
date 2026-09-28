# Borazine inverted-gap reproduction

Source: Shizu, Ishihara, Uratani, Kaji, "Inorganic benzenes with inverted singlet-triplet gaps",
Communications Chemistry (2026), doi:10.1038/s42004-026-02141-0 (CC BY 4.0).
SI1.pdf SHA-256: 2106a4fd1f0ebf32c4b2b4442bef9b000461f1aabb031dec274bbe13c4d9802f.

## Question and boundary

- Post type: research
- Status: running
- Question: does independent PySCF DF-ADC(2)/def2-TZVP on the published PBE0/6-31G(d)
  geometries reproduce the ADC(2) gaps for borazine (1), boroxine (11), 9, 10, 12 and 2a?
- Research falsifier: [PREREGISTRATION.md](PREREGISTRATION.md), P1/P2/S1.
- What this experiment can establish: agreement with the published ADC(2) column under the stated settings.
- What it cannot establish: SCS-CC2 or kF (not run by us), experimental ordering, or S1-geometry behaviour.
- Traceability: not yet established
- Highest reproduction level: none
- Archived-evidence or rerun constraints: the source SI is identified in sources.json;
  SCS-CC2 remains the authors' evidence. The current queue excludes 2b and 2c,
  following Peter's launch instructions; the supplied preregistration is preserved verbatim.

## Layout

- `xyz/`: all 57 S0 geometries from SI Tables 9–65, unchanged; index and basis counts included.
- `expected/published_SI_tables_1-3.csv`: the authors' published values, not our results.
- `tier1/`: supplied PySCF ADC(2), EOM-CCSD and optional ORCA inputs.
- `tier2/`: supplied Turbomole inputs; not run by us.
- `bench/`: supplied timing smoke tests used to size the jobs; not canonical results.

## Run

Calculations run outside the repository in `~/Molecules/ist-borazine/package/`,
using `~/Molecules/ist-borazine/.venv/`. The local launchd queue is started only
once the supplied preregistration has been frozen in the scaffold commit.
Its label is `com.pvjohnston.ist-borazine-tier1` and its runner is
`~/Molecules/ist-borazine/run_queue.sh` (wraps the queue in `caffeinate -ims`).

```sh
bash ~/Molecules/ist-borazine/run_queue.sh
```

The sequential order is ADC(2) 1, 11; EOM-CCSD 1, 11; ADC(2) 9, 10, 12;
EOM-CCSD 9, 10, 12; ADC(2) 2a; EOM-CCSD 2a. Each process uses
`OMP_NUM_THREADS=8` and `--mem-mb 24000`; ADC(2) uses `--basis def2-tzvp
--aux def2-tzvp-ri`, and EOM-CCSD uses `--basis def2-svp`.
Outputs remain in `package/tier1/results/`; `status.json` and `JOURNAL.md`
next to the runner record progress. Existing result JSON files are skipped.
Failed jobs are recorded without editing the frozen scripts or retrying them.

## Generate publication metrics

Pending canonical outputs. No metrics.json or metric generator exists yet;
the draft post has no active experiment binding and contains no run results.

## Data and publication

The coordinates are attributed to the authors' CC BY supplementary information.
The supplied source manifest and parsers record acquisition and extraction.
PUBLIC_FILES.txt currently routes only this README and PREREGISTRATION.md.
Runtime outputs, logs, the venv and caches are excluded from this scaffold.
