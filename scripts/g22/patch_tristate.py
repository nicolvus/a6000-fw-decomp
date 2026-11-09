"""G22 — tres estados de obturador (Mecánico / EFCS / Electrónico): parche de BIONZ sobre el av-cam del 3.38 (offline, sin instalar).

`electronic = [ajustes+0x210] & [ajustes+0x238]` (EFCS desactivado y Silent activado). Sin cuevas (R55: el bloque TPZL 0 no se toca).
Sitios (todos en línea):
  1. copiador `0x43845f2e` (118 B, mismo tamaño): tras `cap+0x41c` = EFCS escribe `cap+0x41d` = electronic (bit 8 de esa palabra);
     los dos lectores de Sony que comparan `== 1` (`0x4384219e`, `0x43842270`) pasan a `ldrb.w` (mismo tamaño); los demás hacen `strb`;
     para ganar sitio se quitan las recargas `ldr r3,[r5]` (r2 de temporal, r0 libre: liveness comprobada con capstone).
  2. paquete de la foto `0x43841472`: `ldr.w r3,[sb,#0x41c]` -> `ldrb.w r3,[sb,#0x41d]` (mismo tamaño).
  3. envío `0x438d01aa..0x438d01c2`: `pkt[0x0e] = [+0x210] & [+0x238]`; el `cbnz r6` de `0x438d01a2` apunta a `0x438d01aa`
     y `cbz r6` elige `0x438d01c8` (r6 == 0) o `0x438d01c2`.
"""
from __future__ import annotations

from e25_24 import patch_bionz as PB

BASE = PB.BASE
LIVE_BASE = 0x43EDF684            # bloque de ajustes: +0x210 EFCS (0/1), +0x238 Silent (0/1, comando 0x40e3)
SHA256_3_38 = "2e9a56a5cbcccbd26a08a4c153b5c1378fd19d770b6d3c30b2dc03bbb70f782e"  # av-cam.integrated.bin del 3.38

SITES: tuple[tuple[int, bytes, bytes, str], ...] = (
    (0x438D01A2, bytes.fromhex("26b9"), bytes.fromhex("16b9"), "cbnz r6 -> 0x438d01aa"),
    (0x438D01AA, bytes.fromhex("03e000bf034b1b6806e0014b1b6806e000bf94f8ed4300bf"),
     bytes.fromhex("044ad2f81032d2f8382213403eb103e000bf") + LIVE_BASE.to_bytes(4, "little") + bytes.fromhex("00bf"),
     "envio: pkt[0x0e] = efcs & silent"),
    (0x4384219E, bytes.fromhex("d7f81c14"), bytes.fromhex("97f81c14"), "lector Sony: ldrb.w r1,[r7,#0x41c] (cmp #1)"),
    (0x43842270, bytes.fromhex("d7f81c24"), bytes.fromhex("97f81c24"), "lector Sony: ldrb.w r2,[r7,#0x41c] (cmp #1)"),
    (0x43841472, bytes.fromhex("d9f81c34"), bytes.fromhex("99f81d34"), "CTOR: ldrb.w r3,[sb,#0x41d]"),
    (0x43845F2E,
     bytes.fromhex("2b68d3f81022c4f81c24d3f8bc22c4f82024d3f8a020d3f80c31c4f8382484f843342b6893f8eb3484f844342b68d3f8943384f845342b68d3f82024d3f82c35c4f84824c4f88c3494f8423284f843322b681b6aa3f10309d9f1000343eb090384f842322b68d3f88021c4f8bc2393f8f13184f8d633"),
     bytes.fromhex("2b68d3f81022c4f81c24d3f83802104084f81d04d3f8bc22c4f82024d3f8a020c4f83824d3f80c2184f8432493f8eb2484f84424d3f8942384f84524d3f82024c4f84824d3f82c25c4f88c2494f8422284f843221a6aa2f10309d9f1000242eb090284f84222d3f88021c4f8bc2393f8f12184f8d623"),
     "copiador: cap+0x41d = efcs & silent"),
)


def apply_bytes(data: bytes) -> tuple[bytes, list[int]]:
    if len(data) != PB.SIZE:
        raise PB.ImageError("tamaño inesperado")
    out, changed = bytearray(data), []
    for addr, old, new, _ in SITES:
        off = addr - BASE
        have = bytes(out[off:off + len(old)])
        if have == new:
            continue
        if have != old:
            raise PB.ImageError(f"bytes inesperados en {addr:#x}: {have.hex()}")
        out[off:off + len(new)] = new
        changed += [addr + i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    return bytes(out), changed


def allowed_addresses() -> set[int]:
    return {addr + i for addr, old, _, _ in SITES for i in range(len(old))}


def restore_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for addr, old, new, _ in SITES:
        off = addr - BASE
        if bytes(out[off:off + len(new)]) != new:
            raise PB.ImageError(f"el parche no está aplicado en {addr:#x}")
        out[off:off + len(old)] = old
    return bytes(out)
