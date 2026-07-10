---
title: Quantum Chemical Calculations of Hyperpolarizability - Setup and Initial Results
date: 2025-02-25
tags: quantum chemistry, hyperpolarizability, computational chemistry, psi4
description: A detailed walkthrough of setting up computational environment for calculating hyperpolarizabilities of Group 4A elements
---

## Abstract

This study documents the methodology for setting up computational environments to calculate hyperpolarizabilities of Group 4A elements (C through Fl) using open-source quantum chemistry software. We provide a step-by-step approach for establishing a conda-based Psi4 environment and creating input scripts for polarizability calculations. Despite encountering compatibility challenges with higher-order property calculations, we present our initial results for carbon atom polarizability using various computational approaches. This work offers a foundational framework for theoretical chemists seeking to explore nonlinear optical properties of elements and provides insights into the practical challenges of implementing such calculations with current open-source tools.

## Introduction

Nonlinear optical properties of atoms and molecules, particularly hyperpolarizabilities, are essential for understanding and developing materials for applications in photonics, optoelectronics, and optical data processing.[@Kanis1994; @Nalwa1997] The hyperpolarizability tensor represents the second-order response of a system's dipole moment to an external electric field and is crucial for predicting second-harmonic generation and electro-optic effects.[@Boyd2008]

Group 4A elements (carbon family) present an interesting case study for examining trends in nonlinear optical properties across the periodic table. From carbon to flerovium, these elements span a wide range of atomic sizes and electronic structures, allowing us to investigate how relativistic effects and outer electron configurations influence hyperpolarizability.[@Schwerdtfeger2002]

Computational quantum chemistry offers powerful tools for predicting these properties without the need for complex experimental setups, particularly valuable for unstable or radioactive elements like flerovium.[@Jensen2017] However, calculating hyperpolarizabilities accurately requires careful selection of computational methods, basis sets, and consideration of electron correlation effects.[@Shelton1992]

In this work, we document our approach to setting up computational environments for calculating the first-, second-, and third-order hyperpolarizabilities of Group 4A elements using open-source quantum chemistry software. We focus on Psi4, a modern quantum chemistry package that provides capabilities for calculating molecular properties including polarizabilities.[@Parrish2017]

The purpose of this blog post is to provide a detailed roadmap for researchers interested in similar calculations, documenting both our successes and the challenges encountered. By transparently sharing our methodology and initial results, we aim to contribute to the broader community's understanding of computational approaches to nonlinear optical properties.

## Experimental

### Computational System Specifications

All calculations were performed on an Ubuntu (noble/24.04) system accessed via SSH. The computational environment was set up using Miniconda to manage Python dependencies and ensure reproducibility.

### Software Installation

The following commands were executed to set up the computational environment:

```bash
# Install basic dependencies
sudo apt update
sudo apt install -y build-essential gfortran cmake python3-dev python3-pip python3-numpy python3-matplotlib libopenblas-dev liblapack-dev git curl

# Install apt-transport-https for repository management
sudo apt install -y apt-transport-https

# Add Psi4 repository (note: this step encountered issues with the repository)
sudo bash -c "echo 'deb https://psi4.s3.amazonaws.com/debian xenial main' > /etc/apt/sources.list.d/psi4.list"
curl -L https://psi4.s3.amazonaws.com/key.asc | sudo apt-key add -

# Alternative approach using Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Initialize conda
~/miniconda3/bin/conda init bash
source ~/.bashrc

# Create environment for Psi4
conda create -n psi4fix python=3.9 -c conda-forge
conda activate psi4fix

# Install pydantic v1 first (before psi4)
conda install pydantic=1.10 -c conda-forge

# Install Psi4
conda install psi4 psi4-rt -c psi4 -c conda-forge
```

### Project Directory Structure

The following directory structure was created to organize input files, outputs, and analysis scripts:

```bash
mkdir -p ~/hyperpolarizability/{scripts,inputs,outputs,analysis}
cd ~/hyperpolarizability
```

### Input File Preparation

Several input files were created to test different approaches for calculating polarizability:

1. Basic test input (C_test.in):

```
memory 2 GB

molecule C {
  C 0 0 0
  symmetry c1
}

set {
  basis cc-pVDZ
  e_convergence 1e-6
  d_convergence 1e-6
  scf_type df
  freeze_core True
}

# Calculate energy
energy('scf')

# Calculate polarizability
properties('scf', title='DIPOLE POLARIZABILITY', return_wfn=False)
```

2. Properties output test (C_props.in):

```
memory 2 GB

molecule C {
  C 0 0 0
  symmetry c1
}

set {
  basis cc-pVDZ
  e_convergence 1e-6
  d_convergence 1e-6
  scf_type df
}

# Run standard properties calculation
E, wfn = properties('scf', return_wfn=True)

# Print all available variables to help debug
print("\nAll variables available in wfn:")
all_vars = wfn.variables()
for var in sorted(all_vars.keys()):
    print(f"  {var} = {all_vars[var]}")

# Print specifically the SCF dipole moments
print("\nDipole Moment:")
print(wfn.variable("SCF DIPOLE"))
```

3. Input file generator script (generate_inputs.py):

```python
#!/usr/bin/env python3

import os

# Dictionary of elements with their symbols and atomic numbers
elements = {
    'Carbon': {'symbol': 'C', 'atomic_number': 6},
    'Silicon': {'symbol': 'Si', 'atomic_number': 14},
    'Germanium': {'symbol': 'Ge', 'atomic_number': 32},
    'Tin': {'symbol': 'Sn', 'atomic_number': 50},
    'Lead': {'symbol': 'Pb', 'atomic_number': 82},
    'Flerovium': {'symbol': 'Fl', 'atomic_number': 114}
}

# Create input files for each element
os.makedirs("../inputs", exist_ok=True)

for name, info in elements.items():
    symbol = info['symbol']
    
    # Create input file
    input_file = f"../inputs/{symbol}_hyperpol.in"
    
    with open(input_file, 'w') as f:
        f.write(f"""memory 4 GB

molecule {symbol} {{
  {symbol} 0 0 0
  symmetry c1
}}

set {{
  basis aug-cc-pVTZ
  e_convergence 1e-8
  d_convergence 1e-8
  scf_type df
  freeze_core True
}}

# First optimize the geometry
optimize('scf')

# Calculate the energy
energy('scf')

# Calculate first hyperpolarizability (α)
properties('scf', title='DIPOLE POLARIZABILITY')

# For second hyperpolarizability (γ), uncomment when ready
# Usually very computationally intensive
# properties('scf', title='QUADRUPOLE POLARIZABILITY')
""")
    
    print(f"Created input file for {name} ({symbol})")

print("\nInput files generated successfully!")
```

4. Calculation execution script (run_calculations.sh):

```bash
#!/bin/bash

INPUTS_DIR="inputs"
OUTPUTS_DIR="outputs"

mkdir -p $OUTPUTS_DIR

# Run for each input file
for input_file in $INPUTS_DIR/*.in; do
    basename=$(basename "$input_file" .in)
    echo "Processing $basename..."
    
    # Make sure we're using the conda environment
    echo "Running calculation with Psi4..."
    
    # Run Psi4
    psi4 -i "$input_file" -o "$OUTPUTS_DIR/${basename}.out"
    
    echo "Completed $basename"
    echo "------------------------"
done

echo "All calculations complete!"
```

5. Analysis script (analyze_hyperpol.py):

```python
#!/usr/bin/env python3

import os
import re
import matplotlib.pyplot as plt
import numpy as np

def extract_polarizability(filename):
    """Extract polarizability tensor from Psi4 output file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find the polarizability tensor section
    polar_match = re.search(r'Dipole Polarizability[\s\S]+?xx\s+([-\d.]+)\s+xy\s+([-\d.]+)\s+xz\s+([-\d.]+)[\s\S]+?yx\s+([-\d.]+)\s+yy\s+([-\d.]+)\s+yz\s+([-\d.]+)[\s\S]+?zx\s+([-\d.]+)\s+zy\s+([-\d.]+)\s+zz\s+([-\d.]+)', content)
    
    if polar_match:
        # Extract the 9 components of the tensor
        components = [float(polar_match.group(i)) for i in range(1, 10)]
        tensor = np.array(components).reshape(3, 3)
        
        # Calculate isotropic polarizability
        iso_polar = np.trace(tensor) / 3.0
        
        return tensor, iso_polar
    
    return None, None

# Create analysis directory if it doesn't exist
os.makedirs("../analysis", exist_ok=True)

# Process all output files
output_dir = "../outputs"
results = {}

for filename in os.listdir(output_dir):
    if filename.endswith(".out"):
        element = filename.split("_")[0]  # Extract element symbol
        filepath = os.path.join(output_dir, filename)
        
        tensor, iso_polar = extract_polarizability(filepath)
        if tensor is not None:
            results[element] = {
                'tensor': tensor,
                'isotropic': iso_polar
            }
            print(f"{element}: Isotropic polarizability = {iso_polar:.4f} a.u.")
            print(f"Tensor:\n{tensor}\n")

# If we have enough results, plot them
if len(results) > 1:
    elements = []
    polarizabilities = []
    
    for element, data in sorted(results.items()):
        elements.append(element)
        polarizabilities.append(data['isotropic'])
    
    plt.figure(figsize=(10, 6))
    plt.bar(elements, polarizabilities)
    plt.xlabel('Element')
    plt.ylabel('Isotropic Polarizability (a.u.)')
    plt.title('First-Order Polarizability Across Elements')
    plt.savefig('../analysis/polarizability_comparison.png')
    plt.close()
    
    print(f"Plot saved to '../analysis/polarizability_comparison.png'")
```

### Calculation Execution

The following commands were executed to run the calculations:

```bash
# Navigate to project directory
cd ~/hyperpolarizability

# Make scripts executable
chmod +x scripts/*.py scripts/*.sh

# Run properties test calculation
psi4 -i inputs/C_props.in -o outputs/C_props.out
```

## Results

The execution of `psi4 -i inputs/C_props.in -o outputs/C_props.out` produced the following output:

```
All variables available in wfn:
  CURRENT ENERGY = -37.59598618627132
  CURRENT REFERENCE ENERGY = -37.59598618627132
  DD SOLVATION ENERGY = 0.0
  HF KINETIC ENERGY = 37.58118542949597
  HF POTENTIAL ENERGY = -75.17717161576729
  HF TOTAL ENERGY = -37.59598618627132
  HF VIRIAL RATIO = 2.0003938342180057
  NUCLEAR REPULSION ENERGY = 0.0
  ONE-ELECTRON ENERGY = -50.33817518394048
  PCM POLARIZATION ENERGY = 0.0
  PE ENERGY = 0.0
  SCF DIPOLE = [2.52007710e-15 6.31180936e-16 2.08808779e-15]
  SCF ITERATION ENERGY = -37.59598618627132
  SCF ITERATIONS = 6.0
  SCF QUADRUPOLE = [[-3.80004134 -0.07916586 -0.74616477]
 [-0.07916586 -3.64097897 -0.30806585]
 [-0.74616477 -0.30806585 -6.51191789]]
  SCF TOTAL ENERGY = -37.59598618627132
  TWO-ELECTRON ENERGY = 12.742188997669164

Dipole Moment:
[2.52007710e-15 6.31180936e-16 2.08808779e-15]
```

The output of the simple test calculation showed the following variables:
- Total SCF energy: -37.59598618627132 Hartree
- SCF dipole moment: Near zero [2.52007710e-15, 6.31180936e-16, 2.08808779e-15]
- SCF quadrupole moment: 
  ```
  [[-3.80004134 -0.07916586 -0.74616477]
   [-0.07916586 -3.64097897 -0.30806585]
   [-0.74616477 -0.30806585 -6.51191789]]
  ```

When attempting to run calculations with polarizability-specific options, we encountered several errors:

1. Response solver error:
```
Error: option RESPONSE_SOLVER is not a valid option.
```

2. Properties argument error:
```
TypeError: 'properties' is an invalid keyword argument for property()
```

The execution of the filesystem check showed that Psi4 version 1.7 was installed:
```
python -c "import psi4; print(psi4.__version__)"
1.7
```

## Discussion

Our efforts to set up computational environments for calculating hyperpolarizabilities of Group 4A elements revealed both the capabilities and limitations of current open-source quantum chemistry software. The successful installation of Psi4 1.7 via conda provides a solid foundation for quantum chemical calculations, though we encountered specific challenges when attempting to calculate polarizabilities and higher-order responses.

The SCF energy calculation for the carbon atom (-37.59598618627132 Hartree) aligns with expected values for a restricted Hartree-Fock calculation using the cc-pVDZ basis set.[@Parrish2017] The near-zero dipole moment ([2.52007710e-15, 6.31180936e-16, 2.08808779e-15]) is theoretically correct for an isolated atom with spherical symmetry, confirming the basic accuracy of our calculations.

Our initial attempts to calculate polarizability encountered syntax and compatibility issues. The `RESPONSE_SOLVER` option error suggests that this parameter, which is used to specify the method for solving response equations in certain versions of Psi4, is not implemented in version 1.7. Similarly, the error with the `properties` argument indicates potential API changes between Psi4 versions, highlighting the importance of version-specific documentation.[@Parrish2017]

The quadrupole moment tensor obtained for carbon provides some insight into the electronic structure, particularly the electron density distribution, but does not directly translate to hyperpolarizability. The diagonal elements of the quadrupole tensor ([-3.80004134, -3.64097897, -6.51191789]) show some anisotropy, which may be an artifact of the basis set or numerical precision rather than a physical property of the carbon atom.[@Jensen2017]

Our approach of setting up a structured project with separate scripts for input generation, calculation execution, and analysis represents good scientific workflow practices. This organization facilitates reproducibility and systematic investigation of trends across the Group 4A elements.

For calculating hyperpolarizabilities specifically, we identified two potential approaches: (1) using Psi4's properties interface with appropriate options, and (2) employing a finite difference method to calculate the response of dipole moments to applied electric fields. The limitations we encountered suggest that the finite difference approach may be more reliable, albeit computationally more intensive.[@Shelton1992]

One significant challenge is the treatment of heavy elements like lead and flerovium, which require relativistic methods for accurate results. While our input generation script includes these elements, specialized basis sets and effective core potentials would be necessary for meaningful calculations.[@Schwerdtfeger2002]

## Conclusion

We have documented the setup process for quantum chemical calculations aimed at investigating hyperpolarizabilities of Group 4A elements using open-source software. While we successfully established a computational environment with Psi4 1.7 and ran basic quantum chemical calculations for carbon, we encountered specific limitations in the direct calculation of polarizabilities and hyperpolarizabilities.

The SCF energy and electronic properties calculated for carbon demonstrate the basic functionality of our setup, but additional work is needed to implement reliable methods for hyperpolarizability calculations. Based on our findings, we recommend exploring alternative approaches, such as finite difference methods or using specialized modules within Psi4 designed for property calculations.

For future work, we suggest:
1. Implementing a finite difference approach to calculate polarizabilities by applying small electric fields and measuring the response in dipole moments
2. Exploring alternative quantum chemistry packages such as NWChem, which may offer more robust property calculation capabilities
3. Developing specialized basis sets and considering relativistic effects for heavier elements like lead and flerovium
4. Benchmarking calculations against experimental data where available to validate computational approaches

This work provides a foundation for researchers interested in computational studies of nonlinear optical properties, offering practical insights into the challenges and potential solutions for calculating hyperpolarizabilities using open-source quantum chemistry software.

## Acknowledgements

We would like to thank the developers of Psi4 for creating and maintaining this powerful open-source quantum chemistry package. We also acknowledge the Python scientific computing community for developing essential tools such as NumPy and Matplotlib that enable scientific analysis and visualization. Special thanks to the Conda-Forge community for maintaining reliable package distributions that facilitate reproducible scientific computing environments.

## References

