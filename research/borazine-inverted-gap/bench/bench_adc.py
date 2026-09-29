"""Timing smoke test ONLY. Not a result. adcc ADC(2) singlets+triplets on published S0 geometry."""
import sys, time, resource, json, os
import numpy as np
from pyscf import gto, scf
import adcc
mid, basis = sys.argv[1], sys.argv[2]
nroots = int(sys.argv[3]) if len(sys.argv) > 3 else 3
fc = (sys.argv[4] if len(sys.argv) > 4 else 'fc') == 'fc'
nthr = int(os.environ.get('OMP_NUM_THREADS', '1'))
adcc.set_n_threads(nthr)
lines = open(f'../xyz/{mid}.xyz').read().splitlines()[2:]
atom = '\n'.join(lines)
mol = gto.M(atom=atom, basis=basis, verbose=0, max_memory=2500)
t0 = time.time()
mf = scf.RHF(mol); mf.conv_tol = 1e-10; mf.conv_tol_grad = 1e-7; mf.kernel()
t1 = time.time()
from pyscf.data import elements
ncore = elements.chemcore(mol) if fc else None
res = {'id': mid, 'basis': basis, 'nao': mol.nao_nr(), 'nocc': mol.nelectron//2, 'frozen_core': ncore, 'threads': nthr,
       'scf_converged': bool(mf.converged), 't_scf_s': round(t1-t0, 1)}
t2 = time.time()
s = adcc.adc2(mf, n_singlets=nroots, frozen_core=ncore, conv_tol=1e-6)
t3 = time.time()
tr = adcc.adc2(mf, n_triplets=nroots, frozen_core=ncore, conv_tol=1e-6)
t4 = time.time()
ev = 27.211386245988
res.update({'t_adc2_singlets_s': round(t3-t2, 1), 't_adc2_triplets_s': round(t4-t3, 1),
            'maxrss_MB': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),
            'SMOKE_S_eV': [round(x*ev, 3) for x in s.excitation_energy],
            'SMOKE_T_eV': [round(x*ev, 3) for x in tr.excitation_energy],
            'SMOKE_S_osc': [round(x, 4) for x in s.oscillator_strength]})
res['SMOKE_dEST_meV'] = round((res['SMOKE_S_eV'][0]-res['SMOKE_T_eV'][0])*1000)
print(json.dumps(res), flush=True)
with open('bench_results.jsonl', 'a') as f: f.write(json.dumps({'kind': 'adcc-adc2', **res})+'\n')
