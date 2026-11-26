#!/usr/bin/env python3
"""Resuelve el nombre importado de un stub .plt de libObj.so leyendo sus dos instrucciones
(add ip,pc,#imm ; ldr pc,[ip,#imm2]) y la reloc R_ARM_JUMP_SLOT del slot GOT resultante."""
import struct, subprocess, sys, re
PATH='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'
D=open(PATH,'rb').read()
def u16(a): return struct.unpack_from('<H',D,a)[0]
def u32(a): return struct.unpack_from('<I',D,a)[0]
rel={}
out=subprocess.run(['readelf','-rW',PATH],capture_output=True,text=True).stdout
for line in out.splitlines():
    f=line.split()
    if len(f)>=5 and f[2]=='R_ARM_JUMP_SLOT':
        rel[int(f[0],16)]=f[4]
def resolve(stub):
    a=stub&~1
    h1=u16(a); h2=u16(a+2)
    if (h1&0xf800)!=0xf000 or (h2&0xf800)!=0xf800:
        return None
    imm12=((h1&0xff)<<8)|((h2>>12)&0xff)
    pc=(a+4)&~3
    ip=pc+imm12
    h3=u16(a+4); h4=u16(a+6)
    if (h3&0xff80)!=0xf880: return None
    imm=(h3&0x7f)<<2 | ((h4>>12)&0xf) if (h4&0x0f00) else (h3&0x7f)*4
    # ldr.w pc,[ip,#imm]: h3=F8D? h4 = 0xF000|Rt<<12|imm12
    if (h3&0xfff0)==0xf8d0:
        imm=h4&0xfff
        return rel.get(ip+imm)
    return None
if __name__=='__main__':
    for a in sys.argv[1:]:
        print(a, resolve(int(a,16)))
