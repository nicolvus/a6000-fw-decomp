#!/usr/bin/env python3
"""Lee memoria física de la cámara (service mode, SOLO LECTURA): senser_readmem.py OUTDIR 0xADDR:0xSIZE ..."""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out, regions = sys.argv[1], [tuple(int(x, 16) for x in r.split(':')) for r in sys.argv[2:]]
os.makedirs(out, exist_ok=True)

def read(cam):
    be = SenserPlatformBackend(cam); be.start()
    for a, n in regions:
        fn = os.path.join(out, 'mem_%08x_%x.bin' % (a, n))
        try:
            with open(fn, 'wb') as f: be.readMemory(a, n, f)
            h = hashlib.sha256(open(fn, 'rb').read()).hexdigest()
            print('OK  %#010x %#x %d B %s' % (a, n, os.path.getsize(fn), h[:16]), flush=True)
            open(os.path.join(out, 'SHA256SUMS'), 'a').write('%s  %s\n' % (h, os.path.basename(fn)))
        except Exception as e:
            print('FALLO %#010x %#x %s' % (a, n, e), flush=True)

senserShellCommand(complete=read)
