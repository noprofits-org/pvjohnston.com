import json, sys
from pyscf import gto
from pyscf.symm import geom
import numpy as np
idx = json.load(open('xyz/index.json'))
rows=[]
for m in idx:
    atoms = [l.split() for l in open(f"xyz/{m['id']}.xyz").read().splitlines()[2:]]
    atom = [(a[0], tuple(map(float,a[1:4]))) for a in atoms]
    r={'id':m['id'],'name':m['name'],'natoms':m['natoms'],'formula':m['formula']}
    for b in ['def2-svp','def2-tzvp']:
        mol = gto.M(atom=atom, basis=b, verbose=0, symmetry=False, spin=None)
        r[b]=mol.nao_nr()
    auxmol = gto.M(atom=atom, basis='def2-tzvp', verbose=0)
    from pyscf import df
    r['def2-tzvp-ri']=df.make_auxmol(auxmol, 'def2-tzvp-ri').nao_nr()
    r['nelec']=mol.nelectron
    # frozen core count: 1s for B,C,N,O; 1s2s2p for Al,Si,P,S; +3s3p (and 3d? ) for Ga,Ge,As,Se -> use pyscf chkcore-like
    from pyscf.data import elements
    r['nocc']=mol.nelectron//2
    r['ncore']=sum(elements.chemcore(mol) for _ in [0])
    try:
        mols = gto.M(atom=atom, basis='sto-3g', verbose=0, symmetry=True, symmetry_subgroup=None)
        r['pg_detected']=mols.topgroup
    except Exception as e:
        r['pg_detected']='err'
    rows.append(r)
    print(r, flush=True)
json.dump(rows, open('xyz/basis_counts.json','w'), indent=1)
