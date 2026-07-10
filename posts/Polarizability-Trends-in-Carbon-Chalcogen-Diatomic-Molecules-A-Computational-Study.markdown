---
title: Polarizability Trends in Carbon-Chalcogen Diatomic Molecules - A Computational Study
date: 2025-02-28
tags: quantum chemistry, polarizability, computational chemistry, psi4, carbon, chalcogens
description: A systematic computational investigation of polarizability in diatomic molecules formed between carbon and Group 16 (O, S, Se, Te) elements, with analysis of geometry-optimized structures and higher-order electronic properties.
---

# Abstract
This study presents a detailed analysis of polarizabilities and hyperpolarizabilities in carbon-chalcogen diatomic molecules (CO, CS, CSe, CTe). Using B3LYP/aug-cc-pVTZ level of theory for lighter elements and def2-TZVP with ECPs for heavier elements, we calculated longitudinal polarizabilities and hyperpolarizabilities for optimized structures. Results show clear periodic trends, with polarizability increasing from CO (15.47 a.u.) to CTe (63.90 a.u.), revealing a strong correlation with bond length and chalcogen size. We observe significant nonlinear optical responses, particularly for CTe which exhibits a hyperpolarizability (β) of -10.25 a.u. and a substantial negative second hyperpolarizability (γ) of -7093.30 a.u. This work provides quantitative insights into how chalcogen substitution affects electronic response properties and demonstrates the effectiveness of automated computational pipelines for systematic prediction of molecular properties.

# Introduction
Polarizability—the measure of a molecule's electron cloud deformability in response to an external electric field—represents a fundamental property governing numerous physical and chemical phenomena, from intermolecular forces to optical properties.[@Jensen2017] In particular, the polarizability (α), first hyperpolarizability (β), and second hyperpolarizability (γ) define how molecules interact with electromagnetic radiation and determine their potential applications in nonlinear optics.
Carbon-chalcogen diatomic molecules (where chalcogens are Group 6A/14 elements: O, S, Se, Te) provide an excellent case study for examining how systematic replacement of the chalcogen affects molecular electronic response properties. As one moves down Group 6A, several important changes occur: increasing atomic size, decreasing electronegativity, more diffuse valence orbitals, and for heavier elements, significant relativistic effects.[@Pyykko2012] These variations should manifest in the polarizability and hyperpolarizability values, revealing important structure-property relationships.
The polarizability tensor component α<sub>zz</sub> (along the molecular axis) can be approximated through the numerical derivative approach known as the finite field method:[@Cohen1975]

$$\alpha_{zz} \approx \frac{\mu_z(F_z = +h) - \mu_z(F_z = -h)}{2h}$$

where h represents the applied electric field strength and μ<sub>z</sub> is the z-component of the dipole moment. Similarly, hyperpolarizabilities can be estimated from higher-order numerical derivatives or from polynomial fits to the field-dependent dipole moment.

Building upon our previous work on Group 14-16 heteronuclear molecules, this study focuses specifically on carbon-chalcogen combinations, with three primary objectives: (1) demonstrating the power of computational automation with geometry optimization for systematic property prediction, (2) identifying periodic trends across the chalcogen series, and (3) exploring higher-order nonlinear optical properties (β and γ) in addition to the linear polarizability (α).

This work contributes to the broader understanding of structure-property relationships in simple diatomic molecules and provides a foundation for future investigations into more complex systems containing carbon and chalcogen elements.

# Experimental
## Environment Setup
All calculations were performed using Psi4 version 1.7 within a dedicated Conda environment running Python 3.8. The computational environment was established as follows:
```bash
# Create a new conda environment for quantum chemistry
conda create -n qchem python=3.8
conda activate qchem

# Install pydantic with a compatible version
pip install pydantic==1.10.8

# Install Psi4 through conda
conda install -c psi4 psi4
conda install -c psi4 dftd3 gcp

# Install additional dependencies
conda install numpy scipy matplotlib
```

## Calculation Approach

We employed the finite field method to calculate polarizabilities and hyperpolarizabilities, applying electric fields of +0.002, +0.001, 0.0, -0.001, and -0.002 atomic units along the molecular axis (z-direction) and measuring the resulting changes in the molecular dipole moment. The use of five field strengths allowed for more robust estimation through linear regression and enabled extraction of higher-order nonlinear terms.

All molecular geometries were first optimized at the B3LYP level of theory to ensure that the electronic property calculations were performed at realistic equilibrium structures. This represents an improvement over fixed-geometry approaches, particularly for ensuring accuracy in the heavier chalcogen compounds where empirical bond lengths may be less reliable.

For each carbon-chalcogen combination, the calculation workflow consisted of:

Geometry optimization at the B3LYP level with an appropriate basis set
Field-dependent energy and dipole calculations at the optimized geometry
Regression analysis to extract polarizability and hyperpolarizability values

Appropriate basis sets were selected based on the elements involved:

For C and O: aug-cc-pVTZ basis sets were employed
For S and Se: aug-cc-pVTZ and def2-TZVP basis sets were used, respectively
For Te: def2-TZVP basis set with effective core potentials (ECPs) was used to account for relativistic effects

## Python Implementation

The calculations were implemented in a Python script that automated the entire process. The script handled geometry optimization, field-dependent calculations, and property extraction, encapsulating the workflow in modular functions that enabled systematic analysis across the series of molecules.
A simplified version of the key calculation functions is shown below:

```python
def optimize_geometry(group14_element):
    """Optimize the geometry of a C-X molecule"""
    molecule_name = f"C{group14_element}"
    
    # Define molecule with initial geometry
    molecule = psi4.geometry(f"""
    0 1
    C 0.0 0.0 0.0
    {group14_element} 0.0 0.0 {initial_bond_length * 1.889725989}
    units bohr
    symmetry c1
    """)
    
    # Set appropriate basis sets and run optimization
    # [basis set selection code]
    
    opt_energy = psi4.optimize('b3lyp')
    optimized_molecule = psi4.core.get_active_molecule()
    
    # Calculate optimized bond length
    natoms = optimized_molecule.natom()
    x1, y1, z1 = optimized_molecule.x(0), optimized_molecule.y(0), optimized_molecule.z(0)
    x2, y2, z2 = optimized_molecule.x(1), optimized_molecule.y(1), optimized_molecule.z(1)
    bond_length = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) / 1.889725989
    
    return optimized_molecule, bond_length

def calculate_properties(group14_element):
    """Calculate dipole moment and polarizabilities for a C-X molecule"""
    # First optimize the geometry
    optimized_molecule, bond_length = optimize_geometry(group14_element)
    
    # Run field-dependent calculations
    field_results = {}
    for field in fields:
        result = run_field_calculation(optimized_molecule, group14_element, field)
        if result:
            field_results[field] = result
    
    # Extract dipole moments for each field
    field_values = []
    dipole_values = []
    for field in sorted(field_results.keys()):
        field_values.append(field)
        dipole_values.append(field_results[field]['dipole'][2])  # Z-component
    
    # Calculate alpha using linear regression
    alpha_model = stats.linregress(field_values, dipole_values)
    alpha = -alpha_model.slope
    
    # Calculate beta and gamma using polynomial fit
    if len(field_values) >= 5:
        cubic_fit = np.polyfit(field_values, dipole_values, 3)
        beta = cubic_fit[1] * 2  # Related to second derivative of energy
        gamma = cubic_fit[0] * 6  # Related to third derivative of energy
    
    # [results storage and return code]
```

This approach enabled systematic and consistent calculation of polarizabilities and hyperpolarizabilities across the entire series of carbon-chalcogen molecules.

# Results

## Optimized Molecular Geometries

The geometry optimization yielded the following equilibrium bond lengths for the carbon-chalcogen series:

**Table 1:** Optimized Carbon-Chalcogen Bond Lengths. Bond lengths obtained from B3LYP geometry optimizations showing systematic increase with increasing chalcogen size.

| Molecule | Bond Length / Å |
|:--------:|:---------------:|
| CO       | 1.126          |
| CS       | 1.534          |
| CSe      | 1.676          |
| CTe      | 1.893          |

The bond lengths show a clear increasing trend down the chalcogen group, consistent with the increasing atomic radii of the chalcogen elements. This trend follows the expected pattern based on the relative sizes of the atoms involved and aligns with experimental values from the literature.

### Dipole Moments and Polarizabilities

Our calculations yielded the following electronic response properties for the carbon-chalcogen series:

**Table 2:** Calculated Electronic Properties for Carbon-Chalcogen Molecules. Electronic response properties including dipole moments, polarizabilities (α), and first (β) and second (γ) hyperpolarizabilities for the optimized carbon-chalcogen molecules.

| Molecule | Dipole Moment / Debye | Polarizability, α / a.u. | Hyperpolarizability, β / a.u. | Second Hyperpolarizability, γ / a.u. |
|:--------:|:---------------------:|:------------------------:|:-----------------------------:|:-----------------------------------:|
| CO       | 0.037                 | 15.47                    | 32.52                         | -1948.61                           |
| CS       | 0.759                 | 38.05                    | 27.40                         | -10026.17                          |
| CSe      | 0.829                 | 46.40                    | 14.09                         | -3590.20                           |
| CTe      | 1.017                 | 63.90                    | -10.25                        | -7093.30                           |


<figure>
  <img src="/images/c-chalcogen-bond-lengths.svg" alt="Bond Length vs. Polarizability">
  <figcaption><strong>Figure 1.</strong> Bond Length vs. Polarizability Correlation. Scatter plot showing the relationship between bond length and polarizability across the carbon-chalcogen molecular series, with a linear trend line showing the strong correlation (R² = 0.995).</figcaption>
</figure>

<figure>
  <img src="/images/c-chalcogen-polarizability-trends.svg" alt="Polarizability Trends">
  <figcaption><strong>Figure 2.</strong> Polarizability Trends for Carbon Elements Across Group VIA. Line plot demonstrating the consistent increase in polarizability when moving from oxygen to tellurium compounds for carbon.</figcaption>
</figure>

# Discussion

## Periodic Trends and Structure-Property Relationships

The systematic increase in polarizability from CO to CTe can be attributed to several factors:

The systematic increase in polarizability from CO to CTe can be attributed to several factors. Longer bonds generally correspond to more diffuse electron distributions that are more easily distorted by external fields. The correlation between bond length and polarizability (Figure 1) supports this interpretation. The electronegativity decreases down Group 16 (O: 3.44, S: 2.58, Se: 2.55, Te: 2.10), resulting in less tightly bound electrons that can respond more readily to applied fields. Additionally, heavier chalcogens have more electrons and larger, more diffuse electron clouds, contributing significantly to the overall polarizability. For the heavier elements, particularly Te, relativistic effects become relevant and can influence the electronic structure and response properties.

## Nonlinear Optical Properties

The hyperpolarizability (β) and second hyperpolarizability (γ) values reveal interesting insights about the nonlinear optical properties of these molecules. The change from positive to negative β values for CTe indicates a fundamental change in the nonlinear response character. This could be related to the shifting balance between σ and π bonding components as the bond becomes longer and weaker. The large negative second hyperpolarizabilities suggest these molecules would exhibit significant negative nonlinear refractive indices at appropriate frequencies. CS shows the most extreme value, which may be related to its particular electronic structure and the balance of σ and π bonding/antibonding contributions. Unlike the polarizability, which increases steadily down the group, the hyperpolarizabilities show more complex behavior. This underscores the fact that higher-order responses depend on subtle details of the electronic structure beyond simple size and bond length considerations.

## Comparison with Previous Work

Our calculated polarizability for CO (15.47 a.u.) aligns well with literature values, which typically range from 13-17 a.u. in experimental and high-level computational studies.[@Maroulis1996] The use of geometry optimization and the B3LYP functional with augmented basis sets has likely contributed to the good agreement with reference data. The increasing trend in polarizability down the chalcogen group is consistent with previous computational studies on similar systems, though our work extends this analysis to include the heavier chalcogens and the higher-order nonlinear properties. Compared to the results from our earlier study on Group 14-16 heteronuclear molecules, the polarizability values for carbon-chalcogen compounds follow similar trends, though with some quantitative differences due to the different computational approach (B3LYP vs. SCF) and the use of geometry optimization in the present work.

## Computational Considerations

The use of geometry optimization prior to property calculations represents an important methodological improvement over fixed-geometry approaches. This is particularly relevant for the heavier chalcogens where experimental geometries may be less readily available or reliable. The B3LYP functional provides a good balance between computational cost and accuracy for these systems, capturing electron correlation effects that are important for accurate polarizability predictions. The augmented basis sets (aug-cc-pVTZ) for the lighter elements ensure appropriate flexibility in the outer regions of the electron density, which is crucial for polarizability calculations. For the heaviest element (Te), the use of effective core potentials (ECPs) was essential to account for relativistic effects without prohibitive computational cost. The successful calculation of properties for the full series from CO to CTe demonstrates the effectiveness of this computational approach.

## Implications and Applications

The systematic dataset of molecular polarizabilities and hyperpolarizabilities presented here contributes to our understanding of fundamental structure-property relationships in carbon-chalcogen compounds. These insights have several potential applications. The trends identified could guide the design of novel materials for nonlinear optical applications, particularly those containing carbon-chalcogen bonds. Accurate polarizability values are essential for modeling dispersion forces and other non-bonded interactions in molecular simulations. Our data could inform parameterization of force fields for systems containing these elements. Polarizability derivatives determine Raman activity, and our results could help predict relative Raman intensities across related molecules. These results provide benchmark data for testing and validating different computational methods for predicting electronic response properties. Beyond specific applications, this work demonstrates a methodologically sound approach to computational property prediction that could be extended to other molecular systems and properties of interest.

## Future Directions

This study provides a foundation for several promising directions of future research. Applying similar analyses to homologous series with other Group 14 elements (Si, Ge, Sn, Pb) bonded to chalcogens would complete the periodic trends across both groups. Employing more sophisticated methods like CCSD(T) for selected molecules would help assess the accuracy of DFT predictions for these properties. Extending to dynamic polarizabilities and hyperpolarizabilities would explore optical dispersion effects relevant to applications. Developing quantitative structure-property relationship models could enable prediction of polarizabilities based on readily available molecular descriptors, facilitating materials design. The computational methodology demonstrated here could also be extended to polyatomic molecules containing carbon-chalcogen bonds, opening pathways to more complex and practically relevant systems.

## Conclusion

This study has successfully mapped the polarizability landscape across the carbon-chalcogen series (CO, CS, CSe, CTe), revealing clear trends and structure-property relationships. The polarizability increases systematically from CO to CTe, correlating strongly with bond length and chalcogen size. The nonlinear optical properties (β and γ) exhibit more complex behavior, with β changing sign for CTe and all molecules showing substantial negative γ values.

The computational methodology employed here—combining geometry optimization, the B3LYP functional, and appropriate basis sets—proved effective for systematically investigating these trends. The automation of the computational workflow through Python scripting enabled efficient calculation and analysis of properties across the molecular series.

# Acknowledgments

We acknowledge the contributions of the Psi4 development team and the Conda-Forge community for providing and maintaining the open-source tools that made this research possible.

# References