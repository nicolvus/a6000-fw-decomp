"""G22 (3.59) — eco local del valor de «Silent Shooting» en `libObj.so` (A6000 fw3.21; dirección = desplazamiento de fichero).

Con el 3.58 el menú abre pero vuelve siempre a Off: la lectura (clave `0x292`, contenedor `obj+0x54c` creado con id `0x6c`) solo se
actualiza con la notificación `0x768f` del núcleo (`0x67984c`, propiedades `0x9984/0x9985`), que en la A6000 no llega.
En el setter `0x686d10`, tras un envío `0x768e` correcto (`cbz r0` de `0x686de4`), el registro de log `0xab2` se sustituye por lo
mismo que hace el manejador de `0x768f` con el elemento 0: `0x68e0ce(cont, 0, valor_UI)` (guarda y avisa al oyente) y
`0x68c39c(cont, 0)`. `r5` = valor UI (1 Off / 2 On), callee-saved y muerto tras este punto. La ruta de error `0xaae` pierde su log;
`0x686df4..0x686dfa` (bl log + b) se conserva porque lo usa la ruta `0xaa9`. Si el núcleo emite `0x768f`, sobrescribe el eco.
"""
from __future__ import annotations

SET_ELEM, MARK = 0x68E0CE, 0x68C39C
SITES: tuple[tuple[int, bytes, bytes, str], ...] = (
    (0x686DE6, bytes.fromhex("1f4a40f6ae2100902b4620467a44"), bytes.fromhex("12e02846002105f0d6fa0de000bf"),
     "error 0xaae -> b 0x686e0e; cont.: mov r0,r5; movs r1,#0; bl 0x68c39c; b 0x686e0e"),
    (0x686DFA, bytes.fromhex("7b6a204640f6b22147f28e6200932b4606f012fb"), bytes.fromhex("2a46d4f84c552846002107f063f9eee700bf00bf"),
     "ok: mov r2,r5; ldr.w r5,[r4,#0x54c]; mov r0,r5; movs r1,#0; bl 0x68e0ce; b 0x686de8"),
)


def apply_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for off, old, new, _ in SITES:
        have = bytes(out[off:off + len(old)])
        if have != new:
            if have != old:
                raise ValueError(f"bytes inesperados en {off:#x}: {have.hex()}")
            out[off:off + len(new)] = new
    return bytes(out)


def restore_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for off, old, new, _ in SITES:
        if bytes(out[off:off + len(new)]) != new:
            raise ValueError(f"el parche no está aplicado en {off:#x}")
        out[off:off + len(old)] = old
    return bytes(out)


def allowed_offsets() -> set[int]:
    return {off + i for off, old, _, _ in SITES for i in range(len(old))}


if __name__ == "__main__":
    import sys
    from pathlib import Path

    Path(sys.argv[2]).write_bytes(apply_bytes(Path(sys.argv[1]).read_bytes()))
