"""Frozen coherence-versus-hop-boundary experiment.

This is a parameter-safe derivative of ``downloads/pulse-independent-ci.py``.
The BMA Hamiltonian and launch are invariant.  The algorithmic stress dial
``pfm_rate_scale`` is passed explicitly through every PFM, electronic, and
ensemble propagation layer and is never stored in mutable module state.

All model equations use atomic units.  Command-line times are femtoseconds.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


AU_TO_FS = 0.024188843265857
FS_TO_AU = 1.0 / AU_TO_FS
PFM_POPULATION_THRESHOLD = 1e-4
FROZEN_PYTHON_VERSION = "3.12.9"
FROZEN_NUMPY_VERSION = "2.2.5"
ENVIRONMENT_FINGERPRINT_SCHEMA_VERSION = 2

FINAL_SCALES = (1.0, 0.5, 0.25, 0.125, 0.10, 0.075, 0.05)
FINAL_SEEDS = (2701, 2702, 2703, 2704)
FINAL_GEOMETRY_COUNT = 4000
FINAL_CENTER_FRACTION = 0.5
FINAL_MOMENTUM_KICK_SIGMA = 0.0
FINAL_TOTAL_FS = 20.0
COARSE_DT_FS = 0.025
COARSE_SUBSTEPS = 10
FINE_DT_FS = 0.0125
FINE_SUBSTEPS = 20
FINER_DT_FS = 0.00625
FINER_SUBSTEPS = 40
CONVERGENCE_SEEDS = (2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694)
LINEAGE_SEED = 2698
LINEAGE_GEOMETRY_COUNT = 64
LINEAGE_DT_FS = 0.05
LINEAGE_ELECTRONIC_SUBSTEPS = 5
LINEAGE_TOTAL_FS = 0.5
EXPECTED_LEGACY_SOURCE_SHA256 = (
    "9a62440a32f99057f699ec9de8c58fc2a19e0bf78f0848fd8826d1b23aa72350"
)
EXPECTED_LEGACY_ARCHIVE_SHA256 = (
    "eb8a7ed3e13c0c02a6872da57f23317a541c764d44f060902b0874b8e99e29d0"
)

TRAJECTORY_GATE_LIMITS = {
    "accepted_event_fraction": 0.02,
    "coherence_lifetime_fs": 0.15,
    "upper_population": 0.02,
    "product_qx_lt_0": 0.02,
    "centroid_x_sigma": 0.03,
}
EXACT_GATE_LIMITS = {
    "upper_population": 2e-4,
    "product_qx_lt_0": 0.005,
    "centroid_x_sigma": 0.01,
    "fine_norm_error": 1e-10,
}
ERROR_THRESHOLDS = {
    "max_upper_population_error": 0.05,
    "max_product_probability_error": 0.05,
    "max_centroid_x_error_sigma": 0.10,
}
LINEAGE_FIELDS = {
    "full": (
        "upper_population", "active_upper_fraction",
        "centroid_x", "centroid_y", "product_qx_lt_0",
        "electronic_norm_error",
    ),
    "reprop_axe": (
        "upper_population", "centroid_x",
        "centroid_y", "product_qx_lt_0", "electronic_norm_error",
        "weight_sum_per_geometry",
    ),
}
LINEAGE_COHERENCE_FIELDS = {
    "full": ("coherence_amplitude", "mean_trajectory_coherence_magnitude"),
    "reprop_axe": ("coherence_amplitude", "mean_trajectory_coherence_magnitude"),
}


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


BMA_MODEL = BMA()


def invariant_contract() -> dict[str, Any]:
    """Return the complete immutable model, launch, and algorithm contract."""

    model = asdict(BMA_MODEL)
    model.update({
        "name": "BMA two-state two-mode linear-vibronic-coupling model",
        "units": "atomic_units",
        "nuclear_masses_electron_mass": [1.0, 1.0],
        "qbar_x": BMA_MODEL.qbar_x,
        "initial_sigma_x": BMA_MODEL.initial_sigma_x,
        "initial_sigma_y": BMA_MODEL.initial_sigma_y,
    })
    return {
        "contract_version": 1,
        "model": model,
        "launch": {
            "center_fraction": FINAL_CENTER_FRACTION,
            "center_x": FINAL_CENTER_FRACTION * BMA_MODEL.qbar_x,
            "center_y": 0.0,
            "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
            "mean_momentum_x": 0.0,
            "electronic_basis": "diabatic_(psi_1,psi_2)",
            "delta_p": BMA_MODEL.delta_p,
            "diabatic_amplitudes": [
                math.sqrt((1.0 + BMA_MODEL.delta_p) / 2.0),
                math.sqrt((1.0 - BMA_MODEL.delta_p) / 2.0),
            ],
            "nuclear_distribution": "product_ground_state_Wigner",
        },
        "trajectory_algorithm": {
            "name": "FP_and_online_RP-AXE_PFMi",
            "nuclear_integrator": "velocity_Verlet",
            "electronic_integrator": "analytic_midpoint_two_state",
            "hop_rule": "two_state_density_flux_isotropic_energy_rescaling",
            "pfm_rate_equation": "Grell_et_al_2025_equation_43",
            "pfm_omega": math.sqrt(BMA_MODEL.omega_x * BMA_MODEL.omega_y),
            "pfm_population_threshold": PFM_POPULATION_THRESHOLD,
            "rng": "numpy_PCG64_default_rng",
            "rng_streams": {
                "initial": "seed",
                "full": "100000+seed",
                "axe": "200000+seed",
            },
        },
        "exact_algorithm": {
            "name": "second_order_split_operator_Fourier_grid",
            "half_width": 96.0,
            "dt_fs": COARSE_DT_FS,
            "sample_every_fs": COARSE_DT_FS,
            "total_fs": FINAL_TOTAL_FS,
        },
    }


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)


MODEL_FINGERPRINT = hashlib.sha256(
    canonical_json(invariant_contract()).encode("utf-8")
).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def runtime_fingerprints() -> dict[str, str]:
    """Bind artifacts to the exact simulator and frozen config bytes."""

    source_path = Path(__file__).resolve()
    config_path = source_path.parents[1] / "config.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"frozen experiment config missing: {config_path}")
    environment_fingerprint = hashlib.sha256(
        canonical_json(environment_record()).encode("utf-8")
    ).hexdigest()
    return {
        "model_fingerprint": MODEL_FINGERPRINT,
        "simulator_sha256": sha256_file(source_path),
        "config_sha256": sha256_file(config_path),
        "environment_fingerprint": environment_fingerprint,
    }


def environment_record() -> dict[str, str | int]:
    """Return the versioned, declared numerical execution boundary.

    Kernel releases and libc build strings are host provenance, not frozen
    numerical controls.  Including ``platform.platform()`` here made resume
    identities differ across otherwise conforming Linux x86-64 hosts.
    ``require_frozen_environment`` checks these declared values before any CLI
    run; the record is also kept in each artifact so its fingerprint remains
    independently auditable.
    """

    return {
        "schema_version": ENVIRONMENT_FINGERPRINT_SCHEMA_VERSION,
        "python_implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "operating_system": platform.system(),
        "machine": platform.machine(),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS", ""),
    }


def require_frozen_environment() -> None:
    checks = {
        "Python implementation": (platform.python_implementation(), "CPython"),
        "Python": (platform.python_version(), FROZEN_PYTHON_VERSION),
        "NumPy": (np.__version__, FROZEN_NUMPY_VERSION),
        "operating system": (platform.system(), "Linux"),
        "machine": (platform.machine(), "x86_64"),
        "OPENBLAS_NUM_THREADS": (os.environ.get("OPENBLAS_NUM_THREADS"), "1"),
    }
    failures = [
        f"{name}={actual!r} (required {expected!r})"
        for name, (actual, expected) in checks.items()
        if actual != expected
    ]
    if failures:
        raise RuntimeError("frozen environment mismatch: " + "; ".join(failures))


def validate_scale(pfm_rate_scale: float) -> float:
    scale = float(pfm_rate_scale)
    if not math.isfinite(scale) or scale < 0.0:
        raise ValueError("pfm_rate_scale must be finite and nonnegative")
    return scale


def make_resume_identity(
    *,
    pfm_rate_scale: float,
    seed: int,
    geometry_count: int,
    dt_fs: float,
    electronic_substeps: int,
    total_fs: float,
    model_fingerprint: str = MODEL_FINGERPRINT,
    simulator_sha256: str | None = None,
    config_sha256: str | None = None,
    environment_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Return every control that makes a trajectory result reusable."""

    steps = int(round(float(total_fs) / float(dt_fs)))
    if steps <= 0 or electronic_substeps <= 0 or geometry_count <= 0:
        raise ValueError("geometry count, time steps, and substeps must be positive")
    actual_dt_fs = float(total_fs) / steps
    fingerprints = runtime_fingerprints()
    simulator_sha256 = (
        fingerprints["simulator_sha256"]
        if simulator_sha256 is None else str(simulator_sha256)
    )
    config_sha256 = (
        fingerprints["config_sha256"]
        if config_sha256 is None else str(config_sha256)
    )
    environment_fingerprint = (
        fingerprints["environment_fingerprint"]
        if environment_fingerprint is None else str(environment_fingerprint)
    )
    return {
        "pfm_rate_scale": validate_scale(pfm_rate_scale),
        "seed": int(seed),
        "geometry_count": int(geometry_count),
        "requested_dt_fs": float(dt_fs),
        "actual_dt_fs": actual_dt_fs,
        "electronic_substeps": int(electronic_substeps),
        "electronic_dt_fs": actual_dt_fs / int(electronic_substeps),
        "total_fs": float(total_fs),
        "center_fraction": FINAL_CENTER_FRACTION,
        "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
        "model_fingerprint": str(model_fingerprint),
        "simulator_sha256": simulator_sha256,
        "config_sha256": config_sha256,
        "environment_fingerprint": environment_fingerprint,
    }


def make_resume_key(**controls: Any) -> str:
    identity = make_resume_identity(**controls)
    return hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()


def electronic_initial_state(delta_p: float = BMA_MODEL.delta_p) -> np.ndarray:
    return np.array([
        math.sqrt((1.0 + delta_p) / 2.0),
        math.sqrt((1.0 - delta_p) / 2.0),
    ], dtype=np.complex128)


def bma_potential(qx: np.ndarray, qy: np.ndarray):
    model = BMA_MODEL
    vbar = 0.5 * (model.omega_x**2 * qx**2 + model.omega_y**2 * qy**2)
    delta = model.c * qy
    kappa = 0.5 * model.omega_x**2 * model.a * qx
    return vbar, delta, kappa


def apply_two_state_potential(
    psi: np.ndarray,
    vbar: np.ndarray,
    delta: np.ndarray,
    kappa: np.ndarray,
    tau: float,
) -> None:
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


def normalized_wavefunction(psi: np.ndarray, volume_element: float) -> np.ndarray:
    norm = math.sqrt(float(np.sum(np.abs(psi) ** 2) * volume_element))
    return psi / norm


def exact_observables(
    psi: np.ndarray,
    qx: np.ndarray,
    qy: np.ndarray,
    delta: np.ndarray,
    kappa: np.ndarray,
    volume_element: float,
) -> dict[str, float]:
    density = np.abs(psi[0]) ** 2 + np.abs(psi[1]) ** 2
    radius = np.hypot(delta, kappa)
    b_expect = (
        kappa * (np.abs(psi[1]) ** 2 - np.abs(psi[0]) ** 2)
        + 2.0 * delta * np.real(np.conj(psi[0]) * psi[1])
    )
    projected = np.zeros_like(density)
    np.divide(b_expect, radius, out=projected, where=radius > 1e-14)
    upper = float(np.sum(0.5 * (density + projected)) * volume_element)
    theta = np.arctan2(delta, kappa)
    cosine = np.cos(0.5 * theta)
    sine = np.sin(0.5 * theta)
    lower = cosine * psi[0] - sine * psi[1]
    upper_amplitude = sine * psi[0] + cosine * psi[1]
    local_density_matrix = np.conj(lower) * upper_amplitude
    ensemble_density_matrix = np.sum(local_density_matrix) * volume_element
    coherence_real = float(2.0 * np.real(ensemble_density_matrix))
    coherence_imag = float(2.0 * np.imag(ensemble_density_matrix))
    return {
        "upper_population": upper,
        "ensemble_coherence_real": coherence_real,
        "ensemble_coherence_imag": coherence_imag,
        "coherence_amplitude": math.hypot(coherence_real, coherence_imag),
        "mean_trajectory_coherence_magnitude": float(
            np.sum(2.0 * np.abs(local_density_matrix)) * volume_element
        ),
        "centroid_x": float(np.sum(qx * density) * volume_element),
        "centroid_y": float(np.sum(qy * density) * volume_element),
        "product_qx_lt_0": float(np.sum(density[qx < 0.0]) * volume_element),
        "norm": float(np.sum(density) * volume_element),
    }


def run_bma_exact(
    *,
    grid_n: int,
    half_width: float = 96.0,
    dt_fs: float = COARSE_DT_FS,
    total_fs: float = FINAL_TOTAL_FS,
    sample_every_fs: float = COARSE_DT_FS,
    progress: bool = False,
) -> dict[str, Any]:
    """Propagate the invariant BMA launch on a periodic square Fourier grid."""

    x = np.linspace(-half_width, half_width, grid_n, endpoint=False)
    dx = float(x[1] - x[0])
    qx, qy = np.meshgrid(x, x, indexing="ij")
    vbar, delta, kappa = bma_potential(qx, qy)
    qbar_x = FINAL_CENTER_FRACTION * BMA_MODEL.qbar_x
    nuclear = np.exp(
        -0.5 * BMA_MODEL.omega_x * (qx - qbar_x) ** 2
        -0.5 * BMA_MODEL.omega_y * qy**2
    ).astype(np.complex128)
    psi = electronic_initial_state()[:, None, None] * nuclear[None, :, :]
    psi = normalized_wavefunction(psi, dx * dx)

    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps
    dt = actual_dt_fs * FS_TO_AU
    sample_stride = max(1, int(round(sample_every_fs / actual_dt_fs)))
    kgrid = 2.0 * np.pi * np.fft.fftfreq(grid_n, d=dx)
    kx, ky = np.meshgrid(kgrid, kgrid, indexing="ij")
    kinetic = np.exp(-0.5j * (kx**2 + ky**2) * dt)[None, :, :]
    time_fs: list[float] = []
    observations: dict[str, list[float]] = {}

    def observe(step: int) -> None:
        time_fs.append(step * actual_dt_fs)
        values = exact_observables(psi, qx, qy, delta, kappa, dx * dx)
        for name, value in values.items():
            observations.setdefault(name, []).append(value)

    observe(0)
    for step in range(1, steps + 1):
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        apply_kinetic(psi, kinetic)
        apply_two_state_potential(psi, vbar, delta, kappa, 0.5 * dt)
        if step % sample_stride == 0 or step == steps:
            observe(step)
        if progress and (step % max(1, steps // 10) == 0 or step == steps):
            print(f"exact {grid_n}^2: {step}/{steps}", flush=True)

    configuration = {
        **runtime_fingerprints(),
        "model_contract": invariant_contract(),
        "grid_n": int(grid_n),
        "half_width": float(half_width),
        "dx": dx,
        "requested_dt_fs": float(dt_fs),
        "actual_dt_fs": actual_dt_fs,
        "sample_every_fs": sample_stride * actual_dt_fs,
        "total_fs": float(total_fs),
        "center_fraction": FINAL_CENTER_FRACTION,
        "center_x": qbar_x,
        "momentum_kick_toward_ci_sigma_px": 0.0,
        "mean_momentum_x": 0.0,
        "initial_sigma_x": BMA_MODEL.initial_sigma_x,
    }
    return {
        "configuration": configuration,
        "time_fs": time_fs,
        **observations,
    }


def bma_adiabatic_quantities(q: np.ndarray):
    qx = q[:, 0]
    qy = q[:, 1]
    vbar, delta, kappa = bma_potential(qx, qy)
    radius = np.hypot(delta, kappa)
    energies = np.column_stack((vbar - radius, vbar + radius))
    grad_vbar_x = BMA_MODEL.omega_x**2 * qx
    grad_vbar_y = BMA_MODEL.omega_y**2 * qy
    grad_radius_x = np.zeros_like(radius)
    grad_radius_y = np.zeros_like(radius)
    nonzero = radius > 1e-12
    dkappa_dx = 0.5 * BMA_MODEL.omega_x**2 * BMA_MODEL.a
    grad_radius_x[nonzero] = kappa[nonzero] * dkappa_dx / radius[nonzero]
    grad_radius_y[nonzero] = delta[nonzero] * BMA_MODEL.c / radius[nonzero]
    lower_force = np.column_stack((
        -grad_vbar_x + grad_radius_x,
        -grad_vbar_y + grad_radius_y,
    ))
    upper_force = np.column_stack((
        -grad_vbar_x - grad_radius_x,
        -grad_vbar_y - grad_radius_y,
    ))
    return energies, np.stack((lower_force, upper_force), axis=1)


def bma_mixing(q: np.ndarray):
    _, delta, kappa = bma_potential(q[:, 0], q[:, 1])
    theta = np.arctan2(delta, kappa)
    return np.cos(0.5 * theta), np.sin(0.5 * theta)


def diabatic_to_adiabatic(c_diabatic: np.ndarray, q: np.ndarray) -> np.ndarray:
    cosine, sine = bma_mixing(q)
    return np.column_stack((
        cosine * c_diabatic[:, 0] - sine * c_diabatic[:, 1],
        sine * c_diabatic[:, 0] + cosine * c_diabatic[:, 1],
    ))


def adiabatic_to_diabatic(c_adiabatic: np.ndarray, q: np.ndarray) -> np.ndarray:
    cosine, sine = bma_mixing(q)
    return np.column_stack((
        cosine * c_adiabatic[:, 0] + sine * c_adiabatic[:, 1],
        -sine * c_adiabatic[:, 0] + cosine * c_adiabatic[:, 1],
    ))


def apply_batch_potential(c_diabatic: np.ndarray, q: np.ndarray, tau: float) -> None:
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


def pfm_rate(
    p_aux: np.ndarray,
    f_aux: np.ndarray,
    *,
    pfm_rate_scale: float,
) -> np.ndarray:
    """PFM rate with its sensitivity parameter explicit and local."""

    scale = validate_scale(pfm_rate_scale)
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
    return scale * (force_term + spreading_term)


def apply_pfm_decoherence(
    c_diabatic: np.ndarray,
    q: np.ndarray,
    active: np.ndarray,
    p_aux: np.ndarray,
    f_aux: np.ndarray,
    dt: float,
    *,
    pfm_rate_scale: float,
) -> None:
    c_ad = diabatic_to_adiabatic(c_diabatic, q)
    rows = np.arange(c_ad.shape[0])
    inactive = 1 - active
    damping = np.exp(-pfm_rate(
        p_aux, f_aux, pfm_rate_scale=pfm_rate_scale
    ) * dt)
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
    threshold: float = PFM_POPULATION_THRESHOLD,
) -> tuple[np.ndarray, np.ndarray]:
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
        0.0, 1.0 - gap[positive_kinetic] / kinetic[positive_kinetic]
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
    p_aux[rows, inactive] = np.where(above_both, propagated, born_momentum)
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


@dataclass
class HopAttempt:
    proposed: np.ndarray
    frustrated: np.ndarray
    accepted: np.ndarray
    from_state: np.ndarray


@dataclass
class HopRecorder:
    trajectory_count: int
    keep_events: bool
    initial_state: np.ndarray | None = None
    proposed_counts: np.ndarray = field(init=False)
    frustrated_counts: np.ndarray = field(init=False)
    accepted_counts: np.ndarray = field(init=False)
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.initial_state is None:
            self.initial_state = np.zeros(self.trajectory_count, dtype=np.int64)
        else:
            self.initial_state = np.asarray(self.initial_state, dtype=np.int64).copy()
            if self.initial_state.shape != (self.trajectory_count,):
                raise ValueError("initial_state must have one entry per trajectory")
            if not np.all(np.isin(self.initial_state, (0, 1))):
                raise ValueError("initial_state entries must be 0 or 1")
        self.proposed_counts = np.zeros(self.trajectory_count, dtype=np.int64)
        self.frustrated_counts = np.zeros(self.trajectory_count, dtype=np.int64)
        self.accepted_counts = np.zeros(self.trajectory_count, dtype=np.int64)

    def record(
        self,
        attempt: HopAttempt,
        *,
        time_fs: float,
        nuclear_step: int,
        electronic_substep: int,
    ) -> None:
        proposed_ids = np.flatnonzero(attempt.proposed)
        for trajectory_id in proposed_ids:
            trajectory_id = int(trajectory_id)
            accepted_before = int(self.accepted_counts[trajectory_id])
            accepted = bool(attempt.accepted[trajectory_id])
            frustrated = bool(attempt.frustrated[trajectory_id])
            from_state = int(attempt.from_state[trajectory_id])
            to_state = 1 - from_state
            self.proposed_counts[trajectory_id] += 1
            if frustrated:
                self.frustrated_counts[trajectory_id] += 1
            if accepted:
                self.accepted_counts[trajectory_id] += 1
            if self.keep_events:
                self.events.append({
                    "trajectory_id": trajectory_id,
                    "time_fs": float(time_fs),
                    "nuclear_step": int(nuclear_step),
                    "electronic_substep": int(electronic_substep),
                    "from_state": from_state,
                    "to_state": to_state,
                    "direction": (
                        "lower_to_upper" if from_state == 0 else "upper_to_lower"
                    ),
                    "outcome": "accepted" if accepted else "frustrated",
                    "proposed": True,
                    "frustrated": frustrated,
                    "accepted": accepted,
                    "accepted_hop_class": (
                        ("first" if accepted_before == 0 else "repeat")
                        if accepted else None
                    ),
                    "accepted_hops_before_event": accepted_before,
                    "recrossing": bool(
                        accepted
                        and accepted_before > 0
                        and to_state == int(self.initial_state[trajectory_id])
                    ),
                })

    def as_dict(self) -> dict[str, Any]:
        accepted_events = [event for event in self.events if event["accepted"]]
        direction_counts: dict[str, dict[str, int]] = {}
        for direction in ("lower_to_upper", "upper_to_lower"):
            selected = [event for event in self.events if event["direction"] == direction]
            direction_counts[direction] = {
                "proposed": len(selected),
                "frustrated": sum(event["frustrated"] for event in selected),
                "accepted": sum(event["accepted"] for event in selected),
            }
        return {
            "trajectory_id_definition": (
                f"zero_based_integer_in_[0,{self.trajectory_count - 1}]"
            ),
            "counts": {
                "proposed": int(np.sum(self.proposed_counts)),
                "frustrated": int(np.sum(self.frustrated_counts)),
                "accepted": int(np.sum(self.accepted_counts)),
                "accepted_first": int(np.sum(self.accepted_counts > 0)),
                "accepted_repeat": int(np.sum(np.maximum(
                    self.accepted_counts - 1, 0
                ))),
                "unique_trajectories_proposed": int(np.sum(self.proposed_counts > 0)),
                "unique_trajectories_accepted": int(np.sum(self.accepted_counts > 0)),
            },
            "direction_counts": direction_counts if self.keep_events else None,
            "accepted_event_time_fs": [event["time_fs"] for event in accepted_events],
            "per_trajectory_proposed_counts": self.proposed_counts.tolist(),
            "per_trajectory_frustrated_counts": self.frustrated_counts.tolist(),
            "per_trajectory_accepted_counts": self.accepted_counts.tolist(),
            "records": self.events if self.keep_events else None,
        }


def attempt_two_state_hops(
    population_before: np.ndarray,
    population_after: np.ndarray,
    active: np.ndarray,
    q: np.ndarray,
    momentum: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, HopAttempt, np.ndarray]:
    rows = np.arange(active.size)
    from_state = active.copy()
    active_before = population_before[rows, active]
    active_after = population_after[rows, active]
    probability = np.maximum(
        0.0, (active_before - active_after) / np.maximum(active_before, 1e-14)
    )
    probability = np.minimum(probability, 1.0)
    proposed = rng.random(active.size) < probability
    accepted = np.zeros(active.size, dtype=bool)
    scale = np.ones(active.size)
    if np.any(proposed):
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
    attempt = HopAttempt(
        proposed=proposed,
        frustrated=proposed & ~accepted,
        accepted=accepted,
        from_state=from_state,
    )
    return active, momentum, attempt, scale


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
    *,
    pfm_rate_scale: float,
) -> tuple[np.ndarray, np.ndarray, list[HopAttempt], np.ndarray]:
    """Advance FP electronics with an explicitly supplied PFM scale."""

    sub_dt = dt / electronic_substeps
    displacement = q_new - q_old
    attempts: list[HopAttempt] = []
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
        active, midpoint_momentum, attempt, scale = attempt_two_state_hops(
            population_before,
            population_after,
            active,
            q_b,
            midpoint_momentum,
            rng,
        )
        attempts.append(attempt)
        cumulative_scale *= scale
        apply_pfm_decoherence(
            c_diabatic,
            q_b,
            active,
            p_aux,
            f_aux,
            sub_dt,
            pfm_rate_scale=pfm_rate_scale,
        )
    return active, midpoint_momentum, attempts, cumulative_scale


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
    *,
    pfm_rate_scale: float,
) -> tuple[np.ndarray, np.ndarray, list[HopAttempt], np.ndarray]:
    """Advance AXE paths/repropagation with an explicit PFM scale."""

    sub_dt = dt / electronic_substeps
    displacement = q_new - q_old
    attempts: list[HopAttempt] = []
    cumulative_scale = np.ones(active.size)
    for substep in range(electronic_substeps):
        fraction_a = substep / electronic_substeps
        fraction_b = (substep + 1) / electronic_substeps
        q_a = q_old + fraction_a * displacement
        q_b = q_old + fraction_b * displacement
        q_mid = 0.5 * (q_a + q_b)
        base_before = np.abs(diabatic_to_adiabatic(base_diabatic, q_a)) ** 2
        apply_batch_potential(base_diabatic, q_mid, sub_dt)
        base_after = np.abs(diabatic_to_adiabatic(base_diabatic, q_b)) ** 2
        active, midpoint_momentum, attempt, scale = attempt_two_state_hops(
            base_before,
            base_after,
            active,
            q_b,
            midpoint_momentum,
            rng,
        )
        attempts.append(attempt)
        cumulative_scale *= scale
        apply_pfm_decoherence(
            base_diabatic,
            q_b,
            active,
            base_p_aux,
            f_aux,
            sub_dt,
            pfm_rate_scale=pfm_rate_scale,
        )
        apply_batch_potential(reprop_diabatic, q_mid, sub_dt)
        apply_pfm_decoherence(
            reprop_diabatic,
            q_b,
            active,
            reprop_p_aux,
            f_aux,
            sub_dt,
            pfm_rate_scale=pfm_rate_scale,
        )
    return active, midpoint_momentum, attempts, cumulative_scale


def sample_bma_wigner(
    count: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample the frozen center=0.5, zero-kick Wigner launch."""

    center_x = FINAL_CENTER_FRACTION * BMA_MODEL.qbar_x
    q = np.column_stack((
        rng.normal(center_x, BMA_MODEL.initial_sigma_x, count),
        rng.normal(0.0, BMA_MODEL.initial_sigma_y, count),
    ))
    sigma_px = math.sqrt(BMA_MODEL.omega_x / 2.0)
    momentum = np.column_stack((
        rng.normal(0.0, sigma_px, count),
        rng.normal(0.0, math.sqrt(BMA_MODEL.omega_y / 2.0), count),
    ))
    return q, momentum


def target_diabatic_coefficients(count: int) -> np.ndarray:
    return np.repeat(electronic_initial_state()[None, :], count, axis=0)


def initialize_full_ensemble(
    q: np.ndarray,
    momentum: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
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


def initialize_axe_ensemble(q: np.ndarray, momentum: np.ndarray) -> dict[str, Any]:
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
    state: dict[str, np.ndarray],
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
    *,
    pfm_rate_scale: float,
) -> list[HopAttempt]:
    q_old = state["q"]
    p_old = state["p"]
    active_old = state["active"].copy()
    energy_old, force_old_all = bma_adiabatic_quantities(q_old)
    population_old = np.abs(diabatic_to_adiabatic(state["c"], q_old)) ** 2
    midpoint_p = p_old + 0.5 * force_for_active(force_old_all, active_old) * dt
    q_new = q_old + midpoint_p * dt
    energy_new, force_new_all = bma_adiabatic_quantities(q_new)
    f_aux = auxiliary_forces(energy_old, energy_new, midpoint_p, dt)
    active_new, midpoint_p, attempts, hop_scale = advance_full_electronics(
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
        pfm_rate_scale=pfm_rate_scale,
    )
    p_new = midpoint_p + 0.5 * force_for_active(force_new_all, active_new) * dt
    kinetic_midpoint = 0.5 * np.sum(midpoint_p**2, axis=1)
    p_aux, _ = update_auxiliary_momenta(
        state["c"], q_new, state["p_aux"], f_aux, active_old, active_new,
        population_old, energy_new, kinetic_midpoint, hop_scale, dt,
    )
    rows = np.arange(active_new.size)
    total_energy = 0.5 * np.sum(p_new**2, axis=1) + energy_new[rows, active_new]
    state["max_energy_drift"] = np.maximum(
        state["max_energy_drift"], np.abs(total_energy - state["initial_energy"])
    )
    state["q"] = q_new
    state["p"] = p_new
    state["active"] = active_new
    state["p_aux"] = p_aux
    return attempts


def step_axe_ensemble(
    state: dict[str, Any],
    dt: float,
    electronic_substeps: int,
    rng: np.random.Generator,
    *,
    pfm_rate_scale: float,
) -> list[HopAttempt]:
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
    midpoint_p = p_old + 0.5 * force_for_active(force_old_all, active_old) * dt
    q_new = q_old + midpoint_p * dt
    energy_new, force_new_all = bma_adiabatic_quantities(q_new)
    f_aux = auxiliary_forces(energy_old, energy_new, midpoint_p, dt)
    active_new, midpoint_p, attempts, hop_scale = advance_axe_electronics(
        state["base_c"], state["reprop_c"], q_old, q_new,
        active_old.copy(), midpoint_p, state["base_p_aux"],
        state["reprop_p_aux"], f_aux, dt, electronic_substeps, rng,
        pfm_rate_scale=pfm_rate_scale,
    )
    p_new = midpoint_p + 0.5 * force_for_active(force_new_all, active_new) * dt
    kinetic_midpoint = 0.5 * np.sum(midpoint_p**2, axis=1)
    base_p_aux, _ = update_auxiliary_momenta(
        state["base_c"], q_new, state["base_p_aux"], f_aux,
        active_old, active_new, base_population_old, energy_new,
        kinetic_midpoint, hop_scale, dt,
    )
    reprop_p_aux, _ = update_auxiliary_momenta(
        state["reprop_c"], q_new, state["reprop_p_aux"], f_aux,
        active_old, active_new, reprop_population_old, energy_new,
        kinetic_midpoint, hop_scale, dt,
    )
    rows = np.arange(active_new.size)
    total_energy = 0.5 * np.sum(p_new**2, axis=1) + energy_new[rows, active_new]
    state["max_energy_drift"] = np.maximum(
        state["max_energy_drift"], np.abs(total_energy - state["initial_energy"])
    )
    state["q"] = q_new
    state["p"] = p_new
    state["active"] = active_new
    state["base_p_aux"] = base_p_aux
    state["reprop_p_aux"] = reprop_p_aux
    return attempts


def coherence_observables(
    c_ad: np.ndarray,
    *,
    weights: np.ndarray | None = None,
    denominator: float | None = None,
) -> dict[str, float]:
    """Return signed ensemble coherence and the legacy local-magnitude proxy."""

    local_density_matrix = np.conj(c_ad[:, 0]) * c_ad[:, 1]
    if weights is None:
        ensemble_density_matrix = np.mean(local_density_matrix)
        local_magnitude = np.mean(2.0 * np.abs(local_density_matrix))
    else:
        if denominator is None or denominator <= 0.0:
            raise ValueError("weighted coherence requires a positive denominator")
        ensemble_density_matrix = np.sum(weights * local_density_matrix) / denominator
        local_magnitude = (
            np.sum(weights * 2.0 * np.abs(local_density_matrix)) / denominator
        )
    coherence_real = float(2.0 * np.real(ensemble_density_matrix))
    coherence_imag = float(2.0 * np.imag(ensemble_density_matrix))
    return {
        "ensemble_coherence_real": coherence_real,
        "ensemble_coherence_imag": coherence_imag,
        "coherence_amplitude": math.hypot(coherence_real, coherence_imag),
        "mean_trajectory_coherence_magnitude": float(local_magnitude),
    }


def observe_full_ensemble(state: dict[str, np.ndarray]) -> dict[str, float]:
    c_ad = diabatic_to_adiabatic(state["c"], state["q"])
    population = np.abs(c_ad) ** 2
    return {
        "upper_population": float(np.mean(population[:, 1])),
        "active_upper_fraction": float(np.mean(state["active"] == 1)),
        **coherence_observables(c_ad),
        "centroid_x": float(np.mean(state["q"][:, 0])),
        "centroid_y": float(np.mean(state["q"][:, 1])),
        "product_qx_lt_0": float(np.mean(state["q"][:, 0] < 0.0)),
        "electronic_norm_error": float(np.max(np.abs(
            electronic_norm(state["c"]) - 1.0
        ))),
    }


def observe_axe_ensemble(state: dict[str, Any]) -> dict[str, float]:
    c_ad = diabatic_to_adiabatic(state["reprop_c"], state["q"])
    population = np.abs(c_ad) ** 2
    weight = state["weights"]
    denominator = float(state["geometry_count"])
    return {
        "upper_population": float(np.sum(weight * population[:, 1]) / denominator),
        **coherence_observables(
            c_ad, weights=weight, denominator=denominator
        ),
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


def append_observation(storage: dict[str, list[float]], observation: dict[str, float]) -> None:
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


def comparison_classification(summary: dict[str, Any]) -> dict[str, Any]:
    fraction = summary["accepted_event_fraction_before_coherence_lifetime"]
    majority = None if not math.isfinite(fraction) else bool(fraction >= 0.5)
    robust = bool(all(
        summary[name] <= threshold
        for name, threshold in ERROR_THRESHOLDS.items()
    ))
    return {
        "majority_accepted_events_before_coherence_lifetime": majority,
        "rp_axe_within_compound_error_thresholds": robust,
        "boundary_reached_and_robust": None if majority is None else majority and robust,
    }


def trajectory_comparison_summary(
    time_fs: np.ndarray,
    full: dict[str, list[float]],
    reprop: dict[str, list[float]],
    accepted_event_times_fs: np.ndarray,
) -> dict[str, Any]:
    coherence = np.asarray(full["coherence_amplitude"])
    lifetime = first_threshold_crossing(time_fs, coherence, coherence[0] / math.e)
    if accepted_event_times_fs.size and math.isfinite(lifetime):
        accepted_fraction = float(np.mean(accepted_event_times_fs <= lifetime))
    else:
        accepted_fraction = float("nan")
    population_error = np.abs(
        np.asarray(full["upper_population"])
        - np.asarray(reprop["upper_population"])
    )
    product_error = np.abs(
        np.asarray(full["product_qx_lt_0"])
        - np.asarray(reprop["product_qx_lt_0"])
    )
    centroid_error_sigma = np.abs(
        np.asarray(full["centroid_x"]) - np.asarray(reprop["centroid_x"])
    ) / BMA_MODEL.initial_sigma_x
    result: dict[str, Any] = {
        "coherence_lifetime_fs": lifetime,
        "successful_full_hops": int(accepted_event_times_fs.size),
        # Compatibility alias: this remains an accepted-event fraction, not a
        # unique-trajectory fraction.  Repeat/recrossing hops stay in its denominator.
        "early_hop_fraction": accepted_fraction,
        "accepted_event_fraction_before_coherence_lifetime": accepted_fraction,
        "accepted_event_fraction_definition": (
            "number of accepted FP hop events at or before the interpolated "
            "1/e FP coherence lifetime divided by all accepted FP hop events; "
            "repeat events remain in both numerator and denominator"
        ),
        "max_upper_population_error": float(np.max(population_error)),
        "max_product_probability_error": float(np.max(product_error)),
        "max_centroid_x_error_sigma": float(np.max(centroid_error_sigma)),
        "population_error_series": population_error.tolist(),
        "product_error_series": product_error.tolist(),
        "centroid_error_sigma_series": centroid_error_sigma.tolist(),
    }
    result["classification"] = comparison_classification(result)
    return result


def run_trajectory_regime(
    *,
    pfm_rate_scale: float,
    seed: int,
    geometry_count: int,
    dt_fs: float,
    electronic_substeps: int,
    total_fs: float,
    progress: bool = False,
) -> dict[str, Any]:
    """Run one paired FP/RP-AXE replicate at the invariant launch."""

    scale = validate_scale(pfm_rate_scale)
    identity = make_resume_identity(
        pfm_rate_scale=scale,
        seed=seed,
        geometry_count=geometry_count,
        dt_fs=dt_fs,
        electronic_substeps=electronic_substeps,
        total_fs=total_fs,
    )
    initial_rng = np.random.default_rng(seed)
    full_rng = np.random.default_rng(100_000 + seed)
    axe_rng = np.random.default_rng(200_000 + seed)
    q_initial, p_initial = sample_bma_wigner(geometry_count, initial_rng)
    full_state = initialize_full_ensemble(q_initial, p_initial, full_rng)
    axe_state = initialize_axe_ensemble(q_initial, p_initial)
    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps
    dt = actual_dt_fs * FS_TO_AU
    time_values = [0.0]
    full_observations: dict[str, list[float]] = {}
    reprop_observations: dict[str, list[float]] = {}
    append_observation(full_observations, observe_full_ensemble(full_state))
    append_observation(reprop_observations, observe_axe_ensemble(axe_state))
    full_recorder = HopRecorder(
        geometry_count, keep_events=True, initial_state=full_state["active"]
    )
    axe_recorder = HopRecorder(
        2 * geometry_count, keep_events=False, initial_state=axe_state["active"]
    )
    for step in range(steps):
        full_attempts = step_full_ensemble(
            full_state, dt, electronic_substeps, full_rng,
            pfm_rate_scale=scale,
        )
        axe_attempts = step_axe_ensemble(
            axe_state, dt, electronic_substeps, axe_rng,
            pfm_rate_scale=scale,
        )
        for substep, attempt in enumerate(full_attempts):
            event_time = (
                step + (substep + 1) / electronic_substeps
            ) * actual_dt_fs
            full_recorder.record(
                attempt,
                time_fs=event_time,
                nuclear_step=step + 1,
                electronic_substep=substep + 1,
            )
        for substep, attempt in enumerate(axe_attempts):
            event_time = (
                step + (substep + 1) / electronic_substeps
            ) * actual_dt_fs
            axe_recorder.record(
                attempt,
                time_fs=event_time,
                nuclear_step=step + 1,
                electronic_substep=substep + 1,
            )
        time_values.append((step + 1) * actual_dt_fs)
        append_observation(full_observations, observe_full_ensemble(full_state))
        append_observation(reprop_observations, observe_axe_ensemble(axe_state))
        if progress and (
            (step + 1) % max(1, steps // 10) == 0 or step + 1 == steps
        ):
            print(
                f"scale={scale:g} seed={seed} {step + 1}/{steps}", flush=True
            )
    full_event_summary = full_recorder.as_dict()
    axe_event_summary = axe_recorder.as_dict()
    accepted_times = np.asarray(full_event_summary["accepted_event_time_fs"])
    comparison = trajectory_comparison_summary(
        np.asarray(time_values), full_observations, reprop_observations,
        accepted_times,
    )
    configuration = {
        **identity,
        "dt_fs": float(dt_fs),
        "n": int(geometry_count),
        "initial_sigma_x": BMA_MODEL.initial_sigma_x,
        "resume_identity": identity,
        "resume_key": make_resume_key(
            pfm_rate_scale=scale,
            seed=seed,
            geometry_count=geometry_count,
            dt_fs=dt_fs,
            electronic_substeps=electronic_substeps,
            total_fs=total_fs,
        ),
        "model_contract": invariant_contract(),
        "pfm_omega": math.sqrt(BMA_MODEL.omega_x * BMA_MODEL.omega_y),
        "pfm_population_threshold": PFM_POPULATION_THRESHOLD,
    }
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
        "full_energy_drift_max_hartree": float(np.max(
            full_state["max_energy_drift"]
        )),
        "axe_energy_drift_max_hartree": float(np.max(
            axe_state["max_energy_drift"]
        )),
        "max_full_internal_consistency_error": float(np.max(np.abs(
            np.asarray(full_observations["upper_population"])
            - np.asarray(full_observations["active_upper_fraction"])
        ))),
    }
    return {
        "configuration": configuration,
        "time_fs": time_values,
        "full": full_observations,
        "reprop_axe": reprop_observations,
        "events": {
            "full": full_event_summary["records"],
            "axe": [],
        },
        "event_summary": {
            "full": full_event_summary,
            "axe": axe_event_summary,
        },
        "full_hop_time_fs": full_event_summary["accepted_event_time_fs"],
        "comparison": comparison,
        "diagnostics": diagnostics,
    }


def _maximum_abs_difference(a: Any, b: Any) -> float:
    left = np.asarray(a, dtype=float)
    right = np.asarray(b, dtype=float)
    if left.shape != right.shape:
        return float("inf")
    finite = np.isfinite(left) & np.isfinite(right)
    if not np.array_equal(np.isfinite(left), np.isfinite(right)):
        return float("inf")
    if not np.any(finite):
        return 0.0
    return float(np.max(np.abs(left[finite] - right[finite])))


def load_legacy_module(path: Path):
    spec = importlib.util.spec_from_file_location("pulse_independent_ci_legacy", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import legacy simulator at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_lineage_comparison(
    *,
    output: Path | None,
    seed: int = LINEAGE_SEED,
    geometry_count: int = LINEAGE_GEOMETRY_COUNT,
    dt_fs: float = LINEAGE_DT_FS,
    electronic_substeps: int = LINEAGE_ELECTRONIC_SUBSTEPS,
    total_fs: float = LINEAGE_TOTAL_FS,
    rtol: float = 1e-12,
    atol: float = 1e-12,
) -> dict[str, Any]:
    """Compare s=1 with the direct legacy implementation."""

    repository = Path(__file__).resolve().parents[3]
    legacy_path = repository / "downloads" / "pulse-independent-ci.py"
    archive_path = repository / "downloads" / "pulse-independent-ci-data.tar.gz"
    source_sha256 = sha256_file(legacy_path)
    archive_sha256 = sha256_file(archive_path)
    source_checksum_matches = source_sha256 == EXPECTED_LEGACY_SOURCE_SHA256
    archive_checksum_matches = archive_sha256 == EXPECTED_LEGACY_ARCHIVE_SHA256
    if not source_checksum_matches or not archive_checksum_matches:
        raise ValueError(
            "refusing to import the ancestor because a frozen lineage checksum failed"
        )
    legacy = load_legacy_module(legacy_path)
    common = {
        "seed": seed,
        "geometry_count": geometry_count,
        "dt_fs": dt_fs,
        "electronic_substeps": electronic_substeps,
        "total_fs": total_fs,
        "progress": False,
    }
    legacy_accepted_records: list[dict[str, Any]] = []
    legacy_full_calls = 0
    original_hop_function = legacy.attempt_two_state_hops
    steps = int(round(total_fs / dt_fs))
    actual_dt_fs = total_fs / steps

    def instrumented_legacy_hops(
        population_before: np.ndarray,
        population_after: np.ndarray,
        active: np.ndarray,
        q: np.ndarray,
        momentum: np.ndarray,
        rng: np.random.Generator,
    ):
        """Observe accepted legacy FP hops without changing ancestor bytes."""

        nonlocal legacy_full_calls
        from_state = active.copy()
        result = original_hop_function(
            population_before, population_after, active, q, momentum, rng
        )
        if active.size == geometry_count:
            nuclear_step = legacy_full_calls // electronic_substeps
            electronic_substep = legacy_full_calls % electronic_substeps
            event_time_fs = (
                nuclear_step + (electronic_substep + 1) / electronic_substeps
            ) * actual_dt_fs
            accepted = result[2]
            for trajectory_id in np.flatnonzero(accepted):
                trajectory_id = int(trajectory_id)
                legacy_accepted_records.append({
                    "trajectory_id": trajectory_id,
                    "time_fs": float(event_time_fs),
                    "from_state": int(from_state[trajectory_id]),
                    "to_state": int(result[0][trajectory_id]),
                })
            legacy_full_calls += 1
        return result

    legacy.attempt_two_state_hops = instrumented_legacy_hops
    try:
        reference = legacy.run_trajectory_regime(
            center_fraction=FINAL_CENTER_FRACTION,
            momentum_kick_sigma=FINAL_MOMENTUM_KICK_SIGMA,
            **common,
        )
    finally:
        legacy.attempt_two_state_hops = original_hop_function
    # Wall-clock timing is intentionally excluded from hash-bound scientific
    # artifacts even though the checksummed ancestor returned it.
    reference.pop("runtime_seconds", None)
    candidate = run_trajectory_regime(pfm_rate_scale=1.0, **common)
    candidate_accepted_records = [
        {
            "trajectory_id": int(event["trajectory_id"]),
            "time_fs": float(event["time_fs"]),
            "from_state": int(event["from_state"]),
            "to_state": int(event["to_state"]),
        }
        for event in candidate["events"]["full"]
        if event["accepted"]
    ]
    instrumentation_complete = legacy_full_calls == steps * electronic_substeps
    differences: dict[str, float] = {
        "time_fs": _maximum_abs_difference(
            reference["time_fs"], candidate["time_fs"]
        ),
        "accepted_event_times_fs": _maximum_abs_difference(
            reference["full_hop_time_fs"], candidate["full_hop_time_fs"]
        ),
    }
    for method, observables in LINEAGE_FIELDS.items():
        for observable in observables:
            differences[f"{method}.{observable}"] = _maximum_abs_difference(
                reference[method][observable], candidate[method][observable]
            )
    for method, (legacy_field, candidate_field) in LINEAGE_COHERENCE_FIELDS.items():
        differences[f"{method}.{candidate_field}"] = _maximum_abs_difference(
            reference[method][legacy_field], candidate[method][candidate_field]
        )
    accepted_events_identical = bool(
        instrumentation_complete
        and legacy_accepted_records == candidate_accepted_records
    )
    max_abs = max(differences.values())
    # Every compared value should be identical up to the declared allclose
    # tolerances.  max_abs <= atol is sufficient here because all observables
    # are O(1); the explicit per-array allclose also applies rtol.
    arrays_close = all(
        np.allclose(
            np.asarray(reference[method][observable]),
            np.asarray(candidate[method][observable]),
            rtol=rtol,
            atol=atol,
            equal_nan=True,
        )
        for method, observables in LINEAGE_FIELDS.items()
        for observable in observables
    )
    arrays_close = arrays_close and all(
        np.allclose(
            np.asarray(reference[method][legacy_field]),
            np.asarray(candidate[method][candidate_field]),
            rtol=rtol,
            atol=atol,
            equal_nan=True,
        )
        for method, (legacy_field, candidate_field) in LINEAGE_COHERENCE_FIELDS.items()
    )
    fingerprints = runtime_fingerprints()
    result = {
        "schema_version": 1,
        "artifact_type": "lineage_comparison",
        "environment": environment_record(),
        **fingerprints,
        "legacy_source": {
            "path": str(legacy_path.relative_to(repository)),
            "expected_sha256": EXPECTED_LEGACY_SOURCE_SHA256,
            "sha256": source_sha256,
            "checksum_matches": source_checksum_matches,
        },
        "legacy_archive": {
            "path": str(archive_path.relative_to(repository)),
            "expected_sha256": EXPECTED_LEGACY_ARCHIVE_SHA256,
            "sha256": archive_sha256,
            "checksum_matches": archive_checksum_matches,
        },
        "configuration": {
            **common,
            "center_fraction": FINAL_CENTER_FRACTION,
            "momentum_kick_toward_ci_sigma_px": 0.0,
            "pfm_rate_scale": 1.0,
            "rtol": rtol,
            "atol": atol,
        },
        "reference": reference,
        "candidate": candidate,
        "accepted_hop_record_comparison": {
            "fields": ["trajectory_id", "time_fs", "from_state", "to_state"],
            "legacy_instrumentation": (
                "runtime wrapper around the checksummed ancestor hop function; "
                "ancestor source bytes were not modified"
            ),
            "instrumentation_complete": instrumentation_complete,
            "legacy_full_electronic_calls": legacy_full_calls,
            "expected_full_electronic_calls": steps * electronic_substeps,
            "reference_records": legacy_accepted_records,
            "candidate_records": candidate_accepted_records,
        },
        "comparison": {
            "accepted_events_identical": accepted_events_identical,
            "maximum_abs_difference_by_array": differences,
            "max_abs_observable_difference": max_abs,
            "rtol": rtol,
            "atol": atol,
            "source_checksum_matches": source_checksum_matches,
            "archive_checksum_matches": archive_checksum_matches,
            "passed": bool(
                source_checksum_matches
                and archive_checksum_matches
                and accepted_events_identical
                and arrays_close
            ),
        },
    }
    if output is not None:
        write_json(output, result)
    return result


def require_passing_lineage(path: Path) -> dict[str, Any]:
    """Reject later stages unless the current frozen lineage gate passed."""

    if not path.is_file():
        raise FileNotFoundError(f"missing {path}; run the frozen lineage gate first")
    with path.open(encoding="utf-8") as handle:
        lineage = json.load(handle)
    if lineage.get("artifact_type") != "lineage_comparison":
        raise ValueError("lineage artifact type is not lineage_comparison")
    for name, expected in runtime_fingerprints().items():
        if lineage.get(name) != expected:
            raise ValueError(f"lineage {name} does not match the current runtime")
    repository = Path(__file__).resolve().parents[3]
    current_source = sha256_file(repository / "downloads" / "pulse-independent-ci.py")
    current_archive = sha256_file(
        repository / "downloads" / "pulse-independent-ci-data.tar.gz"
    )
    comparison = lineage.get("comparison", {})
    record_comparison = lineage.get("accepted_hop_record_comparison", {})
    configuration = lineage.get("configuration", {})
    expected_configuration = {
        "seed": LINEAGE_SEED,
        "geometry_count": LINEAGE_GEOMETRY_COUNT,
        "dt_fs": LINEAGE_DT_FS,
        "electronic_substeps": LINEAGE_ELECTRONIC_SUBSTEPS,
        "total_fs": LINEAGE_TOTAL_FS,
        "center_fraction": FINAL_CENTER_FRACTION,
        "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
        "pfm_rate_scale": 1.0,
        "rtol": 1e-12,
        "atol": 1e-12,
    }
    configuration_matches = all(
        configuration.get(name) == value
        for name, value in expected_configuration.items()
    )
    reference = lineage.get("reference", {})
    candidate = lineage.get("candidate", {})
    try:
        arrays_close = all(
            np.allclose(
                np.asarray(reference[method][observable]),
                np.asarray(candidate[method][observable]),
                rtol=1e-12,
                atol=1e-12,
                equal_nan=True,
            )
            for method, observables in LINEAGE_FIELDS.items()
            for observable in observables
        )
        arrays_close = arrays_close and all(
            np.allclose(
                np.asarray(reference[method][legacy_field]),
                np.asarray(candidate[method][candidate_field]),
                rtol=1e-12,
                atol=1e-12,
                equal_nan=True,
            )
            for method, (legacy_field, candidate_field) in LINEAGE_COHERENCE_FIELDS.items()
        )
        reference_records = record_comparison["reference_records"]
        candidate_records = record_comparison["candidate_records"]
        projected_candidate_records = [
            {
                "trajectory_id": int(event["trajectory_id"]),
                "time_fs": float(event["time_fs"]),
                "from_state": int(event["from_state"]),
                "to_state": int(event["to_state"]),
            }
            for event in candidate["events"]["full"]
            if event["accepted"]
        ]
        records_match = (
            reference_records == candidate_records == projected_candidate_records
            and reference["full_hop_time_fs"]
            == [record["time_fs"] for record in reference_records]
            and candidate["full_hop_time_fs"]
            == [record["time_fs"] for record in candidate_records]
        )
        instrumentation_complete = (
            record_comparison["instrumentation_complete"] is True
            and record_comparison["legacy_full_electronic_calls"]
            == record_comparison["expected_full_electronic_calls"]
            == int(round(LINEAGE_TOTAL_FS / LINEAGE_DT_FS))
            * LINEAGE_ELECTRONIC_SUBSTEPS
        )
    except (KeyError, TypeError, ValueError):
        arrays_close = False
        records_match = False
        instrumentation_complete = False
    required = (
        current_source == EXPECTED_LEGACY_SOURCE_SHA256,
        current_archive == EXPECTED_LEGACY_ARCHIVE_SHA256,
        lineage.get("legacy_source", {}).get("sha256") == current_source,
        lineage.get("legacy_archive", {}).get("sha256") == current_archive,
        comparison.get("source_checksum_matches") is True,
        comparison.get("archive_checksum_matches") is True,
        configuration_matches,
        arrays_close,
        records_match,
        instrumentation_complete,
        comparison.get("accepted_events_identical") is True,
        comparison.get("passed") is True,
    )
    if not all(required):
        raise ValueError("lineage gate is missing a required pass condition")
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "passed": True,
    }


def _paired_interval(values: np.ndarray) -> dict[str, Any]:
    """Return a two-sided 95% t interval for paired seed differences."""

    values = np.asarray(values, dtype=float)
    if values.ndim not in (1, 2) or values.shape[0] < 2:
        raise ValueError("paired convergence values need at least two seed pairs")
    if not np.all(np.isfinite(values)):
        raise ValueError("paired convergence values must be finite")
    critical = {4: 3.182, 8: 2.365}.get(values.shape[0], 1.96)
    mean = np.mean(values, axis=0)
    half_width = critical * np.std(values, axis=0, ddof=1) / math.sqrt(values.shape[0])
    lower = mean - half_width
    upper = mean + half_width
    max_abs_endpoint = float(np.max(np.maximum(np.abs(lower), np.abs(upper))))
    if values.ndim == 1:
        return {
            "paired_differences": values.tolist(),
            "mean": float(mean),
            "half_width": float(half_width),
            "lower": float(lower),
            "upper": float(upper),
            "max_abs_interval_endpoint": max_abs_endpoint,
            "n": int(values.shape[0]),
        }
    return {
        "max_abs_interval_endpoint": max_abs_endpoint,
        "time_index_of_max_abs_interval_endpoint": int(np.argmax(
            np.maximum(np.abs(lower), np.abs(upper))
        )),
        "n": int(values.shape[0]),
    }


def compare_trajectory_settings(
    candidate_runs: list[dict[str, Any]],
    reference_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare fine/finer ensembles with paired-seed uncertainty intervals."""

    candidate_runs = sorted(
        candidate_runs, key=lambda run: int(run["configuration"]["seed"])
    )
    reference_runs = sorted(
        reference_runs, key=lambda run: int(run["configuration"]["seed"])
    )
    candidate_seeds = [int(run["configuration"]["seed"]) for run in candidate_runs]
    reference_seeds = [int(run["configuration"]["seed"]) for run in reference_runs]
    if candidate_seeds != reference_seeds or tuple(candidate_seeds) != CONVERGENCE_SEEDS:
        raise ValueError("convergence settings must contain the eight frozen seed pairs")

    scalar_differences = {
        "accepted_event_fraction": [],
        "coherence_lifetime_fs": [],
    }
    series_differences: dict[str, list[np.ndarray]] = {
        "upper_population": [],
        "product_qx_lt_0": [],
        "centroid_x_sigma": [],
    }
    all_seed_values_finite = True
    candidate_time = np.asarray(candidate_runs[0]["time_fs"], dtype=float)
    for candidate, reference in zip(candidate_runs, reference_runs, strict=True):
        reference_time = np.asarray(reference["time_fs"], dtype=float)
        for key in ("accepted_event_fraction", "coherence_lifetime_fs"):
            field = (
                "accepted_event_fraction_before_coherence_lifetime"
                if key == "accepted_event_fraction" else key
            )
            left = candidate["comparison"].get(field)
            right = reference["comparison"].get(field)
            if left is None or right is None or not (
                math.isfinite(float(left)) and math.isfinite(float(right))
            ):
                all_seed_values_finite = False
                continue
            scalar_differences[key].append(float(left) - float(right))
        if not candidate["full_hop_time_fs"] or not reference["full_hop_time_fs"]:
            all_seed_values_finite = False
        for observable, output_name, scale in (
            ("upper_population", "upper_population", 1.0),
            ("product_qx_lt_0", "product_qx_lt_0", 1.0),
            ("centroid_x", "centroid_x_sigma", BMA_MODEL.initial_sigma_x),
        ):
            reference_values = np.interp(
                candidate_time,
                reference_time,
                np.asarray(reference["full"][observable], dtype=float),
            )
            series_differences[output_name].append(
                (
                    np.asarray(candidate["full"][observable], dtype=float)
                    - reference_values
                ) / scale
            )

    scalar_intervals = {}
    if all_seed_values_finite:
        scalar_intervals = {
            key: _paired_interval(np.asarray(values, dtype=float))
            for key, values in scalar_differences.items()
        }
    series_intervals = {
        key: _paired_interval(np.stack(values, axis=0))
        for key, values in series_differences.items()
    }
    for summary in series_intervals.values():
        summary["time_fs_of_max_abs_interval_endpoint"] = float(
            candidate_time[summary.pop("time_index_of_max_abs_interval_endpoint")]
        )

    candidate_class = aggregate_scale_runs(candidate_runs)[
        "comparison_of_replicate_means"
    ]["classification"]
    reference_class = aggregate_scale_runs(reference_runs)[
        "comparison_of_replicate_means"
    ]["classification"]
    checks = {
        "all_seed_lifetimes_and_event_denominators_finite": all_seed_values_finite,
        "accepted_event_fraction_95_interval_within_0_02": bool(
            all_seed_values_finite
            and scalar_intervals["accepted_event_fraction"]
            ["max_abs_interval_endpoint"]
            <= TRAJECTORY_GATE_LIMITS["accepted_event_fraction"]
        ),
        "coherence_lifetime_95_interval_within_0_15_fs": bool(
            all_seed_values_finite
            and scalar_intervals["coherence_lifetime_fs"]
            ["max_abs_interval_endpoint"]
            <= TRAJECTORY_GATE_LIMITS["coherence_lifetime_fs"]
        ),
        "full_upper_population_95_envelope_within_0_02": (
            series_intervals["upper_population"]["max_abs_interval_endpoint"]
            <= TRAJECTORY_GATE_LIMITS["upper_population"]
        ),
        "full_product_95_envelope_within_0_02": (
            series_intervals["product_qx_lt_0"]["max_abs_interval_endpoint"]
            <= TRAJECTORY_GATE_LIMITS["product_qx_lt_0"]
        ),
        "full_centroid_95_envelope_within_0_03_sigma": (
            series_intervals["centroid_x_sigma"]["max_abs_interval_endpoint"]
            <= TRAJECTORY_GATE_LIMITS["centroid_x_sigma"]
        ),
        "majority_classification_unchanged": (
            candidate_class["majority_accepted_events_before_coherence_lifetime"]
            == reference_class["majority_accepted_events_before_coherence_lifetime"]
        ),
        "compound_robustness_classification_unchanged": (
            candidate_class["rp_axe_within_compound_error_thresholds"]
            == reference_class["rp_axe_within_compound_error_thresholds"]
        ),
    }
    checks["passed"] = bool(all(checks.values()))
    return {
        "limits": TRAJECTORY_GATE_LIMITS,
        "seeds": candidate_seeds,
        "paired_scalar_95_intervals": scalar_intervals,
        "paired_time_series_95_envelopes": series_intervals,
        "candidate_classification": candidate_class,
        "reference_classification": reference_class,
        "gate": checks,
        "selected_final_numerics": {
            "dt_fs": FINE_DT_FS,
            "electronic_substeps": FINE_SUBSTEPS,
            "validated": checks["passed"],
            "reason": (
                "candidate passed every frozen multi-seed fine/finer criterion"
                if checks["passed"]
                else "candidate convergence was not demonstrated; production is blocked"
            ),
        },
    }


def run_trajectory_convergence(
    output: Path,
    lineage_path: Path,
    workers: int = 1,
    progress: bool = False,
    restart: bool = False,
) -> dict[str, Any]:
    lineage_gate = require_passing_lineage(lineage_path)
    if workers <= 0:
        raise ValueError("workers must be positive")
    settings = (
        ("candidate", FINE_DT_FS, FINE_SUBSTEPS),
        ("reference", FINER_DT_FS, FINER_SUBSTEPS),
    )
    jobs = [
        {
            "setting": setting,
            "pfm_rate_scale": 0.05,
            "seed": seed,
            "geometry_count": FINAL_GEOMETRY_COUNT,
            "dt_fs": dt_fs,
            "electronic_substeps": substeps,
            "total_fs": FINAL_TOTAL_FS,
            "progress": progress and workers == 1,
        }
        for setting, dt_fs, substeps in settings
        for seed in CONVERGENCE_SEEDS
    ]
    fingerprints = runtime_fingerprints()
    runs: list[dict[str, Any]] = []
    if output.exists() and not restart:
        with output.open(encoding="utf-8") as handle:
            prior = json.load(handle)
        if prior.get("artifact_type") != "trajectory_convergence":
            raise ValueError("existing convergence artifact has the wrong type")
        for name, expected in fingerprints.items():
            if prior.get(name) != expected:
                raise ValueError(f"existing convergence {name} is stale")
        if prior.get("lineage_gate", {}).get("sha256") != lineage_gate["sha256"]:
            raise ValueError("existing convergence used a different lineage artifact")
        runs = list(prior.get("runs", []))

    declared = {
        (
            job["setting"],
            make_resume_key(**{
                key: value for key, value in job.items()
                if key not in ("setting", "progress")
            }),
        )
        for job in jobs
    }
    completed = {
        (entry["setting"], entry["run"]["configuration"]["resume_key"])
        for entry in runs
    }
    if len(completed) != len(runs) or not completed <= declared:
        raise ValueError("existing convergence contains duplicate or off-protocol runs")

    def checkpoint() -> dict[str, Any]:
        runs.sort(key=lambda entry: (
            0 if entry["setting"] == "candidate" else 1,
            int(entry["run"]["configuration"]["seed"]),
        ))
        candidate = [entry["run"] for entry in runs if entry["setting"] == "candidate"]
        reference = [entry["run"] for entry in runs if entry["setting"] == "reference"]
        complete = len(runs) == len(jobs)
        snapshot = {
            "schema_version": 2,
            "artifact_type": "trajectory_convergence",
            "environment": environment_record(),
            **fingerprints,
            "lineage_gate": lineage_gate,
            "seeds": list(CONVERGENCE_SEEDS),
            "declared_runs": len(jobs),
            "completed_runs": len(runs),
            "complete": complete,
            "runs": runs,
            "candidate": candidate,
            "reference": reference,
            "comparison": (
                compare_trajectory_settings(candidate, reference) if complete else None
            ),
        }
        write_json(output, snapshot)
        return snapshot

    pending = []
    for job in jobs:
        key = make_resume_key(**{
            name: value for name, value in job.items()
            if name not in ("setting", "progress")
        })
        if (job["setting"], key) not in completed:
            pending.append(job)

    def execute(job: dict[str, Any]) -> dict[str, Any]:
        setting = str(job["setting"])
        controls = {key: value for key, value in job.items() if key != "setting"}
        return {"setting": setting, "run": run_trajectory_regime(**controls)}

    if workers == 1:
        for job in pending:
            runs.append(execute(job))
            checkpoint()
            print(f"completed convergence {len(runs)}/{len(jobs)}", flush=True)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(execute, job): job for job in pending}
            for future in concurrent.futures.as_completed(futures):
                runs.append(future.result())
                checkpoint()
                print(f"completed convergence {len(runs)}/{len(jobs)}", flush=True)
    return checkpoint()


def _exact_difference(coarse: dict[str, Any], fine: dict[str, Any]) -> dict[str, float]:
    coarse_time = np.asarray(coarse["time_fs"])
    fine_time = np.asarray(fine["time_fs"])
    differences: dict[str, float] = {}
    for observable, scale in (
        ("upper_population", 1.0),
        ("product_qx_lt_0", 1.0),
        ("centroid_x", BMA_MODEL.initial_sigma_x),
        ("coherence_amplitude", 1.0),
    ):
        fine_values = np.interp(fine_time, coarse_time, np.asarray(coarse[observable]))
        differences[
            "centroid_x_sigma" if observable == "centroid_x" else observable
        ] = float(np.max(np.abs(np.asarray(fine[observable]) - fine_values)) / scale)
    return differences


def compare_exact_grids(
    coarse: dict[str, Any], fine: dict[str, Any]
) -> dict[str, Any]:
    differences = _exact_difference(coarse, fine)
    fine_norm_error = float(np.max(np.abs(np.asarray(fine["norm"]) - 1.0)))
    checks = {
        "upper_population_within_2e_4": (
            differences["upper_population"] <= EXACT_GATE_LIMITS["upper_population"]
        ),
        "product_probability_within_0_005": (
            differences["product_qx_lt_0"] <= EXACT_GATE_LIMITS["product_qx_lt_0"]
        ),
        "centroid_within_0_01_sigma": (
            differences["centroid_x_sigma"] <= EXACT_GATE_LIMITS["centroid_x_sigma"]
        ),
        "fine_norm_error_within_1e_10": (
            fine_norm_error < EXACT_GATE_LIMITS["fine_norm_error"]
        ),
    }
    checks["passed"] = bool(all(checks.values()))
    return {
        "limits": EXACT_GATE_LIMITS,
        "maximum_time_series_differences": differences,
        "fine_max_norm_error": fine_norm_error,
        "gate": checks,
        "valid_reference": checks["fine_norm_error_within_1e_10"],
        "production_grid_n": 384 if checks["passed"] else 512,
        "production_trace": "coarse" if checks["passed"] else "fine",
    }


def run_exact_grid_audit(
    output: Path,
    lineage_path: Path,
    convergence_path: Path,
    progress: bool = False,
) -> dict[str, Any]:
    lineage_gate = require_passing_lineage(lineage_path)
    _, _, _, convergence_sha256 = _selected_sweep_numerics(
        convergence_path, lineage_gate["sha256"]
    )
    coarse = run_bma_exact(grid_n=384, progress=progress)
    fine = run_bma_exact(grid_n=512, progress=progress)
    result = {
        "schema_version": 1,
        "artifact_type": "exact_grid_audit",
        "environment": environment_record(),
        **runtime_fingerprints(),
        "lineage_gate": lineage_gate,
        "convergence_path": str(convergence_path),
        "convergence_sha256": convergence_sha256,
        "coarse": coarse,
        "fine": fine,
        "comparison": compare_exact_grids(coarse, fine),
    }
    write_json(output, result)
    return result


def aggregate_observations(
    runs: list[dict[str, Any]], method: str
) -> dict[str, list[float]]:
    """Pool seed observables, reconstructing coherence after component pooling."""

    fields = runs[0][method]
    pooled = {
        field_name: np.mean([
            np.asarray(run[method][field_name], dtype=float) for run in runs
        ], axis=0).tolist()
        for field_name in fields
        if field_name != "coherence_amplitude"
    }
    coherence_real = np.asarray(pooled["ensemble_coherence_real"], dtype=float)
    coherence_imag = np.asarray(pooled["ensemble_coherence_imag"], dtype=float)
    pooled["coherence_amplitude"] = np.hypot(
        coherence_real, coherence_imag
    ).tolist()
    return pooled


def aggregate_scale_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs:
        raise ValueError("cannot aggregate an empty scale")
    time_fs = np.asarray(runs[0]["time_fs"], dtype=float)
    for run in runs[1:]:
        if not np.allclose(time_fs, np.asarray(run["time_fs"]), atol=1e-12):
            raise ValueError("replicate time grids differ")
    full = aggregate_observations(runs, "full")
    reprop = aggregate_observations(runs, "reprop_axe")
    accepted_times = np.concatenate([
        np.asarray(run["full_hop_time_fs"], dtype=float) for run in runs
    ])
    comparison = trajectory_comparison_summary(
        time_fs, full, reprop, accepted_times
    )
    return {
        "pfm_rate_scale": runs[0]["configuration"]["pfm_rate_scale"],
        "seeds": [run["configuration"]["seed"] for run in runs],
        "replicate_count": len(runs),
        "time_fs": time_fs.tolist(),
        "full": full,
        "reprop_axe": reprop,
        "comparison_of_replicate_means": comparison,
        "accepted_fp_event_count": int(accepted_times.size),
        "proposed_fp_event_count": int(sum(
            run["event_summary"]["full"]["counts"]["proposed"] for run in runs
        )),
        "frustrated_fp_event_count": int(sum(
            run["event_summary"]["full"]["counts"]["frustrated"] for run in runs
        )),
        "per_seed_comparison": [run["comparison"] for run in runs],
    }


def aggregate_sweep_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    aggregates = []
    for scale in FINAL_SCALES:
        selected = [
            run for run in runs
            if run["configuration"]["pfm_rate_scale"] == scale
        ]
        if selected:
            selected.sort(key=lambda run: run["configuration"]["seed"])
            aggregates.append(aggregate_scale_runs(selected))
    return {
        "scale_aggregates": aggregates,
        "primary_fraction_definition": (
            "accepted FP events before the 1/e lifetime divided by all accepted "
            "FP events, after concatenating event times across four seeds"
        ),
    }


def _selected_sweep_numerics(
    convergence_path: Path,
    lineage_sha256: str,
) -> tuple[float, int, dict[str, Any], str]:
    if not convergence_path.exists():
        raise FileNotFoundError(
            f"missing {convergence_path}; run the frozen convergence command first"
        )
    with convergence_path.open(encoding="utf-8") as handle:
        convergence = json.load(handle)
    if convergence.get("artifact_type") != "trajectory_convergence":
        raise ValueError("convergence artifact type is not trajectory_convergence")
    fingerprints = runtime_fingerprints()
    for name, expected in fingerprints.items():
        if convergence.get(name) != expected:
            raise ValueError(
                f"convergence {name} does not match the current frozen runtime"
            )
    if convergence.get("lineage_gate", {}).get("sha256") != lineage_sha256:
        raise ValueError("convergence was not authorized by the current lineage gate")
    if convergence.get("complete") is not True:
        raise ValueError("convergence artifact is incomplete")
    expected_runs = (
        ("candidate", FINE_DT_FS, FINE_SUBSTEPS),
        ("reference", FINER_DT_FS, FINER_SUBSTEPS),
    )
    for label, dt_fs, substeps in expected_runs:
        records = convergence.get(label, [])
        seeds = sorted(int(run["configuration"]["seed"]) for run in records)
        if seeds != list(CONVERGENCE_SEEDS):
            raise ValueError(f"convergence {label} has off-protocol seeds")
        for run in records:
            configuration = run["configuration"]
            expected = {
                "pfm_rate_scale": 0.05,
                "geometry_count": FINAL_GEOMETRY_COUNT,
                "dt_fs": dt_fs,
                "electronic_substeps": substeps,
                "total_fs": FINAL_TOTAL_FS,
            }
            for name, value in expected.items():
                if configuration.get(name) != value:
                    raise ValueError(f"convergence {label} has off-protocol {name}")
            for name, value in fingerprints.items():
                if configuration.get(name) != value:
                    raise ValueError(f"convergence {label} has foreign {name}")
    recomputed = compare_trajectory_settings(
        convergence["candidate"], convergence["reference"]
    )
    stored = convergence.get("comparison", {})
    for field in ("gate", "selected_final_numerics"):
        if canonical_json(stored.get(field)) != canonical_json(recomputed[field]):
            raise ValueError(f"stored convergence {field} is stale or edited")
    selected = recomputed["selected_final_numerics"]
    if recomputed["gate"]["passed"] is not True or selected["validated"] is not True:
        raise ValueError("multi-seed fine/finer convergence gate did not pass")
    return (
        float(selected["dt_fs"]),
        int(selected["electronic_substeps"]),
        selected,
        sha256_file(convergence_path),
    )


def require_valid_exact_audit(
    path: Path,
    *,
    lineage_sha256: str,
    convergence_sha256: str,
) -> dict[str, Any]:
    """Recompute the exact-grid gate and require a valid promoted reference."""

    if not path.is_file():
        raise FileNotFoundError(f"missing {path}; run the frozen exact-grid audit first")
    with path.open(encoding="utf-8") as handle:
        exact = json.load(handle)
    if exact.get("artifact_type") != "exact_grid_audit":
        raise ValueError("exact artifact type is not exact_grid_audit")
    fingerprints = runtime_fingerprints()
    for name, expected in fingerprints.items():
        if exact.get(name) != expected:
            raise ValueError(f"exact audit {name} does not match the current runtime")
    if exact.get("lineage_gate", {}).get("sha256") != lineage_sha256:
        raise ValueError("exact audit was not authorized by the current lineage gate")
    if exact.get("convergence_sha256") != convergence_sha256:
        raise ValueError("exact audit was not run after the current convergence gate")
    for label, grid_n in (("coarse", 384), ("fine", 512)):
        configuration = exact[label]["configuration"]
        expected_configuration = {
            "grid_n": grid_n,
            "half_width": 96.0,
            "requested_dt_fs": COARSE_DT_FS,
            "total_fs": FINAL_TOTAL_FS,
            "center_fraction": FINAL_CENTER_FRACTION,
            "momentum_kick_toward_ci_sigma_px": FINAL_MOMENTUM_KICK_SIGMA,
        }
        for name, expected in expected_configuration.items():
            if configuration.get(name) != expected:
                raise ValueError(f"exact {label} trace has off-protocol {name}")
        for name, expected in fingerprints.items():
            if configuration.get(name) != expected:
                raise ValueError(f"exact {label} trace has foreign {name}")
    recomputed = compare_exact_grids(exact["coarse"], exact["fine"])
    stored = exact.get("comparison", {})
    for field in ("gate", "production_grid_n", "production_trace", "valid_reference"):
        if canonical_json(stored.get(field)) != canonical_json(recomputed[field]):
            raise ValueError(f"stored exact-audit {field} is stale or edited")
    if not recomputed["valid_reference"]:
        raise ValueError("512-grid exact trace failed the mandatory norm gate")
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "production_grid_n": recomputed["production_grid_n"],
        "passed": True,
    }


def run_final_sweep(
    *,
    output: Path,
    convergence_path: Path,
    lineage_path: Path,
    exact_path: Path,
    workers: int = 1,
    progress: bool = False,
) -> dict[str, Any]:
    """Run/resume all 28 frozen jobs using collision-safe identities."""

    lineage_gate = require_passing_lineage(lineage_path)
    dt_fs, substeps, selected, convergence_sha256 = _selected_sweep_numerics(
        convergence_path, lineage_gate["sha256"]
    )
    exact_gate = require_valid_exact_audit(
        exact_path,
        lineage_sha256=lineage_gate["sha256"],
        convergence_sha256=convergence_sha256,
    )
    jobs = [
        {
            "pfm_rate_scale": scale,
            "seed": seed,
            "geometry_count": FINAL_GEOMETRY_COUNT,
            "dt_fs": dt_fs,
            "electronic_substeps": substeps,
            "total_fs": FINAL_TOTAL_FS,
            "progress": progress and workers == 1,
        }
        for scale in FINAL_SCALES
        for seed in FINAL_SEEDS
    ]
    declared_keys = {
        make_resume_key(**{key: value for key, value in job.items() if key != "progress"})
        for job in jobs
    }
    fingerprints = runtime_fingerprints()
    if output.exists():
        with output.open(encoding="utf-8") as handle:
            prior = json.load(handle)
        for name, expected in fingerprints.items():
            if prior.get(name) != expected:
                raise ValueError(
                    f"existing sweep {name} does not match the current runtime"
                )
        if prior.get("lineage_gate", {}).get("sha256") != lineage_gate["sha256"]:
            raise ValueError("existing sweep used a different lineage artifact")
        if prior.get("convergence_sha256") != convergence_sha256:
            raise ValueError("existing sweep used a different convergence artifact")
        if prior.get("exact_gate", {}).get("sha256") != exact_gate["sha256"]:
            raise ValueError("existing sweep used a different exact-grid artifact")
        runs = prior.get("runs", [])
    else:
        runs = []
    for run in runs:
        configuration = run.get("configuration", {})
        controls = {
            "pfm_rate_scale": configuration.get("pfm_rate_scale"),
            "seed": configuration.get("seed"),
            "geometry_count": configuration.get("geometry_count"),
            "dt_fs": configuration.get("requested_dt_fs"),
            "electronic_substeps": configuration.get("electronic_substeps"),
            "total_fs": configuration.get("total_fs"),
        }
        try:
            expected_identity = make_resume_identity(**controls)
            expected_key = make_resume_key(**controls)
        except (TypeError, ValueError) as error:
            raise ValueError("existing sweep contains an invalid run identity") from error
        if canonical_json(configuration.get("resume_identity")) != canonical_json(
            expected_identity
        ):
            raise ValueError("existing sweep contains a stale resume identity")
        if configuration.get("resume_key") != expected_key:
            raise ValueError("existing sweep contains a forged resume key")
    completed_keys = {
        run["configuration"]["resume_key"] for run in runs
    }
    if len(completed_keys) != len(runs):
        raise ValueError("existing sweep contains duplicate resume keys")
    unknown = completed_keys - declared_keys
    if unknown:
        raise ValueError("existing sweep contains runs outside the frozen contract")
    pending = [
        job for job in jobs
        if make_resume_key(**{
            key: value for key, value in job.items() if key != "progress"
        }) not in completed_keys
    ]

    def checkpoint() -> None:
        runs.sort(key=lambda run: (
            FINAL_SCALES.index(run["configuration"]["pfm_rate_scale"]),
            run["configuration"]["seed"],
        ))
        snapshot = {
            "schema_version": 1,
            "artifact_type": "final_resumable_sweep",
            "environment": environment_record(),
            **fingerprints,
            "model_contract": invariant_contract(),
            "lineage_gate": lineage_gate,
            "convergence_path": str(convergence_path),
            "convergence_sha256": convergence_sha256,
            "exact_gate": exact_gate,
            "selected_numerics": selected,
            "scales": list(FINAL_SCALES),
            "seeds": list(FINAL_SEEDS),
            "declared_replicates": len(jobs),
            "completed_replicates": len(runs),
            "complete": len(runs) == len(jobs),
            "declared_resume_keys": sorted(declared_keys),
            "runs": runs,
            "aggregate": aggregate_sweep_runs(runs) if runs else None,
        }
        write_json(output, snapshot)

    if workers <= 0:
        raise ValueError("workers must be positive")
    if workers == 1:
        for job in pending:
            runs.append(run_trajectory_regime(**job))
            checkpoint()
            print(f"completed {len(runs)}/{len(jobs)}", flush=True)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(run_trajectory_regime, **job): job for job in pending
            }
            for future in concurrent.futures.as_completed(futures):
                runs.append(future.result())
                checkpoint()
                print(f"completed {len(runs)}/{len(jobs)}", flush=True)
    checkpoint()
    with output.open(encoding="utf-8") as handle:
        return json.load(handle)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(_json_safe(data), handle, indent=2, allow_nan=False)
        handle.write("\n")
    os.replace(temporary, path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    results_dir = Path(__file__).resolve().parents[1] / "results"

    lineage = commands.add_parser("lineage", help="compare s=1 with the legacy code")
    lineage.add_argument("--output", type=Path, default=results_dir / "lineage.json")
    lineage.add_argument("--seed", type=int, default=2698)
    lineage.add_argument("--geometries", type=int, default=64)
    lineage.add_argument("--dt-fs", type=float, default=0.05)
    lineage.add_argument("--electronic-substeps", type=int, default=5)
    lineage.add_argument("--total-fs", type=float, default=0.5)

    convergence = commands.add_parser(
        "convergence", help="run the frozen multi-seed fine/finer gate"
    )
    convergence.add_argument(
        "--output", type=Path, default=results_dir / "convergence.json"
    )
    convergence.add_argument(
        "--lineage", type=Path, default=results_dir / "lineage.json"
    )
    convergence.add_argument("--workers", type=int, default=1)
    convergence.add_argument("--progress", action="store_true")
    convergence.add_argument(
        "--restart", action="store_true",
        help="discard an existing convergence checkpoint for this output path",
    )

    exact = commands.add_parser(
        "exact-audit", help="run the frozen 384^2 versus 512^2 exact audit"
    )
    exact.add_argument("--output", type=Path, default=results_dir / "exact.json")
    exact.add_argument("--lineage", type=Path, default=results_dir / "lineage.json")
    exact.add_argument(
        "--convergence", type=Path, default=results_dir / "convergence.json"
    )
    exact.add_argument("--progress", action="store_true")

    sweep = commands.add_parser("sweep", help="run or resume the frozen 28-job sweep")
    sweep.add_argument("--output", type=Path, default=results_dir / "sweep.json")
    sweep.add_argument(
        "--convergence", type=Path, default=results_dir / "convergence.json"
    )
    sweep.add_argument("--lineage", type=Path, default=results_dir / "lineage.json")
    sweep.add_argument("--exact", type=Path, default=results_dir / "exact.json")
    sweep.add_argument("--workers", type=int, default=1)
    sweep.add_argument("--progress", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    require_frozen_environment()
    print(
        f"env: Python {platform.python_version()} {platform.machine()} "
        f"| NumPy {np.__version__}",
        flush=True,
    )
    if args.command == "lineage":
        result = run_lineage_comparison(
            output=args.output,
            seed=args.seed,
            geometry_count=args.geometries,
            dt_fs=args.dt_fs,
            electronic_substeps=args.electronic_substeps,
            total_fs=args.total_fs,
        )
        print(json.dumps(result["comparison"], indent=2))
        return 0 if result["comparison"]["passed"] else 2
    if args.command == "convergence":
        result = run_trajectory_convergence(
            args.output, args.lineage, workers=args.workers,
            progress=args.progress, restart=args.restart,
        )
        print(json.dumps(result["comparison"], indent=2))
        return 0 if result["comparison"]["gate"]["passed"] else 2
    if args.command == "exact-audit":
        result = run_exact_grid_audit(
            args.output, args.lineage, args.convergence, progress=args.progress
        )
        print(json.dumps(result["comparison"], indent=2))
        return 0 if result["comparison"]["valid_reference"] else 2
    if args.command == "sweep":
        result = run_final_sweep(
            output=args.output,
            convergence_path=args.convergence,
            lineage_path=args.lineage,
            exact_path=args.exact,
            workers=args.workers,
            progress=args.progress,
        )
        return 0 if result["complete"] else 2
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
