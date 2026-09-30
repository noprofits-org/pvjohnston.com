---
title: "The 2b gap calculation needs more memory"
date: 2026-09-30
author: Peter Johnston
tags: "quantum chemistry, excited states"
description: "Our 2b ADC(2) attempt ended without a gap. The inputs are ready for a team with more compute; the EOM-CCSD checks remain pending."
post-type: research
contribution: "A documented resource limit and executable handoff for the independent 2b ADC(2) rematch, which are not in Shizu et al. 2026."
contribution-type: "untested regime"
experiment: borazine-inverted-gap
status: inconclusive
draft: true
---

## Abstract

We could not complete the 2b ADC(2)/def2-TZVP gap calculation on our MacBook Pro. This continues our independent rematch of Shizu, Ishihara, Uratani, and Kaji's *Inorganic benzenes with inverted singlet-triplet gaps* (2026). [@Shizu2026] We prepared this experiment for a team with access to higher levels of compute to run. No completed 2b ADC(2) excitation energies or gap are available; the exploratory EOM-CCSD and Amendment 1 checks remain pending.

## Introduction

The [first note](/posts/2026-09-28-borazine-inverted-gap.html) reported the initial ADC(2) rematch and small-basis EOM-CCSD checks. The next compound is **2b (anth-BN)**, using the SI label; **2a (naph-BN)** is our smaller completed comparison. The published 2b ADC(2)/def2-TZVP gap is +106 meV. [@Shizu2026] Its frozen S1 sign test fails if our gap is non-positive, and magnitude reproduction requires agreement within ±50 meV. The [preregistration](/research/borazine-inverted-gap/PREREGISTRATION.md), frozen in `59824fd`, remains unchanged by this report.

## Computational Methods

The attempted calculation used PySCF 2.14.0 on the authors' unchanged PBE0/6-31G(d) geometry: conventional RHF, density-fitted ADC(2), def2-TZVP, def2-TZVP-RI and [b_core]{.metric} frozen core orbitals. PySCF supplies the independent implementation; we did not run the authors' Turbomole code. The machine was an M1 Pro with 32 GiB RAM; `--mem-mb 24000` was the solver memory setting. Software versions and threading limitations are in the [environment record](/research/borazine-inverted-gap/environment.md). We requested four singlet and eight unrestricted roots with the frozen script. [@Sun2020PySCF] Code 1 records the exact Python invocation and working directory; the queue also used `/usr/bin/time -l`.

**Code 1.** The stopped 2b attempt used this command; the linked handoff gives a portable invocation for another machine.

```sh
cd ~/Molecules/ist-borazine/package/tier1
OMP_NUM_THREADS=8 ~/Molecules/ist-borazine/.venv/bin/python \
  run_adc2_pyscf.py 2b --basis def2-tzvp --mem-mb 24000 \
  --aux def2-tzvp-ri
```

The downloadable [2b handoff](/research/borazine-inverted-gap/2b-handoff.md) includes coordinates, script hash, basis and frozen-core settings, installation instructions, the [JSON output schema](/research/borazine-inverted-gap/adc2-results.schema.json), the frozen falsifier and the published comparison value. We have not completed the higher-resource calculation described there.

## Results

The 2b log records [b_occupied]{.metric} active occupied and [b_virtual]{.metric} virtual orbitals. It prints MP2 reference correlation energy [mp2_eh]{.metric} Eh, then RADCEE Davidson settings, with no subsequent output. The [journal](/research/borazine-inverted-gap/results/JOURNAL-2026-09-30.md) records termination by SIGTERM, exit −15, on 30 September 2026 at 08:06:42 PDT after [b_seconds]{.metric} s ([b_hours]{.metric} h). User plus system CPU time was [b_cpu_hours]{.metric} h. No 2b ADC(2) result JSON was written.

The final [timing log](/research/borazine-inverted-gap/results/2b-adc2-stopped.time.txt) records [b_rss_gb]{.metric} decimal GB peak RSS and [b_footprint_gb]{.metric} decimal GB peak memory footprint. These are distinct counters. Table 1 records the follow-up outputs available at the [status snapshot](/research/borazine-inverted-gap/results/status-2026-09-30.json), last updated `2026-09-30T16:00:18+00:00`.

**Table 1.** The requested follow-up gap files are absent at this snapshot; each placeholder awaits a completed JSON, and no ΔEST value is assigned.

| Compound | Method and basis | Recorded state | ΔEST (meV) |
| --- | --- | --- | --- |
| 2b (anth-BN) | EOM-CCSD/def2-SVP | Running | **Pending — no result** |
| 1 (Borazine) | EOM-CCSD/def2-TZVP, A1 | Queued after 2b | **Pending — no result** |
| 11 (Boroxine) | EOM-CCSD/def2-TZVP, A1 | Queued after 1 | **Pending — no result** |

## Discussion

The 2b sign test remains **inconclusive** because the attempt supplied no gap. Its failure to finish does not test the published sign. The completed 2a calculation had [a_occupied]{.metric} occupied × [a_virtual]{.metric} virtual orbitals and took [a_hours]{.metric} h with about [a_rss_gb]{.metric} decimal GB peak RSS. A doubles-storage model proportional to $(ov)^2$ gives a [doubles_ratio]{.metric}× size ratio for 2b. Applying it to 2a's measured RSS gives roughly [estimated_gb]{.metric} decimal GB for in-core storage. This extrapolation is a planning estimate; we have not verified either its memory requirement or runtime on a larger machine.

Peter observed a roughly 37 GB footprint and 28.4 of 29.7 GB swap in use near the stop. Those operator observations are preserved in the archived prompt, but no monitor capture was available to verify their timing or counter definitions. The final timing counters above are the retained machine record. We cannot accomplish this calculation without more compute within our budget; we will not occupy this Mac for weeks trying to obtain it.

Amendment 1, frozen in `8c0a21e` before either def2-TZVP EOM-CCSD run, cannot yet receive a verdict. Its rule first requires the boroxine gap to be positive; if ΔEST(11) ≤ 0, A1 is inconclusive. With the control satisfied, ΔEST(1) > +50 meV means method-driven sign disagreement at def2-TZVP; ΔEST(1) < −50 meV means the def2-SVP sign flip was basis-driven. The inclusive interval −50 to +50 meV is non-decisive. The 2b EOM-CCSD/def2-SVP check is exploratory and cannot supply the missing ADC(2) sign test.

## Prompts and data

Code 2 quotes the compute budget in the handoff request. The [full prompt](/research/borazine-inverted-gap/prompts/03-followup-2b-compute-and-amendment1.md) is archived verbatim with a row in the [prompt history](/research/borazine-inverted-gap/prompts/README.md).

**Code 2.** The follow-up prompt sets the Mac’s compute budget.

```text
Peter's compute rule: nothing that would take weeks on this Mac.
```

The [publication manifest](/research/borazine-inverted-gap/PUBLIC_FILES.txt) lists the inputs and retained evidence. A small [metrics generator](/research/borazine-inverted-gap/generate-metrics.mjs) derives the resource figures from the logs and journal; this traceability concerns the incomplete attempt and its resource estimate, not a completed 2b gap. The original post and frozen calculation scripts are unchanged.

## Conclusion

Everything is prepared for anyone with the compute to complete this test. We welcome feedback, comments and results from anyone interested, through the [Contact page](/contact.html) or [GitHub issues](https://github.com/pvjohnston/pvjohnston.com/issues). Please send the environment, exact invocation, result JSON and full convergence log with any result. We will update the clearly marked placeholders when the running queue supplies the remaining outputs.

## References
