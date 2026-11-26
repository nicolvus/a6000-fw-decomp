import struct,sys
p='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(p,'rb').read()
LO,HI=0x120228,0x7A3E84
def u16(a): return struct.unpack_from('<H',d,a)[0]
def bltarget(a):
    h1=u16(a); h2=u16(a+2)
    if (h1 & 0xF800)!=0xF000 or (h2 & 0xD000)!=0xD000: return None
    S=(h1>>10)&1; imm10=h1&0x3FF; J1=(h2>>13)&1; J2=(h2>>11)&1; imm11=h2&0x7FF
    I1=1-(J1^S); I2=1-(J2^S)
    imm=(S<<24)|(I1<<23)|(I2<<22)|(imm10<<12)|(imm11<<1)
    if S: imm-=(1<<25)
    return a+4+imm
targets={int(x,16):[] for x in sys.argv[1:]}
a=LO
while a<HI-4:
    t=bltarget(a)
    if t in targets: targets[t].append(a)
    a+=2
for t,v in targets.items():
    print(hex(t), [hex(x) for x in v])
