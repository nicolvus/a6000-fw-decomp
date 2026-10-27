#!/usr/bin/env python3
"""Solo lectura: campos del objeto C_ImagerCtrl_IMX210 (físico 0x83e7f4a8, vtable 0x43fcc090) tras disparos a varias velocidades.
Uso: camera_imx210_obj.py [n/d ...]   (RemoteShutter abierta). Imprime +0x170/+0x17c (modo de lectura), +0x3a0 (espera ms), +0x3a8, +0x10/+0x12."""
import os
import struct
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST, OBJ = '192.168.1.29', 0x83e7f4a8
get = lambda p, t=60: urllib.request.urlopen(f'http://{HOST}:8080' + p, timeout=t).read().decode().strip()


def rd(addr, n):
    out = run(HOST, [f'dd if=/dev/mem bs=16 skip={addr // 16} count={n // 16} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z'])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(':', ' ').split()
        if parts and len(parts[0]) == 8 and all(c in '0123456789abcdef' for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    assert len(data) == n, f'lectura incompleta {len(data)}'
    return bytes(data)


def show(tag):
    o = rd(OBJ & ~0xf, 0x410)[OBJ & 0xf:]
    assert struct.unpack_from('<I', o, 0)[0] == 0x43fcc090, 'vtable distinta: objeto no está ahí'
    u16 = lambda a: struct.unpack_from('<H', o, a)[0]
    u32 = lambda a: struct.unpack_from('<I', o, a)[0]
    print(f'{tag:>8} +170={u32(0x170)} +174={u32(0x174)} +178={u32(0x178)} +17c={o[0x17c]} +3a0={u16(0x3a0)} +3a8={u32(0x3a8)} '
          f'+10={u16(0x10)} +12={u16(0x12)} +294={u32(0x294):#x}', flush=True)
    return o


show('reposo')
for sp in sys.argv[1:] or ['1/4000', '1/250', '1/30', '1/15']:
    n, d = sp.split('/')
    get(f'/ss?n={n}&d={d}'); get('/shoot')
    t0 = time.time()
    while time.time() - t0 < 40 and not get('/status').startswith(('done', 'shoot-error')):
        time.sleep(0.3)
    show(sp)
