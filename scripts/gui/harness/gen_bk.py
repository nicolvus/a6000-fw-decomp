#!/usr/bin/env python3
"""Convierte un volcado NVRAM BK4 en /usr/share/bk.tbl para el shim. Uso: gen_bk.py backup_flash.bin salida.tbl"""
import io, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'references', 'pmca'))
from pmca.backup import BackupFile
bf = BackupFile(io.BytesIO(open(sys.argv[1], 'rb').read()))
with open(sys.argv[2], 'wb') as o:
    for i, p in bf.listProperties():
        d = bytes(p.data); o.write(struct.pack('<II', i, len(d)) + d + b'\0' * (-len(d) % 4))
