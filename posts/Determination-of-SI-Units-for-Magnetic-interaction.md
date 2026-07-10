---
title: Determination of SI Units for Magnetic Interactions in Quantum Mechanical Calculations
date: 2025-04-19
tags: quantum mechanics, electromagnetism, units, magnetic interaction, computational physics
description: A systematic derivation of the SI units involved in magnetic interactions at the quantum level, focusing on the correct dimensional analysis of magnetic moments, fields, and coupling constants.
---

## Abstract

This work presents a comprehensive analysis of the SI unit system as applied to magnetic interactions in quantum mechanical calculations. By systematically tracing the dimensional relationships between magnetic moments, magnetic fields, and energy, we derive the correct units for magnetic coupling constants and other key parameters in computational models. The analysis clarifies several common misconceptions regarding the units of magnetic quantities and provides a consistent framework for interpreting computational results in terms of measurable physical quantities. This approach is particularly valuable for researchers working at the interface of quantum chemistry and materials science, where precise understanding of magnetic interactions is essential for modeling and predicting the properties of magnetic materials.

## Introduction

Magnetic interactions play a crucial role in a wide range of physical phenomena, from the behavior of quantum spins in molecular magnets to the macroscopic properties of magnetic materials. However, the consistent application of units to magnetic quantities has been a persistent source of confusion in the scientific literature, partly due to the historical use of different unit systems (CGS, Gaussian, SI) and partly due to the inherent complexity of electromagnetic theory.[@Jackson1999]

In computational approaches to magnetic systems, this confusion can lead to errors in the interpretation of calculated results or in the parameterization of models. The situation is further complicated in quantum mechanical calculations, where magnetic moments arise from a combination of electronic and spin contributions, each with their own physical dimensions.[@Griffiths2018]

This work aims to provide a clear and systematic derivation of the SI units for magnetic quantities relevant to quantum mechanical calculations, with a particular focus on magnetic moments, fields, coupling constants, and their relationships to energy. By working from first principles and carefully tracking the dimensions of each quantity, we establish a consistent framework for unit conversion and for the interpretation of computational results.

## Theoretical Framework

### Fundamental Constants and Their Units

To establish a solid foundation for our analysis, we begin with the fundamental constants of electromagnetism in the SI system. The vacuum permeability, denoted by $\mu_0$, has a defined value of $4\pi \times 10^{-7}$ H/m (henries per meter) or equivalently $4\pi \times 10^{-7}$ N/A² (newtons per ampere squared). This constant characterizes the magnetic properties of free space and plays a central role in the formulation of Maxwell's equations, particularly in defining the relationship between magnetic field and the current that generates it.

The vacuum permittivity, $\epsilon_0$, with a value of approximately $8.85 \times 10^{-12}$ F/m (farads per meter), describes the electric properties of free space. It appears in Coulomb's law and relates the electric displacement field to the electric field in a vacuum. This constant is a fundamental parameter in the description of electric phenomena and electromagnetic wave propagation.

The speed of light in vacuum, $c$, equals $2.998 \times 10^{8}$ m/s (meters per second). In electromagnetism, this constant emerges naturally from Maxwell's equations and represents the speed at which electromagnetic waves propagate in free space. Since the 2019 redefinition of SI units, the speed of light has a fixed exact value, and the meter is defined in terms of it.

The elementary charge, $e$, has a value of $1.602 \times 10^{-19}$ C (coulombs). This fundamental physical constant represents the electric charge carried by a single proton or, equivalently, the magnitude of the negative charge carried by an electron. It serves as the natural unit of electric charge in atomic and subatomic processes.

The Planck constant, $h$, with a value of $6.626 \times 10^{-34}$ J·s (joule-seconds), is a fundamental constant in quantum mechanics that relates the energy of a photon to its frequency. It appears in the expressions for quantized energy levels and in the uncertainty principle, establishing the scale at which quantum effects become significant.

The Bohr magneton, $\mu_B$, equals $9.274 \times 10^{-24}$ J/T (joules per tesla). This physical constant represents the magnetic moment of an electron arising from its orbital angular momentum. It serves as a natural unit of magnetic moment in atomic and nuclear physics, particularly in the description of electron spin magnetic moment and in the analysis of magnetic properties of materials.

These constants are related by the fundamental equation:

$$c^2 = \frac{1}{\mu_0 \epsilon_0}$$

which follows from Maxwell's equations and serves as a consistency check for our unit system.[@Griffiths2018]

### Magnetic Moments and Fields

The magnetic moment $\vec{\mu}$ of a particle can arise from its intrinsic spin or from its orbital motion. In the SI system, magnetic moment has units of A·m² (ampere square meter) or, equivalently, J/T (joule per tesla).[@Blundell2001]

The energy of a magnetic moment in an external magnetic field $\vec{B}$ is given by:

$$E = -\vec{\mu} \cdot \vec{B}$$

Since energy is measured in joules (J), and magnetic moment in J/T, the magnetic field $\vec{B}$ must have units of tesla (T), which is equivalent to Vs/m² or kg/(s²·A).

For a current loop with area $A$ and current $I$, the magnetic moment is:

$$\vec{\mu} = I \vec{A}$$

Confirming the units of magnetic moment as A·m².

### Quantum Mechanical Magnetic Moment

In quantum mechanics, the magnetic moment of an electron has contributions from both spin and orbital angular momentum:

$$\vec{\mu}_e = -g_e \frac{e}{2m_e} \vec{S} - \frac{e}{2m_e} \vec{L}$$

where $g_e \approx 2.002$ is the electron g-factor, $e$ is the elementary charge, $m_e$ is the electron mass, $\vec{S}$ is the spin angular momentum, and $\vec{L}$ is the orbital angular momentum.[@Cohen-Tannoudji1991]

The angular momentum (both spin and orbital) has units of $\hbar$, which in SI is J·s. Thus:

$$[\vec{\mu}_e] = \frac{\text{C}}{\text{kg}} \cdot \text{J} \cdot \text{s} = \frac{\text{C} \cdot \text{J} \cdot \text{s}}{\text{kg}} = \frac{\text{A} \cdot \text{s} \cdot \text{J} \cdot \text{s}}{\text{kg}} = \frac{\text{A} \cdot \text{s}^2 \cdot \text{J}}{\text{kg}}$$

Since $\text{J} = \text{kg} \cdot \text{m}^2 / \text{s}^2$, we have:

$$[\vec{\mu}_e] = \frac{\text{A} \cdot \text{s}^2 \cdot \text{kg} \cdot \text{m}^2 / \text{s}^2}{\text{kg}} = \text{A} \cdot \text{m}^2$$

confirming the units of magnetic moment as A·m².

## Magnetic Interaction Energy

### Magnetic Dipole-Dipole Interaction

The energy of interaction between two magnetic dipoles $\vec{\mu}_1$ and $\vec{\mu}_2$ separated by a displacement vector $\vec{r}$ is given by:

$$E = \frac{\mu_0}{4\pi} \left[ \frac{\vec{\mu}_1 \cdot \vec{\mu}_2}{r^3} - \frac{3(\vec{\mu}_1 \cdot \vec{r})(\vec{\mu}_2 \cdot \vec{r})}{r^5} \right]$$

Let's analyze the units term by term:

- $\mu_0/4\pi$ has units of N/A², or equivalently, T·m/A
- $\vec{\mu}_1$ and $\vec{\mu}_2$ have units of A·m²
- $r^3$ and $r^5$ have units of m³ and m⁵, respectively

Combining these:

$$[E] = \frac{\text{T} \cdot \text{m}}{\text{A}} \cdot \frac{\text{A}^2 \cdot \text{m}^4}{\text{m}^3} = \text{T} \cdot \text{A} \cdot \text{m}^2 = \frac{\text{kg}}{\text{s}^2 \cdot \text{A}} \cdot \text{A} \cdot \text{m}^2 = \frac{\text{kg} \cdot \text{m}^2}{\text{s}^2} = \text{J}$$

This confirms that the interaction energy is correctly expressed in units of joules.

### Heisenberg Exchange Interaction

In quantum mechanical systems, the exchange interaction between spins is often expressed using the Heisenberg Hamiltonian:

$$\mathcal{H} = -\sum_{i,j} J_{ij} \vec{S}_i \cdot \vec{S}_j$$

where $J_{ij}$ is the exchange coupling constant and $\vec{S}_i$, $\vec{S}_j$ are dimensionless spin operators (their eigenvalues are pure numbers like $\pm 1/2$ for spin-1/2 particles).[@White2007]

Since the Hamiltonian must have units of energy (J), the exchange coupling constant $J_{ij}$ must also have units of energy, typically expressed in eV, cm⁻¹, or K (kelvin, through the relation $E = k_B T$).

### Zeeman Interaction

The Zeeman interaction describes the coupling of a magnetic moment to an external magnetic field:

$$\mathcal{H}_{\text{Zeeman}} = -\vec{\mu} \cdot \vec{B} = -g\mu_B \vec{S} \cdot \vec{B}$$

where $g$ is the g-factor (dimensionless), $\mu_B$ is the Bohr magneton (J/T), $\vec{S}$ is the dimensionless spin operator, and $\vec{B}$ is the magnetic field (T).

The units check out: $[\mathcal{H}_{\text{Zeeman}}] = \frac{\text{J}}{\text{T}} \cdot \text{T} = \text{J}$, confirming that the Zeeman energy is expressed in joules.

## Computational Implementation

### Finite Field Approach

In computational studies, the magnetic properties of molecules can be calculated using a finite field approach, where the energy is computed in the presence of magnetic fields of varying strengths. The components of the susceptibility tensor can then be obtained by numerical differentiation:

```python
def calculate_magnetic_susceptibility(molecule, field_strength=0.001):
    """
    Calculate magnetic susceptibility using finite field approach.
    
    Parameters:
    -----------
    molecule : str
        Molecule specification in XYZ format.
    field_strength : float
        Strength of magnetic field in Tesla.
        
    Returns:
    --------
    chi : numpy.ndarray
        3x3 magnetic susceptibility tensor in SI units (m³/mol).
    """
    import numpy as np
    from psi4 import energy, set_options
    
    # Setup calculation
    set_options({
        'basis': 'aug-cc-pVDZ',
        'reference': 'rhf',
        'scf_type': 'pk',
        'e_convergence': 1e-10,
        'd_convergence': 1e-10
    })
    
    # Define field directions
    field_directions = np.eye(3)
    
    # Initialize tensor
    chi = np.zeros((3, 3))
    
    # Calculate reference energy (no field)
    e0 = energy('scf', molecule=molecule)
    
    # Calculate energies with fields in different directions
    for i in range(3):
        # Positive field in direction i
        field_vec = field_directions[i] * field_strength
        set_options({'perturb_h': True, 'perturb_with': 'magnetic_field', 'perturb_magnitude': field_strength})
        e_pos = energy('scf', molecule=molecule)
        
        # Negative field in direction i
        field_vec = -field_directions[i] * field_strength
        set_options({'perturb_h': True, 'perturb_with': 'magnetic_field', 'perturb_magnitude': -field_strength})
        e_neg = energy('scf', molecule=molecule)
        
        # Second derivative approximation
        for j in range(3):
            chi[i, j] = (e_pos + e_neg - 2*e0) / (field_strength**2)
    
    # Convert to SI units (m³/mol)
    # Conversion factor depends on how the quantum chemistry program handles units
    conversion_factor = 1.0  # Placeholder - actual value depends on program specifics
    chi *= conversion_factor
    
    return chi
```

This code snippet illustrates the basic approach to calculating magnetic susceptibility using finite differences of the energy with respect to applied magnetic fields.

### Unit Conversions

In practice, computational chemistry programs may use different internal unit systems, requiring conversions to SI units for comparison with experimental data. Here's an example of converting between common unit systems:

```python
def convert_magnetic_coupling_units(j_value, input_unit, output_unit):
    """
    Convert magnetic coupling constant between different units.
    
    Parameters:
    -----------
    j_value : float
        Value of coupling constant in input_unit.
    input_unit : str
        Input unit ('eV', 'cm-1', 'K', 'J').
    output_unit : str
        Output unit ('eV', 'cm-1', 'K', 'J').
        
    Returns:
    --------
    float
        Coupling constant in output_unit.
    """
    # Constants
    kb = 8.617333262e-5  # Boltzmann constant in eV/K
    h = 4.135667696e-15  # Planck constant in eV·s
    c = 299792458        # Speed of light in m/s
    
    # Convert to eV first
    if input_unit == 'eV':
        j_in_ev = j_value
    elif input_unit == 'cm-1':
        j_in_ev = j_value * h * c * 100  # h*c in eV·m, *100 for cm→m
    elif input_unit == 'K':
        j_in_ev = j_value * kb
    elif input_unit == 'J':
        j_in_ev = j_value / 1.602176634e-19  # e in C
    else:
        raise ValueError(f"Unsupported input unit: {input_unit}")
    
    # Convert from eV to output unit
    if output_unit == 'eV':
        return j_in_ev
    elif output_unit == 'cm-1':
        return j_in_ev / (h * c * 100)
    elif output_unit == 'K':
        return j_in_ev / kb
    elif output_unit == 'J':
        return j_in_ev * 1.602176634e-19
    else:
        raise ValueError(f"Unsupported output unit: {output_unit}")
```

This function demonstrates the conversion of magnetic coupling constants between different units commonly used in the scientific literature.

## Common Pitfalls and Misconceptions

### CGS vs. SI Units

One common source of confusion in the literature is the use of different unit systems, particularly CGS (Gaussian) vs. SI units. In the CGS system, the magnetic dipole-dipole interaction energy takes the form:

$$E = \frac{\vec{\mu}_1 \cdot \vec{\mu}_2}{r^3} - \frac{3(\vec{\mu}_1 \cdot \vec{r})(\vec{\mu}_2 \cdot \vec{r})}{r^5}$$

Note the absence of the $\mu_0/4\pi$ factor that appears in the SI expression.

When converting between CGS and SI units for magnetic quantities, it's important to account for both the different units and the explicit appearance of $\mu_0$ in SI formulas:

- Magnetic moment: 1 emu (CGS) = 10⁻³ A·m² (SI)
- Magnetic field: 1 G (Gauss, CGS) = 10⁻⁴ T (SI)
- Magnetic susceptibility: 1 emu/mol (CGS) = 4π×10⁻⁶ m³/mol (SI)

### Dimensionless vs. Dimensional Spin

Another potential source of confusion is the use of dimensionless spin operators in the Heisenberg Hamiltonian versus dimensional angular momentum in the expression for magnetic moment. It's important to remember that:

- Spin operators $\vec{S}$ in the Heisenberg Hamiltonian are dimensionless
- Angular momentum $\vec{L}$ and $\vec{S}$ in the magnetic moment expression have units of $\hbar$

This distinction affects how the g-factor and exchange coupling constants are defined and interpreted.

## Applications

### Molecular Magnetism

In molecular magnets, the magnetic coupling between spin centers determines the overall magnetic behavior of the molecule. By calculating the exchange coupling constants $J_{ij}$ between different spin centers, we can predict magnetic properties such as the ground state spin, susceptibility, and magnetization curves.[@Kahn1993]

For example, in a dinuclear copper(II) complex with two $S=1/2$ centers, the energy gap between the singlet and triplet states is directly related to the exchange coupling constant:

$$\Delta E = E(S=0) - E(S=1) = -2J$$

By calculating this energy gap using quantum chemistry methods, we can determine $J$ and predict the magnetic behavior of the complex.

### Spin Hamiltonians in Materials Science

In materials science, effective spin Hamiltonians are used to model the magnetic properties of extended systems:[@Spaldin2010]

$$\mathcal{H} = -\sum_{\langle i,j \rangle} J_{ij} \vec{S}_i \cdot \vec{S}_j - \sum_i g_i \mu_B \vec{S}_i \cdot \vec{B} + \sum_i D_i (S_i^z)^2 + \sum_{\langle i,j \rangle} \vec{D}_{ij} \cdot (\vec{S}_i \times \vec{S}_j)$$

where the terms represent exchange interaction, Zeeman interaction, single-ion anisotropy, and Dzyaloshinskii-Moriya interaction, respectively.

The consistent application of units is crucial when parameterizing such Hamiltonians based on quantum chemical calculations or when comparing calculated properties with experimental measurements.

## Conclusion

In this work, we have provided a systematic derivation of the SI units involved in magnetic interactions at the quantum level. By carefully tracking the dimensions of each quantity and their relationships, we have established a consistent framework for understanding and interpreting magnetic properties in computational studies.

The key points from this analysis can be summarized as follows. Magnetic moments in SI units are expressed as A·m² or equivalently as J/T, while magnetic fields are quantified in tesla (T). Exchange coupling constants, which are central to quantum mechanical descriptions of magnetic interactions, carry units of energy and may be expressed in joules, electron volts, wavenumbers (cm⁻¹), or kelvin through the Boltzmann constant. It is crucial to note that the magnetic dipole-dipole interaction formula in SI units necessarily includes the factor $\mu_0/4\pi$, which distinguishes it from its CGS counterpart. Additionally, when working with the Heisenberg Hamiltonian, one must remember that the spin operators are dimensionless, unlike the angular momentum operators that appear in expressions for magnetic moments.

This framework provides a solid foundation for computational studies of magnetic systems, ensuring that calculated properties can be correctly related to experimentally measurable quantities.[@atkins2010physical] A comprehensive understanding of these units and their interrelationships is essential for accurate modeling of magnetic phenomena at both quantum and macroscopic scales.

## References
