#!/usr/bin/env python3
"""Resuelve un par ldr/add PIC -> destino, e imprime la cadena."""
import sys, struct
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
def cstr(d,a):
    o=a-BASE
    if o<0 or o>=len(d): return "<fuera>"
    e=o
    while e<len(d) and 32<=d[e]<127: e+=1
    return d[o:e].decode("latin1")
k=sys.argv[1]; B=open(BINS[k],'rb').read()
for arg in sys.argv[2:]:
    a=int(arg,0)
    h=struct.unpack_from("<H",B,a-BASE)[0]
    if (h & 0xF800)==0x4800:
        reg=(h>>8)&7; lit=((a+4)&~3)+((h&0xFF)*4); kind="ldr16"
    elif (h & 0xFF7F)==0xF85F:
        h2=struct.unpack_from("<H",B,a-BASE+2)[0]
        reg=(h2>>12)&0xF; lit=((a+4)&~3)+((((h2>>8)&0xF)<<8)|(h2&0xFF)); kind="ldr32"
    else:
        print(f"0x{a:08x}: no es ldr [pc] (0x{h:04x})"); continue
    W=struct.unpack_from("<I",B,lit-BASE)[0]
    # buscar el add correspondiente: siguiente add rX,pc
    addaddr=None
    for d2 in range(a+2, a+40, 2):
        hh=struct.unpack_from("<H",B,d2-BASE)[0]
        if (hh & 0xFF00)==0x4400 and ((hh>>3)&0xF)==15 and (((hh>>7)&1)<<3|(hh&7))==reg:
            addaddr=d2; break
    tgt = (W + (addaddr+4)) & 0xFFFFFFFF if addaddr else None
    print(f"0x{a:08x} {kind} r{reg} pool=0x{lit:08x} W=0x{W:08x} add=0x{addaddr:08x}" if addaddr else
          f"0x{a:08x} {kind} r{reg} pool=0x{lit:08x} W=0x{W:08x} add=?")
    if tgt: print(f"      -> 0x{tgt:08x}  {cstr(B,tgt)!r}")
