import struct,sys,json
sys.path.insert(0,sys.argv[1]); import vt
S=sys.argv[1]
def load(P,lit,add,n):
    d=open(P,'rb').read()
    def rd(v):
        o=vt.v2o(d,v); return None if o is None else struct.unpack_from('<I',d,o)[0]
    def cs(v):
        o=vt.v2o(d,v); return d[o:o+8].split(b'\0')[0].decode('latin1') if o is not None else '?'
    tab=(rd(lit)+add+4)&0xffffffff
    out={}
    for p in range(n):
        D=rd(tab+4*p); w=[rd(D+4*i) for i in range(12)]
        ms=[]
        for i in range(w[7] if w[6] else 0):
            e=[rd(w[6]+0x24*i+4*k) for k in range(9)]
            ms.append([cs(e[0]),e[2],e[3]])
        bs=[hex(rd(w[8]+0x18*i)) for i in range(w[9] if w[8] else 0)]
        out[p]={'m':ms,'b':bs}
    return out
A=load('analysis/camera-extract/usr/lib/cmn_view_processDataMgr.so',0x755e4,0x755d0,0xe9)
B=load('firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so',0x3c987c,0x3c986a,0x15b)
json.dump({'a6000':A,'a6300':B},open(S+'/desc.json','w'))
print(A[0x46],B[78])
