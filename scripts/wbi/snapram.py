import io
import sys
from bisect import bisect_right
from pathlib import Path
from struct import unpack_from

root = Path.cwd()
sys.path.insert(0,str(root/'references/fwtool'))
from fwtool.sony import wbi  # type: ignore[import-not-found]


class Missing(KeyError): pass

class Ram:
    def __init__(self, path):
        raw=path.read_bytes()
        assert raw[:4] in (b'prof',b'WBI1')
        # The reference reader only recognizes WBI1. Preserve the original header separately.
        self.header=raw[:44]
        self.secs=sorted((c.physicalAddr-0x40000000,c.contents.read()) for c in wbi.readWbi(io.BytesIO(b'WBI1'+raw[4:])))
        self.starts=[s for s,b in self.secs]
        assert all(s+len(b)<=end for (s,b),end in zip(self.secs,self.starts[1:]))
    def read(self,a,n):
        i=bisect_right(self.starts,a)-1
        if i<0: raise Missing(hex(a))
        s,b=self.secs[i]
        if a+n>s+len(b): raise Missing(hex(a))
        return b[a-s:a-s+n]
    def u(self,a): return unpack_from('<I',self.read(a,4))[0]
    def finds(self,pattern):
        for s,b in self.secs:
            i=b.find(pattern)
            while i>=0:
                yield s+i
                i=b.find(pattern,i+1)
    def filename(self,fp):
        de=self.u(fp+12)
        ln=self.u(de+0x34)
        if not 0<ln<=255: raise ValueError((hex(de),ln))
        return self.read(self.u(de+0x38),ln)
    def maps(self,mm):
        v=self.u(mm)
        prev=0
        end=0
        while v:
            owner,start,stop,nxt,prv=unpack_from('<5I',self.read(v,20))
            assert owner==mm and not (start%4096 or stop%4096) and start<stop and start>=end and prev==prv,(hex(v),hex(mm))
            fo=self.u(v+0x4c)
            try: name=self.filename(fo) if fo else b''
            except (ValueError,Missing): name=None
            yield start,stop,self.u(v+0x18),self.u(v+0x48),name
            prev,v,end=v,nxt,stop
    def tasks(self,comm):
        for a in self.finds(comm+b'\0'):
            base=a-0x1e8
            if base%4: continue
            try:
                mm=self.u(base+0xcc)
                first=self.u(mm)
                if mm and self.u(first)==mm and self.u(first+4)==0x8000 and self.u(first+16)==0 and self.filename(self.u(first+0x4c))==comm:
                    yield base,mm
            except (Missing,ValueError): pass

if __name__=='__main__':
    for path in sys.argv[1:]:
        r=Ram(Path(path))
        tasks=list(r.tasks(b'im.elf'))
        print(path,'tasks',[(hex(b),hex(m)) for b,m in tasks],flush=True)
        for mm in {mm for b,mm in tasks}:
            maps=[]
            try: maps.extend(r.maps(mm)); print('complete',len(maps))
            except (Missing,AssertionError) as e: print('incomplete after',len(maps),str(e))
            counts: dict[bytes, int] = {}
            for a,b,flags,pgoff,name in maps:
                if name in (b'im.elf',b'libObj.so',b'viewUnified2.so',b'CautionConfig.so',b'libmpr.so'):
                    counts[name]=counts.get(name,0)+1
                    print(hex(a),hex(b),hex(flags),hex(pgoff),name.decode())
            print('counts',counts,'unidentified',sum(x[-1] is None for x in maps))
