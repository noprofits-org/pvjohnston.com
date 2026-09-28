"""Timing smoke test ONLY. Psi4 EOM-CC2 (unscaled, conventional) singlets; triplets attempted via EOM_REFERENCE ROHF."""
import sys, time, json, resource
import psi4
mid, basis, mode = sys.argv[1], sys.argv[2], sys.argv[3]  # mode: singlet | rohf
lines = open(f'../xyz/{mid}.xyz').read().splitlines()[2:]
psi4.set_memory('2500 MB'); psi4.set_num_threads(4); psi4.core.set_output_file(f'psi4_{mid}_{basis}_{mode}.out', False)
mol = psi4.geometry('0 1\n' + '\n'.join(lines) + '\nsymmetry c2v\nno_reorient\nno_com\n')
opts = {'basis': basis, 'freeze_core': 'true', 'scf_type': 'pk', 'e_convergence': 1e-8, 'd_convergence': 1e-8,
        'roots_per_irrep': [1, 1, 1, 1]}
if mode == 'rohf': opts['eom_reference'] = 'rohf'
psi4.set_options(opts)
t0 = time.time(); e, wfn = psi4.energy('eom-cc2', return_wfn=True); t1 = time.time()
res = {'id': mid, 'basis': basis, 'mode': mode, 'nbf': wfn.nso(), 't_total_s': round(t1-t0, 1),
       'maxrss_MB': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)}
print(json.dumps(res)); open('bench_results.jsonl','a').write(json.dumps({'kind':'psi4-eomcc2',**res})+'\n')
