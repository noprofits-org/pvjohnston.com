---
title: Mathematical Frameworks and Basis Sets in Excited State Calculations
date: 2025-03-22
tags: quantum chemistry, excited states, TD-DFT, EOM-CCSD, basis sets, ADC, CASSCF, benchmark studies
description: A comprehensive explanation of the mathematical principles underlying excited state calculations, including TD-DFT, EOM-CCSD, ADC, and CASSCF methodologies, as well as detailed discussions on basis set selection, computational considerations, and practical applications.
---

## Introduction

Computational chemistry has become an indispensable tool for studying molecular properties, including electronic excited states. Time-dependent density functional theory (TD-DFT) and equation-of-motion coupled-cluster singles and doubles (EOM-CCSD) are two widely used methods for these calculations. Understanding the mathematical frameworks behind these methods and the role of basis sets is crucial for interpreting and evaluating computational results. This text provides a comprehensive overview of these topics, aiming to serve as supplemental educational material.

Excited state calculations are essential for predicting and interpreting spectroscopic properties, understanding photochemical reactions, and designing new materials with specific optical properties. The accuracy of these calculations depends on both the theoretical method employed and the basis set used to represent molecular orbitals. This expanded discussion aims to provide deeper insights into the mathematical foundations, practical considerations, and recent developments in excited state calculations.

## Time-Dependent Density Functional Theory (TD-DFT)

TD-DFT is an extension of density functional theory (DFT) to time-dependent phenomena, enabling the calculation of electronic excitation energies and oscillator strengths. The fundamental principle of DFT is that the electronic energy of a molecule can be determined by its electron density, rather than its many-electron wavefunction.[@Casida1995]

### Mathematical Framework

The time-dependent Kohn-Sham equations are the core of TD-DFT. These equations describe the evolution of the electronic system under a time-dependent external potential:

$$i \frac{\partial \phi_i(\mathbf{r}, t)}{\partial t} = \left[ -\frac{1}{2} \nabla^2 + v_{ext}(\mathbf{r}, t) + v_{H}(\mathbf{r}, t) + v_{xc}(\mathbf{r}, t) \right] \phi_i(\mathbf{r}, t)$$

where $\phi_i(\mathbf{r}, t)$ are the time-dependent Kohn-Sham orbitals, $v_{ext}(\mathbf{r}, t)$ is the external potential due to nuclei, $v_{H}(\mathbf{r}, t)$ is the Hartree potential representing electron-electron Coulomb repulsion, and $v_{xc}(\mathbf{r}, t)$ is the exchange-correlation potential, which accounts for all non-classical electron-electron interactions.[@Marques2012]

The excitation energies are obtained by solving the Casida equations:

$$\mathbf{\Omega F}_i = \omega_i^2 \mathbf{F}_i$$

where $\mathbf{\Omega}$ is the Hessian matrix, $\mathbf{F}_i$ are eigenvectors related to the transition amplitudes, and $\omega_i$ are the excitation energies.

The oscillator strength ($f$), which determines the intensity of electronic transitions, is calculated from the transition dipole moment:

$$f = \frac{2}{3} \omega_i |\langle \Psi_0 | \hat{\mu} | \Psi_i \rangle|^2$$

where $\hat{\mu}$ is the dipole moment operator, and $\Psi_0$ and $\Psi_i$ are the ground and excited state wavefunctions, respectively.

### Linear Response Theory in TD-DFT

The linear response formulation of TD-DFT provides a practical approach for calculating excitation energies. In this framework, we consider the response of the electron density to a small time-dependent perturbation. This relationship can be expressed mathematically as:

$$\delta \rho(\mathbf{r}, t) = \int \chi(\mathbf{r}, \mathbf{r}', t-t') \delta v_{ext}(\mathbf{r}', t') d\mathbf{r}' dt'$$

where $\chi(\mathbf{r}, \mathbf{r}', t-t')$ is the linear response function. The poles of this response function correspond to the excitation energies of the system.[@Marques2012]

The Casida equations mentioned earlier can be rewritten in matrix form:

$$\begin{pmatrix} \mathbf{A} & \mathbf{B} \\ \mathbf{B}^* & \mathbf{A}^* \end{pmatrix} \begin{pmatrix} \mathbf{X} \\ \mathbf{Y} \end{pmatrix} = \omega \begin{pmatrix} \mathbf{1} & \mathbf{0} \\ \mathbf{0} & -\mathbf{1} \end{pmatrix} \begin{pmatrix} \mathbf{X} \\ \mathbf{Y} \end{pmatrix}$$

where $\mathbf{A}$ and $\mathbf{B}$ are matrices with elements:

$$A_{ia,jb} = \delta_{ij} \delta_{ab} (\epsilon_a - \epsilon_i) + (ia|jb) + (ia|f_{xc}|jb)$$
$$B_{ia,jb} = (ia|bj) + (ia|f_{xc}|bj)$$

Here, $i$ and $j$ refer to occupied orbitals, $a$ and $b$ to virtual orbitals, $\epsilon$ are orbital energies, and $f_{xc}$ is the exchange-correlation kernel.

### Exchange-Correlation Functionals

The choice of exchange-correlation functional ($v_{xc}$) is critical in TD-DFT. Hybrid functionals, such as B3LYP and PBE0, combine exact exchange from Hartree-Fock theory with DFT exchange and correlation. Range-separated functionals, like CAM-B3LYP and $\omega$B97X-D, employ different exchange functionals for short-range and long-range interactions, improving the description of charge-transfer and Rydberg states. The selection of an appropriate functional depends on the specific molecular system and the types of excited states being studied.

### Advanced TD-DFT Approaches

The Tamm-Dancoff approximation (TDA) simplifies the TD-DFT equations by setting the $\mathbf{B}$ matrix to zero, resulting in a simplified eigenvalue equation:

$$\mathbf{A X} = \omega \mathbf{X}$$

This approximation reduces computational cost and can sometimes provide more stable results, particularly for systems with triplet instabilities or near conical intersections. The TDA is equivalent to configuration interaction singles (CIS) when using Hartree-Fock orbitals.[@Laurent2013]

Double-hybrid functionals, such as B2PLYP and PWPB95, incorporate both exact exchange and second-order perturbative correlation. In TD-DFT calculations, they can significantly improve accuracy, especially for states with double excitation character, which are poorly described by standard TD-DFT.[@Laurent2013]

Spin-flip TD-DFT allows for the calculation of excited states with different spin multiplicity than the reference state. Starting from a high-spin reference (e.g., triplet), one can access low-spin excited states (e.g., singlets) and ground states that have multi-reference character. This approach is particularly useful for diradicals, conical intersections, and bond-breaking processes.[@Gonzalez2012]

### Limitations of TD-DFT

While TD-DFT is widely used due to its favorable scaling with system size, it has several important limitations. Standard functionals often underestimate the energy of charge-transfer states due to incorrect asymptotic behavior of the exchange-correlation potential. States with significant double excitation character are not well described within the adiabatic approximation commonly used in TD-DFT. Diffuse excited states (Rydberg states) may be poorly described without appropriate long-range corrected functionals and diffuse basis functions. Some systems exhibit triplet instabilities, leading to unphysical negative excitation energies. Additionally, TD-DFT within the adiabatic approximation fails to correctly describe the topology around conical intersections.[@Laurent2013]

## Equation-of-Motion Coupled-Cluster Singles and Doubles (EOM-CCSD)

EOM-CCSD is a high-level method that provides a more accurate description of excited states by explicitly accounting for electron correlation. This approach addresses many of the limitations of TD-DFT but comes with increased computational cost.[@Krylov2008]

### Mathematical Framework

The EOM-CCSD method is based on the coupled-cluster (CC) theory, which approximates the exact wavefunction as:

$$|\Psi_{CC}\rangle = e^{\hat{T}} |\Phi_0\rangle$$

where $\hat{T}$ is the cluster operator, and $|\Phi_0\rangle$ is the Hartree-Fock reference determinant.

The excited state wavefunctions are obtained by applying an excitation operator $\hat{R}$ to the CC ground state:

$$|\Psi_{EOM}\rangle = \hat{R} e^{\hat{T}} |\Phi_0\rangle$$

where $\hat{R} = \sum_i r_i \hat{a}_i^\dagger \hat{a}_0 + \sum_{ijab} r_{ij}^{ab} \hat{a}_a^\dagger \hat{a}_b^\dagger \hat{a}_j \hat{a}_i + ...$ includes single and double excitations.

The excitation energies are then obtained by solving the eigenvalue equation:

$$\bar{H} R = \omega R$$

where $\bar{H} = e^{-\hat{T}} \hat{H} e^{\hat{T}}$ is the similarity-transformed Hamiltonian.

### Detailed Working Equations for EOM-CCSD

The similarity-transformed Hamiltonian can be expressed as a Baker-Campbell-Hausdorff expansion:

$$\bar{H} = \hat{H} + [\hat{H}, \hat{T}] + \frac{1}{2!}[[\hat{H}, \hat{T}], \hat{T}] + \frac{1}{3!}[[[\hat{H}, \hat{T}], \hat{T}], \hat{T}] + \frac{1}{4!}[[[[\hat{H}, \hat{T}], \hat{T}], \hat{T}], \hat{T}]$$

In the EOM-CCSD approach, the cluster operator $\hat{T}$ is truncated at doubles:

$$\hat{T} = \hat{T}_1 + \hat{T}_2 = \sum_{ia} t_i^a \hat{a}_a^\dagger \hat{a}_i + \frac{1}{4} \sum_{ijab} t_{ij}^{ab} \hat{a}_a^\dagger \hat{a}_b^\dagger \hat{a}_j \hat{a}_i$$

Similarly, the excitation operator $\hat{R}$ is truncated at doubles:

$$\hat{R} = \hat{R}_0 + \hat{R}_1 + \hat{R}_2 = r_0 + \sum_{ia} r_i^a \hat{a}_a^\dagger \hat{a}_i + \frac{1}{4} \sum_{ijab} r_{ij}^{ab} \hat{a}_a^\dagger \hat{a}_b^\dagger \hat{a}_j \hat{a}_i$$

The matrix elements of $\bar{H}$ are then computed, and the resulting large eigenvalue problem is solved using iterative techniques such as the Davidson algorithm.[@Sneskov2012]

### EOM-CCSD Variants and Extensions

The spin-flip EOM-CCSD approach starts from a high-spin reference state and accesses low-spin states through spin-flipping excitations. This approach is particularly valuable for systems with multi-reference character, such as diradicals and bond-breaking situations. The method provides a balanced description of states with different spin multiplicities and can describe conical intersections between them.[@Krylov2008]

EOM-CCSD for ionized states (EOM-IP-CCSD) calculates ionization potentials and the corresponding ionized states by applying an electron-removing operator to the CC ground state:

$$|\Psi_{IP}\rangle = \hat{R}_{IP} e^{\hat{T}} |\Phi_0\rangle$$

where $\hat{R}_{IP}$ removes an electron from the system. This approach is valuable for studying cationic states and ionization processes.[@Krylov2008]

Similarly, electron attachment energies are calculated using an electron-attaching operator in the EOM-EA-CCSD approach:

$$|\Psi_{EA}\rangle = \hat{R}_{EA} e^{\hat{T}} |\Phi_0\rangle$$

This variant is particularly useful for studying anionic states and electron attachment processes.

EOM-CCSD can be systematically improved by including higher excitations. EOM-CCSDT includes single, double, and triple excitations, while EOM-CCSDTQ includes singles, doubles, triples, and quadruples. These methods offer increased accuracy but come at significantly higher computational cost. More practical approximations include EOM-CCSD(T), which includes perturbative triples correction, and EOM-CCSDR(3), which includes non-iterative triples correction specific for excited states.[@Sneskov2012]

## Alternative Methods for Excited State Calculations

### Algebraic Diagrammatic Construction (ADC)

Algebraic Diagrammatic Construction (ADC) is a propagator method based on perturbation theory that provides a balanced description of various types of excited states. The ADC scheme can be systematically improved through different orders of perturbation theory. ADC(1) is equivalent to configuration interaction singles (CIS). ADC(2) includes second-order terms, offering a good balance between accuracy and cost. ADC(2)-x is an extended version with additional second-order terms. ADC(3) includes third-order terms for improved accuracy.[@Schirmer2018]

The working equations for ADC can be derived from the polarization propagator:

$$\Pi(\omega) = \langle \Phi_0 | \hat{V}^\dagger \frac{1}{\omega - (\hat{H} - E_0) + i\eta} \hat{V} | \Phi_0 \rangle$$

where $\hat{V}$ is an excitation operator, and $E_0$ is the ground state energy. ADC methods are particularly valuable for calculating core-excited states using the core-valence separated approach (CVS-ADC), which allows for the selective computation of core excitations without having to compute all valence excitations first.

### Complete Active Space Self-Consistent Field (CASSCF)

Complete Active Space Self-Consistent Field (CASSCF) is a multi-reference method that treats a subset of electrons and orbitals (the active space) exactly, while the remaining electrons occupy doubly-occupied or empty orbitals. The wavefunction is expressed as a linear combination of configuration state functions (CSFs):

$$|\Psi_{CASSCF}\rangle = \sum_I c_I |\Phi_I\rangle$$

where $|\Phi_I\rangle$ are CSFs constructed from the active space, and $c_I$ are the expansion coefficients. CASSCF calculations can provide accurate descriptions of excited states with multi-reference character, conical intersections, and bond-breaking processes. However, they require careful selection of the active space and can become computationally demanding for large active spaces.[@Gonzalez2012]

### Multi-Reference Configuration Interaction (MRCI)

Multi-Reference Configuration Interaction (MRCI) extends CASSCF by including dynamic correlation through configuration interaction. The wavefunction is expressed as a sum of reference configurations and additional excited configurations:

$$|\Psi_{MRCI}\rangle = \sum_I c_I |\Phi_I\rangle + \sum_A c_A |\Phi_A\rangle$$

where $|\Phi_I\rangle$ are the reference CSFs (typically from CASSCF), and $|\Phi_A\rangle$ are additional excited configurations. MRCI can provide highly accurate excitation energies but is computationally intensive and typically limited to small or medium-sized molecules.[@Gonzalez2012]

## Basis Sets

Basis sets are sets of atomic orbitals used to approximate molecular orbitals in quantum chemical calculations. The choice of basis set affects the accuracy and computational cost of the calculations. A fundamental understanding of different types of basis sets is essential for selecting appropriate ones for excited state calculations.[@Jensen2017]

### Types of Basis Sets

Minimal basis sets, such as STO-3G, use the minimum number of functions to represent each atom. They are computationally inexpensive but provide limited accuracy. Split-valence basis sets, like 6-31G and 6-311G, use multiple functions to describe valence electrons, improving accuracy for properties that depend on valence electronic structure. Polarized basis sets, including 6-31G(d,p) and 6-311+G(d,p), add polarization functions (d- and p-type functions) that allow for better description of electron density distortion. The "+" notation denotes diffuse functions, which are important for excited states, particularly Rydberg states. Correlation-consistent basis sets, such as cc-pVDZ and cc-pVTZ, are designed to systematically converge to the complete basis set limit, improving correlation energy calculations.

### Mathematical Representation of Basis Functions

Gaussian-type orbitals (GTOs) are commonly used in quantum chemistry due to their computational efficiency. A primitive Gaussian function is expressed as:

$$g_{nlm}(\mathbf{r}, \alpha) = N Y_{lm}(\theta, \phi) r^{n-1} e^{-\alpha r^2}$$

where $N$ is a normalization constant, $Y_{lm}$ are spherical harmonics, $r$ is the distance from the nucleus, and $\alpha$ is the orbital exponent. Contracted Gaussian functions, which are used in most modern basis sets, are linear combinations of primitive Gaussians:

$$\phi_{nlm}(\mathbf{r}) = \sum_i c_i g_{nlm}(\mathbf{r}, \alpha_i)$$

where $c_i$ are contraction coefficients. This mathematical form allows for efficient computation of the necessary integrals in quantum chemical calculations.[@Jensen2017]

### Basis Set Effects on Excited State Calculations

The choice of basis set can significantly affect the accuracy of excited state calculations. Valence excitations typically require at least a split-valence basis set with polarization functions (e.g., 6-31G(d)) for reasonable accuracy. Rydberg excitations involve transitions to diffuse orbitals and require basis sets with diffuse functions (e.g., 6-31+G(d) or aug-cc-pVDZ) to properly describe the extended nature of these states. Charge-transfer excitations are sensitive to the long-range behavior of the basis functions and often require both polarization and diffuse functions to achieve accurate energetics. Core excitations involve transitions from core orbitals and require basis sets with tight functions to properly describe core electrons, such as core-polarized or core-valence basis sets.[@Schreiber2008]

### Specialized Basis Sets for Excited States

Several specialized basis sets have been developed for excited state calculations. Augmented correlation-consistent basis sets (aug-cc-pVXZ, where X = D, T, Q, 5, 6) include additional diffuse functions for each angular momentum. These are particularly important for Rydberg states and electron affinities. Double augmented basis sets (d-aug-cc-pVXZ) include a second set of diffuse functions, which can be important for highly excited Rydberg states. Core-valence basis sets (cc-pCVXZ) include additional tight functions to better describe core-valence correlation, which is important for core-excited states.[@Schreiber2008]

To mitigate basis set incompleteness error, extrapolation schemes can be used. For the Hartree-Fock energy, a common extrapolation formula is:

$$E_X = E_{CBS} + A X^{-3}$$

For the correlation energy, the extrapolation typically takes the form:

$$E_X = E_{CBS} + B X^{-\alpha}$$

where $X$ is the cardinal number of the basis set (2 for DZ, 3 for TZ, etc.), and $\alpha$ is typically between 2.2 and 3.0. These extrapolation schemes can significantly improve the accuracy of excited state calculations.[@Jensen2017]

### Basis Set Differences

Different basis sets have distinct characteristics that make them suitable for various types of calculations. For example, the 6-311+G(d,p) basis set is a split-valence basis set with diffuse and polarization functions. The "6" indicates the core orbitals are represented by six contracted Gaussian functions. The "311" indicates the valence orbitals are represented by three functions, the first is contracted by 3 Gaussians, the other two are single Gaussians. The "+G" indicates diffuse functions, and "(d,p)" indicates polarization functions on heavy atoms and hydrogen atoms.

In contrast, cc-pVDZ is a correlation-consistent basis set of double-zeta quality. "cc" indicates correlation-consistent, "pV" indicates polarization valence, and "DZ" indicates double-zeta. Correlation consistent basis sets are designed to systematically converge to the complete basis set limit.

Table 1 presents a comparison of basis set performance for different types of excited states. This comparison highlights the importance of selecting appropriate basis sets based on the specific types of excited states being studied. As shown in Table 1, augmented basis sets (aug-cc-pVDZ and aug-cc-pVTZ) perform well for Rydberg and charge-transfer states but come with increased computational cost. Standard polarized basis sets like 6-31G(d) may be sufficient for valence excitations but perform poorly for diffuse excited states.

**Table 1.** Comparison of basis set performance for different types of excited states.

| Basis Set | Valence States | Rydberg States | Charge-Transfer States | Computational Cost |
|-----------|---------------|----------------|------------------------|-------------------|
| 6-31G(d)  | Moderate      | Poor           | Poor                   | Low               |
| 6-31+G(d) | Moderate      | Good           | Moderate               | Moderate          |
| 6-311++G(2d,2p) | Good    | Very Good      | Good                   | High              |
| cc-pVDZ   | Moderate      | Poor           | Poor                   | Moderate          |
| aug-cc-pVDZ | Good        | Very Good      | Good                   | High              |
| aug-cc-pVTZ | Very Good   | Excellent      | Very Good              | Very High         |

## Computational Considerations and Best Practices

### Benchmarking and Method Selection

The choice of computational method should be guided by benchmark studies and the specific properties of interest. For valence excited states of closed-shell molecules, TD-DFT with hybrid or range-separated functionals is often sufficient, while EOM-CCSD provides higher accuracy but at increased computational cost. When studying charge-transfer states, range-separated functionals (e.g., CAM-B3LYP, ωB97X-D) or double hybrids are recommended, although EOM-CCSD is more reliable but computationally demanding. For states with multi-reference character, CASSCF/CASPT2 or MRCI are preferred, while spin-flip methods (SF-TD-DFT, SF-EOM-CCSD) can be effective alternatives. When investigating core-excited states, CVS-ADC or restricted-window TD-DFT with appropriate functionals should be employed, and core-valence basis sets are essential.[@Schreiber2008]

### Solvent Effects

Solvent effects can significantly influence excited state properties and should be considered in calculations aimed at reproducing experimental spectra. Implicit solvation models, such as the Polarizable Continuum Model (PCM), Conductor-like Screening Model (COSMO), and Solvation Model based on Density (SMD), represent the solvent as a continuous medium characterized by its dielectric constant. These models can be combined with excited state calculations using either linear-response (LR) or state-specific (SS) approaches. The LR approach includes solvent response to the transition density, while the SS approach considers equilibrium solvation for each state separately. For cases where specific solvent-solute interactions are important, explicit solvent models, including QM/MM approaches and cluster models with explicit solvent molecules, may be necessary.[@Laurent2013]

### Vibronic Structure and Spectral Simulations

To simulate absorption or emission spectra, vibronic effects should be considered. The vertical gradient approach uses harmonic approximation and vertical gradients to estimate Franck-Condon factors, providing a computationally efficient way to include vibronic structure. The adiabatic approach optimizes geometries for both ground and excited states, calculates vibrational frequencies and normal modes for each state, and computes Franck-Condon factors based on the overlap of vibrational wavefunctions. This approach provides a more accurate description of spectral shapes but is computationally more demanding. Herzberg-Teller effects account for intensity borrowing due to vibronic coupling and are important for formally forbidden transitions.[@Gonzalez2012]

### Computational Protocols for Different Applications

Different applications require tailored computational protocols. For UV-visible spectroscopy, a common approach involves optimizing ground state geometry using DFT with a hybrid functional, calculating vertical excitation energies using TD-DFT with a range-separated functional, including solvent effects using PCM or similar models, and considering vibronic effects for detailed spectral shapes. Fluorescence calculations require optimizing excited state geometry using TD-DFT or EOM-CCSD, calculating emission energy as the energy difference between excited and ground states at the excited state geometry, and including solvent relaxation effects using state-specific solvation models. Phosphorescence studies involve calculating triplet excitation energies using TD-DFT or EOM-CCSD, optimizing triplet state geometry, and including spin-orbit coupling for transition probabilities. Photochemical reaction studies require mapping potential energy surfaces of ground and excited states, locating conical intersections or crossing points, calculating minimum energy paths for photochemical pathways, and considering non-adiabatic dynamics for time-dependent properties.

## Recent Developments and Future Perspectives

### Machine Learning in Excited State Calculations

Machine learning approaches are increasingly being applied to accelerate excited state calculations. Neural network potentials, trained on high-level quantum chemical data, enable rapid exploration of excited state potential energy surfaces. Transfer learning leverages knowledge from simpler methods to improve predictions of more complex methods. Delta-learning approaches correct lower-level methods (e.g., TD-DFT) to match higher-level methods (e.g., EOM-CCSD) at reduced computational cost. These machine learning techniques are particularly valuable for studying large molecular systems and for applications requiring extensive sampling of configurational space.[@Gonzalez2012]

### Embedding Methods

Embedding approaches allow for high-level treatment of the important part of the system while using lower-level methods for the environment. QM/MM embedding combines quantum mechanical and molecular mechanical methods and is widely used for biological systems and solutions. Frozen density embedding divides the system into subsystems with frozen electron densities and accounts for polarization and Pauli repulsion between subsystems. Density Matrix Embedding Theory (DMET) embeds a fragment into an environment using a projection operator and can be combined with high-level excited state methods. These embedding approaches are essential for studying excited states in complex environments, such as photobiological processes and photochemical reactions in condensed phases.[@Sneskov2012]

### Beyond Single-Reference Methods

Developments in multi-reference methods continue to expand the range of systems that can be accurately treated. The Density Matrix Renormalization Group (DMRG) allows for larger active spaces than traditional CASSCF and can be combined with perturbation theory (DMRG-CASPT2) to include dynamic correlation. Selected Configuration Interaction methods adaptively select the most important configurations, including approaches like Configuration Interaction using a Perturbative Selection made Iteratively (CIPSI) and heat-bath CI. Multi-Reference Coupled Cluster methods combine the strengths of multi-reference methods and coupled cluster theory, with approaches like Mk-MRCC and internally contracted MRCC showing promise for accurate treatment of strongly correlated systems.[@Gonzalez2012]

## Conclusion

TD-DFT and EOM-CCSD provide powerful tools for calculating excited state properties. Understanding their mathematical frameworks and the role of basis sets is essential for accurate and reliable computational studies. The choice of method and basis set should be carefully considered based on the specific molecular system and properties of interest, as demonstrated in Table 1.

Advanced methods like ADC and CASSCF offer alternatives with specific advantages for certain types of excited states. The field continues to evolve with developments in machine learning, embedding methods, and multi-reference approaches, expanding the range of systems and properties that can be accurately studied computationally.

The combination of theoretical understanding, appropriate method selection, and careful consideration of computational details is crucial for obtaining reliable results in excited state calculations. By following best practices and leveraging recent developments, computational chemists can contribute significantly to the understanding of photophysical and photochemical processes.

## References