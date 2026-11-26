#!/usr/bin/env python3
"""Utilidades: limites de funcion desde .ARM.exidx de libObj.so + atribucion de un sitio de
codigo a su funcion. Solo estatico."""
import struct, subprocess, re

PATH = 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'
EXIDX_VA, EXIDX_OFF, EXIDX_SZ = 0xf5fe34, 0xf5fe34, 0x06a770


def _secs():
    out = subprocess.run(['readelf', '-SW', PATH], capture_output=True, text=True).stdout
    s = {}
    for line in out.splitlines():
        m = re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
        if m:
            n, t, a, o, z = m.groups()
            s[n] = (int(a, 16), None if t == 'NOBITS' else int(o, 16), int(z, 16))
    return s


SEC = _secs()
DATA = open(PATH, 'rb').read()


def prel31(w, addr):
    v = w & 0x7fffffff
    if v & 0x40000000:
        v -= 0x80000000
    return (addr + v) & 0xffffffff


def starts():
    """Direcciones de inicio de funcion segun exidx (ordenadas)."""
    va, off, sz = SEC['.ARM.exidx']
    out = []
    for i in range(0, sz - 7, 8):
        w = struct.unpack_from('<I', DATA, off + i)[0]
        a = prel31(w, va + i)
        out.append(a)
    return sorted(set(out))


def owner(va, st=None):
    st = st or starts()
    lo, hi = 0, len(st) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if st[mid] <= va:
            best = st[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def name_of(addr):
    out = subprocess.run(['readelf', '-sW', PATH], capture_output=True, text=True).stdout
    best = None
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[3] in ('FUNC', 'IFUNC') and f[1] != '00000000':
            try:
                a = int(f[1], 16)
            except ValueError:
                continue
            if a & ~1 == addr:
                best = f[7]
    return best
