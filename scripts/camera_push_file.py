#!/usr/bin/env python3
"""Sube un archivo pequeño a la cámara por telnet (echo -ne con escapes octales; sin adb). Uso: camera_push_file.py LOCAL REMOTO [HOST]
Comprueba el tamaño y el md5sum al final. Pensado para binarios de pocos KB."""
import hashlib, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from camera_telnet import run

local, remote = sys.argv[1], sys.argv[2]; host = sys.argv[3] if len(sys.argv) > 3 else '192.168.1.29'
data = open(local, 'rb').read(); assert len(data) <= 64 * 1024, 'demasiado grande para este método'
run(host, [f': > {remote}'])
for i in range(0, len(data), 96):
    esc = ''.join(f'\\0{b:03o}' for b in data[i:i + 96])
    run(host, [f"echo -ne '{esc}' >> {remote}"])
run(host, [f'chmod 755 {remote}'])
out = run(host, [f'ls -l {remote}; /bin/busybox md5sum {remote}'])[0]
print(out)
assert str(len(data)) in out and hashlib.md5(data).hexdigest() in out, 'verificación fallida'
print('OK', len(data), 'bytes')
