"""E26-R56 — pkt[0x0e] = ajuste EFCS en vivo, en línea en el constructor del envío 0x438d0064.

Sustituye el cálculo de Sony del byte (0x438d01ae–0x438d01c1: `[obj+0x4b68] − [obj+0x1d8]` o 0xff,
solo usado por el `strb.w r3,[r2,#0x4e]` de 0x438d01fa) por la lectura del ajuste en vivo:

    0x438d01ae  ldr r3,[pc,#8]      ; literal en 0x438d01b8
    0x438d01b0  ldr r3,[r3]         ; bloque de ajustes 0x43edf684 + 0x210 (0/1)
    0x438d01b2  b   0x438d01c2      ; continúa como Sony (r2 = 0, strb [obj+0x768])
    0x438d01b4  nop; nop; literal 0x43edf894; nop; nop; nop

También el paquete de la foto en 0x43841070 (CTOR, más abajo).

Sin cuevas: el bloque TPZL 0 de nflasha3 (cabecera de av-cam y 0x43541800…) queda como el de Sony
(R55 §5: modificarlo cuelga el LZP de Linux). Sin selector en 0x43841070 ni C3-B. No instala.
"""
from __future__ import annotations

from e25_24 import patch_bionz as PB

BASE, SIZE, SHA256 = PB.BASE, PB.SIZE, PB.SHA256
SITE = 0x438D01AE
OLD = bytes.fromhex("04f596439b6e23b1d4f8d8219b1adbb200e0ff23")
LIVE_EFCS = PB.LIVE_EFCS
NEW = (bytes.fromhex("024b" "1b68" "06e0" "00bf" "00bf") + LIVE_EFCS.to_bytes(4, "little")
       + bytes.fromhex("00bf00bf00bf"))
assert len(NEW) == len(OLD)

# Paquete de la foto (pkt[8]=0xa0) en 0x43841070: Sony escribe pkt[0x0e]=0 en 0x43841476. Se reescribe
# 0x43841472–0x4384148b (salvo el ldr.w pc-relativo de 0x4384147c, que no se mueve) con instrucciones
# más cortas que dan el mismo pkt[0x0d] y además pkt[0x0e] = [sb+0x41c] (modo EFCS de la captura).
CTOR = (
    (0x43841472, bytes.fromhex("00f00300a37301f00101"),
     bytes.fromhex("d9f81c34" "a373" "8007" "c00e")),      # ldr.w r3,[sb,#0x41c]; strb r3,[r4,#0xe];
                                                            # lsls r0,#30; lsrs r0,#27  -> (r0&3)<<3
    (0x43841480, bytes.fromhex("9201490101ebc00189186173"),
     bytes.fromhex("c907" "890e" "9201" "0918" "8918" "6173")),  # (r1&1)<<5; r2<<6; r1+=r0; r1+=r2; strb
)
SITES = ((SITE, OLD, NEW), *CTOR)


def apply_bytes(data: bytes) -> tuple[bytes, list[dict]]:
    if len(data) != SIZE:
        raise PB.ImageError("tamaño inesperado")
    out = bytearray(data)
    diff: list[dict] = []
    for addr, old, new in SITES:
        off = addr - BASE
        have = bytes(out[off:off + len(old)])
        if have == new:
            continue
        if have != old:
            raise PB.ImageError(f"bytes inesperados en {addr:#x}: {have.hex()}")
        out[off:off + len(new)] = new
        diff += [{"address": addr + i, "before": f"{a:02x}", "after": f"{b:02x}",
                  "role": "pkt[0x0e] = modo EFCS (en línea)"}
                 for i, (a, b) in enumerate(zip(old, new)) if a != b]
    return bytes(out), diff


def allowed_addresses() -> set[int]:
    return {addr + i for addr, old, _ in SITES for i in range(len(old))}


def restore_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for addr, old, new in SITES:
        off = addr - BASE
        if bytes(out[off:off + len(new)]) != new:
            raise PB.ImageError(f"el parche no está aplicado en {addr:#x}")
        out[off:off + len(old)] = old
    return bytes(out)
