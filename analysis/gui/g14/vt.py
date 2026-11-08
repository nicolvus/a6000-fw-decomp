import struct,sys,re
def segs(d):
    phoff,phnum=struct.unpack_from('<I',d,28)[0],struct.unpack_from('<H',d,44)[0]
    return [struct.unpack_from('<8I',d,phoff+32*i) for i in range(phnum)]
def v2o(d,v):
    for t,o,va,pa,fs,ms,fl,al in segs(d):
        if t==1 and va<=v<va+fs: return o+v-va
def o2v(d,o):
    for t,off,va,pa,fs,ms,fl,al in segs(d):
        if t==1 and off<=o<off+fs: return va+o-off
def words_eq(d,val):
    pat=struct.pack('<I',val); return [o2v(d,m.start()) for m in re.finditer(re.escape(pat),d) if m.start()%4==0]
def vtable(P,cls):
    d=open(P,'rb').read()
    name=(str(len(cls))+cls).encode()+b'\0'
    no=d.find(name); nv=o2v(d,no)
    ti=[a-4 for a in words_eq(d,nv)]          # typeinfo: {vptr, name}
    out=[]
    for t in ti:
        for vt in words_eq(d,t):              # vtable: {offset_to_top, typeinfo, fn...}
            o=v2o(d,vt-4)
            if struct.unpack_from('<i',d,o)[0]==0:
                out.append((vt+4,[struct.unpack_from('<I',d,v2o(d,vt+4+4*i))[0] for i in range(40)]))
    return out
if __name__=='__main__':
    for a,f in vtable(sys.argv[1],sys.argv[2]): print(hex(a),[hex(x) for x in f])
