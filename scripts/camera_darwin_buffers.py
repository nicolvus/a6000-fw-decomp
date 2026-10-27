#!/usr/bin/env python3
"""T023: lee (solo lectura) los buffers de envío BIONZ→Darwin IDs 0x12 (4 B), 0x0f (2 B) y 0x13 (10 B) antes y después de un disparo remoto.
Uso: camera_darwin_buffers.py [N_DISPAROS]"""
import sys, time, urllib.request
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

HOST = '192.168.1.29'
# físico = virtual av-cam + 0x40000000; cabeceras {03, NN, len} en 0x436b88e8 / 0x436b8aec / 0x436b8864
BUFS = {'0x12 (03 07, 4 B)': (0x83f91e2e, 4), '0x0f (03 04, 2 B)': (0x83f91f24, 2), '0x13 (03 08, 10 B)': (0x83f91f1a, 10)}


BASE, SIZE = 0x83f91e20, 0x110  # ventana que cubre los tres buffers y el paquete ev1 de 22 B (control)


def snap(tag):
    # sin od en el busybox: hd de Android vía chroot, como el resto de scripts
    out = run(HOST, [f'dd if=/dev/mem bs=16 skip={BASE // 16} count={SIZE // 16} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z'])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(':', ' ').split()
        if parts and len(parts[0]) == 8 and all(c in '0123456789abcdef' for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    assert len(data) == SIZE, f'lectura incompleta: {len(data)} B\n{out}'
    for name, (a, n) in BUFS.items():
        print(f'{tag:>10} ID {name}: {data[a - BASE:a - BASE + n].hex(" ")}', flush=True)
    print(f'{tag:>10} control ev1 22 B: {data[0x83f91e32 - BASE:0x83f91e32 - BASE + 22].hex(" ")}', flush=True)


snap('reposo')
for k in range(int(sys.argv[1]) if len(sys.argv) > 1 else 1):
    t = time.time()
    try:
        urllib.request.urlopen(f'http://{HOST}:8080/shoot', timeout=40).read()
        time.sleep(6)
        st = urllib.request.urlopen(f'http://{HOST}:8080/status', timeout=30).read().decode().strip()
    except Exception as e:
        st = f'sin respuesta ({e})'
    print(f'disparo {k + 1}: {time.time() - t:.3f} s | {st}', flush=True)
    snap(f'tras {k + 1}')
