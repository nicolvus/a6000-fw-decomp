#!/usr/bin/env python3
"""Línea B: bytes REA (read_bytes) == archivo original; direcciones de instrucción REA == objdump Thumb independiente."""
import json, subprocess, re
lib=open('input/libmprctrl.so','rb').read(); BASE=0x10000
F=json.load(open('exp1-functions.json')); inv={v:k for k,v in F.items()}
A={};RB={};OFF={}
for l in open('out/exp1b.jsonl'):
    d=json.loads(l);a=d['call']['args'];t=d['call']['tool']
    if d['result'].get('isError'): continue
    s=d['result']['structuredContent']
    if t=='analyze_function': A[a['procedure']]=s['raw_result']['value']
    if t=='read_bytes': RB[a['address']]=s['raw_result']
    if t=='address_to_file_offset': OFF[a['address']]=s['raw_result']['file_offset']
res=[]
for n,addr in F.items():
    v=A[addr]; b=v['procedure']['body']['ranges'][0]; s=int(b['start'],16); e=int(b['end'],16)
    off=OFF[addr]; ok_off=(off==s-BASE)
    rb=RB[hex(s)]; ok_b=bytes.fromhex(rb['bytes_hex'])==lib[s-BASE:s-BASE+rb['returned_bytes']]
    out=subprocess.run(['llvm-objdump','-D','--triple=thumbv7-none-eabi',f'--start-address={s-BASE}',f'--stop-address={e-BASE+1}','input/libmprctrl.so'],capture_output=True,text=True).stdout
    lines=re.findall(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{4} ?)+\s*\t(.*)$',out,re.M)
    od=[int(x,16)+BASE for x,_ in lines]
    rea=[int(x.split(':')[0],16) for x in v['assembly']]
    nm=lambda t: re.sub(r'[\s\[\]{}]','',t.lower().split('@')[0]).replace('0x0','0x')
    txt_eq=sum(nm(t)==nm(x.split(': ',1)[1]) for (_,t),x in zip(lines,v['assembly']))
    res.append(dict(fn=n,addr=addr,file_offset_ok=ok_off,rea_bytes_eq_file=ok_b,n_rea=len(rea),n_objdump=len(od),addr_seq_equal=rea==od,text_equal_after_norm=txt_eq))
json.dump(res,open('out/exp1-bytes-check.json','w'),indent=1)
for r in res: print(r)
