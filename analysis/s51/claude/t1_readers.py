# T1: accesos a [0x43eefb1c+0x60] tras referencias PIC (xidx de S50). Heurística: registro destino del add pc, ventana 16 instr.
import pickle,re,bisect,collections
pc=pickle.load(open('xidx_pc.pkl','rb')); callers,starts=pickle.load(open('calls.pkl','rb'))
ins=[];idx={}
for l in open('../../s51/shared/av.dis'):
    m=re.match(r'([0-9a-f]+): (?:[0-9a-f]{4} )+(\S+)\s*(.*)',l.strip())
    if m: idx[int(m.group(1),16)]=len(ins); ins.append((int(m.group(1),16),m.group(2),m.group(3)))
fn=lambda a: starts[bisect.bisect_right(starts,a)-1]
refs=pc[0x43eefb1c]; byfn=collections.defaultdict(list)
for r in refs:
    i=idx.get(r); 
    if i is None: continue
    reg=ins[i][2].split(',')[0]
    for j in range(i+1,min(i+16,len(ins))):
        a,op,ar=ins[j]
        if re.search(r'\[%s, #0x60\]'%reg,ar): byfn[fn(r)].append((hex(a),op,ar))
        if ar.startswith(reg+',') and not op.startswith(('str','cmp','tst')): break
print('refs',len(refs),'funcs',len({fn(r) for r in refs}))
for f in sorted({fn(r) for r in refs}): print(hex(f), byfn.get(f,'-'))
