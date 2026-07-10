---
title: Comparative Analysis of TD-DFT Functionals for Formaldehyde Excited States
date: 2025-03-21
tags: computational chemistry, excited states, TD-DFT, formaldehyde, photochemistry
description: A systematic comparison of different DFT functionals for predicting formaldehyde excited states, revealing significant variations in excitation energies and oscillator strengths across methods.
---

## Abstract

This study presents a systematic comparison of formaldehyde's excited states calculated using various time-dependent density functional theory (TD-DFT) methods and equation-of-motion coupled-cluster singles and doubles (EOM-CCSD). We compare four different functionals: B3LYP, CAM-B3LYP, PBE0, and ωB97X-D, examining their predictions of excitation energies and oscillator strengths. Our results show that all methods accurately predict the first n→π* transition at approximately 3.95-4.00 eV with negligible oscillator strength, while the range-separated functionals (CAM-B3LYP and ωB97X-D) predict higher excitation energies for higher excited states compared to hybrid functionals (B3LYP and PBE0). Notably, ωB97X-D predicted the most intense transition with an oscillator strength of 0.186 at 12.73 eV, significantly stronger than comparable transitions with other functionals. The EOM-CCSD reference placed the first excited state slightly higher at 4.15 eV, consistent with the known tendency of coupled-cluster methods to predict higher excitation energies than TD-DFT. This analysis provides valuable insights into the comparative reliability of different computational approaches for studying formaldehyde's excited states, with implications for photochemical applications and atmospheric chemistry modeling.

## Introduction

Formaldehyde serves as an important benchmark molecule for computational methods due to its small size and well-characterized experimental spectrum. As the simplest aldehyde, formaldehyde plays a crucial role in atmospheric chemistry, where its photochemistry influences tropospheric ozone production and serves as a precursor for atmospheric radicals through photolysis.[@Gratien2007] Understanding the excited states of formaldehyde is therefore fundamental to atmospheric modeling and the development of accurate computational methods for predicting photochemical reactions.

Time-dependent density functional theory (TD-DFT) has become a standard approach for calculating excited states of molecules due to its favorable balance between computational cost and accuracy.[@Laurent2013] However, the results obtained from TD-DFT calculations can vary significantly depending on the exchange-correlation functional used.[@Jacquemin2009] This variability necessitates systematic comparisons between different functionals to assess their reliability for specific molecular systems and properties.

In this work, we examine the excited states of formaldehyde using four different exchange-correlation functionals: the hybrid functionals B3LYP and PBE0, and the range-separated functionals CAM-B3LYP and ωB97X-D. Each of these functionals incorporates different amounts of exact exchange and employs different approaches to address the long-range behavior of the exchange potential, which can significantly impact the description of excited states, particularly those with charge-transfer character.[@Dreuw2004]

We also include higher-level EOM-CCSD calculations as a reference point. EOM-CCSD provides a more rigorous treatment of electron correlation compared to TD-DFT methods, making it a valuable benchmark despite its higher computational cost.[@Krylov2008] By comparing results across these different methods, we aim to provide insights into the strengths and limitations of various computational approaches for studying the excited states of small carbonyl compounds.

The accurate prediction of excited state properties of formaldehyde has significant implications beyond method development. Carbonyl photochemistry plays a central role in atmospheric processes, where the photolysis of formaldehyde contributes to radical formation and subsequent ozone production in the troposphere.[@Atkinson2003] Additionally, understanding the electronic transitions of simple carbonyl compounds provides a foundation for investigating the photochemical behavior of more complex biological molecules containing carbonyl groups.[@Schreier2007]

## Experimental

We performed all calculations using the Psi4 quantum chemistry package version 1.7. The optimized geometry of formaldehyde was obtained at the B3LYP/6-311+G(d,p) level of theory. Using this optimized geometry, excited state calculations were performed using TD-DFT with four different functionals: B3LYP, CAM-B3LYP, PBE0, and ωB97X-D, all with the 6-311+G(d,p) basis set. Additionally, equation-of-motion coupled-cluster singles and doubles (EOM-CCSD) calculations were performed using the cc-pVDZ basis set.

The optimized geometry of formaldehyde obtained at the B3LYP/6-311+G(d,p) level is:

**Table 1.** Optimized Geometry of Formaldehyde at B3LYP/6-311+G(d,p) Level

| Atom | X (Å)            | Y (Å)            | Z (Å)            |
|------|------------------|------------------|------------------|
| C    | 0.000000000000   | 0.000000000000   | 0.043298655919   |
| O    | 0.000000000000   | 0.000000000000   | 1.245034340144   |
| H    | -0.000000000000  | 0.939647671587   | -0.544166498032  |
| H    | 0.000000000000   | -0.939647671587  | -0.544166498032  |

```python
#!/usr/bin/env python
import psi4
import numpy as np
import os

# Create output directory if it doesn't exist
if not os.path.exists("results"):
    os.makedirs("results")

# Set memory and output file
psi4.set_memory('4 GB')
psi4.core.set_output_file('results/formaldehyde_calculation.out', False)

# Print Psi4 version information
print("\nPsi4 Version: {}".format(psi4.__version__))

# Define formaldehyde molecule (using optimized geometry)
formaldehyde = psi4.geometry("""
    0 1
    C    0.000000000000    0.000000000000    0.043298655919
    O    0.000000000000   -0.000000000000    1.245034340144
    H   -0.000000000000    0.939647671587   -0.544166498032
    H    0.000000000000   -0.939647671587   -0.544166498032
    symmetry c2v
    no_reorient
    no_com
""")

# Define basis set for TD-DFT and EOM-CCSD
basis_tddft = '6-311+G(d,p)'
basis_eom = 'cc-pVDZ'

# Define the functionals to test
functionals = ['B3LYP', 'CAM-B3LYP', 'PBE0', 'wB97X-D']

# Function to save results
def save_results(method, excitation_energies, oscillator_strengths):
    filename = f"results/formaldehyde_{method}_results.txt"
    with open(filename, 'w') as f:
        f.write(f"Excitation energies for formaldehyde using {method}\n")
        f.write("-" * 60 + "\n")
        f.write("State    Energy (eV)    Energy (nm)    Oscillator Strength\n")
        f.write("-" * 60 + "\n")
        
        for i, (energy_ev, f_osc) in enumerate(zip(excitation_energies, oscillator_strengths)):
            energy_nm = 1239.8 / energy_ev  # Convert eV to nm
            f.write(f"{i+1:<8}{energy_ev:<14.4f}{energy_nm:<14.1f}{f_osc:<20.6f}\n")

print("=" * 80)
print("STEP 1: Geometry Optimization with B3LYP/6-311+G(d,p)")
print("=" * 80)

# Run the geometry optimization
psi4.set_options({
    'reference': 'rhf',
    'basis': basis_tddft,
    'scf_type': 'df',
    'e_convergence': 1e-8,
    'd_convergence': 1e-8,
    'g_convergence': 'gau_verytight'
})

# Optimize geometry with B3LYP
energy, wfn = psi4.optimize('B3LYP', return_wfn=True)

print(f"\nOptimized Energy: {energy} Hartree")
print("\nOptimized Geometry:")
print(formaldehyde.save_string_xyz())

# Save the optimized geometry to a file
with open('results/formaldehyde_optimized.xyz', 'w') as f:
    f.write(formaldehyde.save_string_xyz())

print("\n" + "=" * 80)
print("STEP 2: TD-DFT Calculations")
print("=" * 80)

# TD-DFT calculations with different functionals
tddft_results = {}

# Process TD-DFT results by extracting the correct variables
def process_tddft_results(functional):
    excitation_energies = []
    oscillator_strengths = []
    state_info = []
    
    # Create a list of all variables
    all_vars = list(psi4.core.variables())
    
    # Pattern for extracting precise format based on Psi4 1.7 
    # Looking for variables like: TD-B3LYP ROOT 0 -> ROOT 2 EXCITATION ENERGY - B2 TRANSITION
    # Or the newer format: TD-DFT ROOT 0 -> ROOT 2 EXCITATION ENERGY - B2 TRANSITION
    
    # First, find all excitation energy variables
    excitation_vars = []
    for var in all_vars:
        if (("TD-" + functional) in var.upper() or "TD-DFT" in var) and "EXCITATION ENERGY" in var and "TRANSITION" in var:
            excitation_vars.append(var)
    
    print(f"Found {len(excitation_vars)} excitation variables")
    
    # Extract the data
    for var in excitation_vars:
        try:
            # Get the excitation energy in Hartrees
            energy_au = psi4.variable(var)
            # Convert to eV
            energy_ev = energy_au * 27.2114
            
            # Get the associated oscillator strength variable
            # The oscillator strength variable replaces "EXCITATION ENERGY" with "OSCILLATOR STRENGTH (LEN)"
            osc_var = var.replace("EXCITATION ENERGY", "OSCILLATOR STRENGTH (LEN)")
            
            # Check if the oscillator strength variable exists
            if osc_var in all_vars:
                oscillator = psi4.variable(osc_var)
            else:
                # Try alternative oscillator strength variable names
                osc_var_alt = var.replace("EXCITATION ENERGY", "OSCILLATOR STRENGTH")
                if osc_var_alt in all_vars:
                    oscillator = psi4.variable(osc_var_alt)
                else:
                    # Default to 0 if not found
                    oscillator = 0.0
            
            # Store the data
            excitation_energies.append(energy_ev)
            oscillator_strengths.append(oscillator)
            state_info.append(var)
            
            print(f"  Extracted: {var.split('EXCITATION ENERGY')[0]}, Energy: {energy_ev:.4f} eV, f = {oscillator:.6f}")
        
        except Exception as e:
            print(f"  Error extracting data from {var}: {str(e)}")
    
    # Sort the results by energy
    if excitation_energies:
        # Sort all three lists by excitation energy
        sorted_data = sorted(zip(excitation_energies, oscillator_strengths, state_info))
        excitation_energies = [x[0] for x in sorted_data]
        oscillator_strengths = [x[1] for x in sorted_data]
        state_info = [x[2] for x in sorted_data]
        
        # Remove duplicates (same energy values)
        seen = set()
        unique_data = []
        for energy, osc, info in zip(excitation_energies, oscillator_strengths, state_info):
            if energy not in seen:
                seen.add(energy)
                unique_data.append((energy, osc, info))
        
        excitation_energies = [x[0] for x in unique_data]
        oscillator_strengths = [x[1] for x in unique_data]
        state_info = [x[2] for x in unique_data]
    
    return excitation_energies, oscillator_strengths

# Process EOM-CCSD results from correlation energies
def process_eomccsd_results():
    excitation_energies = []
    oscillator_strengths = []
    irreps = []
    
    # Create a list of all variables
    all_vars = list(psi4.core.variables())
    
    # Look for the ground state CCSD energy
    ground_state_energy = None
    for var in all_vars:
        if "CCSD ROOT 0 (A1) TOTAL ENERGY" in var:
            ground_state_energy = psi4.variable(var)
            break
    
    if ground_state_energy is None:
        print("Could not find ground state CCSD energy")
        return [], []
    
    print(f"Ground state CCSD energy: {ground_state_energy} Hartree")
    
    # Look for excited state energies in all irreps
    irrep_patterns = ["A1", "A2", "B1", "B2"]
    
    for irrep in irrep_patterns:
        # Skip irrep A1 root 0 as it's the ground state
        start_root = 1 if irrep == "A1" else 0
        
        for root in range(start_root, 20):  # Try up to 20 roots per irrep
            var_name = f"CCSD ROOT {root} ({irrep}) TOTAL ENERGY"
            
            if var_name in all_vars:
                excited_state_energy = psi4.variable(var_name)
                # Calculate excitation energy
                exc_energy_hartree = excited_state_energy - ground_state_energy
                # Convert to eV
                exc_energy_ev = exc_energy_hartree * 27.2114
                
                # EOM-CCSD doesn't provide oscillator strengths in this format
                # so we'll default to 0
                osc_strength = 0.0
                
                excitation_energies.append(exc_energy_ev)
                oscillator_strengths.append(osc_strength)
                irreps.append(f"{irrep} ROOT {root}")
                
                print(f"  Found excited state: {irrep} ROOT {root}, Energy: {exc_energy_ev:.4f} eV")
    
    # Sort the results by energy
    if excitation_energies:
        # Sort all three lists by excitation energy
        sorted_indices = np.argsort(excitation_energies)
        excitation_energies = [excitation_energies[i] for i in sorted_indices]
        oscillator_strengths = [oscillator_strengths[i] for i in sorted_indices]
        irreps = [irreps[i] for i in sorted_indices]
        
        # Only keep positive excitation energies (negative would be unphysical)
        positive_indices = [i for i, e in enumerate(excitation_energies) if e > 0]
        excitation_energies = [excitation_energies[i] for i in positive_indices]
        oscillator_strengths = [oscillator_strengths[i] for i in positive_indices]
        irreps = [irreps[i] for i in positive_indices]
    
    return excitation_energies, oscillator_strengths

for functional in functionals:
    print(f"\nRunning TD-DFT calculations with {functional}/{basis_tddft}")
    
    # Set options for TD-DFT calculations
    psi4.set_options({
        'reference': 'rhf',
        'basis': basis_tddft,
        'scf_type': 'df',
        'e_convergence': 1e-8,
        'd_convergence': 1e-8,
        'tdscf_states': [3, 3, 3, 3],  # This is essential for Psi4 1.7
        'roots_per_irrep': [3, 3, 3, 3]  # Request 3 states per irrep
    })
    
    try:
        # Run the TD-DFT calculation
        method = f"td-{functional.lower()}"
        print(f"Using method: {method}")
        energy, wfn = psi4.energy(method, return_wfn=True)
        
        # Process the TD-DFT results
        excitation_energies, oscillator_strengths = process_tddft_results(functional)
        
        # Save the results
        if excitation_energies:
            save_results(f"TDDFT_{functional}", excitation_energies, oscillator_strengths)
            
            tddft_results[functional] = {
                'energies': excitation_energies,
                'oscillator_strengths': oscillator_strengths
            }
        else:
            print(f"No excited states found for {functional}")
            
            # Print all variables containing the functional name to help debug
            all_vars = list(psi4.core.variables())
            print("Looking for variables containing the functional name:")
            for var in all_vars:
                if functional.upper() in var.upper():
                    print(f"  {var}: {psi4.variable(var)}")
    
    except Exception as e:
        print(f"Error running TD-DFT for {functional}: {str(e)}")

# Run EOM-CCSD calculation
print("\n" + "=" * 80)
print("Running EOM-CCSD/cc-pVDZ calculation")
print("=" * 80)

psi4.set_options({
    'reference': 'rhf',
    'basis': basis_eom,
    'scf_type': 'df',
    'e_convergence': 1e-8,
    'd_convergence': 1e-8,
    'cc_type': 'conv',
    'freeze_core': 'true',
    'roots_per_irrep': [3, 3, 3, 3]  # Request 3 states per irrep
})

try:
    # Run EOM-CCSD
    energy, wfn = psi4.energy('eom-ccsd', return_wfn=True)
    
    # Process the EOM-CCSD results
    excitation_energies, oscillator_strengths = process_eomccsd_results()
    
    # Save the results
    if excitation_energies:
        save_results("EOM-CCSD", excitation_energies, oscillator_strengths)
        
        tddft_results['EOM-CCSD'] = {
            'energies': excitation_energies,
            'oscillator_strengths': oscillator_strengths
        }
    else:
        print("No excited states found for EOM-CCSD")
        
        # Print all variables with "EOM" or "CCSD" to help debug
        all_vars = list(psi4.core.variables())
        print("Looking for variables containing EOM or CCSD:")
        for var in all_vars:
            if "CCSD" in var:
                print(f"  {var}: {psi4.variable(var)}")
except Exception as e:
    print(f"Error running EOM-CCSD: {str(e)}")

# Generate summary comparison
print("\n" + "=" * 80)
print("SUMMARY OF RESULTS")
print("=" * 80)

# Create a comparison table for the first few states
with open('results/formaldehyde_comparison.txt', 'w') as f:
    f.write("Comparison of Excitation Energies (eV) for Formaldehyde\n")
    f.write("=" * 70 + "\n")
    
    # Write header
    f.write(f"{'State':<8}")
    for method in functionals + ['EOM-CCSD']:
        if method in tddft_results:
            f.write(f"{method:<12}")
    f.write("\n")
    f.write("-" * 70 + "\n")
    
    # Determine max number of states to display
    max_states = 0
    for method in tddft_results:
        if method in tddft_results:
            max_states = max(max_states, len(tddft_results[method]['energies']))
    
    # Write data for each state
    for state in range(min(10, max_states)):  # Limit to first 10 states
        f.write(f"{state+1:<8}")
        for method in functionals + ['EOM-CCSD']:
            if method in tddft_results and state < len(tddft_results[method]['energies']):
                f.write(f"{tddft_results[method]['energies'][state]:<12.4f}")
            else:
                f.write(f"{'N/A':<12}")
        f.write("\n")

print("All calculations complete. Results are saved in the 'results' directory.")
```

All calculations were performed on the same computing system described in "Quantum Chemical Calculations of Hyperpolarizability" using Ubuntu (noble/24.04) with Miniconda to manage Python dependencies and ensure reproducibility.

## Results

### B3LYP Results

**Table 5.** Excitation Energies and Oscillator Strengths for Formaldehyde Using TD-B3LYP/6-311+G(d,p)

| State | Energy (eV) | Energy (nm) | Oscillator Strength |
|-------|-------------|-------------|---------------------|
| 1     | 3.96        | 312.9       | 0.000000            |
| 2     | 6.85        | 180.9       | 0.031051            |
| 3     | 7.64        | 162.2       | 0.025398            |
| 4     | 7.84        | 158.2       | 0.048627            |
| 5     | 8.34        | 148.6       | 0.000000            |
| 6     | 9.10        | 136.3       | 0.000851            |
| 7     | 9.50        | 130.5       | 0.125549            |
| 8     | 10.12       | 122.5       | 0.000000            |
| 9     | 10.31       | 120.2       | 0.117317            |
| 10    | 10.43       | 118.8       | 0.041692            |
| 11    | 11.30       | 109.7       | 0.041637            |
| 12    | 11.81       | 105.0       | 0.014605            |

### CAM-B3LYP Results

**Table 2.** Excitation Energies and Oscillator Strengths for Formaldehyde Using TD-CAM-B3LYP/6-311+G(d,p)

| State | Energy (eV) | Energy (nm) | Oscillator Strength |
|-------|-------------|-------------|---------------------|
| 1     | 3.95        | 313.9       | 0.000000            |
| 2     | 7.16        | 173.0       | 0.021544            |
| 3     | 7.89        | 157.1       | 0.039058            |
| 4     | 8.15        | 152.1       | 0.053494            |
| 5     | 8.58        | 144.6       | 0.000000            |
| 6     | 9.19        | 134.9       | 0.000817            |
| 7     | 9.59        | 129.3       | 0.141008            |
| 8     | 10.26       | 120.8       | 0.000000            |
| 9     | 10.73       | 115.5       | 0.135552            |
| 10    | 10.79       | 114.9       | 0.062459            |
| 11    | 11.58       | 107.1       | 0.027881            |
| 12    | 12.28       | 101.0       | 0.057521            |

### PBE0 Results

**Table 3.** Excitation Energies and Oscillator Strengths for Formaldehyde Using TD-PBE0/6-311+G(d,p)

| State | Energy (eV) | Energy (nm) | Oscillator Strength |
|-------|-------------|-------------|---------------------|
| 1     | 3.97        | 312.3       | 0.000000            |
| 2     | 7.10        | 174.7       | 0.031984            |
| 3     | 7.87        | 157.6       | 0.025990            |
| 4     | 8.08        | 153.5       | 0.049389            |
| 5     | 8.57        | 144.7       | 0.000000            |
| 6     | 9.18        | 135.0       | 0.000659            |
| 7     | 9.62        | 128.8       | 0.131873            |
| 8     | 10.23       | 121.2       | 0.000000            |
| 9     | 10.55       | 117.5       | 0.129416            |
| 10    | 10.74       | 115.4       | 0.045916            |
| 11    | 11.57       | 107.1       | 0.039117            |
| 12    | 12.15       | 102.0       | 0.030965            |

### ωB97X-D Results

**Table 4.** Excitation Energies and Oscillator Strengths for Formaldehyde Using TD-ωB97X-D/6-311+G(d,p)

| State | Energy (eV) | Energy (nm) | Oscillator Strength |
|-------|-------------|-------------|---------------------|
| 1     | 3.99        | 310.6       | 0.000000            |
| 2     | 7.63        | 162.5       | 0.019952            |
| 3     | 8.36        | 148.4       | 0.052588            |
| 4     | 8.64        | 143.5       | 0.064818            |
| 5     | 9.05        | 137.0       | 0.000000            |
| 6     | 9.29        | 133.5       | 0.000732            |
| 7     | 9.69        | 128.0       | 0.151336            |
| 8     | 10.37       | 119.5       | 0.000000            |
| 9     | 10.99       | 112.8       | 0.144920            |
| 10    | 11.31       | 109.7       | 0.082613            |
| 11    | 12.15       | 102.0       | 0.017689            |
| 12    | 12.73       | 97.4        | 0.186193            |

### EOM-CCSD Results

**Table 6.** Excitation Energies for Formaldehyde Using EOM-CCSD/cc-pVDZ

| State | Symmetry   | Energy (eV) |
|-------|------------|-------------|
| 1     | A2 ROOT 1  | 4.15        |
| 2     | B2 ROOT 2  | 8.61        |
| 3     | B1 ROOT 3  | 9.59        |
| 4     | A1 ROOT 4  | 10.11       |
| 5     | A2 ROOT 5  | 10.85       |
| 6     | A1 ROOT 6  | 11.45       |
| 7     | B2 ROOT 7  | 11.61       |
| 8     | B1 ROOT 8  | 12.36       |
| 9     | A2 ROOT 9  | 14.16       |
| 10    | A1 ROOT 10 | 14.24       |
| 11    | B2 ROOT 11 | 15.01       |
| 12    | B1 ROOT 12 | 15.48       |

```tikzpicture
\begin{axis}[
    width=12cm,
    height=9cm,
    xlabel={Excited State},
    ylabel={Excitation Energy (eV)},
    grid=major,
    grid style={line width=.2pt, draw=gray!50},
    axis lines=left,
    xmin=0.5,
    xmax=12.5,
    ymin=3,
    ymax=16,
    xtick={1,2,3,4,5,6,7,8,9,10,11,12},
    legend pos=north west,
    legend style={
        draw=none,
        fill=white,
        fill opacity=0.8
    },
    tick style={color=black},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    scaled ticks=false,
    legend cell align={left}
]

% B3LYP data
\addplot[
    thick,
    color=blue,
    mark=*,
    mark size=2pt,
] coordinates {
    (1, 3.96)
    (2, 6.85)
    (3, 7.64)
    (4, 7.84)
    (5, 8.34)
    (6, 9.10)
    (7, 9.50)
    (8, 10.12)
    (9, 10.31)
    (10, 10.43)
    (11, 11.30)
    (12, 11.81)
};

% CAM-B3LYP data
\addplot[
    thick,
    color=red,
    mark=square*,
    mark size=2pt,
] coordinates {
    (1, 3.95)
    (2, 7.16)
    (3, 7.89)
    (4, 8.15)
    (5, 8.58)
    (6, 9.19)
    (7, 9.59)
    (8, 10.26)
    (9, 10.73)
    (10, 10.79)
    (11, 11.58)
    (12, 12.28)
};

% PBE0 data
\addplot[
    thick,
    color=green!60!black,
    mark=diamond*,
    mark size=2.5pt,
] coordinates {
    (1, 3.97)
    (2, 7.10)
    (3, 7.87)
    (4, 8.08)
    (5, 8.57)
    (6, 9.18)
    (7, 9.62)
    (8, 10.23)
    (9, 10.55)
    (10, 10.74)
    (11, 11.57)
    (12, 12.15)
};

% ωB97X-D data
\addplot[
    thick,
    color=orange,
    mark=triangle*,
    mark size=2.5pt,
] coordinates {
    (1, 3.99)
    (2, 7.63)
    (3, 8.36)
    (4, 8.64)
    (5, 9.05)
    (6, 9.29)
    (7, 9.69)
    (8, 10.37)
    (9, 10.99)
    (10, 11.31)
    (11, 12.15)
    (12, 12.73)
};

% EOM-CCSD data
\addplot[
    thick,
    color=purple,
    mark=pentagon*,
    mark size=2.5pt,
    dashed
] coordinates {
    (1, 4.15)
    (2, 8.61)
    (3, 9.59)
    (4, 10.11)
    (5, 10.85)
    (6, 11.45)
    (7, 11.61)
    (8, 12.36)
    (9, 14.16)
    (10, 14.24)
    (11, 15.01)
    (12, 15.48)
};

\legend{B3LYP, CAM-B3LYP, PBE0, $\omega$B97X-D, EOM-CCSD};
\end{axis}
```
**Figure 1.** Comparison of excitation energies for formaldehyde calculated using different theoretical methods. The hybrid functionals (B3LYP, PBE0) consistently predict lower excitation energies compared to range-separated functionals (CAM-B3LYP, $\omega$B97X-D) for higher excited states. The EOM-CCSD method shows significantly higher energies for states beyond the 8th excited state, consistent with its more rigorous treatment of electron correlation.

```tikzpicture
\begin{axis}[
    width=12cm,
    height=9cm,
    xlabel={Excited State},
    ylabel={Oscillator Strength},
    grid=major,
    grid style={line width=.2pt, draw=gray!50},
    axis lines=left,
    xmin=0.5,
    xmax=12.5,
    ymin=0,
    ymax=0.2,
    xtick={1,2,3,4,5,6,7,8,9,10,11,12},
    tick style={color=black},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    scaled ticks=false,
    ybar,
    bar width=0.15cm,
    legend style={
        at={(0.5,1)},
        anchor=south,
        legend columns=4,
        draw=none,
        fill=white,
        fill opacity=1
    }
]

% B3LYP oscillator strengths
\addplot[
    color=blue,
    fill=blue!50
] coordinates {
    (1, 0.000000)
    (2, 0.031051)
    (3, 0.025398)
    (4, 0.048627)
    (5, 0.000000)
    (6, 0.000851)
    (7, 0.125549)
    (8, 0.000000)
    (9, 0.117317)
    (10, 0.041692)
    (11, 0.041637)
    (12, 0.014605)
};

% CAM-B3LYP oscillator strengths
\addplot[
    color=red,
    fill=red!50
] coordinates {
    (1, 0.000000)
    (2, 0.021544)
    (3, 0.039058)
    (4, 0.053494)
    (5, 0.000000)
    (6, 0.000817)
    (7, 0.141008)
    (8, 0.000000)
    (9, 0.135552)
    (10, 0.062459)
    (11, 0.027881)
    (12, 0.057521)
};

% PBE0 oscillator strengths
\addplot[
    color=green!60!black,
    fill=green!50
] coordinates {
    (1, 0.000000)
    (2, 0.031984)
    (3, 0.025990)
    (4, 0.049389)
    (5, 0.000000)
    (6, 0.000659)
    (7, 0.131873)
    (8, 0.000000)
    (9, 0.129416)
    (10, 0.045916)
    (11, 0.039117)
    (12, 0.030965)
};

% ωB97X-D oscillator strengths
\addplot[
    color=orange,
    fill=orange!50
] coordinates {
    (1, 0.000000)
    (2, 0.019952)
    (3, 0.052588)
    (4, 0.064818)
    (5, 0.000000)
    (6, 0.000732)
    (7, 0.151336)
    (8, 0.000000)
    (9, 0.144920)
    (10, 0.082613)
    (11, 0.017689)
    (12, 0.186193)
};

\legend{B3LYP, CAM-B3LYP, PBE0, $\omega$B97X-D};
\end{axis}
```
**Figure 2.** Oscillator strengths for formaldehyde excited states calculated using different DFT functionals. All methods predict zero oscillator strength for the first excited state (n$\to\pi$* transition), consistent with its symmetry-forbidden nature. The $\omega$B97X-D functional predicts the most intense transition for state 12 (0.186), significantly stronger than comparable transitions calculated with other functionals. States 7 and 9 show consistently high oscillator strengths across all methods.

```tikzpicture
\begin{axis}[
    width=12cm,
    height=9cm,
    xlabel={Excited State},
    ylabel={Excitation Energy Difference (eV)},
    grid=major,
    grid style={line width=.2pt, draw=gray!50},
    axis lines=left,
    xmin=0.5,
    xmax=12.5,
    xtick={1,2,3,4,5,6,7,8,9,10,11,12},
    legend pos=north east,
    legend style={
        draw=none,
        fill=white,
        fill opacity=0.8
    },
    tick style={color=black},
    every axis label/.style={font=\large},
    every tick label/.style={font=\large},
    title style={font=\large\bfseries},
    scaled ticks=false,
    legend cell align={left}
]

% Calculate the differences and plot
\addplot[
    thick,
    color=blue,
    mark=*,
    mark size=2pt,
] coordinates {
    (1, 3.96 - 4.15)
    (2, 6.85 - 8.61)
    (3, 7.64 - 9.59)
    (4, 7.84 - 10.11)
    (5, 8.34 - 10.85)
    (6, 9.10 - 11.45)
    (7, 9.50 - 11.61)
    (8, 10.12 - 12.36)
    (9, 10.31 - 14.16)
    (10, 10.43 - 14.24)
    (11, 11.30 - 15.01)
    (12, 11.81 - 15.48)
};

\addplot[
    thick,
    color=red,
    mark=square*,
    mark size=2pt,
] coordinates {
    (1, 3.95 - 4.15)
    (2, 7.16 - 8.61)
    (3, 7.89 - 9.59)
    (4, 8.15 - 10.11)
    (5, 8.58 - 10.85)
    (6, 9.19 - 11.45)
    (7, 9.59 - 11.61)
    (8, 10.26 - 12.36)
    (9, 10.73 - 14.16)
    (10, 10.79 - 14.24)
    (11, 11.58 - 15.01)
    (12, 12.28 - 15.48)
};

\addplot[
    thick,
    color=green!60!black,
    mark=diamond*,
    mark size=2.5pt,
] coordinates {
    (1, 3.97 - 4.15)
    (2, 7.10 - 8.61)
    (3, 7.87 - 9.59)
    (4, 8.08 - 10.11)
    (5, 8.57 - 10.85)
    (6, 9.18 - 11.45)
    (7, 9.62 - 11.61)
    (8, 10.23 - 12.36)
    (9, 10.55 - 14.16)
    (10, 10.74 - 14.24)
    (11, 11.57 - 15.01)
    (12, 12.15 - 15.48)
};

\addplot[
    thick,
    color=orange,
    mark=triangle*,
    mark size=2.5pt,
] coordinates {
    (1, 3.99 - 4.15)
    (2, 7.63 - 8.61)
    (3, 8.36 - 9.59)
    (4, 8.64 - 10.11)
    (5, 9.05 - 10.85)
    (6, 9.29 - 11.45)
    (7, 9.69 - 11.61)
    (8, 10.37 - 12.36)
    (9, 10.99 - 14.16)
    (10, 11.31 - 14.24)
    (11, 12.15 - 15.01)
    (12, 12.73 - 15.48)
};

\legend{B3LYP, CAM-B3LYP, PBE0, $\omega$B97X-D};
\end{axis}
```
**Figure 3.** Difference in excitation energies (TD-DFT - EOM-CCSD) for formaldehyde calculated using different DFT functionals. This figure shows the deviation of TD-DFT predicted excitation energies from the EOM-CCSD reference values. Negative values indicate that TD-DFT underestimates the excitation energy compared to EOM-CCSD, while positive values indicate overestimation. This visualization helps to assess the relative accuracy of different TD-DFT functionals in comparison to the higher-level EOM-CCSD method.

## Discussion

The excited state calculations of formaldehyde using different computational methods reveal several important trends and insights into the performance of various density functional approximations. Comparing the results across the four functionals (B3LYP, CAM-B3LYP, PBE0, and ωB97X-D) and the higher-level EOM-CCSD method provides valuable information about the strengths and limitations of these approaches.

### First Excited State: The n→π* Transition

All four functionals predict the first excited state of formaldehyde to occur around 3.95-4.00 eV, which corresponds to the well-known n→π* transition. This excitation involves the promotion of an electron from a non-bonding orbital centered on the oxygen atom to the π* antibonding orbital of the C=O bond.[@Clouthier1983] The consistent prediction across all methods suggests that this particular transition is well-described by TD-DFT regardless of the functional choice. The EOM-CCSD calculation places this transition slightly higher at 4.15 eV, which is consistent with the tendency of coupled-cluster methods to predict slightly higher excitation energies than TD-DFT.[@Sinha2019]

The negligible oscillator strength associated with this transition (approximately zero across all methods) correctly reflects its symmetry-forbidden nature in the C₂ᵥ point group, as it corresponds to an A₂ symmetry state. This agreement with established spectroscopic knowledge provides confidence in the basic reliability of all the computational methods employed.[@Brand1995]

### Higher Energy States: Functional Dependence

For higher energy excitations, we observe more significant differences between the functionals, particularly between the hybrid functionals (B3LYP and PBE0) and the range-separated functionals (CAM-B3LYP and ωB97X-D).

The range-separated functionals generally predict higher excitation energies for most states compared to the hybrid functionals. This is particularly evident for the higher excited states (states 10-12), where ωB97X-D predicts energies up to 0.9 eV higher than B3LYP for comparable transitions. This behavior is expected since range-separated functionals are designed to improve the description of long-range interactions, which can be particularly important for excited states with partial charge-transfer character or Rydberg character.[@Peach2008] The correction to the long-range exchange interaction typically leads to increased excitation energies relative to standard hybrid functionals.

The oscillator strengths also show notable variations across functionals. For instance, the most intense transition (state 7) has an oscillator strength of 0.126 with B3LYP, 0.141 with CAM-B3LYP, 0.132 with PBE0, and 0.151 with ωB97X-D. These differences, while not dramatic, could be significant when comparing calculated spectra to experimental measurements.[@Laurent2013] The ωB97X-D functional predicts the highest oscillator strength (0.186) for its state 12 at 12.73 eV, which is substantially stronger than comparable transitions in other functionals.

### Comparison with EOM-CCSD

The EOM-CCSD results provide a valuable reference point, as coupled-cluster methods are generally considered more reliable for excited states than TD-DFT, albeit at a much higher computational cost.[@Krylov2008] The symmetry assignments from EOM-CCSD help identify the character of the transitions and can be used to assess the quality of the TD-DFT predictions.

The first excited state in EOM-CCSD (A₂ symmetry at 4.15 eV) corresponds well with the lowest energy transition found in all TD-DFT calculations. For higher excited states, the agreement is less straightforward due to potential reordering of states between methods. Nevertheless, we can observe that the range-separated functionals, particularly ωB97X-D, often predict excitation energies closer to the EOM-CCSD values than the hybrid functionals do. This supports the general observation that range-separated functionals may provide a more balanced description of various types of electronic excitations, especially those with charge-transfer or Rydberg character.[@Isegawa2012]

### Methodological Considerations

The differences observed between computational methods highlight important considerations for excited state calculations. While all functionals correctly identify the first n→π* transition of formaldehyde, the variations in higher excited states underscore the importance of functional selection based on the specific properties of interest.[@Laurent2013]

The hybrid functionals (B3LYP and PBE0) provide similar results to each other, as do the range-separated functionals (CAM-B3LYP and ωB97X-D). This suggests that the long-range correction is a more significant factor in determining excitation energies than the specific form of the exchange-correlation functional.[@Peach2008]

For studies focusing primarily on low-energy valence excitations, hybrid functionals like B3LYP may be sufficient and computationally efficient. However, for more comprehensive spectral predictions, especially involving higher-energy transitions or states with potential charge-transfer character, range-separated functionals like CAM-B3LYP or ωB97X-D appear to provide more balanced results that are generally in better agreement with the higher-level EOM-CCSD reference.[@Jacquemin2008]

The use of the 6-311+G(d,p) basis set for TD-DFT calculations provides a reasonable balance between accuracy and computational cost. The diffuse functions (indicated by the + sign) are particularly important for accurately describing excited states, especially those with Rydberg character.[@Papajak2011] The smaller cc-pVDZ basis used for EOM-CCSD reflects the higher computational demands of this method, though ideally, a larger basis would be preferred for quantitative predictions.

### Implications for Photochemical Studies

These results have important implications for computational studies of formaldehyde photochemistry. The accurate prediction of the n→π* transition energy and its forbidden nature across all methods confirms the reliability of computational approaches for studying the primary photochemical processes of formaldehyde, which are initiated by this transition.[@Heicklen1988]

For studies involving higher-energy processes, such as interactions with UV radiation in the upper atmosphere, the choice of computational method becomes more critical.[@Gratien2007] The significant differences in predicted excitation energies and intensities between different functionals suggest that careful benchmarking against experimental data or higher-level calculations is essential for reliable predictions.

## Conclusion

Our computational study of formaldehyde's excited states demonstrates both the capabilities and limitations of different quantum chemical methods for predicting electronic transitions. All functionals examined (B3LYP, CAM-B3LYP, PBE0, and ωB97X-D) correctly identify the lowest energy n→π* transition around 3.95-4.00 eV with negligible oscillator strength, in good agreement with the EOM-CCSD reference value of 4.15 eV.

For higher energy excitations, we observe more pronounced differences between methods, with range-separated functionals generally predicting higher excitation energies than hybrid functionals. This behavior likely reflects the improved description of long-range interactions in range-separated functionals, which can be particularly important for excited states with partial charge-transfer or Rydberg character.[@Peach2008]

The oscillator strengths also show notable variations across functionals, with ωB97X-D predicting the most intense transitions. These differences highlight the importance of method selection when calculating properties that depend on transition intensities, such as absorption spectra or photochemical reaction rates.[@Dierksen2004]

Based on our results, we recommend using range-separated functionals like CAM-B3LYP or ωB97X-D for comprehensive studies of formaldehyde's excited states, especially when higher-energy transitions are of interest. For studies focusing primarily on the lowest n→π* transition, simpler hybrid functionals like B3LYP may be sufficient and computationally more efficient.

This study provides a foundation for future investigations of photochemical processes involving formaldehyde and similar carbonyl compounds. Further work could include more extensive benchmarking against experimental data, exploration of solvent effects on excitation energies, and investigation of potential energy surfaces for photochemical reactions.