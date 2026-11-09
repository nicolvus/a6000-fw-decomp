"""Emula la selección de gamma de la A6000 (0x43853ec2) sobre un av-cam dado: cfg+0x153 = selector → YC+0xbd9 (G18)."""
import struct,sys
from unicorn import *
from unicorn.arm_const import *
BASE=0x43541000
def run(img, sel, movie=1, trace=False):
    mu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    size=(len(img)+0xfff)&~0xfff
    mu.mem_map(BASE,0xc00000)               # ventana de 12 MiB (imagen + .bss + resto)
    mu.mem_write(BASE,img)
    A,C,S,Y,STK=0x10000000,0x10010000,0x10020000,0x10030000,0x10100000
    mu.mem_map(0x10000000,0x200000)
    mu.mem_map(0,0x100000)                  # punteros nulos de globales sin inicializar (.bss) → lecturas a cero
    mu.mem_write(A,struct.pack('<I',C)); mu.mem_write(A+0x34,struct.pack('<I',S))
    mu.mem_write(S+0x7ca,bytes([movie]))     # 0/4 → foto, otro → vídeo (c66)
    mu.mem_write(C+0x153,bytes([sel]))
    calls=[]
    def hook(uc,addr,size,ud):
        ins=uc.mem_read(addr,4)
        h1,h2=struct.unpack('<HH',ins)
        if (h1&0xf800)==0xf000 and (h2&0xd000)==0xd000:   # BL: se salta (stub que devuelve 0)
            calls.append(hex(addr)); uc.reg_write(UC_ARM_REG_R0,0); uc.reg_write(UC_ARM_REG_PC,(addr+4)|1)
    mu.hook_add(UC_HOOK_CODE,hook)
    END=0x10180000; mu.mem_write(END,b'\x00\xbf'*8)
    mu.reg_write(UC_ARM_REG_SP,STK+0x80000); mu.reg_write(UC_ARM_REG_R0,A); mu.reg_write(UC_ARM_REG_R1,Y)
    mu.reg_write(UC_ARM_REG_LR,END|1)
    try:
        mu.emu_start(0x43853ec0|1,END,count=200000)
    except UcError as e:
        raise RuntimeError(f'{e} pc={mu.reg_read(UC_ARM_REG_PC):#x}')
    y=mu.mem_read(Y,0xd00)
    return {'bd9':y[0xbd9],'bd7':y[0xbd7],'bd8':y[0xbd8],'c66':y[0xc66],'bls':len(calls)}
if __name__=='__main__':
    for p in sys.argv[1:]:
        img=open(p,'rb').read()
        print(p.split('/')[-1],{s:run(img,s) for s in (0,3,4,5,6,7,8,9,10,11)})
