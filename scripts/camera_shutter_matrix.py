#!/usr/bin/env python3
"""Dispara por HTTP (RemoteShutter) con distintos valores forzados en RAM. Solo RAM, sin flash.
Uso: camera_shutter_matrix.py [host]   (telnet 23 + RemoteShutter :8080 abiertos)"""
import sys, time, urllib.request
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

HOST = sys.argv[1] if len(sys.argv) > 1 else '192.168.1.29'
MIRROR, COPY = 553352751, 553341948  # palabras de 4 B: 0x83edf8bc/4 y 0x83ed4ff0/4
CASES = [("base", None, None), ("esp=1", 1, None), ("esp=2", 2, None),
         ("esp=1 copia=1", 1, 1), ("esp=2 copia=2", 2, 2), ("base", None, None)]


def w(v, idx):
    return f"echo -ne '\\000{v:o}\\0000\\0000' | dd of=/dev/mem bs=4 seek={idx} count=1 2>/dev/null".replace("\\000", "\\0000", 1) if False else \
           f"echo -ne '\\000{v}\\0000\\0000\\0000' | dd of=/dev/mem bs=4 seek={idx} count=1 2>/dev/null"


def http(p):
    return urllib.request.urlopen(f'http://{HOST}:8080{p}', timeout=40).read().decode().strip()


for n, (name, m, c) in enumerate(CASES, 1):
    if m is not None:
        body = w(m, MIRROR) + ("; " + w(c, COPY) if c is not None else "")
        run(HOST, [f"(i=0; while [ $i -lt 300 ]; do {body}; usleep 20000; i=$((i+1)); done) >/dev/null 2>&1 &"])
        time.sleep(1)
    t = time.strftime('%H:%M:%S')
    http('/shoot')
    time.sleep(7)
    print(f"#{n} {t} {name}: {http('/status')}", flush=True)
