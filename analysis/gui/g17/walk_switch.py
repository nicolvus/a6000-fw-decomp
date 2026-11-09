import struct,sys
from capstone import *
L=sys.argv[1]; pc=int(sys.argv[2],16); val=int(sys.argv[3],16); reg=sys.argv[4] if len(sys.argv)>4 else 'r1'
d=open(L,'rb').read(); md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); U=struct.unpack_from
regs={reg:val}; flags=None; steps=0
cond={'eq':lambda a,b:a==b,'ne':lambda a,b:a!=b,'hi':lambda a,b:a>b,'ls':lambda a,b:a<=b,'hs':lambda a,b:a>=b,'cs':lambda a,b:a>=b,'lo':lambda a,b:a<b,'cc':lambda a,b:a<b,'gt':lambda a,b:a>b,'lt':lambda a,b:a<b,'ge':lambda a,b:a>=b,'le':lambda a,b:a<=b}
nonctl=0
while steps<400:
    i=next(md.disasm(d[pc:pc+4],pc)); steps+=1
    m,o=i.mnemonic,i.op_str
    nxt=pc+i.size
    if m.startswith('cmp') and o.split(',')[0] in regs and '#' in o:
        flags=(regs[o.split(',')[0]],int(o.split('#')[1],16))
    elif m.startswith(('sub','subs')) and len(o.split(','))==3 and o.split(',')[1].strip() in regs and '#' in o:
        regs[o.split(',')[0]]=(regs[o.split(',')[1].strip()]-int(o.split('#')[1],16))&0xffffffff
    elif m.startswith('mov') and len(o.split(','))==2 and o.split(',')[1].strip() in regs:
        regs[o.split(',')[0]]=regs[o.split(',')[1].strip()]
    elif m in('tbb','tbh'):
        r=o.split(',')[1].strip().rstrip(']').split()[0]; x=regs[r]
        b=pc+4; t=b+2*(d[b+x] if m=='tbb' else U('<H',d,b+2*x)[0]); print('tb',hex(pc),'idx',hex(x),'->',hex(t)); nxt=t
    elif m.startswith('b') and o.startswith('#') and m not in('bl','blx','bic','bics'):
        c=m[1:].split('.')[0]
        if c=='' : nxt=int(o[1:],16)
        elif c in cond and flags: 
            if cond[c](*flags): nxt=int(o[1:],16)
        else: print('stop',hex(pc),m,o); break
    elif m in('cbz','cbnz'): print('stop cb',hex(pc)); break
    else:
        nonctl+=1
        if nonctl>6 and not m.startswith(('push','add','ldr','str','sub','mov')): pass
        if m in('bl','blx') or (m.startswith('pop')): print('reached',hex(pc),m,o); break
    if m.startswith(('cmp','b','tb','sub','mov','push','add')) is False: pass
    pc=nxt
print('final pc',hex(pc))
