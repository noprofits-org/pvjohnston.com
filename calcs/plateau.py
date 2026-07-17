"""Is the anomalous -2 a quantized PLATEAU or a coincidental CROSSING?

A quantized displacement must be FLAT in the pump period: that is what quantized
means. Scan T finely with the 4th-order integrator. A plateau at -2 supports
quantization under time evolution; a curve that merely passes through -2 means the
agreement at T=6400 was an accident of where it happened to cross.

The normal case is the positive control: it must show a plateau at -1.
"""
import numpy as np, json
from evolve4 import evolve4
from soliton_solver import solve_at

N, L, DT = 1.45, 60, 0.03
TS = list(range(4000, 12001, 400))

if __name__ == "__main__":
    import sys, platform
    print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}")
    print(f"4th-order Yoshida, dt={DT}, N={N}, L={L}\n", flush=True)
    res = {}
    for name, g, g12, m0, exp in [("normal", 1.0, 1.0, 1.0, -1), ("anom2", 1.0, 0.0, 1.0, -2)]:
        chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
        assert ok
        print(f"{name}: g={g} g12={g12} m0={m0}  paper adiabatic displacement = {exp}", flush=True)
        print(f"  {'T':>6} {'disp':>10} {'min|z|':>8}", flush=True)
        row = []
        for T in TS:
            d, zmin, dr, h, ns = evolve4(m0, g, g12, N, float(T), L=L, dt=DT, chi0=chi0)
            row.append((T, float(d), float(zmin)))
            print(f"  {T:>6} {d:>10.4f} {zmin:>8.4f}", flush=True)
        res[name] = row
        print(flush=True)
    json.dump(res, open("plateau.json", "w"), indent=1)
    print("wrote plateau.json", flush=True)
