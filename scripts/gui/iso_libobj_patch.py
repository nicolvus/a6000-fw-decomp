#!/usr/bin/env python3
"""G104 §8.7 — `libObj` 3.21: códigos de modelo ISO 128000…409600 (`0x4b…0x50`), copiados de la A7S 3.20.

La A7S amplía los mismos dos conversores (VERIFICADO en sus bytes):
  * código → VALUEID (A6000 `0x4e0ea8`, `tbh` ≤ `0x4a`; A7S `0x409830`, ≤ `0x59`): `0x4b…0x50` → `0x3fd, 0x3fe, 0x3ff, 0x50e, 0x50f, 0x510`.
    Lo usa el receptor de las claves `0x1ee/0x1ef/0x1f0` (`0x4db7c4`) que manda `WrapperIso::setIso`: sin conversión no escribe nada.
  * VALUEID → código (A6000 `0x4e10b8`, árbol de `cmp`, desconocido = `0x2a`; A7S `0x409ab8`): esos VALUEID → `0x4b…0x50`.
    Lo usa `0x4e7c30` al armar la orden de ajustes (`PARAMID_ISO_SPEED_RATE_SET`/`MIN`/`MAX`/`ACT`).
Cuevas en los casos por defecto (`movs r0,#0|#0x2a; pop {r7,pc}` → `b.w`), en un segmento R+X añadido; el resto de códigos no cambia.
INFERENCIA: los VALUEID `0x50e…0x510` (256000…409600) no tienen nombre en el A6000 (su tabla de nombres acaba en `0x507`); solo se usan como valores.
Uso: iso_libobj_patch.py ENTRADA SALIDA
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import rueda_film as R

CODIGOS = (0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50)
VALUEIDS = (0x3FD, 0x3FE, 0x3FF, 0x50E, 0x50F, 0x510)
A_VALUEID, DEF_VALUEID = 0x4E0EA8, 0x4E10B4      # código → VALUEID (r1 código, r2 salida); por defecto `movs r0,#0; pop {r7,pc}`
A_CODIGO, DEF_CODIGO = 0x4E10B8, 0x4E13CE        # VALUEID → código (r1 VALUEID); por defecto `movs r0,#0x2a; pop {r7,pc}`


def patch(d: bytes) -> bytes:
    segs = A._segments(d)
    for va, h in ((DEF_VALUEID, "002080bd"), (DEF_CODIGO, "2a2080bd"), (A_VALUEID, "80b500af4a29"), (A_CODIGO, "4629")):
        if d[A._off(segs, va):A._off(segs, va) + len(h) // 2] != bytes.fromhex(h):
            raise ValueError(f"{va:#x}: bytes inesperados (¿otra versión o ya parcheado?)")
    a_val = "".join(f"cmp r1, #{c}; it eq; movweq r3, #{v}; " for c, v in zip(CODIGOS, VALUEIDS))
    a_val = f"sub.w r3, r1, #{CODIGOS[0]}; cmp r3, #{len(CODIGOS) - 1}; bhi v_no; " + a_val + "str r3, [r2]; movs r0, #1; pop {r7, pc}; v_no: movs r0, #0; pop {r7, pc}"
    a_cod = "".join(f"movw r3, #{v}; cmp r1, r3; itt eq; moveq r0, #{c}; popeq {{r7, pc}}; " for c, v in zip(CODIGOS, VALUEIDS)) + "movs r0, #0x2a; pop {r7, pc}"

    def cuevas(rx):
        c1 = R._asm(a_val, rx)
        c1 += b"\0" * (-len(c1) % 4)
        return c1 + R._asm(a_cod, rx + len(c1)), rx + len(c1)

    def parches(out, _, rx, __):
        for sitio, destino in ((DEF_VALUEID, rx), (DEF_CODIGO, cuevas(rx)[1])):
            out[A._off(segs, sitio):A._off(segs, sitio) + 4] = R._asm(f"b.w {destino:#x}", sitio)
        return {}

    return R._anade(d, lambda _: ([], []), lambda _, rx: cuevas(rx)[0], parches)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
    print("ok", sys.argv[2])
