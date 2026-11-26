import sys, struct, json, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmap import ELF

LIBS = {'A6000':'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so',
        'A6300':'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'}

def array_containing(e, slot, prefix):
    d = e.data
    def name_of(k):
        v = struct.unpack_from('<I', d, k)[0]
        t = e.va2off(v)
        if t is None: return None
        end = d.find(b'\0', t)
        if end < 0 or end - t > 80: return None
        try: s = d[t:end].decode('ascii')
        except Exception: return None
        return s if s.startswith(prefix) else None
    k = slot
    while name_of(k - 4): k -= 4
    start = k; seq = []
    while name_of(k):
        seq.append(name_of(k)); k += 4
    return start, seq

def find_slot(e, s):
    out = []
    for o in e.find_str(s):
        va = e.off2va(o); pat = struct.pack('<I', va); k = 0
        while True:
            j = e.data.find(pat, k)
            if j < 0: break
            out.append(j); k = j + 1
    return out
