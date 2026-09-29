import re, json, os
lines = open('SI1.txt').read().splitlines()
hdr = re.compile(r'Supplementary Table (\d+) \| Nuclear coordinates of S0 geometry of (\S+): (.+?) at the')
atom = re.compile(r'^\s*([A-Z][a-z]?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$')
mols = []; cur=None
for i,l in enumerate(lines):
    m = hdr.search(l)
    if m:
        cur = dict(table=int(m.group(1)), id=m.group(2), name=m.group(3).strip(), atoms=[], line=i+1); mols.append(cur); continue
    if cur is None: continue
    a = atom.match(l)
    if a: cur['atoms'].append((a.group(1), *map(float, a.group(2,3,4))))
    elif l.strip().startswith('Supplementary') : cur=None
os.makedirs('xyz', exist_ok=True)
from collections import Counter
out=[]
for m in mols:
    c = Counter(a[0] for a in m['atoms'])
    formula = ''.join(f"{e}{c[e]}" for e in sorted(c))
    fn = f"xyz/{m['id']}.xyz"
    with open(fn,'w') as f:
        f.write(f"{len(m['atoms'])}\n{m['id']}: {m['name']} S0 PBE0/6-31G(d), Shizu et al. Commun. Chem. 2026 SI Table {m['table']}\n")
        for a in m['atoms']: f.write(f"{a[0]:2s} {a[1]:12.6f} {a[2]:12.6f} {a[3]:12.6f}\n")
    out.append(dict(id=m['id'],name=m['name'],table=m['table'],natoms=len(m['atoms']),formula=formula))
    print(m['table'], m['id'], m['name'], len(m['atoms']), formula)
json.dump(out, open('xyz/index.json','w'), indent=1)
