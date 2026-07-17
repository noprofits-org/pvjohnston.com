"""
Is the large-T degradation of the pumped displacement numerics or physics?

Two independent tests:
 1. CONVERGENCE. Halve dt and double the theta-block count at fixed T. If the
    displacement moves toward the quantized value, it was integrator error.
 2. LOCALIZATION. Track the Resta amplitude |z| and the participation ratio over
    the cycle. If the soliton sheds radiation, |z| falls and the centre of mass is
    contaminated -- the displacement is then not measuring a soliton at all.
"""
import numpy as np
from evolve import evolve, _expH_cache
from soliton_solver import solve_at, com_resta, unwrap_step


def evolve_diag(m0, g, g12, N, T, L=60, dt=0.02, nblocks=1500, chi0=None, nsample=300):
    if chi0 is None:
        chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
        assert ok
    psi = chi0.astype(complex).copy()
    n0 = np.vdot(psi, psi).real
    nsteps = max(int(round(T / dt)), 1)
    dt_eff = T / nsteps
    block = max(nsteps // nblocks, 1)
    prt = np.arange(2 * L) ^ 1
    hdt = -0.5j * dt_eff
    j = np.arange(L)
    ph = np.exp(2j * np.pi * j / L)
    x = com_resta(np.abs(psi), L); x0 = x
    every = max(nsteps // nsample, 1)
    rec = []
    U = None
    for n in range(nsteps):
        if n % block == 0:
            U = _expH_cache(2 * np.pi * (n + 0.5) * dt_eff / T, m0, L, dt_eff)
        rho = psi.real**2 + psi.imag**2
        psi *= np.exp(hdt * (g * rho + g12 * rho[prt]))
        psi = U @ psi
        rho = psi.real**2 + psi.imag**2
        psi *= np.exp(hdt * (g * rho + g12 * rho[prt]))
        if n % every == 0 or n == nsteps - 1:
            r = psi.real**2 + psi.imag**2
            rc = (r[0::2] + r[1::2]); rc = rc / rc.sum()
            z = abs(np.sum(rc * ph))
            x = unwrap_step((L / (2 * np.pi)) * np.angle(np.sum(rc * ph)), x, L)
            rec.append((2 * np.pi * (n + 1) * dt_eff / T, x - x0, z, 1.0 / (rc**2).sum()))
    drift = abs(np.vdot(psi, psi).real - n0) / n0
    return np.array(rec), drift


if __name__ == "__main__":
    N, L = 1.45, 60
    m0, g, g12 = 1.0, 1.0, 1.0     # normal case
    chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
    assert ok

    print("TEST 1 -- convergence at fixed T (normal case)")
    print(f"  {'T':>7} {'dt':>6} {'nblocks':>8} | {'displacement':>13} {'drift':>9}")
    for T in (6400.0, 25600.0):
        for dt, nb in ((0.02, 1500), (0.01, 3000), (0.005, 6000)):
            d, dr = evolve(m0, g, g12, N, T, L=L, dt=dt, nblocks=nb, chi0=chi0)
            print(f"  {T:>7.0f} {dt:>6} {nb:>8} | {d:>13.5f} {dr:>9.1e}", flush=True)

    print("\nTEST 1b -- lattice size at fixed T (normal case)")
    print("  On a ring, shed radiation cannot escape: it laps the lattice and re-interacts")
    print("  with the soliton. That would degrade long-T runs specifically. The paper does")
    print("  not state its lattice size.")
    print(f"  {'T':>7} {'L':>5} | {'displacement':>13} {'drift':>9}")
    for T in (6400.0, 25600.0):
        for LL in (60, 100, 160):
            c0, _, ok = solve_at(0.0, m0, g, g12, N, LL)
            if not ok:
                print(f"  {T:>7.0f} {LL:>5} | seed FAILED"); continue
            d, dr = evolve(m0, g, g12, N, T, L=LL, dt=0.02, nblocks=1500, chi0=c0)
            print(f"  {T:>7.0f} {LL:>5} | {d:>13.5f} {dr:>9.1e}", flush=True)

    print("\nTEST 2 -- localization over the cycle (normal case)")
    print(f"  {'T':>7} | {'|z| start':>9} {'|z| end':>8} {'partic start':>12} {'partic end':>11} {'disp':>9}")
    for T in (3200.0, 6400.0, 25600.0):
        rec, dr = evolve_diag(m0, g, g12, N, T, L=L, chi0=chi0)
        print(f"  {T:>7.0f} | {rec[0,2]:>9.4f} {rec[-1,2]:>8.4f} {rec[0,3]:>12.3f} {rec[-1,3]:>11.3f} {rec[-1,1]:>9.4f}", flush=True)
        np.save(f"diag_T{int(T)}.npy", rec)
