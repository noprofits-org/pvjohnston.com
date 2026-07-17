"""
Definitive, convergence-gated T-scan. One integrator (4th-order Yoshida), one
adaptive step-size rule per period, one output the tables are rebuilt from.

For each pump period T, halve dt until two successive step sizes agree within
`tol`; report that value and a `converged` flag. Periods that do not converge even
at the finest dt are reported as such, not silently kept -- the excursions are
sharp near-resonances where dt convergence is itself T-dependent, and hiding that
is the error this rerun exists to correct.

Usage:  python3 converge.py <normal|anom1|anom2>
Writes: conv_<case>.jsonl (one line per T, incremental) and conv_<case>.done
"""
import sys, json, numpy as np
from evolve4 import evolve4
from soliton_solver import solve_at

CASES = {
    "normal": (1.0, 1.0, 1.0, -1),
    "anom1":  (-1.0, 0.0, 1.0, 0),
    "anom2":  (1.0, 0.0, 1.0, -2),
}
N, L = 1.45, 60
TOL = 0.02
DTS = [0.02, 0.01, 0.005, 0.0025]
TS = list(range(400, 12001, 400))


def converged_disp(m0, g, g12, T, chi0):
    vals, zmins, dts_used = [], [], []
    for dt in DTS:
        d, zmin, dr, h, ns = evolve4(m0, g, g12, N, float(T), L=L, dt=dt, chi0=chi0)
        vals.append(float(d)); zmins.append(float(zmin)); dts_used.append(dt)
        if len(vals) >= 2 and abs(vals[-1] - vals[-2]) < TOL:
            return vals[-1], min(zmins), True, dt, list(zip(dts_used, vals))
    return vals[-1], min(zmins), False, DTS[len(vals) - 1], list(zip(dts_used, vals))


if __name__ == "__main__":
    case = sys.argv[1]
    g, g12, m0, exp = CASES[case]
    chi0, _, ok = solve_at(0.0, m0, g, g12, N, L)
    assert ok, f"seed failed for {case}"
    out = open(f"conv_{case}.jsonl", "w")
    print(f"# {case}: g={g} g12={g12} m0={m0} exp={exp}", flush=True)
    print(f"# {'T':>6} {'disp':>10} {'conv':>5} {'dt':>7} {'min|z|':>8}", flush=True)
    for T in TS:
        d, zmin, conv, dt, ladder = converged_disp(m0, g, g12, T, chi0)
        rec = {"T": T, "disp": d, "converged": conv, "dt": dt,
               "min_z": zmin, "ladder": ladder, "exp": exp}
        out.write(json.dumps(rec) + "\n"); out.flush()
        print(f"  {T:>6} {d:>10.4f} {str(conv):>5} {dt:>7} {zmin:>8.4f}", flush=True)
    out.close()
    open(f"conv_{case}.done", "w").write("ok\n")
    print(f"# {case} DONE", flush=True)
