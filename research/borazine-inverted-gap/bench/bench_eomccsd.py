"""Timing smoke test ONLY. PySCF RCCSD + EOM-EE-CCSD singlets/triplets."""
import sys, time, resource, json
from pyscf import gto, scf, cc, lib
from pyscf.data import elements
mid, basis = sys.argv[1], sys.argv[2]; nroots = int(sys.argv[3]) if len(sys.argv)>3 else 3
atom = '\n'.join(open(f'../xyz/{mid}.xyz').read().splitlines()[2:])
mol = gto.M(atom=atom, basis=basis, verbose=0, max_memory=2500)
t0=time.time(); mf = scf.RHF(mol); mf.conv_tol=1e-10; mf.kernel(); t1=time.time()
ncore = elements.chemcore(mol)
mycc = cc.RCCSD(mf, frozen=ncore); mycc.max_memory=2500; mycc.conv_tol=1e-8; mycc.kernel(); t2=time.time()
es, _ = mycc.eomee_ccsd_singlet(nroots=nroots); t3=time.time()
et, _ = mycc.eomee_ccsd_triplet(nroots=nroots); t4=time.time()
ev=27.211386245988
res={'id':mid,'basis':basis,'nao':mol.nao_nr(),'frozen_core':ncore,'threads':lib.num_threads(),'t_scf_s':round(t1-t0,1),
 'ccsd_converged':bool(mycc.converged),'t_ccsd_s':round(t2-t1,1),'t_eom_singlets_s':round(t3-t2,1),'t_eom_triplets_s':round(t4-t3,1),
 'SMOKE_S_eV':[round(float(x)*ev,3) for x in es],'SMOKE_T_eV':[round(float(x)*ev,3) for x in et],
 'maxrss_MB':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)}
res['SMOKE_dEST_meV']=round((res['SMOKE_S_eV'][0]-res['SMOKE_T_eV'][0])*1000)
print(json.dumps(res),flush=True); open('bench_results.jsonl','a').write(json.dumps({'kind':'pyscf-eomccsd',**res})+'\n')
