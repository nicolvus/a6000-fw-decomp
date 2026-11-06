#!/usr/bin/env python3
"""E26-R61 — Genera una variante de un BK4 cambiando un s16 dentro de una propiedad (solo offline; no toca la cámara).

Uso: bk4_variante.py ENTRADA.bin SALIDA.bin ID OFFSET DELTA      (ej.: 0x30102 0x88 500)
Comprueba el checksum de la entrada, suma DELTA (µs) al s16 de la propiedad en OFFSET y recalcula el checksum.
Aplicar después con scripts/senser_backup_restore.py SALIDA.bin SHA256 (ESCRIBE en la cámara)."""
import hashlib, io, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'references', 'pmca'))
from pmca.backup import BackupFile

src, dst, pid, off, delta = sys.argv[1], sys.argv[2], int(sys.argv[3], 0), int(sys.argv[4], 0), int(sys.argv[5], 0)
buf = io.BytesIO(open(src, 'rb').read())
bf = BackupFile(buf)                                   # valida cabecera y checksum
old = bf.getProperty(pid).data
cur = struct.unpack_from('<h', old, off)[0]
new = cur + delta
assert -32768 <= new <= 32767, 'desborda s16'
data = bytearray(old); struct.pack_into('<h', data, off, new)
bf.setProperty(pid, bytes(data)); bf.updateChecksum()
open(dst, 'wb').write(buf.getvalue())
chk = BackupFile(io.BytesIO(buf.getvalue())).getProperty(pid).data
print(f'{pid:#x}+{off:#x}: {cur} -> {struct.unpack_from("<h", chk, off)[0]} µs; sha256 {hashlib.sha256(buf.getvalue()).hexdigest()}')
dif = sum(a != b for a, b in zip(open(src, "rb").read(), buf.getvalue()))
print('bytes distintos respecto a la entrada:', dif)
