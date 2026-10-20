#!/usr/bin/env python3
"""Fuerza [0x43e95950+0x78]=0x40 y [0x43e94ee4+0x34]=1 (RAM, bucle 20 ms) durante un disparo remoto; restaura los originales.
Uso: camera_efcs_conditions.py [d78|e34|ambos]"""
import re, sys, time, urllib.request
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

HOST = '192.168.1.29'
W78, W34 = 0x83e95950 // 4 + 0x78 // 4, 0x83e94ee4 // 4 + 0x34 // 4


def rd(w):
    out = run(HOST, [f'dd if=/dev/mem bs=4 skip={w} count=1 of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z'])[0]
    return bytes.fromhex(re.search(r': ((?:[0-9a-f]{2} ){4})', out).group(1).replace(' ', ''))


esc = lambda b: ''.join(f'\\0{x:03o}' for x in b)
modo = sys.argv[1] if len(sys.argv) > 1 else 'ambos'
sets = []
if modo in ('d78', 'ambos'): sets.append((W78, bytes([0x40, 0, 0, 0])))
if modo in ('e34', 'ambos'): sets.append((W34, bytes([1, 0, 0, 0])))
orig = {w: rd(w) for w, _ in sets}
print('originales', {hex(w * 4): o.hex() for w, o in orig.items()}, flush=True)
body = ' '.join(f'echo -ne "{esc(v)}" | dd of=/dev/mem bs=4 seek={w} count=1 2>/dev/null;' for w, v in sets)
rest = ' '.join(f'echo -ne "{esc(orig[w])}" | dd of=/dev/mem bs=4 seek={w} count=1 2>/dev/null;' for w, _ in sets)
run(HOST, [f'(i=0; while [ $i -lt 400 ]; do {body} usleep 20000; i=$((i+1)); done; {rest}) >/dev/null 2>&1 &'])
time.sleep(1)
try:
    urllib.request.urlopen(f'http://{HOST}:8080/shoot', timeout=40).read()
    time.sleep(6)
    print(modo, urllib.request.urlopen(f'http://{HOST}:8080/status', timeout=30).read().decode().strip())
except Exception as e:
    print('sin respuesta', e)
