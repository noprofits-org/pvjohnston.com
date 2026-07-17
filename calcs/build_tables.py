"""Rebuild every table in the post from the converged scan. Run converge.py first
(one process per case), then this. Prints Table 2 (displacements) and Table 3
(threshold + excursion statistics), plus the |z| ranges and the T_c ratio."""
import json, glob, numpy as np

BAND = 0.15
def load(case):
    rows = [json.loads(l) for l in open(f"conv_{case}.jsonl")]
    return {r["T"]: r for r in rows}

cases = {c: load(c) for c in ("normal", "anom1", "anom2") if glob.glob(f"conv_{c}.jsonl")}

print("=== convergence flags ===")
for c, d in cases.items():
    nonconv = [T for T, r in sorted(d.items()) if not r["converged"]]
    print(f"  {c}: {len(nonconv)} of {len(d)} periods did not converge at dt>=0.0025: {nonconv}")

print("\n=== |z| ranges over ALL tested periods ===")
for c, d in cases.items():
    zs = [r["min_z"] for r in d.values()]
    print(f"  {c}: min|z| in [{min(zs):.4f}, {max(zs):.4f}]")

for c, exp in (("normal", -1), ("anom2", -2)):
    if c not in cases: continue
    d = cases[c]
    Ts = sorted(d)
    dev = {T: abs(d[T]["disp"] - exp) for T in Ts}
    conv = {T: d[T]["converged"] for T in Ts}
    Tc = next((T for T in Ts if dev[T] < BAND and conv[T]), None)
    above = [T for T in Ts if T >= Tc]
    conv_above = [T for T in above if conv[T]]
    out = [T for T in conv_above if dev[T] >= BAND]
    arr = np.array([d[T]["disp"] for T in conv_above])
    print(f"\n=== {c} (exp {exp}) ===")
    print(f"  T_c (first converged period in band) = {Tc}")
    print(f"  converged periods at/above T_c        = {len(conv_above)} of {len(above)}")
    print(f"  of those, OUTSIDE band                = {len(out)}  {out}")
    if len(above) != len(conv_above):
        print(f"  (non-converged above T_c, excluded)   = {[T for T in above if not conv[T]]}")
    print(f"  max |dev| (converged)                 = {max(dev[T] for T in conv_above):.3f} at T={max(conv_above, key=lambda T: dev[T])}")
    print(f"  mean disp (converged)                 = {arr.mean():+.4f}  pop sd = {arr.std():.4f}")

if "normal" in cases and "anom2" in cases:
    print(f"\nT_c ratio = see values above")
