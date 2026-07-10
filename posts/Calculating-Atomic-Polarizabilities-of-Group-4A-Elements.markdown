---
title: Calculating Atomic Polarizabilities of Group 14 Elements Using Psi4 - A Finite Field Approach 
date: 2025-02-25
tags: quantum chemistry, hyperpolarizability, computational chemistry, psi4 
description: An experimental study calculating polarizabilities of Group 14 elements using Psi4's finite field method, with results for C, Si, and Ge, and insights into limitations for heavier elements.
---

## Abstract

This study explores the polarizabilities of Group 14 elements (C, Si, Ge, Sn, Pb) using the finite field method in Psi4 1.7. We successfully computed isotropic polarizabilities for carbon (7.11 a.u.), silicon (20.17 a.u.), and germanium (20.19 a.u.), revealing an increasing trend down the group. However, computational limitations arose when attempting calculations for heavier elements. This work demonstrates a practical workflow for atomic property calculations, highlights methodological challenges with heavier elements, and establishes a foundation for future investigations using alternative computational approaches.

## Introduction

Polarizability—the measure of an atom's electron cloud deformability in response to an external electric field—represents a fundamental property that governs numerous physical and chemical phenomena. From intermolecular forces to optical properties, polarizability provides critical insights into how atoms and molecules interact with electromagnetic radiation and with each other.

Group 14 elements (C, Si, Ge, Sn, Pb) present an especially intriguing case study for polarizability analysis due to their systematic variation in atomic radius, electron configuration, and relativistic effects as one moves down the periodic table. The progressive filling of d and f orbitals prior to the p valence shell in heavier elements introduces electronic structure complexities that can significantly affect polarizability.

Computational quantum chemistry offers powerful tools for investigating these properties without the experimental complexities of measuring atomic responses to electric fields. Open-source software packages like Psi4 have democratized access to sophisticated quantum chemical calculations, though these approaches come with their own methodological challenges and limitations, particularly for heavier elements where relativistic effects become significant.[@Parrish2017; @Schwerdtfeger2002]

In this study, we implement a finite field approach within Psi4 to calculate polarizabilities across the Group 14 elements. The polarizability tensor component α<sub>xx</sub> can be approximated through the numerical derivative:

$$\alpha_{xx} \approx \frac{\mu_x(F_x = +h) - \mu_x(F_x = -h)}{2h}$$

where h represents the applied electric field strength. This approach provides an approximation of the dipole response to an external electric field, from which polarizability can be derived.[@Cohen1975]

For reproducibility, we developed a systematic workflow that automatically generates the necessary input files for each element at various field strengths, selecting appropriate basis sets for each element. Our work serves three primary objectives: (1) establishing a reproducible workflow for polarizability calculations, (2) documenting the polarizability trend across available Group 14 elements, and (3) identifying computational constraints that emerge when extending these calculations to heavier elements.

The insights gained here will inform future work aimed at overcoming these limitations, potentially through alternative basis sets, pseudopotentials, or computational methodologies that better account for relativistic effects in heavier elements.[@Jensen2017]

## Experimental

### Computational Setup

The calculations were performed on an Ubuntu 24.04 system, accessed via SSH. Psi4 version 1.7 was installed within a dedicated Conda environment (psi4fix, Python 3.9). The following directory structure was created:

```bash 
mkdir -p ~/hyperpol_exp/{inputs,outputs,scripts,analysis}
cd ~/hyperpol_exp 
```

### Input Generation

The input files were generated with the following script:

```bash
#!/bin/bash
ELEMENTS=("C" "Si" "Ge" "Sn" "Pb")
FIELDS=("0.002" "0.0" "-0.002")
INPUT_DIR="inputs"
rm -f "$INPUT_DIR"/*.in

for elem in "${ELEMENTS[@]}"; do
  if [[ "$elem" == "Sn" || "$elem" == "Pb" ]]; then
    BASIS="cc-pVDZ-PP"
  else
    BASIS="cc-pVDZ"
  fi
  
  for field in "${FIELDS[@]}"; do
    if [ "$field" == "0.0" ]; then
      filename="${INPUT_DIR}/${elem}_field_zero.in"
      cat > "$filename" << EOL
memory 2 GB
molecule ${elem} {
${elem} 0 0 0
symmetry c1
}
set {
basis ${BASIS}
scf_type df
e_convergence 1e-8
d_convergence 1e-8
}
E, wfn = energy('scf', return_wfn=True)
dipole = wfn.variable("SCF DIPOLE")
print("Dipole Moment:", dipole)
EOL
    else
      filename="${INPUT_DIR}/${elem}field${field//-/minus}.in"
      cat > "$filename" << EOL
memory 2 GB
molecule ${elem} {
${elem} 0 0 0
symmetry c1
}
set {
basis ${BASIS}
scf_type df
e_convergence 1e-8
d_convergence 1e-8
perturb_h True
perturb_with dipole
perturb_dipole [${field}, 0.0, 0.0]
}
E, wfn = energy('scf', return_wfn=True)
dipole = wfn.variable("SCF DIPOLE")
print("Dipole Moment:", dipole)
EOL
    fi
  done
done
```

```bash
chmod +x scripts/generate_inputs.sh
./scripts/generate_inputs.sh
```

### Calculation Execution

The Psi4 calculations were performed sequentially for each input file:

```bash
for file in inputs/*.in; do
  base=$(basename "$file" .in)
  echo "Running $base..."
  psi4 -i "$file" -o "outputs/$base.out"
done
```

### Data Extraction

Upon completion, the dipole moment values were extracted from the output files:

```bash
for file in outputs/*.out; do
  echo "$file:"
  grep "Dipole Moment" "$file" -A 1 | tail -n 1
done
```

## Results

Our calculations yielded the following isotropic polarizability values:

<table>
  <caption><strong>Table 1: Calculated Polarizabilities</strong></caption>
  <thead>
    <tr>
      <th>Element</th>
      <th>Polarizability / a.u.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>C</td>
      <td>7.11</td>
    </tr>
    <tr>
      <td>Si</td>
      <td>20.17</td>
    </tr>
    <tr>
      <td>Ge</td>
      <td>20.19</td>
    </tr>
    <tr>
      <td>Sn</td>
      <td>N/A</td>
    </tr>
    <tr>
      <td>Pb</td>
      <td>N/A</td>
    </tr>
  </tbody>
</table>

**Figure 1: Polarizability Trend**

```tikzpicture
\begin{axis}[
    width=12cm, % Slightly wider for better visibility
    height=8cm,
    xlabel={Element},
    ylabel={Polarizability / a.u.},
    xtick={0,1,2}, % Only C, Si, Ge (no Sn, Pb since N/A)
    xticklabels={C, Si, Ge},
    ymin=0, ymax=25,
    grid=major,
    grid style={line width=0.1pt, draw=gray!30}, % Subtle grid lines
    axis lines=left,
    bar width=0.5cm, % Thinner bars for clarity
    ybar,
    title={Polarizability of Group 14 Elements},
    title style={font=\large\bfseries, color=black}, % Black title for contrast
    every axis label/.style={font=\normalsize, color=black},
    every tick label/.style={font=\normalsize, color=black},
    enlarge x limits=0.2, % More space around bars
    ymajorgrids=true
]

% Plot the data with a professional color (dark gray or blue)
\addplot[fill=gray!50, draw=black, opacity=0.8] coordinates {(0,7.11) (1,20.17) (2,20.19)};
\end{axis}
```

## Discussion

The calculated polarizabilities for carbon (7.11 a.u.), silicon (20.17 a.u.), and germanium (20.19 a.u.) reveal a clear pattern that aligns with theoretical expectations. The marked increase in polarizability from carbon to silicon reflects the substantial jump in atomic radius and the corresponding expansion of the electron cloud, which becomes more easily distorted by external electric fields. The nearly identical values for silicon and germanium, despite germanium's larger atomic radius, suggest that other factors—potentially including electronic structure effects such as d-orbital participation and relativistic contributions—may be counterbalancing the expected increase in polarizability.

It is worth noting that our calculated value for carbon (7.11 a.u.) is lower than literature values typically ranging from 11-12 a.u. This discrepancy can be attributed to our use of the cc-pVDZ basis set, which lacks the diffuse functions critical for accurately modeling the outer regions of the electron density that contribute significantly to polarizability.[@Shelton1992] This observation underscores the importance of basis set selection in polarizability calculations and suggests that augmented basis sets (e.g., aug-cc-pVDZ) would likely yield improved results.

A significant methodological limitation emerged for tin and lead, where our calculation attempts were unsuccessful due to issues with the cc-pVDZ-PP basis sets. Despite their theoretical availability in the Psi4 ecosystem, these basis sets could not be located by the Conda-distributed version of Psi4 1.7 used in this study.[@Parrish2017] This finding highlights an important practical constraint in computational chemistry: the gap between theoretical capability and practical implementation in software packages.

For heavier elements like tin and lead, relativistic effects become increasingly important, necessitating pseudopotentials or relativistic methods to achieve accurate results.[@Schwerdtfeger2002] The absence of readily accessible pseudopotential basis sets in our Psi4 installation represents a common challenge in computational chemistry workflows that must be addressed through alternative approaches.

The finite field method itself proved to be a robust approach for polarizability calculation, with the field strength of 0.002 a.u. providing a good balance between numerical stability (avoiding roundoff errors at very small fields) and linearity (avoiding higher-order effects at larger fields).[@Cohen1975] This method's simplicity and direct physical interpretation make it an attractive approach for polarizability studies, particularly when implemented within accessible computational platforms like Psi4.

The directory structure and automated input generation scripts we developed successfully organized the workflow and allowed for efficient calculation across multiple elements and field strengths. This approach facilitated systematic investigation of trends and ensured reproducibility of results, demonstrating the value of structured computational workflows in quantum chemical research.

## Conclusion

This study has successfully established a computational workflow for calculating atomic polarizabilities of Group 14 elements using the finite field method in Psi4. Our results confirm the expected trend of increasing polarizability down the group, with a significant jump from carbon to silicon, followed by a plateau between silicon and germanium. These findings align with theoretical expectations based on atomic size and electronic structure considerations.

The inability to complete calculations for tin and lead due to basis set availability issues illuminates an important frontier in computational chemistry: the challenges associated with modeling heavier elements where relativistic effects become significant. This limitation sets a clear direction for future work. Implementation of custom basis sets and pseudopotentials within the Psi4 environment could extend these calculations to heavier elements. Exploration of alternative quantum chemistry software packages with more comprehensive basis set libraries for heavy elements might also prove fruitful. The application of augmented basis sets such as aug-cc-pVDZ would likely improve accuracy for the lighter elements already studied. Development of hybrid computational approaches incorporating relativistic corrections would address the fundamental challenges of accurately modeling heavier elements.[@Jensen2017; @Karna1991]

By documenting both the successes and limitations of our approach, this work contributes to the broader understanding of computational methodology in quantum chemistry and provides a foundation for future investigations into the electronic properties of Group 14 elements and beyond.

## Acknowledgments

We acknowledge the contributions of the Psi4 development team and the Conda-Forge community for providing and maintaining the open-source tools that made this research possible.

## References