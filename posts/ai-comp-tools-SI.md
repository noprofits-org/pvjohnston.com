---
title: AI Assisted Computational Tools for TDDFT Analysis of Chromophores Supplemental Information
date: 2025-03-25
tags: computational chemistry, excited states, TD-DFT, chromophores, photochemistry
description: A suite of Python-based computational tools for efficient geometry optimization, TD-DFT calculations, and spectral visualization of chromophores, providing a systematic approach to predicting electronic transitions and optical properties.
---
# Supporting Information

### Input Structure Preparation

The input files used for geometry optimization of urea and DCDHF-Me2 chromophores were prepared using Avogadro, an open-source molecular builder and visualization tool.[@Hanwell2012; @Avogadro] The general workflow for generating these input files involved building molecular structures using Avogadro's graphical interface, performing pre-optimization with the Universal Force Field (UFF) within Avogadro, and exporting the structures as input files for subsequent quantum mechanical geometry optimization.

#### Urea Input Structure

The urea input file (`urea.in`) contains 8 atoms including the carbonyl group and two amino groups. The input structure was created to match the standard geometry of urea with appropriate bond lengths and angles. The original content of the Avogadro-generated file is shown below:

```
8
	Energy:    -115.2781918
N          0.20371        0.16819       -0.10412
C         -1.06311        0.59925        0.05445
N         -1.98034       -0.38739        0.03747
O         -1.35312        1.77482        0.19568
H          0.45121       -0.80639       -0.07401
H          0.93588        0.85986       -0.01745
H         -2.95249       -0.11457        0.08390
H         -1.74996       -1.34295       -0.17591
```

When using this input file with the `optimize.py` script, the file is placed in the `input_structures` directory.

#### DCDHF-Me2 Input Structure

The DCDHF-Me2 structure was created based on the donor-acceptor chromophore described by Lu et al.[@Lu2009] The molecular structure was built in Avogadro based on the molecular connectivity reported in the literature. The Avogadro-generated file contains 39 atoms and is shown below:

```
39
	Energy:      44.1010644
N          1.30016        1.74158        1.49069
C          0.93304        1.74035        0.13814
C         -0.18841        2.46517       -0.28855
H         -0.77438        3.03805        0.42543
C         -0.56453        2.52482       -1.63577
H         -1.43139        3.12966       -1.89443
C          0.16763        1.85097       -2.61881
C          1.28057        1.11677       -2.21283
H          1.87402        0.54966       -2.92382
C          1.66014        1.07514       -0.85989
H          2.53739        0.48626       -0.60735
C          0.22097        1.41135        2.42742
C          2.61408        1.22486        1.86436
H         -0.58363        2.15296        2.40671
H          0.59508        1.39787        3.45757
H         -0.19669        0.42145        2.21094
H          3.40721        1.68558        1.26470
H          2.66022        0.13550        1.76004
H          2.83404        1.47310        2.90897
C         -0.23019        1.98691       -4.02523
C         -1.44605        1.73833       -4.53771
C         -2.51721        1.11841       -3.84474
C          0.65874        2.54589       -5.10396
N         -3.38646        0.59284       -3.28407
O         -0.16750        2.51734       -6.30524
C         -1.47058        2.19592       -5.91182
C          1.90159        1.71406       -5.42867
C          1.03796        4.00891       -4.85646
H          1.65172        0.65234       -5.53864
H          2.67619        1.81370       -4.66232
H          2.33766        2.02717       -6.38495
H          0.14610        4.62934       -4.70756
H          1.55794        4.42529       -5.72711
H          1.68557        4.11961       -3.98083
C         -2.50517        2.43011       -6.74475
C         -3.86482        2.29156       -6.35795
C         -2.25639        2.93810       -8.05356
N         -4.97873        2.21982       -6.04165
N         -2.06490        3.35942       -9.11767
```

The structure is placed in the `input_structures` directory for processing with the `optimize.py` script.

### Hardware and Software Environment

All calculations were performed on a Linux system (Ubuntu noble/24.04) with 15 GB total memory (2.8 GB used, 1.3 GB free, 11 GB buffer/cache), 4.0 GB swap space, and 8 CPU cores. The computational environment utilized Python 3.10, Psi4 1.7, and Miniconda for Python package management.

The AI-assisted development of the computational tools was performed using Claude 3.7 Sonnet.[@Anthropic2025Claude]

### References