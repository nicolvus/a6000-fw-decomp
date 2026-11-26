import sys
sys.path.insert(0,'/tmp')
import mpr
from unicorn import *
from unicorn.arm_const import *

def align(x,a=0x1000): return (x+a-1)&~(a-1)

mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
for po,base,fsz in mpr.SEGS:
    ab = base & ~0xfff
    mu.mem_map(ab, align(fsz + (base-ab)))
    mu.mem_write(base, mpr.D[po:po+fsz])
STACK=0x20000000
mu.mem_map(STACK, 0x10000)
RET=0x30000000
mu.mem_map(RET,0x1000)
RETADDR=RET+0x10

def run(arg, entry=0x7111b0):
    if isinstance(arg, tuple):
        r0,r1,r2,r3 = arg
    else:
        r0=arg; r1=r2=r3=0
    mu.reg_write(UC_ARM_REG_SP, STACK+0x8000)
    mu.reg_write(UC_ARM_REG_LR, RETADDR|1)
    for r,v in ((UC_ARM_REG_R0,r0),(UC_ARM_REG_R1,r1),(UC_ARM_REG_R2,r2),(UC_ARM_REG_R3,r3)):
        mu.reg_write(r,v)
    try:
        mu.emu_start(entry|1, RETADDR, count=6000)
    except UcError as e:
        return ('ERR',str(e))
    return mu.reg_read(UC_ARM_REG_R0)

if __name__=='__main__':
    fams=[0x00,0x1c,0x31,0x30,0x32,0x20,0x21,0x40,0x41,0x10,0x11]
    for hb in fams:
        res={}
        for low in range(0,0x100):
            v=(hb<<24)|low
            r=run(v)
            res.setdefault(r,[]).append(low)
        parts=[]
        for k,v in res.items():
            parts.append('%s<-%s'%(hex(k) if isinstance(k,int) else k, ','.join(hex(x) for x in v)))
        print('family %02x: %s'%(hb,' | '.join(parts)))
