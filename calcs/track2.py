import numpy as np
from soliton_solver import solve_at, newton, com_resta, unwrap_step
from wannier import wannier

def wannier_center_track(m0, L=60, nth=1441):
    """Follow the Wannier center continuously over the cycle -> should equal the Chern number."""
    th = np.linspace(0, 2*np.pi, nth)
    c, W, _ = wannier(0.0, m0, L)
    n = int(np.argmin(np.abs(c - L//2)))
    x = c[n]; xs = [x]
    for t in th[1:]:
        c, W, _ = wannier(t, m0, L)
        # nearest center to previous, on the ring
        d = (c - x) % L
        d[d > L/2] -= L
        k = int(np.argmin(np.abs(d)))
        x = x + d[k]
        xs.append(x)
    return th, np.array(xs) - xs[0]

def soliton_track(m0, g, g12, N=1.45, L=60, nth=1441):
    th = np.linspace(0, 2*np.pi, nth)
    chi, mu, ok = solve_at(0.0, m0, g, g12, N, L)
    if not ok: return None
    xs, mus, prt, errs = [], [], [], []
    x = com_resta(chi, L)
    for i, t in enumerate(th):
        chi, mu, ok, err = newton(chi, mu, t, m0, g, g12, N, L)
        if not ok: return None
        xr = com_resta(chi, L)
        x = unwrap_step(xr, x, L) if i else xr
        rho = chi[0::2]**2 + chi[1::2]**2; rho = rho/rho.sum()
        xs.append(x); mus.append(mu); prt.append(1/(rho**2).sum()); errs.append(err)
    xs = np.array(xs)
    return th, xs - xs[0], np.array(mus), np.array(prt), max(errs)

if __name__ == "__main__":
    print("Linear reference: Wannier-center displacement over one cycle (= Chern number)")
    for m0 in (1.0, 1.3):
        th, x = wannier_center_track(m0)
        print(f"  m0={m0}: displacement = {x[-1]:+.6f}   max|step| = {np.abs(np.diff(x)).max():.4f}")

    print("\nSoliton tracking, N=1.45, L=60, 1441 theta steps")
    print(f"{'case':<22}{'g':>5}{'g12':>6}{'m0':>6} | {'paper':>6} {'measured':>10} {'max|dx|':>9} {'partic@pi':>10}")
    print("-"*80)
    for name, g, g12, m0, exp in [("black / normal",1.,1.,1.,-1), ("blue / anom 1",-1.,0.,1.,0),
                                   ("red / anom 2",1.,0.,1.,-2), ("gold / anom 3",1.,0.,1.3,-3)]:
        r = soliton_track(m0, g, g12)
        if r is None:
            print(f"{name:<22}{g:>5}{g12:>6}{m0:>6} | {exp:>6} {'FAILED':>10}"); continue
        th, x, mu, prt, err = r
        ipi = np.argmin(np.abs(th - np.pi))
        print(f"{name:<22}{g:>5}{g12:>6}{m0:>6} | {exp:>6} {x[-1]:>10.4f} {np.abs(np.diff(x)).max():>9.4f} {prt[ipi]:>10.3f}")
