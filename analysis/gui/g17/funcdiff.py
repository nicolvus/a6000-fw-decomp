"""Funciones (destinos de BL) de av-cam A7S sin pareja en la A6000 por firma de mnemónicos (inmediatos y registros fuera)."""
import struct,sys,json,hashlib,collections
from capstone import *
BASE=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
def bl_targets(d):
    U=struct.unpack_from; t=set()
    for o in range(0,len(d)-4,2):
        h1,h2=U('<HH',d,o)
        if (h1&0xf800)==0xf000 and (h2&0xd000)==0xd000:
            S=(h1>>10)&1; J1=(h2>>13)&1; J2=(h2>>11)&1
            off=(S<<24)|((1-(J1^S))<<23)|((1-(J2^S))<<22)|((h1&0x3ff)<<12)|((h2&0x7ff)<<1)
            if S: off-=1<<25
            a=BASE+o+4+off
            if BASE<=a<BASE+len(d): t.add(a)
    return t
def sig(d,a,n=40):
    ms=[]; body=0
    for i in md.disasm(d[a-BASE:a-BASE+0x400],a):
        ms.append(i.mnemonic); body+=i.size
        if i.mnemonic.startswith('pop') and 'pc' in i.op_str or (i.mnemonic=='bx' and i.op_str=='lr') or len(ms)>=n: break
    return hashlib.md5(' '.join(ms).encode()).hexdigest(), len(ms), body
if __name__=='__main__':
    I='analysis/rea-independent/input/'
    A=open(I+'av-cam.bin','rb').read(); S=open(I+'av-cam-a7s.bin','rb').read()
    sa=collections.Counter(sig(A,a)[0] for a in bl_targets(A))
    only=[]
    for a in sorted(bl_targets(S)):
        h,n,b=sig(S,a)
        if h not in sa and n>=8: only.append((hex(a),n,b))
    json.dump(only,open(sys.argv[1],'w'))
    print('funciones A7S',len(bl_targets(S)),'sin pareja',len(only))
