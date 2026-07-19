"""Stress-test pulse-independent trajectories near a conical intersection.

The experiment has two deliberately separate layers.

1. Exact split-operator propagation reproduces the coherent-state benchmarks
   of Mannouch and Kelly, J. Phys. Chem. Lett. 15, 11687--11695 (2024),
   DOI 10.1021/acs.jpclett.4c02418.
2. A trajectory layer compares full coherent propagation with the RP-AXE
   pulse-independent-trajectory construction of Galiana et al., J. Chem.
   Theory Comput. 22, 1224--1243 (2026),
   DOI 10.1021/acs.jctc.5c01809.

All equations and parameters are in atomic units.  The script intentionally
depends only on NumPy and the Python standard library so the downloadable
experiment is runnable without a chemistry package.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import platform
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


AU_TO_FS = 0.024188843265857
FS_TO_AU = 1.0 / AU_TO_FS


@dataclass(frozen=True)
class BMA:
    """Two-state, two-mode linear-vibronic-coupling BMA model."""

    omega_x: float = 7.743e-3
    omega_y: float = 6.68e-3
    a: float = 31.05
    c: float = 8.092e-5
    delta_p: float = 0.6

    @property
    def qbar_x(self) -> float:
        return self.a / 2.0

    @property
    def initial_sigma_x(self) -> float:
        return math.sqrt(1.0 / (2.0 * self.omega_x))

    @property
    def initial_sigma_y(self) -> float:
        return math.sqrt(1.0 / (2.0 * self.omega_y))


@dataclass(frozen=True)
class OneD:
    """The coherent one-dimensional avoided-crossing benchmark."""

    spring_k: float = 0.02
    coupling_b: float = 0.01
    coupling_a: float = 3.0
    qbar: float = -2.0
    epsilon: float = 0.01
    mass: float = 20_000.0
    delta_p: float = 0.6

    @property
    def omega(self) -> float:
        return math.sqrt(self.spring_k / self.mass)

    @property
    def initial_sigma(self) -> float:
        return math.sqrt(1.0 / (2.0 * self.mass * self.omega))


BMA_MODEL = BMA()
ONE_D_MODEL = OneD()


def electronic_initial_state(delta_p: float = 0.6) -> np.ndarray:
    """Return amplitudes in the paper's diabatic basis (psi_1, psi_2)."""

    return np.array(
        [math.sqrt((1.0 + delta_p) / 2.0),
         math.sqrt((1.0 - delta_p) / 2.0)],
        dtype=np.complex128,
    )


def bma_potential(qx: np.ndarray, qy: np.ndarray, model: BMA = BMA_MODEL):
    vbar = 0.5 * (model.omega_x**2 * qx**2 + model.omega_y**2 * qy**2)
    delta = model.c * qy
    kappa = 0.5 * model.omega_x**2 * model.a * qx
    return vbar, delta, kappa


def oned_potential(q: np.ndarray, model: OneD = ONE_D_MODEL):
    vbar = 0.5 * model.spring_k * q**2
    shifted = q - model.epsilon / (2.0 * model.spring_k * model.qbar)
    delta = model.coupling_b * np.exp(-model.coupling_a * shifted**2)
    kappa = model.spring_k * model.qbar * q - 0.5 * model.epsilon
    return vbar, delta, kappa


def apply_two_state_potential(
    psi: np.ndarray,
    vbar: np.ndarray,
    delta: np.ndarray,
    kappa: np.ndarray,
    tau: float,
) -> None:
    """Apply exp(-i V tau) in place in the (psi_1, psi_2) basis."""

    radius = np.hypot(delta, kappa)
    cosine = np.cos(radius * tau)
    sinc = np.empty_like(radius)
    nonzero = radius > 1e-14
    sinc[nonzero] = np.sin(radius[nonzero] * tau) / radius[nonzero]
    sinc[~nonzero] = tau
    phase = np.exp(-1j * vbar * tau)
    p0 = psi[0].copy()
    p1 = psi[1].copy()
    psi[0] = phase * (cosine * p0 - 1j * sinc * (-kappa * p0 + delta * p1))
    psi[1] = phase * (cosine * p1 - 1j * sinc * (delta * p0 + kappa * p1))


def apply_kinetic(psi: np.ndarray, multiplier: np.ndarray) -> None:
    axes = tuple(range(1, psi.ndim))
    psi_k = np.fft.fftn(psi, axes=axes)
    psi_k *= multiplier
    psi[:] = np.fft.ifftn(psi_k, axes=axes)


def upper_adiabatic_population(
    psi: np.ndarray,
    delta: np.ndarray,
    kappa: np.ndarray,
    volume_element: float,
) -> float:
    density = np.abs(psi[0]) ** 2 + np.abs(psi[1]) ** 2
    radius = np.hypot(delta, kappa)
    b_expect = (
        kappa * (np.abs(psi[1]) ** 2 - np.abs(psi[0]) ** 2)
        + 2.0 * delta * np.real(np.conj(psi[0]) * psi[1])
    )
    projected = np.zeros_like(density)
    np.divide(b_expect, radius, out=projected, where=radius > 1e-14)
    return float(np.sum(0.5 * (density + projected)) * volume_element)


def normalized_wavefunction(psi: np.ndarray, volume_element: float) -> np.ndarray:
    norm = math.sqrt(float(np.sum(np.abs(psi) ** 2) * volume_element))
    return psi / norm


# Digitized from the black dashed exact curve in Figure 6 of Mannouch and Kelly.
# The source is a vector figure; values are sampled at integer femtoseconds.
# The plotted line is about 0.003 population units thick, so this is a comparison
# reference rather than a claim that the paper tabulated five significant digits.
BMA_FIGURE6_EXACT = np.array([
    [0, 0.21689], [1, 0.21370], [2, 0.19941], [3, 0.14572],
    [4, 0.06380], [5, 0.02702], [6, 0.02443], [7, 0.02426],
    [8, 0.02233], [9, 0.02233], [10, 0.02208], [11, 0.02174],
    [12, 0.02139], [13, 0.02134], [14, 0.02174], [15, 0.03681],
    [16, 0.08211], [17, 0.17161], [18, 0.20190], [19, 0.21203],
    [20, 0.21292], [21, 0.20676], [22, 0.18000], [23, 0.10562],
    [24, 0.04296], [25, 0.02709], [26, 0.02540], [27, 0.02511],
    [28, 0.02471], [29, 0.02431], [30, 0.02312], [31, 0.02262],
    [32, 0.02213], [33, 0.02253], [34, 0.02471], [35, 0.04663],
    [36, 0.12471], [37, 0.18334], [38, 0.20080], [39, 0.20297],
    [40, 0.20519],
], dtype=float)


def run_bma_exact(
    grid_n: int = 384,
    half_width: float = 96.0,
    dt_fs: float = 0.025,
    total_fs: float = 40.0,
    sample_every_fs: float = 0.25,
    qbar_x: float | None = None,
    mean_momentum_x: float = 0.0,
    progress: bool = False,
) -> dict:
    """Propagate the BMA model on a square periodic Fourier grid."""

    model = BMA_MODEL
    qbar_x = model.qbar_x if qbar_x is None else float(qbar_x)
    x = np.linspace(-half_width, half_width, grid_n, endpoint=False)
    dx = float(x[1] - x[0])
    qx, qy = np.meshgrid(x, x, indexing="ij")
    vbar, delta, kappa = bma_potential(qx, qy, model)

    nuclear = np.exp(
        -0.5 * model.omega_x * (qx - qbar_x) ** 2
        -0.5 * model.omega_y * qy**2
        + 1j * mean_momentum_x * (qx - qbar_x)
    ).astype(np.complex128)
    electronic = electronic_initial_state(model.delta_p)
    psi = electronic[:, None, None] * nuclear[None, :, :]
    psi = normalized_wavefunction(psi, dx * dx)

    dt = dt_fs * FS_TO_AU
    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps
    dt = actual_dt_fs * FS_TO_AU
    sample_stride = max(1, int(round(sample_every_fs / actual_dt_fs)))
    kgrid = 2.0 * np.pi * np.fft.fftfreq(grid_n, d=dx)
    kx, ky = np.meshgrid(kgrid, kgrid, indexing="ij")
    kinetic = np.exp(-0.5j * (kx**2 + ky**2) * dt)[None, :, :]

    times = []
    upper = []
    centroid_x = []
    centroid_y = []
    product_left = []
    norms = []

    def observe(step: int) -> None:
        density = np.abs(psi[0]) ** 2 + np.abs(psi[1]) ** 2
        norm = float(np.sum(density) * dx * dx)
        times.append(step * actual_dt_fs)
        norms.append(norm)
        upper.append(upper_adiabatic_population(psi, delta, kappa, dx * dx))
        centroid_x.append(float(np.sum(qx * density) * dx * dx))
        centroid_y.append(float(np.sum(qy * density) * dx * dx))
        product_left.append(float(np.sum(density[qx < 0.0]) * dx * dx))

    observe(0)
    started = time.monotonic()
    for step in range(1, steps + 1):
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        apply_kinetic(psi, kinetic)
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        if step % sample_stride == 0 or step == steps:
            observe(step)
        if progress and (step % max(1, steps // 10) == 0 or step == steps):
            elapsed = time.monotonic() - started
            print(f"  BMA exact {grid_n=} {actual_dt_fs=:.5f}: "
                  f"{step}/{steps} ({elapsed:.1f} s)", flush=True)

    times_array = np.asarray(times)
    upper_array = np.asarray(upper)
    ref_t = BMA_FIGURE6_EXACT[:, 0]
    sim_at_ref = np.interp(ref_t, times_array, upper_array)
    residual = sim_at_ref - BMA_FIGURE6_EXACT[:, 1]

    return {
        "configuration": {
            "grid_n": grid_n,
            "half_width": half_width,
            "dx": dx,
            "requested_dt_fs": dt_fs,
            "actual_dt_fs": actual_dt_fs,
            "total_fs": total_fs,
            "sample_every_fs": sample_stride * actual_dt_fs,
            "qbar_x": qbar_x,
            "mean_momentum_x": mean_momentum_x,
        },
        "time_fs": times,
        "upper_population": upper,
        "centroid_x": centroid_x,
        "centroid_y": centroid_y,
        "product_qx_lt_0": product_left,
        "norm": norms,
        "figure6_comparison": {
            "time_fs": ref_t.tolist(),
            "digitized": BMA_FIGURE6_EXACT[:, 1].tolist(),
            "simulation": sim_at_ref.tolist(),
            "rmse": float(np.sqrt(np.mean(residual**2))),
            "max_abs": float(np.max(np.abs(residual))),
        },
        "runtime_seconds": time.monotonic() - started,
    }


def run_oned_exact(
    grid_n: int = 2048,
    half_width: float = 8.0,
    dt_fs: float = 0.05,
    total_fs: float = 200.0,
    sample_every_fs: float = 0.5,
    progress: bool = False,
) -> dict:
    """Propagate the paper's 1D model and retain its total nuclear density."""

    model = ONE_D_MODEL
    q = np.linspace(-half_width, half_width, grid_n, endpoint=False)
    dq = float(q[1] - q[0])
    vbar, delta, kappa = oned_potential(q, model)
    nuclear = np.exp(-0.5 * model.mass * model.omega * (q - model.qbar) ** 2)
    electronic = electronic_initial_state(model.delta_p)
    psi = electronic[:, None] * nuclear[None, :]
    psi = normalized_wavefunction(psi.astype(np.complex128), dq)

    dt = dt_fs * FS_TO_AU
    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps
    dt = actual_dt_fs * FS_TO_AU
    sample_stride = max(1, int(round(sample_every_fs / actual_dt_fs)))
    kgrid = 2.0 * np.pi * np.fft.fftfreq(grid_n, d=dq)
    kinetic = np.exp(-0.5j * kgrid**2 / model.mass * dt)[None, :]

    times = []
    densities = []
    upper = []
    norms = []

    def observe(step: int) -> None:
        density = np.abs(psi[0]) ** 2 + np.abs(psi[1]) ** 2
        times.append(step * actual_dt_fs)
        densities.append(density.astype(np.float32).tolist())
        norms.append(float(np.sum(density) * dq))
        upper.append(upper_adiabatic_population(psi, delta, kappa, dq))

    observe(0)
    started = time.monotonic()
    for step in range(1, steps + 1):
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        apply_kinetic(psi, kinetic)
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        if step % sample_stride == 0 or step == steps:
            observe(step)
        if progress and (step % max(1, steps // 10) == 0 or step == steps):
            elapsed = time.monotonic() - started
            print(f"  1D exact {grid_n=} {actual_dt_fs=:.5f}: "
                  f"{step}/{steps} ({elapsed:.1f} s)", flush=True)

    density_array = np.asarray(densities)
    # Quantitative signatures visible in the paper's exact density panel.
    # Both cutoffs are grid nodes at every declared resolution.  Include that
    # node before applying the trapezoid rule; excluding it moves the effective
    # boundary by half a grid cell and creates an artificial O(dq) difference.
    left_mask = q <= -1.5
    right_mask = q >= -1.0
    left_stationary = np.trapezoid(
        density_array[:, left_mask], q[left_mask], axis=1
    )
    right_moving = np.trapezoid(
        density_array[:, right_mask], q[right_mask], axis=1
    )
    return {
        "configuration": {
            "grid_n": grid_n,
            "half_width": half_width,
            "dq": dq,
            "requested_dt_fs": dt_fs,
            "actual_dt_fs": actual_dt_fs,
            "total_fs": total_fs,
            "sample_every_fs": sample_stride * actual_dt_fs,
        },
        "q": q.tolist(),
        "time_fs": times,
        "density": densities,
        "upper_population": upper,
        "stationary_q_lt_minus_1_5": left_stationary.tolist(),
        "moving_q_gt_minus_1": right_moving.tolist(),
        "norm": norms,
        "runtime_seconds": time.monotonic() - started,
    }


# ---------------------------------------------------------------------------
# Trajectory surface hopping with projected forces and momenta (PFMi)


def bma_adiabatic_quantities(q: np.ndarray, model: BMA = BMA_MODEL):
    """Return energies and forces for a batch of BMA geometries.

    ``q`` has shape (n, 2), energies shape (n, 2), and forces shape
    (n, 2 electronic states, 2 nuclear coordinates).  Electronic state 0 is
    the lower adiabat and state 1 the upper adiabat.
    """

    qx = q[:, 0]
    qy = q[:, 1]
    vbar, delta, kappa = bma_potential(qx, qy, model)
    radius = np.hypot(delta, kappa)
    energies = np.column_stack((vbar - radius, vbar + radius))

    grad_vbar_x = model.omega_x**2 * qx
    grad_vbar_y = model.omega_y**2 * qy
    grad_radius_x = np.zeros_like(radius)
    grad_radius_y = np.zeros_like(radius)
    nonzero = radius > 1e-12
    dkappa_dx = 0.5 * model.omega_x**2 * model.a
    grad_radius_x[nonzero] = (
        kappa[nonzero] * dkappa_dx / radius[nonzero]
    )
    grad_radius_y[nonzero] = (
        delta[nonzero] * model.c / radius[nonzero]
    )
    lower_force = np.column_stack((
        -grad_vbar_x + grad_radius_x,
        -grad_vbar_y + grad_radius_y,
    ))
    upper_force = np.column_stack((
        -grad_vbar_x - grad_radius_x,
        -grad_vbar_y - grad_radius_y,
    ))
    forces = np.stack((lower_force, upper_force), axis=1)
    return energies, forces


def bma_mixing(q: np.ndarray, model: BMA = BMA_MODEL):
    """Cosine and sine for the real local adiabatic transformation."""

    _, delta, kappa = bma_potential(q[:, 0], q[:, 1], model)
    theta = np.arctan2(delta, kappa)
    return np.cos(0.5 * theta), np.sin(0.5 * theta)


def diabatic_to_adiabatic(c_diabatic: np.ndarray, q: np.ndarray) -> np.ndarray:
    cosine, sine = bma_mixing(q)
    lower = cosine * c_diabatic[:, 0] - sine * c_diabatic[:, 1]
    upper = sine * c_diabatic[:, 0] + cosine * c_diabatic[:, 1]
    return np.column_stack((lower, upper))


def adiabatic_to_diabatic(c_adiabatic: np.ndarray, q: np.ndarray) -> np.ndarray:
    cosine, sine = bma_mixing(q)
    psi1 = cosine * c_adiabatic[:, 0] + sine * c_adiabatic[:, 1]
    psi2 = -sine * c_adiabatic[:, 0] + cosine * c_adiabatic[:, 1]
    return np.column_stack((psi1, psi2))


def apply_batch_potential(c_diabatic: np.ndarray, q: np.ndarray, tau: float) -> None:
    """Apply the analytic two-state electronic propagator to trajectories."""

    vbar, delta, kappa = bma_potential(q[:, 0], q[:, 1])
    radius = np.hypot(delta, kappa)
    cosine = np.cos(radius * tau)
    sinc = np.empty_like(radius)
    nonzero = radius > 1e-14
    sinc[nonzero] = np.sin(radius[nonzero] * tau) / radius[nonzero]
    sinc[~nonzero] = tau
    phase = np.exp(-1j * vbar * tau)
    p0 = c_diabatic[:, 0].copy()
    p1 = c_diabatic[:, 1].copy()
    c_diabatic[:, 0] = phase * (
        cosine * p0 - 1j * sinc * (-kappa * p0 + delta * p1)
    )
    c_diabatic[:, 1] = phase * (
        cosine * p1 - 1j * sinc * (delta * p0 + kappa * p1)
    )


def pfm_rate(p_aux: np.ndarray, f_aux: np.ndarray) -> np.ndarray:
    """Equation 43 of Grell et al. (2025) for the two-mode BMA model."""

    omega = math.sqrt(BMA_MODEL.omega_x * BMA_MODEL.omega_y)
    momentum_difference = np.abs(p_aux[:, 0] - p_aux[:, 1])
    force_difference = np.abs(f_aux[:, 0] - f_aux[:, 1])
    force_term = (
        math.pi**2 / (8.0 * omega)
        * momentum_difference
        * force_difference
    )
    spreading_term = momentum_difference * math.sqrt(
        math.pi**2 * 2.0 * omega / 8.0
    )
    return force_term + spreading_term


def apply_pfm_decoherence(
    c_diabatic: np.ndarray,
    q: np.ndarray,
    active: np.ndarray,
    p_aux: np.ndarray,
    f_aux: np.ndarray,
    dt: float,
) -> None:
    """Damp the inactive coefficient and renormalize the active one."""

    c_ad = diabatic_to_adiabatic(c_diabatic, q)
    rows = np.arange(c_ad.shape[0])
    inactive = 1 - active
    damping = np.exp(-pfm_rate(p_aux, f_aux) * dt)
    c_ad[rows, inactive] *= damping
    inactive_population = np.abs(c_ad[rows, inactive]) ** 2
    active_population = np.abs(c_ad[rows, active]) ** 2
    desired_active = np.maximum(0.0, 1.0 - inactive_population)
    safe = active_population > 1e-15
    c_ad[rows[safe], active[safe]] *= np.sqrt(
        desired_active[safe] / active_population[safe]
    )
    unsafe_rows = rows[~safe]
    if unsafe_rows.size:
        c_ad[unsafe_rows, active[~safe]] = np.sqrt(desired_active[~safe])
    c_diabatic[:] = adiabatic_to_diabatic(c_ad, q)


def electronic_norm(c_diabatic: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(c_diabatic) ** 2, axis=1)


def initialize_auxiliary_momenta(momentum: np.ndarray) -> np.ndarray:
    speed = np.linalg.norm(momentum, axis=1)
    return np.repeat(speed[:, None], 2, axis=1)


def auxiliary_forces(
    energy_old: np.ndarray,
    energy_new: np.ndarray,
    midpoint_momentum: np.ndarray,
    dt: float,
) -> np.ndarray:
    speed = np.linalg.norm(midpoint_momentum, axis=1)
    output = np.zeros_like(energy_old)
    moving = speed >= 1e-9
    output[moving] = (
        (energy_old[moving] - energy_new[moving])
        / (speed[moving, None] * dt)
    )
    return output


def update_auxiliary_momenta(
    c_diabatic: np.ndarray,
    q: np.ndarray,
    p_aux_old: np.ndarray,
    f_aux: np.ndarray,
    active_old: np.ndarray,
    active_new: np.ndarray,
    population_old: np.ndarray,
    energy_new: np.ndarray,
    kinetic: np.ndarray,
    hop_scale: np.ndarray,
    dt: float,
    threshold: float = 1e-4,
) -> tuple[np.ndarray, np.ndarray]:
    """Equations 54--61, including momentum injection and packet death."""

    rows = np.arange(c_diabatic.shape[0])
    c_ad = diabatic_to_adiabatic(c_diabatic, q)
    population_new = np.abs(c_ad) ** 2
    inactive = 1 - active_new

    p_aux = p_aux_old.copy()
    active_momentum = (
        p_aux_old[rows, active_old] + f_aux[rows, active_new] * dt
    ) * hop_scale
    p_aux[rows, active_new] = active_momentum

    gap = energy_new[rows, inactive] - energy_new[rows, active_new]
    ratio = np.ones_like(kinetic)
    positive_kinetic = kinetic > 1e-15
    ratio[positive_kinetic] = np.sqrt(np.maximum(
        0.0,
        1.0 - gap[positive_kinetic] / kinetic[positive_kinetic],
    ))
    ratio[~positive_kinetic & (gap > 0.0)] = 0.0
    born_momentum = active_momentum * ratio

    old_inactive_population = population_old[rows, inactive]
    new_inactive_population = population_new[rows, inactive]
    above_both = (
        (old_inactive_population >= threshold)
        & (new_inactive_population >= threshold)
    )
    propagated = p_aux_old[rows, inactive] + f_aux[rows, inactive] * dt
    p_aux[rows, inactive] = np.where(
        above_both, propagated, born_momentum
    )

    gained = np.maximum(0.0, new_inactive_population - old_inactive_population)
    inject = above_both & (gained > 0.0)
    if np.any(inject):
        fraction = np.zeros_like(gained)
        fraction[inject] = gained[inject] / new_inactive_population[inject]
        p_aux[rows[inject], inactive[inject]] = (
            p_aux[rows[inject], inactive[inject]] * (1.0 - fraction[inject])
            + born_momentum[inject] * fraction[inject]
        )

    died = (
        (old_inactive_population >= threshold)
        & (new_inactive_population < threshold)
    )
    if np.any(died):
        died_rows = rows[died]
        c_ad[died_rows, inactive[died]] = 0.0
        phase = np.exp(1j * np.angle(c_ad[died_rows, active_new[died]]))
        c_ad[died_rows, active_new[died]] = phase
        c_diabatic[died] = adiabatic_to_diabatic(c_ad[died], q[died])

    return p_aux, population_new


def attempt_two_state_hops(
    population_before: np.ndarray,
    population_after: np.ndarray,
    active: np.ndarray,
    q: np.ndarray,
    momentum: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Discrete two-state density flux with isotropic energy rescaling."""

    rows = np.arange(active.size)
    active_before = population_before[rows, active]
    active_after = population_after[rows, active]
    probability = np.maximum(
        0.0,
        (active_before - active_after) / np.maximum(active_before, 1e-14),
    )
    probability = np.minimum(probability, 1.0)
    proposed = rng.random(active.size) < probability
    accepted = np.zeros(active.size, dtype=bool)
    scale = np.ones(active.size)
    if not np.any(proposed):
        return active, momentum, accepted, scale

    energies, _ = bma_adiabatic_quantities(q)
    target = 1 - active
    delta_energy = energies[rows, target] - energies[rows, active]
    kinetic = 0.5 * np.sum(momentum**2, axis=1)
    allowed = proposed & (kinetic + 1e-14 >= delta_energy)
    accepted[allowed] = True
    positive = allowed & (kinetic > 1e-15)
    scale[positive] = np.sqrt(np.maximum(
        0.0,
        (kinetic[positive] - delta_energy[positive]) / kinetic[positive],
    ))
    momentum[allowed] *= scale[allowed, None]
    active[allowed] = target[allowed]
    return active, momentum, accepted, scale


def advance_full_electronics(
    c_diabatic: np.ndarray,
    q_old: np.ndarray,
    q_new: np.ndarray,
    active: np.ndarray,
    midpoint_momentum: np.ndarray,
    p_aux: np.ndarray,
    f_aux: np.ndarray,
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Electronic propagation, hops, and PFMi damping for FP trajectories."""

    sub_dt = dt / electronic_substeps
    displacement = q_new - q_old
    hop_counts = np.zeros(electronic_substeps, dtype=np.int64)
    cumulative_scale = np.ones(active.size)
    for substep in range(electronic_substeps):
        fraction_a = substep / electronic_substeps
        fraction_b = (substep + 1) / electronic_substeps
        q_a = q_old + fraction_a * displacement
        q_b = q_old + fraction_b * displacement
        q_mid = 0.5 * (q_a + q_b)
        population_before = np.abs(diabatic_to_adiabatic(c_diabatic, q_a)) ** 2
        apply_batch_potential(c_diabatic, q_mid, sub_dt)
        population_after = np.abs(diabatic_to_adiabatic(c_diabatic, q_b)) ** 2
        active, midpoint_momentum, accepted, scale = attempt_two_state_hops(
            population_before,
            population_after,
            active,
            q_b,
            midpoint_momentum,
            rng,
        )
        hop_counts[substep] = int(np.sum(accepted))
        cumulative_scale *= scale
        apply_pfm_decoherence(
            c_diabatic, q_b, active, p_aux, f_aux, sub_dt
        )
    return active, midpoint_momentum, hop_counts, cumulative_scale


def advance_axe_electronics(
    base_diabatic: np.ndarray,
    reprop_diabatic: np.ndarray,
    q_old: np.ndarray,
    q_new: np.ndarray,
    active: np.ndarray,
    midpoint_momentum: np.ndarray,
    base_p_aux: np.ndarray,
    reprop_p_aux: np.ndarray,
    f_aux: np.ndarray,
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Propagate AXE paths and repropagated coefficients online.

    The repropagation is mathematically the same as replaying stored positions,
    momenta, energies, and active-state histories afterward; doing it online
    avoids a large path file and cannot feed back into the base trajectories.
    """

    sub_dt = dt / electronic_substeps
    displacement = q_new - q_old
    hop_counts = np.zeros(electronic_substeps, dtype=np.int64)
    cumulative_scale = np.ones(active.size)
    for substep in range(electronic_substeps):
        fraction_a = substep / electronic_substeps
        fraction_b = (substep + 1) / electronic_substeps
        q_a = q_old + fraction_a * displacement
        q_b = q_old + fraction_b * displacement
        q_mid = 0.5 * (q_a + q_b)

        base_before = np.abs(
            diabatic_to_adiabatic(base_diabatic, q_a)
        ) ** 2
        apply_batch_potential(base_diabatic, q_mid, sub_dt)
        base_after = np.abs(
            diabatic_to_adiabatic(base_diabatic, q_b)
        ) ** 2
        active, midpoint_momentum, accepted, scale = attempt_two_state_hops(
            base_before,
            base_after,
            active,
            q_b,
            midpoint_momentum,
            rng,
        )
        hop_counts[substep] = int(np.sum(accepted))
        cumulative_scale *= scale
        apply_pfm_decoherence(
            base_diabatic, q_b, active, base_p_aux, f_aux, sub_dt
        )

        apply_batch_potential(reprop_diabatic, q_mid, sub_dt)
        apply_pfm_decoherence(
            reprop_diabatic, q_b, active, reprop_p_aux, f_aux, sub_dt
        )
    return active, midpoint_momentum, hop_counts, cumulative_scale


def sample_bma_wigner(
    count: int,
    center_fraction: float,
    rng: np.random.Generator,
    momentum_kick_sigma: float = 0.0,
    model: BMA = BMA_MODEL,
) -> tuple[np.ndarray, np.ndarray]:
    center_x = center_fraction * model.qbar_x
    q = np.column_stack((
        rng.normal(center_x, model.initial_sigma_x, count),
        rng.normal(0.0, model.initial_sigma_y, count),
    ))
    sigma_px = math.sqrt(model.omega_x / 2.0)
    momentum = np.column_stack((
        rng.normal(-momentum_kick_sigma * sigma_px, sigma_px, count),
        rng.normal(0.0, math.sqrt(model.omega_y / 2.0), count),
    ))
    return q, momentum


def target_diabatic_coefficients(count: int) -> np.ndarray:
    return np.repeat(
        electronic_initial_state(BMA_MODEL.delta_p)[None, :],
        count,
        axis=0,
    )


def initialize_full_ensemble(
    q: np.ndarray,
    momentum: np.ndarray,
    rng: np.random.Generator,
) -> dict:
    count = q.shape[0]
    coefficients = target_diabatic_coefficients(count)
    population = np.abs(diabatic_to_adiabatic(coefficients, q)) ** 2
    active = (rng.random(count) < population[:, 1]).astype(np.int8)
    energies, _ = bma_adiabatic_quantities(q)
    rows = np.arange(count)
    return {
        "q": q.copy(),
        "p": momentum.copy(),
        "c": coefficients,
        "active": active,
        "p_aux": initialize_auxiliary_momenta(momentum),
        "initial_energy": 0.5 * np.sum(momentum**2, axis=1)
            + energies[rows, active],
        "max_energy_drift": np.zeros(count),
    }


def initialize_axe_ensemble(q: np.ndarray, momentum: np.ndarray) -> dict:
    count = q.shape[0]
    q_axe = np.concatenate((q, q), axis=0)
    p_axe = np.concatenate((momentum, momentum), axis=0)
    active = np.concatenate((
        np.zeros(count, dtype=np.int8),
        np.ones(count, dtype=np.int8),
    ))
    pure_ad = np.zeros((2 * count, 2), dtype=np.complex128)
    pure_ad[np.arange(2 * count), active] = 1.0
    base_coefficients = adiabatic_to_diabatic(pure_ad, q_axe)
    target = target_diabatic_coefficients(count)
    target_population = np.abs(diabatic_to_adiabatic(target, q)) ** 2
    weights = np.concatenate((target_population[:, 0], target_population[:, 1]))
    energies, _ = bma_adiabatic_quantities(q_axe)
    rows = np.arange(2 * count)
    return {
        "q": q_axe,
        "p": p_axe,
        "base_c": base_coefficients,
        "reprop_c": np.concatenate((target.copy(), target.copy()), axis=0),
        "active": active,
        "base_p_aux": initialize_auxiliary_momenta(p_axe),
        "reprop_p_aux": initialize_auxiliary_momenta(p_axe),
        "weights": weights,
        "geometry_count": count,
        "initial_energy": 0.5 * np.sum(p_axe**2, axis=1)
            + energies[rows, active],
        "max_energy_drift": np.zeros(2 * count),
    }


def force_for_active(forces: np.ndarray, active: np.ndarray) -> np.ndarray:
    return forces[np.arange(active.size), active]


def step_full_ensemble(
    state: dict,
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    q_old = state["q"]
    p_old = state["p"]
    active_old = state["active"].copy()
    energy_old, force_old_all = bma_adiabatic_quantities(q_old)
    population_old = np.abs(
        diabatic_to_adiabatic(state["c"], q_old)
    ) ** 2
    midpoint_p = p_old + 0.5 * force_for_active(
        force_old_all, active_old
    ) * dt
    q_new = q_old + midpoint_p * dt
    energy_new, force_new_all = bma_adiabatic_quantities(q_new)
    f_aux = auxiliary_forces(energy_old, energy_new, midpoint_p, dt)
    active_new, midpoint_p, hop_counts, hop_scale = advance_full_electronics(
        state["c"],
        q_old,
        q_new,
        active_old.copy(),
        midpoint_p,
        state["p_aux"],
        f_aux,
        dt,
        electronic_substeps,
        rng,
    )
    p_new = midpoint_p + 0.5 * force_for_active(
        force_new_all, active_new
    ) * dt
    kinetic_midpoint = 0.5 * np.sum(midpoint_p**2, axis=1)
    p_aux, _ = update_auxiliary_momenta(
        state["c"],
        q_new,
        state["p_aux"],
        f_aux,
        active_old,
        active_new,
        population_old,
        energy_new,
        kinetic_midpoint,
        hop_scale,
        dt,
    )
    rows = np.arange(active_new.size)
    total_energy = 0.5 * np.sum(p_new**2, axis=1) + energy_new[rows, active_new]
    state["max_energy_drift"] = np.maximum(
        state["max_energy_drift"],
        np.abs(total_energy - state["initial_energy"]),
    )
    state["q"] = q_new
    state["p"] = p_new
    state["active"] = active_new
    state["p_aux"] = p_aux
    return hop_counts


def step_axe_ensemble(
    state: dict,
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    q_old = state["q"]
    p_old = state["p"]
    active_old = state["active"].copy()
    energy_old, force_old_all = bma_adiabatic_quantities(q_old)
    base_population_old = np.abs(
        diabatic_to_adiabatic(state["base_c"], q_old)
    ) ** 2
    reprop_population_old = np.abs(
        diabatic_to_adiabatic(state["reprop_c"], q_old)
    ) ** 2
    midpoint_p = p_old + 0.5 * force_for_active(
        force_old_all, active_old
    ) * dt
    q_new = q_old + midpoint_p * dt
    energy_new, force_new_all = bma_adiabatic_quantities(q_new)
    f_aux = auxiliary_forces(energy_old, energy_new, midpoint_p, dt)
    active_new, midpoint_p, hop_counts, hop_scale = advance_axe_electronics(
        state["base_c"],
        state["reprop_c"],
        q_old,
        q_new,
        active_old.copy(),
        midpoint_p,
        state["base_p_aux"],
        state["reprop_p_aux"],
        f_aux,
        dt,
        electronic_substeps,
        rng,
    )
    p_new = midpoint_p + 0.5 * force_for_active(
        force_new_all, active_new
    ) * dt
    kinetic_midpoint = 0.5 * np.sum(midpoint_p**2, axis=1)
    base_p_aux, _ = update_auxiliary_momenta(
        state["base_c"],
        q_new,
        state["base_p_aux"],
        f_aux,
        active_old,
        active_new,
        base_population_old,
        energy_new,
        kinetic_midpoint,
        hop_scale,
        dt,
    )
    reprop_p_aux, _ = update_auxiliary_momenta(
        state["reprop_c"],
        q_new,
        state["reprop_p_aux"],
        f_aux,
        active_old,
        active_new,
        reprop_population_old,
        energy_new,
        kinetic_midpoint,
        hop_scale,
        dt,
    )
    rows = np.arange(active_new.size)
    total_energy = 0.5 * np.sum(p_new**2, axis=1) + energy_new[rows, active_new]
    state["max_energy_drift"] = np.maximum(
        state["max_energy_drift"],
        np.abs(total_energy - state["initial_energy"]),
    )
    state["q"] = q_new
    state["p"] = p_new
    state["active"] = active_new
    state["base_p_aux"] = base_p_aux
    state["reprop_p_aux"] = reprop_p_aux
    return hop_counts


def observe_full_ensemble(state: dict) -> dict:
    c_ad = diabatic_to_adiabatic(state["c"], state["q"])
    population = np.abs(c_ad) ** 2
    return {
        "upper_population": float(np.mean(population[:, 1])),
        "active_upper_fraction": float(np.mean(state["active"] == 1)),
        "coherence_amplitude": float(np.mean(
            2.0 * np.abs(np.conj(c_ad[:, 0]) * c_ad[:, 1])
        )),
        "centroid_x": float(np.mean(state["q"][:, 0])),
        "centroid_y": float(np.mean(state["q"][:, 1])),
        "product_qx_lt_0": float(np.mean(state["q"][:, 0] < 0.0)),
        "electronic_norm_error": float(np.max(np.abs(
            electronic_norm(state["c"]) - 1.0
        ))),
    }


def observe_axe_ensemble(state: dict) -> dict:
    c_ad = diabatic_to_adiabatic(state["reprop_c"], state["q"])
    population = np.abs(c_ad) ** 2
    weight = state["weights"]
    denominator = float(state["geometry_count"])
    return {
        "upper_population": float(np.sum(weight * population[:, 1]) / denominator),
        "coherence_amplitude": float(np.sum(
            weight * 2.0 * np.abs(np.conj(c_ad[:, 0]) * c_ad[:, 1])
        ) / denominator),
        "centroid_x": float(np.sum(weight * state["q"][:, 0]) / denominator),
        "centroid_y": float(np.sum(weight * state["q"][:, 1]) / denominator),
        "product_qx_lt_0": float(np.sum(
            weight * (state["q"][:, 0] < 0.0)
        ) / denominator),
        "electronic_norm_error": float(np.max(np.abs(
            electronic_norm(state["reprop_c"]) - 1.0
        ))),
        "weight_sum_per_geometry": float(np.sum(weight) / denominator),
    }


def append_observation(storage: dict, observation: dict) -> None:
    for key, value in observation.items():
        storage.setdefault(key, []).append(value)


def first_threshold_crossing(
    time_fs: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    below = np.flatnonzero(values <= threshold)
    if below.size == 0:
        return float("nan")
    index = int(below[0])
    if index == 0:
        return float(time_fs[0])
    t0, t1 = time_fs[index - 1:index + 1]
    y0, y1 = values[index - 1:index + 1]
    if abs(y1 - y0) < 1e-15:
        return float(t1)
    return float(t0 + (threshold - y0) * (t1 - t0) / (y1 - y0))


def trajectory_comparison_summary(
    time_fs: np.ndarray,
    full: dict,
    reprop: dict,
    hop_time_fs: np.ndarray,
) -> dict:
    coherence = np.asarray(full["coherence_amplitude"])
    lifetime = first_threshold_crossing(
        time_fs, coherence, coherence[0] / math.e
    )
    if hop_time_fs.size and math.isfinite(lifetime):
        early_hop_fraction = float(np.mean(hop_time_fs <= lifetime))
    else:
        early_hop_fraction = float("nan")
    population_error = np.abs(
        np.asarray(full["upper_population"])
        - np.asarray(reprop["upper_population"])
    )
    product_error = np.abs(
        np.asarray(full["product_qx_lt_0"])
        - np.asarray(reprop["product_qx_lt_0"])
    )
    centroid_error_sigma = np.abs(
        np.asarray(full["centroid_x"])
        - np.asarray(reprop["centroid_x"])
    ) / BMA_MODEL.initial_sigma_x
    return {
        "coherence_lifetime_fs": lifetime,
        "successful_full_hops": int(hop_time_fs.size),
        "early_hop_fraction": early_hop_fraction,
        "max_upper_population_error": float(np.max(population_error)),
        "time_of_max_upper_population_error_fs": float(
            time_fs[int(np.argmax(population_error))]
        ),
        "max_product_probability_error": float(np.max(product_error)),
        "time_of_max_product_probability_error_fs": float(
            time_fs[int(np.argmax(product_error))]
        ),
        "max_centroid_x_error_sigma": float(np.max(centroid_error_sigma)),
        "time_of_max_centroid_x_error_fs": float(
            time_fs[int(np.argmax(centroid_error_sigma))]
        ),
        "population_error_series": population_error.tolist(),
        "product_error_series": product_error.tolist(),
        "centroid_error_sigma_series": centroid_error_sigma.tolist(),
    }


def run_trajectory_regime(
    center_fraction: float,
    seed: int,
    geometry_count: int = 4000,
    dt_fs: float = 0.05,
    electronic_substeps: int = 5,
    total_fs: float = 20.0,
    momentum_kick_sigma: float = 0.0,
    progress: bool = False,
) -> dict:
    """Run one paired FP/RP-AXE replicate for one launch position."""

    initial_rng = np.random.default_rng(seed)
    full_rng = np.random.default_rng(100_000 + seed)
    axe_rng = np.random.default_rng(200_000 + seed)
    q_initial, p_initial = sample_bma_wigner(
        geometry_count,
        center_fraction,
        initial_rng,
        momentum_kick_sigma=momentum_kick_sigma,
    )
    full_state = initialize_full_ensemble(q_initial, p_initial, full_rng)
    axe_state = initialize_axe_ensemble(q_initial, p_initial)

    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps
    dt = actual_dt_fs * FS_TO_AU
    time_values = [0.0]
    full_observations: dict[str, list] = {}
    reprop_observations: dict[str, list] = {}
    append_observation(full_observations, observe_full_ensemble(full_state))
    append_observation(reprop_observations, observe_axe_ensemble(axe_state))
    full_hop_times = []
    axe_hop_count = 0
    started = time.monotonic()

    for step in range(steps):
        full_hops = step_full_ensemble(
            full_state, dt, electronic_substeps, full_rng
        )
        axe_hops = step_axe_ensemble(
            axe_state, dt, electronic_substeps, axe_rng
        )
        axe_hop_count += int(np.sum(axe_hops))
        for substep, count in enumerate(full_hops):
            if count:
                substep_time = (
                    step + (substep + 1) / electronic_substeps
                ) * actual_dt_fs
                full_hop_times.extend([substep_time] * int(count))
        time_values.append((step + 1) * actual_dt_fs)
        append_observation(full_observations, observe_full_ensemble(full_state))
        append_observation(reprop_observations, observe_axe_ensemble(axe_state))
        if progress and (
            (step + 1) % max(1, steps // 10) == 0 or step + 1 == steps
        ):
            print(
                f"  trajectories center={center_fraction:g} seed={seed} "
                f"{step + 1}/{steps} ({time.monotonic() - started:.1f} s)",
                flush=True,
            )

    time_array = np.asarray(time_values)
    hop_time_array = np.asarray(full_hop_times)
    comparison = trajectory_comparison_summary(
        time_array, full_observations, reprop_observations, hop_time_array
    )
    full_energy_drift = full_state["max_energy_drift"]
    axe_energy_drift = axe_state["max_energy_drift"]
    diagnostics = {
        "max_full_electronic_norm_error": float(np.max(
            full_observations["electronic_norm_error"]
        )),
        "max_reprop_electronic_norm_error": float(np.max(
            reprop_observations["electronic_norm_error"]
        )),
        "max_axe_weight_normalization_error": float(np.max(np.abs(
            np.asarray(reprop_observations["weight_sum_per_geometry"]) - 1.0
        ))),
        "full_energy_drift_max_hartree": float(np.max(full_energy_drift)),
        "full_energy_drift_p99_hartree": float(np.quantile(full_energy_drift, 0.99)),
        "axe_energy_drift_max_hartree": float(np.max(axe_energy_drift)),
        "axe_energy_drift_p99_hartree": float(np.quantile(axe_energy_drift, 0.99)),
        "successful_axe_hops": axe_hop_count,
        "max_full_internal_consistency_error": float(np.max(np.abs(
            np.asarray(full_observations["upper_population"])
            - np.asarray(full_observations["active_upper_fraction"])
        ))),
    }
    return {
        "configuration": {
            "center_fraction": center_fraction,
            "center_x": center_fraction * BMA_MODEL.qbar_x,
            "momentum_kick_toward_ci_sigma_px": momentum_kick_sigma,
            "mean_momentum_x": -momentum_kick_sigma
                * math.sqrt(BMA_MODEL.omega_x / 2.0),
            "seed": seed,
            "geometry_count": geometry_count,
            "requested_dt_fs": dt_fs,
            "actual_dt_fs": actual_dt_fs,
            "electronic_substeps": electronic_substeps,
            "electronic_dt_fs": actual_dt_fs / electronic_substeps,
            "total_fs": total_fs,
            "pfm_omega": math.sqrt(BMA_MODEL.omega_x * BMA_MODEL.omega_y),
            "pfm_population_threshold": 1e-4,
        },
        "time_fs": time_values,
        "full": full_observations,
        "reprop_axe": reprop_observations,
        "full_hop_time_fs": full_hop_times,
        "comparison": comparison,
        "diagnostics": diagnostics,
        "runtime_seconds": time.monotonic() - started,
    }


def mean_ci95(values: list[float]) -> dict:
    array = np.asarray(values, dtype=float)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {"mean": float("nan"), "ci95_half_width": float("nan"), "n": 0}
    if finite.size == 1:
        half_width = float("nan")
    else:
        # Student-t critical value for the preregistered four replicates.
        t_critical = 3.182 if finite.size == 4 else 1.96
        half_width = float(
            t_critical * np.std(finite, ddof=1) / math.sqrt(finite.size)
        )
    return {
        "mean": float(np.mean(finite)),
        "ci95_half_width": half_width,
        "n": int(finite.size),
    }


def aggregate_regime_runs(runs: list[dict]) -> dict:
    if not runs:
        raise ValueError("cannot aggregate an empty regime")
    time_fs = np.asarray(runs[0]["time_fs"])
    for run in runs[1:]:
        if not np.allclose(time_fs, np.asarray(run["time_fs"]), atol=1e-12):
            raise ValueError("replicate time grids differ")

    full_fields = list(runs[0]["full"])
    reprop_fields = list(runs[0]["reprop_axe"])
    full = {
        field: np.mean([
            np.asarray(run["full"][field], dtype=float) for run in runs
        ], axis=0).tolist()
        for field in full_fields
    }
    reprop = {
        field: np.mean([
            np.asarray(run["reprop_axe"][field], dtype=float) for run in runs
        ], axis=0).tolist()
        for field in reprop_fields
    }
    hop_times = np.concatenate([
        np.asarray(run["full_hop_time_fs"], dtype=float) for run in runs
    ])
    comparison = trajectory_comparison_summary(
        time_fs, full, reprop, hop_times
    )
    scalar_comparison_keys = [
        "coherence_lifetime_fs",
        "early_hop_fraction",
        "max_upper_population_error",
        "max_product_probability_error",
        "max_centroid_x_error_sigma",
    ]
    replicate_statistics = {
        key: mean_ci95([run["comparison"][key] for run in runs])
        for key in scalar_comparison_keys
    }
    diagnostics = {
        "maximum_over_replicates": {
            key: float(max(run["diagnostics"][key] for run in runs))
            for key in runs[0]["diagnostics"]
            if key.startswith("max_") or key.endswith("_max_hartree")
        },
        "successful_full_hops": int(sum(
            run["comparison"]["successful_full_hops"] for run in runs
        )),
        "successful_axe_hops": int(sum(
            run["diagnostics"]["successful_axe_hops"] for run in runs
        )),
    }
    return {
        "configuration": runs[0]["configuration"],
        "seeds": [run["configuration"]["seed"] for run in runs],
        "replicate_count": len(runs),
        "time_fs": time_fs.tolist(),
        "full": full,
        "reprop_axe": reprop,
        "comparison_of_replicate_means": comparison,
        "replicate_statistics": replicate_statistics,
        "diagnostics": diagnostics,
    }


def rank_values(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    index = 0
    while index < values.size:
        end = index + 1
        while end < values.size and values[order[end]] == values[order[index]]:
            end += 1
        ranks[order[index:end]] = 0.5 * (index + end - 1) + 1.0
        index = end
    return ranks


def spearman_correlation(x: list[float], y: list[float]) -> float:
    x_array = np.asarray(x, dtype=float)
    y_array = np.asarray(y, dtype=float)
    finite = np.isfinite(x_array) & np.isfinite(y_array)
    if np.sum(finite) < 3:
        return float("nan")
    x_rank = rank_values(x_array[finite])
    y_rank = rank_values(y_array[finite])
    if np.std(x_rank) == 0.0 or np.std(y_rank) == 0.0:
        return float("nan")
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


def regime_key(configuration: dict) -> str:
    return (
        f"center={configuration['center_fraction']:.6g};"
        f"kick={configuration['momentum_kick_toward_ci_sigma_px']:.6g}"
    )


def aggregate_sweep_runs(runs: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for run in runs:
        groups.setdefault(regime_key(run["configuration"]), []).append(run)
    aggregates = [aggregate_regime_runs(group) for group in groups.values()]
    aggregates.sort(key=lambda item: (
        item["configuration"]["momentum_kick_toward_ci_sigma_px"] > 0.0,
        -item["configuration"]["center_fraction"],
        item["configuration"]["momentum_kick_toward_ci_sigma_px"],
    ))

    for aggregate in aggregates:
        configuration = aggregate["configuration"]
        aggregate["stage"] = (
            "original_center_sweep"
            if configuration["momentum_kick_toward_ci_sigma_px"] == 0.0
            else "adaptive_directional_kick"
        )

    stage_analysis = {}
    for stage in ("original_center_sweep", "adaptive_directional_kick"):
        if stage == "adaptive_directional_kick":
            selected = [
                item for item in aggregates
                if item["configuration"]["center_fraction"] == 0.5
            ]
        else:
            selected = [item for item in aggregates if item["stage"] == stage]
        early = [
            item["comparison_of_replicate_means"]["early_hop_fraction"]
            for item in selected
        ]
        errors = {
            "max_upper_population_error": [
                item["comparison_of_replicate_means"]["max_upper_population_error"]
                for item in selected
            ],
            "max_product_probability_error": [
                item["comparison_of_replicate_means"]["max_product_probability_error"]
                for item in selected
            ],
            "max_centroid_x_error_sigma": [
                item["comparison_of_replicate_means"]["max_centroid_x_error_sigma"]
                for item in selected
            ],
        }
        correlations = {
            name: spearman_correlation(early, values)
            for name, values in errors.items()
        }
        early_regimes = []
        for item in selected:
            comparison = item["comparison_of_replicate_means"]
            if comparison["early_hop_fraction"] >= 0.5:
                early_regimes.append({
                    "regime": regime_key(item["configuration"]),
                    "early_hop_fraction": comparison["early_hop_fraction"],
                    "robust_under_declared_thresholds": (
                        comparison["max_upper_population_error"] <= 0.05
                        and comparison["max_product_probability_error"] <= 0.05
                        and comparison["max_centroid_x_error_sigma"] <= 0.1
                    ),
                })
        stage_analysis[stage] = {
            "regime_count": len(selected),
            "spearman_early_hops_vs_errors": correlations,
            "early_hop_regime_reached": bool(early_regimes),
            "early_hop_regimes": early_regimes,
        }
    return {
        "regimes": aggregates,
        "stage_analysis": stage_analysis,
    }


def declared_sweep_jobs() -> list[dict]:
    jobs = []
    for center_fraction in (1.0, 0.75, 0.5, 0.25, 0.0):
        for seed in (1701, 1702, 1703, 1704):
            jobs.append({
                "center_fraction": center_fraction,
                "momentum_kick_sigma": 0.0,
                "seed": seed,
            })
    # The zero-kick adaptive point is identical to center=0.5 above.
    for kick in (0.5, 1.0, 1.5, 2.0):
        for seed in (1701, 1702, 1703, 1704):
            jobs.append({
                "center_fraction": 0.5,
                "momentum_kick_sigma": kick,
                "seed": seed,
            })
    return jobs


def run_declared_sweep(
    output: Path,
    workers: int = 1,
    progress: bool = False,
) -> dict:
    """Run or resume the 36 final replicates, checkpointing every result."""

    if output.exists():
        with output.open(encoding="utf-8") as handle:
            result = json.load(handle)
        runs = result.get("runs", [])
    else:
        runs = []
    completed = {
        (
            run["configuration"]["center_fraction"],
            run["configuration"]["momentum_kick_toward_ci_sigma_px"],
            run["configuration"]["seed"],
        )
        for run in runs
    }
    pending = [
        job for job in declared_sweep_jobs()
        if (
            job["center_fraction"],
            job["momentum_kick_sigma"],
            job["seed"],
        ) not in completed
    ]
    common = {
        "geometry_count": 4000,
        "dt_fs": 0.025,
        "electronic_substeps": 10,
        "total_fs": 20.0,
        "progress": progress and workers == 1,
    }

    def checkpoint() -> None:
        snapshot = {
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            "declared_replicates": len(declared_sweep_jobs()),
            "completed_replicates": len(runs),
            "complete": len(runs) == len(declared_sweep_jobs()),
            "runs": runs,
            "aggregate": aggregate_sweep_runs(runs) if runs else None,
        }
        write_json(output, snapshot)

    if workers == 1:
        for job in pending:
            run = run_trajectory_regime(**job, **common)
            runs.append(run)
            print(
                f"completed {len(runs)}/{len(declared_sweep_jobs())}: "
                f"{regime_key(run['configuration'])} seed={job['seed']}",
                flush=True,
            )
            checkpoint()
    else:
        # NumPy releases the GIL in the vector kernels that dominate these
        # runs.  A thread pool also works in restricted environments where
        # ProcessPoolExecutor cannot query or allocate POSIX semaphores.
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(run_trajectory_regime, **job, **common): job
                for job in pending
            }
            for future in concurrent.futures.as_completed(futures):
                job = futures[future]
                run = future.result()
                runs.append(run)
                print(
                    f"completed {len(runs)}/{len(declared_sweep_jobs())}: "
                    f"{regime_key(run['configuration'])} seed={job['seed']}",
                    flush=True,
                )
                checkpoint()
    checkpoint()
    with output.open(encoding="utf-8") as handle:
        return json.load(handle)


def exact_regime_specifications() -> list[dict]:
    specifications = [
        {"center_fraction": center, "momentum_kick_sigma": 0.0}
        for center in (1.0, 0.75, 0.5, 0.25, 0.0)
    ]
    specifications.extend([
        {"center_fraction": 0.5, "momentum_kick_sigma": kick}
        for kick in (0.5, 1.0, 1.5, 2.0)
    ])
    return specifications


def run_exact_regime_references(output: Path, progress: bool = False) -> dict:
    """Exact 2D quantum references for every final trajectory regime."""

    if output.exists():
        with output.open(encoding="utf-8") as handle:
            result = json.load(handle)
        runs = result.get("runs", [])
    else:
        runs = []
    completed = {
        (
            run["regime"]["center_fraction"],
            run["regime"]["momentum_kick_sigma"],
        )
        for run in runs
    }
    sigma_px = math.sqrt(BMA_MODEL.omega_x / 2.0)
    for specification in exact_regime_specifications():
        key = (
            specification["center_fraction"],
            specification["momentum_kick_sigma"],
        )
        if key in completed:
            continue
        exact = run_bma_exact(
            grid_n=384,
            half_width=96.0,
            dt_fs=0.025,
            total_fs=20.0,
            sample_every_fs=0.025,
            qbar_x=specification["center_fraction"] * BMA_MODEL.qbar_x,
            mean_momentum_x=-specification["momentum_kick_sigma"] * sigma_px,
            progress=progress,
        )
        runs.append({"regime": specification, "exact": exact})
        snapshot = {
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            "grid_convergence_source": "downloads/pulse_ci_baseline.json",
            "configuration_note": (
                "384x384, 0.025 fs references; the published-center baseline "
                "bounds its 512x512 product-side difference by 0.001."
            ),
            "completed_regimes": len(runs),
            "complete": len(runs) == len(exact_regime_specifications()),
            "runs": runs,
        }
        write_json(output, snapshot)
        print(
            f"exact regime {len(runs)}/{len(exact_regime_specifications())}: "
            f"center={key[0]:g};kick={key[1]:g}",
            flush=True,
        )
    with output.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_exact_reference_spot_checks(
    reference_path: Path,
    output: Path,
    progress: bool = False,
) -> dict:
    """Recheck the two most displaced production references on a finer grid."""

    with reference_path.open(encoding="utf-8") as handle:
        reference_data = json.load(handle)
    references = {
        (
            run["regime"]["center_fraction"],
            run["regime"]["momentum_kick_sigma"],
        ): run["exact"]
        for run in reference_data["runs"]
    }
    sigma_px = math.sqrt(BMA_MODEL.omega_x / 2.0)
    field_scales = {
        "upper_population": 1.0,
        "product_qx_lt_0": 1.0,
        "centroid_x": BMA_MODEL.initial_sigma_x,
    }
    runs = []
    for center_fraction, momentum_kick_sigma in ((0.0, 0.0), (0.5, 2.0)):
        fine = run_bma_exact(
            grid_n=512,
            half_width=96.0,
            dt_fs=0.025,
            total_fs=20.0,
            sample_every_fs=0.025,
            qbar_x=center_fraction * BMA_MODEL.qbar_x,
            mean_momentum_x=-momentum_kick_sigma * sigma_px,
            progress=progress,
        )
        reference = references[(center_fraction, momentum_kick_sigma)]
        reference_time = np.asarray(reference["time_fs"])
        fine_time = np.asarray(fine["time_fs"])
        differences = {}
        for field, scale in field_scales.items():
            reference_values = np.interp(
                fine_time, reference_time, np.asarray(reference[field])
            )
            raw_difference = float(np.max(np.abs(
                np.asarray(fine[field]) - reference_values
            )))
            differences[field] = {
                "raw": raw_difference,
                "scaled": raw_difference / scale,
                "scale": (
                    "probability" if scale == 1.0 else "initial_sigma_x"
                ),
            }
        runs.append({
            "regime": {
                "center_fraction": center_fraction,
                "momentum_kick_sigma": momentum_kick_sigma,
            },
            "coarse_grid_n": reference["configuration"]["grid_n"],
            "fine_configuration": fine["configuration"],
            "fine_runtime_seconds": fine["runtime_seconds"],
            "fine_max_norm_error": float(np.max(np.abs(
                np.asarray(fine["norm"]) - 1.0
            ))),
            "maximum_time_series_differences": differences,
        })
    result = {
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "status": "post hoc grid audit performed during drafting",
        "reference_path": str(reference_path),
        "runs": runs,
    }
    write_json(output, result)
    return result


def compare_trajectory_settings(coarse: dict, fine: dict) -> dict:
    coarse_time = np.asarray(coarse["time_fs"])
    fine_time = np.asarray(fine["time_fs"])
    field_scales = {
        "upper_population": 1.0,
        "product_qx_lt_0": 1.0,
        "centroid_x": BMA_MODEL.initial_sigma_x,
    }
    methods = {}
    for method in ("full", "reprop_axe"):
        methods[method] = {}
        for field, scale in field_scales.items():
            coarse_values = np.asarray(coarse[method][field])
            fine_values = np.interp(
                coarse_time, fine_time, np.asarray(fine[method][field])
            )
            methods[method][field] = float(
                np.max(np.abs(coarse_values - fine_values)) / scale
            )
    summary_differences = {
        key: float(abs(
            coarse["comparison"][key] - fine["comparison"][key]
        ))
        for key in (
            "max_upper_population_error",
            "max_product_probability_error",
            "max_centroid_x_error_sigma",
        )
    }
    gate = {
        "full_population_below_0_02":
            methods["full"]["upper_population"] < 0.02,
        "full_product_below_0_02":
            methods["full"]["product_qx_lt_0"] < 0.02,
        "full_centroid_below_0_03_sigma":
            methods["full"]["centroid_x"] < 0.03,
    }
    gate["passed"] = all(gate.values())
    return {
        "maximum_time_series_differences": methods,
        "maximum_error_summary_differences": summary_differences,
        "gate": gate,
        "decision": (
            "use 0.025 fs and ten electronic substeps for all final runs"
            if not gate["passed"]
            else "coarse setting accepted"
        ),
    }


def run_trajectory_convergence(output: Path, progress: bool = False) -> dict:
    coarse = run_trajectory_regime(
        center_fraction=0.25,
        seed=1701,
        geometry_count=4000,
        dt_fs=0.05,
        electronic_substeps=5,
        total_fs=20.0,
        progress=progress,
    )
    fine = run_trajectory_regime(
        center_fraction=0.25,
        seed=1701,
        geometry_count=4000,
        dt_fs=0.025,
        electronic_substeps=10,
        total_fs=20.0,
        progress=progress,
    )
    result = {
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "coarse": coarse,
        "fine": fine,
        "comparison": compare_trajectory_settings(coarse, fine),
    }
    write_json(output, result)
    return result


def downsample_density_result(result: dict, q_points: int = 512) -> dict:
    """Reduce JSON size while preserving the density integral and topology."""

    q = np.asarray(result["q"])
    density = np.asarray(result["density"])
    if q.size <= q_points:
        return result
    factor = q.size // q_points
    usable = factor * q_points
    q_small = q[:usable].reshape(q_points, factor).mean(axis=1)
    density_small = density[:, :usable].reshape(density.shape[0], q_points, factor).mean(axis=2)
    compact = dict(result)
    compact["q"] = q_small.tolist()
    compact["density"] = density_small.astype(np.float32).tolist()
    compact["stored_grid_note"] = (
        f"Density block-averaged from {q.size} to {q_points} q points; "
        "reported scalar observables use the full grid."
    )
    return compact


def convergence_difference(a: dict, b: dict, fields: list[str]) -> dict:
    """Maximum paired difference after interpolating b onto a's time grid."""

    ta = np.asarray(a["time_fs"])
    tb = np.asarray(b["time_fs"])
    output = {}
    for field in fields:
        va = np.asarray(a[field])
        vb = np.interp(ta, tb, np.asarray(b[field]))
        output[field] = float(np.max(np.abs(va - vb)))
    return output


def run_baseline(quick: bool = False, progress: bool = False) -> dict:
    """Run the preregistered published-model gate and convergence checks."""

    if quick:
        bma_configs = [(192, 80.0, 0.05), (256, 96.0, 0.05)]
        oned_configs = [(1024, 8.0, 0.10), (2048, 8.0, 0.10)]
    else:
        bma_configs = [
            (256, 96.0, 0.05),
            (384, 96.0, 0.05),
            (384, 96.0, 0.025),
            (512, 96.0, 0.025),
        ]
        oned_configs = [
            (2048, 8.0, 0.10),
            (2048, 8.0, 0.05),
            (4096, 8.0, 0.05),
        ]

    bma_runs = []
    for grid_n, half_width, dt_fs in bma_configs:
        bma_runs.append(run_bma_exact(
            grid_n=grid_n,
            half_width=half_width,
            dt_fs=dt_fs,
            progress=progress,
        ))
    oned_runs = []
    for grid_n, half_width, dt_fs in oned_configs:
        oned_runs.append(run_oned_exact(
            grid_n=grid_n,
            half_width=half_width,
            dt_fs=dt_fs,
            progress=progress,
        ))

    bma_finest = bma_runs[-1]
    oned_finest = oned_runs[-1]
    bma_conv = [
        convergence_difference(
            run, bma_finest,
            ["upper_population", "centroid_x", "product_qx_lt_0"],
        )
        for run in bma_runs[:-1]
    ]
    oned_conv = [
        convergence_difference(
            run, oned_finest,
            ["upper_population", "stationary_q_lt_minus_1_5", "moving_q_gt_minus_1"],
        )
        for run in oned_runs[:-1]
    ]

    gate = {
        "bma_figure6_rmse_below_0_01":
            bma_finest["figure6_comparison"]["rmse"] < 0.01,
        "bma_figure6_max_abs_below_0_025":
            bma_finest["figure6_comparison"]["max_abs"] < 0.025,
        "bma_norm_drift_below_1e_9":
            max(abs(np.asarray(bma_finest["norm"]) - 1.0)) < 1e-9,
        "bma_finest_pair_population_diff_below_0_002":
            bma_conv[-1]["upper_population"] < 0.002,
        "bma_finest_pair_product_diff_below_0_002":
            bma_conv[-1]["product_qx_lt_0"] < 0.002,
        "oned_norm_drift_below_1e_9":
            max(abs(np.asarray(oned_finest["norm"]) - 1.0)) < 1e-9,
        "oned_finest_pair_branch_diff_below_0_002":
            max(
                oned_conv[-1]["stationary_q_lt_minus_1_5"],
                oned_conv[-1]["moving_q_gt_minus_1"],
            ) < 0.002,
    }
    gate["passed"] = all(gate.values())

    return {
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "quick": quick,
        "bma_runs": bma_runs,
        "bma_convergence_vs_finest": bma_conv,
        "oned_runs": [downsample_density_result(run) for run in oned_runs],
        "oned_convergence_vs_finest": oned_conv,
        "gate": gate,
    }


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Cannot serialize {type(value)}")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=json_default)
        handle.write("\n")
    os.replace(temporary, path)


def print_baseline_summary(result: dict) -> None:
    finest = result["bma_runs"][-1]
    comparison = finest["figure6_comparison"]
    print("\nPublished-model gate")
    print(f"  BMA Figure 6 RMSE:   {comparison['rmse']:.6f}")
    print(f"  BMA Figure 6 max |e|:{comparison['max_abs']:.6f}")
    for index, difference in enumerate(result["bma_convergence_vs_finest"]):
        print(f"  BMA run {index} vs finest: {difference}")
    for index, difference in enumerate(result["oned_convergence_vs_finest"]):
        print(f"  1D run {index} vs finest:  {difference}")
    for name, passed in result["gate"].items():
        print(f"  {name}: {passed}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    baseline = subparsers.add_parser("baseline", help="run exact-model gate")
    baseline.add_argument("--quick", action="store_true", help="small development run")
    baseline.add_argument("--progress", action="store_true")
    baseline.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_baseline.json"),
    )
    regime = subparsers.add_parser("regime", help="run one FP/RP-AXE replicate")
    regime.add_argument("--center", type=float, default=0.25)
    regime.add_argument("--seed", type=int, default=1701)
    regime.add_argument("--geometries", type=int, default=4000)
    regime.add_argument("--dt-fs", type=float, default=0.05)
    regime.add_argument("--electronic-substeps", type=int, default=5)
    regime.add_argument("--total-fs", type=float, default=20.0)
    regime.add_argument(
        "--kick-sigma",
        type=float,
        default=0.0,
        help="mean negative x momentum in units of the Wigner sigma",
    )
    regime.add_argument("--progress", action="store_true")
    regime.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_regime.json"),
    )
    sweep = subparsers.add_parser("sweep", help="run or resume the declared final sweep")
    sweep.add_argument("--workers", type=int, default=1)
    sweep.add_argument("--progress", action="store_true")
    sweep.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_sweep.json"),
    )
    exact_regimes = subparsers.add_parser(
        "exact-regimes", help="run exact quantum references for sweep regimes"
    )
    exact_regimes.add_argument("--progress", action="store_true")
    exact_regimes.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_exact_regimes.json"),
    )
    exact_spot_checks = subparsers.add_parser(
        "exact-spot-checks",
        help="rerun two displaced exact references on a 512x512 grid",
    )
    exact_spot_checks.add_argument("--progress", action="store_true")
    exact_spot_checks.add_argument(
        "--reference",
        type=Path,
        default=Path("downloads/pulse_ci_exact_regimes.json"),
    )
    exact_spot_checks.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_exact_spot_checks.json"),
    )
    convergence = subparsers.add_parser(
        "convergence", help="rerun the declared trajectory time-step gate"
    )
    convergence.add_argument("--progress", action="store_true")
    convergence.add_argument(
        "--output",
        type=Path,
        default=Path("downloads/pulse_ci_convergence.json"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(
        f"env: Python {platform.python_version()} {platform.machine()} "
        f"| NumPy {np.__version__}",
        flush=True,
    )
    if args.command == "baseline":
        result = run_baseline(quick=args.quick, progress=args.progress)
        write_json(args.output, result)
        print_baseline_summary(result)
        print(f"wrote {args.output}")
        return 0 if result["gate"]["passed"] else 2
    if args.command == "regime":
        result = run_trajectory_regime(
            center_fraction=args.center,
            seed=args.seed,
            geometry_count=args.geometries,
            dt_fs=args.dt_fs,
            electronic_substeps=args.electronic_substeps,
            total_fs=args.total_fs,
            momentum_kick_sigma=args.kick_sigma,
            progress=args.progress,
        )
        write_json(args.output, result)
        comparison_for_print = {
            key: value for key, value in result["comparison"].items()
            if not key.endswith("_series")
        }
        print(json.dumps(comparison_for_print, indent=2))
        print(json.dumps(result["diagnostics"], indent=2))
        print(f"wrote {args.output}")
        return 0
    if args.command == "sweep":
        result = run_declared_sweep(
            output=args.output,
            workers=args.workers,
            progress=args.progress,
        )
        print(json.dumps(result["aggregate"]["stage_analysis"], indent=2))
        print(f"wrote {args.output}")
        return 0 if result["complete"] else 2
    if args.command == "exact-regimes":
        result = run_exact_regime_references(args.output, progress=args.progress)
        print(f"wrote {args.output}")
        return 0 if result["complete"] else 2
    if args.command == "exact-spot-checks":
        result = run_exact_reference_spot_checks(
            reference_path=args.reference,
            output=args.output,
            progress=args.progress,
        )
        print(json.dumps(result, indent=2))
        print(f"wrote {args.output}")
        return 0
    if args.command == "convergence":
        result = run_trajectory_convergence(args.output, progress=args.progress)
        print(json.dumps(result["comparison"], indent=2))
        print(f"wrote {args.output}")
        # A failed coarse-setting gate is an expected decision, not a failed
        # experiment: the fine setting is then used for the final data.
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
