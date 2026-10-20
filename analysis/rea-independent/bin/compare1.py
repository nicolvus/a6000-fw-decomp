#!/usr/bin/env python3
"""Compara REA (línea B) con el export Ghidra histórico s37 (línea A) por entrada, bytes y llamadas."""
import json, re, hashlib
H={f['entry']:f for f in json.load(open('../ghidra/s37-library.json'))['functions']}
F=json.load(open('exp1-functions.json'))
lib=open('input/libmprctrl.so','rb').read()
R={}
for l in open('out/exp1b.jsonl'):
    d=json.loads(l); t=d['call']['tool']; a=d['call']['args']
    if d['result'].get('isError'): continue
    if t=='analyze_function': R[a['procedure']]=d['result']['structuredContent']['raw_result']['value']
norm=lambda s: re.sub(r'\s+','',re.sub(r'0x0+(?=[0-9a-f])','0x',s.lower()))
rows=[]
for n,a in F.items():
    r=R[a]; h=H.get('%08x'%int(a,16))
    asmR=[norm(x.split(': ',1)[1]) for x in r['assembly']]
    asmH=[norm(x.split(' ',1)[1]) for x in h['listing']] if h else None
    # bytes REA: base 0x10000 -> file offset = addr-0x10000 (verificado con address_to_file_offset)
    start=int(r['procedure']['body']['ranges'][0]['start'],16); end=int(r['procedure']['body']['ranges'][0]['end'],16)
    RB={}
    rows.append(dict(name=n,addr=a,hist_name=h and h['name'],rea_name=r['procedure']['name'],
        same_name=h and h['name']==r['procedure']['name'],
        n_insn_rea=len(asmR),n_insn_hist=asmH and len(asmH),asm_equal=asmR==asmH,
        callees_rea=sorted(c.get('name') or c.get('address') for c in r['callees']),
        hist_calls=sorted(set(re.findall(r'(?:Dmm\w*::\w+|MprCtrl\w*::\w+|osal_\w+|CheckOSALRetCode|CheckDMMRetCode|GetOSALRetMsg|GetDMMRetMsg|memset|UnitTypeTableSelect)\(',h['pseudo_code']))) if h else None,
        rea_calls=sorted(set(re.findall(r'(?:Dmm\w*::\w+|MprCtrl\w*::\w+|osal_\w+|CheckOSALRetCode|CheckDMMRetCode|GetOSALRetMsg|GetDMMRetMsg|memset|UnitTypeTableSelect)\(',r['pseudocode']))),
        hist_thunk=h and h['thunk'],hist_pseudo_len=h and len(h['pseudo_code']),rea_pseudo_len=len(r['pseudocode'])))
json.dump(rows,open('out/exp1-comparison.json','w'),indent=1)
for x in rows:
    print({k:x[k] for k in ('name','same_name','n_insn_rea','n_insn_hist','asm_equal','hist_thunk')})
    if not x['asm_equal']: print('  hist:',x['hist_calls'],'\n  rea :',x['rea_calls'])
