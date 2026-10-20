"""S60 helper: desensambla Thumb/ARM del av-cam A7S. dis.py ADDR N [arm]"""
import sys, struct
from capstone import *
BIN='firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
BASE=0x43541000
D=open(BIN,'rb').read()
def dis(a,n,arm=False):
    md=Cs(CS_ARCH_ARM,(CS_MODE_ARM if arm else CS_MODE_THUMB)+CS_MODE_LITTLE_ENDIAN)
    for i in md.disasm(D[a-BASE:a-BASE+n],a):
        print(f"{i.address:#x}: {i.mnemonic} {i.op_str}")
def w(a): return struct.unpack_from('<I',D,a-BASE)[0]
if __name__=='__main__':
    a=int(sys.argv[1],16); n=int(sys.argv[2],0); dis(a&~1,n,len(sys.argv)>3)
