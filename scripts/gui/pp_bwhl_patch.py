"""G33-B — Hi-Light Detail (y, opcional, B/W Balance) por la rama nativa del APC del núcleo (`av-cam.bin`, A6000 fw3.21). Solo construye bytes; no instala.

La rama nativa ya lee los bytes Detail del PP (ctx+0x139…0x13f = cfg+0x159…0x15f, copiados por `0x438b83a0`), pero está cerrada por el byte
`[0x43f9a1c2] == 1`, que vive en un bloque de ajuste cargado en ejecución (entrada 133 de la tabla `0x43ff3200`; en el archivo es cero).
El parche no toca código: cambia el desplazamiento GOT del literal de cada sitio para que `r3` apunte a una tabla propia `T` (T[0] = 1).
Solo se redirigen los literales de los sitios elegidos; los otros seis lectores de la bandera siguen igual (no se duplica G33 `pp_gain`/`pp_coring`).
Detalle y límites: docs/gui/g33b-bw-balance-hilight.md.
"""
import struct

BASE, GOT = 0x43541000, 0x4401EEE4
FLAG, FLAG_SLOT, FLAG_OFF = 0x43F9A1C2, 0x44026284, 0x73A0       # GOT+0x73a0 → 0x43f9a1c2
HL_LIT, BW_LIT = 0x438B172C, 0x438B1A1C                           # literales de 0x438b154a (FUN_438b11f0) y 0x438b18ee (FUN_438b177c)
# Hi-Light Detail 0…4 → T[0x1b…0x1f]: con Detail Mode Manual la rama nativa sustituye sp+0x7c (2.º umbral interpolado, r0) por sp+0x7a (1.º, r7) + T[i].
# No es neutra en ningún índice: los valores de Sony están en el bloque de ajuste de ejecución (NO_VERIFICADO).
# shortcut: anchura estimada; leer el bloque 0x43f9a1c2 en cámara (o medir con G33-A) antes de instalar.
HL = (0, 6, 12, 18, 24)
SIZE = 0x24                                                       # puntero (4 B) + T (0x20 B)
# Cueva propuesta: cabeza del hueco de G18 antes de SLOT0 de pp_curves_patch (0x43faf28c…0x43faf300, 0x74 B libres y sin uso).
# Aplicar después de pp_curves_patch, que exige todo el hueco a cero.
CAVE = 0x43FAF290


def patches(base: bytes, cave: int, hl=HL, bw=None) -> list[tuple[int, bytes, str]]:
    """Escrituras (dirección, bytes, descripción). `cave`: 0x24 B a cero, alineados a 4, en una zona que nadie más use.
    `bw`: 5 bytes (nibble bajo → sp+0x34, alto → sp+0x36) para B/W Balance Type1…5; None = no se toca B/W (sus valores neutros no se conocen)."""
    u32 = lambda a: struct.unpack_from("<I", base, a - BASE)[0]
    assert u32(FLAG_SLOT) == FLAG, "ranura GOT de la bandera distinta del fw3.21"
    for lit in (HL_LIT, BW_LIT):
        assert u32(lit) == FLAG_OFF, f"literal {lit:#x} distinto del fw3.21"
    assert cave % 4 == 0 and not any(base[cave - BASE:cave - BASE + SIZE]), "la cueva no está a cero"
    assert len(hl) == 5 and (bw is None or len(bw) == 5)
    t = bytearray(0x20)
    t[0] = 1
    t[0x1B:0x20] = bytes(hl)
    if bw:
        t[0x12:0x17] = bytes(bw)
    off = struct.pack("<I", (cave - GOT) & 0xFFFFFFFF)
    ps = [(cave, struct.pack("<I", cave + 4) + bytes(t), "dato bwhl tabla"), (HL_LIT, off, "literal Hi-Light 0x438b154a")]
    if bw:
        ps.append((BW_LIT, off, "literal B/W 0x438b18ee"))
    return ps
