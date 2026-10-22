#!/usr/bin/env python3
import sys
from capstone import *
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
k=sys.argv[1]; lo=int(sys.argv[2],0); hi=int(sys.argv[3],0)
B=open(BINS[k],'rb').read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
for i in md.disasm(B[lo-BASE:lo-BASE+(hi-lo)], lo):
    print(f"0x{i.address:08x}  {i.mnemonic:8s} {i.op_str}")
