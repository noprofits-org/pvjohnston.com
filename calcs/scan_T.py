import numpy as np, json, sys, time, platform
from evolve import evolve
from soliton_solver import solve_at

CASES = [("normal",    1.0, 1.0, 1.0, -1),
         ("anom1",    -1.0, 0.0, 1.0,  0),
         ("anom2",     1.0, 0.0, 1.0, -2),
         ("anom3",     1.0, 0.0, 1.3, -3)]
TS = [100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200]
N, L, DT, NB = 1.45, 60, 0.02, 1500

print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}", flush=True)
print(f"N={N} L={L} dt={DT} nblocks={NB}", flush=True)
res = {}
for name, g, g12, m0, exp in CASES:
    chi0, mu0, ok = solve_at(0.0, m0, g, g12, N, L)
    assert ok, name
    row = []
    print(f"\n{name} (g={g}, g12={g12}, m0={m0}) -- paper adiabatic displacement = {exp}", flush=True)
    print(f"  {'T':>7} {'displacement':>13} {'norm drift':>11} {'wall(s)':>8}", flush=True)
    for T in TS:
        t0 = time.time()
        d, drift = evolve(m0, g, g12, N, float(T), L=L, dt=DT, nblocks=NB, chi0=chi0)
        row.append((T, float(d), float(drift)))
        print(f"  {T:>7} {d:>13.5f} {drift:>11.1e} {time.time()-t0:>8.1f}", flush=True)
    res[name] = {"g": g, "g12": g12, "m0": m0, "expected": exp, "data": row}
json.dump(res, open("scan_T.json", "w"), indent=1)
print("\nwrote scan_T.json", flush=True)
