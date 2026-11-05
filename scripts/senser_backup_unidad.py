#!/usr/bin/env python3
"""Propiedades BK4 específicas de la unidad (solo lectura). Uso: senser_backup_unidad.py PLANTILLA.bin V1.bin V2.bin ...
Una propiedad es «de la unidad» si es igual en todos los volcados, no es cero y difiere de la plantilla del paquete.
Imprime recuento y bytes por subsistema, y las propiedades que cambian entre volcados."""
import collections, io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.backup import BackupFile

def load(p):
    return {i: bytes(pr.data) for i, pr in BackupFile(io.BytesIO(open(p, 'rb').read())).listProperties()}

tpl, *dumps = (load(p) for p in sys.argv[1:])
assert dumps, 'faltan volcados'
unit, moved = [], []
for i, v0 in dumps[0].items():
    if len({d[i] for d in dumps}) > 1: moved.append(i)
    elif any(v0) and v0 != tpl.get(i): unit.append(i)
for name, ids in (('de la unidad (estables)', unit), ('que cambian entre volcados', moved)):
    c = collections.defaultdict(lambda: [0, 0])
    for i in ids: c[i >> 16][0] += 1; c[i >> 16][1] += len(dumps[0][i])
    print(f'{name}: {len(ids)}')
    for s, (n, b) in sorted(c.items(), key=lambda x: -x[1][1]): print(f'  {s:#x}: {n} props, {b} B')
