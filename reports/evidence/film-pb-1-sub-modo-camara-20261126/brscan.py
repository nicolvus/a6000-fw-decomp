import struct,sys
P='/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(P,'rb').read()
SEGS=[(0x000000,0x000000,0x9bb1c8),(0x9bb1c8,0x009c31c8,0x1c640)]
def off2va(o):
    for po,base,fsz in SEGS:
        if po<=o<po+fsz: return base+o-po
def branches():
    for o in range(0,len(d)-4,2):
        h1,h2=struct.unpack_from('<HH',d,o)
        if (h1>>11)!=0x1E: continue
        op=h2>>14
        if op not in (2,3): continue
        S=(h1>>10)&1;J1=(h2>>13)&1;J2=(h2>>11)&1
        I1=(~(J1^S))&1;I2=(~(J2^S))&1
        imm=(S<<24)|(I1<<23)|(I2<<22)|((h1&0x3FF)<<12)|((h2&0x7FF)<<1)
        if S: imm-=1<<25
        va=off2va(o)
        yield va, va+4+imm, ('BL' if op==3 else 'B.W')
if __name__=='__main__':
    t=int(sys.argv[1],16)
    for va,tgt,kind in branches():
        if tgt==t: print('%s at %08x'%(kind,va))
