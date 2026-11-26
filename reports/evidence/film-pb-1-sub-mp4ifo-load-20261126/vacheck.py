import struct
p='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(p,'rb').read()
e_shoff=struct.unpack_from('<I',d,32)[0]; e_shentsize=struct.unpack_from('<H',d,46)[0]
e_shnum=struct.unpack_from('<H',d,48)[0]; e_shstrndx=struct.unpack_from('<H',d,50)[0]
secs=[struct.unpack_from('<10I',d,e_shoff+i*e_shentsize) for i in range(e_shnum)]
shstr=secs[e_shstrndx]
def nm(s):
    o=shstr[4]+s[0]; return d[o:d.index(b'\0',o)].decode()
S={nm(s):(s[3],s[4],s[5]) for s in secs}
print('# tamano de fichero = 0x%X' % len(d))
for n in ('.text','.rodata','.data','.bss'):
    a,o,sz=S[n]; print('# %-8s VA 0x%08X-0x%08X  off 0x%06X  %d B' % (n,a,a+sz,o,sz))
def where(va):
    for n,(a,o,sz) in S.items():
        if a and a<=va<a+sz: return n
    return 'FUERA'
import sys
vass=[0x698EC8,0x698F18,0x698FB8,0x697D70,0x698B3E,0x6EC1C4,0x6EE13A,0x6F0D4C,0x6F0A54,
      0x3AFA94,0x35EA1C,0x35E04C,0x2B39B8,0x2B2F48,0x2B3948,0x3502CA,0x3502B8,0x350124,
      0x91C945,0x91443D,0x8DD35E,0x8BBA44,0x823999,0x8BCC33,0x91CAD0,0x914F92,0x914EF2,
      0x914F19,0x9D23FC,0xA3699C,0xA4F368,0x698F10,0x698FA4,0x6F0EC0,0x6F0AF4]
for v in vass:
    print('VA 0x%08X -> %s' % (v, where(v)))
