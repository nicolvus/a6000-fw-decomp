#!/usr/bin/env python3
"""Volca un bloque de cadenas de un firmware, en orden."""
import sys
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
def dump(k,lo,hi):
    d=open(BINS[k],'rb').read(); out=[]
    o0,o1=lo-BASE,hi-BASE
    i=o0; prev=False
    while i<o1:
        c=d[i]; cur=32<=c<127
        if cur and not prev:
            s=i
            while i<o1 and 32<=d[i]<127: i+=1
            out.append((s+BASE, d[s:i].decode('latin1')))
        prev=cur; i+=1
    return out
k=sys.argv[1]; lo=int(sys.argv[2],0); hi=int(sys.argv[3],0)
for a,t in dump(k,lo,hi):
    print(f"0x{a:08x}  {t}")
