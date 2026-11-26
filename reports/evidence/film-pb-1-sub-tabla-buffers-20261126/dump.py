import struct, sys
P='/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(P,'rb').read()
SEGS=[(0x000000,0x000000,0x9bb1c8),(0x9bb1c8,0x009c31c8,0x1c640)]
def va2off(va):
    for po,base,fsz in SEGS:
        if base<=va<base+fsz: return po+va-base
    return None
def rd(va,n):
    o=va2off(va)
    return d[o:o+n] if o is not None else b''
def word(va):
    b=rd(va,4)
    return struct.unpack('<I',b)[0] if len(b)==4 else None
def dump(va,n,label=''):
    print('--- %s @ %08x ---'%(label,va))
    for i in range(0,n,0x10):
        a=va+i; b=rd(a,16)
        if len(b)<16: print('%08x: <fuera>'%a); break
        w=struct.unpack('<4I',b)
        asc=''.join(chr(c) if 32<=c<127 else '.' for c in b)
        print('%08x: %08x %08x %08x %08x  %s'%(a,w[0],w[1],w[2],w[3],asc))
if __name__=='__main__':
    va=int(sys.argv[1],16); n=int(sys.argv[2],16) if len(sys.argv)>2 else 0x100
    dump(va,n,sys.argv[3] if len(sys.argv)>3 else '')
