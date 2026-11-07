#!/usr/bin/env python3
"""Lector/escritor de `string_<idioma>.uxc` (G2). Solo lectura del firmware; escribe donde se le indique.

Formato (VERIFICADO sobre string_english.uxc, 4 360/4 360 entradas del índice):
  0x00  'uxc\\x07' + u32 0 + u16 8 + u16 H + u32 (cuenta de ranuras | indicadores)
  0x10  tabla de `cuenta` u16: ranura k = id-0xe000; 0xffff = vacía; valor = (offset registro - base)/4
  base  registros: u16 id, u16 0x1e04, texto UTF-8, NUL, relleno a múltiplo de 4
Uso:  uxc_strings.py dump FICHERO | set FICHERO ID TEXTO SALIDA
"""
import struct
import sys
from pathlib import Path

FIRST_ID, END = 0xE000, 0xFFFF


def parse(d: bytes):
    """Devuelve (cabecera+tabla original, base, {id: texto})."""
    count = struct.unpack_from("<I", d, 12)[0] & 0x1FFF
    base = 0x10 + 2 * count
    recs, pos = {}, base
    while pos + 4 <= len(d):
        rid, typ = struct.unpack_from("<HH", d, pos)
        assert typ == 0x1E04, f"registro inesperado en {pos:#x}"
        end = d.index(b"\0", pos + 4)
        recs[rid] = d[pos + 4:end].decode("utf-8")
        pos += (end - pos + 1 + 3) & ~3
    return d[:base], base, recs


def build(head: bytes, recs: dict) -> bytes:
    """Reconstruye fichero e índice (el orden de registros sigue al de los ids)."""
    head, body, table = bytearray(head), bytearray(), {}
    for rid in sorted(recs):
        table[rid - FIRST_ID] = len(body) // 4
        raw = recs[rid].encode("utf-8") + b"\0"
        body += struct.pack("<HH", rid, 0x1E04) + raw + b"\0" * (-len(raw) % 4)
    assert len(body) // 4 < END, "los registros no caben en el índice de 16 bits"
    for k in range((len(head) - 0x10) // 2):
        struct.pack_into("<H", head, 0x10 + 2 * k, table.get(k, END))
    return bytes(head) + bytes(body)


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    head, _, recs = parse(Path(path).read_bytes())
    if cmd == "dump":
        for rid, txt in sorted(recs.items()):
            print(f"{rid:#06x}\t{txt!r}")
    elif cmd == "set":
        recs[int(sys.argv[3], 0)] = sys.argv[4]
        Path(sys.argv[5]).write_bytes(build(head, recs))
