#!/usr/bin/env python3
"""Tier 1 cross-check script (NOT RUN YET). EOM-EE-CCSD singlets + triplets (spin-adapted, RHF reference),
PySCF >= 2.14, conventional integrals, frozen core = chemcore, default basis def2-SVP (def2-TZVP only for
1 and 11 if memory allows; vvvv ~ 6.5 GB for borazine/TZVP). Exploratory: NOT part of the frozen falsifier.
Usage: python run_eomccsd_pyscf.py <id> [--basis def2-svp] [--nroots 4] [--mem-mb 20000]"""
import argparse, json, os, time, platform
import numpy as np, pyscf
from pyscf import gto, scf, cc, lib
from pyscf.data import elements
EV = 27.211386245988
p = argparse.ArgumentParser(); p.add_argument('id'); p.add_argument('--basis', default='def2-svp')
p.add_argument('--nroots', type=int, default=4); p.add_argument('--mem-mb', type=int, default=20000)
a = p.parse_args(); here = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(here, 'results'), exist_ok=True)
atom = '\n'.join(open(os.path.join(here, '..', 'xyz', f'{a.id}.xyz')).read().splitlines()[2:])
mol = gto.M(atom=atom, basis=a.basis, verbose=4, max_memory=a.mem_mb, output=os.path.join(here, 'results', f'{a.id}_eomccsd_{a.basis}.log'))
t0 = time.time(); mf = scf.RHF(mol); mf.conv_tol = 1e-10; mf.kernel(); assert mf.converged
ncore = elements.chemcore(mol)
mycc = cc.RCCSD(mf, frozen=ncore); mycc.conv_tol = 1e-8; mycc.max_memory = a.mem_mb; mycc.kernel(); assert mycc.converged
es, _ = mycc.eomee_ccsd_singlet(nroots=a.nroots); et, _ = mycc.eomee_ccsd_triplet(nroots=a.nroots)
out = dict(id=a.id, basis=a.basis, frozen_core=ncore, pyscf=pyscf.__version__, machine=platform.machine(), threads=lib.num_threads(),
           singlets_eV=[float(x)*EV for x in np.atleast_1d(es)], triplets_eV=[float(x)*EV for x in np.atleast_1d(et)], wall_s=time.time()-t0)
out['dEST_meV'] = (out['singlets_eV'][0]-out['triplets_eV'][0])*1000
json.dump(out, open(os.path.join(here, 'results', f'{a.id}_eomccsd_{a.basis}.json'), 'w'), indent=1); print(json.dumps(out))
