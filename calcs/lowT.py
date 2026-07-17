"""4th-order scan at low T: locate the adiabatic threshold cleanly for both cases."""
import numpy as np, json
from evolve4 import evolve4
from soliton_solver import solve_at
N, L, DT = 1.45, 60, 0.03
TS = list(range(400, 5601, 400))
if __name__ == "__main__":
    res = {}
    for name, g, g12, m0, exp in [("normal",1.0,1.0,1.0,-1), ("anom2",1.0,0.0,1.0,-2)]:
        chi0,_,ok = solve_at(0.0,m0,g,g12,N,L); assert ok
        print(f"\n{name}: paper adiabatic displacement = {exp}", flush=True)
        print(f"  {'T':>6} {'disp':>10} {'|dev|':>8} {'min|z|':>8}", flush=True)
        row=[]
        for T in TS:
            d,zmin,dr,h,ns = evolve4(m0,g,g12,N,float(T),L=L,dt=DT,chi0=chi0)
            row.append((T,float(d),float(zmin)))
            print(f"  {T:>6} {d:>10.4f} {abs(d-exp):>8.4f} {zmin:>8.4f}", flush=True)
        res[name]=row
    json.dump(res, open("lowT.json","w"), indent=1)
    print("\nwrote lowT.json", flush=True)
