---
title: "Does borazine keep its inverted singlet-triplet gap? (draft)"
date: 2026-09-28
author: Peter Johnston
tags: "quantum chemistry, excited states"
description: "An independent ADC(2) reproduction on the published borazine and boroxine geometries is running; results are pending."
post-type: research
contribution: "An independent open-source ADC(2)/def2-TZVP singlet-triplet gap for borazine and boroxine on the published geometries, which is not in Shizu et al. 2026."
contribution-type: "untested regime"
draft: true
# experiment: borazine-inverted-gap  (add when metrics.json exists)
---

## Abstract

TODO: state the finding after the preregistered calculations finish.

## Introduction

This independent reproduction tests the borazine and boroxine singlet-triplet gaps reported by Shizu, Ishihara, Uratani and Kaji in "Inorganic benzenes with inverted singlet-triplet gaps" (2026). [@Shizu2026]

## Computational Methods

The [preregistration](/research/borazine-inverted-gap/PREREGISTRATION.md) specifies the P1/P2/S1 falsifiers and frozen protocol: PySCF DF-ADC(2)/def2-TZVP on the authors' PBE0/6-31G(d) geometries, with an exploratory EOM-CCSD/def2-SVP cross-check. We use the authors' coordinates with independently supplied PySCF scripts, not their Turbomole program. SCS-CC2 is not run by us; the numbers in `expected/` are the authors' published values. [@Shizu2026]

## Results

Calculations running; no results yet.

## Discussion

TODO: apply the preregistered verdict rules and describe limitations.

## Conclusion

TODO: state what was learned and any direct next experiment.

## References
