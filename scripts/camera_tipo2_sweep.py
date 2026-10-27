#!/usr/bin/env python3
"""Parche en RAM del selector de tipo (T020: and r2,r2,#7 -> mov.w r2,#1 en 0x83793166) + barrido de velocidades; revierte siempre.
Uso: camera_tipo2_sweep.py OUTDIR [n/d ...]   (RemoteShutter abierta, escena fija)."""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST, CODE, G784 = '192.168.1.29', 0x83793164, 0x83e9bccc
ORIG, PATCH = '012302f00702013a', '01234ff00102013a'


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
cur = rd(CODE, 8)
print('codigo', cur, 'G+0x784', rd(G784, 4), flush=True)
assert cur == ORIG, f'código inesperado {cur}: no se parchea'
try:
    wr(CODE + 2, PATCH[4:12])
    assert rd(CODE, 8) == PATCH, 'parche no aplicado'
    print('parcheado', PATCH, flush=True)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'camera_shutter_sweep.py'), out, *sys.argv[2:]], check=False)
    print('G+0x784 tras el barrido', rd(G784, 4), flush=True)
finally:
    wr(CODE + 2, ORIG[4:12])
    time.sleep(0.5)
    fin = rd(CODE, 8)
    print('revertido', fin, 'OK' if fin == ORIG else 'FALLO', flush=True)
