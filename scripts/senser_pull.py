#!/usr/bin/env python3
"""Copia ficheros de la cámara (service mode, SOLO LECTURA): senser_pull.py OUTDIR /ruta1 /ruta2 ..."""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out, paths = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)

def pull(cam):
    be = SenserPlatformBackend(cam); be.start()
    for p in paths:
        fn = os.path.join(out, p.strip('/').replace('/', '__'))
        try:
            with open(fn, 'wb') as f: be.readFile(p, f)
            h = hashlib.sha256(open(fn, 'rb').read()).hexdigest()
            print('OK  ', p, os.path.getsize(fn), h[:16], flush=True)
            open(os.path.join(out, 'SHA256SUMS'), 'a').write('%s  %s\n' % (h, os.path.basename(fn)))
        except Exception as e:
            print('FALLO', p, e, flush=True)
            if os.path.exists(fn) and os.path.getsize(fn) == 0: os.remove(fn)

senserShellCommand(complete=pull)
