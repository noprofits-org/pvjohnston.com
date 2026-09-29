import re, csv, json
L = open('SI1.txt').read().splitlines()
PG = r'(D3h|D2h|C2v|C3v|Cs|CS|C2|C1|S6|S12|Th|O|Td|C5h|C7h|C8h|C9h|C10h)'
N = r'([−-]?\d+)'
E = r'(\d+\.\d\d)'
pat = re.compile(r'^\s*(\w+): (.+?)\s+\S.*?\s' + PG + r'\s+' + N + r'\s+' + E + r'\s+' + E + r'\s+(.*)$')
out=[]
hdr=[i+1 for i,l in enumerate(L) if re.match(r'\s*Supplementary Table [1-4] \|',l)]
spans={'S1':(hdr[0],hdr[1]),'S2':(hdr[1],hdr[2]),'S3':(hdr[2],hdr[3])}
for tab,(a,b) in spans.items():
    i=a-1
    while i<b:
        l=L[i]; m=pat.match(l)
        if m:
            rest=m.group(7)
            # ADC(2) triple = last three numeric tokens on this line or following continuation lines
            j=i; tail=rest
            toks=re.findall(r'[−-]?\d+(?:\.\d+)?',tail)
            while len(re.findall(r'\d+\.\d\d\s+\d+\.\d\d\s*$',tail))==0 and j+1<b:
                j+=1; tail=tail+' '+L[j]
            adc=re.findall(r'([−-]?\d+)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s*$',tail)
            fl=lambda s: float(s.replace('−','-'))
            out.append(dict(table='Supp. Table '+tab[1],id=m.group(1),name=m.group(2).split('  ')[0].strip(),pg=m.group(3),
                scs_cc2_dEST_meV=int(fl(m.group(4))),scs_cc2_ES1_eV=fl(m.group(5)),scs_cc2_ET1_eV=fl(m.group(6)),
                adc2_dEST_meV=int(fl(adc[0][0])) if adc else None,adc2_ES1_eV=fl(adc[0][1]) if adc else None,adc2_ET1_eV=fl(adc[0][2]) if adc else None,
                si_line=i+1))
            i=j+1 if j>i else i+1
        else: i+=1
with open('expected/published_SI_tables_1-3.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o['table'][-1],o['id'],o['pg'],o['scs_cc2_dEST_meV'],o['scs_cc2_ES1_eV'],o['scs_cc2_ET1_eV'],'|',o['adc2_dEST_meV'],o['adc2_ES1_eV'],o['adc2_ET1_eV'])
print(len(out))
