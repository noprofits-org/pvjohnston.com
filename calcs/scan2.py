"""Focused T-scan with dt scaled to hold the Strang error T*dt^2 fixed, and |z| tracked
so a displacement is only reported when the state is still a soliton."""
import numpy as np, json, time, sys, platform
from evolve import _expH_cache
from soliton_solver import solve_at, com_resta, unwrap_step

def run(m0, g, g12, N, T, L=60, dt0=0.02, T0=3200.0, nblocks=1500, chi0=None):
    dt = dt0*min(1.0, np.sqrt(T0/T))          # Strang error ~ T*dt^2 -> hold fixed
    psi = chi0.astype(complex).copy()
    n0 = np.vdot(psi, psi).real
    nsteps = max(int(round(T/dt)), 1); dt_eff = T/nsteps
    block = max(nsteps//nblocks, 1)
    prt = np.arange(2*L) ^ 1; hdt = -0.5j*dt_eff
    ph = np.exp(2j*np.pi*np.arange(L)/L)
    def com_z(p):
        r = p.real**2+p.imag**2; rc = r[0::2]+r[1::2]; rc = rc/rc.sum()
        zz = np.sum(rc*ph); return (L/(2*np.pi))*np.angle(zz), abs(zz)
    x, zmin = None, 1.0
    U = None; every = max(nsteps//400, 1)
    x0, _ = com_z(psi); x = x0
    for n in range(nsteps):
        if n % block == 0:
            U = _expH_cache(2*np.pi*(n+0.5)*dt_eff/T, m0, L, dt_eff)
        rho = psi.real**2+psi.imag**2
        psi *= np.exp(hdt*(g*rho + g12*rho[prt]))
        psi = U @ psi
        rho = psi.real**2+psi.imag**2
        psi *= np.exp(hdt*(g*rho + g12*rho[prt]))
        if n % every == 0 or n == nsteps-1:
            xr, z = com_z(psi); x = unwrap_step(xr, x, L); zmin = min(zmin, z)
    drift = abs(np.vdot(psi, psi).real-n0)/n0
    return x-x0, zmin, drift, dt, nsteps

if __name__ == "__main__":
    CASES = [("normal", 1.0,1.0,1.0,-1), ("anom1",-1.0,0.0,1.0,0),
             ("anom2", 1.0,0.0,1.0,-2), ("anom3", 1.0,0.0,1.3,-3)]
    TS = [400,800,1200,1600,2400,3200,4800,6400,9600,12800]
    N,L = 1.45,60
    print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}")
    print(f"N={N} L={L}, dt = 0.02*min(1, sqrt(3200/T))  [holds Strang error T*dt^2 fixed]", flush=True)
    res={}
    for name,g,g12,m0,exp in CASES:
        chi0,_,ok = solve_at(0.0,m0,g,g12,N,L); assert ok
        print(f"\n{name}: g={g} g12={g12} m0={m0}  paper adiabatic displacement = {exp}", flush=True)
        print(f"  {'T':>6} {'dt':>7} {'disp':>10} {'min|z|':>8} {'drift':>9} {'s':>6}", flush=True)
        row=[]
        for T in TS:
            t0=time.time()
            d,zmin,dr,dt,ns = run(m0,g,g12,N,float(T),L=L,chi0=chi0)
            row.append((T,float(d),float(zmin),float(dr),float(dt)))
            print(f"  {T:>6} {dt:>7.4f} {d:>10.4f} {zmin:>8.4f} {dr:>9.1e} {time.time()-t0:>6.0f}", flush=True)
        res[name]={"g":g,"g12":g12,"m0":m0,"expected":exp,"data":row}
    json.dump(res, open("scan2.json","w"), indent=1)
    print("\nwrote scan2.json", flush=True)
