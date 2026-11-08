import sys,json,struct,re,glob
S=sys.argv[1]; sys.path.insert(0,S); sys.path.insert(0,'scripts/gui')
import vt, elf_scan
from capstone import *
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
PAT=re.compile(r'ParamList3add|PrmNumberList3GET|Prm\w*List3GET|ParamBaseC2|getNumber|Param\w*C[12]E')
def scan(P,ranges=None):
    d=open(P,'rb').read(); x=elf_scan.Elf(P); plt=x.plt_map()
    text=[s for s in vt.segs(d) if s[0]==1][0]
    spans=ranges or [(0,text[4])]
    out=[]
    for a,b in spans:
        regs={}
        o=vt.v2o(d,a)
        pos=a
        while pos<b:
            got=False
            for i in md.disasm(d[vt.v2o(d,pos):vt.v2o(d,b)],pos):
                got=True; pos=i.address+i.size
                if i.mnemonic in('movs','movw','mov.w','mov') and '#' in i.op_str:
                    r=i.op_str.split(',')[0]
                    try: regs[r]=int(i.op_str.split('#')[1],16)
                    except: pass
                elif i.mnemonic in('bl','blx') and i.op_str.startswith('#'):
                    t=int(i.op_str[1:],16); n=plt.get(t) or plt.get(t+4) or ''
                    if PAT.search(n) and 'r1' in regs: out.append((regs['r1'],re.sub(r'^_ZN?\d+','',n)[:28],i.address))
                    regs={}
            if not got: pos+=2
    return out
if __name__=='__main__':
    R='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/'
    A=set()
    for f in sorted(glob.glob(R+'*.so')):
        try: A|={v for v,_,_ in scan(f)}
        except Exception as e: print('err',f,e)
    json.dump(sorted(A),open(S+'/a6000_params.json','w')); print(len(A))
