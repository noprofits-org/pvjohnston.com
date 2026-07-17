import numpy as np, sys, platform
from soliton_solver import track_cycle
print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}")
print("\nGATE: reproduce Fig 2a displacements (N=1.45, L=60, 361 theta steps)")
print(f"{'case':<24}{'g':>5}{'g12':>6}{'m0':>6} | {'paper':>6} {'measured':>10} {'max|dx| step':>13} {'resid':>10}")
print("-"*82)
cases = [("black / normal",    1.0, 1.0, 1.0, -1),
         ("blue / anomalous 1",-1.0, 0.0, 1.0,  0),
         ("red / anomalous 2",  1.0, 0.0, 1.0, -2),
         ("gold / anomalous 3", 1.0, 0.0, 1.3, -3)]
out = {}
for name, g, g12, m0, expect in cases:
    r = track_cycle(m0, g, g12, 1.45, L=60, nth=361)
    if r is None:
        print(f"{name:<24}{g:>5}{g12:>6}{m0:>6} | {expect:>6} {'FAILED':>10}"); continue
    th, x, mu, err = r
    out[name] = (th, x, mu)
    print(f"{name:<24}{g:>5}{g12:>6}{m0:>6} | {expect:>6} {x[-1]:>10.4f} {np.abs(np.diff(x)).max():>13.4f} {err:>10.1e}")
np.savez("gate_out.npz", **{k: np.vstack([v[0], v[1], v[2]]) for k, v in out.items()})
