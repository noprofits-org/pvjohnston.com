"""Timing smoke test ONLY. PySCF DF-ADC(2): RADC-ee singlets and UADC-ee (Ms=0 singlets+triplets)."""
import sys, time, resource, json, os
from pyscf import gto, scf, adc, lib
from pyscf.data import elements
mid, basis, aux = sys.argv[1], sys.argv[2], sys.argv[3]
nroots = int(sys.argv[4]) if len(sys.argv) > 4 else 3
which = sys.argv[5] if len(sys.argv) > 5 else 'both'
atom = '\n'.join(open(f'../xyz/{mid}.xyz').read().splitlines()[2:])
mol = gto.M(atom=atom, basis=basis, verbose=0, max_memory=2500)
t0 = time.time(); mf = scf.RHF(mol).density_fit(aux.replace('-ri','-jkfit') if False else 'def2-universal-jkfit'); mf.conv_tol=1e-10; mf.kernel(); t1 = time.time()
ncore = elements.chemcore(mol)
res = {'id': mid, 'basis': basis, 'aux': aux, 'nao': mol.nao_nr(), 'frozen_core': ncore, 'threads': lib.num_threads(), 't_scf_s': round(t1-t0,1)}
ev = 27.211386245988
if which in ('both','r'):
    t2=time.time(); a = adc.ADC(mf, frozen=ncore).density_fit(aux); a.method='adc(2)'; a.method_type='ee'; a.max_memory=2500
    e, v, p, x = a.kernel(nroots=nroots); t3=time.time()
    res.update({'t_radc2_singlets_s': round(t3-t2,1), 'SMOKE_S_eV':[round(float(z)*ev,3) for z in e]})
if which in ('both','u'):
    umf = scf.addons.convert_to_uhf(mf)
    t4=time.time(); u = adc.ADC(umf, frozen=(ncore,ncore)).density_fit(aux); u.method='adc(2)'; u.method_type='ee'; u.max_memory=2500
    eu, vu, pu, xu = u.kernel(nroots=2*nroots); t5=time.time()
    res.update({'t_uadc2_ms0_s': round(t5-t4,1), 'SMOKE_U_eV':[round(float(z)*ev,3) for z in eu]})
    try: res['SMOKE_U_S2'] = [round(float(s),2) for s in u.spin_square()] if hasattr(u,'spin_square') else None
    except Exception as ex: res['SMOKE_U_S2'] = str(ex)[:60]
res['maxrss_MB'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
print(json.dumps(res), flush=True)
open('bench_results.jsonl','a').write(json.dumps({'kind':'pyscf-dfadc2',**res})+'\n')
