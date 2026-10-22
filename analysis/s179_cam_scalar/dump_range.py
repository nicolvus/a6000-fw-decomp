#!/usr/bin/env python3
import sys
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
def dump(k,lo,hi):
    d=open(BINS[k],'rb').read()
    o0,o1=lo-BASE,hi-BASE
    i=o0; prev=False
    while i<o1:
        c=d[i]; cur=32<=c<127
        if cur and not prev:
            s=i
            while i<o1 and 32<=d[i]<127: i+=1
            print(f"  {k} 0x{s+BASE:08x}  {d[s:i].decode('latin1')}")
        prev=cur; i+=1
if sys.argv[1]=='find':
    key=sys.argv[2].encode()
    for k in BINS:
        d=open(BINS[k],'rb').read(); j=d.find(key)
        print(k, hex(j+BASE) if j>=0 else "no")
else:
    lo=int(sys.argv[1],0); hi=int(sys.argv[2],0)
    for k in BINS: dump(k,lo,hi)
