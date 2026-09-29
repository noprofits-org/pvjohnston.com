import json
rows = {r['id']: r for r in json.load(open('xyz/basis_counts.json'))}
targets = ['1','11','9','10','12','2a','2c','2b']
ref = rows['1']
def act(r, b): 
    o = r['nocc'] - r['ncore']; v = r[b] - r['nocc']; return o, v
# measured on box (4 threads)
T_RADC_TZ = 404.4          # s, borazine DF-RADC(2) 3 singlets def2-TZVP
U_OVER_R = 203.8/33.8      # UADC(6 roots)/RADC(3 roots) at def2-SVP
T_EOM_SVP = 9.7+49.5+66.9  # s, borazine CCSD + 3S + 3T def2-SVP
o0,v0 = act(ref,'def2-tzvp'); n0 = ref['def2-tzvp-ri']; b0 = ref['def2-tzvp']
os0,vs0 = act(ref,'def2-svp')
out=[]
for t in targets:
    r = rows[t]; o,v = act(r,'def2-tzvp'); naux = r['def2-tzvp-ri']; nb = r['def2-tzvp']
    f_ov = (o**2*v**2*naux)/(o0**2*v0**2*n0)
    f_n5 = (nb/b0)**5
    f = max(f_ov, f_n5)
    radc = T_RADC_TZ*f; uadc = radc*U_OVER_R
    os_,vs_ = act(r,'def2-svp'); f6 = (os_**2*vs_**4)/(os0**2*vs0**4)
    eom_svp = T_EOM_SVP*f6
    ot,vt = act(r,'def2-tzvp'); f6t=(ot**2*vt**4)/(os0**2*vs0**4); eom_tz=T_EOM_SVP*f6t
    vvvv_tz_GB = vt**4*8/1e9/2; vvvv_svp_GB = vs_**4*8/1e9/2
    out.append(dict(id=t,name=r['name'],nbf_tz=nb,nbf_svp=r['def2-svp'],o_act=o,v_tz=v,naux=naux,f_ov=round(f_ov,2),f_n5=round(f_n5,2),
        radc_s_h=round(radc/3600,2),uadc_st_h=round(uadc/3600,2),eom_svp_h=round(eom_svp/3600,2),eom_tz_h=round(eom_tz/3600,1),
        vvvv_svp_GB=round(vvvv_svp_GB,1),vvvv_tz_GB=round(vvvv_tz_GB,1)))
for x in out: print(x)
json.dump(out, open('estimates.json','w'), indent=1)
