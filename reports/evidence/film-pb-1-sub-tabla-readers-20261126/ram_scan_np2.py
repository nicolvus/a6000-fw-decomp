import numpy as np, struct
p='analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin'
d=open(p,'rb').read(); B=0x80000000
a=np.frombuffer(d,dtype='<u2')
SEQ=[0x10,0x11,0x12,0x20,0x21,0x28,0x29,0x2c,0x2d,0x30,0x31,0x38,0x39,0x40,0x60,0x61,0x68,0x6c,0x62,0x63,
     0x90,0x91,0x92,0xa0,0xb1,0xb2,0xb3,0xb8,0xbc,0xbd]
S=10; n=len(a)
pos=np.nonzero(a==SEQ[0])[0]
print('u16=0x10:',len(pos))
pos=pos[pos+S*29<n]
for k in range(1,30):
    pos=pos[a[pos+S*k]==SEQ[k]]
    print('  tras SEQ[%d]=%02x: %d' % (k,SEQ[k],len(pos)))
print('TABLAS candidatas: %d' % len(pos))
for i in pos:
    i=int(i); va=B+i*2
    print('  tabla en %08x' % va)
    for k in range(30):
        o=i*2+0x14*k
        print('    [%02d] sec=%04x +4=%08x +8=%08x +c=%08x +10=%08x' % (k,
            struct.unpack_from('<H',d,o)[0], struct.unpack_from('<I',d,o+4)[0],
            struct.unpack_from('<I',d,o+8)[0], struct.unpack_from('<I',d,o+0xc)[0],
            struct.unpack_from('<I',d,o+0x10)[0]))
