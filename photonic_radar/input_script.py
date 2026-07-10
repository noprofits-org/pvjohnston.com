#!/usr/bin/env python3
import warnings
# Ignore NumPy version warnings
warnings.filterwarnings("ignore", message="A NumPy version")

import psi4
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from scipy import stats

# Setup output directory
output_dir = "lithium_niobate_results"
os.makedirs(output_dir, exist_ok=True)

# Configure Psi4 resources - optimized for your system
psi4.set_memory('8 GB')  # Increased to use more of your available RAM
psi4.set_num_threads(6)  # Using 6 of 8 available threads, leaving some for system
psi4.core.set_output_file(os.path.join(output_dir, 'psi4_output.dat'), False)

# Create LiNbO3 structures
def create_linbo3_structure(structure_type, dopant=None, dopant_position='Li', strain_factor=1.0):
    """Create LiNbO3 structures with various modifications"""
    # Base structure parameters
    a = 5.148 * strain_factor  # Apply strain if specified
    c = 13.863 * strain_factor
    
    # Initialize geometry variable
    geometry = ""
    
    if structure_type == "minimal":
        # Minimal cluster for quick calculations
        geometry = f"""
        0 1
        Li  0.0000  0.0000  0.0000
        Nb  0.0000  0.0000  2.5000
        O   1.0607  0.6124  1.2500
        O  -1.0607  0.6124  1.2500
        O   0.0000 -1.2248  1.2500
        units angstrom
        symmetry c1
        """
    elif structure_type == "extended":
        # More realistic cluster with more atoms
        geometry = f"""
        0 1
        Li  0.0000  0.0000  0.0000
        Nb  0.0000  0.0000  2.5000
        O   1.0607  0.6124  1.2500
        O  -1.0607  0.6124  1.2500
        O   0.0000 -1.2248  1.2500
        Li  2.5740  0.0000  0.0000
        Nb  2.5740  0.0000  2.5000
        O   3.6347  0.6124  1.2500
        O   1.5133  0.6124  1.2500
        O   2.5740 -1.2248  1.2500
        units angstrom
        symmetry c1
        """
    elif structure_type == "oxygen_deficient":
        # Start with the minimal structure but remove one oxygen
        geometry = f"""
        0 1
        Li  0.0000  0.0000  0.0000
        Nb  0.0000  0.0000  2.5000
        O   1.0607  0.6124  1.2500
        O  -1.0607  0.6124  1.2500
        units angstrom
        symmetry c1
        """
    else:
        # Default to minimal if structure type not recognized
        geometry = f"""
        0 1
        Li  0.0000  0.0000  0.0000
        Nb  0.0000  0.0000  2.5000
        O   1.0607  0.6124  1.2500
        O  -1.0607  0.6124  1.2500
        O   0.0000 -1.2248  1.2500
        units angstrom
        symmetry c1
        """
    
    # Apply dopant if specified
    if dopant and structure_type != "oxygen_deficient":
        lines = geometry.strip().split('\n')
        modified_lines = []
        
        for line in lines:
            if dopant_position in line.split() and dopant_position in ["Li", "Nb"] and "0.0000  0.0000  0.0000" in line:
                # Replace the first occurrence of the specified atom
                modified_lines.append(line.replace(dopant_position, dopant))
                continue
            modified_lines.append(line)
        
        geometry = '\n'.join(modified_lines)
    
    return geometry

# Finite field method for polarizability
def calculate_polarizability(structure_name, geometry, basis_set='def2-svp'):
    """Calculate polarizability using finite field method"""
    print(f"Calculating polarizability for {structure_name}...")
    
    # Define field strengths
    fields = [0.002, 0.001, 0.0, -0.001, -0.002]  # Using 5 points for better accuracy
    
    # Store results
    field_results = {}
    
    for field in fields:
        # Set output file for this calculation
        output_file = os.path.join(output_dir, f"{structure_name}_field{field:.6f}.dat")
        psi4.core.set_output_file(output_file, False)
        
        # Create molecule
        molecule = psi4.geometry(geometry)
        
        # Set options
        psi4.set_options({
            'basis': basis_set,
            'scf_type': 'df',
            'e_convergence': 1e-6,
            'd_convergence': 1e-6,
            'maxiter': 100
        })
        
        # Apply field if needed
        if field != 0.0:
            psi4.set_options({
                'perturb_h': True,
                'perturb_with': 'dipole',
                'perturb_dipole': [0.0, 0.0, field]
            })
        
        # Run calculation
        try:
            energy, wfn = psi4.energy('scf', return_wfn=True)
            dipole = wfn.variable("SCF DIPOLE")
            field_results[field] = {
                'energy': energy,
                'dipole': dipole
            }
            print(f"  Field {field}: Completed (E = {energy:.8f} Eh, μz = {dipole[2]:.6f} a.u.)")
        except Exception as e:
            print(f"  Field {field}: Error - {str(e)}")
    
    # Calculate polarizability if we have all results
    if len(field_results) == len(fields):
        # Extract dipoles
        fields_sorted = sorted(field_results.keys())
        dipoles = [field_results[f]['dipole'][2] for f in fields_sorted]
        
        # Use linear regression to get alpha (more accurate than 2-point)
        slope, intercept, r_value, p_value, std_err = stats.linregress(fields_sorted, dipoles)
        alpha_zz = -slope  # Negative because dipole = -alpha*field
        
        # Calculate R² as quality metric
        r_squared = r_value**2
        
        print(f"  Calculated alpha_zz = {alpha_zz:.6f} a.u. (R² = {r_squared:.4f})")
        
        # Save the result
        with open(os.path.join(output_dir, f"{structure_name}_polarizability.dat"), 'w') as f:
            f.write(f"Structure: {structure_name}\n")
            f.write(f"Alpha_zz: {alpha_zz:.6f} a.u.\n")
            f.write(f"R-squared: {r_squared:.6f}\n")
            f.write("\nField-Dipole Data:\n")
            f.write("Field (a.u.)\tDipole_z (a.u.)\n")
            for field, dipole in zip(fields_sorted, dipoles):
                f.write(f"{field:.6f}\t{dipole:.6f}\n")
        
        # Create a dipole vs. field plot
        plt.figure(figsize=(8, 6))
        plt.scatter(fields_sorted, dipoles, color='blue', label='Calculated')
        
        # Add regression line
        x_line = np.linspace(min(fields_sorted), max(fields_sorted), 100)
        y_line = intercept + slope * x_line
        plt.plot(x_line, y_line, color='red', label=f'Linear fit (α = {alpha_zz:.2f})')
        
        plt.xlabel('Electric Field (a.u.)')
        plt.ylabel('Dipole Moment (a.u.)')
        plt.title(f'Dipole Response to Electric Field - {structure_name}')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{structure_name}_dipole_field.png"), dpi=300)
        
        return {
            'alpha_zz': alpha_zz,
            'r_squared': r_squared,
            'dipoles': dipoles,
            'fields': fields_sorted
        }
    
    return None

# Calculate band gap
def calculate_electronic_properties(structure_name, geometry, basis_set='def2-svp'):
    """Calculate electronic properties including HOMO-LUMO gap"""
    print(f"Calculating electronic properties for {structure_name}...")
    
    # Set output file
    output_file = os.path.join(output_dir, f"{structure_name}_electronic.dat")
    psi4.core.set_output_file(output_file, False)
    
    # Create molecule
    molecule = psi4.geometry(geometry)
    
    # Set options
    psi4.set_options({
        'basis': basis_set,
        'scf_type': 'df',
        'e_convergence': 1e-6,
        'd_convergence': 1e-6
    })
    
    # Run calculation
    try:
        energy, wfn = psi4.energy('scf', return_wfn=True)
        
        # Extract orbital energies
        epsilon_a = wfn.epsilon_a()
        nocc = wfn.nalpha()
        nvir = epsilon_a.dim() - nocc
        
        # Find HOMO and LUMO 
        homo_energy = epsilon_a.get(nocc-1)
        lumo_energy = epsilon_a.get(nocc)
        gap = lumo_energy - homo_energy
        
        # Convert to eV
        homo_energy_ev = homo_energy * 27.211396
        lumo_energy_ev = lumo_energy * 27.211396
        gap_ev = gap * 27.211396
        
        print(f"  HOMO: {homo_energy_ev:.4f} eV")
        print(f"  LUMO: {lumo_energy_ev:.4f} eV")
        print(f"  Gap: {gap_ev:.4f} eV")
        
        # Save results
        with open(output_file, 'w') as f:
            f.write(f"Structure: {structure_name}\n")
            f.write(f"HOMO (Eh): {homo_energy:.6f}\n")
            f.write(f"LUMO (Eh): {lumo_energy:.6f}\n")
            f.write(f"Gap (Eh): {gap:.6f}\n")
            f.write(f"HOMO (eV): {homo_energy_ev:.6f}\n")
            f.write(f"LUMO (eV): {lumo_energy_ev:.6f}\n")
            f.write(f"Gap (eV): {gap_ev:.6f}\n")
        
        return {
            'homo': homo_energy,
            'lumo': lumo_energy,
            'gap': gap,
            'homo_ev': homo_energy_ev,
            'lumo_ev': lumo_energy_ev,
            'gap_ev': gap_ev
        }
    
    except Exception as e:
        print(f"  Error calculating electronic properties: {str(e)}")
        return None

# Main function
def main():
    start_time = time.time()
    print(f"Starting LiNbO3 property calculations at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {os.path.abspath(output_dir)}")
    
    # Define structures to analyze
    structures = {
        'LiNbO3_minimal': {'type': 'minimal'},
        'LiNbO3_extended': {'type': 'extended'},
        'LiNbO3_Mg_doped': {'type': 'minimal', 'dopant': 'Mg', 'position': 'Li'},
        'LiNbO3_Fe_doped': {'type': 'minimal', 'dopant': 'Fe', 'position': 'Li'},
        'LiNbO3_strained_0.98': {'type': 'minimal', 'strain': 0.98},
        'LiNbO3_O_deficient': {'type': 'oxygen_deficient'}
    }
    
    # Create actual geometry strings
    geometries = {}
    for name, params in structures.items():
        structure_type = params.get('type', 'minimal')
        dopant = params.get('dopant', None)
        position = params.get('position', 'Li')
        strain = params.get('strain', 1.0)
        
        geometries[name] = create_linbo3_structure(
            structure_type, 
            dopant=dopant, 
            dopant_position=position,
            strain_factor=strain
        )
    
    # Calculate properties
    results = {}
    for name, geometry in geometries.items():
        # Start with electronic properties (faster calculation)
        elec_props = calculate_electronic_properties(name, geometry)
        
        # Then do polarizability (more intensive)
        polar_props = calculate_polarizability(name, geometry)
        
        # Store combined results
        results[name] = {
            **(elec_props or {}),
            **(polar_props or {})
        }
        
        # Checkpoint by saving current results
        np.save(os.path.join(output_dir, "results_checkpoint.npy"), results)
    
    # Save final results
    np.save(os.path.join(output_dir, "final_results.npy"), results)
    
    # Generate summary report
    with open(os.path.join(output_dir, "summary_report.txt"), 'w') as f:
        f.write("LiNbO3 Computational Study Summary\n")
        f.write("=================================\n\n")
        
        f.write("Structure\tPolarizability (a.u.)\tBand Gap (eV)\n")
        f.write("-------------------------------------------------\n")
        
        for name, props in results.items():
            alpha = props.get('alpha_zz', 'N/A')
            gap = props.get('gap_ev', 'N/A')
            
            if alpha != 'N/A':
                alpha = f"{alpha:.4f}"
            if gap != 'N/A':
                gap = f"{gap:.4f}"
                
            f.write(f"{name}\t{alpha}\t{gap}\n")
    
    # Generate comparison plots
    if results:
        # Polarizability comparison
        valid_results = {k: v for k, v in results.items() if 'alpha_zz' in v}
        if valid_results:
            plt.figure(figsize=(10, 6))
            names = list(valid_results.keys())
            values = [results[name]['alpha_zz'] for name in names]
            
            # Sort by polarizability value
            sorted_idx = np.argsort(values)
            names = [names[i] for i in sorted_idx]
            values = [values[i] for i in sorted_idx]
            
            # Create bar chart
            plt.barh(names, values)
            plt.xlabel('Polarizability (a.u.)')
            plt.title('Comparison of Polarizabilities in LiNbO3 Structures')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'polarizability_comparison.png'), dpi=300)
        
        # Band gap comparison
        valid_results = {k: v for k, v in results.items() if 'gap_ev' in v}
        if valid_results:
            plt.figure(figsize=(10, 6))
            names = list(valid_results.keys())
            values = [results[name]['gap_ev'] for name in names]
            
            # Sort by gap value
            sorted_idx = np.argsort(values)
            names = [names[i] for i in sorted_idx]
            values = [values[i] for i in sorted_idx]
            
            # Create bar chart
            plt.barh(names, values)
            plt.xlabel('Band Gap (eV)')
            plt.title('Comparison of Band Gaps in LiNbO3 Structures')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'bandgap_comparison.png'), dpi=300)
        
        # Correlation plot
        valid_results = {k: v for k, v in results.items() if 'alpha_zz' in v and 'gap_ev' in v}
        if valid_results:
            plt.figure(figsize=(8, 6))
            names = list(valid_results.keys())
            x_values = [results[name]['gap_ev'] for name in names]
            y_values = [results[name]['alpha_zz'] for name in names]
            
            plt.scatter(x_values, y_values)
            for i, name in enumerate(names):
                plt.annotate(name, (x_values[i], y_values[i]), fontsize=8)
            
            plt.xlabel('Band Gap (eV)')
            plt.ylabel('Polarizability (a.u.)')
            plt.title('Correlation Between Band Gap and Polarizability')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'correlation_plot.png'), dpi=300)
    
    # Calculate runtime
    end_time = time.time()
    runtime = end_time - start_time
    hours, remainder = divmod(runtime, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"\nCalculations completed in {int(hours)}h {int(minutes)}m {seconds:.1f}s")
    print(f"Results saved to {output_dir}")
    
    # Write runtime to summary
    with open(os.path.join(output_dir, "summary_report.txt"), 'a') as f:
        f.write(f"\nTotal runtime: {int(hours)}h {int(minutes)}m {seconds:.1f}s\n")
        f.write(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()