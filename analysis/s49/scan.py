import struct,sys
def scan(path,lo,hi,tabs):
    b=open(path,'rb').read(); res=[]
    for a in range(lo,hi,2):
        h=struct.unpack_from('<H',b,a)[0]
        if h>>11==9:
            rx=(h>>8)&7; la=((a+4)&~3)+((h&0xff)<<2); v=struct.unpack_from('<I',b,la)[0]
            for j in range(2,16,2):
                g=struct.unpack_from('<H',b,a+j)[0]
                if (g&0xff78)==0x4478 and ((g&7)|((g>>4)&8))==rx:
                    t=(v+a+j+4)&0xffffffff
                    if any(s<=t<e for s,e in tabs): res.append((hex(a),hex(t)))
                    break
    return res
