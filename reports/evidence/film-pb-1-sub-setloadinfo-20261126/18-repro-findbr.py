import sys
from capstone import *
F="/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
d=open(F,'rb').read()
TA,TS=0x120228,0x683c5c
targets={int(x,16) for x in sys.argv[1:]}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
code=d[TA:TA+TS]
a=TA; hits=[]
while a < TA+TS-4:
    got=False
    for ins in md.disasm(code[a-TA:a-TA+16], a, count=1):
        got=True
        if ins.mnemonic in ('bl','b.w','b') and ins.op_str.startswith('#'):
            try: t=int(ins.op_str[1:],16)
            except: t=None
            if t in targets: hits.append((ins.address,ins.mnemonic,ins.op_str))
        a=ins.address+ins.size
    if not got: a+=2
for h in hits: print("%#x %s %s"%h)
print(len(hits),"hits")
