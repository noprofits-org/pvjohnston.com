---
title: "Borazine keeps its inverted ADC(2) gap (draft)"
date: 2026-09-28
author: Peter Johnston
tags: "quantum chemistry, excited states"
description: "PySCF reproduces borazine's inverted ADC(2) gap; a smaller-basis EOM-CCSD check gives the opposite sign."
post-type: research
contribution: "An independent open-source ADC(2)/def2-TZVP singlet-triplet gap for borazine and boroxine on the published geometries, which is not in Shizu et al. 2026."
contribution-type: "untested regime"
draft: true
---

## Abstract

Borazine keeps its inverted singlet–triplet gap in our independent PySCF ADC(2)/def2-TZVP calculation. This preregistered rematch uses the published geometries from Shizu, Ishihara, Uratani, and Kaji's *Inorganic benzenes with inverted singlet-triplet gaps* (2026). [@Shizu2026] We obtain −192 meV against the authors' −193 meV, while the boroxine control remains positive. The completed ADC(2) gaps meet the frozen magnitude tolerance; 2a carries a convergence caveat. Exploratory EOM-CCSD/def2-SVP gives positive gaps throughout the completed set, including +118 meV for borazine. A preregistered larger-basis check will test that method-and-basis discrepancy.

## Introduction

An inverted gap places the lowest excited singlet below the lowest triplet: $\Delta E_{\mathrm{ST}} = E(S_1)-E(T_1) < 0$. That ordering is of interest for light-emitting materials because triplet-to-singlet conversion need not climb the usual singlet–triplet energy gap. Shizu and co-workers propose borazine and related inorganic rings as candidates with inverted gaps and fast radiative decay, using SCS-CC2 and ADC(2). [@Shizu2026] Our question is narrower: does an independent, open-source ADC(2) implementation recover their reported gaps on their own geometries? Reproducing that column would test implementation agreement without establishing the experimental state ordering or reproducing their SCS-CC2 calculation.

## Preregistration

The original [preregistration](/research/borazine-inverted-gap/PREREGISTRATION.md) was frozen in commit `59824fdc22e3f548946878a41b3790dd7fc64d46` on 28 September 2026 at 12:51:07 PDT, before the canonical queue started. Its original SHA-256 was `2fe308306a92ec2bf937913044227da0ad92dd3e79542af2ca6da334719e2fb7`. The current file also contains Amendment 1, committed as `8c0a21e` at 16:58:39 PDT that day, before any EOM-CCSD/def2-TZVP run.

- **P1, borazine:** a non-negative ADC(2)/def2-TZVP gap falsifies our inversion hypothesis. A negative gap within ±50 meV of −193 meV supports the hypothesis and reproduces the magnitude; a negative gap outside that interval supports inversion without reproducing the magnitude.
- **P2, boroxine:** the control must remain positive. A non-positive control makes the Tier 1 verdict inconclusive regardless of P1; agreement within ±50 meV of +279 meV reproduces its magnitude.
- **S1, secondary molecules:** magnitude reproduction requires an absolute difference of at most 50 meV. Sign tests apply where the published gap's magnitude exceeds 50 meV: 12 must remain negative and 2b positive. The signs of 2a, 9, and 10 are non-decisive under this rule. [@Shizu2026]

The ±50 meV band was chosen to allow for density fitting and auxiliary-basis effects, the frozen-core convention, solver convergence and root targeting, rounded supplementary values, and differences between PySCF and Turbomole. The SI does not specify the core-freezing threshold. The band was deliberately wider than the differences anticipated for these valence states; its reasoning and limitations are recorded in the preregistration. A failed reproduction would have been reported under the same rule.

The freeze was not blind to every preliminary number. Untuned box-sizing smoke tests had already printed borazine gaps of −129 meV at DF-ADC(2)/def2-SVP and +118 meV at EOM-CCSD/def2-SVP. That prior knowledge was disclosed before freezing. Those preliminary values do not enter P1/P2/S1; the canonical outputs below were produced afterward.

## Computational Methods

We used the authors' unchanged PBE0/6-31G(d) ground-state geometries and independently supplied PySCF scripts. ADC(2) used def2-TZVP with the def2-TZVP-RI auxiliary basis, a conventional RHF reference, and frozen core from `pyscf.data.elements.chemcore`. Four spin-adapted singlet roots and eight unrestricted roots in the $M_S=0$ manifold were requested. Triplets were selected by $|\langle S^2\rangle-2|<0.3$; all completed runs returned spin-square values, so the RADC-matching fallback was unused. S1 and T1 are the lowest selected roots, independent of brightness. SCS-CC2 was not run by us; the comparison values in `expected/` are the authors' results. [@Shizu2026; @Sun2020PySCF]

The environment was PySCF 2.14.0, Python 3.13.12, NumPy 2.5.3, SciPy 1.18.1, and h5py 3.16.0 on an Apple M1 Pro with 32 GiB RAM and macOS 27.0. RHF energy and gradient tolerances for ADC(2) were $10^{-10}$ hartree and $10^{-7}$, respectively. Jobs ran sequentially with a 24,000 MB memory setting. The JSON `threads` field records **1**, despite `OMP_NUM_THREADS=8`: the wheel has no OpenMP support and uses Apple Accelerate. Operational observation was roughly two cores in use, which is distinct from the recorded PySCF thread counter. The [environment record](/research/borazine-inverted-gap/environment.md) gives the installation details; the scripts set no random seed.

Code 1 is the root-selection and gap-calculation excerpt from the [full frozen ADC(2) script](/research/borazine-inverted-gap/tier1/run_adc2_pyscf.py). The exploratory [EOM-CCSD script](/research/borazine-inverted-gap/tier1/run_eomccsd_pyscf.py) used def2-SVP, the same geometries and frozen-core convention, and four singlet and four triplet roots. Its small-basis cross-check was outside the frozen falsifier and supplies no P1/P2/S1 verdict.

**Code 1.** The ADC(2) script selects triplet roots and computes the signed gap from excitation energies in eV; the reported gap is in meV.

```python
sing = np.array(out['singlets_eV'])
trip = [e for i, e in enumerate(out['uadc_eV'])
        if (out['uadc_s2'] is not None and abs(out['uadc_s2'][i]-2.0) < 0.3)
        or (out['uadc_s2'] is None and np.min(np.abs(sing-e)) > 2e-3)]
out['triplets_eV'] = trip
out['S1_eV'] = float(sing[0]); out['T1_eV'] = float(trip[0]) if trip else None
out['dEST_meV'] = (out['S1_eV']-out['T1_eV'])*1000 if trip else None
```

## Results

Table 1 lists the ADC(2) excitation energies, gaps, published comparison values, and outcomes under the stated decision rules. Gaps and absolute differences were calculated from unrounded JSON values before rounding; the excitation energies are displayed to four decimal places.

**Table 1.** Frozen-core RI-ADC(2)/def2-TZVP results from PySCF 2.14.0 on the M1 Pro are compared with the authors' ADC(2) values; S1 and T1 are in eV, and all gap columns are in meV. [@Shizu2026]

| ID | Compound | S1 | T1 | ΔEST ours | ΔEST published | Absolute difference | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Borazine | 6.7687 | 6.9606 | −191.9 | −193.0 | 1.1 | P1 supported; magnitude reproduced |
| 11 | Boroxine | 7.7906 | 7.5121 | +278.4 | +279.0 | 0.6 | P2 passes; reproduced |
| 9 | Borthiin | 4.9498 | 4.9205 | +29.3 | +26.0 | 3.3 | Reproduced; sign non-decisive |
| 10 | Boroselenol | 4.3577 | 4.4046 | −46.9 | −47.0 | 0.1 | Reproduced; sign non-decisive |
| 12 | GaN analogue | 5.3475 | 5.5061 | −158.5 | −160.0 | 1.5 | Reproduced; sign test passes |
| 2a | naph-BN | 6.5247 | 6.4897 | +35.0 | +34.0 | 1.0 | Reproduced with caveat; sign non-decisive |

For 2a, the log reports `conv = False` for the fourth singlet at 7.40 eV. Its S1 and selected T1 roots report convergence. This higher root does not enter the displayed ΔEST. The protocol consequence of retaining that row is discussed below.

Table 2 gives the exploratory EOM-CCSD/def2-SVP gaps. Each recorded value is positive, including borazine.

**Table 2.** Exploratory frozen-core EOM-CCSD/def2-SVP gaps on the same geometries are given in meV; these calculations are outside the frozen falsifier.

| ID | Compound | ΔEST |
| --- | --- | ---: |
| 1 | Borazine | +117.6 |
| 11 | Boroxine | +473.2 |
| 9 | Borthiin | +15.1 |
| 10 | Boroselenol | +44.8 |
| 12 | GaN analogue | +29.0 |
| 2a | naph-BN | +151.0 |

The [journal](/research/borazine-inverted-gap/results/JOURNAL.md) records 20.97 h of summed wall time for these completed jobs: 20.41 h for ADC(2) and 33.49 min for EOM-CCSD. ADC(2) jobs ranged from 29.78 to 692.87 min, with peak RSS from 16.15 to 23.28 GiB. EOM-CCSD jobs ranged from 0.91 to 15.80 min, with peak RSS from 2.08 to 12.71 GiB. These totals use the journal's completed entries and exclude the later zero-time skips. Peak RSS is the macOS `/usr/bin/time -l` maximum resident set size, converted from bytes to GiB.

## Discussion

P1 is **supported, magnitude reproduced**, and the positive P2 control passes and is reproduced. Our independent ADC(2) gaps closely reproduce the authors' column under the preregistered tolerance. [@Shizu2026] The completed secondary values also fall within that band, with 12 passing its sign test; 2a, 9, and 10 retain their preregistered non-decisive sign status.

There is a protocol caveat for 2a. The frozen text says to stop and not report when SCF or Davidson fails to converge, but the supplied script checks SCF convergence and still writes a JSON when a higher Davidson root fails. We retain the 2a row with this departure disclosed: the unconverged fourth singlet lies above both converged roots used for ΔEST and has no role in their subtraction. Its presence does not change the reported gap, but we do not call the full requested root set converged or the row a fully compliant execution of that stopping rule. No rerun or script change was made for this draft.

The EOM-CCSD cross-check gives positive gaps across the entire completed set. Relative to ADC(2), that changes the sign for borazine, 10, and 12; boroxine, 9, and 2a are positive in both calculations. Borazine's +118 meV cross-check mixes a change of electronic-structure method with a change from def2-TZVP to def2-SVP. It cannot distinguish those causes or overturn the frozen ADC(2) verdict. That is the comparison Amendment 1 was written to test. Neither approximation establishes the experimental ordering, and the authors' SCS-CC2 results remain untested by us.

The runtimes are pessimistic as laptop benchmarks. From 21 September through 29 September 2026, a parked, unrelated ORCA job kept relaunching on the same Mac and shared its cores. That contention affects elapsed time, not the computed energies; no estimate of uncontended speedup is inferred here.

## Prompts

Code 2 records the launch prompt's freeze requirement, wrapped for readability. The numerical outputs came from the committed chemistry scripts. The prompt directed the agent to prepare the environment, record the protocol, and launch the queue.

**Code 2.** This excerpt requires the preregistration commit to precede production calculations.

```text
The preregistration (falsifier) is already written and must be frozen by
a commit BEFORE any production calculation starts.
```

The [full setup and launch prompt](/research/borazine-inverted-gap/prompts/01-setup-and-launch-tier1.codex.md) and [prompt archive README](/research/borazine-inverted-gap/prompts/README.md) preserve that history. The README records a checksum deviation: the prompt named an earlier input tarball, and a rebuilt package carried the smoke-test disclosure and approved 2b run. The original frozen preregistration is identified by the commit and file hash above. The archived prompt describes the initial queue; its original exclusions are not a description of today's expanded queue.

## What comes next

As of 29 September 2026, 2b ADC(2)/def2-TZVP is running, with its EOM-CCSD/def2-SVP check queued next. The published ADC(2) gap is +106 meV, making 2b the second secondary sign test alongside 12. [@Shizu2026]

Amendment 1 then runs EOM-CCSD/def2-TZVP on borazine and boroxine, on the same geometries. Its frozen decision rule first requires boroxine to remain positive; otherwise A1 is inconclusive. With that control satisfied, borazine above +50 meV means method-driven sign disagreement at def2-TZVP; below −50 meV means agreement at def2-TZVP and a basis-driven def2-SVP sign flip. The inclusive interval from −50 to +50 meV is non-decisive. This secondary test cannot change P1/P2/S1 or establish which method is correct.

This begins a series of inverted-gap rematches, run on a laptop where feasible. Cases requiring weeks of computation will be written up as **prepared for a team with access to higher levels of compute to run**, with inputs committed and no claim that we ran them. This post will be updated when 2b and Amendment 1 finish. Corrections to the state assignments or comparison assumptions are welcome.

## Data and code availability

The [experiment README](/research/borazine-inverted-gap/README.md) and [publication manifest](/research/borazine-inverted-gap/PUBLIC_FILES.txt) link the completed result JSONs, journal snapshot, prompts, both executable scripts, environment record, and geometries used here. The authors' comparison values are retained in the [published SI table extract](/research/borazine-inverted-gap/expected/published_SI_tables_1-3.csv), with acquisition information in [sources.json](/research/borazine-inverted-gap/sources.json). The coordinates come from the authors' CC BY supplementary information. [@Shizu2026] Results were copied unchanged from the run directory; calculations continued there while this draft was prepared. This draft has no `experiment` binding or `metrics.json`, so it does not yet claim the site's automated traceability label.

## References
