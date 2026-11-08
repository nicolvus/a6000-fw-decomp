#!/usr/bin/env python3
"""Escribe la tabla EFCS por velocidad de Darwin v3 (R82) en la NVRAM de la cámara (propiedad 0x1850000, G+0x48..0x7f).
Sin volcado previo a fichero: lee la NVRAM en memoria, cambia solo esos 56 bytes (exige que estén a cero), recalcula el checksum,
escribe, relee y sincroniza. ESCRIBE en la cámara solo con --execute (por defecto lee y muestra). Reversión: --zero.
Tablas: modelo R82 (por defecto), --zero (neutra), --test (prueba de llegada a Darwin: una sola entrada, c = 2000 µs a todas las velocidades).
Uso: senser_efcs_table_write.py [--execute] [--zero | --test]   (PYTHONPATH=references/pmca)"""
import argparse
import io
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'e26_r76'))
import e26_r76_parche_darwin_tabla as P
from pmca.backup import BackupFile
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

# modelo R74/R82 (Tmax µs, c µs); bytes de referencia en docs/capture/e26-r82-parche-efcs-v3.md §5
MODEL = [(347, 1264), (551, 1287), (1752, 1310), (1982, 1266), (2091, 1157), (2199, 1374), (3504, 1266), (4411, 1050),
         (5560, 793), (7008, 462), (9834, 24)]
DOC = bytes.fromhex("0cf4f004d8f40705" "89f91e056ffaf204" "dcfa850448fb5e05" "6100f204ec031a04" "69081903110ece01" "1b191800" + "00800000" * 3)
ap = argparse.ArgumentParser()
ap.add_argument('--execute', action='store_true')
ap.add_argument('--zero', action='store_true', help='deja la tabla a ceros (neutra)')
ap.add_argument('--test', action='store_true', help='c = 2000 µs (máximo) a todas las velocidades: sobreexpone ~+0,8 EV a 1/1000 si Darwin lo lee')
args = ap.parse_args()


def run(cam):
    be = SenserPlatformBackend(cam)
    be.start()
    assert b'CX77500_E38' in be.getBackupStatus(), 'región distinta'
    cur = be.getBackupData()
    bf = BackupFile(io.BytesIO(cur))
    g = bytearray(bf.getProperty(0x1850000).data)
    assert len(g) == 128, len(g)
    g42 = struct.unpack_from('<H', g, 0x42)[0]
    print('G+0x42 =', g42, '| tabla actual:', bytes(g[P.TAB_OFF:]).hex())
    model = P.tabla_bytes(MODEL, g42)
    assert g42 == 3407 and model == DOC, 'la tabla calculada no coincide con la de R82'
    cur_tab = bytes(g[P.TAB_OFF:])
    assert cur_tab in (bytes(56), DOC, P.tabla_bytes([(30000, 2000)], g42)), 'tabla actual desconocida: abortar'
    new = bytes(56) if args.zero else P.tabla_bytes([(30000, 2000)], g42) if args.test else model
    if not args.execute:
        print('SIMULACIÓN. Escribiría:', new.hex())
        return
    buf = io.BytesIO(cur)
    bf = BackupFile(buf)
    g[P.TAB_OFF:] = new
    bf.setProperty(0x1850000, bytes(g))
    bf.updateChecksum()
    out = buf.getvalue()
    assert len(out) == len(cur)
    be.setBackupData(out)
    back = BackupFile(io.BytesIO(be.getBackupData())).getProperty(0x1850000).data
    assert bytes(back[P.TAB_OFF:]) == new, 'la relectura no coincide: no se sincroniza'
    print('verificación en memoria: OK')
    be.syncBackup()
    print('sincronizado a flash')


senserShellCommand(complete=run)
