"""Genera la tabla de sitios lógicos del av-cam (3.21 -> CFW) y los volcados de evidencia."""
import hashlib, json, struct, sys
from pathlib import Path

BASE = 0x43541000
EVI = Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/reports/evidence/film-pb-1-sub-avcam-parches-20261126')
EVI.mkdir(parents=True, exist_ok=True)
A = Path('/tmp/avc/avcam_321.bin').read_bytes()
B0 = Path('/tmp/avc/avcam_base.bin').read_bytes()
P = Path('/tmp/avc/avcam_pp.bin').read_bytes()

# (etiqueta, VA inicio, VA fin EXCLUSIVO, familia, categoría, qué)
SITES = [
    ("T1", 0x43841472, 0x43841488, "integrado", "captura", "ctor del paquete de foto (0x0c): EFCS/Silent"),
    ("T2", 0x4384219E, 0x438421A2, "integrado", "captura", "lector Sony cap+0x41c -> ldrb"),
    ("T3", 0x43842270, 0x43842274, "integrado", "captura", "lector Sony cap+0x41c -> ldrb"),
    ("T4", 0x43845F2E, 0x43845FA4, "integrado", "captura", "copiador de ajustes a cap+0x41c/0x41d (118 B)"),
    ("T5", 0x438C82FE, 0x438C8302, "integrado", "captura", "gancho silent r5 en la secuencia de foto"),
    ("T6", 0x43FB7E00, 0x43FB7E6C, "integrado", "captura", "cueva silent r5 (Tv -> cap+0x64c)"),
    ("T7", 0x438D01A2, 0x438D01A6, "integrado", "captura", "envio a Darwin: cbnz r6"),
    ("T8", 0x438D01AA, 0x438D01C2, "integrado", "captura", "envio a Darwin: pkt[0x0e]=silent"),
    ("P1", 0x437A2728, 0x437A2744, "pp", "imagen/color", "monocromo = tipo Color Mode 8 (B&W)"),
    ("P2", 0x437A44D2, 0x437A44D6, "pp", "imagen/color", "S-Gamut3: limite del conjunto de deltas 0x18 -> 0x1a"),
    ("P3", 0x437A44FA, 0x437A44FE, "pp", "imagen/color", "S-Gamut3: gancho a cueva de deltas"),
    ("P4", 0x437A4B42, 0x437A4B46, "pp", "imagen/color", "S-Gamut3: limite de matriz 0xf -> 0x11"),
    ("P5", 0x437A4B62, 0x437A4B66, "pp", "imagen/color", "S-Gamut3: gancho a cueva de matrices"),
    ("P6", 0x437A4DB2, 0x437A4DB6, "pp", "imagen/color", "switch id Color Mode: caso por defecto -> cueva"),
    ("P7", 0x437AA816, 0x437AA818, "pp", "imagen/color", "tabla tipo->id: cmp 6 -> 0xa"),
    ("P8", 0x437AAFE0, 0x437AAFE4, "pp", "imagen/color", "literal de la tabla tipo->id -> cueva 0x43fb7410"),
    ("P9", 0x43802B64, 0x43802B68, "pp", "control/ajustes", "desempaquetador del 0x4066: snapshot pp"),
    ("P10", 0x43853226, 0x4385322A, "pp", "imagen/YC", "tramplin curva LUT (constructor 1)"),
    ("P11", 0x4385392E, 0x43853932, "pp", "imagen/YC", "tramplin curva LUT (constructor 2)"),
    ("P12", 0x43853C8E, 0x43853C92, "pp", "imagen/YC", "tramplin curva LUT (constructor 3)"),
    ("P13", 0x4386783A, 0x4386783C, "pp", "imagen/YC", "S-Log3: cmp gamma <= 2 -> <= 3 (0x14..0x17)"),
    ("P14", 0x43867924, 0x43867926, "pp", "imagen/YC", "S-Log3: blo 0x4386794c -> 0x43867932 (clase S-Log2)"),
    ("P15", 0x438B172C, 0x438B1730, "pp", "imagen/YC", "literal GOT de Hi-Light -> tabla de la cueva"),
    ("P16", 0x438B336E, 0x438B3372, "pp", "imagen/YC", "APC coring: tramplin (job_apc_coring_stl)"),
    ("P17", 0x438B3D52, 0x438B3D56, "pp", "imagen/YC", "APC ganancia: tramplin (job_apc_gain_stl)"),
    ("D1", 0x43BC868C, 0x43BC8690, "pp", "datos", "tabla de clase por gamma [0x17] = 8"),
    ("D2", 0x43CB56EA, 0x43CB56FE, "pp", "datos", "tabla selector->gamma (13 entradas de 2 B)"),
    ("D3", 0x43FAF290, 0x43FAF2B4, "pp", "datos", "datos Hi-Light de la cueva (puntero + T)"),
    ("D0", 0x43FB7400, 0x43FB7450, "pp", "datos", "datos de color: tabla tipo->id, matrices S-Gamut3 y deltas"),
    ("D4", 0x43FB7450, 0x43FB74F0, "pp", "codigo-cueva", "cueva del switch/matrices/deltas de Color Mode"),
    ("D5", 0x43FB7528, 0x43FB7982, "pp", "codigo-cueva", "cueva de tono: gancho 0x4066 + pp_curve/pp_gain/pp_coring"),
    ("D6", 0x43FAF300, 0x43FB7400, "pp", "tablas", "8 curvas de gamma de 0x101A B"),
    ("D7", 0x440014A8, 0x440014E4, "pp", "datos", "punteros de curva (tabla 0x44001404, indices 0x14..0x17)"),
]


def runs(x, y, lo, hi):
    out, s = [], None
    for i in range(lo, hi):
        if x[i] != y[i]:
            if s is None: s = i
            e = i
        elif s is not None:
            out.append((s, e)); s = None
    if s is not None: out.append((s, e))
    return out


rows, tot_diff = [], 0
for tag, lo, hi, fam, cat, what in SITES:
    rr = runs(A, P, lo - BASE, hi - BASE)
    n = sum(e - s + 1 for s, e in rr)
    r0 = runs(A, B0, lo - BASE, hi - BASE)
    n0 = sum(e - s + 1 for s, e in r0)
    tot_diff += n
    rows.append((tag, lo, hi, hi - lo, n, n0, len(rr), fam, cat, what, rr))
    print(f'{tag:3s} {lo:08x}..{hi-1:08x} span={hi-lo:5d} dif={n:5d} integrados={n0:4d} runs={len(rr):3d} {fam:9s} {cat:16s} {what}')

diff_all = sum(1 for i in range(len(A)) if A[i] != P[i])
covered = set()
for tag, lo, hi, *_ , rr in rows:
    for s, e in rr:
        for i in range(s, e + 1): covered.add(i)
print(f'\ntotal bytes distintos 3.21 -> CFW: {diff_all}')
print(f'cubiertos por los sitios de la tabla: {len(covered)}  fuera: {diff_all - len(covered)}')
print(f'suma de la columna dif: {tot_diff}')

json.dump([{'tag': t, 'va': hex(lo), 'va_end': hex(hi), 'span': sp, 'dif': n, 'dif_integrados': n0,
            'runs': [[hex(BASE + s), hex(BASE + e)] for s, e in rr], 'familia': f, 'categoria': c, 'que': w}
           for t, lo, hi, sp, n, n0, nr, f, c, w, rr in rows],
          open(EVI / 'sitios.json', 'w'), indent=1)
