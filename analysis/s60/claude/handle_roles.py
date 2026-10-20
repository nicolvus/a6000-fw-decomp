"""S60-Claude: familia de handles 0x8f0xxx: qué wrapper OSAL recibe cada uno (r0=literal -> primer BL a wrapper)."""
import sys,re,collections,json,struct
sys.path.insert(0,'analysis/s60/claude'); import a7dis
from capstone import *
D,B=a7dis.D,a7dis.BASE
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB+CS_MODE_LITTLE_ENDIAN)
w={int(k,16):int(v,16) for k,v in json.load(open('analysis/s60/claude/osal_wrappers.json')).items()}
w[0x4355f520]=0x1e0
lit={B+i:struct.unpack_from('<I',D,i)[0] for i in range(0,len(D)-4,4) if struct.unpack_from('<I',D,i)[0]>>12==0x8f0}
tally=collections.defaultdict(collections.Counter); ex={}
for a in range(0,len(D)-4,2):
    for ins in md.disasm(D[a:a+4],B+a,1):
        if ins.mnemonic=='ldr' and ins.op_str.startswith('r0, [pc'):
            m=re.search(r'#(0x[0-9a-f]+)',ins.op_str)
            if not m: continue
            t=((ins.address+4)&~3)+int(m.group(1),16)
            if t in lit:
                for j in md.disasm(D[ins.address-B+2:ins.address-B+2+0x14],ins.address+2):
                    if j.mnemonic=='bl':
                        try:T=int(j.op_str.lstrip('#'),16)
                        except: break
                        if T in w: tally[lit[t]][hex(w[T])]+=1; ex.setdefault((lit[t],hex(w[T])),hex(ins.address))
                        break
res={hex(h):dict(c) for h,c in tally.items()}
json.dump(dict(roles=res,examples={f"{hex(k[0])}:{k[1]}":v for k,v in ex.items()}),open('analysis/s60/claude/handle_roles.json','w'),indent=1)
for h,c in sorted(tally.items(),key=lambda x:-sum(x[1].values()))[:25]: print(hex(h),dict(c))
