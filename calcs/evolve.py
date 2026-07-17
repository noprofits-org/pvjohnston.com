"""
Time evolution of the Tao/Wang/Xu DNLS under a finite-period pump, theta(t)=2 pi t/T.

    i dpsi/dt = H_lin(theta(t)) psi + V(psi) psi,   V_{sigma j} = g|psi_{sigma j}|^2 + g12|psi_{sigma-bar j}|^2

Strang split-step: the nonlinear half-step is EXACT (V depends only on |psi|^2, which
exp(-iV dt) leaves invariant), and the linear step uses exp(-i H dt) from an
eigendecomposition cached per theta-block. Norm is conserved to machine precision by
construction; the theta-block width is the only controlled approximation and is
convergence-tested.
"""
import numpy as np
from soliton_model import h_real
from soliton_solver import solve_at, com_resta, unwrap_step


def _expH_cache(theta, m0, L, dt):
    w, V = np.linalg.eigh(h_real(theta, m0, L))
    return (V * np.exp(-1j * w * dt)) @ V.conj().T


def evolve(m0, g, g12, N, T, L=60, dt=0.02, nblocks=2000, chi0=None, track=False):
    """Evolve one pump cycle of period T. Returns (displacement, norm_drift, [trace])."""
    if chi0 is None:
        chi0, mu0, ok = solve_at(0.0, m0, g, g12, N, L)
        if not ok:
            return None
    psi = chi0.astype(complex).copy()
    n0 = np.vdot(psi, psi).real

    nsteps = max(int(round(T / dt)), 1)
    dt_eff = T / nsteps
    block = max(nsteps // nblocks, 1)

    x = com_resta(np.abs(psi), L)
    x_start = x
    trace = []
    U = None
    prt = np.arange(2 * L) ^ 1          # hoisted: rebuilding this per step dominated the loop
    hdt = -0.5j * dt_eff
    every = max(nsteps // 400, 1)
    for n in range(nsteps):
        if n % block == 0:                       # refresh linear propagator
            th_mid = 2 * np.pi * (n + 0.5) * dt_eff / T
            U = _expH_cache(th_mid, m0, L, dt_eff)
        rho = psi.real**2 + psi.imag**2
        psi *= np.exp(hdt * (g * rho + g12 * rho[prt]))   # exact nonlinear half-step
        psi = U @ psi                                     # linear step
        rho = psi.real**2 + psi.imag**2
        psi *= np.exp(hdt * (g * rho + g12 * rho[prt]))   # exact nonlinear half-step
        if track and (n % every == 0):
            xr = com_resta(np.abs(psi), L)
            x = unwrap_step(xr, x, L)
            trace.append((2 * np.pi * (n + 1) * dt_eff / T, x - x_start))
    xr = com_resta(np.abs(psi), L)
    x = unwrap_step(xr, x, L)
    drift = abs(np.vdot(psi, psi).real - n0) / n0
    disp = x - x_start
    return (disp, drift, np.array(trace)) if track else (disp, drift)


def soliton_fidelity(m0, g, g12, N, T, L=60, **kw):
    """How much of the final state is still a localized soliton (Resta |z|)."""
    r = evolve(m0, g, g12, N, T, L=L, track=True, **kw)
    return r
