#!/usr/bin/env python3
"""G42 — «ISO expandido» (parche del CONSUMIDOR): `libObj.so` 3.21 sustituye el MAX de ISO recibido de av-cam por 102400 (código 0x29).

Sitio: conversor de mensaje `0x4db7c4`, tras `0x42ac00(msg, 0x1f0, &v)` (v = código ISO máximo, [r7+0x38]); el valor va luego a `0x4e0ea8`
y se guarda como `PARAMID_ISO_SPEED_RATE_MAX` (0x96ff). Se reutilizan los 14 B del aviso «Invalid ObjMsg» (`cbz; ldr; add.w; add; bl`) como
`ldr r1,[r7,#0x38]; sub.w r2,r1,#0x26; cmp r2,#3; it lo; movlo r1,#0x29; str r1,[r7,#0x38]`: los códigos 0x26..0x28 pasan a 0x29. Sin cueva.
shortcut: se pierde el log de error de ese campo; el rango estándar (0x377 → 0x98a1) no se toca.
ATENCIÓN: solo es seguro junto a `wrapperIso::getIso` (acepta ≤0x26) y a nodos de menú >51200 (no existen): ver docs/gui/g42-iso-consumidor.md.
Uso: iso_max_patch.py [--51200] ENTRADA.so SALIDA.so   (--51200: MAX 0x23..0x28 -> 0x26; valida los bytes originales; idempotente)
"""
import sys

SITE = 0x4DB86E
OLD = bytes.fromhex("28b19a4907f11800794403f0effc")  # cbz r0,+0x0e; ldr r1,[pc]; add.w r0,r7,#0x18; add r1,pc; bl 0x4df25a
NEW = bytes.fromhex("b96ba1f1260203 2a38bf2921b963".replace(" ", ""))
# Variante 51200 (G48): códigos 0x23..0x28 -> 0x26 (sub.w r2,r1,#0x23; cmp r2,#6; movlo r1,#0x26). Basta con la lista Default + `wrapperIso::getIso` (<=0x26).
NEW51 = bytes.fromhex("b96ba1f12302062a38bf2621b963")
NEXT = bytes.fromhex("2846b96b07f14402")            # mov r0,r5; ldr r1,[r7,#0x38]; add.w r2,r7,#0x44 (ancla de lo que sigue)


def patch(d: bytes, new: bytes = NEW) -> bytes:
    assert len(new) == len(OLD) == 14
    assert d[SITE + 14:SITE + 22] == NEXT, "ancla de 0x4db87c distinta del fw3.21"
    cur = d[SITE:SITE + 14]
    if cur == new:
        return d
    assert cur in (OLD, NEW, NEW51), f"bytes inesperados {cur.hex()}"
    return d[:SITE] + new + d[SITE + 14:]


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--51200"]
    open(a[1], "wb").write(patch(open(a[0], "rb").read(), NEW51 if "--51200" in sys.argv else NEW))
    dst = a[1]
    print("ok", dst)
