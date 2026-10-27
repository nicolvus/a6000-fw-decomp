#!/usr/bin/env python3
"""Solo lectura: muestrea en bucle (en la cámara) los registros de tiempo del IMX210 durante disparos y los separa por ID1.
Campos (emulación del prólogo de SetExposure 0x436d6f6c): r5=param+0 (14 bits) en 0x4401c746/0x4401c686, r6=param+4 (12 bits)
en 0x4401c7e2/0x4401c67a, r7=param+6 (12 bits) en 0x4401c69a/0x4401c766; ID1 en 0x4401ca2e. Físico = virtual + 0x40000000.
Uso: camera_imx210_timing.py OUTDIR [n/d ...]   (RemoteShutter abierta)."""
import collections
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adb_shell.adb_device import AdbDeviceTcp
from camera_telnet import run

H, BASE, N = '192.168.1.29', 0x8401c670, 0x3c0  # 60 bloques de 16 B: 0x8401c670..0x8401ca2f
get = lambda p: urllib.request.urlopen(f'http://{H}:8080' + p, timeout=60).read().decode().strip()
out = sys.argv[1]
os.makedirs(out, exist_ok=False)
dev = AdbDeviceTcp(H, 5555, default_transport_timeout_s=60)
dev.connect(rsa_keys=None, auth_timeout_s=10)


def regs(rec):
    b = lambda v: rec[v - 0x4401c670]
    return (b(0x4401c746) | (b(0x4401c686) & 0x3f) << 8, b(0x4401c7e2) | (b(0x4401c67a) & 0xf) << 8,
            b(0x4401c69a) | (b(0x4401c766) & 0xf) << 8, b(0x4401ca2e))


with open(f'{out}/log.txt', 'w') as log:
    for sp in sys.argv[2:] or ['1/4000', '1/250', '1/15']:
        n, d = sp.split('/')
        get(f'/ss?n={n}&d={d}')
        run(H, [f'rm -f /android/dev/s; (i=0; while [ $i -lt 1500 ]; do dd if=/dev/mem bs=16 skip={BASE // 16} count={N // 16} 2>/dev/null >> /android/dev/s; i=$((i+1)); done) >/dev/null 2>&1 &'])
        time.sleep(0.3)
        get('/shoot')
        time.sleep(9)
        dev.pull('/dev/s', f'{out}/{n}_{d}.bin')
        with open(f'{out}/{n}_{d}.bin', 'rb') as f:
            raw = f.read()
        assert len(raw) % N == 0, f'registro de tamaño irregular: {len(raw)}'
        c = collections.Counter(regs(raw[k:k + N]) for k in range(0, len(raw), N))
        line = f'{sp:>7} {get("/status"):16} muestras={len(raw) // N} ' + ' '.join(
            f'[r5={a} r6={b} r7={r} ID1={i:#x}]x{k}' for (a, b, r, i), k in c.most_common(8))
        print(line, flush=True)
        print(line, file=log)
run(H, ['rm -f /android/dev/s'])
