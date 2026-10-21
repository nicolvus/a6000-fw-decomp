#!/usr/bin/env python3
"""Volcado SOLO LECTURA (RMEM por service mode) de las regiones de periféricos que declara /proc/iomem, cada una por separado.

Uso: python -W ignore scripts/senser_regions_dump.py OUTDIR [REGION ...]
Una región que falle no detiene las demás. Aviso: leer registros puede tener efectos de lectura (FIFO/limpiar-al-leer); se limita a lo declarado en iomem."""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

ALL = [('arm7sram', 0x00000000, 0x4000), ('arm7io', 0x00011000, 0x1000), ('nandreg', 0x00020000, 0x10000), ('nandc', 0x10000000, 0x10000),
           ('usb_ehci', 0xf0200000, 0x1000), ('usb_ohci', 0xf0201000, 0x1000), ('usb_udc', 0xf0210000, 0x20000),
           ('uart0', 0xf2000000, 0x1000), ('uart2', 0xf2002000, 0x1000), ('sfr_f1000000', 0xf1000000, 0x100)]
REGIONS = [r for r in ALL if len(sys.argv) < 3 or r[0] in sys.argv[2:]]  # opcional: nombres de región a leer
out = sys.argv[1]; os.makedirs(out, exist_ok=True)


def dump(cam):
    be = SenserPlatformBackend(cam); be.start(); sums = []
    for name, addr, size in REGIONS:
        p = os.path.join(out, '%s_%#x_%#x.bin' % (name, addr, size))
        try:
            with open(p, 'wb') as f:
                class W:
                    def write(self, d): f.write(d); return len(d)
                be.readMemory(addr, size, W())
            d = open(p, 'rb').read(); sums.append('%s  %s' % (hashlib.sha256(d).hexdigest(), os.path.basename(p)))
            print('OK    %-14s %#x +%#x' % (name, addr, size), flush=True)
        except Exception as e:
            os.path.exists(p) and os.remove(p); print('FALLO %-14s %#x: %s' % (name, addr, e or type(e).__name__), flush=True)
    open(os.path.join(out, 'SHA256SUMS'), 'w').write('\n'.join(sums) + '\n')

senserShellCommand(complete=dump)
