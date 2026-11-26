#!/usr/bin/env python3
"""Reconstruye el árbol de CmnViewSettingNode construido por la init de viewUnified2.so.

Cada página/sección se construye con CmnViewSettingNode(hijos, cuenta, props):
  ldr.w r8,[pc,#imm] ; add r8,pc        -> objeto destino (.bss)
  movs  r2,#N                           -> cuenta
  ldr.w r1,[pc,#imm] ; add r1,pc        -> array de punteros a hijos (.data)
Los hijos son o bien símbolos ABS32 (cmnViewSettingNodeRootX de CautionConfig.so) o
bien punteros RELATIVE a otros objetos .bss (páginas construidas antes).
Solo lectura. Uso: arbol_paginas.py [LIB] [objetivo...]
"""
import struct, sys
sys.path.insert(0, '/tmp')
from elfhelper import Elf

BASE = ('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/'
        'nflasha15_unpacked_unpacked/')


def hw(e, va):
    return struct.unpack('<H', e.read(va, 2))[0]


def w32(e, va):
    return struct.unpack('<I', e.read(va, 4))[0]


def reloc_map(e):
    addr, off, size = e.sec['.rel.dyn']
    sym_off, str_off = e.sec['.dynsym'][1], e.sec['.dynstr'][1]
    out = {}
    for i in range(0, size, 8):
        r_off, r_info = struct.unpack_from('<II', e.d, off + i)
        si, typ = r_info >> 8, r_info & 0xff
        st = struct.unpack_from('<I', e.d, sym_off + 16 * si)[0]
        nm = e.d[str_off + st:e.d.index(b'\0', str_off + st)].decode('latin1')
        out[r_off] = (typ, nm)
    return out


def is_add_pc(e, va, rd=None):
    h = hw(e, va)
    if (h >> 8) != 0x44 or ((h >> 3) & 0xf) != 0xf:
        return False
    r = ((h >> 4) & 0x8) | (h & 7)
    return rd is None or r == rd


def ldrw(e, va, rd):
    for back in range(2, 0x30, 2):
        h1, h2 = hw(e, va - back), hw(e, va - back + 2)
        if h1 == 0xF8DF and ((h2 >> 12) & 0xf) == rd:
            return ((va - back + 4) & ~3) + (h2 & 0xfff)
    return None


def sites(e):
    txt_va, _, txt_sz = e.sec['.text']
    out = []
    for va in range(txt_va, txt_va + txt_sz - 4, 2):
        if not is_add_pc(e, va, 1):
            continue
        lit = ldrw(e, va, 1)
        if lit is None:
            continue
        arr = (va + 4 + w32(e, lit)) & 0xffffffff
        cnt = None
        for back in range(2, 0x14, 2):
            h = hw(e, va - back)
            if (h & 0xFF00) == 0x2200:
                cnt = h & 0xff
                break
        obj = None
        for back in range(2, 0x50, 2):
            if is_add_pc(e, va - back, 8):
                l2 = ldrw(e, va - back, 8)
                if l2 is not None:
                    obj = (va - back + 4 + w32(e, l2)) & 0xffffffff
                break
        if cnt is not None:
            out.append((arr, cnt, obj, va))
    return out


def main(lib, targets):
    e = Elf(lib)
    rel = reloc_map(e)
    nodes = {}
    for arr, cnt, obj, va in sites(e):
        kids = []
        for k in range(cnt):
            cell = arr + 4 * k
            r = rel.get(cell)
            if r and r[0] == 2:
                kids.append(('sym', r[1]))
            elif r and r[0] == 23:
                kids.append(('obj', w32(e, cell)))
            else:
                kids.append(('raw', w32(e, cell)))
        nodes[(obj, va)] = (arr, cnt, kids)
    # índice por objeto
    by_obj = {}
    for (obj, va), v in nodes.items():
        if obj is None:
            continue
        by_obj.setdefault(obj, []).append((va,) + v)
    children_objs = set()
    for obj, lst in by_obj.items():
        for va, arr, cnt, kids in lst:
            for t, v in kids:
                if t == 'obj':
                    children_objs.add(v)
    roots = sorted((o for o in by_obj if o not in children_objs), key=lambda x: (x is None, x))
    print('objetos construidos: %d ; raices (no son hijo de nadie): %d' % (len(by_obj), len(roots)))
    for r in roots:
        va, arr, cnt, kids = by_obj[r][0]
        print('  raiz %#x (cnt=%d) construida en %#x' % (r, cnt, va))
        for t, v in kids:
            print('      %s %s' % (t, hex(v) if isinstance(v, int) else v))
    # alcanzabilidad
    seen = set()
    stack = list(roots)
    while stack:
        o = stack.pop()
        if o in seen:
            continue
        seen.add(o)
        for va, arr, cnt, kids in by_obj.get(o, []):
            for t, v in kids:
                if t == 'obj' and v not in seen:
                    stack.append(v)
    print('alcanzables desde las raices: %d de %d' % (len(seen), len(by_obj)))
    for t in targets:
        print('objetivo %#x: construido=%s alcanzable=%s' % (t, t in by_obj, t in seen))
        if t in by_obj:
            for va, arr, cnt, kids in by_obj[t]:
                print('   construido en %#x arr=%#x cnt=%d : %s' % (va, arr, cnt,
                      [hex(v) if isinstance(v, int) else v for _, v in kids]))


if __name__ == '__main__':
    lib = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else BASE + 'lib/viewUnified2.so'
    tg = [int(x, 16) for x in sys.argv[2:]] or [0x4c2acc, 0x4c3e14, 0x4c6018, 0x4c4f0c, 0x4c2dec, 0x4c35fc, 0x4c2cd4, 0x4c4a58]
    main(lib, tg)
