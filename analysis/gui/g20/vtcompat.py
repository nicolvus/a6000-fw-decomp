"""¿Es binariamente compatible la base de las clases PP de la A7S con la de la A6000? Compara vtables por nombre de símbolo (G20)."""
import subprocess, struct, sys
from pathlib import Path
R7 = Path('firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/cmn_view_processDataMgr.so')
R0 = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/cmn_view_processDataMgr.so')
def load(p):
    d = p.read_bytes(); s = {}
    for ln in subprocess.run(['readelf', '-sW', '--dyn-syms', str(p)], capture_output=True, text=True).stdout.splitlines():
        f = ln.split()
        if len(f) >= 8 and f[0].endswith(':') and f[0][:-1].isdigit() and f[6] != 'UND': s[f[7].split('@')[0]] = (int(f[1], 16), int(f[2], 0))
    ph = subprocess.run(['readelf', '-lW', str(p)], capture_output=True, text=True).stdout
    segs = [(int(x[1], 16), int(x[2], 16), int(x[4], 16)) for x in (l.split() for l in ph.splitlines()) if x and x[0] == 'LOAD']
    def rd(v):
        for off, va, sz in segs:
            if va <= v < va + sz: return struct.unpack_from('<I', d, v - va + off)[0]
    rel = {}
    for ln in subprocess.run(['readelf', '-rW', str(p)], capture_output=True, text=True).stdout.splitlines():
        f = ln.split()
        if len(f) >= 5 and f[2] in ('R_ARM_ABS32',): rel[int(f[0], 16)] = f[4].split('@')[0]
    by = {}
    for n, (a, sz) in s.items(): by.setdefault(a, n)
    return s, rd, rel, by
def slots(p, cls):
    s, rd, rel, by = load(p)
    vt = s[f'_ZTV{len(cls)}{cls}']; n = vt[1] // 4
    out = []
    for i in range(2, n):
        a = vt[0] + 4 * i
        out.append(rel.get(a) or by.get(rd(a)) or by.get(rd(a) | 1) or hex(rd(a) or 0))
    return out
def dm(xs): return subprocess.run(['c++filt'], input='\n'.join(xs), capture_output=True, text=True).stdout.splitlines()
if __name__ == '__main__':
    base = 'CmnViewProcessDataElementCustomBase'
    a, b = slots(R7, base), slots(R0, base)
    print('CustomBase slots a7s', len(a), 'a6000', len(b))
    for i, (x, y) in enumerate(zip(dm(a), dm(b))):
        print(i, 'OK ' if x == y else 'DIF', x[:70], '|', y[:70] if x != y else '')
    g = slots(R7, 'CmnViewProcessDataElementCustomPictureProfileGamma'); print('Gamma slots', len(g))
