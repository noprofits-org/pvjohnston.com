"""Minimal-basis LCAO-MO model of the H2+ ground state and its force.

The two protons carry one 1s Slater function each (exponent zeta = 1). The
symmetric (bonding, 1s-sigma-g) molecular orbital energy follows from the
closed-form two-centre integrals over 1s functions (see any quantum-chemistry
text, e.g. Jensen, Introduction to Computational Chemistry, or Atkins & de Paula,
Physical Chemistry):

    S(R) = e^{-R} (1 + R + R^2/3)                      overlap
    J(R) = 1/R - e^{-2R} (1 + 1/R)                      electron-(other nucleus)
    K(R) = e^{-R} (1 + R)                               resonance integral
    E_el(R) = -1/2 - (J + K) / (1 + S)                  electronic energy (hartree)
    V(R)    = E_el(R) + 1/R                             total potential (hartree)

All quantities are in atomic units; R is the internuclear distance in bohr.
This is a deliberately crude one-electron model. It is NOT the UHF/aug-cc-pV5Z
curve of the parent post; it is an independent, fully analytic H2+ curve that
carries the same qualitative structure (a 1/R repulsive wall at short R, a bound
minimum, dissociation to -1/2 hartree) and is therefore adequate for an internal
comparison of two training targets on one and the same curve.

The module exposes V(R) and its exact derivative dV/dR (hence the force
F = -dV/dR), computed analytically and cross-checked against complex-step
differentiation. Running the file executes the validation self-tests.
"""

from __future__ import annotations

import numpy as np

E_1S = -0.5  # hydrogen 1s energy for zeta = 1 (hartree)


def _S(R):
    return np.exp(-R) * (1.0 + R + R * R / 3.0)


def _J(R):
    return 1.0 / R - np.exp(-2.0 * R) * (1.0 + 1.0 / R)


def _K(R):
    return np.exp(-R) * (1.0 + R)


def electronic_energy(R):
    """LCAO bonding electronic energy E_el(R) in hartree."""
    return E_1S - (_J(R) + _K(R)) / (1.0 + _S(R))


def potential(R):
    """Total H2+ potential V(R) = E_el(R) + 1/R in hartree."""
    return electronic_energy(R) + 1.0 / R


# ---- analytic first derivatives (all in hartree / bohr) --------------------

def _dS(R):
    return -np.exp(-R) * R * (R + 1.0) / 3.0


def _dK(R):
    return -np.exp(-R) * R


def _dJ(R):
    return -1.0 / (R * R) + np.exp(-2.0 * R) * (2.0 + 2.0 / R + 1.0 / (R * R))


def d_electronic_energy(R):
    S, J, K = _S(R), _J(R), _K(R)
    dS, dJ, dK = _dS(R), _dJ(R), _dK(R)
    num = (dJ + dK) * (1.0 + S) - (J + K) * dS
    return -num / (1.0 + S) ** 2


def d_potential(R):
    """dV/dR in hartree/bohr (exact analytic derivative)."""
    return d_electronic_energy(R) - 1.0 / (R * R)


def force(R):
    """Force on the nuclei F = -dV/dR in hartree/bohr."""
    return -d_potential(R)


# ---- validation ------------------------------------------------------------

def _complex_step_derivative(func, R, h=1e-30):
    Rc = np.asarray(R, dtype=np.complex128) + 1j * h
    return np.imag(func(Rc)) / h


def _self_test():
    rng_R = np.geomspace(0.15, 20.0, 401)

    # 1. analytic dV/dR must match complex-step differentiation to machine eps.
    ana = d_potential(rng_R)
    cs = _complex_step_derivative(potential, rng_R)
    max_rel = np.max(np.abs(ana - cs) / (np.abs(cs) + 1e-12))
    assert max_rel < 1e-8, f"derivative mismatch {max_rel:.2e}"

    # 2. textbook integral values at R = 2 bohr (zeta = 1).
    assert abs(_S(2.0) - 0.586453) < 1e-5, _S(2.0)
    assert abs(_J(2.0) - 0.472530) < 1e-5, _J(2.0)
    assert abs(_K(2.0) - 0.406006) < 1e-5, _K(2.0)

    # 3. dissociation limit V(R->inf) -> -1/2 hartree.
    assert abs(potential(60.0) - E_1S) < 1e-3, potential(60.0)

    # 4. a bound minimum exists near the known LCAO value R_e ~ 2.49 bohr.
    grid = np.linspace(1.5, 4.0, 4001)
    Re = grid[int(np.argmin(potential(grid)))]
    assert 2.3 < Re < 2.7, Re
    De = E_1S - potential(Re)  # binding energy relative to H(1s)+p
    assert 0.05 < De < 0.09, De

    # 5. a repulsive wall: V rises steeply toward short R.
    assert potential(0.15) > potential(1.0) > potential(Re)

    return {
        "S_2": float(_S(2.0)),
        "J_2": float(_J(2.0)),
        "K_2": float(_K(2.0)),
        "V_2": float(potential(2.0)),
        "R_e_bohr": float(Re),
        "D_e_hartree": float(De),
        "max_rel_derivative_error": float(max_rel),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(_self_test(), indent=2))
