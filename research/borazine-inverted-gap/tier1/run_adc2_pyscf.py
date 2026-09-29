#!/usr/bin/env python3
"""Tier 1 production script (NOT RUN YET). ADC(2)/def2-TZVP singlets + triplets on the published
PBE0/6-31G(d) S0 geometry (Shizu et al., Commun. Chem. 2026, SI Tables 9-54), unchanged.

Engine: PySCF >= 2.14 DF-ADC(2).
  singlets : spin-adapted RADC(2)-ee            (pyscf.adc, method_type='ee')
  triplets : UADC(2)-ee on the RHF solution (Ms=0 manifold contains singlets AND triplets);
             triplet roots are those with <S^2> ~ 2 (compute_spin_square=True), cross-checked
             against the RADC singlet list (any UADC root not matching a RADC singlet within 2 meV).
Settings (frozen in PREREGISTRATION.md):
  basis def2-TZVP; RI auxiliary def2-TZVP-RI (ADC step); SCF conventional RHF, conv_tol 1e-10;
  frozen core = pyscf.data.elements.chemcore (B,C,N,O: 1s; S: 1s2s2p; Ga,Se: 1s-3p, 3d active);
  Davidson conv_tol 1e-6 Eh (PySCF default for ADC); nroots singlet 4, UADC 8.
Usage: python run_adc2_pyscf.py <id> [--basis def2-tzvp] [--aux def2-tzvp-ri] [--mem-mb 20000]
Writes results/<id>_adc2_<basis>.json.  No number from this script is a result until the
canonical run under PREREGISTRATION.md.
"""
import argparse, json, os, platform, time
import numpy as np
import pyscf
from pyscf import gto, scf, adc, lib
from pyscf.data import elements
EV = 27.211386245988
p = argparse.ArgumentParser()
p.add_argument('id'); p.add_argument('--basis', default='def2-tzvp'); p.add_argument('--aux', default='def2-tzvp-ri')
p.add_argument('--mem-mb', type=int, default=20000); p.add_argument('--nroots-s', type=int, default=4)
p.add_argument('--nroots-u', type=int, default=8); p.add_argument('--skip-triplets', action='store_true')
a = p.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
xyz = os.path.join(here, '..', 'xyz', f'{a.id}.xyz')
atom = '\n'.join(open(xyz).read().splitlines()[2:])
os.makedirs(os.path.join(here, 'results'), exist_ok=True)
mol = gto.M(atom=atom, basis=a.basis, charge=0, spin=0, verbose=4, max_memory=a.mem_mb,
            output=os.path.join(here, 'results', f'{a.id}_adc2_{a.basis}.log'))
t0 = time.time()
mf = scf.RHF(mol); mf.conv_tol = 1e-10; mf.conv_tol_grad = 1e-7; mf.max_cycle = 200; mf.kernel()
assert mf.converged, 'SCF not converged: stop, do not report'
ncore = elements.chemcore(mol)
out = dict(id=a.id, basis=a.basis, aux=a.aux, nao=mol.nao_nr(), nelec=mol.nelectron, frozen_core=ncore,
           e_hf=mf.e_tot, pyscf=pyscf.__version__, numpy=np.__version__, python=platform.python_version(),
           machine=platform.machine(), threads=lib.num_threads(), t_scf_s=time.time()-t0)
t1 = time.time()
ra = adc.ADC(mf, frozen=ncore).density_fit(a.aux); ra.method = 'adc(2)'; ra.method_type = 'ee'; ra.max_memory = a.mem_mb
es, vs, ps, _ = ra.kernel(nroots=a.nroots_s)
out.update(singlets_eV=[float(x)*EV for x in es], singlets_f=[float(x) for x in ps], t_radc_s=time.time()-t1)
if not a.skip_triplets:
    t2 = time.time()
    umf = scf.addons.convert_to_uhf(mf)
    ua = adc.ADC(umf, frozen=(ncore, ncore)).density_fit(a.aux); ua.method = 'adc(2)'; ua.method_type = 'ee'
    ua.max_memory = a.mem_mb; ua.compute_spin_square = False
    eu, vu, pu, _ = ua.kernel(nroots=a.nroots_u)
    try:
        s2, _ = ua._adc_es.get_spin_square()   # <S^2> of each Ms=0 root (PySCF 2.14 internals)
    except Exception as ex:
        print('spin_square unavailable, falling back to RADC matching:', ex); s2 = None
    out.update(uadc_eV=[float(x)*EV for x in eu], uadc_f=[float(x) for x in pu],
               uadc_s2=[float(x) for x in s2] if s2 is not None else None, t_uadc_s=time.time()-t2)
    sing = np.array(out['singlets_eV'])
    trip = [e for i, e in enumerate(out['uadc_eV'])
            if (out['uadc_s2'] is not None and abs(out['uadc_s2'][i]-2.0) < 0.3)
            or (out['uadc_s2'] is None and np.min(np.abs(sing-e)) > 2e-3)]
    out['triplets_eV'] = trip
    out['S1_eV'] = float(sing[0]); out['T1_eV'] = float(trip[0]) if trip else None
    out['dEST_meV'] = (out['S1_eV']-out['T1_eV'])*1000 if trip else None
json.dump(out, open(os.path.join(here, 'results', f'{a.id}_adc2_{a.basis}.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in out if k in ('id', 'S1_eV', 'T1_eV', 'dEST_meV')}))
