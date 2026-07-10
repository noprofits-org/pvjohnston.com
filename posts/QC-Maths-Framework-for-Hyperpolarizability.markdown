---
title: Mathematical Framework for Hyperpolarizability Calculations
date: 2025-02-25
tags: quantum chemistry, hyperpolarizability, computational chemistry, theoretical physics
description: A detailed explanation of the mathematical principles underlying hyperpolarizability calculations
---

## Introduction

Hyperpolarizability calculations represent a complex area of quantum chemistry that connects theoretical physics with practical applications in nonlinear optics and materials science. This post outlines the mathematical foundations that underpin the computational approaches we attempted to implement using Psi4. Understanding these equations is essential for interpreting results and troubleshooting computational issues in hyperpolarizability studies.[@Jensen2017]

## Energy Expansion in an External Electric Field

When a molecule is placed in an external electric field $\vec{F}$, its energy can be expressed as a Taylor series expansion:[@Bishop1990]

$$E(\vec{F}) = E^{(0)} - \sum_i \mu_i F_i - \frac{1}{2!} \sum_{ij} \alpha_{ij} F_i F_j - \frac{1}{3!} \sum_{ijk} \beta_{ijk} F_i F_j F_k - \frac{1}{4!} \sum_{ijkl} \gamma_{ijkl} F_i F_j F_k F_l - \ldots$$

where:
- $E^{(0)}$ is the energy of the molecule in the absence of an electric field
- $\mu_i$ is the permanent dipole moment (first-order term)
- $\alpha_{ij}$ is the polarizability tensor (second-order term)
- $\beta_{ijk}$ is the first hyperpolarizability tensor (third-order term)
- $\gamma_{ijkl}$ is the second hyperpolarizability tensor (fourth-order term)
- $i, j, k, l$ refer to Cartesian coordinates ($x$, $y$, $z$)

This expansion provides the theoretical basis for extracting polarizability and hyperpolarizability values from energy calculations.[@Kurtz1990]

## Dipole Moment Expansion

Similarly, the dipole moment of a molecule in the presence of an electric field can be expressed as:[@Boyd2008]

$$\mu_i(\vec{F}) = \mu_i^{(0)} + \sum_j \alpha_{ij} F_j + \frac{1}{2!} \sum_{jk} \beta_{ijk} F_j F_k + \frac{1}{3!} \sum_{jkl} \gamma_{ijkl} F_j F_k F_l + \ldots$$

where $\mu_i^{(0)}$ is the permanent dipole moment in the absence of an external field.

## Relation to Energy Derivatives

These properties can be rigorously defined as derivatives of the energy with respect to the field components:[@Karna1991]

$$\mu_i = -\left(\frac{\partial E}{\partial F_i}\right)_{\vec{F}=0}$$

$$\alpha_{ij} = -\left(\frac{\partial^2 E}{\partial F_i \partial F_j}\right)_{\vec{F}=0}$$

$$\beta_{ijk} = -\left(\frac{\partial^3 E}{\partial F_i \partial F_j \partial F_k}\right)_{\vec{F}=0}$$

$$\gamma_{ijkl} = -\left(\frac{\partial^4 E}{\partial F_i \partial F_j \partial F_k \partial F_l}\right)_{\vec{F}=0}$$

Alternatively, these properties can be expressed as derivatives of the dipole moment:

$$\alpha_{ij} = \left(\frac{\partial \mu_i}{\partial F_j}\right)_{\vec{F}=0}$$

$$\beta_{ijk} = \left(\frac{\partial^2 \mu_i}{\partial F_j \partial F_k}\right)_{\vec{F}=0}$$

$$\gamma_{ijkl} = \left(\frac{\partial^3 \mu_i}{\partial F_j \partial F_k \partial F_l}\right)_{\vec{F}=0}$$

## Finite Field Method

In computational chemistry, a common approach to calculate these properties is the finite field (FF) method.[@Cohen1975] For example, the polarizability component $\alpha_{xx}$ can be approximated as:

$$\alpha_{xx} \approx \frac{\mu_x(F_x=+h) - \mu_x(F_x=-h)}{2h}$$

where $h$ is a small electric field strength (typically 0.001-0.005 atomic units).

For the first hyperpolarizability component $\beta_{xxx}$, a similar finite difference approach gives:[@Rice1991]

$$\beta_{xxx} \approx \frac{\mu_x(F_x=+h) - 2\mu_x(F_x=0) + \mu_x(F_x=-h)}{h^2}$$

More generally, using a 5-point stencil for better numerical stability:[@Sekino1986]

$$\beta_{xxx} \approx \frac{-\mu_x(F_x=+2h) + 8\mu_x(F_x=+h) - 8\mu_x(F_x=-h) + \mu_x(F_x=-2h)}{12h^2}$$

## Coupled-Perturbed Hartree-Fock Method

In quantum chemistry software like Psi4, polarizabilities and hyperpolarizabilities can be calculated using response theory, particularly the Coupled-Perturbed Hartree-Fock (CPHF) method.[@Karna1991] In this approach, we solve for the response of the molecular orbitals to an external field.

The CPHF equations can be written as:

$$\sum_{bj} (A_{ai,bj} - \omega \delta_{ab}\delta_{ij})U_{bj}^{(k)}(\omega) = -V_{ai}^{(k)}$$

where:
- $a, b$ refer to virtual (unoccupied) orbitals
- $i, j$ refer to occupied orbitals
- $A_{ai,bj}$ is the electronic Hessian matrix
- $U_{bj}^{(k)}(\omega)$ is the orbital response to a perturbation in the $k$ direction
- $V_{ai}^{(k)}$ is the perturbation matrix element
- $\omega$ is the frequency of the electric field (0 for static properties)

Once the orbital response $U_{bj}^{(k)}$ is determined, the polarizability is calculated as:[@Parrish2017]

$$\alpha_{ij}(\omega) = -\sum_{ak} U_{ak}^{(i)}(\omega) V_{ak}^{(j)} + \sum_{ak} U_{ak}^{(j)}(\omega) V_{ak}^{(i)}$$

## Isotropic Averages and Invariants

For analysis purposes, it's common to calculate isotropic (orientation-independent) values:[@Shelton1992]

**Isotropic polarizability**:
$$\alpha = \frac{1}{3}(\alpha_{xx} + \alpha_{yy} + \alpha_{zz})$$

**Isotropic first hyperpolarizability**:
$$\beta = \sqrt{\beta_x^2 + \beta_y^2 + \beta_z^2}$$

where:
$$\beta_i = \frac{1}{3}\sum_j (\beta_{ijj} + \beta_{jij} + \beta_{jji})$$

**Isotropic second hyperpolarizability**:
$$\gamma = \frac{1}{5}(\gamma_{xxxx} + \gamma_{yyyy} + \gamma_{zzzz} + 2\gamma_{xxyy} + 2\gamma_{xxzz} + 2\gamma_{yyzz})$$

## Units and Conversion

In quantum chemistry calculations, properties are typically reported in atomic units (a.u.), which often need conversion for comparison with experimental values:[@Kajzar1989]

- Polarizability: 1 a.u. = 0.1482×10^(-24) cm³
- First hyperpolarizability: 1 a.u. = 8.6393×10^(-33) cm⁴/statvolt = 3.2063×10^(-53) C³m³/J²
- Second hyperpolarizability: 1 a.u. = 5.0367×10^(-40) cm⁵/statvolt = 6.2353×10^(-65) C⁴m⁴/J³

## Computational Implementation Considerations

When implementing these calculations in quantum chemistry packages like Psi4, several practical considerations arise:[@Parrish2017]

1. **Basis set selection**: Diffuse functions are crucial for accurate polarizability calculations, as they capture the response of the electron density to external fields
2. **Field strength**: The finite field method requires careful selection of field strengths—too large causes nonlinear effects, too small leads to numerical noise
3. **Symmetry handling**: Electric fields break molecular symmetry, which can complicate SCF convergence
4. **Method dependence**: Accurate hyperpolarizability calculations typically require correlated methods beyond Hartree-Fock, such as MP2, CCSD, or DFT with appropriate functionals

Our attempts to implement these calculations in Psi4 encountered challenges related to the specific implementation of property calculations in Psi4 1.7, particularly in the syntax for requesting polarizability calculations and handling response equations.

## Conclusion

The mathematical framework presented here forms the theoretical foundation for the computational approaches we attempted to implement. While we encountered practical challenges in our specific implementation with Psi4 1.7, the equations remain valid and could be implemented using alternative approaches or software packages. The finite field method, in particular, offers a robust alternative that can be applied across different software environments, provided appropriate care is taken in selecting field strengths and handling numerical derivatives.[@Jensen2017]

## References
