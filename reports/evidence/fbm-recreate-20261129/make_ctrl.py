#!/usr/bin/env python3
"""Genera una pagina de control FBS parcheada a partir de la ultima pagina
valida del volcado D3 (nand-20261105-total), anadiendo fileTypes que faltan.

Formato deducido del firmware (libmpr.so):
  +0x000 u32 estado = 0
  +0x004 u16 0x004A  +0x006 u16 0x004A      (constante en las 382 paginas validas)
  +0x008 18 x 8 B  {u32 fileType, u8 status, u8 bloquesBase, u8 bloquesMax, u8 0xFF}
  +0x3F8 u32 secuencia (= page*6 + block dentro del anillo de 384)
  +0x3FC u32 checksum de 0x000..0x3FB (funcion 0x2B05B0)
"""
import struct, sys

SRC='analysis/camera-dumps/nand-20261105-total/dev_nflasha4.bin'
LIB='analysis/camera-extract/usr/lib/libmpr.so'
LAST=319          # pagina con seq 380
NEWSEQ=381        # 381 % 6 = 3 (bloque), 381 // 6 = 63 (pagina) -> offset 0x6FC00

def cksum(b):
    r2=0; r0=0
    for i in range(0x3FC):
        v=b[i]; r2^=v; r0=(r0+((v<<(i&3))&0xffffffff))&0xffffffff
    return ((r0&0xffffff)|(r2<<24))&0xffffffff

def filetype_table():
    import importlib.util
    spec=importlib.util.spec_from_file_location('eh','/tmp/elfhelper.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    e=m.Elf(LIB); info={}
    for i in range(39):
        ft,flg,base,mx=struct.unpack('<4I',e.read(0x9D2794+16*i,16))
        info[ft]=(base,mx)
    return info

def build(types):
    d=open(SRC,'rb').read()
    s=bytearray(d[LAST*1024:(LAST+1)*1024])
    assert struct.unpack_from('<I',s,0x3F8)[0]==380
    info=filetype_table()
    used=[struct.unpack_from('<I',s,8+8*k)[0] for k in range(18) if struct.unpack_from('<I',s,8+8*k)[0]!=0xffffffff]
    for ft in types:
        if ft in used: continue
        base,mx=info[ft]
        b=(base+0x1ffff)//0x20000; m=(mx+0x1ffff)//0x20000
        k=next(k for k in range(18) if struct.unpack_from('<I',s,8+8*k)[0]==0xffffffff)
        struct.pack_into('<IBBBB',s,8+8*k,ft,0,b,m,0xff)
    struct.pack_into('<I',s,0x3F8,NEWSEQ)
    struct.pack_into('<I',s,0x3FC,cksum(s))
    return bytes(s)

if __name__=='__main__':
    types=[int(x,16) for x in sys.argv[1:]] or [0x90,0x91,0x92,0x60,0x61,0x68,0x6c,0x63]
    img=build(types)
    open('reports/evidence/fbm-recreate-20261129/ctrl_seq381.bin','wb').write(img)
    print('fileTypes anadidos:', ' '.join('0x%02x'%t for t in types))
    for i in range(0,0x20,16):
        print('%03x  %s'%(i,img[i:i+16].hex(' ')))
    print('...')
    for i in range(0x3E0,0x400,16):
        print('%03x  %s'%(i,img[i:i+16].hex(' ')))
    print('seq',struct.unpack_from('<I',img,0x3F8)[0],'checksum',hex(struct.unpack_from('<I',img,0x3FC)[0]),
          'calc',hex(cksum(img)))
