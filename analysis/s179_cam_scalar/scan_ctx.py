#!/usr/bin/env python3
import sys, os
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
key=sys.argv[1].encode()
pad=int(sys.argv[2]) if len(sys.argv)>2 else 300
for k,v in BINS.items():
    d=open(v,'rb').read()
    i=0
    n=len(d)
    print(f"=== {k} ===")
    while True:
        j=d.find(key,i)
        if j<0: break
        s=j
        while s>0 and 32<=d[s-1]<127: s-=1
        e=j
        while e<n and 32<=d[e]<127: e+=1
        print(f"  0x{s+BASE:08x}  {d[s:e].decode('latin1')}")
        i=j+1
