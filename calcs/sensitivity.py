"""Decisive test of sensitive dependence.

Perturb the initial soliton by a relative amount eps (renormalized to the same N)
and evolve. If a 1e-12 perturbation -- far below any physical scale -- changes the
pumped displacement by O(1), the displacement is not a robust observable of the
dynamics, however 'quantized' the instantaneous branch is.
"""
import numpy as np, time
from scan2 import run
from soliton_solver import solve_at

N, L = 1.45, 60
CASES = [("normal", 1.0, 1.0, 1.0, -1), ("anom2", 1.0, 0.0, 1.0, -2)]
EPS = [0.0, 1e-12, 1e-10, 1e-8]
SEEDS = [1, 2, 3]

print("Sensitivity of the pumped displacement to a tiny initial perturbation")
print("(dt fixed by the T*dt^2 rule; only the initial condition is perturbed)\n", flush=True)
for name, g, g12, m0, exp in CASES:
    chi0, _, ok = solve_at(0.0, m0, g, g12, N, L); assert ok
    print(f"{name}: g={g} g12={g12} m0={m0}  paper adiabatic displacement = {exp}", flush=True)
    for T in (3200.0, 6400.0, 12800.0):
        print(f"  T={T:.0f}", flush=True)
        for eps in EPS:
            ds = []
            for sd in (SEEDS if eps > 0 else [0]):
                rng = np.random.default_rng(sd)
                c = chi0 + eps * rng.standard_normal(chi0.shape) * np.abs(chi0).max()
                c = c * np.sqrt(N / (c @ c))
                d, zmin, dr, dt, ns = run(m0, g, g12, N, T, L=L, chi0=c)
                ds.append(d)
            ds = np.array(ds)
            spread = ds.max() - ds.min() if len(ds) > 1 else 0.0
            vals = " ".join(f"{v:+8.4f}" for v in ds)
            print(f"    eps={eps:<7.0e} disp = {vals}   spread={spread:.4f}", flush=True)
        print(flush=True)
