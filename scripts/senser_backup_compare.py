#!/usr/bin/env python3
"""Compara volcados BK4 propiedad a propiedad (solo lectura). Uso: senser_backup_compare.py A.bin B.bin [C.bin ...]
Imprime cabecera, bytes distintos, propiedades distintas (id, atributos, tamaño, valor corto) y bytes fuera de propiedades."""
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.backup import BackupFile

def load(p):
    raw = open(p, 'rb').read()
    bf = BackupFile(io.BytesIO(raw))  # valida magia, revisión y checksum
    props = {i: (pr.attr, bytes(pr.data)) for i, pr in bf.listProperties()}
    return raw, bf, props

def cmp(na, a, nb, b):
    (ra, fa, pa), (rb, fb, pb) = a, b
    print(f'\n=== {na}  vs  {nb} ===')
    print('tamaño', len(ra), len(rb), '| checksum cabecera', hex(fa.header.checksum), hex(fb.header.checksum))
    nd = sum(x != y for x, y in zip(ra, rb)); print('bytes distintos totales:', nd)
    ch = [i for i in sorted(set(pa) | set(pb)) if pa.get(i) != pb.get(i)]
    print('propiedades:', len(pa), len(pb), '| distintas:', len(ch))
    bysub = {}
    for i in ch: bysub.setdefault(i >> 16, []).append(i)
    print('por subsistema:', {hex(k): len(v) for k, v in bysub.items()})
    for i in ch[:80]:
        x, y = pa.get(i), pb.get(i)
        f = lambda t: '-' if t is None else f'a={t[0]:#x} n={len(t[1])} {t[1][:16].hex()}'
        print(f'  {i:#x}  {f(x)}  ->  {f(y)}')
    if len(ch) > 80: print('  ...', len(ch) - 80, 'más')
    return ch

if __name__ == '__main__':
    L = [(p, load(p)) for p in sys.argv[1:]]
    for (n1, d1), (n2, d2) in zip(L, L[1:]): cmp(os.path.basename(os.path.dirname(n1)) + '/' + os.path.basename(n1), d1, os.path.basename(os.path.dirname(n2)) + '/' + os.path.basename(n2), d2)
