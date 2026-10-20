#!/usr/bin/env python3
"""Fuerza una palabra del espejo 0x83edf684+off a un valor durante ~3 s (solo RAM), restaura y comprueba que la cámara sigue viva.
Uso: [BASE=0x83e9b548] [SHOOT=1] camera_bisect_fields.py VALOR OFF1 OFF2 ...   (offsets hex dentro del bloque)"""
import os, re, socket, sys, time, urllib.request
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

HOST, BASEW = '192.168.1.29', int(os.environ.get('BASE', '0x83edf684'), 16) // 4  # BASE: físico del bloque/copia
val = int(sys.argv[1])


def alive():
    try:
        socket.create_connection((HOST, 23), timeout=4).close(); return True
    except OSError:
        return False


def rd(w):
    out = run(HOST, [f'dd if=/dev/mem bs=4 skip={w} count=1 of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z'])[0]
    m = re.search(r': ((?:[0-9a-f]{2} ){4})', out)
    return bytes.fromhex(m.group(1).replace(' ', ''))


def wr(w, b):
    esc = ''.join(f'\\0{x:03o}' for x in b)
    run(HOST, [f"echo -ne '{esc}' | dd of=/dev/mem bs=4 seek={w} count=1 2>/dev/null"])


for o in sys.argv[2:]:
    off = int(o, 16); w = BASEW + off // 4
    orig = rd(w)
    esc = f'\\0{val:03o}\\0000\\0000\\0000'
    run(HOST, [f'(i=0; while [ $i -lt 120 ]; do echo -ne "{esc}" | dd of=/dev/mem bs=4 seek={w} count=1 2>/dev/null; usleep 20000; i=$((i+1)); done) >/dev/null 2>&1 &'])
    st = ''
    if os.environ.get('SHOOT'):
        time.sleep(1)
        try:
            urllib.request.urlopen(f'http://{HOST}:8080/shoot', timeout=30).read()
            time.sleep(6)
            st = urllib.request.urlopen(f'http://{HOST}:8080/status', timeout=30).read().decode().strip()
        except Exception as e:
            st = f'sin respuesta ({e})'
    else:
        time.sleep(4)
    ok = alive()
    print(f'+{off:#x} orig={orig.hex()} forzado a {val}: cámara {"viva" if ok else "CAÍDA"} {st}', flush=True)
    if not ok:
        break
    wr(w, orig)
