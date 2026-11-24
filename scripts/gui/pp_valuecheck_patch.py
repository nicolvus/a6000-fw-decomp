#!/usr/bin/env python3
"""G107 — `libObj.so` 3.21: el validador de órdenes admite los Color Mode y Gamma que añade el CFW.

Causa de «PP7–PP10 no se pueden elegir» y de que S-Gamut no se guarde (VERIFICADO en bytes y con Unicorn): toda orden a la cámara pasa por `PreTypeCheck`
(`0xa3a9xx…0xa3ac90`), que para cada PARAMID enumerado llama a `EnumValueCheck` (`0xa3a21c`) con la lista de su definición de tipo (`0x95aca8` → registro de
12 B `{tipo, clase | cuenta << 16, lista}` en `0xfde034 + 12·(PARAMID − 0x9500)`, clase 4 = enumerado). Las listas de fábrica de `PP_COLOR_MODE_TYPE(_SET)` solo
traen los 8 Color Mode nativos y las de `PP_GAMMA_TYPE(_SET)` los 12 Gamma nativos: B&W, S-Gamut, S-Gamut3(.Cine), S-Log3 y HLG dan «ValueCheck ERROR» y la orden
no sale (PP7/PP8 llevan S-Gamut; PP9/PP10, S-Log3 y S-Gamut3).
Arreglo: listas nuevas = nativa + las del CFW (`patch_libobj_pp.COLOR` / `VALUEID(_HLG)`), en un segmento RW añadido (`rueda_film._anade`); en cada registro cuya
lista es la nativa se cambian el puntero (dirección absoluta con relocación RELATIVE: el sumando va en el sitio) y la cuenta. Idempotente.
Uso: pp_valuecheck_patch.py ENTRADA SALIDA [--hlg]
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import patch_libobj_pp as P
import rueda_film as R

REG_BASE, PID0, PID1 = 0xFDE034, 0x9500, 0x9A44          # tabla de definiciones de `0xaf4c1c` (PARAMID 0x9500…0x9a44)
COLOR_FABRICA = P.COLOR[:8]
GAMMA_FABRICA = (0x1B7, 0x1B8, 0x1B9, 0x1BA, 0x39C, 0x39D, 0x39E, 0x39F, 0x3A0, 0x3A1, 0x480, 0x481)
R_ARM_RELATIVE = 23


def _registros(d: bytes):
    segs = A._segments(d)
    for pid in range(PID0, PID1 + 1):
        va = REG_BASE + 12 * (pid - PID0)
        _, b, p = struct.unpack_from("<3I", d, A._off(segs, va))
        if b & 0xFF == 4 and p:
            yield va, b, p, list(struct.unpack_from(f"<{b >> 16}I", d, A._off(segs, p)))


def patch(d: bytes, hlg: bool = False) -> bytes:
    gamma = GAMMA_FABRICA + tuple(v for v in (P.VALUEID_HLG if hlg else P.VALUEID) if v not in GAMMA_FABRICA)
    nuevas = {COLOR_FABRICA: P.COLOR, GAMMA_FABRICA: gamma}
    sitios = [(va, b, tuple(lista)) for va, b, _, lista in _registros(d) if tuple(lista) in nuevas or tuple(lista) in nuevas.values()]
    assert len(sitios) >= 4, "definiciones de Color Mode/Gamma no encontradas (¿otra libObj?)"
    if all(lista in nuevas.values() for _, _, lista in sitios):
        return d
    assert all(lista in nuevas for _, _, lista in sitios), "listas a medio parchear"
    orden = list(nuevas.values())
    palabras = [v for lista in orden for v in lista]

    def parches(out, pal, _, rel):
        segs = A._segments(bytes(out))
        for va, b, lista in sitios:
            nueva = nuevas[lista]
            assert R._rel_de(bytes(out), rel, va + 8)[1] & 0xFF == R_ARM_RELATIVE, f"{va + 8:#x} sin relocación RELATIVE"
            dest = pal + 4 * sum(len(x) for x in orden[:orden.index(nueva)])
            struct.pack_into("<II", out, A._off(segs, va + 4), (len(nueva) << 16) | (b & 0xFFFF), dest)
        return {}

    return R._anade(d, lambda _: (palabras, []), None, parches)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes(), "--hlg" in sys.argv))
    print("ok", sys.argv[2])
