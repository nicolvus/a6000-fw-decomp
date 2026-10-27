#!/usr/bin/env python3
"""Parche en RAM + barrido de velocidades; revierte siempre. Por defecto el selector de tipo de T020
(and r2,r2,#7 -> mov.w r2,#1 en 0x83793166); otro con RAMPATCH=DIR_FÍSICA:ORIG_HEX:NUEVO_HEX[,DIR:ORIG:NUEVO…] (alineado a 2, longitud par de halfwords).
Uso: [RAMPATCH=...] camera_tipo2_sweep.py OUTDIR [n/d ...]   (RemoteShutter abierta, escena fija)."""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST, G784 = '192.168.1.29', 0x83e9bccc
PATCHES = [(int(a, 16), o, n) for a, o, n in
           (p.split(':') for p in os.environ.get('RAMPATCH', '0x83793166:02f00702:4ff00102').split(','))]


def rd(addr, n):
    # sin od/hexdump en el busybox: hd de Android vía chroot, como camera_darwin_buffers.py
    out = run(HOST, [f'dd if=/dev/mem bs=1 skip={addr} count={n} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z'])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(':', ' ').split()
        if parts and len(parts[0]) == 8 and all(c in '0123456789abcdef' for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    return data[:n].hex()


def wr(addr, hexs):
    esc = ''.join(f'\\0{int(hexs[i:i + 2], 16):03o}' for i in range(0, len(hexs), 2))
    assert addr % 2 == 0 and len(hexs) % 4 == 0
    run(HOST, [f"echo -ne '{esc}' | dd of=/dev/mem bs=2 seek={addr // 2} count={len(hexs) // 4} 2>/dev/null"])


if __name__ != '__main__':
    raise ImportError('solo como script')
out = sys.argv[1]
cur = [rd(a, len(o) // 2) for a, o, _ in PATCHES]
print('codigo', cur, 'G+0x784', rd(G784, 4), flush=True)
assert cur == [o for _, o, _ in PATCHES], f'código inesperado {cur}: no se parchea'
try:
    for a, _, n in PATCHES:
        wr(a, n)
    assert [rd(a, len(n) // 2) for a, _, n in PATCHES] == [n for _, _, n in PATCHES], 'parche no aplicado'
    print('parcheado', [n for _, _, n in PATCHES], flush=True)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'camera_shutter_sweep.py'), out, *sys.argv[2:]], check=False)
    print('G+0x784 tras el barrido', rd(G784, 4), flush=True)
finally:
    for a, o, _ in PATCHES:
        wr(a, o)
    time.sleep(0.5)
    fin = [rd(a, len(o) // 2) for a, o, _ in PATCHES]
    print('revertido', fin, 'OK' if fin == [o for _, o, _ in PATCHES] else 'FALLO', flush=True)
