import struct
p='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(p,'rb').read()
LO,HI=0x120228,0x7A3E84
def u16(a): return struct.unpack_from('<H',d,a)[0]
targets={0x6d5,0x53c,1749,1340}
hits=[]
a=LO
while a<HI-4:
    h1=u16(a); h2=u16(a+2)
    if (h1 & 0xFBF0)==0xF240:  # movw T3: 11110 i 10 0100 imm4
        i=(h1>>10)&1; imm4=(h1>>0)&0xF; imm3=(h2>>12)&0x7; rd=(h2>>8)&0xF; imm8=h2&0xFF
        imm=(imm4<<12)|(i<<11)|(imm3<<8)|imm8
        if imm in (0x6d5,0x53c):
            hits.append((a,rd,imm))
    a+=2
print(len(hits))
for a,rd,imm in hits[:80]:
    print(hex(a),'r%d'%rd,hex(imm))
