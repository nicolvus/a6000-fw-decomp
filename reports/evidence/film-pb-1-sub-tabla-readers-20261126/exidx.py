import sys, struct
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from elfhelper import Elf
P='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
e=Elf(P); d=e.d
a,o,sz=e.sec['.ARM.exidx']
starts=[]
for i in range(sz//8):
    w0,w1=struct.unpack_from('<II',d,o+i*8)
    if w0==1: continue
    prel=w0 & 0x7FFFFFFF
    if prel & 0x40000000: prel -= 0x80000000
    ea=a+i*8
    fn=(ea+prel) & 0xFFFFFFFF
    if fn>=0x100000:
        starts.append((fn,i*8))
pickle_ok=False
import json
starts=sorted(set(x[0] for x in starts))
print("funciones exidx: %d  rango %08x-%08x" % (len(starts), starts[0], starts[-1]))
sel=[s for s in starts if 0x2B0000<=s<0x2B6000]
print("--- funciones en 0x2B0000-0x2B6000 (%d) ---" % len(sel))
prev=None
for s in sel:
    print("  %08x" % s)
json.dump(starts, open('/tmp/fstarts.json','w'))
