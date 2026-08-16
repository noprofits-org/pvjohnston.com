# Environment

`environment-psi4_19.yml` is the conda export of the environment that produced
the canonical results. This file records the execution boundary the lockfile
cannot express.

That export is **byte-identical** to `research/dcdhf-me2-transitions/environment-psi4_19.yml`,
which is not incidental. This experiment substitutes into that experiment's
DCDHF-Me2 B3LYP/def2-SVP minimum to build the TCF rung, so the two have to have
been computed under the same software, and a diff of the two exports is the
cheapest way for a reader to confirm it.

- Operating system and version: Linux, kernel 7.0.0-28-generic (glibc 2.39)
- Architecture: x86_64
- Interpreter/compiler and version: Python 3.10.17 (conda env `psi4_19`)
- Dependency manager and version: conda (Miniconda), env exported to
  `environment-psi4_19.yml` with `--no-builds`
- Key packages: Psi4 1.9.1, NumPy 2.2.5
- Hardware assumptions: developed and run on 8 cores / 15 GB RAM. `run_all.sh`
  defaults to 6 threads and a 6 GB Psi4 memory budget (which Psi4 reports as
  5.588 GiB) and runs the stages in series. Each results file records the
  threads and memory actually used.
- Locale/timezone: not relevant to any output; the only timestamps are UTC
  ISO-8601 strings in the environment records and metrics provenance
- Random seeds and nondeterministic operations: none by design. Geometry
  construction is analytic and deterministic; the SCF and the TD-DFT
  eigensolver are deterministic given the same starting geometry and
  convergence thresholds. Results are reproducible to convergence tolerance,
  not bitwise: Psi4's density fitting and threaded BLAS make the last digits
  dependent on thread count and BLAS build.
- Required environment variables: `PSI_SCRATCH` — set automatically by
  `run_tddft.py` to `<experiment dir>/scratch` **before** `import psi4`, which
  is load-bearing; setting it after the import has no effect. Override with
  `PSI_SCRATCH` in the environment if that filesystem is unsuitable.
  `PSI4_PYTHON`, `THREADS`, `MEMORY`, `TD_BASIS`, `STATES` and `MOLECULES`
  optionally override `run_all.sh` defaults.
- External services, models, and dated version identifiers: none. No network
  access is required. The only inputs are the committed starting geometries and
  the prior experiment's committed results.

## No structure-generation toolkit is available here

RDKit, OpenBabel and ASE are all absent from both the `psi4_19` environment and
the system interpreter, verified by import. This is why `build_geometries.py`
constructs the CN and DCV rungs analytically from standard bond lengths and
angles rather than generating and force-field-optimizing them, and it is the
same constraint `research/dcdhf-me2-transitions` recorded when it built its
benzene starting structure by hand.

The consequence is stated rather than worked around: that experiment measured
how far a UFF force-field structure sits from the DFT minimum, and **no
equivalent measurement exists here**. Nothing in this experiment claims a
force-field starting point.

## Known version-specific behaviour

In Psi4 1.9.1 the TD-DFT eigensolver's iteration limit **cannot be raised**.
Verified directly in the prior experiment: passing `maxiter=120` as a keyword
argument to `tdscf_excitations`, setting the `TDSCF_MAXITER` global option to
120, or doing both, all leave the solver running at **60** — it accepts each
silently and reports 60 in its own printed options. `r_convergence` behaves
differently and *does* take effect (the solver reports the requested 1e-5
rather than the 1e-4 default).

This matters because 60 is a real ceiling, not a nominal one: a slowly
converging charge-transfer root that needs more than 60 iterations cannot be
given them without patching Psi4. It fails loudly rather than silently —
`_solve_loop` raises `TDSCFConvergenceError` — so an unconverged result cannot
reach `results/` unnoticed.

`run_tddft.py` therefore does **not** record the values it requested as though
they were applied. It parses the solver's own printed header after the run and
stores both: `tdscf_requested` (what was asked for) and `tdscf_effective` (what
the solver reported using). Where those disagree, the disagreement is visible in
the published record instead of being papered over.
