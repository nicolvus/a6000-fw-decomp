import struct,sys,json,re,glob
sys.path.insert(0,sys.argv[1]); import vt
sys.path.insert(0,'scripts/gui'); import elf_scan
from capstone import *
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
MODEL=re.compile(rb'@M[0-9A-F]{3}\0')
def pairs_in(P,ranges=None):
    d=open(P,'rb').read(); x=elf_scan.Elf(P); plt=x.plt_map()
    text=[s for s in vt.segs(d) if s[0]==1][0]
    mstr={vt.o2v(d,m.start()):d[m.start():m.start()+5].decode() for m in MODEL.finditer(d)}
    out=set()
    # literal words L such that L + (B+4) == model addr, with 'add rX,pc' at B
    N=text[4]
    for o in range(0,N-4,2):
        h=struct.unpack_from('<H',d,o)[0]
        if h&0xff78!=0x4478: continue
        B=o; 
        if ranges and not any(a<=B<b for a,b in ranges): continue
        # find preceding ldr rX,[pc,#]
        rd_=(h&7)|((h>>4)&8)
        for back in range(2,24,2):
            p=B-back; h2=struct.unpack_from('<H',d,p)[0]
            if h2>>11==0b01001 and (h2>>8)&7==rd_:
                lit=struct.unpack_from('<I',d,((p+4)&~3)+(h2&0xff)*4)[0]
                tgt=(lit+B+4)&0xffffffff
                if tgt in mstr:
                    imm=None; mreg='r%d'%(rd_+1)
                    for i in md.disasm(d[B+2:B+2+48],B+2):
                        if i.mnemonic=='mov' and i.op_str.startswith('r') and i.op_str.split(',')[1].strip()=='r%d'%rd_:
                            mreg='r%d'%(int(i.op_str.split(',')[0][1:])+1)
                        if i.mnemonic in('movs','movw','mov.w') and i.op_str.startswith(mreg+', #'): imm=int(i.op_str.split('#')[1],16)
                        if i.mnemonic in('bl','blx'):
                            t=int(i.op_str.lstrip('#'),16); n=plt.get(t) or plt.get(t+4) or ''
                            if 'Model' in n or 'model' in n: out.add((mstr[tgt],imm,re.sub(r'^_ZN?\d+','',n).split('E')[0][:40])+((B,) if ranges else ()))
                            break
                break
    return out
if __name__=='__main__':
    R='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/'
    A=set()
    for f in sorted(glob.glob(R+'*.so')):
        try: A|=pairs_in(f)
        except Exception as e: pass
    json.dump(sorted([list(p) for p in A],key=str),open(sys.argv[1]+'/a6000_pairs.json','w'))
    print(len(A)); print(sorted(A,key=str)[:10])
