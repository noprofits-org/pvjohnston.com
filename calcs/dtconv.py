"""Decisive: are the erratic anomalous displacements dt-converged (physics) or not (my error)?"""
import numpy as np, time
from scan2 import run
from soliton_solver import solve_at
N,L = 1.45,60
for name,g,g12,m0,exp in [("anom2",1.0,0.0,1.0,-2), ("anom3",1.0,0.0,1.3,-3)]:
    chi0,_,ok = solve_at(0.0,m0,g,g12,N,L); assert ok
    print(f"\n{name} (g={g}, g12={g12}, m0={m0}) -- paper adiabatic displacement = {exp}", flush=True)
    print(f"  {'T':>6} {'dt0':>7} {'dt':>8} {'disp':>10} {'min|z|':>8} {'drift':>9} {'s':>5}", flush=True)
    for T in (6400.0, 9600.0, 12800.0):
        for dt0 in (0.02, 0.01, 0.005):
            t0=time.time()
            d,zmin,dr,dt,ns = run(m0,g,g12,N,T,L=L,dt0=dt0,chi0=chi0)
            print(f"  {T:>6.0f} {dt0:>7} {dt:>8.5f} {d:>10.4f} {zmin:>8.4f} {dr:>9.1e} {time.time()-t0:>5.0f}", flush=True)
