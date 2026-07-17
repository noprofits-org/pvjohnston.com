"""
Sensitive-dependence test at the EXCURSION period, under the 4th-order integrator.

The original sensitivity.py tested T = 3200/6400/12800 with the Strang-based
scan2.run -- neither the excursion period (T=9600) nor the deprecated integrator.
This retests at T=9600 (and 8800, the other large excursion) with evolve4, so the
determinism claim is checked for the scenario it is used to explain.
"""
import numpy as np
from evolve4 import evolve4
from soliton_solver import solve_at

N, L = 1.45, 60


def run_pert(m0, g, g12, T, chi0, eps, seed, dt=0.01):
    rng = np.random.default_rng(seed)
    c = chi0 + eps * rng.standard_normal(chi0.shape) * np.abs(chi0).max()
    c = c * np.sqrt(N / (c @ c))
    d, zmin, dr, h, ns = evolve4(m0, g, g12, N, float(T), L=L, dt=dt, chi0=c)
    return d


if __name__ == "__main__":
    import sys, platform
    print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}")
    print("4th-order Yoshida, dt=0.01. Perturb initial soliton, measure displacement spread.\n", flush=True)
    g, g12, m0, exp = 1.0, 0.0, 1.0, -2
    chi0, _, ok = solve_at(0.0, m0, g, g12, N, L); assert ok
    for T in (8800.0, 9600.0):
        base = run_pert(m0, g, g12, T, chi0, 0.0, 0)
        print(f"anom2 T={T:.0f}  unperturbed disp = {base:+.4f}", flush=True)
        for eps in (1e-12, 1e-10, 1e-8):
            ds = [run_pert(m0, g, g12, T, chi0, eps, sd) for sd in (1, 2, 3)]
            spread = max(ds) - min(ds)
            print(f"  eps={eps:.0e}: {' '.join(f'{v:+.4f}' for v in ds)}   spread={spread:.4f}", flush=True)
        print(flush=True)
    open("sensitivity4.done", "w").write("ok\n")
