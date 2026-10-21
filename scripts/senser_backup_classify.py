#!/usr/bin/env python3
"""Clasifica propiedades BK4 entre base (A), fallada (F) y restaurada (R). Solo lectura. Uso: senser_backup_classify.py A F R [--md]"""
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.backup import BackupFile

def load(p):
    raw = open(p, 'rb').read(); bf = BackupFile(io.BytesIO(raw))
    return {i: (pr.attr, bytes(pr.data)) for i, pr in bf.listProperties()}

A, F, R = (load(p) for p in sys.argv[1:4])
cls = {}
for i in sorted(set(A) | set(F) | set(R)):
    a, f, r = A.get(i), F.get(i), R.get(i)
    if a == f == r: continue
    k = ('F=A, R distinta (cambió tras restaurar)' if a == f else
         'restaurada (R=A)' if r == a else
         'R=F (no se restauró)' if r == f else 'las tres distintas')
    cls.setdefault(k, []).append(i)
print({k: len(v) for k, v in cls.items()}, 'propiedades iguales:', sum(1 for i in A if A[i] == F.get(i) == R.get(i)))
def diffs(x, y):
    return [j for j in range(min(len(x), len(y))) if x[j] != y[j]]
for k, ids in cls.items():
    print(f'\n## {k}: {len(ids)}')
    by = {}
    for i in ids: by.setdefault(i >> 16, []).append(i)
    for s, L in by.items():
        print(f'- subsistema {s:#x}: {len(L)} props, p. ej. ' + ', '.join(hex(i) for i in L[:6]))
    if len(ids) <= 40 or '--md' in sys.argv:
        for i in ids[:60]:
            a, f, r = A.get(i), F.get(i), R.get(i)
            def show(t, ref=a):
                if t is None: return '-'
                if len(t[1]) <= 12: return t[1].hex()
                d = diffs(t[1], ref[1]) if ref else []
                return f'{len(t[1])}B' + (f' dif@{",".join(hex(j) for j in d[:5])}' if d else '')
            print(f'  {i:#x} attr={(a or f or r)[0]:#x} n={len((a or f or r)[1])} A={show(a)} F={show(f)} R={show(r)}')
