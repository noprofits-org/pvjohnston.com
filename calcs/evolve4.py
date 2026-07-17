"""
4th-order Yoshida-composed split-step for the DNLS.

Strang S2(h) has error ~ h^3/step, i.e. ~ T h^2 over a pump cycle. Near the
intersite-soliton branch point the anomalous outcome turns on the trajectory at the
~1e-1 level, which T h^2 does not resolve at accessible h. Yoshida composition

    S4(h) = S2(w1 h) S2(w0 h) S2(w1 h),
    w1 = 1/(2 - 2^(1/3)),  w0 = -2^(1/3)/(2 - 2^(1/3))

is 4th order: error ~ T h^4. Three Strang substeps per step, so ~3x cost per step,
but h can be far larger at equal accuracy.

The nonlinear substep remains exact (V depends only on |psi|^2, which the phase
rotation preserves), so the norm is conserved to machine precision as before.
"""
import numpy as np
from soliton_model import h_real
from soliton_solver import solve_at, com_resta, unwrap_step

CBRT2 = 2.0 ** (1.0 / 3.0)
W1 = 1.0 / (2.0 - CBRT2)
W0 = -CBRT2 / (2.0 - CBRT2)
assert abs(2 * W1 + W0 - 1.0) < 1e-14


def _prop(theta, m0, L, h):
    w, V = np.linalg.eigh(h_real(theta, m0, L))
    return (V * np.exp(-1j * w * h)) @ V.conj().T


def evolve4(m0, g, g12, N, T, L=60, dt=0.02, nblocks=1500, chi0=None, nsample=400):
    if chi0 is None:
        chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
        if not ok:
            return None
    psi = chi0.astype(complex).copy()
    n0 = np.vdot(psi, psi).real
    nsteps = max(int(round(T / dt)), 1)
    h = T / nsteps
    block = max(nsteps // nblocks, 1)
    prt = np.arange(2 * L) ^ 1
    ph = np.exp(2j * np.pi * np.arange(L) / L)

    def com_z(p):
        r = p.real**2 + p.imag**2
        rc = r[0::2] + r[1::2]
        rc = rc / rc.sum()
        z = np.sum(rc * ph)
        return (L / (2 * np.pi)) * np.angle(z), abs(z)

    def strang(p, U, hh):
        rho = p.real**2 + p.imag**2
        p = p * np.exp(-0.5j * hh * (g * rho + g12 * rho[prt]))
        p = U @ p
        rho = p.real**2 + p.imag**2
        return p * np.exp(-0.5j * hh * (g * rho + g12 * rho[prt]))

    x0, _ = com_z(psi)
    x, zmin = x0, 1.0
    U1 = U0 = None
    every = max(nsteps // nsample, 1)
    for n in range(nsteps):
        if n % block == 0:
            th = 2 * np.pi * (n + 0.5) * h / T
            U1 = _prop(th, m0, L, W1 * h)
            U0 = _prop(th, m0, L, W0 * h)
        psi = strang(psi, U1, W1 * h)
        psi = strang(psi, U0, W0 * h)
        psi = strang(psi, U1, W1 * h)
        if n % every == 0 or n == nsteps - 1:
            xr, z = com_z(psi)
            x = unwrap_step(xr, x, L)
            zmin = min(zmin, z)
    drift = abs(np.vdot(psi, psi).real - n0) / n0
    return x - x0, zmin, drift, h, nsteps


if __name__ == "__main__":
    import time, sys, platform
    print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}")
    N, L = 1.45, 60
    print("\n4th-order Yoshida: dt-convergence where Strang failed")
    for name, g, g12, m0, exp in [("normal", 1.0, 1.0, 1.0, -1), ("anom2", 1.0, 0.0, 1.0, -2),
                                  ("anom3", 1.0, 0.0, 1.3, -3)]:
        chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
        assert ok
        print(f"\n{name}: g={g} g12={g12} m0={m0}  paper adiabatic displacement = {exp}", flush=True)
        print(f"  {'T':>6} {'dt':>7} {'disp':>10} {'min|z|':>8} {'drift':>9} {'s':>5}", flush=True)
        for T in (6400.0, 9600.0, 12800.0):
            for dt in (0.04, 0.02, 0.01):
                t0 = time.time()
                d, zmin, dr, h, ns = evolve4(m0, g, g12, N, float(T), L=L, dt=dt, chi0=chi0)
                print(f"  {T:>6.0f} {dt:>7} {d:>10.4f} {zmin:>8.4f} {dr:>9.1e} {time.time()-t0:>5.0f}", flush=True)
