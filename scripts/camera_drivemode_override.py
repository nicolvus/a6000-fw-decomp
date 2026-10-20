#!/usr/bin/env python3
"""Fuerza el override de drive_mode [0x43e95950+0x86] (físico 0x83e959d6) durante un disparo remoto y lo restaura (solo RAM).
Uso: camera_drivemode_override.py HEX [HEX ...]   p.ej. 0x37 0x38"""
import sys, time, urllib.request
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

HOST, W = '192.168.1.29', 0x83e95984 // 4  # palabra D+0x84; el byte D+0x86 es su byte 2 (little endian)
for a in sys.argv[1:]:
    v = int(a, 16)
    esc = f'\\0000\\0000\\0{v:03o}\\0000'
    run(HOST, [f'(i=0; while [ $i -lt 400 ]; do echo -ne "{esc}" | dd of=/dev/mem bs=4 seek={W} count=1 2>/dev/null; usleep 20000; i=$((i+1)); done; echo -ne "\\0000\\0000\\0000\\0000" | dd of=/dev/mem bs=4 seek={W} count=1 2>/dev/null) >/dev/null 2>&1 &'])
    time.sleep(1)
    try:
        urllib.request.urlopen(f'http://{HOST}:8080/shoot', timeout=40).read()
        time.sleep(6)
        st = urllib.request.urlopen(f'http://{HOST}:8080/status', timeout=30).read().decode().strip()
    except Exception as e:
        st = f'sin respuesta ({e})'
    print(f'override={v:#x}: {st}', flush=True)
    time.sleep(4)
