#!/usr/bin/env python3
"""Convierte un volcado NVRAM BK4 en /usr/share/bk.tbl para el shim: registros {id u32, len u32, datos rellenados a 4}.
Uso: gen_bk.py backup_flash.bin salida.tbl"""
import io
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'references', 'pmca'))
from pmca.backup import BackupFile

with open(sys.argv[1], 'rb') as f:
    bf = BackupFile(io.BytesIO(f.read()))
with open(sys.argv[2], 'wb') as o:
    for i, p in bf.listProperties():
        d = bytes(p.data)
        o.write(struct.pack('<II', i, len(d)) + d + b'\0' * (-len(d) % 4))
