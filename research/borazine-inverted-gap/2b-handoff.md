# 2b (anth-BN): prepared calculation, no completed ADC(2) gap

We prepared this experiment for a team with access to higher levels of compute to run.
Our M1 Pro attempt was stopped without an excitation-energy result. Nothing here supplies a 2b ADC(2) gap.

## Inputs and version

Preserve the experiment's directory layout when downloading files from [PUBLIC_FILES.txt](PUBLIC_FILES.txt).
- Geometry: [xyz/2b.xyz](xyz/2b.xyz), unchanged SI PBE0/6-31G(d) S0 geometry; SHA-256 `2f26f267156a7ef492f795f90c9d9173c04fbb3c1b99697c7e9d57e2273517ff`.
- Script: [tier1/run_adc2_pyscf.py](tier1/run_adc2_pyscf.py), identical to freeze commit `59824fdc22e3f548946878a41b3790dd7fc64d46`; SHA-256 `a47d12d2ec4db08b8d7d35bb77550738e01154bd13553eb3408640e13dc3247e`.
- Protocol: [PREREGISTRATION.md](PREREGISTRATION.md), original freeze `59824fd`, with Amendment 1 appended in `8c0a21e`. The S1 rule is unchanged.
- Software: PySCF 2.14.0, Python 3.13.12, NumPy 2.5.3, SciPy 1.18.1, h5py 3.16.0; see [environment.md](environment.md). Record the new machine and BLAS when rerunning.
- Settings: neutral, singlet RHF reference; def2-TZVP orbital basis; def2-TZVP-RI auxiliary basis in ADC; 14 frozen occupied orbitals from `chemcore`; 33 active occupied and 447 virtual orbitals.
- RHF: energy tolerance 1e-10 Eh, gradient tolerance 1e-7; four RADC singlet roots and eight UADC roots; triplet selection follows the frozen script's spin-square/fallback logic.
- The stopped log records RADCEE max_space=12, max_cycle=50, conv_tol=1e-8. The script's introductory comment gives a different nominal tolerance; retain the script and inspect the actual solver log.

## Execute

Code 1 gives the stopped attempt's Python command, working directory and thread environment. The queue additionally measured it with `/usr/bin/time -l` under `caffeinate -ims`.

**Code 1.** These arguments reproduce the recorded 2b invocation; running this command starts an expensive calculation.

```sh
cd ~/Molecules/ist-borazine/package/tier1
OMP_NUM_THREADS=8 ~/Molecules/ist-borazine/.venv/bin/python \
  run_adc2_pyscf.py 2b --basis def2-tzvp --mem-mb 24000 \
  --aux def2-tzvp-ri
```

For a different machine, create a fresh venv with `python3 -m venv .venv`, then `.venv/bin/pip install 'pyscf==2.14.0'`. From this experiment directory, the equivalent invocation is `OMP_NUM_THREADS=8 .venv/bin/python tier1/run_adc2_pyscf.py 2b --basis def2-tzvp --mem-mb 24000 --aux def2-tzvp-ri`. The script finds `xyz/2b.xyz` relative to itself. Its `max_memory` setting is an algorithm hint, not a hard process-RAM limit. No installation or rerun was performed while preparing this handoff.

## Output and decision rule

The full run writes `tier1/results/2b_adc2_def2-tzvp.json` and a same-stem `.log`. [adc2-results.schema.json](adc2-results.schema.json) describes every output field, including excitation energies in eV, the spin-square array, timings in seconds and ΔEST in meV. A completed [2a JSON](results/2a_adc2_def2-tzvp.json) illustrates the format; it is not a 2b result. Require a selected T1 and non-null ΔEST, and check SCF and Davidson convergence in the log: the frozen script can write JSON even when a higher Davidson root is unconverged. Schema validity alone is insufficient. Follow the frozen stopping rule rather than silently changing the script or accepting unconverged roots.

Compute ΔEST = 1000 × (S1_eV − T1_eV). The authors' ADC(2)/def2-TZVP value for 2b (anth-BN) is +106 meV in [the SI table extract](expected/published_SI_tables_1-3.csv), Supp. Table 1. Under S1, the sign test fails if our ΔEST ≤ 0; magnitude reproduction requires an absolute difference from +106 meV of at most 50 meV. Missing or unconverged energies yield no verdict. Source: Shizu et al., Communications Chemistry (2026), doi:10.1038/s42004-026-02141-0; acquisition and attribution are in [sources.json](sources.json).

## Resource estimate and retained evidence

The completed 2a (naph-BN) ADC attempt used 24 occupied × 324 virtual orbitals, 41572.01 s (11.5 h) and 24992956416 bytes (about 25 decimal GB) peak RSS. Applying the doubles-storage model (o × v)^2 gives (33 × 447 / (24 × 324))^2 = 3.5986. Scaling 2a's peak RSS by that factor gives 89.94 decimal GB, approximately 90 GB. This is a planning estimate for in-core storage, with no guarantee about the actual allocation peak or wall time. It is not a benchmark on a larger machine.

The [stopped PySCF log](results/2b-adc2-stopped.pyscf.txt) prints MP2 reference correlation energy −2.03570034 Eh and ends at RADCEE setup. The [journal snapshot](results/JOURNAL-2026-09-30.md) records 70412.486 s wall time, exit −15 and termination at 2026-09-30 08:06:42 PDT. The [timing log](results/2b-adc2-stopped.time.txt) records 14338.82 s user + 30423.90 s system CPU time (12.4 h), 25.57 decimal GB peak RSS and 73.46 decimal GB peak memory footprint. RSS and memory footprint are different counters.

Peter reported a roughly 37 GB footprint snapshot and 28.4 of 29.7 GB swap used near the stop. Those observations are preserved in the [prompt archive](prompts/03-followup-2b-compute-and-amendment1.md), but no timestamped monitor capture was available to verify them. They are not substituted for the final timing counters. [generate-metrics.mjs](generate-metrics.mjs) regenerates the resource figures from the preserved logs and journal; run `node research/borazine-inverted-gap/generate-metrics.mjs --check` from the repository root.

We cannot accomplish this calculation on this Mac within our compute budget. We welcome feedback, comments and results through the [Contact page](/contact.html) or [GitHub issues](https://github.com/pvjohnston/pvjohnston.com/issues). Please include the exact command, script hash, environment, JSON, complete convergence log and timing/memory record. We do not undertake jobs expected to occupy this Mac for weeks.
