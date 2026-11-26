import struct
B='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(B,'rb').read()
# .data VA->off: ELF p_offset para .data es 0x9bc2e8 con sh_addr 0x9c42e8 => off = va - 0x8000
def u32(va): return struct.unpack_from('<I',d,va-0x8000)[0]
def u16(va): return struct.unpack_from('<H',d,va-0x8000)[0]
SECT=[u32(0x9D2380+4*i) for i in range(30)]
print('lista 0x9D2380 (30 sectores):', ' '.join('%02x'%s for s in SECT))
print()
# tabla en RAM (dump 20-10): base 0x8A5CB000, tabla = base+0xA3699C
ram=open('analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin','rb')
def ramu32(va):
    ram.seek(va-0x80000000); return struct.unpack('<I',ram.read(4))[0]
TAB=0x8A5CB000+0xA3699C
print('idx sec  | filas(userID,mediaID,OM) que piden ese sector | RAM 20-10: +4 +8 +C +10')
for i,s in enumerate(SECT):
    rows=[]
    for r in range(40):
        w=[u32(0x9D23FC+0x18*r+4*k) for k in range(4)]
        if w[0]==0: break
        if w[2]==s: rows.append('(%02x,%d,OM%d)'%(w[0],w[1],w[3]))
    print('%02d  %02x  | %-46s | %08x %08x %02x %02x' % (
        i,s,','.join(rows)[:46], ramu32(TAB+0x14*i+4), ramu32(TAB+0x14*i+8),
        ramu32(TAB+0x14*i+0xc)&0xff, ramu32(TAB+0x14*i+0x10)&0xff))
