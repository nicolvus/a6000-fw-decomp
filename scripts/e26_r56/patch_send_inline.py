"""E26-R56 — pkt[0x0e] = ajuste EFCS en vivo, en línea en el constructor del envío 0x438d0064.

Sustituye el cálculo de Sony del byte (0x438d01ae–0x438d01c1: `[obj+0x4b68] − [obj+0x1d8]` o 0xff,
solo usado por el `strb.w r3,[r2,#0x4e]` de 0x438d01fa) por la lectura del ajuste en vivo:

    0x438d01ae  ldr r3,[pc,#8]      ; literal en 0x438d01b8
    0x438d01b0  ldr r3,[r3]         ; bloque de ajustes 0x43edf684 + 0x210 (0/1)
    0x438d01b2  b   0x438d01c2      ; continúa como Sony (r2 = 0, strb [obj+0x768])
    0x438d01b4  nop; nop; literal 0x43edf894; nop; nop; nop

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


def apply_bytes(data: bytes) -> tuple[bytes, list[dict]]:
    if len(data) != SIZE:
        raise PB.ImageError("tamaño inesperado")
    off = SITE - BASE
    have = data[off:off + len(OLD)]
    if have == NEW:
        return data, []
    if have != OLD:
        raise PB.ImageError(f"bytes inesperados en {SITE:#x}: {have.hex()}")
    out = data[:off] + NEW + data[off + len(NEW):]
    diff = [{"address": SITE + i, "before": f"{a:02x}", "after": f"{b:02x}",
             "role": "envío: pkt[0x0e] = ajuste EFCS en vivo (en línea)"}
            for i, (a, b) in enumerate(zip(OLD, NEW)) if a != b]
    return out, diff


def allowed_addresses() -> set[int]:
    return {SITE + i for i in range(len(OLD))}


def restore_bytes(data: bytes) -> bytes:
    off = SITE - BASE
    if data[off:off + len(NEW)] != NEW:
        raise PB.ImageError(f"el parche no está aplicado en {SITE:#x}")
    return data[:off] + OLD + data[off + len(OLD):]
