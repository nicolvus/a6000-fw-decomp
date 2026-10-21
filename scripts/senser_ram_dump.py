#!/usr/bin/env python3
"""Volcado SOLO LECTURA de la RAM física del sistema en marcha vía service mode (senser, RMEM).

Uso: python -W ignore scripts/senser_ram_dump.py OUTDIR [INICIO=0x80000000] [FIN=0xC0000000]
Lee tramos de 16 MiB a ram_<inicio>.bin; se detiene en el primer fallo. Escribe SHA256SUMS."""
import hashlib, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out = sys.argv[1]; os.makedirs(out, exist_ok=False)
start = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x80000000
end = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xC0000000
STEP = 0x1000000


def dump(cam):
    be = SenserPlatformBackend(cam); be.start()
    path = os.path.join(out, 'ram_%#x.bin' % start); h = hashlib.sha256(); n = 0; t0 = time.time()
    with open(path, 'wb') as f:
        for off in range(start, end, STEP):
            class W:
                def write(self, d): f.write(d); h.update(d); return len(d)
            try:
                be.readMemory(off, STEP, W())
            except Exception as e:
                print('Parado en %#x: %s' % (off, e or type(e).__name__)); break
            n += 1
            if n % 8 == 0: print('%d MiB (%.0fs)' % (n * 16, time.time() - t0), flush=True)
    open(os.path.join(out, 'SHA256SUMS'), 'w').write('%s  %s\n' % (h.hexdigest(), os.path.basename(path)))
    print('Terminado: %d tramos, %d MiB, sha256 %s' % (n, n * 16, h.hexdigest()))

senserShellCommand(complete=dump)
