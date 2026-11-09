"""Dependencias de las clases PP de la A7S (cmn_view_processDataMgr.so) y si la A6000 las tiene (G20). Solo lee."""
import json, re, struct, subprocess, sys
from pathlib import Path
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
sys.path.insert(0, 'scripts/gui'); import elf_scan
R7 = Path('firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib')
R0 = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib')

def syms(p, defined=True):
    out = {}
    for ln in subprocess.run(['readelf', '-sW', '--dyn-syms', str(p)], capture_output=True, text=True).stdout.splitlines():
        f = ln.split()
        if len(f) >= 8 and f[0].endswith(':') and f[3] in ('FUNC', 'OBJECT'):
            if (f[6] != 'UND') == defined: out[f[7].split('@')[0]] = (int(f[1], 16), int(f[2], 0))
    return out

def demangle(names):
    r = subprocess.run(['c++filt'], input='\n'.join(names), capture_output=True, text=True).stdout.splitlines()
    return dict(zip(names, r))

def main(lib='cmn_view_processDataMgr.so', pat='PictureProfile'):
    p = R7 / lib; d = p.read_bytes(); e = elf_scan.Elf(p); plt = e.plt_map(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    defs = syms(p); dm = demangle(list(defs))
    byaddr = {a & ~1: n for n, (a, s) in defs.items() if s}
    mine = {n: v for n, v in defs.items() if pat in n and v[1] and not dm[n].startswith(('vtable', 'typeinfo', 'guard'))}
    ext, internal = set(), set()
    for n, (a, s) in mine.items():
        a &= ~1
        for i in md.disasm(d[a:a + s], a):
            if i.mnemonic in ('bl', 'blx') and i.op_str.startswith('#'):
                t = int(i.op_str[1:], 16)
                if t in plt or t + 4 in plt: ext.add(plt.get(t) or plt.get(t + 4))
                elif t in byaddr and pat not in byaddr[t]: internal.add(byaddr[t])
    a6000 = set()
    for f in R0.glob('*.so'): a6000 |= set(syms(f))
    pd0 = set(syms(R0 / lib))
    res = {'clases_funciones': len(mine), 'bytes': sum(v[1] for v in mine.values()),
           'externas_faltan_en_a6000': sorted(dm.get(x, x) for x in demangle(sorted(ext)) if x not in a6000) ,
           'externas_ok': len([x for x in ext if x in a6000]),
           'internas_faltan_en_pd_a6000': sorted(demangle(sorted(internal))[x] for x in internal if x not in pd0),
           'internas_ok': len([x for x in internal if x in pd0])}
    dm2 = demangle(sorted(ext)); res['externas_faltan_en_a6000'] = sorted(dm2[x] for x in ext if x not in a6000)
    return res

if __name__ == '__main__':
    print(json.dumps(main(*sys.argv[1:]), indent=1, ensure_ascii=False))
